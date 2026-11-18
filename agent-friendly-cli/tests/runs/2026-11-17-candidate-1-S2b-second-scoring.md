# Scenario 2b — second blind scoring of the candidate-1 control cell

- **Date:** 2026-11-17
- **Why:** the first scorer failed arm 3 on the first assertion although that arm reports no hang; a fresh scorer was given the same packet (same verbatim assertions, same unlabeled outputs) and asked to name the finding each verdict rests on.
- **Result:** the same 2/3 on the first assertion and 3/3 on the second.

| Arm | Assertion | First scorer | Second scorer | Second scorer's evidence |
| --- | --- | --- | --- | --- |
| S2b-withskill-1 | A1 | PASS | PASS | F5 (P2) '### F5 — P2 — Exit code `4` for `CONFIRMATION_REQUIRED` is undeclared'; positive note: 'With `< /dev/null` it did not hang.' P0 hypothetical in F6 (P2) concerns `clean`, not sync. |
| S2b-withskill-1 | A2 | PASS | PASS | F1 (P1): '`ls --json` mixes a banner, an update-check line, and a summary into stdout with the payload' |
| S2b-withskill-2 | A1 | PASS | PASS | F5 (P2) '### F5 — P2: exit `4` for `CONFIRMATION_REQUIRED` is undeclared'; credit: '`sync` with stdin closed did **not** hang'. Top severity is P1; no sync finding at P1. |
| S2b-withskill-2 | A2 | PASS | PASS | F1 (P1): '`ls --json` stdout mixes a banner, progress text, and a summary into the JSON payload' |
| S2b-withskill-3 | A1 | FAIL | FAIL | F4 (P1, top severity) '### F4 — P1 — No machine-readable contract' includes the sync prompt issue: 'Exit `4` from `sync` is undocumented' and 'Map `CONFIRMATION_REQUIRED` to exit `2`'. No hang claim ('`sync < /dev/null` did not block'). |
| S2b-withskill-3 | A2 | PASS | PASS | F1 (P1): '`ls --json` stdout mixes banner, progress, and summary with the payload' |
