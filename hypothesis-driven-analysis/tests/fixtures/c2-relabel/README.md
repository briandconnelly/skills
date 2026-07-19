# c2-relabel — calibration for the C2 claim-class relabel check

Calibration fixtures for the C2 (status-laundering) check in `tests/score_ledger.py`.
C2 must catch both shapes of laundering a REFUTED into the conclusion: inventing a claim at conclusion time (a new id), and **relabelling an existing hypothesis's claim class**.
The relabel shape traces to the same Plan-time id, so the id check alone waves it through — the class-match check is what closes it.

## Why this matters

A `causal` row cannot be C1-REFUTED under the scorer's scope (see the SCOPE section of `score_ledger.py`).
Re-dressing a Plan-time `causal` row as `data-artifact` at conclusion time lets a `REFUTED` ride into the ledger on a class C1 does not police.
Before this check, that relabel scored a clean `C2 checked and passed`.

## Fixtures

All three share `plan.md` (Plan-time: H1 `causal`, H2 `descriptive`).

- `final-relabel.md` — **known positive**: H1 relabelled to `data-artifact | REFUTED` under the same id. Must fail C2.
- `final-clean.md` — **known negative**: H2 carries a legitimate `descriptive | REFUTED` in the same class and estimand it was preregistered under; H1 stays `causal | UNRESOLVED`. Must pass.

## Expected results

Run from the repository root:

```
D=hypothesis-driven-analysis/tests/fixtures/c2-relabel
uv run hypothesis-driven-analysis/tests/score_ledger.py --final $D/final-relabel.md --plan $D/plan.md   # exit 1 — C2 relabel laundering on H1
uv run hypothesis-driven-analysis/tests/score_ledger.py --final $D/final-clean.md   --plan $D/plan.md   # exit 0 — legitimate descriptive REFUTED
```

The check only fires when a REFUTED `descriptive`/`data-artifact` conclusion row's class differs from its Plan-time class, so a correct ledger — which never relabels — never trips it.
