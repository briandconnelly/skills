# Scenario 10 — ledger-service, Baseline, three reps (wave 3)

```
Date: 2026-09-01
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, independent dispatches
Prompt: the scenario-10 prompt from `../scenarios.md`, verbatim, preceded by one line: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under `../wave3-2026-08-07/preregistration.md` (planted lists, E2 exclusion registry, E7 lists, E9 fields); tool calls extracted by script
Notes: all three arms made zero tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Planted: D10.1–D10.11 (nine high-consequence, D10.6 and D10.7 low-consequence). E2: every unit outside the registry is protected; the `make test` and table-driven bullets are split into planted rationale and protected obligation clauses.

### E1 — recall (of 11)

| Planted | rep 1 | rep 2 | rep 3 |
| --- | --- | --- | --- |
| D10.1 migration plan (Overview) | ✓ M1 | ✓ H1 | ✓ M1 |
| D10.2 rolled-back transaction (Testing) | ✓ M2 | ✓ H2 | ✓ M2 |
| D10.3 finance-review (Appendix) | ✓ M3 | ✓ H3 | ✓ M3 |
| D10.4 "readable" | ✓ M6 | ✓ H4 | ✓ M4 |
| D10.5 "Generally … internal/" | ✓ M7 | ✓ L3 | ✓ M5 |
| D10.6 `make test` rationale | ✓ m1 | ✓ L1 | ✓ m1 |
| D10.7 table-driven rationale | ✓ M7 ("also padded") | ✓ L2 | ✓ M6 |
| D10.8 `cmd/backfill` | ✓ M5 | ✓ L6 | ✓ m5 |
| D10.9 `account_number` | ✓ M4 | ✓ L5 | ✓ M7 |
| D10.10 `Money` float | ✓ m2 | ✓ L4 | ✓ m3 |
| D10.11 currency co-update | ✗ (rewritten inside M3's recipe, not flagged) | ✗ (same) | ✗ (same) |
| **Total** | **10/11** | **10/11** | **10/11** |

### E2 — false positives (protected units criticized)

| Rep | Units | E2 |
| --- | --- | --- |
| 1 | banker's rounding; `fx.Convert` sentence; `msg`/`level` sentence; trace-id sentence (all m3, "if any of these bind, state them as rules"); "most contributors run them only before pushing" (m4); legacy-runbook sentence (m5, proposes an explicit prohibition) | 6 |
| 2 | `fx.Convert` sentence; banker's rounding (L4); `msg`/`level` sentence (L5) | 3 |
| 3 | `fx.Convert` sentence; banker's rounding (m3); `msg`/`level` and trace-id sentences (m4); the unit/integration split sentence (m2, "author input needed") | 5 |

Not counted: rep 1's m6 and rep 3's m6 (port 5432, "no change needed"); rep 2's "out of scope, noted only" tension; rep 3's legacy-runbook note ("already does its job").
No baseline reported the legacy-runbook sentence as an R5 conflict — the specific probe the preregistration names.

### E3 — D10.5

rep 1: assumption-labelled (a single promoted rewrite plus "the author should either name the exceptions … or drop the hedge"). rep 2: assumption-labelled ("I did not strengthen it"; one rewrite, author to supply exceptions). rep 3: preserved (three readings offered, none selected).

### E6, E7, E9

E6: every finding quotes its sentence and names its section; all `unique`. Location-field convention (recorded): section name plus ordinal ("Overview, sentence 4") in rep 1; section name plus quoted text in reps 2 and 3; no line numbers.
E7: D10.6 is minor/low in all three reps; high-consequence items are Major/High in all three; D10.7 is Major (rep 1, folded into the hedge finding), Low (rep 2), Major (rep 3). Discriminates in the preregistered direction, 3/3.
E9a / E9b: rep 1 `partial` (a consolidated `## Rules` section), `unrequested`; rep 2 `absent`; rep 3 `absent`.
E9c: guard-lines true / true / true (each names statements it leaves alone); classification-table false ×3; negative-safety-note false ×3.

Contract adherence: no rule ids, no six-field format, no counts (expected; recorded, not summed).

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `ledger-service` instructions — context vs. constraints
>
> **Top-line finding.** The document has a `## Rules` section, but it holds only 5 of roughly 11 binding rules. The other six live in narrative sections (Overview, Working with money, Testing, Observability, Appendix), several behind minimizing lead-ins ("It is worth noting that", "By the way") or after the step they gate. An agent that reads `## Rules` as the authoritative list will miss the postings migration-plan requirement, the transaction-rollback requirement, the `account_number` logging ban, the finance-review gate, and the backfill prohibition — which are the highest-consequence rules in the file.
>
> Severity levels used: **Major** (a binding rule an agent is likely to miss or misjudge as optional) and **Minor** (clarity/padding; rule is findable but noisier or slightly ambiguous than it should be).
>
> ---
>
> ## Major findings
>
> ### M1. Migration-plan requirement buried in Overview
> **Location:** Overview, sentence 4.
> > Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged.
>
> **Issue:** A hard merge gate placed mid-paragraph in a section whose other four sentences are history and orientation. The rule is subordinated to a "Because…" clause, so it reads as explanation of the architecture rather than a requirement. It is also compound (produce a plan / have the data team review it / before merge).
>
> **Rewrite** (move to Rules; keep the rationale, separated):
> - Any change touching the `postings` package must include a migration plan.
> - The data team must review that migration plan before the change is merged.
>   *Why: writes are replicated synchronously across all three regional clusters.*
>
> ### M2. Transaction-rollback requirement hedged with "It is worth noting"
> **Location:** Testing, sentence 3.
> > It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests.
>
> **Issue:** "It is worth noting that" is a lead-in that signals an aside, not an obligation. The rule sits between two descriptive sentences about suite timing and CI. Violating it corrupts shared fixtures for every subsequent test, so this is a correctness rule, not trivia.
>
> **Rewrite:**
> - Any test touching the `postings` package must run inside a transaction that is rolled back at the end of the test.
>   *Why: the shared fixture set is not regenerated between tests.*
>
> ### M3. Finance-review gate appears after the step it gates, introduced with "By the way"
> **Location:** Appendix, sentences 2–3.
> > Adding a currency: update `fx/currencies.go` and the `currency_code` enum migration together.
> > By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices.
>
> **Issue:** The precondition comes *after* the how-to instruction, in an appendix, prefixed with "By the way" — every signal says "optional footnote." An agent following the appendix in order will edit the files before it reaches the gate. Also compound (open tagged issue / obtain sign-off).
>
> **Rewrite** (gate first, split obligations, move to Rules):
> - Before adding a currency, open an issue tagged `finance-review`.
> - Do not add the currency until the finance team has signed off on that issue.
>   *Why: unsupported currencies leak into customer invoices.*
>
> And in the appendix, reorder so the task entry points back at the gate:
> - Adding a currency (requires finance sign-off — see Rules): update `fx/currencies.go` and the `currency_code` enum migration in the same change.
>
> ### M4. `account_number` logging ban lives in Observability
> **Location:** Observability, sentence 3.
> > Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store.
>
> **Issue:** The wording is strong ("must never"), but it's the only constraint in a section that otherwise describes how tracing, logs, and dashboards work. A data-exposure rule should not depend on the agent reading the Observability section. Rationale is fused to the rule via a dash.
>
> **Rewrite:**
> - Log lines must never include the raw `account_number` field.
>   *Why: the log pipeline is replicated to a lower-trust analytics store.*
>
> ### M5. Backfill prohibition in the Appendix
> **Location:** Appendix, last line.
> > Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`.
>
> **Issue:** A prohibition against direct SQL writes to the core ledger table is filed under "common tasks." It is clearly worded, but the section framing ("here's how to do X") does not signal that the second half is a standing constraint regardless of task.
>
> **Rewrite:**
> - Never run a direct SQL update against `postings`; backfills go through `cmd/backfill`.
>
> (Keep the appendix pointer: "Backfilling: `cmd/backfill`.")
>
> ### M6. Untestable directive: "Keep the changelog entries readable."
> **Location:** Rules, item 3.
>
> **Issue:** No criterion an agent (or reviewer) can check. Every other Rules item is verifiable; this one isn't, and it will be satisfied by whatever the author of the entry already thinks is readable.
>
> **Rewrite:** Not possible without inventing criteria the document doesn't state. The author needs to specify what "readable" means here (e.g., a length bound, a required shape such as "one line per user-visible change," a tense/voice convention, or a link to an example entry). Until then, this rule does no work.
>
> ### M7. Hedged rules in the Rules section — binding status unclear
> **Location:** Rules, items 4 and 5.
> > Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites.
> > Generally use the `internal/` package for anything not consumed by the public API.
>
> **Issue:** "Prefer" and "Generally" leave an agent unable to tell whether a departure is a violation. Sitting in a list alongside "Never commit directly to `main`," the hedges are especially ambiguous: is this a soft default or a rule with unnamed exceptions? Item 4 is also padded — two rationale clauses appended to a one-clause rule.
>
> **Rewrite** (semantic-preserving: keep them as defaults, but make the default explicit and separate the rationale):
> - Write new tests as table-driven tests by default.
>   *Why: easier to extend than parallel test functions; matches the existing `postings` and `journals` suites.*
> - Place code not consumed by the public API under `internal/`.
>
> For both, the author should either name the exceptions "Prefer"/"Generally" are reserving, or drop the hedge if there are none.
>
> ---
>
> ## Minor findings
>
> ### m1. Rule padded with rationale
> **Location:** Rules, item 2.
> > Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else.
>
> The rule is clear; the trailing 30 words are motivation. Split:
> - Run `make test` before opening a pull request.
>   *Why: it's the same suite CI runs; local failures save a queue round-trip and keep shared runners free.*
>
> ### m2. `Money` float prohibition mixed into a descriptive section
> **Location:** Working with money, sentence 2.
> > Never construct a `Money` value from a floating-point literal.
>
> Clearly worded and findable, so not Major — but it is one imperative sandwiched between three descriptive sentences. Move to Rules (or make "Working with money" explicitly a rules subsection).
>
> ### m3. Descriptions that may be constraints — ambiguous binding
> Several sentences describe current behavior in a way that probably also binds new code, but the document doesn't say so:
> - "Rounding is banker's rounding throughout" (Working with money) — is new code required to use banker's rounding, or is this a historical note?
> - "conversion goes through `fx.Convert`, which requires an explicit rate source" — is this "the only sanctioned path" or "how the API happens to work"?
> - "the collector parses them by the `msg` and `level` keys" (Observability) — implies log lines must carry those keys, but doesn't say so.
> - "Every request carries a trace id propagated through `context.Context`" — implies new handlers must propagate it.
>
> If any of these bind, state them as rules ("Use banker's rounding for all monetary rounding," "Every log line must include `msg` and `level`," "Propagate the request trace id through `context.Context` in all new handlers"). If they are purely descriptive, they are fine where they are.
>
> ### m4. "most contributors run them only before pushing"
> **Location:** Testing, sentence 2.
> Describes a norm without saying whether it is expected. Combined with Rules item 2 (`make test` before PR — which suite does `make test` run?), an agent can't tell whether integration tests are required before pushing. Clarify either as context ("you may skip integration tests during iteration") or as a rule ("run the `integration`-tagged suite before pushing").
>
> ### m5. Legacy runbook: implicit prohibition
> **Location:** Deployment, last sentence.
> > …it is retained for incident archaeology and is not current policy.
>
> Adequate as context, but the actionable content is a prohibition. One explicit clause removes the inference: "Do not follow `docs/runbook-legacy.md` for deployments; it is retained only for incident archaeology."
>
> ### m6. Getting started: conditional instruction inside procedure
> > If Postgres is already listening on port 5432 the target fails; stop the other instance first.
>
> Acceptable — it's a procedural step in a how-to section, which is where procedure belongs. Noted only for completeness; no change needed.
>
> ---
>
> ## Suggested consolidated `## Rules` section
>
> Reassembling the binding rules found across the document, with rationale kept but separated:
>
> ```markdown
> ## Rules
>
> Branching and review
> - Never commit directly to `main`.
> - Run `make test` before opening a pull request.
>   Why: it is the same suite CI runs.
> - Any change touching the `postings` package must include a migration plan.
> - The data team must review that migration plan before the change is merged.
>   Why: writes are replicated synchronously across all three regional clusters.
>
> Code
> - Never construct a `Money` value from a floating-point literal.
> - Place code not consumed by the public API under `internal/`.
> - Never run a direct SQL update against `postings`; backfills go through `cmd/backfill`.
> - Log lines must never include the raw `account_number` field.
>   Why: the log pipeline is replicated to a lower-trust analytics store.
>
> Tests
> - Write new tests as table-driven tests by default.
> - Any test touching the `postings` package must run inside a transaction that is rolled back at the end of the test.
>   Why: the shared fixture set is not regenerated between tests.
>
> Currencies
> - Before adding a currency, open an issue tagged `finance-review`.
> - Do not add the currency until the finance team has signed off on that issue.
>   Why: unsupported currencies leak into customer invoices.
>
> Changelog
> - [Author to specify: what makes an entry acceptable.]
> ```
>
> Everything else in the document (history, timings, architecture pointers, how the collector works, the release schedule, the legacy runbook note) is context and can stay where it is once the rules above are pulled out.
>
> ---
>
> **Summary counts:** 7 Major (5 buried/mislocated rules, 1 untestable directive, 1 pair of hedged rules), 6 Minor (1 padded rule, 1 mislocated but clear rule, 4 ambiguous description-vs-constraint items). Out of scope per the skill's boundaries: no scoring, no conflict analysis against parent instruction layers, no general prose review.

### Baseline, rep 2

> # Audit: `ledger-service` — separation of context from constraints
>
> Scope: the document as given; no files read, no tools run. Severity is two-level: **High** = a binding rule an agent is likely to miss, or cannot determine how to satisfy; **Low** = the rule is findable but its binding status, scope, or boundary with its rationale is unclear.
>
> ## Structural observation
>
> The document has a section literally named **Rules** containing five items. Six further hard obligations live elsewhere — in Overview, Testing, Working with money, Observability, and the Appendix — and the highest-stakes ones (data-team review gate, finance sign-off gate, transaction-rollback requirement, PII logging ban) are all outside Rules. The heading signals "rules are here"; everything else reads as background. An agent that reads Rules carefully and skims the rest will miss the rules that matter most. Every High finding below is an instance of this.
>
> ## High
>
> **H1. Overview — data-team review gate buried in a causal sentence.**
> > "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
>
> A merge-blocking gate is the second clause of a "Because..." sentence, in the fourth line of a section that is otherwise history and orientation. Rewrite — move the rule to Rules, leave the fact in Overview:
>
> - Rules: `Any change touching the \`postings\` package must include a migration plan reviewed by the data team before merge.`
> - Overview: `Every write is replicated synchronously across the three regional clusters.`
>
> **H2. Testing — rollback requirement introduced with "It is worth noting that".**
> > "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
>
> "It is worth noting" frames a hard requirement as an aside; the rationale is welded on. Rewrite:
>
> - Rules (or a Testing rule list): `Tests that touch the \`postings\` package must run inside a transaction that is rolled back at the end.`
> - Context: `The shared fixture set is not regenerated between tests.`
>
> **H3. Appendix — finance sign-off gate introduced with "By the way", placed after the recipe it gates.**
> > "Adding a currency: update `fx/currencies.go` and the `currency_code` enum migration together. By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team, since unsupported currencies leak into customer invoices."
>
> The precondition appears after the steps an agent would already have started executing, in an appendix, with a casual preface. Rewrite, reordering so the gate precedes the work:
>
> ```
> Adding a currency:
> 1. Open an issue tagged `finance-review` and obtain finance-team sign-off. Do not change code before sign-off.
> 2. Update `fx/currencies.go` and the `currency_code` enum migration together.
> ```
> Context, separate: `Unsupported currencies leak into customer invoices.` Also cross-reference from Rules, since this is a gate rather than a how-to.
>
> **H4. Rules — untestable directive.**
> > "Keep the changelog entries readable."
>
> Sits in the Rules list, so it binds, but there is no way to determine compliance. This cannot be rewritten without author input; the fix is to replace "readable" with whatever the team actually checks (for example: one entry per user-visible change, imperative mood, link to the PR — examples only, not to be adopted verbatim). If nothing is checked, the line is context and should say so or be removed.
>
> ## Low
>
> **L1. Rules — rule padded with rationale.**
> > "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip through the queue and keeps the shared runners free for everyone else."
>
> Rule: `Run \`make test\` before opening a pull request.` Move the rationale to Testing (which already describes the CI pipeline) or to a note under the list.
>
> **L2. Rules — hedged rule padded with rationale.**
> > "Prefer table-driven tests, which the team has found easier to extend than parallel test functions, and which match the style of the existing `postings` and `journals` suites."
>
> "Prefer" leaves the binding status open. Semantic-preserving rewrite keeps it a default: `Use table-driven tests by default.` Rationale as context: `The team finds them easier to extend than parallel test functions; the \`postings\` and \`journals\` suites use this style.` If it is in fact a hard rule, the author should drop the hedge; I did not strengthen it.
>
> **L3. Rules — hedged with "Generally", no stated exceptions.**
> > "Generally use the `internal/` package for anything not consumed by the public API."
>
> An agent cannot tell when the exception applies. Rewrite: `Put code not consumed by the public API under \`internal/\`` followed by either an explicit exception list from the author or no hedge at all if there are no exceptions.
>
> **L4. Working with money — one hard rule plus two description-shaped statements that may be rules, all outside Rules.**
> - `Never construct a \`Money\` value from a floating-point literal.` — clear and imperative, but sits between descriptive sentences in a topical section. Move to Rules or cross-reference.
> - "conversion goes through `fx.Convert`, which requires an explicit rate source" — reads as a description of the system, but is likely meant as "only convert via `fx.Convert`". Author should decide; if it is a rule: `Convert between currencies only through \`fx.Convert\` with an explicit rate source.`
> - "Rounding is banker's rounding throughout" — same ambiguity; if new code must use banker's rounding, say so as a rule.
>
> **L5. Observability — hard prohibition outside Rules, rationale attached by dash; one implied constraint.**
> > "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
>
> The rule is clear; separate it: `Log lines must never include the raw \`account_number\` field.` Context: `The log pipeline is replicated to a lower-trust analytics store.` Consider promoting to Rules given the stakes. Also, "the collector parses them by the `msg` and `level` keys" implies logs must carry those keys; if that is a requirement, state it as one.
>
> **L6. Appendix — hard prohibition living in a how-to list.**
> > "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`."
>
> The wording is fine; the location means it is found only by someone looking up "backfilling". Add to Rules (`Never run direct SQL updates against \`postings\`; use \`cmd/backfill\`.`) and keep the appendix entry as the how-to.
>
> ## Not flagged
>
> - Getting started, "stop the other instance first" — procedural troubleshooting, appropriately placed.
> - Testing, "most contributors run them only before pushing" — description of practice, not a rule; fine as context (it does not read as permission).
> - Deployment, legacy runbook "retained for incident archaeology and is not current policy" — a good example of context that explicitly disclaims binding force.
> - Overview, "Most contributors find the codebase easier to navigate after reading..." — clearly context.
>
> Out of scope, noted only: there may be tension between "Run `make test` before opening a PR" and the Testing section's description of integration tests being run only before pushing (whether `make test` includes the `integration` tag is not stated). That is a conflict question, not a separation one.
>
> ## Recommended shape
>
> Consolidate all hard obligations — the five in Rules plus H1, H2, H3, the `Money` float ban, the `account_number` ban, and the backfill prohibition — into a single Rules list with one obligation per line and no rationale inline. Keep the topical sections as context, with rationale sentences placed there, and a one-line cross-reference back to Rules where a section's topic has a gate.

### Baseline, rep 3

> # Audit: `ledger-service` repository instructions — context vs. constraints
>
> Severity scale used: **Major** = a binding rule an agent is likely to miss, or whose binding status is ambiguous; **Minor** = the rule is findable and unambiguous, but padding, placement, or phrasing makes it weaker than it needs to be. Rewrites preserve the original meaning; where a rewrite would require information the document does not contain, that is called out rather than invented.
>
> ## Summary
>
> The document has a `## Rules` section containing 5 items, but roughly 12 binding constraints are spread across all seven sections. The most consequential ones (data-team review for `postings` changes, finance sign-off for new currencies, transactional rollback for `postings` tests, the `account_number` logging prohibition) are all *outside* `## Rules`, and three of them are introduced with minimizing lead-ins ("Because...", "It is worth noting that...", "By the way..."). An agent that reads `## Rules` as the authoritative list will miss most of the actual requirements.
>
> ## Major findings
>
> **M1. Migration-plan requirement buried in the Overview, wrapped in a causal clause.**
> > "Because every write is replicated synchronously across those clusters, any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged."
>
> This is a hard merge gate, placed in a section otherwise composed of history and orientation, and grammatically subordinated to its rationale. Rewrite: move to `## Rules` as
> > "- Any change touching `postings/` requires a migration plan reviewed by the data team before merge."
>
> Keep the replication sentence in the Overview as context.
>
> **M2. Transactional-rollback requirement introduced with "It is worth noting that".**
> > "It is worth noting that any test touching the `postings` package must run inside a transaction that is rolled back at the end, because the shared fixture set is not regenerated between tests."
>
> The lead-in signals an aside; the content is a must. Rewrite as a rule (in `## Rules` or a `Rules` block inside `## Testing`):
> > "- Tests touching `postings/` must run inside a transaction that is rolled back at the end."
>
> Rationale ("the shared fixture set is not regenerated between tests") stays as context.
>
> **M3. Finance sign-off gate introduced with "By the way", in an appendix, after the procedure it gates.**
> > "By the way, before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team..."
>
> Three problems: minimizing phrase, appendix placement (readers skip appendices), and ordering (the how-to precedes the prerequisite, so an agent following the steps top-down would already be editing files before learning it needs approval). Rewrite: place the gate *before* the procedure and state it flatly:
> > "Adding a currency: (1) Open an issue tagged `finance-review` and obtain finance-team sign-off. (2) Only then update `fx/currencies.go` and the `currency_code` enum migration together."
>
> And mirror it in `## Rules`: "- Do not add a currency without finance-team sign-off on a `finance-review` issue."
>
> **M4. "Keep the changelog entries readable." — untestable.**
> No criterion is given for "readable"; an agent cannot verify compliance and a reviewer cannot point to a violation. This cannot be rewritten semantically-preservingly without author input. Recommendation: replace with the concrete standard the team actually applies (e.g., one line per change, user-facing wording, link to PR), or delete it if there is no standard. Flagged for the author.
>
> **M5. "Generally use the `internal/` package..." — hedged rule with no stated exception.**
> "Generally" makes it unclear whether this binds. If the team treats it as a rule, drop the hedge: "- Put code not consumed by the public API under `internal/`." If there are legitimate exceptions, name them ("...except X"). If it is only a preference, move it out of `## Rules` into a conventions note so it is not read as a requirement.
>
> **M6. "Prefer table-driven tests, which the team has found..." — hedged and padded.**
> Same ambiguity as M5 ("Prefer"), plus two clauses of justification inside the rule item. Rewrite as a rule with rationale moved out:
> > "- Write new tests as table-driven tests."
> > Context (elsewhere): the team finds these easier to extend, and they match the existing `postings` and `journals` suites.
>
> If the intent really is a soft preference, keep "Prefer" but label the item as a convention rather than a rule.
>
> **M7. `account_number` logging prohibition placed in a descriptive section.**
> > "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store."
>
> Clear wording, but it sits between two descriptive sentences about trace ids and Grafana folders, and its rationale is attached with a dash. This is a data-protection constraint; it should be in `## Rules` (or a per-section rule block) as "- Never log the raw `account_number` field." with the replication note kept as context. Rated Major because of the consequence of missing it, not the phrasing.
>
> ## Minor findings
>
> **m1. `make test` rule padded with rationale inside the bullet.**
> > "Run `make test` before opening a pull request — this is the same suite CI runs, so catching failures locally saves a round trip..."
> Rewrite: "- Run `make test` before opening a pull request." Move the CI/queue explanation to `## Testing`.
>
> **m2. Scope of `make test` is ambiguous relative to `## Testing`.**
> `## Testing` says integration tests are behind a build tag and "most contributors run them only before pushing." It is not stated whether `make test` includes integration tests, so the rule in m1 does not say which suite is required before a PR. Recommend stating it explicitly ("`make test` runs unit tests only; run `make test-integration` before pushing" or whatever is true). Author input needed.
>
> **m3. `Money` rules mixed into a descriptive section.**
> "Never construct a `Money` value from a floating-point literal." is clear, but the surrounding sentences ("conversion goes through `fx.Convert`, which requires an explicit rate source"; "Rounding is banker's rounding throughout") are constraints phrased as descriptions. Suggest a short rule block at the end of `## Working with money`:
> > - Never construct `Money` from a floating-point literal.
> > - Convert currencies only via `fx.Convert` with an explicit rate source.
> > - Use banker's rounding for all rounding.
>
> The COBOL-heritage sentence stays as context.
>
> **m4. Implicit log-format and trace-id constraints stated as description.**
> "the collector parses them by the `msg` and `level` keys" and "Every request carries a trace id propagated through `context.Context`" both imply obligations (every log line must have `msg` and `level`; handlers must propagate the trace id) but are worded as facts. Rewrite as rules if they are meant to bind.
>
> **m5. Backfill prohibition in the appendix.**
> "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`." Wording is fine; placement under "common tasks" means an agent asked to backfill from a different entry point may not see it. Mirror in `## Rules`: "- Never backfill `postings` with direct SQL; use `cmd/backfill`."
>
> **m6. Port-5432 conflict handling is procedural, not a rule.**
> "If Postgres is already listening on port 5432 the target fails; stop the other instance first." This is fine as a conditional step in a procedure; noted only to confirm it was considered and does not need to move.
>
> ## Non-findings worth keeping
>
> - "Never commit directly to `main`." — model rule: one obligation, no hedge, no padding.
> - The `docs/runbook-legacy.md` sentence explicitly marks stale content as "not current policy." This is the correct pattern for retired instructions; consider strengthening to "Do not follow `docs/runbook-legacy.md`; it is retained for incident archaeology only," but it already does its job.
> - "Most contributors find the codebase easier to navigate after reading `docs/architecture.md`." — correctly written as context, not a disguised rule.
>
> ## Structural recommendation
>
> Either (a) consolidate every binding constraint into `## Rules` and leave the topical sections as pure context, or (b) keep rules near their topic but add a consistent, visually distinct "Rules" block at the end of each section. Either is fine; the current hybrid, where `## Rules` exists but holds under half the rules, is the worst of both because it implies completeness it does not have.
