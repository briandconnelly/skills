# C4 calibration — positive-contradiction adequacy (issue #85)

C4 (score_ledger.py) fails closed when a hypothesis whose refutation rests on a
positive/distributional contradiction is marked REFUTED without recording the
documented `adequacy: <rate> ± <uncertainty> (variants: <range>)` atom beside its
outcome. It is opt-in via `--c4-positive-contradiction H<n>`, the caller's
attestation that the named hypothesis is a positive contradiction (a deterministic
refutation is exempt and must not be flagged).

Calibrate before trusting the check:

- `positive-no-bound.md` — known positive: H4 REFUTED, no atom. Flagged → C4 FAILS.
  This is the skipped-estimate route the two old-wording S6 arms took ("a full
  census, so no check triggered").

  `uv run ../../score_ledger.py --final positive-no-bound.md --plan plan.md --c4-positive-contradiction H4`  → FAIL (C4)

- `negative-bound-recorded.md` — known negative: same row, atom recorded in the
  CONTRADICTED Tests Evidence cell. Flagged → C4 PASSES.

  `uv run ../../score_ledger.py --final negative-bound-recorded.md --plan plan.md --c4-positive-contradiction H4`  → OK

- `negative-deterministic.md` — known negative: a legitimate deterministic timing
  refutation (H1). UN-flagged → C4 never sees it; the run is clean. This is the
  over-correction guard: C4 must not fail a legitimate refutation.

  `uv run ../../score_ledger.py --final negative-deterministic.md --plan plan.md`  → OK

- `negative-na.md` — known negative: `adequacy: N/A (variants: none)` passes the
  syntactic presence check by design (quality is the rubric grader's job, exactly
  as `estimand: N/A` is for C2).

  `uv run ../../score_ledger.py --final negative-na.md --plan plan.md --c4-positive-contradiction H4`  → OK

`plan.md` is the shared Plan-time ledger so the descriptive REFUTED rows also clear
C2 (they trace to a Plan-time id + class naming a non-empty estimand).
