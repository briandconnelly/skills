# Scenario 15 — support-triage, With-Skill, three reps, the E9 control, and three author-usability arms (wave 3, W11)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: every arm made exactly two tool calls (script): Read SKILL.md, cat example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

```
Date: 2026-09-01
Run: control
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only." with the request line "… and report your findings, and give me the rewritten document:"
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: E9 known positive for scenario 15; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

```
Date: 2026-09-02
Run: author-usability
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "You are the author of the document at `<scratchpad>/s15-usability/support-triage.md`. An audit report on it is at `<scratchpad>/s15-usability/report-repN.md`. Read those two files and nothing else; do not edit any file. Resolve every decision this report asks you to make and produce the revised document. Reply with the revised document in full, preceded by a short list stating, for each decision the report raised, which option you chose. If you cannot resolve a decision from the information you have, say so explicitly instead of guessing."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: one author arm per with-skill report (rep N reads report N); each made exactly two Read calls (script), the target and the report; the first dispatch of all three died with HTTP 429 before producing output and was re-dispatched 2026-09-02 with identical prompts; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring — audit arms

| Rep | E1 (of 9) | D15.6 | D15.8 | D15.10 | E2 | E3 over the nine | Words (× 193) | E9a |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9/9 | flagged, R2 (+R3) | flagged, R2 minor | **flagged, R2 (+R1), material** | 1 | preserved 9/9 (promoted + demoted, author decision, none selected) | 1648 (8.5×) | absent |
| 2 | 9/9 | flagged, R2 (+R3) minor | not flagged (guard list) | **flagged, R2 (+R1), material** | 1 | preserved 9/9 | 1554 (8.1×) | absent |
| 3 | 9/9 | flagged, R2 minor | not flagged (guard list) | **flagged, R2 (+R1), material** | 1 | preserved 9/9 | 1580 (8.2×) | absent |
| control | 9/9 | flagged | flagged, minor | flagged | 1 | preserved 9/9 | 1859 (9.6×) | **full-document**, `requested` |

E9c: guard-lines true ×3; classification-table false ×3 (the not-flagged lists name three or four statements without classes); negative-safety-note true ×3.
Contract adherence: six fields, ids, counts with secondary-id arithmetic, safety note — 4/4.

**D15.10 for the preregistration.** "Feel free to reassign a ticket if it lands in the wrong queue." is the fixture's false-positive probe, protected as an explicit permission. Six of six audit arms today flag it — every with-skill rep under R2 with R1 secondary, on the ground that a permission inside a `## Rules` list either cannot fail (context in disguise) or hides an obligation. Like scenario 2's `MUST NOT` sentence and scenario 10's D10.11, this is a unanimous arm reading against a preregistered protection, recorded as an adjudication question for the author rather than absorbed into E2.

**D15.6** is flagged 3/3 under R2 (with R3 secondary in two reps) — the W10-gap observation, consistent with scenario 13 (undecidable trigger caught under R3) and scenario 2.

Standing assertions: 1 (nine findings) ✓ ×3; 2 (promoted + demoted, author decision) ✓ ×3; 3 (no silent selection) ✓ ×3; 4 (two unhedged rules unflagged) ✓ ×3; 5 (D15.10 no finding) **FAIL ×3**; E9a absent ✓ ×3; control full-document ✓.

## Scoring — usability endpoint (W11)

| Author arm | Reads report | Of the nine: resolved | asked for clarification / explicitly declined | silently dropped | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | rep 1 | 6 | 3 (D15.1, D15.7, D15.12 — strength resolved as binding, the "unless [exception]" left as a bracketed author placeholder) | 0 | also left D15.6's fallback as a placeholder; chose not to demote anything, citing the Context sentence |
| 2 | rep 2 | 9 | 0 | 0 | states its basis (placement in `## Rules` plus the stated purpose) and names the two items the original author may have meant as discretionary |
| 3 | rep 3 | 8 | 1 (D15.7 — "should normally" read as a default whose exception the document does not name; left unchanged) | 0 | — |

Every decision in all three arms was either resolved or explicitly escalated; **no decision was silently dropped in 27**. The escalations are all the same shape: the report's default-with-override alternative asks the author to name an exception, and the author arm, having only the document, declines to invent one.

**W11 verdict.** The premise under test — that an exhaustive author-decision contract makes reports unusable at volume — predicted silent drops. None occurred. Reports run 8.1–8.5× the target's length and one of three author arms resolved all nine; the other two resolved eight and six and escalated the rest with reasons. The preregistered "nothing changes" row asks for all nine resolved; it is met by one arm of three. The premise does not hold in the form it was stated (silent drops), and the residue is a length observation, not a usability failure. Recorded for the author; `SKILL.md:59`, `:84`, `:86` untouched.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `support-triage`
>
> Method: read SKILL.md and `references/example-audit.md`; classified each statement with the two-question litmus test; ran R1–R5. Line numbers count the fenced document from its opening `---` (line 1), so the Rules bullets are lines 10–23 and the Context paragraph is line 27.
>
> Structural picture: the document is long-form (labeled sections) and its structure is sound — a dedicated `## Rules` section, a separate `## Context` section holding only discretionary context. The defect is concentrated in one place: 12 of the 14 bullets in `## Rules` are hedged, so a reader cannot tell which of them bind. Only lines 10 and 23 are unambiguous.
>
> ## Findings
>
> **1. R2 Explicit strength** — line 11
> Quoted: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" leaves unclear whether the ordering is required or merely common practice; an agent may assign an owner first with no way to say whether that was wrong.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Assign severity before assigning an owner."
> - Default (the word "generally" suggests unstated exceptions exist): "Assign severity before assigning an owner unless [author-specified condition]."
> - Demoted (move to `## Context`): "Severity is usually assigned before an owner; this document does not require that order."
>
> **2. R2 Explicit strength** — line 12
> Quoted: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" does not say whether a reproduction attempt is mandatory before contacting the reporter or merely encouraged. Either reading is checkable (a reproduction note in the ticket before the first detail request), but the binding status is not.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Attempt to reproduce the reported behavior, and record the result in the ticket, before asking the reporter for more detail."
> - Demoted (`## Context`): "Reproducing first often avoids unnecessary back-and-forth with reporters; this document does not require it."
>
> **3. R2 Explicit strength** — line 13
> Quoted: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" makes the highest-stakes rule in the document optional-sounding; an agent can read a data-loss ticket and reasonably decide this is one of the "unusual" cases without any stated criterion.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Escalate to on-call when a ticket mentions data loss."
> - Default ("usually" implies exceptions): "Escalate to on-call when a ticket mentions data loss unless [author-specified exception, e.g. the reporter confirms the data was recovered]."
> - Demoted (`## Context`): "Data-loss tickets are commonly escalated to on-call; this document does not require it."
>
> **4. R2 Explicit strength** — line 14
> Quoted: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference but not whether it binds — must the triager link when a matching issue exists, or is opening a new one acceptable? The natural override (no matching issue exists) is left implicit.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Link the ticket to an existing issue when one matches; open a new issue only when no matching issue exists."
> - Demoted (`## Context`): "Linking to an existing issue is the usual practice; this document does not require it."
>
> **5. R2 Explicit strength** — line 15
> Quoted: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" directs the agent to think about closing, which cannot fail; whether the ticket should actually be closed at day fourteen is undetermined. The fourteen-day threshold is verifiable, so the only gap is strength.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Close tickets that have had no reporter response for fourteen days."
> - Demoted (`## Context`): "Tickets with no reporter response for fourteen days are candidates for closure; this document does not require closing them."
>
> **6. R2 Explicit strength** (secondary R3) — line 16
> Quoted: "Where possible, tag the affected component."
> Why it fails: the obligation is clear and checkable (a component tag is present or absent), but the exception "where possible" has no stated boundary, so a missing tag can never be shown to be a violation — the escape clause defeats verification.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Tag the affected component." (If a ticket genuinely has no identifiable component, name the fallback tag, e.g. "tag `component:unknown`.")
> - Default with a stated exception: "Tag the affected component unless [author-specified condition, e.g. the report does not identify any product surface]."
> - Demoted (`## Context`): "Component tags help routing; this document does not require them."
>
> **7. R2 Explicit strength** — line 17
> Quoted: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" signals a default with exceptions but names none, so the agent cannot tell when it is permitted to triage a non-enterprise ticket ahead of an enterprise one.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Triage tickets from enterprise accounts before other tickets."
> - Default: "Triage tickets from enterprise accounts first unless [author-specified condition, e.g. a non-enterprise ticket reports data loss]."
> - Demoted (`## Context`): "Enterprise tickets are generally worked first; this document does not require that order."
>
> **8. R2 Explicit strength** — line 18
> Quoted: "Avoid promising a fix date in the first reply."
> Why it fails: "Avoid" conventionally reads as a prohibition and the output is checkable (the first reply either contains a date commitment or not), but amid thirteen other hedged bullets it does not clearly signal whether this is "never" or "preferably not."
> Severity: minor.
> Rewrite (author decision):
> - Promoted: "Never promise a fix date in the first reply."
> - Demoted (`## Context`): "First replies usually omit fix dates; this document does not prohibit them."
>
> **9. R2 Explicit strength** — line 19
> Quoted: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus passive, descriptive phrasing ("are recorded") makes this read as an aspiration about the world rather than a directive; an agent that links a document has no way to know whether it violated anything.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> - Demoted (`## Context`): "Reproduction steps are easier to find when kept in the ticket; this document does not require it."
>
> **10. R2 Explicit strength** (secondary R1) — line 20
> Quoted: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: this grants permission rather than directing behavior, so as written it cannot fail — a "rule" that cannot fail is context in disguise (R1). If reassignment is actually expected, the permissive wording hides an obligation.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Reassign any ticket that lands in the wrong queue to the correct queue."
> - Demoted (`## Context`): "Triagers are permitted to reassign misrouted tickets."
>
> **11. R2 Explicit strength** — line 21
> Quoted: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" is the same hedge class as "try to"; the length target is observable, but whether exceeding it is a violation is not stated.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Keep the triage note to one paragraph or less."
> - Demoted (`## Context`): "Short triage notes are preferred; this document sets no length limit."
>
> **12. R2 Explicit strength** — line 22
> Quoted: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: "typically" plus descriptive phrasing ("are ... closed") describes what tends to happen rather than what the agent must do, so the two decisions it implies (close the duplicate; keep the older) both float.
> Severity: material.
> Rewrite (author decision):
> - Promoted: "Close duplicate tickets in favor of the older ticket."
> - Default ("typically" implies exceptions): "Close duplicate tickets in favor of the older ticket unless [author-specified condition, e.g. the newer ticket has more complete reproduction steps]."
> - Demoted (`## Context`): "Duplicates are usually closed in favor of the older ticket; this document does not require it."
>
> ## Not flagged (false-positive guards)
>
> - Line 10 ("Acknowledge every ticket within one business day") and line 23 ("Never share another customer's ticket contents with a reporter"): mandatory, verifiable against timestamps and reply content. Clean.
> - Line 27 (`## Context`): discretionary rationale, correctly placed outside `## Rules`.
> - Lines 13 and 17 (data-loss escalation vs. enterprise-first ordering) are not an R5 conflict: escalation and triage order are different decisions, so they do not prescribe incompatible outcomes for the same input. If the author adopts the default rewrite for line 17, the exception clause is where any intended interaction should be stated.
> - No R4 findings: each bullet carries one obligation (ordering rules like line 11 are a single condition–action unit).
> - Line 3 (description) is a trigger statement, not a rule.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R2 12, R1 1 (secondary, finding 10), R3 1 (secondary, finding 6). Per-rule total 14.
> Counts per severity: material 11, minor 1. Total findings 12.
>
> Overall assessment: the document's structure is exactly right — rules in a labeled section, rationale in a separate context section — but the rules themselves are almost uniformly hedged ("generally", "try to", "usually", "consider", "where possible", "should normally", "ideally", "feel free to", "aim to", "typically"), so only two of fourteen bullets clearly bind. This is a single, repeated R2 defect rather than a mixing of context and constraints, and every instance requires the same author decision: promote the bullet to a plain imperative (optionally with a named exception), or demote it to `## Context` as explicitly nonbinding practice. The two most consequential decisions are line 13 (data-loss escalation) and line 17 (enterprise ordering), because the hedges there give an agent unstated license to skip the safety-relevant action or reorder work. No R5 precedence findings apply, and the context paragraph needs no change.

### With-skill, rep 2

> # Audit: `support-triage`
>
> Line numbers count the opening `---` of the frontmatter as line 1; `## Rules` is line 8, the fourteen rule items are lines 10–23, and the `## Context` paragraph is line 27.
>
> ## Findings
>
> **1. R2 Explicit strength**
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" hedges the ordering requirement without naming when it may be broken, so a reader cannot tell whether owner-before-severity is a violation or a permitted variation.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted (mandatory): "Assign severity before assigning an owner."
> - Default with override (the wording indicates a binding preference; the author supplies the exception): "Assign severity before assigning an owner unless [condition the author names]."
> - Demoted (context, outside `## Rules`): "Severity is usually assigned before an owner; this document does not require that order."
>
> **2. R2 Explicit strength**
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" leaves unclear whether a reproduction attempt is required before the first request for detail or merely encouraged; an agent could skip it entirely without clearly violating the rule.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail, and record the attempt in the ticket."
> - Demoted (context): "Reproducing the reported behavior before asking for more detail is common practice; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" hedges a high-consequence escalation rule with no stated exception, so an agent cannot tell whether a data-loss ticket left unescalated is a violation.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Escalate to on-call whenever a ticket mentions data loss."
> - Default with override: "Escalate to on-call when a ticket mentions data loss unless [condition the author names]."
> - Demoted (context): "Data-loss tickets have usually been escalated to on-call; this document does not require escalation."
>
> **4. R2 Explicit strength**
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: the statement signals a preference but does not state its override condition, so a reader cannot tell whether opening a new issue when a matching one exists is permitted. The obligation itself is still recognizable, and the main exception (no existing issue) is implicit, so intended behavior is mostly clear.
> Severity: minor.
> Suggested rewrite (author decision):
> - Default with override: "Link the ticket to an existing issue when one matches; open a new issue only when no matching issue exists."
> - Demoted (context): "Linking to an existing issue is generally preferred over opening a new one; this document does not require it."
>
> **5. R2 Explicit strength**
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" states a prompt to think, not an obligation or a permission; an agent cannot tell whether a fourteen-day-silent ticket left open is a violation, and a "rule" that only asks for consideration cannot fail.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Close tickets that have had no reporter response for fourteen days."
> - Demoted (context): "Tickets with no reporter response for fourteen days are candidates for closure; this document does not require closing them."
>
> **6. R2 Explicit strength** (secondary: R3)
> Location: line 16.
> Quoted text: "Where possible, tag the affected component."
> Why it fails: "Where possible" functions as an override clause but does not state the condition, so a missing tag cannot be classified as a violation or a permitted exception (R3: the exception is not tied to observable evidence). The obligation itself is clear.
> Severity: minor.
> Suggested rewrite (author decision):
> - Default with override: "Tag the affected component when the ticket identifies one."
> - If a different exception is intended, name its observable condition instead.
>
> **7. R2 Explicit strength**
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" invites exceptions without naming any, so an agent cannot tell when triaging a non-enterprise ticket ahead of an enterprise one is permitted; the prioritization could be dropped without a clear violation.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Triage tickets from enterprise accounts before other tickets."
> - Default with override: "Triage tickets from enterprise accounts first unless [condition the author names]."
> - Demoted (context): "Enterprise tickets have normally been triaged first; this document does not require that ordering."
>
> **8. R2 Explicit strength**
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus passive, descriptive phrasing states an aspiration rather than a directive; an agent can leave reproduction steps in a linked document without clearly violating anything.
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Record reproduction steps in the ticket itself, not only in a linked document."
> - Demoted (context): "Reproduction steps are best kept in the ticket rather than a linked document; this document does not require it."
>
> **9. R2 Explicit strength** (secondary: R1)
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: "Feel free to" grants permission rather than imposing an obligation, so a misrouted ticket left in place is not clearly a violation; if it is only a permission, it cannot fail and is context in disguise inside `## Rules` (R1).
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "Reassign any ticket that lands in the wrong queue."
> - Demoted (context or a permissions note outside `## Rules`): "Triagers may reassign a ticket that lands in the wrong queue."
>
> **10. R2 Explicit strength** (secondary: R3)
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" is best-effort language that does not say whether an overlong note is a violation, and "under a paragraph" has no fixed observable length (R3). The intent (a short note) remains recognizable and a multi-paragraph note is detectable.
> Severity: minor.
> Suggested rewrite (author decision):
> - Promoted: "Keep the triage note to a single paragraph." (If a sharper measure is intended, e.g. a sentence count, the author must supply it.)
> - Demoted (context): "Triage notes are typically a single paragraph; this document does not enforce a length."
>
> **11. R2 Explicit strength** (secondary: R1)
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: this is a passive description of practice with a "typically" hedge, not a directive; an agent cannot tell whether closing the older one, or leaving both open, is a violation. As written it describes rather than directs and cannot fail, so it reads as context placed inside `## Rules` (R1).
> Severity: material.
> Suggested rewrite (author decision):
> - Promoted: "When tickets are duplicates, close the newer ticket in favor of the older one."
> - Default with override: "Close the newer duplicate in favor of the older one unless [condition the author names]."
> - Demoted (context): "Duplicate tickets have typically been closed in favor of the older one; this document does not require it."
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Acknowledge every ticket within one business day." — mandatory, unhedged, verifiable against reply timestamps.
> - Line 18, "Avoid promising a fix date in the first reply." — "Avoid" reads as a prohibition and is checkable against the first reply's text; strength is not ambiguous.
> - Line 23, "Never share another customer's ticket contents with a reporter." — mandatory, verifiable against output.
> - Line 27, the first-response-time history — discretionary context, correctly placed in `## Context`.
> - R4: no item bundles independently checkable obligations; lines 12, 14, and 22 each express one decision with its ordering or alternative.
> - R5: lines 13 and 17 were considered (data-loss escalation vs enterprise-first ordering) and do not conflict — one governs escalation, the other queue order, so they do not prescribe incompatible outcomes for the same decision. No other pair reaches a realistic conflict.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 2, R2 11, R3 2, R4 0, R5 0 (per-rule total 15, including secondary ids).
> Counts per severity: material 8 (lines 11, 12, 13, 15, 17, 19, 20, 22), minor 3 (lines 14, 16, 21). Total findings: 11.
>
> The document has the right skeleton — a labeled `## Rules` section and a separate `## Context` section, with the history paragraph correctly outside the rules — but eleven of its fourteen rule items are hedged ("generally", "try to", "usually", "consider", "ideally", "feel free", "aim to", "typically", "should normally", "where possible", "it is preferable"), so only three items (acknowledge within a day, avoid promising a fix date, never share another customer's contents) state whether they bind. The ones on escalation for data loss, ticket closure, duplicate handling, prioritization, and reassignment are the consequential ones, and two (reassignment, duplicates) are phrased as permission or description rather than direction. Every finding is an author decision between a binding rule (mandatory or a default with a named exception) and demoted context; the audit does not select among them.

### With-skill, rep 3

> # Audit: `support-triage`
>
> Method: read `SKILL.md` and its one referenced file, `references/example-audit.md`; classified each of the target's 15 statements (13 rule items, the description, the context sentence) with the two-question litmus test; ran R1–R5. Line numbers refer to the fenced document as given (line 1 is the opening `---`; rule items are lines 10–23; the Context sentence is line 27).
>
> Structurally the document is in good shape: it has a dedicated `## Rules` section, a separate `## Context` section, the context section holds only discretionary rationale, and no rule is buried in prose. The defect is concentrated on one axis: 11 of the 13 rules carry a hedge that leaves the reader unable to tell whether the statement binds.
>
> ## Findings
>
> **1. R2 Explicit strength**
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" hedges the ordering requirement; an agent cannot tell whether assigning an owner first is a violation or an acceptable variation, and a reviewer cannot check it.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Assign severity before assigning an owner."
> Demoted: move out of `## Rules` into `## Context`: "Severity is commonly assigned before an owner; this document does not require that order."
>
> **2. R2 Explicit strength**
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" leaves unclear whether a reproduction attempt is required before contacting the reporter or merely encouraged, so skipping the attempt cannot be called a violation.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail." (The obligation is the attempt, which is observable in the ticket record; success is not required.)
> Demoted: move to `## Context`: "Reproducing the behavior before asking the reporter for more detail is common practice; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" hedges an escalation trigger; an agent that does not escalate a data-loss ticket cannot be shown to have broken the rule, and no exception condition is named that would justify not escalating.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Escalate to on-call when a ticket mentions data loss."
> Demoted: move to `## Context`: "Data-loss tickets are frequently escalated to on-call; this document does not require escalation."
>
> **4. R2 Explicit strength**
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference without saying whether it binds or when opening a new issue is acceptable; the wording does indicate a binding preference is intended, but no override condition is given.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Link the ticket to an existing issue rather than opening a new one."
> Default with override (author supplies the condition): "Link the ticket to an existing issue when one covers the report; open a new issue only when no existing issue does."
> Demoted: move to `## Context`: "Linking to an existing issue is preferred over opening a new one; this document does not require it."
>
> **5. R2 Explicit strength**
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" can mean a required action, a permitted action, or a prompt to think about it; an agent leaving a 30-day-silent ticket open cannot be said to have violated anything.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Close tickets with no reporter response after fourteen days."
> Demoted: move to `## Context`: "Tickets with no reporter response for fourteen days may be closed; this document does not require closure."
>
> **6. R2 Explicit strength**
> Location: line 16.
> Quoted text: "Where possible, tag the affected component."
> Why it fails: this is phrased as a default with an override, which is a legitimate rule form, but the override condition ("possible") is left to the agent's judgment, so an untagged ticket cannot be distinguished from a permitted skip. Intended behavior (tag when the component is identifiable) is still reasonably clear.
> Severity: minor.
> Suggested rewrite (author decision):
> Promoted: "Tag the affected component."
> Default with named override: "Tag the affected component unless the component cannot be identified from the ticket."
>
> **7. R2 Explicit strength**
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" indicates a priority preference but not whether it binds or what displaces it; the wording indicates a binding preference is intended, but no override condition is given.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Triage tickets from enterprise accounts first."
> Default with override (author supplies the condition, e.g. severity): "Triage tickets from enterprise accounts first unless [condition]."
> Demoted: move to `## Context`: "Enterprise-account tickets are commonly triaged first; this document does not require it."
>
> **8. R2 Explicit strength**
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus descriptive, passive phrasing ("are recorded") reads as an aspiration rather than a directive; an agent that puts steps in a linked document has not clearly violated anything.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> Demoted: move to `## Context`: "Reproduction steps are ideally kept in the ticket rather than a linked document; this document does not require it."
>
> **9. R2 Explicit strength** (secondary: R1)
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: "Feel free to" is a permission. If that is the intent, the item cannot fail and is context in disguise inside `## Rules` (R1); if the author intended an obligation to reassign misrouted tickets, the permissive wording lets an agent leave the ticket where it is.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Reassign any ticket that lands in the wrong queue to the correct queue."
> Demoted: move to `## Context`: "Triagers are permitted to reassign tickets that land in the wrong queue."
>
> **10. R2 Explicit strength** (secondary: R3)
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" hedges whether the length bound binds. Secondarily, "under a paragraph" is not a clean observable threshold (it is unclear whether exactly one paragraph complies).
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Keep the triage note to at most one paragraph." (Author to confirm the bound; a sentence or word limit would be more directly checkable.)
> Demoted: move to `## Context`: "Triage notes are usually a paragraph or less; this document does not set a length limit."
>
> **11. R2 Explicit strength**
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: "typically" plus descriptive phrasing states what tends to happen rather than what the agent must do; closing the newer or leaving both open cannot be called a violation.
> Severity: material.
> Suggested rewrite (author decision):
> Promoted: "Close duplicate tickets in favor of the older one."
> Demoted: move to `## Context`: "Duplicate tickets are usually closed in favor of the older one; this document does not require it."
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Acknowledge every ticket within one business day." Imperative, mandatory by form, checkable against timestamps.
> - Line 18, "Avoid promising a fix date in the first reply." "Avoid" reads as a standard prohibition and is checkable against reply text; not treated as a hedge.
> - Line 23, "Never share another customer's ticket contents with a reporter." Mandatory and checkable.
> - Line 27, the first-response-time history sentence: discretionary rationale, correctly placed in `## Context`.
> - Line 3, the description: a trigger condition, not a behavioral rule.
> - R4: no rule bundles independent obligations; line 14 and line 22 each express one decision with two sides.
> - R5: no reachable conflicts. Line 14 (ticket-to-issue linking) and line 22 (duplicate ticket closure) govern different decisions; line 17 (enterprise ordering) and line 10 (acknowledgement deadline) are compatible; any tension between line 11 (severity before owner) and line 13 (escalate on data loss) is speculative, since escalation and owner assignment are not shown to be the same act.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 1 (secondary, finding 9), R2 11, R3 1 (secondary, finding 10), R4 0, R5 0. Per-rule total 13.
> Counts per severity: material 10, minor 1. Total findings 11.
>
> The document's structure is sound: rules live in a labeled `## Rules` section, the sole context sentence is correctly separated, nothing is buried in prose, no rule is compound, and no realistic precedence conflict exists. Its single systematic defect is strength: only three of thirteen rules (lines 10, 18, 23) state unambiguously that they bind, while the other ten plus one permission-phrased item (line 20) use hedges ("generally", "try to", "usually", "preferable", "consider", "where possible", "should normally", "ideally", "feel free", "aim to", "typically") that leave an agent free to skip them without violating anything. Every one of the eleven findings requires an author decision between the promoted (binding) and demoted (context) readings; the audit did not select either, and where the wording indicated a preference with unstated exceptions (lines 14, 16, 17) a default-with-override form is offered as a third alternative for the author to complete.

### E9 control (rewrite requested)

> I've read the skill and its one referenced file (`references/example-audit.md`); nothing else was needed, and I read nothing under `tests/` or elsewhere. Report follows.
>
> # Audit: `support-triage`
>
> Line numbers refer to the fenced document as supplied (line 1 = opening `---`; the `## Rules` list is lines 10–23; `## Context` is line 27).
>
> ## Findings
>
> **1. R2 Explicit strength** (secondary: none)
> Location: line 11.
> Quoted text: "Generally assign severity before assigning an owner."
> Why it fails: "Generally" admits unnamed exceptions, so a reader cannot tell whether assigning an owner before severity violates the rule or falls inside the exceptions.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Assign severity before assigning an owner."
> Default (only if a binding preference with exceptions is intended): "Assign severity before assigning an owner unless [author names the exception]."
> Demoted (context, outside `## Rules`): "Severity is commonly assigned before an owner; this document does not require the order."
>
> **2. R2 Explicit strength**
> Location: line 12.
> Quoted text: "Try to reproduce the reported behavior before asking the reporter for more detail."
> Why it fails: "Try to" leaves unclear whether a reproduction attempt is required before requesting detail or merely encouraged; the ordering can be checked against ticket history, but the hedge means a skipped attempt cannot be called a violation.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Attempt to reproduce the reported behavior before asking the reporter for more detail." (The obligation is the attempt, checkable by the order of actions in the ticket history; reproduction itself may fail.)
> Demoted: "Reproducing the reported behavior before requesting more detail is common practice; this document does not require it."
>
> **3. R2 Explicit strength**
> Location: line 13.
> Quoted text: "Usually escalate to on-call when a ticket mentions data loss."
> Why it fails: "Usually" admits unnamed exceptions to a high-stakes action, so an agent can decline to escalate a data-loss ticket without checkably violating anything.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Escalate to on-call when a ticket mentions data loss."
> Default: "Escalate to on-call when a ticket mentions data loss unless [author names the exception]."
> Demoted: "Data-loss tickets are commonly escalated to on-call; this document does not require it."
>
> **4. R2 Explicit strength**
> Location: line 14.
> Quoted text: "It is preferable to link the ticket to an existing issue rather than opening a new one."
> Why it fails: "It is preferable" states a preference without saying it binds; the action and its natural condition (an existing issue covers the behavior) are clear and checkable, but the reader cannot tell whether opening a new issue when a matching one exists is a violation.
> Severity: minor.
> Suggested rewrite: author decision.
> Promoted (default with override, which is the reading the wording most nearly implies): "Link the ticket to an existing issue when one covers the reported behavior; open a new issue only when none does."
> Demoted: "Linking to an existing issue is preferred to opening a new one; this document does not require it."
>
> **5. R2 Explicit strength** (secondary: R3)
> Location: line 15.
> Quoted text: "Consider closing tickets with no reporter response after fourteen days."
> Why it fails: "Consider" makes the literal obligation an act of deliberation, which is not observable (R3), and leaves unclear whether closing after fourteen days is required, permitted, or merely suggested.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Close tickets that have had no reporter response for fourteen days."
> Permitted (if only permission is intended): "Tickets with no reporter response for fourteen days may be closed."
> Demoted: "Tickets with no reporter response for fourteen days are candidates for closure; this document does not require closing them."
>
> **6. R2 Explicit strength** (secondary: R3)
> Location: line 16.
> Quoted text: "Where possible, tag the affected component."
> Why it fails: "Where possible" is an override condition with no stated content, so an omitted tag can never be shown to violate the rule (R3); the reader cannot tell when tagging binds.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Tag the affected component."
> Default: "Tag the affected component unless [author names the condition, e.g. the component cannot be determined from the ticket], in which case [author names the fallback]."
> Demoted: "Tagging the affected component is encouraged; this document does not require it."
>
> **7. R2 Explicit strength**
> Location: line 17.
> Quoted text: "Tickets from enterprise accounts should normally be triaged first."
> Why it fails: "should normally" admits unnamed exceptions to a prioritization rule, so triaging a non-enterprise ticket first cannot be checked as a violation.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Triage tickets from enterprise accounts before other tickets."
> Default: "Triage tickets from enterprise accounts before other tickets unless [author names the exception]."
> Demoted: "Enterprise-account tickets are customarily triaged first; this document does not require the order."
>
> **8. R2 Explicit strength**
> Location: line 18.
> Quoted text: "Avoid promising a fix date in the first reply."
> Why it fails: "Avoid" is softer than a prohibition; the action is clear and checkable against the first reply, but the strength marker does not say whether a promised date is a violation.
> Severity: minor.
> Suggested rewrite: author decision.
> Promoted: "Do not promise a fix date in the first reply."
> Demoted: "First replies customarily do not promise a fix date; this document does not prohibit it."
>
> **9. R2 Explicit strength** (secondary: R1)
> Location: line 19.
> Quoted text: "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
> Why it fails: "Ideally" plus passive, descriptive phrasing reads as a statement of a desirable state rather than a directive (R1: only its position in `## Rules` signals that it binds), and the reader cannot tell whether steps recorded only in a linked document violate anything.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Record reproduction steps in the ticket itself, not only in a linked document."
> Demoted: "Reproduction steps are best kept in the ticket rather than a linked document; this document does not require it."
>
> **10. R2 Explicit strength**
> Location: line 20.
> Quoted text: "Feel free to reassign a ticket if it lands in the wrong queue."
> Why it fails: "Feel free to" grants permission, so a misrouted ticket left in the wrong queue violates nothing; the reader cannot tell whether reassignment is an obligation or an option.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Reassign any ticket that lands in the wrong queue to the correct queue."
> Permitted (if only permission is intended): "A ticket that lands in the wrong queue may be reassigned."
> Demoted: "Misrouted tickets can be reassigned; this document does not require it."
>
> **11. R2 Explicit strength** (secondary: R3)
> Location: line 21.
> Quoted text: "Aim to keep the triage note under a paragraph."
> Why it fails: "Aim to" makes the obligation an aspiration, and "under a paragraph" has no measurable bound (R3) — a paragraph can be one sentence or ten — so the note length cannot be checked as compliant or not.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Keep the triage note to at most one paragraph." (If a firmer bound is intended, state a sentence or character count; that is a tightening the author must choose.)
> Demoted: "Triage notes are kept short, typically one paragraph; this document sets no limit."
>
> **12. R2 Explicit strength** (secondary: R1)
> Location: line 22.
> Quoted text: "Duplicate tickets are typically closed in favor of the older one."
> Why it fails: "typically" plus passive description of practice reads as context (R1: nothing in the phrasing signals a directive), and the reader cannot tell whether keeping the newer duplicate open, or closing the older one, violates anything.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted: "Close duplicate tickets in favor of the older ticket."
> Demoted (context, outside `## Rules`): "Duplicate tickets are usually closed in favor of the older one; this document does not require it."
>
> **Not flagged (false-positive guards)**
> - Line 10 "Acknowledge every ticket within one business day." and line 23 "Never share another customer's ticket contents with a reporter." — mandatory, verifiable against timestamps and reply contents; clean.
> - Line 27 (`## Context`) — discretionary rationale, correctly placed outside `## Rules`.
> - R4: no statement bundles independently checkable obligations.
> - R5: no reachable conflict. Enterprise-first (line 17) and data-loss escalation (line 13) govern different decisions (triage order vs. escalation); linking to an existing *issue* (line 14) and closing a duplicate *ticket* (line 22) act on different objects; the acknowledgement deadline (line 10) and reproduce-before-asking (line 12) are compatible because an acknowledgement is not a request for detail.
>
> **Safety note:** none. The document contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 2, R2 12, R3 3, R4 0, R5 0 (per-rule total 17, secondary ids included).
> Counts per severity: material 10, minor 2 (12 findings).
>
> The document's structure is sound — a dedicated `## Rules` section, context kept out of it, and two rules (acknowledgement deadline, never share another customer's contents) that are unambiguous and verifiable. The defect is concentrated in one pattern: twelve of fourteen rules are hedged ("generally", "usually", "try to", "consider", "where possible", "feel free to", "ideally", "aim to", "typically", "preferable", "avoid"), so the reader cannot tell which bind, and none of the hedges names the exception it implies. Two are additionally phrased as descriptions of practice rather than directives, and three carry conditions or thresholds that cannot be observed. Every finding is an author decision between a binding rule (optionally a default with a named override) and explicitly nonbinding context; the audit does not select. Given the `## Context` rationale (first-response time drifting past three days), the author will likely want most of these to bind, but that is an inference for the author to confirm, not the audit's.
>
> ## Rewritten Document
>
> This illustrative rewrite assumes the author selects the **promoted** (binding) reading for every finding, and for line 14 the default-with-override reading. Those are supplied assumptions, not meanings inferred by the audit; any rule the author intends as context should instead move under `## Context` using the demoted wording above, and any intended exception (findings 1, 3, 6, 7) must be named by the author.
>
> ```markdown
> ---
> name: support-triage
> description: Use when triaging inbound support tickets.
> ---
>
> # support-triage
>
> ## Rules
>
> 1. Acknowledge every ticket within one business day.
> 2. Assign severity before assigning an owner.
> 3. Attempt to reproduce the reported behavior before asking the reporter for more detail.
> 4. Escalate to on-call when a ticket mentions data loss.
> 5. Link the ticket to an existing issue when one covers the reported behavior; open a new issue only when none does.
> 6. Close tickets that have had no reporter response for fourteen days.
> 7. Tag the affected component.
> 8. Triage tickets from enterprise accounts before other tickets.
> 9. Do not promise a fix date in the first reply.
> 10. Record reproduction steps in the ticket itself, not only in a linked document.
> 11. Reassign any ticket that lands in the wrong queue to the correct queue.
> 12. Keep the triage note to at most one paragraph.
> 13. Close duplicate tickets in favor of the older ticket.
> 14. Never share another customer's ticket contents with a reporter.
>
> ## Context
>
> Triage was formalized after a quarter in which the median first-response time drifted past three days.
> ```

### Author-usability arm 1 (reads report 1)

> I read both files. Here are my decisions, then the revised document.
>
> ## Decisions
>
> Resolved (chose a complete option from the report):
>
> 1. **Finding 2 (line 12, "Try to reproduce")** — Promoted: "Attempt to reproduce the reported behavior, and record the result in the ticket, before asking the reporter for more detail."
> 2. **Finding 3 (line 13, data-loss escalation)** — Promoted, unconditionally: "Escalate to on-call when a ticket mentions data loss." I am deliberately dropping whatever exception "usually" covered: over-escalating a recovered-data ticket is cheap; missing a real one is not.
> 3. **Finding 4 (line 14, link to existing issue)** — Promoted: "Link the ticket to an existing issue when one matches; open a new issue only when no matching issue exists." The only exception is the natural one, already stated.
> 4. **Finding 5 (line 15, fourteen-day close)** — Promoted: "Close tickets that have had no reporter response for fourteen days."
> 5. **Finding 8 (line 18, fix date)** — Promoted: "Never promise a fix date in the first reply."
> 6. **Finding 9 (line 19, repro steps location)** — Promoted: "Record reproduction steps in the ticket itself, not in a linked document."
> 7. **Finding 10 (line 20, reassign)** — Promoted: "Reassign any ticket that lands in the wrong queue to the correct queue."
> 8. **Finding 11 (line 21, note length)** — Promoted: "Keep the triage note to one paragraph or less."
>
> Not resolvable from the information I have (the hedge signals an exception the original author knew and the document does not record; the report's "default" option needs that exception filled in, and its "promoted" option silently discards it, which is not semantic-preserving):
>
> 9. **Finding 1 (line 11, "Generally assign severity first")** — strength resolved (binding, stays in Rules); exception condition unknown. Left as a bracketed placeholder.
> 10. **Finding 6 (line 16, "Where possible, tag the component")** — strength resolved (binding); I do not know the tag taxonomy, so I can neither name a fallback tag nor state the boundary of "where possible". Placeholder.
> 11. **Finding 7 (line 17, enterprise first)** — strength resolved (binding); exception unknown. The report's suggested candidate (a non-enterprise ticket reporting data loss) is plausible but not something I can confirm. Placeholder.
> 12. **Finding 12 (line 22, duplicates)** — strength resolved (binding); exception unknown. Placeholder.
>
> I chose not to demote any bullet: all fourteen sit under `## Rules`, and the Context line says triage was formalized to fix response-time drift, which reads as intent to bind rather than to describe practice.
>
> Unchanged per the report's not-flagged list: lines 3, 10, 23, and the Context paragraph.
>
> ## Revised document
>
> ```markdown
> ---
> name: support-triage
> description: Use when triaging inbound support tickets.
> ---
>
> # support-triage
>
> ## Rules
>
> - Acknowledge every ticket within one business day.
> - Assign severity before assigning an owner unless [AUTHOR: exception not recorded — state it or delete this clause].
> - Attempt to reproduce the reported behavior, and record the result in the ticket, before asking the reporter for more detail.
> - Escalate to on-call when a ticket mentions data loss.
> - Link the ticket to an existing issue when one matches; open a new issue only when no matching issue exists.
> - Close tickets that have had no reporter response for fourteen days.
> - Tag the affected component unless [AUTHOR: condition not recorded — state it, or name a fallback tag for tickets with no identifiable component].
> - Triage tickets from enterprise accounts before other tickets unless [AUTHOR: exception not recorded — state it or delete this clause].
> - Never promise a fix date in the first reply.
> - Record reproduction steps in the ticket itself, not in a linked document.
> - Reassign any ticket that lands in the wrong queue to the correct queue.
> - Keep the triage note to one paragraph or less.
> - Close duplicate tickets in favor of the older ticket unless [AUTHOR: exception not recorded — state it or delete this clause].
> - Never share another customer's ticket contents with a reporter.
>
> ## Context
>
> Triage was formalized after a quarter in which the median first-response time drifted past three days.
> ```
>
> The four bracketed bullets are not final; each needs one fact from whoever wrote the original hedges. Everything else is ready as written.

### Author-usability arm 2 (reads report 2)

> Both files read. Decisions, then the revised document.
>
> **Decisions**
>
> 1. Line 11 (severity before owner) — Promoted (mandatory).
> 2. Line 12 (reproduce before asking) — Promoted, using the report's wording. Note: this wording adds "and record the attempt in the ticket," which is a new obligation the original did not state; I accepted it because without it the rule is not checkable.
> 3. Line 13 (data-loss escalation) — Promoted.
> 4. Line 14 (link to existing issue) — Default with override, using the report's condition ("when one matches; open a new issue only when no matching issue exists"), which is the exception already implicit in the original.
> 5. Line 15 (fourteen-day close) — Promoted.
> 6. Line 16 (tag component) — Default with override, using the report's condition ("when the ticket identifies one").
> 7. Line 17 (enterprise first) — Promoted.
> 8. Line 19 (reproduction steps in ticket) — Promoted.
> 9. Line 20 (reassign misrouted tickets) — Promoted.
> 10. Line 21 (triage note length) — Promoted as "a single paragraph"; I did not supply a sentence count because the document gives no basis for one.
> 11. Line 22 (duplicates) — Promoted.
>
> Two caveats. First, for findings 1, 3, 7, and 11 the report also offered "default with override unless [condition the author names]"; I did not pick that option for any of them because the document contains no exception I could name, and inventing one would be a guess. Second, every finding was resolvable as a choice between binding and demoted, but the choice itself rests on the items' placement in `## Rules` and on the document's stated purpose (triage formalized to fix response times), not on any explicit statement of intent — the original author may have meant items 5 and 9 ("consider", "feel free") as genuinely discretionary, in which case the demoted options should be taken instead. No `## Context` changes were needed since nothing was demoted.
>
> **Revised document**
>
> ```markdown
> ---
> name: support-triage
> description: Use when triaging inbound support tickets.
> ---
>
> # support-triage
>
> ## Rules
>
> - Acknowledge every ticket within one business day.
> - Assign severity before assigning an owner.
> - Attempt to reproduce the reported behavior before asking the reporter for more detail, and record the attempt in the ticket.
> - Escalate to on-call whenever a ticket mentions data loss.
> - Link the ticket to an existing issue when one matches; open a new issue only when no matching issue exists.
> - Close tickets that have had no reporter response for fourteen days.
> - Tag the affected component when the ticket identifies one.
> - Triage tickets from enterprise accounts before other tickets.
> - Avoid promising a fix date in the first reply.
> - Record reproduction steps in the ticket itself, not only in a linked document.
> - Reassign any ticket that lands in the wrong queue.
> - Keep the triage note to a single paragraph.
> - When tickets are duplicates, close the newer ticket in favor of the older one.
> - Never share another customer's ticket contents with a reporter.
>
> ## Context
>
> Triage was formalized after a quarter in which the median first-response time drifted past three days.
> ```
>
> No files were edited.

### Author-usability arm 3 (reads report 3)

> **Decisions, per finding in the report**
>
> 1. Line 11 (severity before owner) — **Promoted**: "Assign severity before assigning an owner."
> 2. Line 12 (reproduce before asking) — **Promoted**, using the report's "attempt" wording so the obligation is the observable attempt, not success.
> 3. Line 13 (data-loss escalation) — **Promoted**: "Escalate to on-call when a ticket mentions data loss." No exception is intended.
> 4. Line 14 (link vs. new issue) — **Default with override**, adopting the report's condition ("when one covers the report; open a new issue only when no existing issue does"). That condition follows from what "existing issue" means, so it is not new policy.
> 5. Line 15 (fourteen-day close) — **Promoted**. The specific threshold was meant as a policy, not a suggestion.
> 6. Line 16 (tag component) — **Default with named override**: "unless the component cannot be identified from the ticket."
> 7. Line 17 (enterprise first) — **Unresolved.** "Should normally" was meant as a binding default with exceptions, so a flat promotion misstates it and a demotion drops it, and the document contains nothing that names the displacing condition (the report's "e.g. severity" is the auditor's example, not something I can confirm). I have left line 17 unchanged rather than invent the condition; it still needs an author-supplied override.
> 8. Line 19 (repro steps in ticket) — **Promoted**: "Record reproduction steps in the ticket itself, not in a linked document."
> 9. Line 20 (reassign misrouted ticket) — **Promoted** to an obligation; the item was in the rule list so misrouted tickets get moved, and a bare permission would not achieve that.
> 10. Line 21 (triage note length) — **Promoted** as "at most one paragraph." I confirm the bound is one paragraph; I am not adding a sentence or word limit because the document gives no basis for picking a number.
> 11. Line 22 (duplicate closure) — **Promoted**: "Close duplicate tickets in favor of the older one."
>
> Nothing was demoted, so `## Context` is unchanged. Items the report did not flag (lines 3, 10, 18, 23, 27) are unchanged.
>
> **Revised document**
>
> ```markdown
> ---
> name: support-triage
> description: Use when triaging inbound support tickets.
> ---
>
> # support-triage
>
> ## Rules
>
> - Acknowledge every ticket within one business day.
> - Assign severity before assigning an owner.
> - Attempt to reproduce the reported behavior before asking the reporter for more detail.
> - Escalate to on-call when a ticket mentions data loss.
> - Link the ticket to an existing issue when one covers the report; open a new issue only when no existing issue does.
> - Close tickets with no reporter response after fourteen days.
> - Tag the affected component unless the component cannot be identified from the ticket.
> - Tickets from enterprise accounts should normally be triaged first.
> - Avoid promising a fix date in the first reply.
> - Record reproduction steps in the ticket itself, not in a linked document.
> - Reassign any ticket that lands in the wrong queue to the correct queue.
> - Keep the triage note to at most one paragraph.
> - Close duplicate tickets in favor of the older one.
> - Never share another customer's ticket contents with a reporter.
>
> ## Context
>
> Triage was formalized after a quarter in which the median first-response time drifted past three days.
> ```
>
> Files read: `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/s15-usability/support-triage.md` and `.../s15-usability/report-rep3.md`. No files were edited.
