# Scenario 2 (fix a broken spec) — with skill — 2026-07-19

Scored run of `tests/scenarios.md` Scenario 2, performed end to end with the skill's guidance.
This is the seed run: the known positive that shows the harness distinguishes a genuinely fixed spec from a broken one.

## Prompt given

> This Vega-Lite spec won't render.
> Diagnose the problem using the skill's validation loop and fix it.

## Step 1: the broken spec

Fenced as `jsonc` so `tests/check_specs.py` does not treat it as a must-pass example — it is the intentionally-broken input.

```jsonc
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Weekly active users by platform.",
  "data": {
    "values": [
      {"week": "2024-01-01", "platform": "iOS", "users": 1200},
      {"week": "2024-01-08", "platform": "iOS", "users": 1350},
      {"week": "2024-01-01", "platform": "Android", "users": 980},
      {"week": "2024-01-08", "platform": "Android", "users": 1105}
    ]
  },
  "marks": "line",
  "encoding": {
    "x": {"field": "week", "type": "temporal", "title": "Week"},
    "y": {"field": "users", "type": "quantitative", "title": "Weekly active users"},
    "color": {"field": "platform", "type": "nominal", "title": "Platform"}
  }
}
```

## Step 2: actual `render.py` output on the broken spec

Ran per the skill's Spine step 6 (Validate, render, inspect):

```
uv run vega-lite/scripts/render.py broken.json
```

Real output:

```
vl-convert 1.9.0 | embedded Vega-Lite 5.8, 5.14, 5.15, 5.16, 5.17, 5.20, 5.21, 6.1, 6.4
[PASS] parse
[FAIL] schema — <root>: {'$schema': 'https://vega.github.io/schema/vega-lite/v6.json', 'description': 'Weekly active users by platform.', 'data': {'values': [{'week': '2024-01-01', 'platform': 'iOS', 'users': 1200}, {'week': '2024-01-08', 'platform': 'iOS', 'users': 1350}, {'week': '2024-01-01', 'platform': 'Android', 'users': 980}, {'week': '2024-01-08', 'platform': 'Android', 'users': 1105}]}, 'marks': 'line', 'encoding': {'x': {'field': 'week', 'type': 'temporal', 'title': 'Week'}, 'y': {'field': 'users', 'type': 'quantitative', 'title': 'Weekly active users'}, 'color': {'field': 'platform', 'type': 'nominal', 'title': 'Platform'}}} is not valid under any of the given schemas
FAILED
```

Exit code: `1`.

## Step 3: diagnosis

`parse` passed (the JSON is syntactically valid), so the break is structural, not a syntax error.
`schema` failed at `<root>` with the entire spec echoed back rather than a pointer to the one bad key — this is the exact caveat `references/validation-and-debugging.md` documents: a large `anyOf` over mark/encoding shapes can't always localize which alternative almost matched.
Per that caveat, the fix is to re-read the spec's own keys rather than parse the dumped error for a clue.
Scanning the top-level keys against `references/authoring-basics.md` and `references/composition.md`, every key is a recognized top-level property (`$schema`, `description`, `data`, `encoding`) except one: `"marks": "line"`.
Vega-Lite's single-view top level takes `mark` (singular), not `marks` — the plural is a Vega (not Vega-Lite) and general-charting-library convention that doesn't apply here.
Because `marks` isn't a recognized property, the schema also has no `mark` at all for this view, which is required — so this single typo is simultaneously an unknown property and a missing required field.
Everything else in the spec is already correct for the intended chart: `week` is `temporal` (the data is plain ISO-8601, so no `format.parse` is needed per `references/authoring-basics.md`), `users` is `quantitative`, `platform` is `nominal` and correctly redundant-encoded via `color` to distinguish the two lines.
The fix is narrow: rename `marks` to `mark`.

## Step 4: the fixed spec

Fenced as `json` so `tests/check_specs.py` runs it and it must pass.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Weekly active users by platform, line per platform colored by platform.",
  "data": {
    "values": [
      {"week": "2024-01-01", "platform": "iOS", "users": 1200},
      {"week": "2024-01-08", "platform": "iOS", "users": 1350},
      {"week": "2024-01-01", "platform": "Android", "users": 980},
      {"week": "2024-01-08", "platform": "Android", "users": 1105}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "week", "type": "temporal", "title": "Week"},
    "y": {"field": "users", "type": "quantitative", "title": "Weekly active users"},
    "color": {"field": "platform", "type": "nominal", "title": "Platform"}
  }
}
```

## Step 5: actual `render.py` output on the fixed spec

```
uv run vega-lite/scripts/render.py fixed.json fixed.png
```

Real output:

```
vl-convert 1.9.0 | embedded Vega-Lite 5.8, 5.14, 5.15, 5.16, 5.17, 5.20, 5.21, 6.1, 6.4
[PASS] parse
[PASS] schema
[PASS] compile
[PASS] render
OK
```

Exit code: `0`.
The rendered `fixed.png` (51,641 bytes) was inspected: two colored lines (iOS, Android), each with two points at the `2024-01-01`/`2024-01-08` weeks, a temporal `x`-axis, a quantitative `y`-axis titled "Weekly active users," and a "Platform" color legend — the intended chart, not a blank or degenerate render.

## Step 6: actual `check_specs.py` output on this run file

Ran against this very file, so the fenced `jsonc` broken spec above is skipped and only the fenced `json` fixed spec is extracted and checked:

```
$ cd vega-lite && uv run tests/check_specs.py tests/runs/2026-07-19-scenario2-with-skill.md
[OK ] 2026-07-19-scenario2-with-skill.md#json[0]  parse:PASS schema:PASS compile:PASS render:PASS
```

Exit code: `0`.

## Scoring against Scenario 2's success criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) Passes every validation stage | PASS | Step 5: `parse`/`schema`/`compile`/`render` all `PASS`, exit `0`; Step 6: `check_specs.py` reports `[OK ]`, exit `0`. |
| (b) Correct semantic types + parsing | PASS | `week` temporal, `users` quantitative, `platform` nominal, unchanged from the input and already correct; no `format.parse` needed since the dates are plain ISO-8601. |
| (c) Idiomatic composition/scale choice | PASS | The fix is the minimal, correct one (`marks` → `mark`); the chart keeps its one-line-per-platform shape via `color`, the idiomatic way to compare a small number of categorical trends on one `line` mark. |
| (d) Validation actually performed | PASS | Step 2 shows the real pre-fix failure; Step 5 shows the real post-fix pass; the rendered `fixed.png` was produced and inspected, not merely claimed. |

**Total: 4/4.**
