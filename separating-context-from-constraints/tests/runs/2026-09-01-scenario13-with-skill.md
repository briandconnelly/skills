# Scenario 13 — design-review, With-Skill, three reps (wave 3)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, independent dispatches
Prompt: the scenario-13 prompt from `../scenarios.md`, verbatim, preceded by one line: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under `../wave3-2026-08-07/preregistration.md` (planted lists, E2 exclusion registry, E7 lists, E9 fields); tool calls extracted by script
Notes: every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

| Rep | D13.1 | E3 on D13.1 | D13.2 (observation) | B13.1 treatment | Protected units criticized | E2 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ✓ R3 material | preserved (promoted / demoted, none selected) | flagged, **R3 material**, ground: undecidable trigger (+ actor); cross-layer caveat stated | left alone ("verifiable against tool traces") | none — rule 5's locus noted as "observation only, not a finding" | 0 |
| 2 | ✓ R3 material | preserved (three labelled alternatives) | flagged, **R3 minor**, ground: undecidable trigger | left alone | none | 0 |
| 3 | ✓ R3 material | preserved (promoted / demoted) | flagged, **R3 minor**, ground: undecidable trigger; three alternatives incl. "remove the condition (a strengthening the author must opt into)" | left alone | none | 0 |

Standing assertions: 1 (D13.1 R3) pass ×3; observation recorded — D13.2 flagged 3/3, under R3, on the trigger every time; 3 (B13.1 left alone or escalated) pass ×3; 4 (no finding on rules 4–5 or Context) pass ×3. **3/3 scored assertions per rep.**

**R3 report obligation (preregistration, "R3's scope").** Scenario 13's E2 is 0 in every rep, so no false positive was scored on the criterion the arm could not read.
But the observation is the point: three of three with-skill arms flag the undecidable trigger under R3 — the reading the preregistration says R3 "as scoped" does not license — and do so with the author-decision contract intact.
Together with scenario 2 (3/3 arms flag unnamed exception evidence under R3) and 12b (2/3 flag an undecidable retry condition under R3), the arms' R3 is operational determinacy already. The preregistered criterion, not the wording, is what disagrees with them.
Scenario 13's own reachable verdict — "if arms already catch the undecidable trigger under some existing rule and leave the unobservable-but-legitimate obligation alone, R3 needs no rewording" — is reached: caught 3/3 under R3, B13.1 left alone 3/3.

E9c: guard-lines true ×3; classification-table true ×3 (rep 2 by the not-flagged-list rule); negative-safety-note true ×3.
E6: every finding `unique` (line numbers with the frontmatter convention stated, plus quoted text).
Contract adherence: six fields, rule ids, counts, safety note — 3/3.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `design-review`
>
> Line numbers count from the frontmatter (`---` is line 1; the five rule bullets are lines 10–14; the Context sentence is line 18).
>
> ## Classification
>
> - Lines 10–14: binding rules (all imperative or `Never`).
> - Line 18: discretionary context (rationale), correctly placed under `## Context`.
> - Line 3 (frontmatter description): trigger metadata, not audited as a rule.
>
> R1 (structure), R2 (strength), R4 (atomicity), and R5 (precedence) are clean: the document is long-form with a dedicated `## Rules` section that contains no context or facts, every rule states unhedged mandatory strength, each bullet carries one obligation (line 14 is a single condition–action–exception unit sharing one trigger), and no two rules prescribe incompatible outcomes on any realistic input.
>
> ## Findings
>
> **Finding 1 — R3 Verifiability**
> Location: line 12.
> Quoted text: "Keep the review tone professional."
> Why it fails: "professional" names no observable evidence — nothing in the output, tool calls, or repository state lets a reader decide whether the rule was followed or violated. It is the same shape as "be concise". The statement does not reveal the safeguard the author intends (no personal remarks? no sarcasm? a particular register?), so the rewrite is an author decision.
> Severity: Material (prevents verification).
> Suggested rewrite (author decision, alternatives labeled, none selected):
> - Promoted, with observable criteria supplied by the author — for example: "Address the design, not the author: do not characterize the author's competence, motives, or effort, and state each objection as a specific problem with the design." The author should substitute whatever criteria they actually intend; the example only shows the checkable form.
> - Demoted to context, removed from `## Rules`: "Reviews are expected to read professionally; this skill defines no specific tone requirement."
>
> **Finding 2 — R3 Verifiability**
> Location: line 11.
> Quoted text: "For major changes, add an entry to `docs/decisions/`."
> Why it fails: the action (an entry exists in `docs/decisions/`) is checkable against repository state, but the trigger "major changes" is a magnitude judgment with no observable anchor, so a missing entry cannot be distinguished from a correctly skipped one. A secondary ambiguity is the actor: a reviewer whose deliverable is a PR comment (line 13) may not be the party who commits to `docs/decisions/`, and the rule does not say whether the agent writes the entry or requires the design author to. Caveat: if a parent instruction layer or repository convention already defines "major change", this gap is inherited and outside this audit's scope (cross-layer analysis is a non-goal).
> Severity: Material (prevents verification of whether the obligation fired).
> Suggested rewrite (author decision, alternatives labeled, none selected):
> - Observable trigger: "Add an entry to `docs/decisions/` when the design [author-supplied criteria, e.g., introduces a new external dependency, changes a public interface or stored schema, or replaces an existing component]."
> - Judgment surfaced as evidence: "When you judge a change major, add an entry to `docs/decisions/` and state in the review comment that you did so." Note this alternative adds a reporting obligation that the original does not contain; it is offered only because it makes the judgment checkable, and the author must accept that strengthening explicitly.
> - In either alternative, name the actor ("the reviewer adds…" or "require the author to add… before approval").
>
> ## Not flagged (false-positive guards)
>
> - Line 10 ("Read the linked design document in full before proposing an approach."): verifiable against tool traces; clean.
> - Line 13 (single PR comment, not inline): verifiable against GitHub state; clean.
> - Line 14 (never approve a new external dependency without a named maintenance owner): verifiable; one trigger with an exception, so it is atomic under R4. Observation only, not a finding: "without naming" leaves it slightly open whether the owner must appear in the design document or in the review comment. Behavior is checkable under either reading, so this does not meet the R3 bar, but the author may wish to pin the locus.
> - Line 18 (history of why design reviews exist): discretionary context, correctly outside `## Rules`. It hints at a "written rationale" requirement, but that is already carried by line 11 rather than buried here.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: Material 2, Minor 0. Total findings: 2 (no secondary rule ids, so the per-rule total equals the severity total).
>
> This is a well-separated document: rules live in a dedicated section free of context, the single context sentence is correctly placed, every rule signals mandatory strength without hedging, obligations are atomic, and no reachable precedence conflict exists. The only defects are two rules whose triggers or content are not checkable against observable evidence — "professional" tone (line 12) and the "major changes" condition (line 11) — and both require an author decision rather than a mechanical rewrite, because the document does not reveal the intended safeguard in either case.

### With-skill, rep 2

> # Audit: `design-review`
>
> Line numbers refer to the fenced document as given (line 1 = opening `---`).
>
> ## Findings
>
> **R3 Verifiability**
> Location: line 12 (`## Rules`, third item).
> Quoted text: "Keep the review tone professional."
> Why it fails: there is no observable evidence — output, tool call, or artifact — against which "professional" can be checked. The rule is of the same shape as "be concise": a reader cannot tell whether a given review complied or violated it, so it can neither be reliably followed nor audited. The statement does not reveal which safeguard the author intended.
> Severity: material.
> Suggested rewrite: this requires an author decision because the statement does not identify the intended safeguard.
> If specific conduct is intended, name the observable behavior, e.g. "Address the design, not its author: do not characterize the author or their competence, and state each objection as a concrete defect in the document." (checkable against the posted comment text).
> If the statement is only intent or framing, remove it from `## Rules` and place it in `## Context` as nonbinding: "Reviews are expected to be professional in tone; this document defines no specific tone rule."
> If another safeguard is intended (e.g. a template or a required structure for objections), name its observable output instead of choosing either example.
>
> **R3 Verifiability**
> Location: line 11 (`## Rules`, second item).
> Quoted text: "For major changes, add an entry to `docs/decisions/`."
> Why it fails: the action is checkable in repository state (an entry exists or does not), but the trigger "major changes" has no observable criterion, so for any change that is not obviously large an auditor cannot determine whether the obligation applied and therefore whether it was met. This is a partial verifiability gap — the intended behavior (record decisions for significant changes) is clear, which is why this is not rated material.
> Severity: minor.
> Suggested rewrite: this requires an author decision about what "major" means.
> If an observable threshold is intended, state it, e.g. "Add an entry to `docs/decisions/` when the design introduces a new external dependency, changes a public interface, or requires a data migration."
> If reviewer judgment is intended, say so explicitly so the discretion is visible: "Add an entry to `docs/decisions/` when, in the reviewer's judgment, the change is major; state that judgment in the review."
> The rule's actor (author vs. reviewer) is also unstated; the rewrite should name who adds the entry, but that choice is the author's.
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Read the linked design document in full before proposing an approach." — binding, mandatory, atomic, and checkable against tool traces (the document read precedes the proposal). Correctly placed.
> - Line 13, "Post the review as a single pull request comment rather than as inline comments." — binding, explicit, checkable against the PR. Correctly placed.
> - Line 14, "Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner." — condition–action–exception sharing one trigger, which R4 permits as a single unit; checkable against the approval and the named owner. Correctly placed.
> - Line 18, the origin-of-design-reviews sentence — discretionary context (rationale that degrades gracefully if lost) and correctly kept out of `## Rules`.
> - R1: the `## Rules` section contains no context or load-bearing facts, and `## Context` contains no buried rules. No finding.
> - R2: every rule uses unhedged mandatory wording (imperative or "never"); the conditional in line 11 is explicit. No finding.
> - R5: no two rules prescribe incompatible outcomes on a realistic input (the comment-format rule, the decision-record rule, and the dependency-approval rule govern different decisions). No finding.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 1 (R3), minor 1 (R3).
> No finding carries a secondary rule id, so the per-rule total of two equals the two findings counted by severity.
>
> This is a structurally sound document: rules and context are already separated into labeled sections, every rule signals mandatory strength, no rule is compound, and no reachable precedence conflict exists. The only defects are on the verifiability axis — one rule ("professional" tone) is entirely unverifiable and should be either replaced with a named observable safeguard or demoted to context, and one rule's trigger ("major changes") lacks an observable threshold. Both require author decisions before a rewrite can claim to preserve intended behavior; the tone finding is the one that could plausibly change reviewer behavior or prevent an auditor from checking compliance.

### With-skill, rep 3

> ## Audit: `design-review`
>
> Files consulted: `/Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md` and `/Users/bdc/projects/skills/separating-context-from-constraints/references/example-audit.md`. Line numbers below count from the opening `---` of the frontmatter as line 1.
>
> ### Classification
>
> | Line | Statement | Class |
> |---|---|---|
> | 3 | `description: Use when reviewing a design document before implementation.` | Binding rule (invocation trigger), structurally marked by the frontmatter field |
> | 10 | Read the linked design document in full before proposing an approach. | Binding rule — mandatory, checkable against tool traces, atomic |
> | 11 | For major changes, add an entry to `docs/decisions/`. | Binding rule — mandatory conditional, action checkable against repository state (see Finding 2 on the trigger) |
> | 12 | Keep the review tone professional. | Binding rule — mandatory, not checkable (Finding 1) |
> | 13 | Post the review as a single pull request comment rather than as inline comments. | Binding rule — mandatory, checkable against PR state, atomic |
> | 14 | Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner. | Binding rule — mandatory condition–action–exception on one trigger, checkable against the approval decision and review text |
> | 18 | Design reviews were introduced after two rewrites shipped without any written rationale. | Discretionary context, correctly placed under `## Context` |
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> Location: line 12, `## Rules`.
> Quoted text: "Keep the review tone professional."
> Why it fails: "professional" names no observable evidence — no output pattern, tool call, or artifact — against which compliance can be checked, in the same way the skill's example "Be concise" cannot be checked. The statement does not reveal which behavior the author wants to prevent, so the intended safeguard is unknown.
> Severity: material (prevents verification).
> Suggested rewrite: author decision; the auditor does not select.
> - Promoted (binding, with observable criteria): "Address the design, not its author: the review contains no personal remarks, sarcasm, or profanity." If a different safeguard is intended (for example, a required structure such as "state each concern as a question or a concrete change request"), name its observable form instead of adopting this example.
> - Demoted (nonbinding context, moved out of `## Rules` into `## Context`): "Reviews are expected to read professionally; this skill defines no checkable tone requirement."
>
> **Finding 2 — R3 Verifiability**
> Location: line 11, `## Rules`.
> Quoted text: "For major changes, add an entry to `docs/decisions/`."
> Why it fails: the obligation itself is verifiable (an entry under `docs/decisions/` either exists or does not), but the trigger "major changes" is undefined, so for any change where no entry was added, a checker cannot determine whether the rule was violated or simply did not apply. This is narrower than Finding 1: the safeguard is clear, only the threshold is not, and compliance remains checkable for plainly major changes.
> Severity: minor.
> Suggested rewrite: author decision among alternatives; the auditor does not select.
> - (a) Define the trigger by observable properties: "For changes that [author to specify — e.g., alter a public interface, add or remove a service, or change a stored data schema], add an entry to `docs/decisions/`."
> - (b) Make the classification itself observable while keeping it a judgment call: "State in the review whether the change is major; for major changes, add an entry to `docs/decisions/`."
> - (c) Remove the condition (a strengthening the author must opt into explicitly): "Add an entry to `docs/decisions/` for every reviewed design."
>
> ### Not flagged (false-positive guards)
>
> - Line 18 is discretionary rationale, placed under `## Context` and absent from `## Rules` — correct under R1.
> - Lines 10, 13, 14 are mandatory, atomic, and verifiable; no hedges (R2), no bundling (R4).
> - Line 14's "without naming that dependency's maintenance owner" is an exception sharing the rule's single trigger, which R4 permits as one unit.
> - R5: no pair of rules prescribes incompatible outcomes for the same decision on a realistic input (lines 13 and 14 govern different decisions; lines 10 and 11 govern different phases). No precedence statement is required.
> - The `## Rules` section contains no context or load-bearing facts, and the document uses a dedicated labeled rules section as R1 requires for long-form documents.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 1 (R3), minor 1 (R3). Total findings: 2. No finding carries a secondary rule id, so the per-rule total equals the severity total.
>
> This is a well-separated document: rules live in a labeled `## Rules` section, every rule is stated in unhedged imperative or "never" form, no rule bundles multiple obligations, and the single background sentence is correctly quarantined in `## Context`. The two findings are both verifiability gaps — one material ("professional" tone names no checkable evidence and needs the author to either supply observable criteria or demote it to context) and one minor (the "major changes" threshold is undefined, though the obligation it gates is checkable). Both require author decisions before a rewrite can claim to preserve intended behavior.
