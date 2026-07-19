# Scenario 17 — Trigger reach under the final description, Post-hardening Probe

Date: 2026-07-18
Run: revalidation probe dispatched AFTER the Codex-review hardening commit (`dd39d96`) re-scoped the description's exclusion clause; the transcript's prompt carries the final description verbatim ("where nothing is asserted" scoping retrieval as well as descriptive queries), machine-checked against `SKILL.md` line 3.
Purpose: validate that the exclusion re-scope did not close the claim-adjudication entry path the Ninth wave opened.
Model: Sonnet.
Prompt: identical to the Ninth wave's S17 arms (Scenario 11's claim, catalog stated, skill not named).
Fixture: `tests/fixtures/s11-mini/checkout_latency.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The skill activates from its description alone (transcript shows the skill file read and followed) | PASS | Manifest ordinal 1 is `Read` of `<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md`, ordinal 2 `references/ledger-template.md`, both before any data touch; opening statement names the skill and cites the description's adjudication example. |
| 2 | Once loaded, routes mini and answers correctly that the claim is false (consistent with S11) | PASS | Routed mini with a one-paragraph ledger; outcome cell `CONTRADICTED` (inside the mini template's closed set — no vocabulary drift this run, unlike post-a's `REFUTED`); verdict "the claim is false", p95 ≈392ms, bootstrap CI [374.9, 409.4]ms, 20-of-24-hour coverage limitation stated. |

Total: 2/2.

Verbatim opening statement: "I'm using the hypothesis-driven-analysis skill, since this is exactly the adjudication example it names (\"someone says p95 exceeded 500ms yesterday\")."
The Ninth wave's caveat carries over unchanged: this prompt near-verbatim matches the description's example, so this probe demonstrates that the final wording preserved reach, not generalization — the paraphrase evidence remains the wave's n=1 probe.
One errored Bash (`cd` into a not-yet-created scratch directory, retried with `mkdir -p`) is visible in the committed manifest; no repository writes (machine-checked with the wave's three scans, planted positives fired).
Cost: 6 tool calls, ~49.5k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md` (Final-description probes section; committed manifest included).
