# Scenario 2 — Non-trigger guard after the description edit, Trigger Scoring

Date: 2026-07-18
Run: guard arm dispatched after the description edit (`aa1470e`), testing that broadening the description to claim adjudication did not start capturing bare descriptive queries.
Model: Sonnet.
Prompt: Scenario 2's bare median question ("Here's `orders.csv`. What was the median order value in June?") with the same three-skill catalog stated (amended description verbatim in the transcript's prompt).
Fixture: `tests/fixtures/s1-conversion/orders.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes direct: computes the median and answers | PASS | Two tool calls (one Read of the CSV, one python one-liner); answer: all 268 rows fall in June 2026, median order value **$76.36**. |
| 2 | No ledger, no hypothesis language, no PPDAC ceremony | PASS | Zero Write/Edit tool_use in the manifest (machine-checked); no ledger, hypothesis, or PPDAC vocabulary in either text block; the run never read `SKILL.md`. |

Total: 2/2.

The run declined the skill by citing the amended exclusion itself: "this is a bounded descriptive computation (a single column's median), not a competing-hypotheses question, so per the hypothesis-driven-analysis skill's own scope note it should be answered directly" — i.e. the narrowed wording ("bounded descriptive queries where nothing is asserted") still reads as an exclusion when nothing is asserted.
One guard run is consistency, not proof, that the S2 boundary held through the edit.
Cost: 2 tool calls, ~38.7k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md`.
