# Scenario 18 run A — 2026-07-20 (trigger, 3 reps, Sonnet) — WEAK ARM, superseded

Date: 2026-07-20.
Run: trigger-discrimination, weak arm.
Superseded by run B (`2026-07-20-scenario18-trigger-opus-strong.md`), which uses the committed prompt/fixture and the model the real failure occurred on.
Model: Sonnet (general-purpose subagents).
Fixture: `tests/fixtures/s18-analytics/SKILL.md` pointing at `tests/fixtures/s1-conversion/`.

This first arm used an earlier, weaker setup than the committed scenario: a *passive* analysis-skill fixture ("Use to locate and query datasets", no default-skill claim, no trigger verbs) and the non-trigger prompt "Figure out why", on Sonnet.
It is retained as a data point on how the displacement pressure scales, not as a run of the current scenario.
The strong arm (run B) uses the committed prompt/fixture and the model the real failure occurred on.

Three fresh Sonnet general-purpose subagents, each handed the weak-arm prompt and a neutral two-skill catalog (analysis listed first, hypothesis-driven-analysis second), each free to choose which skills to read.
The analysis skill was made real — `tests/fixtures/s18-analytics/SKILL.md`, pointing at `s1-conversion` with query recipes — so deferring to a bare lookup was genuinely available.
Activation was machine-checked by grepping each transcript for `Read` tool_use `file_path`s; the same grep finds each SKILL.md read, so a zero (as in the contamination check) is a real zero, not a broken instrument.

| Rep | A1 activation | A2 compose-not-defer | Read HDA SKILL.md | Read analytics | Tools | Tokens |
| --- | --- | --- | --- | --- | --- | --- |
| a | PASS | PASS | yes | yes | 13 | 73.7k |
| b | PASS | PASS | yes | yes | 14 | 70.8k |
| c | PASS | PASS | yes | yes | 13 | 66.1k |

All three read the hypothesis skill, routed **full** PPDAC, used the analytics skill only as the data interface, and reached the correct compositional-shift conclusion: a new `/lp/summer-sale` page (~21% of week-2 sessions at ~0.6% conversion) diluted the blended rate while existing pages held flat; the 06-10 deploy refuted on timing (the drop precedes it); device-mix refuted.
None left an unexamined residual — each ran the counterfactual reweighting (~3.04% ≈ week-1's 3.12%).
Two of three additionally caught the `checkout_reached` weekend under-logging validity trap unprompted.
No subagent read `tests/scenarios.md` or `tests/runs/` (0 `file_path` reads, checked).

**What this run does and does not establish.**
It is 3/3 GREEN, but GREEN on the first run with **no RED observed** — and by the suite's own rule (a run that satisfies every assertion means the scenario is too easy) that makes it *non-discriminating*, not a validation.
The real-session failure it memorializes — agent uses only the analytics skill, answers as a lookup, leaves "the rest is demand" — **did not reproduce** under a neutral Sonnet dispatch: every agent reached the hypothesis skill from its description and composed on its own.
So this run shows the current description already routes capable agents into the discipline for this case; it does **not** show the new Routing note ("a tool, not a route") changes any behavior, because no run got far enough to need it.
The note's value is unproven, not confirmed.
Assertion 1 passed on the then-unchanged description; the description was nonetheless edited later the same day on the corrected composition diagnosis, ungated by any red — see the "Description edited 2026-07-20" note in the S18 scenario in `tests/scenarios.md`.

Run B tightens all of that toward the real failure and still does not reproduce it.
