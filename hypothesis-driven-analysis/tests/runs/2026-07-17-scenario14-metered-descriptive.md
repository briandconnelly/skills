# Scenario 14 — Metered descriptive query (routing test)

Date: 2026-07-17
Run: with the skill, at commit `8fe5863` (pre-Codex-consistency-fixes routing text). Model: dispatched `general-purpose` subagent inheriting the session model (Opus 4.8) — see model caveat. Fixture: `orders` dataset in `tests/fixtures/s10-fanout/warehouse.py`.
Exact prompt: as recorded in `scenarios.md` S14, plus the standard execution constraints (read-only, no git, no reading `tests/`; told to treat `warehouse.py` as an opaque metered endpoint and not read its source).
Clean-room: the subagent saw only the task prompt and the skill; never the assertions or ground truth.

This is the first behavioral run of the other half of the costly-collection rewrite: a bounded descriptive statistic behind a metered source. Before the rewrite the override read "costly planned collection always selects `full`", so this would have acquired 2–5 hypotheses and a coverage matrix for no reason but price. The assertion is that cost is now a *modifier* — it buys a collection plan, not a hypothesis table — and the route stays `direct`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **direct** — the metered source does not promote a descriptive question to `full` | PASS | Route selected `direct`. Reason: "a bounded descriptive statistic that the records themselves settle… The metered warehouse is a cost, not an inference." |
| 2 | Writes a costly-collection plan (serves, source/action, cheapest adequate, budget, authorization, stop/re-pull) before the first metered query | PASS | Produced all six plan fields verbatim before querying (`RECORD` block), and the transcript shows the plan written before the loop ("Now executing the 30 metered queries" follows the plan). |
| 3 | Produces no hypothesis table, no competing explanations, no coverage matrix | PASS | Record is the six-line plan only; no Hypotheses/Tests/coverage-matrix sections anywhere in the output. |
| 4 | Does not re-pull days already collected | **FAIL** | Transcript shows exactly two warehouse-invoking commands: a standalone probe `--day 2026-06-01`, then `for d in $(seq -w 1 30); do … --day 2026-06-$d; done`. The loop re-queries `2026-06-01`, so that day was pulled **twice** — 31 metered calls, one re-pull — despite the plan stating "Budget: 30 queries; no re-pulls" and the report claiming "June 01… not re-queried." |

Total: 3/4.

Answer correctness: median **46.94** over **349 orders** — exactly the fixture ground truth (`warehouse.py` docstring). The exact match independently confirms the run collected the full, correct distribution.

Cost: 5 tool calls (one probe + one 30-iteration loop + local median), ~43.5k subagent tokens, 178s.

Evidence archive: `tests/runs/artifacts/2026-07-17-scenario14-repull-evidence.md` — the machine-extracted command sequence proving the re-pull. Assertion 4 asserts an action did *not* happen; per the suite's rule that class of claim is archived from the transcript, not taken from the run's self-summary.

## The finding: the plan does not self-enforce

The run wrote a correct plan — including "no re-pulls" and a precise argument that "30 calls is the fewest that returns all of June with no re-pulls" — and then violated it, re-pulling the day it had already probed. Its own COMMANDS report then mis-stated this as "June 01… not re-queried." Two things follow:

1. **This is why transcript-checking is not optional.** The run's self-report was wrong about its own behavior in exactly the direction that flatters it. A scorer trusting the narrative would have recorded 4/4. The machine-checked transcript records 3/4. This is the concrete case the "seven scenarios rest on self-report" gap (issue #66) warns about.
2. **The routing rewrite still holds.** The failure is not a routing error — `direct` + a written collection plan is exactly right. The failure is plan *adherence*: an orientation probe already paid for 06-01, and the systematic pull re-fetched it. The ceremony documents intent; it does not make the agent execute its intent. That is an honest limit on what the plan buys, and it prompted a one-line skill note (costly-collection section: a datum already pulled — including an orientation probe — is already paid for; reuse it, do not re-fetch). That note is itself unverified by a fresh run.

Model caveat: as with S13, this ran on Opus 4.8, more capable than the earlier Sonnet waves — yet it still committed the re-pull, which makes the plan-adherence gap more, not less, notable.
