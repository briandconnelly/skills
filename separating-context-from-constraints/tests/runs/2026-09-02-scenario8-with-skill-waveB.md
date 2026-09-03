# Scenario 8 — upload-router, With-Skill, three reps (Wave B rerun, R5 regression, scenario 14 known positive)

```
Date: 2026-09-02
Run: with-skill
SKILL.md blob: 2cb876f4010f55a3259fe740a46d1e8aaea78eea
Commit: a9f0116 (branch `separating-context-wave3`, Wave B wording; not on `main`)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md: read that file and any file it references under /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/references/. Do not read any other file anywhere, do not read anything under any tests/ directory, do not load any skill through the harness, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under the preregistration's Rerun classification; per-defect tables transcribed and reconciled by a Claude subagent (opus) against the archived outputs; tool calls extracted by script
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script)
```

## Scoring

Assertion labels follow the order of the bullets in `tests/scenarios.md`, scenario 8: A1 one material R5 finding on the pair; A2 the finding attaches to and quotes both statements; A3 the rewrite presents both precedence policies as author decisions; A4 the specific-over-general reading may be identified but is not silently selected.
The A1 column is also this cell's second role: it is the live known positive scenario 14 cites, so an arm reading the current `SKILL.md` still finds a reachable R5 conflict.

| Rep | A1 material R5 on the pair (known-positive evidence) | A2 attaches to and quotes both statements | A3 both policies as author decisions | A4 specific-over-general not silently selected | E2 |
| --- | --- | --- | --- | --- | --- |
| 1 | ✓ "**R5 Reachable precedence**", severity material | ✓ "Location: lines 5–6 (attached to the pair)", both sentences quoted | ✓ "requires an author decision between two plausible precedence policies", both spelled out | ✓ "the natural specific-over-general interpretation, but the auditor must label it as an assumption rather than silently selecting it" | 0 |
| 2 | ✓ "**R5 Reachable precedence**", severity material | ✓ "Location: lines 5–6 (the pair)", both sentences quoted | ✓ "an author decision between two plausible precedence policies; the auditor does not select one" | ✓ "the natural specific-over-general reading, but an assumption until the author confirms it" | 0 |
| 3 | ✓ "**R5 Reachable precedence**", severity material | ✓ "Location: lines 5–6 (the pair)", both sentences quoted | ✓ "an author decision between the two plausible precedence policies; the auditor does not select one" | ✓ "The EU-wins reading is the natural specific-over-general interpretation, but it is an assumption, not something the document states." | 0 |

Scored assertions: **4/4 ×3.**
R5 conflict reported 3/3, which is the known-positive evidence scenario 14 cites.

E9c: guard-lines true ×3; classification-table true ×3 (reps 1 and 2 print a classification table, rep 3 a classification paragraph, which is scored true per the scenario-16 precedent at `2026-09-02-scenario16-with-skill.md`); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** Nothing changed against the archived cell: the pair still draws one material R5 finding in every rep, quoted on both statements, with the two precedence policies offered as an author decision and the specific-over-general reading labelled an assumption.
This is the regression the deleted `:59` field/object scope guard could have disturbed, and it did not: the guard's removal leaves R5's reach on a genuine two-rule collision intact.
That is what makes this cell admissible as scenario 14's known positive: it ran against the same `SKILL.md` blob `2cb876f4010f55a3259fe740a46d1e8aaea78eea`, the same model and the same harness as scenario 14's arms, and produced a found conflict 3/3.
The two cells were dispatched in different batches of the same rerun session — scenario 8's reps at 2026-09-02T20:31:40Z, 20:31:43Z and 20:31:46Z, scenario 14's at 20:35:30Z, 20:35:35Z and 20:35:40Z, about four minutes apart.
That deviates from the preregistration's N6 wording, which asks for the arms to be "dispatched together" and the known positive to run "in the same batch", while meeting its stated purpose of proving the instrument under the same configuration, same blob, same model and same harness; it is recorded here as a process note and whether the cell stands is an author decision.

## Scored Outputs (verbatim)

### With-skill, rep 1

> ## Audit: `upload-router`
>
> ### Classification
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Always use the global endpoint for uploads." | Binding rule |
> | 6 | "For EU customer uploads, use the EU endpoint." | Binding rule |
>
> The document contains no load-bearing facts and no discretionary context; both statements direct behavior.
>
> ### Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (attached to the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: the two rules prescribe incompatible outcomes for the same decision on a realistic input — an upload from an EU customer. Line 5 says the global endpoint is used for every upload ("Always"), line 6 says the EU endpoint is used for this subset, and nothing in the document states which governs. A reader following line 5 literally routes EU uploads to the global endpoint; a reader applying specific-over-general routes them to the EU endpoint. The document does not determine the answer.
> Severity: material — the defect could plausibly change behavior (which endpoint receives EU uploads).
> Suggested rewrite: this requires an author decision between two plausible precedence policies.
> If the EU exception wins: "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global-endpoint default."
> If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not route EU uploads to the EU endpoint." (This reading makes line 6 dead text; the author would also need to decide whether to delete it or keep it as nonbinding context explaining that an EU endpoint exists.)
> The EU-wins reading is the natural specific-over-general interpretation, but the auditor must label it as an assumption rather than silently selecting it.
>
> ### Not flagged (false-positive guards)
>
> - **R1**: both rules are list items in a labeled `## Rules` section with no interleaved context; they are structurally distinguishable.
> - **R2**: "Always" and the bare imperative "use" both signal mandatory strength; no hedge is present.
> - **R3**: the trigger "EU customer uploads" is an ordinary domain predicate the reader can decide from the situation, and the result (which endpoint received the upload) is checkable against tool calls or request logs.
> - **R4**: each rule states a single obligation.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1, minor 0.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity.
>
> This is a compact, well-structured document: both statements are correctly placed and marked as rules, carry explicit mandatory strength, and are individually verifiable. Its single defect is that the two rules directly conflict on the realistic case of an EU customer upload and the document does not say which wins. Because the choice determines where EU uploads are routed, this is an author decision the document must resolve before it can be followed unambiguously.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.

### With-skill, rep 2

> # Audit: `upload-router`
>
> ## Classification
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Always use the global endpoint for uploads." | Binding rule — marked (list item in `## Rules`), mandatory ("Always"), atomic, checkable against tool calls/request targets. |
> | 6 | "For EU customer uploads, use the EU endpoint." | Binding rule — marked, imperative, atomic; "EU customer upload" is an ordinary domain predicate the reader can decide from the situation, and the endpoint used is observable. |
>
> No discretionary context or load-bearing facts appear anywhere in the document, so there is nothing misplaced under R1, no hedged strength under R2, no untestable trigger or result under R3, and no bundled obligations under R4.
>
> ## Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: the two rules prescribe incompatible outcomes for the same decision on a realistic input — an upload from an EU customer. Line 5's "Always" admits no exception, while line 6 directs a different endpoint for a subset of the same uploads. The document does not say which rule wins, so an agent handling an EU upload cannot determine the required endpoint from the document alone.
> Severity: material.
> Suggested rewrite: this is an author decision between two plausible precedence policies; the auditor does not select one.
> - If the EU-specific rule wins (the natural specific-over-general reading, but an assumption until the author confirms it): "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global default."
> - If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not route EU customer uploads to the EU endpoint." (This makes the current line 6 dead text and it should be removed.)
>
> **Not flagged (false-positive guards)**
> - Line 6 is not an R2 finding: the imperative "use the EU endpoint" carries no hedge, so its strength is not ambiguous — the defect is the unresolved conflict with line 5, not unclear binding.
> - Neither rule is an R3 finding: which endpoint a request targets is observable in tool calls, and "EU customer" is a decidable domain predicate. The document does not define what "the global endpoint" and "the EU endpoint" resolve to, but that is a missing load-bearing fact possibly supplied by a parent layer or tool description; cross-layer completeness is outside this audit's scope.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1 (R5), minor 0.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity. Safety notes: none.
>
> The document is structurally sound on the context/constraints axis — both statements are clearly marked, unhedged, atomic binding rules with nothing else mixed into the rule section. Its single defect is a reachable precedence gap: an EU customer upload triggers both rules and they demand different endpoints, with no stated winner. Resolving that requires the author to choose which rule governs; once chosen, the rewrite above collapses the pair into one condition–action–exception unit with explicit precedence.

### With-skill, rep 3

> ## Audit: `upload-router`
>
> Line references use the document as given: line 1 `# upload-router`, line 3 `## Rules`, line 5 first bullet, line 6 second bullet.
>
> ### Classification
>
> Both statements direct behavior, so both are binding rules. The document contains no load-bearing facts and no discretionary context; the `## Rules` section holds only directives, and each rule stands as its own list item.
>
> ### Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: an EU customer upload is a realistic input on which both rules apply and prescribe incompatible outcomes — one endpoint versus the other — for the same routing decision. The first rule's "Always" explicitly claims no exceptions, so the second rule cannot be read as a carve-out the document has already granted. Nothing in the document says which rule governs.
> Severity: material — an agent could route an EU customer upload to either endpoint and be following the document.
> Suggested rewrite: this is an author decision between the two plausible precedence policies; the auditor does not select one.
> - If the EU rule wins (specific over general): "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global default."
> - If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not use the EU endpoint." (Under this choice the second rule is unreachable and should be removed rather than left as a dead rule.)
>
> The EU-wins reading is the natural specific-over-general interpretation, but it is an assumption, not something the document states.
>
> ### Not flagged (false-positive guards)
>
> - R1: both rules are list items under a labeled rule section; neither is embedded in informing prose. No finding.
> - R2: "Always" is explicit mandatory strength; the second rule is an unhedged imperative. Neither is ambiguous. The unresolved override is a precedence question (R5), not a strength question.
> - R3: "uploads" and "EU customer uploads" are ordinary domain predicates the reader can decide from the situation; the result (which endpoint was called) is checkable against tool calls. No finding.
> - R4: each rule states a single obligation. No finding.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1, minor 0.
> No finding carries a secondary rule id, so the per-rule total equals the one finding counted by severity.
>
> The document is structurally clean: rules are marked, grouped, unhedged, atomic, and verifiable, with no context mixed into the rule section. Its single defect is that its two rules collide on a realistic input — EU customer uploads — and the "Always" wording of the first rule forecloses reading the second as an implied exception, so precedence must be stated explicitly. Which rule wins is an author decision; the rewrite cannot preserve semantics until that is chosen.
