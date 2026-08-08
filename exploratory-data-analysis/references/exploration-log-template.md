# Exploration Log Template

Create the log at Frame time, before the first look.
Create means write: the log exists as a file before any exploration output, so the precommitment leaves a record the transcript can verify — a log first materialized in the final report is a reconstruction.
The looks register and amendments are append-only; a lead row's `disposition` is the only sanctioned in-place update.
Keep it in scratch space by default, named recognizably (e.g. `exploration-log.md`); put it in the project directory when the user wants a durable artifact.
The profile route fills only Frame-lite (scope and budget) and the Orientation record.

## Template

```markdown
# Exploration: <one-line goal>

## Frame

- Goal: <what a useful lead would look like; the decision or audience served, if any>
- Scope: <dataset(s), timeframe, units>
- Effort budget: <tool calls | queries | wall-clock — pick one and a number>
- Stop rule: <precommitted condition for stopping>
- Confirmation reservation: <the holdout — later window, unexamined slice, independent source — Explore will not touch; or "none feasible: <why>">

## Orientation record

| id | Origin (file, query, system) | Acquired | Notes |
| --- | --- | --- | --- |
| S1 | ... | ... | ... |

- Schema and grain: <tables, keys, one row means ...>
- Quality: <missingness, duplicates, sentinel values found>
- Coverage: <at the exploration grain, against an expected schedule or independent denominator — or "unverifiable: <why>">
- Absence semantics: <per source whose absent records could bear on a lead: event absent | event unrecorded | export incomplete | UNKNOWN — why no evidence discriminates>
- Instrument caveats: <exporters, sampling, dashboards>

## Looks register

| id | Family | Examined | Comparisons exposed | Note |
| --- | --- | --- | --- | --- |
| L1 | ... | ... | ... | ... |

## Leads

| id | Statement (associational) | Class | Evidence | Search context | Alternatives noted | Cheapest confirming test | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | ... | pattern | L... | ... | ... | ... | reported |

## Amendments

- <date>: <what changed and why — budget extension, reservation change, route change>
```

## Worked example (abridged)

```markdown
# Exploration: what does orders.csv suggest about our store?

## Frame

- Goal: leads worth confirming about ordering behavior; serves the growth team's next-quarter planning.
- Scope: orders.csv, 2026-01-01..2026-06-30, one row = one order.
- Effort budget: 20 queries.
- Stop rule: stop at budget, or earlier when two consecutive families yield no new candidate.
- Confirmation reservation: June rows untouched; explore January–May only.

## Orientation record

| id | Origin (file, query, system) | Acquired | Notes |
| --- | --- | --- | --- |
| S1 | orders.csv (user-provided export) | 2026-08-08 | 41,213 rows |

- Schema and grain: order_id, timestamp, amount, region, device; one row = one order.
- Quality: no duplicate order_ids; amount has 14 zero rows (sentinel?); device null for 3% of rows.
- Coverage: daily row counts vs the site's published order-volume dashboard — matches within 2% except 03-14 (export gap, 60% low).
- Absence semantics: S1 UNKNOWN — no export contract checked; absence of a day's rows cannot distinguish no-orders from dropped-rows.
- Instrument caveats: amounts are pre-refund.

## Looks register

| id | Family | Examined | Comparisons exposed | Note |
| --- | --- | --- | --- | --- |
| L1 | univariate | amount distribution (all, Jan–May) | 1 | right-skewed, zero spike |
| L2 | time | weekly order counts by region | 24 | EU flat, NA rising |
| L3 | segment | amount by device × region table | 8 | mobile-EU low |

## Leads

| id | Statement (associational) | Class | Evidence | Search context | Alternatives noted | Cheapest confirming test | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Mobile-EU orders average ~30% lower amounts than other segments in Jan–May | pattern | L3 | 3 looks, 3 families, ~33 comparisons | currency mix; the 14 zero-amount rows sit in this cell | recompute on reserved June rows | handed-off |
| D2 | 03-14 export gap (60% low vs dashboard) | data-quality | Orientation | n/a — found in Orient | none | ask the export owner for the 03-14 job log | reported |

## Amendments

- (none)
```
