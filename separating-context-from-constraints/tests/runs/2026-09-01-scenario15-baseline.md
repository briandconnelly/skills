# Scenario 15 — support-triage, Baseline, three reps (wave 3, W11)

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

Nine R2 defects (D15.1, 2, 3, 4, 5, 7, 9, 11, 12). D15.6 is a W10-gap observation, D15.8 an adjudication item, D15.10 the false-positive probe (protected).

| Rep | E1 (of 9) | D15.6 | D15.8 | D15.10 | Other protected units criticized | E2 | E3 over the nine | Words (× target 193) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9/9 | flagged (H1 table) | flagged, Low (L2) | **flagged, Low (L1)** | none | 1 | assumption-labelled 5 (D15.1, 3, 5, 7, 11 carry "author decision"); silent-selection 4 (D15.2, 4, 9, 12 promoted with no flag) | 1197 (6.2×) |
| 2 | 9/9 | flagged | flagged, Low | **flagged, High** | none | 1 | assumption-labelled 9 (the report frames every rewrite as branch (a) of a stated per-item author decision) | 1056 (5.5×) |
| 3 | 9/9 | flagged (F6) | flagged, Minor (F12) | **flagged, Major (F5)** | none | 1 | assumption-labelled 9 (F1 frames the per-bullet decision; F3, F5 offer both branches) | 1094 (5.7×) |

E9a: rep 1 `absent`; rep 2 `absent`; rep 3 `partial` (a "Recommended shape" Rules/Defaults skeleton), `unrequested`.
E9c: guard-lines true ×3; classification-table false ×3; negative-safety-note false ×3.
Contract adherence: none (expected).

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `support-triage` — separation of context from constraints
>
> **Scope note.** Per your instruction I audited the document as pasted, with no files, tools, or skills loaded. Severity is two-level: **High** = an agent following this document could reasonably conclude a rule does not bind (or cannot tell what compliance looks like); **Low** = clarity or structure issue that does not change what the agent will do.
>
> ## Summary
>
> Structurally the document is already in good shape: rules are in a `## Rules` list, the `## Context` section contains no directives, and the description is a clean trigger. The problem is inside the rules list. Of 14 bullets, only 3 (acknowledge within one business day, avoid promising a fix date, never share another customer's ticket) are stated as binding. The other 11 carry a hedge (`generally`, `try to`, `usually`, `it is preferable`, `consider`, `where possible`, `should normally`, `ideally`, `feel free to`, `aim to`, `typically`) that leaves an agent unable to tell whether the bullet is a requirement, a default with unstated exceptions, or a description of current practice. Because these sit in the same list as `Acknowledge every ticket` and `Never share`, the hedges also dilute the firm rules by association.
>
> Every rewrite below is intended to preserve meaning. Where the hedge genuinely encodes an exception the author has in mind, the rewrite keeps a slot for it rather than inventing one — those are marked **author decision**.
>
> ## High
>
> **H1. Hedged obligations — 10 bullets.** Each of the following reads as a rule but the qualifier makes binding status ambiguous. For each, the fix is one of: (a) state it as an imperative, (b) state it as an imperative plus the specific exception the hedge was covering, or (c) move it to Context as a description of practice. Suggested rewrites use (a) or (b); the author should confirm no exception is being silently dropped.
>
> | # | Current | Suggested rewrite |
> |---|---|---|
> | 2 | Generally assign severity before assigning an owner. | Assign severity before assigning an owner. *(author decision: if there is a case where owner comes first, name it.)* |
> | 3 | Try to reproduce the reported behavior before asking the reporter for more detail. | Attempt to reproduce the reported behavior before asking the reporter for more detail. *(The sequencing is the testable part; "try to" hid it.)* |
> | 4 | Usually escalate to on-call when a ticket mentions data loss. | Escalate to on-call when a ticket mentions data loss. *(author decision: "usually" on a data-loss trigger is the most consequential hedge in the document — if an exception exists it must be spelled out here.)* |
> | 5 | It is preferable to link the ticket to an existing issue rather than opening a new one. | If a matching issue exists, link the ticket to it instead of opening a new one. *(Also supplies the missing condition; "preferable" gave no trigger.)* |
> | 6 | Consider closing tickets with no reporter response after fourteen days. | Close tickets that have had no reporter response for fourteen days. *(author decision: "consider" may mean this is discretionary — if so, state it as permission: "You may close…")* |
> | 7 | Where possible, tag the affected component. | Tag the affected component. If it cannot be determined, [state what to do — e.g. leave untagged / tag `unknown`]. *("Where possible" is an undefined condition.)* |
> | 8 | Tickets from enterprise accounts should normally be triaged first. | Triage tickets from enterprise accounts before others in the queue. *(author decision: "should normally" is a double hedge; name the override if one exists, e.g. data-loss tickets from any account.)* |
> | 10 | Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document. | Record reproduction steps in the ticket itself, not in a linked document. |
> | 12 | Aim to keep the triage note under a paragraph. | Keep the triage note under a paragraph. *(author decision: if a longer note is acceptable in some case, name it.)* |
> | 13 | Duplicate tickets are typically closed in favor of the older one. | Close duplicate tickets in favor of the older ticket. *(Also fixes passive/descriptive voice — as written this describes what happens rather than instructing.)* |
>
> **H2. Firm and hedged rules are interleaved in one list.** Rules 1, 9, and 14 are unambiguous; the rest are not. An agent scanning a uniform bullet list has no signal that `Never share another customer's ticket contents` is categorically different from `Feel free to reassign`. If the author's intent is that some bullets are hard requirements and others are defaults, split the section: `## Rules` (binding, no hedges) and `## Defaults` (each stated with its exception). If the intent is that all bind, apply H1 and the split is unnecessary.
>
> ## Low
>
> **L1. Permission stated as a rule (bullet 11).** "Feel free to reassign a ticket if it lands in the wrong queue" is a grant of permission, not an obligation, but it sits in a list of obligations. Rewrite to make the modality explicit: "You may reassign a ticket that has landed in the wrong queue." If it is actually meant to be required, "Reassign tickets that land in the wrong queue."
>
> **L2. Softened prohibition (bullet 9).** "Avoid promising a fix date in the first reply" is functionally binding, but "avoid" is weaker than the "Never" used in bullet 14 for the other prohibition. For consistency: "Do not promise a fix date in the first reply."
>
> **L3. The hardest rule is last.** Bullet 14 (never share another customer's ticket contents) is the only rule with a confidentiality consequence and sits at the bottom of 13 softer items. Move it to the top of the list, or to a short "Always / Never" block ahead of the workflow rules, so it is not lost after truncation or skimming.
>
> **L4. Bullet 3 is outcome-untestable as "try to".** Covered in the H1 rewrite, but noting separately: the observable compliance signal is *ordering* (reproduction attempt precedes the request for detail), not effort. If the author wants an observable record, add "and note the result in the ticket" — but that is a new obligation, not a rewrite, so it is flagged rather than applied.
>
> ## What is already correct
>
> - `## Context` contains only background (why triage was formalized) and no buried directive. Nothing needs to move out of it.
> - The frontmatter description is a trigger condition, not a rule dump.
> - Rules 1 and 14 are model constraints: imperative, single obligation, testable threshold (one business day; zero disclosure).
> - No compound bullets bundle unrelated obligations; each bullet is one rule.
> - The Context sentence implicitly motivates Rule 1 (three-day median → one-day acknowledgment). That link is fine left implicit; adding "(see Context)" to Rule 1 is optional.
>
> ## Recommended edit order
>
> 1. Apply H1 rewrites, resolving the five **author decision** items (bullets 2, 4, 6, 8, 12) — bullet 4 (data loss) first.
> 2. Decide H2: single binding list vs. Rules/Defaults split.
> 3. Apply L1–L3 in the same pass; they are one-line edits.

### Baseline, rep 2

> # Audit: `support-triage` — separation of context from constraints
>
> Scope note: per your instruction I used only the document in the prompt. No files read, no tools called, no skill loaded. Severity is two-level: **High** = an agent reading in good faith could reasonably conclude the rule does not bind, or could not verify compliance; **Low** = binding status is recoverable but the phrasing is weaker than the heading implies.
>
> ## Structural verdict
>
> The document's skeleton is correct. Rules and context live in separately labeled sections, the Rules section is a flat list with no explanatory padding, and the Context section contains no directive (it motivates rule 1 without restating it). Nothing needs to move between sections.
>
> The defect is uniform rather than structural: **12 of 14 items under a heading called "Rules" carry a hedge, preference marker, or permission phrasing.** Only two items (1 and 14) are unambiguously binding. An agent has no way to tell whether "Generally", "Usually", "Consider", "Ideally", "Feel free to" etc. mean "this binds, with exceptions I haven't listed" or "this is advice you may ignore". The context section does not resolve any of these, since it names no exception conditions.
>
> The author has to make one decision per hedged item: either (a) it binds — drop the hedge, and if there is a real exception, name it; or (b) it does not bind — move it to a separate "Guidance" or "Defaults" section so the "Rules" heading stays trustworthy. The rewrites below give the binding form (a); where the hedge plausibly encodes a real exception I say so.
>
> ## Findings
>
> **Rule 2 — High.** "Generally assign severity before assigning an owner."
> Hedge: "Generally". Rewrite: "Assign severity before assigning an owner." If there is a case where an owner is assigned first, state it as an explicit exception; "generally" leaves the agent to guess it.
>
> **Rule 3 — High.** "Try to reproduce the reported behavior before asking the reporter for more detail."
> Hedge: "Try to" — and "trying" is not checkable. The obligation here is the attempt, not success, so a semantic-preserving form is: "Before asking the reporter for more detail, attempt to reproduce the reported behavior." That makes the attempt mandatory and the outcome free.
>
> **Rule 4 — High.** "Usually escalate to on-call when a ticket mentions data loss."
> Hedge on the highest-stakes rule in the document. "Usually" invites the agent to decide a data-loss report is the unusual case. Rewrite: "Escalate to on-call when a ticket mentions data loss." If some data-loss mentions genuinely should not escalate (e.g. already-known incident), name that condition explicitly.
>
> **Rule 5 — High.** "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Preference language. The implicit condition is that a matching issue exists. Rewrite: "Link the ticket to an existing issue when one matches. Open a new issue only when none does."
>
> **Rule 6 — High.** "Consider closing tickets with no reporter response after fourteen days."
> "Consider" is not a rule; it asks the agent to think about it. Rewrite: "Close tickets that have had no reporter response for fourteen days." If closure is discretionary, this belongs in a Guidance section, not under Rules.
>
> **Rule 7 — High.** "Where possible, tag the affected component."
> "Where possible" is an untestable escape hatch. Rewrite: "Tag the affected component. If it cannot be identified, say so in the triage note." (The second sentence is a suggested fallback so the exception path is observable; drop it if the author prefers "when it can be identified" alone.)
>
> **Rule 8 — High.** "Tickets from enterprise accounts should normally be triaged first."
> Hedge: "normally". Rewrite: "Triage tickets from enterprise accounts before other tickets." Name the exception if one exists (e.g. rule 4 escalations outrank this).
>
> **Rule 9 — Low.** "Avoid promising a fix date in the first reply."
> "Avoid" is a soft prohibition; the intent is almost certainly a hard one. Rewrite: "Do not promise a fix date in the first reply."
>
> **Rule 10 — High.** "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Descriptive voice plus "Ideally" — reads as an observation about good tickets, not an instruction. Rewrite: "Record reproduction steps in the ticket itself, not in a linked document."
>
> **Rule 11 — High.** "Feel free to reassign a ticket if it lands in the wrong queue."
> Permission phrasing under a Rules heading. Two possible intents, and the agent cannot tell which: an obligation ("Reassign any ticket that lands in the wrong queue.") or a grant of authority ("You may reassign a ticket that lands in the wrong queue without asking."). Either is fine; pick one. Note the second form is still a binding statement, just of permission rather than obligation.
>
> **Rule 12 — Low.** "Aim to keep the triage note under a paragraph."
> Hedge: "Aim to". The limit itself is checkable. Rewrite: "Keep the triage note to one paragraph or less."
>
> **Rule 13 — High.** "Duplicate tickets are typically closed in favor of the older one."
> Descriptive voice ("are ... closed") plus "typically" — states a practice, not a directive. Rewrite: "Close duplicate tickets in favor of the older one."
>
> **Rules 1 and 14 — no finding.** "Acknowledge every ticket within one business day." and "Never share another customer's ticket contents with a reporter." are imperative, unhedged, and checkable. They are the model the rest of the list should match.
>
> **Context section — no finding.** Correctly placed, purely explanatory, no smuggled directive. One observation: it explains only rule 1. If the hedges in rules 2–13 encode real exceptions the team knows about, this section (or inline exception clauses) is where that knowledge should go; right now it exists nowhere in the document.
>
> ## Summary
>
> - Structure: sound. No content needs to change sections.
> - 10 High findings, 2 Low findings, 2 rules clean.
> - Single root cause: pervasive hedging makes the "Rules" heading unreliable. Fix by deciding, per item, bind-or-guidance, and either dropping the hedge (naming the exception if real) or relocating the item to a non-binding section.
> - Rule 4 (data loss) is the one to fix first regardless of what happens with the rest.
>
> Out of scope and not assessed: whether these rules conflict with any parent instruction layer, internal consistency between rules 5 and 13, and general prose quality.

### Baseline, rep 3

> # Audit: `support-triage` — separation of context from constraints
>
> Scope note: per your instruction I did not load the `separating-context-from-constraints` skill or any file; this audit uses the skill's stated method (two-level severity, semantic-preserving rewrites) as I understand it. Severity labels below are **Major** (an agent could reasonably treat the rule as optional, or cannot test compliance) and **Minor** (wording weakens or blurs a rule that is otherwise clear).
>
> ## Summary
>
> The document's structure is right: rules are in a list, one per bullet, under a `## Rules` heading, and the `## Context` section is a single sentence of rationale with no rules hidden in it. The problem is inside the Rules list. Of the 14 bullets, only 3 (acknowledge within one business day; avoid promising a fix date; never share another customer's contents) read as binding. The other 11 carry hedges — *generally, try to, usually, it is preferable, consider, where possible, normally, ideally, feel free, aim to, typically* — so the heading says "rules" while the wording says "suggestions." An agent has no way to tell which bullets it must satisfy and which it may skip, and the hard rules are camouflaged among the soft ones.
>
> ## Findings
>
> ### F1 (Major) — Heading/wording mismatch across the Rules list
> The `## Rules` heading asserts every bullet binds; 11 of 14 bullets are hedged. This is the root finding; F3–F13 are its instances.
>
> **Fix (choose one, author decides per bullet):**
> - Promote: drop the hedge where the rule is meant to bind.
> - Demote explicitly: move genuine defaults to a `## Defaults` section, each stated as "Default: X. Deviate when Y." — keeping the hedge's meaning but naming the exception so it is testable.
>
> Do not simply delete hedges wholesale; several encode real conditions (see F6, F8) that should become explicit conditions rather than vanish.
>
> ### F2 (Major) — Data-loss escalation is hedged
> > Usually escalate to on-call when a ticket mentions data loss.
>
> "Usually" lets the agent decide not to escalate a data-loss ticket. If there is an exception, it needs to be named; if not, the hedge is a hazard.
> **Rewrite:** "Escalate to on-call when a ticket mentions data loss." (If an exception exists: "...unless [condition].")
>
> ### F3 (Major) — "Consider" is untestable
> > Consider closing tickets with no reporter response after fourteen days.
>
> Compliance with "consider" cannot be checked. The threshold (fourteen days) is precise, but the action is not.
> **Rewrite (binding):** "Close tickets with no reporter response after fourteen days."
> **Rewrite (permission, if discretion is intended):** "A ticket with no reporter response for fourteen days may be closed."
>
> ### F4 (Major) — Rules phrased as descriptions of practice, not instructions
> > Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document.
> > Duplicate tickets are typically closed in favor of the older one.
>
> Both are passive, actor-less statements of what tends to happen. An agent can read them as background, not as something it must do.
> **Rewrites:**
> - "Record reproduction steps in the ticket itself, not in a linked document."
> - "Close duplicate tickets in favor of the older one."
>
> ### F5 (Major) — "Feel free" is a permission dressed as a rule
> > Feel free to reassign a ticket if it lands in the wrong queue.
>
> Unclear whether reassignment is required or merely allowed.
> **Rewrite (obligation):** "Reassign tickets that land in the wrong queue."
> **Rewrite (permission):** "You may reassign a ticket that lands in the wrong queue without seeking approval."
>
> ### F6 (Minor) — "Where possible" hides a real condition
> > Where possible, tag the affected component.
>
> The implied condition is "when the component can be identified." Make it explicit.
> **Rewrite:** "Tag the affected component when it can be identified."
>
> ### F7 (Minor) — "Try to" on reproduction
> > Try to reproduce the reported behavior before asking the reporter for more detail.
>
> The intent is an ordering constraint on an attempt, which is testable if phrased as such.
> **Rewrite:** "Attempt to reproduce the reported behavior before asking the reporter for more detail."
>
> ### F8 (Minor) — "It is preferable" hides a condition
> > It is preferable to link the ticket to an existing issue rather than opening a new one.
>
> The preference only applies when a matching issue exists.
> **Rewrite:** "If an existing issue matches, link the ticket to it instead of opening a new one."
>
> ### F9 (Minor) — "Generally" on severity-before-owner
> > Generally assign severity before assigning an owner.
>
> **Rewrite:** "Assign severity before assigning an owner." (or demote per F1 with a named exception).
>
> ### F10 (Minor) — "Should normally" on enterprise priority
> > Tickets from enterprise accounts should normally be triaged first.
>
> **Rewrite:** "Triage tickets from enterprise accounts before other tickets." (or demote per F1 with a named exception).
>
> ### F11 (Minor) — "Aim to" plus an ambiguous measure
> > Aim to keep the triage note under a paragraph.
>
> "Aim to" is soft, and "under a paragraph" literally means less than one paragraph, which is presumably not intended.
> **Rewrite:** "Keep the triage note to one paragraph or less."
>
> ### F12 (Minor) — "Avoid" is nearly binding but softer than the others
> > Avoid promising a fix date in the first reply.
>
> **Rewrite:** "Do not promise a fix date in the first reply."
>
> ## What is fine as-is
>
> - "Acknowledge every ticket within one business day." — imperative, measurable.
> - "Never share another customer's ticket contents with a reporter." — imperative, absolute, testable.
> - `## Context` — a single rationale sentence, correctly separated, contains no directive. It explains rule 1 without restating it, which is the right placement.
> - One obligation per bullet; no compound rules found. (The duplicate rule bundles "close" and "keep the older," but that is one decision, not two.)
> - Frontmatter description is out of scope for this audit.
>
> ## Recommended shape
>
> ```markdown
> ## Rules
> - Acknowledge every ticket within one business day.
> - Escalate to on-call when a ticket mentions data loss.
> - Attempt to reproduce the reported behavior before asking the reporter for more detail.
> - Record reproduction steps in the ticket itself, not in a linked document.
> - Do not promise a fix date in the first reply.
> - Never share another customer's ticket contents with a reporter.
> - [others the author confirms are binding]
>
> ## Defaults
> Each default states when to deviate.
> - Assign severity before assigning an owner. Deviate when: [condition].
> - Triage enterprise-account tickets first. Deviate when: [condition].
> - ...
> ```
>
> The bracketed conditions are the author's to fill; the audit cannot infer them, and inventing them would not be semantic-preserving.
