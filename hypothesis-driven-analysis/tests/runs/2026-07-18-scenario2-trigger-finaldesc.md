# Scenario 2 — Non-trigger guard under the final description, Post-hardening Probe

Date: 2026-07-18
Run: guard probe dispatched AFTER the Codex-review hardening commit (`dd39d96`) re-scoped the description's exclusion clause, testing that attaching "where nothing is asserted" to retrieval as well as descriptive queries did not start capturing bare descriptive questions.
Model: Sonnet.
Prompt: Scenario 2's bare median question with the same three-skill catalog stated; the transcript's prompt carries the final description verbatim, machine-checked against `SKILL.md` line 3.
Fixture: `tests/fixtures/s1-conversion/orders.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes direct: computes the median and answers | PASS | Three tool calls (fixture Read, an errored `cd` into a not-yet-created scratch dir, the retried python one-liner); answer: all 268 rows fall in June 2026, median order value **$76.36** — matching the Ninth-wave guard run. |
| 2 | No ledger, no hypothesis language, no PPDAC ceremony | PASS | Zero Write/Edit tool_use in the manifest (machine-checked); the run never read `SKILL.md` (manifest ordinal 1 is the fixture Read); the only occurrence of "hypotheses" is inside the decline rationale quoting the skill's scope, not in any analysis structure. |

Total: 2/2.

Fidelity note, recorded not scored: the final message omits the requested state-your-skill-choice sentence; the choice is stated in the transcript's opening text block instead, before any tool call: "I am not using any of the listed skills — this is a direct, bounded descriptive computation (median of a column, filtered to June), not a diagnostic/comparative question with competing hypotheses, so hypothesis-driven-analysis's own scope note excludes it, and no other skill applies."
So the guard's substance held (declined by scope, answered directly) while the reporting instruction was only partially followed — the mirror image of the pre arm's placement drift.
One guard run is consistency, not proof, that the S2 boundary held through the exclusion re-scope.
Cost: 3 tool calls; the dispatch record reached the scoring session without a token figure, so none is recorded rather than one reconstructed.
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md` (Final-description probes section; committed manifest included).
