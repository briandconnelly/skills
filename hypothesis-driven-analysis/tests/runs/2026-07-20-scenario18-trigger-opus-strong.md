# Scenario 18 run B — 2026-07-20 (trigger, 3 reps, Opus 4.8) — strong arm, committed scenario

Date: 2026-07-20.
Run: trigger-discrimination, committed strong arm; supersedes run A (`2026-07-20-scenario18-trigger-sonnet-weak.md`).
Model: Opus 4.8, the model the observed failure occurred on.
Fixture: `tests/fixtures/s18-analytics/SKILL.md` (assertive default-skill stand-in) pointing at `tests/fixtures/s1-conversion/`.

The RED attempt, built from the real conflicting skill's *shape* (reported by the maintainer): an assertive "analysis" fixture that declares itself the **default** skill for analytical questions and triggers on "break it down" / "how much" / "analyze or summarize", listed first; the committed prompt "Break it down and tell me what's driving it" (the trigger verb over a genuine *why*); and Opus 4.8, the model the observed failure occurred on.
The real skill's own text is deliberately absent — it is internal and closed-source; only the generic pattern is reproduced.
One dimension of the observed session is **not** reproduced: reasoning effort.
The dispatch harness sets the subagent model but not effort, so these ran at the subagent default, not the observed High.

| Rep | A1 activation | A2 compose-not-defer | Read HDA SKILL.md | Read analysis | Tools | Tokens |
| --- | --- | --- | --- | --- | --- | --- |
| a | PASS | PASS | yes | yes | 10 | 71.9k |
| b | PASS | PASS | yes | yes | 8 | 63.1k |
| c | PASS | PASS | yes | yes | 7 | 59.6k |

All three read the hypothesis skill despite the aggressive default-skill competitor listed first, routed **full** PPDAC, and used the analysis skill only as the data interface.
Conclusions were strong: per-landing-page decomposition (one used a named Kitagawa decomposition), the counterfactual reweighting closing ~86–109% of the drop, the 06-10 deploy refuted on timing, the desktop "collapse" correctly identified as a Simpson's-paradox artifact of campaign mix, and the `checkout_reached` logging anomaly caught unprompted (one tied it to the 06-12 logging deploy).
No unexamined residual; causal caveats stated.
No subagent read `tests/scenarios.md` or `tests/runs/` (0 `file_path` reads, checked).

**Verdict: 6/6 GREEN across both arms, and the failure still did not reproduce.**
Strengthening the competitor to a self-declared default skill with matching trigger verbs, using the trigger-shaped prompt, and moving to Opus 4.8 did not make any agent defer — each reached the discipline from its description and composed.
Consequences, unchanged from run A and now on stronger evidence:

- The new Routing note ("a tool, not a route") remains **unexercised**: no run activated-then-deferred, so nothing tested the note. It is cheap defense-in-depth, not a validated fix.
- Assertion 1 passed on the **then-unchanged description** even against the default-skill competitor — so selection was not the out-of-harness failure mode. (The description was still edited later that day on the corrected composition diagnosis, ungated by any red; see the "Description edited 2026-07-20" note in the S18 scenario in `tests/scenarios.md`. This bullet does not say the edit was unwarranted — the corrected diagnosis, not this run, motivates it.)
- The scenario is still **non-discriminating** (too easy) by the suite's own rule. The one variable left unreproduced is reasoning effort; a harness that can dispatch a subagent at a pinned effort, or the real skill auto-invoked by the harness before the agent chooses, are the remaining levers to try before concluding the failure is not description-addressable.

Treat the composition fix as **untested**, not confirmed: 6/6 GREEN here measures that the failure is hard to reproduce out-of-harness, not that the note prevents it.

Evidence (per-rep scores, manifest greps with known-positive validation, conclusion content, both arms): `tests/runs/artifacts/2026-07-20-scenario18-evidence.md`.
