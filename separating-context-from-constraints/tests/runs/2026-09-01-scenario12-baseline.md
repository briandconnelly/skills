# Scenario 12 — Baseline, three reps per sub-case (wave 3)

```
Date: 2026-09-01
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, nine independent dispatches (three per sub-case)
Prompt: the 12a, 12b, and 12c prompts from `../scenarios.md`, verbatim, each preceded by one line: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry (12a/12c section findings and 12b retrieval-pressure and seat-count R4 findings are observation items) in `../wave3-2026-08-07/preregistration.md`; tool calls extracted by script
Notes: all nine arms made zero tool calls (script check); every arm's system prompt also carried the harness's installed-skill listing (this skill's frontmatter description among them), a condition of this harness rather than of the preregistration; the first dispatch of 12b with-skill (3 reps) and all of 12c (6 reps) died with HTTP 429 (API session limit) before producing output and were re-dispatched after the limit reset, with the same prompts — no output from a failed dispatch was read or scored; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Nothing is planted; E2 counts every protected unit criticized. Registry exclusions: on 12a and 12c a finding demanding a dedicated rules section is `W9-verdict` (observation, excluded by name); on 12b an R1 finding grounded in retrieval pressure and R4 findings against the seat-count sentences are observations.
Units are clauses. A criticism of the document's overall structure that names no clause is recorded as `structure` and counted once, except where the registry routes it (12a/12c section demands → `W9-verdict`; 12b interleaving → retrieval-pressure observation).

### 12a — `release-notes-helper`

| Rep | Findings (arm's own labels) | Protected units criticized | E2 | `W9-verdict` | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- |
| 1 | Major: `internal` rule needs a rules section; Minor: "Run it against a milestone" binding status; Minor: Purpose sentence smuggles constraints | milestone sentence, Purpose sentence | 2 | 1 | false / false / false |
| 2 | High: same section demand; Low: milestone sentence; Low: Purpose sentence | milestone sentence, Purpose sentence | 2 | 1 | false / false / false |
| 3 | major: section demand; minor: milestone; minor: Purpose; minor: "no stated output constraint" (conditional, "if none exists, no change needed" — not counted) | milestone sentence, Purpose sentence | 2 | 1 | false / false / false |

Every rep also shipped a restructured document (prose note only; E9a is scoped to scenarios 10 and 15).

### 12b — `provision_workspace`

Units: the ten description sentences, with sentence 2 (billing account; UUID) as one unit, plus `markers` for a document-level complaint about inconsistent modal strength.

| Rep | Protected units criticized | E2 | Observations (excluded) | E9c guard / class / safety |
| --- | --- | --- | --- | --- |
| 1 | region rule, `markers`, duplicate-call rule (rationale bundling, exit condition), seat cap, sentence 2 (bundling), async sentence | 6 | F1 interleaving — retrieval-pressure ground | true (sentence 8 "cannot be supplied" declared correct) / true (inventory table) / false |
| 2 | region rule, seat cap, sentence 2, duplicate-call rule, async sentence, trial-expiry sentence | 6 | F1 interleaving — retrieval-pressure ground | true (sentence 8) / true / false |
| 3 | duplicate-call rationale ("must be deleted by support"), seat cap, `markers`, sentence 2, async sentence | 5 | F1 interleaving — retrieval-pressure ground; "not flagged" note on seat range and region pointer | true / true / false |

All three shipped a full rewritten description.

### 12c — `backfill-runbook`

| Rep | Findings | Protected units criticized | E2 | Moves the `--force` prohibition out of step 3? | `W9-verdict` | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Major: step 3 bundles action, prohibition, rationale; Minor: step 4 compound; Minor: step 2 purpose clause | step 3, step 4, step 2 | 3 | offered as an alternative (a `## Constraints` block) — counted as yes | 1 (the Constraints-block alternative) | true (Background, steps 1 and 3) / false / false |
| 2 | F1 Major: step 3 bundling, rewrite moves the prohibition to `## Constraints`; F2 Minor: no constraints section | step 3 | 1 | yes | 1 (F2) | true / false / false |
| 3 | Minor: step 3 bundling; rewrite keeps the prohibition as a sub-bullet of step 3 and moves only the rationale to Background | step 3 | 1 | no | 0 | true / false / false |

Contract adherence: no rule ids, no six-field format, no summary counts in any rep (expected for a baseline; recorded, not summed).

## Scored Outputs (verbatim)

### 12a baseline, rep 1

> # Audit: `release-notes-helper` — separation of context from constraints
>
> Scope note: per your instruction I audited the document as given, without loading the `separating-context-from-constraints` skill or any other file, so the severity labels below (Major / Minor) are my own two-level scheme rather than the skill's exact vocabulary. No score is assigned, no parent-layer conflicts are analyzed, and general prose quality is out of scope.
>
> ## Findings
>
> ### 1. Major — The only hard prohibition is buried inside a how-to paragraph
>
> > `## Usage` — "Run it against a milestone. Never include pull requests labeled `internal` in the notes."
>
> "Never include pull requests labeled `internal`" is the document's single binding rule, and it is the second sentence of a section titled "Usage," which an agent reads as procedural context ("here is how you invoke this"). There is no section whose heading signals "these bind." An agent skimming for requirements has nothing to anchor on; the rule survives only if the reader happens to weight the word "Never."
>
> The rule itself is well-formed: single obligation, testable (a PR either carries the `internal` label or it does not), no padding. The problem is placement, not wording.
>
> **Suggested rewrite (semantic-preserving):**
>
> ```markdown
> ## Usage
>
> Run it against a milestone.
>
> ## Rules
>
> - MUST NOT include pull requests labeled `internal` in the notes.
> ```
>
> ### 2. Minor — "Run it against a milestone" has ambiguous binding status
>
> The imperative mood reads as a rule; the "Usage" placement reads as a description of the normal invocation. The two readings diverge in practice:
>
> - If it **binds**: running against a tag, a date range, or the whole repository is a violation, and it belongs in the Rules section (e.g. "MUST scope the run to a single milestone").
> - If it is **context**: it should stay in Usage, and rewording to declarative ("Runs against a milestone.") removes the false imperative signal.
>
> I cannot resolve this without changing meaning, so the author has to choose. Either outcome is a one-line edit.
>
> ### 3. Minor — The Purpose sentence smuggles two implicit input constraints
>
> > "Drafts release notes from the titles of merged pull requests."
>
> Read as description, this is fine context. But it quietly encodes two restrictions an agent may or may not be expected to honor:
>
> - **merged** — are open or closed-unmerged PRs in the milestone excluded by rule, or is "merged" just the typical case?
> - **titles** — if PR bodies are available, is the agent forbidden from drawing on them, or is "titles" simply what the tool uses by default?
>
> If either is a real constraint (e.g. the notes must never leak content from unmerged work), it should be promoted to the Rules section alongside finding 1. If neither binds, leave the sentence as is; it is doing honest descriptive work. Flagged so the author makes the call consciously rather than leaving it to the reader.
>
> ## What is already right
>
> - The `internal` rule is atomic and testable; no hedging ("generally," "try to"), no bundled obligations.
> - Purpose and Usage are correctly separated from each other; the fix is adding a third section, not restructuring.
>
> ## Consolidated rewrite (assuming only the `internal` rule binds)
>
> ```markdown
> # release-notes-helper
>
> ## Purpose
>
> Drafts release notes from the titles of merged pull requests.
>
> ## Usage
>
> Run it against a milestone.
>
> ## Rules
>
> - MUST NOT include pull requests labeled `internal` in the notes.
> ```
>
> If the author decides that milestone scoping and/or merged-only / titles-only also bind, add them as separate bullets under Rules rather than expanding the existing one.

### 12a baseline, rep 2

> # Audit: `release-notes-helper` — context vs. constraints
>
> Scope note: per the instructions I worked from the document text alone; no files, tools, or skills were loaded. Severity uses two levels: **High** (a binding rule is likely to be missed or misread as optional) and **Low** (binding status is ambiguous but the most plausible reading still works).
>
> ## Findings
>
> ### 1. The only hard rule is buried in a how-to section — High
>
> **Where:** `## Usage` — "Run it against a milestone. Never include pull requests labeled `internal` in the notes."
>
> **Problem:** The document has exactly one unambiguous constraint (`Never include ... internal`), and it sits as the second sentence of a section titled "Usage", immediately after a procedural how-to sentence. Section headings are the primary signal an agent uses to decide what is background and what binds; "Usage" signals guidance, not obligation. An agent that reads Purpose, skims Usage for the invocation pattern, and proceeds is likely to draft notes that include `internal` PRs. The rule itself is well-formed (single obligation, unhedged, testable), so the defect is purely placement.
>
> **Suggested rewrite (semantics unchanged):**
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
> ### 2. "Run it against a milestone" has unclear binding status — Low
>
> **Where:** `## Usage`, first sentence.
>
> **Problem:** This is written as an imperative, so it reads like a rule, but it is not clear whether it binds (the tool must only ever be run scoped to a milestone; refuse or ask if none is given) or merely describes the normal invocation (context). Nothing tells the agent what to do when no milestone is supplied. Because it shares a paragraph with the `internal` rule, the two statements borrow force from each other: the how-to looks more mandatory than it may be, and the prohibition looks more like a usage tip than it is.
>
> **Suggested rewrite:** pick one reading and make it explicit. If it is context:
>
> ```markdown
> ## Usage
>
> Typical invocation is against a single milestone.
> ```
>
> If it binds:
>
> ```markdown
> ## Rules
>
> - Scope every run to exactly one milestone. If no milestone is given, ask for one before drafting.
> ```
>
> I cannot determine which the author intended from the text; do not adopt the binding version unless that is actually the requirement.
>
> ### 3. Implicit scope constraints hidden inside the Purpose statement — Low
>
> **Where:** `## Purpose` — "Drafts release notes from the **titles** of **merged** pull requests."
>
> **Problem:** This reads as descriptive context, which is appropriate for a Purpose section, but it carries two candidate constraints: (a) only merged PRs are eligible, and (b) entries are derived from titles (not bodies, commit messages, or linked issues). If either is a real requirement — e.g. an open-but-milestoned PR must never appear, or the agent must not embellish from PR bodies — it is currently only inferable, and an agent treating Purpose as flavor text can violate it without ever seeing a rule. If they are not requirements, no change is needed.
>
> **Suggested rewrite (only if these are binding; otherwise leave Purpose as-is):**
>
> ```markdown
> ## Rules
>
> - Include only pull requests that are merged.
> - Derive each entry from the pull request title only.
> - Never include pull requests labeled `internal` in the notes.
> ```
>
> ## What is already sound
>
> - The `internal` prohibition is a model constraint in form: one obligation, absolute wording, mechanically checkable (label present or not).
> - Purpose contains no hedged pseudo-rules ("generally", "try to") and no untestable directives.
> - Rules are not padded with rationale; the only fix needed is structural placement, not rewriting.
>
> ## Summary
>
> One High finding (the sole hard rule lives in a how-to section under a heading that signals guidance) and two Low findings (an imperative whose binding status is unclear; two scope constraints that exist only implicitly in the Purpose sentence). The minimal fix is to add a `## Rules` section and move the `internal` prohibition into it; the two Low items need an author decision before any rewrite, since resolving them either way changes semantics.

### 12a baseline, rep 3

> # Audit: release-notes-helper — context vs. constraints
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or read any file, so severity labels below are my own two-level scheme (**major** = an agent could plausibly miss or misread a binding rule; **minor** = ambiguity that is unlikely to change behavior but should be tightened).
>
> ## Findings
>
> ### 1. [major] The only hard rule is buried in a "Usage" section next to procedural prose
>
> `Never include pull requests labeled `internal` in the notes.` is the one non-negotiable requirement in the document, but it lives in a section titled **Usage**, on the same line as an operational how-to ("Run it against a milestone"). An agent skimming for "how do I invoke this" reads Usage as narrative and can treat the exclusion as an aside. The document has no section whose title signals "these bind."
>
> Suggested rewrite (semantics preserved):
>
> ```markdown
> ## Rules
>
> - Exclude every pull request labeled `internal` from the release notes.
> ```
>
> Keeping "Never include" is also fine; the important change is the dedicated section.
>
> ### 2. [minor] "Run it against a milestone" — unclear whether it binds
>
> This reads as either (a) a constraint: *input must be a milestone; don't run it against a branch, tag, or date range*, or (b) a description of typical use. The two readings lead to different behavior when a user asks for notes "since last Tuesday." Pick one:
>
> - If binding: move to Rules — `- Scope the run to exactly one milestone.`
> - If descriptive: leave in Usage but reword to signal it — `Typically run against a milestone.`
>
> ### 3. [minor] Purpose sentence smuggles two possible constraints
>
> `Drafts release notes from the titles of merged pull requests.` describes behavior, but it implies two restrictions that may or may not bind:
>
> - **Source restriction**: titles only — should the agent ignore PR bodies/commit messages, or is that just where it starts?
> - **Merge-state restriction**: merged only — is including an open-but-approved PR a violation, or merely atypical?
>
> If either is a requirement, an agent has no way to tell from a Purpose sentence. If they bind, add to Rules (`- Use only merged pull requests.` / `- Derive entries from PR titles only.`); if not, the Purpose sentence is fine as context.
>
> ### 4. [minor] "Drafts" and "release notes" carry an unstated output expectation
>
> Not a rule-separation defect per se, but there's no stated constraint on output (format, ordering, grouping), so an agent will invent one. If any exists, it's missing; if none exists, no change needed.
>
> ## Suggested restructured document
>
> ```markdown
> # release-notes-helper
>
> ## Purpose
>
> Drafts release notes from the titles of merged pull requests in a milestone.
>
> ## Usage
>
> Run it against a milestone.
>
> ## Rules
>
> - Exclude every pull request labeled `internal` from the release notes.
> - Use only merged pull requests.            <!-- keep only if binding -->
> - Scope the run to exactly one milestone.   <!-- keep only if binding -->
> ```
>
> ## Summary
>
> One major finding: the single binding rule (`internal` exclusion) has no rule-labeled home and is co-located with how-to prose. Three minor findings are all the same shape — descriptive sentences ("from titles", "merged", "against a milestone") that may be constraints in disguise; the author needs to decide which bind and promote those into the Rules section.

### 12b baseline, rep 1

> # Audit: `provision_workspace` tool description — separation of context from constraints
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or any file; this applies the skill's published criteria (rules buried in prose, unclear binding force, untestable directives, compound rules, rationale padding) from its description. Severity uses two levels: **Blocker** (an agent reading for obligations is likely to miss or misapply a rule) and **Advisory** (clarity/consistency improvement, low risk of misbehaviour).
>
> ## Inventory
>
> The single-paragraph description carries five binding rules interleaved with seven context statements:
>
> | # | Text | Kind |
> |---|------|------|
> | 1 | Provision a customer workspace. | Context (purpose) |
> | 2 | Requires an existing billing account | **Rule** (precondition) |
> | 3 | account_id must be a UUID, never a customer-facing account number | **Rule** (format) |
> | 4 | MUST NOT provision into a region the customer's contract does not cover | **Rule** |
> | 5 | the covered regions are returned by list_contract_regions | Context (pointer) — but carries an implied procedural rule |
> | 6 | Seat count must be at least one and at most the contract seat cap | **Rule** |
> | 7 | If seat_count is omitted it defaults to ... one for trial, five otherwise | Context (default behaviour) |
> | 8 | Provisioning is asynchronous ... does not exist until the job reports done | Context — with an implied rule |
> | 9 | Never call this tool twice for the same account_id without first checking get_provision_job | **Rule** |
> | 10 | because a duplicate call creates a second workspace that must be deleted by support | Context (rationale) |
> | 11 | Workspace name is derived from legal entity name; cannot be supplied | Context (schema fact) |
> | 12 | Trial workspaces expire after fourteen days | Context |
> | 13 | Returns {job_id, estimated_ready_at} | Context (return shape) |
>
> ## Findings
>
> ### F1 — Blocker: rules and context are interleaved in one undifferentiated paragraph
> Rules 2, 3, 4, 6, 9 are scattered across positions 2–9 with context sentences (5, 7, 8) between them and pure context (11–13) trailing. Nothing signals where the obligations start or stop; an agent skimming for "what must I do before calling" has to reconstruct the rule list from prose. This is the root cause of most findings below. Fix: restructure into a one-line summary, a numbered rule block, and a notes block (full rewrite at the end).
>
> ### F2 — Blocker: the region rule states the constraint but hides the check as a fact
> "MUST NOT provision into a region the customer's contract does not cover — the covered regions are returned by list_contract_regions." The only way for an agent to satisfy the rule is to call `list_contract_regions` first, but that step is phrased as background ("are returned by"), not as an obligation. Compare rule 9, where the prerequisite check ("without first checking get_provision_job") is explicit. An agent can plausibly "know" a region from the user's request and skip the lookup. Rewrite: "Before calling, call list_contract_regions for the account. The region must be one of the values it returns."
>
> ### F3 — Advisory: inconsistent binding markers imply a false priority order
> Five rules use five different strength signals: "Requires", "must be ... never", "MUST NOT" (the only capitalised one), "must be at least", "Never". A reader can reasonably infer that the capitalised region rule outranks the others, when all five are hard preconditions of equal force (a duplicate call is described as requiring support cleanup — at least as costly as a wrong region). Use one marker consistently (e.g. plain "must"/"do not") or capitalise all of them.
>
> ### F4 — Advisory: duplicate-call rule bundles rule with rationale
> Rule 9 and its "because ..." clause are one sentence. The rationale is useful context but lengthens the rule and blurs its boundary; move it to the notes block so the rule reads as a single testable instruction.
>
> ### F5 — Advisory: duplicate-call rule leaves its exit condition unstated
> "Never call this tool twice for the same account_id without first checking get_provision_job" says what to check but not what outcome permits a second call (job failed? job not found? any outcome?). As written the check is a ritual rather than a decision. I have not invented a condition in the rewrite (that would change semantics); flag for the author to specify.
>
> ### F6 — Advisory: seat-cap rule references a value with no source
> "at most the contract seat cap" gives no pointer to where the cap comes from, unlike the region rule which names `list_contract_regions`. The rule is testable only if the agent already knows the cap. Author should add the source (a tool, a field on the account, or the user).
>
> ### F7 — Advisory: first sentence bundles two independent rules
> "Requires an existing billing account; the account_id must be a UUID, never a customer-facing account number." One sentence carries a precondition (billing account exists) and a format rule (UUID, not account number). Split into two numbered rules.
>
> ### F8 — Advisory: async context carries an implied constraint
> "the workspace does not exist until the job reports done" is stated as a fact, but it functions as a rule for downstream behaviour (do not report the workspace as ready, do not act on it, until `get_provision_job` reports done). If that is intended to bind, state it as a rule; if it is purely informational, leave it in notes. The rewrite keeps it in the summary as context, since the original does not phrase it as an instruction.
>
> No findings on items 7, 11, 12, 13: they are genuine context and belong in a notes block, which the rewrite provides.
>
> ## Suggested rewrite (semantic-preserving)
>
> Kept as a single string suitable for the JSON `description` field; line breaks used for structure. Nothing added except structure and the explicit region-lookup step already implied by the original; F5 and F6 gaps are left for the author.
>
> ```
> Provision a customer workspace. Provisioning is asynchronous: returns {job_id, estimated_ready_at}, and the workspace does not exist until get_provision_job reports the job done.
>
> Rules:
> 1. The account must have an existing billing account.
> 2. account_id must be a UUID. Do not pass a customer-facing account number.
> 3. Before calling, call list_contract_regions for the account. Do not provision into a region that is not in its result.
> 4. If seat_count is supplied, it must be at least 1 and at most the contract seat cap.
> 5. Do not call this tool a second time for the same account_id without first checking get_provision_job for the earlier job.
>
> Notes:
> - If seat_count is omitted it defaults to the contract minimum: 1 for trial contracts, 5 otherwise.
> - The workspace name is derived from the account's legal entity name and cannot be supplied by the caller.
> - A duplicate call creates a second workspace that must be deleted by support.
> - Trial workspaces expire after fourteen days.
> ```
>
> ## Summary
> Two blockers (F1 interleaving; F2 region check disguised as context), six advisories. The document contains no hedged rules ("generally", "try to") and no untestable vagueness of the "be concise" kind; its problems are structural (no rule/context boundary, mixed binding markers) plus two rules whose test inputs are unspecified (F5, F6).

### 12b baseline, rep 2

> # Audit: `provision_workspace` tool description
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or any file, so severity labels below are my own two-level scheme (Major = an agent following the text as written can plausibly violate a rule or fail to act on one; Minor = clarity/structure cost without a likely behavioral failure).
>
> ## Inventory
>
> The description is a single 10-sentence paragraph. Classifying each sentence:
>
> | # | Sentence (abridged) | Kind |
> |---|---|---|
> | 1 | Provision a customer workspace. | Context (purpose) |
> | 2 | Requires an existing billing account; account_id must be a UUID, never a customer-facing number. | **Rule** (two bundled) |
> | 3 | MUST NOT provision into an uncovered region — covered regions come from list_contract_regions. | **Rule** + context |
> | 4 | Seat count must be ≥1 and ≤ contract seat cap. | **Rule** |
> | 5 | If seat_count omitted, defaults to contract minimum (1 trial / 5 otherwise). | Context (behavior) |
> | 6 | Asynchronous: returns job_id; workspace doesn't exist until job done. | Context with an implicit rule |
> | 7 | Never call twice for same account_id without first checking get_provision_job, because… | **Rule** + rationale |
> | 8 | Workspace name derived from legal entity name; cannot be supplied. | Context (schema fact) |
> | 9 | Trial workspaces expire after fourteen days. | Context (unrelated to the call) |
> | 10 | Returns {job_id, estimated_ready_at}. | Context (return shape) |
>
> Five binding rules (six if sentence 2 is split) interleaved with five context sentences, in no particular order, with no structural signal.
>
> ## Findings
>
> **F1 — Major — Rules and context are interleaved in one paragraph.**
> Rules sit at positions 2, 3, 4, 7; context at 1, 5, 6, 8, 9, 10. The most consequential rule (duplicate call → orphan workspace requiring support cleanup) is sentence 7 of 10, after three sentences of background. An agent skimming for "how do I call this" gets the async return shape and the default seat count before it gets the idempotency rule. Fix: split into a labeled rules block and a behavior block (rewrite below).
>
> **F2 — Major — Region rule states where the data lives, not what the caller must do.**
> "MUST NOT provision into a region the customer's contract does not cover — the covered regions are returned by list_contract_regions." The binding clause is about an outcome the agent can't observe directly; the checkable action (pick a region from `list_contract_regions` output) is phrased as an aside after a dash. An agent could take a region from the user's request and pass it without checking. Semantic-preserving rewrite: "`region` MUST be one of the regions returned by `list_contract_regions` for this account." (Assumes the parameter is named `region`; the description never names it.)
>
> **F3 — Minor — Seat cap rule has no stated source.**
> "at most the contract seat cap" is binding but the description never says where the cap comes from (a field on the account? another tool?). The agent can't self-check before calling. This is a content gap rather than a separation defect, so I can't fix it without author knowledge: name the source (e.g., "as returned by `get_contract`") or state explicitly that the server enforces it and the caller need not pre-check.
>
> **F4 — Minor — Sentence 2 bundles two different obligations.**
> "Requires an existing billing account" (a precondition on state) and "account_id must be a UUID, never a customer-facing account number" (an input-format rule) share a sentence joined by a semicolon. Split into two bullets so each is independently checkable.
>
> **F5 — Minor — Duplicate-call rule carries its rationale inline.**
> The "because a duplicate call creates a second workspace that must be deleted by support" clause is useful and should stay, but as a trailing sentence rather than inside the rule. Separately, the rule is under-specified: it says a second call is allowed after checking `get_provision_job`, but not under what job state (failed only? any terminal state?). Worth a question to the author; I have not changed the semantics in the rewrite.
>
> **F6 — Minor — Async sentence carries an implicit rule as a fact.**
> "the workspace does not exist until the job reports done" is stated as behavior, but the thing an agent must actually do is not report the workspace as ready, or hand its identifiers to downstream steps, until `get_provision_job` says done. If the author intends that as binding, phrase it as a rule; if it's informational only, it's fine as context. The rewrite keeps it as context but names the tool to poll, which sentence 6 omits (only sentence 7 mentions `get_provision_job`).
>
> **F7 — Minor — Sentence 9 is background with no bearing on the call.**
> "Trial workspaces expire after fourteen days" doesn't affect any argument or sequencing. Keep it, but at the end of the context block so it doesn't sit between the idempotency rule and the schema fact.
>
> No finding on sentence 8: "cannot be supplied by the caller" is a schema fact correctly presented as context, and it's clear.
>
> ## Suggested rewrite (semantics preserved; structure only)
>
> ```
> Provision a customer workspace. Asynchronous: returns {job_id, estimated_ready_at}. The workspace does not exist until get_provision_job reports the job done.
>
> Rules:
> - The billing account MUST already exist.
> - account_id MUST be the billing account's UUID. Never pass a customer-facing account number.
> - region MUST be one of the regions returned by list_contract_regions for this account.
> - seat_count, if supplied, MUST be at least 1 and at most the contract seat cap.
> - Do NOT call this tool again for the same account_id until you have checked get_provision_job for the earlier job. A duplicate call creates a second workspace that support must delete.
>
> Behavior:
> - If seat_count is omitted it defaults to the contract minimum: 1 for trial contracts, 5 otherwise.
> - The workspace name is derived from the account's legal entity name; there is no name parameter.
> - Trial workspaces expire after fourteen days.
> ```
>
> Two things the author should confirm before adopting: the region parameter's actual name (F2), and where the seat cap is obtainable (F3). Neither is inferable from the text.

### 12b baseline, rep 3

> # Audit: `provision_workspace` tool description — context vs. constraints
>
> Scope note: per your instruction I did not load the skill or any file, so the severity labels below are my own two-level scheme (**Major** = an agent following the text as written could plausibly violate or miss a binding rule; **Minor** = clarity/placement issue with low miss risk).
>
> ## Inventory
>
> The description contains **5 binding rules** and **6 pieces of context**, all interleaved in one paragraph with no structural separation.
>
> Rules (bind the caller):
> 1. Billing account must already exist.
> 2. `account_id` must be a UUID, not a customer-facing account number.
> 3. Must not provision into a region outside the contract (source: `list_contract_regions`).
> 4. `seat_count` must be in [1, contract seat cap].
> 5. Never call twice for the same `account_id` without first checking `get_provision_job`.
>
> Context (informs, does not bind): purpose statement; async behavior and return shape; `seat_count` default (1 trial / 5 otherwise); workspace name derivation; 14-day trial expiry; the duplicate-call consequence ("second workspace that must be deleted by support").
>
> ## Findings
>
> **F1 — Major. No structural separation; rules are buried mid-paragraph.**
> The five rules sit at sentence positions 2, 3, 4, 7 of a nine-sentence paragraph, each flanked by explanatory prose. The most consequential rule (no duplicate call, #5) is sentence 7, after the async explanation and before the name/expiry trivia. An agent skimming for "what does this tool do and return" gets purpose + return shape and can miss #5 entirely.
>
> **F2 — Major. False modal: "must be deleted by support" is a consequence, not a constraint.**
> "...a duplicate call creates a second workspace that **must** be deleted by support." This "must" is descriptive (what happens afterward), but it uses the same modal as the real rules. An agent pattern-matching on "must" may read it as an obligation on itself (e.g. call a delete tool after a duplicate). Rewrite to a non-modal consequence: "which support then has to remove."
>
> **F3 — Major. Rule #4 has no verification path; rule #3 does.**
> Rule #3 tells the agent where to get the covered regions (`list_contract_regions`). Rule #4 says "at most the contract seat cap" but names no tool or field that returns the cap. As written, the agent cannot check compliance before calling — it can only find out on rejection. Either point to the source of the cap or state that the server enforces it (which changes it from a caller rule to context). This is at the edge of a separation audit (it is really a completeness gap), but it is flagged because an uncheckable rule reads as flavor.
>
> **F4 — Minor. Inconsistent modal strength across rules.**
> Rules use four different forms: "Requires" (#1), "must be" (#2, #4), "MUST NOT" in caps (#3), "Never" (#5). The capitalized MUST NOT on #3 alone implies it is the only hard rule and the others are softer. All five are meant to bind equally; use one form.
>
> **F5 — Minor. Rule + rationale fused (#5).**
> "Never call this tool twice ... without first checking get_provision_job, because a duplicate call creates a second workspace..." The rule is the first clause; the "because" clause is context. Keep the rationale but detach it (parenthetical or a following sentence) so the rule's boundary is visible. This also fixes F2.
>
> **F6 — Minor. Two obligations bundled in one sentence (#1 + #2).**
> "Requires an existing billing account; the account_id must be a UUID, never a customer-facing account number." Two separate checks (account existence; identifier format) joined by a semicolon. Split into two bullets.
>
> **F7 — Minor. Implicit rule stated as fact.**
> "the workspace does not exist until the job reports done" is written as context, but it implies a binding behavior (do not treat the workspace as provisioned, or act on it, until `get_provision_job` reports done). Its binding status is ambiguous. If it is meant to bind, state it as a rule; if it is informational, leave it in the context section. The rewrite below keeps it as context, since promoting it would add a rule the original did not clearly assert.
>
> **F8 — Minor. Ambiguous precondition (#1).**
> "Requires an existing billing account" does not say whether the caller must verify existence beforehand or whether the server rejects the call. Same class as F3 but lower stakes, since the identifier rule (#2) already forces the caller to hold a real account UUID.
>
> **Not flagged (deliberately):** "at least one and at most the contract seat cap" looks compound but is a single range bound; splitting it would not help. The em-dash pointer in rule #3 ("— the covered regions are returned by list_contract_regions") is rule + verification path, which is the desired shape; keep it attached.
>
> ## Suggested rewrite (semantics preserved)
>
> ```
> Provision a customer workspace. Asynchronous: returns {job_id, estimated_ready_at}.
> The workspace does not exist until get_provision_job reports the job done.
>
> Rules:
> - The billing account MUST already exist.
> - account_id MUST be the billing account's UUID, not a customer-facing account number.
> - The region MUST be one returned by list_contract_regions for this account.
> - seat_count, if supplied, MUST be between 1 and the contract seat cap, inclusive.
>   [TODO: name the tool/field that returns the seat cap, or state that the server enforces it.]
> - Do NOT call this tool a second time for the same account_id without first
>   checking get_provision_job for the earlier job. (A duplicate call creates a
>   second workspace, which support then has to remove.)
>
> Notes:
> - If seat_count is omitted, it defaults to the contract minimum: 1 for trial
>   contracts, 5 otherwise.
> - The workspace name is derived from the account's legal entity name; there is
>   no name parameter.
> - Trial workspaces expire after fourteen days.
> ```
>
> Changes made and why: rules and notes are sectioned (F1); one modal form throughout (F4); rationale for the duplicate-call rule is parenthetical with the false "must" removed (F2, F5); account-existence and UUID-format are separate bullets (F6); the seat-cap source is marked as a gap rather than invented (F3). The async sentence stays as context (F7) — promote it to a rule only if that is the intended semantics.

### 12c baseline, rep 1

> # Audit: `backfill-runbook` — context vs. constraints
>
> Scope note: per your instruction I worked from the document text alone and did not load the `separating-context-from-constraints` skill or any file, so severity labels below are my own two-level scale (Major / Minor), not the skill's exact vocabulary.
>
> ## Findings
>
> ### 1. Major — Step 3 bundles a procedural step, a standing prohibition, and its rationale into one line
>
> > 3. Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range.
>
> Three different kinds of content share one list item:
>
> - an action ("Run `make backfill`")
> - a binding, always-on prohibition ("Never pass `--force`")
> - explanatory context ("it bypasses the idempotency check and double-posts…")
>
> Problems this causes:
>
> - The prohibition is the highest-consequence rule in the document, and it is the only rule not given its own line. An agent skimming the numbered steps sees "Run `make backfill`" as the instruction and the rest as commentary.
> - "Never" is unscoped (it applies any time the tool is invoked), but its placement inside step 3 makes it read as scoped to this one step.
> - The rationale is welded to the rule with a semicolon, so an agent that paraphrases or summarizes the step can drop the rule while keeping the explanation, or vice versa.
> - The referent is slightly loose: the step names `make backfill` but the rule says "the backfill command." If those differ (e.g. the Makefile target vs. the underlying binary), the rule is harder to check.
>
> Suggested rewrite (semantics preserved; rationale kept, but separated):
>
> ```markdown
> 3. Run `make backfill`.
>    - Never pass `--force` to `make backfill`.
>      (Context: `--force` bypasses the idempotency check, so every entry in the range is posted twice.)
> ```
>
> Or, if the prohibition should be visible independent of step order, add a short constraints block above the procedure:
>
> ```markdown
> ## Constraints
>
> - Never pass `--force` to `make backfill`.
>
> ## Procedure
> ...
> 3. Run `make backfill`.
> ...
>
> ## Background
>
> - `--force` bypasses the backfill idempotency check; every entry in the range is posted twice.
> - The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
> ```
>
> ### 2. Minor — Step 4 is a compound rule (two obligations)
>
> > 4. Open a pull request and request review from the data team.
>
> Two separately checkable obligations ("open a PR"; "request review from the data team") are joined by "and." An agent can satisfy the first and consider the step done. Suggested rewrite:
>
> ```markdown
> 4. Open a pull request.
> 5. Request review from the data team on that pull request.
> ```
>
> ### 3. Minor — Step 2 attaches a purpose clause to an imperative
>
> > 2. Run `make migrate` to apply pending migrations.
>
> "to apply pending migrations" is context, not a constraint. It is harmless here, but it is the same pattern as finding 1 in miniature and worth normalizing if you adopt a "steps are bare imperatives" convention:
>
> ```markdown
> 2. Run `make migrate`.
> ```
>
> (with "applies pending migrations" moved to Background, or simply dropped since `make migrate` is self-describing).
>
> ## What is correctly separated
>
> - **Background** contains no directives. "written during the 2024 migration and rerun about a dozen times" is pure context and is correctly placed outside the procedure. One observation, not a finding: "rerun about a dozen times" could be read by an agent as an implicit "rerunning is safe" signal, which slightly softens the `--force` prohibition. It stays context either way; if you adopt the Constraints block in finding 1, the rule will be visible enough that this does not matter.
> - No hedged language ("generally", "try to", "should probably") anywhere; every directive is unambiguously binding.
> - No untestable directives; every step has an observable completion condition.
> - Steps 1 and 3 (the action half) are clean single imperatives.
>
> ## Summary
>
> One Major finding (the `--force` prohibition buried inside step 3 alongside its rationale) and two Minor findings (compound step 4; purpose clause on step 2). The Background section is already doing its job. The main fix is to give the `--force` rule its own line — ideally its own section — and move the "why" to a clearly marked context note.

### 12c baseline, rep 2

> # Audit: `backfill-runbook` — separation of context from constraints
>
> **Scope note:** Per your instruction I audited only the text in the prompt; no files, tools, or skills were used.
>
> ## Summary
>
> The document is short and mostly well-separated: the `Background` section is pure context with no hidden rules, and steps 1, 2, and 4 are plain, testable directives. There is one real problem — the document's only prohibition is buried inside a procedure step and bundled with its rationale — plus one minor structural observation.
>
> ## Findings
>
> ### F1 (Major) — Binding prohibition buried mid-step and bundled with rationale
>
> **Location:** Procedure, step 3:
>
> > Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range.
>
> **Problem:** This one step carries three different kinds of content:
>
> 1. an action to perform (`Run make backfill`),
> 2. a binding prohibition (`Never pass --force`), and
> 3. an explanation of why (`it bypasses the idempotency check and double-posts...`).
>
> The prohibition is the most consequential rule in the whole runbook (the only thing that can cause data damage), yet it has no standalone home. An agent skimming the numbered list for "what do I do next" sees step 3 as "run the backfill" and can treat the second sentence as commentary. The rationale clause after the semicolon compounds this: the sentence reads as narrative, so its load-bearing half ("Never pass `--force`") sits at the same visual weight as flavor text. The wording itself is fine — "Never" is unhedged and the condition is testable (the flag is either present or not) — the defect is placement and bundling, not strength.
>
> **Semantic-preserving rewrite** (rule and rationale both kept, but separated):
>
> ```markdown
> ## Procedure
>
> 1. Create a branch from `main`.
> 2. Run `make migrate` to apply pending migrations.
> 3. Run `make backfill`.
> 4. Open a pull request and request review from the data team.
>
> ## Constraints
>
> - Never pass `--force` to `make backfill`.
>
> ## Background
>
> - `--force` bypasses the backfill's idempotency check. With it, every entry in the range is posted twice.
> - The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
> ```
>
> If you would rather keep the prohibition adjacent to the step it governs (defensible for a runbook read top-to-bottom), a lighter fix that still removes the bundling:
>
> ```markdown
> 3. Run `make backfill`.
>    - Constraint: never pass `--force`. (Why: it bypasses the idempotency check and double-posts every entry in the range.)
> ```
>
> Either version preserves the exact obligation and the exact explanation; neither adds or removes a requirement.
>
> ### F2 (Minor) — No constraints section; rules and steps share one heading
>
> **Location:** Document structure (`## Procedure`, `## Background`).
>
> **Problem:** The headings offer two buckets — "things to do" and "context" — with no place for "things you must not do regardless of step." That absence is what pushed the `--force` rule into step 3 in the first place. This is a structural cause of F1 rather than an independent defect; it is resolved by the first rewrite above and needs no separate action if you adopt it.
>
> ## What is already correct (no action)
>
> - **`Background` section:** Pure context. It states history ("written during the 2024 migration", "rerun about a dozen times") without smuggling in any obligation. This is the shape the rest of the document should follow.
> - **Steps 1, 2, 4:** Each is a single, unhedged, checkable action. Step 2's trailing clause "to apply pending migrations" is a purpose annotation, not a second obligation, and does not need splitting.
> - **Rule wording:** No hedges ("generally", "try to", "should probably") anywhere; no untestable directives.
>
> ## Recommended action
>
> Adopt the first rewrite under F1 (add a `## Constraints` section, move the `--force` rationale to `## Background`). This is a one-edit fix that resolves both findings without changing what the runbook requires.

### 12c baseline, rep 3

> # Audit: `backfill-runbook` — separation of context from constraints
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or any tool; this is a manual read of the document as given, using that skill's framing (two-level severity, semantic-preserving rewrites).
>
> ## Overall
>
> The document is in good shape. Constraints live in a clearly labeled `Procedure` section as numbered imperatives; context lives in a clearly labeled `Background` section that contains no binding language. I found one minor issue and nothing major.
>
> ## Findings
>
> ### 1. Minor — Step 3 bundles a command, a standing prohibition, and its rationale in one line
>
> > 3. Run `make backfill`. Never pass `--force` to the backfill command; it bypasses the idempotency check and double-posts every entry in the range.
>
> - The rule (`Never pass --force`) is stated unambiguously and precedes the explanation, so an agent is likely to catch it. That is why this is minor rather than major.
> - Still, the line does three things: an action ("Run"), a prohibition ("Never"), and an explanation ("it bypasses..."). The explanation is context, not a constraint, and it sits inside the constraint list. An agent that reads step 3 as "the thing to run" may not register that it also carries a rule with consequences beyond this step.
>
> Suggested rewrite (preserves meaning; only re-partitions):
>
> ```markdown
> ## Procedure
>
> 1. Create a branch from `main`.
> 2. Run `make migrate` to apply pending migrations.
> 3. Run `make backfill`.
>    - Never pass `--force` to the backfill command.
> 4. Open a pull request and request review from the data team.
>
> ## Background
>
> The backfill tool was written during the 2024 migration and has been rerun about a dozen times since.
>
> `--force` bypasses the backfill's idempotency check and double-posts every entry in the range; that is why the procedure forbids it.
> ```
>
> If you prefer to keep the rationale adjacent to the rule (a reasonable choice for a safety-critical prohibition), a parenthetical after the rule on its own sub-bullet works too; the important part is that the rule is a distinct line, not the tail of a "Run X" sentence.
>
> ## Checked and clean
>
> - Hedged directives ("generally", "try to", "should probably"): none.
> - Untestable directives ("be careful", "be concise"): none. Every step names a concrete action or a concrete prohibition.
> - Rules buried in narrative prose: none. `Background` contains only facts (origin, rerun count) and no verbs of obligation.
> - Section ordering: constraints before context; context is labeled as such.
> - Step 4 is compound in form ("open a PR and request review") but both clauses are actions in the same step of a sequence, not two separable obligations that could be followed independently, so I did not flag it.
