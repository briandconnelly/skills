# Scenario 7 — Serial degradation (no subagent capability)

Date: 2026-07-16
Run: with the skill, harness declared to have no subagent capability. Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 5 | On a harness without subagents, the same tests run serially with the same ledger | PASS | Full ledger (Problem, Hypotheses H1–H4, Sources, Data Validity, Tests T1–T4, Amendments, Conclusion) produced inline; same conclusion, same status vocabulary, no degradation in structure vs the fan-out-capable run. |

Total: 1/1 (this run scores only assertion 5; assertions 1–4 belong to `scenario7-fanout`).

Cost: 12 tool calls, ~47.6k subagent tokens, 162s — statistically indistinguishable from the fan-out-capable run (12 calls, ~48.5k), which also chose to stay inline.

**Graceful degradation confirmed.** Removing subagents changed nothing about the investigation, because the fan-out criterion had already selected inline in the capable run. The two runs reached the same answer (`/lp/summer-sale` composition, ~0.57% vs ~3% baseline; deploy refuted) with the same ledger shape.

## Best sensitivity check of the whole suite

This run performed a genuine known-positive check before trusting a negative — the only run to do so on this fixture:

> "the same daily-rate method that found the artifact-negative result (T4) does detect real signal elsewhere — it clearly surfaces the sessions-count step change at the week boundary (600→760/day) and the deploy-day client_version cutover, so the instrument is not blind to step changes of this size."

That is exactly what the skill's sensitivity rule asks for. Notably it still missed the mobile undercount: the check validated the instrument against a *volume* step at the week boundary but never compared per-segment coverage across days, so the 06-13/06-14 mobile gap stayed invisible. Third independent with-skill miss on this fixture.
