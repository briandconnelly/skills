# Composition

This file owns three things: the `layer` operator, the `facet` operator (and the `facet`/`row`/`column` encoding channels), and `resolve`.
It names `repeat` and `concat` only to say they are deferred; it does not teach them.
It does not cover encoding-level transforms or `data.format.parse` (`references/authoring-basics.md`), view-level `filter`/`calculate` (`references/transforms.md`), or scale types/domains/axis/legend configuration beyond the minimum `resolve` needs (`references/scales-axes-legends.md`).

## `layer`

`layer` draws two or more marks in the same coordinate space, one on top of the other.
An encoding placed on the top-level `encoding` is shared: it is inherited by *every* layer and always applied to it, whether or not that layer's own mark would naturally use it.
An encoding placed inside one layer's own `encoding` applies only to that layer.
A layer's own encoding is merged with the shared top-level encoding, not replacing it — so if a shared `x` is present at the top level, every layer is positioned by it, even a layer that only declares `y` itself.
There is no way for a layer to opt out of an inherited channel: put a channel at the top level only when every layer should genuinely use it, and keep everything else scoped to the layer that needs it.

Layers draw in array order, and later layers draw on top of earlier ones — this is drawing order, not a suggestion.
A bar chart with a target-threshold rule drawn afterward sits visibly above the bars; reverse the array and the bars would cover the rule instead.

A complete two-layer spec — bars with their own `x`/`y`, plus a mean-threshold rule layer with only its own `y` and no `x` anywhere, so it spans the full plot width:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Monthly sales as bars with a mean-sales threshold rule spanning the full width on top.",
  "data": {
    "values": [
      {"month": "Jan", "sales": 80},
      {"month": "Feb", "sales": 95},
      {"month": "Mar", "sales": 130},
      {"month": "Apr", "sales": 110}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "month", "type": "nominal", "sort": null, "title": "Month"},
        "y": {"field": "sales", "type": "quantitative", "title": "Sales"}
      }
    },
    {
      "mark": {"type": "rule", "color": "firebrick", "strokeWidth": 2, "strokeDash": [4, 4]},
      "encoding": {
        "y": {"aggregate": "mean", "field": "sales", "type": "quantitative"}
      }
    }
  ]
}
```

The rule layer has no `x` at the top level and adds none of its own, so nothing positions it along `x`; a `rule` with only `y` (no `x`/`x2`) spans the full width of the plot.
That is what makes it read as a single horizontal threshold line rather than one mark per month — if `x` were shared at the top level instead, the rule would inherit it too and draw one short vertical dash per month rather than a full-width line.
Rendering this spec shows four bars with a single dashed red line crossing all of them at the mean of `sales` (≈ 103.75), drawn on top of every bar it crosses.

By default the two layers also share their `y` scale — both draw into the same `sales`-only domain here, which is fine since they measure the same quantity.
When layered fields measure different things (a count and a rate, say), sharing a scale distorts one of them; see `resolve` below.

## `facet`

`facet` produces small multiples: the same view definition repeated once per distinct value of a faceting field, each copy showing only the rows matching that value.
There are two ways to ask for it.

**The `facet`/`row`/`column` encoding channels**, added to an ordinary single-view spec's `encoding`.
`row` and `column` each lay out one dimension of a grid — use both together for a two-dimensional grid of small multiples:

```jsonc
"encoding": {
  "row": {"field": "sensor", "type": "nominal"},
  "column": {"field": "year", "type": "ordinal"}
}
```

Use the single `facet` channel instead of `row`/`column` when one faceting field should wrap into a grid rather than lay out along only one dimension; `columns` sets how many panels appear per row before wrapping to the next:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Small multiples of sales by region, wrapped into 2 columns, with a custom header title.",
  "data": {
    "values": [
      {"region": "North", "quarter": "Q1", "sales": 40},
      {"region": "North", "quarter": "Q2", "sales": 55},
      {"region": "South", "quarter": "Q1", "sales": 30},
      {"region": "South", "quarter": "Q2", "sales": 65},
      {"region": "East", "quarter": "Q1", "sales": 50},
      {"region": "East", "quarter": "Q2", "sales": 45},
      {"region": "West", "quarter": "Q1", "sales": 60},
      {"region": "West", "quarter": "Q2", "sales": 35}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "quarter", "type": "nominal", "title": "Quarter"},
    "y": {"field": "sales", "type": "quantitative", "title": "Sales"},
    "facet": {
      "field": "region",
      "type": "nominal",
      "columns": 2,
      "title": "Region",
      "header": {"labelFontWeight": "bold", "titleFontSize": 12}
    }
  }
}
```

Rendered, this produces a 2x2 grid of panels — East, North, South, West — each a two-bar chart of `Q1`/`Q2` sales, under a shared "Region" title with bold per-panel labels (`header.labelFontWeight`) and a larger group title (`header.titleFontSize`); `header` accepts the usual title/label font, size, and color properties for either the row/column/facet channel or the operator form below.

**The `facet` operator**, a spec shaped `{"facet": ..., "spec": {...}}` at the top level instead of an encoding channel:

```jsonc
{
  "facet": {"field": "region", "type": "nominal", "columns": 2},
  "spec": {
    "layer": [
      {"mark": "bar", "encoding": {"x": {"field": "quarter", "type": "nominal"}, "y": {"field": "sales", "type": "quantitative"}}},
      {"mark": "rule", "encoding": {"y": {"datum": 50}}}
    ]
  }
}
```

Reach for the operator form specifically when the thing being repeated per panel is itself a `layer` (as above) — the `facet`/`row`/`column` encoding channels only attach to a single mark's encoding, so a per-panel view that needs more than one layer needs the operator's separate `spec`.

## `resolve`

Scales, axes, and legends default to `"shared"` across a composition's layers or facets: one scale, one set of tick marks, one legend, reused everywhere so values are directly comparable.
Set `resolve.scale`, `resolve.axis`, or `resolve.legend` per channel to `"independent"` to break that sharing when it hides more than it clarifies — each layer or facet then gets its own scale, axis, or legend for that channel.

The clearest case is layering two fields with unrelated magnitudes on the same `y`.
Take the sales-bars-plus-rule spec's shape, but layer `revenue` (in the hundreds) with a `growth_rate` (a fraction near 0.1) instead of a fixed threshold — with the default shared `y` scale, both layers are forced into one domain sized to the larger field, and the line collapses to a flat smear near zero:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Revenue bars layered with growth-rate line, each on its own y-scale via resolve.",
  "data": {
    "values": [
      {"month": "Jan", "revenue": 120, "growth_rate": 0.05},
      {"month": "Feb", "revenue": 200, "growth_rate": 0.12},
      {"month": "Mar", "revenue": 150, "growth_rate": 0.08},
      {"month": "Apr", "revenue": 300, "growth_rate": 0.20},
      {"month": "May", "revenue": 250, "growth_rate": 0.15}
    ]
  },
  "resolve": {
    "scale": {"y": "independent"}
  },
  "encoding": {
    "x": {"field": "month", "type": "nominal", "sort": null, "title": "Month"}
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "y": {"field": "revenue", "type": "quantitative", "title": "Revenue"}
      }
    },
    {
      "mark": {"type": "line", "color": "firebrick", "point": true},
      "encoding": {
        "y": {"field": "growth_rate", "type": "quantitative", "title": "Growth rate"}
      }
    }
  ]
}
```

With `resolve.scale.y` set to `"independent"`, this renders with two `y`-axes — a left axis for `Revenue` (0-300) and a right axis for `Growth rate` (0-0.20) — and the line traces its own actual shape across the full plot height.
Drop the `resolve` block (or set it to `"shared"`, the default) and re-render: both fields are forced onto one merged `y` domain sized to `revenue`'s 0-300 range, so `growth_rate`'s 0.05-0.20 values flatten to a thin band hugging the bottom of the chart, and there is only one `y`-axis instead of two.
Compiling both variants confirms the same thing structurally: the shared version produces a single Vega scale named `y` whose domain is built from *both* fields, while the independent version produces two separate scales (`layer_0_y`, `layer_1_y`), each keyed only to its own field.

`resolve.axis` and `resolve.legend` follow the same `"shared"`/`"independent"` choice for their own concern — `resolve.axis.y` controls whether ticks/labels are drawn once or once per layer independent of whether the scale itself is shared, and `resolve.legend.color` controls whether two layers that both encode `color` (for two different fields) merge into one legend or get two:

```jsonc
"resolve": {
  "legend": {"color": "independent"}
}
```

`resolve` applies the same way to `facet`: panels share a `y` scale by default so bar heights compare fairly across panels, and setting `resolve.scale.y` to `"independent"` gives each facet panel its own domain sized to only its own subset of the data — useful when panels vary wildly in range, at the cost of losing that cross-panel comparability.

## Deferred

`repeat` (repeating a view template across a list of fields) and `concat` (arbitrary side-by-side/stacked composition of dissimilar views) are out of this skill's v1 scope.
Both are named here only so an author knows they exist and where they'd go looking; author around them with `layer`/`facet` for now, or wait for v2.

## Pitfalls

- **Mismatched layer scales.** Layering fields with very different magnitudes or units on a shared scale (a count layered with a rate, a price layered with a percentage) silently squashes the smaller-magnitude layer flat against the axis baseline — it is still being drawn, just at a scale where its real variation is invisible.
  Reach for `resolve.scale` set to `"independent"` on that channel once two layers stop measuring comparable things.
- **Faceting a field that should just be a color/column encoding.** Faceting splits a field into fully separate panels, each with its own axes and (by default) shared scales; that is the right call when panels genuinely need separate scales or would be too cluttered overlaid in one view, but a field with few categories that *should* be directly compared point-for-point (e.g. a handful of product lines on the same axes) is usually clearer as a single view with `color` (or `column` as a lighter-weight single-row facet) than as a wall of near-identical small panels.
