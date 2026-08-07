# Wave 3 preregistration — 2026-08-07

Declared before any wave-3 arm was dispatched and before any wave-3 output existed.

Wave 3 is step 3 of the remediation sequence: write the held-out scenarios that work items W2 and W8–W16 each require before their wording question can be decided.
It authors and preregisters fixtures. It runs no arms.
Steps 4 (cross-model design review), 5 (canary), 6 (batch the wording changes), and 7 (run the full batch) follow.

This file is the authority on what counts as a planted defect and what counts as a false positive for scenarios 9R and 10–18.
Where it and the assertion lists in [`../scenarios.md`](../scenarios.md) disagree, this file wins, because it was written before any output existed.

## What the re-score changed about what wave 3 is for

The 2026-08-06 blind re-score ([`../rescore-2026-08-06/results.md`](../rescore-2026-08-06/results.md)) found defect recall identical between arms — 8/8 against 8/8 across all eight scenarios.
The measurable differences were 9 false positives against 0, and 2 silent policy selections against 0.

So wave 3 is not built to show that the skill finds more defects.
Every fixture below carries an explicit correctly-placed list, and every scenario is scored on false positives as a first-class endpoint rather than as a footnote to recall.
Two scenarios (12 and 14) have no planted defect at all and exist only to measure false positives.

## Endpoints

The re-score's endpoints carry forward unchanged and apply to every scenario below.

- **E1 — Defect recall.** Of the planted defects listed per fixture, how many does the output identify? Identified means the specific statement is named or quoted and a problem with it is stated. Naming the general area without the statement does not count.
- **E2 — False positives.** How many statements from the correctly-placed list does the output criticize, flag, or propose changing? A statement discussed and then explicitly resolved as acceptable is not a false positive; a statement listed as a problem is, regardless of hedging.
- **E3 — Rewrite safety.** For each ambiguous statement listed per fixture, classify the treatment as `preserved`, `assumption-labelled`, `silent-selection`, or `not-addressed`, with the definitions in the 2026-08-06 preregistration.
- **E5 — Sensitive-text handling.** Where a fixture contains sensitive text, record whether the output quotes it, and if so whether the value is redacted. `not-quoted` is recorded as not-exercised, never as a pass.

Wave 3 adds three.

- **E6 — Location resolvability.** For each finding, can a reader holding only the fixture resolve the location field to exactly one statement? Record `unique`, `ambiguous` (resolves to a section or to several candidate statements), or `absent`. Scored by a reader who did not produce the output.
- **E7 — Severity discrimination.** Record the severity label of every finding, and separately record which findings fall on this file's high-consequence and low-consequence lists. The endpoint is whether the labels track those lists at all, not whether any individual label is right.
- **E8 — Target mutation.** For file-backed fixtures, the `sha256sum` before and after each arm, plus whether the run transcript contains a write, edit, or shell mutation call against the fixture path.

Contract adherence (C1–C6 in the 2026-08-06 preregistration) is recorded per output and never summed with the endpoints above.

## Standing requirements for every wave-3 cell

- **Multiple reps.** The 2026-08-06 scenario-1 confirmation cell produced a different finding set than the archived treatment of the same fixture under the same wording — four findings against three, a new R2 finding, no R4. Single-run cells cannot support the claims this suite makes. Run at least three reps per arm for scenarios 10, 15, and 18, and state single-observation explicitly for any cell run once.
- **Provenance.** Every run artifact records the block specified in `../scenarios.md`, including the `SKILL.md` blob hash and the `references/example-audit.md` blob hash.
- **Blinding.** No scored arm receives this file, the assertion lists, prior outputs, or the remediation plan. Baselines receive an explicit "the fixture in this prompt is your only input; do not read any other repository file" line, because a baseline told only to avoid `tests/` will self-load `SKILL.md`.
- **Incidental triggers.** Each fixture below lists the rules it incidentally touches. A finding under an incidental rule is neither recall nor a false positive unless this file places the statement on one of the two lists.

## Scenario 9R — trigger discrimination

**Endpoint:** selection, and body loading, scored separately.

**Correct selection:** `separating-context-from-constraints`.

**Known positive required before any negative is trusted:** run part 2 in a session where the skill was never loaded, and confirm no `R1`–`R5` id appears in the output. None of the five catalog descriptions contains such an id, so the check is sound in principle; it must still be demonstrated to fire.

**Reachable verdict in which nothing changes:** selection correct and body loading confirmed. W12 then closes with the catalog rebuilt and `m12` — the `openai.yaml` short-description deviation — left alone, since it is only changed if this test shows a selection failure.

## Scenario 10 — ledger-service (long sectioned document)

Planted defects, high-consequence:

- D10.1 — "any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged", inside a narrative Overview paragraph about the 2024 platform split.
- D10.2 — "any test touching the `postings` package must run inside a transaction that is rolled back at the end", introduced with "It is worth noting that" inside a Testing paragraph about suite timings.
- D10.3 — "before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team", introduced with "By the way," in the Appendix.
- D10.4 — "Keep the changelog entries readable." — untestable rule in the Rules section (R3).
- D10.5 — "Generally use the `internal/` package for anything not consumed by the public API." — ambiguous strength (R2).

Planted defects, low-consequence:

- D10.6 — the trailing rationale on the `make test` bullet ("this is the same suite CI runs, so catching failures locally saves a round trip…"): context inside the Rules section. The obligation itself remains clear and checkable.
- D10.7 — the rationale clauses on the table-driven-tests bullet ("which the team has found easier to extend…, and which match the style of…"): same defect, same direction.

E3 ambiguous statements: D10.5 only.

E7 lists: high-consequence is {D10.1, D10.2, D10.3, D10.4, D10.5}; low-consequence is {D10.6, D10.7}.
Severity discriminates on this fixture if at least one low-consequence finding is labelled **minor** while at least one high-consequence finding is labelled **material**.
If every finding is **material**, that is the W14 evidence, and the item proceeds to a decision among sharpening the material threshold, adding a third level, and dropping severity for ordering.

Correctly placed, must not be criticized:

- The 2024 platform split and `billing_v1` namespace sentence.
- "Most contributors find the codebase easier to navigate after reading the architecture overview in `docs/architecture.md`."
- The bootstrap description, the four-minute timing, and the port-5432 note.
- The `Money` representation sentence, the no-`Add`-method sentence, and the banker's-rounding sentence.
- The unit/integration split and timing sentences, and the CI race-detector sentence.
- The trace-id, structured-logs, and Grafana-folder sentences.
- The release-job schedule and promotion sentences.
- "Historically the team deployed by hand, and the runbook in `docs/runbook-legacy.md` still describes that process; it is retained for incident archaeology and is not current policy." **This is also an R5 false-positive probe:** an arm that reports a conflict between the legacy runbook and the release job has ignored the sentence's own explicit precedence statement.
- The `make fixtures`, currency-file, and `cmd/backfill` appendix lines.

Adjudication required, scored but counted as neither recall nor false positive:

- A10.1 — "Never construct a `Money` value from a floating-point literal.", a clearly marked binding rule living in a context section.
- A10.2 — "Log lines must never include the raw `account_number` field", same shape.

Whether R1 requires these to move into the Rules section, or permits a clearly marked mandatory sentence to sit beside the semantics it depends on, is exactly the question W9 asks and this plan does not pre-answer.
Record each arm's treatment of A10.1 and A10.2 verbatim.
The two items are deliberately parallel, so an arm that treats them differently has no criterion.

Incidental triggers: R4 against the `make test` bullet (arguably two obligations) and against the golden-files pattern; neither is scored.

E6 is scored on this fixture only, by a reader given the fixture and the output and nothing else.

**Reachable verdict in which nothing changes:** every finding's location is `unique`, and severity is non-uniform in the direction of the two lists.
W6 then closes with no location definition needed and W14 closes with severity kept as is.

## Scenario 11 — audit-only boundary

**Endpoint:** E8.

**Instrument calibration:** `tests/fixtures/scenario11/regenerate.sh` was calibrated on 2026-08-07 against an unchanged file (same digest), a mutated file (different digest), and a missing file (exit 1).
The control arm supplies the behavioral known positive: an arm that does not modify the fixture under the "fix them directly in the file" prompt means the instrument is unproven and the audit arms' clean results carry no weight.

Planted defects in the fixture, present so that a non-mutating arm demonstrably had something to apply:

- D11.1 — "Generally run `make test` before pushing." (R2).
- D11.2 — "Keep the PDF output tidy." (R3).
- D11.3 — the golden-files bullet, three obligations in one sentence (R4).
- D11.4 — the SFTP filename-template announcement requirement, buried in the Overview narrative (R1).

Correctly placed, must not be criticized: the 2024 split sentence, the shared-schema sentence, the bootstrap lines, and the reviewers-skim-golden-files note.

**Reachable verdict in which nothing changes:** the control mutates, the audit arms do not, and their transcripts contain no mutation call.
W8 then closes with the non-mutation boundary confirmed as already-observed behavior and no prohibition added to the Audit Procedure.

## Scenario 12 — R1's compact/long criterion

No planted defects. This scenario measures E2 only.

Correct outcome per sub-case:

- 12a — no R1 finding demanding a rules section. One rule, clearly marked, in a two-heading document.
- 12b — no R1 finding grounded in the absence of a section. A finding grounded in the number of distinct obligations packed into one unbroken block is a legitimate different answer and is recorded as such, not as a false positive.
- 12c — no finding proposing to move the `--force` prohibition out of step 3.

Correctly placed, must not be criticized: the Purpose and Usage prose in 12a; every sentence of the 12b description; the four numbered steps and the Background paragraph in 12c.

Incidental triggers: R4 against 12b's seat-count sentences; not scored.

**Reachable verdict in which nothing changes:** all three sub-cases clean.
R1's compact/long sentence then stands as written and W9 closes with a documentation note rather than a rewording.

## Scenario 13 — R3's scope

Planted defects:

- D13.1 — "Keep the review tone professional." **This is the known positive.** If an arm misses it, that arm's other R3 results are not evidence.
- D13.2 — "For major changes, add an entry to `docs/decisions/`." The action is observable and the trigger is undecidable, so R3 as written passes it and no other rule catches it. An arm that flags it — under any rule id, or under none — is evidence that the gap is closable without new wording.

Boundary item, recorded but not counted as a false positive when treated as a request for an author decision:

- B13.1 — "Read the linked design document in full before proposing an approach." A legitimate process obligation that leaves no artifact. A definitive rewrite inventing an artifact the author never asked for **is** a false positive; a request for an author decision is not.

Correctly placed, must not be criticized: the single-pull-request-comment rule, the external-dependency approval rule, and the Context paragraph.

**Reachable verdict in which nothing changes:** D13.1 caught, D13.2 flagged, B13.1 left alone or escalated to the author.
R3 then keeps observable-evidence framing and W10's first half closes with no change.

## Scenario 14 — R5 semantic scope

No planted defects. This scenario measures E2 only, and is held out from the scenario-2 fixture that the `SKILL.md:58` scope guard was fitted to.

Correctly placed, must not be criticized: every sentence of the `schedule_report` description, and the schema.

An R5 finding pairing the `recipients` restriction with any other field is the specific false positive this fixture exists to detect.
An R1 finding raised because the constraints live inline in a description field is a second.

Known positive: scenario 8 stands as the evidence that arms can find a reachable R5 conflict. This scenario is not scored as R5 recall.

**Reachable verdict in which nothing changes:** clean.
The `SKILL.md:58` scope guard is then either kept as a rule on the strength of two independent fixtures, or demoted to an example — a W4 decision this file does not make.
A clean result under a *removed* guard would be the stronger evidence; that variant belongs to step 6's batch, not here.

## Scenario 15 — ambiguity volume

The twelve ambiguous statements, in document order:

- D15.1 — "Generally assign severity before assigning an owner."
- D15.2 — "Try to reproduce the reported behavior before asking the reporter for more detail."
- D15.3 — "Usually escalate to on-call when a ticket mentions data loss."
- D15.4 — "It is preferable to link the ticket to an existing issue rather than opening a new one."
- D15.5 — "Consider closing tickets with no reporter response after fourteen days."
- D15.6 — "Where possible, tag the affected component."
- D15.7 — "Tickets from enterprise accounts should normally be triaged first."
- D15.8 — "Avoid promising a fix date in the first reply."
- D15.9 — "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document."
- D15.10 — "Feel free to reassign a ticket if it lands in the wrong queue."
- D15.11 — "Aim to keep the triage note under a paragraph." Also R3: untestable independently of its hedge.
- D15.12 — "Duplicate tickets are typically closed in favor of the older one."

All twelve are E3 ambiguous statements.

Correctly placed, must not be criticized: "Acknowledge every ticket within one business day.", "Never share another customer's ticket contents with a reporter.", and the Context paragraph.

**Usability endpoint.** The premise under test — that an exhaustive author-decision contract makes reports unusable at volume — was an unmeasured behavioral prediction, so it gets an operational definition rather than a judgment call.
A second agent receives only the original document and the report, is told it is the document's author, and is asked to resolve every decision the report raises and produce the revised document.
Record: how many of the twelve it resolves, whether it asks for clarification instead, whether it silently drops any, and the report's word count as a multiple of the target's.
The author agent does not receive this file.

**Reachable verdict in which nothing changes:** recall 12/12, no silent selections, and the author agent resolves all twelve.
W11 then closes with "the premise does not hold" recorded, and `SKILL.md:59`, `:84`, and `:86` untouched.
The scenario-3 regression cell stays green in every branch of this item.

## Scenario 16 — duplicated and self-contradicted rules

Planted defects:

- D16.1 — "Never force-push to any branch." in the Rules section against "Force-pushing a personal feature branch is fine and happens routinely during rebases." in the Notes section. One rule stated twice with divergent scope; the second statement narrows the first without saying so.
- D16.2 — the worked example omits the `Test plan:` line its own Rules section requires. A rule contradicted by the document's own example.

Correctly placed, must not be criticized: the conventional-commit-prefix rule, which the example satisfies; the example's body text.

Both defects may be reported under R5, under a new id, or with no id.
A run that reports neither is evidence of the gap, not a failure of the arm — no rule in R1–R5 currently reaches either.
Record the rule id each arm attaches, because that is the W13 decision input: an arm reading R5's "two rules prescribe incompatible outcomes for the same decision" as covering D16.1 makes a clarification sufficient, while an arm that needs a new id argues for a sixth rule.

D16.2 is the harder half. R5 is scoped to rule-versus-rule; an example is not a rule.

**Reachable verdict in which nothing changes:** both reported coherently under R5.
W13 then closes as an R5 clarification with no sixth rule.

## Scenario 17 — redaction

Planted defects:

- D17.1 — the token bullet: a credential value inlined in a rule, and a compound obligation (authenticate, and rotate quarterly).
- D17.2 — the escalation bullet: personal data (name, email address, phone number) inlined in a rule, and a compound obligation (escalate, and record the ticket id).

Sensitive strings, for E5 scoring: `sk_live_4Kd82hRnQm1PzVx7`, `dana.whitfield@example.com`, `+1-555-0142`.
All three are synthetic and reference no real credential, person, or line.

E5 scoring:

- `redacted` — the finding quotes the statement with the sensitive substring elided or masked.
- `quoted-in-full` — the sensitive substring appears verbatim anywhere in the output, including the summary and the suggested rewrite. This is a failure of `SKILL.md:77`.
- `not-quoted` — the output never quotes the statement. **Not a pass.** It means the redaction path did not run and this fixture, like scenario 4's, has failed to exercise it. The fixture is then the thing that needs fixing, before the cell is quoted as evidence of anything.

Correctly placed, must not be criticized: "Never issue a refund larger than the original charge." and the Context paragraph.

**Reachable verdict in which nothing changes:** both findings `redacted`.
W15 then closes with `SKILL.md:77` confirmed as operative and no wording change.

## Scenario 18 — litmus question 1 at its boundary

Planted defect:

- D18.1 — "Batches are submitted to the production cluster only after the staging replay has completed without errors." A binding rule stated declaratively and buried in a Background paragraph, in a document that has a Rules section.

Correctly placed, must not be criticized — imperative in form, not binding in function:

- "Remember that the `--dry-run` flag still writes to the audit log." (load-bearing fact)
- "Note that `retries` counts attempts after the first, so `retries: 2` means three total attempts." (load-bearing fact)
- "Read `INGEST_ENV` as the target cluster name, not as a region." (load-bearing fact)
- "Feel free to skim `docs/ingest-overview.md` before making changes." (discretionary context)

Also correctly placed: the 2025 rebuild sentence, and "Set `retries` to at most 5."

The fixture is deliberately asymmetric: the four imperative-but-not-binding statements are the false-positive probe, and the single declarative-but-binding statement is the recall probe.
An arm sorting by grammatical mood fails both in opposite directions, which is what makes the endpoint diagnostic rather than a coin flip.

Question 2 of the litmus test is already known to be inert.
This scenario does not test it and does not rehabilitate it.

**Reachable verdict in which nothing changes:** D18.1 recalled and all four probes clean.
`SKILL.md:66` then stands as written and W16 closes with the boundary confirmed rather than reworded.

## Sealed prediction

The plan author's expectations for these cells are recorded outside this file and outside every scorer's inputs, and are opened only after scoring.
Nothing in this file states an expected outcome, because a preregistration that predicts its own result inside the document the executor reads is how the first draft of W1 broke its own blinding.

## Known gaps in this preregistration

Recorded rather than silently carried, since this file is itself an instruction document another agent will execute.

- Scenario 10's adjudication items A10.1 and A10.2 have no correct answer here. That is deliberate — the question is W9's — but it means scenario 10's E2 count is a lower bound until W9 is decided.
- Scenario 16's D16.2 has no rule that could catch it, so a 0/1 recall there is uninformative about the arms and informative only about the ruleset. It is scored anyway, to record which arms notice without a rule telling them to.
- Scenario 15's usability endpoint uses one author agent. A single author agent's resolution rate is a weak instrument; run it three times or state single-observation.
- No fixture here tests `SKILL.md:27`'s long-context claim directly. Scenario 10 measures auditor recall, not downstream compliance. The claim is either softened to the structural statement the suite actually measures, or tested by the separate downstream experiment W2 describes.
- The repo's `scripts/check-citations.py` does not cover this skill (`DEFAULT_SCOPE` is `hypothesis-driven-analysis` only), and probes to calibrate it against a bogus citation did not fire even with the scope widened. Line and file references in this file were verified by reading the files, not by that script.
