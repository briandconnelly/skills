# Investigation: does C2 catch a claim-class relabel at conclusion time?

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | the deploy caused the 09:10 step | step aligns with deploy | step precedes deploy | the step must not precede the deploy | T1 | deploy log |
| H2 | descriptive (estimand: median handle time) | median handle time rose | median up ≥30ms | median flat | the median must move ≥30ms | T2 | request logs |
