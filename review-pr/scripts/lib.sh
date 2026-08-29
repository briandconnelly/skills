#!/usr/bin/env bash
# Shared helpers for review-pr scripts. Sourced, not executed.
# Exit codes: 0 ok, 1 tool failure, 2 usage, 3 prerequisite (spec: Components).

die() { # die CODE MESSAGE...
  local code="$1"; shift
  printf 'review-pr: %s\n' "$*" >&2
  exit "$code"
}

need_cmd() { command -v "$1" >/dev/null 2>&1 || die 3 "missing required command: $1"; }

# R1.2
validate_ref() { # validate_ref OWNER/REPO N
  local slug="$1" n="$2"
  [[ "$slug" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die 2 "first argument must be OWNER/REPO, got '$slug'"
  [[ "$n" =~ ^[1-9][0-9]*$ ]] || die 2 "PR number must be a positive integer, got '$n'"
}

# R7.2
check_claude_version() {
  local v
  v="$(claude --version 2>/dev/null | awk '{print $1}')" || die 3 "cannot run 'claude --version'"
  local want=2.1.247
  # sort -V puts the smaller version first; the floor must not sort after the found version.
  [ "$(printf '%s\n%s\n' "$want" "$v" | sort -V | head -1)" = "$want" ] \
    || die 3 "Claude Code $want or newer is required, found $v"
}

# R6.1/R6.2: only the exact value 1 keeps the scratch directory.
keep_requested() { [ "${REVIEW_PR_KEEP:-}" = 1 ]; }

# R2.2/R3.1: working-tree checkouts of untrusted content run without the caller's global or
# system git config, so a PR-supplied .gitattributes cannot select a configured filter driver
# (smudge/process, e.g. git-lfs). The repo-local config of a fresh clone is ours, so it stays.
# GIT_CONFIG_PARAMETERS and GIT_CONFIG_COUNT (with GIT_CONFIG_KEY_n/VALUE_n) inject config through the
# environment and would survive the file overrides, so they are unset too.
git_wt() {
  env -u GIT_CONFIG_PARAMETERS -u GIT_CONFIG_COUNT -u GIT_CONFIG \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 git "$@"
}

# R3.1: reviewer policy paths. Root-only entries, and basenames matched at any depth.
# shellcheck disable=SC2034  # used by isolate-policy.sh
POLICY_ROOT=(.claude .mcp.json)
POLICY_RE='(^|/)(CLAUDE\.md|CLAUDE\.local\.md|AGENTS\.md)$|^\.claude/|^\.mcp\.json$'

# is_policy_path PATH — bash regex match on the whole path; a newline inside a directory name
# is an ordinary character here, never a separator.
is_policy_path() { [[ "$1" =~ $POLICY_RE ]]; }

# policy_paths DIR TREEISH -> NUL-separated tracked policy paths at TREEISH (may be empty).
# Paths stay NUL-delimited end to end (ls-tree -z), so names containing newlines or tabs are
# neither split nor quoted.
policy_paths() {
  local p
  while IFS= read -r -d '' p; do is_policy_path "$p" && printf '%s\0' "$p"; done \
    < <(git -C "$1" ls-tree -r -z --name-only "$2")
}

# R2.3: ensure_merge_base CLONE BASE_SHA HEAD_SHA PULL_REF
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

# R6.3: refuse to delete anything that is not a directory this tool created.
scratch_guard() { # scratch_guard DIR
  local d="$1"
  [ -n "${REVIEW_PR_SCRATCH:-}" ] || die 1 "REVIEW_PR_SCRATCH unset during cleanup"
  case "$d" in "$REVIEW_PR_SCRATCH"/*) ;; *) die 1 "refusing to remove '$d': outside REVIEW_PR_SCRATCH";; esac
  [ -f "$d/.review-pr" ] || die 1 "refusing to remove '$d': no .review-pr marker"
}
