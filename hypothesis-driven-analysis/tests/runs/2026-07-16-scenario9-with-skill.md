# Scenario 9 — Estimation routing, With-Skill Scoring

Date: 2026-07-16
Run: with the skill. Model: Sonnet. Fixture: `tests/fixtures/s9-ab/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes estimation: states estimand, population, uncertainty statement, and practical threshold | PASS | "Route: Estimation ('is B better, and by how much' — no causal 'why', single comparison)"; estimand = "difference in signup conversion rate (signups/visits), B − A"; population = "all visits during the 2-week test (28,050 visits)"; uncertainty = two-proportion z + paired t + Wilcoxon; threshold = "None was supplied by the requester; I used '95% CI excludes 0' as the statistical bar and report the raw effect size so the reader can apply their own business threshold." |
| 2 | Does not invent causal "why" hypotheses or a full PPDAC ledger | PASS | "No ledger artifact was created (estimation route only requires stating estimand/population/method/threshold inline)." |
| 3 | Reports the estimate with uncertainty rather than a bare point difference | PASS | "+0.63pp... 95% CI [0.15pp, 1.12pp]", stability checked across both weeks. |

Total: 3/3.

Correctness: **correct** — B > A by ~0.63pp.
Cost: 5 tool calls, ~37.0k subagent tokens, 71s (vs baseline 4 calls / ~33.4k).

The estimation route earns its place here. The routing table selected it explicitly and correctly declined the hypothesis ledger, so the added ceremony over baseline is one paragraph of framing — ~11% more tokens, the smallest delta in the suite.

The one real difference in output quality: the run surfaced the *absence* of a practical threshold as a limitation rather than defaulting to statistical significance, and flagged that randomization was claimed but not verified ("associative evidence *within a claimed A/B test structure*, not independently verified as a randomized experiment"). The baseline did neither.
