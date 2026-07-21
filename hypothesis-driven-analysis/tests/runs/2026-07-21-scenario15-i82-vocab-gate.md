# Scenario 15 — issue #82 vocabulary gate: does claim-class drift persist under the #73/#84 wording?

Date: 2026-07-21 (dispatch and scoring same session).
Purpose: the measurement issue #82 defers on — PR #84 (`8f0c22d`) added SKILL.md wording naming the closed claim-class set and redirecting `associative`/`statistical`; no ledger-producing run had exercised it, so the rename proposal was gated on this run.
Scope: this wave scores the vocabulary gate only — ledger parse under `score_ledger.py` and C1 — not S15's full ten-assertion table; no plan-time ledger was archived, so C2/`check_prereg`/`compare_prereg` were out of scope by design.

## Design

Three free with-skill Sonnet arms against skill @ `9f48a9f` (HEAD, post-#84), S15 prompt verbatim, fixture `tests/fixtures/s15-assist-rollout/` read-only, one scratch directory per arm (the S16/#72 shared-output race avoided).
The known positive validating the free-run instrument is the Tenth-wave arm d record (`2026-07-19-scenario15-poststrengthening-d.md`): same scenario, same dispatch shape, skill @ `b8602fb` (pre-#84), drifted `associative` into a claim cell.
Ten focused decision-point probes were run alongside, per the #72 probe method: an identical neutral prompt (write the Hypotheses and per-hypothesis summary tables for the S15 situation, with an "associative-only" H5 and a "statistical artifact of aggregation" H2 as the measured temptations), five arms on SKILL.md @ `31b345e` (pre-#84) and five @ HEAD.

## Results

| Arm | Skill | Ledger/tables parse | Drift tokens in claim/status cells | Tool calls | Tokens |
| --- | --- | --- | --- | --- | --- |
| free a | HEAD | `score_ledger.py` OK, C1 passed (3 summary rows, 0 REFUTED), exit 0 | none | 16 | 78.2k |
| free b | HEAD | OK, C1 passed (4 summary rows, 0 REFUTED), exit 0 | none | 15 | 77.1k |
| free c | HEAD | OK, C1 passed (5 summary rows, 0 REFUTED), exit 0 | none | 17 | 78.4k |
| probe old 1–5 | `31b345e` | all clean | none | 4 ea | 53.2–56.7k |
| probe new 1–5 | HEAD | all clean | none | 4–5 ea | 56.9–61.4k |

Instrument validation for the negative result, both directions:

- Free-run instrument: `score_ledger.py` was re-run against a mutated copy of arm a's ledger with one claim cell set to `associative`; it fails at parse with the near-miss hint and exit 1, so the scorer catches the exact drift class in the exact ledger format these arms produce.
- Probe instrument: the pre-#84 control arm produced 0/5 drift, so the probe never reproduced its known positive and is **non-discriminating** — probe results carry no evidential weight either way, and the probe-vs-free contrast itself measures something: small-context probes read the template and copy its vocabulary, while drift historically appeared in full free runs under context pressure, consistent with the #73 finding that treatment runs follow SKILL.md's inline text and skip the reference.

## Verdict on the issue #82 gate

Drift did not recur in 3/3 free ledger-producing runs under the current wording, measured by the same scorer that fails the known positive; C1 evaluated 3/3, where the Tenth-wave arm d under the pre-#84 wording drifted.
What this identifies is bounded: three SKILL.md commits landed between #84 and HEAD (#86, #89, #90), the historical arm is not a contemporaneous control, and the only contemporaneous old-wording arms were the non-discriminating probes — so this wave measures the absence of drift under HEAD's wording as a whole, not #84's sentences in isolation.
That is nonetheless the question #82's gate asks — "measure whether drift persists under that wording before taking on a rename" — since a rename is only warranted if drift persists in what runs actually read today.
The suite's honest limit on the n: if arms were independent and the current per-arm drift probability equaled the historical point estimates — 1-in-3 (Tenth-wave S15, arm d of three) or 1-in-7 (Eighth-wave S6, ws-g of seven) — a clean 3/3 would miss a persisting drift with probability (1−p)³ ≈ 30% or ≈ 63% respectively; those are observed proportions from different scenarios, not calibrated bounds, so read 3/3 as evidence, not proof of extinction.
Recommendation recorded for the controller: close #82 — its gating measurement found no drift under the current wording, and the rename's measured blast radius (scorer column tuples, four fixtures, ~80 historical run ledgers) is not justified by an unobserved failure — and re-open if any future wave's ledger fails parse on claim-class drift, which the row-local handling from #84 already caps at one unscored row per occurrence.

Deviation noted, not scored: free arm c annotated one `data-artifact` claim cell with an estimand suffix (`data-artifact (estimand: ...)`) in its Hypotheses table; the template reserves that annotation for `descriptive` rows, the summary table was conformant, and the scorer accepts it — recorded as a template-grammar observation, not #73-class drift.

Evidence: `tests/runs/artifacts/2026-07-21-scenario15-i82-vocab-evidence.md` (digests, verbatim scorer output, summary tables, mutation check).
Token counts are harness-reported per the suite's convention.
