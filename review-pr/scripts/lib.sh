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

# R6.3: refuse to delete anything that is not a directory this tool created.
scratch_guard() { # scratch_guard DIR
  local d="$1"
  [ -n "${REVIEW_PR_SCRATCH:-}" ] || die 1 "REVIEW_PR_SCRATCH unset during cleanup"
  case "$d" in "$REVIEW_PR_SCRATCH"/*) ;; *) die 1 "refusing to remove '$d': outside REVIEW_PR_SCRATCH";; esac
  [ -f "$d/.review-pr" ] || die 1 "refusing to remove '$d': no .review-pr marker"
}
