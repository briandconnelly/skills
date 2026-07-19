# Transcript evidence — `compare_prereg.py` calibration (issue #78)

The plan-vs-final preregistered-cell comparator `tests/compare_prereg.py` closes the instrument gap recorded in `tests/runs/artifacts/2026-07-18-scenario15-completeness-evidence.md` ("Plan-vs-final diff, arm e"; also flagged in `tests/runs/2026-07-19-scenario15-poststrengthening-e.md` as "the silent plan-row rewording … caught only by manually diffing … no committed instrument requires that diff").
That manual diff is now a committed check.
Everything below is the tool's actual output, re-executed at scoring time against the on-disk fixtures — not carried over from any run's self-report.

## What the checker asserts

For every row present in both the Plan-time and final ledger under the same id, every Hypotheses-table cell and every Tests-table cell except `outcome`/`evidence` (the only sanctioned in-place updates per `references/ledger-template.md`) must be byte-identical after unescaping the cell.
A Plan-time row missing from the final ledger, or a row added only in the final ledger, is reported.
A difference whose row is named by a dated Amendment entry is labelled a candidate amendment for human review, but never auto-passed: any preregistered difference exits 1.
The run fails closed (exit 2) if either ledger's Hypotheses or Tests table cannot be uniquely parsed, carries a repeated or empty id, or the two ledgers do not carry the same columns for a table (exempt columns included — a well-formed Tests table always has Outcome and Evidence at Plan time).

## Calibration fixtures

`tests/fixtures/s15-prereg-drift/` (see its `README.md` for provenance).
Recovered from `s15-post-e.jsonl`, sha256 `8a9129069a04e17d1016ac00ee46e6f895c1be3374f2fe10eb3d3d515029f298`.

- `arm-e-plan.md` — Plan-time ledger, verbatim from the ordinal-11 `Write` (11,184 chars).
- `arm-e-final.md` — final ledger, the ordinal-18 outcome-fill `Edit` applied to that plan. **Known positive**: the fill silently reworded eight preregistered Tests cells.
- `arm-e-final-clean.md` — **known negative**: the same plan with only `outcome`/`evidence` filled, every preregistered cell left identical.

## Verbatim output

### Known positive — arm-e-plan.md vs arm-e-final.md

```text
DIFFERENCES:
  - CHANGED [reworded]: Tests row T1, column 'method' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : 'Compute naive medians/means, then a worst-case bound imputing missing (still-open) durations, then severity-stratified contrasts'
    final: 'Naive (closed-only) medians/means by workflow, then severity-stratified medians/means, then severity-mix-reweighted aggregate'
  - CHANGED [reworded]: Tests row T1, column 'preregistered prediction' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : 'Adjusted contrast (censoring bound + mix control) still shows Assist faster'
    final: 'Adjusted contrast (severity-mix control) still shows Assist faster'
  - CHANGED [reworded]: Tests row T3, column 'method' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : "Cross-tab missing-row incidents by workflow and severity vs. each arm's population rate"
    final: "Cross-tab missing-row incidents by workflow and severity vs. each arm's population rate; compare age-at-extract of missing incidents against the max observed closed duration"
  - CHANGED [reworded]: Tests row T4, column 'method' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : "Compare composition tables; reweight one week's severity mix onto the other's per-severity medians"
    final: "Compare composition tables; reweight one week's severity mix onto the other's per-severity means"
  - CHANGED [reworded]: Tests row T5, column 'method' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : 'Compare responder-minutes and reopened_within_72h/handoffs distributions manual vs assist, closed incidents only, stratified by severity'
    final: 'Compare responder-minutes, handoffs, reopened_within_72h manual vs assist, closed incidents only, stratified by severity'
  - CHANGED [reworded]: Tests row T5, column 'preregistered prediction' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : 'An independent slice (e.g., responder-minutes, which the censoring bound does not directly touch the same way, or handoffs/reopen rate as secondary signals) corroborates or fails to corroborate the direction of T1'
    final: "An independent slice (responder-minutes, handoffs, reopened_within_72h, stratified by severity) corroborates the direction of T1's naive improvement"
  - CHANGED [reworded]: Tests row T6, column 'method' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : 'Filter to severity=sev1 and closed (has activity row), compare responder_minutes/handoffs assist vs manual'
    final: 'Filter to severity=sev1 and closed (has activity row); compare responder_minutes, handoffs, reopened_within_72h assist vs manual'
  - CHANGED [reworded]: Tests row T6, column 'preregistered prediction' -- UNEXPLAINED -- no dated amendment names this row (fail closed)
    plan : "Among closed sev1 incidents, assist responder-minutes/handoffs exceed manual's"
    final: "Among closed sev1 incidents, assist responder-minutes and/or handoffs exceed manual's"
checked:
  - Hypotheses table compared: 5 shared row(s) across 8 immutable column(s) (candidate explanation, cheapest adequate test, claim, data needed, id, necessary prediction (failure refutes), prediction if false, prediction if true); 0 plan-only, 0 final-only
  - Tests table compared: 6 shared row(s) across 4 immutable column(s) (hypothesis, id, method, preregistered prediction); 0 plan-only, 0 final-only
exit=1
```

The eight caught cells are exactly the ones the manual Tenth-wave diff named (T1 dropped censoring bound, T4 medians→means, T5 independent-slice rewording, T6 `/`→`and/or`), plus the T1/T5/T6 method rewordings and the T3 method extension the manual diff summarised.
The Hypotheses table compared clean, matching the manual finding that it was byte-identical across the outcome fill.

### Known negative — arm-e-plan.md vs arm-e-final-clean.md

```text
OK: no preregistered cell changed between plan and final
  - Hypotheses table compared: 5 shared row(s) across 8 immutable column(s) (candidate explanation, cheapest adequate test, claim, data needed, id, necessary prediction (failure refutes), prediction if false, prediction if true); 0 plan-only, 0 final-only
  - Tests table compared: 6 shared row(s) across 4 immutable column(s) (hypothesis, id, method, preregistered prediction); 0 plan-only, 0 final-only
exit=0
```

The instrument passes a ledger that filled only the sanctioned `outcome`/`evidence` cells, so the exit-1 above is a real detection, not a checker that fails everything.

## Fail-closed branch checks (synthetic)

Each exercised at scoring time by deriving a one-off fixture from `arm-e-plan.md`; results confirm the exit contract.

| case | derivation | expected | observed |
| --- | --- | --- | --- |
| covered change | rewrite T6 prediction + add a dated Amendment naming T6 | exit 1, `CANDIDATE AMENDMENT` | matched |
| deleted row | final drops the T6 Tests row | exit 1, `DELETED` | matched |
| added row | final inserts a T7 Tests row absent from the plan | exit 1, `ADDED` | matched |
| duplicate id | final repeats a T1 Tests row | exit 2, `UNVERIFIABLE` (repeated id) | matched |
| formatting-only | backticks added around a field name in a T2 prediction | exit 1, `[formatting-only]` label | matched |
| column mismatch | final Tests header carries an extra column | exit 2, `UNVERIFIABLE` (column sets differ) | matched |
| unreadable file | `--final` points at a nonexistent path | exit 2, `UNVERIFIABLE` (cannot read) | matched |
| Hypotheses reword | a Hypotheses `prediction if true` cell edited | exit 1, `CHANGED … Hypotheses` | matched |
| backslash-pipe | plan cell `\\|` vs final `\|` (one backslash dropped) | exit 1 (difference detected, not collapsed) | matched |

## Cross-model review

A Codex review of `compare_prereg.py` (via `codex_review_changes`) found two paths by which a genuinely reworded preregistered cell could have returned exit 0, both since fixed and covered by the last two rows above:

- The `outcome`/`evidence` exemption was applied to both tables, so a Hypotheses column named `outcome`/`evidence` would have been exempted against the stated rule that every Hypotheses cell is immutable. Now exempted only for the Tests table.
- Cells were unescaped a second time here even though `score_ledger.parse_tables` already unescapes them; the second pass is not idempotent (`\\|` → `\|` → `|`) and could collapse a real difference. Now the cells are compared as the parser returns them. Confirmed by live demonstration before the fix: `\\|` and `\|` compared equal under the double unescape and unequal under a single one.

## Lint / type

`uvx ruff check`, `uvx ruff format --check`, and `uvx ty check` all pass on `tests/compare_prereg.py` under the repo's `ruff.toml` gate.
