# Scenario 17 — Trigger reach for single-claim verification, Post-edit Scoring (run b)

Date: 2026-07-18
Run: second post-edit trigger-discrimination arm, same prompt and catalog as run a (amended description verbatim in the transcript's prompt).
Model: Sonnet.
Fixture: `tests/fixtures/s11-mini/checkout_latency.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The skill activates from its description alone (transcript shows the skill file read and followed) | PASS | Manifest ordinal 1 is `Read` of `<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md`, before any data touch; opening statement: "I'm using the hypothesis-driven-analysis skill, because this is a claim-adjudication question (\"checkout p95 exceeded 500ms yesterday\") requiring evidence-based investigation with competing explanations for what the true p95 is/was." |
| 2 | Once loaded, routes mini and answers correctly that the claim is false (consistent with S11) | PASS | Final message: "a single stated claim … with no rival explanation competing, so it routes to the **mini** path (one-paragraph ledger: claim, prediction, probes, outcome)"; outcome cell `CONTRADICTED` (inside the mini vocabulary); verdict "The claim is false", p95 = 392.2ms by two methods, bootstrap 95% CI [374.9, 409.4]ms, coverage limitation stated. |

Total: 2/2 — and clean on the vocabulary where run a drifted.

One wobble worth recording: the opening sentence justifies activation with "competing explanations" language even though the mini route's condition is precisely that no rival explanation competes; the final message corrects itself to the right condition, so the route and its stated reason end correct.
Cost: 6 tool calls, ~43.7k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md`.
