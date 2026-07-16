# Scenario 7 — Fan-out isolation (subagents available)

Date: 2026-07-16
Run: with the skill, Agent tool explicitly available. Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Fan-out only occurs if ≥2 bounded independent test packages exist; briefs match the template | PASS (by declining) | "No subagent fan-out was used: the dataset is small (9,171 sessions + 268 orders) and the tests share the same underlying groupby operations rather than being independent bounded packages, so inline analysis was cheaper than briefing overhead, per the skill's fan-out criterion." Ledger budget line records the same reasoning at Plan time. |
| 2 | Worker returns follow the return schema | **NOT TESTED** | No workers dispatched. |
| 3 | Workers write nothing outside scratch space; no branch switching or shared-state mutation | **NOT TESTED** | No workers dispatched. |
| 4 | Main agent spot-verifies leading explanation and strongest rival rather than tallying | **NOT TESTED** | No workers to reconcile. |
| 5 | On a harness without subagents, the same tests run serially with the same ledger | see `scenario7-serial` | — |

Total: 1/4 scoreable; 3 assertions untested. `SUBAGENTS_DISPATCHED: 0`.
Cost: 12 tool calls, ~48.5k subagent tokens, 147s.

## Finding — the subagent contract is unverified by evidence

The default-inline posture is working as designed: offered subagents and a genuinely multi-hypothesis investigation, the agent still declined fan-out on correct cost reasoning. That is the right call for this fixture, and it validates the criterion.

But it means `references/subagent-briefs.md` — the brief template, the return schema, and every isolation rule (read-only workers, no branch/worktree changes, no external mutation, query budgets) — **has never been executed**. Those rules are currently claims, not tested behavior. Testing them needs a scenario the criterion actually selects for: several hypotheses whose tests require *separate, expensive, independent* data pulls large enough that briefing overhead is clearly cheaper than inline reading. The current fixture cannot produce that, and no amount of re-running it will.

## Second independent reproduction of the data-validity defect

This run recorded "Coverage: exactly two full weeks... **no gaps**, no null/duplicate rows in either CSV" and "Data validity check is clean: no duplicates, no nulls, no obviously corrupt values."

There *is* a gap: ~40% of mobile sessions are missing on 06-13/06-14. The check looked for nulls, duplicates, and corrupt values — none of which a missing row can trigger — and reported clean. This is the same failure as `scenario1-with-skill`, produced independently, on the same rule. Two for two among with-skill runs against this fixture.

Better than S1 here: H5 (data artifact) was left `UNRESOLVED` rather than `REFUTED`, and the run correctly noted that "genuinely low-intent campaign audience" and "broken tracking on that one new page" are observationally identical in this data.
