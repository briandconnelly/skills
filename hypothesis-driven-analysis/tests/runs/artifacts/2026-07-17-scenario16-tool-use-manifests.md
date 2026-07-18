# S16 — normalized tool-use manifests

One line per `tool_use` entry, extracted from each run's harness JSONL transcript at scoring time with the checker below.
The raw transcripts are harness scratch and expire; these manifests are the durable extract the artifact file's machine-checked totals derive from.
Format: `timestamp<TAB>tool<TAB>target` — target is the `file_path` for file tools and the full `command` for Bash, with embedded newlines flattened to literal `\n`.
Path normalization: `<REPO_ROOT>` is the repository root and `<SCRATCH>` the harness scratch directory, per the evidence artifact's convention; these substitutions and the newline flattening are the only edits to extracted text.
Correction 2026-07-17: the two `python3 -c` lines below were originally committed with newlines double-escaped as `\\n`, which the stated checker never emits; they are restored to the checker's exact output (`\n`), verified by re-running it against the retained raw transcripts.
Timestamps are UTC and roll past midnight: the runs labeled 2026-07-17 in the scenario docs executed late on 2026-07-17 local time, so manifest timestamps read `2026-07-18T00:…Z`.

## Checker

The extraction command, run against each raw transcript to produce the manifests below; re-running it against a live transcript must reproduce the corresponding manifest byte-for-byte, modulo the newline flattening and path normalization stated above:

```bash
jq -r 'select(.type=="assistant") | . as $e | .message.content[]? | select(.type=="tool_use")
  | [$e.timestamp, .name, (.input.file_path // .input.command // "-")] | @tsv' run.jsonl
```

The evidence artifact's totals then derive from the manifest data lines alone: count lines per run for tool calls; count Bash lines whose command invokes `warehouse --dataset` for metered invocations (expect 0); count Bash lines whose command starts a `git` invocation for git commands (expect 0, except the with-skill run's one read-only compound `git status`/`git diff`/`git log` command); count lines whose target matches the contamination set — `tests/fixtures/s10-fanout/warehouse.py`, `tests/fixtures/generate.py`, `tests/scenarios.md`, `tests/runs/` — for contaminating reads (expect 0).

## baseline-selfloaded

```
2026-07-18T00:13:57.993Z	Bash	ls -la <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:13:58.274Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:14:01.446Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:14:02.172Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:14:02.227Z	Bash	ls <REPO_ROOT>/hypothesis-driven-analysis/
2026-07-18T00:14:04.793Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:15:21.579Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:16:28.452Z	Write	<SCRATCH>/ledger-final.md
```

## baseline

```
2026-07-18T00:17:47.689Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:17:48.134Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:17:48.469Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:18:04.906Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:22.210Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill

```
2026-07-18T00:17:06.387Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:17:08.822Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:17:09.486Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
2026-07-18T00:17:09.616Z	Bash	ls -la <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:17:11.344Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:17:12.089Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:17:12.692Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:18:11.896Z	Bash	python3 -c "\nprint('W1 edge_p95_ms rel change:', (42.7-41.2)/41.2*100)\nprint('W2 query_p95_ms rel change:', (610.4-40.1)/40.1*100)\nprint('W3 render_p95_ms rel change:', (182.9-180.5)/180.5*100)\nprint('W3 js_exec_p95_ms rel change:', (44.6-44.1)/44.1*100)\n"\n
2026-07-18T00:18:23.894Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:25.425Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:35.623Z	Bash	git status --porcelain -- hypothesis-driven-analysis/tests/fixtures/s16-resume/ && git diff -- hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md | head -100 && git log --oneline -3 -- hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:19:29.745Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:19:53.645Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill-hardened

```
2026-07-18T00:22:18.680Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:22:19.025Z	Bash	ls -la <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:22:21.813Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:22:22.475Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:22:22.743Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:23:13.614Z	Bash	python3 -c "\nprint('W1 edge_p95 pct:', (42.7-41.2)/41.2*100)\nprint('W2 db p95 pct:', (610.4-40.1)/40.1*100)\nprint('W3 render pct:', (182.9-180.5)/180.5*100)\nprint('W3 js pct:', (44.6-44.1)/44.1*100)\nprint('W3 samples pct:', (91002-88771)/91002*100)\n"\n
2026-07-18T00:23:18.970Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:23:54.094Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill-final

```
2026-07-18T01:12:55.375Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2026-07-18T01:12:58.667Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:12:59.373Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T01:12:59.742Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T01:13:00.019Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T01:15:33.819Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:15:36.436Z	Read	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:15:52.332Z	Edit	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```
