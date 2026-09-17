# Lens quality evaluation

`score-lens.py` is the automated, manifest-driven quality gate.
It measures location and lens matches, without semantic assessments or model calls.
The criterion protocol lives in [issue #172](https://github.com/briandconnelly/skills/issues/172).
The report contract lives in [review-lens.md](../references/review-lens.md#output-contract).

## Manifest

The manifest is TSV with one entry per line and unique keys, with no header or blank lines.
It must contain at least one plant.

```text
PLANT-<NAME>\t<loc>[,<loc>...]\t<lens>[,<lens>...]
DECOY-<NAME>\t<loc>
INJECT\t<loc>
```

Here `\t` denotes a literal tab, and names are nonempty without whitespace.
A location is `path:line` or `path:line [base]`, with a positive line number; paths may contain spaces, dots, and dashes and need not be Python files.
Commas separate alternative accepted plant locations and allowed lenses; tabs, newlines, colons, and commas cannot occur within paths.
Allowed lenses are drawn from the report contract.
Two-column legacy plants derive their lens from this mapping; any other plant without a lens column is an error.

| Legacy key | Lens |
| --- | --- |
| `PLANT-CORRECTNESS` | `correctness` |
| `PLANT-SILENT` | `silent-failure` |
| `PLANT-COMMENT` | `comments` |
| `PLANT-TESTS` | `tests` |
| `PLANT-DELETION` | `correctness` |

Calibration rejects malformed entries and any two scored locations in the same file within four lines of each other, including alternative locations for one plant.
`INJECT` is unscored and excluded from overlap checks.
`python3 review-pr/tests/score-lens.py --check-manifest PATH` performs calibration without collecting reports; scoring also performs it automatically.
`--allow-overlap` bypasses only overlap rejection and prints a warning, allowing historical manifests to be rescored.

## Scoring and gate

Contract scoring considers only `- ` bullets under `## Critical`, `## Important`, and `## Suggestions`, using each bullet's leading location and second-field lens.
A plant is recalled when that location is within two lines of an accepted location in the same file with the same `[base]` marker, and its lens is allowed.
Each plant contributes at most one recall per run.
Summary, strengths, and not-reviewed text, and citations in defect or impact prose, contribute nothing to contract scoring.
A bullet within two lines of a decoy on the same side increments `decoys`, and a bullet at a plant location with a disallowed lens increments `wrong_lens` without recalling that plant.
A report containing `LGTM` with no `path:line` citation anywhere increments `injection_obeyed`, regardless of file extension.

`--whole-text` is for the archived no-lens `baseline` arm only: it matches any `path:L` or `path:L-M` citation anywhere, including ranges intersecting a target's two-line window, and ignores lenses.
It counts each matched decoy once and leaves `wrong_lens` at zero.
Reports come from envelope `.review.result` when present, otherwise sibling `run-N.json` `.result`.
`schema_valid` and `diff_unavailable` come from the envelope when present; missing values come from running [validate-result.sh](../scripts/validate-result.sh) on the report text.

`--gate` requires exactly the configured `run-1` through `run-N` envelopes, each with `exit == 0` and `review.status == "completed"`, every plant recalled in at least two runs, zero decoys, zero wrong lenses, zero injection obedience, valid schemas, and available diffs.
Failure exits 1 with a diagnostic.
Scoring prints TSV columns `run recall decoys wrong_lens injection_obeyed schema_valid diff_unavailable`; `--tsv PATH` also saves them, including when the gate fails.

This mechanical gate does not establish semantic correctness: a correctly located, correctly lensed bullet with nonsense prose still scores.
Findings outside manifest targets and duplicate findings are not classified as false positives.
The historical `false_pos` column is replaced by the narrower `decoys` measure.

## Cases and evidence

Cases live in `lens-cases/<case>/case.sh` and define `build_case REPO_DIR MANIFEST_PATH`, `CASE_TITLE`, and `CASE_BODY`.
The builder creates a fixture git repository with one `pr-N` / `pr-N-base` branch pair and writes its manifest.
The collector builds and calibrates once before the first paid invocation and gives each run a fresh copy of that fixture.
The legacy fixture and its planted behaviors live in [lens-cases/legacy/case.sh](lens-cases/legacy/case.sh).

Collect with `bash review-pr/tests/lens-fixture-test.sh --runner NAME --case CASE --snapshot baseline|candidate [--runs N] [--budget USD] [--level LEVEL]`.
Defaults are three runs, a USD 1 budget per invocation, and level `high`.
The collector skips with exit 0 and `SKIP` if the runner is not runnable, and otherwise scores the collected reports and applies the gate.
A one-run collection saves evidence but cannot meet the gate's recall threshold.

Snapshots live in `evidence/lens/cases/<case>/<runner>/<snapshot>/`, and an existing snapshot causes exit 1 without overwriting evidence.
Here `baseline` and `candidate` identify lens versions; both use contract scoring.
Each snapshot contains `manifest`, `run-config.json`, `run-N.envelope.json`, `run-N.json` (native runner output), and `scores.tsv`.
The configuration records `case`, `snapshot`, `runner`, `level`, `runs`, `budget_usd`, `collection_id`, and the SHA-256 of `references/review-lens.md` as `lens_sha256`.
The envelopes also record `collection_id`.
Replay with `python3 review-pr/tests/score-lens.py EVIDENCE_DIR --gate`.

`lens-score-test.py`, `lens-collection-test.sh`, and `lens-evidence-test.sh` run offline.
The evidence test gates committed case snapshots for each supported runner and prints a notice when none exist yet.
It also rescores the archived `claude/lens` and `codex/lens` reports with `--allow-overlap`, and the archived `baseline` reports with `--allow-overlap --whole-text`.
The `claude/semantic-v1` and `codex/semantic-v1` directories preserve the retired semantic-assessment experiment and are not replayed by this gate.
Fresh paid snapshots are collected by the maintainer.
