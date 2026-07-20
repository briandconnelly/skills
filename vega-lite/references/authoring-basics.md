# Authoring Basics

This is where every spec starts: what the data is, what each field means, and how to map that meaning onto a mark and encoding.
Composition (`layer`/`facet`/`resolve`), view-level `filter`/`calculate`, scale/axis/legend tuning, and color/typography principles live in the sibling references — this file only covers data sources and parsing, semantic types, marks, encoding channels, and the four encoding-level transforms `bin`, `timeUnit`, and `aggregate`.

## Data sources & parsing

Vega-Lite specs get their data from `data.values` (inline, embedded in the JSON) or `data.url` (a separate file or endpoint fetched at render time).
Inline data is self-contained and easiest to validate and share; prefer it for small, static datasets and for any example embedded in documentation.
`data.url` is appropriate for larger or externally-owned datasets, but it defers validation until fetch time and makes the spec unusable offline — every spec in this skill's examples uses inline data for that reason.

Inline JSON values keep whatever type `JSON.parse` gives them: numbers stay numbers, booleans stay booleans, and strings stay strings.
Declaring an encoding's `type` does not convert a field's raw values — `"type": "temporal"` tells Vega-Lite how to *scale and format* a field, it does not parse a string into a date.
A date given as the string `"2024-05-01"` stays that literal string through the pipeline unless `data.format.parse` explicitly parses it, and an unparsed date string sorts and scales lexicographically, not chronologically.

Use `data.format.parse` to map field names to `"date"`, `"boolean"`, or `"number"` so raw strings become the values their encoding `type` expects:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Daily signups from raw string dates and numeric-as-string counts, both parsed via data.format.parse.",
  "data": {
    "values": [
      {"day": "2024-06-01", "signups": "12"},
      {"day": "2024-06-02", "signups": "18"},
      {"day": "2024-06-03", "signups": "9"},
      {"day": "2024-06-04", "signups": "15"}
    ],
    "format": {"parse": {"day": "date", "signups": "number"}}
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "day", "type": "temporal", "title": "Day"},
    "y": {"field": "signups", "type": "quantitative", "title": "Signups"}
  }
}
```

Set a field to `null` in `format.parse` (e.g. `{"id": null}`) to force it to stay a raw string when Vega-Lite's default inference would otherwise coerce it — useful for zip codes or IDs that look numeric but aren't quantities.
`format.parse` is a data-source concern, distinct from the view-level `calculate` transform (see `references/transforms.md`), which derives new fields from already-typed data rather than reading raw input.

## Semantic types

Every field used in an encoding needs an explicit semantic type: nominal (`N`), ordinal (`O`), quantitative (`Q`), or temporal (`T`).

| Type | Meaning | Use when | Example fields |
| --- | --- | --- | --- |
| Nominal (`N`) | Discrete categories with no inherent order | Grouping or coloring by identity | `region`, `product_sku`, `status` |
| Ordinal (`O`) | Discrete categories with a meaningful order | The category sequence itself carries information | `size ("S","M","L")`, `rating ("low","medium","high")` |
| Quantitative (`Q`) | Continuous numeric measurements | Position, size, or aggregation on a magnitude | `revenue`, `count`, `temperature` |
| Temporal (`T`) | Date or date-time values | Time-based axes, `timeUnit` grouping | `order_date`, `timestamp` |

Nominal and ordinal both partition data into discrete groups; the only difference is whether Vega-Lite should sort and scale them by an inherent order (ordinal) or treat their order as arbitrary (nominal, sorted alphabetically by default unless you override `sort`).
Getting this choice wrong doesn't error — it silently mis-sorts categories or picks the wrong color scale (categorical vs. sequential), so choose deliberately rather than by whatever the field happens to look like.

Secondary range channels — `x2`, `y2`, and the error-representation channels (`xError`, `xError2`, `yError`, `yError2`) — take no `type` of their own:

```jsonc
"encoding": {
  "x": {"field": "start", "type": "temporal"},
  "x2": {"field": "end"}
}
```

`x2`/`y2` inherit their scale and semantic type from the primary `x`/`y` channel they pair with; giving `x2` its own `type` is redundant at best and a schema violation at worst.
This is the same rule the SKILL.md enforced-rules list states directly: never substitute an `x2`/`y2`/error-range encoding for a primary channel's own type declaration.

## Marks

Pick the mark that matches the comparison being made, not the one that looks closest to a reference image.

- **bar** — magnitude comparison across discrete categories (nominal or ordinal `x`/`y`); the default for "how much of X per category."
- **line** — trend across a continuous or temporal axis; implies an ordering along that axis, so it fits `T` or `Q` on the connected axis, not unordered `N` categories.
- **area** — like `line`, but the filled region emphasizes cumulative magnitude or volume under the trend; use sparingly with multiple overlapping series since fills occlude each other (layering and opacity are `references/composition.md`'s and `references/aesthetics.md`'s territory).
- **point** (and its `circle`/`square` mark-type variants) — relationships between two quantitative fields (scatter), or a quantitative field against a categorical one when individual observations matter more than an aggregate.
- **tick** — the distribution of individual values along one axis, especially many observations against one categorical field; a lighter-weight alternative to a full box plot for showing spread.
- **rect** — binned/aggregated 2D density (heatmaps, via `bin` on both axes) or discrete interval blocks (`x`/`x2` timelines, Gantt-style spans).

Defaults, not absolutes: a `bar` can encode a continuous `x` once it's binned (a histogram), and a `line` can connect ordinal categories if their order is meaningful (e.g. `"low" → "medium" → "high"`) — the underlying rule is always "does the mark's visual grammar match what the data and axis actually mean."

## Encoding channels

- **x / y** — position; the primary channels for almost every mark, and the only channels that carry `bin`, `timeUnit`, or `aggregate` transforms directly (below).
- **color** — a redundant or primary encoding for a nominal/ordinal category (categorical scale) or a quantitative/temporal gradient (sequential or diverging scale); which scale type applies is `references/scales-axes-legends.md`'s territory.
- **size** — quantitative magnitude on `point`, `bar`, or `text` marks (bubble charts, weighted scatter); position and length are perceptually more precise than area, so prefer `x`/`y` for comparisons that need accuracy.
- **shape** — distinguishes nominal categories on `point` marks; works best with a small number of categories (roughly five or fewer) since shapes are harder to discriminate at a glance than color or position.
- **column / row** — encoding-channel shorthand for small multiples: faceting a view by a nominal/ordinal field without reaching for the top-level `facet` operator.
  These two channels are the only facet-shaped thing this reference covers; independent-vs-shared scales/axes/legends across the resulting multiples is `references/composition.md`'s `resolve` territory.

Every one of these channels needs the explicit `type` from the table above — see Pitfalls below for what happens when you skip it.

## Encoding-level transforms

`bin`, `timeUnit`, and `aggregate` are transforms attached directly to an encoding channel, so they travel with the field they modify instead of living in a separate `transform` array (that's where view-level `filter`/`calculate`/`window` live — see `references/transforms.md`).

- **`bin`** — groups a quantitative field into discrete intervals (`"bin": true` or `"bin": {"maxbins": 10}`), typically paired with a `count` aggregate on the other axis to build a histogram.
- **`timeUnit`** — groups a temporal field to a coarser granularity (`"timeUnit": "month"`, `"year"`, `"day"`, etc.) without a separate derived column; requires the field to already be a real temporal value (parsed per the Data sources section above), not a raw string.
- **`aggregate`** — collapses multiple rows sharing the same value on the other encoded fields into one summary statistic (`"aggregate": "mean"`, `"sum"`, `"count"`, `"median"`, `"min"`, `"max"`, etc.).

A mean-per-category aggregate, the shape you'll reach for most often:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Mean order value per region, aggregated in-spec.",
  "data": {
    "values": [
      {"region": "North", "order_value": 42},
      {"region": "North", "order_value": 58},
      {"region": "South", "order_value": 30},
      {"region": "South", "order_value": 36},
      {"region": "East", "order_value": 51},
      {"region": "East", "order_value": 47}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "region", "type": "nominal", "title": "Region"},
    "y": {"field": "order_value", "type": "quantitative", "aggregate": "mean", "title": "Mean order value"}
  }
}
```

Any field left un-aggregated in an encoding acts as an implicit grouping key once another channel aggregates — Vega-Lite aggregates *within* each combination of the non-aggregated fields, not across the whole dataset.

## Pitfalls

- **Relying on type inference.** Vega-Lite will render a spec with an omitted `type` by guessing one, but a guess is not a decision — always write the `type` explicitly so the chart's meaning doesn't silently change if the guess ever changes.
- **Using `type` to paper over unparsed strings.** Setting `"type": "temporal"` on a field that is still a raw, unparsed string does not parse it; the axis will look plausible but sort and scale wrong (see Data sources & parsing above) — fix the data with `format.parse`, not the encoding.
- **Over-binning.** Passing an unbounded field straight into `"bin": true` with the default bin count can produce too many or too few bins for the data's actual range; check the rendered histogram and tune `maxbins` (or set explicit `extent`/`step`) rather than trusting the default sight unseen.
