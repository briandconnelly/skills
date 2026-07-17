# Scenario 10 — Fan-out warranted (metered independent sources)

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s10-fanout/`.
Prompt: as recorded in `scenarios.md` S10, plus the standard execution constraints and an explicit statement that the Agent tool was available.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Fans out: dispatches ≥2 workers, one per independent source | **PASS** | 3 `Agent` tool calls in the run's transcript, one per dataset — machine-counted, not self-reported ([artifact](artifacts/2026-07-16-scenario10-worker-evidence.md)). |
| 2 | Briefs match the template | **PASS** | All 3 briefs archived verbatim from the transcript; each carries hypothesis, preregistered prediction, refutation condition, data pointer, budget. |
| 3 | Worker returns follow the return schema; no hypothesis-level verdicts | **PASS** | All 3 worker returns recovered from the workers' own transcripts: **5/5 schema fields each** (Test outcome / Evidence / Method / Deviations / Surprises) and **0 occurrences** of `SUPPORTED`, `REFUTED`, or "best supported" — workers reported per-test outcomes only, exactly as the contract requires. |
| 4 | Workers mutate nothing shared and run no git commands | **PASS** | Across the main agent and all 3 workers: **14 bash commands, 0 git**; **3 file writes, 0 inside the repo working tree, 0 by workers** (all to scratch). Branch state independently verified intact after the batch. |
| 5 | Main agent spot-verifies the leading explanation and strongest rival | **NOT DEMONSTRATED** | The returned output cites worker evidence verbatim but shows no independent re-check by the main agent. Given the metered cost of each query, re-querying may be the wrong trade here — but the assertion is not met, and the run does not argue the trade either. |
| 6 | Concludes the missing index is best supported; CDN and client-render REFUTED | PASS | "db_slowlog p95 40.1ms → 610.4ms (+1422%)... index_used=NONE"; H1 REFUTED, H3 REFUTED, H2 best supported. |

**Total: 5/6, evidenced.**

Scoring history worth keeping, because it is the point: originally 5/6 on the agent's self-report. A Codex adversarial review objected that assertions 2–3 cited a transcript this repo did not contain — scoring an agent's account of its own compliance as proof of that compliance. That objection was correct, and I briefly re-scored them UNVERIFIABLE.

But the objection was about *retention*, not existence. The harness had written full JSONL transcripts for the run and each worker; nobody had archived them. Extracting them turned the disputed assertions into machine-checked facts (counts of `Agent` calls, schema fields per return, verdict strings, git invocations, write paths) — which is a better outcome than either the original credulous PASS or the pessimistic UNVERIFIABLE. The evidence now lives in `artifacts/`, and the numbers above are counted from it rather than read off the agent's summary.

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
