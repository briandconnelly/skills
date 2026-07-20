# Aesthetics

This file owns color usage principles, intentional-vs-accidental redundant encoding, typography and titles, and labels-over-tooltips guidance for accessible, legible static output.
It does not cover the `scheme`/scale/legend *mechanics* — how to set a scheme, position a legend, or disable one — that's `references/scales-axes-legends.md`'s territory; this file is about which palette to choose and why.
It also does not cover encoding-level transforms (`references/authoring-basics.md`) or `layer`/`facet`/`resolve` composition (`references/composition.md`).

## Color

Default to a restrained categorical palette for nominal fields: enough distinct hues to tell categories apart, not so many that adjacent swatches blur together.
Beyond roughly ten categories, a categorical scheme stops helping — group or filter the data instead of asking a legend to carry fifteen-plus colors.
For quantitative or ordered data, reach for a sequential scheme (one hue ramping in lightness, e.g. `"viridis"`, `"blues"`) when values run low-to-high with no meaningful midpoint, or a diverging scheme (two hues meeting at a neutral center) when values run negative-to-positive around a meaningful zero or baseline.
This is a default, not an absolute: a categorical palette can still suit a small number of ordered bins where discreteness matters more than gradient (e.g. a five-point rating rendered as distinct colors rather than a ramp).

`"tableau10"` and `"viridis"` are this skill's two default named schemes, and each is colorblind-safe by design:

- **`"tableau10"`** — ten qualitative hues, chosen to stay distinguishable under the common forms of color vision deficiency; reach for it as the default categorical scheme for nominal fields with up to ten values.
- **`"viridis"`** — a perceptually-uniform sequential ramp (dark purple to yellow) that also degrades gracefully to grayscale; reach for it as the default for quantitative or ordered fields, including as a diverging-adjacent choice when a true diverging scheme isn't needed.

Setting either is a one-line `scale.scheme`; see `references/scales-axes-legends.md` for the mechanic and for how discrete vs. continuous schemes map onto scale types.

## Intentional redundancy

Redundant encoding — showing the same distinction on two channels at once — is a deliberate accessibility technique when it's *intentional*: pairing `color` with `shape` (for point-like marks) or `color` with `strokeDash` (for line-like marks) on the same nominal field means a reader who can't distinguish the colors (color vision deficiency, grayscale print, a black-and-white photocopy) can still read the chart from shape or dash pattern alone.
Reach for this whenever a chart is likely to be printed, screenshotted into a grayscale context, or viewed by someone with color vision deficiency — which in practice means most standalone charts, not just ones with a known accessibility requirement.

Contrast this with *accidental* redundancy: encoding `color` by the same field already shown on `x` or `y` adds a second channel that carries no new information — it doesn't help any reader, colorblind or not, and just adds a legend that repeats what the axis already says.
The difference is not the redundancy itself, it's whether the second channel earns its place: `color` + `shape` on the same categorical field earns it (accessibility, print-safety); `color` repeating an axis's own categories usually doesn't, unless the color also does other work (e.g. letting a reader keeping their eyes on a legend track categories that have scrolled off an axis).
When redundant color genuinely adds nothing, either drop the encoding or set `"legend": null` on it — see `references/scales-axes-legends.md` for that mechanic.

## Typography & titles

Keep axis, legend, and chart `title` values concise — a short noun phrase (`"Revenue"`, `"Region"`) rather than a full sentence; Vega-Lite auto-generates a `title` from the field name and any aggregate/bin/timeUnit annotation when none is set, so an explicit `title` is worth setting whenever that default reads awkwardly or ambiguously (e.g. relabeling `"sum_revenue"` to `"Revenue"`).
Set a top-level `description` on every spec that ships to an end audience: it doesn't render visually, but it's exposed as ARIA text to screen readers and is the only way a non-visual user gets a summary of what the chart shows — write it as a complete sentence describing the chart's content, not a restatement of the title.

## Labels over tooltips

Put essential facts directly on the chart as labels or annotations (a `text` mark layered on the data, or a `mark.tooltip`-independent value label) rather than relying solely on `tooltip` to carry them, because tooltips are interactive-only: they never appear in a static PNG/SVG export, which is this skill's primary output.
A value a reader must know at a glance — the exact number behind a bar, an outlier's identity — belongs in a label if the chart's output is ever static.
Adding a field to `tooltip` also isn't free of side effects: an un-aggregated field added to `tooltip` alongside an aggregated `y` becomes an implicit grouping key exactly like any other un-aggregated encoding, silently changing how rows are grouped before the aggregate runs — see `references/authoring-basics.md`'s aggregate-transform section for that mechanic, and check the aggregated values after adding a tooltip field, don't assume tooltip-only fields are aggregation-neutral.

## Note

A shipped `config` house theme (a top-level `config` block setting default fonts, colors, and mark styling once for every chart in a set) is out of scope for this skill's v1 — the guidance above (restrained palettes, colorblind-safe schemes, concise titles) should be applied per-spec for now, with a shared theme a candidate for a future version.

A complete spec pairing `color` and `shape` on the same nominal field — order status, shown with both a distinct color and a distinct point shape per status so the distinction survives grayscale printing or color vision deficiency:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Order delivery time by status, encoding status redundantly with both color and point shape so the distinction survives grayscale printing or color vision deficiency.",
  "data": {
    "values": [
      {"order_id": 1, "days_to_deliver": 2, "status": "on-time"},
      {"order_id": 2, "days_to_deliver": 3, "status": "on-time"},
      {"order_id": 3, "days_to_deliver": 4, "status": "on-time"},
      {"order_id": 4, "days_to_deliver": 7, "status": "delayed"},
      {"order_id": 5, "days_to_deliver": 9, "status": "delayed"},
      {"order_id": 6, "days_to_deliver": 8, "status": "delayed"},
      {"order_id": 7, "days_to_deliver": 1, "status": "cancelled"},
      {"order_id": 8, "days_to_deliver": 1, "status": "cancelled"}
    ]
  },
  "mark": "point",
  "encoding": {
    "x": {"field": "order_id", "type": "ordinal", "title": "Order"},
    "y": {"field": "days_to_deliver", "type": "quantitative", "title": "Days to deliver"},
    "color": {"field": "status", "type": "nominal", "title": "Status", "scale": {"scheme": "tableau10"}},
    "shape": {"field": "status", "type": "nominal", "title": "Status"}
  }
}
```

Rendered, this compiles to two independent ordinal scales keyed on the same `status` field — a `color` scale producing three swatches (on-time/delayed/cancelled) and a `shape` scale producing three distinct point shapes (triangle/square/circle) — and because both scales share the same field and domain, Vega-Lite merges them into a single "Status" legend whose three entries each show the matching color *and* shape together, rather than drawing two separate legends.
Every mark on the plot draws with the color and the shape that match its own `status` value: confirmed by rendering the spec and inspecting both the compiled Vega scales (`color` and `shape`, each domained on `status`) and the rendered image, where on-time points are pink triangles, delayed points are orange squares, and cancelled points are blue circles, matching the merged legend's three swatches exactly.

## Pitfalls

- **Redundant color that repeats an axis isn't automatically wrong, but it isn't automatically helpful either.** Check whether the second channel does independent work (accessibility, tracking off-axis) before adding it, and prefer `"legend": null` or dropping the encoding when it doesn't (see `references/scales-axes-legends.md`).
- **A missing `description` is invisible until a screen reader is the audience.** It costs one line and never renders on-screen, so there's no visual cue reminding an author to add it — set it as a habit on every spec, not just ones with a known accessibility requirement.
- **Tooltip fields are not accounting-neutral.** An un-aggregated field added only for `tooltip` still changes the implicit grouping key next to an aggregated channel; verify aggregated values after adding one (see `references/authoring-basics.md`).
