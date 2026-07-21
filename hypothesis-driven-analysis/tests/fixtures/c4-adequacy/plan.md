# Investigation: slow-cluster warm-up (C4 calibration plan)

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | descriptive (estimand: p95 step time) | the deploy caused the p95 step | step aligns with deploy | step precedes deploy | the p95 step must not precede the deploy | T1 | deploy log, metrics |
| H4 | descriptive (estimand: share of slow events in first third) | a decaying warm-up effect across the 6h window | slow events cluster early | slow events spread evenly | a majority of the 6 slow events fall in the first third | T4 | latency sample |
