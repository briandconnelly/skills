# S16 — normalized tool-use manifests

One line per `tool_use` entry, extracted from each run's harness JSONL transcript at scoring time with the checker below.
The raw transcripts are harness scratch and expire; these manifests are the durable extract the artifact file's machine-checked totals derive from.
Format: `timestamp<TAB>tool<TAB>target` — target is the `file_path` for file tools and the full `command` for Bash, with embedded newlines flattened to literal `\n`.

## Checker

The extraction command, run against each raw transcript to produce the manifests below; re-running it against a live transcript must reproduce the corresponding manifest byte-for-byte (modulo the newline flattening):

```bash
jq -r 'select(.type=="assistant") | . as $e | .message.content[]? | select(.type=="tool_use")
  | [$e.timestamp, .name, (.input.file_path // .input.command // "-")] | @tsv' run.jsonl
```

The evidence artifact's totals then derive from the manifest data lines alone: count lines per run for tool calls; count Bash lines whose command invokes `warehouse --dataset` for metered invocations (expect 0); count Bash lines whose command starts a `git` invocation for git commands (expect 0, except the with-skill run's one read-only `git status`/`git diff`); count lines whose target matches the contamination set — `s10-fanout/warehouse.py`, `tests/fixtures/generate.py`, `tests/scenarios.md`, `tests/runs/` — for contaminating reads (expect 0).

## baseline-selfloaded

```
2026-07-18T00:13:57.993Z	Bash	ls -la /Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:13:58.274Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:14:01.446Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:14:02.172Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:14:02.227Z	Bash	ls /Users/bdc/projects/skills/hypothesis-driven-analysis/
2026-07-18T00:14:04.793Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:15:21.579Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:16:28.452Z	Write	/private/tmp/claude-501/-Users-bdc-projects-skills/38dd8eb5-5b41-4791-9cf6-d2800ccb9a6c/scratchpad/ledger-final.md
```

## baseline

```
2026-07-18T00:17:47.689Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:17:48.134Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:17:48.469Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:18:04.906Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:22.210Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill

```
2026-07-18T00:17:06.387Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:17:08.822Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:17:09.486Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/references/subagent-briefs.md
2026-07-18T00:17:09.616Z	Bash	ls -la /Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:17:11.344Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:17:12.089Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:17:12.692Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:18:11.896Z	Bash	python3 -c "\\nprint('W1 edge_p95_ms rel change:', (42.7-41.2)/41.2*100)\\nprint('W2 query_p95_ms rel change:', (610.4-40.1)/40.1*100)\\nprint('W3 render_p95_ms rel change:', (182.9-180.5)/180.5*100)\\nprint('W3 js_exec_p95_ms rel change:', (44.6-44.1)/44.1*100)\\n"\\n
2026-07-18T00:18:23.894Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:25.425Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:18:35.623Z	Bash	git status --porcelain -- hypothesis-driven-analysis/tests/fixtures/s16-resume/ && git diff -- hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md | head -100 && git log --oneline -3 -- hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:19:29.745Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:19:53.645Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill-hardened

```
2026-07-18T00:22:18.680Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/SKILL.md
2026-07-18T00:22:19.025Z	Bash	ls -la /Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/
2026-07-18T00:22:21.813Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T00:22:22.475Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T00:22:22.743Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T00:23:13.614Z	Bash	python3 -c "\\nprint('W1 edge_p95 pct:', (42.7-41.2)/41.2*100)\\nprint('W2 db p95 pct:', (610.4-40.1)/40.1*100)\\nprint('W3 render pct:', (182.9-180.5)/180.5*100)\\nprint('W3 js pct:', (44.6-44.1)/44.1*100)\\nprint('W3 samples pct:', (91002-88771)/91002*100)\\n"\\n
2026-07-18T00:23:18.970Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T00:23:54.094Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```

## with-skill-final

```
2026-07-18T01:12:55.375Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/SKILL.md
2026-07-18T01:12:58.667Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:12:59.373Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-briefs.md
2026-07-18T01:12:59.742Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/worker-returns.md
2026-07-18T01:13:00.019Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/references/ledger-template.md
2026-07-18T01:15:33.819Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:15:36.436Z	Read	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
2026-07-18T01:15:52.332Z	Edit	/Users/bdc/projects/skills/hypothesis-driven-analysis/tests/fixtures/s16-resume/ledger.md
```
