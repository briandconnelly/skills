# Scales, Axes & Legends

This file owns scale types and `domain` (the mapping from data values to visual position or color), axis configuration (`title`, `format`, `labelAngle`, `grid`), legend configuration (`title`, `orient`, disabling), and d3 number/date format strings.
It does not cover encoding-level transforms or `data.format.parse` (`references/authoring-basics.md`), view-level `filter`/`calculate` (`references/transforms.md`), or `layer`/`facet`/`resolve` mechanics (`references/composition.md` — a scale, axis, or legend can be shared or made independent across a composition there; this file only covers the scale/axis/legend properties themselves).
Which color scheme to choose for accessibility is `references/aesthetics.md`'s territory; this file owns only the `scheme` mechanic that applies whichever palette is chosen.

## Scales

Every encoded field gets a scale that maps its data domain onto a visual range — position, size, or color.
Vega-Lite infers a default scale type from the field's semantic type and the mark, but the type can always be set explicitly with `"scale": {"type": "..."}`:

| Scale type | When it's the default | Use it for |
| --- | --- | --- |
| `linear` | Quantitative fields | Evenly-spaced continuous magnitude; the default for almost every quantitative axis |
| `log` | Never (opt-in) | Data spanning multiple orders of magnitude, where equal ratios (not equal differences) should look equally spaced |
| `sqrt` | Never (opt-in) | A `size` encoding where the mark's *area* (not its radius) should scale linearly with the value |
| `point` | Nominal/ordinal fields on `x`/`y`, when the mark has no width (`point`, `line`, `text`) | Evenly-spaced categories with no reserved band width |
| `band` | Nominal/ordinal fields on `x`/`y`, when the mark has width (`bar`, `rect`) | Categories reserved as discrete bands so bars/rects have room to draw |
| `time` / `utc` | Temporal fields (`time` is the default; `utc` is opt-in) | Date/time position; use `utc` instead of the default `time` when the data is UTC-serialized and renders must be timezone-independent, since `time` interprets ticks in the local/browser timezone |

These defaults were confirmed directly by compiling minimal specs: a nominal `x` on a `point` mark compiles to an `x` scale of type `point`, the same field on a `bar` mark compiles to `band`, a temporal `x` compiles to `time`, and a quantitative `size` encoding compiles to `linear` — not `sqrt` — so area-proportional sizing always needs an explicit `"scale": {"type": "sqrt"}`, never assume it's automatic.

### `domain`

`domain` overrides the range of input values a scale maps from, most often a two-element `[min, max]` array for a quantitative or temporal field.
Leave it unset to let Vega-Lite compute the domain from the data (plus `zero`/`nice`, below); set it explicitly to pin an axis across multiple charts for comparability, to add padding beyond the data's actual extent, or to deliberately restrict the visible range.
Setting an explicit `domain` also changes the `zero` default (next) for that scale, since Vega-Lite no longer assumes you want the automatic zero baseline once you've told it the domain yourself.

### `zero`

`zero` controls whether a quantitative scale's domain is forced to include a `0` baseline.
Its default is `true` for `x`/`y` channels when the field is unbinned and no explicit `domain` is given, and `false` otherwise — log, time, and utc scales don't support `zero` at all, since a logarithmic or date scale has no meaningful zero to anchor to.
This default is exactly why `bar` and `area` marks look correct out of the box: their quantitative axis gets an automatic zero baseline unless you override `domain` yourself (see Pitfalls).

### `nice`

`nice` extends a computed domain to round numbers so tick labels land on clean values instead of the data's exact, often-ugly extent (e.g. `[0.2, 1.0]` instead of `[0.2015..., 0.9967...]`).
It defaults to `true` for unbinned quantitative fields without an explicit `domain`, and for `time`/`utc` scales accepts a specific interval (`"month"`, `"year"`, etc.) instead of a boolean, to snap to calendar boundaries rather than arbitrary round numbers.

### `scheme` (color scales)

For a `color` encoding, `scheme` names a d3/Vega color scheme (`"tableau10"`, `"blues"`, `"category10"`, etc.) to use as the scale's range instead of Vega-Lite's default palette:

```jsonc
"color": {"field": "region", "type": "nominal", "scale": {"scheme": "tableau10"}}
```

This is the mechanic only — discrete schemes work with discrete/discretizing scales and continuous schemes with continuous color scales, but *which* scheme is colorblind-safe or otherwise appropriate for the data is `references/aesthetics.md`'s call, not this file's.

## Axes

An axis renders the ticks, labels, and gridlines for a position (`x`/`y`) scale; its properties live under an encoding channel's `"axis": {...}` object.

- **`title`** — the label shown along the axis; defaults to the field name (plus any `aggregate`/`bin`/`timeUnit` annotation, e.g. `"Sum of Profit"`); set an explicit string for a clearer label, or `null` to remove the title entirely.
- **`format`** — a d3 format string controlling how tick labels render numbers or dates; see Formatting below.
- **`labelAngle`** — rotates tick labels in degrees; defaults to `-90` for nominal/ordinal fields (to fit long category names without overlapping) and `0` otherwise; set explicitly (e.g. `-45`) when default rotation still overlaps or wastes space.
- **`grid`** — whether gridlines extend from this axis's ticks across the plot; defaults to `true` for continuous, unbinned scales and `false` otherwise; turn it off (`"grid": false`) when gridlines add clutter without helping comparison, or turn it on for a binned/discrete axis where alignment across categories matters.

## Legends

A legend renders the key for a non-position channel (`color`, `size`, `shape`, etc.); its properties live under that channel's `"legend": {...}` object.

- **`title`** — same rule as an axis title: defaults to the field name (with any aggregate/bin/timeUnit annotation), overridable to a clearer string, or `null` to remove it.
- **`orient`** — where the legend sits relative to the plot: `"left"`, `"right"` (the default), `"top"`, `"bottom"`, or a corner combination (`"top-left"`, etc.); reach for `"bottom"` or `"top"` on a wide plot with a narrow legend, or a corner value to reclaim space `"right"` would otherwise waste.
- **`"legend": null`** — disables the legend for that channel entirely, removing it from the render rather than just hiding it — appropriate when a redundant encoding (e.g. `color` that repeats what `x` already shows) doesn't need its own key, or when a single-category encoding's legend would only ever show one entry.

A complete spec exercising both `scheme` and legend `orient` — revenue by quarter, colored by region with an explicit palette and a bottom-oriented legend:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Revenue by region and quarter, colored by region with an explicit color scheme and a bottom-oriented legend.",
  "data": {
    "values": [
      {"region": "North", "quarter": "Q1", "revenue": 42},
      {"region": "North", "quarter": "Q2", "revenue": 51},
      {"region": "South", "quarter": "Q1", "revenue": 33},
      {"region": "South", "quarter": "Q2", "revenue": 39},
      {"region": "East", "quarter": "Q1", "revenue": 28},
      {"region": "East", "quarter": "Q2", "revenue": 35}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "quarter", "type": "nominal", "title": "Quarter"},
    "y": {"field": "revenue", "type": "quantitative", "title": "Revenue"},
    "color": {
      "field": "region",
      "type": "nominal",
      "title": "Region",
      "scale": {"scheme": "tableau10"},
      "legend": {"orient": "bottom"}
    }
  }
}
```

Rendered, this shows a stacked bar chart with a "Region" legend of three tableau10-colored swatches (East/North/South) sitting below the plot rather than to its right.
Changing that spec's `color.legend` from `{"orient": "bottom"}` to `null` and re-rendering removes the legend entirely — the same three-colored stacked bars still draw with the same `tableau10` colors, but there is no swatch key anywhere in the image telling a viewer which color is which region; confirmed by rendering both variants side by side.

## Formatting

`format` (on an axis, legend, or text mark) takes a d3 pattern string, and which d3 formatter runs depends on the field's type: d3-format for quantitative fields, d3-time-format for temporal ones.

**d3 number format** (quantitative fields):

| Pattern | Example input | Renders as |
| --- | --- | --- |
| `.0%` | `0.15` | `15%` |
| `.1%` | `0.156` | `15.6%` |
| `$,.2f` | `1234.5` | `$1,234.50` |
| `,.0f` | `1234567` | `1,234,567` |
| `.2s` | `1500000` | `1.5M` |

**d3 time format** (temporal fields):

| Pattern | Renders as |
| --- | --- |
| `%b` | `Jan`, `Feb`, ... (abbreviated month) |
| `%b %Y` | `Jan 2024` |
| `%Y-%m-%d` | `2024-01-15` |
| `%B` | `January` (full month name) |
| `%a` | `Mon`, `Tue`, ... (abbreviated weekday) |

The percent pattern was confirmed by rendering a `.0%`-formatted quantitative axis against `[0.08, 0.15, 0.21]`: the tick labels came out as `0%, 2%, 4%, ... 22%`, not the raw decimals.

A complete spec that sets an explicit scale `domain` on `y` and an explicit axis `format` on `x` — monthly average temperature as a line, with the `y` scale pinned to `[0, 100]` and the `x` axis showing abbreviated month names:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Monthly average temperature with an explicit y-domain and an abbreviated-month x-axis format.",
  "data": {
    "values": [
      {"date": "2024-01-15", "temp": 62},
      {"date": "2024-04-15", "temp": 68},
      {"date": "2024-07-15", "temp": 74},
      {"date": "2024-10-15", "temp": 66}
    ]
  },
  "mark": {"type": "line", "point": true},
  "encoding": {
    "x": {"field": "date", "type": "temporal", "title": "Month", "axis": {"format": "%b"}},
    "y": {"field": "temp", "type": "quantitative", "title": "Avg temp (F)", "scale": {"domain": [0, 100]}}
  }
}
```

Rendering this spec and the same spec with the `axis.format` and `scale.domain` removed shows two concrete, verified differences.
First, the x-axis tick labels change from full month names (`February`, `April`, `June`, `October` — the default temporal format at month granularity) to the abbreviated `%b` form (`Feb`, `Apr`, `Jul`, `Oct`).
Second, the y-axis range changes from the default's auto-computed `[0, 80]` (zero baseline plus `nice`-rounding to the data's ~74 max) to the explicit `[0, 100]`, which visibly compresses the plotted line lower in the frame since the same temperature values now occupy a smaller fraction of a taller domain.

## Pitfalls

- **Log scale with zero or negative data silently produces an empty chart, not an error.** A `log` scale has no defined value at `0` or below, so a field containing a zero (confirmed by rendering `{"scale": {"type": "log"}}` against data including a `0` value) compiles and renders successfully — every stage of the parse-schema-compile-render pipeline passes — but produces a blank plot with no bars, no y-axis tick labels, and no visible error at all; a clean render is not proof the chart is correct (see `references/validation-and-debugging.md`), and this is the sharpest case of that rule.
  Switch to `linear` or `sqrt`, or filter/shift the zero and negative values out before applying `log`, if the field must include them.
- **Truncating a bar chart's y-domain misleads.** Bars encode magnitude as length from a baseline, so a bar's visual comparison is only honest when that baseline is `0` — setting an explicit `domain` that excludes zero (e.g. `[90, 100]` for values in the 90s) turns `zero`'s default off (see `zero` above) and stretches small real differences to fill the entire plot height, exaggerating them.
  Confirmed by rendering the same three scores (92, 95, 98) both ways: with the default zero baseline the three bars are nearly indistinguishable in height (the true ~6% spread reads as ~6% of the plot), while with `domain: [90, 100]` the identical three bars span the plot's full height and look dramatically different.
  Bars (and areas, for the same reason) should include zero as a strong default.
  The honest exception is a mark like `line` or `point`, where the reader is tracking relative change or position rather than reading bar length as absolute magnitude from a baseline — a temperature or stock-price line zoomed to its own range is standard practice, not misleading, as long as the axis labels make the actual range visible.
  This exact failure mode — a truncated bar-chart y-domain — is what `tests/scenarios.md`'s misleading-scale eval scenario exercises; see that file for the scored case.
