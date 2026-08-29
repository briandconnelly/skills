#!/usr/bin/env bash
# Offline: input validation, adapter selection, and prerequisite errors.
set -euo pipefail
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
export REVIEW_PR_SCRATCH="$S"

expect_exit() { # expect_exit CODE PATTERN -- cmd...
  local code="$1" pat="$2"; shift 2
  local out rc=0
  out="$("$@" 2>&1 >/dev/null)" || rc=$?
  [ "$rc" = "$code" ] || { echo "FAIL: '$*' exit $rc, want $code"; FAIL=1; }
  grep -q -- "$pat" <<<"$out" || { echo "FAIL: '$*' stderr lacks '$pat': $out"; FAIL=1; }
}

# Input errors.
expect_exit 2 'usage' "$SRC/checkout-pr.sh"
expect_exit 2 'usage' "$SRC/checkout-pr.sh" 'owner/repo'
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'not-a-slug' 12
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'own er/repo' 12
expect_exit 2 'positive integer' "$SRC/checkout-pr.sh" 'owner/repo' 0
expect_exit 2 'positive integer' "$SRC/checkout-pr.sh" 'owner/repo' 12x
expect_exit 2 'REVIEW_PR_SCRATCH' env -u REVIEW_PR_SCRATCH "$SRC/checkout-pr.sh" 'owner/repo' 12
expect_exit 2 'REVIEW_PR_MAX_POLICY_FILES' env REVIEW_PR_SCRATCH="$S" REVIEW_PR_MAX_POLICY_FILES=bad "$SRC/checkout-pr.sh" 'owner/repo' 12
# Host validation also rejects a URL passed directly to the script.
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'https://gitlab.com/o/r' 12

# Missing generic prerequisites have distinct errors.
FAKEBIN="$S/bin"; mkdir -p "$FAKEBIN"
for c in git jq bash dirname grep; do ln -s "$(command -v "$c")" "$FAKEBIN/$c"; done
expect_exit 3 'missing required command: gh' env PATH="$FAKEBIN" "$SRC/checkout-pr.sh" 'owner/repo' 12

# Unsupported adapters fail before network access.
expect_exit 3 'unsupported review runner: missing' env REVIEW_PR_RUNNER=missing PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/checkout-pr.sh" 'owner/repo' 12

# Claude prerequisites belong to the Claude adapter and are checked by the wrapper.
printf '#!/usr/bin/env bash\necho "2.1.250 (Claude Code)"\n' > "$FAKEBIN/claude"; chmod +x "$FAKEBIN/claude"
printf '#!/usr/bin/env bash\nexit 0\n' > "$FAKEBIN/gh"; chmod +x "$FAKEBIN/gh"
expect_exit 3 'Claude Code 2.1.251 or newer' env PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/review-pr.sh" 'owner/repo' 12

# A passing version gets past the adapter gate.
printf '#!/usr/bin/env bash\necho "2.1.251 (Claude Code)"\n' > "$FAKEBIN/claude"
rc=0; out="$(env PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/review-pr.sh" 'owner/repo' 12 2>&1 >/dev/null)" || rc=$?
grep -q 'Claude Code 2.1.251 or newer' <<<"$out" && { echo "FAIL: version gate rejected 2.1.251"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "validate-test: OK"
exit "$FAIL"
