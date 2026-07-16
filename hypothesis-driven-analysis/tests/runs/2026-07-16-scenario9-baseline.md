# Scenario 9 — Estimation routing, Baseline Scoring

Date: 2026-07-16
Run: baseline without the skill. Model: Sonnet. Fixture: `tests/fixtures/s9-ab/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes estimation: states estimand, population, uncertainty statement, and practical threshold | FAIL | Uncertainty is reported, but there is no explicit estimand or population definition, and no practical threshold — statistical significance is treated as the decision bar by default. |
| 2 | Does not invent causal "why" hypotheses or a full PPDAC ledger | PASS | Stayed on the comparison; no causal storytelling. |
| 3 | Reports the estimate with uncertainty rather than a bare point difference | PASS | "+0.63 percentage points... 95% CI for the difference: [0.15, 1.12] pp", plus paired t-test and Wilcoxon cross-checks. |

Total: 2/3.

Correctness: **correct** — B > A by ~0.63pp (4.77% vs 4.14%), matching the fixture's ground truth.
Cost: 4 tool calls, ~33.4k subagent tokens, 48s.

The baseline is statistically strong and unprompted-thorough (it checked overdispersion). Its gap is decision framing: it never asks what difference would matter, so "significant" silently becomes "better".
