# Scenario 13 — One claim, many probes (routing test)

Date: 2026-07-17
Run: with the skill, at commit `8fe5863` (pre-Codex-consistency-fixes routing text). Model: dispatched `general-purpose` subagent inheriting the session model (Opus 4.8) — see the model caveat at the foot of this file. Fixture: `tests/fixtures/s13-conjunctive/`.
Exact prompt: as recorded in `scenarios.md` S13 (repointed to the `s13-conjunctive` fixture), plus the standard execution constraints (read-only fixtures, no git, no reading `tests/scenarios.md` or `tests/runs/`).
Clean-room: the subagent was given only the task prompt and told to load and follow `SKILL.md`; it never saw the assertions, the fixture ground truth, or this suite's prior runs.

This is the first behavioral run of the case the routing rewrite was written to fix: one non-causal claim that needs ≥3 probes to settle. Before the rewrite it was UNROUTABLE (`mini` was capped at two probes, `full` required multiple explanations / a causal claim). The assertion is that it now routes `mini` on claim count, not `full` on probe count.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **mini** despite needing ≥3 probes; does not build a hypothesis table | PASS | Route selected `mini`; record is a one-paragraph ledger (claim/prediction/probes/outcome/answer), no Hypotheses/Sources/Tests sections. Reason quoted the table: "one stated claim… non-causal… no rival explanation competes for it — that is exactly the mini condition." |
| 2 | Does not route `full` on the grounds that the probe count exceeds two | PASS | Quoted the controlling sentence verbatim: "a claim that takes four probes to settle is still one claim — a probe budget is not a second hypothesis." Ran 3 probes (orient → hourly p95 → device×user_type × 5 evening windows) inside the mini route. |
| 3 | Settles each conjunct (device, evening window, returning-vs-new) and answers correctly that the claim as stated is FALSE | PASS | Answered "the claim as stated does NOT hold." The prompt does not define "evening peak," so the agent located it empirically **and tested five windows — 17–21, 18–20, 18–21, 19–21, and 18–22 (the fixture's own definition)** — reporting mobile∧returning p95 = 435–462ms across all of them, never ≥500. The verdict is therefore robust to the window and percentile convention, not an artifact of the agent's 18:00–20:00 nearest-rank figure (462.4ms) happening to match the scorer's 18:00–21:59 linear-interp figure (438.6ms). It also localized the breach to **new** users (mobile+new 832ms, desktop+new 631ms), refuting "only returning" and "only on mobile." |

Total: 3/3.

Cost: 6 tool calls, ~42.4k subagent tokens, 107s.

## What this establishes and what it does not

The load-bearing point — the rewritten table routes a many-probe single claim to `mini`, not `full` — held behaviorally, and the run cited the exact rewrite sentence as its reason. That converts S13 from "written, never run" to run.

The run **exceeded** the assertion: it did not merely settle each conjunct, it caught that the fixture's trap (the two-way mobile∧evening slice p95 = 601ms, which the scorer confirms) is driven by new users, so an agent that stopped after two conjuncts would have wrongly answered TRUE. This run did not.

Model caveat: this ran on a more capable model (Opus 4.8) than the earlier Sonnet waves. A stronger model routing correctly is weaker evidence that the *text* is followable by a weaker reader than a Sonnet pass would be. The clean-room trace rounds (round 4, `scenarios.md`) already established mechanical followability on the text alone; this run adds that a capable agent, handed only the skill, actually produces the `mini` ceremony and the correct answer. A Sonnet re-run would strengthen the followability claim and is worth doing before calling the model question closed.
