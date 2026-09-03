# Scenario 10 — ledger-service, With-Skill, three reps plus the E9 control (wave 3)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, independent dispatches
Prompt: the scenario-10 prompt from `../scenarios.md`, verbatim, preceded by one line: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under `../wave3-2026-08-07/preregistration.md` (planted lists, E2 exclusion registry, E7 lists, E9 fields); tool calls extracted by script
Notes: every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

```
Date: 2026-09-01
Run: control
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, independent dispatches
Prompt: the scenario-10 prompt from `../scenarios.md`, verbatim, preceded by one line: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only." and with the request line changed to "… and report your findings, and give me the rewritten document:"
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under `../wave3-2026-08-07/preregistration.md` (planted lists, E2 exclusion registry, E7 lists, E9 fields); tool calls extracted by script
Notes: the E9 known positive for scenario 10; one arm; E9b = requested by construction; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

### E1 — recall (of 11)

| Planted | rep 1 | rep 2 | rep 3 | control |
| --- | --- | --- | --- | --- |
| D10.1 | ✓ F1 material | ✓ 1 material | ✓ 1 material | ✓ 1 material |
| D10.2 | ✓ F2 material | ✓ 7 material | ✓ 7 material | ✓ 7 material |
| D10.3 | ✓ F3 material (+R4) | ✓ 9 material | ✓ 9 material (+R4) | ✓ 9 material |
| D10.4 | ✓ F10 R3 material | ✓ 3 R3 material | ✓ 3 R3 material | ✓ 3 R3 material |
| D10.5 | ✓ F9 R2 material | ✓ 5 R2 material | ✓ 5 R2 material | ✓ 5 R2 material |
| D10.6 | ✓ F7 minor | ✓ 2 minor | ✓ 2 minor | ✓ 2 minor |
| D10.7 | ✓ F8 minor | ✓ 4 minor | ✓ 4 minor | ✓ 4 minor |
| D10.8 | ✓ F6 minor | ✓ 10 minor | ✓ 10 minor | ✓ 10 minor |
| D10.9 | ✓ F5 minor | ✓ 8 minor | ✓ 8 minor | ✓ 8 minor |
| D10.10 | ✓ F4 minor | ✓ 6 minor | ✓ 6 minor | ✓ 6 minor |
| D10.11 | ✗ — explicitly left alone as procedure ("Line 61's 'together' shares one trigger … treated as procedural walkthrough") | ✗ — same | ✗ — same | ✗ — same |
| **Total** | **10/11** | **10/11** | **10/11** | **10/11** |

**D10.11 for the preregistration.** Seven of seven arms today (three baselines, three with-skill, the control) classify "Adding a currency: update `fx/currencies.go` and the `currency_code` enum migration together." as a procedural how-to, and three of the with-skill arms say so in their false-positive guards. The B1 table plants it on the ground that "together" forecloses updating one file alone. No reader applied that reading. This is recorded as an adjudication question about the B1 verdict on that row, not as a recall miss the ruleset should be tuned to.

### E2 — false positives

0, 0, 0 (and 0 on the control). Every protected probe the preregistration names — the two how-tos, the port-5432 remedy, the legacy-runbook sentence, the `Money` facts, "most contributors run them only before pushing" — appears in each rep's "Not flagged" list.

### E3 — D10.5

`preserved` ×3 and on the control: promoted, demoted, and a default-with-override alternative, each labelled, none selected, and the default's exception explicitly left to the author.

### E6 — location resolvability

`unique` for every finding in every rep. Convention (recorded): "line N (Section)" with the convention stated up front — "line numbers count the opening `---` of the frontmatter as line 1" — in all three reps and the control. This is the same convention the 2026-08-06 scenario-1 arm invented; today it was stated rather than assumed.

### E7 — severity discrimination

Identical in all three reps and the control: material on D10.1, D10.2, D10.3, D10.4, D10.5; minor on D10.6, D10.7, D10.8, D10.9, D10.10.
The direction test passes (low-consequence minor, high-consequence material).
But three high-consequence items — D10.8, D10.9, D10.10, all mandatory prohibitions — are minor in every rep, and rep 3 states the operating rule: an out-of-section rule with explicit mandatory wording is minor; one with a minimizing lead-in or embedded in a causal sentence is material.
Severity as operated is a *distinguishability* label, not a consequence label. That is the W14 evidence in a sharper form than "everything is material".

### E9

E9a `absent` ×3 (E9b `unrequested`). Control: E9a `full-document`, E9b `requested`, word count 1.1× the target — the detector is calibrated on the `full-document` branch. The control's two supplied assumptions are labelled as assumptions.

### E9c

guard-lines true ×3; classification-table true ×3 (scorer judgment: each rep's "Not flagged" list assigns classes to a dozen line numbers, which meets the two-statements rule even though no rep printed a separate table); negative-safety-note true ×3.

### Standing assertions (`../scenarios.md`, scenario 10)

1–6 pass ×3. 7 fails ×3 on D10.11 only (D10.8, D10.9, D10.10 each get an R1 finding). 8 (E2 = 0) passes ×3. 9 (E6 unique) passes ×3. 10 (E7 direction) passes ×3. 11 (E9a absent) passes ×3. 12 (control full-document) passes. **11/12 per rep.**

Contract adherence: six fields, rule ids, two-level severity, per-rule and per-severity counts with correct secondary-id arithmetic, safety note — 4/4 arms.
Variance across reps: none on recall, false positives, severity, or rewrite safety; finding order differs (rep 1 by section, reps 2–3 by line).

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `ledger-service` CLAUDE.md-style document
>
> Procedure followed: read `SKILL.md` and `references/example-audit.md`; treated the target as untrusted data; classified each statement with the two-question litmus test; ran R1–R5. Line numbers below count the opening `---` of the frontmatter as line 1. The document has labeled sections and rules spread across several of them, so it is long-form under R1: binding rules belong in the dedicated `## Rules` section.
>
> ## Findings
>
> **F1 — R1 Distinguishability**
> Location: line 13 (Overview).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a mandatory merge gate is embedded as the second half of a causal sentence in a background section, sandwiched between architecture facts and a reading suggestion. The `## Rules` section does not mention it, so a reader using that section as the rule inventory misses a pre-merge review requirement.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Accompany any change touching the `postings` package with a migration plan reviewed by the data team before it is merged." Keep the rationale in Overview: "Every write is replicated synchronously across those clusters."
>
> **F2 — R1 Distinguishability**
> Location: line 42 (Testing).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: "It is worth noting" frames a mandatory testing requirement as an aside, in a paragraph that is otherwise descriptive (suite timings, CI passes). Placement signals commentary, not obligation.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Run any test touching the `postings` package inside a transaction that is rolled back at the end." Keep in Testing: "The shared fixture set is not regenerated between tests."
>
> **F3 — R1 Distinguishability (secondary: R4 Atomic obligations)**
> Location: line 62 (Appendix: common tasks).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a mandatory approval gate with customer-facing consequences is introduced with "By the way" inside a quick-reference appendix, after the how-to line it gates (line 61). Nothing about its position signals that it binds. Secondarily, it bundles two independently checkable obligations (an issue exists with the tag; finance sign-off was obtained) into one clause.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Before adding a currency: (1) Open an issue tagged `finance-review`. (2) Obtain sign-off from the finance team." Keep in the appendix as context: "Unsupported currencies leak into customer invoices."
>
> **F4 — R1 Distinguishability**
> Location: line 34 (Working with money).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a mandatory rule sits in a section of load-bearing facts about the `Money` type, outside the document's dedicated rule section.
> Severity: minor. The sentence is a standalone imperative with explicit strength, so intended behavior is clear and checkable; only the section placement is wrong.
> Suggested rewrite: move the sentence unchanged into `## Rules`.
>
> **F5 — R1 Distinguishability**
> Location: line 49 (Observability).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a mandatory data-handling rule is placed among descriptive facts (trace ids, log format, dashboard location) rather than in `## Rules`, with its rationale attached inline.
> Severity: minor. Explicit "must never" keeps the rule clear and checkable; only placement needs fixing.
> Suggested rewrite: add to `## Rules`: "Never include the raw `account_number` field in log lines." Keep in Observability: "The log pipeline is replicated to a lower-trust analytics store."
>
> **F6 — R1 Distinguishability**
> Location: line 63 (Appendix: common tasks).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: a prohibition on direct writes to the core table is formatted as a how-to entry in the appendix, not as a rule.
> Severity: minor. "never" makes the strength explicit and the rule is checkable against the change; only placement needs fixing.
> Suggested rewrite: add to `## Rules`: "Use `cmd/backfill` for backfills; never run a direct SQL update against `postings`." Keep the appendix entry as "Backfilling: `cmd/backfill`."
>
> **F7 — R1 Distinguishability**
> Location: line 26 (Rules).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule is padded with a fact (same suite as CI) and rationale (queue time, shared runners) inside the rule section.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Run `make test` before opening a pull request." Move to Testing: "`make test` runs the same suite CI runs; catching failures locally saves a round trip through the queue and keeps the shared runners free."
>
> **F8 — R1 Distinguishability**
> Location: line 28 (Rules).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: the rule carries two rationale clauses inside the rule section. "Prefer" is an explicit default, so strength is not at issue.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Prefer table-driven tests." Move to Testing: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **F9 — R2 Explicit strength**
> Location: line 29 (Rules).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" leaves the reader unable to tell whether placing a non-public package outside `internal/` violates the rule or is an acceptable deviation.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted (mandatory): "Place any package not consumed by the public API under `internal/`."
> Demoted (context, outside `## Rules`): "Packages not consumed by the public API are typically placed under `internal/`; this document does not require it."
> Default with override (offered because the statement's presence in `## Rules` indicates some binding preference is intended): "Place packages not consumed by the public API under `internal/` unless [author names the exception]." The override condition must come from the author.
>
> **F10 — R3 Verifiability**
> Location: line 27 (Rules).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence; no output, diff, or artifact can show the rule was followed or violated.
> Severity: material.
> Suggested rewrite: author decision, because the statement does not reveal the intended safeguard.
> If a format is intended: state its checkable properties (for example entry length, tense, required elements) — the audit does not choose them.
> If it is only guidance: remove from `## Rules` and state as context: "Changelog entries are read by humans; this document defines no format requirement."
>
> ## Not flagged (false-positive guards)
>
> - Lines 10–12, 14, 33, 35–36, 40–41, 43, 47–48, 50, 54–56: load-bearing facts or discretionary context, correctly outside `## Rules`. Line 36 ("Rounding is banker's rounding throughout") and line 35 (no mixed-currency `Add`; `fx.Convert` requires an explicit rate source) are descriptive tool semantics; they were not promoted to rules because the audit does not silently strengthen policy. Line 41 ("most contributors run them only before pushing") and line 14 (architecture doc) describe practice rather than direct it.
> - Line 56: the legacy runbook sentence explicitly demotes itself ("is not current policy"); this is context handled well.
> - Lines 18, 21, 60–61: setup and how-to steps stated as imperatives inside sections whose headings name them as procedures. Line 61's "together" shares one trigger (adding a currency) and stays a single unit under R4. These were treated as procedural walkthrough, not policy rules; the author may reasonably disagree for line 21.
> - Line 25 ("Never commit directly to `main`") and line 54 (deploys are cut from `main`): no conflict — one is a rule, the other a fact about the release job.
> - R5: no reachable conflicts found. Line 26 (`make test` before a PR) versus line 41 (integration tests before pushing) does not conflict because line 41 is descriptive, not a rule.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 1 (secondary, on F3), R5 0. Per-rule total 11.
> Counts per severity: material 5 (F1, F2, F3, F9, F10), minor 5 (F4, F5, F6, F7, F8). Total findings 10. The per-rule total exceeds the finding count by one because F3 carries a secondary R4 id.
>
> The document has a `## Rules` section, but it holds only five of the roughly eleven binding statements; the other six are distributed across Overview, Working with money, Testing, Observability, and the appendix. Three of those (the `postings` migration-plan gate, the rolled-back-transaction requirement, and the `finance-review` sign-off) are wrapped in narrative framing ("Because...", "It is worth noting", "By the way") that makes them read as commentary, and they are the highest-consequence rules in the file. The three others are explicit imperatives that only need relocating. Inside `## Rules`, two entries carry rationale that belongs in the descriptive sections, one hedges its strength with "Generally", and one ("readable") cannot be verified. No precedence conflicts exist. F9 and F10 require author decisions before a rewrite can claim to preserve intended behavior; the remaining eight are mechanical moves and trims.

### With-skill, rep 2

> I have everything the skill requires (SKILL.md and its one referenced file, `references/example-audit.md`). Here is the audit.
>
> # Audit: `ledger-service` repository instructions
>
> Line numbers count from the opening `---` of the frontmatter as line 1. The document has labeled sections and a dedicated `## Rules` section, so it is treated as long-form under R1: binding rules belong in `## Rules`, and `## Rules` should hold only rules.
>
> ## Findings
>
> **1. R1 Distinguishability**
> Location: line 13 (`## Overview`).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: this is a mandatory merge gate, but it sits mid-paragraph in the Overview between architecture facts and a navigation tip, led by a "Because..." rationale clause. A reader who consults `## Rules` as the rule set will not find it; its placement signals background, not obligation.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any change touching the `postings` package must include a migration plan reviewed by the data team before it is merged." Leave the rationale in the Overview: "Every write is replicated synchronously across the three clusters, which is why `postings` changes require a reviewed migration plan (see Rules)."
>
> **2. R1 Distinguishability**
> Location: line 26 (`## Rules`).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule itself is clear, but the clause after the dash is discretionary rationale living inside the rule section. It lengthens the rule without adding an obligation.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Run `make test` before opening a pull request." Move the rationale to `## Testing`: "`make test` runs the same suite CI runs; catching failures locally saves a round trip through the queue and keeps the shared runners free."
>
> **3. R3 Verifiability**
> Location: line 27 (`## Rules`).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence — no length, format, tense, or content requirement — so neither the agent nor a reviewer can determine whether an entry complies.
> Severity: material.
> Suggested rewrite: this is an author decision because the statement does not reveal the intended safeguard.
> If a format is intended, state it in checkable terms, e.g. "Each changelog entry is a single sentence in the imperative mood that names the affected package" (the specific shape must come from the author; this is only the required form of the rule).
> If an existing style reference is intended, cite it: "Changelog entries follow the format in `<file>`."
> If it is only guidance with no enforceable requirement, remove it from `## Rules` and state as context: "Changelog entries are read by release and support staff; this document defines no format requirement."
>
> **4. R1 Distinguishability**
> Location: line 28 (`## Rules`).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: "Prefer table-driven tests" is a legitimate default (R2 is satisfied), but the two "which..." clauses are rationale and precedent — discretionary context inside the rule section.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Prefer table-driven tests." Move the rest to `## Testing`: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **5. R2 Explicit strength**
> Location: line 29 (`## Rules`).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" hedges the statement so that a reader cannot tell whether placing a non-public package outside `internal/` violates the rule or is an allowed judgment call. It is listed under `## Rules`, which signals that something binding is intended, but the wording does not say what.
> Severity: material.
> Suggested rewrite: author decision among three non-hedged readings.
> Promoted (mandatory): "Place every package not consumed by the public API under `internal/`."
> Default with override (the target's placement in `## Rules` suggests a binding preference is intended; the author must supply the exception): "Place packages not consumed by the public API under `internal/` unless <author-specified condition>."
> Demoted (context): remove from `## Rules` and state in the Overview: "Packages not consumed by the public API conventionally live under `internal/`; this document does not require it."
>
> **6. R1 Distinguishability**
> Location: line 34 (`## Working with money`).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a mandatory rule placed in a topical section between two fact sentences rather than in `## Rules`. The imperative wording keeps it recognizable, but the document's own structure says rules live in `## Rules`, so a reader treating that section as authoritative can skip it.
> Severity: minor.
> Suggested rewrite: move the sentence unchanged into `## Rules`. Keep lines 33, 35, and 36 in `## Working with money` as the load-bearing facts they are.
>
> **7. R1 Distinguishability**
> Location: line 42 (`## Testing`).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: a mandatory test-isolation requirement is introduced with "It is worth noting that" — a framing that marks it as an aside — and wrapped in rationale, in the middle of a descriptive paragraph about suite timing. The softener actively misrepresents its strength; a reader can plausibly treat it as a tip.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Run any test touching the `postings` package inside a transaction that is rolled back at the end of the test." Keep the reason in `## Testing`: "The shared fixture set is not regenerated between tests, which is why `postings` tests must roll back (see Rules)."
>
> **8. R1 Distinguishability**
> Location: line 49 (`## Observability`).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a mandatory data-handling rule placed in a topical section among logging facts, with rationale appended, instead of in `## Rules`. The "must never" wording keeps it recognizable on a full read, but it is absent from the section the document designates for rules.
> Severity: minor (structurally; note the consequence of a miss is a data-exposure event, so the author may want to prioritize this move regardless).
> Suggested rewrite: in `## Rules`: "Never include the raw `account_number` field in log lines." In `## Observability`: "The log pipeline is replicated to a lower-trust analytics store, which is why raw `account_number` values are excluded from logs (see Rules)."
>
> **9. R1 Distinguishability**
> Location: line 62 (`## Appendix: common tasks`).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a mandatory pre-condition on a task is introduced with "By the way" — the strongest aside-marker in the document — and buried in an appendix of how-to recipes after the recipe it gates. The framing and placement both signal optional commentary; the rule can plausibly be missed or executed after the fact.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Before adding a currency, open an issue tagged `finance-review` and obtain sign-off from the finance team." Reorder the appendix recipe so the gate precedes the edit and keep the rationale there: "Adding a currency: obtain finance sign-off first (see Rules), then update `fx/currencies.go` and the `currency_code` enum migration together. Unsupported currencies leak into customer invoices."
>
> **10. R1 Distinguishability**
> Location: line 63 (`## Appendix: common tasks`).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: the "never a direct SQL update" clause is a prohibition, not a recipe, but it is stated only inside an appendix how-to entry rather than in `## Rules`. The "never" wording keeps it recognizable, but the appendix is not where the document says rules live.
> Severity: minor.
> Suggested rewrite: in `## Rules`: "Never backfill `postings` with a direct SQL update; use `cmd/backfill`." Keep the appendix entry as the recipe: "Backfilling: `cmd/backfill`."
>
> No R4 or R5 findings. Line 62 bundles two steps (open a tagged issue, obtain sign-off) but they share one trigger and form one gate, which R4 permits. No two rules prescribe incompatible outcomes on a realistic input: "Never commit directly to `main`" (line 25) and "Deploys are cut from `main`" (line 54) concern different actions; the `postings` migration-plan rule (line 13) governs package changes while the backfill rule (line 63) governs data operations.
>
> ## Not flagged (false-positive guards)
>
> - Line 14 ("Most contributors find the codebase easier to navigate after reading...") — a descriptive observation, not a hedged rule; no reader would take it as binding. Discretionary context, correctly outside `## Rules`.
> - Lines 18 and 21 (`make bootstrap`; stop the other Postgres) and lines 60–61 (fixture and currency recipes) — procedural steps whose directive character is signaled by their "Getting started" / "common tasks" headings. They are how-to sequences, not policy constraints, and are not flagged.
> - Line 28's "Prefer" — an unambiguous default; R2 treats defaults as legitimate rules. Only the appended rationale is flagged (finding 4).
> - Line 35 (`fx.Convert` requires an explicit rate source) and lines 33, 36, 40, 43, 47, 48, 50, 54, 55 — load-bearing facts about tool and process semantics, correctly placed outside `## Rules`.
> - Line 41 ("most contributors run them only before pushing") — descriptive context; not a rule.
> - Line 56 (legacy runbook "is retained for incident archaeology and is not current policy") — explicitly marked nonbinding. This is the pattern the demoted rewrites above follow.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 0, R5 0.
> Counts per severity: material 5 (R1 lines 13, 42, 62; R2 line 29; R3 line 27), minor 5 (R1 lines 26, 28, 34, 49, 63).
> No finding carries a secondary rule id, so the per-rule total of ten equals the ten findings counted by severity.
>
> The document has a well-formed `## Rules` section but uses it for only five of its eleven binding rules; the other six are distributed across Overview, Working with money, Testing, Observability, and the Appendix. Three of those six are actively disguised by aside-markers ("Because...", "It is worth noting", "By the way") and are the material R1 findings; the other three are crisp imperatives that survive a full read but are missing from the designated rule list. Inside `## Rules`, two entries carry rationale that belongs in the topical sections, one entry is unverifiable ("readable"), and one is hedged ("Generally") so that its strength cannot be determined. The facts about `Money`, the test suites, logging, and deployment are correctly placed as context, and the legacy-runbook note is a good model of explicit nonbinding marking. The R2 and R3 findings require author decisions before a rewrite can claim to preserve intended behavior; the eight R1 findings are mechanical moves that preserve semantics as written.

### With-skill, rep 3

> # Audit: `ledger-service` CLAUDE.md-style document
>
> Line numbers count from the opening `---` of the fenced document as line 1. The document is long-form (labeled sections, rules spread across several sections), so R1 requires binding rules to live in a dedicated labeled section; it has a `## Rules` section, which raises the cost of every rule placed elsewhere because a reader can reasonably treat that section as exhaustive.
>
> Severity line I applied for out-of-section rules: a standalone sentence with explicit mandatory wording ("Never", "must never") is distinguishable inline and rated **minor**; a rule with a minimizing lead-in ("It is worth noting", "By the way") or embedded in a causal/narrative sentence is not distinguishable and rated **material**.
>
> ## Findings
>
> **1. R1 Distinguishability**
> Location: line 13 (`## Overview`).
> Quoted text: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a mandatory merge gate is stated as the consequence clause of a rationale sentence, in the middle of a descriptive overview paragraph, four sections away from `## Rules`. Nothing in its placement signals that it binds; it reads as architecture commentary.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged." Keep the rationale in Overview: "Every write is replicated synchronously across the three clusters, which is why `postings` changes require a reviewed migration plan (see Rules)."
>
> **2. R1 Distinguishability**
> Location: line 26 (`## Rules`).
> Quoted text: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule is clear, but the trailing clause is discretionary rationale inside the rule section.
> Severity: minor.
> Suggested rewrite: rule item becomes "Run `make test` before opening a pull request." Move the remainder to `## Testing`: "`make test` is the same suite CI runs; running it locally saves a round trip through the queue and keeps the shared runners free."
>
> **3. R3 Verifiability**
> Location: line 27 (`## Rules`).
> Quoted text: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable criterion; no output or artifact can show the rule was followed or violated, and the statement does not reveal the intended safeguard.
> Severity: material.
> Suggested rewrite: author decision.
> If a format is intended: name it, e.g. "Each changelog entry is a single sentence stating the user-visible change, placed under the current unreleased heading" (illustrative; the author supplies the actual criteria).
> If it is only aspiration: remove it from `## Rules` and state as context: "Changelog entries are written for readers of release notes; this document defines no format requirement."
>
> **4. R1 Distinguishability**
> Location: line 28 (`## Rules`).
> Quoted text: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: "Prefer" is an unambiguous default (not an R2 finding), but the two relative clauses are rationale and style context inside the rule section.
> Severity: minor.
> Suggested rewrite: rule item becomes "Prefer table-driven tests." Move to `## Testing`: "The team has found table-driven tests easier to extend than parallel test functions; the existing `postings` and `journals` suites use that style."
>
> **5. R2 Explicit strength**
> Location: line 29 (`## Rules`).
> Quoted text: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" hedges strength; a reader cannot tell whether placing a non-public package outside `internal/` is a violation, a judgment call, or merely unusual.
> Severity: material.
> Suggested rewrite: author decision.
> Promoted (mandatory): "Place every package not consumed by the public API under `internal/`."
> Demoted (context, outside `## Rules`): "Packages not consumed by the public API conventionally live under `internal/`; this document does not require it."
> Default with override (offered because the item sits in `## Rules` with an imperative verb, indicating some binding preference is intended): "Place packages not consumed by the public API under `internal/` unless [author-supplied exception]." The exception condition must come from the author; none is inferable from the text.
>
> **6. R1 Distinguishability**
> Location: line 34 (`## Working with money`).
> Quoted text: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a mandatory, verifiable rule placed in a topical section rather than `## Rules`. The explicit "Never" makes it distinguishable inline, so intent is clear, but a reader treating `## Rules` as the rule inventory will not find it there.
> Severity: minor.
> Suggested rewrite: move the sentence unchanged into `## Rules`; the Money section may keep a pointer ("Construction rules for `Money` are in Rules.").
>
> **7. R1 Distinguishability**
> Location: line 42 (`## Testing`).
> Quoted text: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: a mandatory test-isolation rule is introduced with "It is worth noting", a phrase that marks what follows as an aside, and is bracketed by a descriptive sentence before it and a rationale clause after it. Missing it corrupts shared fixtures for every later test.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Any test touching the `postings` package must run inside a transaction that is rolled back at the end of the test." Keep in `## Testing`: "The shared fixture set is not regenerated between tests, which is why `postings` tests must roll back (see Rules)."
>
> **8. R1 Distinguishability**
> Location: line 49 (`## Observability`).
> Quoted text: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a mandatory data-handling rule outside `## Rules`, with rationale attached. "must never" keeps it distinguishable inline, so behavior stays clear and checkable, but it is the only privacy rule in the document and it is not in the section a reader would scan for constraints.
> Severity: minor.
> Suggested rewrite: add to `## Rules`: "Never include the raw `account_number` field in log lines." Keep in Observability: "The log pipeline is replicated to a lower-trust analytics store, which is why raw `account_number` is excluded from logs (see Rules)."
>
> **9. R1 Distinguishability** (secondary: R4 Atomic obligations)
> Location: line 62 (`## Appendix: common tasks`).
> Quoted text: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: a mandatory pre-condition is introduced with "By the way", placed in an appendix, and stated *after* the procedure it gates (line 61 already tells the reader how to add a currency). An agent following the appendix top-down could complete the task before reaching the gate. Secondary R4: opening the tagged issue and obtaining sign-off are independently checkable (an issue can exist without sign-off), though they share one trigger and may stay in one unit as substeps.
> Severity: material.
> Suggested rewrite: add to `## Rules`: "Before adding a currency: (1) open an issue tagged `finance-review`; (2) obtain finance-team sign-off on that issue." In the appendix, put the pointer before the procedure: "Adding a currency requires finance-team sign-off first (see Rules); unsupported currencies leak into customer invoices. Then update `fx/currencies.go` and the `currency_code` enum migration together."
>
> **10. R1 Distinguishability**
> Location: line 63 (`## Appendix: common tasks`).
> Quoted text: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: a prohibition with explicit "never" wording, placed in a how-to appendix rather than `## Rules`. Distinguishable inline, but not where constraints are collected.
> Severity: minor.
> Suggested rewrite: add to `## Rules`: "Never backfill `postings` with a direct SQL update; use `cmd/backfill`." Appendix keeps "Backfilling: `cmd/backfill`."
>
> ## Not flagged (false-positive guards)
>
> - Lines 10–12, 19–20, 33, 35–36, 40, 43, 47–48, 50, 54–55: load-bearing facts or discretionary context correctly placed outside `## Rules`. Line 36 ("Rounding is banker's rounding throughout") is descriptive of a codebase invariant, a domain fact, not a directive; I did not treat it as a hidden rule.
> - Line 14 ("Most contributors find the codebase easier to navigate after reading...") and line 41 ("most contributors run them only before pushing"): observations about practice, not directives, so not R2 hedges.
> - Lines 18, 21, 60, 61: setup and task procedures in sections whose titles signal procedure. I treated these as the task itself rather than policy constraints; the one policy attached to a procedure (line 62) is flagged above.
> - Line 25: clean mandatory, verifiable rule.
> - Line 56: explicitly de-binds the legacy runbook ("is not current policy"), which is the right way to keep a legacy reference as context.
> - R5: no reachable conflicts. Line 25 versus line 54 (release job cuts from `main`) is compatible; line 26 versus line 41 is a rule versus a description, not two rules; line 13 (package changes) versus line 63 (data backfills) govern different decisions.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 1 (secondary on finding 9), R5 0. Per-rule total 11.
> Counts per severity: material 5 (findings 1, 3, 5, 7, 9), minor 5 (findings 2, 4, 6, 8, 10). Total findings 10.
>
> The document has a `## Rules` section but only five of its roughly eleven binding rules live there, and two of the five it does contain are padded with rationale. The three most consequential rules in the file, the `postings` migration-plan gate, the `postings` test rollback requirement, and the finance-review gate on new currencies, are all outside the section and each is framed in a way that downplays it ("Because...", "It is worth noting", "By the way"); these are the material R1 findings. Within the section, one rule is unverifiable ("readable") and one is hedged ("Generally"), both needing author decisions. Three further mandatory rules (`Money` float literals, `account_number` in logs, SQL backfills) are clearly worded but scattered across topical sections; consolidating them into `## Rules` with pointers left behind would make the section a trustworthy inventory. No precedence conflicts exist, and the surrounding facts and background are largely well placed.

### E9 control (rewrite requested)

> ## Audit: `ledger-service` (CLAUDE.md-style repository instructions)
>
> Skill and its one referenced file (`references/example-audit.md`) read; nothing else read, nothing edited. Line numbers count the first `---` of the fenced block as line 1. The document is long-form (labeled sections, rules spread across several sections), so R1 expects binding rules in the dedicated `## Rules` section.
>
> ### Findings
>
> **1. R1 Distinguishability — material**
> Location: line 13 (Overview).
> Quoted: "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
> Why it fails: a mandatory merge gate is buried mid-paragraph in the Overview, between a deployment fact and a navigation tip, and the sentence leads with rationale. A reader scanning `## Rules` for obligations misses it.
> Rewrite: add to `## Rules`: "Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged." Keep the replication fact in Overview as context.
>
> **2. R1 Distinguishability — minor**
> Location: line 26 (Rules).
> Quoted: "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
> Why it fails: the rule is clear, but two-thirds of the item is discretionary rationale inside the rule section.
> Rewrite: rule item becomes "Run `make test` before opening a pull request." Move the rationale to `## Testing`.
>
> **3. R3 Verifiability — material**
> Location: line 27 (Rules).
> Quoted: "Keep the changelog entries readable."
> Why it fails: "readable" names no observable evidence; no output, diff, or artifact can show the rule was followed or broken, and the statement does not reveal the intended safeguard.
> Rewrite: author decision.
> - If a standard is intended: state the checkable form (a template, a length limit, a required structure, or a linter) — e.g. "Each changelog entry is a single sentence naming the user-visible change." The auditor cannot pick the standard.
> - If it is only a value statement: remove it from `## Rules` and state as context "Changelog readability is valued; this document defines no checkable requirement for entries."
>
> **4. R1 Distinguishability — minor**
> Location: line 28 (Rules).
> Quoted: "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
> Why it fails: "Prefer" is an unambiguous default (not an R2 finding), but the item carries two clauses of rationale inside the rule section.
> Rewrite: rule item becomes "Prefer table-driven tests." Move the rationale to `## Testing`.
>
> **5. R2 Explicit strength — material**
> Location: line 29 (Rules).
> Quoted: "Generally use the `internal/` package for anything not consumed by the public API."
> Why it fails: "Generally" leaves the reader unable to tell whether a public-API-free package placed outside `internal/` violates the document.
> Rewrite: author decision.
> - Promoted (mandatory): "Place any package not consumed by the public API under `internal/`."
> - Default with override (the target's "Generally" suggests a preference with unstated exceptions): "Place packages not consumed by the public API under `internal/` unless [author names the exception]."
> - Demoted (context, outside Rules): "Packages not consumed by the public API conventionally live under `internal/`; this document does not require it."
>
> **6. R1 Distinguishability — minor**
> Location: line 34 (Working with money).
> Quoted: "Never construct a `Money` value from a floating-point literal."
> Why it fails: a binding rule sits between two semantic facts in a topical section rather than in `## Rules`. The "Never" wording keeps it distinguishable inline, so behavior is clear; only placement is at fault.
> Rewrite: move the sentence unchanged into `## Rules`.
>
> **7. R1 Distinguishability — material**
> Location: line 42 (Testing).
> Quoted: "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
> Why it fails: "It is worth noting" frames a mandatory test requirement as an aside, in a paragraph otherwise describing suite timing and contributor habits, with rationale appended. It reads as commentary and could be missed.
> Rewrite: add to `## Rules`: "Any test touching the `postings` package must run inside a transaction that is rolled back at the end." Keep the fixture fact in `## Testing`.
>
> **8. R1 Distinguishability — minor**
> Location: line 49 (Observability).
> Quoted: "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
> Why it fails: a binding rule with attached rationale sits among descriptive facts outside `## Rules`. "Must never" keeps it distinguishable; placement and padding are the defect.
> Rewrite: add to `## Rules`: "Log lines must never include the raw `account_number` field." Keep the replication fact in `## Observability`.
>
> **9. R1 Distinguishability — material**
> Location: line 62 (Appendix).
> Quoted: "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
> Why it fails: "By the way" explicitly marks a hard approval gate as an afterthought, placed after the how-to it gates and inside an appendix of recipes. An agent following line 61's recipe has already acted before reaching it.
> Rewrite: add to `## Rules`: "Before adding a currency, open an issue tagged `finance-review` and obtain finance-team sign-off on it." Keep the invoice-leak fact as context and have the appendix recipe point at the rule.
>
> **10. R1 Distinguishability — minor**
> Location: line 63 (Appendix).
> Quoted: "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
> Why it fails: a prohibition is stated as one entry in a task-recipe list. "Never" keeps it distinguishable; it belongs in `## Rules`.
> Rewrite: add to `## Rules`: "Backfill with `cmd/backfill`; never run a direct SQL update against `postings`." Appendix entry becomes a pointer.
>
> **Not flagged (false-positive guards)**
> - Lines 18 and 21 (Getting started): setup procedure in a labeled procedural section; imperative and distinguishable, not standing rules.
> - Line 14, line 41: descriptions of what contributors do ("most contributors find…", "most contributors run them only before pushing"), not directives; correctly left out of Rules.
> - Line 56: legacy runbook explicitly labeled "not current policy" — a model of correct demotion.
> - Line 61: a two-file recipe sharing one trigger; procedure, not an R4 bundle.
> - R5: no pair of rules prescribes incompatible outcomes on a realistic input (e.g. "never commit to `main`" vs "deploys are cut from `main`" concern different decisions). No precedence findings.
>
> **Safety note:** none. The document contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 8, R2 1, R3 1, R4 0, R5 0.
> Counts per severity: material 5 (R1 ×3, R2, R3), minor 5 (R1 ×5). No secondary ids, so the per-rule total of 10 equals the 10 findings.
>
> The document's facts are generally well placed and its Deployment section explicitly demotes stale policy, but its `## Rules` section holds only five of the roughly ten binding rules the document actually contains; the other five are scattered across Overview, Working with money, Testing, Observability, and the Appendix, three of them wrapped in aside-markers ("Because…", "It is worth noting", "By the way") that make them read as commentary. Within the rules section, two items are padded with rationale, one is untestable, and one hedges its strength. Findings 3 and 5 need author decisions before a rewrite can claim to preserve intended behavior.
>
> ### Rewritten document
>
> Assumptions supplied for the two author decisions (not inferred by the audit): rule 5 uses the promoted (mandatory) reading of line 29; the changelog statement uses the demoted reading because no checkable standard exists to promote it to. Everything else is a placement change with the original wording preserved.
>
> ```markdown
> ---
> name: ledger-service
> description: Repository instructions for the ledger-service backend.
> ---
>
> # ledger-service
>
> ## Overview
>
> ledger-service is the double-entry accounting core behind the billing platform.
> It was extracted from the monolith during the 2024 platform split, which is why several module names still echo the old `billing_v1` namespace.
> The service is written in Go and deployed to three regional clusters.
> Every write is replicated synchronously across those clusters, which is why changes to the `postings` package require a reviewed migration plan (rule 2).
> Most contributors find the codebase easier to navigate after reading the architecture overview in `docs/architecture.md`.
>
> ## Getting started
>
> Clone the repository and run `make bootstrap`.
> The bootstrap target installs the Go toolchain pinned in `.tool-versions`, provisions a local Postgres instance, and seeds it with the fixtures under `testdata/`.
> Bootstrap takes about four minutes on a warm cache.
> If Postgres is already listening on port 5432 the target fails; stop the other instance first.
>
> ## Rules
>
> 1. Never commit directly to `main`.
> 2. Any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged.
> 3. Run `make test` before opening a pull request.
> 4. Prefer table-driven tests.
> 5. Place any package not consumed by the public API under `internal/`.
> 6. Never construct a `Money` value from a floating-point literal.
> 7. Any test touching the `postings` package must run inside a transaction that is rolled back at the end.
> 8. Log lines must never include the raw `account_number` field.
> 9. Before adding a currency, open an issue tagged `finance-review` and obtain finance-team sign-off on it.
> 10. Backfill with `cmd/backfill`; never run a direct SQL update against `postings`.
>
> ## Working with money
>
> Amounts are represented as `Money` structs holding an integer minor-unit value and an ISO 4217 currency code.
> The `Money` type deliberately has no `Add` method for mixed currencies; conversion goes through `fx.Convert`, which requires an explicit rate source.
> Rounding is banker's rounding throughout, matching the ledger's original COBOL implementation.
> Unsupported currencies leak into customer invoices, which is why adding a currency requires finance sign-off (rule 9).
>
> ## Testing
>
> The suite is split into unit tests, which run in about twenty seconds, and integration tests behind the `integration` build tag, which need the local Postgres from bootstrap.
> Integration tests are slow enough that most contributors run them only before pushing.
> `make test` is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else (rule 3).
> The team has found table-driven tests easier to extend than parallel test functions, and the existing `postings` and `journals` suites use that style (rule 4).
> The shared fixture set is not regenerated between tests, which is why `postings` tests run inside a rolled-back transaction (rule 7).
> The CI pipeline runs both suites plus a race-detector pass.
>
> ## Changelog
>
> Changelog readability is valued; this document defines no checkable requirement for entries.
>
> ## Observability
>
> Every request carries a trace id propagated through `context.Context`.
> Structured logs go to stdout as JSON; the collector parses them by the `msg` and `level` keys.
> The log pipeline is replicated to a lower-trust analytics store, which is why raw `account_number` is excluded from log lines (rule 8).
> Dashboards live in the `ledger` Grafana folder.
>
> ## Deployment
>
> Deploys are cut from `main` by the release job, which runs every weekday at 10:00 UTC.
> The release job builds a container, runs the smoke suite against staging, and promotes to production only if the smoke suite passes.
> Historically the team deployed by hand, and the runbook in `docs/runbook-legacy.md` still describes that process; it is retained for incident archaeology and is not current policy.
>
> ## Appendix: common tasks
>
> Regenerating fixtures: `make fixtures`.
> Adding a currency: complete the finance-review gate (rule 9), then update `fx/currencies.go` and the `currency_code` enum migration together.
> Backfilling: `cmd/backfill` (rule 10).
> ```
