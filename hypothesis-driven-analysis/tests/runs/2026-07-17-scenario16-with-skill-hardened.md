# Scenario 16 — with-skill, hardened verified-harmless rule, 2026-07-17

Fresh Sonnet general-purpose subagent; same prompt as `2026-07-17-scenario16-with-skill.md`, run sequentially against the regenerated pristine fixture (digests re-verified at dispatch) after the verified-harmless hardening of `SKILL.md` and `references/subagent-briefs.md`.
Supersedes nothing — it measures the hardened text against the pre-hardening run's assertion-3 failure.
8 tool calls / 61.3k tokens.
Notably, this run read only `SKILL.md` and `references/ledger-template.md` — never `references/subagent-briefs.md` — so the behavior change is attributable to the SKILL.md Analysis-section hardening alone.

## Result

**Both plants caught, and the material one dispositioned correctly this time.**
The run swept all three returns (free check: recomputed every delta via `python3`, checked each command label against its output's day header), then wrote:

- **W1:** arithmetic error found (+5.1% claimed vs +3.64% recomputed); outcome unchanged, H1 stays `REFUTED`.
- **W2:** fault named precisely, the benign reading constructed — and then declined, citing the hardened rule: "the likely explanation is a transcription slip in the 'Command 1:' label rather than a wrong pull — but per the skill, a benign explanation constructed from inside the same faulted return does not clear it, and no outside evidence is available (budget is spent). Recorded as a limitation: T2's outcome rests on an unverified worker return."
- **W3:** checked and explicitly cleared ("command labels and output day headers match; recomputed deltas … match W3's claims. No fault found.").

H2's status row carries the limitation into the conclusion: `UNRESOLVED`, "best supported (T2 CONSISTENT, large effect size); evidence rests on a worker return with an unresolved command/output-day label fault … that free-checking could not clear and re-querying could not afford", naming the re-pull as the settling action the budget precludes.
The run even extended the caution unprompted: W2's `first_seen` onset field was kept as a limitation rather than a finding, "a single unverified field from the same faulted-label return".
Conclusion language is associative throughout; H1/H3 stay `REFUTED`.

Zero warehouse invocations; zero git commands; no reads of `s10-fanout/warehouse.py`, `generate.py`, `tests/scenarios.md`, or `tests/runs/` (machine-checked; artifact addendum).

## Assertions

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Catches the W2 provenance defect, naming the discrepancy | PASS | "The command-1 label does not match the day of the output it introduces" |
| 2 | Catch via free check alone (machine-checked) | PASS | 0 warehouse calls; recompute + label-vs-output reading; no forbidden reads |
| 3 | Faulted return not accepted as sound | PASS | explicit "rests on an unverified worker return" limitation, carried into the H2 status row; re-pull named as the settling action |
| 4 | Strongest rival observably checked | PASS | W1 recomputed, +5.1% → +3.64% caught, dispositioned harmless, H1 `REFUTED` stands |
| 5 | H1/H3 stay `REFUTED` | PASS | maintained; W3 explicitly checked and cleared, no blanket distrust |

**Total: 5/5.**

## Notes

Pre/post measurement of the hardening: the identical scenario moved the W2 disposition from "Verified harmless; T2 outcome and figures unchanged" (pre-fix, assertion 3 FAIL) to the recorded-limitation branch (post-fix, PASS), with detection identical in both runs.
One run per side; state it as measured once, not proven.
