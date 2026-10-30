#!/usr/bin/env bash
# Offline: validate-result.sh implements the output contract in review-lens.md.
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
Lenses checked: correctness, silent-failure, tests, comments.
Adds a port validator. One real bug, otherwise sound.

## Changes
Adds is_valid_port to app/parse.py.

## Critical
- app/parse port.py:12 — correctness — Port 65535 rejected — is_valid_port uses < 65535 — Legal port 65535 cannot be configured

## Important
(none)

## Suggestions
- app/parse.py:20 — tests — Trailing dot untested — normalize_host trailing-dot branch has no test — A regression there would ship silently

## Not reviewed
(none)'

check valid true false <<<"$VALID"
# A finding about the pull-request description cites the exact location token `PR body`.
SUGGESTION='- app/parse.py:20 — tests — Trailing dot untested — normalize_host trailing-dot branch has no test — A regression there would ship silently'
PR_BODY_BULLET='- PR body — correctness — Dev Tables missing — The description lacks the section AGENTS.md requires — Reviewers cannot check the tables'
check pr-body-location true false <<<"${VALID/"$SUGGESTION"/"$PR_BODY_BULLET"}"
for bad in 'PR body [base]' 'pr body' 'PR-body' ' PR body' 'PR body:'; do
  check "pr-body-variant:$bad" false false <<<"${VALID/"$SUGGESTION"/"${PR_BODY_BULLET/PR body/$bad}"}"
done
check missing-coverage false false <<<"$(sed '/^Lenses checked:/d' <<<"$VALID")"
check marker-only-summary false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
missing_lens="$(mktemp)"
printf '%s\n' 'No coverage marker here.' > "$missing_lens"
[ "$(REVIEW_PR_LENS="$missing_lens" "$V" </dev/null | jq -r .schema_errors[0])" = 'review lens has no lenses-checked line' ] \
  || { echo "FAIL: missing lens marker is not reported"; FAIL=1; }
rm -f "$missing_lens"
check valid-all-none true false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
Docs only.

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check sentinel true true <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
Could not read the diff.

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Not reviewed
- DIFF-UNAVAILABLE: the pinned diff file was unreadable
- app/ not read'
check missing-heading false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Important
(none)

## Not reviewed
(none)'
check duplicate-heading false false <<<"$VALID

## Critical
(none)"
check reordered false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Important
(none)

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check extra-heading false false <<<"$VALID

## Extra
stuff"
check text-before-summary false false <<<"Here is my review.
$VALID"
check body-neither-none-nor-bullets false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
Looks fine to me.

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check unknown-lens false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
- app/parse.py:12 — style — foo — bar — baz

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check no-path-line false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
- parse.py — correctness — foo — bar — baz

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check sentinel-misplaced false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
- DIFF-UNAVAILABLE: nope

## Important
(none)

## Suggestions
(none)

## Not reviewed
(none)'
check sentinel-not-first false false <<<'## Summary
Lenses checked: correctness, silent-failure, tests, comments.
x

## Changes
Adds is_valid_port to app/parse.py.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Not reviewed
- app/ not read
- DIFF-UNAVAILABLE: nope'
# Malformed report text must remain valid JSON even when diagnostics quote it.
critical_heading='## Critical'
important_section=$'## Important\n(none)'
check backslash-heading false false <<<"${VALID/"$critical_heading"/## Crit\\ical}"
check tab-heading false false <<<"${VALID/"$critical_heading"/$'## Crit\tical'}"
check quoted-heading false false <<<"${VALID/"$critical_heading"/## \"Critical\"}"
check none-before-bullet false false <<<"${VALID/"$important_section"/## Important$'\n'(none)$'\n'- app.py:1 — correctness — Bad — bad — breaks}"
check none-after-bullet false false <<<"${VALID/"$important_section"/## Important$'\n'- app.py:1 — correctness — Bad — bad — breaks$'\n'(none)}"
check duplicate-none false false <<<"${VALID/"$important_section"/## Important$'\n'(none)$'\n'(none)}"
check prose-em-dash true false <<<"${VALID/uses < 65535/uses < 65535 — and more}"
check blank-impact false false <<<"${VALID/Legal port 65535 cannot be configured/   }"
check zero-line false false <<<"${VALID/parse port.py:12/parse port.py:0}"
check deleted-file true false <<<"${VALID/parse port.py:12/parse port.py:12 [base]}"
check invalid-side false false <<<"${VALID/parse port.py:12/parse port.py:12 [head]}"

FIX_BULLET='- app/parse port.py:12 — correctness — Port 65535 rejected — is_valid_port uses < 65535 — Legal port 65535 cannot be configured'
BUG="$FIX_BULLET"
withbug() { printf '%s' "${VALID/"$BUG"/"$1"}"; }
check five-field true false <<<"$VALID"
check six-field-fix true false <<<"$(withbug "$BUG — Fix: Restore the bit")"
check defect-with-dashes-and-fix-text false false <<<"$(withbug '- a.py:1 — tests — T — one — Fix: x — more — plain impact')"
check impact-starting-fixing true false <<<"$(withbug '- a.py:1 — tests — T — defect — Fixing this restores startup')"
check four-field false false <<<"$(withbug '- a.py:1 — tests — T — defect')"
check fix-then-dash-text false false <<<"$(withbug '- a.py:1 — correctness — Title — defect — impact — Fix: Do A — then B')"
check fix-two-spaces false false <<<"$(withbug '- a.py:1 — tests — T — defect — impact — Fix:  Do A')"
check fix-no-space false false <<<"$(withbug '- a.py:1 — tests — T — defect — impact — Fix:Do A')"
check fix-tab false false <<<"$(withbug "- a.py:1 — tests — T — defect — impact — Fix:$(printf '\t')x")"
check blank-fix false false <<<"$(withbug "$BUG — Fix: ")"
check fix-without-impact false false <<<"$(withbug '- a.py:1 — tests — T — defect — Fix: x')"
check strengths-present false false <<<"${VALID/"## Not reviewed"/"## Strengths
- Small

## Not reviewed"}"
check changes-missing false false <<<"$(awk '/^## Changes/{skip=1;next} /^## Critical/{skip=0} !skip' <<<"$VALID")"
check changes-none false false <<<"${VALID/"Adds is_valid_port to app/parse.py."/(none)}"
check changes-blank false false <<<"${VALID/"Adds is_valid_port to app/parse.py."/   }"
check changes-sentinel false false <<<"${VALID/"Adds is_valid_port to app/parse.py."/DIFF-UNAVAILABLE: x}"
check empty false false <<<''

[ "$FAIL" = 0 ] && echo "validate-result-test: OK"
exit "$FAIL"
