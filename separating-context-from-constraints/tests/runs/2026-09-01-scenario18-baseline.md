# Scenario 18 — retry-policy, Baseline, three reps (wave 3, W16)

```
Date: 2026-09-01
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: all three arms made zero tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

> **Rescored 2026-09-02.** E2 in this artifact was scored by sentence or bullet; the preregistration's unit is the clause. See `../wave3-2026-08-07/rescore-2026-09-02.md` for the unit inventory and corrected counts; that file wins where they differ.


Planted: D18.1 (declarative production gate in Background). Protected probes: the three Semantics statements ("Remember that…", "Note that…", `INGEST_ENV`), "Feel free to skim…", the 2025 sentence, the `retries` rule.

| Rep | D18.1 | Probes criticized | E2 | Classification stated? by |
| --- | --- | --- | --- | --- |
| 1 | ✓ Major (#1) | "Feel free" (#2 Minor); `--dry-run` sentence (#3, "fact framed as an imperative"); `retries` note (#4); the `retries` rule (#4, proposes a clarification) | 4 | yes — by grammatical mood ("Remember that" is an instruction; "imperative form implies an obligation") |
| 2 | ✓ Major (#1) | "Feel free" (#2 Minor); `--dry-run` and `retries` notes (#3, "facts dressed as directives") | 3 | yes — by mood ("imperative framings wrapped around context") |
| 3 | ✓ Major (#1) | "Feel free" (#2); the `retries` rule (#3, "not self-contained"); `--dry-run` and `retries` notes (#4, "directive-shaped softeners") | 4 | yes — by mood |

`INGEST_ENV` (copular, no imperative verb) is criticized by no baseline, and the 2025 sentence by none: the false positives fall exactly on the three imperative-in-form non-rules, which is the grammar-sorting failure the fixture was built to elicit.
Every rep also shipped a restructured document (prose note only).
E9c: guard-lines true ×3; classification-table false ×3; negative-safety-note false ×3.

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `retry-policy` — separation of context from constraints
>
> **Summary.** The document has a dedicated `## Rules` section, but it captures only one of the document's binding constraints. At least one hard rule is buried in `## Background` as a description of practice, and two further statements use imperative or hedged framing ("Remember that…", "Feel free to skim…") that leaves their binding status unclear. The `## Semantics` facts are genuinely context, but their imperative preambles make them read like directives with no testable action.
>
> ## Findings
>
> ### 1. Binding rule buried in narrative prose — Major
>
> **Location:** `## Background`, sentence 2:
> > Engineers submit batches to the production cluster only after the staging replay has completed without errors.
>
> **Issue:** This is a gating constraint (staging replay must succeed before any production submission) written in descriptive present tense, sandwiched between a history note and a docs pointer. An agent skimming `## Rules` for its obligations will miss it entirely; an agent reading `## Background` has no signal that this sentence binds while its neighbours do not.
>
> **Rewrite (move to `## Rules`):**
> - Do not submit a batch to the production cluster until the staging replay has completed without errors.
>
> Remove the sentence from `## Background` (or leave a non-binding cross-reference such as "See Rules for the staging-replay gate").
>
> ### 2. Hedged directive with unclear binding status — Minor
>
> **Location:** `## Background`, sentence 3:
> > Feel free to skim `docs/ingest-overview.md` before making changes.
>
> **Issue:** "Feel free to skim" signals optional, but "before making changes" reads as a sequencing requirement. The agent cannot tell whether skipping the doc violates the policy. Pick one.
>
> **Rewrite, if optional (keep in `## Background`):**
> > `docs/ingest-overview.md` describes the current pipeline design.
>
> **Rewrite, if required (move to `## Rules`):**
> - Read `docs/ingest-overview.md` before changing retry configuration.
>
> ### 3. Fact framed as an imperative with no testable action — Minor
>
> **Location:** `## Semantics`, sentence 1:
> > Remember that the `--dry-run` flag still writes to the audit log.
>
> **Issue:** "Remember that" is an instruction to hold a fact in mind, not a constraint on behaviour, yet its imperative form implies an obligation the document never states (e.g., "do not use `--dry-run` to test against production"). If a consequence is intended, it belongs in `## Rules`; if not, the sentence is context and should be stated as a plain fact.
>
> **Rewrite (as context):**
> > `--dry-run` still writes to the audit log.
>
> If an obligation is intended, add to `## Rules`, e.g.:
> - Treat `--dry-run` invocations as audit-log writes; do not use them to test against a cluster whose audit log must stay clean.
>
> (The author must confirm the intended rule; the rewrite above is illustrative, not a semantic inference from the text.)
>
> ### 4. Context preamble padding — Minor
>
> **Location:** `## Semantics`, sentence 2:
> > Note that `retries` counts attempts after the first, so `retries: 2` means three total attempts.
>
> **Issue:** The content is correct context, but "Note that" is the same imperative framing as finding 3. Strip it. Separately, this fact directly determines the meaning of the one stated rule (`retries ≤ 5` means at most 6 attempts), and the rule does not reference it; an agent reading `## Rules` in isolation may misinterpret the cap.
>
> **Rewrite (context):**
> > `retries` counts attempts after the first; `retries: 2` means three total attempts.
>
> **Rewrite (rule, optional clarification):**
> - Set `retries` to at most 5 (at most 6 total attempts).
>
> ### 5. `## Rules` undercounts the document's constraints — structural, Major
>
> **Issue:** `## Rules` lists one rule; the document actually carries two or three (finding 1 is unambiguous, findings 2 and 3 depend on author intent). Because a rules section exists, an agent is entitled to treat it as exhaustive, which makes the buried constraints more dangerous than they would be in a document with no rules section at all.
>
> ## What is fine as-is
>
> - `INGEST_ENV` holds the target cluster name, not a region. — plain fact, correctly placed, no rewrite needed.
> - The 2025 rebuild sentence — pure history, correctly placed.
> - `Set retries to at most 5.` — clear, atomic, testable.
>
> ## Suggested restructured document (semantics preserved; items marked [confirm] need the author's intent)
>
> ```markdown
> ---
> name: retry-policy
> description: Use when configuring retries for the ingest pipeline.
> ---
>
> # retry-policy
>
> ## Rules
>
> - Set `retries` to at most 5 (at most 6 total attempts).
> - Do not submit a batch to the production cluster until the staging replay has completed without errors.
> - [confirm] Read `docs/ingest-overview.md` before changing retry configuration.
> - [confirm] Do not rely on `--dry-run` to avoid audit-log writes.
>
> ## Semantics
>
> - `retries` counts attempts after the first; `retries: 2` means three total attempts.
> - `--dry-run` still writes to the audit log.
> - `INGEST_ENV` holds the target cluster name, not a region.
>
> ## Background
>
> The pipeline was rebuilt in 2025 after the original queue-based design proved hard to reason about under backpressure. `docs/ingest-overview.md` describes the current design.
> ```
>
> **Finding counts:** 2 Major (1, 5), 3 Minor (2, 3, 4). Findings 2 and 3 cannot be closed without the author stating whether an obligation was intended; the rewrites offer both readings rather than guessing.

### Baseline, rep 2

> # Audit: `retry-policy` — separation of context from constraints
>
> **Summary.** The document has the right skeleton (two context sections, one rules section), but one binding constraint is hidden in `## Background` as a descriptive sentence, one directive is hedged so its binding status is unclear, and the context sections use directive framing for plain facts. The `## Rules` section itself is clean.
>
> ## Findings
>
> ### 1. Major — Binding rule buried in narrative prose (`## Background`)
>
> > Engineers submit batches to the production cluster only after the staging replay has completed without errors.
>
> Written in descriptive present tense as if it were history, but "only after" is a gate: it states a precondition for a production action. An agent reading `## Rules` as the authoritative list will never see it. This is the exact failure mode the separation is meant to prevent, and it is the highest-consequence sentence in the document (it governs production writes, while the only listed rule governs a config integer).
>
> Suggested rewrite — move to `## Rules`, semantics preserved:
>
> > - Do not submit a batch to the production cluster until the staging replay has completed without errors.
>
> If the author genuinely meant this as a description of current practice rather than a requirement, the sentence should say so explicitly ("Current practice is…"); as written, the ambiguity itself is the defect.
>
> ### 2. Minor — Hedged directive with unclear binding status (`## Background`)
>
> > Feel free to skim `docs/ingest-overview.md` before making changes.
>
> "Feel free to" signals optional; "before making changes" has the shape of a precondition. An agent cannot tell whether skipping this violates the document. Pick one:
>
> - If optional, drop the directive shape and make it a pointer: "Overview of the pipeline: `docs/ingest-overview.md`."
> - If required, move to `## Rules`: "Read `docs/ingest-overview.md` before changing retry configuration."
>
> ### 3. Minor — Facts dressed as directives (`## Semantics`)
>
> > Remember that the `--dry-run` flag still writes to the audit log.
> > Note that `retries` counts attempts after the first…
>
> "Remember that" / "Note that" are imperative framings wrapped around context. They add no obligation but make the reader work out whether something is being required. Strip the framing so the section reads uniformly as definitions:
>
> > - `--dry-run` still writes to the audit log.
> > - `retries` counts attempts after the first; `retries: 2` means three total attempts.
> > - `INGEST_ENV` holds the target cluster name, not a region.
>
> One follow-up question for the author, not a finding: if there is an obligation implied by the `--dry-run` fact (for example, a restriction on dry-running against production because of audit-log noise), it is not stated anywhere. If none exists, the fact is correctly placed as context.
>
> ### 4. No finding — `## Rules` is well-formed
>
> > - Set `retries` to at most 5.
>
> Single obligation, testable, no explanatory padding. The split with `## Semantics` is correct: the rule is stated in the config field's own unit, and the semantics section defines that unit (so "at most 5" unambiguously means at most 6 total attempts). Keep this as the model for the rules you move in.
>
> ## Structural note
>
> `## Semantics` and `## Background` are both context sections; that is fine, but after applying findings 1 and 2 nothing in either should have directive shape. Optionally collapse them into one `## Context` section so the document has exactly two kinds of content and the reader knows which section binds.
>
> Out of scope for this audit but worth flagging: the frontmatter description scopes the skill to "configuring retries," while the buried production-submission gate concerns batch submission generally. Moving it into `## Rules` will make that scope mismatch visible; the author may want a separate home for it.
>
> ## Suggested revised body
>
> ```markdown
> ## Context
>
> - `--dry-run` still writes to the audit log.
> - `retries` counts attempts after the first; `retries: 2` means three total attempts.
> - `INGEST_ENV` holds the target cluster name, not a region.
> - The pipeline was rebuilt in 2025 after the original queue-based design proved hard to reason about under backpressure.
> - Overview of the pipeline: `docs/ingest-overview.md`.
>
> ## Rules
>
> - Set `retries` to at most 5.
> - Do not submit a batch to the production cluster until the staging replay has completed without errors.
> ```
>
> (If reading the overview doc is meant to be mandatory, add "Read `docs/ingest-overview.md` before changing retry configuration." to `## Rules` and drop the pointer from `## Context`.)

### Baseline, rep 3

> # Audit: `retry-policy` — context vs. constraints
>
> Severity scale used: **Major** = a binding requirement an agent could reasonably read as non-binding (or miss entirely); **Minor** = the obligation is recoverable but phrasing/placement blurs whether or how it binds.
>
> ## Findings
>
> ### 1. Major — Binding rule hidden in Background as a description of practice
>
> > "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
>
> This is the most consequential constraint in the document, and it is the only one *not* in `## Rules`. It is written in descriptive present tense ("Engineers submit…"), sitting between a history note and a reading suggestion, so it reads as an observation about how the team works rather than an instruction. Two ways an agent misses it: (a) it treats the Background section as skippable flavor, or (b) it does not identify as an "engineer" and so does not apply the sentence to itself.
>
> Suggested rewrite (move to `## Rules`, no change in meaning):
>
> ```
> - Submit batches to the production cluster only after the staging replay has completed without errors.
> ```
>
> ### 2. Minor — Hedged directive with unclear binding status
>
> > "Feel free to skim `docs/ingest-overview.md` before making changes."
>
> "Feel free to" and "skim" both signal optionality, but the sentence is still shaped as an instruction, so it is ambiguous whether an agent is expected to read the file. Since the author's phrasing indicates it is optional, the semantic-preserving fix is to restate it as a plain pointer rather than promote it to a rule:
>
> ```
> `docs/ingest-overview.md` gives an overview of the pipeline (optional reading).
> ```
>
> If the author actually intends it as a prerequisite, it belongs in `## Rules` as "Read `docs/ingest-overview.md` before making changes." — but that would change the meaning, so flag for the author rather than apply.
>
> ### 3. Minor — The rule is not self-contained; its meaning depends on a definition in another section
>
> > Rules: "Set `retries` to at most 5."
> > Semantics: "`retries` counts attempts after the first, so `retries: 2` means three total attempts."
>
> The only rule is testable, but its practical effect (at most 6 total attempts) depends on a definition two sections away that the rule does not reference. An agent reading the Rules section in isolation will get it subtly wrong. Suggested rewrite:
>
> ```
> - Set `retries` to at most 5 (i.e. at most 6 total attempts; `retries` counts attempts after the first).
> ```
>
> The definition can stay in Semantics as well; the point is that the constraint should carry what it needs to be applied correctly.
>
> ### 4. Minor — Directive-shaped softeners on facts
>
> > "Remember that the `--dry-run` flag still writes to the audit log."
> > "Note that `retries` counts attempts after the first…"
>
> "Remember that" / "Note that" are imperative lead-ins on statements that are actually facts. They make context look like rules (and dilute the signal of real imperatives elsewhere). Strip them so facts read as facts:
>
> ```
> The `--dry-run` flag still writes to the audit log.
> `retries` counts attempts after the first, so `retries: 2` means three total attempts.
> ```
>
> Additionally, the `--dry-run` fact has an unstated consequence — presumably "do not rely on `--dry-run` to avoid audit-log side effects." If the author intends that as a constraint, it should be stated in `## Rules`; if it is purely informational, the bare fact above is sufficient. Flag for author; do not invent the rule.
>
> ## Items reviewed with no finding
>
> - "`INGEST_ENV` holds the target cluster name, not a region." — plain declarative context, correctly placed.
> - "The pipeline was rebuilt in 2025 …" — pure background, correctly placed.
> - Frontmatter `description` — a trigger condition, not in scope for this audit.
>
> ## Suggested resulting structure
>
> ```markdown
> ## Semantics
> The `--dry-run` flag still writes to the audit log.
> `retries` counts attempts after the first, so `retries: 2` means three total attempts.
> `INGEST_ENV` holds the target cluster name, not a region.
>
> ## Background
> The pipeline was rebuilt in 2025 after the original queue-based design proved hard to reason about under backpressure.
> `docs/ingest-overview.md` gives an overview of the pipeline (optional reading).
>
> ## Rules
> - Set `retries` to at most 5 (at most 6 total attempts).
> - Submit batches to the production cluster only after the staging replay has completed without errors.
> ```
>
> Net: one Major (the staging-replay gate is a real rule masquerading as background), three Minor (hedged optional pointer, non-self-contained rule, imperative softeners on facts). Two open questions for the author: whether the overview doc is required reading, and whether the `--dry-run` audit-log fact is meant to impose a constraint.
