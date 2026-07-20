# Transforms

This file owns the view-level `transform` array for v1: `filter` and `calculate`.
Encoding-level `bin`, `timeUnit`, and `aggregate` — transforms attached directly to a channel rather than living in the `transform` array — are `references/authoring-basics.md`'s territory.
`layer`/`facet`/`resolve` composition is `references/composition.md`'s territory.

## When to transform in-spec vs upstream

Default to in-spec `filter`/`calculate` for small, chart-local derivations: a threshold cutoff, a derived ratio, a unit conversion — anything that exists only to make this one chart correct.
Preprocess upstream instead when the data is large enough that shipping it inline is impractical, when the same derived logic is shared across multiple charts and would otherwise be duplicated in every spec, when the operation is security-sensitive (redacting or masking fields before they ever reach a spec an author can inspect), or when Vega-Lite doesn't support the operation at all in this skill's v1 scope (see Deferred transforms below).
This is a default with exceptions, not an absolute: the question is always whether the derivation is small and chart-local, or big/shared/sensitive/unsupported.

## `filter`

A `filter` transform drops rows before they reach the mark, and takes one of two predicate forms.

**Expression string** — an arbitrary Vega expression that evaluates to truthy/falsy per row, referencing fields as `datum.<fieldName>`:

```jsonc
{"filter": "datum.revenue > 10"}
```

**Field predicate object** — a structured predicate keyed by `field` plus one comparison:

```jsonc
{"filter": {"field": "amount", "range": [0, 100]}}
{"filter": {"field": "category", "oneOf": ["A", "B"]}}
{"filter": {"field": "status", "equal": "active"}}
```

`range` keeps values within an inclusive `[min, max]`, `oneOf` keeps values matching any in a list, and `equal` keeps values matching exactly one.
Either form is a valid single entry in the `transform` array; reach for the expression string when the condition is a computation (`>`, `&&`, arithmetic) and the field predicate object when it's a plain membership or range check.

## `calculate`

A `calculate` transform derives a new field from existing ones with a Vega expression, storing the result under the name given in `"as"`:

```jsonc
{"calculate": "datum.price * datum.quantity", "as": "revenue"}
```

The new field (`revenue` above) becomes available to any encoding or later transform in the same spec, exactly like a field that was already in the data.
This is distinct from encoding-level `aggregate` (a field-def property that collapses rows into a summary statistic, covered in `references/authoring-basics.md`): `calculate` runs per-row over the `transform` array before encoding, while `aggregate` runs at the encoding channel, after the `transform` array, and can combine multiple rows into one.

A complete spec using both — filtering out-of-stock items, then deriving `revenue` for the ones that remain:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Revenue per item, excluding out-of-stock items and deriving revenue via calculate.",
  "data": {
    "values": [
      {"item": "Widget", "price": 10, "quantity": 5},
      {"item": "Gadget", "price": 20, "quantity": 3},
      {"item": "Gizmo", "price": 15, "quantity": 0},
      {"item": "Doohickey", "price": 8, "quantity": 12},
      {"item": "Thingamajig", "price": 25, "quantity": 2}
    ]
  },
  "transform": [
    {"filter": "datum.quantity > 0"},
    {"calculate": "datum.price * datum.quantity", "as": "revenue"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "item", "type": "nominal", "title": "Item"},
    "y": {"field": "revenue", "type": "quantitative", "title": "Revenue"}
  }
}
```

Drop the `transform` array from that spec and re-render it: the chart goes empty — zero bars, an x-axis with "0 values," and a y-axis fixed at "0 to 0" — because `revenue` no longer exists for any row to encode, and the zero-quantity `Gizmo` row that `filter` was dropping is no longer excluded either (it just has nothing to plot alongside the rest).
With the transform, four bars render (`Widget` 50, `Gadget` 60, `Doohickey` 96, `Thingamajig` 50); `Gizmo` never appears.

## Deferred transforms

`window`, `joinaggregate`, `fold`, `pivot`, `lookup`, `impute`, `regression`, `loess`, and `density` are out of this skill's v1 scope.
Author these upstream (in the data pipeline that produces the spec's inline values) or wait for v2 — do not invent in-spec guidance for them here.

## Pitfalls

- **Filter runs before encoding-level `aggregate`, not after.** A `filter` transform only ever sees raw row values, so `{"filter": "datum.count > 5"}` fails if `count` is a field produced by an encoding's `"aggregate": "count"` rather than a raw column, since the aggregate hasn't happened yet when the transform array runs — to filter on an aggregated result, aggregate the rows first (a view-level `aggregate` transform, or upstream) and filter that output instead.
- **Expression strings need `datum.`, not a bare field name.** `"datum.revenue > 10"` works while `"revenue > 10"` does not, because the expression evaluates in a scope where the current row is the `datum` object rather than its fields as bare identifiers, and a field name with spaces or other non-identifier characters needs bracket notation such as `datum["order date"]`.
