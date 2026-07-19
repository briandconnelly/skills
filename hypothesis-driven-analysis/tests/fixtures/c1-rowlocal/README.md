# c1-rowlocal — calibration for row-local C1 auditing under vocabulary drift

Calibration fixtures for `tests/score_ledger.py`, issue #73.
When a ledger drifts its claim/status vocabulary, the scorer must still fail closed (exit 1) **and** still audit C1 on every sibling row that parses.
The defect these fixtures pin: a single drifted claim-column token used to suppress C1 across the whole table, so a genuine `causal | REFUTED` violation — the exact thing C1 exists to catch — went unreported behind the parse error.

## Why the claim column, specifically

The scorer validated claim cells in a table-wide pre-pass (`check_claims`) whose failure short-circuited every per-row C1/C2 check.
So an unrecognized **claim** cell (`associative`, `statistical` — the tokens measured across the Eighth–Tenth waves) blinded C1 on the rows beside it.
Status cells were never in that pre-pass; they were already checked per row inside `_check_row`, so a drifted **status** cell (`Best supported`) never blinded C1.
The fix moves both checks into `_check_row` and bails audit-wide only on structural faults — a malformed table grid (no table with the required columns, more than one, a repeated column name, or a row whose cell count does not match the header) or a missing/ambiguous id — where the row grid itself cannot be trusted.
A cell-count mismatch therefore still suppresses the audit table-wide; only an unrecognized claim/status *value* in a well-formed row is row-local.

## Fixtures

Each final ledger carries a genuine `H1 | causal | REFUTED` C1 violation plus one drifted sibling row.

- `final-mixed.md` — sibling `H2 | associative | UNRESOLVED`. **Known positive for the fix**: the drift is in the claim column, which used to blind C1.
- `final-status-drift.md` — sibling `H2 | causal | Best supported`. The status path was never blinded; this pins that it stays row-local and that the near-miss hint fires.

## Expected results

Run from the repository root (paths are repo-root-relative, matching the rest of the suite):

```
D=hypothesis-driven-analysis/tests/fixtures/c1-rowlocal
uv run hypothesis-driven-analysis/tests/score_ledger.py --final $D/final-mixed.md         # exit 1 — C1 on H1 AND parse hint on H2
uv run hypothesis-driven-analysis/tests/score_ledger.py --final $D/final-status-drift.md   # exit 1 — C1 on H1 AND parse hint on H2
```

For `final-mixed.md` the audit-wide-fail version reported only the H2 parse error and stayed silent on H1 — a broken instrument and a clean run looked identical.
Both fixtures must keep C1 on H1 visible: the drifted row fails closed, but it never buys the offending row an exemption from the audit.
The near-miss hint is a non-authoritative repair pointer; the scorer never coerces a drift token to a class.
