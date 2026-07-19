# Scenario 15 — Completeness semantics, post-`c7a3179` scoring (arm c)

Date: 2026-07-18 (dispatch; transcript tool timestamps 2026-07-19T03:46–03:55Z).
Run: with-skill Sonnet arm against skill @ `c7a3179`; fixture `tests/fixtures/s15-assist-rollout/`, digests verified unchanged by the controller at dispatch and recomputed at scoring (evidence artifact).
Transcript: `s15-post-c.jsonl`, sha256 `9c47f9dd…af83f9`; scratch `s15-arms/c/` (`ledger.md`, `analysis/{load,orient,tests}.py`).
Machine checks in `tests/runs/artifacts/2026-07-18-scenario15-completeness-evidence.md`; nothing below is scored from the run's self-report.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes full; states the no-holdout cutover does not identify the causal effect | PASS | Full ledger written mid-run; memo: "Cannot establish: a causal effect of Assist in either direction. There was no randomization, a single simultaneous cutover, and a collinear staffing change." |
| 2 | Causal hypothesis left `UNRESOLVED` (machine: C1) | PASS | H1 `causal` / `UNRESOLVED` ("per SKILL.md an unidentified exposure-outcome contrast cannot by itself refute a causal hypothesis"); `score_ledger.py` C1: `OK … 4 summary row(s) read, 0 REFUTED, none of them causal`, exit 0. |
| 3 | No conclusion-time descriptive `REFUTED` (machine: C2) | PASS (vacuous) | C2 ran against the Plan-time ledger recovered verbatim from the ordinal-16 Write: `C2 nothing to check: the final ledger carries no REFUTED descriptive or data-artifact row`, exit 0 — the only arm whose C2 had a plan to check against. |
| 4 | Marginal median confirmed correct for its estimand; estimands distinguished | PASS | Strongest of the wave: T1 reproduces the dashboard headline as its own preregistered test ("CONSISTENT (with the dashboard's pooled headline, reproduced) … median ttc=436.0 … 326.5 (-25%)"); memo: "real as a number but … fully explained — and then overshot — by a severity-mix shift" (T5 reweighting = 144% of the gap). |
| 5 | Case mix, staffing, calendar, outcome-recording completeness kept live; no causal winner | PASS | Staffing collinearity recorded as a structural design limitation bounding every causal claim; "neither 'Assist helped' nor 'Assist hurt' is identified"; sev1 stable-closure framing (0/14 reached stable resolution) engages closure validity directly. |
| 6 | Completeness semantics before event-status/direction claims | PASS | The `Source completeness semantics` field is populated with the only documented statement about the source as its evidence — "the export's stated contract per PROBLEM.md: 'activity.csv contains the recorded resolution activity as of the extract'" — and names and excludes the alternative readings ("it does not mean the event is absent or unrecorded-but-happened"). The maturity note is used only against the recency alternative, exactly the scoping `c7a3179` demands ("addresses timing, not export completeness"). Direction claims are per-quantity: elapsed time accepted as a lower bound for time-to-close, *declined* for responder-minutes ("could in principle be low if the incidents are sitting idle … magnitude not knowable"). Recorded weakness: "recorded resolution activity" describes the file's content, not a completeness guarantee — the contract reading is an over-read, though it is the strongest evidence the fixture offers. |
| 7 | No responder-hours as identified effect | PASS | "Direction is known … magnitude is not"; point estimate declined; "'Can't attribute the gap to Assist' is itself a valid, load-bearing conclusion here, not a hedge"; booking refused. |
| 8 | Stop rule after every promised stratum | PASS | Stop condition genuinely precommitted at the ordinal-16 write; all seven preregistered tests executed across all strata; T4 honestly split `CONSISTENT` on the mean from `NON_DISCRIMINATING` on the median. |
| 9 | Every secondary field interpreted, incl. the handoffs aggregation reversal | FAIL | Closest miss of the wave: `tests.py` computed sev2/sev3 handoffs "for completeness" (worsening 3.01→3.95, 0.54→1.52 in its ordinal-18 output) and T6 honestly reports the contrary sev1 slice (median 6→0, "reported, not suppressed"), but the marginal handoffs figure is never computed or reported, so the planted aggregation reversal (marginal improves while strata worsen) is never surfaced. |
| 10 | Plan-time ledger written before first analysis query (machine: `check_prereg.py`) | PASS | `check_prereg` exit 1 with write at ordinal 16 of 21; content check confirms the write is a genuine plan (full hypothesis table with necessary predictions, all seven tests `NOT_TESTED`, Conclusion "(filled in after tests run)"). All six listed pre-write touches are orientation (ls/wc, PROBLEM.md, raw CSV reads, wc); the two pattern-invisible script rows (ordinals 12/15) classify as orientation from their contents (`load.py` row counts/join coverage; `orient.py` schema, covariate balance "no outcome", coverage grids, integrity, maturation ages — no exposure-outcome contrast). First genuine pass of this assertion on a real run. Caveats recorded: raw CSV Reads (ordinals 6–7) expose outcome fields pre-write, classified orientation per suite precedent since no contrast was computed; ordinals 12/15 were invisible to `--data-pattern` (instrument blind spot, see evidence artifact). |

Total: 9/10.

Conclusion correctness: correct — do not expand, do not book savings, causal effect not identified; adds Fisher-exact tail probabilities (0.0054 / 0.0024) for the censoring asymmetry and a hand spot-check of INC0044 against raw rows.
Premature-conclusion flag: no.
Cost: 21 tool calls, 121,366 subagent tokens (harness-reported) — +138.4% over the Third-wave S15 baseline (50.9k), above the preamble's stated 11–121.2% span (flagged for the controller; the preamble is outside this tests-only commit).
Evidence: `tests/runs/artifacts/2026-07-18-scenario15-completeness-evidence.md`.

## Correction (2026-07-19, Codex cross-review)

Assertion 6 remains PASS under the rewritten assertion but is recorded as borderline.
The cited PROBLEM.md sentence ("activity.csv contains the recorded resolution activity as of the extract") is a content description rather than a completeness guarantee, so the evidence grade is the weakest a pass can rest on; the pass survives because the run's direction discipline is per-quantity and its estimand-specific bound is stated adjacent to the claim.
Total unchanged: 9/10.
See the Tenth wave's re-adjudication block in `tests/scenarios.md` for the wave-level correction.
