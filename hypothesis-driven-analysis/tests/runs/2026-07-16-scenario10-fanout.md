# Scenario 10 — Fan-out warranted (metered independent sources)

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s10-fanout/`.
Prompt: as recorded in `scenarios.md` S10, plus the standard execution constraints and an explicit statement that the Agent tool was available.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Fans out: dispatches ≥2 workers, one per independent source | **PASS** | `SUBAGENTS_DISPATCHED: 3` — "Three parallel workers were dispatched (one per dataset — independent sources, metered slow queries, exactly the skill's fan-out trigger)." |
| 2 | Briefs match the template | PASS | One hypothesis per brief with its prediction and data pointer; briefs reproduced in the run transcript. |
| 3 | Worker returns follow the return schema; no hypothesis-level verdicts | PASS | "each returned exactly the prescribed schema (Test outcome / Evidence / Method / Deviations / Surprises), no deviations reported." Outcomes are per-test (`CONSISTENT`/`CONTRADICTED`), not verdicts. |
| 4 | Workers mutate nothing shared and run no git commands | PASS | No writes outside worker scratch; branch state verified intact after the batch. |
| 5 | Main agent spot-verifies the leading explanation and strongest rival | **NOT DEMONSTRATED** | The returned output cites worker evidence verbatim but shows no independent re-check by the main agent. Given the metered cost of each query, re-querying may be the wrong trade here — but the assertion is not met, and the run does not argue the trade either. |
| 6 | Concludes the missing index is best supported; CDN and client-render REFUTED | PASS | "db_slowlog p95 40.1ms → 610.4ms (+1422%)... index_used=NONE"; H1 REFUTED, H3 REFUTED, H2 best supported. |

**Total: 5/6.**

Conclusion correctness: **correct** — matches fixture ground truth exactly (missing `idx_sessions_user_id` from 09:00 on 07-15; CDN and RUM flat).
Cost: 20 tool calls, ~80.7k subagent tokens, 376s — the most expensive run in the suite, and the only one where that cost buys wall-clock back (3 × 18s metered queries in parallel rather than serial).

## The subagent contract is no longer unverified

This closes the gap the reviewer called out and that the first fan-out attempt could not test. The old criterion asked the agent to predict whether delegation would beat an inline run it had not performed; faced with that, it declined and the entire worker contract went unexecuted. Given observable conditions instead — three separate systems, no shared preprocessing, metered ~18s queries — the criterion fires, and every piece of `references/subagent-briefs.md` ran for the first time: brief template, return schema, isolation rules, per-test outcomes.

That is direct evidence the F7 fix was the right diagnosis. The trigger wasn't too strict; it was unknowable.

## Honest gap: reconciliation is still untested

Assertion 5 fails. The main agent consumed three worker reports and concluded from them without independently re-checking the evidence behind the winner (`db_slowlog`) or the strongest rival. The skill requires exactly that, precisely because a compact worker return can hide a bad join or a misread unit.

There is a real tension the skill does not address: when collection is metered, "spot-verify the leading explanation" means paying for the query twice. Either the rule should say re-verification is worth the second charge, or it should name a cheaper form of verification (re-reading the worker's method and sample rather than re-running its query). As written it says neither, and this run silently skipped it.

## Note on skill mutation during the run

`SKILL.md`'s Gates section was edited while this run was in flight (the S4 authorization hardening). This run reads the routing and analysis sections, not Gates, and its route decision cites the post-`e55ba78` override ("causal question + metered/costly collection"), so its scoring is unaffected. Recorded because editing a skill under a live run is a methodology error regardless of whether it bit this time.
