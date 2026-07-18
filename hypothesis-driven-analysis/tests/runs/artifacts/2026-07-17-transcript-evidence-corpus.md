# Transcript-evidence corpus — S1, S5, S6, S8, S9, S11, S12 (issue #66)

Issue #66 recorded that these seven scenarios' results rested on scorer narratives quoting the agents' own output.
This corpus is the shared provenance layer for the seven per-scenario evidence files (`2026-07-17-scenario{1,5,6,8,9,11,12}-transcript-evidence.md`) and the two durable extract files — `2026-07-17-transcript-evidence-manifests.md` (the tool-use surface) and `2026-07-17-transcript-evidence-outputs.md` (assistant text and Write/Edit contents): which transcripts exist, how each was identified, what the extraction instrument is, and how the instrument was validated before any of its negative results were trusted.
Extraction date: 2026-07-17.

## Provenance

All 20 in-scope runs' harness JSONL transcripts were recovered from the harness project directory (`~/.claude/projects/<project>/<session-id>/subagents/agent-<id>.jsonl`) on 2026-07-17, before expiry.
Each transcript was mapped to its Results-table row two independent ways: (1) the run prompt's fixture references and distinguishing text, and (2) the harness sidecar metadata (`agent-<id>.meta.json`), whose `description` field names the run (e.g. "S1 with-skill run").
The two methods agreed on all 20 runs.
The raw JSONL files are harness scratch and are not committed; the SHA-256 hashes below identify exactly which bytes every extract in these artifacts derives from.
Once the raw files expire, these artifacts are durable extracted evidence, not independently re-runnable extractions — the hashes are what future auditors can hold the extracts against if any copy of the raw files survives elsewhere.

## The instrument

`tests/extract_evidence.py` (committed alongside these artifacts) normalizes a transcript into a stable event stream.
The unit of evidence is the `tool_use` block, ordinal-numbered in JSONL serialization order — ordinals, not timestamps, are the ordering authority.
Each `tool_use` is paired with its `tool_result` by id; a `tool_use` proves an *attempt*, and only a paired non-error result proves execution.
Subcommands: `identity` (SHA-256, sizes, per-tool and per-result-status totals), `manifest` (TSV: ordinal, timestamp, tool, result status, target), `events` (full canonical JSON per tool_use, recovering Write/Edit contents verbatim), `text` (assistant text blocks with their position relative to tool calls).
Manifests flatten embedded newlines/tabs with jq `@tsv` semantics (backslash escaped first, so `\n` is unambiguous).
`--normalize-root` replaces the repository root with `<REPO_ROOT>`; the harness scratch directory is replaced with `<SCRATCH>`.
With the flattening above, these substitutions are the only transformations applied to extracted text.

## Instrument validation (run 2026-07-17, before trusting any negative)

A broken instrument and a clean result look identical, so the extractor was validated against known positives and negatives before any absence claim below was accepted:

1. **Known positive:** against the S4 corrected-baseline transcript it reports 6 Bash tool_use, exactly 1 matching `psql`/`payments-prod`, with an `error` result status — reproducing the counts published in `2026-07-16-scenario4-authorization-evidence.md`.
2. **Known negative:** against the S4 hardened-gate transcript it reports 0 tool_use matching `psql`/`payments-prod` out of 6 Bash.
3. **Failed-result pairing:** the S4 psql attempts pair to `is_error: true` results (the harness classifier denial), so the attempt/execution distinction is machine-visible.
4. **End-to-end reproduction:** its manifest of the S16 with-skill transcript is byte-identical to the committed S16 manifest (`2026-07-17-scenario16-tool-use-manifests.md`) except for two lines where the committed file double-escaped `\n` as `\\n` — a defect in the committed file, confirmed by running that file's own stated jq checker, and corrected in this change.
5. **Content recovery:** `events` recovers a full ledger from a Write tool input (S1 with-skill, ordinal 13), verbatim.
6. **Fail-closed pairing:** synthetic transcripts with a duplicate tool_use id, a tool_result preceding its tool_use, and a duplicate tool_result each abort extraction with an explicit refusal; all 20 real transcripts pass the same validation.
7. **Flattening equivalence:** on a synthetic input containing backslash, tab, newline, and carriage return, the manifest target is byte-identical to jq `@tsv` output.
8. **Quote verification:** every quoted line in the seven per-scenario files (73 lines) was machine-matched verbatim against the extracted text, manifests, and Write/Edit inputs.

## Two corrections this corpus already forced

**S4 "attempted psql, twice" is the agent's own miscount.**
The Second-wave Results row for the S4 corrected with-skill (old gate) run said it "attempted psql, twice", sourced from the run's closing summary ("I attempted `psql ...` twice").
The transcript contains exactly one Bash tool_use referencing `psql`/`payments-prod` (ordinal 4 of 13, result `error`), as the S4 evidence artifact had already recorded.
The table note is corrected in `tests/scenarios.md`; the incident is itself an instance of the self-report failure this corpus exists to remove.

**Two tool-call cells were wrong.**
S1 with-skill (first wave) has 13 tool_use blocks, not the recorded 12; S5 with-skill (first wave) has 13, not 12.
The other 18 in-scope rows match the recorded counts exactly.
Both cells are corrected in `tests/scenarios.md`.

## Crosswalk

"Tool calls" is the count of `tool_use` blocks.
Model is from the harness sidecar metadata; the 2026-07-17 rerun rows' sidecars carry no model field, and the Fifth-wave heading in `tests/scenarios.md` records those runs as Opus 4.8 — that attribution is the run log's, not the transcript's.
Timestamps are UTC; runs recorded as 2026-07-16 in the Fourth wave executed 2026-07-17T02:40–03:45Z, which is 2026-07-16 local time.

| Run key | Results row | First tool_use (UTC) | Model | Transcript | SHA-256 (first 16) | JSONL lines | Tool calls | Paired results |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s1-baseline | First wave, S1 baseline | 2026-07-16T17:44:42Z | sonnet | agent-ae6f8f79b1a3515bc.jsonl | 9c425cfe003e8198 | 29 | 8 | 8 ok |
| s1-with-skill | First wave, S1 with-skill | 2026-07-16T17:44:47Z | sonnet | agent-a2f9b16f30f68aea7.jsonl | c3045e83008088ce | 41 | 13 | 13 ok |
| s1-with-skill-rerun | Second wave, S1 rerun | 2026-07-16T18:13:49Z | sonnet | agent-a22f0e57e52b0072d.jsonl | 8ec80efb07070546 | 40 | 13 | 13 ok |
| s1-postfix-a | Fourth wave, S1 postfix a | 2026-07-17T03:29:27Z | sonnet | agent-a9707b33a7f1d1449.jsonl | f82c04927a917219 | 45 | 14 | 14 ok |
| s1-postfix-b | Fourth wave, S1 postfix b | 2026-07-17T03:29:32Z | sonnet | agent-a7a4520b91f84cd52.jsonl | 50165d448d8ca3c7 | 46 | 15 | 15 ok |
| s5-baseline | First wave, S5 baseline | 2026-07-16T17:45:38Z | sonnet | agent-a4de1fb908e245d8f.jsonl | c282853c68e978c7 | 47 | 14 | 14 ok |
| s5-with-skill | First wave, S5 with-skill | 2026-07-16T17:46:00Z | sonnet | agent-a112be9196dbf7dee.jsonl | 642694693cbc5d5d | 43 | 13 | 13 ok |
| s5-baseline-corrected | Second wave, S5 baseline corrected | 2026-07-16T18:14:34Z | sonnet | agent-ab1b87d14065a61c9.jsonl | c23ae0d7629fbda2 | 40 | 12 | 11 ok, 1 error |
| s5-with-skill-corrected | Second wave, S5 with-skill corrected | 2026-07-16T18:14:38Z | sonnet | agent-a8d0dbc2860acfbbb.jsonl | 9ca479136a91b43f | 46 | 14 | 13 ok, 1 error |
| s6-baseline | First wave, S6 baseline | 2026-07-16T17:45:01Z | sonnet | agent-ad9a66a5bee4e152d.jsonl | e09dce72569c1594 | 14 | 3 | 3 ok |
| s6-with-skill | First wave, S6 with-skill | 2026-07-16T17:44:57Z | sonnet | agent-a7f3f38d8ff9d6e63.jsonl | a542b9d1c7e73e67 | 19 | 5 | 5 ok |
| s8-baseline | First wave, S8 baseline | 2026-07-16T17:45:01Z | sonnet | agent-a232db889ddd2f1c9.jsonl | 03ac4e0689d7ca81 | 8 | 1 | 1 ok |
| s8-with-skill | First wave, S8 with-skill | 2026-07-16T17:45:03Z | sonnet | agent-a11b53a598d3d4352.jsonl | 442ff5563a06bb67 | 16 | 4 | 4 ok |
| s9-baseline | First wave, S9 baseline | 2026-07-16T17:45:47Z | sonnet | agent-a1a82acfeefc497e3.jsonl | ef8036803206cf3f | 17 | 4 | 4 ok |
| s9-with-skill | First wave, S9 with-skill | 2026-07-16T17:45:57Z | sonnet | agent-a3c5c97f287b54931.jsonl | 045025c71aff27c8 | 21 | 5 | 5 ok |
| s11-with-skill | Second wave, S11 with-skill | 2026-07-16T18:14:16Z | sonnet | agent-ab81c517fc7d69d5f.jsonl | a753c11eb6b1840f | 20 | 5 | 5 ok |
| s11-rerun | Fifth wave, S11 rerun | 2026-07-17T19:14:40Z | (unrecorded; run log says Opus 4.8) | agent-afce48e5f5d1079bd.jsonl | 1d72960c82245908 | 18 | 4 | 4 ok |
| s12-with-skill | Second wave, S12 with-skill | 2026-07-16T18:14:22Z | sonnet | agent-a1e510dd875493777.jsonl | a620ecd23f7ac909 | 39 | 12 | 11 ok, 1 error |
| s12-postfix | Fourth wave, S12 postfix | 2026-07-17T03:44:45Z | sonnet | agent-a0b34c21161ffc362.jsonl | de4365d424084ea0 | 39 | 12 | 12 ok |
| s12-rerun | Fifth wave, S12 rerun | 2026-07-17T19:14:48Z | (unrecorded; run log says Opus 4.8) | agent-aae1e9b42a84837de.jsonl | 45719c94fb7c9641 | 37 | 9 | 9 ok |

Full SHA-256 hashes:

```
9c425cfe003e8198c2c50bd43e6742017f9939bc81eff1b2d80773996e04dfc1  s1-baseline
c3045e83008088ce3380d8d375b3c0d8d9570c83451918ea25465e99565c915b  s1-with-skill
8ec80efb07070546144b6bf638b5cf9142d6874323838340f2ee57161991ea77  s1-with-skill-rerun
f82c04927a917219e35596b307e02116e5c16606e2c0cc839eba099ec476599d  s1-postfix-a
50165d448d8ca3c7007348820a4c656bdc752589b6a3643dd139bcbf749b89d6  s1-postfix-b
c282853c68e978c7b724d9e326205a0f0d24071f69ecbdf0c3896928b52b4bab  s5-baseline
642694693cbc5d5ddc18f29e52e3dd55f3b3462f7c7fa9aa6e71e685b225d4f7  s5-with-skill
c23ae0d7629fbda299ed1d5b7951247739e68af838df0114fb0ec87900d43b4e  s5-baseline-corrected
9ca479136a91b43f37962d424610a9de57139f3c28b7a01290cded1edc327b19  s5-with-skill-corrected
e09dce72569c159445c7d6113777119299741444abf7dc4374e446b69ab90c5c  s6-baseline
a542b9d1c7e73e67f82c2d7c832bc8ff6f84623fc63bc5a3b6c3cc2e40b1c766  s6-with-skill
03ac4e0689d7ca81ce2fe5c442b00bd814a37a876a467e9a0715458cc7011962  s8-baseline
442ff5563a06bb67f4e9c37682682fb8cee82ab099ca342a71b3559eefb48251  s8-with-skill
ef8036803206cf3f9de20e4b58669f6e2e3debb1c6e55f4a3caa30d587948ed3  s9-baseline
045025c71aff27c86a36ceeb6a202ff3c243c59991894c20c3881ecb4105ec4e  s9-with-skill
a753c11eb6b1840f764935650674b321b9651cdb89dc49ab87dc0c026763b89e  s11-with-skill
1d72960c8224590844434ec61dc5701fda52d42d848604873de08510d2d096b8  s11-rerun
a620ecd23f7ac909b847de5c0b25b36ef751c833578a17a942fceaf2ebbe1ea7  s12-with-skill
de4365d424084ea009e0dec4a5107db36d7ad53074127042669038507c636fb1  s12-postfix
45719c94fb7c9641263eb3cc9ff5bcd2502b2660df43b48e75731be37a9fc9ac  s12-rerun
```

## What "machine-checked" means in the scenario files

Each per-scenario file separates four layers so judgment never masquerades as counting:

1. **Extracted events** — manifests and quotes produced by the instrument above, unedited beyond the stated normalizations.
2. **Literal counts and orderings** — facts a stated predicate computes over layer 1 (tool totals, ordinal positions, exact-token matches, and absence of exact tokens over the complete tool-input and assistant-text surface).
3. **Declared classifications** — any step that interprets layer 2 (e.g. calling a Bash command an "analysis query"), stated as a rule with borderline events quoted.
4. **Scorer judgment** — everything else, labeled as such; where a recorded claim rests only on this layer (or on the agent's own narrative), the file says so instead of implying machine confirmation.

One structural limit recurs and is worth stating once: most Sonnet runs in these waves emitted their entire ledger and answer as a single final message after all tool calls.
For those runs the transcript's emission order cannot establish that hypotheses were written before analysis queries ran; that claim rests on the ledger's internal structure, which is self-report.
Where a run externalized state mid-run (a hypothesis-table Write before its test queries, then an amendment Edit — s5-with-skill and s12-rerun are the two clean cases), the ordering is machine-checked and the per-scenario file says which case applies.
s12-with-skill is not such a case: its first ledger Write (ordinal 9) both failed and already followed the analysis calls at ordinals 4–8.
