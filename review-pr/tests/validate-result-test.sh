#!/usr/bin/env bash
# Offline: validate-result.sh implements the R5.6 contract check (R5.7).
set -euo pipefail
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
V="$SRC/validate-result.sh"

check() { # check NAME EXPECT_VALID EXPECT_DIFF_UNAVAILABLE <<< result
  local name="$1" want_valid="$2" want_du="$3" out
  out="$("$V")" || { echo "FAIL [$name]: validator exited non-zero"; FAIL=1; return; }
  jq -e . >/dev/null <<<"$out" || { echo "FAIL [$name]: not JSON: $out"; FAIL=1; return; }
  [ "$(jq -r .schema_valid <<<"$out")" = "$want_valid" ] || { echo "FAIL [$name]: schema_valid=$(jq -c . <<<"$out")"; FAIL=1; }
  [ "$(jq -r .diff_unavailable <<<"$out")" = "$want_du" ] || { echo "FAIL [$name]: diff_unavailable=$(jq -c . <<<"$out")"; FAIL=1; }
  if [ "$want_valid" = true ]; then
    [ "$(jq -r '.schema_errors | length' <<<"$out")" = 0 ] || { echo "FAIL [$name]: errors on valid input: $out"; FAIL=1; }
  else
    [ "$(jq -r '.schema_errors | length' <<<"$out")" -gt 0 ] || { echo "FAIL [$name]: invalid input reported no errors"; FAIL=1; }
  fi
}

VALID='## Summary
Adds a port validator. One real bug, otherwise sound.

## Critical
- app/parse.py:12 — correctness — is_valid_port rejects 65535 — off-by-one excludes a legal port

## Important
(none)

## Suggestions
- app/parse.py:20 — tests — normalize_host trailing-dot branch has no test — a regression there would ship silently

## Strengths
- Small, focused diff

## Not reviewed
(none)'

check valid true false <<<"$VALID"
check valid-all-none true false <<<'## Summary
Docs only.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check sentinel true true <<<'## Summary
Could not read the diff.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
- DIFF-UNAVAILABLE: git diff pr-7-base...pr-7 was denied
- app/ not read'
check missing-heading false false <<<'## Summary
x

## Critical
(none)

## Important
(none)

## Strengths
(none)

## Not reviewed
(none)'
check duplicate-heading false false <<<"$VALID

## Critical
(none)"
check reordered false false <<<'## Summary
x

## Important
(none)

## Critical
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check extra-heading false false <<<"$VALID

## Extra
stuff"
check text-before-summary false false <<<"Here is my review.
$VALID"
check body-neither-none-nor-bullets false false <<<'## Summary
x

## Critical
Looks fine to me.

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check unknown-lens false false <<<'## Summary
x

## Critical
- app/parse.py:12 — style — foo — bar

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check no-path-line false false <<<'## Summary
x

## Critical
- parse.py — correctness — foo — bar

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check sentinel-misplaced false false <<<'## Summary
x

## Critical
- DIFF-UNAVAILABLE: nope

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
check sentinel-not-first false false <<<'## Summary
x

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
- app/ not read
- DIFF-UNAVAILABLE: nope'
check empty false false <<<''

[ "$FAIL" = 0 ] && echo "validate-result-test: OK"
exit "$FAIL"
