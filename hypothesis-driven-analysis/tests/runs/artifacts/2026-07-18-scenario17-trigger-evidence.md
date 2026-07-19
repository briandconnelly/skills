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

## Machine checks: zero git commands, zero write-tool rows, zero absolute-path repo redirects

Across all six manifests (24 rows, one per tool_use), each scan below returned zero matches, and each scan's pattern was validated against a planted positive in the same session before its negative was trusted:

- git commands: `grep -E '(^|[^a-zA-Z])git[[:space:]]'` over all six manifests — no match; the same pattern fires on a planted `Bash ok git status` row.
- write tools: `awk '$3=="Write"||$3=="Edit"||$3=="NotebookEdit"'` over all six manifests — zero rows; fires on a planted Write row.
- bash redirects into the repository: `grep -E '(>|>>|tee)[[:space:]]*"?<REPO_ROOT>'` — no match; fires on a planted `echo hi > <REPO_ROOT>/x.md` line.

Correction 2026-07-18 (Codex cross-review): the row-count sentence above originally read "36 pattern-bearing rows"; the six manifests contain 24 rows — 3+5+6+5+2+3, one per tool_use, agreeing with the identity table above — re-derived in the close-out session by regenerating all six manifests with the committed instrument and counting with `wc -l`.
The zero-match results are unaffected: all three scans were re-run over the regenerated manifests in the same close-out session, zero matches, planted positives fire.

Scope narrowed 2026-07-18 (Codex cross-review): these scans establish exactly that the manifests contain no Write/Edit/NotebookEdit rows and no Bash command text redirecting (`>`, `>>`, `tee`) to an absolute repository path.
They do not cover relative redirects after a `cd` into the repository (two arms `cd` into fixture directories), file-writing utilities without redirects (`touch`, `cp`, `sed -i`), or in-interpreter writes (a Python `open(..., 'w')` inside a heredoc or `-c` script).
The heredoc and `-c` bodies visible in the manifests were read and contain only stdout prints and reads of the fixtures, and every observed write path targets the per-arm scratch directories (`<SCRATCH>/s17-arms/*`, `<SCRATCH>/s2-arm`, `<SCRATCH>/s3-arm`) — but that reading is a scorer judgment, not a machine check.
Two corroborating checks were run in the close-out session and came back clean: `git status --porcelain -- hypothesis-driven-analysis/` printed nothing (no modified and no untracked files under the skill directory, which covers the write paths the scans miss for both tracked and untracked non-ignored files), and the three fixture digests below were recomputed with `shasum -a 256` and match the recorded values byte-for-byte.
These corroborate state at close-out time; they cannot rule out a file written and deleted between run and close-out.

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

## Final-description probes (post-`dd39d96`), 2026-07-18

Two Sonnet probe arms were dispatched after commit `dd39d96` re-scoped the description's exclusion clause, to validate the final wording in both directions (trigger and guard); scored in `tests/runs/2026-07-18-scenario17-trigger-finaldesc.md` and `tests/runs/2026-07-18-scenario2-trigger-finaldesc.md`.
Both transcripts' first user messages carry the final exclusion wording verbatim ("or for direct retrieval and bounded descriptive queries where nothing is asserted (answer those directly)") and not the pre-`dd39d96` ordering — checked programmatically against the committed `SKILL.md` line 3 in the close-out session, so the attribution is machine-established.

sha256 (piped through `shasum -a 256` in the close-out session; the `identity` subcommand's own digests agree byte-for-byte):

```text
8bc21829fc70c99d5e11a5ab8a0feee23d62ec1d25160e613f4dd8aae535a209  s17-trigger-finaldesc.jsonl
62b231a64591cea9c6c17185a63b4f32828298a6059e41a30836111b17923feb  s2-trigger-finaldesc.jsonl
```

| Transcript | tool_use (identity) | breakdown | paired results | harness-reported | match |
| --- | --- | --- | --- | --- | --- |
| s17-trigger-finaldesc | 6 | Bash: 4, Read: 2 | error: 1, ok: 5 | 6 | yes |
| s2-trigger-finaldesc | 3 | Bash: 2, Read: 1 | error: 1, ok: 2 | not passed to scoring | — |

The one errored Bash in each probe is a `cd` into a not-yet-created per-arm scratch directory, retried immediately with `mkdir -p` prepended; both error rows are visible in the committed manifests below.
The s17 probe's token total is harness-reported (49,538); the s2 probe's dispatch record reached the scoring session without a token figure, so none is recorded rather than one reconstructed.

Verbatim skill-choice statements:

**s17 finaldesc** (opening, before any tool call): "I'm using the hypothesis-driven-analysis skill, since this is exactly the adjudication example it names (\"someone says p95 exceeded 500ms yesterday\")."
Activation facts: `SKILL.md` read at ordinal 1 and `references/ledger-template.md` at ordinal 2, before any data touch; routed mini; outcome cell `CONTRADICTED`, inside the mini template's closed set — no vocabulary drift this run; verdict "the claim is false", p95 ≈392ms with bootstrap CI [374.9, 409.4]ms and the 20-of-24-hour coverage limitation stated.

**s2 finaldesc**: the final message omits the requested skill-choice sentence; the statement appears instead in the transcript's opening text block, before any tool call: "I am not using any of the listed skills — this is a direct, bounded descriptive computation (median of a column, filtered to June), not a diagnostic/comparative question with competing hypotheses, so hypothesis-driven-analysis's own scope note excludes it, and no other skill applies."
Recorded as a fidelity note (choice stated, but at the opening rather than in the final message as instructed); the run never read `SKILL.md` (manifest ordinal 1 is the fixture Read) and answered median **$76.36** across all 268 June rows.

## Committed manifests

Full `manifest` output for the six original trigger arms and the two final-description probes, generated in the close-out session with `uv run hypothesis-driven-analysis/tests/extract_evidence.py --normalize-root <REPO_ROOT> manifest <transcript>` — the issue-#66 corpus precedent of committing sanitized manifests so absence claims stay auditable after the scratch transcripts expire.
Columns: ordinal, timestamp, tool, paired-result status, target.
Secrets scan before committing: every row was read, and a pattern scan (api-key/token/password/bearer/private-key markers, validated against a planted positive in the same session) returned zero matches across all eight manifests — read-only analysis commands throughout; nothing needed redaction.

### s17-trigger-pre

```text
1	2026-07-18T21:09:57.622Z	Bash	ok	wc -l <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv && head -20 <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv
2	2026-07-18T21:10:07.864Z	Bash	ok	cd <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini\necho "--- date range ---"\ntail -n +2 checkout_latency.csv | cut -d, -f1 | cut -dT -f1 | sort -u\necho "--- row count per date ---"\ntail -n +2 checkout_latency.csv | cut -d, -f1 | cut -dT -f1 | sort | uniq -c\necho "--- last few lines ---"\ntail -5 checkout_latency.csv\necho "--- check for blank/malformed latency values ---"\nawk -F, 'NR>1 && ($3=="" || $3 !~ /^[0-9.]+$/) {print}' checkout_latency.csv\necho "--- duplicate request_ids ---"\ntail -n +2 checkout_latency.csv | cut -d, -f2 | sort | uniq -d | head\necho "--- duplicate timestamps ---"\ntail -n +2 checkout_latency.csv | cut -d, -f1 | sort | uniq -d | head\n
3	2026-07-18T21:10:19.842Z	Bash	ok	cd <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini\npython3 - <<'EOF'\nimport csv, statistics\n\nwith open("checkout_latency.csv") as f:\n    reader = csv.DictReader(f)\n    rows = list(reader)\n\nlat = [float(r["latency_ms"]) for r in rows]\nn = len(lat)\nlat_sorted = sorted(lat)\n\ndef pct_nearest_rank(data, p):\n    k = int((p/100) * len(data))  # 0-indexed nearest-rank variant\n    k = min(k, len(data)-1)\n    return data[k]\n\ndef pct_linear(data, p):\n    # numpy-style linear interpolation\n    idx = (p/100) * (len(data)-1)\n    lo = int(idx)\n    hi = min(lo+1, len(data)-1)\n    frac = idx - lo\n    return data[lo] + (data[hi]-data[lo])*frac\n\ndef pct_excel_style(data, p):\n    # "exclusive" nearest rank ceil method common in monitoring (e.g., ceil(p/100*N))\n    import math\n    k = math.ceil((p/100)*len(data))\n    k = min(k, len(data))\n    return data[k-1]\n\nprint("n =", n)\nprint("min, max:", min(lat), max(lat))\nprint("mean:", statistics.mean(lat))\nprint("median:", statistics.median(lat))\nprint()\nprint("p95 (linear interpolation, numpy default):", round(pct_linear(lat_sorted,95),2))\nprint("p95 (nearest-rank, 0-indexed floor):", round(pct_nearest_rank(lat_sorted,95),2))\nprint("p95 (ceil/exclusive method):", round(pct_excel_style(lat_sorted,95),2))\nprint("statistics.quantiles (inclusive, n=100)[94]:", round(statistics.quantiles(lat, n=100, method='inclusive')[93],2))\nprint("statistics.quantiles (exclusive, n=100)[94]:", round(statistics.quantiles(lat, n=100, method='exclusive')[93],2))\n\nprint()\nprint("count > 500ms:", sum(1 for x in lat if x > 500))\nprint("fraction > 500ms:", sum(1 for x in lat if x > 500)/n)\nprint("top 20 highest latencies:", sorted(lat, reverse=True)[:20])\n\n# also p99, p90 for context\nprint()\nprint("p90 (linear):", round(pct_linear(lat_sorted,90),2))\nprint("p99 (linear):", round(pct_linear(lat_sorted,99),2))\nEOF\n
```

### s17-trigger-post-a

```text
1	2026-07-19T02:35:23.752Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-19T02:35:31.290Z	Bash	ok	wc -l <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv; head -5 <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv
3	2026-07-19T02:35:44.062Z	Bash	ok	cd <SCRATCH>/s17-arms/post-a && python3 - <<'EOF'\nimport csv\npath = "<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv"\nrows = list(csv.DictReader(open(path)))\nprint("rows:", len(rows))\nts = [r["timestamp"] for r in rows]\nprint("first:", ts[0], "last:", ts[-1])\nprint("unique ts:", len(set(ts)))\ndates = set(t[:10] for t in ts)\nprint("dates:", dates)\nlat = [r["latency_ms"] for r in rows]\nprint("nulls in latency:", sum(1 for x in lat if x=="" or x is None))\nids = [r["request_id"] for r in rows]\nprint("unique request_ids:", len(set(ids)), "dup count:", len(ids)-len(set(ids)))\nvals = [float(x) for x in lat if x!=""]\nprint("min,max:", min(vals), max(vals))\nEOF
4	2026-07-19T02:35:55.316Z	Bash	ok	cd <SCRATCH>/s17-arms/post-a && python3 - <<'EOF'\nimport csv, statistics\npath = "<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv"\nrows = list(csv.DictReader(open(path)))\nvals = sorted(float(r["latency_ms"]) for r in rows)\nn = len(vals)\n\ndef pct_nearest_rank(p):\n    import math\n    rank = math.ceil(p/100 * n)\n    return vals[rank-1]\n\ndef pct_linear(p):\n    # numpy default linear interpolation\n    idx = (p/100) * (n-1)\n    lo = int(idx)\n    hi = min(lo+1, n-1)\n    frac = idx - lo\n    return vals[lo] + (vals[hi]-vals[lo])*frac\n\nprint("n:", n)\nprint("p95 nearest-rank:", pct_nearest_rank(95))\nprint("p95 linear-interp:", pct_linear(95))\nprint("max:", vals[-1], "top 10 values:", vals[-10:])\nprint("count > 500:", sum(1 for v in vals if v > 500))\nprint("count >= 500:", sum(1 for v in vals if v >= 500))\n# sign-test style interval: order statistics around rank 95th percentile for CI\nimport math\n# Using binomial-based CI for order statistic (95% CI on the 95th percentile) \nEOF
5	2026-07-19T02:36:13.060Z	Bash	ok	cd <SCRATCH>/s17-arms/post-a && python3 - <<'EOF'\nimport csv, random, statistics\npath = "<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv"\nrows = list(csv.DictReader(open(path)))\nvals = [float(r["latency_ms"]) for r in rows]\nn = len(vals)\nrandom.seed(42)\n\ndef p95(sample):\n    s = sorted(sample)\n    import math\n    rank = math.ceil(0.95 * len(s))\n    return s[rank-1]\n\nboots = []\nfor _ in range(5000):\n    sample = [vals[random.randrange(n)] for _ in range(n)]\n    boots.append(p95(sample))\nboots.sort()\nlo = boots[int(0.025*len(boots))]\nhi = boots[int(0.975*len(boots))]\nprint("point estimate p95:", p95(vals))\nprint("95% bootstrap CI for p95:", (lo, hi))\n\n# also check hourly breakdown to see if any hour's p95 exceeds 500 (in case "yesterday" sub-window matters)\nfrom collections import defaultdict\nby_hour = defaultdict(list)\nfor r in rows:\n    hour = r["timestamp"][11:13]\n    by_hour[hour].append(float(r["latency_ms"]))\nimport math\nfor h in sorted(by_hour):\n    s = sorted(by_hour[h])\n    rank = math.ceil(0.95*len(s))\n    print(h, "n=",len(s), "p95=", s[rank-1], "max=", s[-1])\nEOF
```

### s17-trigger-post-b

```text
1	2026-07-19T02:35:30.223Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-19T02:35:34.660Z	Bash	ok	wc -l <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv && head -5 <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv
3	2026-07-19T02:35:42.456Z	Bash	ok	cd <SCRATCH>/s17-arms/post-b && mkdir -p work && cd work\nCSV=<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv\necho "--- tail ---"\ntail -5 "$CSV"\necho "--- unique dates ---"\ntail -n +2 "$CSV" | cut -d'T' -f1 | sort -u\necho "--- row count (excl header) ---"\ntail -n +2 "$CSV" | wc -l\necho "--- duplicate request_ids ---"\ntail -n +2 "$CSV" | cut -d, -f2 | sort | uniq -d | wc -l\necho "--- null/empty latency check ---"\nawk -F, 'NR>1 && ($3=="" || $3=="NA") {c++} END{print c+0}' "$CSV"\n
4	2026-07-19T02:35:52.618Z	Bash	ok	cd <SCRATCH>/s17-arms/post-b/work\nCSV=<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv\npython3 - "$CSV" <<'EOF'\nimport csv, sys, statistics\npath = sys.argv[1]\nvals = []\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        vals.append(float(row['latency_ms']))\nvals.sort()\nn = len(vals)\nprint("n =", n)\nprint("min, max =", vals[0], vals[-1])\n\ndef pct_nearest_rank(v, p):\n    # nearest-rank method\n    k = max(1, int(round(p/100 * len(v))))\n    k = min(k, len(v))\n    return v[k-1]\n\ndef pct_linear(v, p):\n    # linear interpolation, numpy 'linear' default\n    if len(v) == 1:\n        return v[0]\n    idx = (p/100) * (len(v)-1)\n    lo = int(idx)\n    hi = min(lo+1, len(v)-1)\n    frac = idx - lo\n    return v[lo] + (v[hi]-v[lo])*frac\n\nprint("p95 nearest-rank:", pct_nearest_rank(vals, 95))\nprint("p95 linear-interp:", pct_linear(vals, 95))\nprint("p99 linear-interp:", pct_linear(vals, 99))\nprint("mean:", statistics.mean(vals))\nprint("median:", statistics.median(vals))\n# count over 500\nover500 = sum(1 for x in vals if x > 500)\nprint("count >500ms:", over500, "fraction:", over500/n)\n# top 20 values\nprint("top 20:", vals[-20:])\nEOF\n
5	2026-07-19T02:36:03.585Z	Bash	ok	cd <SCRATCH>/s17-arms/post-b/work\nCSV=<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv\npython3 - "$CSV" <<'EOF'\nimport csv, sys, random\npath = sys.argv[1]\nvals = []\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        vals.append(float(row['latency_ms']))\nn = len(vals)\nrandom.seed(42)\n\ndef pct_linear(v, p):\n    v = sorted(v)\n    idx = (p/100) * (len(v)-1)\n    lo = int(idx)\n    hi = min(lo+1, len(v)-1)\n    frac = idx - lo\n    return v[lo] + (v[hi]-v[lo])*frac\n\nB = 5000\nboot = []\nfor _ in range(B):\n    sample = [vals[random.randrange(n)] for _ in range(n)]\n    boot.append(pct_linear(sample, 95))\nboot.sort()\nlo_idx = int(0.025*B)\nhi_idx = int(0.975*B)\nprint("bootstrap p95 2.5%/97.5%:", boot[lo_idx], boot[hi_idx])\nprint("bootstrap p95 mean:", sum(boot)/B)\nEOF\n
6	2026-07-19T02:36:19.428Z	Bash	ok	cd <SCRATCH>/s17-arms/post-b/work\nCSV=<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv\npython3 - "$CSV" <<'EOF'\nimport csv, sys\npath = sys.argv[1]\nrows = []\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        hour = int(row['timestamp'][11:13])\n        rows.append((hour, float(row['latency_ms'])))\n\n# per-hour p95-ish (just max/mean to see trend)\nfrom collections import defaultdict\nbyhour = defaultdict(list)\nfor h, v in rows:\n    byhour[h].append(v)\n\nfor h in sorted(byhour):\n    vals = sorted(byhour[h])\n    n = len(vals)\n    mean = sum(vals)/n\n    mx = vals[-1]\n    print(f"hour {h:02d}: n={n} mean={mean:.1f} max={mx:.1f}")\nEOF\n
```

### s17-trigger-post-para

```text
1	2026-07-19T02:35:38.562Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-19T02:35:44.227Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
3	2026-07-19T02:35:47.936Z	Bash	ok	wc -l <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv; head -5 <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv
4	2026-07-19T02:35:57.902Z	Bash	ok	cd <SCRATCH>/s17-arms/post-para && python3 - <<'EOF'\nimport csv\nfrom datetime import datetime\n\npath = "<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv"\nrows = []\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        rows.append(row)\n\nprint("total rows:", len(rows))\nprint("first:", rows[0])\nprint("last:", rows[-1])\n\n# check timestamp range and gaps\nts = [datetime.fromisoformat(row['timestamp'].replace('Z','+00:00')) for row in rows]\nprint("min ts:", min(ts), "max ts:", max(ts))\n\n# check duplicates in request_id\nids = [row['request_id'] for row in rows]\nprint("unique request_ids:", len(set(ids)), "vs rows:", len(ids))\n\n# check for missing minutes (assuming 1-min grain)\ndiffs = set()\nfor i in range(1, len(ts)):\n    diffs.add((ts[i]-ts[i-1]).total_seconds())\nprint("distinct gaps (seconds):", diffs)\n\n# latency stats\nlat = [float(row['latency_ms']) for row in rows]\nlat_sorted = sorted(lat)\nn = len(lat_sorted)\nprint("min", min(lat), "max", max(lat))\nprint("mean", sum(lat)/n)\n\ndef pct(p):\n    idx = p/100*(n-1)\n    lo = int(idx)\n    hi = min(lo+1, n-1)\n    frac = idx - lo\n    return lat_sorted[lo] + (lat_sorted[hi]-lat_sorted[lo])*frac\n\nfor p in [50,90,95,99]:\n    print(f"p{p}:", pct(p))\n\n# count over 500\nover500 = [x for x in lat if x > 500]\nprint("count >500ms:", len(over500), "of", n, "=", len(over500)/n*100, "%")\nprint("over500 values:", sorted(over500)[:20])\n\n# any nulls / malformed\nbad = [row for row in rows if row['latency_ms'] in ('', None)]\nprint("bad latency rows:", len(bad))\nEOF
5	2026-07-19T02:36:10.791Z	Bash	ok	cd <SCRATCH>/s17-arms/post-para && python3 - <<'EOF'\nimport csv\nfrom datetime import datetime\nfrom collections import defaultdict\n\npath = "<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv"\nrows = []\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        rows.append(row)\n\nby_hour = defaultdict(list)\nfor row in rows:\n    ts = datetime.fromisoformat(row['timestamp'].replace('Z','+00:00'))\n    by_hour[ts.hour].append(float(row['latency_ms']))\n\ndef pct(sorted_list, p):\n    n = len(sorted_list)\n    idx = p/100*(n-1)\n    lo = int(idx)\n    hi = min(lo+1, n-1)\n    frac = idx - lo\n    return sorted_list[lo] + (sorted_list[hi]-sorted_list[lo])*frac\n\nfor h in sorted(by_hour):\n    vals = sorted(by_hour[h])\n    print(f"hour {h:02d}: n={len(vals)} p50={pct(vals,50):.1f} p95={pct(vals,95):.1f} max={max(vals):.1f} count>500={sum(1 for v in vals if v>500)}")\nEOF
```

### s2-trigger-postdesc

```text
1	2026-07-19T02:35:45.282Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s1-conversion/orders.csv
2	2026-07-19T02:35:50.696Z	Bash	ok	cd <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s1-conversion && python3 -c "\nimport csv, statistics\nvals = []\nmonths = set()\nwith open('orders.csv') as f:\n    r = csv.DictReader(f)\n    for row in r:\n        ts = row['timestamp']\n        months.add(ts[:7])\n        if ts.startswith('2026-06'):\n            vals.append(float(row['amount']))\nprint('distinct year-months in file:', months)\nprint('n june orders:', len(vals))\nprint('median:', statistics.median(vals))\n"\n
```

### s3-trigger-postdesc

```text
1	2026-07-19T02:35:54.684Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s3-bug/test_dateutils.py
2	2026-07-19T02:36:24.771Z	Bash	ok	cd <SCRATCH>/s3-arm && python3 -c "\nfrom datetime import datetime\ns = '2026-07-14T03:12:09Z'\ntry:\n    d = datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')\n    print('parsed ok:', d)\nexcept ValueError as e:\n    print('ERROR (no %z):', e)\n"\n
3	2026-07-19T02:36:31.877Z	Bash	ok	cd <SCRATCH>/s3-arm && python3 -c "\nimport sys\nfrom datetime import datetime\nprint('python version:', sys.version)\ns = '2026-07-14T03:12:09Z'\n\n# candidate fix 1: add %z to strptime format (Python 3.7+ accepts literal 'Z' for %z)\nd1 = datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')\nprint('fix1 strptime %z ->', d1, 'year=', d1.year)\n\n# candidate fix 2: fromisoformat with Z replaced (portable across versions)\nd2 = datetime.fromisoformat(s.replace('Z', '+00:00'))\nprint('fix2 fromisoformat replace ->', d2, 'year=', d2.year)\n\n# candidate fix 3 (3.11+): fromisoformat directly handles trailing Z\ntry:\n    d3 = datetime.fromisoformat(s)\n    print('fix3 fromisoformat direct ->', d3, 'year=', d3.year)\nexcept ValueError as e:\n    print('fix3 fromisoformat direct FAILS on this python version:', e)\n"\n
```

### s17-trigger-finaldesc

```text
1	2026-07-19T03:24:33.583Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-19T03:24:38.681Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/ledger-template.md
3	2026-07-19T03:24:42.300Z	Bash	ok	wc -l <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv && head -5 <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv
4	2026-07-19T03:24:48.417Z	Bash	error	cd <SCRATCH>/s17-arms/post-final && python3 -c "\nimport csv\nrows = []\nwith open('<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv') as f:\n    r = csv.DictReader(f)\n    for row in r:\n        rows.append(row)\n\nprint('n rows:', len(rows))\nprint('first ts:', rows[0]['timestamp'], 'last ts:', rows[-1]['timestamp'])\n\ndates = sorted(set(row['timestamp'][:10] for row in rows))\nprint('dates present:', dates)\n\n# check for duplicate/missing minutes\nts = [row['timestamp'] for row in rows]\nprint('unique timestamps:', len(set(ts)) == len(ts))\n\nlat = [float(row['latency_ms']) for row in rows]\nprint('min latency:', min(lat), 'max latency:', max(lat))\nprint('any missing/empty latency:', sum(1 for row in rows if row['latency_ms']=='') )\n"\n
5	2026-07-19T03:24:54.499Z	Bash	ok	mkdir -p <SCRATCH>/s17-arms/post-final && cd <SCRATCH>/s17-arms/post-final && python3 -c "\nimport csv\nrows = []\nwith open('<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv') as f:\n    r = csv.DictReader(f)\n    for row in r:\n        rows.append(row)\n\nprint('n rows:', len(rows))\nprint('first ts:', rows[0]['timestamp'], 'last ts:', rows[-1]['timestamp'])\n\ndates = sorted(set(row['timestamp'][:10] for row in rows))\nprint('dates present:', dates)\n\nts = [row['timestamp'] for row in rows]\nprint('unique timestamps:', len(set(ts)) == len(ts))\n\nlat = [float(row['latency_ms']) for row in rows]\nprint('min latency:', min(lat), 'max latency:', max(lat))\nprint('any missing/empty latency:', sum(1 for row in rows if row['latency_ms']=='') )\n"\n
6	2026-07-19T03:25:09.158Z	Bash	ok	cd <SCRATCH>/s17-arms/post-final && python3 -c "\nimport csv, statistics, random\n\nrows = []\nwith open('<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s11-mini/checkout_latency.csv') as f:\n    r = csv.DictReader(f)\n    for row in r:\n        rows.append(float(row['latency_ms']))\n\nn = len(rows)\nsrt = sorted(rows)\n\ndef pct_nearest_rank(data, p):\n    k = int(round(p/100 * len(data) + 0.5))\n    k = max(1, min(len(data), k))\n    return data[k-1]\n\ndef pct_linear(data, p):\n    # numpy default linear interpolation\n    idx = (p/100) * (len(data)-1)\n    lo = int(idx)\n    hi = min(lo+1, len(data)-1)\n    frac = idx - lo\n    return data[lo] + (data[hi]-data[lo])*frac\n\np95_nr = pct_nearest_rank(srt, 95)\np95_lin = pct_linear(srt, 95)\nprint('n:', n)\nprint('p95 nearest-rank:', p95_nr)\nprint('p95 linear-interp:', p95_lin)\nprint('count > 500:', sum(1 for x in rows if x > 500), 'fraction:', sum(1 for x in rows if x>500)/n)\nprint('count >= 500:', sum(1 for x in rows if x >= 500))\nprint('top 20 values:', srt[-20:])\n\n# bootstrap CI for p95\nrandom.seed(42)\nboots = []\nfor _ in range(5000):\n    sample = [random.choice(rows) for _ in range(n)]\n    sample.sort()\n    boots.append(pct_linear(sample, 95))\nboots.sort()\nlo_ci = boots[int(0.025*len(boots))]\nhi_ci = boots[int(0.975*len(boots))]\nprint('bootstrap 95% CI for p95:', lo_ci, hi_ci)\n"\n
```

### s2-trigger-finaldesc

```text
1	2026-07-19T03:24:43.878Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s1-conversion/orders.csv
2	2026-07-19T03:24:51.593Z	Bash	error	cd <SCRATCH>/s2-arm-final && python3 -c "\nimport csv, statistics\nfrom datetime import datetime\n\npath = '<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s1-conversion/orders.csv'\namounts = []\nmonths = set()\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        ts = row['timestamp']\n        dt = datetime.fromisoformat(ts.replace('Z','+00:00'))\n        months.add((dt.year, dt.month))\n        if dt.year == 2026 and dt.month == 6:\n            amounts.append(float(row['amount']))\n\nprint('distinct year-months in file:', months)\nprint('count in june:', len(amounts))\namounts.sort()\nprint('median:', statistics.median(amounts))\nprint('min/max:', min(amounts), max(amounts))\n"\n
3	2026-07-19T03:24:58.117Z	Bash	ok	mkdir -p <SCRATCH>/s2-arm-final && cd <SCRATCH>/s2-arm-final && python3 -c "\nimport csv, statistics\nfrom datetime import datetime\n\npath = '<REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s1-conversion/orders.csv'\namounts = []\nmonths = set()\nwith open(path) as f:\n    r = csv.DictReader(f)\n    for row in r:\n        ts = row['timestamp']\n        dt = datetime.fromisoformat(ts.replace('Z','+00:00'))\n        months.add((dt.year, dt.month))\n        if dt.year == 2026 and dt.month == 6:\n            amounts.append(float(row['amount']))\n\nprint('distinct year-months in file:', months)\nprint('count in june:', len(amounts))\namounts.sort()\nprint('median:', statistics.median(amounts))\nprint('min/max:', min(amounts), max(amounts))\n"\n
```
