# s2-run: median order value in June

## Routing

Read `hypothesis-driven-analysis/SKILL.md` routing table and the "Two questions
separate the three cheap routes" section.

The skill gives this exact question as its own worked example of the **direct**
route: "What was the median order value in June" has not [asserted a claim] —
compute it, answer, stop.

Confirmed against the routing criteria independently:
- No claim is being adjudicated (nobody asserted a number to check).
- The answer is a fact the records themselves settle: the median of the
  amount column for June rows, computed directly from the CSV — no
  explanatory/causal inference, no generalization past what the file
  contains.
- Collection is not costly: local fixture file, no price/quota/latency
  constraint stated or observed.

=> Route: **direct**. Ceremony: none — answer and stop. No ledger required.

## Data

Source: `/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s1-conversion/orders.csv`
Columns: order_id, timestamp, amount, client_version.

## Computation

```python
import csv, statistics
path = ".../orders.csv"
rows = list(csv.DictReader(open(path)))
total = len(rows)                                  # 268
june = [r for r in rows if r["timestamp"].startswith("2026-06")]
non_june = total - len(june)                        # 0
amounts = sorted(float(r["amount"]) for r in june)
median = statistics.median(amounts)
```

Results:
- total rows: 268
- june rows: 268
- non-june rows: 0
- timestamp range: 2026-06-01T08:24:00Z .. 2026-06-14T16:54:00Z
- n amounts: 268 (even count -> median = mean of 134th/135th sorted values)
- **median amount: 76.36**

## Answer

Median order value in June: **$76.36** (n = 268 orders, all rows in the
fixture fall within June 2026).
