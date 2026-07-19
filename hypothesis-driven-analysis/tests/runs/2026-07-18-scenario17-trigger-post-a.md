# Scenario 17 — Trigger reach for single-claim verification, Post-edit Scoring (run a)

Date: 2026-07-18
Run: trigger-discrimination arm dispatched AFTER the description edit (`aa1470e`); the transcript's prompt carries the amended description verbatim (adjudication clause present, exclusion narrowed to "bounded descriptive queries where nothing is asserted").
Model: Sonnet.
Prompt: identical to the before-state arm (Scenario 11's claim, catalog stated, skill not named).
Fixture: `tests/fixtures/s11-mini/checkout_latency.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The skill activates from its description alone (transcript shows the skill file read and followed) | PASS | Manifest ordinal 1 is `Read` of `<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md`, before any data touch; the opening statement names the skill and cites the description's adjudication example as the reason. |
| 2 | Once loaded, routes mini and answers correctly that the claim is false (consistent with S11) | PASS | Final message: "the skill's own routing table classifies as **mini** (one claim, no rival explanations, non-causal)"; one-paragraph ledger (claim, prediction, probes, outcome); verdict "The claim is **false**", p95 = 392.2ms with a bootstrap CI [374.7, 409.4]ms and the 20-of-24-hour coverage limitation stated. |

Total: 2/2.

Vocabulary drift, recorded not scored: the mini-ledger outcome cell reads `REFUTED`, which is outside the mini template's closed outcome set (`CONSISTENT / CONTRADICTED / NON_DISCRIMINATING`, `references/ledger-template.md` line 99) — `REFUTED` is a hypothesis status from the full ledger, not a mini outcome.
This is an issue #73-class instance (claim/status vocabulary drift recurring despite the template stating the closed sets), now reproduced on the mini route.
Verbatim opening statement: "I am using the hypothesis-driven-analysis skill, since this task asks me to adjudicate a specific claim (\"p95 exceeded 500ms yesterday\") against data, which is exactly the \"someone says p95 exceeded 500ms yesterday\" example in that skill's description."
That sentence is also the caveat: this run activated on a near-verbatim match between the description's example and the prompt, so it demonstrates reach, not generalization — the paraphrase probe run carries that burden.
Cost: 5 tool calls, ~43.3k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md`.
