#!/usr/bin/env bash
# Offline: input validation and prerequisite errors for checkout-pr.sh (R1.2, R1.3, R7.1, R7.2).
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

# R1.2 usage errors
expect_exit 2 'usage' "$SRC/checkout-pr.sh"
expect_exit 2 'usage' "$SRC/checkout-pr.sh" 'owner/repo'
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'not-a-slug' 12
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'own er/repo' 12
expect_exit 2 'positive integer' "$SRC/checkout-pr.sh" 'owner/repo' 0
expect_exit 2 'positive integer' "$SRC/checkout-pr.sh" 'owner/repo' 12x
expect_exit 2 'REVIEW_PR_SCRATCH' env -u REVIEW_PR_SCRATCH "$SRC/checkout-pr.sh" 'owner/repo' 12
# R1.3 host check happens in SKILL.md parsing, but a URL passed through must be rejected
expect_exit 2 'OWNER/REPO' "$SRC/checkout-pr.sh" 'https://gitlab.com/o/r' 12

# R7.1 missing command -> exit 3, distinct message
FAKEBIN="$S/bin"; mkdir -p "$FAKEBIN"
for c in git jq; do ln -s "$(command -v $c)" "$FAKEBIN/$c"; done
expect_exit 3 'missing required command: gh' env PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/checkout-pr.sh" 'owner/repo' 12

# R7.2 old claude -> exit 3
printf '#!/usr/bin/env bash\necho "2.1.200 (Claude Code)"\n' > "$FAKEBIN/claude"; chmod +x "$FAKEBIN/claude"
printf '#!/usr/bin/env bash\nexit 0\n' > "$FAKEBIN/gh"; chmod +x "$FAKEBIN/gh"
expect_exit 3 'Claude Code 2.1.247 or newer' env PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/checkout-pr.sh" 'owner/repo' 12

# Known positive for the instrument: a passing version must get past the version gate.
printf '#!/usr/bin/env bash\necho "2.1.247 (Claude Code)"\n' > "$FAKEBIN/claude"
rc=0; out="$(env PATH="$FAKEBIN:/usr/bin:/bin" "$SRC/checkout-pr.sh" 'owner/repo' 12 2>&1 >/dev/null)" || rc=$?
grep -q 'Claude Code 2.1.247 or newer' <<<"$out" && { echo "FAIL: version gate rejected 2.1.247"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "validate-test: OK"
exit "$FAIL"
