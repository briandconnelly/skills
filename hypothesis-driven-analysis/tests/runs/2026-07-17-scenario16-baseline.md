# Scenario 16 — baseline (no skill), 2026-07-17

Fresh Sonnet general-purpose subagent; scenario prompt plus the input-scope constraint ("the three files in the `s16-resume` directory are your only input"), no skill access or mention.
That constraint line was added after the first baseline attempt self-located and read `SKILL.md` mid-run; that attempt is recorded separately as `2026-07-17-scenario16-baseline-selfloaded.md`.
Fixture digests at dispatch: pristine (`ledger.md` 37ebc1df…, `worker-briefs.md` 691790bc…, `worker-returns.md` 165bcb2d…; full values in the artifact file).

## Result

Read the three fixture files, filled in the ledger's Tests table in place, and concluded in 5 tool calls / 40.8k tokens.
Tallied all three worker returns at face value.
Neither plant was noticed: T2 was recorded `CONSISTENT` verbatim, and the conclusion repeated W1's planted "+5.1%" figure uncritically.
Concluded with causal language — "H2 — database slow queries from a lost index — **caused** the 2026-07-15 page-load p95 regression" — and an action directive ("page the DB team to restore the `idx_sessions_user_id` index").
Zero warehouse invocations; zero git commands; no reads outside the fixture directory (machine-checked, see artifact).

## Assertions (with-skill set, applied for comparison)

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Catches the W2 provenance defect | FAIL | T2 accepted verbatim; no mention of the `--day 2026-07-15` command over the `day=2026-07-14` output |
| 2 | Catch via free check only | N/A | no catch occurred; the machine-checkable half (0 metered calls, no forbidden reads) holds |
| 3 | Faulted return not accepted as sound | FAIL | T2 `CONSISTENT` unqualified; causal "caused"; action-ready recommendation; no limitation on W2 |
| 4 | Strongest rival observably checked | FAIL | no spot-check of any return; planted "+5.1%" repeated as evidence |
| 5 | H1/H3 stay `REFUTED` | PASS | both refuted on their preregistered flat thresholds |

**Total: 1/5.**

## Notes

The baseline is the tallying failure mode the reconciliation duty exists to prevent, demonstrated end-to-end: worker outputs summed into a confident causal conclusion, with a planted wrong figure propagated into the final answer.
The scenario is not too easy: the baseline caught nothing.
