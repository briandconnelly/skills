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
  unset -f adapter_check adapter_is_policy_path adapter_context_paths adapter_build_command adapter_normalize 2>/dev/null || true
  unset ADAPTER_POLICY_ROOTS ADAPTER_ALWAYS_REMOVE
  # shellcheck disable=SC1090
  . "$adapter_dir/$name.sh"
  declare -F adapter_check adapter_is_policy_path adapter_context_paths adapter_build_command adapter_normalize >/dev/null \
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

# policy_paths DIR TREEISH -> NUL-separated tracked policy paths at TREEISH (may be empty).
# Paths stay NUL-delimited end to end (ls-tree -z), so names containing newlines or tabs are
# neither split nor quoted.
policy_paths() {
  local p
  # if/fi, not `&&`: under pipefail a non-matching final path would otherwise fail the whole loop.
  while IFS= read -r -d '' p; do if adapter_is_policy_path "$p"; then printf '%s\0' "$p"; fi; done \
    < <(git -C "$1" ls-tree -r -z --name-only "$2")
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
  local dir="$1" tree="$2" link="$3" text part prefix="" mode
  local -a comps=() parts=()
  text="$(git -C "$dir" cat-file blob "$4")" || { echo "link text is unreadable"; return 1; }
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
      if git -C "$dir" --literal-pathspecs ls-tree -r --format='%(objectmode)' "$tree" -- "$prefix/" | grep -qE '^(120000|160000)$'; then
        echo "target directory contains a symlink or submodule: $prefix"; return 1
      fi;;
    '') echo "target does not exist: $prefix"; return 1;;
    *) echo "target is neither a regular file nor a directory: $prefix"; return 1;;
  esac
  printf '%s\n' "$prefix"
}

# policy_links DIR TREEISH -> NUL-separated LINK TARGET pairs, one per policy symlink in TREEISH.
# Dies on a symlink RC11 does not admit, so call it in the current shell, not a process substitution,
# before anything is restored.
policy_links() {
  local entry p oid target
  while IFS= read -r -d '' entry; do
    [ "${entry%% *}" = 120000 ] || continue
    p="${entry#*$'\t'}"
    policy_link_selected "$p" || continue
    oid="${entry%%$'\t'*}"; oid="${oid##* }"
    target="$(policy_link_target "$1" "$2" "$p" "$oid")" \
      || die 1 "base reviewer policy symlink must name a file or directory inside the base tree: $p ($target)"
    printf '%s\0%s\0' "$p" "$target"
  done < <(git -C "$1" ls-tree -r -z "$2")
}

# policy_index DIR TREEISH -> NUL-separated `git update-index -z --index-info` records of TREEISH's policy.
# Each policy symlink is replaced by its target's blobs placed under the link path, so restored policy is
# base content wherever the link pointed. Callers validate with policy_links first: a refusal here happens
# inside a process substitution and cannot stop the caller.
policy_index() {
  local entry p link target i
  local -a links=() targets=()
  while IFS= read -r -d '' link && IFS= read -r -d '' target; do
    links+=("$link"); targets+=("$target")
  done < <(policy_links "$1" "$2")
  while IFS= read -r -d '' entry; do
    p="${entry#*$'\t'}"
    if [ "${entry%% *}" = 120000 ] && policy_link_selected "$p"; then continue; fi
    if adapter_is_policy_path "$p"; then printf '%s\0' "$entry"; fi
  done < <(git -C "$1" ls-tree -r -z "$2")
  [ "${#links[@]}" -gt 0 ] || return 0
  for i in "${!links[@]}"; do
    while IFS= read -r -d '' entry; do
      p="${entry#*$'\t'}"
      if [ "$p" = "${targets[$i]}" ]; then p="${links[$i]}"; else p="${links[$i]}/${p#"${targets[$i]}"/}"; fi
      printf '%s\t%s\0' "${entry%%$'\t'*}" "$p"
    done < <(git -C "$1" --literal-pathspecs ls-tree -r -z "$2" -- "${targets[$i]}")
  done
}

# restored_policy_paths DIR TREEISH -> NUL-separated paths that policy restoration writes from TREEISH.
restored_policy_paths() {
  local entry
  while IFS= read -r -d '' entry; do printf '%s\0' "${entry#*$'\t'}"; done < <(policy_index "$1" "$2")
}

# context_paths_json DIR TREEISH -> JSON array of adapter-selected passive policy paths.
context_paths_json() {
  adapter_context_paths "$1" "$2" \
    | jq -Rs -c 'split("\u0000") | map(select(length > 0))'
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
