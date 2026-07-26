# Critical review: `vega-lite`

Reviewed 2026-07-24 against `SKILL.md`, all six files in `references/`, `examples/`, `scripts/render.py`, and `tests/`.
Unlike a read-only review, the executable claims here were re-run: `tests/test_render.py` (15 passed), `tests/check_specs.py` over `examples/ references/ SKILL.md tests/` (16 specs, all four stages PASS), and independent probes of the reference files' "confirmed" assertions using `vl-convert-python==1.9.0` — the same version the skill pins.

## Claims independently reproduced

These were re-derived from scratch rather than accepted from the prose, and every one holds.

- **Relative `data.url` silently fetches the wrong data.** `{"url": "data/cars.json"}` renders 402 marks pulled from the vega-datasets CDN; `data/zzz-nonexistent-dataset-xyz.json` renders a blank frame (10 SVG elements). Exactly as `validation-and-debugging.md:93` describes.
- **`log` scale on `bar` breaks with all-positive data.** Rendering `[5, 15, 21]` produced `d="M1,0h18v0h-18Z"` — the literal path string quoted at `scales-axes-legends.md:161`.
- **`x2` with an explicit `type` is a real schema violation**, not merely redundant (`authoring-basics.md:78`); the same spec with `type` removed validates clean.
- **The color+shape legend merge is accurate down to the swatches.** The compiled Vega emits one legend carrying both `stroke: color` and `shape: shape`; rendered strokes are `#4c78a8` / `#f58518` / `#e45756`, which under the alphabetical nominal domain gives cancelled=blue circle, delayed=orange square, on-time=pink triangle — exactly `aesthetics.md:82`.
- **Day-first dashes really are misparsed.** `01-06-2024` / `02-06-2024` / `03-06-2024` with no `format.parse` land on Jan 6 / Feb 6 / Mar 6, not June 1–3.

That level of "I ran it and here is the actual output" is unusual and is the strongest thing about this skill.

## Findings

### 1. Scenario 1's central criterion is wrong, and the eval cannot discriminate

I rendered the scenario fixture with and without the parse block the criterion demands:

```
B  no-parse mm/dd/yyyy: ['2024-01-06', ..., '2024-01-07', ..., '2024-01-08']
B2 parsed  mm/dd/yyyy: ['2024-01-06', ..., '2024-01-07', ..., '2024-01-08']
```

Identical.
`tests/scenarios.md:46` requires `data.format.parse` mapping `day` to `"date:'%m/%d/%Y'"` and calls the pattern "required"; `tests/scenarios.md:50` predicts a skill-less baseline will plot "the points on the wrong dates."
Neither holds, because the fixture is declared US-style `MM/DD/YYYY` — the very order the engine already assumes for slash dates.
The parse is a no-op, the predicted baseline failure cannot occur, and a correct skill-less spec would be scored as failing (b).

The underlying guidance is sound; only this fixture is miscast.
Fix the fixture rather than the criterion: make the source genuinely day-first (e.g. `06/01/2024` *meaning* 6 January), which is the case where the default silently lands on June 1.

The same overstatement appears in the prose that the scenario derives from.
`authoring-basics.md:14` and `SKILL.md:49` describe slash-separated dates as having "locale-dependent" month/day order; under vl-convert the order is deterministic month-first.
The risk is real but it is *source*-dependent (day-first input), not locale-dependent, and the current wording will keep producing fixtures like this one.

### 2. An enforced rule that no bar, area, or rect chart can satisfy

`SKILL.md:52` requires that categorical distinctions be carried on a redundant channel — `shape` or `strokeDash` — "not on color alone."
`shape` applies only to point-like marks and `strokeDash` only to line-like ones, so for `bar`, `area`, and `rect` the rule has no compliant form at all.

The skill's own examples demonstrate this: `scales-axes-legends.md:72` (stacked bar, region on color alone), `composition.md`'s facet and layer specs, and `examples/faceted.vl.json` all violate it, and none can be repaired as written.
Only `examples/scatter.vl.json` and the `aesthetics.md` point spec comply, both because they use `point`.

An agent that takes the rule literally on a bar chart is stuck with no escape hatch.
The rule needs an explicit mark-class exemption plus the alternatives that actually exist for width-bearing marks: direct value labels, faceting instead of color, or deliberate ordering plus a clear legend.

### 3. No `width` / `height` guidance anywhere

Grep across `SKILL.md`, all six references, and all examples returns zero mentions of `width`, `height`, or `autosize` as spec properties.
For a skill whose entire spine terminates in "render it to a PNG and look at it," the ~200px default plot is the first thing an author must override to get a legible image.
It also interacts directly with advice the skill *does* give: `scales-axes-legends.md:59`'s `labelAngle: -90` default exists to fit long category names into a width the skill never tells you to set.

### 4. The schema stage fails closed and swallows the better diagnostic

`run_all` (`scripts/render.py:117`) returns immediately on a schema FAIL, so `compile` never runs.
For `"type": "nominl"` that means the only message an author sees is the entire spec echoed back at `<root>` — bad enough that `validation-and-debugging.md:61-63` spends a paragraph apologizing for it.
The compile stage, had it run, reports `Invalid field type "undefined"` — localized, actionable, and free.

Two cheap fixes, either sufficient: on a schema FAIL still attempt `compile` and report both stages, or add a `--no-schema` flag so an author can reach the better error on demand.
Right now there is no way to get past a schema FAIL without editing the script.

### 5. Nothing enforces any of this

`.github/workflows/prek.yml` runs `prek run --all-files`, and `prek.toml` carries local hooks for `agent-bot-identity` and `agent-friendly-mcp` — but none for vega-lite.
`tests/scenarios.md:166-167` says both test files are "run manually or in CI"; in practice, neither runs in CI.

The stated reason for having no hook (`scenarios.md:168` — a ~30 MB `vl-convert` wheel and network on every commit) justifies excluding `check_specs.py`, but not `test_render.py`: 13 of its 15 tests use stub `Deps` and complete offline in milliseconds.
Only `test_integration_renders_inline_bar_png` and `test_preflight_reports_versions` need the wheel.
A hook over the stub-only subset would cost nothing and would catch regressions in the staging logic, exit codes, and cache repair.

### 6. `examples/` is unreachable from the skill

No file in `SKILL.md` or `references/` points at `examples/`.
The only mention anywhere is `tests/scenarios.md:166`, which names it while describing the test harness.
Six curated, validated specs — bar, line, scatter, layered, faceted, parsed-dates — are effectively invisible to an agent using the skill.

They are also inconsistent with the skill's own title rule (`SKILL.md:54`): `examples/faceted.vl.json` and `examples/layered.vl.json` ship bare `g` / `n` / `a` / `t` / `v` axis titles, which is precisely the awkward auto-derived title the rule says to replace.
`bar.vl.json` and `line.vl.json` do set titles, so the set contradicts itself.

### 7. Trigger cases have never been run

`tests/trigger_cases.md:5` instructs storing results in `tests/runs/YYYY-MM-DD-trigger.md`; no such file exists, and `tests/runs/` contains only the scenario-2 seed run.
Commit `2074981` ("broaden description triggers") widened the description *after* the cases were written, without re-running them.
The description is now 877 characters against the 1024-character cap enforced by `check-skill-frontmatter`, much of it a long negative-scope clause that has never been tested against a real skill catalog.

## Minor

- The schema cache (`~/.cache/vega-lite-skill/`) never expires and is fetched from the *live* v6 schema, while `compile`/`render` use vl-convert's embedded 6.4. If the published schema advances, `schema` can PASS specs the renderer rejects. `--vl-version`'s help text notes the targets differ but the drift risk isn't documented.
- The "illustrative snippets use ```jsonc, real specs use ```json" convention is load-bearing for `check_specs.py` but enforced nowhere. `_looks_like_spec` accepts any dict containing `mark`, `layer`, or `facet`.
- "Labels over tooltips" (`SKILL.md:55`, `aesthetics.md:43`) is an enforced rule, but text-mark layering is an admitted documentation gap (`SKILL.md:14`). The rule has no supporting mechanic anywhere in the skill.
- `aesthetics.md:17`'s "no built-in palette is reliably colorblind-safe" is slightly strong; ColorBrewer `dark2` and `set2` qualify at three or fewer classes.
- `render.py` writes every line — stage results, preflight, final verdict — to stderr and nothing to stdout.

## Credit where due

The evidence discipline in `scales-axes-legends.md`'s Pitfalls section is the best part of the skill: measured canvas heights (3015px vs 343px), actual SVG path strings, and the ranged-vs-single-value bar distinction are all things someone genuinely ran, and all of them reproduce.
`validation-and-debugging.md`'s relative-URL caveat is the single most useful paragraph here — it documents a silent-wrong-data failure that most authors would never think to test for.
And `tests/scenarios.md:161-162` disclosing that the seed run was author-scored with full knowledge of the criteria, and therefore records no efficacy evidence, is the right call and rare.

## Suggested order of work

1. Fix the Scenario 1 fixture and the "locale-dependent" wording it derives from (finding 1) — it is the only finding where the skill would actively mis-score a correct answer.
2. Add the mark-class exemption to the redundant-encoding rule (finding 2).
3. Add sizing guidance to `scales-axes-legends.md` and point `SKILL.md`'s spine at it (finding 3).
4. Add a prek hook over the offline subset of `test_render.py` (finding 5).
5. Link `examples/` from `SKILL.md` and normalize its titles (finding 6).

## Meta-review of this review

This is a strong audit draft, but it needs factual corrections before it can serve as the authoritative review.
Its evidence-first approach is valuable, while the test-count error, false example classification, and runtime-specific date conclusion weaken its reliability.

### 1. Correct the reported test evidence

The claim above that `tests/test_render.py` produced 15 passes is incorrect.
Running that file with its declared dependencies produces 12 passes.
Running the complete `vega-lite/tests/` directory produces 15 passes because it includes the three tests in `tests/test_check_specs.py`.

The later claim that 13 of 15 renderer tests use stub dependencies is therefore also incorrect.
Three of the 12 renderer tests require `vl-convert`: `test_integration_renders_inline_bar_png`, `test_preflight_reports_versions`, and `test_main_reports_missing_spec_file_cleanly`.
The missing-file test needs `vl-convert` because `main()` calls `preflight()` before attempting to read the input file.
Nine renderer tests avoid `vl-convert`, although the schema-violation test still requires `jsonschema`.

The review should record the exact commands used and distinguish the 12-test renderer file from the 15-test complete suite.

### 2. Reframe the categorical-redundancy finding

The claim that the composition facet and layer examples violate the color-redundancy rule is incorrect.
Those examples do not encode categorical identity through color alone.
The facet example carries region through a facet channel, while the layer examples use position, mark type, or constant styling.
`examples/faceted.vl.json` likewise contains no color encoding.

The statement that `strokeDash` applies only to line-like marks is also too categorical.
Vega-Lite defines `strokeDash` as a general mark-property channel, so stroked bars, areas, and rects can use it.
Such border styling may still be too weak to provide effective categorical accessibility, especially for filled marks.

The valid underlying finding is that the enforced rule gives filled marks insufficient and potentially ineffective accessibility guidance.
The stacked-bar example in `scales-axes-legends.md` remains a clear internal contradiction because it carries region on color alone.

### 3. Narrow the date conclusion to the evaluated runtime

The review correctly demonstrates that Scenario 1 cannot discriminate under the pinned `vl-convert` runtime.
US-style slash dates already land on the requested dates in that runtime, so the scenario's predicted baseline failure is unsupported by its harness.

The conclusion that slash-date behavior is deterministically month-first and purely source-dependent goes too far.
Vega documents that `toDate()` falls back to JavaScript `Date.parse()`, whose behavior can differ across browsers.
That portability concern matters because the skill also covers Vega-Embed and notebook contexts.

The finding should say that the fixture is non-discriminating under the pinned evaluation runtime, while explicit parsing remains prudent for portable handling of ambiguous slash dates.
“Runtime-dependent” is more accurate than either “locale-dependent” or “deterministically month-first.”
A clearly declared day-first fixture would test the intended failure more effectively.

### 4. Strengthen the CI recommendation

The review too readily accepts the claim that dependency installation requires a network download on every commit.
`uv` caches downloaded dependencies, so the `vl-convert` wheel is not normally downloaded on every local run.

More importantly, an offline unit-test subset cannot enforce the skill's defining promise that shipped specifications compile and render.
The fast unit subset can run in a local hook if desired.
The complete renderer tests and `tests/check_specs.py` should run in CI, preferably only when `vega-lite/**` changes and with the `uv` cache enabled.

### 5. Keep the sizing finding but make it context-sensitive

The absence of practical `width`, `height`, and `autosize` guidance is a valid finding.
The claim that every chart has an approximately 200-pixel plot that must be overridden is too absolute.
Continuous dimensions default to approximately 200 pixels, while discrete dimensions normally derive their size from a step per distinct value.
Embedded charts may need responsive `"container"` sizing rather than fixed dimensions.

The recommendation should cover fixed static exports, discrete-step sizing, responsive embeds, and the sizing limitations of composed views.

### 6. Improve the schema diagnostic rather than primarily bypassing it

The review correctly identifies that `run_all` stops after a schema failure.
The compiler's `Invalid field type "undefined"` message is more specific than the schema dump, but it is not truly localized because it does not identify the offending field path.

A `--no-schema` option would weaken the validator's staged contract.
The primary fix should traverse `jsonschema.ValidationError.context` and report the most relevant leaf errors and paths.
Compilation after a schema failure could be an explicitly supplemental diagnostic while the overall result remains failed.

### 7. Make the executable evidence reproducible

The review says its independent probes were rerun, but it provides neither exact commands nor durable probe fixtures.
The abbreviated date output cannot be reconstructed from this document alone.
The incorrect test count demonstrates why the commands and full outputs should be preserved.

Add a reproduction appendix or convert the independent probes into committed regression tests.

### 8. Separate valid findings from weak signals

The absence of recorded trigger runs is a valid finding.
The description being 877 characters against a 1024-character limit is not itself a defect.
The meaningful risk is untested trigger behavior, not proximity to the length cap.

Writing all CLI diagnostics to stderr is also not inherently defective.
That point should remain only if the review identifies a concrete affected workflow and proposes a clear stdout/stderr contract.

### 9. Conform the review to repository Markdown style

This file contains multiple sentences on the same Markdown source line.
Before committing it, reflow the original sections so every sentence occupies its own line as required by the repository's `AGENTS.md`.

### Revised priority order

1. Correct the test commands, counts, and offline-subset analysis.
2. Correct the categorical-redundancy examples and reframe the filled-mark accessibility gap.
3. Rewrite the date finding as a pinned-runtime evaluation flaw rather than a universal parsing claim.
4. Require the complete renderer and specification checks in CI.
5. Add context-sensitive sizing guidance.
6. Improve schema error localization.
7. Link and normalize the examples.
8. Run and record the trigger evaluation.
9. Preserve the probes as reproducible tests or an appendix.
