# Test Scenarios for vega-lite

Behavioral eval scenarios for this skill, following the baseline/with-skill methodology used elsewhere in this repo (see `separating-context-from-constraints/tests/scenarios.md` for the house convention this file adapts).
Run each scenario with a fresh subagent that does NOT have the skill loaded (baseline), then with the skill loaded (treatment), and compare against the success criteria below.
A baseline run that already satisfies every criterion means the scenario is too easy; tighten it.
A criterion the with-skill run misses is a finding against the skill, not against the agent.
Give each agent only the scenario prompt and inline-data fixture, plus skill access for the treatment run; do not reveal the success criteria, expected baseline failures, or prior outputs.
Every fixture is inline data with no `data.url` fetch, so every run is reproducible offline.

## How to run

1. **Baseline:** dispatch a subagent with only the scenario prompt and fixture, no skill access.
   Record which criteria its output satisfies.
2. **Treatment:** dispatch a fresh subagent with the skill available (loaded directly or triggered via its frontmatter description) and the same prompt and fixture.
3. **Score:** every scenario is scored against all four of the criteria below; each is pass/fail with a one-line evidence pointer into the scored output.
4. **Store:** save each scored run to `tests/runs/YYYY-MM-DD-scenarioN-baseline.md` or `tests/runs/YYYY-MM-DD-scenarioN-with-skill.md`.
   A scored run is a scored output — the transcript plus a criteria table and evidence pointers — not a raw, unannotated agent transcript.

## Scoring criteria (apply to every scenario)

- **(a) Validation stages.** The produced spec passes every stage `scripts/render.py` runs: `parse`, `schema`, `compile`, `render` (a `schema` `SKIP` from an uncached/offline schema is allowed; a `FAIL` at any stage is not).
- **(b) Semantic typing.** Every encoded field has the correct explicit semantic type (`nominal`/`ordinal`/`quantitative`/`temporal`), and `data.format.parse` is present wherever the raw data needs it (non-ISO or ambiguous date strings, numeric-as-string fields meant to be quantitative).
- **(c) Idiomatic choice.** The mark, composition (`layer`/`facet`/`resolve`), and scale/axis choices match what the reference files recommend for this data shape — a semantic judgment about correctness and honesty of the chart, not merely "it rendered."
- **(d) Validation performed.** `render.py` (or `check_specs.py`) was actually run against the final spec, and the rendered image exists on disk — not just claimed.

## Scenario 1: Messy inline data needing `format.parse`

**Prompt:**

> Here is inline daily error-count data from a service log.
> Dates are US-style `MM/DD/YYYY`, and the error counts came out of the log as strings.
> Build a Vega-Lite line chart of error count over time.
>
> ```jsonc
> [
>   {"day": "01/06/2024", "errors": "14"},
>   {"day": "01/07/2024", "errors": "9"},
>   {"day": "01/08/2024", "errors": "22"},
>   {"day": "01/09/2024", "errors": "5"}
> ]
> ```

**Success criteria:**

- (a) The final spec passes `parse`/`schema`/`compile`/`render`.
- (b) `x` is `"type": "temporal"` with `data.format.parse` mapping `day` to `"date:'%m/%d/%Y'"` (the default `toDate()` would misread `01/06/2024`, since day/month order is locale-dependent for a slash-separated date); `y` is `"type": "quantitative"` with `errors` parsed via `format.parse: {"errors": "number"}` so the string values are treated as numbers rather than left as unparsed strings.
- (c) The mark is `line` (a trend over a continuous/temporal axis), not `bar` or `point`, since the task is showing a count trending over time.
- (d) `render.py` was run against the final spec and the output image exists.

**Expected baseline failure:** a skill-less run often trusts `"type": "temporal"` alone to fix the date parsing (missing that `01/06/2024` is ambiguous without an explicit pattern), and frequently leaves `errors` as a raw string field, relying on undeclared inference rather than an explicit `quantitative` type plus `format.parse`.

## Scenario 2: Fix a broken spec

**Prompt:**

> This Vega-Lite spec won't render.
> Diagnose the problem using the skill's validation loop and fix it.
>
> ```jsonc
> {
>   "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
>   "description": "Weekly active users by platform.",
>   "data": {
>     "values": [
>       {"week": "2024-01-01", "platform": "iOS", "users": 1200},
>       {"week": "2024-01-08", "platform": "iOS", "users": 1350},
>       {"week": "2024-01-01", "platform": "Android", "users": 980},
>       {"week": "2024-01-08", "platform": "Android", "users": 1105}
>     ]
>   },
>   "marks": "line",
>   "encoding": {
>     "x": {"field": "week", "type": "temporal", "title": "Week"},
>     "y": {"field": "users", "type": "quantitative", "title": "Weekly active users"},
>     "color": {"field": "platform", "type": "nominal", "title": "Platform"}
>   }
> }
> ```

**Success criteria:**

- (a) The repaired spec passes `parse`/`schema`/`compile`/`render` (the broken spec fails at `schema`, since `marks` is not a recognized top-level property and `mark` is effectively missing).
- (b) Semantic types are unchanged and already correct: `week` temporal, `users` quantitative, `platform` nominal.
- (c) The fix renames `marks` to `mark` rather than restructuring the spec some other way; the chart remains a `line` mark with one line per platform via the `color` encoding, which is the idiomatic shape for comparing a trend across a small number of categories.
- (d) `render.py` was run on both the broken spec (to see the actual failure) and the repaired spec (to confirm the fix), and the rendered image from the repaired spec exists.

**Expected baseline failure:** a skill-less run sometimes guesses at the fix without running `render.py` first to see the actual stage and error, or "fixes" the spec by removing the color encoding or restructuring it into `layer` instead of making the one-property correction the error actually calls for.

## Scenario 3: `layer` composition with `resolve` for mismatched units

**Prompt:**

> Show monthly signups as bars with the conversion rate as a line on top, from this inline data.
> Signups are counts in the hundreds; conversion rate is a fraction between 0 and 1.
>
> ```jsonc
> [
>   {"month": "Jan", "signups": 120, "conversion_rate": 0.04},
>   {"month": "Feb", "signups": 200, "conversion_rate": 0.09},
>   {"month": "Mar", "signups": 150, "conversion_rate": 0.06},
>   {"month": "Apr", "signups": 300, "conversion_rate": 0.12}
> ]
> ```

**Success criteria:**

- (a) The final spec passes `parse`/`schema`/`compile`/`render`.
- (b) `month` is `nominal`, `signups` and `conversion_rate` are both `quantitative`.
- (c) The spec uses `layer` (a `bar` layer for `signups`, a `line` layer for `conversion_rate`) with `resolve.scale.y` set to `"independent"`, since the two fields have unrelated magnitudes and sharing one `y` scale would flatten `conversion_rate` to a thin band near the bottom of the chart; each layer gets its own `y` axis and title.
- (d) `render.py` was run and the rendered image shows two distinct y-axes (confirmed by inspecting the image, not just assumed from the spec).

**Expected baseline failure:** a skill-less run commonly layers both fields on a shared `y` scale (or omits `resolve` entirely), producing a chart where the conversion-rate line is visually flat and unreadable against the signups bars.

## Scenario 4: Correct a misleading truncated-axis bar chart

**Prompt:**

> This bar chart of quarterly customer-satisfaction scores is going into a public report.
> A reviewer says the y-axis makes small differences look huge.
> Fix the chart so it is not misleading.
>
> ```jsonc
> {
>   "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
>   "description": "Quarterly customer satisfaction score.",
>   "data": {
>     "values": [
>       {"quarter": "Q1", "score": 92},
>       {"quarter": "Q2", "score": 95},
>       {"quarter": "Q3", "score": 98},
>       {"quarter": "Q4", "score": 96}
>     ]
>   },
>   "mark": "bar",
>   "encoding": {
>     "x": {"field": "quarter", "type": "nominal", "title": "Quarter"},
>     "y": {"field": "score", "type": "quantitative", "title": "Satisfaction score", "scale": {"domain": [90, 100]}}
>   }
> }
> ```

**Success criteria:**

- (a) The fixed spec passes `parse`/`schema`/`compile`/`render`.
- (b) Semantic types are unchanged and already correct: `quarter` nominal, `score` quantitative.
- (c) The fix matches `references/scales-axes-legends.md`'s Pitfalls guidance for this exact failure mode: since a `bar` mark's length always draws from a literal `0` baseline regardless of `domain`, an explicit non-zero `domain` like `[90, 100]` does not "zoom in" honestly — the fix either removes the `domain` override so the bar axis includes zero, or switches the mark to `line`/`point` (where a zoomed axis on a non-length channel is legitimate) with the zoomed range clearly labeled.
- (d) `render.py` was run on the fixed spec and the rendered image exists; if the fix keeps `bar`, the image is inspected to confirm bars now draw from a zero baseline rather than overflowing the frame.

**Expected baseline failure:** a skill-less run often "fixes" the complaint by adding `"clip": true` to crop the overflow while keeping the non-zero `domain` — which renders cleanly but is exactly the actively-misleading case `scales-axes-legends.md` warns about, not a genuine fix.

## Results

| Date | Scenario | Run | Criteria passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-19 | 2 (fix a broken spec) | with skill | 4/4 | Seed run; recorded in `tests/runs/2026-07-19-scenario2-with-skill.md`. |
| — | 1 (messy inline data) | not yet run | — | Baseline and with-skill runs pending. |
| — | 2 (fix a broken spec) | baseline | — | Baseline run pending. |
| — | 3 (layer + resolve) | not yet run | — | Baseline and with-skill runs pending. |
| — | 4 (truncated axis) | not yet run | — | Baseline and with-skill runs pending. |
