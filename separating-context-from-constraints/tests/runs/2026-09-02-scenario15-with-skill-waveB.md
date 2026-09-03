# Scenario 15 — support-triage, With-Skill, three reps (Wave B rerun, W11, W10, W17 E9a; D15.6 planted)

```
Date: 2026-09-02
Run: with-skill
SKILL.md blob: 2cb876f4010f55a3259fe740a46d1e8aaea78eea
Commit: a9f0116 (branch `separating-context-wave3`, Wave B wording; not on `main`)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md: read that file and any file it references under /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/references/. Do not read any other file anywhere, do not read anything under any tests/ directory, do not load any skill through the harness, and do not edit any file. Reply with your report only." followed by the scenario-15 prompt from `../scenarios.md`, verbatim
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under the preregistration's Rerun classification; per-defect tables transcribed and reconciled by a Claude subagent (opus) against the archived outputs; tool calls extracted by script
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); no dispatch for this scenario failed, so every rep is a first dispatch
```

## Scoring

Each cell gives the rule id, the severity, and whether the finding presents both a promoted and a demoted rewrite marked as an author decision, with the finding number in parentheses.
The table runs to D15.12 rather than stopping at D15.10, because two of the nine scored R2 defects — D15.11 and D15.12 — sit beyond it in document order.

| Statement | Rep 1 | Rep 2 | Rep 3 |
| --- | --- | --- | --- |
| D15.1 "Generally assign severity…" | R2 / material / yes (F1) | R2 / material / yes (F1) | R2 / material / yes (F1) |
| D15.2 "Try to reproduce…" | R2 (+R3) / material / yes (F2) | R2 / material / yes (F2) | R2 / material / yes (F2) |
| D15.3 "Usually escalate to on-call…" | R2 / material / yes (F3) | R2 / material / yes (F3) | R2 / material / yes (F3) |
| D15.4 "It is preferable to link…" | R2 / material / yes, plus a default (F4) | R2 (+R1) / material / yes, plus a default (F4) | R2 / material / yes, plus a default (F4) |
| D15.5 "Consider closing tickets…" | R2 / material / yes (F5) | R2 (+R3) / material / yes (F5) | R2 / material / yes, plus a permissive reading (F5) |
| D15.6 "Where possible, tag…" (planted on rerun) | R3 / minor / author decision, two labelled alternatives (F6) | missed — passed in the guard list as an ordinary domain predicate | R3 (+R2) / material / author decision, three labelled alternatives including a demotion (F6) |
| D15.7 "should normally be triaged first" | R2 (+R3) / material / yes, plus a default (F7) | R2 / material / yes, plus a default (F6) | R2 / material / yes, plus a default (F7) |
| D15.8 "Avoid promising a fix date…" — adjudication (excluded) | R2 / minor / yes (F8) | R2 / minor / yes (F7) | R2 / minor / yes (F8) |
| D15.9 "Ideally the reproduction steps…" | R2 / minor / yes, plus a default (F9) | R2 (+R1) / minor / yes, plus a default (F8) | R2 / minor / yes (F9) |
| D15.10 "Feel free to reassign…" — protected → E2 | R2 (+R1) / minor / yes (F10) | R2 (+R1) / material / yes (F9) | R2 (+R1) / material / yes (F10) |
| D15.11 "Aim to keep the triage note…" | R2 / minor / yes (F11) | R2 / minor / yes (F10) | R2 / minor / yes (F11) |
| D15.12 "Duplicate tickets are typically closed…" | R2 / material / yes (F12) | R2 (+R1) / material / yes, plus a default (F11) | R2 / material / yes, plus a default (F12) |
| **E1 over the nine R2 defects plus D15.6** | **10/10** | **9/10** | **10/10** |

| Rep | E2 | E3 over the nine | E9a |
| --- | --- | --- | --- |
| 1 | 1 (D15.10) | `preserved` 9/9, no silent selection | `absent` (E9b `unrequested`) |
| 2 | 1 (D15.10) | `preserved` 9/9, no silent selection | `absent` (E9b `unrequested`) |
| 3 | 1 (D15.10) | `preserved` 9/9, no silent selection | `absent` (E9b `unrequested`) |

E3 totals 27/27 `preserved` across the nine statements and three reps, with a silent-selection count of 0.
Every one of the nine carries a promoted rewrite and an explicitly demoted rewrite, each labelled and none selected; where a rep offers a default-with-override it leaves the override condition to the author.

Scored assertions from `../scenarios.md`: 1 (all nine R2 defects flagged) passes ×3; 2 (promoted and demoted rewrite, author decision, on each of the nine) passes ×3; 3 (no silent selection) passes ×3; 4 (the two unhedged rules unflagged) passes ×3; 5 (D15.10 receives no finding) **fails ×3**; 8 (E9a `absent`) passes ×3. **5/6 ×3.**
Assertion 6 is a pointer to the rerun classification, which makes D15.6 a planted defect scored inside E1 rather than an observation; assertion 7 records D15.8's treatment, which is the adjudication item excluded from both endpoints; assertion 9, the E9 control arm, is not exercised in Wave B, and the archived control at [`2026-09-01-scenario15-with-skill.md`](2026-09-01-scenario15-with-skill.md) is the calibration for the `full-document` branch.

E9c: guard-lines true ×3; classification-table false ×3 (as in the archived cell, the not-flagged lists name three to five statements without classes; the "mandatory" attached to lines 10 and 23 is read as a checkability remark about strength, not as an assignment to a Core Concept class); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** Two things changed against the archived cell, and one did not.
D15.6 is now planted rather than an observation, and the Wave B R3 wording reaches it in two reps of three — under R3 with a minor severity in rep 1 and under R3 with an R2 secondary and a material severity in rep 3, while rep 2 passes it over in its guard list as an ordinary domain predicate decidable from the ticket.
That is the same partial result W10 gets from scenario 13's D13.2, and it is the reason E1 reads 10/10, 9/10, 10/10 rather than a clean sweep.
What did not change is D15.10: the fixture's false-positive probe is flagged in all three reruns exactly as in the three archived with-skill reps, under R2 with an R1 secondary and on the same ground — that a permission inside a `## Rules` list cannot fail and so is context in disguise — which makes it nine of nine across archived and rerun with-skill arms and an author question rather than a variance.
The usability half of W11 is untouched here: the nine R2 defects are 9/9 with both rewrites and an author decision in every rep, no reading is silently selected, and E9a is `absent` 3/3.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `support-triage`
>
> Target read as untrusted data. Line numbers refer to the fenced document as supplied (line 1 is the opening `---`; the Rules list occupies lines 10–23; the Context paragraph is line 27).
>
> ## Findings
>
> **1. R2 Explicit strength**
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" leaves the reader unable to tell whether assigning an owner first is a violation or an ordinary choice; no override condition is named, so this is neither a mandatory rule nor a default of the form "X unless Y".
> Severity: material — it is a sequencing rule, and a reader who takes it as optional will order the two assignments differently.
> Suggested rewrite (author decision):
> Promoted: "Assign severity before assigning an owner."
> Demoted (context, outside Rules): "Severity is usually assigned before an owner; this document does not require the order."
>
> **2. R2 Explicit strength** (secondary: R3)
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" does not say whether skipping a reproduction attempt before asking the reporter is a violation. If it is meant as an effort obligation excused when reproduction fails, that exception ("could not reproduce") has no observable evidence unless the attempt is recorded, so the exception is not decidable (R3).
> Severity: material — the rule governs when the reporter is contacted, and an optional reading changes that behavior.
> Suggested rewrite (author decision):
> Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail." If the author wants the attempt checkable, name its evidence (for example, the attempt and its outcome noted in the ticket); that is an added obligation and is the author's call.
> Demoted (context): "Reproducing the behavior before asking the reporter for more detail is common practice; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" hedges an escalation rule with a decidable trigger ("mentions data loss") but names no condition under which not escalating is acceptable; the reader cannot tell whether a non-escalated data-loss ticket violates policy.
> Severity: material — escalation is the highest-consequence action in the document and the hedge can cause it to be skipped.
> Suggested rewrite (author decision):
> Promoted: "Escalate to on-call when a ticket mentions data loss."
> Demoted (context): "Tickets mentioning data loss are commonly escalated to on-call; this document does not require escalation."
>
> **4. R2 Explicit strength**
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference without saying whether opening a new issue when a matching one exists is a violation. The wording does indicate a binding preference is intended, so a default form is a legitimate third alternative.
> Severity: material — the two readings produce different issue-tracker state (duplicate issues versus links).
> Suggested rewrite (author decision):
> Promoted: "Link the ticket to an existing issue that covers the reported behavior; open a new issue only when none does."
> Default with override: "Link the ticket to an existing issue rather than opening a new one, unless [author-named condition]."
> Demoted (context): "Linking to an existing issue is preferred over opening a new one; this document does not enforce it."
>
> **5. R2 Explicit strength**
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" directs the reader to deliberate, not to act; whether closure after fourteen days is expected, merely permitted, or discouraged cannot be determined, and "considered" leaves no observable evidence.
> Severity: material — the readings differ on whether stale tickets are closed at all.
> Suggested rewrite (author decision):
> Promoted: "Close tickets that have had no reporter response for fourteen days." (The anchor for the fourteen days — ticket creation or the last request to the reporter — is unstated; the author should name it.)
> Demoted (context): "Tickets with no reporter response for fourteen days may be closed; this document does not require closure."
>
> **6. R3 Verifiability**
> Location: line 16.
> Quoted text: "Where possible, tag the affected component."
> Why it fails: the obligation and its evidence (a component tag on the ticket) are clear, but the exception "where possible" has no observable evidence — nothing in the document lets a reader decide when tagging was not possible, so any omission can claim the exception.
> Severity: minor — intended behavior remains clear and checkable in the ordinary case; only the escape condition is undecidable.
> Suggested rewrite (author decision):
> Mandatory: "Tag the affected component."
> Default with decidable exception: "Tag the affected component unless [author-named observable condition, e.g. no existing component tag matches]."
>
> **7. R2 Explicit strength** (secondary: R3)
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" signals a default priority but names no condition for deviating, so the reader cannot tell whether triaging a non-enterprise ticket first is a violation; the implied exception is not decidable (R3). The wording indicates a binding preference is intended.
> Severity: material — it determines triage order across the queue.
> Suggested rewrite (author decision):
> Promoted: "Triage tickets from enterprise accounts before other tickets."
> Default with override: "Triage tickets from enterprise accounts first, unless [author-named condition]."
> Demoted (context): "Enterprise tickets are usually triaged first; this document does not require the order."
>
> **8. R2 Explicit strength**
> Location: line 18.
> Quoted text: "Avoid promising a fix date in the first reply."
> Why it fails: "Avoid" reads as a prohibition but is weaker than "never" and does not say whether a promised date is a violation or a discouraged choice.
> Severity: minor — the intended behavior (no fix date in the first reply) is clear and checkable against the reply text.
> Suggested rewrite (author decision):
> Promoted: "Do not promise a fix date in the first reply."
> Demoted (context): "First replies usually do not promise a fix date; this document does not prohibit it."
>
> **9. R2 Explicit strength**
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus a descriptive passive states an aspiration, not a rule; the reader cannot tell whether a linked document is a violation. The wording indicates a preference is intended.
> Severity: minor — the intended behavior (steps in the ticket) is clear and checkable.
> Suggested rewrite (author decision):
> Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> Default with override: "Record reproduction steps in the ticket itself unless [author-named condition]."
> Demoted (context): "Reproduction steps are preferably kept in the ticket rather than a linked document; this document does not require it."
>
> **10. R2 Explicit strength** (secondary: R1)
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: the trigger is decidable, but "Feel free to" is a permission, and the reader cannot tell whether leaving a misrouted ticket in place is a violation. Read purely as a permission, the statement cannot fail — nothing else in the document forbids reassignment — so it is context in disguise inside the Rules section (R1).
> Severity: minor — reassignment is acceptable under either reading.
> Suggested rewrite (author decision):
> Promoted: "Reassign a ticket that lands in the wrong queue."
> Demoted (context): "Triagers may reassign a ticket that lands in the wrong queue; this document does not require it."
>
> **11. R2 Explicit strength**
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" hedges a bounded requirement; the reader cannot tell whether a two-paragraph note is a violation.
> Severity: minor — the bound ("under a paragraph") makes intended behavior clear and roughly checkable.
> Suggested rewrite (author decision):
> Promoted: "Keep the triage note under one paragraph."
> Demoted (context): "Triage notes are usually kept under a paragraph; this document sets no limit."
>
> **12. R2 Explicit strength**
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: this is a description of practice ("are typically closed") placed in the Rules list; the reader cannot tell whether closing the older ticket instead, or leaving both open, is a violation.
> Severity: material — the readings produce different ticket states for every duplicate.
> Suggested rewrite (author decision):
> Promoted: "Close duplicate tickets in favor of the older one."
> Demoted (context): "Duplicate tickets are typically closed in favor of the older one; this document does not require it."
>
> **Not flagged (false-positive guards)**
> - Line 10, "Acknowledge every ticket within one business day": mandatory, decidable trigger, checkable against reply timestamps.
> - Line 23, "Never share another customer's ticket contents with a reporter": mandatory, checkable against reply content.
> - Line 27, the first-response-time history: discretionary context, correctly placed in `## Context`.
> - R4: no item bundles independently checkable obligations; line 12 is a single condition–action unit.
> - R5: no reachable conflict. Line 17 (enterprise first) and line 10 (one-business-day acknowledgement) govern different decisions — order versus latency — and prescribing both is compatible; line 22 (close duplicate ticket) and line 14 (link to existing issue) act on different objects.
>
> ## Summary
>
> Counts per rule: R1 1, R2 11, R3 3, R4 0, R5 0 (per-rule total 15, secondary ids included).
> Counts per severity: material 7 (findings 1, 2, 3, 4, 5, 7, 12), minor 5 (findings 6, 8, 9, 10, 11); 12 findings total.
>
> The document is structurally sound — rules are a list in a labeled section, context is separated into its own section, and nothing is buried in prose — but twelve of its fourteen rule items are hedged ("generally", "try to", "usually", "preferable", "consider", "where possible", "should normally", "avoid", "ideally", "feel free", "aim to", "typically"), so only the acknowledgement deadline and the confidentiality prohibition state their strength. Every hedged item is an author decision between a binding rule and explicitly nonbinding context; three of them (lines 14, 17, 19) indicate a preference and so also admit a default-with-override form, provided the author names the override condition. No R4 or R5 findings.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions.

### With-skill, rep 2

> # Audit: `support-triage`
>
> Method: read `SKILL.md` and its one referenced file, `references/example-audit.md`; classified each statement with the two-question litmus test; ran R1–R5. Line numbers refer to the fenced target, with line 1 = the opening `---`. The document is long-form (labeled `## Rules` and `## Context` sections), so demoted rewrites move to `## Context`.
>
> ## Findings
>
> Every finding below is primarily R2. The `## Rules` section is structurally sound — fourteen list items, two of them cleanly mandatory — but eleven of the fourteen carry a hedge that leaves the reader unable to tell whether the item binds. One finding per statement.
>
> **1. R2 Explicit strength**
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" hedges the ordering obligation; no override condition is named, so a reader cannot tell whether assigning the owner first violates the rule.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Assign severity before assigning an owner."
> - Demoted (to `## Context`): "Severity is commonly assigned before an owner; this document does not require that order."
>
> **2. R2 Explicit strength**
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" is an ambiguous hedge; it is unclear whether an attempt at reproduction is required before contacting the reporter or merely encouraged.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail." (The attempt is checkable when recorded in the ticket.)
> - Demoted (to `## Context`): "Triagers often attempt reproduction before asking the reporter for more detail; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" hedges an escalation rule with a clearly decidable trigger (the ticket mentions data loss) and no named exception; a reader cannot tell whether not escalating is a violation.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Escalate to on-call when a ticket mentions data loss."
> - Demoted (to `## Context`): "Tickets mentioning data loss are commonly escalated to on-call; this document does not require it."
>
> **4. R2 Explicit strength** (secondary: R1)
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference without saying whether it binds; the grammar is evaluative rather than directive, so as written the statement prescribes nothing and cannot fail (R1: context in disguise). The target does indicate a preference, so a default form is a legitimate third alternative.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Link the ticket to an existing issue when one matches; open a new issue only when none matches."
> - Default: "Prefer linking the ticket to an existing issue over opening a new one, unless <author-named condition>."
> - Demoted (to `## Context`): "Linking to an existing issue is generally preferred over opening a new one; this document does not require it."
>
> **5. R2 Explicit strength** (secondary: R3)
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" hedges strength; read literally, the only obligation is to consider, which leaves no observable evidence (R3). The trigger itself — fourteen days with no reporter response — is decidable.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Close tickets with no reporter response after fourteen days."
> - Demoted (to `## Context`): "Tickets with no reporter response after fourteen days are candidates for closure; this document does not require closing them."
>
> **6. R2 Explicit strength**
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" signals that exceptions exist but names none, so a reader cannot tell when triaging a non-enterprise ticket first is a violation. "normally" indicates a default is intended, so a default form is a legitimate alternative if the author names the exception.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Triage tickets from enterprise accounts before other tickets."
> - Default: "Triage tickets from enterprise accounts before other tickets, unless <author-named condition>."
> - Demoted (to `## Context`): "Enterprise-account tickets are typically triaged first; this document does not require that order."
>
> **7. R2 Explicit strength**
> Location: line 18.
> Quoted text: "Avoid promising a fix date in the first reply."
> Why it fails: "Avoid" is a softened prohibition; most readers take it as "do not", but it does not state whether an exception exists.
> Severity: minor — the intended behavior (no fix date in the first reply) is clear and checkable against the reply text.
> Suggested rewrite (author decision):
> - Promoted: "Do not promise a fix date in the first reply."
> - Demoted (to `## Context`): "First replies generally do not promise a fix date; this document does not prohibit it."
>
> **8. R2 Explicit strength** (secondary: R1)
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus passive, evaluative grammar states an aspiration, not a directive; as written it cannot fail (R1). The target indicates a preference, so a default form is a legitimate alternative.
> Severity: minor — the preferred location is clear and checkable; the ambiguity concerns only the form of the triager's own record.
> Suggested rewrite (author decision):
> - Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> - Default: "Record reproduction steps in the ticket itself rather than a linked document, unless <author-named condition>."
> - Demoted (to `## Context`): "Reproduction steps are best kept in the ticket itself rather than a linked document; this document does not require it."
>
> **9. R2 Explicit strength** (secondary: R1)
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: "Feel free to" grants permission rather than imposing an obligation; a permission cannot fail, so as written the item is context in a rule section (R1). It is unclear whether a triager who leaves a misrouted ticket in place has violated anything.
> Severity: material — the demoted and promoted readings produce different ticket states.
> Suggested rewrite (author decision):
> - Promoted: "Reassign a ticket that lands in the wrong queue to the correct queue."
> - Demoted (to `## Context`): "Triagers may reassign a ticket that lands in the wrong queue; this document does not require it."
>
> **10. R2 Explicit strength**
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" hedges strength; the bound (under a paragraph) is stated, but whether exceeding it is a violation is not.
> Severity: minor — the intended length is clear and checkable.
> Suggested rewrite (author decision):
> - Promoted: "Keep the triage note under one paragraph."
> - Demoted (to `## Context`): "Triage notes are typically under a paragraph; this document sets no limit."
>
> **11. R2 Explicit strength** (secondary: R1)
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: "typically" plus descriptive passive grammar reports what usually happens rather than directing anything; as written it cannot fail (R1), and a reader cannot tell whether closing the older ticket instead is a violation. The target indicates a default (older wins), so a default form is a legitimate alternative.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Close duplicate tickets in favor of the older one."
> - Default: "Close duplicate tickets in favor of the older one, unless <author-named condition>."
> - Demoted (to `## Context`): "Duplicate tickets are usually closed in favor of the older one; this document does not require it."
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Acknowledge every ticket within one business day." — imperative, mandatory, decidable trigger, checkable against timestamps. Clean.
> - Line 16, "Where possible, tag the affected component." — a default with an override condition ("where possible"); whether a component can be identified is an ordinary domain predicate decidable from the ticket, so it passes R2 and R3. This is the closest call in the document; an author who wants it stricter can name the condition, but that is not a finding.
> - Line 23, "Never share another customer's ticket contents with a reporter." — mandatory, checkable against output. Clean.
> - Line 27, the first-response-time history — discretionary context, correctly placed in `## Context`, and it is the rationale for line 10 rather than a buried rule.
> - R4: no item bundles independently checkable obligations; lines 11 and 12 each carry a single ordering obligation.
> - R5: lines 13 and 17 (data-loss escalation vs. enterprise-first ordering) are not a conflict — a non-enterprise data-loss ticket can be both triaged after enterprise tickets and escalated when reached, so both are satisfiable. Lines 14 and 22 concern different objects (issue links vs. duplicate tickets). No reachable conflicts.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 4 (all secondary), R2 11, R3 1 (secondary), R4 0, R5 0. Per-rule total 16.
> Counts per severity: material 8 (lines 11, 12, 13, 14, 15, 17, 20, 22), minor 3 (lines 18, 19, 21). Finding total 11.
> Safety notes: 0.
>
> The document's structure is right — a labeled `## Rules` list and a separate `## Context` section, with no rules buried in prose and no context misfiled into the rule list — but its rule list is almost entirely hedged: eleven of fourteen items use "generally", "try to", "usually", "preferable", "consider", "normally", "avoid", "ideally", "feel free", "aim to", or "typically", none with a named override condition, so a reader cannot tell which items bind. Severity was split by consequence: material where the promoted and demoted readings yield different ticket states or customer interactions (ordering, escalation, closure, priority, linking, reassignment, duplicates); minor where the hedge attaches to the form of the triager's own record or is conventionally read as binding ("avoid"). Four items (14, 17, 19, 22) express a genuine preference, and for those a default-with-exception form is offered as a third alternative, but every finding is an author decision — the audit has not selected a strength for any of them.

### With-skill, rep 3

> ## Audit: `support-triage`
>
> Line numbers count from the first `---` of the fenced document (line 1), so `## Rules` is line 8 and the rule items are lines 10–23.
>
> ### Findings
>
> **1. R2 Explicit strength**
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" hedges the ordering; a reader cannot tell whether assigning an owner before severity is a violation or an accepted variation.
> Severity: material — the ordering obligation can be skipped as optional.
> Suggested rewrite (author decision):
> - Promoted: "Assign severity before assigning an owner."
> - Demoted (move to `## Context`): "Severity is commonly assigned before an owner; this document does not require that order."
>
> **2. R2 Explicit strength**
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" leaves unclear whether a reproduction attempt is required before the first request for detail, or merely encouraged.
> Severity: material — the reproduce-first obligation can be missed.
> Suggested rewrite (author decision):
> - Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail, and record the attempt's result in the ticket."
> - Demoted (move to `## Context`): "Triagers often attempt reproduction before asking the reporter for detail; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" hedges an escalation rule with a decidable trigger (the ticket mentions data loss); the reader cannot tell whether not escalating is a violation.
> Severity: material — a data-loss escalation can be omitted, and the omission is the highest-consequence gap in the document.
> Suggested rewrite (author decision):
> - Promoted: "Escalate to on-call when a ticket mentions data loss."
> - Demoted (move to `## Context`): "Data-loss reports are often escalated to on-call; this document does not require escalation."
>
> **4. R2 Explicit strength**
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference without saying whether opening a new issue when a matching one exists is a violation, and without an override condition that would make it a default.
> Severity: material — the choice between linking and opening can go either way with no checkable policy.
> Suggested rewrite (author decision; the target indicates a binding preference is intended, so a default is offered as a separate alternative):
> - Promoted: "Link the ticket to an existing issue when one matches; do not open a new issue for a ticket that matches an existing one."
> - Default with override: "Link the ticket to an existing issue when one matches, unless <author-named condition, e.g., the existing issue is closed>."
> - Demoted (move to `## Context`): "Linking to an existing issue is preferred over opening a new one; this document does not require it."
>
> **5. R2 Explicit strength**
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" directs the reader to think about closure, which cannot fail; whether closure at fourteen days is required, permitted, or merely suggested is undetermined. (R3 passes: the fourteen-day trigger is a quantity.)
> Severity: material — whether stale tickets are closed at all depends on the reading.
> Suggested rewrite (author decision):
> - Promoted: "Close tickets with no reporter response after fourteen days."
> - Permissive: "Tickets with no reporter response for fourteen days may be closed." (labeled as a plausible intended reading of "Consider", not selected)
> - Demoted (move to `## Context`): "Tickets with no reporter response for fourteen days are candidates for closure; this document does not require closing them."
>
> **6. R3 Verifiability** (secondary: R2)
> Location: line 16.
> Quoted text: "Where possible, tag the affected component."
> Why it fails: the imperative binds, but its exception "where possible" names no observable evidence — nothing in the document lets a reader or checker decide when tagging was not possible, so the rule is satisfied by any untagged ticket the triager declares impossible. In effect the exception is a hedge (R2).
> Severity: material — the exception prevents verification.
> Suggested rewrite (author decision; the statement does not reveal what makes tagging impossible):
> - If the exception means no component is identifiable from the report: "Tag the affected component; if no component can be identified from the report, tag `component:unknown`" (or whichever recorded marker the author uses).
> - If no exception is intended: "Tag the affected component on every ticket."
> - Demoted (move to `## Context`): "Tagging the affected component helps routing; this document does not require it."
>
> **7. R2 Explicit strength**
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" signals a default but states no override condition, so the reader cannot tell whether triaging a non-enterprise ticket first ever violates policy or when it is allowed.
> Severity: material — queue ordering changes with the reading.
> Suggested rewrite (author decision; the target indicates a binding priority is intended, so a default is offered separately):
> - Promoted: "Triage tickets from enterprise accounts before tickets from other accounts."
> - Default with override: "Triage tickets from enterprise accounts first, unless <author-named condition>."
> - Demoted (move to `## Context`): "Enterprise-account tickets are usually triaged first; this document does not require that order."
>
> **8. R2 Explicit strength**
> Location: line 18.
> Quoted text: "Avoid promising a fix date in the first reply."
> Why it fails: "Avoid" is softer than the document's own "Never" (line 23), and the contrast leaves unclear whether a fix date in the first reply is a violation or a discouraged practice.
> Severity: minor — the prohibition is inferable and checkable against the first reply; only its strength is blurred.
> Suggested rewrite (author decision):
> - Promoted: "Do not promise a fix date in the first reply."
> - Demoted (move to `## Context`): "Fix dates are usually withheld from the first reply; this document does not prohibit them."
>
> **9. R2 Explicit strength**
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus descriptive voice ("are recorded") reads as an aspiration, not a directive; a reader cannot tell whether a linked document is a violation.
> Severity: minor — the preferred location is clear and checkable; the hedge blurs only whether deviation is a violation.
> Suggested rewrite (author decision):
> - Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> - Demoted (move to `## Context`): "Reproduction steps are easiest to find when recorded in the ticket itself; this document does not require it."
>
> **10. R2 Explicit strength** (secondary: R1)
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: "Feel free to" grants permission; as written the statement cannot be violated, so it is context in disguise inside the rule section (R1), unless the author intended an obligation to reassign, which the wording does not convey (R2). The trigger "wrong queue" is a decidable domain predicate and is not at issue.
> Severity: material — if an obligation was intended, mis-queued tickets can be left in place with no violation.
> Suggested rewrite (author decision):
> - Promoted: "Reassign any ticket that lands in the wrong queue to the correct queue."
> - Demoted (move to `## Context`): "Triagers may reassign a ticket that lands in the wrong queue; this document does not require it."
>
> **11. R2 Explicit strength**
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" leaves unclear whether a longer note violates policy. (R3 passes: "under a paragraph" bounds the judgment.)
> Severity: minor — the intended length is clear and checkable against the note; only its strength is blurred.
> Suggested rewrite (author decision):
> - Promoted: "Keep the triage note under one paragraph."
> - Demoted (move to `## Context`): "Triage notes are usually kept under a paragraph; this document sets no length limit."
>
> **12. R2 Explicit strength**
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: "typically" plus descriptive voice ("are ... closed") reports a practice rather than directing one; the reader cannot tell whether closing the newer duplicate is required, nor whether keeping the newer one is a violation.
> Severity: material — whether duplicates are closed, and which one, depends on the reading.
> Suggested rewrite (author decision; "in favor of the older one" indicates a binding preference, so a default is offered separately):
> - Promoted: "Close duplicate tickets in favor of the older ticket."
> - Default with override: "Close duplicate tickets in favor of the older ticket, unless <author-named condition>."
> - Demoted (move to `## Context`): "Duplicate tickets are usually closed in favor of the older one; this document does not require it."
>
> ### Not flagged (false-positive guards)
>
> - Line 10, "Acknowledge every ticket within one business day." — imperative, mandatory, checkable against reply timestamps. Clean.
> - Line 23, "Never share another customer's ticket contents with a reporter." — mandatory, checkable against output. Clean.
> - Line 27, the first-response-time history — discretionary context, correctly placed under `## Context`.
> - Line 3, the description — a trigger statement, not a rule.
> - R1: every rule is a list item under a labeled `## Rules` section, so all are structurally marked; no rule is embedded in narrative and no load-bearing fact or context sits in the rule section (the two descriptive-voice items, lines 19 and 22, are hedged rules and are handled under R2).
> - R4: no item bundles independently checkable obligations; the ordering rules (lines 11, 12) each state one obligation.
> - R5: considered and rejected — line 13 (escalate on data loss) vs line 17 (enterprise first): escalation and triage order are different decisions and both can be satisfied on the same queue; line 14 (link to existing issue) vs line 22 (close duplicates): a ticket can be both linked and closed, so the outcomes are not incompatible. No reachable conflict.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 1 (secondary, finding 10), R2 12 (11 primary + 1 secondary on finding 6), R3 1, R4 0, R5 0. Per-rule total 14.
> Counts per severity: material 9 (findings 1–7, 10, 12), minor 3 (findings 8, 9, 11). Total 12 findings; the per-rule total exceeds it by the two secondary ids.
>
> The document's structure is sound — all fourteen rules are list items in a labeled rule section, the one context paragraph is correctly placed, no rule is compound, and no pair reaches a real conflict — but twelve of the fourteen rules carry a hedge ("generally", "try to", "usually", "it is preferable", "consider", "where possible", "should normally", "avoid", "ideally", "feel free to", "aim to", "typically") that leaves the reader unable to tell whether the rule binds. Only lines 10 and 23 state their strength. The highest-consequence gap is line 13, where the data-loss escalation is hedged. Every finding is an author decision between a promoted binding rule and a demoted context statement; three (lines 14, 17, 22) also plausibly intend a default, offered as a separate alternative with the override condition left for the author to name, and one (line 16) needs the author to identify what makes tagging impossible before a verifiable exception can be written.
