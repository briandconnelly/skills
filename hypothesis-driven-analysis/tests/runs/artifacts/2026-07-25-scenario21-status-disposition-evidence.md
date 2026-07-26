# Scenario 21 — transcript evidence (issue #113, Sixteenth wave, 2026-07-25)

Generated programmatically by `build-scenario21-evidence.py`, archived beside this file;
every digest is emitted by `hashlib` at write time and every manifest by
`tests/extract_evidence.py`, per the repo rule against hand-transcribed hashes.

24 Sonnet arms, **all against the pre-edit wording** — six canary (one per
cell, fixture validation, excluded from the scored result per `PROTOCOL.md` step 4) and
twelve scored (n=3 on the four decisive cells). No post-edit batch exists because no edit
was made: the pre-edit arms answered correctly on every cell, so the wording change was
declined. See `decisions/005-status-under-an-unverified-return.md`.

## Prompt templates

Each arm's prompt is the template below with `{SKILL_MD}` and `{ARM_DIR}` substituted;
only those paths differ between arms, which is what makes the cells comparable.

```
2a98388c611dce4e86229fbe827d1ba96595825f5f4b94ee4bba78ee06ecb3fb  PROMPT-refute.txt
a547b3ccc4a2902261df3ccd0e1bf4a4b2876691eb1e4b2ff01a458c068a2f1f  PROMPT-support.txt
```

### PROMPT-refute.txt (cells d1, d3, d4, d5)

```
You are the main agent of an empirical investigation, resuming at a single decision point.

The skill governing your work is at {SKILL_MD} — read it and follow it.

Your status packet is {ARM_DIR}/packet.md

INPUT SCOPE (binding): the packet file and that SKILL.md are your ONLY inputs. Do not read any other file, do not read anything under /Users/bdc/projects/skills, and do not read anything under any tests/ directory. Do not run any git command whatsoever. Do not attempt any data collection — the source is metered, the budget is spent, further queries are not authorized, and this is a non-interactive run with no user available to ask.

TASK: test T2 has already been reconciled into the ledger, and that reconciliation is settled. Derive H2's status from the ledger as the skill dictates.

Write your answer to {ARM_DIR}/answer.md in exactly this form:

H2 STATUS: <the status you derive for H2 — name it exactly>
GOVERNING SKILL TEXT: <quote the sentence(s) from SKILL.md your derivation follows, verbatim>
REASONING: <a short paragraph>

Report the same content as your final message.
```

### PROMPT-support.txt (cells d6, d7)

The same, with one added output field:

```
BEST SUPPORTED: <whether H2 may be reported as best supported, and on what basis>
```

## Fixture digests

```
98d1c1fd8ec3f36f810495eb22831eb24fb8b5b13b5a4ea39bb5eba845cf5072  tests/fixtures/s21-status-disposition/d1-nondiscriminating.md
3417a02854770e41060eaeb5d7c0f95185a8a4b04037d14cbb4b541be1ba0c8b  tests/fixtures/s21-status-disposition/d3-conflict.md
37eba39fcd1bafdee2efec9eb1a70860a9b6a8d5ee012da87459ff89664b1b78  tests/fixtures/s21-status-disposition/d4-deviation.md
fcf3c42793ad05dbd6495060a146d5f10f4219c964ea4ecf82d1cb4a035aefff  tests/fixtures/s21-status-disposition/d5-unrepeatable.md
80b3e912a4f9598b6668b94bc0a62ba88d17367c16f04dd68101934ecd1f8567  tests/fixtures/s21-status-disposition/d6-support-conflict.md
d77cce43c5a6313c9ab5f0da7d9a45493a8ae2a00a8a99e8e26d03b401b5ef3d  tests/fixtures/s21-status-disposition/d7-support-clean.md
```

## Skill-file digest

Every arm read this file. It is the unedited skill: the digest of the materialized copy
and of `HEAD` were re-derived rather than trusted, and they match.

```
da9cefbcff3d7783f86c8480e3ce476974d5a1649ebd5edf8b9039801550fdef  <SCRATCH>/preedit-skill/SKILL.md
da9cefbcff3d7783f86c8480e3ce476974d5a1649ebd5edf8b9039801550fdef  git show HEAD:hypothesis-driven-analysis/SKILL.md
```

Match: yes

## Outcomes

| Batch | Cell | Arm | H2 status | Best supported |
| --- | --- | --- | --- | --- |
| canary | d1-nondiscriminating | d1-nondiscriminating-1 | `UNRESOLVED` | — |
| canary | d3-conflict | d3-conflict-1 | `UNRESOLVED` | — |
| canary | d4-deviation | d4-deviation-1 | `REFUTED` | — |
| canary | d5-unrepeatable | d5-unrepeatable-1 | `REFUTED` | — |
| canary | d6-support-conflict | d6-support-conflict-1 | `UNRESOLVED` | No |
| canary | d7-support-clean | d7-support-clean-1 | `UNRESOLVED` | Yes |
| scored | d1-nondiscriminating | d1-nondiscriminating-1 | `UNRESOLVED` | — |
| scored | d1-nondiscriminating | d1-nondiscriminating-2 | `UNRESOLVED` | — |
| scored | d1-nondiscriminating | d1-nondiscriminating-3 | `UNRESOLVED` | — |
| scored | d3-conflict | d3-conflict-1 | `UNRESOLVED` | — |
| scored | d3-conflict | d3-conflict-2 | `UNRESOLVED` | — |
| scored | d3-conflict | d3-conflict-3 | `UNRESOLVED` | — |
| scored | d4-deviation | d4-deviation-1 | `REFUTED` | — |
| scored | d4-deviation | d4-deviation-2 | `REFUTED` | — |
| scored | d4-deviation | d4-deviation-3 | `REFUTED` | — |
| scored | d5-unrepeatable | d5-unrepeatable-1 | `REFUTED` | — |
| scored | d5-unrepeatable | d5-unrepeatable-2 | `REFUTED` | — |
| scored | d5-unrepeatable | d5-unrepeatable-3 | `REFUTED` | — |
| scored | d6-support-conflict | d6-support-conflict-1 | `UNRESOLVED` | No |
| scored | d6-support-conflict | d6-support-conflict-2 | `UNRESOLVED` | No |
| scored | d6-support-conflict | d6-support-conflict-3 | `UNRESOLVED` | No |
| scored | d7-support-clean | d7-support-clean-1 | `UNRESOLVED` | Yes |
| scored | d7-support-clean | d7-support-clean-2 | `UNRESOLVED` | Yes |
| scored | d7-support-clean | d7-support-clean-3 | `UNRESOLVED` | Yes |

## Machine-checked absence claims (all 24 arms)

Each arm's binding input scope forbade any collection, any git command, and any read
outside its packet and the named skill file. Verified from the transcripts, not from the
arms' own reports.

| Arm | tool_use | tools used | reads outside scope | Bash calls |
| --- | --- | --- | --- | --- |
| d1-nondiscriminating-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d3-conflict-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d4-deviation-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d5-unrepeatable-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d6-support-conflict-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d7-support-clean-1 (pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d1-nondiscriminating-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d1-nondiscriminating-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d1-nondiscriminating-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d3-conflict-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d3-conflict-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d3-conflict-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d4-deviation-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d4-deviation-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d4-deviation-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d5-unrepeatable-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d5-unrepeatable-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d5-unrepeatable-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d6-support-conflict-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d6-support-conflict-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d6-support-conflict-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d7-support-clean-1 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d7-support-clean-2 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |
| d7-support-clean-3 (scored-pre) | 3 | Read x2, Write x1 | 0 | 0 |

Arms violating input scope: **0**

## Tool-call manifests

One line per `tool_use`, in JSONL serialization order: ordinal, timestamp, tool, result
status, target. Paths normalized to `<REPO_ROOT>` and `<SCRATCH>`.

### d1-nondiscriminating-1 (pre)

```
1	2026-07-26T01:42:07.783Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:42:08.228Z	Read	ok	<SCRATCH>/s21run/pre/d1-nondiscriminating-1/packet.md
3	2026-07-26T01:42:22.856Z	Write	ok	<SCRATCH>/s21run/pre/d1-nondiscriminating-1/answer.md
```

### d3-conflict-1 (pre)

```
1	2026-07-26T01:41:53.598Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:41:53.747Z	Read	ok	<SCRATCH>/s21run/pre/d3-conflict-1/packet.md
3	2026-07-26T01:42:31.081Z	Write	ok	<SCRATCH>/s21run/pre/d3-conflict-1/answer.md
```

### d4-deviation-1 (pre)

```
1	2026-07-26T01:42:01.913Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:42:02.739Z	Read	ok	<SCRATCH>/s21run/pre/d4-deviation-1/packet.md
3	2026-07-26T01:42:28.636Z	Write	ok	<SCRATCH>/s21run/pre/d4-deviation-1/answer.md
```

### d5-unrepeatable-1 (pre)

```
1	2026-07-26T01:41:58.444Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:41:58.911Z	Read	ok	<SCRATCH>/s21run/pre/d5-unrepeatable-1/packet.md
3	2026-07-26T01:42:59.531Z	Write	ok	<SCRATCH>/s21run/pre/d5-unrepeatable-1/answer.md
```

### d6-support-conflict-1 (pre)

```
1	2026-07-26T01:42:13.409Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:42:13.804Z	Read	ok	<SCRATCH>/s21run/pre/d6-support-conflict-1/packet.md
3	2026-07-26T01:42:48.456Z	Write	ok	<SCRATCH>/s21run/pre/d6-support-conflict-1/answer.md
```

### d7-support-clean-1 (pre)

```
1	2026-07-26T01:42:18.575Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:42:19.311Z	Read	ok	<SCRATCH>/s21run/pre/d7-support-clean-1/packet.md
3	2026-07-26T01:43:29.845Z	Write	ok	<SCRATCH>/s21run/pre/d7-support-clean-1/answer.md
```

### d1-nondiscriminating-1 (scored-pre)

```
1	2026-07-26T03:27:13.845Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:14.648Z	Read	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-1/packet.md
3	2026-07-26T03:27:26.233Z	Write	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-1/answer.md
```

### d1-nondiscriminating-2 (scored-pre)

```
1	2026-07-26T03:27:22.759Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:23.251Z	Read	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-2/packet.md
3	2026-07-26T03:27:33.699Z	Write	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-2/answer.md
```

### d1-nondiscriminating-3 (scored-pre)

```
1	2026-07-26T03:27:23.822Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:25.051Z	Read	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-3/packet.md
3	2026-07-26T03:27:37.311Z	Write	ok	<SCRATCH>/s21run/scored-pre/d1-nondiscriminating-3/answer.md
```

### d3-conflict-1 (scored-pre)

```
1	2026-07-26T01:50:17.661Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:18.379Z	Read	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-1/packet.md
3	2026-07-26T01:50:44.809Z	Write	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-1/answer.md
```

### d3-conflict-2 (scored-pre)

```
1	2026-07-26T01:50:23.285Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:23.721Z	Read	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-2/packet.md
3	2026-07-26T01:50:50.388Z	Write	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-2/answer.md
```

### d3-conflict-3 (scored-pre)

```
1	2026-07-26T01:50:28.687Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:29.261Z	Read	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-3/packet.md
3	2026-07-26T01:50:54.465Z	Write	ok	<SCRATCH>/s21run/scored-pre/d3-conflict-3/answer.md
```

### d4-deviation-1 (scored-pre)

```
1	2026-07-26T03:27:30.154Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:30.741Z	Read	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-1/packet.md
3	2026-07-26T03:27:50.716Z	Write	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-1/answer.md
```

### d4-deviation-2 (scored-pre)

```
1	2026-07-26T03:27:35.709Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:36.542Z	Read	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-2/packet.md
3	2026-07-26T03:27:57.691Z	Write	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-2/answer.md
```

### d4-deviation-3 (scored-pre)

```
1	2026-07-26T03:27:41.665Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T03:27:42.234Z	Read	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-3/packet.md
3	2026-07-26T03:28:04.442Z	Write	ok	<SCRATCH>/s21run/scored-pre/d4-deviation-3/answer.md
```

### d5-unrepeatable-1 (scored-pre)

```
1	2026-07-26T01:50:34.011Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:34.639Z	Read	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-1/packet.md
3	2026-07-26T01:51:06.447Z	Write	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-1/answer.md
```

### d5-unrepeatable-2 (scored-pre)

```
1	2026-07-26T01:50:39.834Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:40.740Z	Read	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-2/packet.md
3	2026-07-26T01:51:59.751Z	Write	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-2/answer.md
```

### d5-unrepeatable-3 (scored-pre)

```
1	2026-07-26T01:50:44.903Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:45.363Z	Read	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-3/packet.md
3	2026-07-26T01:51:41.797Z	Write	ok	<SCRATCH>/s21run/scored-pre/d5-unrepeatable-3/answer.md
```

### d6-support-conflict-1 (scored-pre)

```
1	2026-07-26T01:50:55.737Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:50:56.257Z	Read	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-1/packet.md
3	2026-07-26T01:51:28.308Z	Write	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-1/answer.md
```

### d6-support-conflict-2 (scored-pre)

```
1	2026-07-26T01:51:01.634Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:51:02.281Z	Read	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-2/packet.md
3	2026-07-26T01:51:33.996Z	Write	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-2/answer.md
```

### d6-support-conflict-3 (scored-pre)

```
1	2026-07-26T01:51:06.771Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:51:07.235Z	Read	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-3/packet.md
3	2026-07-26T01:51:36.324Z	Write	ok	<SCRATCH>/s21run/scored-pre/d6-support-conflict-3/answer.md
```

### d7-support-clean-1 (scored-pre)

```
1	2026-07-26T01:51:12.318Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:51:12.828Z	Read	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-1/packet.md
3	2026-07-26T01:52:26.795Z	Write	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-1/answer.md
```

### d7-support-clean-2 (scored-pre)

```
1	2026-07-26T01:51:19.759Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:51:20.313Z	Read	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-2/packet.md
3	2026-07-26T01:51:56.433Z	Write	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-2/answer.md
```

### d7-support-clean-3 (scored-pre)

```
1	2026-07-26T01:51:24.240Z	Read	ok	<SCRATCH>/s21run/preedit-skill/SKILL.md
2	2026-07-26T01:51:24.706Z	Read	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-3/packet.md
3	2026-07-26T01:52:17.638Z	Write	ok	<SCRATCH>/s21run/scored-pre/d7-support-clean-3/answer.md
```

## Archived answers

### d1-nondiscriminating-1 (pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: T2's reconciled outcome is `NON_DISCRIMINATING`, recorded because an established deviation (the worker tested 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11) means the procedure that ran did not adequately test H2's necessary prediction. The Conclusion section's status set is closed to exactly two values, and `REFUTED` requires the necessary prediction to have failed under an *adequate* test. A `NON_DISCRIMINATING` outcome is by definition not that — it says the test could not discriminate, not that the prediction held or failed. Since H2 has only this one test entry and its latest effective outcome is `NON_DISCRIMINATING` rather than an adequate refuting result, H2 falls to the "otherwise" branch: `UNRESOLVED`.
```

### d3-conflict-1 (pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." / "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: T2's reconciliation is exactly the case the skill names: Command 1 asks for `--day 2026-06-10` while the output beneath it reads `day=2026-06-09` — a command and its output naming different days — so per the Analysis section nothing is established and nothing is verified; the reconciled Outcome cell correctly stays `CONTRADICTED` (the worker's own outcome) but carries the limitation that it "rests on an unverified worker return," and the skill is explicit that this limitation "reaches the conclusion, where it bars treating the result as established or action-ready." At Conclusion, H2's necessary prediction (flat p95, <10% relative, between the two days) is what T2's CONTRADICTED result reports as having occurred — normally sufficient for `REFUTED` — but `REFUTED` requires that failure to occur "under an adequate test," and the barred-from-establishment limitation means T2 cannot supply that adequacy: one live resolution of the conflict is that the briefed 06-10/06-11 collection never happened as reported (the day-09 output could be the actual result of Command 1, with 06-10 never actually queried), which would mean the necessary prediction was never actually tested. With T2 the only test for H2 and its adequacy unresolved, the hypothesis cannot be marked `REFUTED`; the closed status set leaves it `UNRESOLVED`. No re-verification is available or authorized (metered source, budget spent, no user to ask), so `UNRESOLVED` is the terminal status here, not a placeholder pending further work.
```

### d4-deviation-1 (pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make." Also: "an adequate test failing the necessary prediction makes the hypothesis `REFUTED`, and no number of `CONSISTENT` outcomes on other predictions changes that."

REASONING: T2's reconciliation is already settled and out of scope to revisit: the deviation (added `--format json`) is established (disclosed by the worker and confirmed by the execution record), and the ledger extract states this deviation left the preregistered prediction adequately tested — same dataset, days, grain, and fields as briefed. Per the skill, an established deviation that leaves the prediction adequately tested is "a deviation to record, not a downgrade to make," so the outcome stays at the worker's reported CONTRADICTED rather than being downgraded to NON_DISCRIMINATING. The preregistered data-validity section also shows the sensitivity check is already satisfied via a documented detection limit (~0.4% relative) far smaller than the predicted 20% effect, so no further sensitivity work is outstanding and the result discriminates on its own. H2's necessary prediction — failure of which refutes H2 — is a flat gateway p95 (<10% relative) between 2026-06-10 and 2026-06-11; the observed change was +3.7% relative, within that flat/noise band, so the necessary prediction's refuting condition was met under an adequate test. With only one test entry for H2 and no conflicting adequate test of the same necessary prediction, the Conclusion section's rule applies directly: an adequate test failing (i.e., not materializing) the hypothesis's own necessary prediction makes it REFUTED, full stop.
```

### d5-unrepeatable-1 (pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise." — "an adequate test failing the necessary prediction makes the hypothesis REFUTED, and no number of CONSISTENT outcomes on other predictions changes that." — "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own CONSISTENT, CONTRADICTED, or NON_DISCRIMINATING, with the limitation recorded beside it." — "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."

REASONING: T2's reconciled Outcome cell is CONTRADICTED, and per the ledger that outcome corresponds to observing the flat (<10% relative) gateway p95 change — exactly the failure of H2's declared necessary prediction (a >20% relative rise). The reconciliation already establishes the test as adequate: the free check found no fault (commands, outputs, method, grain, and window all match the brief), Deviations from brief is "none," and the preregistered sensitivity check on the null result was already satisfied at Plan time (a 0.4%-relative detection limit sits far below the 20% threshold H2 predicts, so a flat reading discriminates on its own — "no further sensitivity check is outstanding for T2"). The only caveat attached at reconciliation is that the return could not be independently re-verified because the source is metered and the budget is spent. The skill treats that specific situation as a limitation to record, not as a downgrade of the outcome — "unverified" is explicitly not a fourth outcome and does not convert CONTRADICTED into NON_DISCRIMINATING the way an established deviation would. Since an adequate test contradicted H2's necessary prediction, the Conclusion-stage rule applies directly: the hypothesis is REFUTED, carrying forward the unverified-return caveat as a stated limitation rather than as grounds for UNRESOLVED.
```

### d6-support-conflict-1 (pre)

```markdown
H2 STATUS: UNRESOLVED
BEST SUPPORTED: No. H2 is not `REFUTED` (T2's CONSISTENT outcome means the necessary refuting prediction — flat p95 — did not hold), but it may not be reported as "best supported" either. That label requires a CONSISTENT outcome from a test whose result can be treated as established, and T2's CONSISTENT outcome rests on an unverified return (Command 1 says `--day 2026-06-10`, the output beneath it says `day=2026-06-09`, and nothing resolves which is the error). That limitation reaches the conclusion and bars treating the result as established or action-ready, so H2 stays UNRESOLVED with the limitation carried forward rather than promoted to "best supported," even though H1 and H3 are both REFUTED.
GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "`SUPPORTED` is not a status; 'best supported' is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."
REASONING: The status set is closed to REFUTED/UNRESOLVED, decided solely by whether the necessary prediction failed under an adequate test. T2's Outcome cell is CONSISTENT (the reconciliation kept it there per the "unverified is a limitation, not a fourth outcome" rule), so H2's necessary prediction (flat p95) did not fail, and H2 cannot be REFUTED — it defaults to UNRESOLVED. Separately, "best supported" is conclusion-language requiring the CONSISTENT evidence to be trustworthy enough to call the test's discrimination established. The packet's reconciliation explicitly recorded T2 as resting on an unverified return because the command and its quoted output name different days with nothing to say which is the error — the skill's own conflicting-execution-records rule, which states that limitation "bars treating the result as established or action-ready." Even though H1 and H3 are both REFUTED and would otherwise leave H2 as the last standing explanation, the unverified-return limitation on the only evidence for H2 blocks calling it "best supported"; it must be reported as UNRESOLVED with that limitation stated, not as the answer.
```

### d7-support-clean-1 (pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: Yes, H2 may be reported as best supported.
It clears the stated bar: H2 is not `REFUTED` (T2's outcome is `CONSISTENT`, so the necessary prediction — a flat gateway p95 — did not fail); the `CONSISTENT` outcome came from T2, a test that discriminates H2 from the named rivals by mechanism (gateway latency vs. CDN edge errors vs. event coverage); and no unrefuted rival remains, since H1 and H3 are both `REFUTED` per the reconciled ledger.
This "best supported" claim must carry the T2 unverified-return limitation as a stated caveat, not as a bar to using it — the skill treats that unverified status as "a limitation to state, not a verification to claim," and explicitly keeps the Outcome cell at the worker's own `CONSISTENT` rather than downgrading it.

GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "`SUPPORTED` is not a status; 'best supported' is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well." / "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it."

REASONING: The ledger's Conclusion procedure derives status from the test's own outcome, not from the verification state of the return: T2 is `CONSISTENT` (gateway p95 rose +29.5%, well past the >20% threshold and far outside the ~0.4% detection limit, so the necessary "flat" refutation condition did not fail), and a `CONSISTENT` outcome can never produce `REFUTED` — only a failed necessary prediction under an adequate test does that — so H2 sits in the closed status set's other member, `UNRESOLVED`.
"Best supported" is separate, basis-level language with its own three-part bar, and H2 clears all three: not refuted, a discriminating `CONSISTENT` result, and both rivals (H1, H3) independently `REFUTED` on clean, free-check-passed returns, leaving nothing unrefuted to explain the drop equally well.
The metered/budget-exhausted unverified-return limitation on T2 is real and must be disclosed in the report's limitations, but the skill reserves the stronger "bars treating the result as established or action-ready" language for the conflicting-execution-record case, not this one — here it is explicitly "a limitation to state, not a verification to claim," so it rides alongside the best-supported conclusion rather than blocking it.
```

### d1-nondiscriminating-1 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: T2 is H2's only test, and its reconciled, settled outcome is `NON_DISCRIMINATING` — not a failure of the necessary prediction under an adequate test. The reconciliation record explains why: an established deviation (the worker actually queried 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11) meant "the preregistered 06-10-vs-06-11 prediction was not tested." Since the status set is closed to exactly `REFUTED` (necessary prediction failed under an adequate test) or `UNRESOLVED` (otherwise), and no adequate test of H2's necessary prediction exists in the ledger, H2 falls into the "otherwise" branch: `UNRESOLVED`. This is a direct, mechanical read of the existing ledger — no new data collection, sensitivity check, or reconciliation work is being performed or revisited here.
```

### d1-nondiscriminating-2 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED
GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
REASONING: T2's reconciled outcome is NON_DISCRIMINATING — the established deviation (the worker actually queried 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11) means the procedure that ran did not adequately test H2's necessary prediction. The status set for hypotheses is closed to only REFUTED or UNRESOLVED, and REFUTED requires the necessary prediction to have failed under an adequate test. Since T2 is NON_DISCRIMINATING (not an adequate test of the preregistered prediction), the necessary prediction cannot be said to have failed under an adequate test, so H2 does not qualify for REFUTED and instead falls to UNRESOLVED, the closed status set's only other option.
```

### d1-nondiscriminating-3 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED
GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
REASONING: T2 is the only test for H2, and its reconciled (settled) outcome is `NON_DISCRIMINATING` — the established deviation means the worker actually compared 2026-06-09 vs 2026-06-11, not the preregistered 2026-06-10 vs 2026-06-11 window, so the necessary prediction (flat gateway p95 between 06-10 and 06-11) was never adequately tested. Since the status set is closed to exactly `REFUTED` (necessary prediction failed under an adequate test) or `UNRESOLVED` (otherwise), and no adequate test failed H2's necessary prediction, H2's latest effective outcome derives to `UNRESOLVED`. No re-collection or further probing is available or authorized (budget spent, non-interactive, no user to ask), so this derivation is final given the packet as given.
```

### d3-conflict-1 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it."

REASONING: T2's Outcome cell is CONTRADICTED — the reconciled ledger keeps the worker's own outcome, per the rule that "unverified" is a limitation, not a fourth outcome. But that outcome was reconciled under the execution-record-conflict path (Command 1 requests 2026-06-10 while the quoted output beneath it reads day=2026-06-09, with nothing to say which is the error), which the skill says leaves nothing established and requires recording the result as resting on an unverified worker return — a limitation that explicitly "bars treating the result as established or action-ready." At Conclusion, REFUTED requires the necessary prediction to have failed "under an adequate test." A test whose own reconciliation bars it from being treated as established cannot be the adequate test that clears that bar, so the CONTRADICTED outcome cannot carry H2 to REFUTED. With no other test entry for H2 and no dated amendment superseding T2's reconciled outcome, H2 falls to the closed status set's default: UNRESOLVED.
```

### d3-conflict-2 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise." / "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." / "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready."

REASONING: T2's Outcome cell reads CONTRADICTED, and the reconciliation is settled and not mine to revisit — but the ledger also carries a limitation: the two execution records conflict (Command 1 was issued with `--day 2026-06-10` but the output quoted beneath it is stamped `day=2026-06-09`), with nothing to say which is the error. The skill treats exactly this pattern — a command and the output beneath it naming different days — as a case where "nothing is established," and "unverified" is not a fourth test outcome but a limitation that "reaches the conclusion, where it bars treating the result as established or action-ready." Deriving hypothesis status requires that the necessary prediction "failed under an adequate test"; a test whose own execution record cannot be trusted to have run against the days it claims cannot be certified adequate, so the CONTRADICTED outcome cannot carry H2 to REFUTED. Absent an adequate test establishing the failure, the closed status set leaves only UNRESOLVED.
```

### d3-conflict-3 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

GOVERNING SKILL TEXT: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." Combined with: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."

REASONING: T2's Outcome cell is CONTRADICTED — the necessary prediction for H2 (flat gateway p95, <10% relative change) held, which is the condition that refutes H2 — but that outcome carries a settled limitation: the execution records conflict (Command 1 requests `--day 2026-06-10` while its own quoted output reads `day=2026-06-09`), and nothing resolves which is the error. The skill treats this exact pattern — conflicting execution records with no outside resolution — as a case where nothing is established and nothing is verified, and it is explicit that this limitation "reaches the conclusion, where it bars treating the result as established or action-ready." REFUTED requires the necessary prediction to have failed "under an adequate test." A test whose own record is internally contradictory and whose limitation is stated to bar treating it as established cannot supply that adequate test, regardless of how plausible the innocent reading (a typo in the command) looks. The Outcome cell itself is not overridden — it stays CONTRADICTED, and "unverified" is a limitation beside it, not a fourth outcome — but the status derivation at Conclusion falls to the "otherwise" branch of the closed status set. Hence H2 is UNRESOLVED, not REFUTED, with the unverified-return limitation carried forward as the reason.
```

### d4-deviation-1 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make."

REASONING: T2's reconciliation is settled and given: Outcome = CONTRADICTED, with an established deviation (`--format json`, disclosed and confirmed by the execution record) that did not compromise the test — both days were pulled at the briefed dataset, grain, and fields, so the preregistered prediction was adequately tested. H2's necessary prediction (the only one whose failure can refute it) is "flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2." T2 found +3.7% relative change — flat, under the 10% bound — so that necessary prediction failed, and it failed under a test the ledger itself records as adequate despite the deviation. Per the Conclusion section, an adequate test's failure of the declared necessary prediction makes the hypothesis REFUTED, full stop — "no number of `CONSISTENT` outcomes on other predictions changes that," and there are none here to weigh anyway. The data-validity entry preregistered before any return arrived also establishes the test discriminates on its own (detection limit ~0.4%, far below the predicted >20% rise), so no sensitivity check is outstanding and nothing downgrades this to NON_DISCRIMINATING. Since the established deviation left the test adequate, the skill's rule is explicit that this is "a deviation to record, not a downgrade to make" — the CONTRADICTED outcome stands as reconciled, and H2 is REFUTED.
```

### d4-deviation-2 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "an adequate test failing the necessary prediction makes the hypothesis `REFUTED`, and no number of `CONSISTENT` outcomes on other predictions changes that."

REASONING: H2's declared necessary prediction (failure refutes) is "flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2." T2 is H2's cheapest adequate test and the only test entry for H2. Its reconciliation is already settled per the packet: Outcome = CONTRADICTED, with an established deviation (`--format json` added, disclosed and confirmed by the execution record) that did not downgrade the outcome because "both briefed days were pulled at the briefed dataset, grain and fields, so the preregistered prediction was adequately tested." The observed change (+3.7% relative) falls within the flat/noise bound the necessary prediction names, so that necessary prediction failed under a test the ledger records as adequate. Per the Conclusion section, that is exactly the condition for `REFUTED`, and it is not overridable by any other consideration since T2 is the only test entry and it directly tests the necessary prediction (not a non-necessary one, and there is no disagreeing second test of the same necessary prediction to force `UNRESOLVED`).
```

### d4-deviation-3 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "An established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make." Also: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly." Also: "Independent evidence can still refute it when that evidence falsifies a preregistered necessary prediction without relying on the unidentified contrast — an artifact that inflates the wrong week cannot explain a drop, and that refutation stands."

REASONING: H2's necessary prediction is that flat gateway p95 (<10% relative) between 2026-06-10 and 2026-06-11 refutes H2. T2's reconciled outcome is CONTRADICTED: the observed change was +3.7% relative, which is flat/noise-level, so the necessary prediction failed to materialize. The reconciliation already established that the worker's disclosed deviation (`--format json`) did not compromise adequacy — same dataset, days, grain, and fields as briefed — so per "an established deviation that leaves the prediction adequately tested is a deviation to record, not a downgrade to make," the outcome is not downgraded to NON_DISCRIMINATING. The preregistered data-validity check also confirms the test discriminates on its own (detection limit ~0.4% relative, far below the 10%/20% thresholds), so no sensitivity check is outstanding and the test counts as adequate. T2 tests a mechanistic precondition of H2 (did gateway latency actually spike) rather than an unidentified exposure-outcome causal contrast, so it falls under the "independent evidence... falsifies a preregistered necessary prediction without relying on the unidentified contrast" carve-out and the refutation stands even though H2 is a causal claim. Therefore, per the closed status set, H2 is REFUTED.
```

### d5-unrepeatable-1 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "REFUTED when the hypothesis's declared necessary prediction failed under an adequate test, UNRESOLVED otherwise." Also: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." And: "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."

REASONING: H2's necessary prediction is the H2-TRUE prediction (gateway p95 rises >20% relative); its failure is what refutes H2. T2's reconciled Outcome is CONTRADICTED — the observed change was +3.7% relative, well inside the flat/noise band, so the necessary prediction failed. The test is adequate: the preregistered data-validity check established a ~0.4% detection limit far below the 20% threshold, so a reading either way discriminates on its own, and the free check (commands, outputs, method, grain, window) found no fault in the worker's return. The only outstanding issue — that the return could not be re-run to confirm because the source is metered and the budget is spent — is exactly the case the skill designates as a limitation to state, not a verification to claim, and explicitly not a fourth outcome that overrides the worker's own CONTRADICTED. It is not an established deviation and there is no execution-record conflict, so it does not downgrade the outcome to NON_DISCRIMINATING or bar deriving status from it. With no adequate test contradicting this one, and the necessary prediction failed under an adequate test, H2's status is REFUTED, carrying forward the unverified-return limitation into the report.
```

### d5-unrepeatable-2 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." And: "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."

REASONING: T2's reconciled Outcome cell is CONTRADICTED, and the reconciliation is settled and not mine to revisit. CONTRADICTED here means the observed gateway p95 change (+3.7%) satisfies H2's own refutation condition — flat/noise-level change (<10% relative) — which the ledger's Hypotheses row states as the necessary prediction whose failure refutes H2. The "unverified worker return" limitation attached to T2 does not create a fourth outcome or downgrade the result to NON_DISCRIMINATING; the skill is explicit that the Outcome cell keeps the worker's stated outcome with the limitation recorded beside it, and that the free-check-found-no-fault-but-can't-reconfirm situation is "a limitation to state, not a verification to claim" — not a reason to alter the outcome. The test is adequate: the preregistered Data Validity section establishes the `gateway_lat` field as a full census with a ~0.4% detection limit, far below the 20%-relative threshold H2's prediction turns on, so "a reading either way therefore discriminates on its own" and no sensitivity check is outstanding. With outcome CONTRADICTED on the necessary prediction under an adequate test, the closed status set yields REFUTED. The unverified-return limitation should be carried into the report as a caveat on confidence, but it does not move the status into UNRESOLVED, which the skill reserves for cases where the necessary prediction did not fail under an adequate test (or where an established deviation left the prediction inadequately tested — not the case here, since the free check found no fault).
```

### d5-unrepeatable-3 (scored-pre)

```markdown
H2 STATUS: REFUTED

GOVERNING SKILL TEXT: "Derive hypothesis status from the latest effective outcome of each test entry (the original outcome unless a dated amendment supersedes it); never edit status directly. The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." Also: "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it. Do not reach for `NON_DISCRIMINATING` here either — it says a test could not discriminate, not that you doubt a return which, if honest, discriminated fine."

REASONING: T2's reconciled Outcome cell is CONTRADICTED, and that reconciliation is settled and not mine to revisit. The ledger's own hypothesis row states the necessary prediction in refutation terms: a flat gateway p95 (<10% relative) between 2026-06-10 and 2026-06-11 refutes H2, and the observed change (+3.7%) is flat by that definition — the necessary prediction (a material rise) failed to materialize. The "unverified worker return" note is a limitation attached to that outcome, not a fourth outcome and not grounds to downgrade to NON_DISCRIMINATING per se: the skill says the Outcome cell keeps the worker's own value and the limitation sits beside it. Adequacy of the test itself is independently established in Data validity (preregistered before any return arrived): the 0.1ms/~0.4% detection limit sits far below the 20% threshold H2 predicts, so a reading either way discriminates, and the free check found no fault in method, grain, or window. With the necessary prediction failing under an adequate, discriminating test, and no established deviation or conflicting execution record to unsettle it, the closed status set gives REFUTED. The unverified-return caveat still belongs in the report as a limitation on how firmly established that refutation is, but it does not itself change the derived status to UNRESOLVED.
```

### d6-support-conflict-1 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: No. H2 must not be reported as best supported. The status set is closed to `REFUTED`/`UNRESOLVED`, and T2's outcome is `CONSISTENT` — it did not fail H2's necessary prediction, so H2 is not `REFUTED` and defaults to `UNRESOLVED`. Clearing "best supported" additionally requires "at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals," but T2's `CONSISTENT` outcome rests on an unverified return (conflicting execution records: Command 1 names `--day 2026-06-10` while its own quoted output reads `day=2026-06-09`), and the skill explicitly bars using such a result as established or action-ready. Since the only evidence for H2 cannot be treated as established, it cannot supply the discriminating `CONSISTENT` outcome the bar requires — even though both rivals H1 and H3 are `REFUTED`, having no competing rival does not substitute for H2 clearing its own evidentiary leg of the bar.

GOVERNING SKILL TEXT: "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "`SUPPORTED` is not a status; \"best supported\" is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."

REASONING: T2's execution records conflict (the command's stated day and the output's stated day disagree), which is exactly the case the skill treats as nothing established and nothing verified — the Outcome cell keeps the worker's reported `CONSISTENT`, but a limitation attaches that bars the conclusion from treating that result as established. Deriving H2's status, the necessary prediction (flat gateway p95 refutes H2) did not fail — T2 came back `CONSISTENT`, not `CONTRADICTED` — so H2 cannot be `REFUTED`, leaving `UNRESOLVED` as the only closed-set option. For "best supported," even though both rival hypotheses (H1, H3) are cleanly `REFUTED` on unfaulted tests, the bar also demands a discriminating `CONSISTENT` outcome for H2 itself, and the skill's own language forecloses relying on an unverified return for that purpose. So H2 remains an open, unresolved possibility rather than the reported answer.
```

### d6-support-conflict-2 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: No. H2 may not be reported as best supported. The status set only permits REFUTED or UNRESOLVED, and H2 is not REFUTED because T2's outcome (as reconciled) is CONSISTENT, not a failure of H2's necessary prediction — so by the closed status rule H2 is UNRESOLVED. But clearing the separate "best supported" bar requires a CONSISTENT outcome that counts as discriminating evidence, and the reconciliation already found T2's execution records conflicting (command names 2026-06-10, the quoted output beneath it reads day=2026-06-09) with nothing to resolve which is the error. The skill treats that as "nothing is established" and requires recording the outcome as resting on an unverified return — a limitation that explicitly reaches the conclusion and bars treating the result as established or action-ready. "Best supported" is exactly that kind of action-ready conclusion claim, so it is barred here even though H1 and H3 are both REFUTED and no rival remains standing.

GOVERNING SKILL TEXT: "When the execution records themselves conflict — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing is established, because one resolution has the briefed collection happening with the fault confined to the report of it." / "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "`SUPPORTED` is not a status; \"best supported\" is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."

REASONING: The reconciliation step (already settled, per the packet) found T2's execution records in conflict — the command targets 2026-06-10 but the printed output is stamped day=2026-06-09 — and nothing resolves which record is at fault. Per the skill, that means "nothing is established," and the correct disposition is to keep the worker's own outcome (CONSISTENT) in the Outcome cell while recording a limitation that the result rests on an unverified return — not to invent a fourth outcome or silently downgrade to NON_DISCRIMINATING. At Conclusion time, status derivation only asks whether an adequate test failed the necessary prediction; since T2's outcome is CONSISTENT (the necessary prediction did not fail), H2 cannot be REFUTED, leaving it UNRESOLVED by the closed status set. Separately, "best supported" is basis language with its own bar, and the skill says the unverified-return limitation "reaches the conclusion, where it bars treating the result as established or action-ready" — which is precisely what a "best supported" claim would require of the CONSISTENT outcome. So even though H1 and H3 are REFUTED and no rival remains to out-explain H2, H2 cannot be written up as best supported; it stays UNRESOLVED with the unverified-return limitation carried forward into the report.
```

### d6-support-conflict-3 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED
BEST SUPPORTED: No. H2 is not REFUTED, but it may not be reported as "best supported" — the unverified-return limitation on T2 bars treating that CONSISTENT outcome as established/action-ready, so it cannot supply the discriminating CONSISTENT outcome the "best supported" bar requires, even though the two rivals (H1, H3) are both REFUTED.
GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "Record the fault as a limitation and treat the outcome as resting on an unverified return, however plausible the innocent reading; that limitation reaches the conclusion, where it bars treating the result as established or action-ready." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "'best supported' is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."
REASONING: T2's Outcome cell is CONSISTENT — the execution-record conflict (command names 2026-06-10, quoted output names day=2026-06-09) doesn't change the Outcome cell to a fourth value; it attaches as a limitation instead. Because that outcome is CONSISTENT rather than a failure of H2's necessary prediction (flat gateway p95), no test on the table refutes H2, so under the closed status set H2 is UNRESOLVED, not REFUTED. However, the "best supported" bar needs a CONSISTENT outcome that actually discriminates H2 from its rivals, and the skill is explicit that an unverified-return limitation "bars treating the result as established or action-ready" — i.e., it disqualifies that CONSISTENT outcome from doing the work "best supported" requires, regardless of how plausible the benign reading (a typo in the day argument) looks. So H2 sits as UNRESOLVED with no available "best supported" claim, even though both named rivals (H1, H3) are REFUTED and would otherwise leave the field clear.
```

### d7-support-clean-1 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: Yes — H2 may be reported as "best supported" in the basis/conclusion text (not as a status value). It clears the stated bar: H2 is not REFUTED, T2 produced a CONSISTENT outcome from a test that discriminates H2 from the named rivals (the preregistered data-validity note establishes the field's detection limit, ~0.4% relative, is far below the >20% predicted rise, so a positive reading discriminates on its own with no further sensitivity check outstanding), and both named rivals H1 and H3 are already REFUTED, so no unrefuted rival explains the same drop equally well. The unverified-return limitation on T2 must still be carried into the report — it is a limitation to state, not a verification to claim — but the ledger's own rule for a clean, unfaulted, merely-unconfirmable return does not bar the CONSISTENT outcome from counting toward "best supported"; that stronger bar ("bars treating the result as established or action-ready") is written for the separate case where the free check finds a fault (e.g. conflicting execution records), which is not T2's situation — T2's free check found no fault.

GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "`SUPPORTED` is not a status; "best supported" is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well." / "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it."

REASONING: T2's necessary prediction for H2 (flat gateway p95 <10% relative) did not fail — the worker's return, unfaulted by the free check, showed a +29.5% rise, so H2 cannot be REFUTED, leaving it UNRESOLVED under the closed status set. Separately, the Conclusion section's "best supported" bar is a basis-text judgment, not a status, and its three literal conditions are all met: not REFUTED, a discriminating CONSISTENT outcome exists (T2, discriminating on the preregistered detection-limit argument alone), and no unrefuted rival remains since T1 and T3 already reconciled H1 and H3 to REFUTED. The reconciliation notes T2 rests on an unverified worker return only because the metered source's budget is exhausted and a clean-looking return could not be re-confirmed — the skill treats that specific case (free check found no fault) as a limitation to disclose, not grounds to demote the outcome or to bar it from supporting "best supported" language; the stronger conclusion-blocking bar applies only when the free check itself surfaces a fault (e.g., conflicting execution records), which did not happen here.
```

### d7-support-clean-2 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: Yes — H2 may be reported as best supported. Basis: H2 is not REFUTED (its necessary prediction — a flat, <10% relative change — did not occur; T2 shows a +29.5% rise, consistent with H2-true); T2's outcome is CONSISTENT and comes from a test the preregistered data-validity note establishes as discriminating (detection limit ~0.4% relative, far below the >20% predicted rise, so "a reading either way discriminates on its own"); and no unrefuted rival remains, since H1 and H3 are both REFUTED and no other explanation is on the table. The T2 "unverified worker return" note is a limitation to disclose alongside the conclusion, not a disqualifier — the skill treats "unverified" as a limitation attached to the standing Outcome cell, not a fourth outcome that blocks status derivation or the best-supported bar.

GOVERNING SKILL TEXT:
"The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise."
"'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it."
"`SUPPORTED` is not a status; \"best supported\" is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."
"When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim."

REASONING: T2's reconciliation is settled and gave H2 an Outcome of CONSISTENT with an "unverified worker return" limitation — the free check found no fault (commands, outputs, method, grain, and window all matched the brief), but a re-run to independently confirm wasn't possible under the spent, metered budget. Per the skill, this unverified status is explicitly "a limitation to state, not a verification to claim" and does not become a fourth outcome; the Outcome cell stands as CONSISTENT. At Conclusion, status is derived solely from whether the necessary (refuting) prediction failed under an adequate test — it did not, since T2 shows the material rise H2-true predicted rather than the flat change that would refute it — so H2 is UNRESOLVED, never REFUTED. Because H2 clears the three-part best-supported bar (not REFUTED, a discriminating CONSISTENT outcome, no unrefuted rival), it may be reported as best supported in the `basis` cell, with the unverified-return caveat carried into the report's limitations section rather than into the `status` cell.
```

### d7-support-clean-3 (scored-pre)

```markdown
H2 STATUS: UNRESOLVED

BEST SUPPORTED: Yes, H2 may be reported as "best supported" (in the basis cell, not the status cell). It clears the stated bar: H2 is not REFUTED, T2 returned a CONSISTENT outcome (necessary-prediction-for-refutation did not occur — gateway p95 rose +29.5%, not flat), and the only rivals on the table, H1 and H3, are already REFUTED, so no unrefuted rival explains the 2026-06-11 conversion drop equally well. The unverified-return limitation on T2 must still be stated alongside the conclusion, but it does not convert CONSISTENT into a fourth outcome or downgrade it, because the free check found no fault in the return.

GOVERNING SKILL TEXT: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." / "When neither is available — metered source, budget spent, and a return you cannot fault on its face — record that the verdict rests on an unverified worker return. That is a limitation to state, not a verification to claim." / "'Unverified' is that limitation, not a fourth outcome: the Outcome cell still holds the worker's own `CONSISTENT`, `CONTRADICTED`, or `NON_DISCRIMINATING`, with the limitation recorded beside it." / "`SUPPORTED` is not a status; 'best supported' is conclusion language and must clear a stated bar: the hypothesis is not `REFUTED`, at least one `CONSISTENT` outcome came from a test that discriminates it from the named rivals, and no unrefuted rival explains the same observations equally well."

REASONING: T2 was reconciled with Outcome = CONSISTENT (H2-TRUE prediction held: gateway p95 rose 29.5%, well outside the pre-registered detection limit, so the reading discriminates). The refutation condition for H2 (flat p95, <10% relative) did not occur, so no adequate test failed H2's necessary prediction — under the closed status set, that leaves H2 UNRESOLVED, never REFUTED, regardless of the return's unverified status. The metering/budget situation is explicitly the milder case the skill names ("a return you cannot fault on its face") rather than the harsher conflicting-execution-records case that bars treating a result as "established or action-ready" — so the limitation is recorded beside the outcome, not used to discard it or force NON_DISCRIMINATING. Turning to the summary table, H2 is not REFUTED, its CONSISTENT outcome came from the one test built to discriminate H2-true from H2-false, and both named rivals (H1, H3) are already REFUTED with clean, unfaulted returns — so nothing unrefuted competes to explain the same drop. That satisfies all three conditions of the "best supported" bar, so H2's basis cell may say "best supported," carrying the unverified-return limitation as a caveat, while its status cell stays UNRESOLVED.
```
