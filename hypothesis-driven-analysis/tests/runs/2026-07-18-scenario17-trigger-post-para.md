# Scenario 17 — Paraphrase robustness probe, outside S17's assertion table

Date: 2026-07-18
Run: robustness probe, not an S17 assertion run — this row feeds no assertion table and its result is recorded as supporting evidence only.
Model: Sonnet.
Prompt: paraphrased claim ("A teammate is insisting that our checkout flow blew through its 500ms latency SLO at the 95th percentile on 2026-07-15, and wants it escalated. Can you check whether that actually happened?"), sharing no verbatim phrasing with the description's example; same catalog with the amended description.
Fixture: `tests/fixtures/s11-mini/checkout_latency.csv` (sha256 in the 2026-07-18 S17 evidence artifact).

Why this run exists: the amended description's adjudication example ("someone says p95 exceeded 500ms yesterday") literally quotes S17's prompt, so the two post-edit assertion passes demonstrate activation by near-verbatim match — weak evidence that the description works as a description rather than as a lookup key.
This probe removes the verbatim overlap and asks whether activation survives.

Observed, from the transcript:

- Activated: manifest ordinals 1–2 are `Read` of `SKILL.md` and `references/ledger-template.md`, before any data touch; opening statement: "I am using the hypothesis-driven-analysis skill, since this is exactly the \"someone claims a metric crossed a threshold\" adjudication case it's designed for."
- Routed mini: "hypothesis-driven-analysis, mini route — this is exactly one stated claim … being adjudicated, non-causal, with no rival explanation to discriminate against."
- Outcome cell `CONTRADICTED` (inside the mini vocabulary); verdict correct: the claim does not hold, p95 = 392.2ms overall, every hourly p95 in 324–460ms, ~100ms of headroom, with the 20-of-24-hour coverage caveat framed for the escalation decision.

Reading: one paraphrase, one activation — consistent with the description generalizing beyond its own example, and the only evidence in this wave that it does; a single probe cannot establish robustness.
Cost: 5 tool calls, ~49.3k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md`.
