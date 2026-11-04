#!/usr/bin/env bash
# Shared helpers for review-pr scripts. Sourced, not executed.
# Exit codes: 0 ok, 1 tool failure, 2 usage, 3 prerequisite (spec: Components).

# An inherited repository-routing variable (set, for example, when invoked from a git hook) would
# redirect every `git -C` below, and the child's git, into the caller's repository and index.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_PREFIX

die() { # die CODE MESSAGE...
  local code="$1"; shift
  printf 'review-pr: %s\n' "$*" >&2
  exit "$code"
}

need_cmd() { command -v "$1" >/dev/null 2>&1 || die 3 "missing required command: $1"; }

validate_ref() { # validate_ref OWNER/REPO N
  local slug="$1" n="$2"
  [[ "$slug" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die 2 "first argument must be OWNER/REPO, got '$slug'"
  [[ "$n" =~ ^[1-9][0-9]*$ ]] || die 2 "PR number must be a positive integer, got '$n'"
}

load_adapter() { # load_adapter NAME
  local name="$1" adapter_dir supported_file
  [[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die 2 "invalid runner name: $name"
  adapter_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/adapters" >/dev/null 2>&1 && pwd -P)"
  supported_file="$adapter_dir/supported"
  if [ ! -r "$supported_file" ] || ! grep -Fxq -- "$name" "$supported_file"; then
    die 3 "unsupported review runner: $name"
  fi
  [ -f "$adapter_dir/$name.sh" ] || die 3 "supported review runner is missing its adapter: $name"
  unset -f adapter_check adapter_is_policy_path adapter_context_paths adapter_is_skill_path adapter_build_command adapter_normalize 2>/dev/null || true
  unset ADAPTER_POLICY_ROOTS ADAPTER_ALWAYS_REMOVE
  # shellcheck disable=SC1090
  . "$adapter_dir/$name.sh"
  declare -F adapter_check adapter_is_policy_path adapter_context_paths adapter_is_skill_path adapter_build_command adapter_normalize >/dev/null \
    || die 3 "runner adapter '$name' does not implement the required interface"
  declare -p ADAPTER_POLICY_ROOTS ADAPTER_ALWAYS_REMOVE >/dev/null 2>&1 \
    || die 3 "runner adapter '$name' does not declare its policy paths"
}

semver_at_least() { # semver_at_least HAVE WANT
  awk -v have="$1" -v want="$2" 'BEGIN {
    nh=split(have, h, "."); nw=split(want, w, "."); n=(nh>nw?nh:nw)
    for (i=1; i<=n; i++) {
      hv=h[i]+0; wv=w[i]+0
      if (hv>wv) exit 0
      if (hv<wv) exit 1
    }
    exit 0
  }'
}

valid_semver() { [[ "$1" =~ ^[0-9]+([.][0-9]+){2}$ ]]; }

validate_normalized_result() { # validate_normalized_result FILE
  jq -e '
    type == "object" and
    (.engine | type == "string" and length > 0) and
    (.engine_version == null or (.engine_version | type == "string")) and
    (.status == "completed" or .status == "error") and
    (.result | type == "string") and
    (.duration_ms == null or (.duration_ms | type == "number")) and
    (.cost_usd == null or (.cost_usd | type == "number")) and
    (.subtype == null or (.subtype | type == "string")) and
    (.errors | type == "array") and
    (.denials | type == "array")
  ' "$1" >/dev/null 2>&1
}

keep_requested() { [ "${REVIEW_PR_KEEP:-}" = 1 ]; }

# Working-tree checkouts of untrusted content run without the caller's global or
# system git config, so a PR-supplied .gitattributes cannot select a configured filter driver
# (smudge/process, e.g. git-lfs). The repo-local config of a fresh clone is ours, so it stays.
# GIT_CONFIG_PARAMETERS and GIT_CONFIG_COUNT (with GIT_CONFIG_KEY_n/VALUE_n) inject config through the
# environment and would survive the file overrides, so they are unset too.
git_wt() {
  env -u GIT_CONFIG_PARAMETERS -u GIT_CONFIG_COUNT -u GIT_CONFIG \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 git "$@"
}

# tree_listing DIR TREEISH [--name-only] -> path of a new temporary file holding TREEISH's `ls-tree -r -z` output.
# Whole-tree loops read this file rather than a pipe: bash reads a pipe one byte per system call but a regular
# file in blocks, which is most of a large tree's walk time. The caller removes the file.
tree_listing() {
  local listing
  listing="$(mktemp "${TMPDIR:-/tmp}/review-pr-tree.XXXXXX")" || die 1 "cannot create a temporary file"
  git -C "$1" ls-tree -r -z ${3:+"$3"} "$2" > "$listing" || { rm -f "$listing"; die 1 "cannot list tree $2"; }
  printf '%s\n' "$listing"
}

# policy_paths DIR TREEISH -> NUL-separated tracked policy paths at TREEISH (may be empty).
# Paths stay NUL-delimited end to end (ls-tree -z), so names containing newlines or tabs are
# neither split nor quoted.
policy_paths() {
  # Byte-wise matching (C locale): in a UTF-8 locale a pattern fails to match a name that is not valid UTF-8.
  local p listing LC_ALL=C
  listing="$(tree_listing "$1" "$2" --name-only)" || exit "$?"
  # The listing is unlinked once open, so a die mid-walk leaves nothing behind.
  # if/fi, not `&&`: under pipefail a non-matching final path would otherwise fail the whole loop.
  # shellcheck disable=SC2094 # Unlinking the open listing is deliberate.
  { rm -f "$listing"; while IFS= read -r -d '' p; do if adapter_is_policy_path "$p"; then printf '%s\0' "$p"; fi; done; } \
    < "$listing"
}

# policy_link_selected PATH -> success when a symlink at PATH would be read as reviewer policy.
policy_link_selected() {
  adapter_is_policy_path "$1" && return 0
  local root
  if [ "${#ADAPTER_POLICY_ROOTS[@]}" -gt 0 ]; then
    for root in "${ADAPTER_POLICY_ROOTS[@]}"; do [ "$1" != "$root" ] || return 0; done
  fi
  return 1
}

# policy_link_target DIR TREEISH LINK OID -> the path inside TREEISH that symlink LINK (blob OID) names.
# Implements RC11's resolution: the link text is resolved lexically against TREEISH, never through a working
# tree, so a head checkout cannot supply the target. On refusal it prints the reason and returns 1.
policy_link_target() {
  local dir="$1" tree="$2" link="$3" text size part prefix="" mode modes
  local -a comps=() parts=()
  # The trailing sentinel keeps trailing newlines that command substitution would strip.
  text="$(git -C "$dir" cat-file blob "$4" && printf x)" || { echo "link text is unreadable"; return 1; }
  text="${text%x}"
  size="$(git -C "$dir" cat-file -s "$4")" || { echo "link text is unreadable"; return 1; }
  # Bash drops NUL bytes from command substitution, so a byte count below the blob size means one.
  [ "$(LC_ALL=C; printf '%s' "${#text}")" = "$size" ] || { echo "link text contains a NUL byte"; return 1; }
  case "$text" in
    '') echo "link text is empty"; return 1;;
    /*) echo "link text is absolute"; return 1;;
    *$'\n'*) echo "link text contains a newline"; return 1;;
  esac
  case "$link" in */*) text="${link%/*}/$text";; esac
  IFS=/ read -r -a comps <<<"$text"
  for part in "${comps[@]}"; do
    case "$part" in
      ''|.) ;;
      ..) [ "${#parts[@]}" -gt 0 ] || { echo "target leaves the repository"; return 1; }
          unset "parts[$((${#parts[@]} - 1))]";;
      *) parts+=("$part");;
    esac
  done
  [ "${#parts[@]}" -gt 0 ] || { echo "target is the repository root"; return 1; }
  # Every ancestor must be a directory of TREEISH: an intermediate symlink would need a second resolution.
  for part in "${parts[@]}"; do
    if [ -n "$prefix" ]; then
      mode="$(git -C "$dir" --literal-pathspecs ls-tree --format='%(objectmode)' "$tree" -- "$prefix")"
      [ "$mode" = 040000 ] || { echo "target is not reached through directories only: $prefix"; return 1; }
    fi
    prefix="${prefix:+$prefix/}$part"
  done
  mode="$(git -C "$dir" --literal-pathspecs ls-tree --format='%(objectmode)' "$tree" -- "$prefix")"
  case "$mode" in
    100644|100755) ;;
    040000)
      # A symlink or submodule inside the target would put content outside the base tree at the link path.
      # Capture the listing before matching: under pipefail, `ls-tree | grep -q` fails open when grep's early
      # exit gives a large listing SIGPIPE.
      modes="$(git -C "$dir" --literal-pathspecs ls-tree -r --format='%(objectmode)' "$tree" -- "$prefix/")" \
        || { echo "target directory cannot be listed: $prefix"; return 1; }
      if grep -qE '^(120000|160000)$' <<<"$modes"; then
        echo "target directory contains a symlink or submodule: $prefix"; return 1
      fi;;
    '') echo "target does not exist: $prefix"; return 1;;
    *) echo "target is neither a regular file nor a directory: $prefix"; return 1;;
  esac
  printf '%s\n' "$prefix"
}

# policy_index DIR TREEISH [LINKS_FILE] -> NUL-separated `git update-index -z --index-info` records of TREEISH's
# policy, from one walk of TREEISH. Each policy symlink is replaced by its target's blobs placed under the link
# path, so restored policy is base content wherever the link pointed; LINKS_FILE, when given, receives the
# NUL-separated LINK TARGET pairs. Dies on a symlink RC11 does not admit, so a caller that must stop on refusal
# runs it in the current shell, not a process substitution, before anything is restored.
policy_index() {
  local entry p oid target listing i LC_ALL=C
  local -a links=() targets=()
  listing="$(tree_listing "$1" "$2")" || exit "$?"
  # shellcheck disable=SC2094 # Unlinking the open listing is deliberate: a die mid-walk leaves nothing behind.
  {
    rm -f "$listing"
    while IFS= read -r -d '' entry; do
      p="${entry#*$'\t'}"
      if [ "${entry%% *}" = 120000 ] && policy_link_selected "$p"; then
        oid="${entry%%$'\t'*}"; oid="${oid##* }"
        target="$(policy_link_target "$1" "$2" "$p" "$oid")" \
          || die 1 "base reviewer policy symlink must name a file or directory inside the base tree: $p ($target)"
        links+=("$p"); targets+=("$target")
      elif adapter_is_policy_path "$p"; then
        printf '%s\0' "$entry"
      fi
    done
  } < "$listing"
  [ -z "${3:-}" ] || : > "$3"
  [ "${#links[@]}" -gt 0 ] || return 0
  for i in "${!links[@]}"; do
    [ -z "${3:-}" ] || printf '%s\0%s\0' "${links[$i]}" "${targets[$i]}" >> "$3"
    while IFS= read -r -d '' entry; do
      p="${entry#*$'\t'}"
      if [ "$p" = "${targets[$i]}" ]; then p="${links[$i]}"; else p="${links[$i]}/${p#"${targets[$i]}"/}"; fi
      printf '%s\t%s\0' "${entry%%$'\t'*}" "$p"
    done < <(git -C "$1" --literal-pathspecs ls-tree -r -z "$2" -- "${targets[$i]}")
  done
}

# restored_policy_paths DIR TREEISH -> NUL-separated paths that policy restoration writes from TREEISH.
# Inside context_paths_json it reads the index that call already built for the same DIR and TREEISH, so the
# adapter's selection does not walk the tree a second time.
restored_policy_paths() {
  local entry
  if [ -n "${_REVIEW_PR_INDEX_FILE:-}" ] && [ "$1" = "$_REVIEW_PR_INDEX_DIR" ] && [ "$2" = "$_REVIEW_PR_INDEX_TREE" ]; then
    while IFS= read -r -d '' entry; do printf '%s\0' "${entry#*$'\t'}"; done < "$_REVIEW_PR_INDEX_FILE"
    return 0
  fi
  while IFS= read -r -d '' entry; do printf '%s\0' "${entry#*$'\t'}"; done < <(policy_index "$1" "$2")
}

# nul_paths_json -> JSON array of the NUL-separated paths on stdin, in input order.
# Dies on a path that is not valid UTF-8 (RC11): jq -R replaces such bytes with U+FFFD, so the array would name a
# different file, and two such paths could become one entry. The check is that the JSON decodes back to the input
# bytes exactly, which is the property callers rely on; iconv is not used because macOS iconv accepts sequences
# above U+10FFFF that jq replaces.
nul_paths_json() {
  local paths json p bad=""
  paths="$(mktemp "${TMPDIR:-/tmp}/review-pr-paths.XXXXXX")" || die 1 "cannot create a temporary file"
  cat > "$paths"
  json="$(jq -Rs -c 'split("\u0000") | map(select(length > 0))' < "$paths")" || { rm -f "$paths"; die 1 "jq failed"; }
  if ! printf '%s' "$json" | jq -j '.[] | . + "\u0000"' | cmp -s - "$paths"; then
    while IFS= read -r -d '' p; do
      [ "$(printf '%s' "$p" | jq -Rs -j . && printf x)" = "${p}x" ] || { bad="$p"; break; }
    done < "$paths"
    rm -f "$paths"
    [ -z "$bad" ] || die 1 "policy path is not valid UTF-8: $(printf '%q' "$bad")"
    die 1 "policy paths do not round-trip through JSON"
  fi
  rm -f "$paths"
  printf '%s\n' "$json"
}

# policy_selection_json DIR TREEISH -> JSON array of {path, oid, mandatory}: the adapter-selected passive policy
# paths, one per base source and sorted by byte order (RC8), each with the base blob restored there. The base source
# of a path restored under a policy symlink is its path under the link target; any other path is its own source.
# Sources and blobs come from the base tree alone, never from the head. An entry is a skill (mandatory false) only
# when every selected path that reaches its source is one, so a file selected as policy under any name stays policy.
# Paths are validated by nul_paths_json first, so jq sees exact UTF-8 and its string order is byte order; grouping
# is O(n log n), each destination looking up its own ancestors in the link map rather than scanning entries.
policy_selection_json() {
  local work r p entry LC_ALL=C
  work="$(mktemp -d "${TMPDIR:-/tmp}/review-pr-context.XXXXXX")" || die 1 "cannot create a temporary directory"
  # Both run in this shell, not a process substitution, so a refusal or selector failure stops here.
  policy_index "$1" "$2" "$work/links" > "$work/records"
  local _REVIEW_PR_INDEX_FILE="$work/records" _REVIEW_PR_INDEX_DIR="$1" _REVIEW_PR_INDEX_TREE="$2"
  adapter_context_paths "$1" "$2" > "$work/selected" || { rm -rf "$work"; die 1 "adapter_context_paths failed"; }
  _REVIEW_PR_INDEX_FILE=""
  : > "$work/remove"; : > "$work/skills"; : > "$work/blobs"
  if [ "${#ADAPTER_ALWAYS_REMOVE[@]}" -gt 0 ]; then
    for r in "${ADAPTER_ALWAYS_REMOVE[@]}"; do printf '%s\0' "$r" >> "$work/remove"; done
  fi
  while IFS= read -r -d '' p; do if adapter_is_skill_path "$p"; then printf '%s\0' "$p" >> "$work/skills"; fi; done < "$work/selected"
  # Records are `MODE TYPE OID<TAB>PATH`; the pairs file maps each restored path to its base blob.
  while IFS= read -r -d '' entry; do
    p="${entry#*$'\t'}"; entry="${entry%%$'\t'*}"; printf '%s\0%s\0' "$p" "${entry##* }" >> "$work/blobs"
  done < "$work/records"
  nul_paths_json < "$work/selected" > "$work/selected.json"
  nul_paths_json < "$work/links" > "$work/links.json"
  nul_paths_json < "$work/remove" > "$work/remove.json"
  nul_paths_json < "$work/skills" > "$work/skills.json"
  nul_paths_json < "$work/blobs" > "$work/blobs.json"
  # A destination equal to its source represents it; otherwise the first alias in byte order does.
  jq -n -c --slurpfile sel "$work/selected.json" --slurpfile links "$work/links.json" --slurpfile rm "$work/remove.json" \
    --slurpfile skills "$work/skills.json" --slurpfile blobs "$work/blobs.json" '
    def pairs($a): [range(0; $a | length; 2) | {key: $a[.], value: $a[. + 1]}] | from_entries;
    pairs($links[0]) as $map
    | pairs($blobs[0]) as $oid
    | ($skills[0] | map({key: ., value: true}) | from_entries) as $skill
    | [ $sel[0][] as $d
        | select(all($rm[0][]; . as $r | $d != $r and ($d | startswith($r + "/") | not)))
        | ($d | split("/")) as $c
        | (first(range($c | length; 0; -1) as $n | ($c[:$n] | join("/")) | select($map[.] != null)) // null) as $link
        | {dest: $d, src: (if $link == null then $d else $map[$link] + $d[($link | length):] end), skill: ($skill[$d] == true)} ]
    | group_by(.src)
    | map(((map(select(.dest == .src)) | first) // min_by(.dest)) as $rep
          | {path: $rep.dest, oid: $oid[$rep.dest], mandatory: any(.[]; .skill | not)})
    | sort_by(.path)
  ' || { rm -rf "$work"; die 1 "cannot build the policy manifest"; }
  rm -rf "$work"
}

# context_paths_json DIR TREEISH -> JSON array of the paths policy_selection_json selects, skills included.
context_paths_json() {
  local selection
  selection="$(policy_selection_json "$1" "$2")" || exit "$?"
  jq -c 'map(.path)' <<<"$selection"
}

# json_string_exact FILE -> the JSON string of FILE's bytes, or failure when JSON cannot carry them exactly (bytes
# that are not valid UTF-8, which jq would replace with U+FFFD).
json_string_exact() {
  local json
  json="$(jq -Rs . < "$1")" || return 1
  printf '%s' "$json" | jq -j . | cmp -s - "$1" || return 1
  printf '%s\n' "$json"
}

# skill_frontmatter_json DIR OID -> {"name","description"} from the base blob OID of a SKILL.md, or failure.
# The grammar is deliberately narrow (RC8): a leading `---` fence closed by `---`; top-level `key: value` lines,
# comment lines, and indented continuation lines; `name` a single-line plain or quoted scalar; `description` a
# plain scalar with indented continuation lines, a single-line quoted scalar, or a `>`/`|` block scalar. Other keys
# and their indented children are skipped. Anything else, a duplicate or missing name or description, a double-quoted
# escape, or a description over 1024 characters fails, and the caller lists that skill as a mandatory read instead.
skill_frontmatter_json() {
  local work name desc
  work="$(mktemp -d "${TMPDIR:-/tmp}/review-pr-skill.XXXXXX")" || die 1 "cannot create a temporary directory"
  git -C "$1" cat-file blob "$2" > "$work/skill" 2>/dev/null || { rm -rf "$work"; return 1; }
  # shellcheck disable=SC2016 # awk program, not shell expansions.
  if ! LC_ALL=C awk -v out_name="$work/name" -v out_desc="$work/desc" '
    function fail(code) { err = code; exit }
    function unquote(v,   inner) {
      if (v ~ /^'\''/) {
        if (v !~ /'\''$/ || length(v) < 2) fail(3)
        v = substr(v, 2, length(v) - 2)
        # Inside single quotes only a doubled quote may appear.
        inner = v; gsub(/'\'''\''/, "", inner)
        if (index(inner, "'\''")) fail(3)
        gsub(/'\'''\''/, "'\''", v); return v
      }
      if (v ~ /^"/) {
        if (v !~ /"$/ || length(v) < 2) fail(3)
        v = substr(v, 2, length(v) - 2)
        if (index(v, "\\") || index(v, "\"")) fail(3)
        return v
      }
      sub(/[ \t]+#.*$/, "", v)
      # A plain scalar may not open with a YAML indicator: a flow collection, anchor, alias, tag, block or quote
      # character, directive or reserved character, or a sequence, complex-key or mapping marker before a space.
      if (v ~ /^[][{}&*!|>'\''"%@`,#]/ || v ~ /^[-?:]([ \t]|$)/) fail(3)
      return v
    }
    NR == 1 { if ($0 != "---") fail(2); next }
    $0 == "---" { closed = 1; exit }
    {
      line = $0
      if (line ~ /^[ \t]/ || line == "") {
        if (cur == "name") { if (line != "") fail(3); next }
        if (cur != "description") next
        if (mode == "plain") {
          sub(/^[ \t]+/, "", line)
          if (line == "") next
          # An indented collection is not a continuation: a sequence entry, a mapping key, or (opening the scalar)
          # any indicator unquote() would reject on the key line.
          if (line ~ /^[-?:]([ \t]|$)/ || line ~ /^[^ \t#][^:]*:([ \t]|$)/) fail(3)
          if (desc == "" && line ~ /^[][{}&*!|>'\''"%@`,#]/) fail(3)
          desc = desc (desc == "" ? "" : " ") line; next
        }
        if (mode == "folded" || mode == "literal") {
          if (line == "") { blank++; next }
          # YAML indents with spaces only, and no block line may sit left of the first one.
          match(line, /^[ \t]*/)
          if (index(substr(line, 1, RLENGTH), "\t")) fail(3)
          if (indent == "") indent = RLENGTH
          if (RLENGTH < indent) fail(3)
          line = substr(line, indent + 1)
          if (desc != "") desc = desc (mode == "literal" ? "\n" : (blank ? "\n" : " "))
          while (blank-- > 1) desc = desc "\n"
          blank = 0; desc = desc line; next
        }
        # A quoted scalar closed on its key line: a blank line after it is skipped, an indented line is not.
        if (mode == "quoted" && line == "") next
        fail(3)
      }
      if (line ~ /^#/) { cur = ""; next }
      if (!match(line, /^[A-Za-z0-9_-]+:([ \t]|$)/)) fail(3)
      key = substr(line, 1, index(line, ":") - 1); val = substr(line, index(line, ":") + 1)
      sub(/^[ \t]+/, "", val); sub(/[ \t]+$/, "", val)
      cur = key
      if (key == "name") { if (seen[key]++) fail(3); name = unquote(val); next }
      if (key == "description") {
        if (seen[key]++) fail(3)
        if (val ~ /^[>|][-+]?$/) { mode = (val ~ /^>/) ? "folded" : "literal"; indent = ""; blank = 0; desc = ""; next }
        if (val ~ /^['\''"]/) { mode = "quoted"; desc = unquote(val); next }
        mode = "plain"; desc = unquote(val); next
      }
      cur = "other"
    }
    END {
      if (err) exit err
      if (!closed || name == "" || !seen["description"] || desc == "") exit 4
      printf "%s", name > out_name; printf "%s", desc > out_desc
    }
  ' "$work/skill"; then rm -rf "$work"; return 1; fi
  if ! name="$(json_string_exact "$work/name")" || ! desc="$(json_string_exact "$work/desc")"; then rm -rf "$work"; return 1; fi
  rm -rf "$work"
  jq -n -c --argjson name "$name" --argjson desc "$desc" \
    'if ($name | length) > 64 or ($desc | length) > 1024 then error("too long") else {name: $name, description: $desc} end' \
    2>/dev/null
}

# policy_manifest_json DIR TREEISH -> the policy-manifest.json object (RC8): {"version": 2, "policy_files": [...],
# "skills": [{"path", "name", "description"}, ...]}, both lists sorted by path. A selected skill whose frontmatter
# skill_frontmatter_json cannot read is listed in policy_files, so its body stays a mandatory read.
# FALLBACK_FILE, when given, receives how many skills were listed in policy_files because their frontmatter could not
# be read. Paths never leave JSON: each skill is addressed by its index, so no shell decoding can alter one.
policy_manifest_json() {
  local selection i n oid meta fallback=0 metas='{}'
  selection="$(policy_selection_json "$1" "$2")" || exit "$?"
  n="$(jq length <<<"$selection")"
  for ((i = 0; i < n; i++)); do
    [ "$(jq -r --argjson i "$i" '.[$i].mandatory' <<<"$selection")" = false ] || continue
    oid="$(jq -r --argjson i "$i" '.[$i].oid' <<<"$selection")"
    if meta="$(skill_frontmatter_json "$1" "$oid")"; then
      metas="$(jq -c --arg i "$i" --argjson m "$meta" '. + {($i): $m}' <<<"$metas")"
    else
      fallback=$((fallback + 1))
    fi
  done
  [ -z "${3:-}" ] || printf '%s\n' "$fallback" > "$3"
  jq -c --argjson metas "$metas" '
    to_entries
    | {version: 2,
       policy_files: ([.[] | select($metas[.key | tostring] == null) | .value.path] | sort),
       skills: ([.[] | select($metas[.key | tostring] != null) | {path: .value.path} + $metas[.key | tostring]] | sort_by(.path))}
  ' <<<"$selection"
}

# write_policy_manifest DIR TREEISH OUTPUT -> writes the manifest and enforces RC9's bounds, so checkout-pr.sh and the
# lens collector prepare the same artifact.
write_policy_manifest() {
  local manifest max_files="${REVIEW_PR_MAX_POLICY_FILES:-40}" max_skills="${REVIEW_PR_MAX_SKILL_INDEX:-200}" n_files n_skills n_fallback fallback_file
  [[ "$max_files" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_POLICY_FILES must be a non-negative integer, got '$max_files'"
  [[ "$max_skills" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_SKILL_INDEX must be a non-negative integer, got '$max_skills'"
  fallback_file="$(mktemp "${TMPDIR:-/tmp}/review-pr-fallback.XXXXXX")" || die 1 "cannot create a temporary file"
  manifest="$(policy_manifest_json "$1" "$2" "$fallback_file")" || { rm -f "$fallback_file"; exit 1; }
  n_fallback="$(cat "$fallback_file")"; rm -f "$fallback_file"
  n_files="$(jq '.policy_files | length' <<<"$manifest")"
  n_skills="$(jq '.skills | length' <<<"$manifest")"
  [ "$n_files" -le "$max_files" ] \
    || die 1 "base policy manifest has $n_files files, exceeding REVIEW_PR_MAX_POLICY_FILES=$max_files ($n_fallback of them skills whose frontmatter could not be read)"
  [ "$n_skills" -le "$max_skills" ] \
    || die 1 "base skill index has $n_skills skills, exceeding REVIEW_PR_MAX_SKILL_INDEX=$max_skills"
  printf '%s\n' "$manifest" > "$3"
}

# ensure_merge_base CLONE BASE_SHA HEAD_SHA PULL_REF
# Deepens until the merge base is present. Every fetch names PULL_REF as well as the configured
# refspec: without it, `git fetch --deepen origin` follows only refs/heads/* and never deepens the
# PR-only lineage (tests/deepen-test.sh), so only --unshallow would ever recover.
ensure_merge_base() {
  local clone="$1" base="$2" head="$3" pull="$4"
  have() { git -C "$clone" cat-file -e "$base^{commit}" 2>/dev/null && git -C "$clone" merge-base "$base" "$head" >/dev/null 2>&1; }
  have && return 0
  git -C "$clone" fetch --quiet origin "$base" 2>/dev/null || true
  for _ in 1 2 3; do have && return 0; git -C "$clone" fetch --quiet --deepen=200 origin "$pull" || true; done
  have && return 0
  git -C "$clone" fetch --quiet --unshallow origin "$pull" || true
  have
}

# Refuse to delete anything that is not a directory this tool created.
scratch_guard() { # scratch_guard DIR
  local d="$1"
  [ -n "${REVIEW_PR_SCRATCH:-}" ] || die 1 "REVIEW_PR_SCRATCH unset during cleanup"
  case "$d" in "$REVIEW_PR_SCRATCH"/*) ;; *) die 1 "refusing to remove '$d': outside REVIEW_PR_SCRATCH";; esac
  [ -f "$d/.review-pr" ] || die 1 "refusing to remove '$d': no .review-pr marker"
}
