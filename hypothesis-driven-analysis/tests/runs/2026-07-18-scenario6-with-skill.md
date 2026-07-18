# Scenario 6 — Underpowered null with a distributional trap, With-Skill Scoring

Date: 2026-07-18
Run: with-skill treatment against the tightened fixture (issue #67). Model: Sonnet. Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, see the 2026-07-18 artifact file).
Files read (machine-checked from the transcript): `SKILL.md`, `references/ledger-template.md`, the fixture CSV — nothing else.
Supersedes nothing: the 2026-07-16 S6 rows scored the pre-tightening fixture and do not carry over.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument (or a demonstrated known-positive check before trusting a null) | FAIL | Ran the skill-prescribed known-positive check and built it invalidly: "a synthetic +30ms shift applied to the same data was caught by the identical method in 100% of simulated resamples… confirming the method's detection limit is ≤30ms." The procedure (transcript tool_use 8) shifts the *same observed sample* +30ms and resamples it, which collapses between-sample variability. Scorer reproduction: the run's procedure yields 99.7%, but the true power of its CI-excludes-200 test under a genuinely shifted population is ≈77%; the exact binomial 95% CI [177.6, 252.9] contains 230, and a sign test against median=230 gives p=0.117 — the sample cannot resolve the claim. |
| 2 | No-difference result recorded as `NON_DISCRIMINATING` with detection limit, not as refutation | FAIL | Ledger records T1 as `CONTRADICTED` for H1 and the summary marks H1 "**REFUTED** … (positive-control +30ms shift detected 100% of 2,000 sims, so the null wasn't a power artifact)". The misclassification follows directly from the invalid sensitivity check; the correct outcome for T1 at ~77% power with 230 inside the CI is `NON_DISCRIMINATING` with the ~50ms limit stated. |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | PASS | The distinction is drawn explicitly and maintained: "the data cannot rule out that something real happened and is either fading or hiding in the tail"; "'the rebuild did nothing' isn't established either. This is a **stop-with-limits** case." The unsound refuted branch is scored at assertions 1–2, not here. |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | Dedicated hypothesis H4 with "p95=662ms, p99=688ms, 6/41 (14.6%) of samples >500ms, mean 267ms vs. median 202ms"; the answer states the 600–700ms band and that the tail "inflates the mean… plausibly exactly what users are noticing." |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; discriminating evidence named | PASS | T3 recorded `NON_DISCRIMINATING`: "no pre-rebuild tail data exists"; H4 kept unresolved with "attribution to the rebuild is untestable here"; names the settling evidence (retain p95/p99 and raw distributions; re-sample 24–48h post-rebuild). The incidental time drift was correctly labeled a `retrospective` hypothesis (H2) and left `UNRESOLVED`. |

Total: 3/5.

Cost: 9 tool calls, ~61.1k subagent tokens, 364s. Token delta vs. baseline: +72%.

**Both failures are findings against the skill, not the agent** (methodology, top of `scenarios.md`).
SKILL.md's sensitivity rule — "the same method surfaces a known positive comparable in size and grain to the predicted effect" — was followed to the letter: the agent constructed a known positive and its method surfaced it.
The rule does not say the known positive must model *between-sample variability*, so a positive control built by shifting the observed sample and resampling it passes the rule while overstating power (100% claimed vs. ≈77% actual here), which then licenses `REFUTED` where the ground truth is `NON_DISCRIMINATING`.
The unstructured baseline failed the same three assertions by a cruder route, so the scenario discriminates in the right direction; but the skill's margin on its own home turf (null-result discipline) is now measured at one assertion, and the fix belongs in the sensitivity rule's wording.
Filed as a follow-up issue rather than patched in this branch, so the wording change gets its own measurement.

**Two behaviors worth keeping visible:** the run self-labeled its post-hoc warm-up hypothesis `retrospective` and refused to promote it without held-out data, and it kept the tail hypothesis alive as the plausible driver of user perception — both exactly what the skill exists to produce.
