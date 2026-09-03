# Scenario 12 — R1's compact/long criterion, With-Skill, three reps (Wave B rerun, W9, R1 marking criterion)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); scenario 12 ran as nine independent dispatches, three per sub-case, in batches 2–4, none of which failed; each arm's prompt was the quoted preface followed by the 12a, 12b, or 12c fixture prompt from `../scenarios.md`, verbatim
```

## Scoring — 12a (`release-notes-helper`)

| Rep | Findings | Section demand? | E2 (strict) | E2 (per-statement) | Ground quoted |
| --- | --- | --- | --- | --- | --- |
| 1 | none — "**Result: clean — no findings.**" | no | 0 | 0 | "a document whose rules are already marked and grouped does not owe a dedicated rule section, whatever its headings; the `## Usage` heading is not a defect" |
| 2 | none — "**Result: clean — no findings.**" | no | 0 | 0 | "per R1 it does not owe a separate rule section regardless of heading name" |
| 3 | none — "**Clean — no findings.**" | no | 0 | 0 | "a document whose rules are already marked and grouped does not owe a dedicated rule section, whatever its headings" |

Standing assertions: 12a-1 (no R1 finding demands a dedicated rules section) passes 3/3; 12a-2 (E2 is 0) passes 3/3.
Scored assertions: **2/2 ×3.**

E9c: guard-lines true ×3; classification-table true ×3 (reps 1–3 each print a per-statement classification table); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The archived cell was E2 0 ×3 with a `W9-verdict` section demand in reps 2 and 3; under the Rerun classification that demand is now an E2 false positive, and it did not occur in any rep.
All three reps reach the outcome archived rep 1 reached alone, and each cites the new "marked and grouped" clause by name.
W9's 12a half closes.

## Scoring — 12b (`provision_workspace`)

Sentences are numbered as in the fixture description, in reading order: S4 "Seat count must be at least one and at most the contract seat cap.", S5 "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise.", S7 the duplicate-call sentence ("Never call this tool twice for the same account_id without first checking get_provision_job, because …").
Rep 2 numbers the same sentences 5, 6, and 8, and rep 3 numbers the duplicate-call sentence 7; the fixture sentences, not an arm's numbering, are the units below.

| Rep | Findings (rule id → sentence) | R1 finding? | Units a rewrite would alter (strict) | E2 (strict) | E2 (per-statement) |
| --- | --- | --- | --- | --- | --- |
| 1 | one finding, R3 with secondary R5 → S4 and S5 (one pair) | no | S4's lower-bound clause ("at least one"), S5 | 2 | 2 |
| 2 | one finding, R3 minor → S7 | no | S7's rule clause | 1 | 1 |
| 3 | Finding 1, R3 material → S7; Finding 2, R5 material → S4 and S5 | no | S7's rule clause, S4's lower-bound clause, S5 | 3 | 3 |

Per-statement derivation (the Scoring record gives strict counts only): count each distinct fixture sentence a finding names, and count a finding pair carrying two rule ids on the same sentence once.
Rep 1's single R3+R5 pair names S4 and S5 in its location and quotes both, so it counts once for S4 and once for S5 — 2.
Rep 2's finding names S7 alone — 1.
Rep 3's two findings name S7, and S4 with S5 — 3.
Strict and per-statement agree in every rep here, because no rep alters two clauses of one sentence: rep 1's and rep 3's alternative (b)/(B) rewrites leave "at most the contract seat cap" verbatim and change only the lower bound.

**Unit convention for 12b (controller ruling).** `../wave3-2026-08-07/rescore-2026-09-02.md` carries no clause inventory for 12b, and the archived 12b cell (1, 2, 2) counted flagged fixture sentences, so the rerun counts flagged fixture sentences the same way.
A rationale clause restated in place or dropped inside the flagged sentence's own rewrite is not a separate unit; 12c's S3c counts because the inventory lists it as a unit and the rewrite moves it to a different section.
Footnote: under a full clause inventory rep 3 would count 4, because its alternative (a) rewords the rationale clause ("A second call while the job is pending or done creates a duplicate workspace that support must delete."), which would make 12b's strict total 7 rather than 6; the sentence-unit count is the recorded value and the clause-unit count is given so the reader can reproduce either.
Rep 2's alternatives keep the rationale wording unchanged, so rep 2 stays 1 under both readings.

Standing assertions: 12b-1 (no R1 finding raised merely because the rules live inline in a single description field) passes 3/3 — every rep classifies the document as compact and says so in its own words.
12b-2 (an R1 finding must name retrieval pressure) is vacuous: no rep raises an R1 finding.
Scored assertions: **1/1 ×3**, with 12b-2 vacuous.

E9c: guard-lines true ×3; classification-table true ×3 (reps 1 and 2 print a sentence-classification table; rep 3 assigns the sentences to classes in a classification paragraph); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The archived cell was strict E2 1, 2, 2; the rerun is 2, 1, 3.
The findings moved rather than disappeared: the archived R1 finding on the duplicate-call rationale clause is gone, the archived R3 minor on the seat cap's missing evidence source (archived reps 2 and 3) is gone too — rerun reps 2 and 3 demote that same criticism to an explicit non-finding, "Observation only, not a finding" and "Observation only" — and what remains is the W10-class R3 on the duplicate-call rule (reps 2 and 3) plus new R3/R5 findings on the seat-count and default sentences (reps 1 and 3).
Both sentences are protected by the scenario text, so the findings count as false positives; they are the second open author question and are recorded, not decided, here.

## Scoring — 12c (`backfill-runbook`)

Units are the 12c inventory in `../wave3-2026-08-07/rescore-2026-09-02.md`: S1, S2a, S2b, S3a "Run `make backfill`.", S3b "Never pass `--force`…", S3c the rationale clause, S4a, S4b, B1.

| Rep | Finding | Units the rewrite alters (strict) | E2 (strict) | E2 (per-statement) | S3b moved into `## Rules`? | S4a/S4b, B1 flagged? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | R1 minor on step 3 | S3b (lifted and reworded to "`make backfill`"), S3c (moved to `## Background`) | 2 | 1 | yes | no / no |
| 2 | R1 minor on step 3 | S3a (rewritten as "Run `make backfill` (without `--force`; see Rules)."), S3b, S3c | 3 | 2 | yes | no / no |
| 3 | R1 minor on step 3 | S3b, S3c | 2 | 1 | yes | no / no |

Per-statement counts follow the same rule as 12b: S3b and S3c are the two clauses of one semicolon-joined sentence, so reps 1 and 3 count that sentence once — 1.
Rep 2 additionally rewrites S3a, a separate sentence — 2.
Rep 3's offer to "keep a pointer ('see Rules')" in step 3 is labeled optional and "a presentation choice, not a semantic one", so S3a is not counted for that rep.

Every rep cites the new liftability clause by name: "the rule is liftable — obeying it does not depend on the step's passage" (rep 1), "The rule is liftable: obeying it does not depend on the surrounding step (it names the command it governs)" (rep 2), "The rule is liftable: obeying 'never pass `--force`' does not depend on its position in the step sequence" (rep 3).

Standing assertions: 12c-1 (no finding proposes moving the `--force` prohibition out of step 3) FAILS 0/3 — every rep's rewrite lifts S3b into a `## Rules` section.
12c-2 (the Background paragraph is not flagged) passes 3/3.
Scored assertions: **1/2 ×3.**

E9c: guard-lines true ×3; classification-table true ×3 (reps 2 and 3 print a classification list; rep 1's not-flagged list assigns classes — "procedural" to steps 1, 2 and 4 and "discretionary context" to line 12 — which is `true` on the scenario-16 precedent, where rep 2's not-flagged list was read the same way); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The archived cell was strict E2 3, 3, 3 with S3b moved by no arm; the rerun is 2, 3, 2 with S3b moved 3/3.
The direction reversed: the archived arms left the prohibition in step 3 and reached strict 3 on S3c (R1 on the rationale clause) plus S4a and S4b (R4 splitting step 4), while every Wave B arm lifts the prohibition itself into a dedicated `## Rules` section, citing the new liftability clause.
Step 4 is unflagged in every Wave B rep — each rep names it in its false-positive guards as procedural and therefore out of R4's reach — so the archived R4 pair is the other change against the archive.
Under the registry that move remains an E2 false positive — the 2026-08-24 amendment classes a finding that moves the `--force` prohibition away from the step whose semantics it modifies as a false positive, and the Rerun classification leaves that treatment unchanged — so it is scored as one here.
Whether S3b is in fact liftable under the new R1 or protected as a `## Procedure` step is the open author question; this artifact records the reversal and decides nothing.

## Scored Outputs (verbatim)

### 12a, rep 1

> ## Audit: `release-notes-helper`
>
> **Result: clean — no findings.**
>
> ### Statement classification (two-question litmus test)
>
> | Line | Statement | Directs or informs? | Class |
> |---|---|---|---|
> | 5 | "Drafts release notes from the titles of merged pull requests." | Informs | Load-bearing fact (tool semantics: the source of note content is merged-PR titles; losing it would change what the agent produces notes from) |
> | 9a | "Run it against a milestone." | Imperative grammar, but tells a reader already committed to drafting notes how to invoke the tool | Procedural step, not a binding rule (R1: "a step that only tells a reader already committed to a task how to carry it out is procedural, not binding, however imperative its grammar") |
> | 9b | "Never include pull requests labeled `internal` in the notes." | Directs | Binding rule |
>
> ### Rule check on the one binding rule (line 9b)
>
> - **R1 Distinguishability — passes.** The rule is marked by an imperative sentence with explicit mandatory wording ("Never"). It is not embedded: its paragraph contains only directives (the procedural invocation step and the rule itself), with no facts or background mixed in. The document has labeled sections, so it is long-form, but a document whose rules are already marked and grouped does not owe a dedicated rule section, whatever its headings; the `## Usage` heading is not a defect.
> - **R2 Explicit strength — passes.** "Never" is unambiguous mandatory strength; no hedge.
> - **R3 Verifiability — passes.** Trigger: a merged PR carries the `internal` label (an ordinary domain predicate decidable from the situation). Result: that PR is absent from the notes, checkable against the output.
> - **R4 Atomic obligations — passes.** One obligation, one trigger.
> - **R5 Reachable precedence — passes.** No second rule exists to conflict with it. Line 9a, even under a binding reading, prescribes invocation scope, not inclusion, so the two cannot prescribe incompatible outcomes for the same decision.
>
> ### Not flagged (false-positive guards)
>
> - **Line 5** is a load-bearing fact correctly placed under `## Purpose`, outside any rule text.
> - **Line 9a** is procedural. Even if an author intended it as binding, it would still pass: unhedged imperative (R2), checkable against the tool invocation carrying a milestone argument (R3), single obligation (R4). Its co-location with the rule does not embed the rule, because the paragraph holds only directives.
> - **No rule section** is not a finding: the sole rule is marked inline and there is nothing else to group it with.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (reported separately, excluded from counts).
>
> This compact two-section document contains one load-bearing fact, one procedural invocation step, and one binding rule. The rule is marked with explicit mandatory wording, sits in a paragraph containing only directives, has a decidable trigger and an output-checkable result, carries a single obligation, and has no conflicting peer. Separation of context from constraints is adequate as written; no rewrite is owed.

### 12a, rep 2

> ## Audit: `release-notes-helper`
>
> **Result: clean — no findings.**
>
> ### Classification (two-question litmus test)
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Drafts release notes from the titles of merged pull requests." | Load-bearing fact — informs; defines the tool's input (merged PR titles) and output (release notes). Losing it would make output wrong, but it does not direct behavior. |
> | 9 | "Run it against a milestone." | Directive. Either a procedural step (how to invoke, for a reader already committed to the task) or a binding scope rule; on either reading it is imperative and unhedged. |
> | 9 | "Never include pull requests labeled `internal` in the notes." | Binding rule — mandatory. |
>
> ### Rule checks
>
> - **R1 Distinguishability** — pass. Both directives on line 9 are imperative sentences, and the paragraph they share holds only directives, so neither is embedded in informing prose. The document has labeled sections (long-form), but its rules are already marked and grouped under `## Usage`; per R1 it does not owe a separate rule section regardless of heading name. Line 5 is a fact and is correctly placed outside the directive paragraph.
> - **R2 Explicit strength** — pass. "Never" is explicit mandatory wording; "Run it against a milestone" carries no hedge. No ambiguous strength.
> - **R3 Verifiability** — pass. The `internal` rule has a decidable trigger (a PR carries the label `internal`, observable in repository state) and a result checkable against output (the PR is absent from the drafted notes). The milestone directive is checkable against the tool call or invocation target.
> - **R4 Atomic obligations** — pass. Each sentence states one obligation.
> - **R5 Reachable precedence** — pass. Line 5 describes the input set ("merged pull requests"); it is a fact, not a rule prescribing that every merged PR appear, so it does not conflict with the `internal` exclusion. No pair of rules prescribes incompatible outcomes.
>
> Not flagged (false-positive guard): the `## Usage` heading rather than `## Rules` — R1 does not require a specific heading when rules are marked and grouped. Not flagged: "Run it against a milestone" — even if read as procedural rather than binding, it is a directive, not an informing statement, so it does not embed the neighboring rule.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety note: none — the target contains no auditor-directed instructions.
>
> This compact two-section document keeps its single load-bearing fact (what the tool consumes and produces) in `## Purpose` and its directives together in `## Usage`, each as an unhedged imperative with an observable trigger and result. The one mandatory rule is distinguishable, explicit in strength, verifiable against output, atomic, and free of reachable conflict. No rewrites are owed.

### 12a, rep 3

> ## Audit: `release-notes-helper`
>
> Skill followed: `SKILL.md` plus its one referenced file, `references/example-audit.md`. No other files read, nothing edited.
>
> ### Classification (two-question litmus test)
>
> | Location | Statement | Class |
> |---|---|---|
> | line 5 | "Drafts release notes from the titles of merged pull requests." | Load-bearing fact (informs; losing it would make output wrong — the source of note content is PR titles, restricted to merged PRs) |
> | line 9, sentence 1 | "Run it against a milestone." | Procedural step (directs how to invoke; not a policy whose violation is wrong behavior) |
> | line 9, sentence 2 | "Never include pull requests labeled `internal` in the notes." | Binding rule |
>
> ### Findings
>
> **Clean — no findings.**
>
> Rule-by-rule check of the single binding rule (line 9, sentence 2):
>
> - **R1 Distinguishability** — passes. The rule is marked (imperative sentence with explicit mandatory wording, "Never"). It is not embedded: its paragraph holds only directives (the procedural step and the rule); no facts or background are mixed in. The document has labeled sections, so it is long-form under R1, but a document whose rules are already marked and grouped does not owe a dedicated rule section, whatever its headings. The `## Usage` placement is therefore not a defect.
> - **R2 Explicit strength** — passes. "Never" is unambiguously mandatory; no hedge.
> - **R3 Verifiability** — passes. Trigger is decidable from repository state (a PR carries the `internal` label or it does not); result is checkable against the output (the drafted notes contain or omit that PR).
> - **R4 Atomic obligations** — passes. One trigger, one obligation.
> - **R5 Reachable precedence** — passes. Only one binding rule exists, so no conflict is reachable.
>
> Not flagged (false-positive guards):
>
> - Line 5 is a load-bearing fact correctly placed in `## Purpose`, outside any rule content.
> - Line 9, sentence 1 ("Run it against a milestone.") is procedural — it tells a reader already committed to drafting notes how to scope the run. Per R1, a step of this kind is not binding however imperative its grammar, so it is neither an embedded rule nor context polluting a rule section. Its imperative form also means it does not count as an "informing statement" that would render the adjacent rule embedded.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: none.
>
> The document contains exactly one binding rule, and it is marked, mandatory, verifiable against observable evidence, atomic, and free of any reachable conflict. Its one factual statement sits in a purpose section, and its one procedural instruction sits alongside the rule without diluting it. Nothing in the document requires an author decision, and no rewrite is owed.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### 12b, rep 1

> **Audit: `provision_workspace` tool description**
>
> Skill followed: `SKILL.md` plus its one reference, `references/example-audit.md`. No other files read, no files edited.
>
> **Document class.** This is a compact document — a single flat description with no sections. Under R1, inline marking is all a rule owes here, and interleaving rules with facts is not a finding.
>
> **Classification (by sentence)**
>
> | # | Statement | Role |
> |---|---|---|
> | 1 | "Provision a customer workspace." | Discretionary context (purpose) |
> | 2 | "Requires an existing billing account; the account_id must be a UUID, never a customer-facing account number." | Binding rules (two, semicolon-separated), marked |
> | 3 | "MUST NOT provision into a region … returned by list_contract_regions." | Binding rule, marked, verifiable via named artifact |
> | 4 | "Seat count must be at least one and at most the contract seat cap." | Binding rule, marked |
> | 5 | "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise." | Load-bearing fact (tool semantics) |
> | 6 | "Provisioning is asynchronous: … does not exist until the job reports done." | Load-bearing fact |
> | 7 | "Never call this tool twice for the same account_id without first checking get_provision_job, because …" | Binding rule, marked, with attached rationale |
> | 8 | "The workspace name is derived … cannot be supplied by the caller." | Load-bearing fact |
> | 9 | "Trial workspaces expire after fourteen days." | Load-bearing fact |
> | 10 | "Returns {job_id, estimated_ready_at}." | Load-bearing fact |
>
> **Findings**
>
> **R3 Verifiability** (secondary: R5)
> Location: sentences 4–5.
> Quoted text: "Seat count must be at least one and at most the contract seat cap." / "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise."
> Why it fails: the rule states the lower bound as one, but the adjacent fact names a "contract minimum" of five for non-trial contracts. The reader cannot decide whether `seat_count = 3` on a non-trial contract is valid: the rule says yes, the word "minimum" says no. The lower bound is therefore not decidable from the document, and the two statements prescribe incompatible outcomes for the same decision (R5).
> Severity: material — an agent could pass a value the tool rejects, or refuse a valid request.
> Suggested rewrite: author decision between two readings; both preserve the stated defaults and differ only on whether 2–4 seats are valid on non-trial contracts.
> - A (lower bound is one; "minimum" names only the default): keep sentence 4 unchanged; rewrite sentence 5 as "If seat_count is omitted it defaults to one for trial contracts and five otherwise."
> - B (lower bound is the contract minimum): "Seat count must be at least the contract minimum — one for trial contracts, five otherwise — and at most the contract seat cap. If seat_count is omitted it defaults to the contract minimum."
>
> **Not flagged (false-positive guards)**
> - Sentence 2 bundles two obligations but as separate semicolon-delimited clauses, each independently checkable; not an R4 finding.
> - Sentence 4 does not name where the "contract seat cap" comes from (unlike sentence 3, which names `list_contract_regions`). R3 accepts a bound by a named quantity; where to fetch it may be inherited from sibling tools, which is cross-layer analysis and a non-goal.
> - Mixed "MUST NOT" and lowercase "must"/"never": both are unambiguous mandatory wording; not an R2 finding.
> - Sentence 7's rationale ("because a duplicate call …") sits inside the rule sentence; in a compact document that is permitted. The rule is verifiable against the tool trace (a `get_provision_job` call between two `provision_workspace` calls). Observation outside the R1–R5 axis: the rule's letter is satisfied by checking and then calling anyway, which the rationale says should not happen; the author may want to state what result of `get_provision_job` permits a second call. Not counted.
> - Sentences 6, 8, 9, 10 are load-bearing facts correctly stated as information, not directives.
>
> **Safety note:** none. The document contains no auditor-directed instructions.
>
> **Summary**
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 1 (secondary id on the same finding).
> Counts per severity: material 1, minor 0. The per-rule total of two exceeds the single finding because that finding carries a secondary id.
>
> This description is largely well separated for a compact document: every rule uses explicit mandatory wording, the region rule names its verification source, the duplicate-call rule has an observable exception, and the tool-semantics facts (async behavior, derived name, trial expiry, return shape) are stated as information rather than dressed as rules. The one material defect is the seat-count lower bound, which the document states two incompatible ways; that requires an author decision before either rewrite can claim to preserve intent.

### 12b, rep 2

> # Audit: `provision_workspace` tool description
>
> Document class: compact (single flat description, no sections). Under R1, inline marking is all a rule owes here, so embedding of rules alongside facts and rationale is not a finding.
>
> ## Statement classification
>
> | # | Statement | Role |
> |---|---|---|
> | 1 | "Provision a customer workspace." | Discretionary context (purpose) |
> | 2 | "Requires an existing billing account" | Binding rule (precondition), marked by "Requires" |
> | 3 | "the account_id must be a UUID, never a customer-facing account number" | Binding rule, mandatory |
> | 4 | "MUST NOT provision into a region the customer's contract does not cover — the covered regions are returned by list_contract_regions" | Binding rule + load-bearing fact naming the evidence source |
> | 5 | "Seat count must be at least one and at most the contract seat cap." | Binding rule, mandatory |
> | 6 | "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise." | Load-bearing fact (tool semantics) |
> | 7 | "Provisioning is asynchronous: this tool returns a job_id and the workspace does not exist until the job reports done." | Load-bearing fact |
> | 8 | "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support." | Binding rule + rationale |
> | 9 | "The workspace name is derived from the account's legal entity name and cannot be supplied by the caller." | Load-bearing fact |
> | 10 | "Trial workspaces expire after fourteen days." | Load-bearing fact |
> | 11 | "Returns {job_id, estimated_ready_at}." | Load-bearing fact |
>
> ## Findings
>
> **R3 Verifiability**
> Location: statement 8.
> Quoted text: "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support."
> Why it fails: the trigger (a repeat call for the same account_id) is decidable and the exception is observable in the tool trace (a prior get_provision_job call), so the rule as written is checkable. But the rule names only the act of checking, not what the check must show before a second call is permitted. The stated rationale is preventing duplicate workspaces, and an agent that checks, sees the job reported `done` (or still running), and calls again has satisfied the rule verbatim while defeating its purpose. The safeguard the author intends — which job states license a repeat call — is not revealed, so the definitive rewrite is an author decision.
> Severity: minor. Intended behavior is inferable from the rationale and the rule is checkable as written; the gap is that the check's outcome is not bound.
> Suggested rewrite: author decision between the following.
> (a) If checking is the whole obligation (keep semantics as written): "Before calling this tool a second time for the same account_id, call get_provision_job for the earlier job. A duplicate call creates a second workspace that must be deleted by support."
> (b) If a repeat call is permitted only after a failed job: "Never call this tool twice for the same account_id unless get_provision_job reports the earlier job as failed. A duplicate call creates a second workspace that must be deleted by support."
> (c) If a repeat call is never permitted while a job exists in any state, name that state set explicitly instead of choosing (a) or (b).
>
> ## Not flagged (false-positive guards)
>
> - Statement 8 mixes a rule with its rationale in one sentence. In a compact document this is not an R1 finding; the rule is inline-marked by "Never."
> - Statement 5, "at most the contract seat cap": the rule bounds judgment with a named quantity from a named artifact (the contract), which passes R3 as written. Observation only, not a finding: the region rule (statement 4) names its evidence source (`list_contract_regions`) while the seat-cap rule does not; naming where the cap is obtained would make the two rules parallel, but its absence does not make the rule undecidable.
> - Statement 6 (default of five for non-trial contracts) versus statement 5 (cap): not an R5 conflict. Statement 6 is a server-side fact, not a caller rule, so the two do not prescribe incompatible outcomes for the same caller decision.
> - Statement 3 ("must be a UUID, never a customer-facing account number"): the negative clause restates the same single check, so this is not an R4 bundling.
> - Statement 5 (lower and upper bound): one range check with one trigger; not an R4 bundling.
> - Statement 9 ("cannot be supplied by the caller"): stated as a fact about the tool surface, not a rule, so R1's "a rule that cannot fail is context in disguise" does not apply; it is already in context form.
> - R2: no hedged strength anywhere. "Requires," "must," "MUST NOT," and "Never" all signal mandatory strength unambiguously.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 0, minor 1. No finding carries a secondary rule id, so the per-rule total equals the severity total.
>
> This description separates rules from context well for a compact document: every binding statement is inline-marked with mandatory wording, strengths are unambiguous, the region rule names the tool that supplies its evidence, and the asynchronous-job, naming, expiry, and return-shape statements are stated as facts rather than dressed as rules. The single finding is that the duplicate-call rule binds the act of checking `get_provision_job` but not what the check must show, leaving the intended safeguard against duplicate workspaces to be inferred from the rationale; resolving it is an author decision among the labeled alternatives above.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### 12b, rep 3

> I have read `SKILL.md` and the one file it references, `references/example-audit.md`. Report follows.
>
> ## Audit: `provision_workspace` tool description
>
> Document type: compact (a single flat description, no sections). Under R1, rules owe only inline marking here, and embedding is not a finding. Sentences are numbered 1–10 in reading order for location.
>
> Classification: sentences 2 (both clauses), 3, 4, and 7 are binding rules; 5, 6, 8, 9, 10 and the tail of 3 ("the covered regions are returned by list_contract_regions") are load-bearing facts; sentence 1 and the "because..." tail of 7 are discretionary context.
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> Location: sentence 7.
> Quoted text: "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support."
> Why it fails: the trigger (a second call for the same account_id) is decidable and the exception names a recorded action (calling get_provision_job), but the rule does not say which job state licenses the second call. Read literally, any check satisfies the exception, so an agent that checks, sees the job pending or done, and calls again has obeyed the rule while producing exactly the duplicate the rationale warns about. The rationale reveals the intended safeguard (no second workspace), but the rule as written binds only the check, not the outcome.
> Severity: material — the literal and intended readings diverge on a realistic input (job done, another provision request for the same account).
> Suggested rewrite: author decision between two readings.
> (a) Retry-after-failure: "Before calling this tool again for an account_id, call get_provision_job with the earlier job_id, and call again only if that job reports failed. A second call while the job is pending or done creates a duplicate workspace that support must delete."
> (b) Check-only (the literal text): "Before calling this tool again for the same account_id, call get_provision_job with the earlier job_id." — this preserves the current obligation exactly but leaves the stated harm unprevented, so the author should confirm it is what they intend rather than have the auditor assume (a).
>
> **Finding 2 — R5 Reachable precedence**
> Location: sentences 4–5 (the pair).
> Quoted text: "Seat count must be at least one and at most the contract seat cap." / "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise."
> Why it fails: the rule sets a floor of one, but the next sentence introduces a "contract minimum" of five for non-trial contracts. On a realistic input — a non-trial contract with seat_count=3 — the two statements prescribe incompatible outcomes (accepted under the explicit floor; below the contract minimum if that minimum binds supplied values), and the document does not say which governs. The word "minimum" is what creates the conflict; if only a default were meant, no floor is implied.
> Severity: material — an agent may either supply a value the contract forbids or refuse a value the tool accepts.
> Suggested rewrite: author decision between two precedence choices.
> (a) The contract minimum binds supplied values: "Seat count must be at least the contract minimum — one for trial contracts, five otherwise — and at most the contract seat cap. If seat_count is omitted it defaults to the contract minimum."
> (b) The minimum is only a default: "Seat count must be at least one and at most the contract seat cap. If seat_count is omitted it defaults to one for trial contracts and five otherwise."
>
> ### Not flagged (false-positive guards)
>
> - Sentence 2, "Requires an existing billing account; the account_id must be a UUID, never a customer-facing account number." Two obligations share a sentence, but each has its own clause and verb and is independently checkable as written; not an R4 finding. Splitting into two sentences is optional polish.
> - Sentence 3. Marked "MUST NOT", trigger decidable, and the attached fact names the artifact (list_contract_regions) that makes it checkable. Clean; the inline fact is not embedding in a compact document.
> - Sentence 4's upper bound, "the contract seat cap". A named quantity on a named artifact passes R3. Observation only: the region rule names where its evidence comes from and the cap rule does not; the author may want to name the source, but that is not a finding.
> - Sentences 5, 6, 8, 9, 10. Load-bearing facts about tool semantics (defaults, asynchrony, derived name, trial expiry, return shape); not directives, correctly placed as context. "Cannot be supplied by the caller" describes interface capability, not an obligation.
> - R2: no hedges anywhere. "Requires", "must", "never", "MUST NOT" are all unambiguous. The mixed capitalization (one "MUST NOT" among lowercase "must"/"never") does not make any statement's strength ambiguous, so it is not a finding.
> - Sentence 1 is purpose framing; discretionary, fine.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 1.
> Counts per severity: material 2, minor 0. No finding carries a secondary id, so the per-rule total (2) equals the severity total (2).
>
> This is a well-marked compact description: every binding rule uses explicit mandatory wording, no rule is hedged, and the tool-semantics facts (asynchrony, default seat count, derived name, expiry, return shape) are correctly stated as context rather than dressed up as rules. The two defects are both material and both sit at the boundary between a rule and an adjacent fact: the duplicate-call rule binds a check but not the outcome the check is meant to gate, and the seat-count floor is contradicted by an unstated "contract minimum" for non-trial contracts. Both require an author decision before a rewrite can claim to preserve intended behavior; the labeled alternatives above do not select one.

### 12c, rep 1

> # Audit: `backfill-runbook`
>
> ## Findings
>
> **R1 Distinguishability**
> Location: line 7 (Procedure, step 3).
> Quoted text: "Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range."
> Why it fails: "Never pass `--force` to the backfill command" is the document's one binding rule — ignoring it violates a policy, unlike the surrounding steps, which only tell a reader already running the backfill how to carry it out. It is marked (explicit "Never"), but it is embedded: it shares a single list item with a procedural step and a rationale clause ("it bypasses the idempotency check and double-posts every entry in the range"), so it does not stand as its own item and its paragraph mixes it with an informing statement. The document is long-form (labeled sections), and the rule is liftable — obeying it does not depend on the step's passage — so the rewrite moves it into a dedicated rule section and moves the rationale to `## Background`.
> Severity: minor. The rule is short, occupies its own sentence, and uses explicit mandatory wording at the exact point where the reader executes the command, so intended behavior remains clear and checkable; only the structural separation could be improved.
> Suggested rewrite (semantics preserved; no author decision needed):
>
> ```markdown
> ## Rules
>
> - Never pass `--force` to `make backfill`.
>
> ## Procedure
>
> 1. Create a branch from `main`.
> 2. Run `make migrate` to apply pending migrations.
> 3. Run `make backfill`.
> 4. Open a pull request and request review from the data team.
>
> ## Background
>
> The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
> `--force` bypasses the backfill's idempotency check and double-posts every entry in the range.
> ```
>
> Not flagged (false-positive guard): steps 1, 2, and 4 (lines 5, 6, 8) are procedural — they tell a reader already committed to the backfill how to carry it out — so their imperative grammar does not make them binding rules; step 4's two actions are therefore not an R4 compound obligation.
> Not flagged (false-positive guard): line 12, the 2024-migration history, is discretionary context that degrades gracefully if lost, and it is correctly placed in `## Background`.
> Not flagged: R2 — "Never" is unambiguous mandatory strength. R3 — the trigger (any invocation of the backfill command) is decidable and the result is checkable against the command line in tool traces. R5 — the document contains one rule, so no reachable conflict exists.
>
> ## Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity.
>
> This is a nearly clean document. Its single binding rule is clearly worded and mandatory, verifiable, atomic, and unconflicted; the only defect is that it lives inside a procedure step alongside its rationale rather than in a marked rule section. The historical background is correctly separated. The suggested rewrite lifts the rule and its rationale into their proper sections without changing what the document requires.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### 12c, rep 2

> I have read SKILL.md and its single referenced file (references/example-audit.md). Here is the audit.
>
> ## Audit: backfill-runbook
>
> ### Classification
>
> - Lines 5, 6, 8 (steps 1, 2, 4) and the first sentence of line 7 ("Run `make backfill`.") — procedural steps. They tell a reader already committed to the backfill task how to carry it out; under R1, that is procedural, not binding, despite the imperative grammar.
> - Line 7, second sentence, first clause ("Never pass `--force` to the backfill command") — binding rule. Ignoring it violates a policy (double-posting), independent of which procedure the reader is following.
> - Line 7, second sentence, second clause ("it bypasses the idempotency check and double-posts every entry in the range") — informing statement: tool semantics that serve as rationale for the rule.
> - Line 12 (Background) — discretionary context; degrades gracefully if lost.
>
> The document has labeled sections (`## Procedure`, `## Background`), so it is long-form under R1, not compact.
>
> ### Findings
>
> **R1 Distinguishability**
> Location: line 7, step 3.
> Quoted text: "Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range."
> Why it fails: the document's only binding rule ("Never pass `--force`...") is marked by explicit mandatory wording, but it does not stand as its own list item — it shares step 3 with a procedural instruction and with an informing statement (the idempotency/double-post rationale). Under R1 a rule whose paragraph mixes it with facts or background is embedded, and in a long-form document an embedded rule is a finding. The rule is liftable: obeying it does not depend on the surrounding step (it names the command it governs), so the rewrite moves it to a dedicated rule section rather than marking it in place.
> Severity: minor. Intended behavior remains clear and checkable — the strength is explicit ("Never"), the trigger is decidable (passing `--force` to the backfill command), and compliance is verifiable against tool traces. Only the structural separation is deficient.
> Suggested rewrite (semantics preserved; rationale relocated, not dropped):
>
> ```markdown
> # backfill-runbook
>
> ## Rules
>
> - Never pass `--force` to the backfill command.
>
> ## Procedure
>
> 1. Create a branch from `main`.
> 2. Run `make migrate` to apply pending migrations.
> 3. Run `make backfill` (without `--force`; see Rules).
> 4. Open a pull request and request review from the data team.
>
> ## Background
>
> Passing `--force` to the backfill command bypasses the idempotency check and double-posts every entry in the range.
> The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
> ```
>
> ### Not flagged (false-positive guards)
>
> - Steps 1, 2, 4 (lines 5, 6, 8): procedural, not binding; R1 does not treat them as rules, so their imperative grammar and their placement in `## Procedure` owe nothing.
> - Step 4 ("Open a pull request and request review from the data team"): two actions in one item, but both are procedural steps, not obligations; R4 applies to independently checkable obligations and does not reach it.
> - The rationale clause on line 7 is not a separate misplaced-context finding: the document has no rule section for it to sit inside, so the consolidation rule (one finding per misplaced statement when a document both buries rules and pads its rule section) does not apply. It is handled by the R1 rewrite.
> - Line 12 (Background): discretionary historical context, correctly placed outside any rule section.
> - R2: "Never" states mandatory strength unambiguously; no hedge.
> - R3: decidable trigger, result checkable against tool calls; no finding.
> - R5: one binding rule, no conflicting pair; no precedence is owed.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1.
> No finding carries a secondary rule id, so the per-rule total equals the one finding counted by severity.
>
> This runbook is close to clean. Its single binding rule is clearly marked as mandatory, has a decidable trigger, and is verifiable against tool traces, but it is embedded inside a procedure step alongside a procedural instruction and its own rationale rather than standing as a distinguishable rule in a long-form document. Lifting it into a dedicated rule section and moving the rationale to Background resolves the only finding without changing policy; no author decisions are required.

### 12c, rep 3

> ## Audit: `backfill-runbook`
>
> Files consulted: `SKILL.md` and its single reference, `references/example-audit.md`. Nothing else was read; nothing was edited.
>
> Classification (line numbers refer to the target as quoted):
>
> - Lines 5, 6, 8 — procedural steps. Under R1, a step that tells a reader already committed to the task how to carry it out is procedural, not binding, however imperative its grammar. The trailing "to apply pending migrations" (line 6) is a load-bearing fact riding inside a step, not a rule.
> - Line 7 — three roles in one list item: a procedural step ("Run `make backfill`."), a binding rule ("Never pass `--force` to the backfill command"), and an informing statement giving tool semantics/rationale ("it bypasses the idempotency check and double-posts every entry in the range").
> - Line 12 — discretionary context (tool history), correctly placed under `## Background`.
>
> The document has labeled sections, so it is long-form under R1; the compact-document exemption does not apply.
>
> ### Findings
>
> **R1 Distinguishability**
> Location: line 7, step 3 of `## Procedure`.
> Quoted text: "Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range."
> Why it fails: the only binding rule in the document is marked (explicit "Never") but embedded — its list item mixes it with a procedural directive and an informing statement about what `--force` does. It does not stand as its own list item and its paragraph does not hold only directives, so R1 classifies it as embedded. The rule is liftable: obeying "never pass `--force`" does not depend on its position in the step sequence, since it names the command it constrains.
> Severity: minor. Intended behavior remains clear (mandatory strength is explicit) and checkable against the tool trace (whether `--force` appears in the backfill invocation); the defect is structural separation only. It is not material because the rule sits directly beside the command it governs, so a reader executing step 3 encounters it at the moment it applies.
> Suggested rewrite (semantics preserved): add a dedicated rule section and keep the step and the rationale where they inform.
>
> ```markdown
> ## Rules
>
> - Never pass `--force` to `make backfill`.
>
> ## Procedure
>
> 1. Create a branch from `main`.
> 2. Run `make migrate` to apply pending migrations.
> 3. Run `make backfill`.
> 4. Open a pull request and request review from the data team.
>
> ## Background
>
> The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
> `--force` bypasses the backfill tool's idempotency check and double-posts every entry in the range.
> ```
>
> Optionally, step 3 may keep a pointer ("see Rules") without restating the rule; that is a presentation choice, not a semantic one.
>
> ### Not flagged (false-positive guards)
>
> - Line 8, "Open a pull request and request review from the data team." — two actions in one step, but it is a procedural step, not a binding rule, so R4 (atomic obligations) does not apply. Even read as obligations, both share one trigger and are each observable in PR state.
> - Line 6, "to apply pending migrations" — a load-bearing fact inside a procedural step; `## Procedure` is not a rule section, so R1's "keep rule sections free of facts" does not apply.
> - Line 12 — discretionary background, correctly outside any rule content.
> - R2, R3, R5: the single rule has explicit strength ("Never"), a decidable trigger (invoking the backfill command) with an observable result (command arguments), and there is no second rule for it to conflict with. No findings.
>
> ### Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1.
> No finding carries a secondary rule id, so the per-rule total equals the severity total.
>
> This is a nearly clean document. It contains exactly one binding rule, stated with explicit mandatory strength and a verifiable trigger, but that rule is embedded in a procedure step alongside the command it governs and the rationale for it, rather than standing as its own marked item in a rule section. Lifting it into a short `## Rules` section and moving the `--force` semantics to `## Background` completes the separation without changing what the document requires. The procedural steps and the background sentence are correctly classified and need no change.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
