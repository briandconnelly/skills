# Trigger Cases for vega-lite

Positive prompts that MUST trigger this skill, and negative prompts that MUST NOT, checked against SKILL.md's frontmatter `description`.
The description scopes the skill to authoring, editing, repairing, or reviewing a raw Vega-Lite JSON specification, plus the mandatory render-and-validate loop, and it explicitly excludes Altair or other language bindings, low-level Vega specs, interactive params/selections (deferred), and generic charting-library or image-export tasks that are not raw Vega-Lite JSON.
Run each prompt against the skill catalog without naming the expected skill in the request; store the result in `tests/runs/YYYY-MM-DD-trigger.md`.

## Positive cases (must trigger)

| Prompt | Expected | Reason |
| --- | --- | --- |
| "Here's a Vega-Lite JSON spec that won't render — can you find out why and fix it?" | trigger | Repairing a raw Vega-Lite JSON spec is the skill's core scope. |
| "Write me a Vega-Lite spec for a bar chart of these monthly sales figures." | trigger | Authoring a new raw Vega-Lite spec from data is the skill's core scope. |
| "Review this Vega-Lite spec for correct semantic types and accessible color before we ship it." | trigger | Reviewing an existing Vega-Lite spec is explicitly named in the description. |
| "Add a facet by region to this Vega-Lite spec and make sure the scales stay independent." | trigger | Editing an existing spec's composition (`facet`/`resolve`) is explicitly named in the description. |
| "Render this Vega-Lite JSON to a PNG so I can check it actually looks right." | trigger | Validating a spec by actually compiling and rendering it is explicitly named in the description as a triggering condition. |
| "This chart's y-axis starts at 90 — here's the Vega-Lite spec, is that misleading?" | trigger | Reviewing scale/axis correctness on a raw Vega-Lite spec falls under both "review" and the scales/axes coverage named in the description. |

## Negative cases (must NOT trigger)

| Prompt | Expected | Reason |
| --- | --- | --- |
| "Make me an Altair chart in Python for this dataframe." | don't-trigger | The description explicitly excludes Altair and other language bindings; Altair is a Python API, not raw Vega-Lite JSON. |
| "Here's a low-level Vega spec (not Vega-Lite) — the signal expression is broken, can you fix it?" | don't-trigger | The description explicitly excludes low-level Vega specs; Vega's signals/scenegraph model is a different, lower-level spec format this skill does not cover. |
| "Make me a PNG chart of monthly revenue." | don't-trigger | No Vega-Lite spec is mentioned or implied; this is a generic image-export request the description explicitly excludes absent raw Vega-Lite JSON. |
| "Turn this spreadsheet of sales data into a chart in Google Sheets." | don't-trigger | A spreadsheet-native chart is not a raw Vega-Lite JSON spec; the description's scope is authoring/editing/repairing/reviewing that JSON format specifically. |
| "Add a brush selection so users can zoom into this time range on the chart." | don't-trigger | Interactive params/selections are explicitly named as deferred in the description; this request falls entirely outside the static v1 scope. |
