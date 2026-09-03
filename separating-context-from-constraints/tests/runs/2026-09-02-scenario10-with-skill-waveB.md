# Scenario 10 — ledger-service, With-Skill, three reps (Wave B rerun, W6, W14 direction test, W17 E9a; D10.11 protected)

```
Date: 2026-09-02
Run: with-skill
SKILL.md blob: 2cb876f4010f55a3259fe740a46d1e8aaea78eea
Commit: a9f0116 (branch `separating-context-wave3`, Wave B wording; not on `main`)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md: read that file and any file it references under /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/references/. Do not read any other file anywhere, do not read anything under any tests/ directory, do not load any skill through the harness, and do not edit any file. Reply with your report only." followed by the scenario-10 prompt from `../scenarios.md`, verbatim
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under the preregistration's Rerun classification; per-defect tables transcribed and reconciled by a Claude subagent (opus) against the archived outputs; tool calls extracted by script
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); no dispatch for this scenario failed, so every rep is a first dispatch
```

## Scoring

Each cell gives the rule id and severity the rep's own finding states, with the finding number in parentheses.

| Planted defect | Rep 1 | Rep 2 | Rep 3 |
| --- | --- | --- | --- |
| D10.1 migration plan | R1 / material (F1) | R1 / material (F1) | R1 / material (F1) |
| D10.2 rolled-back transaction | R1 / material (F7) | R1 / material (F7) | R1 / material (F7) |
| D10.3 `finance-review` sign-off | R1 (+R4 secondary) / material (F9) | R1 / material (F9) | R1 / material (F9) |
| D10.4 "Keep the changelog entries readable." | R3 / material (F3) | R3 / material (F3) | R3 / material (F3) |
| D10.5 "Generally use the `internal/` package…" | R2 / material (F5) | R2 / material (F5) | R2 / material (F5) |
| D10.6 `make test` trailing rationale | R1 / minor (F2) | R1 / minor (F2) | R1 / minor (F2) |
| D10.7 table-driven-tests rationale | R1 / minor (F4) | R1 / minor (F4) | R1 / minor (F4) |
| D10.8 `cmd/backfill` prohibition | R1 / minor (F10) | R1 / minor (F10) | R1 / minor (F10) |
| D10.9 raw `account_number` | R1 / minor (F8) | R1 / minor (F8) | R1 / minor (F8) |
| D10.10 `Money` from a float literal | R1 / minor (F6) | R1 / minor (F6) | R1 / minor (F6) |
| D10.11 currency co-update (protected on rerun) | not flagged | not flagged | not flagged |
| **E1 over D10.1–D10.10** | **10/10** | **10/10** | **10/10** |

| Rep | E2 | E3 (D10.5) | E9a |
| --- | --- | --- | --- |
| 1 | 0 | `preserved` — promoted, demoted, and a default whose override condition is left to the author, none selected | `absent` (E9b `unrequested`) |
| 2 | 0 | `preserved` — same three labelled alternatives, none selected | `absent` (E9b `unrequested`) |
| 3 | 0 | `preserved` — same three labelled alternatives, none selected | `absent` (E9b `unrequested`) |

E7 direction test: passes ×3, identically in every rep — D10.6 and D10.7 minor, D10.1 through D10.5 material, and D10.8, D10.9, D10.10 minor.
The direction the preregistration asks for is satisfied because at least one low-consequence defect is minor while at least one high-consequence defect is material, and the three high-consequence prohibitions labelled minor in every rep are the same W14 observation the archived cell recorded.
Rep 1 is the only rep to carry a secondary id: an R4 on D10.3, for the two independently checkable results (a tagged issue exists, sign-off is recorded) that share one trigger.

E6: `unique` for every finding in every rep, read from the outputs alone.
Every rep states its line-numbering convention in its opening paragraph and gives each finding a `line N (Section)` location plus the quoted sentence.

Scored assertions from `../scenarios.md`: 1–6 pass ×3; 7 passes ×3 as amended for Wave B, since D10.8, D10.9 and D10.10 each get an R1 finding and D10.11's treatment is now the rerun classification's protection, superseding the archived cell's 11/12 per rep, where assertion 7 failed ×3 on D10.11 alone; 8 (E2 = 0) passes ×3; 9 (E6 `unique`) passes ×3; 10 (E7 direction) passes ×3; 11 (E9a `absent`) passes ×3. **11/11 ×3.**
Assertion 12, the E9 control arm, is not exercised in Wave B; the archived control at [`2026-09-01-scenario10-with-skill.md`](2026-09-01-scenario10-with-skill.md) is the calibration for the `full-document` branch of the detector.

E9c: guard-lines true ×3; classification-table true ×3 (no rep prints a separate table, but each rep's "Not flagged" list assigns Core Concept classes — procedural, load-bearing fact, descriptive or discretionary context — to well over two statements); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** Nothing in this cell moved except the denominator.
The three reps reproduce the archived cell finding for finding: the same ten defects, the same rule ids, the same severities, the same zero false positives, and the same explicit refusal to flag D10.11 as anything but a procedural how-to.
What changed is the preregistration, which now protects D10.11 rather than planting it, so the archived 10/11 becomes 10/10 without any arm behaving differently.
The reruns therefore hold D10.11's protection 3/3 and confirm that the Wave B wording did not disturb W6's location convention, W14's severity direction, or the E9a `absent` result W17 rests on.

## Scored Outputs (verbatim)

### With-skill, rep 1

> I have read the skill and its one referenced file; nothing else is needed. Here is the audit.
>
> # Audit: `ledger-service` (CLAUDE.md-style repository instructions)
>
> Line numbers refer to the fenced document with line 1 = the opening `---`. The document is long-form (labeled sections, including a `## Rules` section), so under R1 embedded rules that are liftable are rewritten into `## Rules`.
>
> ## Findings
>
> **1. R1 Distinguishability**
> Location: line 13 (Overview).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a merge-gating obligation is embedded in a paragraph of background facts, in a section framed as orientation, and led by a causal clause that makes it read as explanation. The document has a `## Rules` section, so a reader who goes there for the rules misses this one. It is liftable — obeying it does not depend on the surrounding passage.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged." Keep the fact in Overview: "Every write is replicated synchronously across the three clusters."
>
> **2. R1 Distinguishability**
> Location: line 26 (Rules).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule is clear, but the item carries discretionary rationale inside the rule section.
> Severity: minor.
> Suggested rewrite: rule item: "Run `make test` before opening a pull request." Move to Testing: "`make test` is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free."
>
> **3. R3 Verifiability**
> Location: line 27 (Rules).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence — no template, length bound, lint, or artifact — against which compliance can be checked. The statement does not reveal the intended safeguard.
> Severity: material.
> Suggested rewrite: author decision.
> (a) If a concrete standard is intended, state it as the checkable result — a named template, a length bound, or a lint the entry must pass — using the author's actual standard, not an invented one.
> (b) If it is only a value statement, remove it from `## Rules` and place it as context: "The team values readable changelog entries; this document defines no format requirement."
>
> **4. R1 Distinguishability**
> Location: line 28 (Rules).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: the default is explicit ("Prefer"), but the item pads the rule section with rationale and a fact about existing suites.
> Severity: minor.
> Suggested rewrite: rule item: "Prefer table-driven tests." Move to Testing: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **5. R2 Explicit strength**
> Location: line 29 (Rules).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" hedges strength; a reader cannot tell whether placing non-public code outside `internal/` violates the rule.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted (mandatory): "Place code not consumed by the public API in the `internal/` package."
> Demoted (context, outside `## Rules`): "Code not consumed by the public API conventionally lives under `internal/`; this document does not require it."
> Default (offered because placement in `## Rules` indicates some binding preference is intended): "Place code not consumed by the public API in `internal/` unless [author-named override condition]." The author must supply the condition.
>
> **6. R1 Distinguishability**
> Location: line 34 (Working with money).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: an explicit prohibition sits in a paragraph otherwise made of type semantics and history, outside the rule section. It is marked ("Never") and liftable.
> Severity: minor — the wording is clear and checkable against code; only placement is off.
> Suggested rewrite: move the sentence unchanged into `## Rules`. The section keeps lines 33, 35, and 36 as load-bearing facts.
>
> **7. R1 Distinguishability**
> Location: line 42 (Testing).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: a hard test-structure obligation is introduced with "It is worth noting", a phrase that signals discretionary commentary, and is surrounded by descriptive facts about suite timing. Liftable.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any test touching the `postings` package must run inside a transaction that is rolled back at the end." Keep in Testing: "The shared fixture set is not regenerated between tests."
>
> **8. R1 Distinguishability**
> Location: line 49 (Observability).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: an explicit prohibition embedded among facts about tracing, log format, and dashboards, outside the rule section. Marked and liftable.
> Severity: minor — wording is clear and checkable against log output; placement is the defect.
> Suggested rewrite: add to `## Rules`: "Log lines must never include the raw `account_number` field." Keep in Observability: "The log pipeline is replicated to a lower-trust analytics store."
>
> **9. R1 Distinguishability** (secondary: R4)
> Location: line 62 (Appendix).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a pre-change approval gate is introduced with "By the way" in a how-to appendix, after the procedural entry it governs, with its rationale attached. Nothing in placement or framing signals that it binds. Secondary R4: two independently checkable results (an issue exists with the tag; sign-off is recorded) share one trigger and can be listed separately under it.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Before adding a currency: (1) open an issue tagged `finance-review`; (2) obtain sign-off from the finance team." Keep in the Appendix as context: "Unsupported currencies leak into customer invoices."
>
> **10. R1 Distinguishability**
> Location: line 63 (Appendix).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: the "never" clause is a policy prohibition, not a how-to step, but it is filed as a common-task entry in a paragraph that mixes procedure and rationale. Marked and liftable.
> Severity: minor — the prohibition is explicit and checkable against tool traces.
> Suggested rewrite: add to `## Rules`: "Never run a direct SQL update against `postings`; backfill with `cmd/backfill`." Keep in the Appendix: "Backfilling: `cmd/backfill`."
>
> ## Not flagged (false-positive guards)
>
> - Line 14 ("Most contributors find the codebase easier to navigate...") and line 41 ("most contributors run them only before pushing"): descriptive context, not hedged rules — they inform, they do not direct.
> - Lines 18 and 21 (`make bootstrap`; stop the other Postgres instance): procedural steps for a reader already committed to setup; ignoring them fails the bootstrap, not a policy.
> - Line 28's "Prefer": strength is unambiguous (a default). No override condition is stated, but R2 flags only ambiguous strength.
> - Line 35 (`fx.Convert` requires an explicit rate source) and line 48 (collector parses `msg`/`level`): load-bearing tool semantics, correctly outside `## Rules`.
> - Line 56: the legacy runbook is explicitly marked "not current policy" — correct nonbinding framing.
> - Line 61 ("update `fx/currencies.go` and the `currency_code` enum migration together"): read as a procedural how-to. If the author intends "together" as a same-change invariant, it is a rule and belongs in `## Rules`; the document does not say so, so it is not flagged.
> - R5: no reachable conflicts. `make test` (line 26), the CI description (line 43), and the integration-test habit (line 41) are consistent; the currency gate (line 62) and the currency procedure (line 61) are sequential, not competing.
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 1 (secondary, on finding 9), R5 0 — per-rule total 11.
> Counts per severity: material 5 (findings 1, 3, 5, 7, 9), minor 5 (findings 2, 4, 6, 8, 10) — 10 findings.
>
> The document has a `## Rules` section but keeps only five of its roughly eleven binding rules there, and two of those five carry rationale padding. The six rules living elsewhere are all explicitly worded (must/never), so the defect is placement rather than intent; the three that are additionally framed as asides ("Because...", "It is worth noting", "By the way") are the ones most likely to be skipped by a reader who treats Overview, Testing, and the Appendix as background. Inside the rule section, one rule is unverifiable ("readable") and one is hedged ("Generally"), both needing author decisions before a semantic-preserving rewrite is possible. Facts and history are otherwise well placed, and the legacy runbook is correctly marked nonbinding.
>
> Safety note: none. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 2

> # Audit: `ledger-service` CLAUDE.md-style document
>
> Procedure followed: read `SKILL.md` and its one reference (`references/example-audit.md`); classified each statement with the two-question litmus test; ran R1–R5. Line numbers refer to the target document as pasted (line 1 = opening `---`). The document is long-form (labeled sections, including a `## Rules` section), so embedded rules owe a move into that section when liftable.
>
> ## Findings
>
> **1. R1 Distinguishability**
> Location: line 13 (Overview).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a binding rule (a reviewed migration plan is a merge precondition) is embedded in a paragraph of facts (lines 10–12, 14), subordinated inside a "Because..." sentence that reads as architectural explanation. The document has a `## Rules` section and this rule is not in it.
> Severity: material — the causal framing and Overview placement make it plausible a reader treats it as background and misses the obligation.
> Suggested rewrite: add to `## Rules`: "Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged." Keep the rationale in Overview: "Every write is replicated synchronously across those clusters, which is why `postings` changes require a reviewed migration plan (see Rules)."
>
> **2. R1 Distinguishability**
> Location: line 26 (Rules).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule is clear, but the rule section carries a fact (same suite as CI) and rationale (queue round trips, shared runners). R1 keeps rule sections free of context.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Run `make test` before opening a pull request." Move to Testing: "`make test` runs the same suite CI runs; catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
>
> **3. R3 Verifiability**
> Location: line 27 (Rules).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence; nothing in the document lets a reader decide whether an entry passes or fails.
> Severity: material.
> Suggested rewrite: author decision — the statement does not reveal the intended safeguard.
> If a specific form is intended, name the observable property, e.g. "Each changelog entry is one sentence naming the affected package and the user-visible change" (illustrative only; the author must supply the actual property).
> If it is only guidance, remove it from `## Rules` and state it as context: "Changelog entries are read by [audience]; the team values readability, but this document defines no format requirement."
>
> **4. R1 Distinguishability**
> Location: line 28 (Rules).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: the two relative clauses are rationale and codebase background living inside the rule section.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Prefer table-driven tests." Move to Testing: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **5. R2 Explicit strength**
> Location: line 29 (Rules).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" hedges; a reader cannot tell whether placing a non-public package outside `internal/` violates policy.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted (mandatory): "Place any package not consumed by the public API under `internal/`."
> Demoted (context): remove from `## Rules`; in Overview: "Packages not consumed by the public API conventionally live under `internal/`; this document does not require it."
> Because the statement sits in `## Rules`, the target indicates a binding preference may be intended; if so, a third alternative is a default with an author-supplied override: "Place packages not consumed by the public API under `internal/` unless <condition the author names>."
>
> **6. R1 Distinguishability**
> Location: line 34 (Working with money).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a binding rule embedded in a paragraph otherwise made of load-bearing facts (lines 33, 35, 36), outside the `## Rules` section.
> Severity: minor — the sentence is explicitly marked ("Never") and unmistakable to a reader who reaches the section; only placement is defective.
> Suggested rewrite: move the sentence unchanged into `## Rules`; leave lines 33, 35, 36 in place.
>
> **7. R1 Distinguishability**
> Location: line 42 (Testing).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: a binding rule introduced with "It is worth noting that", which frames it as an aside, embedded among facts about suite timing and CI (lines 40, 41, 43).
> Severity: material — the aside framing plausibly causes the rule to be read as a tip rather than a requirement.
> Suggested rewrite: add to `## Rules`: "Any test touching the `postings` package must run inside a transaction that is rolled back at the end." Keep in Testing: "The shared fixture set is not regenerated between tests."
>
> **8. R1 Distinguishability**
> Location: line 49 (Observability).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a binding rule with attached rationale, embedded in a paragraph of tool-semantics facts (lines 47, 48, 50), outside `## Rules`.
> Severity: minor — explicitly marked ("must never"); placement only.
> Suggested rewrite: add to `## Rules`: "Never include the raw `account_number` field in log lines." Keep in Observability: "The log pipeline is replicated to a lower-trust analytics store."
>
> **9. R1 Distinguishability**
> Location: line 62 (Appendix).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a merge-gating rule opened with "By the way", placed in a how-to appendix after the procedural line it governs (line 61), with rationale attached. Nothing in placement signals that it binds.
> Severity: material — the aside framing and appendix location plausibly cause the obligation to be missed by a reader who consults `## Rules`.
> Suggested rewrite: add to `## Rules`: "Before adding a currency, open an issue tagged `finance-review` and obtain sign-off from the finance team." Keep in the appendix: "Unsupported currencies leak into customer invoices, which is why currency additions require finance sign-off (see Rules)." (The two actions share one trigger and stay together under R4.)
>
> **10. R1 Distinguishability**
> Location: line 63 (Appendix).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: a prohibition sits inside a "task: how" line in a paragraph of procedural steps (lines 60–61); only the word "never" separates policy from procedure.
> Severity: minor — the prohibition is explicitly marked and clear.
> Suggested rewrite: add to `## Rules`: "Never backfill `postings` with a direct SQL update; use `cmd/backfill`." Reduce the appendix line to "Backfilling: `cmd/backfill`."
>
> ## Not flagged (false-positive guards)
>
> - Lines 18, 21, 60, 61: procedural steps for a reader already committed to a task (bootstrap, port conflict, regenerate fixtures, add a currency); imperative grammar but not binding under R1.
> - Lines 33, 35, 36, 40, 43, 47, 48, 50, 54, 55: load-bearing facts (type semantics, build tags, log keys, release job behavior); correctly outside `## Rules`.
> - Lines 14, 41: descriptive statements about what contributors do; not hedged rules.
> - Line 56: legacy runbook explicitly labeled "not current policy" — discretionary context, correctly framed.
> - Line 28 "Prefer": signals default strength clearly; R2 flags only hedges that leave binding status unclear. The missing override condition is not, by itself, ambiguous strength.
> - R4: no compound rule bundles independent obligations; line 62's two actions share one trigger.
> - R5: no reachable conflicts. Line 25 (never commit to `main`) and line 54 (release job cuts from `main`) govern different actors; line 13 (migration plan for `postings` changes) and line 63 (backfill via `cmd/backfill`) prescribe compatible outcomes.
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 0, R5 0.
> Counts per severity: material 5 (R1 lines 13, 42, 62; R2 line 29; R3 line 27), minor 5 (R1 lines 26, 28, 34, 49, 63).
> No finding carries a secondary rule id, so the per-rule total of 10 equals the 10 findings counted by severity.
>
> The document has a `## Rules` section but keeps only five of its eleven binding statements there; the other six are scattered across Overview, Working with money, Testing, Observability, and the Appendix, three of them framed as asides or explanation ("Because...", "It is worth noting that...", "By the way..."). Two items inside `## Rules` carry rationale that belongs in the topical sections, one rule is untestable ("readable"), and one is hedged ("Generally"). The R2 and R3 findings require author decisions before a rewrite can claim to preserve intended behavior; the eight R1 findings are mechanical moves with no semantic change.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 3

> # Audit: `ledger-service` (CLAUDE.md-style repository instructions)
>
> Line numbers count the opening `---` of the frontmatter as line 1. The document is long-form (labeled sections, including a `## Rules` section), so under R1 an embedded rule that is liftable owes a move into `## Rules`.
>
> ## Findings
>
> **1. R1 Distinguishability**
> Location: line 13 (`## Overview`).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a binding merge gate is embedded in a narrative paragraph of service description (language, cluster count, history), led by its rationale clause, in a section a reader treats as background. The rule is liftable; nothing about obeying it depends on the passage.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged." Keep the rationale in `## Overview` as a fact: "Every write is replicated synchronously across the three clusters."
>
> **2. R1 Distinguishability**
> Location: line 26 (`## Rules`).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule item carries explanatory context (what the suite is, why local runs help) inside the rule section; R1 keeps rule sections free of facts and rationale.
> Severity: minor.
> Suggested rewrite: rule item becomes "Run `make test` before opening a pull request." Move the remainder to `## Testing`: "`make test` runs the same suite CI runs; catching failures locally saves a round trip through the queue and keeps the shared runners free."
>
> **3. R3 Verifiability**
> Location: line 27 (`## Rules`).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence and the document bounds it with no quantity, format, or named artifact; the rule cannot be checked as followed or violated. It does not reveal the intended safeguard, so this is an author decision.
> Severity: material.
> Suggested rewrite: labeled alternatives, none selected.
> - If a format convention is intended: state it observably, e.g. "Write each changelog entry as one sentence under the release heading, naming the affected package" (illustrative; the author supplies the real convention).
> - If an existing artifact defines the format: "Follow the entry format used in `CHANGELOG.md`" (or a named template).
> - If only aspiration: remove from `## Rules` and state as context, "Changelog entries are read by [audience]; this document defines no format requirement."
>
> **4. R1 Distinguishability**
> Location: line 28 (`## Rules`).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: rationale and a style observation are bundled into the rule item inside the rule section. ("Prefer" is read as a stated default and is not flagged under R2.)
> Severity: minor.
> Suggested rewrite: rule item becomes "Prefer table-driven tests." Move the rest to `## Testing`: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **5. R2 Explicit strength**
> Location: line 29 (`## Rules`).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" hedges strength; a reader cannot tell whether placing a non-public package outside `internal/` violates the rule or is an ordinary judgment call.
> Severity: material.
> Suggested rewrite: author decision.
> - Promoted (mandatory): "Place every package not consumed by the public API under `internal/`."
> - Demoted (context, outside `## Rules`): "Packages not consumed by the public API conventionally live under `internal/`; this document does not require it."
> - Default with override (offered only because placement in `## Rules` indicates some binding preference is intended): "Place packages not consumed by the public API under `internal/` unless [author-named override condition]." The author must supply the condition.
>
> **6. R1 Distinguishability**
> Location: line 34 (`## Working with money`).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a marked, mandatory rule sits inside a paragraph of type-semantics facts (struct layout, `fx.Convert`, rounding); the document has a `## Rules` section and the rule is liftable.
> Severity: minor.
> Suggested rewrite: move the sentence unchanged into `## Rules`. The surrounding facts stay in `## Working with money`.
>
> **7. R1 Distinguishability**
> Location: line 42 (`## Testing`).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: the frame "It is worth noting that" presents a binding requirement as an aside, mid-paragraph among descriptive facts about suite timing and contributor habits; placement and framing both signal nonbinding color. Liftable.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any test touching the `postings` package must run inside a transaction that is rolled back at the end." Keep in `## Testing` as a fact: "The shared fixture set is not regenerated between tests."
>
> **8. R1 Distinguishability**
> Location: line 49 (`## Observability`).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a marked, mandatory rule embedded in a paragraph of tracing and logging facts; liftable.
> Severity: minor.
> Suggested rewrite: add to `## Rules`: "Log lines must never include the raw `account_number` field." Keep in `## Observability`: "The log pipeline is replicated to a lower-trust analytics store."
>
> **9. R1 Distinguishability**
> Location: line 62 (`## Appendix: common tasks`).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a mandatory pre-condition on a task is introduced with "By the way" inside an appendix of how-to one-liners; the frame and location present it as an afterthought rather than a gate. Liftable. (The trigger is decidable and the evidence — a tagged issue and a recorded sign-off — is observable, so R3 is not cited.)
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Before adding a currency, open an issue tagged `finance-review` and obtain sign-off from the finance team." Keep the rationale in the appendix or context: "Unsupported currencies leak into customer invoices." The appendix line for adding a currency may point to the rule.
>
> **10. R1 Distinguishability**
> Location: line 63 (`## Appendix: common tasks`).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: a marked prohibition is embedded in a list of procedural task tips; a reader consulting the appendix for how-to steps is not signaled that the second clause is policy. Liftable.
> Severity: minor.
> Suggested rewrite: add to `## Rules`: "Never run a direct SQL update against `postings`; use `cmd/backfill` for backfills." Appendix line becomes "Backfilling: `cmd/backfill`."
>
> **Not flagged (false-positive guards):**
> - Lines 18, 21, 60, 61: imperative but procedural — they tell a reader already committed to bootstrapping, or to adding a currency, how to carry it out; no policy is violated by ignoring them.
> - Lines 14 and 41 ("Most contributors find...", "most contributors run them only before pushing"): descriptive observations that inform rather than direct; classified as discretionary context, not hedged rules.
> - Line 35 (`Money` has no mixed-currency `Add`; conversion goes through `fx.Convert`): a load-bearing fact about type semantics, enforced by the type itself; a rule that cannot fail is context.
> - Line 56 (legacy runbook "is not current policy"): the document explicitly demotes this; correctly placed.
> - Line 25 ("Never commit directly to `main`"): clean — marked, mandatory, checkable against repository state.
> - R4: line 62 bundles issue-opening and sign-off, but both share one trigger and sign-off depends on the issue; permitted as one unit.
> - R5: no two rules prescribe incompatible outcomes on a realistic input (e.g. "never commit to `main`" and "deploys are cut from `main`" govern different decisions).
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 0, R5 0.
> Counts per severity: material 5 (findings 1, 3, 5, 7, 9), minor 5 (findings 2, 4, 6, 8, 10).
> No finding carries a secondary rule id, so the per-rule total of ten equals the ten findings counted by severity.
>
> The document holds eleven binding rules but places only five of them in `## Rules`, and four of those five carry defects: two are padded with rationale, one ("readable") is untestable, and one ("Generally") has ambiguous strength. The six rules outside the section are all mandatory in wording, but three are disguised by their framing ("Because...", "It is worth noting that", "By the way") and location in overview, testing narrative, and a how-to appendix — these are the ones most likely to be missed by an agent that reads `## Rules` as the rule inventory. The remaining three embedded rules are clearly marked in their own sentences and owe only a move. Findings 3 and 5 require author decisions before a semantic-preserving rewrite is possible; the other eight can be applied mechanically. The document's facts (money representation, log parsing, release schedule) and its explicit demotion of the legacy runbook are correctly handled and need no change.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
