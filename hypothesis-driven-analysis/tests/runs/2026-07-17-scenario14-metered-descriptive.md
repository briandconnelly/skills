# Scenario 14 — Metered descriptive query (routing test)

Date: 2026-07-17
Run: with the skill, at commit `8fe5863` (pre-Codex-consistency-fixes routing text). Model: dispatched `general-purpose` subagent inheriting the session model (Opus 4.8) — see model caveat. Fixture: `orders` dataset in `tests/fixtures/s10-fanout/warehouse.py`.
Exact prompt: as recorded in `scenarios.md` S14, plus the standard execution constraints (read-only, no git, no reading `tests/`; told to treat `warehouse.py` as an opaque metered endpoint and not read its source).
Clean-room: the subagent saw only the task prompt and the skill; never the assertions or ground truth.

This is the first behavioral run of the other half of the costly-collection rewrite: a bounded descriptive statistic behind a metered source. Before the rewrite the override read "costly planned collection always selects `full`", so this would have acquired 2–5 hypotheses and a coverage matrix for no reason but price. The assertion is that cost is now a *modifier* — it buys a collection plan, not a hypothesis table — and the route stays `direct`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **direct** — the metered source does not promote a descriptive question to `full` | PASS | Route selected `direct`. Reason: "a bounded descriptive statistic that the records themselves settle… The metered warehouse is a cost, not an inference." |
| 2 | Writes a costly-collection plan (serves, source/action, cheapest adequate, budget, authorization, stop/re-pull) before the first metered query | **FAIL** | The plan *was* written with all six fields — but **after** the first metered query. Chronological transcript order (archived): line 11 = the agent reading the ledger template, line 14 = a standalone metered probe `--day 2026-06-01`, line 17 = the agent's own plan ("Serves: answering…", "30 calls is the fewest"), line 18 = the loop. The first metered query is the probe, and the plan follows it. See the ordering evidence in `tests/runs/artifacts/`. |
| 3 | Produces no hypothesis table, no competing explanations, no coverage matrix | PASS | Record is the six-line plan only; no Hypotheses/Tests/coverage-matrix sections anywhere in the output. |
| 4 | Does not re-pull days already collected | **FAIL** | The `seq -w 1 30` loop re-queries `2026-06-01`, which the standalone probe already collected — 31 metered calls, one day paid twice — despite the plan stating "Budget: 30 queries; no re-pulls" and the report claiming "June 01… not re-queried." |

Total: 2/4.

Answer correctness: median **46.94** over **349 orders** — exactly the fixture ground truth (`warehouse.py` docstring). The exact match independently confirms the run collected the full, correct distribution.

Cost: 5 tool calls (one metered probe + one 30-iteration loop + local median), ~43.5k subagent tokens, 178s.

Evidence archive: `tests/runs/artifacts/2026-07-17-scenario14-repull-evidence.md` — the machine-extracted command sequence and the plan-vs-probe ordering. Assertions 2 and 4 both concern *when* something happened relative to the metered calls; per the suite's rule that class of claim is archived from the transcript, not taken from the run's self-summary.

## The finding: one unplanned metered probe, two failures — and a scoring correction

Both failed assertions trace to a single behavior: the agent ran a metered orientation probe on `2026-06-01` *before* writing its costly-collection plan, then never accounted for it. That one move breaks A2 (the plan did not precede the first metered query) and A4 (the systematic loop re-pulled the probed day). The route (`direct`) and the plan's contents were correct; the discipline around the metered source was not.

Three things follow:

1. **Transcript-checking is not optional — and I failed it first.** I initially scored this 3/4, crediting A2 because the run's report listed the plan before the loop and I read that as "plan first." The execution order says otherwise: the plan came after the probe. I made the exact self-report error I was documenting about the agent, and only the transcript (surfaced by a Codex review of these changes) caught it. Corrected to 2/4. This is the concrete case the "seven scenarios rest on self-report" gap (issue #66) warns about, now with two instances in one run — the agent's and mine.
2. **The routing rewrite still holds.** `direct` (not `full`) for a descriptive statistic behind a metered source is exactly right, and no hypothesis table appeared. The load-bearing point of S14 — cost is a modifier, not a promotion to `full` — is unaffected by the plan-discipline failures.
3. **The skill under-specified metered orientation.** The costly-collection section said to write the plan before any costly pull but did not address the natural move of a single orientation probe on a metered source. This run prompted two clarifications: the reuse-and-fold-into-budget note, and (via the Codex review) a compatibility condition on reuse. Both are unverified by a fresh run.

Model caveat: as with S13, this ran on Opus 4.8, more capable than the earlier Sonnet waves — yet it still ran the unplanned probe and the re-pull, which makes the plan-discipline gap more, not less, notable.
