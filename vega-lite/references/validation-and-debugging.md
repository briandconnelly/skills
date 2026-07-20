# Validation and Debugging

This file owns the staged validator's semantics, how to read its stage errors back to a fix, its runtime/font/URL caveats, and the checklist for a chart that renders but is blank or wrong.
It does not teach field typing, transforms, composition, scales/axes/legends, or color — those are `references/authoring-basics.md`, `references/transforms.md`, `references/composition.md`, `references/scales-axes-legends.md`, and `references/aesthetics.md`; this file only tells you how to catch mistakes in any of those areas by actually running the spec.

## The four stages

`scripts/render.py` runs every spec through four stages, in order, and stops at the first one that fails:

1. **`parse`** — the spec text is valid JSON.
   Catches syntax errors: trailing commas, unclosed braces, unquoted keys.
2. **`schema`** — the parsed spec validates against the official Vega-Lite v6 JSON Schema (fetched once from `vega.github.io` and cached to `~/.cache/vega-lite-skill/`).
   Catches structural mistakes: an invalid `type` value, an unknown property, a value outside its enum.
   If the schema can't be fetched and isn't already cached (no network, offline), this stage reports `SKIP`, not a pass — `SKIP` means "not checked," and a spec that only ever got a `SKIP` here has not actually been validated against the schema.
3. **`compile`** — the spec compiles from Vega-Lite to Vega (`vl_convert.vegalite_to_vega`).
   Catches mistakes the schema's shape-checking can't, because they depend on cross-field relationships the schema doesn't encode.
4. **`render`** — the compiled Vega spec renders to an image (`vl_convert.vegalite_to_png`/`_svg`).
   Catches mistakes that only surface once real data flows through scales and marks.

A `PASS` on all four stages is evidence the spec is well-formed and renders without error — it is **not** proof the chart is correct.
None of the four stages knows what you meant to show: a filtered-empty dataset, a typo'd field name, or a quantitative field mistyped as nominal all compile and render cleanly, producing a blank or misleading chart with an all-`PASS` run.
Always open the rendered image and check it against what the chart is supposed to show; see Blank-but-valid below for the specific ways a clean run still hides a wrong chart.

## Running it

```
uv run vega-lite/scripts/render.py <spec.json> <out.png>
uv run vega-lite/scripts/render.py <spec.json> <out.svg>
```

The output format is inferred from the extension you give (`.png` or `.svg`); anything else raises an error before any stage runs.
Pipe a spec through stdin with `-` in place of a path:

```
cat spec.json | uv run vega-lite/scripts/render.py - out.png
```

Omit the output path entirely to run all four stages — including a real render — without writing an image to disk; useful when you only want the pass/fail result:

```
uv run vega-lite/scripts/render.py <spec.json>
```

`--vl-version` picks which schema version the `schema` stage validates against (e.g. `--vl-version 6`); it does not change what `compile`/`render` target, since that's fixed by the bundled vl-convert version.
Every stage result prints to stderr as one `[STATUS] stage — detail` line, preceded by a preflight line reporting the vl-convert and embedded-Vega-Lite versions in use; the process exits `1` if `parse`, `schema`, `compile`, or `render` `FAIL`ed, and `0` otherwise (a `SKIP` on `schema` does not fail the run).

## Reading errors

The table below shows real `render.py` output, not paraphrased messages.

| Symptom | Stage that catches it | What `render.py` actually prints | Fix |
| --- | --- | --- | --- |
| Malformed JSON (unclosed object, trailing comma) | `parse` | `[FAIL] parse — Expecting property name enclosed in double quotes: line 4 column 1 (char 83)` | Fix the JSON syntax; `python -m json.tool spec.json` or an editor's JSON linter localizes it faster than the exception text does. |
| Invalid value for a known property, e.g. `"type": "nominl"` | `schema` | `[FAIL] schema — <root>: {...the entire spec, echoed back...} is not valid under any of the given schemas` | See the caveat below — the message won't point at the bad key. Check every `type` against the four values `authoring-basics.md` covers (`nominal`/`ordinal`/`quantitative`/`temporal`), and every enum-valued property against the schema. |
| Unknown top-level or nested property, e.g. `"marks"` instead of `"mark"` | `schema` | Same shape of message: `[FAIL] schema — <root>: {...entire spec...} is not valid under any of the given schemas` | Check the property name against `references/authoring-basics.md`, `transforms.md`, `composition.md`, or `scales-axes-legends.md` (whichever area it belongs to) for the correct key. |
| Field name typo'd against the data, e.g. encoding `"amoutn"` when the data has `"amount"` | none — all four stages `PASS` | `OK` (the field just resolves to `undefined` for every row) | Not caught by any stage. Cross-check every `field` value in `encoding` against the actual keys in `data.values` (or your data source), and inspect the rendered image — it will be missing marks or show them at a degenerate position. |
| Mark with no positional encoding, or a `filter` that excludes every row | none — all four stages `PASS` | `OK` | Not caught by any stage; the render genuinely succeeds and is genuinely empty. See Blank-but-valid below. |

**Caveat on the schema-stage message:** when the `schema` stage fails, `jsonschema` reports the error at `<root>` and echoes the *entire* spec back in the message rather than pointing at the one bad key.
This happens because Vega-Lite's schema expresses mark- and encoding-shape validity as a large `anyOf` over many alternative sub-schemas, and a validator matching against `anyOf` can't always localize which alternative almost matched.
In practice this means the `schema` FAIL message tells you *that* something is wrong but not *where* — re-read your own diff or recently-changed keys first, rather than trying to parse the dumped spec for a clue.

The intentionally-broken spec behind the first schema row above (fenced as `jsonc`, not `json`, so `tests/check_specs.py` does not treat it as a must-pass example):

```jsonc
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bad type value.",
  "data": {"values": [{"category": "A", "amount": 28}]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominl"},
    "y": {"field": "amount", "type": "quantitative"}
  }
}
```

Running it produces exactly the `parse`/`schema` lines shown in the table, and exits `1`:

```
vl-convert 1.9.0 | embedded Vega-Lite 5.8, 5.14, 5.15, 5.16, 5.17, 5.20, 5.21, 6.1, 6.4
[PASS] parse
[FAIL] schema — <root>: {'$schema': 'https://vega.github.io/schema/vega-lite/v6.json', 'description': 'Bad type value.', 'data': {'values': [{'category': 'A', 'amount': 28}]}, 'mark': 'bar', 'encoding': {'x': {'field': 'category', 'type': 'nominl'}, 'y': {'field': 'amount', 'type': 'quantitative'}}} is not valid under any of the given schemas
FAILED
```

## Caveats

- **First run needs a network connection and downloads vl-convert's compiled wheel (roughly 30 MB), plus the Vega-Lite schema on first use (cached after to `~/.cache/vega-lite-skill/`).** After both are cached, subsequent runs work offline; without a cached schema and no network, the `schema` stage reports `SKIP` rather than blocking the other stages.
- **Font resolution is silent, not validated.** Setting `config.font` (or a mark-level `font`) to a family that isn't installed on the machine running `render.py` does not fail any stage — `schema`/`compile`/`render` all still `PASS` — it just falls back to whatever default the renderer finds, so the same spec can render with different label width/wrapping on a different machine; don't assume a font name is honored just because the run reports `OK`.
- **Vega-Editor-style relative data paths (`{"url": "data/cars.json"}`) are not supported here, and the failure is silent.** There is no bundled `data/` directory and no server serving one, and confirmed above: pointing `data.url` at one does not fail any stage — `parse`/`schema`/`compile`/`render` all `PASS` — it just renders an empty chart (axes and frame, zero marks), because the fetch silently resolves to no rows. Use `data.values` (inline data) or an absolute URL (`https://...`) instead.

## Blank-but-valid

A spec can pass all four stages and still render a chart that is empty or wrong.
Since nothing flags this automatically, check for these specifically whenever a render looks blank:

- **A `transform.filter` (or a chain of transforms) excludes every row.** Confirmed above: filtering out all rows with a condition that never matches still passes `parse`/`schema`/`compile`/`render` and prints `OK`.
- **A `field` name doesn't match the data.** A typo'd or renamed field resolves to `undefined` for every row; every stage still passes.
- **A field's `type` collapses the scale that should show variation.** Confirmed above: a genuinely quantitative field (e.g. sequential day numbers) encoded as `"type": "nominal"` still renders `OK`, but the scale becomes categorical instead of continuous, and a `line` mark connecting nominal x-positions can lose the ordering or spacing the data actually has.
- **A mark has no positional encoding at all** (e.g. only `color` is set, no `x`/`y`). Confirmed above: this passes every stage and renders `OK`, typically producing a single mark placed at a default position rather than one per data row.

For any of these, the fix is never in `render.py`'s output — it passed — the fix is in the spec itself, per the reference file that owns the mistake (`authoring-basics.md` for typing/fields, `transforms.md` for `filter`).
