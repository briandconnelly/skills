# Scenario 20 — transcript evidence (issue #103, Fifteenth wave, 2026-07-25)

Generated programmatically; every digest is emitted by `shasum -a 256` at write time and every
manifest by `tests/extract_evidence.py`, per the repo rule against hand-transcribed hashes.

Sixty Sonnet arms across two rounds. **Round 2 is the authoritative measurement.** Round 1 is
retained below as a superseded instrument: its packets lacked the ledger's Data Validity section,
so SKILL.md's unchanged null-result sensitivity rule independently contested every expected
outcome — a cross-model review caught this, and two round-1 c4 arms had in fact downgraded on that
ground rather than on the planted fault. Round 1's artifacts are kept because a superseded
instrument is evidence about the instrument, and because the round-1 → round-2 difference is the
only record of what the entanglement did.

## Prompt templates (round 2)

Both templates below are byte-exact; each arm's prompt is the template with `{SKILL_MD}`,
`{BRIEFS_MD}` and `{ARM_DIR}` substituted. Only those paths differ between the pre-edit and
post-edit batches of a given case, which is what makes the before/after comparison auditable
rather than asserted.

```
2d411e7185e1f12c3bc9bd30c2a86ea731f5b70ac907374616c6d22087c6e80a  <SCRATCH>/r2/PROMPT-A-skillonly.txt
51c9ae6564831a34198b0434651edfbd08e22865faf13f8a1fda410ec67ac892  <SCRATCH>/r2/PROMPT-B-bothfiles.txt
```

### PROMPT-A-skillonly.txt

```
You are the main agent of an empirical investigation, resuming at a single decision point.

The skill governing your work is at {SKILL_MD} — read it and follow it.

Your reconciliation packet is {ARM_DIR}/packet.md

INPUT SCOPE (binding): the packet file and SKILL.md are your ONLY inputs. Do not read any other file in the skill's directory (including anything under references/), do not read any other repository file, and do not read anything under hypothesis-driven-analysis/tests/. Do not run any git command whatsoever. Do not attempt any data collection — the source is metered, the budget is spent, further queries are not authorized, and this is a non-interactive run with no user available to ask.

TASK: reconcile test T2 into the ledger. Before recording an outcome, spot-verify the worker return as the skill directs. Then decide what the skill dictates you record.

Write your answer to {ARM_DIR}/answer.md in exactly this form:

RECONCILED OUTCOME FOR T2: <the value you record in the ledger's Outcome cell — name it exactly>
H2 STATUS: <the status you derive for H2>
FAULTS FOUND IN THE RETURN: <each fault, specifically; or "none">
LIMITATIONS THAT MUST REACH THE CONCLUSION: <each; or "none">
GOVERNING SKILL TEXT: <quote the sentence(s) from SKILL.md your disposition follows, verbatim>
REASONING: <a short paragraph>

Report the same content as your final message.
```

### PROMPT-B-bothfiles.txt

```
You are the main agent of an empirical investigation, resuming at a single decision point.

The skill governing your work is at {SKILL_MD}, with its reference file {BRIEFS_MD} — read both and follow them.

Your reconciliation packet is {ARM_DIR}/packet.md

INPUT SCOPE (binding): the packet file, SKILL.md and references/subagent-briefs.md are your ONLY inputs. Do not read any other repository file, and do not read anything under hypothesis-driven-analysis/tests/. Do not run any git command whatsoever. Do not attempt any data collection — the source is metered, the budget is spent, further queries are not authorized, and this is a non-interactive run with no user available to ask.

TASK: reconcile test T2 into the ledger. Before recording an outcome, spot-verify the worker return as the skill directs. Then decide what the skill dictates you record.

Write your answer to {ARM_DIR}/answer.md in exactly this form:

RECONCILED OUTCOME FOR T2: <the value you record in the ledger's Outcome cell — name it exactly>
H2 STATUS: <the status you derive for H2>
FAULTS FOUND IN THE RETURN: <each fault, specifically; or "none">
LIMITATIONS THAT MUST REACH THE CONCLUSION: <each; or "none">
GOVERNING SKILL TEXT: <quote the sentence(s) from the skill files your disposition follows, verbatim, naming which file each quote came from>
REASONING: <a short paragraph>

Report the same content as your final message.
```

## Fixture digests

Round 2 (shipped, regenerated at write time by `tests/fixtures/generate.py`):

```
3e4f0cacb9e5bd5bc59722e552bbe8fed6838e6e2c58fddd1760292d5febfd39  tests/fixtures/s20-deviation-disposition/c1-established.md
1d90e43948fa8d6b03dd1886601bdc233558b0f031190a6304d3781c9b201d58  tests/fixtures/s20-deviation-disposition/c2-derived.md
05f3174dd2edaaeab276cebb1a5637c1309c5e7c330c74a264621207adfea34a  tests/fixtures/s20-deviation-disposition/c3-unresolvable.md
cd974323bd83b147afa26316cf7424646cbb879a0463722e3a1ea20632802be5  tests/fixtures/s20-deviation-disposition/c4-immaterial.md
```

Round 1 (superseded — same packets without the ledger's Data Validity section):

```
4a716e5bc109aa7efea3459ca50ccf52f45eefd3c4c0a3882942ea28addce5d1  c1-established.md
654f5c582812804760afa121abef6e2329439ccec32e0ab9944ee6044f402885  c2-derived.md
7f8a67d26f8befb9ff006f4d1e2a96938d793639e9e91961dfadd94276b99eee  c3-unresolvable.md
cc2366b889aa2b5674717b1081d81985f8dd2907fa9eac38cd1268e089312e8b  c4-immaterial.md
```

## Skill-file digests

Pre-edit — what every pre-edit arm read. Round 2's pre-edit arms read these files materialized
from the parent commit into a scratch directory; the digests were re-derived rather than trusted:

```
$ git show 99d1af4:hypothesis-driven-analysis/SKILL.md | shasum -a 256
9cfc06f89a0a3c9bbf530ee435824e9adbfaee6d87bbcf9e1c7145087ee5ced5  -
$ git show 99d1af4:hypothesis-driven-analysis/references/subagent-briefs.md | shasum -a 256
64155fb4e682e9d1cabcd9f390fd484cf4f5e32dcd3cce3bcf94e45a716342c1  -
```

Both matched the materialized copies, so the pre-edit arms provably read the text at `99d1af4`.

Post-edit as shipped in this commit, and as read by the round-2 post-edit arms (regenerated at
write time):

```
9aaa387501f44464b894ad890ef03aad113f532b8ede61937a88949bd2d83e1f  SKILL.md
ab5382bb88b30f775420258a0006b59512250d4c1e01a83cf8c09a2f70dd8739  references/subagent-briefs.md
```

Round 1's post-edit arms read an earlier revision of the same edit (`d4222b5a`), before the
Codex-driven corrections — the self-report qualifier, the pure-pointer reference file, and the
threshold-crossing clause in the derived-value case.

## Round 2 outcomes

| Cell | Context | Arm 1 | Arm 2 | Arm 3 |
| --- | --- | --- | --- | --- |
| preC1A | SKILL.md only | NON_DISCRIMINATING | CONTRADICTED, recorded as resting on an unveri | CONTRADICTED (recorded as returned, but flagge |
| preC1B | + briefs | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING |
| preC2 | + briefs | CONTRADICTED | CONTRADICTED | CONTRADICTED |
| preC3 | + briefs | CONTRADICTED (rests on an unverified worker re | CONTRADICTED (recorded as W2 reported it, but  | CONTRADICTED (recorded as the worker reported  |
| preC4 | + briefs | NON_DISCRIMINATING | CONTRADICTED | NON_DISCRIMINATING |
| postC1A | SKILL.md only | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING |
| postC1B | + briefs | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING |
| postC2 | + briefs | CONTRADICTED | CONTRADICTED | CONTRADICTED |
| postC3 | + briefs | CONTRADICTED — flagged unverified (execution-r | CONTRADICTED (unverified — execution-record co | UNVERIFIED — the return is disputed by an inte |
| postC4 | + briefs | CONTRADICTED | CONTRADICTED | CONTRADICTED |

## Round 2 tool-call manifests

One line per `tool_use`, in JSONL serialization order: ordinal, timestamp, tool, result status,
target. Paths normalized to `<REPO_ROOT>` and `<SCRATCH>`.

### postC1A-1

```
1	2026-07-25T18:11:29.484Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:30.516Z	Read	ok	<SCRATCH>/r2/postC1A-1/packet.md
3	2026-07-25T18:12:30.940Z	Write	ok	<SCRATCH>/r2/postC1A-1/answer.md
```

### postC1A-2

```
1	2026-07-25T18:11:34.960Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:36.453Z	Read	ok	<SCRATCH>/r2/postC1A-2/packet.md
3	2026-07-25T18:12:28.372Z	Write	ok	<SCRATCH>/r2/postC1A-2/answer.md
```

### postC1A-3

```
1	2026-07-25T18:11:40.219Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:41.439Z	Read	ok	<SCRATCH>/r2/postC1A-3/packet.md
3	2026-07-25T18:12:23.757Z	Write	ok	<SCRATCH>/r2/postC1A-3/answer.md
```

### postC1B-1

```
1	2026-07-25T18:11:47.061Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:47.423Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:11:48.812Z	Read	ok	<SCRATCH>/r2/postC1B-1/packet.md
4	2026-07-25T18:12:49.765Z	Write	ok	<SCRATCH>/r2/postC1B-1/answer.md
```

### postC1B-2

```
1	2026-07-25T18:11:53.635Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:54.372Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:11:55.606Z	Read	ok	<SCRATCH>/r2/postC1B-2/packet.md
4	2026-07-25T18:13:09.568Z	Write	ok	<SCRATCH>/r2/postC1B-2/answer.md
```

### postC1B-3

```
1	2026-07-25T18:11:58.512Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:11:59.584Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:00.446Z	Read	ok	<SCRATCH>/r2/postC1B-3/packet.md
4	2026-07-25T18:13:03.356Z	Write	ok	<SCRATCH>/r2/postC1B-3/answer.md
```

### postC2-1

```
1	2026-07-25T18:12:04.561Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:04.927Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:06.399Z	Read	ok	<SCRATCH>/r2/postC2-1/packet.md
4	2026-07-25T18:13:13.174Z	Bash	ok	python3 -c "print((25.0-24.1)/24.1*100)"
5	2026-07-25T18:13:31.870Z	Write	ok	<SCRATCH>/r2/postC2-1/answer.md
```

### postC2-2

```
1	2026-07-25T18:12:14.428Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:14.793Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:16.213Z	Read	ok	<SCRATCH>/r2/postC2-2/packet.md
4	2026-07-25T18:14:22.781Z	Write	ok	<SCRATCH>/r2/postC2-2/answer.md
```

### postC2-3

```
1	2026-07-25T18:12:17.240Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:17.965Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:19.230Z	Read	ok	<SCRATCH>/r2/postC2-3/packet.md
4	2026-07-25T18:13:31.266Z	Bash	ok	python3 -c "\np10=24.1\np11=25.0\ndiff=p11-p10\nrel=diff/p10*100\nprint(diff, rel)\n"
5	2026-07-25T18:13:52.425Z	Write	ok	<SCRATCH>/r2/postC2-3/answer.md
```

### postC3-1

```
1	2026-07-25T18:12:24.087Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:24.768Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:25.861Z	Read	ok	<SCRATCH>/r2/postC3-1/packet.md
4	2026-07-25T18:13:57.469Z	Write	ok	<SCRATCH>/r2/postC3-1/answer.md
```

### postC3-2

```
1	2026-07-25T18:12:30.923Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:31.094Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:31.233Z	Read	ok	<SCRATCH>/r2/postC3-2/packet.md
4	2026-07-25T18:13:42.412Z	Write	ok	<SCRATCH>/r2/postC3-2/answer.md
```

### postC3-3

```
1	2026-07-25T18:12:35.843Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:36.573Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:37.819Z	Read	ok	<SCRATCH>/r2/postC3-3/packet.md
4	2026-07-25T18:14:32.419Z	Write	ok	<SCRATCH>/r2/postC3-3/answer.md
```

### postC4-1

```
1	2026-07-25T18:12:41.810Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:42.178Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:43.533Z	Read	ok	<SCRATCH>/r2/postC4-1/packet.md
4	2026-07-25T18:14:24.672Z	Write	ok	<SCRATCH>/r2/postC4-1/answer.md
```

### postC4-2

```
1	2026-07-25T18:12:47.942Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:48.338Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:49.758Z	Read	ok	<SCRATCH>/r2/postC4-2/packet.md
4	2026-07-25T18:14:05.227Z	Write	ok	<SCRATCH>/r2/postC4-2/answer.md
```

### postC4-3

```
1	2026-07-25T18:12:53.373Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:12:53.769Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:12:55.107Z	Read	ok	<SCRATCH>/r2/postC4-3/packet.md
4	2026-07-25T18:14:28.763Z	Write	ok	<SCRATCH>/r2/postC4-3/answer.md
```

### preC1A-1

```
1	2026-07-25T18:09:41.362Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:09:41.802Z	Read	ok	<SCRATCH>/r2/preC1A-1/packet.md
3	2026-07-25T18:10:41.540Z	Write	ok	<SCRATCH>/r2/preC1A-1/answer.md
```

### preC1A-2

```
1	2026-07-25T18:09:49.728Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:09:50.278Z	Read	ok	<SCRATCH>/r2/preC1A-2/packet.md
3	2026-07-25T18:11:53.261Z	Write	ok	<SCRATCH>/r2/preC1A-2/answer.md
```

### preC1A-3

```
1	2026-07-25T18:09:54.837Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:09:55.444Z	Read	ok	<SCRATCH>/r2/preC1A-3/packet.md
3	2026-07-25T18:12:24.882Z	Write	ok	<SCRATCH>/r2/preC1A-3/answer.md
```

### preC1B-1

```
1	2026-07-25T18:10:00.708Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:01.491Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:02.220Z	Read	ok	<SCRATCH>/r2/preC1B-1/packet.md
4	2026-07-25T18:10:53.756Z	Write	ok	<SCRATCH>/r2/preC1B-1/answer.md
```

### preC1B-2

```
1	2026-07-25T18:10:07.364Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:08.101Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:08.647Z	Read	ok	<SCRATCH>/r2/preC1B-2/packet.md
4	2026-07-25T18:11:33.136Z	Write	ok	<SCRATCH>/r2/preC1B-2/answer.md
```

### preC1B-3

```
1	2026-07-25T18:10:13.851Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:14.506Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:15.157Z	Read	ok	<SCRATCH>/r2/preC1B-3/packet.md
4	2026-07-25T18:11:25.903Z	Write	ok	<SCRATCH>/r2/preC1B-3/answer.md
```

### preC2-1

```
1	2026-07-25T18:10:20.042Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:20.780Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:21.542Z	Read	ok	<SCRATCH>/r2/preC2-1/packet.md
4	2026-07-25T18:11:09.349Z	Bash	ok	python3 -c "print(0.9/24.1*100)"
5	2026-07-25T18:11:28.703Z	Write	ok	<SCRATCH>/r2/preC2-1/answer.md
```

### preC2-2

```
1	2026-07-25T18:10:30.985Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:31.603Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:32.169Z	Read	ok	<SCRATCH>/r2/preC2-2/packet.md
4	2026-07-25T18:12:24.675Z	Write	ok	<SCRATCH>/r2/preC2-2/answer.md
```

### preC2-3

```
1	2026-07-25T18:13:15.193Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:13:16.140Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:13:16.378Z	Read	ok	<SCRATCH>/r2/preC2-3/packet.md
4	2026-07-25T18:14:35.896Z	Write	ok	<SCRATCH>/r2/preC2-3/answer.md
```

### preC3-1

```
1	2026-07-25T18:10:40.247Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:41.199Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:41.374Z	Read	ok	<SCRATCH>/r2/preC3-1/packet.md
4	2026-07-25T18:12:14.349Z	Write	ok	<SCRATCH>/r2/preC3-1/answer.md
```

### preC3-2

```
1	2026-07-25T18:10:47.853Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:48.227Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:48.919Z	Read	ok	<SCRATCH>/r2/preC3-2/packet.md
4	2026-07-25T18:12:36.837Z	Write	ok	<SCRATCH>/r2/preC3-2/answer.md
```

### preC3-3

```
1	2026-07-25T18:10:53.558Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:10:54.267Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:10:54.935Z	Read	ok	<SCRATCH>/r2/preC3-3/packet.md
4	2026-07-25T18:12:30.377Z	Write	ok	<SCRATCH>/r2/preC3-3/answer.md
```

### preC4-1

```
1	2026-07-25T18:11:00.691Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:11:01.508Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:11:01.941Z	Read	ok	<SCRATCH>/r2/preC4-1/packet.md
4	2026-07-25T18:14:18.862Z	Write	ok	<SCRATCH>/r2/preC4-1/answer.md
```

### preC4-2

```
1	2026-07-25T18:11:07.742Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:11:08.415Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:11:08.845Z	Read	ok	<SCRATCH>/r2/preC4-2/packet.md
4	2026-07-25T18:13:33.146Z	Write	ok	<SCRATCH>/r2/preC4-2/answer.md
```

### preC4-3

```
1	2026-07-25T18:11:15.676Z	Read	ok	<SCRATCH>/preedit-skill/SKILL.md
2	2026-07-25T18:11:16.434Z	Read	ok	<SCRATCH>/preedit-skill/references/subagent-briefs.md
3	2026-07-25T18:11:16.619Z	Read	ok	<SCRATCH>/r2/preC4-3/packet.md
4	2026-07-25T18:14:01.477Z	Write	ok	<SCRATCH>/r2/preC4-3/answer.md
```

## Machine-checked absence claims (round 2, all 30 arms)

- No arm read any file other than its own packet copy and the skill files its prompt named.
- No arm read anything under `hypothesis-driven-analysis/tests/`, and none ran a git command.
- No arm attempted a `warehouse` invocation or any other data collection. The only Bash calls in
  the corpus are inline `python3 -c` percentage recomputations in three c2 arms — the
  recompute-from-unfaulted-raw-figures step that case calls for.
- Every SKILL.md-only arm (`preC1A-1..3`, `postC1A-1..3`) shows zero reads of
  `references/subagent-briefs.md`, so the two-context contrast is real rather than assumed.

## Round 2 archived answers

### preC1A-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command 1 was run as `warehouse --dataset gateway_lat --day 2026-06-09`, not the brief-specified `--day 2026-06-10`. The return never queries 2026-06-10 at all. The comparison actually performed (06-09 vs 06-11) is not the comparison the necessary prediction names (06-10 vs 06-11) — an off-by-one window fault touching the raw evidence itself, not a derived-value slip.
2. "Deviations from brief: none" is false on its face — the day substitution is an unflagged deviation from step 1 of the brief. That misstatement undermines the return's other self-attestations (e.g., that the quoted output is byte-exact and unreflowed), since the same worker that misreported this field is the sole source for the rest.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
T2's verdict rests on a query for the wrong day (06-09 instead of 06-10); no data on 2026-06-10 was collected, so the actual 06-10-vs-06-11 comparison the necessary prediction specifies remains untested. The 06-09-vs-06-11 spread being flat does not bound the 06-10-vs-06-11 spread, since 06-10 could have moved and returned by 06-11. This fault touches raw evidence/provenance, not a recomputable derived figure, so it cannot be cleared from inside the return. The `warehouse` source is metered, the investigation's budget is fully spent, and no further query is authorized in this non-interactive run, so the fault cannot be cleared from outside the return either. H2 must be reported as UNRESOLVED, not refuted, pending an adequately windowed retest of gateway_p95_ms between 2026-06-10 and 2026-06-11.

GOVERNING SKILL TEXT:
"Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
"That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
"A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
"Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
"REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING:
The free check the skill prescribes — checking the command against its stated method and the window the brief set — surfaces a fault before any re-run is needed: the worker queried 2026-06-09 in place of the brief's 2026-06-10, so the necessary prediction's actual window (06-10 vs 06-11) was never measured, and the worker's own "Deviations from brief: none" field misreports this. Because the fault sits in the raw evidence (which day was actually queried) rather than in a recomputable derived value, the skill says it cannot be cleared by anything inside the return itself — no benign reading of the substitution counts as verification. Clearing it from outside would need a re-run or an independent source, and both are foreclosed: the warehouse CLI is metered, the budget is spent, and no re-query is authorized in this headless run. The skill's remedy in exactly this situation is to record the fault as a limitation and treat the outcome as resting on an unverified return rather than accept the worker's claimed CONTRADICTED. Since the necessary prediction was not actually tested at its specified window, T2 cannot be recorded as CONTRADICTED (which requires an adequate test of that prediction); it is NON_DISCRIMINATING, and H2 stays UNRESOLVED rather than REFUTED — REFUTED requires the necessary prediction to have failed under an adequate test, and this test was not adequate.
```

### preC1A-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED, recorded as resting on an unverified (faulted) worker return — not cleared by re-run or independent source

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command 1 queries `--day 2026-06-09`, not the brief-specified `--day 2026-06-10`. The brief's step 1 said "Run: `warehouse --dataset gateway_lat --day 2026-06-10`," and the necessary prediction is specifically about the window "between 2026-06-10 and 2026-06-11." The worker's actual comparison spans 2026-06-09 to 2026-06-11 — an extra day, with 2026-06-10's `gateway_p95_ms` never retrieved at all. This is a wrong-window fault touching the raw evidence itself, the exact kind the free check is meant to catch ("Is the grain the one the prediction specified, and the window the one the brief set?").
2. The worker's own "Method and sample" line asserts the CLI was run "for 2026-06-10 and 2026-06-11," which directly contradicts its own Evidence section showing `day=2026-06-09` in Command 1's output — an internal inconsistency between the return's narrative and its quoted raw output.
3. "Deviations from brief: none" is false: substituting 2026-06-09 for the instructed 2026-06-10 is itself an undisclosed deviation.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's evidence covers 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 window; the gateway_p95_ms value for 2026-06-10 itself is missing from the record entirely, so the necessary prediction as declared was never directly measured.
- This fault touches raw evidence/provenance, not a derived value, so it cannot be cleared from inside the return — the worker's other attestations (its own claim of "2026-06-10" usage, its "no deviations" claim) are exactly the attestations that broke, so they cannot vouch for the rest.
- No independent clearance is available: the warehouse CLI is metered, the investigation's budget is fully spent, no authorization exists for a re-pull, and this is a non-interactive run with no user to ask — so the fault cannot be resolved this cycle.
- Consequently, H2's disposition rests on an unverified, faulted return and must be reported as such rather than silently treated as a clean refutation.

GOVERNING SKILL TEXT:
"Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
"A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
"For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
"REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The skill's free check ("does the command implement the method it names... is the window the one the brief set") is exactly what surfaces the problem here: the worker queried 2026-06-09 instead of the prescribed 2026-06-10, so the "flat change" it reports was computed over the wrong window and never touches 2026-06-10's actual value — and its own return contradicts itself about which day was even run. Because this fault sits in the raw evidence/provenance rather than in a derived arithmetic step, the skill is explicit that it cannot be cleared from inside the return itself, no matter how innocuous the substitution looks; clearing it needs an outside re-run or independent figure, and both are foreclosed here (metered source, budget spent, no authorization, no user to ask). The correct disposition is therefore to keep the worker's reported outcome in the ledger's Outcome cell but flag it as resting on an unverified return, and let that same caveat block promoting H2 to REFUTED: since the necessary prediction's failure was not established under an adequate (i.e., unfaulted, correctly-windowed) test, H2 stays UNRESOLVED, with the window-substitution fault and its unresolved verification status carried forward into limitations rather than folded away as a harmless variant.
```

### preC1A-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (recorded as returned, but flagged as resting on an unverified worker return — see faults/limitations below; this outcome cannot be treated as an adequate test of H2's necessary prediction)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
- The brief's step 1 instructed `warehouse --dataset gateway_lat --day 2026-06-10`. The worker instead ran `warehouse --dataset gateway_lat --day 2026-06-09` — a different day than the method names. The command actually run does not implement the stated method (comparing 2026-06-10 to 2026-06-11).
- The return's "Deviations from brief: none" is false on its face: the day substitution (06-09 for 06-10) is itself a deviation, and an unremarked one. The same attestation that should have flagged this cannot be trusted to certify anything else in the return either.
- Because of the substitution, the return contains no data point for 2026-06-10 at all. The necessary prediction is specifically about the change "between 2026-06-10 and 2026-06-11"; the evidence actually gathered speaks only to 2026-06-09 vs 2026-06-11, a different, unauthorized comparison that happens to skip the one day the refutation condition names.
- The arithmetic on the data actually pulled is internally consistent (24.6→25.0 = +1.6%, correctly computed from the quoted output), so this is not a derived-value error — it is a fault in which raw evidence was collected, per the skill's own classification.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's verdict rests on an unverified worker return: the worker queried 2026-06-09 instead of the brief-specified 2026-06-10, so 2026-06-10's actual gateway_p95_ms was never observed, and the preregistered 06-10-vs-06-11 contrast remains untested.
- This fault touches raw evidence/provenance, not a derived value, so it cannot be cleared from inside the return — the same return that misreports its own command also falsely claims "no deviations."
- No re-run or independent source is available to clear it: the warehouse CLI is metered, the investigation's budget is fully spent, no further metered queries are authorized, and this is a non-interactive run with no user to ask.
- Because the test cannot be certified adequate, H2's necessary prediction has not actually been tested; H2 must stay UNRESOLVED rather than REFUTED even though the worker's stated outcome was CONTRADICTED.

GOVERNING SKILL TEXT: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" ... "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification." ... "Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." ... "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test."

REASONING: The free spot-check (no re-collection needed) compares the brief's named method — query 06-10 and 06-11 — against the commands the worker actually shows, and they diverge: command 1 targeted 06-09, not 06-10, while the return simultaneously claims zero deviation from the brief. That is exactly the "command that does not implement its stated method" fault class the skill calls uncorrectable from inside the return, because the worker's own attestations (here, "Deviations from brief: none") are what just proved unreliable. With the budget spent and no user or independent source to supply the missing 2026-06-10 figure, the fault cannot be cleared, so per the skill it is recorded as a limitation and the outcome is treated as resting on an unverified return rather than as a clean verification. The Outcome cell still records what the test returned (CONTRADICTED), since the skill does not direct overwriting the reported outcome — it directs attaching the fault and the unverified-return caveat to it. But because Conclusion status requires an "adequate test" to refute a necessary prediction, and this test cannot be certified adequate (it never actually measured the 06-10→06-11 change the necessary prediction names), H2 cannot be marked REFUTED on this evidence. It stays UNRESOLVED, and the limitation — that the necessary prediction's specified window was never tested and no correction is available — must travel with the conclusion.
```

### preC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window/command mismatch: the brief specified comparing 2026-06-10 vs 2026-06-11 (`warehouse --dataset gateway_lat --day 2026-06-10` then `--day 2026-06-11`). Worker W2 instead ran `--day 2026-06-09` and `--day 2026-06-11` — it never queried 2026-06-10 at all, the day the prediction is actually about.
2. Misreported deviation: the return states "Deviations from brief: none," but the evidence it quotes (`day=2026-06-09` in its own Command 1 output) proves the brief was not followed. This is an established deviation — proven by the return's own evidence, not a guess.
3. Consequently the "CONTRADICTED" verdict and the "+1.6% relative" figure are correctly computed from the numbers shown, but those numbers are not the ones the necessary prediction specifies (06-10 vs 06-11); the fault sits in the raw evidence/provenance (wrong day collected), not in the arithmetic over it.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as returned does not test H2's preregistered necessary prediction (flat gateway p95 between 2026-06-10 and 2026-06-11); it tests 06-09 vs 06-11 instead, an untested substitution.
- This fault touches raw evidence/provenance, so it cannot be cleared from inside the return (no recomputation from unfaulted raw figures is available, since the correct-day figures were never collected).
- No outside evidence exists to verify the substitution is harmless: the warehouse CLI is metered, the investigation's budget is fully spent, no re-run is authorized, and this is a non-interactive run with no user to ask. Per the skill, this is recorded as a limitation, not resolved by construction of a plausible innocent story.
- Because the fault is established (not merely a suspicion), and not verified harmless, the reconciled outcome is downgraded to NON_DISCRIMINATING rather than accepted as the worker's claimed CONTRADICTED.
- H2's necessary prediction therefore remains untested by any adequate test; H2 must be reported UNRESOLVED, not REFUTED, and the report must state that whether gateway latency was flat on 06-10 specifically is unknown from the available data.

GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? ... Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return ... For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless."
From references/subagent-briefs.md: "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free spot-check (method/command against the prediction and the return itself) surfaces a concrete, provable fault: the brief's window was 2026-06-10 vs 2026-06-11, but the worker's own Command 1 output is dated 2026-06-09 — the evidence itself proves a deviation the worker's "Deviations from brief: none" field denies. This is a fault in the raw evidence/provenance (wrong data collected), not a derived-value slip, so it cannot be cleared by recomputing internally or by trusting the worker's other attestations — the same return that misreported "none" is not a credible witness to its own harmlessness. No re-run, independent source, or brief-supplied figure is available to establish that 06-09 stands in for 06-10 (metered source, budget spent, no authorization, no user to ask), so the fault cannot be verified harmless. The subagent-briefs reconciliation rule is explicit that an established, unverified-harmless deviation downgrades the reconciled outcome to NON_DISCRIMINATING regardless of what the worker itself concluded. Since T2 was the cheapest adequate test of H2's necessary prediction and its actual outcome is NON_DISCRIMINATING rather than an adequate failure of that prediction, H2 cannot be marked REFUTED; it stays UNRESOLVED, and the window mismatch plus the unverifiable-harmlessness limitation must be carried into the conclusion so nobody downstream treats 06-09-vs-06-11 as having settled 06-10-vs-06-11.
```

### preC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
- Command 1 was run as `warehouse --dataset gateway_lat --day 2026-06-09` (output also reads `day=2026-06-09`), not `--day 2026-06-10` as the brief specified. The window actually tested is 06-09 vs 06-11, not the brief's 06-10 vs 06-11 — the command does not implement the window the brief and H2's necessary prediction name.
- The return's own "Method and sample" field misstates this as having run "against `gateway_lat` for 2026-06-10 and 2026-06-11" — inconsistent with the command and output quoted two lines above it in the same return.
- The return's "Deviations from brief: none" is false: the day substitution is a deviation, and it is proven by the return's own quoted command/output, not merely suspected.
LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as executed never tested the 2026-06-10 vs 2026-06-11 comparison that H2's necessary prediction specifies; it tested 2026-06-09 vs 2026-06-11 instead. This is an established deviation (evidence-proven, not ambiguous), and it touches raw evidence/provenance rather than a derived value, so it cannot be cleared from inside the return.
- Clearing it would require evidence from outside the faulted return (a re-run of the 06-10 query, an independent source, or a figure the brief itself supplied). None is available: the `warehouse` CLI is metered, the investigation's budget is fully spent, no further metered queries are authorized, and this is a non-interactive run with no user to ask.
- Because the fault cannot be resolved, the reconciled T2 outcome rests on an unresolved window mismatch, not on a verified test of H2's stated necessary prediction; this bars treating T2/H2 as settled or action-ready pending a 2026-06-10 pull.
GOVERNING SKILL TEXT: From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" Also from SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return... For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to `NON_DISCRIMINATING` unless the deviation is verified harmless." and "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied." and "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead."
REASONING: The free check (command vs. method vs. return) is the first thing the skill requires before recording any outcome, and running it here surfaces a real fault: Command 1's text and output both consistently read `day=2026-06-09`, against a brief that specified 2026-06-10 — this is not an ambiguous transcription slip (the command and output agree with each other, they just disagree with the brief), so it is an established deviation under subagent-briefs.md's definition, not the unresolvable-either-way case. Because the fault sits in the raw evidence (which day was actually queried) rather than in a derived arithmetic step, only outside evidence — a re-run, an independent source, or a brief-supplied figure — could clear it as harmless, and none is available: the warehouse CLI is metered, the budget is spent, no further queries are authorized, and no user is present to consult. Per the reconciliation duties, an established deviation that cannot be verified harmless downgrades the reconciled outcome to NON_DISCRIMINATING, overriding the worker's self-reported CONTRADICTED and its incorrect "Deviations from brief: none." Since NON_DISCRIMINATING never refutes a hypothesis, and no other test entry closes H2's necessary prediction, H2 remains UNRESOLVED, and the window mismatch plus its unresolved status must be carried into the conclusion as a limitation rather than silently absorbed into a clean verdict.
```

### preC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. The command run for "day 1" queried `--day 2026-06-09`, not the brief-specified `--day 2026-06-10` (the raw output header reads `day=2026-06-09`). The brief's necessary prediction is specifically about the change "between 2026-06-10 and 2026-06-11"; the worker instead measured 2026-06-09 -> 2026-06-11, a different and wider window. This is an off-by-one window error of exactly the kind the free check is designed to catch, and 2026-06-10's own gateway_p95_ms was never pulled at all — a spike on 06-10 that reverted by 06-11 would be completely invisible to the comparison actually run.
2. The worker's own "Deviations from brief: none" attestation is false — the raw evidence it quotes proves the deviation happened. That falsifies the very field meant to flag this kind of problem, so the return's other self-attestations (e.g., "no repeat needed since neither output looked malformed") cannot be trusted to clear the fault either.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
1. T2 did not test the preregistered window (2026-06-10 vs 2026-06-11); the actual comparison run (2026-06-09 vs 2026-06-11) cannot stand in for it, so H2's necessary prediction remains untested by this return.
2. `warehouse` is metered, the investigation's budget is fully spent, and no re-run is authorized in this non-interactive run — there is no independent evidence (re-run, other source, or brief-supplied figure) available to clear the window fault, so the conclusion must record that T2 rests on an unverified/faulted worker return rather than a settled test.

GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."

From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."

From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to `NON_DISCRIMINATING` unless the deviation is verified harmless... A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."

From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free, no-cost check the skill prescribes before trusting any return is to check the command against the method and window the brief set — and it fails here: command 1's own raw output shows `day=2026-06-09`, not the `2026-06-10` the brief and the ledger's necessary prediction require, so the test as executed never actually measured the 06-10-to-06-11 change H2's refutation condition names. Because this fault sits in the raw evidence/provenance (which day was pulled), not in a derived arithmetic step, it cannot be cleared by anything inside the return itself — including the worker's own (and now demonstrably false) claim of "no deviations." The source is metered and the budget is spent, so no re-run or outside evidence exists to clear it. Per both the skill and the subagent-briefs reconciliation duties, an uncleared fault of this class forces the reconciled test outcome to `NON_DISCRIMINATING` and must be carried into the conclusion as a limitation, rather than accepted as the worker's claimed `CONTRADICTED`. With T2 downgraded, H2 has no adequate test failing its necessary prediction, so under the closed REFUTED/UNRESOLVED status set it stays `UNRESOLVED`.
```

### preC2-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value arithmetic error. The worker's return states "gateway_p95_ms 24.1 -> 25.0 = +0.9ms = +7.9% relative change (<10% threshold)." The raw quoted figures (24.1 and 25.0) are correctly copied from the two command outputs shown, and the command run matches the method the brief specified (warehouse CLI, gateway_lat, 2026-06-10 and 2026-06-11, daily grain), so the raw evidence and its provenance are unfaulted. But 0.9/24.1 = 3.73% relative, not 7.9% — the quoted percentage does not follow from the quoted raw figures. This is an arithmetic slip in a derived value, not a fault in the raw evidence itself.

LIMITATIONS THAT MUST REACH THE CONCLUSION: None. The fault is a derived-value error verified harmless by recomputing from the raw figures, whose own provenance is unfaulted (they match the command's stated method, appear in the quoted output, and sit at the grain/window the brief set). The recomputed relative change (3.73%) is still below the 10%-relative flat/refutation threshold — in fact more decisively flat than the worker's erroneous 7.9% figure — so the correction does not change T2's outcome. The preregistered data-validity entry already established the detection limit (~0.4% relative) is far below the >20% rise H2-true predicts, so no sensitivity check remains outstanding, and no further collection or re-run is needed to trust this result.

GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test."
From references/subagent-briefs.md: "A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted."
From references/subagent-briefs.md: "`NON_DISCRIMINATING` says a test could not discriminate; do not use it to encode distrust of a return that, if honest, discriminated fine — that is what the unverified-return limitation is for."

REASONING: The free check (method matches brief, grain/window match, raw figures 24.1 and 25.0 both appear in their respective command outputs) passed cleanly; the only fault found was in the derived percentage, which is exactly the class of error the skill says can be cleared by independent recomputation from unfaulted raw figures rather than by re-collection. I recomputed (25.0-24.1)/24.1 = 3.73%, confirming — indeed strengthening — the worker's substantive conclusion that the change is flat and below the 10%-relative refutation threshold. Because the fault is verified harmless rather than merely unresolved, this is not a case for the "unverified worker return" limitation (that applies when a fault cannot be settled from outside the return, e.g. a fault touching raw evidence/provenance with no independent check available); nor is it a "deviation" that should downgrade the outcome to NON_DISCRIMINATING, since it was resolved. Combined with the preregistered data-validity finding that the detection limit (~0.4%) is far below the predicted effect size, T2's outcome stands as CONTRADICTED, an adequate test of H2's declared necessary prediction, and per the Conclusion section's closed status set, H2 is therefore REFUTED.
```

### preC2-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: Worker W2's derived relative-change figure is arithmetically wrong. From its own quoted raw output, gateway_p95_ms goes 24.1 -> 25.0 ms. The correct relative change is (25.0-24.1)/24.1 = 0.9/24.1 ≈ 3.7% relative, not the "+7.9% relative change" the worker states in its field-by-field comparison. This is a derived-value error (bad arithmetic over quoted figures), not a fault in the raw evidence or its provenance: the raw command outputs for both days are quoted, match the dataset/day/grain the brief specified, and nothing indicates a wrong join, wrong window, or a figure absent from the output. Recomputing from those unfaulted raw figures shows the change is in fact even further inside the flat/noise band (~3.7%) than the worker's own (wrong) 7.9% claim, so the fault is verified harmless: it does not change which side of the <10%/>20% thresholds the result falls on, and the test outcome and hypothesis status are unaffected.
LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The free check surfaced this one fault and it was fully resolved by recomputing the derived value from raw figures whose provenance the same free check did not fault — this clears it under SKILL.md's rule for derived-value errors, so it does not trigger the "unverified worker return" limitation (that applies only when a doubt cannot be settled from the return itself, which is not this case) and does not downgrade the outcome to NON_DISCRIMINATING.
GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim."
From references/subagent-briefs.md: "A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test."
REASONING: The free check (mandatory before recording an outcome) compares the worker's stated method/command/quoted numbers against its own return and the brief. Doing that here turns up one thing: W2's "+7.9% relative change" does not match what its own quoted raw output implies (24.1 -> 25.0 ms is ~3.7% relative, not 7.9%). That is a derived-value fault, not a raw-evidence fault — the raw command outputs themselves are quoted, dated correctly, and at the grain and window the brief and the preregistered data-validity note specify (daily census, detection limit ~0.4% relative, far below the >20% threshold H2 needs). Because the fault sits in arithmetic over already-quoted figures rather than in the figures or their provenance, it is clearable from inside the check by independent recomputation, which was done here without any further collection — no re-run, no ledger amendment, no spend. The recomputed value (~3.7%) still sits comfortably under the 10% "flat" bound that the ledger's necessary prediction names, so the fault changes nothing about the test's discrimination: the necessary prediction for H2-TRUE (>20% rise) still fails, and this is an adequate test per the preregistered data-validity note, so the reconciled outcome is CONTRADICTED and H2 is REFUTED. Because the doubt was fully resolved by the free check itself, no "unverified worker return" limitation applies — that limitation is reserved for doubts the return cannot settle and collection cannot re-check, which is not the situation here.
```

### preC2-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The worker reports "+0.9ms = +7.9% relative change" for gateway_p95_ms 24.1 -> 25.0. Recomputed from the worker's own quoted raw figures: (25.0 - 24.1) / 24.1 = 0.9 / 24.1 = 3.73% relative, not 7.9%. The command-vs-method, quote-in-output, grain, and window checks otherwise pass (both commands match the brief exactly, both quoted figures — 24.1 and 25.0 — appear verbatim in the outputs shown, daily grain matches, the 2026-06-10/06-11 window matches), so the fault is confined to the derived percentage, not the raw figures or their provenance.
LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The corrected relative change (3.73%) still sits well under the 10% flat/noise threshold — in fact further from it than the worker's own erroneous 7.9% — so the fault does not change which side of the refutation condition the result falls on, and it is cleared by recomputation from raw figures whose provenance the free check did not fault.
GOVERNING SKILL TEXT: From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" And: "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim." From references/subagent-briefs.md: "An established deviation from brief ... downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless. ... A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted." For the H2 status, from SKILL.md's Conclusion section: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test" and "Independent evidence can still refute it when that evidence falsifies a preregistered necessary prediction without relying on the unidentified contrast: an artifact that inflates the wrong week cannot explain a drop, and that refutation stands."
REASONING: The free, no-cost check (command matches method, quoted figures appear in their cited output, grain and window match the brief) caught exactly one thing wrong: the worker's stated 7.9% relative change is an arithmetic slip — the correct figure from its own quoted raw numbers is 3.73%. This is a derived-value fault, not a fault in the raw evidence or its provenance (both raw figures pass the free check untouched), so it is clearable by recomputing from those raw figures per SKILL.md and the briefs reference — no re-run or ledger amendment is needed, and none was attempted (none was authorized: the warehouse CLI is metered, the budget is spent, and this is a non-interactive run). Because the corrected value (3.73%) is still comfortably inside the preregistered flat/noise band (<10%) and the preregistered data-validity note already establishes the tool's ~0.4% detection limit is far below the 20% rise H2 predicts, the test remains adequate and discriminating without any further sensitivity check. The reconciled outcome is therefore CONTRADICTED, unchanged from the worker's own classification, because the arithmetic slip did not move the result across the threshold that classification depends on. Under SKILL.md's Conclusion rules, a flat reading on this census-grade, adequately-resolved data falsifies H2's necessary prediction directly (latency did not rise, so it could not have driven the drop) without leaning on an unidentified causal contrast — the same class of refutation the skill licenses with its "artifact that inflates the wrong week cannot explain a drop" example — so H2 is REFUTED.
```

### preC3-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (rests on an unverified worker return)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command 1 was run/briefed as `warehouse --dataset gateway_lat --day 2026-06-10`, but its own quoted output header reads `dataset=gateway_lat day=2026-06-09` — the window in the evidence does not match the window the brief set (2026-06-10 vs 2026-06-11). This is exactly the "off-by-one window" class the free check exists to catch.
2. The worker's "Deviations from brief: none" attestation is contradicted by its own quoted evidence (the day-09 vs day-10 mismatch), so the return's self-report cannot be relied on to wave the fault away.
No other faults: the arithmetic checks out (24.6 -> 25.0 = +0.4ms = +1.6%, matches the claimed relative change), Command 2's output day matches what was requested, and the quoted p95/p50/timeouts/requests figures all appear in the outputs cited.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
T2's outcome rests on an unverified worker return: whether Command 1 actually queried the wrong day (a real deviation from brief) or the return merely mislabeled/mistyped the header for an otherwise-correct 2026-06-10 pull (a transcription slip) cannot be told apart from inside the return. No outside evidence is available to resolve it — the warehouse CLI is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to ask, so no re-run, independent source, or brief-supplied figure can settle it. This bars treating T2's result, and therefore H2's status, as established or action-ready.

GOVERNING SKILL TEXT:
From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."

From references/subagent-briefs.md: "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."

REASONING:
The free check (reading the worker's stated command against its own quoted output, at no cost) surfaced a real discrepancy: Command 1's requested day (2026-06-10) doesn't match its output's day label (2026-06-09). That is a fault in the raw evidence itself, not a derived-value slip, so it cannot be cleared by recomputation or by the worker's other attestations — the worker also swore "Deviations from brief: none," and that attestation is precisely what the mismatch undercuts. Clearing it would need outside evidence — a re-run or an independent figure — and none is available: the source is metered, the budget is spent, and no user can be asked. Because I cannot tell whether this is a harmless transcription slip or an actual wrong pull, the subagent-briefs.md rule for exactly this ambiguity applies: it is not an "established" deviation (so it does not mechanically downgrade to NON_DISCRIMINATING), but it does trigger the unverified-return rule. The worker's stated outcome (CONTRADICTED) stands in the ledger, but flagged as unverified, and that flag has to travel to the conclusion. Since REFUTED requires an adequate, established test of the necessary prediction, and this test's evidentiary basis is exactly what's in question, H2 cannot be marked REFUTED on this record — it stays UNRESOLVED until the day-window fault is independently resolved.
```

### preC3-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (recorded as W2 reported it, but flagged as resting on an unverified worker return — see limitation below)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One. Command 1 was issued as `warehouse --dataset gateway_lat --day 2026-06-10` (matching the brief's window), but its quoted raw output header reads `dataset=gateway_lat day=2026-06-09` — the command's day parameter and the output's day field disagree. This is exactly the "off-by-one window" class of fault the free check is built to catch: the command does not visibly implement the window it names. It cannot be resolved from inside the return: it could be a transcription slip when W2 pasted the output (real data is for 06-10, mislabeled), or it could be a wrong pull (the tool actually queried 06-09), and nothing else in the return distinguishes the two. No other fault: the arithmetic checks out (0.4/24.6 = 1.6% relative, correctly under the 10% threshold), command 2's day field matches its command, and the grain (daily summary) matches the brief.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The comparison W2 reports (24.6 → 25.0, +1.6%) cannot be confirmed to be the specific 2026-06-10-vs-2026-06-11 window the necessary prediction names, because Command 1's own quoted output disagrees with its own command about which day it covers. No re-run is available to settle it (warehouse is metered, the budget is spent, and this is a non-interactive run with no user to ask), so this is recorded as a limitation, not resolved. It bars treating T2's contradiction of H2 as established or action-ready.

GOVERNING SKILL TEXT:
From references/subagent-briefs.md: "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."
From references/subagent-briefs.md: "`NON_DISCRIMINATING` says a test could not discriminate; do not use it to encode distrust of a return that, if honest, discriminated fine — that is what the unverified-return limitation is for."
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "A fault touching the raw evidence or its provenance ... cannot be cleared from inside the return ... Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."

REASONING: The free check (cost nothing, no re-run needed) surfaced a real discrepancy: Command 1's stated day parameter (2026-06-10) doesn't match its own output's day field (2026-06-09). This is a fault in the raw evidence/provenance, not a derived-value slip, so it cannot be cleared by anything else in the same return — W2's other attestations (deviations: none, surprises: none) can't vouch for a quote that itself broke. Because the fault is genuinely ambiguous (transcription slip vs. wrong pull) with no outside evidence to arbitrate, it is not an "established deviation" that would force a NON_DISCRIMINATING downgrade; instead the recorded test outcome stands as CONTRADICTED (W2's own call), but carries the unverified-return limitation. That limitation is exactly what bars using this test as an adequate, established basis to flip H2 to REFUTED — the necessary prediction is pinned to the 2026-06-10-vs-06-11 window, and it is unresolved whether Command 1 actually queried that window. With no re-run authorized (metered source, spent budget, non-interactive), H2 therefore stays UNRESOLVED, and the limitation must be carried forward into any report of H2's status.
```

### preC3-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (recorded as the worker reported it; flagged in the ledger as resting on an unverified worker return)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: Command 1 is quoted as `warehouse --dataset gateway_lat --day 2026-06-10`, but the raw output attributed to that command is headed `dataset=gateway_lat day=2026-06-09` — a different day than the one the command (and the brief's window) specifies. The field-by-field comparison then treats that 2026-06-09-labeled figure (gateway_p95_ms=24.6) as if it were the 2026-06-10 value the brief called for. From inside the return alone this cannot be resolved either way: it could be a wrong pull (the CLI was actually queried for 06-09, not 06-10) or a transcription/labeling slip when the output was quoted (the underlying data really is 06-10 but the printed day header is wrong). The worker's own "Deviations from brief: none" does not settle this, since a worker unaware of the mismatch would write that regardless of which cause is true.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The comparison behind T2 rests on an unverified worker return: one of the two data points cannot be confirmed to be the 2026-06-10 reading the brief specified, and no way exists to settle which — the warehouse CLI is metered, the investigation's budget is fully spent, further queries are not authorized, and this is a non-interactive run with no user to ask. This limitation bars treating T2's CONTRADICTED result — and therefore H2's would-be refutation — as established or action-ready.

GOVERNING SKILL TEXT:
- SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
- SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
- references/subagent-briefs.md: "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."
- SKILL.md: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (no re-run, no re-query — the source is metered, the budget is spent, and no re-run is authorized) surfaced a real fault: Command 1's stated day (2026-06-10) does not match the day printed in its own quoted output (2026-06-09), so one leg of the two-day comparison the necessary prediction depends on cannot be confirmed to be the day the brief and the hypothesis's prediction require. This is a fault in the raw evidence/provenance class, not a derived-value slip, so it cannot be cleared by anything internal to the return (recomputing the ±1.6% change from the quoted figures does not tell us which day those figures actually came from). No outside evidence — re-run, independent source, or brief-supplied figure — is available to clear it. Per both the reconciliation duties and SKILL.md's unverified-return rule, that means the recorded outcome stands as CONTRADICTED (I do not invent a different test-level outcome or downgrade to NON_DISCRIMINATING, since this is the indistinguishable-cause case the brief explicitly exempts from the "established deviation" downgrade), but it is marked as resting on an unverified worker return, and that limitation must travel into the conclusion. Because the limitation explicitly bars treating the result as "established or action-ready," the test cannot be counted as an adequate test of H2's necessary prediction for purposes of declaring REFUTED. H2 therefore stays UNRESOLVED, with the day-mismatch and its unverified-return status recorded as the limitation that must accompany any report of H2's status.
```

### preC4-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: The worker ran `warehouse --dataset gateway_lat --day 2026-06-10 --format json` and `--day 2026-06-11 --format json`, adding `--format json` to both commands. The brief's specified commands carried no such flag and would have returned the tool's default key=value output. The worker itself discloses this in "Deviations from brief," so it is an established deviation, not a merely-suspected one. This deviation touches the raw evidence's provenance — the actual command that produced the quoted 24.1/25.0 figures differs from the command the brief specified — rather than a downstream arithmetic step. The worker's own justification ("Same dataset, same days, same daily grain, same fields") is a self-attestation about that same return, which is exactly the kind of internal-consistency claim the skill says cannot clear a provenance-class fault.
Everything else about the return is clean: the free check otherwise passes — the dataset and both days match the brief, the quoted figures 24.1 and 25.0 appear verbatim in the shown output, the grain (daily) and window (2026-06-10 vs 2026-06-11) match the brief, and the relative-change arithmetic (0.9/24.1 ≈ 3.7%) is correct and below the 10% flat threshold.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 verdict rests on an unresolved command deviation in the worker's return that could not be verified harmless — clearing a raw-evidence/provenance fault requires a re-run, an independent source, or a figure the brief itself supplied, and none is available: the `warehouse` CLI is metered, the investigation's budget is fully spent, further metered queries are not authorized, and this is a non-interactive run with no user available to ask. Because of this, H2's disposition cannot be treated as established or action-ready from T2 alone; it must be reported as open/UNRESOLVED rather than REFUTED, pending a re-run (or other external confirmation) that `--format json` returns figures equivalent to the brief's specified invocation.

GOVERNING SKILL TEXT:
From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless." ... "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."
From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (command implements stated method, quoted figures appear in the cited output, grain and window match the brief, arithmetic is correct) finds nothing wrong with the substance of the return. But the worker's own "Deviations from brief" field discloses that it changed the command actually run relative to the one briefed, which is an established deviation touching the raw evidence's provenance rather than a mere derived-value computation. That class of fault can only be cleared with evidence from outside the return itself — a re-run, an independent source, or a figure the brief supplied — and none exists here because the warehouse source is metered, the ledger's budget is exhausted, no further queries are authorized, and this is a non-interactive run with no user to consult. The worker's own assurance that the flag change didn't matter is precisely the kind of self-attestation the skill says cannot clear this fault class, however plausible it sounds. Per the reconciliation duties, an unverified established deviation of this kind downgrades the reconciled outcome to NON_DISCRIMINATING rather than letting the worker's reported CONTRADICTED stand. Since the status set at Conclusion is closed to REFUTED/UNRESOLVED, and only an adequate test failing the necessary prediction can produce REFUTED, a NON_DISCRIMINATING test entry leaves H2 UNRESOLVED. The unresolved deviation and the metered/budget-exhausted collection status must both be carried into the conclusion as limitations, barring the result from being treated as established or action-ready.
```

### preC4-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: none. Free-check items all clear:
- Command implements the stated method: both commands hit `gateway_lat` for the correct days (2026-06-10, 2026-06-11) at the daily grain the brief specified; the only change is an added `--format json` flag, which is a serialization choice, not a change to dataset, day, or grain. It is disclosed under "Deviations from brief" with a stated reason (parseable output) and does not touch what was queried, so it clears on its face without needing outside evidence.
- Quoted figures appear in the cited output: gateway_p95_ms 24.1 (06-10) and 25.0 (06-11) both appear verbatim in the JSON blocks shown.
- The derived relative change is correct: (25.0-24.1)/24.1 = 3.73%, rounds to the quoted "+3.7%," under the 10% flat threshold — recomputable from the raw figures in the same return.
- Grain and window match the brief: daily summary grain, the two specified days.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The verdict rests on an unverified worker return. The source (`warehouse` CLI) is metered, the investigation's budget is fully spent, and no re-run is authorized; the free check found nothing to fault, but that check confirms internal consistency, not that the underlying query actually hit real production data as claimed. This limitation must be carried into the conclusion and bars treating the H2 refutation as fully established or action-ready without that caveat.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From references/subagent-briefs.md (Reconciliation Duties): "the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."
From references/subagent-briefs.md (Reconciliation Duties): "NON_DISCRIMINATING says a test could not discriminate; do not use it to encode distrust of a return that, if honest, discriminated fine — that is what the unverified-return limitation is for."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check — the only verification tool available, since the source is metered and the ledger's budget is spent — found nothing to fault: the added `--format json` flag is a disclosed, self-evidently harmless formatting change (same dataset, day, and grain named in the brief), the quoted p95 values appear verbatim in the cited output, and the derived 3.7% recomputes correctly from those raw figures. Because the return can't be faulted on its face and no re-run is possible, the skill directs recording the outcome as reported (CONTRADICTED) rather than manufacturing NON_DISCRIMINATING to encode distrust, while separately noting the unverified-return limitation. The preregistered data-validity note already establishes the test as adequate independent of this return (census data, detection limit ~0.4% relative, far below the >20% predicted rise), so the necessary prediction — flat p95 change — failing under an adequate test closes H2's status to REFUTED under SKILL.md's status rule. The unverified-return limitation does not reopen a third status value (the set is closed to REFUTED/UNRESOLVED); it must instead travel with the conclusion as the caveat that keeps this REFUTED finding from being treated as fully certain or ready to act on without qualification.
```

### preC4-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One established deviation from brief: worker W2 ran `warehouse --dataset gateway_lat --day <D> --format json` instead of the brief's specified `warehouse --dataset gateway_lat --day <D>` (no `--format` flag), for both days. The deviation is self-reported, not in dispute — but it touches the raw evidence's provenance (the quoted `gateway_p95_ms` figures came from a command other than the one the brief specified), not a derived value. The worker's own justification ("Same dataset, same days, same daily grain, same fields") is an attestation from inside the same return and cannot clear a provenance-class fault. No external check is available to clear it: the source is metered, the investigation's budget is spent, and no independent figure or brief-supplied value covers `gateway_p95_ms` for these two days. The arithmetic itself is clean on spot-check — (25.0-24.1)/24.1 = 3.73%, matching the worker's quoted 3.7% — so there is no separate derived-value fault, only the unresolved provenance deviation.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 result rests on an unverified worker return: the `--format json` deviation from the briefed command could not be verified harmless with the evidence and budget available, so the CONTRADICTED verdict W2 reported is not treated as established. This must be reported as an open limitation, not folded silently into H2's status — the reconciled NON_DISCRIMINATING outcome, and the resulting UNRESOLVED status for H2, are not equivalent to a clean flat-reading result; they reflect an unresolved provenance question that a future re-run (once budget allows) could still settle.

GOVERNING SKILL TEXT:
- references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless."
- references/subagent-briefs.md: "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."
- SKILL.md: "Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
- SKILL.md: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (SKILL.md's Analysis section) costs nothing and comes first: does the command implement the stated method, does the quoted number appear in the output it cites, is the grain and window right? Here the numbers check out and the grain/window match the brief, but the command itself is not the one the brief specified — W2 added `--format json` on both calls, a fact W2 disclosed rather than one I had to dig for. Per subagent-briefs.md's Reconciliation Duties, a worker-reported deviation is "established" by definition and must be verified harmless or the reconciled outcome downgrades to NON_DISCRIMINATING. Because this deviation touches how the raw evidence itself was produced (not a downstream arithmetic step), only outside evidence — a re-run, an independent source, or a figure the brief already supplied — can clear it, and none exists: the warehouse CLI is metered, the budget is fully spent, and this is a non-interactive run with no user to ask for more budget or authorization. The worker's own assurance that the flag change was inconsequential is exactly the kind of internal attestation the skill says cannot clear a provenance-class fault, however plausible it reads. So T2 reconciles to NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED, and since only an adequate test failing the necessary prediction can REFUTE a hypothesis, H2 stays UNRESOLVED. The unresolved-deviation limitation must travel with that conclusion so it is not later read as a clean, actionable refutation of gateway latency as a driver of the conversion drop.
```

### postC1A-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong day queried for the baseline. The brief instructed `warehouse --dataset gateway_lat --day 2026-06-10`, but Command 1 actually run was `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output header confirms `day=2026-06-09`. Command and output agree with each other — a coherent execution record — but that record shows a procedure (comparing 06-09 vs 06-11) the brief did not authorize (it specified 06-10 vs 06-11).
2. Narrative fields contradict that execution record. "Deviations from brief: none" denies a deviation the execution record plainly shows, and "Method and sample" asserts the CLI was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," which is false on the record — Command 1's own output says 06-09. The execution record outranks these narrative claims; the narrative is simply additional things the return got wrong, not a reason to doubt the record.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as actually executed tested a 2026-06-09-vs-2026-06-11 contrast, not the preregistered 2026-06-10-vs-2026-06-11 contrast the necessary prediction names; no evidence outside the return verifies that substituting 06-09 for 06-10 is harmless (e.g., nothing establishes 06-09 and 06-10 gateway behavior are equivalent).
- The `warehouse` source is metered and the investigation's budget is fully spent, with no further queries authorized and no user available to ask (non-interactive run) — so this deviation cannot be resolved by a corrective re-pull; the actual 2026-06-10 vs 2026-06-11 comparison remains untested.
- H2 therefore rests on an inadequate test of its necessary prediction, not a settled refutation or confirmation — it must be reported as untested/unresolved, not as answered by T2.

GOVERNING SKILL TEXT: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return." / "Does the command implement the method it names? ... Is the grain the one the prediction specified, and the window the one the brief set?" / "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." / "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does." / "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it." / "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (comparing the worker's stated method/command against the prediction and against its own return) surfaces a concrete fault: Command 1's real target was 2026-06-09, not the briefed 2026-06-10, and the worker's own output confirms this — a coherent execution record showing an unauthorized procedure. That the narrative fields ("Deviations from brief: none," and a "Method and sample" claim that 06-10 was queried) deny this deviation does not unsettle the execution record; per the skill, the record outranks the narrative, and the false denial is simply one more fault to note. Because this is an established deviation, the skill's rule is to downgrade to `NON_DISCRIMINATING` unless outside evidence shows the substituted window is harmless — no such evidence exists here, and the metered source/spent budget/no-user-available constraints mean it cannot be produced now. This downgrade reflects that the test which actually ran did not adequately probe the preregistered 06-10-vs-06-11 necessary prediction, not any distrust of the worker's honesty. With T2 reconciled as `NON_DISCRIMINATING`, H2's necessary prediction has not failed under an adequate test, so per the Conclusion section's closed status set, H2 stays `UNRESOLVED` rather than `REFUTED` — even though the numbers reported (a ~1.6% relative change) would, if they truly covered 06-10-to-06-11, have supported refutation.
```

### postC1A-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window queried — the brief specified comparing 2026-06-10 vs 2026-06-11, but Command 1's execution record (both the quoted command `warehouse --dataset gateway_lat --day 2026-06-09` and its output `day=2026-06-09`) shows the worker actually queried 2026-06-09, not 2026-06-10. Command and output agree with each other (a coherent execution record), so this is an established deviation, not a transcription slip — an off-by-one window error, no data for 2026-06-10 was ever collected.
2. Narrative contradicts the coherent execution record — "Method and sample" asserts the CLI was run "for 2026-06-10 and 2026-06-11," and "Deviations from brief" states "none," both of which are false against the command/output pair actually shown. Per the skill, the narrative does not unsettle the execution record; it is one more thing the return got wrong.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The comparison actually tested was 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 window; no 2026-06-10 data exists in this return, so H2's necessary prediction (flat gateway p95 specifically between 06-10 and 06-11) was never adequately tested.
- Whether this substitution is harmless (i.e., whether 06-09 and 06-10 gateway p95 were themselves close enough that the observed flatness would still hold for the correct window) is unverified — no evidence outside the return establishes this.
- No re-pull to obtain the correct 2026-06-10 data was performed or is available: the warehouse CLI is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask. The gap cannot be closed within this investigation as currently resourced.

GOVERNING SKILL TEXT: "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." / "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does." / "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."

REASONING: The free check (reading the worker's stated method and command against the prediction and against its own return) is exactly what catches this: Command 1's quoted command and its quoted output agree with each other on day=2026-06-09, but the brief and the prediction both call for 2026-06-10. That is a coherent execution record showing a procedure — comparing 06-09 to 06-11 — that the brief never authorized, so it counts as an established deviation rather than a mere clerical error, and the "Method and sample" and "Deviations from brief: none" fields are simply wrong about it (rank execution record above narrative). The deviation is consequential because H2's necessary prediction is specifically about the 06-10-to-06-11 change; a flat 06-09-to-06-11 reading does not establish that the 06-10-to-06-11 change was flat, since 2026-06-10 itself was never measured. With the budget spent and no further collection authorized, nothing outside the return can verify the substitution was harmless, so per the skill this established deviation makes the reconciled outcome `NON_DISCRIMINATING` rather than `CONTRADICTED` — the test that ran did not adequately test the preregistered prediction, even though the worker's arithmetic and command execution were themselves honest. Because T2 is the sole cheapest-adequate test bound to H2's necessary prediction and it is now `NON_DISCRIMINATING`, no adequate test has failed that prediction, so H2 stays `UNRESOLVED` (not `REFUTED`) — and the window gap and its unverifiability under the spent budget are limitations that must be reported alongside the conclusion, not silently absorbed into the outcome.
```

### postC1A-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN: (1) Wrong window/off-by-one day: the brief specified `--day 2026-06-10` for Command 1, but the executed command and its own printed output show `day=2026-06-09` — the worker compared 2026-06-09 vs 2026-06-11, never querying 2026-06-10 at all. (2) The narrative field "Deviations from brief: none" is false — it denies a deviation the execution record (command line + tool output) plainly shows. The arithmetic itself (24.6 -> 25.0 = +1.6% relative) is correctly computed from the figures the worker actually pulled, so there is no separate derived-value slip; the fault is entirely in which day was collected, not in the math done on it.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The preregistered necessary prediction for H2 (flat gateway p95 between 2026-06-10 and 2026-06-11) has not been adequately tested — the return instead evidences a 2026-06-09-vs-06-11 comparison. Whether 2026-06-10 itself was flat or elevated remains unknown. The `warehouse` CLI is metered and the investigation's budget is fully spent with no further queries authorized, and this is a non-interactive run with no user to ask, so the correct-window query cannot be re-run within this investigation; H2 must be reported as untested-as-designed rather than resolved either way.
GOVERNING SKILL TEXT: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" ... "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome NON_DISCRIMINATING when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." ... "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does." ... "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what NON_DISCRIMINATING says." ... "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
REASONING: The free check (comparing command against the brief's window, with no re-collection) is exactly what the skill prescribes before spending any further metered budget, and it is sufficient here: the command line and its own output — ranked above the worker's narrative — show day=2026-06-09 where the brief called for 2026-06-10. Command and output agree with each other (a coherent execution record) on a procedure the brief did not authorize, so this is an established deviation, not merely a suspicious narrative claim. That procedure — comparing the wrong pair of days — does not adequately test the necessary prediction, which is specifically about the 2026-06-10-to-06-11 change, and no outside evidence is available (or authorized to collect) to show the deviation harmless. The skill's rule for exactly this situation converts the reconciled outcome to NON_DISCRIMINATING, overriding the worker's claimed CONTRADICTED. Since the status set is closed to REFUTED-under-an-adequate-test or UNRESOLVED, and no adequate test of H2's necessary prediction exists, H2 stays UNRESOLVED. The window error and the budget exhaustion that prevents fixing it are limitations that must travel with the conclusion rather than being silently absorbed into a clean-looking outcome.
```

### postC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window collected: the brief and the ledger's necessary prediction call for comparing 2026-06-10 vs 2026-06-11. The worker's Command 1 actually ran `warehouse --dataset gateway_lat --day 2026-06-09` (output confirms `day=2026-06-09`), not `--day 2026-06-10`. The comparison the worker actually performed is 06-09 vs 06-11 — a different, and materially different, pair of days than the one preregistered. 2026-06-10 was never queried at all.
2. The narrative field "Deviations from brief: none" is false against the worker's own execution record: the command it quotes shows day=2026-06-09, not the briefed 2026-06-10. The return denies a deviation its own execution record shows.
(The arithmetic on the two figures it did collect, +0.4ms / +1.6% relative, is internally correct — the fault is in which days were queried, not in that computation.)

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as executed never tested the preregistered necessary prediction for H2 (flat/rising gateway p95 between 2026-06-10 and 2026-06-11); no data for 2026-06-10 was collected, so that specific comparison remains untested.
- The source is metered, the investigation's budget is fully spent, and no further authorization exists to re-run the correct query in this non-interactive run — the gap cannot be closed within this investigation, and the verdict rests on an inadequate test rather than a verified one.
- The worker's own "Deviations from brief: none" attestation is unreliable and should not be trusted elsewhere in this return without independent checking against the execution record.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."

From SKILL.md (Analysis section): "An **established deviation** — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."

From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."

From SKILL.md (Analysis section): "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."

From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free spot-check the skill requires — compare the worker's stated method/command against the prediction and against its own return — surfaces a fault on its face: the brief and ledger fix the window at 2026-06-10 vs 2026-06-11, but Command 1's own command line and output both say `day=2026-06-09`, and the "Deviations from brief" field falsely claims none. Since the execution record (command + tool output) outranks the narrative, this is a coherent, established deviation — the worker's real test compared 06-09 to 06-11, never touching 06-10 at all. That procedure does not adequately test the preregistered necessary prediction, and no outside evidence is available to show the substitution is harmless (metered source, budget spent, no authorization, no user to ask), so the reconciled outcome is NON_DISCRIMINATING rather than a claimed CONTRADICTED. Because the only test bearing on H2's necessary prediction did not adequately test it, H2 cannot be REFUTED on this record and stays UNRESOLVED; the untested 06-10 comparison and the exhausted budget/authorization must be carried into the conclusion as limitations rather than silently absorbed into a clean refutation.
```

### postC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
1. Wrong window queried — an established deviation. The brief specified 2026-06-10 vs 2026-06-11. The quoted, self-consistent execution record (command + the tool's own output header) shows Command 1 actually ran `--day 2026-06-09`, not `--day 2026-06-10`; Command 2 correctly ran `--day 2026-06-11`. So the worker tested 2026-06-09 vs 2026-06-11, a different, wider window that skips 2026-06-10 entirely and cannot isolate the day-over-day change the necessary prediction names.
2. Narrative misrepresentation contradicting that execution record — the "Method and sample" field asserts the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief" states "none." Both statements are false against the worker's own quoted command/output, which is the account of what actually ran.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
The T2 verdict for H2 rests on a test that queried 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 window; the actual change specific to 2026-06-10 (the day of the conversion drop) was never measured, so a spike confined to that day masked by a broader-window comparison cannot be ruled out. No re-collection is available to verify the deviation harmless: the `warehouse` source is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask. This reaches the conclusion as an open possibility for H2 (gateway latency on 2026-06-11) rather than a settled refutation.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis section): "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md (Analysis section): "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md (Analysis section): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "How a faulted return is dispositioned is SKILL.md's Analysis section, and that is the single authority — read the rule there and apply it from there."

REASONING:
The free spot-check required before recording an outcome — comparing the worker's stated method and command against the prediction and against its own return — surfaces a clear fault: the first quoted command queried 2026-06-09, not the briefed 2026-06-10, even though the narrative fields ("Method and sample," "Deviations from brief: none") claim the briefed window was used. Because the quoted command and its own output agree with each other, this is a coherent execution record showing a procedure the brief did not authorize — an established deviation — and the narrative's denial of any deviation does not unsettle that record; it is simply one more thing the return got wrong. That deviation means the necessary prediction (flat/noise-level change specifically between 2026-06-10 and 2026-06-11) was never actually tested — a 2026-06-09-vs-2026-06-11 comparison cannot isolate what happened on 2026-06-10. With no cheap re-run available (metered source, budget spent, no authorization, no user to ask), there is no way to verify the deviation harmless, so per the skill the reconciled outcome must be downgraded to `NON_DISCRIMINATING` rather than accepted as the worker's claimed `CONTRADICTED`. Since the status set is closed to `REFUTED`/`UNRESOLVED` and refutation requires an adequate test of the necessary prediction, and no adequate test of it exists yet, H2 remains `UNRESOLVED`, with the untested 2026-06-10 window recorded as a limitation carried into the conclusion.
```

### postC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window (off-by-one day): the brief specified querying `--day 2026-06-10` and `--day 2026-06-11`. Command 1 in the execution record actually ran `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output header confirms `day=2026-06-09` — a coherent (self-consistent) execution record, but for the wrong day entirely. 2026-06-10 was never queried.
2. The narrative fields contradict that execution record instead of disclosing the deviation: "Method and sample" asserts the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief" states "none" — both deny the day-09-for-day-10 substitution that the quoted command and output plainly show.

(The arithmetic itself — 24.6 -> 25.0 = +1.6% relative — is correct and not a fault; the fault is entirely in which day was collected, not in how the numbers were compared.)

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The preregistered necessary prediction for H2 (flat/rise in gateway p95 specifically between 2026-06-10 and 2026-06-11) was never tested; the return instead evidences a 2026-06-09-to-2026-06-11 comparison, a different window the brief did not authorize.
- 2026-06-10 gateway_p95_ms data has not been observed at all; whether it was flat, elevated, or spiked relative to both neighboring days is unknown.
- No re-verification or re-pull is possible: the warehouse source is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask — so the deviation cannot be verified harmless and the gap cannot be closed.
- The worker's self-reported "Deviations from brief: none" and "Method and sample" narrative should not be trusted as an accurate description of what ran; the quoted commands and tool output are the reliable account.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."

From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."

From SKILL.md (Analysis section): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."

From SKILL.md (Analysis section, free-check description): "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."

From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING:
The free, no-cost check the skill prescribes — checking the command against the method it names and against the brief's window — is exactly what surfaces the fault here: Command 1 queried 2026-06-09, not the briefed 2026-06-10, and the command's own output confirms that day, so the execution record is internally coherent even though it deviates from the brief. The worker's narrative fields ("Method and sample," "Deviations from brief: none") assert the opposite and must yield to the execution record per the skill's ranking rule. Because that deviation was never authorized and the actual test (06-09 vs 06-11) does not test the preregistered 06-10-vs-06-11 comparison, and because the metered budget is exhausted so nothing outside the return can verify the substitution harmless, the established-deviation rule dictates `NON_DISCRIMINATING` rather than treating the worker's claimed `CONTRADICTED` outcome at face value. A `NON_DISCRIMINATING` test cannot refute H2, so under the closed status set H2 stays `UNRESOLVED`; the untested window and the missing 2026-06-10 data are limitations that must travel with any conclusion drawn about H2.
```

### postC2-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value arithmetic error. The worker quotes gateway_p95_ms=24.1 (2026-06-10) and gateway_p95_ms=25.0 (2026-06-11) — both figures appear verbatim in the raw output blocks they cite, and the command, grain, and window all match the brief exactly. But the worker's stated relative change, "+7.9% relative change," does not follow from those raw figures: (25.0-24.1)/24.1 = 3.73%, not 7.9%. Recomputed from the unfaulted raw figures, the true relative change is ~3.7%.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The arithmetic slip is a derived-value error, settled by recomputing from raw figures whose own provenance is unfaulted — the recomputed value (3.7%) sits on the same side of the 10% flat/noise threshold as the worker's erroneous value (7.9%), so the correction does not cross the threshold the prediction named and leaves the outcome and conclusion unchanged. The preregistered Data Validity entry already establishes the test as self-discriminating (detection limit ~0.4% relative, far below both the true ~3.7% observed change and the >20% rise H2 predicts), so no further sensitivity check or re-collection is outstanding. Because the free check did fault the return and that fault was fully resolved by recomputation, this does not fall into the "return you cannot fault on its face" case, so no "unverified worker return" limitation applies here.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim."
From SKILL.md (Analysis): "Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."
From SKILL.md (Conclusion): "an adequate test failing the necessary prediction makes the hypothesis REFUTED, and no number of CONSISTENT outcomes on other predictions changes that."

REASONING: The free, no-cost check (comparing command to method, quoted figures to their cited output, and grain/window to the brief) found the commands, grain, and window all matched the brief, and both cited raw figures (24.1 and 25.0) appear verbatim in the outputs the worker quotes them from — no fault in the raw evidence or its provenance. The one fault is in the worker's own derived arithmetic: 7.9% does not follow from 24.1 -> 25.0 (the correct figure is ~3.7%). Because this is a derived-value error with unfaulted raw inputs, the skill directs recomputing rather than re-running the metered collection, and recording the corrected figure's implied outcome — which stands as the worker's original outcome only if the correction doesn't cross the named threshold. Both 7.9% and 3.7% are comfortably under the 10% "flat" bound, and the Data Validity section already shows the test discriminates cleanly (detection limit ~0.4%, far under any interpretation of the observed change), so nothing about the correction changes the disposition. T2 therefore reconciles to CONTRADICTED — the necessary prediction for H2 (flat p95, <10% relative) held under an adequate test — which by the Conclusion section's precedence rule makes H2 REFUTED, with the arithmetic fault recorded as a fault found (and corrected) rather than an unverified-return limitation, since the free check settled it fully.
```

### postC2-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The worker's raw quoted figures are gateway_p95_ms=24.1 (2026-06-10) and gateway_p95_ms=25.0 (2026-06-11); the delta is +0.9ms. The worker labels this "+7.9% relative change," but 0.9/24.1 = 3.73% relative, not 7.9% — the quoted derived number does not follow from the quoted raw output it cites. Recomputing from the raw figures (whose own provenance is unfaulted — the two commands and their outputs are internally consistent, name the correct days, and match the brief's grain/window) gives 3.73% relative change. This corrected figure sits on the same side of the 10% "flat" threshold as the worker's (wrong) 7.9% figure, so the correction does not cross the boundary the prediction named — both readings clear the <10% flat/refutation bound, and both request/p50 companion fields moved comparably marginally, consistent with a flat day-over-day reading. No other fault: command 1 and command 2 exactly match the brief's two `warehouse --dataset gateway_lat --day <date>` calls, the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match what the brief and the ledger's preregistered prediction specify, and the worker's declared outcome label (CONTRADICTED) is the correct classification for a flat reading against H2's prediction-if-true.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The arithmetic fault was fully settled by recomputing from the return's own unfaulted raw figures (no re-collection needed, so the metered/budget-spent/unauthorized-further-query state noted in the packet never comes into play for T2), the correction leaves the outcome and conclusion unchanged, and the preregistered Data Validity entry already establishes the test's adequacy (census data, ~0.4% detection limit far below the >20% effect H2 predicts, so a flat reading discriminates on its own). This refutation also does not depend on an unidentified exposure–outcome contrast: T2 tests only whether the proposed causal mechanism's own necessary precondition (a material gateway p95 rise) occurred at all, independent of any causal identification of gateway latency's effect on conversion — the case the skill explicitly says can still refute a causal hypothesis.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim. Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test... Independent evidence can still refute it when that evidence falsifies a preregistered necessary prediction without relying on the unidentified contrast — an artifact that inflates the wrong week cannot explain a drop, and that refutation stands."
From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free (zero-cost) check the skill prescribes is exactly recomputing the worker's cited percentage from its own quoted raw numbers, and doing so surfaces a real arithmetic slip (7.9% claimed vs. 3.73% actual). Because this is an error in a derived value rather than a conflict in the execution record itself — the two commands and their outputs are mutually consistent, name the correct days, and match the brief's grain and window — SKILL.md's derived-value rule applies: recompute from the unfaulted raw figures and keep the worker's outcome only if the correction doesn't cross the threshold the prediction named. Both 7.9% and the corrected 3.73% fall well under the 10% flat/refutation bound the ledger preregistered, so the reconciled test outcome stays CONTRADICTED. Given the ledger's Data Validity section already establishes this as an adequate test (a census reading with a detection limit two orders of magnitude below the predicted effect), and given the refutation rests on a necessary precondition of H2's own mechanism rather than on an unidentified causal contrast, H2's necessary prediction failed under an adequate test, so H2 is REFUTED. No unverified-return limitation applies because the fault was fully resolved on the return's own evidence, at no cost, without needing the spent/unauthorized metered budget.
```

### postC2-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) error. The worker reports the gateway_p95_ms relative change as "+7.9% relative change (<10% threshold)," but recomputing from the worker's own quoted raw figures — gateway_p95_ms=24.1 (2026-06-10) and gateway_p95_ms=25.0 (2026-06-11), both byte-verifiable in the quoted command outputs — gives (25.0-24.1)/24.1 ≈ 3.73% relative change, not 7.9%. The raw figures themselves are unfaulted: they appear verbatim in the outputs quoted, the two commands run match the method and the two days (2026-06-10, 2026-06-11) the brief specified, the grain (daily summary) matches what the brief called for, and the worker used 2 of its 3 budgeted calls with no unexplained deviation. The fault is confined to the derived percentage, not the underlying data.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The arithmetic slip is a derived-value error settled by recomputing from raw figures whose own provenance is unfaulted, and the corrected figure (~3.7%) sits on the same side of the named 10%/20% thresholds as the worker's mistaken figure (7.9%) — both are well inside the "flat" (<10%) band and nowhere near the >20% rise H2-true requires — so the correction leaves the reconciled outcome and H2's status unchanged. This is not the "unverified worker return" case (that applies only when the return cannot be faulted or checked on its face); here the fault was found and independently settled by recomputation, so no residual limitation attaches to the conclusion. The preregistered Data Validity entry already establishes the test as adequate (a documented ~0.4% detection limit, far below the predicted >20% rise, so a flat reading discriminates on its own with no further sensitivity check outstanding), so no adequacy limitation is owed either.

GOVERNING SKILL TEXT:

From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."

From SKILL.md (Analysis section): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim. Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."

From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free check (mandated before any other move) means re-deriving the worker's arithmetic from its own quoted output rather than trusting its prose. Doing so shows the worker's "7.9%" is wrong — the correct relative change between the quoted 24.1 and 25.0 figures is ~3.73% — but because both the correct and incorrect percentages fall on the same side of the two named decision thresholds (well under the 10% "flat" line, nowhere near the 20% "rise" line), this is a derived-value slip that SKILL.md says to correct and then use — not one that changes the outcome or that need be carried forward as an unresolved limitation. The commands, days, and grain match the brief exactly, and the raw p95 figures are traceable to the quoted outputs, so nothing else about the return is in doubt. With the necessary prediction (a material, >20% p95 rise) having failed to materialize under a test the preregistered Data Validity section already certified as adequate (detection limit ~0.4%, far finer than the predicted effect), H2's necessary prediction fails under an adequate test, so H2 is REFUTED, and the ledger's Outcome cell for T2 records CONTRADICTED — the worker's own outcome value, preserved because the correction left it and the conclusion unchanged.
```

### postC3-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED — flagged unverified (execution-record conflict; not established). Record in the Outcome cell as "CONTRADICTED (unverified return — see limitation)", not a bare CONTRADICTED and not NON_DISCRIMINATING.

H2 STATUS: UNRESOLVED.

FAULTS FOUND IN THE RETURN: One fault. Command 1 was issued as `warehouse --dataset gateway_lat --day 2026-06-10`, but its quoted output header reads `dataset=gateway_lat day=2026-06-09` — the command's day and the returned output's day disagree. This is a conflict between two execution records (the command actually run vs. the tool's own output), not a narrative slip: the worker's Method-and-sample field claims the query ran "for 2026-06-10 and 2026-06-11," which the output for Command 1 itself contradicts. Because the command and its output name different days, this is the off-by-one-window / conflicting-execution-records case, not a derived-value arithmetic error (the +1.6% figure is correctly computed from the numbers shown) and not an authorized-but-undisclosed deviation (command and output disagree rather than agreeing on some other procedure).

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 result rests on an unverified worker return: Command 1's execution records conflict on which day was actually queried (2026-06-10 per the command, 2026-06-09 per the output), so it cannot be established whether the briefed 06-10-vs-06-11 comparison ran with only the day label misreported, or whether 06-09 was queried instead of 06-10. The warehouse source is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user available to authorize or perform a re-pull, so the conflict cannot be resolved. This limitation bars treating T2's result as established or action-ready, and therefore bars using it to mark H2 REFUTED.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"

From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it. Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready. Do not reach for `NON_DISCRIMINATING` here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."

From SKILL.md (Conclusion section): "`REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

From references/subagent-briefs.md: "Preserve each worker's return unchanged as raw evidence (linked or appended), then record a reconciled outcome in the ledger's test entry; the reconciled outcome is the main agent's call."

REASONING: The free, no-cost check the skill prescribes before any re-pull — checking command against output — surfaces exactly the fault SKILL.md names verbatim as its example: a command and the output beneath it naming different days (Command 1 asked for 2026-06-10, its output is labeled 2026-06-09). That is a conflict between execution records, not a narrative deviation or an arithmetic slip, so it falls under the "execution records themselves conflict" rule rather than the "established deviation" or "derived value" rules. Per that rule, nothing about T2 is established — a benign reading (mislabeled output) is a plausible story, not a verification — and since the warehouse source is metered, the budget is spent, and no user is available in this non-interactive run, the conflict cannot be resolved by re-running. The rule is explicit that this is not `NON_DISCRIMINATING` (the return, if honest, would have discriminated fine); instead the fault is recorded as a limitation and the outcome is recorded as resting on an unverified return. That limitation must reach the conclusion and bars treating the test as adequate, so even though the worker's claimed outcome (CONTRADICTED, i.e. a flat reading that would refute H2) is exactly what H2's necessary prediction requires to fail, it cannot be credited as an adequate test. Per the Conclusion section's closed status rule, `REFUTED` requires an adequate test failing the necessary prediction; absent that, H2 stays `UNRESOLVED`.
```

### postC3-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (unverified — execution-record conflict; not established, not action-ready)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: Command 1 was issued as `warehouse --dataset gateway_lat --day 2026-06-10`, but the raw output beneath it is labeled `day=2026-06-09` — the command and its own returned row name different days. This is an internal conflict in the execution record itself (not a narrative-vs-record mismatch): there is no way to tell, from the return alone, whether the CLI actually queried 2026-06-09 and the day label in the printed row is simply correct-but-wrong-request, or whether it queried 2026-06-10 correctly and the printed `day=` field is the thing that's wrong. Either resolution is consistent with the bytes shown. Compounding this, the worker's own "Deviations from brief: none" and "Method and sample" narrative ("run … against gateway_lat for 2026-06-10 and 2026-06-11") assert the 06-10 query succeeded as briefed, but that attestation cannot be trusted to settle the question — it comes from the same return whose quoted evidence already broke.

LIMITATIONS THAT MUST REACH THE CONCLUSION: T2's comparison rests on an unverified worker return: Command 1's requested day (2026-06-10) and its output's labeled day (2026-06-09) disagree, and the source is metered with the budget spent, so no re-query can resolve which day was actually sampled. This bars treating T2 as an adequate, established test of H2's necessary prediction — the reported +1.6% "flat" comparison cannot be relied on as a 06-10-vs-06-11 comparison specifically. H2's status cannot rest on this test; it must be reported as unresolved pending a re-pull that is not currently authorized.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it."
From SKILL.md (Analysis section): "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md (Analysis section): "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md (Analysis section): "Do not reach for NON_DISCRIMINATING here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Conclusion section): "The status set is closed: REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "How a faulted return is dispositioned is SKILL.md's Analysis section, and that is the single authority — read the rule there and apply it from there."

REASONING: The free, no-cost spot-check the skill prescribes — checking the command against its own quoted output — surfaces exactly the case SKILL.md calls out by name: Command 1 was run for 2026-06-10 but the row printed beneath it is labeled day=2026-06-09. That is an execution-record-vs-execution-record conflict, not a narrative slip, so the "established deviation" and "derived-value error" repair paths don't apply, and NON_DISCRIMINATING is explicitly barred as a landing spot — that status would imply the test ran cleanly but couldn't distinguish predictions, and this test's cleanliness is exactly what's in doubt. The prescribed disposition is to keep the worker's claimed outcome (CONTRADICTED) but record it as resting on an unverified return, carrying that limitation forward so nobody downstream treats the comparison as settled. Since T2 was the cheapest adequate test standing for H2's necessary prediction, and it is no longer an adequate, verified test of that prediction, H2 cannot be marked REFUTED — the closed status set leaves only UNRESOLVED. No re-query is possible: the packet states the warehouse CLI is metered, the budget is fully spent, further queries are unauthorized, and this is a non-interactive run with no user to ask, so the limitation must be reported as-is rather than resolved.
```

### postC3-3

```markdown
RECONCILED OUTCOME FOR T2: UNVERIFIED — the return is disputed by an internal execution-record conflict and is not recorded as CONTRADICTED, CONSISTENT, or NON_DISCRIMINATING. Evidence: Command 1's quoted command is `warehouse --dataset gateway_lat --day 2026-06-10`, but its own returned output header reads `dataset=gateway_lat day=2026-06-09` — the command and the output beneath it name different days. Per SKILL.md, nothing is established by this test; the ledger records the fault as a limitation and treats the outcome as resting on an unverified worker return, not as a verified CONTRADICTED result.

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command/output day mismatch: the Command 1 evidence block names `--day 2026-06-10` but the raw output it presents is headed `day=2026-06-09`. This is precisely the "command and the output beneath it naming different days" conflict SKILL.md calls out — it is not a derived-value arithmetic slip and not a confessed deviation.
2. The worker's narrative fields paper over that conflict rather than disclosing it: "Method and sample" asserts the tool was "run twice, once per day... for 2026-06-10 and 2026-06-11," and "Deviations from brief: none" — both statements are contradicted by the worker's own Command 1 output. Per SKILL.md, a narrative contradicting a coherent execution record does not unsettle the record; here the narrative simply adds a second thing the return got wrong rather than resolving the first.
(Command 2 — day 2026-06-11 — shows no such conflict: its command and output agree.)

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's result rests on an unverified worker return: which day Command 1 actually queried (2026-06-10 as briefed, or 2026-06-09 as the output header states) cannot be determined from the return itself, and the source is metered with the investigation's budget fully spent, so a re-pull to settle it is not available. This bars treating T2's result as established or action-ready for H2.
- Because the necessary-prediction test (flat gateway p95 between 2026-06-10 and 2026-06-11) cannot be confirmed to have actually run over those two named days, H2 cannot be marked REFUTED on this evidence; it must stay UNRESOLVED pending a trustworthy comparison.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it."
From SKILL.md (Analysis section): "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md (Analysis section): "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md (Analysis section): "Do not reach for NON_DISCRIMINATING here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Conclusion section): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "Treat worker reports as claims, not conclusions. How a faulted return is dispositioned is SKILL.md's Analysis section, and that is the single authority — read the rule there and apply it from there. No summary of it belongs here."

REASONING: The free spot-check (comparing the worker's stated command against its own quoted output, per SKILL.md's "does the command implement the method it names" checklist) surfaces exactly the conflict SKILL.md names as its own worked example: Command 1 is labeled for 2026-06-10 but returns a row headed 2026-06-09. That is not a derived-value slip fixable by recomputation, and it is not a confessed deviation the worker owns — the narrative fields flatly assert the 06-10/06-11 comparison was clean, which the return's own execution record contradicts. SKILL.md is explicit that this class of conflict settles nothing (not the worker's claimed CONTRADICTED, not a NON_DISCRIMINATING re-read) and instead must be recorded as a fault/limitation with the outcome resting on an unverified return. With the metered source exhausted and no re-query authorized, that limitation cannot be resolved, so it travels forward and blocks treating T2 as an adequate test of H2's necessary prediction — leaving H2 UNRESOLVED rather than REFUTED.
```

### postC4-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: none — the free check (command vs. method, quoted figures vs. output, grain/window vs. brief) surfaces nothing wrong. Command 1 and Command 2 target `gateway_lat` for 2026-06-10 and 2026-06-11 respectively, at the daily grain the brief specified. The quoted figures (24.1, 25.0) appear verbatim in the JSON blocks cited as their source. The relative-change arithmetic is correct: (25.0-24.1)/24.1 = 3.73%, which the worker rounds to "+3.7%," under the 10% flat threshold. The one deviation — adding `--format json` instead of the brief's default key=value output — is disclosed, and the command/output pair is internally coherent (a JSON request producing valid JSON of the same dataset, day, and fields). It changes only serialization, not the dataset, day, or grain queried, so it does not leave the preregistered prediction inadequately tested; per SKILL.md, that makes it "a deviation to record, not a downgrade to make."
LIMITATIONS THAT MUST REACH THE CONCLUSION: the T2 verdict rests on an unverified worker return. The free check found nothing to fault, but the warehouse CLI is metered, the investigation's budget is fully spent, and no further query is authorized in this non-interactive run, so the raw collection itself was never independently re-run or cross-checked beyond reading the return. This is a limitation to state alongside H2's REFUTED status, not a reason to withhold it.
GOVERNING SKILL TEXT: From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it." Also from SKILL.md (Analysis): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." Also from SKILL.md (Analysis): "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make." From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test." From references/subagent-briefs.md (Reconciliation Duties): "When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
REASONING: The preregistered data-validity note already cleared the sensitivity check for T2 (the tool's ~0.4% detection limit is far below both the predicted 20% rise and the observed 3.7% change, so a flat reading discriminates on its own), so the only remaining reconciliation duty was the free spot-check of W2's return. That check found the command implementing the briefed method, the quoted p95 figures traceable to their own output, correct grain and window, and correct arithmetic; the one deviation (a JSON format flag) is disclosed and harmless to what was actually tested, so it is recorded, not treated as a downgrade trigger. Because re-running the collection to independently verify is unavailable (metered source, budget spent, non-interactive run), full verification cannot be claimed — only the free check was performed — so the outcome is recorded as CONTRADICTED with an explicit limitation that it rests on an unverified return. Since T2 is H2's only, cheapest-adequate test and it is CONTRADICTED (the necessary >20% relative rise did not materialize; the observed 3.7% change meets the refutation condition), H2 is REFUTED under the Conclusion section's rule, with the unverified-return limitation carried forward into the conclusion rather than silently dropped.
```

### postC4-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: none — the free check (command implements the stated method; quoted figures 24.1 and 25.0 appear verbatim in the two JSON outputs quoted; the arithmetic 0.9ms / 24.1ms = 3.7% relative is correct; grain is the daily summary the brief specified; window is 2026-06-10 vs 2026-06-11 as briefed) surfaces no discrepancy. The disclosed deviation (adding `--format json` instead of the brief's default key=value output) is an established deviation — the worker reports it and the execution record (both commands and outputs shown) is coherent with that report — but it changes only output formatting, not dataset, day, grain, or fields, so it leaves the preregistered prediction adequately tested and is a deviation to record, not a downgrade to make.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The verdict for T2 rests on an unverified worker return: the warehouse CLI is metered, the investigation's budget is fully spent, and no further query is authorized, so the figures 24.1→25.0 (and 9.7→9.9) could not be independently re-pulled to confirm them — only checked for internal consistency, which they passed. This is a limitation to state, not a verification to claim, and it must be carried forward alongside H2's REFUTED status.
GOVERNING SKILL TEXT: From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" — and — "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." — and — "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make." From SKILL.md (Conclusion): "an adequate test failing the necessary prediction makes the hypothesis REFUTED, and no number of CONSISTENT outcomes on other predictions changes that". From references/subagent-briefs.md (Reconciliation Duties): "When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
REASONING: The spot-verify free check is free and available regardless of budget, so it was run: the command matches the briefed method, the quoted p95 figures trace to the outputs cited, the arithmetic checks out (3.7% < the 10% flat-change threshold), and the grain/window match the brief and the preregistered data-validity note (complete census, 0.4% detection limit, no further sensitivity check outstanding). No fault was found, and the one disclosed deviation (JSON formatting) is harmless because it left the test's grain, days, and fields untouched. Because the source is metered and the budget is spent, the second tier of verification (re-running the collection) is unavailable, so per SKILL.md and subagent-briefs.md the correct disposition is to accept the worker's CONTRADICTED outcome as the reconciled T2 outcome while recording — as a limitation carried to the conclusion, not a verification — that this rests on an unverified return. Since T2 is an adequate test of H2's necessary prediction (flat p95 <10% relative) and that prediction held (3.7% observed), H2 is REFUTED.
```

### postC4-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: none. Free (no-cost) check performed: the commands run (`warehouse --dataset gateway_lat --day 2026-06-10/11`) implement the briefed method; the quoted gateway_p95_ms figures (24.1, 25.0) appear verbatim in the quoted JSON output; the recomputed relative change (0.9/24.1 = 3.73%, rounds to the worker's "+3.7%") checks out and is correctly compared against the 10% threshold; the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief exactly. One deviation was noted — the worker added `--format json`, which the brief's literal commands omit — but this is a coherent, disclosed formatting deviation only (same dataset, same days, same grain, same fields), and it does not leave the preregistered prediction inadequately tested, so it is recorded as a deviation, not a fault, and does not trigger a NON_DISCRIMINATING downgrade.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The reconciled outcome rests on an unverified worker return. The warehouse CLI is metered, the investigation's budget is fully spent, and no further metered queries are authorized (this is a non-interactive run with no user to ask), so only the free, face-value check was possible — there was no way to re-run the collection to independently confirm the underlying figures. The return could not be faulted on its face, but that is not the same as verification: it must be stated as a limitation on H2's REFUTED status, not represented as confirmed/re-verified evidence.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis section): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md (Analysis section): "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."
From SKILL.md (Conclusion section): "an adequate test failing the necessary prediction makes the hypothesis `REFUTED`, and no number of `CONSISTENT` outcomes on other predictions changes that"
From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief... When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."

REASONING: The packet's preregistered data-validity note establishes the test as self-discriminating (detection limit ~0.4% relative, far below both the 20% "true" threshold and the 10% "false"/refutation threshold), so an adequately-run comparison settles H2 without further sensitivity work. Running the free check — command vs. method, quoted figures vs. output, grain and window vs. brief — surfaced no fault: the arithmetic is correct, the quotes are traceable to the shown output, and the grain/window match the brief. The one deviation (an added `--format json` flag) is disclosed, coherent with the execution record, and immaterial to what is being measured, so it is recorded but does not downgrade the outcome. Since collection is metered and the budget is spent, no re-run is available to go beyond the free check, so per the skill this return is recorded as unfaulted-but-unverified — the outcome stands as the worker reported (CONTRADICTED, i.e., the flat/noise-level change is what the brief defined as the necessary prediction whose observation refutes H2), and the unverified-return limitation must travel with H2's REFUTED status into the conclusion rather than being silently absorbed.
```

## Round 1 (superseded) archived answers

Kept for the record. These arms ran against packets whose null result had no sensitivity evidence,
so their outcomes reflect that entanglement as much as the planted fault; the c4 cells in
particular are contaminated. Do not score against these.

### round1-preA1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING (rests on an unverified/faulted return — see limitations)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window/off-by-one day: the brief instructed `warehouse --dataset gateway_lat --day 2026-06-10` then `--day 2026-06-11`. Command 1 in the return is `warehouse --dataset gateway_lat --day 2026-06-09` (output header reads `day=2026-06-09`), not 2026-06-10. The comparison actually performed is 2026-06-09 vs 2026-06-11 — the necessary prediction names 2026-06-10 vs 2026-06-11 specifically, and no data for 2026-06-10 appears anywhere in the return.
2. The "Method and sample" narrative misstates what was run: it claims the CLI was run "for 2026-06-10 and 2026-06-11," which contradicts the command and output actually shown in the Evidence section.
3. "Deviations from brief: none" is false on the return's own face — using 2026-06-09 instead of the specified 2026-06-10 is a deviation, and it was not disclosed as one.
(The arithmetic itself — 24.6→25.0 = +1.6% — is correctly derived from the output shown, so that part is not separately faulted.)

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as executed does not test the necessary prediction as declared (change between 2026-06-10 and 2026-06-11); it substitutes 2026-06-09 for 2026-06-10, a fault touching the raw evidence/provenance, not a derived-value slip.
- This fault cannot be cleared from inside the return: the same worker whose window was wrong also attested "Deviations from brief: none," so its remaining attestations cannot vouch for the substitution. That 06-09 and 06-11 look similar is a plausible story, not a verification that 06-10 itself was flat — a spike confined to 06-10 that reverted by 06-11 would be invisible to this comparison.
- No re-run or independent source is available to clear it: the `warehouse` CLI is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to ask.
- Consequently H2's necessary prediction has not been adequately tested; the hypothesis cannot be marked REFUTED on this evidence and remains UNRESOLVED pending a future adequate test of the 2026-06-10-vs-06-11 window.

GOVERNING SKILL TEXT: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it." / "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." / "an adequate test failing the necessary prediction makes the hypothesis REFUTED" (Conclusion) — implying an inadequate test cannot do so, leaving the status `UNRESOLVED`.

REASONING: The free check requires comparing the worker's stated method/command against the prediction and against its own return before trusting the outcome — and doing that surfaces an off-by-one window fault: the return's own Command 1 output is stamped `day=2026-06-09`, not the `2026-06-10` the brief specified and the "Method and sample" section claims was used. Because this fault sits in the raw evidence itself (which day was actually queried) rather than in downstream arithmetic, it belongs to the class the skill says cannot be cleared from inside the return — no amount of internal consistency (the 1.6% figure is correctly read off the shown output) can vouch for a day that was never queried. Clearing it needs an outside re-run or independent source, and both are foreclosed here: the source is metered, the budget is spent, and there's no user to authorize a re-pull. Per the skill's disposition for this exact situation, the fault must be recorded as a limitation and the outcome treated as resting on an unverified return rather than accepted at face value. Since the necessary prediction is specifically about 2026-06-10 vs 2026-06-11, and no adequate test of that window exists, T2 cannot support a REFUTED verdict for H2 — it is recorded as NON_DISCRIMINATING, and H2 remains UNRESOLVED.
```

### round1-preA2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED, recorded with an explicit unverified/faulted-return flag — not a clean, trusted CONTRADICTED

H2 STATUS: UNRESOLVED (not REFUTED)

FAULTS FOUND IN THE RETURN:
- Command 1 in the Evidence block queried `--day 2026-06-09`, not `--day 2026-06-10` as the brief instructed ("Run: `warehouse --dataset gateway_lat --day 2026-06-10`") and as H2's necessary prediction specifies ("between 2026-06-10 and 2026-06-11"). This is an off-by-one-day window error — exactly the failure mode the free check is designed to catch ("Is the grain the one the prediction specified, and the window the one the brief set?").
- The worker's own "Method and sample" line asserts the queries ran "for 2026-06-10 and 2026-06-11," which contradicts the command it just quoted (`--day 2026-06-09`). The stated method does not match the command shown.
- "Deviations from brief: none" is false: querying 2026-06-09 instead of the specified 2026-06-10 is a deviation, undisclosed. Because this self-attestation is wrong, the return's other self-attestations (e.g., "no repeat needed... neither output looked malformed") can't be taken on trust either.
- Net effect: no data for 2026-06-10 — the day the necessary prediction names — was ever collected. The reported flat 06-09→06-11 comparison is arithmetically self-consistent (24.6→25.0 ≈ +1.6%, checks out), but it answers a different question than the one preregistered.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's evidence does not cover the preregistered window (2026-06-10 vs 2026-06-11); it covers 2026-06-09 vs 2026-06-11 instead, so it has not actually tested H2's necessary prediction as stated.
- This is a fault touching raw evidence (the command run), not a derived-value slip, so it cannot be cleared from inside the return; no re-run is available (warehouse is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask).
- Therefore the outcome rests on an unverified, faulted return, and H2's status cannot rely on this test as an adequate test of its necessary prediction.

GOVERNING SKILL TEXT:
"Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."

"A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."

"the status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (mandatory before any re-run) caught a real fault: the worker's Command 1 pulled 2026-06-09, not the brief's 2026-06-10, while its own "Method and sample" line falsely claims 2026-06-10 was queried, and its "Deviations from brief: none" line falsely claims no deviation occurred. This is a fault in the raw evidence itself (which day was actually queried), not a downstream arithmetic error, so per the skill it cannot be cleared by anything inside the return — a plausible innocent story ("maybe close enough") is not a verification. Clearing it would require a re-run, an independent source, or a brief-supplied figure for 2026-06-10; none exists, and the warehouse tool is metered with the budget already spent and no user reachable to authorize more collection, so no fix is available. The skill's instruction for this exact situation is to record the fault as a limitation and treat the resulting outcome as resting on an unverified return — not to silently accept it, and not to pay to re-verify it. I therefore keep W2's reported label (CONTRADICTED) in the ledger but flag it as unverified/faulted, and — because Conclusion requires an *adequate* test to REFUTE a necessary prediction, and a test that never actually measured the specified window cannot be called adequate — H2 stays UNRESOLVED rather than REFUTED. The window mismatch and the unresolved verification status both need to travel with the write-up so the eventual report doesn't overstate confidence in the gateway-latency rebuttal.
```

### round1-preA3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING (recorded with the fault stated as a limitation — the test as executed does not test the preregistered 2026-06-10 vs 2026-06-11 window, and the fault cannot be cleared given the metered/budget-exhausted collection status)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong day queried (off-by-one window): the brief instructed `warehouse --dataset gateway_lat --day 2026-06-10` then `--day 2026-06-11`. The Evidence section's Command 1 actually shows `warehouse --dataset gateway_lat --day 2026-06-09` — a different day than the brief specified, and the tool's own output header confirms `day=2026-06-09`. The 2026-06-10 gateway figure was never collected.
2. Self-contradictory attestation: the "Method and sample" field states the CLI was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief: none" — both false against the worker's own quoted Evidence, which shows 06-09 and 06-11. The return's narrative fields contradict its own raw evidence block.
3. Consequently, the reported comparison ("2026-06-10 and 2026-06-11" in the field-by-field write-up) mischaracterizes what was actually compared (06-09 vs 06-11, a two-day span, not the one-day pre/post window the necessary prediction names).

These are faults touching the raw evidence/provenance (the command run does not implement the brief's stated method), not a derived-value arithmetic slip — the arithmetic (24.6→25.0 = +1.6%) is internally consistent with the output shown, so the fault is in which data was pulled, not in computing from it.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's evidence never establishes the 2026-06-10 gateway_p95_ms value; the necessary prediction (flat <10% change between 06-10 and 06-11) is untested by this return.
- The outcome rests on a faulted return that cannot be cleared from inside itself (the worker's own attestations are the thing that broke), and no re-run or independent source is available: the `warehouse` source is metered, the investigation budget is fully spent, no reauthorization exists, and this is a non-interactive run with no user to ask.
- H2 therefore remains untested on its necessary prediction; a correctly-windowed 06-10-vs-06-11 pull would be needed to resolve it, and that collection is not currently authorized.

GOVERNING SKILL TEXT: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it." / "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (comparing the worker's stated command and method against the brief, and against its own quoted evidence) surfaces exactly the "off-by-one window" fault the skill names as the thing this check is meant to catch: Command 1 pulled 2026-06-09, not the 2026-06-10 the brief and the necessary prediction require, and the worker's own "Method and sample" and "Deviations from brief" fields falsely assert the correct days were used — contradicting the Evidence block sitting right beside them. Because this fault sits in the raw evidence/provenance (which day was actually queried), not in a derived computation, it is the class the skill says cannot be cleared from inside the return itself — the worker's other attestations are not independent of the broken one. Clearing it would require a re-run or an independent source, and neither is available: the `warehouse` CLI is metered, the budget is spent, no reauthorization exists, and no user is reachable in this non-interactive run. Since the necessary prediction was never actually tested at its specified window, the test cannot be treated as adequate, so it cannot refute H2 (a CONTRADICTED read here would be status laundering off of a faulted return); the honest Outcome is NON_DISCRIMINATING, carrying the fault and the missing-06-10-data limitation forward, which leaves H2 UNRESOLVED per the closed status set (REFUTED requires an adequate test of the necessary prediction; this one wasn't adequate).
```

### round1-preB1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN: The brief specified comparing gateway_lat for 2026-06-10 vs 2026-06-11. The worker's actual Command 1 queried `--day 2026-06-09` (its own quoted raw output literally reads `day=2026-06-09`), not 2026-06-10 as briefed — so the comparison actually performed is 06-09 vs 06-11, a window the brief never specified. The worker's "Method and sample" field falsely asserts the query ran "for 2026-06-10 and 2026-06-11," contradicting its own quoted Command 1 output. The worker's "Deviations from brief: none" is also false on the return's own face — the day substitution is an undisclosed deviation, proven by the evidence itself rather than merely reported.
LIMITATIONS THAT MUST REACH THE CONCLUSION: T2's verdict rests on a worker return with a proven window fault that cannot be cleared: the gateway_p95_ms comparison that actually ran (06-09 vs 06-11) does not test the briefed contrast (06-10 vs 06-11), so whether gateway latency on 2026-06-10 itself — the incident day — was flat or elevated remains untested. The `warehouse` source is metered and the investigation's budget is fully spent with no user available to authorize a re-pull, so this cannot be re-run or independently checked; the outcome must be reported as resting on an unverified/faulted worker return, and H2 must be reported as untested on its actual necessary-prediction window rather than as refuted.
GOVERNING SKILL TEXT: From SKILL.md: "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification." From SKILL.md: "For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless." From references/subagent-briefs.md: "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied." From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
REASONING: The free check (comparing the worker's stated method and quoted command against the brief and against the return's own numbers) surfaces a real fault: the raw evidence shows Command 1 queried 2026-06-09, not the briefed 2026-06-10, so the actual test compares the wrong pair of days even though the worker's prose claims otherwise and denies any deviation. This is a fault in the raw evidence/provenance itself (wrong window queried), not a derived-value arithmetic slip, so it can only be cleared by evidence from outside the return — a re-run, an independent source, or a figure the brief supplied. None is available: the warehouse CLI is metered, the budget is spent, and this is a non-interactive run with no one to ask for authorization to re-pull. Per the skill, an established deviation (proven by the evidence itself) that cannot be verified harmless downgrades the reconciled outcome to NON_DISCRIMINATING, and that unresolved fault must be carried into the conclusion as a limitation rather than silently absorbed. Because no adequate test has yet failed H2's necessary prediction (flat p95 between the actual 06-10/06-11 window), H2 remains UNRESOLVED rather than REFUTED — the worker's contradicted-outcome claim does not survive reconciliation, since it was built on the wrong day's data.
```

### round1-preB2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
- The brief's step 1 specified `warehouse --dataset gateway_lat --day 2026-06-10` (baseline day matching the necessary prediction's stated window, 2026-06-10 vs 2026-06-11). The worker instead ran `warehouse --dataset gateway_lat --day 2026-06-09` — a different day than the brief set. The comparison actually performed (06-09 vs 06-11) is not the comparison the necessary prediction names (06-10 vs 06-11); no data for 2026-06-10 appears anywhere in the return.
- The worker's own "Deviations from brief: none" field is false: the evidence in its own return (the `day=2026-06-09` line) proves a deviation occurred that was never disclosed.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- H2's necessary prediction (flat gateway p95, <10% relative, specifically between 2026-06-10 and 2026-06-11) was never actually tested; the return's +1.6% figure describes 2026-06-09→2026-06-11, a different window, so it cannot stand as evidence for or against the necessary prediction as preregistered.
- No correction is available: the warehouse CLI is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask — so the missing 2026-06-10 data cannot be obtained and the fault cannot be verified harmless from outside the return.
- Consequently, whether payment-gateway latency rose materially into 2026-06-11 remains unknown from this data; H2 is neither supported nor refuted, and any report must not treat T2 as having exercised the preregistered test.

GOVERNING SKILL TEXT:
- From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
- From SKILL.md (Analysis): "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside... For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return."
- From references/subagent-briefs.md (Reconciliation Duties): "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to NON_DISCRIMINATING unless the deviation is verified harmless... A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."
- From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free, no-cost check the skill prescribes before trusting any worker return is exactly what catches this: comparing the brief's specified window (2026-06-10 vs 2026-06-11) against the commands actually shown in the return reveals the worker queried 2026-06-09 instead of 2026-06-10, while its own "Deviations from brief" field falsely claims "none." This is not an ambiguous, unresolvable discrepancy (transcription slip vs. wrong pull) — the return's own text proves the wrong day was queried — so it is an established deviation, and it touches the raw evidence itself (which data was collected), not a downstream arithmetic step. That class of fault can only be cleared with evidence from outside the return, and none is available: the warehouse source is metered, the budget is spent, no re-run is authorized, and there is no user to ask. Per the reconciliation duties, an established deviation that cannot be verified harmless downgrades the reconciled outcome to NON_DISCRIMINATING, so T2 is recorded that way regardless of the worker's self-reported "CONTRADICTED." Since NON_DISCRIMINATING cannot refute a necessary prediction, H2 stays UNRESOLVED, and the missing 2026-06-10 data plus the unverified/uncorrectable nature of the fault must be carried into the conclusion as limitations rather than silently absorbed into a clean verdict.
```

### round1-preB3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window substitution in the raw evidence: the brief specified `warehouse --dataset gateway_lat --day 2026-06-10` as Command 1, but the worker's actual Command 1 (and its quoted output) is for `day=2026-06-09`. The worker never queried 2026-06-10 at all — the day the ledger's necessary prediction names as one endpoint of the comparison.
2. The worker's "Deviations from brief: none" attestation is false — the evidence it quotes (the command line and the output's own `day=` field) proves the deviation happened, so this is not a matter of trusting the worker's self-report; the return contradicts itself.
3. The reported CONTRADICTED outcome and the "+1.6% relative, within flat/noise bound" arithmetic are computed over 2026-06-09 vs 2026-06-11, not the briefed 2026-06-10 vs 2026-06-11 — an off-by-one window, exactly the class of error the free check exists to catch. The 06-10 figure this test needed was never collected.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- No data for 2026-06-10 was ever collected in this test; the necessary prediction for H2 ("flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2") remains untested — T2 as executed does not speak to it.
- The `warehouse` source is metered and the investigation's budget is fully spent, with no authorization for further queries and no user available to ask; a re-run to obtain the correct 2026-06-10 figure, or any outside evidence to check whether the 06-09 substitution happened to be harmless, is not available.
- Because the raw-evidence fault cannot be cleared from outside the return, the reconciled T2 outcome must be downgraded from the worker's claimed CONTRADICTED to NON_DISCRIMINATING, and H2 stays UNRESOLVED pending an adequate test of its stated window.

GOVERNING SKILL TEXT:
From SKILL.md: "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
From SKILL.md: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to `NON_DISCRIMINATING` unless the deviation is verified harmless." and "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."

REASONING: The free, no-cost check the skill prescribes — checking command against method, window, and grain against the brief, and quoted figures against the output they cite — surfaces a real fault here: the worker's Command 1 queried and quotes 2026-06-09, not the briefed 2026-06-10, so the comparison behind the claimed CONTRADICTED outcome never touches the window H2's necessary prediction names, and the worker's own "none" under Deviations from brief is contradicted by its own quoted output. This is a fault in the raw evidence itself (which day was actually queried), not a derived-arithmetic slip, so under both SKILL.md and the subagent-briefs reconciliation duties it can only be cleared by evidence from outside the return — a re-run for 2026-06-10, an independent source, or a figure the brief already supplied. None exists: the warehouse CLI is metered, the investigation's budget is spent, no further queries are authorized, and this is non-interactive with no user to ask. The deviation is therefore established (proven by the evidence) but not verified harmless, so per subagent-briefs.md it downgrades the reconciled T2 outcome to NON_DISCRIMINATING, carrying forward the limitation that the 2026-06-10 figure needed to test H2's necessary prediction was never obtained. With no adequate test of that necessary prediction on record, H2's status under SKILL.md's closed status set (REFUTED or UNRESOLVED, derived only from an adequate test's outcome) is UNRESOLVED.
```

### round1-preC2-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The return states the relative change in gateway_p95_ms is "+0.9ms = +7.9% relative change," but recomputing from the worker's own quoted raw figures (24.1 -> 25.0) gives (25.0-24.1)/24.1 = 0.9/24.1 ≈ 3.73%, not 7.9%. The command matches the method it names (the two `warehouse --dataset gateway_lat --day <date>` calls implement the stated "run day 1, run day 2, compare fields"), the cited figures (24.1, 25.0) appear verbatim in the quoted outputs, and the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief exactly — so the fault sits in the derived percentage, not in the raw evidence or its provenance.
LIMITATIONS THAT MUST REACH THE CONCLUSION: None. The fault is a derived-value error, and recomputing it from the raw quoted p95 figures (whose provenance the free check did not fault) verifies it harmless: the corrected relative change, ~3.73%, is still under the 10% flat/noise threshold the necessary prediction names, so the correction does not change the qualitative result the worker reported. Because the fault was found and cleared by independent recomputation, the "unverified worker return" limitation (reserved for a return you cannot fault on its face, or a raw-evidence fault with no outside evidence to clear it) does not attach here.
GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim."
From SKILL.md: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted."
REASONING: The free check (method-vs-command, quote-vs-output, grain, window) turned up one fault: the worker's stated 7.9% relative change does not follow from its own quoted p95 figures, which actually yield ~3.73%. Because this fault sits in a derived quantity (a percentage computed from the raw numbers) rather than in the raw evidence or its provenance, SKILL.md and the briefs direct clearing it by recomputing from the unfaulted raw figures rather than treating it as an unresolved deviation — and since 3.73% still lands inside the <10% "flat" band the necessary prediction names, the correction leaves the substantive finding unchanged. The reconciled test outcome therefore stays CONTRADICTED (the necessary prediction — flat gateway p95 — held), which under the Conclusion section's closed status set makes H2 REFUTED: its own necessary prediction (a >20% relative rise) failed under an adequate test, and no limitation needs to qualify that because the one fault found was affirmatively cleared rather than left unverified.
```

### round1-preC2-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (H2's if-true prediction of a >20% relative rise in gateway_p95_ms did not materialize; the necessary prediction failed under an adequate test)

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value arithmetic error. The worker reports "gateway_p95_ms 24.1 -> 25.0 = +0.9ms = +7.9% relative change," but 0.9/24.1 = 3.7% relative change, not 7.9% — the worker's own quoted raw figures (24.1 and 25.0, both present verbatim in the two command outputs) do not support the percentage it derived from them. The raw evidence itself is unfaulted: both commands match the method named (`warehouse --dataset gateway_lat --day <date>` for exactly the two brief-specified days), the grain is the daily summary grain the brief called for, and the quoted figures appear in the outputs they are cited from.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The fault is confined to a derived value (a mislabeled percentage), not to the raw evidence or its provenance, so it is clearable from inside the packet by recomputing from the unfaulted raw figures rather than requiring a re-run or independent source. Recomputing 0.9/24.1 gives ~3.7% relative change, which — like the worker's erroneous 7.9% — is still under the 10% flat/noise threshold in the necessary prediction, so the corrected figure does not change the test outcome or the refutation.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim."
From SKILL.md (Conclusion): "an adequate test failing the necessary prediction makes the hypothesis REFUTED, and no number of CONSISTENT outcomes on other predictions changes that."
From references/subagent-briefs.md (Reconciliation Duties): "A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted." and "`NON_DISCRIMINATING` says a test could not discriminate; do not use it to encode distrust of a return that, if honest, discriminated fine — that is what the unverified-return limitation is for."

REASONING: The free check (no cost, done first per SKILL.md) compared the worker's named method and quoted output against the brief and found one fault: a wrong percentage computed from correctly-quoted raw figures. Because the fault sits in a derived value and not in the raw evidence or its provenance, it is clearable in-context by recomputing from those same raw figures — which I did (0.9/24.1 ≈ 3.7%) — rather than needing a re-run of the metered `warehouse` query, consistent with "verifying does not mean paying twice." The recomputed figure still lands well inside the <10% flat/noise bound the necessary prediction specifies as refuting H2, so the reconciled test outcome matches what the worker reported (CONTRADICTED) and the arithmetic slip does not survive as a limitation on the conclusion — it was resolved, not merely excused. Since T2 is an adequate test of H2's declared necessary prediction and that prediction failed (no material rise in gateway latency between the two days), H2 is REFUTED under the Conclusion section's precedence rule, and this is not the unidentified-contrast case the Conclusion section separately warns about — T2 tests the mechanism's own precondition (whether latency rose at all), not a confounded exposure–outcome comparison of conversion outcomes across groups.
```

### round1-preC2-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (H2's "if TRUE" prediction — a >20% relative rise in gateway_p95_ms — failed to materialize; the necessary prediction refuting H2, a flat/<10% relative change, held)

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The worker's "Field-by-field comparison" states the change from gateway_p95_ms=24.1 (2026-06-10) to gateway_p95_ms=25.0 (2026-06-11) is "+7.9% relative change." Recomputing from the same two quoted figures gives (25.0-24.1)/24.1 = 3.73% relative (or 3.6% if 25.0 is used as the denominator instead) — not 7.9%. The raw figures themselves (24.1 and 25.0) are not at fault: both appear verbatim in the command outputs quoted in the return, the commands shown (`warehouse --dataset gateway_lat --day 2026-06-10` / `--day 2026-06-11`) implement exactly the method and window the brief specified, and the grain (gateway_p95_ms, daily) is the grain the prediction named. No other deviation from brief was found.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The arithmetic fault is a derived-value error over unfaulted raw figures, and recomputing from those raw figures (3.6-3.73%) still falls under the 10% flat threshold — the same side of the threshold as the worker's mistaken 7.9%. The fault is therefore verified harmless and does not change the reconciled outcome or H2's status; it does not need to be carried forward as an unresolved limitation.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis section): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is verified harmless by recomputing it from raw figures whose own provenance is unfaulted: the recomputation is evidence independent of the worker's claim."
From references/subagent-briefs.md (Reconciliation Duties): "A derived-value error — bad arithmetic over quoted figures — is cleared by recomputing from raw evidence whose own provenance is unfaulted."
From SKILL.md (Conclusion section): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test."

REASONING: The free check (command matches stated method, quoted numbers trace to the outputs shown, grain and window match the brief) turned up no fault in the raw evidence — only in the worker's own derived percentage. Because that fault sits in a derived value rather than in the raw evidence or its provenance, the skill's rule for that class applies: recompute from the raw figures, which are themselves unfaulted, and treat that recomputation as independent evidence. Doing so (24.1 → 25.0 is ~3.6-3.73% relative, not 7.9%) still lands well inside the <10% "flat" band the brief set as the condition that refutes H2, so the correction changes nothing about which side of the threshold the result falls on. The reconciled outcome therefore stands as the worker reported it (CONTRADICTED), the necessary prediction for H2 (a >20% rise) failed under this adequate test, and per the Conclusion section's closed status set, H2 is REFUTED. No limitation needs to travel forward because the fault was resolved by independent recomputation, not left as an unverified return.
```

### round1-preC3-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED, recorded as resting on an unverified worker return (limitation attached, not cleared).

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: Command 1 was issued as `warehouse --dataset gateway_lat --day 2026-06-10`, but its own output block is headed `dataset=gateway_lat day=2026-06-09` — the day label in the raw output does not match the day the command (and the brief's window) specified. This could be a harmless transcription slip when the worker wrote up the return, or it could mean the tool actually pulled (and the comparison is built on) 2026-06-09 data mislabeled as the 06-10 baseline — a wrong pull / off-by-one window. Nothing in the return or the packet lets me tell these two readings apart.

LIMITATIONS THAT MUST REACH THE CONCLUSION: T2's CONTRADICTED outcome rests on an unverified worker return: the day-label mismatch in Command 1's output cannot be resolved as harmless or substantive, because the source (`warehouse`) is metered, the investigation's budget is fully spent, and no independent source or brief-supplied figure exists to check which day the 24.6ms/9.8ms/41/488210 line actually describes. This limitation bars treating T2's result, and any conclusion drawn from it, as established or action-ready — so H2 cannot be marked REFUTED on this test alone.

GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From references/subagent-briefs.md: "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (SKILL.md's "read the worker's stated method and command... against its own return") surfaces one concrete fault: Command 1's cited day (2026-06-10) and its output's own day label (2026-06-09) disagree. Re-running is unavailable — the warehouse CLI is metered and the budget is spent — and nothing else in the packet can independently confirm which day the figure belongs to, so this is exactly the unresolvable case subagent-briefs.md describes: a fault that "may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart." That class is explicitly "not thereby an established deviation," so it does not trigger the NON_DISCRIMINATING downgrade reserved for proven deviations; instead the worker's reported outcome (CONTRADICTED) stands in the ledger, but carries the unverified-return limitation forward. Because that limitation "bars treating the result as established," T2's CONTRADICTED outcome cannot serve as the "adequate test" SKILL.md's Conclusion section requires to declare a necessary prediction failed, so H2 stays UNRESOLVED rather than REFUTED until the day-10 figure's provenance can be confirmed.
```

### round1-preC3-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED — recorded as resting on an unverified worker return (limitation attached; not an established deviation, so not downgraded to NON_DISCRIMINATING).

H2 STATUS: REFUTED — but carrying forward the unverified-return limitation, which bars treating this REFUTED status as established or action-ready.

FAULTS FOUND IN THE RETURN: Command 1 was issued as `warehouse --dataset gateway_lat --day 2026-06-10`, but its quoted output header reads `day=2026-06-09` — the window in the raw evidence does not match the window the brief set (2026-06-10) or the command that was supposedly run. This is a fault touching the raw evidence/provenance itself, not a derived-value slip: the p95 delta (24.6→25.0, +1.6%) is arithmetically consistent with the two quoted lines, but the identity of the "day 1" data point is thrown into doubt. It could be a transcription slip in the printed header (data really is for 06-10) or a wrong pull (the tool actually queried 06-09), and nothing inside the return distinguishes these.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 verdict (and hence H2's REFUTED status) rests on an unverified worker return: Command 1's labeled day (2026-06-09) does not match the day it was briefed and commanded to fetch (2026-06-10), and — with the warehouse CLI metered, the investigation's budget fully spent, and no re-run or independent source available — this discrepancy cannot be cleared from inside the return. The comparison actually evidenced may be 06-09-vs-06-11 rather than the preregistered 06-10-vs-06-11, though the conclusion (flat/noise-level change) would likely read the same either way. This must be reported as a limitation barring the H2 refutation from being treated as established or action-ready.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis section): "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return... For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
From references/subagent-briefs.md (Reconciliation Duties): "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."

REASONING: Running the free check (no cost, no re-pull) against W2's return surfaces exactly one discrepancy: Command 1 was issued for 2026-06-10 but its output header says day=2026-06-09, so the window doesn't verifiably match the brief. This is a fault in the raw evidence/provenance, not a derived-value arithmetic error (the 1.6% delta computes correctly from the quoted lines), so it cannot be waved away by internal consistency of the rest of the return. With the warehouse CLI metered and the budget spent, no re-run or independent source is available to tell a transcription slip apart from a wrong-day pull. Per subagent-briefs.md, that exact ambiguity is not an "established deviation" (which would force NON_DISCRIMINATING) — instead the recorded outcome stands as CONTRADICTED, and the unverified-return status travels forward as a limitation. Mechanically deriving H2's status from that CONTRADICTED outcome on its necessary prediction yields REFUTED, but the limitation must be stated alongside and explicitly bars presenting that REFUTED status as settled or ready to act on.
```

### round1-preC3-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN: Command 1 was run as `warehouse --dataset gateway_lat --day 2026-06-10`, but its returned output header reads `day=2026-06-09` — the raw evidence is labeled a day earlier than the window the brief and the command both specify. This means the "24.6ms" figure used as the 2026-06-10 anchor may actually be 2026-06-09's value; the field-by-field comparison the worker performed (and the +1.6% conclusion drawn from it) may therefore be comparing 06-09 vs 06-11, not the briefed 06-10 vs 06-11 window. Command 2's command and output day agree (2026-06-11 / day=2026-06-11), so the fault is isolated to Command 1. All quoted figures (24.6, 9.8, 41, 488210, 25.0, 9.9, 44, 497015) do appear in their respective outputs, and the +1.6% arithmetic is correct given the quoted numbers — the fault is in which day those numbers actually belong to, not in the arithmetic performed on them.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 outcome (and, through it, H2's non-refutation) rests on an unverified worker return: Command 1's requested day (2026-06-10) does not match its output's day label (2026-06-09), and this could be either a transcription slip when the return was written up or an actual wrong-day pull by the tool — nothing in the return distinguishes these. No outside evidence is available to resolve it: the `warehouse` source is metered, the investigation's budget is spent, and no re-run or independent source is authorized. This limitation bars treating T2's result as established or action-ready, and must be carried into any reported conclusion about H2.
GOVERNING SKILL TEXT: From SKILL.md (Analysis): "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" — and: "A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return... For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." From SKILL.md (Conclusion): "The status set is closed: REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise." From references/subagent-briefs.md (Reconciliation Duties): "A fault that cannot be resolved either way — a quote that may be a transcription slip or may be a wrong pull, with no outside evidence to tell them apart — is not thereby an established deviation; it follows SKILL.md's unverified-return rule instead: the recorded outcome stands, marked as resting on an unverified worker return, and that limitation must reach the conclusion, where it bars treating the result as established or action-ready."
REASONING: The free check (compare command to output) surfaces exactly the class of fault SKILL.md names — an off-by-one window: Command 1 asked for 2026-06-10 but the returned row is labeled 2026-06-09. Because the discrepancy could equally be a transcription slip in the write-up or a genuinely wrong pull, and nothing in the return or elsewhere distinguishes those two readings, subagent-briefs.md is explicit that this is not an "established deviation" subject to automatic downgrade to NON_DISCRIMINATING — instead the worker's claimed outcome stands as recorded (CONTRADICTED), but flagged as resting on an unverified return. A re-run would resolve it cheaply in principle, but the packet states the source is metered, the budget is spent, and no further queries are authorized, and this is a non-interactive run with no one to ask — so no re-run or independent source can clear the fault, and it must be logged as a limitation rather than resolved. Because the limitation "bars treating the result as established or action-ready," T2 cannot serve as the "adequate test" the Conclusion section requires to mark H2 REFUTED, even though its outcome value is CONTRADICTED (which would otherwise satisfy the refutation condition for H2's necessary prediction). H2 therefore stays UNRESOLVED, with the unverified-return limitation carried forward to any reported conclusion.
```

### round1-preC4-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: none. Free check: the quoted figures (24.1, 25.0 ms p95, and the rest) appear byte-exact in the JSON blocks shown; the command run (`warehouse --dataset gateway_lat --day <date> --format json`) still targets the same dataset and day named in the brief's method, and the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief exactly. The one disclosed deviation — adding `--format json` — only changes serialization, not what was queried, so it implements the brief's stated method and is not a fault. The worker's own arithmetic (0.9/24.1 = +3.7% relative) is also correct.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The observed +3.7% change is a negative/null result (no material rise) being used to refute H2, and SKILL.md requires a sensitivity check before such a result counts as evidence: an interval around the claim's estimand (order-statistic, sign-test, or bootstrap), or, where that doesn't fit, a documented detection limit or a demonstrated known positive. None of these was computed — the return is a bare two-point comparison (one value per day) with no distributional or repeated-sampling basis to bound noise, and no detection limit is stated. The source (`warehouse`) is metered and the investigation's budget is fully spent with no further queries authorized, and this is a non-interactive run, so the check cannot be performed now. Consequently the flat reading cannot yet be treated as established discriminating evidence against H2; report the gateway-latency explanation as not ruled out by this data, and state explicitly that the required sensitivity check on this null result is outstanding and unaffordable under the current budget.

GOVERNING SKILL TEXT:
- SKILL.md (Data): "A negative or null result counts as evidence only after a sensitivity check, and the interval form of that check comes first: compute the interval the data puts around the claim's own estimand — an order-statistic, sign-test, or bootstrap interval at the claim's grain, around the contrast itself when the claim compares two estimated quantities — and read it directly: the value the claim predicts sitting inside the interval means the result is `NON_DISCRIMINATING` no matter what any power simulation reports, and sitting outside it means the null result discriminates."
- SKILL.md (Data): "Where the interval form does not fit the estimand, the check can instead be carried by a documented detection limit smaller than the predicted effect, or by a demonstrated known positive that models the same sampling process as the null it licenses... Otherwise record the outcome as `NON_DISCRIMINATING` with the detection limit stated."
- SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
- SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
- references/subagent-briefs.md (Reconciliation Duties): "`NON_DISCRIMINATING` says a test could not discriminate; do not use it to encode distrust of a return that, if honest, discriminated fine — that is what the unverified-return limitation is for."

REASONING: The free check clears the return on its face — figures are quoted exactly, the command still targets the briefed dataset/day/grain, and the one disclosed deviation (`--format json`) is a serialization choice, not a change in what was measured, so it needs no external re-verification and is not a fault. But clearing the return is not the same as clearing the outcome: the worker's CONTRADICTED label rests on a flat/null result, and SKILL.md gates any negative or null result behind a sensitivity check before it "counts as evidence" — none was run, none can be reconstructed from a single day-pair, and the metered budget forecloses collecting one now. That is a genuine test-adequacy gap, not a defect in the worker's honesty, so `NON_DISCRIMINATING` is the correct label per the "test could not discriminate" standard rather than the separate unverified-return framing. Because the test is not adequate, H2's necessary prediction has not "failed under an adequate test," so H2 remains UNRESOLVED; the missing sensitivity check must be carried into limitations so the conclusion does not treat gateway latency as ruled out.
```

### round1-preC4-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One fault. Worker W2 self-reports, under "Deviations from brief," that it ran `warehouse --dataset gateway_lat --day <date> --format json` for both days instead of the brief's literal commands (`warehouse --dataset gateway_lat --day <date>`, no `--format json`). This is an established deviation — the worker itself reports it, so there is no ambiguity about whether it happened. It touches raw-evidence collection itself (the actual commands run), not a downstream arithmetic step. The rest of the free check is clean: the command still targets the right dataset and days, the quoted p95 figures (24.1 and 25.0) appear verbatim in the quoted JSON blocks, the grain is the daily summary the brief specified, the window is 2026-06-10 vs 2026-06-11 as briefed, and the arithmetic (0.9 / 24.1 ≈ 3.7% relative) is correct. The sole fault is the unauthorized format-flag substitution.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 verdict rests on an unverified worker return. The worker's own justification for the `--format json` substitution ("same dataset, same days, same daily grain, same fields") is an attestation inside the faulted return, not outside evidence, so it cannot clear the fault. No re-run is available (the warehouse CLI is metered and the investigation's budget is fully spent, with further metered queries not authorized), there is no independent source, and the brief supplied no comparison figure. Because harmlessness cannot be verified from outside the return, H2 cannot be treated as refuted on this evidence, and this limitation — that the apparent flat (<10% relative) gateway p95 change rests on an unverified return — must be carried into the conclusion.

GOVERNING SKILL TEXT:
From references/subagent-briefs.md: "An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to `NON_DISCRIMINATING` unless the deviation is verified harmless."
From references/subagent-briefs.md: "A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied."
From references/subagent-briefs.md: "The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification."
From SKILL.md: "A fault touching the raw evidence or its provenance ... cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md: "Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (command vs. method, quote vs. output, grain, window) turns up clean on every point it was designed to catch, but the worker separately and explicitly discloses that it substituted `--format json` for the brief's literal command — an established deviation by the skill's own definition ("one the worker reports"), and one that touches the raw evidence-gathering step rather than a downstream calculation. Because it touches raw evidence/provenance, only outside evidence (re-run, independent source, or a brief-supplied figure) can verify it harmless; the worker's own "same dataset, same days, same grain, same fields" explanation is exactly the "plausible story" both skill files say cannot do that job. With the budget spent and no further metered queries authorized, no such outside evidence exists, so the fault cannot be cleared. Per the reconciliation duties, that leaves the reconciled outcome at `NON_DISCRIMINATING` rather than the worker's claimed `CONTRADICTED`, and per the Conclusion section's closed status set, a test that does not adequately discriminate cannot REFUTE H2 — so H2 stays `UNRESOLVED`, with the unverified-return limitation carried forward so nothing downstream treats the flat-latency reading as established.
```

### round1-preC4-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: Worker W2 self-reported a deviation from the brief: it ran `warehouse --dataset gateway_lat --day <date> --format json` instead of the exact commands the brief specified (`warehouse --dataset gateway_lat --day 2026-06-10` / `--day 2026-06-11`, with no `--format` flag). This is an established deviation because the worker itself disclosed it under "Deviations from brief," not merely a suspicion. The worker's justification for the deviation — "Same dataset, same days, same daily grain, same fields" — is an attestation from inside the same return, not independent evidence; it is the "benign explanation you can construct" the skill says is a plausible story, not a verification. The deviation touches how the raw evidence was produced (the actual command run differs from the one the brief specified), which is a provenance-class fault, not a derived-value arithmetic error, so it cannot be cleared by recomputation from the worker's own quoted figures. No outside evidence is available to clear it: the warehouse CLI is metered, the investigation's budget is fully spent, no further queries are authorized, and this is a non-interactive run with no user to ask. (The arithmetic itself checks out — 24.1→25.0 is +3.7% relative, correctly under the 10% threshold, so there is no separate derived-value fault — but that does not clear the provenance-class deviation.)

LIMITATIONS THAT MUST REACH THE CONCLUSION: T2's outcome rests on an unverified worker return: the format-flag deviation from the briefed command could not be confirmed harmless, and the source is metered with the budget spent and no re-collection authorized. Any statement about H2 must carry this limitation — the flat gateway p95 result cannot be treated as an established or action-ready refutation of H2 until the deviation is verified (e.g., by a future re-run of the exact briefed command, or an independent figure), and H2 must be reported as unresolved rather than refuted on this evidence.

GOVERNING SKILL TEXT: From SKILL.md (Analysis section): "When the free check *does* fault a return, what can clear the fault depends on what it touches. ... A fault touching the raw evidence or its provenance — a command that does not implement its stated method, a quoted output with no source among the commands shown — cannot be cleared from inside the return: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. For that class, harmlessness needs evidence from outside the return — a re-run, an independent source, a figure the brief itself supplied. Without it, record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading." From references/subagent-briefs.md (Reconciliation Duties): "Treat worker reports as claims, not conclusions. An established deviation from brief — one the worker reports, or one the evidence proves happened — downgrades the reconciled outcome to `NON_DISCRIMINATING` unless the deviation is verified harmless. ... A fault in the raw evidence or its provenance needs evidence from outside the faulted return: a re-run, an independent source, or a figure the brief itself supplied. The rest of the return's own attestations cannot clear a fault they sit beside — internal consistency of the surviving fields is a plausible story, not a verification." From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check itself (command implements the named method, quoted figures appear in the cited output, grain and window match the brief) passes cleanly, and the percentage arithmetic is correct. But the worker separately, and explicitly, disclosed a deviation from the literal briefed commands (adding `--format json`), which makes the deviation established regardless of how the free check reads. Per subagent-briefs.md, an established deviation downgrades the reconciled outcome to NON_DISCRIMINATING unless verified harmless, and per SKILL.md, harmlessness for a fault touching the raw evidence's provenance must come from outside the return — a re-run, an independent source, or a figure the brief supplied. None of those is available: the collection is metered, the budget is spent, no further queries are authorized, and there is no user to ask. The worker's own claim that the flag change didn't affect dataset, day, grain, or fields is exactly the kind of internally-sourced reassurance the skill says cannot clear this class of fault. So the reconciled test outcome must be recorded as NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED, carrying the unverified-return limitation forward. Since T2 is H2's cheapest adequate test and its outcome is no longer an adequate refutation (NON_DISCRIMINATING, not a failed necessary prediction under an adequate test), H2 remains UNRESOLVED rather than REFUTED.
```

### round1-postC1A-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window (established deviation): the brief specified the necessary-prediction window as 2026-06-10 vs 2026-06-11. The worker's actual commands and their own outputs — both internally consistent (`--day 2026-06-09` / `day=2026-06-09` and `--day 2026-06-11` / `day=2026-06-11`) — show it queried 2026-06-09 and 2026-06-11, never touching 2026-06-10 at all. This is an off-by-one window error: the execution record is coherent but evidences a procedure the brief did not authorize.
2. Narrative misstates the execution record: "Method and sample" claims the tool was "run twice, once per day, against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief" claims "none." Both are contradicted by the commands and outputs actually shown. Per the skill, the execution record outranks the narrative, so this false narrative does not unsettle the finding above — it is simply one more thing the return got wrong.

No arithmetic fault: the quoted +1.6% relative change is correctly derived from the (wrong-day) figures shown (25.0 - 24.6 = 0.4; 0.4/24.6 ≈ 1.6%), so this is not a derived-value slip to recompute — the fault is in which raw data was pulled, not in the arithmetic on it.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as executed never tested the preregistered 2026-06-10-to-2026-06-11 comparison; gateway_p95_ms for 2026-06-10 itself is unmeasured. A latency spike confined to 06-10 that had receded by 06-11 would be invisible to the 06-09-vs-06-11 comparison the worker actually ran.
- The `warehouse` source is metered, the investigation's budget is fully spent, and no further queries are authorized, so this cannot be corrected inside this investigation — H2 remains untested on its necessary prediction and stays UNRESOLVED for lack of an adequate test, not because the evidence in hand supports it.
- The worker's own "Deviations from brief: none" is unreliable and should not be trusted for any other test this worker returned without independent execution-record verification.

GOVERNING SKILL TEXT: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it." / "An established deviation — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." / "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong." / "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."

REASONING: The free check (comparing the brief's stated method/window against the worker's own quoted commands and outputs) surfaces a fault on its face: the brief's necessary prediction concerns 2026-06-10 vs 2026-06-11, but the commands actually run — corroborated by their own outputs — queried 2026-06-09 and 2026-06-11. This is a coherent execution record showing an unauthorized procedure (an established deviation), not a case of internally conflicting records, since each command agrees with the output beneath it. Because 2026-06-10 was never queried, the test that ran cannot speak to whether gateway p95 was flat specifically between 06-10 and 06-11 — the procedure did not adequately test the preregistered necessary prediction. No re-run is available (metered source, budget spent, no authorization, non-interactive), and there is no outside evidence that the deviation is harmless, so per the skill this forces the reconciled T2 outcome to `NON_DISCRIMINATING` rather than the worker's claimed `CONTRADICTED`. With T2 downgraded, H2's necessary prediction has not failed under any adequate test, so under the closed status set (`REFUTED` / `UNRESOLVED`) H2 stays `UNRESOLVED`, and the window gap must be carried into the conclusion as a stated limitation rather than silently accepting the worker's contradiction.
```

### round1-postC1A-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window fault (off-by-one window): the brief specified `warehouse --dataset gateway_lat --day 2026-06-10` as Command 1, but the return's Command 1 is `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output confirms `day=2026-06-09`. No 2026-06-10 data was ever collected, so the 2026-06-10→2026-06-11 comparison the necessary prediction names was never run — a 2026-06-09→2026-06-11 comparison was substituted for it.
2. Narrative-vs-execution-record contradiction: "Method and sample" asserts the CLI was run "for 2026-06-10 and 2026-06-11," and "Deviations from brief: none" asserts nothing was done differently — both statements are contradicted by the coherent execution record (command 1 and its own output agree on 2026-06-09, not 2026-06-10). The narrative fields mask the actual deviation rather than disclosing it.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The gateway_p95 change actually measured (24.6 -> 25.0, +1.6%) is over 2026-06-09 vs 2026-06-11, not the 2026-06-10 vs 2026-06-11 window the necessary prediction specifies; it cannot be read as evidence for or against that prediction.
- The `warehouse` source is metered and the investigation's budget is fully spent, with no re-pull authorized in this non-interactive run — the 2026-06-10 vs 2026-06-11 comparison remains untested and unrecoverable within this investigation's current authorization.
- H2 is UNRESOLVED, not refuted or supported: the one adequate, undone test (an actual 2026-06-10 vs 2026-06-11 pull) is the specific, available test that could change the answer if budget or authorization is later granted.

GOVERNING SKILL TEXT: "Is the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" / "An established deviation — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome NON_DISCRIMINATING when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." / "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong." / "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what NON_DISCRIMINATING says." / "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (reading the worker's stated commands and their own outputs against the brief and the prediction, at zero cost) surfaces a concrete fault: Command 1's day parameter and its output both say 2026-06-09, not the 2026-06-10 the brief specified and the necessary prediction depends on — an off-by-one window, exactly the class of error this check exists to catch. Because the command and its output agree with each other on this substituted day, the deviation is established directly from the execution record, not merely alleged; the narrative fields claiming "2026-06-10" and "no deviations" are contradicted by that record and do not unsettle it — they are simply one more thing the return got wrong. A 2026-06-09-to-2026-06-11 comparison does not adequately test a prediction specifically anchored to the day immediately preceding the conversion drop (2026-06-10) versus the drop day itself, and nothing outside the return is available to verify the substitution is harmless (the source is metered and the budget is spent, so no re-pull can settle it). Per the skill, an established deviation that leaves the preregistered prediction inadequately tested reconciles to NON_DISCRIMINATING rather than to the worker's claimed CONTRADICTED — this is not distrust of the worker, only a record that the test which actually ran did not test what was necessary. With T2 downgraded to NON_DISCRIMINATING, H2's necessary prediction has not failed under an adequate test, so per the Conclusion section's closed status set, H2 remains UNRESOLVED.
```

### round1-postC1A-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window substitution in the execution record: the brief and the preregistered prediction both name the window 2026-06-10 vs 2026-06-11, but Command 1 actually run was `warehouse --dataset gateway_lat --day 2026-06-09` (output confirms `day=2026-06-09`), not `--day 2026-06-10`. The comparison actually performed is 2026-06-09 vs 2026-06-11 — 2026-06-10 was never queried at all.
2. Narrative/execution-record conflict: the "Method and sample" field asserts the CLI was run "for 2026-06-10 and 2026-06-11," which contradicts the commands and outputs shown in the Evidence section (2026-06-09, not 2026-06-10). Per the skill, the execution record outranks the narrative, so the narrative is simply wrong here.
3. False "Deviations from brief: none": using 2026-06-09 in place of the briefed 2026-06-10 is an unreported deviation from the brief's explicit instructions (step 1 said `--day 2026-06-10`).

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The preregistered prediction for H2 (flat/noise-level gateway p95 specifically between 2026-06-10 and 2026-06-11) has not actually been tested; the data collected instead bears on a different, unbriefed window (2026-06-09 vs 2026-06-11). Whether gateway p95 moved materially specifically from 06-10 to 06-11 remains unknown.
- The warehouse CLI is metered, the budget is fully spent, and no re-query is authorized in this non-interactive run, so this gap cannot be closed and no outside evidence can verify the deviation harmless. The verdict rests on an inadequate — not merely unverified — test of the necessary prediction.

GOVERNING SKILL TEXT: "An established deviation — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong." "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it." "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (comparing the worker's stated method and command against the prediction it claims to test, and against its own return) surfaces that the command actually executed queried 2026-06-09, not the brief-mandated 2026-06-10, even though the worker's narrative claims to have compared 06-10 and 06-11. Command and output agree with each other internally (a coherent execution record), so this is an established deviation, not an unresolvable internal conflict — and the skill directs ranking that execution record above the contradicting narrative, and above the false "Deviations: none" claim. Because the necessary prediction specifically names the 06-10-to-06-11 window, a test that silently substitutes 06-09 for 06-10 did not adequately test it, and no outside evidence is available (or collectable, given the spent budget and no authorization) to show the substitution was harmless. The skill's rule for exactly this situation forces the reconciled outcome to NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED. Since a NON_DISCRIMINATING outcome is not an adequate test failing the necessary prediction, H2 cannot be REFUTED on this evidence, so it stays UNRESOLVED — and the gap (06-10 never queried) must be carried into the conclusion as a stated limitation rather than silently absorbed.
```

### round1-postC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window/day mismatch — the brief's step 1 said `Run: warehouse --dataset gateway_lat --day 2026-06-10`, but the worker's Command 1 as executed was `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output header confirms `day=2026-06-09`. The briefed baseline day (2026-06-10) was never queried at all; the return only contains 2026-06-09 and 2026-06-11 data.
2. Narrative contradicts the execution record — "Method and sample" states the CLI was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief: none" asserts no departure occurred. Both claims are false against the coherent command+output pair (Command 1's command and its own output agree with each other on 2026-06-09, so that pair is the established fact of what ran). This is a fault in the narrative, not a reason to doubt the execution record.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The preregistered necessary prediction ("flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2") was never actually tested — the worker substituted 2026-06-09 for the briefed 2026-06-10 baseline, an unauthorized procedure change, so the specific day-over-day contrast the hypothesis needed checked is untested. No outside evidence can verify this substitution is harmless: the `warehouse` CLI is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to ask, so a corrective re-pull of 2026-06-10 is not authorized. This limitation — H2's necessary prediction remains untested, not merely unconfirmed — must be carried into the conclusion; H2 cannot be reported as REFUTED, and the report must not treat T2 as having adequately discriminated H2.

GOVERNING SKILL TEXT:
- From SKILL.md (Analysis): "An established deviation — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
- From SKILL.md (Analysis): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
- From SKILL.md (Analysis): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong."
- From SKILL.md (Analysis): "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
- From SKILL.md (Conclusion): "`REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
- From references/subagent-briefs.md (Reconciliation Duties): "a derived-value slip is recomputed and the corrected figure's outcome recorded, an established deviation that leaves the preregistered prediction untested becomes `NON_DISCRIMINATING`, and a fault the execution records cannot settle leaves the outcome standing as an unverified return whose limitation must reach the conclusion."

REASONING: The free check the skill prescribes — comparing the worker's stated method and command against the brief and against its own return — surfaces a real fault: the brief called for 2026-06-10 vs 2026-06-11, but the actual command executed (and its own matching output) queried 2026-06-09, not 2026-06-10. That command/output pair is internally coherent (they agree with each other), so this is a single, established, unauthorized deviation from the brief, not a case where the execution records themselves conflict. The worker's Method-and-sample and Deviations-from-brief narrative falsely claims the briefed days were used; per the skill, that narrative does not unsettle the execution record, it is simply another thing the return got wrong. Because the procedure actually run substituted a different baseline day than the one the necessary prediction was anchored to, it did not adequately test that prediction, and no outside evidence (a re-pull, an independent source) is available to certify the substitution harmless — the warehouse CLI is metered, the budget is spent, and no user is present to authorize more collection. Per the skill's explicit rule for this situation, the reconciled outcome is NON_DISCRIMINATING, not CONTRADICTED as the worker labeled it. Since T2 was H2's cheapest adequate test and no adequate test has failed H2's necessary prediction, H2 remains UNRESOLVED, and the untested-window limitation must be carried forward into the conclusion rather than silently absorbed into a REFUTED verdict.
```

### round1-postC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Off-by-one window: the brief specified `warehouse --dataset gateway_lat --day 2026-06-10` as the baseline query, but the worker's Command 1 actually ran `--day 2026-06-09`, and the tool's own output header confirms it (`day=2026-06-09`). Command and output agree with each other — this is a coherent execution record, not a garbled one — but that procedure was never authorized by the brief. The comparison the worker actually performed is 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11.
2. The narrative fields contradict that established execution record: "Deviations from brief" says "none," and "Method and sample" asserts the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11" — both false, per the return's own quoted command and output. The 24.6→25.0 (+1.6%) arithmetic itself is correct given the (wrong) inputs, so this is not a derived-value slip; the fault is entirely in which day was queried, compounded by a narrative that misrepresents it.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The preregistered necessary prediction for H2 (flat/rising gateway p95 specifically between 2026-06-10 and 2026-06-11) has not actually been tested; the only data collected substitutes 2026-06-09 for the baseline day, and no evidence in or outside the return establishes that 2026-06-09 stands in for 2026-06-10 (e.g., no data showing the two days are equivalent).
- No re-query is available to correct this: the `warehouse` source is metered, the investigation's budget is fully spent, further queries are not authorized, and this is a non-interactive run with no user to ask — so this limitation must be reported as an open gap, not silently resolved.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "An error in a **derived value** ... is settled by recomputing it from raw figures whose own provenance is unfaulted" — ruled out here because the 24.6→25.0 arithmetic is correct; the fault is in which day was queried, not in the delta computed from it.
From SKILL.md (Analysis section): "An **established deviation** — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong."
From SKILL.md (Analysis section): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From references/subagent-briefs.md (Reconciliation Duties): "check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."
From SKILL.md (Conclusion section): "`REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free spot-check (comparing the worker's quoted commands/output against the brief) surfaces a real fault at no cost: Command 1 queried 2026-06-09, not the briefed 2026-06-10, and the command/output pair agree with each other on that fact, so this is an established deviation rather than an internal contradiction. The worker's narrative fields ("Deviations: none," and a Method description claiming 2026-06-10 was queried) are simply wrong and do not get to override that execution record. Because the necessary prediction for H2 is specifically about the 2026-06-10→2026-06-11 change, and no data on 2026-06-10 was actually collected, the procedure that ran did not adequately test that prediction, and nothing outside the return shows the substitution is harmless. Per SKILL.md, that makes the reconciled T2 outcome `NON_DISCRIMINATING` rather than the worker's claimed `CONTRADICTED`. With T2 downgraded, H2's necessary prediction has not failed under an adequate test, so H2 stays `UNRESOLVED`. Re-running the query to get the correct day is the obvious fix, but the packet states the warehouse CLI is metered, the budget is fully spent, and no further queries are authorized in this non-interactive run — so that gap must be carried forward as a limitation rather than silently patched or assumed away.
```

### round1-postC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Off-by-one window (execution-record fault, not narrative): Command 1 as quoted is `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output header reads `day=2026-06-09` — command and tool output agree with each other, so this is a coherent execution record. The brief specified 2026-06-10 as the first day. The test W2 actually ran therefore compares 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 window. This is exactly the "off-by-one window" failure mode the free check is meant to catch, and the free check (reading the quoted command against the brief's window) surfaces it at no cost.
2. Narrative fields contradict that execution record: "Method and sample" claims the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11," and "Deviations from brief" claims "none." Both are false against the commands actually quoted. Per SKILL.md this doesn't unsettle the execution record — the record stands — but it is a second, independent fault: the worker's self-description misrepresents what it ran.

LIMITATIONS THAT MUST REACH THE CONCLUSION: gateway_p95_ms for 2026-06-10 itself was never queried by this worker; no data on that day exists in the return. H2's necessary prediction is specifically about the change between 2026-06-10 and 2026-06-11, and that window remains untested — the 06-09-vs-06-11 comparison the worker actually ran does not stand in for it, and nothing in the packet supplies outside evidence that 06-09 tracks 06-10 closely enough to make the substitution harmless. The `warehouse` source is metered, the investigation's budget is fully spent, and no further queries are authorized in this non-interactive run, so this gap cannot be closed now — it must be reported as an open item, not silently absorbed into the verdict.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
From SKILL.md (Analysis section): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md (Analysis section): "An established deviation — one the worker reports, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless. A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong. That downgrade records the inadequacy of the test that ran, not distrust of the worker."
From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free spot-check the skill prescribes before trusting any return is to compare the quoted commands and their own output against the brief's window — and doing that here shows Command 1 queried 2026-06-09, not the briefed 2026-06-10, while the worker's Method and Deviations fields both falsely describe the run as covering 2026-06-10. Because the command and its output agree with each other (a coherent execution record) on a window the brief did not authorize, this is an established deviation, not merely an unverified or internally-conflicted return. That deviation did not adequately test the preregistered prediction, which names the 2026-06-10-to-06-11 change specifically, and no outside evidence in the packet shows the 06-09 substitute is harmless — collecting one is explicitly out of scope here. The skill's rule for exactly this situation is to record the reconciled outcome as NON_DISCRIMINATING rather than accept the worker's self-reported CONTRADICTED, and since NON_DISCRIMINATING is not "the necessary prediction failed under an adequate test," H2 stays UNRESOLVED. The untested 2026-06-10 window and the source's exhausted metered budget must both be carried into the conclusion as limitations rather than absorbed into the verdict.
```

### round1-postC2-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: One derived-value arithmetic slip. The return states the relative change in gateway_p95_ms as "+0.9ms = +7.9% relative change," but recomputed from the same return's own quoted raw figures (24.1 -> 25.0 ms), the relative change is (25.0-24.1)/24.1 ≈ +3.7%, not 7.9%. The raw p95 readings themselves (24.1 and 25.0) are unfaulted — both appear verbatim in the quoted command output — so this is a mislabeled/miscalculated percentage on top of good data, not a collection or join error. Everything else checks out on the free check: the two commands implement the method named (one `gateway_lat` query per day), the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief, and 2 of the budgeted 3 calls were used with no unexplained gap.

LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The corrected relative change (≈3.7%) sits on the same side of every threshold in the ledger as the worker's flawed figure (≈7.9%) — both are comfortably under the 10% "flat" bound and nowhere near the 20% "rise" bound the H2-true prediction needed — so the slip does not cross a threshold the prediction named. Per the skill, a derived-value error only changes or taints the outcome when correction crosses that line; here it doesn't, so the reconciled outcome stands unchanged and no downgrade or caveat is required.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
Also from SKILL.md (Analysis section): "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim. Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."
From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return... Re-run the collection when it is cheap, or when that check leaves a doubt its return cannot settle and the budget covers the second charge. When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
From SKILL.md (Conclusion section): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."

REASONING: The free check (mandatory before recording any outcome) surfaces exactly one problem: the worker's quoted 7.9% does not follow from its own quoted p95 figures — the actual relative change is about 3.7%. Because this is an arithmetic slip on a derived quantity, not a doubt about the raw figures or the query itself, the skill's remedy is to recompute from the unfaulted raw numbers already in the return rather than re-running the metered query (which the budget-spent/no-user state forecloses anyway, and which would be paying twice for something the free check already settles). Recomputing gives ≈3.7% relative change, which — like the worker's flawed 7.9% — is well inside the "<10% relative" flat/noise band the ledger's necessary prediction names as the H2-false condition, and nowhere near the 20% rise the H2-true condition needed. Since the correction doesn't carry the figure across any threshold the prediction named, the skill directs recording the outcome the corrected figure implies, which is the same outcome the worker reached: CONTRADICTED. With no established deviation, no conflicting execution records, and an adequate test of H2's necessary prediction (flat p95 change) now confirmed by corrected arithmetic, H2's necessary prediction failed under an adequate test, so H2 is REFUTED. No limitation needs to reach the conclusion beyond noting the corrected percentage in the ledger's evidence trail, since the fault didn't change what the test discriminates.
```

### round1-postC2-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The worker quotes gateway_p95_ms=24.1 (2026-06-10) and gateway_p95_ms=25.0 (2026-06-11), both present verbatim in the command outputs it cites, and the command/method/grain/window all match the brief (daily `gateway_lat` summary, correct two days, field-by-field comparison as instructed). But the relative change it reports, "+7.9% relative change," does not follow from those raw figures: (25.0-24.1)/24.1 = 3.73%, not 7.9%. Recomputing from the unfaulted raw figures gives ~3.73% relative change, still well inside the <10% flat/noise bound the refutation condition names, so the corrected figure implies the same outcome the worker reported.
LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The fault is a derived-value slip, and correcting it does not move the figure across the 10% threshold the necessary prediction names, so per the skill's rule this stays the worker's outcome rather than becoming a footnoted limitation. No established deviation, no conflicting execution records, and no unauthorized re-pull was needed to resolve it (the raw figures already in the return sufficed).
GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "An error in a **derived value** — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim. Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."
From SKILL.md: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: Running the free spot-check first (method/command match the brief, quoted figures appear in the cited output, grain and window are correct) turned up one thing the return got wrong on its face: its own quoted 7.9% doesn't follow from its own quoted 24.1 and 25.0. That's a derived-value error, not an established deviation or a conflict between execution records — the raw figures behind it are unfaulted (they're the tool's own output, both quoted and matching the command that produced them), so the skill says to recompute rather than discount the test. Recomputing gives ~3.73%, which sits on the same side of the 10% threshold as the worker's own 7.9%, so the correction leaves the test's outcome and H2's status exactly where the worker put them: the necessary prediction (a material, >20% rise) failed to materialize under an adequately-executed test, which refutes H2. No re-pull was needed or authorized, and none was warranted — the fault was fully resolved by the free check alone.
```

### round1-postC2-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: One derived-value (arithmetic) fault. The worker reports gateway_p95_ms moving 24.1 → 25.0 and labels that "+0.9ms = +7.9% relative change." The correct relative change from those same two (unfaulted) raw figures is 0.9 / 24.1 = 3.73%, not 7.9% — the quoted percentage does not follow from the quoted raw numbers. No other fault: the commands match the briefed method (one `warehouse --dataset gateway_lat` call per day), the raw figures 24.1/25.0/9.7/9.9/38/44/502774/497015 all appear verbatim in the quoted command outputs, the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief, and there is no established deviation or conflict between the quoted commands and the quoted outputs.
LIMITATIONS THAT MUST REACH THE CONCLUSION: none. The fault was a derived-value slip settled by recomputing from raw figures whose own provenance is unfaulted, which the skill treats as independent evidence rather than an unverified return; the corrected figure (3.73%) sits on the same side of the 10% threshold as the worker's erroneous figure (7.9%), so the correction does not change the outcome and needed no re-collection.
GOVERNING SKILL TEXT:
- SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
- SKILL.md: "An error in a derived value — an arithmetic slip in a delta, a mislabeled percentage — is settled by recomputing it from raw figures whose own provenance is unfaulted, since the recomputation is evidence independent of the worker's claim."
- SKILL.md: "Record the outcome the corrected figure implies: that is the worker's outcome only where the correction leaves it and the conclusion unchanged, and a slip that carries the figure across the threshold the prediction named changes the outcome rather than surviving as a footnote."
- references/subagent-briefs.md: "a derived-value slip is recomputed and the corrected figure's outcome recorded"
- SKILL.md: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
- SKILL.md: "Independent evidence can still refute it when that evidence falsifies a preregistered necessary prediction without relying on the unidentified contrast — an artifact that inflates the wrong week cannot explain a drop, and that refutation stands."
REASONING: The free check (command vs. method, quoted figures vs. output, grain/window vs. brief) turns up exactly one fault: the worker's "+7.9%" is a mislabeled derived percentage — the raw figures it was computed from (24.1 and 25.0) are themselves unfaulted, so per SKILL.md this is settled by recomputing rather than by re-querying the metered source or discounting the return as unverified. Recomputing gives +3.73% relative change, which — like the worker's erroneous +7.9% — still falls below the 10% "flat" bound the brief's refutation condition names, so the correction does not carry the figure across the threshold and the worker's outcome (CONTRADICTED) stands unchanged. H2 is a causal claim ("gateway latency drove the drop"), but this test doesn't need an identified before/after design to refute it: it directly falsifies the mechanism's own necessary precondition (that gateway p95 rose materially), which SKILL.md explicitly allows independent evidence to do without relying on an unidentified exposure–outcome contrast. With the sole preregistered necessary prediction for H2-TRUE (>20% relative rise) failing under this test, and no established deviation or conflicting execution record to downgrade the test to NON_DISCRIMINATING, H2 is REFUTED.
```

### round1-postC3-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (unverified return — see limitation)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command/output day mismatch on Command 1: the worker ran (and quotes) `warehouse --dataset gateway_lat --day 2026-06-10`, but the raw output block beneath it is headed `dataset=gateway_lat day=2026-06-09` — the command asked for 06-10, the returned row says 06-09. This is exactly the brief's window: the prediction and refutation condition both name 2026-06-10 vs 2026-06-11, so a first-day row that is actually 06-09 (if the header is to be trusted) means the comparison actually run was 06-09-vs-06-11, not the briefed 06-10-vs-06-11.
2. The worker's narrative fields are not reliable given fault 1: "Method and sample" asserts the CLI was run "for 2026-06-10 and 2026-06-11," and "Deviations from brief: none" — both contradicted by the worker's own quoted output line, so these attestations cannot be used to wave the fault away.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's outcome rests on an unverified worker return: the command/output conflict means it cannot be established which day's data actually backs the "before" figure (24.6ms), nor can it be verified that no such conflict exists (a re-run is unavailable — the warehouse CLI is metered and the investigation's budget is fully spent, with no authorization for a further pull).
- This bars treating T2 as an adequate/established test of H2's necessary prediction, and bars treating H2's status as action-ready pending reconciliation of the day mismatch.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." … "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready. Do not reach for NON_DISCRIMINATING here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Conclusion section): "The status set is closed: REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free, no-cost check the skill mandates before any re-pull is comparing each command to its own quoted output; doing that here surfaces that Command 1's declared day (2026-06-10) and its output's day header (2026-06-09) disagree — the precise "command and the output beneath it naming different days" example SKILL.md names as a conflicting-execution-record fault, not a mere established deviation (those require command and output to agree on what ran). Because the records conflict, no resolution can be preferred over another from inside the return itself, and the worker's own narrative attestations ("Deviations: none") are worthless as a tiebreaker since the same return's quoting already failed once. A re-run would resolve it cheaply, but it is a second (metered) collection and the packet states the budget is spent and no further queries are authorized — so per the skill the only correct move is to keep the worker's reported outcome in the cell while flagging it as resting on an unverified return, explicitly avoiding NON_DISCRIMINATING (which would misstate this as a power/detection problem rather than a return integrity problem). Because the test cannot be called adequate, H2's necessary-prediction failure is not established, so H2 cannot be marked REFUTED under the closed status set; it stays UNRESOLVED, with the day-mismatch limitation carried into the conclusion so the result is not treated as established or action-ready.
```

### round1-postC3-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED — recorded as resting on an unverified worker return (execution-record conflict unresolved; not treated as an established or action-ready refutation of H2)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Execution-record conflict on Command 1: the command run was `warehouse --dataset gateway_lat --day 2026-06-10`, but the quoted raw output beneath it reads `dataset=gateway_lat day=2026-06-09` — the command and its own output name different days. This is the exact conflict pattern the skill calls out, not a mere derived-value slip, since the discrepancy sits in the tool's own output, not in the worker's arithmetic.
2. False/contradicted attestation: the worker's "Deviations from brief: none" narrative is contradicted by its own execution record (the day-1 command/output mismatch is itself a deviation), so the narrative cannot be trusted to certify the rest of the return as clean.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's verdict rests on an unverified worker return: the free spot-check surfaced a command/output day conflict that neither re-running (metered source, budget spent, no authorization) nor the return itself can settle.
- This limitation bars treating T2 as an adequate, established test of H2's necessary prediction — it is stated as a limitation, not resolved into a verification, however plausible an innocent explanation (e.g., an off-by-one day typo) might be.
- Consequently H2 cannot be marked REFUTED on this test; it remains UNRESOLVED pending a trustworthy re-test of the 2026-06-10 vs 2026-06-11 comparison.

GOVERNING SKILL TEXT:
From SKILL.md: "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it."
From SKILL.md: "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md: "Do not reach for `NON_DISCRIMINATING` here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free, no-cost spot-check (comparing each command against its own quoted output) surfaces a genuine conflict: Command 1 was issued for 2026-06-10 but its output block is labeled day=2026-06-09, so the figures the worker built its 24.6→25.0 comparison from cannot be confirmed to be the 06-10/06-11 contrast the brief and H2's necessary prediction require. This is exactly the "execution records themselves conflict" case in SKILL.md, not a derived-value arithmetic slip (recomputable) and not an authorized deviation (nothing in the return flags or justifies it — indeed the return denies any deviation occurred). Per the skill, such a conflict establishes nothing, and the worker's own narrative attestations (including "Deviations from brief: none") cannot rehabilitate the fault since the same return that produced the mismatch also vouches for its own cleanliness. Because re-running is unavailable (metered source, budget spent, no authorization, no user to ask), the correct disposition is to record the outcome as the worker reported it while flagging it as resting on an unverified return — explicitly not downgrading to NON_DISCRIMINATING, which would misrepresent a trust problem as a power problem. That limitation must propagate to the conclusion: absent an adequate, trustworthy test of the necessary prediction, H2 cannot be marked REFUTED and stays UNRESOLVED.
```

### round1-postC3-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (recorded with an attached limitation flagging it as resting on an unverified return — not treated as established/action-ready)
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN: One fault — the execution record for Command 1 is internally conflicting: the command line shown is `warehouse --dataset gateway_lat --day 2026-06-10`, but the raw output block returned beneath it begins `dataset=gateway_lat day=2026-06-09` — a command and the output beneath it naming different days. The worker's narrative ("Method and sample") then asserts the query ran "for 2026-06-10 and 2026-06-11," doubling down on the day the command claims rather than the day the output actually shows, and "Deviations from brief: none" / "Surprises: none" give no acknowledgment of the mismatch. Nothing else in the return is faulted: Command 2's command and output agree on 2026-06-11, and the +1.6% relative-change arithmetic (24.6 -> 25.0) is correctly derived from the figures quoted.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The Command-1 day conflict cannot be resolved — not by the free check (the return's own narrative doubling down on 06-10 is not independent confirmation, since the same return produced the broken quote) and not by re-collection (the `warehouse` source is metered and the investigation's budget is fully spent, with no authorization for a further query). It is therefore unknown whether the "2026-06-10" figures (p95=24.6) actually describe 2026-06-10 or 2026-06-09, which undermines the day-over-day comparison T2 was built to make. This limitation must be reported alongside H2's conclusion: T2's CONTRADICTED result cannot be treated as an adequate, established test of H2's necessary prediction, and H2's status cannot rest on it being action-ready.
GOVERNING SKILL TEXT: From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." Continuing: "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification. Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready. Do not reach for NON_DISCRIMINATING here — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine." From SKILL.md (Conclusion section): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise." From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."
REASONING: The free spot-check (comparing each command against its own quoted output, per the skill's first-line check) surfaces exactly the conflict the skill names almost verbatim: Command 1's invocation says `--day 2026-06-10` while its own raw output header says `day=2026-06-09`. This is not a derived-value slip (recomputing the percentage from the given figures wouldn't touch it) and not a clean "established deviation" (there is no coherent command-and-output agreement on an unauthorized procedure to point to — the command and its own output disagree with each other). It is the "execution records themselves conflict" case, for which the skill is explicit: nothing is established and nothing is verified, the fault becomes a limitation rather than grounds for a downgrade to NON_DISCRIMINATING, and the worker's stated outcome is recorded as-is but treated as resting on an unverified return. Since re-running the query is unavailable (metered source, exhausted budget, non-interactive run), the only route left is to record CONTRADICTED in the Outcome cell while carrying the fault forward as a limitation. At Conclusion, REFUTED requires an adequate test failing the necessary prediction; with the underlying comparison's date integrity unverified, T2 cannot supply that adequacy, so H2 stays UNRESOLVED rather than REFUTED, and the limitation must travel with the conclusion so the result is never presented as established or action-ready.
```

### round1-postC4-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED

H2 STATUS: REFUTED

FAULTS FOUND IN THE RETURN: none. The free check clears the return: the commands implement the method the brief names (same dataset `gateway_lat`, same two days, daily-grain comparison, "field by field"); the quoted figures (24.1 -> 25.0 for gateway_p95_ms) appear verbatim in the two JSON blocks the worker quotes, and the recomputed relative change, (25.0-24.1)/24.1 ≈ 3.7%, matches the worker's arithmetic; the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief exactly. The one departure — adding `--format json` to both commands instead of the brief's bare invocation — is a disclosed deviation, not a fault: same dataset, same days, same grain, same fields, only the serialization differs, so it does not compromise the test of the preregistered prediction.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The reconciled outcome and H2's REFUTED status rest on an unverified worker return. The `warehouse` source is metered and the investigation's budget is fully spent, so no re-pull is available to independently confirm W2's numbers against the source; the free check establishes only that the return is internally coherent and matches its own stated method, not that the underlying warehouse query itself is correct. This must be stated as a limitation alongside the conclusion.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
From SKILL.md (Analysis): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md (Analysis): "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief... When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."

REASONING: The brief's necessary prediction for H2-TRUE was a >20% relative rise in gateway_p95_ms; its failure is the refutation condition. The free check — the only verification tool available given the metered source and spent budget — found the worker's return internally sound: the commands match the briefed method and dataset/day/grain, the quoted p95 figures appear byte-legible in the cited JSON outputs, and the recomputed 3.7% relative change is correct and falls well inside the <10% "false" band, nowhere near the >20% band needed for H2-TRUE. The only deviation (JSON formatting) is disclosed and does not touch the query's dataset, day, grain, or fields, so per the skill it is recorded, not downgraded. That leaves the reconciled outcome as the worker reported it, CONTRADICTED, and because the necessary prediction failed under what the free check shows to be an adequate test, H2 is REFUTED. Because re-collection was neither cheap nor authorized (metered source, budget spent), and the return could not be faulted on its face, the skill directs recording that the verdict nonetheless rests on an unverified worker return — a limitation carried into the conclusion rather than a reason to change the outcome or invent a NON_DISCRIMINATING call the free check gives no grounds for.
```

### round1-postC4-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: none. The free check clears the return on its own terms: the commands implement the briefed method (same `--dataset gateway_lat`, same two `--day` values, same daily grain); the quoted figures (24.1, 25.0) appear verbatim in the JSON outputs shown beneath them; the worker's arithmetic (24.1→25.0 = +3.7% relative) is correct; and the one disclosed deviation — adding `--format json` — changes serialization only, not the dataset, day, or fields queried, so it is an established, harmless deviation to record, not a downgrade to make.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's result is a negative/null finding relative to H2's predicted rise (observed change sits well under the "false" threshold), and SKILL.md requires a sensitivity check — the interval form first, or a documented detection limit / demonstrated known positive where the interval form doesn't fit — before a negative result counts as evidence. No such check was performed by the worker (the return contains only the two point aggregates and a threshold comparison, no interval, detection limit, or known-positive check), and none can be performed now: the warehouse CLI is metered, the budget is spent, and no further queries are authorized. Per the skill's explicit fallback, this means the outcome must be recorded as NON_DISCRIMINATING with the detection limit stated — and no detection limit can in fact be stated from two single-day aggregate snapshots with no day-to-day baseline variability or request-level distribution data available.
- Independent of that gap, the reported figures were never independently re-queried (the source is metered and the budget is exhausted), so even a satisfied sensitivity check would still leave the verdict resting on an unverified worker return — a limitation the skill requires to be stated rather than treated as verification.

GOVERNING SKILL TEXT:
From SKILL.md (Data section): "A negative or null result counts as evidence only after a sensitivity check, and the interval form of that check comes first: compute the interval the data puts around the claim's own estimand ... and read it directly."
From SKILL.md (Data section): "Where the interval form does not fit the estimand, the check can instead be carried by a documented detection limit smaller than the predicted effect, or by a demonstrated known positive that models the same sampling process as the null it licenses ... Otherwise record the outcome as NON_DISCRIMINATING with the detection limit stated."
From SKILL.md (Analysis section): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md (Conclusion section): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."

REASONING: The free spot-check (command matches method, quoted figures match output, grain/window match the brief) finds no fault in W2's return — the only deviation, an added `--format json` flag, is disclosed and cosmetic, so it does not undermine adequacy. But the worker's return is a negative result (the predicted >20% rise did not appear), and SKILL.md gates every negative/null result on a sensitivity check before it "counts as evidence" — an interval, a documented detection limit, or a known-positive demonstration. None of the three was done, and the metered/exhausted-budget condition means none can be done now, which the skill's own "Otherwise" clause resolves by defaulting the outcome to NON_DISCRIMINATING with the (unstatable, here) detection limit noted. Because T2 is the sole test of H2's necessary prediction and it lands NON_DISCRIMINATING rather than an adequate refutation, H2 cannot be marked REFUTED under the Conclusion section's closed rule and instead stays UNRESOLVED. Both the missing-sensitivity-check gap and the unverified-return limitation must travel into the conclusion rather than being absorbed into a clean "CONTRADICTED → REFUTED" call.
```

### round1-postC4-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN: none. The free check (command implements the stated method; the quoted p95 figures — 24.1 and 25.0 — appear in the quoted JSON outputs they are drawn from; the arithmetic checks out, (25.0-24.1)/24.1 = 3.73%, matching the worker's stated "+3.7%"; the grain (daily) and window (2026-06-10 vs 2026-06-11) match the brief) surfaces no defect on the return's face. The one deviation — adding `--format json` to both commands — is disclosed by the worker, is a coherent execution-record change (same dataset, same days, same grain, same fields, only the serialization differs), and does not alter what was tested, so it is a deviation to record rather than a fault or a downgrade.
LIMITATIONS THAT MUST REACH THE CONCLUSION:
1. No sensitivity check was performed on this negative/null result before it was used to refute H2. The worker (and the brief that drove it) only compared two single-day summary point values against a fixed 10% threshold; no interval was computed around the day-over-day estimand (no raw per-request latencies were collected to bootstrap or order-statistic one), no detection limit was documented, and no known-positive demonstration was run. The source is metered, the investigation's budget is fully spent, and further collection is not authorized, so this check cannot be performed now — it is not merely undone, it is currently unperformable.
2. Separately, because the free check found nothing to fault but no re-run was possible to independently confirm the return, the verdict also rests on an unverified worker return; that must be carried forward as a limitation, not treated as a verification.
GOVERNING SKILL TEXT:
From SKILL.md (Data section): "A negative or null result counts as evidence only after a sensitivity check, and the interval form of that check comes first: compute the interval the data puts around the claim's own estimand — an order-statistic, sign-test, or bootstrap interval at the claim's grain, around the contrast itself when the claim compares two estimated quantities — and read it directly: the value the claim predicts sitting inside the interval means the result is `NON_DISCRIMINATING` no matter what any power simulation reports, and sitting outside it means the null result discriminates."
From SKILL.md (Data section): "Where the interval form does not fit the estimand, the check can instead be carried by a documented detection limit smaller than the predicted effect, or by a demonstrated known positive that models the same sampling process as the null it licenses ... Otherwise record the outcome as `NON_DISCRIMINATING` with the detection limit stated."
From SKILL.md (Analysis section): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md (Analysis section): "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."
From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
REASONING: The worker's return itself is clean on the free check — its one deviation is disclosed and harmless, and its arithmetic and sourcing are internally consistent — so there is nothing here that the fault-classification machinery (derived-value slip / established deviation / unsettled execution record) needs to downgrade on execution grounds. But T2's finding is a negative/null result (p95 barely moved, below the 10% flat threshold) being used to refute H2, and the skill gates that use unconditionally on a sensitivity check — an interval around the estimand first, else a detection limit or known-positive demonstration, else `NON_DISCRIMINATING`. None of the three was done, the raw per-request data needed to construct one was never collected, and the metered budget is spent with no re-pull authorized, so the gate cannot be cleared now. The skill's own fallback for that situation is explicit: record `NON_DISCRIMINATING`. Because the test's outcome is `NON_DISCRIMINATING` rather than an adequate refutation, H2's necessary prediction has not been shown to fail under an adequate test, so per the closed status set H2 stays `UNRESOLVED` rather than `REFUTED`. Both the missing sensitivity check and the inability to independently reverify the return are limitations that must travel with the conclusion, not be silently absorbed into an accepted `CONTRADICTED`/`REFUTED` call.
```

## Round 3 — validation arms for the review-driven wording change

A review of PR #112 proposed stating explicitly that "unverified" is a limitation and not a fourth
Outcome label — the exact drift round 2 measured at 1/3 on c3. Adopting it changes the shipped
wording after round 2's arms had run, so measured-wording results do not transfer and validation
arms are owed before push.

Two cells were rerun against the amended text: c3 (does the sentence fix the drift?) and c1 with
both files (does insisting on closed-set labels wrongly discourage the `NON_DISCRIMINATING`
downgrade where it is correct?). Prompts and packets are byte-identical to round 2's; only the
amended SKILL.md differs.

Amended skill digests, regenerated at write time:

```
f394ce505ed92973f4c85bf0261e302f71c39627b1ff7037eca0ec7f95ccad3d  SKILL.md
ab5382bb88b30f775420258a0006b59512250d4c1e01a83cf8c09a2f70dd8739  references/subagent-briefs.md
```

| Cell | Arm 1 | Arm 2 | Arm 3 | Round 2 | Result |
| --- | --- | --- | --- | --- | --- |
| c3 unresolvable | CONTRADICTED (the worker | CONTRADICTED (worker W2' | CONTRADICTED (the worker | 2/3 | **3/3 — drift fixed** |
| c1 established (+briefs) | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING | 3/3 | **3/3 — no over-correction** |

All three c3 arms keep the worker's own `CONTRADICTED` in the Outcome cell with the limitation
recorded beside it, and two quote the new sentence verbatim. No arm invented an out-of-set label.
c2 and c4 were not rerun: the added sentence sits inside the conflicting-execution-records
paragraph, which neither packet reaches. That is a scoping judgement, not a measurement.

### Round 3 manifests

#### vC1B-1

```
1	2026-07-25T18:23:48.932Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:23:49.533Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:23:50.572Z	Read	ok	<SCRATCH>/r3/vC1B-1/packet.md
4	2026-07-25T18:24:55.109Z	Write	ok	<SCRATCH>/r3/vC1B-1/answer.md
```

#### vC1B-2

```
1	2026-07-25T18:23:54.465Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:23:54.863Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:23:56.322Z	Read	ok	<SCRATCH>/r3/vC1B-2/packet.md
4	2026-07-25T18:25:19.063Z	Write	ok	<SCRATCH>/r3/vC1B-2/answer.md
```

#### vC1B-3

```
1	2026-07-25T18:24:00.179Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:24:00.872Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:24:02.105Z	Read	ok	<SCRATCH>/r3/vC1B-3/packet.md
4	2026-07-25T18:25:38.953Z	Write	ok	<SCRATCH>/r3/vC1B-3/answer.md
```

#### vC3-1

```
1	2026-07-25T18:23:29.640Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:23:30.004Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:23:31.357Z	Read	ok	<SCRATCH>/r3/vC3-1/packet.md
4	2026-07-25T18:24:28.797Z	Write	ok	<SCRATCH>/r3/vC3-1/answer.md
```

#### vC3-2

```
1	2026-07-25T18:23:36.825Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:23:37.574Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:23:38.798Z	Read	ok	<SCRATCH>/r3/vC3-2/packet.md
4	2026-07-25T18:24:31.370Z	Write	ok	<SCRATCH>/r3/vC3-2/answer.md
```

#### vC3-3

```
1	2026-07-25T18:23:41.221Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T18:23:41.576Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T18:23:43.038Z	Read	ok	<SCRATCH>/r3/vC3-3/packet.md
4	2026-07-25T18:25:00.537Z	Write	ok	<SCRATCH>/r3/vC3-3/answer.md
```

### Round 3 archived answers

#### vC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
1. Off-by-one window: the brief required comparing 2026-06-10 vs 2026-06-11. Command 1 as quoted is `warehouse --dataset gateway_lat --day 2026-06-09`, and its own output is headed `day=2026-06-09` — command and output agree with each other, so the executed procedure is established as 2026-06-09 vs 2026-06-11, not the brief's 2026-06-10 vs 2026-06-11. The brief's window (2026-06-10) was never queried at all.
2. Narrative contradicts the coherent execution record: "Deviations from brief: none" and "Method and sample: ... against `gateway_lat` for 2026-06-10 and 2026-06-11" both assert the brief's window was used, which the command/output pair shows is false. Per the skill, this narrative fault doesn't unsettle the execution record — it's simply one more thing the return got wrong.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- The test that actually ran (2026-06-09 vs 2026-06-11) did not adequately test H2's preregistered necessary prediction, which is specifically about the 2026-06-10-to-2026-06-11 transition; the day immediately preceding the conversion drop was never sampled, so a change concentrated in the 06-09→06-10 span could be masked or a change concentrated in 06-10→06-11 could be diluted, and this return cannot speak to either.
- No data for 2026-06-10 exists anywhere in this packet, the `warehouse` source is metered, the investigation's budget is fully spent, and no further collection is authorized in this non-interactive run — so the gap cannot be closed now.
- H2 therefore remains UNRESOLVED rather than refuted or supported; obtaining 2026-06-10 vs 2026-06-11 data is the specific follow-up action needed if/when budget is available, and this should be reported as an open item, not silently dropped.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md (Analysis): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md (Analysis): "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md (Analysis): "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "How a faulted return is dispositioned is SKILL.md's Analysis section, and that is the single authority — read the rule there and apply it from there."

REASONING: The free spot-verification check (comparing the worker's stated method and command against the brief and against its own return) directly surfaces a fault: the "day-before" query was run against 2026-06-09, not the brief's 2026-06-10, even though the quoted arithmetic (24.6→25.0, +1.6%) is faithfully drawn from the (wrong) outputs shown. The command and its output agree with each other, so this is a coherent execution record establishing an unauthorized procedure, not an internal conflict requiring the "unverified return" treatment. Because that procedure — comparing 06-09 to 06-11 — never touches the 06-10-to-06-11 transition the necessary prediction is about, and no outside evidence certifies 06-09 as a harmless stand-in for 06-10, the skill's established-deviation rule requires downgrading the reconciled outcome to `NON_DISCRIMINATING` regardless of the worker's self-reported `CONTRADICTED`. With T2 reconciled as `NON_DISCRIMINATING`, H2's necessary prediction has not failed under an adequate test, so H2 stays `UNRESOLVED` per the closed status set — it is neither refuted nor "best supported," and the untested 06-10 window belongs in limitations as the concrete gap remaining.
```

#### vC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
1. Wrong window queried — Command 1 is `warehouse --dataset gateway_lat --day 2026-06-09`, not the briefed 2026-06-10 (brief step 1: "Run: `warehouse --dataset gateway_lat --day 2026-06-10`"). The comparison actually executed is 06-09 vs 06-11, not the preregistered 06-10 vs 06-11 pair, even though command and its own output agree with each other (day=2026-06-09 in both) — the execution record is internally coherent, it just runs a procedure the brief did not authorize.
2. "Deviations from brief: none" is false — the execution record (the command actually run) shows the day-09 substitution; the narrative denies a deviation the record shows.
3. "Method and sample" narrative also misstates this, claiming the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11," which contradicts the quoted command/output pair for Command 1.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
1. T2 as actually executed did not adequately test H2's preregistered necessary prediction (flat gateway p95 specifically between 2026-06-10 and 2026-06-11): the 06-10 baseline was never queried, so the reconciled outcome is NON_DISCRIMINATING and H2 remains UNRESOLVED rather than REFUTED, despite the worker's own CONTRADICTED call.
2. No 2026-06-10 gateway_lat data exists in the return, and none can be obtained now — the warehouse CLI is metered, the investigation's budget is fully spent, further queries are not authorized, and this is a non-interactive run with no user to ask — so the deviation cannot be verified harmless and the necessary prediction stays untested from this evidence.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md (Analysis section): "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md (Analysis section, the free check): "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? ... That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."
From SKILL.md (Conclusion section): "the status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free check (reading the worker's commands and quoted output against the brief, at no collection cost) surfaces that Command 1 queried 2026-06-09 instead of the briefed baseline day 2026-06-10 — the command and its own output agree with each other, so this is a coherent execution record, but it evidences a procedure (the 09-vs-11 comparison) the brief never authorized. That is an established deviation, and per SKILL.md it downgrades the outcome to NON_DISCRIMINATING because the procedure the record actually shows did not test the preregistered 06-10-vs-06-11 prediction, and nothing outside the return — no re-query is affordable, the warehouse CLI is metered and the budget is spent — verifies that substituting 06-09 for 06-10 was harmless. The worker's narrative fields ("Deviations from brief: none"; "Method and sample" citing 06-10) are additional faults but do not unsettle the coherent execution record; per the skill they rank below it and are simply more things the return got wrong. Because the reconciled test outcome is NON_DISCRIMINATING rather than an adequately-tested refutation, H2's necessary prediction has not failed under an adequate test, so H2 stays UNRESOLVED — the closed status set offers no third option, and NON_DISCRIMINATING never refutes.
```

#### vC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window substitution — the brief set the window as 2026-06-10 vs 2026-06-11, but Command 1 as actually run and quoted is `warehouse --dataset gateway_lat --day 2026-06-09`, with output `day=2026-06-09 gateway_p95_ms=24.6 ...`. Command and output agree with each other (internally coherent), so 2026-06-10 itself was never queried at all — the return tests 2026-06-09 vs 2026-06-11 instead of the briefed 2026-06-10 vs 2026-06-11.
2. Narrative denial/misstatement contradicting the execution record — "Deviations from brief: none" and "Method and sample" ("warehouse CLI run twice ... against `gateway_lat` for 2026-06-10 and 2026-06-11") both assert the briefed days were used, which the quoted commands and outputs (2026-06-09, not 2026-06-10) contradict.

The +1.6% arithmetic itself is not faulted: 24.6 and 25.0 both appear verbatim in the quoted outputs, and (25.0-24.6)/24.6 ≈ 1.6% checks out — the fault is in which days were queried and in the narrative's false description of it, not in the derived percentage.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
The necessary prediction for H2 — flat/rise specifically between 2026-06-10 and 2026-06-11 — was never actually tested; the executed comparison (2026-06-09 vs 2026-06-11) omits 2026-06-10 entirely, so whether gateway p95 moved from 06-10 to 06-11 specifically remains unknown. No correction is available: the warehouse CLI is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to ask, so the window gap cannot be closed and stands as an open limitation on H2 rather than a settled negative.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md: "An established deviation — one the worker reports and its execution record does not contradict, or one a coherent execution record shows, its command and the tool's own output agreeing on a procedure the brief did not authorize — makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md: "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING:
The free spot-check the skill prescribes — command against method, quoted figures against their output, window against the brief — surfaces a real fault: the first command queried 2026-06-09, not the briefed 2026-06-10, and command and output agree with each other on this, so it is a coherent execution record showing a procedure (the wrong day) the brief never authorized, i.e. an established deviation, not an internal conflict needing an "unverified" disposition. The worker's narrative fields ("Deviations from brief: none"; "Method and sample" naming 06-10/06-11) deny or misdescribe that deviation, but the skill is explicit that a narrative contradicting a coherent execution record doesn't unsettle the record — it's just one more fault the return carries. The determinative question is then whether the procedure that actually ran adequately tested H2's necessary prediction, which names the 2026-06-10-to-06-11 window specifically. It does not: 2026-06-10 was never queried, so the flat +1.6% reading (2026-06-09 to 2026-06-11) cannot speak to what happened on the specific day the prediction names — an earlier or later movement inside that omitted day would be invisible to this comparison. No outside evidence verifies the substitution harmless, and no re-query is authorized (metered source, budget spent, no user available), so per the skill this is exactly "an honest query against the wrong window" that "leaves the preregistered prediction untested" — the reconciled outcome downgrades from the worker's claimed CONTRADICTED to NON_DISCRIMINATING. With T2 downgraded, H2 has no adequate test of its necessary prediction, so under the closed status set (REFUTED requires an adequate test failing the necessary prediction; otherwise UNRESOLVED) H2 stays UNRESOLVED, and the untested window is a limitation that must be reported alongside the conclusion rather than silently absorbed into a clean-looking result.
```

#### vC3-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (the worker's own outcome, retained in the Outcome cell) — with a limitation recorded beside it: the verdict rests on an unverified return.

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One fault — the execution records conflict. Command 1 as issued was `warehouse --dataset gateway_lat --day 2026-06-10`, but the output block beneath it is headed `dataset=gateway_lat day=2026-06-09` — the command and its own quoted output name different days. This is not a derived-value slip (nothing to recompute from unfaulted raw figures) and not a confessed/evidenced deviation (the worker's narrative says "Deviations from brief: none," which itself conflicts with what the execution record shows) — it is the case where the command and the output beneath it disagree on which day was actually queried, so no reading of which day's data the 24.6ms figure belongs to is established. Command 2's request (`--day 2026-06-11`) and its output (`day=2026-06-11`) do agree, and the arithmetic on the quoted figures (24.6→25.0 = +1.6%) checks out internally — but that internal consistency can't rehabilitate Command 1, since per the skill the worker's own attestations ("Deviations: none," "no repeat needed since neither output looked malformed") can't clear a fault they sit beside once one quote has already broken.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2/H2 verdict rests on an unverified worker return: whether the "24.6ms" baseline figure actually describes 2026-06-10 (the briefed comparison day) or 2026-06-09 (the day the output itself claims) is unresolved, and the warehouse CLI is metered with the investigation's budget fully spent and no re-query authorized, so this cannot be settled by re-running. This bars treating H2 as established or action-ready on this test alone.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it."
From SKILL.md: "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it. Do not reach for NON_DISCRIMINATING here either — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From references/subagent-briefs.md: "check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The skill directs the free spot-check first — command against method, quoted figures against their own output, grain and window against the brief. Running that check on W2's return surfaces exactly the conflict SKILL.md names as its worked example: Command 1 was issued for 2026-06-10, but its own output block is labeled day=2026-06-09. That is not a derived-value arithmetic error (nothing to recompute) and not a self-consistent-but-unauthorized deviation (the narrative denies any deviation, which is itself part of the conflict) — it is the "execution records themselves conflict" case, where nothing is established because a resolution exists (fault confined to the report) that leaves the briefed collection intact. Per the skill, this is a limitation, not a fourth outcome: the Outcome cell keeps the worker's own CONTRADICTED, with the unverified-return limitation recorded beside it. That limitation is explicit that it "bars treating the result as established or action-ready," so at Conclusion, deriving REFUTED for H2 from a test whose adequacy this fault puts in question is not licensed — H2 stays UNRESOLVED, and the limitation (which day's figure the comparison actually rests on, unresolvable because the metered budget is spent and no re-query is authorized) must be carried into the reported conclusion.
```

#### vC3-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (worker W2's own reported outcome, recorded unchanged, with an "unverified return" limitation noted beside it in the ledger)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One fault — an execution-record conflict, not a derived-value error. Command 1 as issued and quoted is `warehouse --dataset gateway_lat --day 2026-06-10`, but the raw output block beneath it is headed `dataset=gateway_lat day=2026-06-09` — the command and the output beneath it name different days. Command 2's output (`day=2026-06-11`) matches its command, so the conflict is confined to the first pull, but that first pull is exactly the 2026-06-10 baseline the H2 comparison needs. This is not settled by recomputation (it isn't a derived-value arithmetic slip) and it isn't an "established deviation" (the worker's own Deviations field says "none," which itself conflicts with the mismatched header) — it is the two-piece-of-evidence conflict the skill names directly.

LIMITATIONS THAT MUST REACH THE CONCLUSION: The T2 verdict rests on an unverified worker return. It is unknown whether the figures reported as "2026-06-10" (gateway_p95_ms=24.6, etc.) actually describe 2026-06-10 or actually describe 2026-06-09 mislabeled in the report — the command and its own output disagree, and the worker's remaining attestations (its "Deviations: none" and its claim that outputs are exact) cannot clear this because the same return is the source of the conflict. No re-verification is possible: the warehouse CLI is metered, the investigation's budget is spent, and no user is available to authorize a re-pull. This limitation bars treating T2's CONTRADICTED result as established or action-ready, and therefore bars using it to REFUTE H2.

GOVERNING SKILL TEXT: From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." And: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." And: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it." From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief." From SKILL.md (Conclusion section): "an adequate test failing the necessary prediction makes the hypothesis REFUTED" — implying an inadequate/unverified test cannot do so, leaving the hypothesis in the default "UNRESOLVED" bucket ("The status set is closed: REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise.").

REASONING: The free check the skill prescribes before concluding — command versus method versus the worker's own return — surfaces exactly the conflict SKILL.md names as an example: Command 1's stated day (2026-06-10) does not match the day printed in its own output header (2026-06-09). This is not a recomputable arithmetic error (no derived value to recheck against unfaulted raw figures) and it is not a "established deviation" the execution record coherently shows (the worker's Deviations field flatly says "none," contradicting the mismatch rather than explaining it), so neither of those two settle-in-place paths applies. That leaves the "execution records conflict" path: nothing is established, because a mislabeled-but-correct pull and an actually-wrong-day pull are equally consistent with what's on the page, and the worker's assurances can't discriminate between them since the same return that broke is the one making the assurances. With the source metered, the budget spent, and no user reachable, a re-run to settle it is not available, so per the skill the correct disposition is to keep the Outcome cell as the worker's own reported value (CONTRADICTED) but attach the unverified-return limitation, and let that limitation carry forward to block treating the test as an adequate discriminating test at Conclusion time. Since H2 can only be marked REFUTED by an adequate test failing its necessary prediction, and T2 cannot currently be certified adequate, H2 stays UNRESOLVED rather than REFUTED.
```

#### vC3-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (the worker's own reported outcome — recorded as-is per the ledger's Outcome cell, with the fault/limitation below noted beside it, not substituted for it)

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command/output day mismatch: Command 1 was run as `warehouse --dataset gateway_lat --day 2026-06-10`, but its returned output header reads `day=2026-06-09` — a different day than requested. This is a conflict within the execution record itself, not a narrative discrepancy: the command and the output beneath it name different days.
2. Consequence of (1): because the day-06-10 side of the comparison is the exact figure whose provenance is in doubt, the whole 06-10-vs-06-11 comparison the test rests on cannot be confirmed to be at the grain/window the brief specified (2026-06-10 vs 2026-06-11) — it may actually be 06-09 vs 06-11, or a mislabeled-but-correct 06-10 pull. The return gives no way to tell which.
(Command 2's output is internally consistent — requested and labeled 2026-06-11 — and the quoted figures 24.6/9.8/41/488210 and 25.0/9.9/44/497015 do appear verbatim in their respective outputs, so no other fault was found.)

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's verdict rests on an unverified worker return: the day-mismatch in Command 1's execution record cannot be resolved (the `warehouse` source is metered, the investigation's budget is fully spent, no re-pull is authorized, and this is a non-interactive run with no user to ask). This limitation bars treating T2's result as established or action-ready, so H2's conclusion must be reported as unresolved pending a re-verifiable pull of 2026-06-10, not as a settled refutation.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it."
From SKILL.md: "Nor is anything verified: the same worker whose quote broke also attested that its quotes were exact, so the return's remaining attestations cannot clear the fault they sit beside, and a benign explanation you can construct is a plausible story, not a verification."
From SKILL.md: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."
From SKILL.md: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." and "Do not reach for `NON_DISCRIMINATING` here either — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: Running the free spot-check the skill prescribes — command against method, quoted figures against their own output, grain/window against the brief — surfaces that Command 1's requested day (2026-06-10) does not match its own output's day label (2026-06-09). The worker declared no deviations, and command and output disagree rather than coherently agreeing on an authorized substitution, so this is the "execution records themselves conflict" case, not an established deviation and not a derived-value slip. Per SKILL.md that means nothing about T2 is established and nothing about the return is verified, but "unverified" is a limitation to record, not a fourth outcome — so the ledger's Outcome cell keeps the worker's own value, CONTRADICTED. That same limitation, however, is directed to reach the conclusion and explicitly bars treating the result as established or action-ready. Since REFUTED under SKILL.md's closed status set requires an adequate test failing the necessary prediction, and adequacy is exactly what the unresolved day-mismatch calls into question, and the metered/budget-spent/non-interactive constraints foreclose a re-pull to settle it, H2 cannot be marked REFUTED here. It stays UNRESOLVED, with the unverified-return limitation carried into the conclusion rather than the fault being buried in the test row alone.
```

## Round 4 — validation arms for the second review round

A second review round raised two parseability defects in agent-executed guidance: the
established-deviation definition packed its condition into an appositive ("...or one a coherent
execution record shows, its command and the tool's own output agreeing on..."), and the reference
file used "is dispositioned" as a verb. Both were reworded — the definition split into two
sentences, the pointer rephrased — with no intended change of meaning.

The definition sentence is the rule c1 and c4 turn on, so those two cells were rerun. c2 and c3 are
governed by other paragraphs, left untouched by this edit.

Amended skill digests, regenerated at write time:

```
da9cefbcff3d7783f86c8480e3ce476974d5a1649ebd5edf8b9039801550fdef  SKILL.md
d54463a0e8d12f8828dd60b9688ba72f1889431c1104e1e1015eaed199823a94  references/subagent-briefs.md
```

| Cell | Arm 1 | Arm 2 | Arm 3 | Prior | Result |
| --- | --- | --- | --- | --- | --- |
| c1 established (+briefs) | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING | 3/3 | **3/3 — preserved** |
| c4 immaterial | CONTRADICTED (worker W | CONTRADICTED (the work | CONTRADICTED | 3/3 | **3/3 — preserved** |

The rewording changed how the rule reads, not what it does: c1 still downgrades on the established
deviation, c4 still records the disclosed `--format json` deviation without downgrading, and no arm
invented an out-of-set label.

### Round 4 manifests

#### wC1B-1

```
1	2026-07-25T20:57:05.933Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:06.593Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:07.912Z	Read	ok	<SCRATCH>/r4/wC1B-1/packet.md
4	2026-07-25T20:58:12.880Z	Write	ok	<SCRATCH>/r4/wC1B-1/answer.md
```

#### wC1B-2

```
1	2026-07-25T20:57:11.078Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:11.732Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:13.020Z	Read	ok	<SCRATCH>/r4/wC1B-2/packet.md
4	2026-07-25T20:58:19.881Z	Write	ok	<SCRATCH>/r4/wC1B-2/answer.md
```

#### wC1B-3

```
1	2026-07-25T20:57:16.559Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:17.296Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:18.719Z	Read	ok	<SCRATCH>/r4/wC1B-3/packet.md
4	2026-07-25T20:58:43.789Z	Write	ok	<SCRATCH>/r4/wC1B-3/answer.md
```

#### wC4-1

```
1	2026-07-25T20:57:23.406Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:23.746Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:25.094Z	Read	ok	<SCRATCH>/r4/wC4-1/packet.md
4	2026-07-25T20:58:53.085Z	Write	ok	<SCRATCH>/r4/wC4-1/answer.md
```

#### wC4-2

```
1	2026-07-25T20:57:29.238Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:29.607Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:31.013Z	Read	ok	<SCRATCH>/r4/wC4-2/packet.md
4	2026-07-25T20:58:49.964Z	Write	ok	<SCRATCH>/r4/wC4-2/answer.md
```

#### wC4-3

```
1	2026-07-25T20:57:34.880Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T20:57:35.506Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T20:57:36.683Z	Read	ok	<SCRATCH>/r4/wC4-3/packet.md
4	2026-07-25T20:58:47.533Z	Write	ok	<SCRATCH>/r4/wC4-3/answer.md
```

### Round 4 archived answers

#### wC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN: One established deviation. The brief instructed two commands — `warehouse --dataset gateway_lat --day 2026-06-10` and `--day 2026-06-11` — but the worker's Command 1, as actually executed and as shown in its own output (`day=2026-06-09`), queried 2026-06-09, not 2026-06-10. Command and output agree with each other (a coherent execution record), so this is an established deviation, not a mere clerical slip: the worker substituted an unbriefed window (06-09→06-11, a two-day span) for the preregistered one (06-10→06-11). The worker's narrative fields deny or obscure this: "Deviations from brief" says "none," and "Method and sample" asserts the run was "against `gateway_lat` for 2026-06-10 and 2026-06-11" — both contradicted by the command and output the same return quotes. The derived arithmetic itself is correct (0.4/24.6 = 1.6% relative, matching the report), so there is no separate derived-value error to fix by recomputation — the fault is in which window was tested, not in the math applied to it.

LIMITATIONS THAT MUST REACH THE CONCLUSION: (1) T2 as executed tested 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 baseline-to-drop-day comparison H2's necessary prediction names; the correct window has not been tested. (2) The `warehouse` CLI is metered and the investigation's budget is fully spent, so the deviation's harmlessness cannot be verified by re-running against the correct window in this run, and no re-pull is authorized. (3) H2's necessary prediction (flat p95 between 06-10 and 06-11) therefore remains untested pending an adequately-windowed query; the 1.6% figure is evidence about a different, overlapping quantity, not a discriminating test of the stated prediction.

GOVERNING SKILL TEXT: From SKILL.md: "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize." From SKILL.md: "An established deviation makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does." From SKILL.md: "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says." From SKILL.md: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it." From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." From references/subagent-briefs.md: "check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free spot-check the skill requires — comparing the worker's quoted commands/output against the brief's window — surfaces a real fault: Command 1 ran against 2026-06-09, not the briefed 2026-06-10, even though the worker's own Deviations and Method fields claim otherwise. Because the command and its output agree with each other, this is a coherent execution record showing an unbriefed procedure, which SKILL.md classifies as an established deviation regardless of what the narrative fields say. The window mismatch means the necessary prediction named at Plan time — flat p95 specifically between 06-10 and 06-11 — was never actually tested; a 06-09-to-06-11 comparison is a different quantity that could over- or under-state the 06-10→06-11 change. With the warehouse CLI metered and the budget spent, there is no way to verify the substitution is harmless, so per SKILL.md the reconciled outcome must be NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED. A NON_DISCRIMINATING test cannot refute a necessary prediction, so H2 stays UNRESOLVED per the Conclusion section's closed status set, and the window mismatch plus the spent budget must be carried into the conclusion as limitations rather than silently absorbed into a clean "flat, refuted" narrative.
```

#### wC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Wrong window queried — Command 1 in the Evidence section is `warehouse --dataset gateway_lat --day 2026-06-09`, and its output header confirms `day=2026-06-09`. The brief specified `--day 2026-06-10` as the first query. The worker's actual comparison spans 2026-06-09 to 2026-06-11, not the preregistered 2026-06-10 to 2026-06-11.
2. Narrative contradicts the execution record — the "Method and sample" field asserts the CLI was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," which is false against the quoted command in Evidence.
3. Undisclosed deviation — "Deviations from brief: none" denies a deviation that the coherent execution record (command + its own output, both reading 2026-06-09) plainly shows.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2's reconciled outcome rests on a test that substituted 2026-06-09 for the preregistered 2026-06-10 baseline; whether gateway p95 on 2026-06-10 itself was flat relative to 2026-06-11 was never tested.
- The `warehouse` source is metered and the investigation's budget is fully spent (non-interactive run, no user available), so the correct-window query cannot be re-run to verify the substitution was harmless.

GOVERNING SKILL TEXT:
From SKILL.md (Analysis section): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set? That costs nothing and catches what actually goes wrong — a wrong join, a unit error, an off-by-one window, a figure that appears nowhere in the rows behind it."

From SKILL.md (Analysis section): "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize."

From SKILL.md (Analysis section): "An established deviation makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."

From SKILL.md (Analysis section): "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."

From SKILL.md (Conclusion section): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free check (mandated before any re-pull is even considered) compares the worker's stated method against its own quoted evidence, and the two disagree: the brief's window was 2026-06-10 vs 2026-06-11, but Command 1's exact text and its own output both read `day=2026-06-09`. That is a coherent execution record — command and output agree with each other — showing a procedure the brief never authorized, so the deviation is established regardless of the worker's narrative denying it. Because the tested window (06-09 to 06-11) is not the preregistered window (06-10 to 06-11), the procedure that actually ran did not adequately test H2's necessary prediction, which specifically concerns 2026-06-10 to 2026-06-11. No evidence outside the return can verify this substitution is harmless — the warehouse CLI is metered, the budget is spent, and this is a non-interactive run with no user to authorize a re-pull — so the harmless-substitution exception does not apply. The rule therefore requires downgrading the reconciled Outcome cell to `NON_DISCRIMINATING`, not recording the worker's claimed `CONTRADICTED`. Since the necessary prediction was not tested under an adequate procedure, H2 cannot be `REFUTED`; the closed status set leaves it `UNRESOLVED`. The wrong-window fault and the unavailability of a corrective re-pull both belong in the conclusion's limitations, not buried in the ledger alone.
```

#### wC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
1. Window substitution (the fault the free check is meant to catch): the brief instructed `warehouse --dataset gateway_lat --day 2026-06-10` as Command 1. The worker instead ran `warehouse --dataset gateway_lat --day 2026-06-09`, and the tool's own output confirms `day=2026-06-09` — command and output agree with each other, so this is a coherent execution record showing a procedure the brief did not authorize (2026-06-09 substituted for 2026-06-10). The necessary prediction is specifically about the 2026-06-10-to-2026-06-11 transition; a 2026-06-09-to-2026-06-11 comparison never measures the day the brief and the ledger's necessary prediction named, so it cannot establish flatness (or a rise) over the required pair.
2. Narrative contradicts the execution record: the worker's "Deviations from brief: none" field is false. The coherent execution record (command 1's `--day 2026-06-09` and its output's `day=2026-06-09`) shows a deviation the narrative denies.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
1. The gateway-latency comparison for the specific pair the necessary prediction names (2026-06-10 vs 2026-06-11) has not actually been performed; the return substituted 2026-06-09 for 2026-06-10, so H2's necessary prediction remains untested despite the worker's flat/CONTRADICTED framing.
2. No re-query is available to fix this: the warehouse CLI is metered, the investigation's budget is fully spent, further metered queries are not authorized, and this is a non-interactive run with no user to ask — so the correct-window test cannot be obtained now, and the gap is a limitation to report, not a verification to claim.
3. The worker's self-reported "Deviations from brief: none" is unreliable evidence of its own procedure (it denies a deviation its own execution record shows), so its narrative fields should not be trusted without independently checking the execution record.

GOVERNING SKILL TEXT:
From SKILL.md: "Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize."
From SKILL.md: "An established deviation makes the reconciled outcome NON_DISCRIMINATING when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md: "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what NON_DISCRIMINATING says."
From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md: "check the worker's stated method and command against the prediction it was briefed on and against its own return — command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free spot-check (comparing the worker's commands/output against the brief) found that Command 1 queried 2026-06-09, not the brief-specified 2026-06-10, and the tool's own output corroborates that wrong day — a coherent execution record showing an unauthorized substitution, which SKILL.md treats as an established deviation regardless of the worker's "Deviations from brief: none" narrative (the narrative is simply one more thing the return got wrong). Because the ledger's necessary prediction is specifically about the 2026-06-10-to-2026-06-11 gateway p95 change, and that pair was never actually queried, the procedure this record evidences did not adequately test the preregistered prediction — there is no comparison-day data available (metered source, budget spent, non-interactive run) to verify the substitution harmless. Per the established-deviation rule, the reconciled outcome is downgraded to NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED. Since T2 is H2's cheapest adequate test and its only test, and NON_DISCRIMINATING is not an adequate test failing the necessary prediction, H2 cannot be REFUTED; it is UNRESOLVED, with the untested-window gap and the unavailability of further metered queries carried forward as limitations.
```

#### wC4-1

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (worker W2's outcome stands, unchanged, with a limitation recorded beside it — see below)
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: none. The free check clears the return: the commands (`warehouse --dataset gateway_lat --day 2026-06-10`/`--06-11`) implement the briefed method against the briefed dataset and days; the quoted gateway_p95_ms figures (24.1, 25.0) appear verbatim in the JSON output blocks they're cited from; the recomputed relative change, (25.0-24.1)/24.1 ≈ 3.73%, matches the worker's stated 3.7% and sits below the 10% flat/refutation threshold, so there is no derived-value slip; and the grain (daily summary) and window (2026-06-10 vs 2026-06-11) match the brief exactly. The one departure — adding `--format json` to both commands — is self-reported by the worker, is consistent with what the execution record shows (clean JSON rather than default key=value lines), and does not touch the dataset, days, grain, or fields, so it does not impair the test of the necessary prediction. That makes it an established deviation to record, not a fault and not a downgrade.
LIMITATIONS THAT MUST REACH THE CONCLUSION: T2's verdict rests on an unverified worker return. The `warehouse` CLI is metered, the investigation's budget is fully spent, and no further queries are authorized in this non-interactive run, so no re-run of the collection was possible even though the free check found nothing to fault. Per the skill, that combination (metered source, spent budget, a return unfaulted on its face) is itself recorded as resting on an unverified return — a limitation to state, not a verification actually performed — and it should travel with H2's REFUTED status rather than being reported as independently confirmed.
GOVERNING SKILL TEXT:
From SKILL.md (Analysis): "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md (Analysis): "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md (Analysis): "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it. Do not reach for NON_DISCRIMINATING here either — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."
From SKILL.md (Analysis): "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."
From SKILL.md (Conclusion): "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md (Reconciliation Duties): "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding... When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
REASONING: The preregistered data-validity note already established that a flat reading discriminates on its own (detection limit ~0.4% relative, far below both the 20% rise and 10% flat thresholds), so no sensitivity check remained outstanding once the numbers were confirmed. The free check — the only verification step available given the spent, metered budget — found the command, quoted figures, grain, and window all consistent with the brief and with each other, and the one deviation (a format flag) is disclosed and harmless to the test's adequacy. That leaves the worker's own CONTRADICTED outcome standing unmodified, which under the Conclusion rules means the necessary prediction (flat p95, <10% relative) failed and H2 is REFUTED. But because the source is metered and the budget is exhausted, the main agent never independently re-ran the collection — only inspected it — so the skill requires flagging that the verdict rests on an unverified worker return, a limitation that must accompany H2's REFUTED status into the report rather than letting it read as independently confirmed.
```

#### wC4-2

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED (the worker's own outcome, recorded with the limitation below beside it)
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: none. The free check clears the return on every point it checks: the commands implement the briefed method (warehouse queried for gateway_lat on 2026-06-10 and 2026-06-11, the exact window the brief and ledger set); the quoted figures (24.1, 25.0) appear verbatim in the quoted JSON outputs; the grain is the daily summary grain the brief specified; and the relative-change arithmetic is correct (0.9/24.1 = 3.7%, under the 10% flat threshold, so the necessary prediction for H2-TRUE failed to materialize as claimed). The one deviation — adding `--format json` — is reported by the worker and corroborated by a coherent execution record (the commands shown carry the flag, the outputs are valid JSON of the same fields), so it is an established deviation; it changes serialization only, not dataset, day, or grain, so it leaves the preregistered prediction adequately tested and is recorded, not treated as a downgrade.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The verdict rests on an unverified worker return: the warehouse CLI is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to authorize a re-pull, so the free check (which found nothing to fault) could not be followed by an independent re-run to confirm the return beyond its own face. State this as a limitation on H2's REFUTED status, not as a verification achieved.
GOVERNING SKILL TEXT: From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?" Also from SKILL.md: "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." Also from SKILL.md: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it." Also from SKILL.md: "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make." Also from references/subagent-briefs.md: "When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
REASONING: The free check is the whole verification budget left for T2, and it passes on every axis it examines — method, figures, grain, window — leaving no fault to classify and no basis to override the worker's stated CONTRADICTED outcome or to reach for NON_DISCRIMINATING (which would misrepresent a test that discriminated fine as one that couldn't). But passing the free check is not the same as verification: the skill is explicit that when the source is metered, the budget is spent, and no fault surfaces, the correct record is that the verdict rests on an unverified return — a limitation, not a clean bill of health. So T2's ledger Outcome cell records CONTRADICTED with that limitation noted beside it, exactly as the return arrived, and H2's necessary prediction (flat p95 <10% relative) failed under what is otherwise an adequate test, so H2 is REFUTED — with the unverified-return limitation carried forward into the conclusion rather than silently dropped.
```

#### wC4-3

```markdown
RECONCILED OUTCOME FOR T2: CONTRADICTED
H2 STATUS: REFUTED
FAULTS FOUND IN THE RETURN: none. The free check clears the return on every point the skill names: both commands implement the briefed method (same dataset `gateway_lat`, same two days, daily-summary grain); the quoted figures (24.1, 25.0) appear verbatim in the JSON output blocks they are drawn from; the recomputed relative change, (25.0-24.1)/24.1 = 3.73% ≈ "+3.7%", matches the worker's arithmetic; and the grain/window match the brief exactly (daily grain, 2026-06-10 vs 2026-06-11). The one deviation — adding `--format json` to both commands — is self-reported, confirmed by the execution record (the quoted commands themselves show the flag), and changes only output formatting, not dataset/day/grain/fields, so it is an established-but-harmless deviation to record, not a fault and not a downgrade.
LIMITATIONS THAT MUST REACH THE CONCLUSION: The reconciled outcome rests on an unverified worker return. The free check found nothing to fault, but the `warehouse` source is metered and the investigation's budget is fully spent, so no re-run or independent recomputation from raw rows was possible to confirm the returned figures themselves are genuine — only their internal consistency with the brief and with each other was checked.
GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."
From SKILL.md: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it."
From SKILL.md: "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."
From SKILL.md: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md: "When the source is metered and the budget is spent, record that the verdict rests on an unverified return; that is a limitation, not a verification."
REASONING: The free check — the only verification step available, since the warehouse CLI is metered and the budget is spent — turns up nothing wrong: the commands match the briefed method, the quoted p95 figures are present in the JSON they're cited from, the recomputed relative change agrees with the worker's own 3.7%, and grain and window match the brief. The only departure from the brief, the added `--format json` flag, is established by the worker's own commands and is harmless to the test's adequacy. Because the free check clears the return but no re-run or independent confirmation was possible, the skill requires recording the verdict as resting on an unverified return — a limitation, not a fourth outcome — while the Outcome cell keeps the worker's own call, CONTRADICTED. The preregistered data-validity note already established this test's discriminating power (a >20% predicted rise cannot hide inside a ~0.4% detection limit), so the observed 3.7% flat change is an adequate test of H2's necessary prediction (flat p95 refutes H2), and that necessary prediction failed. Per the Conclusion section's closed status set, an adequate test failing the necessary prediction makes the hypothesis REFUTED; the unverified-return limitation travels forward into the conclusion/limitations text but does not create a third status or block deriving REFUTED from the recorded CONTRADICTED outcome.
```

## Round 5 — validation arms after the reference file's bullet promotion

A third review round found four stale cross-references, all created by this PR's own edits: the
deferral sentence was indented as a continuation of the preceding bullet rather than standing as
its own duty; a generator comment and two `scenarios.md` passages still pointed at
`subagent-briefs.md` text this PR deleted, or at a `scenarios.md:641` line number that adding
Scenario 20 had shifted.

Only the first touches a file agents read. The sentence is byte-identical — it was promoted from a
continuation line to its own list item — so the behavioral risk is small but not zero, and the
standing rule here is that a changed agent-read file gets measured rather than reasoned about.
c1 with both files rerun:

```
da9cefbcff3d7783f86c8480e3ce476974d5a1649ebd5edf8b9039801550fdef  SKILL.md
b1b6d497dfcb97b225eeb3ef502de07aee28e69c5d9725984226133ec1d1a1c2  references/subagent-briefs.md
```

| Cell | Arm 1 | Arm 2 | Arm 3 | Prior | Result |
| --- | --- | --- | --- | --- | --- |
| c1 established (+briefs) | NON_DISCRIMINATING | NON_DISCRIMINATING | NON_DISCRIMINATING | 3/3 | **3/3 — unchanged** |

The other three fixes touch `generate.py` comments and `scenarios.md` prose, neither of which any
arm may read, so no cell was rerun for them. The fixture bytes are unchanged — the generator edit
was comment-only, and regenerating reproduces all four packet digests exactly.

### Round 5 manifests

#### xC1B-1

```
1	2026-07-25T21:06:26.872Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T21:06:27.147Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T21:06:28.877Z	Read	ok	<SCRATCH>/r5/xC1B-1/packet.md
4	2026-07-25T21:07:30.778Z	Write	ok	<SCRATCH>/r5/xC1B-1/answer.md
```

#### xC1B-2

```
1	2026-07-25T21:06:32.822Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T21:06:33.184Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T21:06:34.913Z	Read	ok	<SCRATCH>/r5/xC1B-2/packet.md
4	2026-07-25T21:07:37.738Z	Write	ok	<SCRATCH>/r5/xC1B-2/answer.md
```

#### xC1B-3

```
1	2026-07-25T21:06:39.269Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/SKILL.md
2	2026-07-25T21:06:39.608Z	Read	ok	<REPO_ROOT>/hypothesis-driven-analysis/references/subagent-briefs.md
3	2026-07-25T21:06:41.344Z	Read	ok	<SCRATCH>/r5/xC1B-3/packet.md
4	2026-07-25T21:07:48.862Z	Write	ok	<SCRATCH>/r5/xC1B-3/answer.md
```

### Round 5 archived answers

#### xC1B-1

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Window substitution: the brief instructed `warehouse --dataset gateway_lat --day 2026-06-10` as Command 1, but the execution record shows Command 1 was actually run as `warehouse --dataset gateway_lat --day 2026-06-09` (output confirms `day=2026-06-09`). The worker's comparison is therefore 2026-06-09 vs 2026-06-11, not the briefed 2026-06-10 vs 2026-06-11 — no data on 2026-06-10 itself was collected at all.
2. The "Deviations from brief" field falsely states "none," contradicting the command/output pair shown immediately above it.
3. The "Method and sample" field falsely narrates the run as covering "2026-06-10 and 2026-06-11," which also contradicts the execution record.
The derived arithmetic itself is not faulted: +0.4ms / 24.6ms = +1.6% is correctly computed from the quoted output, and 2 of 3 budgeted calls is within budget — the fault is confined to which day was queried and how that was described.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- Gateway p95 for 2026-06-10 — the day the preregistered prediction is actually about — was never queried; the reconciled verdict on H2's necessary prediction (flat change between 2026-06-10 and 2026-06-11) rests on no direct evidence about 2026-06-10.
- The deviation cannot be corrected or verified harmless within this run: the `warehouse` CLI is metered, the investigation's budget is fully spent, no further metered queries are authorized, and this is a non-interactive run with no user available to ask — so a re-pull to obtain the correct day is not possible here.
- H2 stays UNRESOLVED, not REFUTED and not supported: the test that ran did not adequately test the necessary prediction as preregistered.

GOVERNING SKILL TEXT:
From SKILL.md: "Start with the free check: read the worker's stated method and command against the prediction it claims to test, and against its own return. Does the command implement the method it names? Does the quoted number appear in the output it came from? Is the grain the one the prediction specified, and the window the one the brief set?"
From SKILL.md: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md: "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize."
From SKILL.md: "An established deviation makes the reconciled outcome NON_DISCRIMINATING when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md: "The status set is closed: REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise."
From references/subagent-briefs.md: "Spot-verify the evidence behind the leading explanation and the strongest rival before concluding. The free form comes first and is usually the one that catches something: check the worker's stated method and command against the prediction it was briefed on and against its own return: command matches method, quoted figures appear in the output they cite, grain and window match the brief."

REASONING: The free check (comparing the brief's window against the worker's own quoted commands) surfaces a real fault: Command 1 was run against 2026-06-09, not the briefed 2026-06-10, so the worker actually tested a 06-09-vs-06-11 contrast while both its Deviations field ("none") and its Method narrative ("2026-06-10 and 2026-06-11") misdescribe this. The execution record — the command and its own output — outranks those narrative fields, so the deviation is established rather than dismissed. Because 2026-06-10, the day the necessary prediction names, was never queried, the procedure that ran did not adequately test the preregistered prediction, and no outside evidence is available to show the substitution is harmless (the source is metered, the budget is spent, and no re-query is authorized in this non-interactive run). That combination is exactly the case SKILL.md routes to NON_DISCRIMINATING rather than accepting the worker's self-reported CONTRADICTED. With T2 downgraded to NON_DISCRIMINATING, H2's necessary prediction has not failed under an adequate test, so per the closed status set H2 remains UNRESOLVED — and the window gap plus the inability to re-collect must both be carried into the conclusion as limitations, not silently absorbed into a verdict.
```

#### xC1B-2

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING

H2 STATUS: UNRESOLVED

FAULTS FOUND IN THE RETURN:
1. Command/window substitution: the brief required querying `gateway_lat` for 2026-06-10 and 2026-06-11 (the exact window H2's necessary prediction names). The worker's actual Command 1 ran `--day 2026-06-09`, not `--day 2026-06-10`, and its own quoted output confirms `day=2026-06-09`. 2026-06-10 — the drop day itself — was never queried at all.
2. Narrative misrepresents the execution record in two fields: "Method and sample" states the tool was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," which the commands contradict; and "Deviations from brief: none" denies any deviation despite the coherent command+output record showing one (querying 06-09 in place of the briefed 06-10).
3. The derived arithmetic itself is not faulted: 24.6 -> 25.0 = +1.6% is correctly computed from the worker's own quoted output, so this is a window/deviation fault, not a derived-value error.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
- T2 as actually executed measured the 2026-06-09 -> 2026-06-11 change, not the preregistered 2026-06-10 -> 2026-06-11 change; it does not adequately test H2's necessary prediction, so the necessary prediction was not tested.
- Gateway p95 for 2026-06-10 itself is unknown from this return; a spike on 06-10 that partly reverted by 06-11 could be masked by the 06-09-anchored comparison, so the "flat" reading cannot be read as ruling out a 06-10 rise.
- No re-verification is possible: the warehouse source is metered, the investigation's budget is fully spent, and this is a non-interactive run with no user to authorize a re-pull — so this limitation stands unresolved rather than closed by re-query.
- The worker's narrative fields (Method and sample; Deviations from brief) are shown unreliable on this return and should not be trusted uncorroborated in future reconciliation.

GOVERNING SKILL TEXT:
From SKILL.md: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md: "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize."
From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md: "An established deviation makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md: "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free spot-check (read the worker's stated method and commands against the brief and against its own return) surfaces a mismatch the worker's narrative denies: Command 1 queried 2026-06-09, not the briefed 2026-06-10, yet "Method and sample" claims 06-10 was queried and "Deviations from brief" claims none occurred. Because the command and its own output agree with each other on the wrong day, this is a coherent execution record establishing a deviation, which outranks the contradicting narrative fields. That deviation left the actual preregistered window (06-10 vs 06-11) untested — 06-10 data never appears anywhere in the return — so the procedure did not adequately test H2's necessary prediction, and no outside evidence is available to show the deviation harmless (source metered, budget spent, no user to ask). The skill's rule for exactly this situation assigns `NON_DISCRIMINATING` as the reconciled outcome, overriding the worker's self-reported `CONTRADICTED`. With T2 downgraded to `NON_DISCRIMINATING`, H2 has no adequate test failing its necessary prediction, so per the closed status set it stays `UNRESOLVED` rather than `REFUTED`.
```

#### xC1B-3

```markdown
RECONCILED OUTCOME FOR T2: NON_DISCRIMINATING
H2 STATUS: UNRESOLVED
FAULTS FOUND IN THE RETURN:
1. Wrong window queried: the brief specified "Run: `warehouse --dataset gateway_lat --day 2026-06-10`" as Command 1, but the return's actual Command 1 is `warehouse --dataset gateway_lat --day 2026-06-09`, and its output header reads `day=2026-06-09` — command and output agree with each other, so this is a coherent execution record showing an unbriefed substitution (2026-06-09 baseline instead of 2026-06-10).
2. The narrative "Method and sample" field asserts the CLI was run "against `gateway_lat` for 2026-06-10 and 2026-06-11," which the execution record contradicts (Command 1 is for 06-09, not 06-10).
3. "Deviations from brief: none" denies the deviation the execution record establishes.

LIMITATIONS THAT MUST REACH THE CONCLUSION:
T2's comparison actually ran 2026-06-09 vs 2026-06-11 (a two-day gap), not the preregistered 2026-06-10 vs 2026-06-11 (one-day) comparison the necessary prediction names; whether 2026-06-09 gateway latency stood in adequately for 2026-06-10 is unverified, no outside evidence confirms the substitution was harmless, and the warehouse CLI is metered with the investigation budget fully spent and no further queries authorized, so this cannot be checked. H2 therefore stays UNRESOLVED on this test rather than REFUTED, pending an adequate test of the actual 2026-06-10-to-2026-06-11 window.

GOVERNING SKILL TEXT:
From SKILL.md: "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize."
From SKILL.md: "An established deviation makes the reconciled outcome NON_DISCRIMINATING when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless."
From SKILL.md: "A narrative field contradicting a coherent execution record does not unsettle it; it is one more thing the return got wrong, whether it confesses a deviation the record does not show or denies one the record does."
From SKILL.md: "That downgrade records the inadequacy of the test that ran, not distrust of the worker — an honest query against the wrong window still leaves the preregistered prediction untested, which is what `NON_DISCRIMINATING` says."
From SKILL.md: "Rank the return's execution record above its narrative: the quoted commands and the parameters the tool itself emitted are the account of what ran, while Method and Deviations are the worker's description of it."
From SKILL.md (Conclusion): "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: The free spot-check (comparing the worker's stated method and its own quoted commands/output against the brief) surfaces a real fault, not a clean return: Command 1 in the evidence names and returns 2026-06-09, while the brief called for 2026-06-10, and both the command flag and the output header agree with each other on 06-09 — a coherent execution record of an unbriefed substitution, which the SKILL.md text ranks above the worker's narrative claims ("Method and sample" saying 06-10, "Deviations: none") that deny or misstate it. Because the necessary prediction is specifically about the 2026-06-10-to-2026-06-11 change, and the test actually run used 2026-06-09 as the baseline with no outside evidence that 06-09 stood in for 06-10, the procedure the record evidences did not adequately test the preregistered prediction. Per SKILL.md, that established, unverified-harmless deviation forces the reconciled outcome to NON_DISCRIMINATING rather than the worker's claimed CONTRADICTED (which was H2-FALSE-consistent, i.e., would have refuted H2). Re-running is not an option: the warehouse CLI is metered, the budget is spent, and this is a non-interactive run with no user to authorize a re-pull, so per SKILL.md the shortfall is recorded as a limitation rather than resolved. With T2 downgraded to NON_DISCRIMINATING, H2 has no adequate test of its necessary prediction, so under the closed status set it remains UNRESOLVED — it cannot be REFUTED on an inadequate test, and NON_DISCRIMINATING is an outcome value for the test entry, not grounds for any status other than UNRESOLVED.
```
