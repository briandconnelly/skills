# Scenario 17 — Trigger reach for single-claim verification, Before-state Scoring

Date: 2026-07-18
Run: trigger-discrimination arm dispatched BEFORE the description edit (`aa1470e`); the transcript's own prompt carries the pre-edit frontmatter description verbatim (no adjudication clause, `bounded descriptive queries` exclusion unqualified).
Model: Sonnet.
Prompt: Scenario 11's claim ("Someone claims our checkout p95 latency exceeded 500ms yesterday") with a three-skill catalog stated and the skill not named in the request.
Fixture: `tests/fixtures/s11-mini/checkout_latency.csv` (sha256 in the 2026-07-18 S17 evidence artifact; realized p95 ≈ 392ms, claim false).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The skill activates from its description alone (transcript shows the skill file read and followed) | FAIL | Manifest: 3 tool_use, all Bash against the fixture CSV; zero reads of `SKILL.md` or any skill file. The run declined the skill by name, quoting the old exclusion: "the three candidate skills' own scope notes rule them out (hypothesis-driven-analysis explicitly excludes \"bounded descriptive queries\")". |
| 2 | Once loaded, routes mini and answers correctly that the claim is false (consistent with S11) | FAIL | Never loaded, so no mini ledger exists to score; the run answered directly and correctly (claim false, p95 ≈382–392ms depending on percentile method), but a correct answer outside the skill does not satisfy the assertion. |

Total: 0/2 — the before-state the scenario predicts: the old description's own wording blocks the mini route it defines from ever being reached by description-based activation.

Conclusion correctness: the direct answer itself was right and well-hedged (14/1200 requests over 500ms, p99 ≈ 506ms, 20-of-24-hour coverage caveat stated).
The failure is reach, not competence — which is exactly what S17 was built to measure.
Prompt-fidelity note, not scored: the prompt asked for the skill-choice statement before doing anything else, and this run's first choice statement appears after its first tool call (text block 1 follows tool_use 1 in the transcript).
Cost: 3 tool calls, ~33.7k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md` (transcript sha256, manifest, verbatim skill-choice sentences, machine checks).
