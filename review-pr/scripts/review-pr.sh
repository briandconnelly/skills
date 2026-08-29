#!/usr/bin/env bash
# review-pr.sh OWNER/REPO N [LEVEL]
# Implements the calling-session procedure in SKILL.md.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

[ "$#" -ge 2 ] && [ "$#" -le 3 ] || die 2 "usage: review-pr.sh OWNER/REPO N [LEVEL]"
SLUG="$1"
N="$2"
LEVEL="${3:-}"
validate_ref "$SLUG" "$N"

RUNNER="${REVIEW_PR_RUNNER:-claude}"
load_adapter "$RUNNER"
adapter_check

REVIEW_PR_SCRATCH="${REVIEW_PR_SCRATCH:-${TMPDIR:-/tmp}}"
mkdir -p "$REVIEW_PR_SCRATCH"
REVIEW_PR_SCRATCH="$(cd -- "$REVIEW_PR_SCRATCH" >/dev/null 2>&1 && pwd -P)" \
  || die 2 "REVIEW_PR_SCRATCH is not an accessible directory"
export REVIEW_PR_SCRATCH REVIEW_PR_RUNNER="$RUNNER"

JOB=""
cleanup() {
  local rc=$?
  if [ -n "$JOB" ] && [ -d "$JOB" ] && ! keep_requested; then
    scratch_guard "$JOB" && rm -rf "$JOB"
  fi
  exit "$rc"
}
trap cleanup EXIT

CHECKOUT="$("$HERE/checkout-pr.sh" "$SLUG" "$N")"
JOB="$(jq -er .dir <<<"$CHECKOUT")"
printf '%s' "$CHECKOUT" | "$HERE/run-child.sh" "$LEVEL"
