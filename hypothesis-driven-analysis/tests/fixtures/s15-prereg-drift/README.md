# s15-prereg-drift — calibration pair for `compare_prereg.py`

Calibration fixtures for the plan-vs-final preregistered-cell comparator (`tests/compare_prereg.py`, issue #78).
The comparator must fail on a ledger whose preregistered cells were silently reworded at outcome-fill time and pass on one where only the sanctioned `outcome`/`evidence` cells changed.
A checker that cannot do both is uncalibrated: a broken instrument and a clean ledger look identical.

## Provenance

The pair is recovered from the archived scenario-15 arm e transcript `s15-post-e.jsonl`, sha256 `8a9129069a04e17d1016ac00ee46e6f895c1be3374f2fe10eb3d3d515029f298` — the same transcript scored in `tests/runs/2026-07-19-scenario15-poststrengthening-e.md` and diffed by hand in `tests/runs/artifacts/2026-07-18-scenario15-completeness-evidence.md` (the "Plan-vs-final diff, arm e" section), which is the manual finding this instrument now automates.

- `arm-e-plan.md` — the Plan-time ledger, verbatim from the ordinal-11 `Write` (11,184 chars; the size recorded in the evidence artifact). Every Tests row reads `NOT_TESTED` with an empty Evidence cell.
- `arm-e-final.md` — the final ledger, reconstructed by applying the ordinal-18 outcome-fill `Edit` (a single `old_string`→`new_string` replacement) to the ordinal-11 plan. This is the **known positive**: its outcome fill also silently reworded eight preregistered Tests cells (T1/T3/T4/T5/T6 prediction and/or method — the T1 censoring bound dropped, T6's `/` widened to `and/or`) while Amendments reads "(none …)". The Hypotheses table is byte-identical to the plan's.
- `arm-e-final-clean.md` — the **known negative**, derived from the same plan by filling only the sanctioned cells: each Tests row's `outcome` and `evidence` are taken from `arm-e-final.md` and the Conclusion is filled, but every preregistered cell is left byte-identical to the plan. This is the ledger arm e should have written.

## Expected results

Run from the repository root (paths are repo-root-relative, matching the rest of the suite):

```
D=hypothesis-driven-analysis/tests/fixtures/s15-prereg-drift
uv run hypothesis-driven-analysis/tests/compare_prereg.py --plan $D/arm-e-plan.md --final $D/arm-e-final.md        # exit 1 — 8 CHANGED cells
uv run hypothesis-driven-analysis/tests/compare_prereg.py --plan $D/arm-e-plan.md --final $D/arm-e-final-clean.md   # exit 0 — no cell changed
```

Verbatim tool output for both is archived in `tests/runs/artifacts/2026-07-19-scenario15-prereg-comparator-evidence.md`.
