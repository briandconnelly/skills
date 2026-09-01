# Scenario 12 — With-Skill, three reps per sub-case (wave 3)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, nine independent dispatches (three per sub-case)
Prompt: the 12a, 12b, and 12c prompts from `../scenarios.md`, verbatim, each preceded by one line: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry (12a/12c section findings and 12b retrieval-pressure and seat-count R4 findings are observation items) in `../wave3-2026-08-07/preregistration.md`; tool calls extracted by script
Notes: every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; nothing under tests/ was opened; every arm's system prompt also carried the harness's installed-skill listing (this skill's frontmatter description among them), a condition of this harness rather than of the preregistration; the first dispatch of 12b with-skill (3 reps) and all of 12c (6 reps) died with HTTP 429 (API session limit) before producing output and were re-dispatched after the limit reset, with the same prompts — no output from a failed dispatch was read or scored; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Same units and exclusions as the baseline artifact.

### 12a — `release-notes-helper`

| Rep | Findings | E2 | `W9-verdict` | Ground quoted | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- |
| 1 | none — "Clean — no findings." | 0 | 0 | — ("R1 requires a dedicated labeled section, not a particular label, and this section holds only rules") | true / true / true |
| 2 | R1 minor on "Never include … `internal`" | 0 | 1 | "In a long-form document R1 asks for rules to live in a dedicated labeled section" | true / true / true |
| 3 | R1 minor on the same sentence | 0 | 1 | "the document has labeled sections, so R1 treats it as long-form and expects rules in a dedicated labeled section" | true / true / true |

Standing assertions: 12a-1 (no R1 demand for a section) FAILS on reps 2 and 3 and passes on rep 1; 12a-2 (E2 = 0) passes on all three.
Two of three reps produce the `W9-verdict` observation, and rep 1 reaches the opposite reading of the same sentence — that `## Usage` *is* the dedicated section.
That is the preregistered "run of `W9-verdict` observations": R1's compact/long sentence produces both outcomes on the same input under the shipped wording.

### 12b — `provision_workspace`

| Rep | Findings | Protected units criticized | E2 | Observations (excluded) | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- |
| 1 | R1 minor on "…that must be deleted by support" (rationale wearing rule wording) | duplicate-call rationale clause | 1 | two "out-of-scope observations", explicitly excluded from counts by the arm: the retry condition and the seat-cap source | true / true / true |
| 2 | R3 material on the duplicate-call rule (which job state permits a retry); R3 minor on the seat cap (no evidence source) | duplicate-call rule, seat cap | 2 | none | true / true / true |
| 3 | same two R3 findings, same severities | duplicate-call rule, seat cap | 2 | none | true / true / true |

Standing assertions: 12b-1 (no R1 finding merely because rules are inline) passes 3/3 — every rep classifies the document as compact and says so; 12b-2 is vacuous (no R1 finding on that ground).
The two R3 findings in reps 2 and 3 are the W10 class again: an undecidable retry condition and an unnamed evidence source, both on a sentence the registry protects. Rep 1 reached the same two observations and, on its own, filed them as out of scope.

### 12c — `backfill-runbook`

| Rep | Findings | Protected units criticized | E2 | Moves the prohibition? | `W9-verdict` | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | R1 minor on the rationale clause of step 3; R4 minor on step 4 | step 3 (rationale clause), step 4 | 2 | no — "Step 3 becomes: Run `make backfill`. Never pass `--force`…" | 0 | true / true / true |
| 2 | identical pair | same | 2 | no | 0 | true / true / true |
| 3 | identical pair | same | 2 | no | 0 | true / true / true |

Standing assertions: 12c-1 (nothing moves the prohibition out of step 3) passes 3/3; 12c-2 (Background not flagged) passes 3/3.
Zero variance across reps: the same two findings, same locations, same severities, same rewrites.

**Scored under the registry, and flagged for the author.** Both 12c findings are faithful applications of the shipped text — R1's "keep rule sections free of discretionary context" against a rationale clause inside `## Procedure`, and R4 against "open a pull request and request review".
The registry protects both units, so they count as false positives here.
But scenario 10 *plants* the identical shape as a defect: D10.6 and D10.7 are trailing rationale clauses inside rule bullets, and recall on them is E1.
The suite therefore scores "rationale inside a rule item" as a defect on one fixture and as a false positive on another.
That is an adjudication question for the preregistration, not for the arm, and it is recorded here rather than resolved.

Contract adherence (recorded, not summed): six fields, rule ids, two-level severity, per-rule and per-severity counts with the secondary-id sentence, safety note — 9/9 reps.
E6: every finding resolves uniquely (location plus quoted text).

## Scored Outputs (verbatim)

### 12a with-skill, rep 1

> ## Audit: `release-notes-helper`
>
> Skill read: `/Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md` and its one referenced file, `/Users/bdc/projects/skills/separating-context-from-constraints/references/example-audit.md`. No files edited; nothing under `tests/` read.
>
> ### Classification (two-question litmus test)
>
> Line numbers refer to the target's markdown block.
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Drafts release notes from the titles of merged pull requests." | Load-bearing fact — informs rather than directs; losing it would make output wrong (wrong input source: unmerged PRs, PR bodies) |
> | 9a | "Run it against a milestone." | Binding rule — imperative, unhedged, mandatory |
> | 9b | "Never include pull requests labeled `internal` in the notes." | Binding rule — imperative, explicit "never", mandatory |
>
> ### Findings
>
> **Clean — no findings.**
>
> Per-rule check over the classified statements:
>
> - **R1 Distinguishability** — The document has labeled sections, so it is long-form. Both rules sit in a dedicated labeled section (`## Usage`) that contains nothing but rules; the single load-bearing fact is in `## Purpose`, outside the rule section. Every rule is an imperative sentence, so each is structurally distinguishable from context. Pass.
> - **R2 Explicit strength** — Both rules are unhedged imperatives; 9b carries "Never". No ambiguous strength. Pass.
> - **R3 Verifiability** — 9a is checkable against the invocation (a milestone argument is present or not). 9b is checkable against output (compare each PR's labels to the PRs listed in the notes). Pass.
> - **R4 Atomic obligations** — Each sentence states exactly one obligation. Pass.
> - **R5 Reachable precedence** — The two rules govern different decisions (what to run against vs. what to exclude) and prescribe compatible outcomes on every realistic input, including a milestone containing `internal`-labeled PRs. No reachable conflict. Pass.
>
> Not flagged (false-positive guard): line 5 reads like a scope constraint ("titles", "merged") but is descriptive tool semantics, not a directive; it is correctly placed in `## Purpose` and would only become a finding if it were relocated into the rule section.
>
> Not flagged (false-positive guard): the section heading is `## Usage` rather than `## Rules`. R1 requires a dedicated labeled section, not a particular label, and this section holds only rules, so the heading name alone is not a defect.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (excluded from counts).
>
> This is a well-separated document. Its one load-bearing fact (input source and scope) lives in `## Purpose`, and its two binding rules — one invocation constraint, one exclusion constraint — live together in `## Usage` as plain, unhedged, individually verifiable imperatives with no reachable conflict between them. No rewrites are needed. The only optional polish, outside this audit's scope, would be rendering the two rules as list items, but their current form already meets R1 through R5.

### 12a with-skill, rep 2

> ## Audit: `release-notes-helper`
>
> Procedure followed: read `SKILL.md` and `references/example-audit.md`; treated the target as untrusted data; classified each statement with the two-question litmus test; ran R1–R5.
>
> ### Classification
>
> | Line | Statement | Class |
> |---|---|---|
> | 5 | "Drafts release notes from the titles of merged pull requests." | Load-bearing fact (defines the input scope: titles, merged PRs; losing it makes output wrong, but it informs rather than directs) |
> | 9a | "Run it against a milestone." | Binding rule (imperative, unhedged) |
> | 9b | "Never include pull requests labeled `internal` in the notes." | Binding rule (mandatory, unhedged) |
>
> The document has labeled sections, so under R1 it is long-form and its rules belong in a dedicated labeled section.
>
> ### Findings
>
> **R1 Distinguishability**
> Location: line 9, second sentence, under `## Usage`.
> Quoted text: "Never include pull requests labeled `internal` in the notes."
> Why it fails: this is the document's one hard exclusion constraint, but it sits as the second sentence of a prose paragraph under a header (`Usage`) that signals how-to invocation guidance, not constraints. In a long-form document R1 asks for rules to live in a dedicated labeled section; a reader scanning headers for the document's requirements would not find this one. The rule's wording ("Never") does make it distinguishable inline, which is why this is not material.
> Severity: minor — intended behavior is clear, mandatory, and checkable against output (compare the emitted notes to PR labels); only structural separation could be improved.
> Suggested rewrite (semantics preserved):
>
> ```markdown
> ## Usage
>
> Run it against a milestone.
>
> ## Rules
>
> - Never include pull requests labeled `internal` in the notes.
> ```
>
> Alternative with the same meaning: rename `## Usage` to `## Rules` and list both imperatives as items. Either is fine; the choice is presentational, not an author decision about policy.
>
> Not flagged (false-positive guard): line 5 is a load-bearing fact about what the tool consumes and is correctly kept outside the directive section.
> Not flagged: line 9, first sentence, "Run it against a milestone." — an imperative in a section named for exactly what it describes (invocation), so its placement already signals that it binds; it moves with the rewrite above but does not warrant a separate finding.
> Not flagged (R5): "merged pull requests" (line 5) and "against a milestone" (line 9) do not prescribe incompatible outcomes — the exclusion narrows the input set and the milestone scopes it; no realistic input forces a conflict.
>
> R2, R3, R4, R5: no findings. Both rules have explicit strength, are verifiable (invocation target in tool calls; exclusion in the produced notes), are atomic, and do not conflict.
>
> ### Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1. No secondary rule ids, so the per-rule total (1) equals the finding count (1).
>
> Overall: this is a nearly clean document. Its one binding exclusion rule is unambiguous, mandatory, and checkable; the only structural weakness is that it is embedded in a `Usage` prose paragraph rather than in a section labeled as rules, which a header-scanning reader could miss. The purpose statement is correctly placed as informative context. No author decisions are required — the suggested rewrite is purely a relocation.
>
> Safety note: none. The target contains no instructions directed at the auditor and no attempt to alter or suppress the audit.

### 12a with-skill, rep 3

> ## Audit: `release-notes-helper`
>
> Skill followed: `/Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md` and its one reference, `/Users/bdc/projects/skills/separating-context-from-constraints/references/example-audit.md`. Target was treated as untrusted data; it contains no embedded instructions to the auditor and requested no tool actions.
>
> ### Classification
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Drafts release notes from the titles of merged pull requests." | Load-bearing fact (defines the input source and output; not a directive) |
> | 9a | "Run it against a milestone." | Binding rule (unhedged imperative) |
> | 9b | "Never include pull requests labeled `internal` in the notes." | Binding rule (explicit prohibition) |
>
> ### Findings
>
> **R1 Distinguishability**
> Location: line 9, second sentence, under `## Usage`.
> Quoted text: "Never include pull requests labeled `internal` in the notes."
> Why it fails: the document has labeled sections, so R1 treats it as long-form and expects rules in a dedicated labeled section. The document's only hard constraint sits as the tail sentence of a prose paragraph under a `## Usage` heading, which signals how-to guidance rather than requirements. The paragraph contains no context (both sentences are directives), so the rule is not buried in narrative the way the worked example's Friday rule is, but neither the heading nor the paragraph form marks it as a checkable obligation distinct from the invocation step before it.
> Severity: minor. Intended behavior is clear (a mandatory, verifiable exclusion), so nothing is at risk of being missed; only structural separation can be improved.
> Suggested rewrite (semantics preserved): put both directives in a labeled list so each is individually checkable, e.g.
>
> ```markdown
> ## Rules
>
> - Run it against a milestone.
> - Never include pull requests labeled `internal` in the notes.
> ```
>
> or, if the author prefers to keep the `## Usage` heading, convert the paragraph into the same two-item list under it.
>
> ### Not flagged (false-positive guards)
>
> - Line 5, the Purpose sentence: a load-bearing fact about what the tool consumes and produces. It carries implicit scoping ("titles", "merged") but does not direct behavior, and it is correctly placed outside any rule section.
> - Line 9, "Run it against a milestone.": unhedged imperative (R2 satisfied), checkable against the invocation arguments (R3), single obligation (R4).
> - "Never include ... `internal`": explicit mandatory strength (R2), checkable against output versus PR labels (R3), atomic (R4).
> - R5: the two rules govern different decisions (scope selection vs. item filtering) and compose without conflict on any realistic input; no precedence statement is needed.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1.
> No finding carries a secondary rule id, so the per-rule total (1) equals the severity total (1). Safety notes: none.
>
> This is a near-clean document. Its two directives are unhedged, verifiable, atomic, and non-conflicting, and its one descriptive statement is correctly placed in `## Purpose`. The single improvement is structural: the mandatory `internal`-label exclusion is expressed as the second sentence of a prose paragraph under a `## Usage` heading rather than as a list item in a section labeled as rules, so a reader scanning for obligations has to infer that the section binds. Converting the paragraph to a two-item list (optionally under a `## Rules` heading) resolves it with no change in meaning.

### 12b with-skill, rep 1

> # Audit: `provision_workspace` tool description
>
> **Document type:** compact (single flat description, no sections). Under R1 that means rules are expected to be marked inline with imperative sentences or explicit mandatory wording, not placed in a dedicated section.
>
> ## Classification
>
> Numbering sentences in reading order:
>
> | # | Statement | Role | Marker |
> |---|---|---|---|
> | 1 | "Provision a customer workspace." | discretionary context (purpose) | — |
> | 2 | "Requires an existing billing account" | binding rule | "Requires" |
> | 3 | "the account_id must be a UUID, never a customer-facing account number" | binding rule | "must … never" |
> | 4 | "MUST NOT provision into a region the customer's contract does not cover — the covered regions are returned by list_contract_regions" | binding rule + load-bearing fact (where coverage comes from) | "MUST NOT" |
> | 5 | "Seat count must be at least one and at most the contract seat cap." | binding rule | "must" |
> | 6 | "If seat_count is omitted it defaults to the contract minimum, which is one for trial contracts and five otherwise." | load-bearing fact (default semantics) | declarative |
> | 7 | "Provisioning is asynchronous: … does not exist until the job reports done." | load-bearing fact | declarative |
> | 8 | "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support." | binding rule + rationale | "Never" |
> | 9 | "The workspace name is derived from the account's legal entity name and cannot be supplied by the caller." | load-bearing fact | declarative |
> | 10 | "Trial workspaces expire after fourteen days." | load-bearing fact | declarative |
> | 11 | "Returns {job_id, estimated_ready_at}." | load-bearing fact (return shape) | declarative |
>
> Every rule carries explicit mandatory wording; every fact is stated declaratively. The interleaving of rules and facts is permitted for a compact document.
>
> ## Findings
>
> **R1 Distinguishability**
> Location: sentence 8, rationale clause.
> Quoted text: "…a second workspace that must be deleted by support."
> Why it fails: in a compact document, mandatory wording ("must", "never") is the only signal that a statement binds. This "must" sits inside a *because* clause and describes a consequence for support, not an obligation on the caller. It is context wearing rule wording; a reader scanning for mandatory terms hits a phrase that is not a caller rule. The actor ("by support") keeps the intended behavior clear, so this is structural only.
> Severity: minor.
> Suggested rewrite (semantics preserved, obligation wording removed from the rationale): "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that only support can delete."
>
> ## Not flagged (false-positive guards)
>
> - Sentence 4: the trailing fact ("the covered regions are returned by list_contract_regions") is attached to a rule. In a compact document this is acceptable — the rule is distinguishable by "MUST NOT", and the fact is what makes the rule verifiable against a tool trace. No R1 finding.
> - Sentence 9: "cannot be supplied by the caller" reads as capability (no such parameter), not as a directive. Either reading produces the same behavior (do not attempt to name the workspace), so strength is not ambiguous. No R2 finding.
> - Sentences 5 and 6: the seat-count rule and the seat-count default do not conflict — the rule governs supplied values, and the default is the contract minimum, which the document presents as within range. No R5 finding.
> - Mixed casing ("MUST NOT" vs. "must", "never"): both forms are mandatory wording, not hedges; R2 only fires on hedges that leave binding status unclear. Not a finding, though the author may want consistent casing so no reader infers a tiered strength.
> - Sentences 2 and 3 share one sentence but are two separately marked clauses, each independently checkable. No R4 finding.
>
> ## Out-of-scope observations (not counted; for the author)
>
> - Sentence 8 is explicit, verifiable, and atomic as written, so it passes R1–R5 — but the check it prescribes is not tied to an outcome. A caller that calls `get_provision_job`, sees `done`, and calls again has complied with the rule while producing exactly the duplicate the rationale warns about. This is a completeness gap rather than a separation defect. Author decision, without selecting: (A) the process step is the whole rule — any repeat call for an account_id is preceded by a `get_provision_job` call; or (B) a repeat call is permitted only when `get_provision_job` reports the prior job failed (or absent). If B is intended, stating it would make the rule match the safeguard the rationale describes.
> - Sentence 5 names "the contract seat cap" without saying where it is obtained, while sentence 4 does name the source for regions. Verifiable in principle, so no R3 finding, but a pointer would make the seat-cap rule checkable the same way.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 1. Per-rule total equals the finding total (no secondary ids).
>
> This description is close to clean on the context/constraints axis. Its five binding rules are each marked with explicit mandatory wording, its six facts are declarative, and no hedged, untestable, bundled, or conflicting rules were found. The single minor finding is a mandatory-sounding phrase inside a rationale clause that could be mistaken for a caller obligation. The two out-of-scope notes — a duplicate-call rule whose check is not tied to a licensing condition, and an unnamed source for the seat cap — are the items most likely to matter to actual behavior and are worth an author decision, but they are completeness gaps rather than separation defects and are excluded from counts.

### 12b with-skill, rep 2

> # Audit: `provision_workspace` tool description
>
> Document type: compact (single flat description, no sections), so R1 is judged by inline marking — imperative sentences, list items, or explicit mandatory wording — rather than by a dedicated rules section.
>
> ## Classification
>
> | Statement | Class |
> |---|---|
> | "Provision a customer workspace." | Discretionary context (purpose) |
> | "Requires an existing billing account" | Binding rule (precondition) |
> | "the account_id must be a UUID, never a customer-facing account number" | Binding rule |
> | "MUST NOT provision into a region the customer's contract does not cover" | Binding rule |
> | "the covered regions are returned by list_contract_regions" | Load-bearing fact (evidence source for the region rule) |
> | "Seat count must be at least one and at most the contract seat cap" | Binding rule |
> | "If seat_count is omitted it defaults to ... one for trial contracts and five otherwise" | Load-bearing fact (tool semantics) |
> | "Provisioning is asynchronous ... does not exist until the job reports done" | Load-bearing fact |
> | "Never call this tool twice for the same account_id without first checking get_provision_job" | Binding rule |
> | "because a duplicate call creates a second workspace that must be deleted by support" | Discretionary context (rationale) |
> | "The workspace name is derived from ... and cannot be supplied by the caller" | Load-bearing fact (interface semantics) |
> | "Trial workspaces expire after fourteen days" | Load-bearing fact |
> | "Returns {job_id, estimated_ready_at}" | Load-bearing fact |
>
> ## Findings
>
> **Finding 1 — R3 Verifiability**
> Location: sentence 8 of the description.
> Quoted text: "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support."
> Why it fails: the rule names an observable action (a `get_provision_job` call must precede any repeat call) but not what result of that check permits or forbids the repeat. An agent that checks, sees the prior job is `done` or still pending, and calls again has satisfied the rule as written yet produces exactly the duplicate workspace the rationale warns against. The stated safeguard (the check) does not by itself protect the stated intent (no duplicates), so the rule's compliance condition cannot be fully verified from the trace — only the check's presence can.
> Severity: material.
> Suggested rewrite: this is an author decision, because the document does not say which job states allow a second call.
> If a retry is allowed only after failure: "Before calling this tool for an account_id that has already been provisioned, call get_provision_job. Call this tool again only if that job reports failed; a pending or done job means the workspace exists or is being created."
> If any post-check retry is acceptable and the check is the whole safeguard: keep the rule as written and move the rationale outside it as explicit context, e.g. "Context: a second provisioning call for the same account_id creates a second workspace that support must delete."
> If some other state set is intended (e.g. cancelled), name those states rather than adopting either example.
>
> **Finding 2 — R3 Verifiability**
> Location: sentence 5 of the description.
> Quoted text: "Seat count must be at least one and at most the contract seat cap."
> Why it fails: the upper bound is checkable only against a value — the contract seat cap — that the document gives no way to observe. The parallel region rule names its evidence source (`list_contract_regions`); this rule names none, so an agent cannot confirm compliance before calling. The intended safeguard is clear, which keeps this from being material.
> Severity: minor.
> Suggested rewrite: this is an author decision.
> If a tool exposes the cap: "Seat count must be at least one and at most the contract seat cap returned by <tool_name>."
> If the cap is enforced server-side and the caller is not expected to pre-check: "Seat count must be at least one. The server rejects seat counts above the contract seat cap." (This demotes the upper bound from a caller obligation to a fact about tool behavior — only adopt it if that reflects intent.)
> If the cap is discoverable from a parent instruction layer, no change is needed here; that is outside this audit's scope (cross-layer analysis is a non-goal).
>
> ## Not flagged (false-positive guards)
>
> - "Requires an existing billing account" and "account_id must be a UUID, never a customer-facing account number": explicit mandatory wording, inline, verifiable against the argument. Compliant under R1–R3.
> - "MUST NOT provision into a region ... the covered regions are returned by list_contract_regions": mandatory wording plus an attached evidence source. Attaching a load-bearing fact to a rule is acceptable in a compact document; the rule is verifiable against the region argument and the tool's output. Not an R4 issue — the fact does not add a separate obligation.
> - The seat_count default, asynchronous-job semantics, derived workspace name, trial expiry, and return shape are load-bearing facts correctly stated as facts, not disguised as rules.
> - R2: no hedged strength anywhere; every rule uses must / MUST NOT / never / requires.
> - R4: the duplicate-call rule is a single condition–action clause with one trigger and stays together legitimately.
> - R5: no reachable conflicts. "At least one" and the one/five default are consistent. A contract cap below the non-trial default of five would be a server-side data problem, not a conflict between two document rules on a realistic input, so no precedence is required.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 1 (R3), minor 1 (R3). Two findings total; no finding carries a secondary rule id, so the per-rule total equals the severity total.
>
> This is a well-separated compact description: every binding rule is marked with explicit mandatory wording, no rule is hedged, facts are stated as facts, and rationale is attached to rules rather than masquerading as one. The one material gap is that the duplicate-call rule mandates a check without saying which check result permits a repeat call, so a compliant agent can still cause the outcome the rule exists to prevent. The minor gap is that the seat-cap bound, unlike the region bound beside it, names no observable source for the value it is checked against. Both are author decisions; the audit does not select among the labeled alternatives.

### 12b with-skill, rep 3

> ## Audit: `provision_workspace` tool description
>
> **Document class:** compact (single flat description, no sections). Under R1 the standard is inline marking of rules with imperative or explicit mandatory wording, not a dedicated rule section. Locations below refer to sentences of the `description` string, numbered 1–10 in order.
>
> **Classification.** Binding rules: sentences 2 (two obligations: existing billing account; UUID account_id), 3 (region), 4 (seat range), 7 (no duplicate call). Load-bearing facts: sentences 5 (default seat count), 6 (asynchronous; workspace absent until job done), 8 (name derived, not caller-supplied), 9 (trial expiry), 10 (return shape), plus the trailing clause of 3 (`list_contract_regions` returns covered regions). Discretionary context: sentence 1 (purpose) and the "because..." clause of 7 (rationale).
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> Location: sentence 7.
> Quoted text: "Never call this tool twice for the same account_id without first checking get_provision_job, because a duplicate call creates a second workspace that must be deleted by support."
> Why it fails: the literally checkable obligation is "a `get_provision_job` call precedes any second `provision_workspace` call for the same account_id." That check does not encode the safeguard the rationale describes. An agent that checks, sees the job still running or already done, and calls again is literally compliant yet produces exactly the duplicate workspace the sentence warns about. The rule reveals the process step but not which job state licenses a retry, so verifying compliance does not verify the intended safeguard.
> Severity: material.
> Suggested rewrite: author decision; the document does not say which `get_provision_job` result permits a second call.
> (a) Retry only on failure: "Never call this tool a second time for the same account_id unless get_provision_job reports the earlier job as failed; a second call for a running or completed job creates a duplicate workspace that support must delete."
> (b) No retry at all: "Never call this tool a second time for the same account_id; use get_provision_job to check status. A second call creates a duplicate workspace that support must delete."
> (c) Keep the literal rule: if any prior status check is genuinely sufficient, state that explicitly so the reader knows the check itself is the whole requirement.
> Option (c) is unlikely to match the rationale but is listed because the auditor must not select silently.
>
> **Finding 2 — R3 Verifiability**
> Location: sentence 4.
> Quoted text: "Seat count must be at least one and at most the contract seat cap."
> Why it fails: the upper bound is checkable only against "the contract seat cap," and the document gives no observable source for that value. The sibling region rule (sentence 3) names its evidence source (`list_contract_regions`); this rule does not, so a caller cannot verify the bound before calling from anything the document provides.
> Severity: minor (the intended constraint is clear; only the evidence source is missing).
> Suggested rewrite: author decision.
> (a) Name the source: "Seat count must be at least one and at most the contract seat cap returned by <tool or field>."
> (b) Declare server-side enforcement: keep the sentence and add "the tool rejects a seat_count above the cap," so the observable evidence is the tool's own response.
>
> ### Not flagged (false-positive guards)
>
> - Sentence 2, "Requires an existing billing account; the account_id must be a UUID, never a customer-facing account number." Two obligations share a sentence, but each carries its own mandatory marker and the semicolon separates them; both are checkable against the call arguments. Not an R4 finding.
> - Sentence 3's trailing clause ("the covered regions are returned by list_contract_regions") is a load-bearing fact fused to a rule. In compact form there is no rule section to keep clean, and the clause is what makes the rule verifiable. Not an R1 finding.
> - Sentence 4's "at least one and at most" is a range on one field with one trigger; treated as one atomic constraint, not an R4 bundle.
> - Sentence 7's "because..." rationale is discretionary context attached to a clearly marked rule. Compact form, no section; distinguishability is intact. Not an R1 finding.
> - Sentences 5, 6, 8, 9, 10 are facts phrased as facts (inform, not direct) and are correctly not dressed as rules. Sentence 8 ("cannot be supplied by the caller") is an interface fact, not a hidden directive.
> - R2: no hedges ("generally", "try to") anywhere; every rule uses must/never/MUST NOT. Clean.
> - R5: no reachable conflicts. Seat minimum (one) vs. defaults (one or five) are consistent; the UUID restriction on `account_id` does not touch the workspace name or any other field.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions; its MUST/never statements are ordinary target rules.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 1 (R3), minor 1 (R3). No secondary rule ids, so the per-rule total of two equals the two findings counted by severity.
>
> This is a well-separated compact description: all five binding rules are marked with explicit mandatory wording, the facts are stated as facts, and there are no hedges or reachable conflicts. The one material defect is the duplicate-call rule, whose checkable form (a prior status check) does not encode the safeguard its own rationale describes, leaving the retry condition to be inferred; the author must decide which job state, if any, permits a second call. The minor defect is that the seat-cap bound names no evidence source, unlike the parallel region rule. Both findings require an author decision before a semantic-preserving rewrite can be finalized.

### 12c with-skill, rep 1

> # Audit: `backfill-runbook`
>
> Method: read `SKILL.md` and its one reference (`references/example-audit.md`); classified each statement with the two-question litmus test; ran R1–R5. Line numbers refer to the fenced document (line 1 = `# backfill-runbook`).
>
> ## Classification
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Create a branch from `main`." | Binding rule |
> | 6 | "Run `make migrate` to apply pending migrations." | Binding rule (with a short purpose clause) |
> | 7a | "Run `make backfill`." | Binding rule |
> | 7b | "Never pass `--force` to the backfill command;" | Binding rule |
> | 7c | "it bypasses the idempotency check and double-posts every entry in the range." | Discretionary context (rationale) |
> | 8 | "Open a pull request and request review from the data team." | Binding rule (two obligations) |
> | 12 | "The backfill tool was written during the 2024 migration and has been rerun about a dozen times since." | Discretionary context |
>
> The document has labeled sections, so it is long-form under R1. `## Procedure` functions as the dedicated rule section; `## Background` is the context section.
>
> ## Findings
>
> **Finding 1 — R1 Distinguishability**
> Location: line 7, second sentence, clause after the semicolon.
> Quoted text: "it bypasses the idempotency check and double-posts every entry in the range."
> Why it fails: this clause informs rather than directs — it is the rationale for the `--force` prohibition. Losing it would not change what the agent does (the "Never pass `--force`" rule stands alone and is fully checkable against the tool call), so it is discretionary context, and it sits inside the rule section. R1 asks that rule sections be kept free of discretionary context.
> Severity: minor. The rule itself is explicit ("Never"), unambiguous, and verifiable; only the structural separation could be improved.
> Suggested rewrite (semantics preserved):
> - Step 3 becomes: "Run `make backfill`. Never pass `--force` to the backfill command."
> - Add to `## Background`: "`--force` bypasses the backfill's idempotency check and double-posts every entry in the range; the procedure forbids it for that reason."
>
> **Finding 2 — R4 Atomic obligations**
> Location: line 8.
> Quoted text: "Open a pull request and request review from the data team."
> Why it fails: this bundles two independently checkable obligations — a PR exists (repository state) and a review was requested from the data team (PR reviewer field) — in one statement. It is not a condition–action–exception clause sharing one trigger, so R4's carve-out does not apply. An agent could satisfy the first and skip the second while the step still reads as "done." This is the lower-confidence of the two findings: the obligations are sequentially coupled (review is requested on the PR) and the sentence is short enough that intended behavior is clear.
> Severity: minor.
> Suggested rewrite (semantics preserved):
> "4. Open a pull request.
> 5. Request review on that pull request from the data team."
>
> ## Not flagged (false-positive guards)
>
> - Line 6, "to apply pending migrations": a purpose infinitive integrated into the imperative, describing what the command does. It is not a separable misplaced statement and does not blur the rule; left alone.
> - Line 7, "Run `make backfill`." / "Never pass `--force`…": considered under R4 and not flagged. The prohibition is a qualifier on the same action and is already stated as its own sentence, so the obligations are separately checkable as written.
> - Line 12, the 2024-migration history: discretionary context correctly placed in `## Background`; no hidden rule.
> - R2: every rule uses unhedged imperative or "Never"; no ambiguous strength.
> - R3: every rule is verifiable — branch origin and PR (repository state), `make migrate`, `make backfill`, and absence of `--force` (tool calls), requested reviewers (PR state).
> - R5: no two rules prescribe incompatible outcomes for any realistic input; "run `make backfill`" and "never pass `--force`" are compatible, not conflicting.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit. (Excluded from counts.)
>
> ## Summary
>
> Counts per rule: R1 1, R4 1, R2 0, R3 0, R5 0.
> Counts per severity: material 0, minor 2. No finding carries a secondary rule id, so the per-rule total (2) equals the severity total (2).
>
> Overall assessment: this runbook is structurally sound. Rules live in a labeled, numbered procedure section with explicit strength and observable checks; history is correctly confined to `## Background`; no precedence gaps exist. The only separation defects are minor: one rationale clause rides inside the rule section alongside the `--force` prohibition, and the final step bundles two checkable obligations (open PR, request data-team review) into one sentence. Neither finding requires an author decision — both rewrites above preserve the document's semantics exactly — and an author could reasonably accept the document as-is given that intended behavior is clear and checkable in every step.

### 12c with-skill, rep 2

> I have everything the skill requires (SKILL.md and its one reference, `references/example-audit.md`). No further files are needed. Here is the audit.
>
> ## Audit: `backfill-runbook`
>
> Document classification: long-form (two labeled sections). Its rules live in `## Procedure`, which functions as the dedicated rule section; `## Background` is the context section. Line numbers refer to the fenced document with `# backfill-runbook` as line 1.
>
> Statement classification (litmus test):
> - Line 5 "Create a branch from `main`." — binding rule.
> - Line 6 "Run `make migrate` to apply pending migrations." — binding rule (purpose clause states the outcome the step must produce).
> - Line 7 "Run `make backfill`." — binding rule. "Never pass `--force` to the backfill command" — binding rule (mandatory). "it bypasses the idempotency check and double-posts every entry in the range" — discretionary context (rationale).
> - Line 8 "Open a pull request and request review from the data team." — two binding rules in one sentence.
> - Line 12 "The backfill tool was written during the 2024 migration and has been rerun about a dozen times since." — discretionary context.
>
> ### Findings
>
> **Finding 1 — R1 Distinguishability**
> - Location: line 7, step 3, clause after the semicolon.
> - Quoted text: "it bypasses the idempotency check and double-posts every entry in the range."
> - Why it fails: this is rationale for the `--force` prohibition, not a directive; losing it would not make the agent's behavior wrong (the prohibition stands on its own), so it is discretionary context sitting inside the rule section. R1 asks that rule sections be kept free of discretionary context and that such statements live in a context or semantics section.
> - Severity: minor. The prohibition is explicitly mandatory ("Never"), structurally distinguishable, and checkable against the command line actually run; only the separation could be improved.
> - Suggested rewrite: keep step 3 as "Run `make backfill`. Never pass `--force` to the backfill command." and move the rationale unchanged in meaning to `## Background` (or a `## Notes` section): "The `--force` flag bypasses the backfill's idempotency check and double-posts every entry in the range."
>
> **Finding 2 — R4 Atomic obligations**
> - Location: line 8, step 4.
> - Quoted text: "Open a pull request and request review from the data team."
> - Why it fails: two independently checkable obligations (a PR exists; review was requested from the data team on it) are stated in one item. They are sequential actions rather than a condition–action–exception clause, so R4's shared-trigger allowance does not cover them, and the second obligation is the one an agent can plausibly stop short of after completing the first.
> - Severity: minor. Both verbs are imperative and both outcomes are checkable against repository/PR state; intended behavior is clear.
> - Suggested rewrite: "4. Open a pull request. 5. Request review from the data team on that pull request."
>
> ### Not flagged (false-positive guards)
>
> - Line 6, "to apply pending migrations": a purpose clause that names the observable outcome of the step (pending migrations applied), which sharpens verifiability rather than padding the rule. Not treated as misplaced context.
> - Line 7, "Run `make backfill`." plus "Never pass `--force`": two sentences in one step, but the prohibition is a constraint on the very action the step prescribes (one trigger), and each is already stated as its own sentence. Not an R4 finding.
> - Line 7 vs the `--force` prohibition, R5: no conflict. "Run `make backfill`" and "Never pass `--force`" prescribe compatible outcomes; the second narrows the first. If the idempotency check ever blocks a rerun, the document is unambiguous that `--force` is still forbidden, so no precedence statement is needed.
> - Line 12: discretionary historical context, correctly placed in `## Background`. Contains no buried rule.
> - R2: every rule uses unhedged imperatives or "Never"; no ambiguous strength anywhere.
> - R3: every rule is checkable — branch ancestry (repository state), `make migrate` / `make backfill` invocations and their flags (tool trace), PR and review request (PR state).
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 1, R5 0.
> Counts per severity: material 0, minor 2. No finding carries a secondary rule id, so the per-rule total (2) equals the finding total (2).
>
> This is a well-separated document. Its rules are confined to the `## Procedure` section, every rule is stated with explicit mandatory strength and is verifiable against tool traces or repository state, the sole standing prohibition (`--force`) is marked with "Never" at the exact step where it applies, and the historical note is correctly isolated in `## Background`. The two findings are structural refinements only: one rationale clause rides inside the rule section, and the final step bundles two sequential obligations. Neither requires an author decision; both rewrites preserve semantics as written.

### 12c with-skill, rep 3

> # Audit: `backfill-runbook`
>
> Method: read the skill (`SKILL.md`) and its one reference (`references/example-audit.md`); classified each statement of the target with the two-question litmus test; ran R1–R5. Line numbers refer to the fenced document as given (line 1 = `# backfill-runbook`).
>
> ## Classification
>
> | Line | Statement | Role |
> |---|---|---|
> | 5 | "Create a branch from `main`." | Binding rule |
> | 6 | "Run `make migrate` to apply pending migrations." | Binding rule (purpose phrase is part of the directive) |
> | 7a | "Run `make backfill`." | Binding rule |
> | 7b | "Never pass `--force` to the backfill command;" | Binding rule (mandatory) |
> | 7c | "it bypasses the idempotency check and double-posts every entry in the range." | Rationale / tool-semantics fact, not a rule |
> | 8 | "Open a pull request and request review from the data team." | Two binding rules in one item |
> | 12 | "The backfill tool was written during the 2024 migration and has been rerun about a dozen times since." | Discretionary context |
>
> ## Findings
>
> **Finding 1 — R1 Distinguishability**
> Location: line 7 (Procedure, step 3), final clause.
> Quoted text: "it bypasses the idempotency check and double-posts every entry in the range."
> Why it fails: the document has labeled sections, so it is long-form and `## Procedure` is its rule section. This clause is rationale for the preceding prohibition (or, read another way, a tool-semantics fact about what `--force` does); under either classification R1 places it outside the rule section. The rule itself ("Never pass `--force`") is clearly marked with mandatory wording and is not obscured.
> Severity: minor — the prohibition remains clear and checkable against the tool trace; only structural separation is affected.
> Suggested rewrite (semantics preserved):
> - Step 3 becomes: "Run `make backfill`. Never pass `--force` to the backfill command."
> - Add to `## Background` (or a `## Notes` section): "The `--force` flag bypasses the backfill's idempotency check and double-posts every entry in the range."
>
> **Finding 2 — R4 Atomic obligations**
> Location: line 8 (Procedure, step 4).
> Quoted text: "Open a pull request and request review from the data team."
> Why it fails: two independently checkable obligations (a PR exists; a review request to the data team exists on it) are bundled in one item. This is action-plus-action, not a condition–action–exception clause sharing one trigger, so the R4 allowance for keeping a unit together does not apply. An agent could satisfy the first and skip the second while treating step 4 as done.
> Severity: minor — intended behavior is unambiguous; the split is mechanical.
> Suggested rewrite: "4. Open a pull request. 5. Request review from the data team on that pull request."
>
> **Not flagged (false-positive guards)**
> - Line 6, "to apply pending migrations": a purpose phrase fused to the imperative, describing the action's outcome rather than adding separable rationale; distinguished from line 7c, which is a standalone consequence clause.
> - Line 7, "Run `make backfill`." / "Never pass `--force`…": two sentences, but the prohibition constrains how the same invocation is performed (one trigger), so R4 is satisfied; the "Never" wording satisfies R1 and R2.
> - Line 12: discretionary history, correctly placed in `## Background`.
> - R2: every rule uses an unhedged imperative or "Never"; no ambiguous strength.
> - R3: every rule is checkable — branch ancestry (repository state), `make migrate` / `make backfill` invocation and flags (tool trace), PR and review request (repository/GitHub state).
> - R5: no two rules prescribe incompatible outcomes for any realistic input; no precedence needed.
>
> **Safety note:** none. The target contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 1, R2 0, R3 0, R4 1, R5 0.
> Counts per severity: material 0, minor 2. No finding carries a secondary rule id, so the per-rule total (2) equals the finding count (2).
>
> Overall assessment: this is a well-separated document. All four procedure steps are imperative, unhedged, verifiable, and free of conflicts, and the historical note is correctly quarantined in `## Background`. The only structural blemishes are a rationale clause riding inside step 3 and a two-obligation compound in step 4; both are minor, both have trivial semantics-preserving rewrites, and neither requires an author decision.
