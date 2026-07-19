# Transcript evidence — Ninth wave, S17 trigger before/after, S2/S3 guards, and the check_prereg calibration re-run

Six Sonnet subagent trigger arms dispatched 2026-07-18, scored in `tests/runs/2026-07-18-scenario17-trigger-{pre,post-a,post-b,post-para}.md` and `tests/runs/2026-07-18-scenario{2,3}-trigger-postdesc.md`.
Transcripts were snapshotted to scorer scratch and processed with the committed instrument, `tests/extract_evidence.py` (`identity`, `manifest --normalize-root`, and `text` subcommands); machine-checkable claims below derive from those manifests and re-executed commands, not from any run's self-report.
The `pre` arm ran before the description edit `aa1470e` and its transcript's prompt carries the old frontmatter description verbatim (no adjudication clause, unqualified `bounded descriptive queries` exclusion); all five other arms' prompts carry the amended description verbatim — both verified by reading the first user message of each transcript, so the before/after attribution is machine-established, not assumed.

## Transcript digests (sha256)

Piped through `shasum -a 256` in the scoring session (never hand-copied); the `identity` subcommand's own digests of the same files agree byte-for-byte on all six:

```text
c993a199f69b8b44fe1c6b5d20504675267664ef5733b80cab577c650a2e4f74  s17-trigger-pre.jsonl
56a3c00c1e9873914a90c53c1e8663cd9e89863e8148cb9900c63e722333dce9  s17-trigger-post-a.jsonl
548522fd756b7e626a1c12a8a965b2f9b82ea356d5cdd8f71369b1855294e943  s17-trigger-post-b.jsonl
1a01dd29926ff5fbcaa0fc2edd120537bc900ae86812a117562c4a3f8c028abf  s17-trigger-post-para.jsonl
ed53e8934e50dd807aa5bc3fdc30bbba58e6b4455c8738e2adf4b2bce558881f  s2-trigger-postdesc.jsonl
8893c358b6b735a6a27ea11d8ed4e7bde2c593c0bbb240ddac48658f540eb118  s3-trigger-postdesc.jsonl
```

## Identity counts vs harness-reported

| Transcript | tool_use (identity) | breakdown | paired results | harness-reported | match |
| --- | --- | --- | --- | --- | --- |
| s17-trigger-pre | 3 | Bash: 3 | ok: 3 | 3 | yes |
| s17-trigger-post-a | 5 | Bash: 4, Read: 1 | ok: 5 | 5 | yes |
| s17-trigger-post-b | 6 | Bash: 5, Read: 1 | ok: 6 | 6 | yes |
| s17-trigger-post-para | 5 | Bash: 3, Read: 2 | ok: 5 | 5 | yes |
| s2-trigger-postdesc | 2 | Bash: 1, Read: 1 | ok: 2 | 2 | yes |
| s3-trigger-postdesc | 3 | Bash: 2, Read: 1 | ok: 3 | 3 | yes |

Token totals in the run files and wave table (33,664 / 43,273 / 43,664 / 49,251 / 38,671 / 33,952) are harness-reported, per the suite's convention.
An attempted independent re-derivation from the transcripts' embedded usage fields did not reproduce them under any simple combination (input+output, with or without cache-creation tokens, all overshoot), so they rest on the harness's accounting alone; the relative ordering across arms is consistent between the two accountings.

## Machine checks: zero git commands, zero repository writes

Across all six manifests (36 pattern-bearing rows), each scan below returned zero matches, and each scan's pattern was validated against a planted positive in the same session before its negative was trusted:

- git commands: `grep -E '(^|[^a-zA-Z])git[[:space:]]'` over all six manifests — no match; the same pattern fires on a planted `Bash ok git status` row.
- write tools: `awk '$3=="Write"||$3=="Edit"||$3=="NotebookEdit"'` over all six manifests — zero rows; fires on a planted Write row.
- bash redirects into the repository: `grep -E '(>|>>|tee)[[:space:]]*"?<REPO_ROOT>'` — no match; fires on a planted `echo hi > <REPO_ROOT>/x.md` line.

All file writes observed in any arm target the per-arm scratch directories (`<SCRATCH>/s17-arms/*`, `<SCRATCH>/s2-arm`, `<SCRATCH>/s3-arm`) via heredoc scripts only.

## Verbatim skill-selection sentences

Each arm was instructed to state its skill choice; these are the transcript sentences, quoted exactly.

**pre** (final message): "**Skill used:** None. This is a bounded computational/verification query (compute one metric, compare to a fixed threshold), not an explanatory/diagnostic investigation, a bug to debug, or a visualization request — the three candidate skills' own scope notes rule them out (hypothesis-driven-analysis explicitly excludes \"bounded descriptive queries\")."
The pre arm's first choice statement appears after its first tool call, not before as instructed (recorded in the run file as a fidelity note, not scored).

**post-a** (opening): "I am using the hypothesis-driven-analysis skill, since this task asks me to adjudicate a specific claim (\"p95 exceeded 500ms yesterday\") against data, which is exactly the \"someone says p95 exceeded 500ms yesterday\" example in that skill's description."

**post-b** (opening): "I'm using the hypothesis-driven-analysis skill, because this is a claim-adjudication question (\"checkout p95 exceeded 500ms yesterday\") requiring evidence-based investigation with competing explanations for what the true p95 is/was."

**post-para** (opening): "I am using the hypothesis-driven-analysis skill, since this is exactly the \"someone claims a metric crossed a threshold\" adjudication case it's designed for."

**s2 guard** (final message): "Skill used: none — this is a bounded descriptive computation (a single column's median), not a competing-hypotheses question, so per the hypothesis-driven-analysis skill's own scope note it should be answered directly."

**s3 guard** (opening): "I am using the **systematic-debugging** skill (not hypothesis-driven-analysis), because this is a reproducible test failure with a specific error message, and hypothesis-driven-analysis explicitly excludes that case in favor of a dedicated debugging skill."

Activation facts behind the S17 scores: the pre manifest contains no `Read` of any skill file; post-a and post-b each open with `Read <REPO_ROOT>/hypothesis-driven-analysis/SKILL.md` at ordinal 1; post-para opens with `SKILL.md` (ordinal 1) then `references/ledger-template.md` (ordinal 2); the s2 and s3 guards read no skill file.
Outcome cells: post-a `REFUTED` (outside the mini template's closed set `CONSISTENT / CONTRADICTED / NON_DISCRIMINATING` — issue #73-class vocabulary drift, recorded in its run file); post-b and post-para `CONTRADICTED`.

## Fixture digests the arms saw (sha256)

```text
eea96d9793a56153d23f7412a1cebbba2ac0fb2eadd0acb4f1b9a41650a8523c  tests/fixtures/s11-mini/checkout_latency.csv
39486b25560ac523af351bf4376d1fe9e4c8d2c267c63b95e7e9fa7b1ada1ddc  tests/fixtures/s1-conversion/orders.csv
47279ba7b5d49cc6523c692a77d90bbdbe9e8881d08cdb51216050fe7a9b28b9  tests/fixtures/s3-bug/test_dateutils.py
```

## check_prereg.py calibration re-run (post-`71bb4b5`)

The three constructed calibration cases from the Task 4 report were re-executed in this scoring session against the committed script (which now includes `71bb4b5`'s fail-closed invalid-pattern path), using the same on-disk TSVs and the same `--ledger-pattern 'ledger' --data-pattern 's1-conversion'` invocations.
All three verdicts match the Task 4 report (3/3):

```text
$ check_prereg.py clean.tsv ...
PREREG_WRITE: ordinal 2 (Write -> /s/ledger.md)
CLEAN: no data-matching tool_use precedes the ledger write
exit=0

$ check_prereg.py classify.tsv ...
PREREG_WRITE: ordinal 2 (Write -> /s/ledger.md)
CLASSIFY: 1 data-matching tool_use(s) precede the ledger write; classify each as orientation or analysis in the evidence artifact:
  - ordinal 1: Bash [ok] head -5 /repo/tests/fixtures/s1-conversion/orders.csv
exit=1

$ check_prereg.py unverifiable.tsv ...
UNVERIFIABLE: no executed Write/Edit matches --ledger-pattern 'ledger'; preregistration ordering cannot be established from this transcript
exit=2
```

Honest discrepancy, cosmetic only: the on-disk TSVs' target cells differ from the Task 4 report's rendering (`/s/ledger.md` where the report printed `<SCRATCH>/ledger.md`, and a simplified `awk` string) — the tool/status/ordering structure and every verdict line are identical, so the three behavior classes the calibration exercises are unchanged.

The fail-closed invalid-pattern path added by `71bb4b5` was exercised once, on the valid `clean.tsv`:

```text
$ check_prereg.py clean.tsv --ledger-pattern '(' --data-pattern 's1-conversion'
UNVERIFIABLE: invalid pattern '(': missing ), unterminated subpattern at position 0
exit=2
```

Exit 2 with an `UNVERIFIABLE` line, as required: an unusable pattern is reported as inability to verify, never as a clean result.
