# S6 (underpowered null) — transcript evidence

Grounds the S6 rows in `tests/scenarios.md` (First wave).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

## Scope

| Run key | Wave | Recorded score |
| --- | --- | --- |
| s6-baseline | First | 3/3 |
| s6-with-skill | First | 3/3 |

## Machine-checked counts and facts

| Run | Tool calls | Bash | Read | Result statuses | `NON_DISCRIMINATING` occurrences in output |
| --- | --- | --- | --- | --- | --- |
| s6-baseline | 3 | 2 | 1 | 3 ok | 0 |
| s6-with-skill | 5 | 2 | 3 | 5 ok | 4 |

Both counts match the recorded cells (3 and 5).
The with-skill run's three Reads are `SKILL.md`, `references/ledger-template.md`, and the fixture; both runs' two Bash calls are pandas/scipy analyses of `latency_sample.csv` only — no query outside the fixture appears in either manifest.
The literal token `NON_DISCRIMINATING` appears 4 times in the with-skill run's output (T1 outcome, T3 outcome, sensitivity-check rule, per-hypothesis summary) and 0 times in the baseline's, which instead reasons about power in plain language.

**Independent recomputation (not from either transcript):** from the committed fixture, n = 41, sd = 106.8 ms, normal-approximation SE of the median ≈ 20.9 ms, 95% half-width ≈ 41 ms.
The with-skill run's bootstrap-derived ~47 ms half-width and the baseline's ~21 ms SE / "~30% power" are both consistent with this: by either method the detection limit exceeds the claimed 30 ms effect, so the scenario's premise holds against an independent check rather than only the agents' own arithmetic.

## Verbatim testimony behind the recorded judgments

**s6-baseline refused the null on its own power check** (final text, its only text block):

> **Power check**: Given the observed variance, the standard error of the median at n=41 is ~21ms. Detecting a true 30ms shift at this noise level has only ~30% power. You'd need roughly n≈200+ samples (or the full population) to reliably confirm/rule out a 30ms regression.

> **Inconclusive — not confirmable with this data.** The point estimate is directionally consistent with the claimed ~30ms slowdown (233 vs 200ms), but with only 41 heavy-tailed samples, 200ms sits comfortably inside the confidence interval for the post-rebuild median, and neither the Wilcoxon nor sign test rejects "no change."

**s6-with-skill recorded the null as `NON_DISCRIMINATING` with the detection limit stated** (ledger, emitted as its final text):

> Sensitivity check performed (required before trusting any null result): computed the bootstrap-CI detection limit for a one-sample test at n=41 against this variance — see T1. The detection limit (~±47ms half-width) exceeds the claimed effect (30ms), so a "CI contains 200" outcome must be recorded as `NON_DISCRIMINATING`, not as evidence of no change.

```
| T1 | H1 / H2 | H1: 95% CI of sample median excludes 200ms and is centered near 230ms. H2: CI comfortably contains 200ms. | Percentile bootstrap (20,000 resamples) of median; sign test and Wilcoxon signed-rank vs 200ms | NON_DISCRIMINATING | median=233.4ms, mean=230.8ms; bootstrap 95% CI [169.0, 263.3]ms (contains 200); sign test n>200=24, n<200=17, p=0.35; Wilcoxon p=0.11 (S1). Detection-limit half-width (~47ms) > claimed effect (30ms), so per the sensitivity-check rule this cannot count as a clean negative for H1, nor is it a significant positive. |
```

## Reconciliation with the Results tables

Both tool-call cells match as recorded.
One recorded claim is weakened: the with-skill row's note says the run "pre-committed the null's classification *before* testing".
The transcript cannot establish that — the run emitted its entire ledger as a single text block after both analysis calls (its only text block follows tool_use 5), so the prediction rows and the outcomes were externalized together.
The pre-commitment may have happened in-context, but it is the ledger's own narrative, not an observable ordering; the corresponding note in `tests/scenarios.md` is qualified accordingly.
The assertion-level judgments (recognizing the resolution limit, distinguishing "no evidence of regression" from "evidence of no regression") remain scorer readings of the quoted text.
