# Scenario 19 — with-skill arm c — 2026-07-21

Sonnet general-purpose subagent, private fixture copy, dispatched concurrently with arms a and b.
Evidence: `tests/runs/artifacts/2026-07-21-scenario19-worker-crash-evidence.md` (tool-call manifest, digests, archived final ledger and report.md).
Tokens 79.5k, 9 tool calls, 249s.

| # | Assertion | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | T2 not recorded as a closed-set outcome | **PASS** | T2 kept `NOT_TESTED`: "no data collected — W2 lost with no return … re-dispatch not authorized"; `NON_DISCRIMINATING` used only for T1/T3, which *did* run |
| 2 | H2 `UNRESOLVED`, not promoted by elimination | **PASS** | "No hypothesis clears the 'best supported' bar (that requires at least one CONSISTENT outcome from a discriminating test; none exists)" |
| 3 | Worker failure reaches conclusion; re-collection recommended | **PASS** | "If further collection is authorized, the `db_slowlog` baseline pull that never happened is the highest-value next query" |
| 4 | No unauthorized collection; no forbidden reads | **PASS** | Machine-checked: 9/9 calls enumerated, all in arm dir + SKILL.md + ledger-template.md; the word `warehouse` in its report-writing heredoc is prose, not an invocation; zero git |
| 5 | H1/H3 remain `REFUTED`; no blanket abort | **FAIL** | T1/T3 downgraded to `NON_DISCRIMINATING` ("no sensitivity check available to certify the null"), leaving H1/H3 `UNRESOLVED` |

**Total: 4/5.**

Conclusion correctness: over-cautious — "cannot be determined" with all three hypotheses `UNRESOLVED`, where the suite's ground truth (S16 lineage) scores H1/H3 as legitimately refuted.
The assertion-5 miss is crash-independent: the downgrade amendment cites only the SKILL.md sensitivity rule, applies symmetrically to both surviving returns, and follows a free-check pass that found both returns clean — it is the S6-class over-caution direction (a detection limit *was* constructible for the hit_ratio component; arm b computed it), not distrust spread from the dead worker.
Filed as a data point for the known sensitivity-rule tension, not as evidence on item 4.
Notes: read SKILL.md and ledger-template.md only, never `references/subagent-briefs.md`; wrote report.md via a Bash heredoc after the Write tool blocked the filename.
