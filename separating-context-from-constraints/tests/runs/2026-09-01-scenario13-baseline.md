# Scenario 13 — design-review, Baseline, three reps (wave 3)

```
Date: 2026-09-01
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, independent dispatches
Prompt: the scenario-13 prompt from `../scenarios.md`, verbatim, preceded by one line: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under `../wave3-2026-08-07/preregistration.md` (planted lists, E2 exclusion registry, E7 lists, E9 fields); tool calls extracted by script
Notes: all three arms made zero tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Planted: D13.1 (known positive). Observation item: D13.2. Adjudication item by treatment: B13.1 (left alone or escalated → neither; definitive rewrite inventing an artifact → false positive). Protected: rule 4, rule 5, Context.

| Rep | D13.1 | E3 on D13.1 | D13.2 (observation) | B13.1 treatment | Protected units criticized | E2 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ✓ Major | assumption-labelled — one definitive rewrite, "confirm it matches intent" | flagged, Major, ground: undefined trigger + actor | left alone ("testable, single obligation") | rule 5 (ambiguous subject); Context ("implies a requirement", author question) | 2 |
| 2 | ✓ Minor | preserved — two options, "author must pick" | flagged, Minor, ground: undefined trigger + actor | left alone | rule 5; Context | 2 |
| 3 | ✓ Major | assumption-labelled — definitive rewrite, "author should confirm" | flagged, Major, ground: undefined threshold + actor | **definitive rewrite** (F4, "Read … before writing any part of the review") — invents no artifact, but neither leaves it alone nor escalates; scored as a false positive, judgment recorded | rule 5; rule 1 (B13.1); Context | 3 |

E9c: guard-lines true ×3 ("Not findings"/"What is already right" name statements); classification-table false ×3; negative-safety-note false ×3.
Contract adherence: none (expected).

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `design-review` — separation of context from constraints
>
> **Overall:** Structurally sound. Rules and Context live in separate, labeled sections; every rule is imperative; there are no hedges ("generally", "try to") and no explanatory padding in the Rules section. The Context section contains no buried directive. The findings below are about individual rules whose binding condition or subject is not testable, plus one implied requirement that lives only in Context.
>
> ## Findings
>
> ### 1. Major — Rule 3 is an untestable directive
> > Keep the review tone professional.
>
> "Professional" has no observable pass/fail criterion; an agent cannot verify compliance and a reader cannot tell what it prohibits. This is the "be concise" class of rule.
>
> Suggested rewrite (narrows to observable behavior; confirm it matches intent):
> > Address the design, not the author. Do not use sarcasm, insults, or dismissive language in the review.
>
> ### 2. Major — Rule 2's trigger condition is undefined
> > For major changes, add an entry to `docs/decisions/`.
>
> The rule binds only when a change is "major", but "major" is never defined, so the agent cannot determine when the obligation fires. The rule also leaves the actor ambiguous: does the reviewer add the entry, or does the reviewer require the design author to add it?
>
> Suggested rewrite (fill in the threshold and actor; both are author decisions, not something I can infer):
> > If the design [meets criterion, e.g. "changes a public interface or replaces an existing component"], do not approve it until an entry exists in `docs/decisions/`.
>
> ### 3. Minor — Rule 5 has an ambiguous subject
> > Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner.
>
> "Without naming" could attach to the design or to the reviewer. The obligation is single (good), but who satisfies it is unclear.
>
> Suggested semantic-preserving rewrite:
> > Do not approve a design that introduces a new external dependency unless the design document names a maintenance owner for that dependency.
>
> ### 4. Minor — Context implies a requirement that no rule states
> > Design reviews were introduced after two rewrites shipped without any written rationale.
>
> This sentence is correctly placed as background, but it implies the review's core purpose is to ensure written rationale exists — and no rule in the Rules section requires the reviewer to check for it. An agent following the flavor text may enforce this; an agent following only the Rules will not. Promoting it would change semantics, so this is a question for the author rather than a rewrite: if "the design document must state its rationale" is a binding requirement, add it to Rules; if it is motivation only, leave Context unchanged.
>
> ## Not findings (checked, clean)
> - Rule 1 ("Read the linked design document in full before proposing an approach") — testable, single obligation.
> - Rule 4 ("Post the review as a single pull request comment rather than as inline comments") — the "rather than" clause is part of the constraint (it prohibits inline comments), not explanatory padding.
> - Frontmatter description — a trigger condition only; contains no rules.
> - No compound rules bundling multiple obligations; no rules embedded mid-paragraph in prose.

### Baseline, rep 2

> # Audit: `design-review` — separation of context from constraints
>
> **Overall:** Good structural separation. Rules live in a dedicated `## Rules` section as imperative bullets; the `## Context` section is a single past-tense descriptive sentence with no embedded directives. No hedging language ("generally", "try to", "prefer"), no explanatory padding in the rule list, no rules buried mid-paragraph. No major findings. Four minor findings below.
>
> ## Findings
>
> ### 1. Minor — Rule 3 is untestable
> > Keep the review tone professional.
>
> "Professional" has no observable criterion; an agent cannot verify compliance, and two agents will apply it differently. It reads as a rule but functions as guidance.
>
> Options (author must pick; each changes semantics slightly):
> - Make it observable: "Address the design, not the author. Do not use sarcasm, insults, or speculation about the author's motives."
> - Or demote it out of `## Rules` into a `## Style` or guidance section so the binding rules remain fully testable.
>
> ### 2. Minor — Rule 2 has an undefined trigger and an ambiguous actor
> > For major changes, add an entry to `docs/decisions/`.
>
> - "Major" is undefined. The agent cannot determine when the rule binds, so it will either over-apply or skip it.
> - The actor is ambiguous in a review skill: does the *reviewer* add the entry, or must the reviewer *require the author* to add one before approval?
>
> Suggested rewrite (semantics to be confirmed by the author):
> "If the design [meets definition of major — e.g. changes a public interface, adds a service, or replaces an existing subsystem], do not approve until an entry exists in `docs/decisions/`."
>
> ### 3. Minor — Rule 5 has an ambiguous actor for "naming"
> > Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner.
>
> The prohibition itself is clear and testable, but "without naming" does not say *who* names the owner or *where*. Readings: (a) the design document must name the owner; (b) the reviewer must name it in the approval comment. Resolve by stating the location.
>
> Suggested rewrite (preserving the reading most consistent with a review gate):
> "Never approve a design that introduces a new external dependency unless the design document names that dependency's maintenance owner."
>
> ### 4. Minor — Context implies an obligation the Rules do not state
> > Design reviews were introduced after two rewrites shipped without any written rationale.
>
> This is correctly placed as context and carries no imperative. However, the stated purpose (ensure written rationale) is only partially covered by the Rules: Rule 2 requires a decisions entry for "major" changes, but nothing requires the reviewer to check that the design document itself contains its rationale. An agent following the flavor text may infer a rule that isn't there, or one following only the Rules may miss the intended purpose.
>
> If a rationale check is intended, promote it to `## Rules` (e.g. "Do not approve a design document that does not state the rationale for the change."). If not, no change needed — the context is fine as background.
>
> ## What is clean
> - Rules 1 and 4 are single-obligation, imperative, and testable as written.
> - Rule 5 is a single conditional prohibition, not a compound rule.
> - Frontmatter description is a plain trigger condition with no rules embedded.
> - No rules are smuggled into the Context section; no context is smuggled into the Rules section.

### Baseline, rep 3

> # Audit: `design-review` — separation of context from constraints
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or read any file, so the format below approximates its conventions (two-level severity, semantic-preserving rewrites) from the description rather than the skill body.
>
> ## Overall
>
> Structure is sound. Rules live in a dedicated `## Rules` section, are imperative, unhedged, and free of explanatory padding. The `## Context` section contains no buried directives. The problems are inside individual rules: two are not reliably testable as written, and two leave the acting party ambiguous. One piece of context carries an implied obligation that the rules never state.
>
> ## Findings
>
> ### F1 — Rule 3 is untestable (Major)
>
> > Keep the review tone professional.
>
> "Professional" gives an agent no observable criterion; it cannot tell whether it complied, and neither can a checker. This is the "be concise" pattern.
>
> Suggested rewrite (narrows to observable behavior; author should confirm this captures the intent):
>
> > Address the design, not its author. Do not use sarcasm, insults, or speculation about the author's motives.
>
> ### F2 — Rule 2 has an undefined threshold and an unclear actor (Major)
>
> > For major changes, add an entry to `docs/decisions/`.
>
> Two gaps. "Major" is undefined, so the trigger condition is a judgment call the agent will resolve inconsistently. And the actor is unclear: does the *reviewer* write the decision entry, or does the reviewer *require the design* to include one? In a review skill, the second reading is more likely, but the sentence says the first.
>
> Suggested rewrite (placeholder marks what only the author can fill in):
>
> > If the design <threshold — e.g. changes a public interface, data schema, or service boundary>, do not approve it until an entry exists in `docs/decisions/`.
>
> If the reviewer genuinely is meant to author the entry, say so explicitly: "…add an entry to `docs/decisions/` yourself before posting the review."
>
> ### F3 — Rule 5 leaves the naming party ambiguous (Minor)
>
> > Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner.
>
> "Without naming" can attach to the design (the document must name an owner) or to the reviewer (the review must name one). The constraint is otherwise clear and testable.
>
> Suggested rewrite:
>
> > Do not approve a design that introduces a new external dependency unless the design document names that dependency's maintenance owner.
>
> ### F4 — Rule 1's trigger does not match the reviewer's role (Minor)
>
> > Read the linked design document in full before proposing an approach.
>
> "Proposing an approach" describes an implementer, not a reviewer. An agent may conclude the rule does not apply to it (it is reviewing, not proposing) and skip the full read. Also "the linked design document" presumes a link exists; fine if the trigger context guarantees it.
>
> Suggested rewrite:
>
> > Read the linked design document in full before writing any part of the review.
>
> ### F5 — Context implies an obligation the rules do not state (Minor)
>
> > Design reviews were introduced after two rewrites shipped without any written rationale.
>
> This is correctly placed as context, but it implies the reviewer should verify that a written rationale exists — and no rule says that. Rule 2 covers only "major" changes and only `docs/decisions/`. An agent following the document's flavor will either invent a rationale check or ignore it; both are unpredictable.
>
> Options: if checking for rationale is expected, add a rule ("Do not approve a design that lacks a stated rationale for the chosen approach"); if not, the context is fine as is and no change is needed.
>
> ## What is already right
>
> - Rules are separated from context by heading, and the context section is pure background.
> - No hedges ("generally", "try to", "consider") anywhere in the rules.
> - Rule 4 (single PR comment, not inline) is a model constraint: clear actor, clear observable outcome.
> - No compound rules bundling independent obligations.
>
> ## Summary
>
> | ID | Rule | Issue | Severity |
> |----|------|-------|----------|
> | F1 | 3 | Untestable ("professional") | Major |
> | F2 | 2 | Undefined threshold ("major"); unclear actor | Major |
> | F3 | 5 | Ambiguous who names the owner | Minor |
> | F4 | 1 | Trigger phrased for implementer, not reviewer | Minor |
> | F5 | Context | Implied rationale-check obligation not stated as a rule | Minor |
