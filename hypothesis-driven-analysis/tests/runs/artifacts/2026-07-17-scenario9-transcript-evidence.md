# S9 (estimation routing) — transcript evidence, historical only

Grounds the S9 rows in `tests/scenarios.md` (First wave).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

**These transcripts are historical evidence for the old prompt and the old routing table, nothing more.**
The S9 prompt changed on 2026-07-16 (it now states randomized assignment), `tests/scenarios.md` records that the earlier runs do not carry over, and the corrected S9 remains unrun on the current routing table.
Nothing in this file is evidence that the current S9 assertions pass; a run reaching `estimation` under the old prompt was reading randomization into "A/B", which the current skill text forbids.

## Machine-checked counts and facts

| Run | Tool calls | Bash | Read | Write | Result statuses | Ledger-structure predicate matches in output |
| --- | --- | --- | --- | --- | --- | --- |
| s9-baseline | 4 | 3 | 1 | 0 | 4 ok | 0 |
| s9-with-skill | 5 | 3 | 2 | 0 | 5 ok | 0 |

Both counts match the recorded cells (4 and 5).
Neither run made a Write or Edit, and neither run's assistant text matches the ledger-structure predicate `^\| H[0-9]|^#+ +Hypotheses|^#+ +(Sources|Tests|Amendments)\b` (the same predicate fires 8 times on the s12-rerun transcript, so the zero is a working instrument's zero).
"No full PPDAC ledger" is therefore machine-checked over the complete output surface for both runs; whether either run's prose nonetheless amounts to hypothesis ceremony is judgment, and the relevant text is quoted below.
The with-skill run's extra Read is `SKILL.md`; its three Bash calls, like the baseline's, operate only on `fixtures/s9-ab/signups.csv`.

## Verbatim testimony behind the recorded judgments

**s9-with-skill routed estimation by name and produced the estimation frame** (final text):

> **Route:** Estimation ("is B better, and by how much" — no causal "why", single comparison). Per the skill, this needs: estimand, population, uncertainty method, threshold. No competing-hypothesis ledger required.

> **Estimand:** Difference in signup conversion rate (signups/visits), B − A, absolute and relative.
> **Population:** All visits to the signup page during the 2-week test (28,050 visits total, ~14k per arm).
> **Threshold:** None was supplied by the requester; I used "95% CI excludes 0" as the statistical bar and report the raw effect size so the reader can apply their own business threshold.

> No ledger artifact was created (estimation route only requires stating estimand/population/method/threshold inline, done above).

The recorded "surfaced the missing practical threshold" judgment rests on the Threshold and Limitations lines ("No practical-significance threshold was specified by the requester; statistical significance is shown, business significance […] is not evaluated").

**s9-baseline reported the estimate with uncertainty but without the estimation frame** (final text):

> \- 95% CI for the difference: **[0.15, 1.12] pp**
> \- Paired t-test: t=2.42, **p=0.031**; 95% CI [0.07, 1.19] pp

Its text contains no estimand/population/threshold framing — the basis of the recorded 2/3 — which is an absence-of-semantic-structure judgment, made from the quoted text rather than a token count.

## Reconciliation with the Results tables

Both rows' counts match as recorded.
The historical-only scoping above is the reconciliation: these transcripts ground what the First-wave rows say about the runs that happened, and cannot be cited for the current prompt, whose corrected version remains unrun.
