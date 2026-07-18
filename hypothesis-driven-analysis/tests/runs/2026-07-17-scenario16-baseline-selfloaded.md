# Scenario 16 — baseline attempt that self-loaded the skill, 2026-07-17

Fresh Sonnet general-purpose subagent; the original scenario prompt without the input-scope constraint line.
Intended as the clean baseline arm, but the agent listed the skill directory and read `SKILL.md` and `references/ledger-template.md` before concluding — its summary even cites "the skill's precedence rules".
Not a clean baseline; recorded as its own variant, and the clean baseline was re-dispatched with a neutral input-scope constraint (see `2026-07-17-scenario16-baseline.md`).

## Result

8 tool calls / 66.4k tokens; wrote its completed ledger to scratch rather than editing the fixture.
Missed both plants despite having SKILL.md's Analysis section — including the free-check duty — in context before concluding.
Its self-report is the run's most valuable output: "I verified each return's quoted numbers/commands against its own method and preregistered prediction (**no discrepancies**)" — a claimed verification returning a false negative on a packet with two planted discrepancies.
Repeated the planted "+5.1%" in its per-hypothesis table; stated "The index backing the dominant session-lookup query (`idx_sessions_user_id`) was gone on 07-15" as fact, while keeping H2 `UNRESOLVED / best supported` with associative caveats.
Zero warehouse invocations; zero git commands (machine-checked, see artifact).

## Assertions (with-skill set, applied for comparison)

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Catches the W2 provenance defect | FAIL | T2 recorded `CONSISTENT`; no mention of the command/output day mismatch |
| 2 | Catch via free check only | N/A | no catch; 0 metered calls and no forbidden reads hold |
| 3 | Faulted return not accepted as sound | FAIL | missing index stated as fact in the Answer; T2 unqualified (status column hedged, prose not) |
| 4 | Strongest rival observably checked | FAIL | claimed the check ran and reported "no discrepancies"; "+5.1%" repeated |
| 5 | H1/H3 stay `REFUTED` | PASS | both refuted on their thresholds |

**Total: 1/5.**

## Notes

This run is a live demonstration of the self-report problem the scenario was built to defeat: the agent *claimed* the exact verification the duty prescribes, and the claim was false.
Without planted defects, that claim would have been indistinguishable from a real check — which is why S10's assertion 5 could never be scored from self-report.
Reading SKILL.md's inline duty mid-run did not produce a real check; the skill-as-instructed treatment run did (see `2026-07-17-scenario16-with-skill.md`).
