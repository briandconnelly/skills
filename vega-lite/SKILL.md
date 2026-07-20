---
name: vega-lite
description: Use when authoring, editing, repairing, or reviewing a raw Vega-Lite JSON specification — bar/line/area/point charts, layered or faceted small multiples, encodings, scales, axes, legends, in-spec filter/calculate/bin/timeUnit/aggregate transforms — and when a chart must be validated by actually compiling and rendering it. Also triggers when you see a raw spec with a $schema of .../vega-lite/vN.json, a .vl.json file, or a request to fix a Vega-Lite spec embedded in Vega-Embed, Streamlit, or a notebook. Covers correct semantic field typing (nominal/ordinal/quantitative/temporal), data parsing via data.format.parse, layer/facet composition with resolve, and accessible color. Do not use for Altair or other language bindings, low-level Vega specs, interactive params/selections (deferred), or generic charting-library or image-export tasks that are not raw Vega-Lite JSON.
---

# Vega-Lite

Author correct, idiomatic, static Vega-Lite v6 JSON specifications, and validate every one by actually rendering it rather than by eyeballing the JSON.

## Scope

This is v1 of the skill, and it covers static Vega-Lite only: single or composed (layer/facet) views, encodings, scales/axes/legends, and in-spec transforms.
It defers interactivity (params, selections, signals), `repeat`/`concat` composition, advanced transforms (e.g. `regression`, `loess`, `window` folds beyond simple cases), and geospatial specs (`projection`, `geoshape`) to a future v2.
Some common *static* constructs are in scope conceptually but not yet documented in these references — stacked and grouped bars (`stack`, `xOffset`/`yOffset`), error bars/bands, and text-label layering; for those, author from general Vega-Lite v6 knowledge and lean harder on the render-and-inspect loop, since the reference files won't walk you through them.
If a task needs any of these, say so explicitly and proceed only with the static subset that remains in scope.

## Spine

These steps are the recommended order for authoring or editing a spec, not a rigid sequence — expect to loop back as the rendered image reveals problems (step 7).
The one hard requirement here is step 6: no spec is done until it has been rendered and inspected, and that requirement is enforced separately under Enforced rules below.

1. **Understand the data.**
   Determine the shape of the data, the semantic type of each field used in an encoding, and whether raw values need `data.format.parse` before they can be typed correctly.
   See `references/authoring-basics.md`.
2. **Choose mark and encoding.**
   Pick the mark that matches the comparison being made and map fields onto channels with explicit types.
   See `references/authoring-basics.md`.
3. **Transform in-spec for small chart-local derivations.**
   Use `filter`, `calculate`, `bin`, `timeUnit`, and `aggregate` inside the spec rather than pre-processing data outside it, unless a named exception applies.
   See `references/transforms.md`.
4. **Compose with `layer`/`facet` when one view is not enough.**
   Use `resolve` to control shared vs. independent scales, axes, and legends across composed views.
   See `references/composition.md`.
5. **Get scales, axes, and legends right.**
   Choose the correct scale type for each field's semantic type and make labels, ticks, and formatting readable.
   See `references/scales-axes-legends.md`.
6. **Validate, render, inspect — non-negotiable.**
   Compile and render the spec to an image and look at it; a successful render is evidence the spec is well-formed, not proof the chart is correct.
   See `references/validation-and-debugging.md`.
7. **Refine on what the image reveals.**
   Fix whatever the rendered chart shows — wrong types, overlapping labels, misleading scales — and repeat from the relevant step above.

## Enforced rules

These are the always-applicable rules that hold for every spec.
Each reference file also states rules local to its own area — log scales with `bar`/`area` marks (`references/scales-axes-legends.md`), relative `data.url` paths silently fetching the wrong data (`references/validation-and-debugging.md`), tooltip fields acting as implicit grouping keys (`references/aesthetics.md`), and others — and those bind just as firmly when you are working in that area, even though they are not repeated here.

- Give every encoding channel that maps a data `field` an explicit semantic `type`, and never rely on inference. Constant `value` definitions (`{"value": "steelblue"}`) and secondary range channels (`x2`/`y2`, error channels) take no `type` at all — the secondary channels inherit it from their primary, so don't add one there or let a secondary stand in for the primary's declaration — while a `datum` literal (`{"datum": 50}`) needs a `type` only to override its inferred one.
- Never conflate type with parsing: a field's `type` says how to treat it, `data.format.parse` says how to read it. A plain ISO-8601 date string and a numeric-looking string are coerced automatically by their encoding `type` with no `parse` at all; `parse` is load-bearing only for a non-ISO or ambiguous date — day-first `15-01-2024`, slash-separated `06/01/2024` — which otherwise silently lands on the wrong dates, and for forcing a numeric-looking field to stay a string. See `references/authoring-basics.md`.
- Default to in-spec transforms (`filter`, `calculate`, `bin`, `timeUnit`, `aggregate`) for chart-local derivations; only pre-process data outside the spec for a named exception (e.g. joins, heavy reshaping, or data too large to inline).
- Pin `$schema` to the major Vega-Lite version (e.g. `https://vega.github.io/schema/vega-lite/v6.json`); never omit it or leave it generic.
- For sequential or ordered data, use a colorblind-safe scheme (e.g. `viridis`); for categorical (nominal) data — where no built-in palette is reliably colorblind-safe — keep the category count small and carry the distinction on a redundant channel (`shape` or `strokeDash`) too, not on color alone (see `references/aesthetics.md`).
- Add that redundant encoding intentionally, to carry meaning — never as an accidental side effect such as `color` merely repeating what an axis already shows.
- Always set a top-level `description` on every spec that ships, and a top-level `title` when the chart needs a headline — Vega-Lite auto-generates no view title, so an untitled chart simply has none; separately, replace an auto-derived axis/legend title (from the field name) with an explicit string when it reads awkwardly.
- Put essential facts directly in visible labels (axis titles, legend titles, text marks), not only in tooltips, since tooltips are not always available or discoverable.

### Validate

Every spec must be validated by actually rendering it, not just checked for syntactic JSON validity.
Invoke this skill's own `scripts/render.py` — it lives in the skill directory, not your working directory, so give an absolute path (or one relative to the skill root); the `vega-lite/scripts/...` form below assumes you are at this repo's root and will not resolve from an arbitrary cwd:

```
uv run <skill-dir>/scripts/render.py <spec.json> <out.png>
```

Every example this skill ships is checked the same way via `tests/check_specs.py`.

## Aesthetics

For color palettes, typography, layout, and other visual-design guidance beyond correctness, see `references/aesthetics.md`.
