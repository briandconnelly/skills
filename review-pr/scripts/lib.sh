#!/usr/bin/env bash
# Shared helpers for review-pr scripts. Sourced, not executed.
# Exit codes: 0 ok, 1 tool failure, 2 usage, 3 prerequisite (spec: Components).

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
