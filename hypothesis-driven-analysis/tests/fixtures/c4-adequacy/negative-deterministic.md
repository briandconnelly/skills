# Investigation: deploy timing (C4 known negative — deterministic refutation)

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | the p95 step must not precede the deploy | align deploy log with metrics | CONTRADICTED | step at 09:12, deploy at 14:30 — the step precedes the deploy (S1 §1) |

## Conclusion

- Answer: the deploy hypothesis is refuted on timing.
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | descriptive (estimand: p95 step time) | REFUTED | deterministic timing prediction failed under T1; a cause cannot follow its effect |
