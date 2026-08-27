#!/usr/bin/env bash
# checkout-pr.sh OWNER/REPO N
# Pins a PR to SHAs, clones it into $REVIEW_PR_SCRATCH, isolates policy files, and prints one JSON object.
# Spec: docs/superpowers/specs/2026-08-27-review-pr-design.md (R1.2, R2, R3, R6.3, R7).
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

[ "$#" -eq 2 ] || die 2 "usage: checkout-pr.sh OWNER/REPO N"
SLUG="$1"; N="$2"
validate_ref "$SLUG" "$N"
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set to a writable directory"

for c in git jq gh claude; do need_cmd "$c"; done   # R7.1
check_claude_version                                 # R7.2

# Task 3 continues here.
echo "not implemented" >&2; exit 1
