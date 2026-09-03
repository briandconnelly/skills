# Scenario 9R — Trigger Discrimination (parts 1, 2, 1n, and the part-2 known positive)

Eleven arms, all dispatched 2026-09-01 after the step-4 reviews of `4e3c01f`, `de3eb63`, and the hygiene commit `b2f11be` (Codex jobs `6282abe27dfa42f59e27f37c3fcf9fd3` and `27e5076462324f41b677263622ff48a5`; the last verdict was "concerns" with no semantic finding).
Three reps of part 1, each continued into part 2 in the same session; three reps each of 1n-a and 1n-b; two reps of the part-2 known-positive control.
Transcripts were copied to the session scratchpad at scoring time and every tool call was extracted by script: the six part-1n arms and both controls made **zero** tool calls; each part-1 arm made zero in part 1 and exactly two in part 2 — `Skill: separating-context-from-constraints`, then a read of `references/example-audit.md` through the `~/.claude/skills/` symlink, which resolves to the checkout. No arm read anything under `tests/`.
Every arm's system prompt also carried the harness's own installed-skill listing, which includes this skill's frontmatter description; that listing repeats the catalog text and adds no vocabulary, and is recorded here because it is a condition of this harness, not of the preregistration.

## Provenance

```
Date: 2026-09-01
Run: trigger
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent; part 2 delivered by resuming the part-1 agent (same session, second user turn)
Prompt: parts 1, 1n-a, 1n-b, and 2 verbatim from `../scenarios.md` "Scenario 9R", each preceded by one line forbidding file reads, tool calls, and skill loading (lifted for part 2, with `tests/` still forbidden)
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; selection and rule-id fields extracted by script from the archived transcripts, then read by hand
Notes: the two controls are filed under `control` below with their own block
```

```
Date: 2026-09-01
Run: control
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent; part 2 delivered by resuming the part-1 agent (same session, second user turn)
Prompt: part 2 verbatim, preceded by: "Earlier in this workflow a skill named `separating-context-from-constraints` was chosen for the task below, but that skill is not available in this session and cannot be loaded. Do the review yourself from this prompt alone: do not read any files, do not call any tools, and do not load any skill."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; selection and rule-id fields extracted by script from the archived transcripts, then read by hand
Notes: known positive for assertion 4 — a session in which the body was never loaded; the skill's name was given, its body was not
```

## Results

### Part 1 — selection (three reps)

| # | Assertion | rep 1 | rep 2 | rep 3 | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Selects `separating-context-from-constraints` | PASS | PASS | PASS | first backticked skill name in each answer, extracted by script |
| 2 | Justification names obligations indistinguishable from commentary, not only the file type | PASS | PASS | PASS | all three cite "reviewers unable to agree which sentences bind" / "which sentences bind" and "skipping required steps" |
| 3 | Does not select `agent-friendly-docs` on the instruction-file ground | PASS | PASS | PASS | all three name `agent-friendly-docs` only to note that it excludes this audit |

### Part 2 — body loading (three reps, same sessions)

| # | Assertion | rep 1 | rep 2 | rep 3 | Evidence |
| --- | --- | --- | --- | --- | --- |
| 4 | Output contains a rule id of the form R1–R5 | PASS | PASS | PASS | script: `{R1,R2,R3,R4,R5}` present in every part-2 output; absent from every part-1 answer |
| — | *Observation:* `six-field-format-without-id` / `clean-verdict-without-id` | neither | neither | neither | every part-2 output carries ids, so the branches are moot |

### Part 2 known positive — two control reps

| Question | rep 1 | rep 2 | Evidence |
| --- | --- | --- | --- |
| No R1–R5 id appears when the body was never loaded | PASS | PASS | script: no `R[1-5]` token in either output; rep 2 invents its own `F1`–`F3` labels, rep 1 uses "higher/lower severity" |
| Recorded observations | six-field format absent; no clean verdict | six-field format absent; no clean verdict | both controls produce free-form findings and, unprompted, a restructured after-document |

Assertion 4's check can fail: the same prompt without the body produced no rule id twice, so the three part-2 passes are evidence that the body loaded.

### Part 1n — negative control (three reps each; gate satisfied by part 1 above, same model, harness, and catalog)

| Request | Field | rep 1 | rep 2 | rep 3 | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1n-a | `over-selection` | false | false | false | no rep selects this skill |
| 1n-a | `correct-alternative` | true | true | true | all select `agent-friendly-docs` |
| 1n-b | `over-selection` | false | false | false | no rep selects this skill |
| 1n-b | `correct-alternative` | true | true | true | all select `agent-friendly-mcp` |

Every 1n rep also volunteers, unasked, why this skill does *not* apply — two of the 1n-a reps and all three 1n-b reps name it as the rejected alternative. That is not scored; it is recorded because it shows the over-selection detector was exercised, not merely un-triggered.

### Totals

Part 1: 3/3 assertions on all three reps. Part 2: 1/1 on all three reps, known positive 2/2. Part 1n: 4/4 on all three reps.
The preregistered reachable verdict in which nothing changes was reached on every part: selection correct, body loading confirmed, `over-selection = false` on both requests.
W12 closes with the catalog rebuilt; review finding F5 closes; W21 has no over-triggering evidence and its description decision rests on part 1 and body loading alone.

## Scored Outputs (verbatim, extracted from the transcripts)

### Part 1, rep 1

> `separating-context-from-constraints` — the symptoms (agents echoing philosophy while skipping required steps, reviewers unable to agree which sentences bind) are exactly the rules-vs-context separation problem this skill audits in CLAUDE.md files, whereas `agent-friendly-docs` explicitly excludes rules-vs-context audits of instruction-file content.

### Part 1, rep 2

> `separating-context-from-constraints`: the symptoms (agents echoing the philosophy while skipping required steps, and reviewers unable to agree which sentences bind) are exactly the rules-vs-context separation problem in an instruction file that this skill audits, whereas `agent-friendly-docs` explicitly excludes rules-vs-context audits of instruction-file content.

### Part 1, rep 3

> `separating-context-from-constraints` — the symptoms (agents echoing the philosophy while skipping required steps, and reviewers unable to agree on which sentences bind) are exactly the rules-vs-context problem this skill audits in a CLAUDE.md, which `agent-friendly-docs` explicitly excludes.

### Part 2, rep 1 (same session as part 1 rep 1)

> Audit of `deploy-helper` using `separating-context-from-constraints` (skill loaded from `/Users/bdc/.claude/skills/separating-context-from-constraints/SKILL.md`, worked example read from `references/example-audit.md`; nothing under `tests/` was read and no files were edited).
>
> **Classification**
>
> The document has no sections, so it is compact under R1: rules must be marked inline by imperative sentences, list items, or mandatory wording.
>
> - Line 3, "Deploys are cut weekly." — informs rather than directs. Losing it could make output wrong (an agent might expect or schedule a deploy at the wrong cadence), so it is a load-bearing fact, not a rule. Correctly left unmarked. Not flagged.
> - Line 4, "Try to keep the release notes short." — directs behavior (an imperative), so it is a rule candidate. Marked inline as an imperative, satisfying R1's compact-form requirement. It fails R2 and R3 below.
>
> **Findings**
>
> **R2 Explicit strength** (secondary: R3 Verifiability)
> Location: line 4.
> Quoted text: "Try to keep the release notes short."
> Why it fails: "Try to" hedges strength; a reader cannot tell whether short release notes are required or merely encouraged, so the statement can be neither reliably followed nor checked. Secondarily, "short" names no observable threshold (line count, word count, section limit), so even a promoted reading cannot be verified against output without an author-supplied bound.
> Severity: material.
> Suggested rewrite: author decision between two non-hedged readings.
> Promoted (mandatory): "Keep release notes to N lines or fewer," where N is a bound the author must supply; the audit cannot choose it without inventing policy.
> Demoted (context): "Release notes are usually short; this document does not require a length limit." Placed as context, not as a directive.
> A defeasible default ("Prefer short release notes unless X") is not offered, because nothing in the document indicates a binding preference is intended.
>
> **R1**: no findings. **R4**: no findings (the single obligation is atomic). **R5**: no findings (only one rule; no reachable conflict).
>
> **Safety note**
>
> None. The document contains no instructions directed at the auditor and requests no tool actions.
>
> **Summary**
>
> Counts per rule: R1 0, R2 1, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0.
> One finding carries a primary R2 id and a secondary R3 id, so the per-rule total of two exceeds the single finding counted by severity.
>
> This two-line document keeps its one load-bearing fact (weekly deploy cadence) correctly unmarked and states its one behavioral directive as an inline imperative, which is the right form for a compact document. The directive itself, however, is hedged and names no checkable threshold, so the document's only rule cannot be confidently classified as binding or verified once followed. The R2 finding requires an author decision (promote with a numeric bound, or demote to context) before a semantics-preserving rewrite can be claimed.
>
> My earlier routing answer stands: `separating-context-from-constraints` is the skill for the 300-line CLAUDE.md problem, and this audit illustrates the kind of output it produces.

### Part 2, rep 2 (same session as part 1 rep 2)

> **Audit of `deploy-helper`** (using `separating-context-from-constraints`)
>
> Document class: compact (a single flat description with no sections), so rules must be marked inline by imperative or explicit mandatory wording.
>
> ## Findings
>
> **R2 Explicit strength** (secondary: R3 Verifiability)
> Location: line 4.
> Quoted text: "Try to keep the release notes short."
> Why it fails: "Try to" hedges the strength, so a reader cannot tell whether release-note length is a binding requirement or a preference; and even if it binds, "short" names no observable threshold (line count, word count, section count) against which output could be checked.
> Severity: material — the only candidate rule in the document can be either skipped as optional or followed without any way to verify compliance.
> Suggested rewrite: this is an author decision between two non-hedged readings, and the promoted reading also needs a threshold the document does not supply.
> Promoted (mandatory): "Keep release notes to N lines or fewer." — the author must choose N (or another observable bound such as a word count or fixed section list); the auditor does not select one.
> Demoted (context): "Release notes are customarily kept short; this document does not require a length." — stated as nonbinding background, not as a rule.
> A defeasible default (for example "Keep release notes under N lines unless a release includes breaking changes") is offered only as a third alternative if the author intends some binding preference; the target does not indicate which.
>
> Not flagged (false-positive guard): line 3, "Deploys are cut weekly." This informs rather than directs; it is a load-bearing environmental fact about cadence (an agent that assumed a daily cut would be wrong), so it is correctly stated as context and needs no restructuring in a compact document.
>
> ## Summary
>
> Counts per rule: R2 1, R3 1 (secondary on the same finding).
> Counts per severity: material 1, minor 0. One finding total; the per-rule total of two exceeds it because the single finding carries a secondary id.
> Safety note: none — the document contains no auditor-directed instructions.
>
> The document contains one factual context statement and one hedged, unverifiable directive. The cadence fact is correctly placed. The release-notes sentence is the document's only candidate rule and neither signals whether it binds nor supplies a checkable bound; resolving it requires the author to decide first whether it binds and, if so, what "short" means in observable terms. No R1, R4, or R5 findings: with only one directive there is nothing to separate, bundle, or conflict.
>
> ---
>
> Earlier routing answer stands: `separating-context-from-constraints` is the single skill for the three-hundred-line CLAUDE.md, because agents echoing philosophy while skipping required steps and reviewers disagreeing about which sentences bind are precisely the rules-vs-context separation problem this skill audits (and `agent-friendly-docs` explicitly excludes that audit).

### Part 2, rep 3 (same session as part 1 rep 3)

> Audit of `deploy-helper` using `separating-context-from-constraints` (skill body plus `references/example-audit.md` read; nothing under `tests/` touched, no files edited).
>
> **Classification**
>
> - Line 3, "Deploys are cut weekly." — informs rather than directs; a load-bearing fact about release cadence. Declarative, not imperative, so in a compact (sectionless) document it is already distinguishable as context. Not flagged.
> - Line 4, "Try to keep the release notes short." — directs behavior; it is the document's only rule.
>
> **Findings**
>
> **R2 Explicit strength** (secondary: R3 Verifiability)
> Location: line 4.
> Quoted text: "Try to keep the release notes short."
> Why it fails: "Try to" hedges strength, so a reader cannot tell whether the statement binds or is merely encouraged; and "short" names no observable threshold (line count, word count, section limit), so even a promoted reading could not be checked against the produced release notes.
> Severity: material.
> Suggested rewrite: this is an author decision; the auditor must not select one.
> - Promoted (mandatory): "Keep release notes to N lines or fewer." The author must supply the observable limit N (or an equivalent checkable bound); the audit cannot infer it.
> - Demoted (context, outside any rule): "The team prefers short release notes; this document does not enforce a length."
> - Default with override (only if the author intends a binding preference, which "try to" weakly suggests): "Keep release notes to N lines or fewer unless the release requires more detail." Again N must come from the author.
>
> Not flagged (false-positive guard): line 3 is a load-bearing fact, correctly stated as context and not as a rule. No R1 finding: the document is compact and its single rule is already an inline imperative. No R4 finding: one obligation. No R5 finding: no two rules can conflict.
>
> **Summary**
>
> Counts per rule: R2 1, R3 1 (secondary id on the same finding).
> Counts per severity: material 1, minor 0. The per-rule total of two exceeds the one finding because that finding carries a secondary id.
>
> The document is one context sentence and one rule. The context is correctly placed and distinguishable. The sole rule is defective on two axes: its strength is hedged so it is unclear whether it binds, and its target ("short") is unverifiable, so no rewrite can preserve semantics until the author decides whether it is mandatory, a default, or non-binding preference, and supplies an observable length bound if it binds.
>
> **Safety note**: none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> Routing answer from the prior turn stands: `separating-context-from-constraints` is the single skill for the 300-line CLAUDE.md problem, since agents echoing philosophy while skipping required steps and reviewers disagreeing over which sentences bind is precisely the rules-vs-context audit it performs and `agent-friendly-docs` excludes.

### Part 1n-a, rep 1

> `agent-friendly-docs` — the problem is README token bloat on an agent's read path (a repo documentation surface being read whole every session), which that skill names directly under placement, discoverability, and token economy, whereas `separating-context-from-constraints` only audits whether rules are separated from context inside an instruction document, not the size or layering of the docs surface itself.

### Part 1n-a, rep 2

> `agent-friendly-docs` — the problem is README token bloat and read-path structure (agents reading a whole 4,000-word file they rarely need), which is squarely that skill's territory of layering, placement, and token economy for the documentation surface agents read, not a rules-vs-context audit.

### Part 1n-a, rep 3

> `agent-friendly-docs` — the problem is README token bloat and layering/placement of repo documentation that agents read every session, which is exactly that skill's stated scope, whereas `separating-context-from-constraints` only audits rules-vs-context in instruction files and `agent-friendly-github` covers repo safety configuration rather than doc structure.

### Part 1n-b, rep 1

> `agent-friendly-mcp` — the problem is tool-surface design (a large tool count with overlapping, undifferentiated tools and no guidance on which to pick), which is exactly the "agents picking the wrong tool from many candidates" symptom that skill exists to diagnose and fix.

### Part 1n-b, rep 2

> `agent-friendly-mcp` — the problem is tool-surface design on an MCP server (sixty overlapping tools with nothing telling agents which "list resources" tool to pick), which is exactly the "agents picking the wrong tool from many candidates" symptom that skill owns, whereas `separating-context-from-constraints` only audits whether an individual description separates rules from context, not whether the tool set itself is disambiguated.

### Part 1n-b, rep 3

> `agent-friendly-mcp` — the problem is tool-selection ambiguity in an MCP server (many candidates, overlapping tools, no guidance on which to use when), which is exactly the tool-design and schema-hardening territory that skill covers, whereas `separating-context-from-constraints` only audits whether existing description text separates rules from context and would not fix redundant or poorly differentiated tools.

### Part 2 known-positive control, rep 1

> I could not load `separating-context-from-constraints` in this session, so this review follows the skill's published contract (findings with two-level severity, semantic-preserving rewrites, no score, no parent-layer conflict analysis, no general prose critique) rather than its exact procedure. Severity labels below are my approximation of its two levels.
>
> ## Findings
>
> ### 1. Hedged, untestable directive — `Try to keep the release notes short.` (higher severity)
>
> Two problems stacked on one line:
>
> - **Hedge leaves binding status unclear.** "Try to" does not tell an agent whether short release notes are a requirement it must satisfy or a preference it may trade off. An agent can write long notes and honestly claim compliance ("I tried").
> - **Untestable predicate.** "Short" has no threshold. Neither the agent nor a reviewer can determine whether a given set of release notes passes.
>
> The document does not contain enough information to pick a threshold without inventing one, so the rewrite has to make the author choose. Two semantic-preserving options:
>
> - If it binds: `Release notes MUST be short.` — and the author must supply the bound (e.g. a line or word limit, or "one line per user-visible change"). Without a bound this remains untestable even after the hedge is removed.
> - If it is a preference: `Prefer short release notes; longer notes are acceptable when needed.` — this makes the non-binding status explicit rather than implied by "try to".
>
> Do not add a specific number in the rewrite unless the author confirms it; that would change meaning.
>
> ### 2. Context and rule interleaved with no separation (lower severity)
>
> `Deploys are cut weekly.` is a background fact, and the next line is a directive. They sit together as undifferentiated prose with no marker telling the agent which line it must obey and which it should merely know. In a two-line document this is survivable, but it is the exact pattern that scales badly as the file grows.
>
> Suggested structure (no wording changes):
>
> ```markdown
> # deploy-helper
>
> ## Context
> Deploys are cut weekly.
>
> ## Rules
> - <rule from finding 1, once the author chooses binding vs. preference>
> ```
>
> ### 3. Descriptive statement that could be read as prescriptive — `Deploys are cut weekly.` (lower severity)
>
> As written this is a fact about cadence. An agent could also read it as an implicit constraint ("do not cut a deploy outside the weekly cadence"). If it is meant only as context, placing it under a Context heading (finding 2) resolves the ambiguity. If it is actually a rule, it should be rewritten as one: `Cut deploys weekly; do not cut off-cycle deploys.` — but only if that is the author's intent, since it adds an obligation the current text does not state.
>
> ## Summary
>
> - 1 higher-severity finding: the only directive in the document is both hedged and untestable.
> - 2 lower-severity findings: no structural separation between context and rules; the context line is ambiguously prescriptive.
> - Action required from the author before any rewrite can be finalized: decide whether "short release notes" is binding, and if so, define "short".

### Part 2 known-positive control, rep 2

> Note: per the launch instructions I did not load the skill or call any tools; this review applies the skill's stated method (context-vs-constraint separation, two-level severity, semantic-preserving rewrites, no scoring) from memory of its description.
>
> ## Review: `deploy-helper`
>
> **Document under review**
>
> ```markdown
> # deploy-helper
>
> Deploys are cut weekly.
> Try to keep the release notes short.
> ```
>
> ### Findings
>
> **F1 — Major — Hedged directive: "Try to keep the release notes short."**
> "Try to" leaves it undecidable whether this binds. An agent can satisfy it by attempting and failing, or ignore it as a soft preference; neither reading is wrong as written. Additionally, "short" has no observable test — two agents could produce a 3-line and a 30-line note and both claim compliance.
> Semantic-preserving rewrite (author must pick the intended branch):
> - If binding: `Release notes MUST be short. [Author: define "short" — e.g. a maximum bullet or line count.]`
> - If non-binding: `Preference (non-binding): shorter release notes are preferred.`
> The bracketed placeholder is deliberate — I have not invented a limit, because the current text does not contain one.
>
> **F2 — Major — Ambiguous status: "Deploys are cut weekly."**
> Written as a statement of fact, but its position in a document named `deploy-helper` (consumed as instructions) makes it read either as background ("this is our cadence") or as a rule ("do not cut a deploy outside the weekly schedule"). The document gives no signal which. If it is a rule, it is buried in narrative prose; if it is context, it is unlabeled and an agent may over-enforce it.
> Semantic-preserving rewrite (author must pick):
> - If context: move under a `## Context` heading unchanged.
> - If binding: `Rule: Cut deploys only on the weekly schedule. Do not cut ad hoc deploys.` (Author: state which day/trigger constitutes "weekly" so the rule is testable.)
>
> **F3 — Minor — No structural separation between context and rules.**
> Both sentences sit in a single unlabeled block under the title. There is no section that tells an agent "these are the things you must do" versus "this is background." F1 and F2 are symptoms of this; fixing the structure resolves the ambiguity even if the wording of each line stays close to the original.
>
> ### Suggested restructured document
>
> ```markdown
> # deploy-helper
>
> ## Context
> Deploys are cut weekly.
>
> ## Rules
> - Release notes MUST be short. [Author: define a maximum bullet/line count.]
> ```
>
> If "Deploys are cut weekly" is meant to bind, move it into `## Rules` using the F2 rewrite instead.
>
> ### Out of scope (per the skill's boundaries)
> No score assigned; no analysis of conflicts with parent CLAUDE.md/AGENTS.md layers; no general prose-quality comments beyond what affects whether a line binds and is testable.
