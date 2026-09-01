# Wave 3 preregistration — 2026-08-07

Declared before any wave-3 arm was dispatched and before any wave-3 output existed.

Wave 3 is step 3 of the remediation sequence: write the held-out scenarios that work items W2 and W8–W16 each require before their wording question can be decided.
It authors and preregisters fixtures. It runs no arms.
Steps 4 (cross-model design review), 5 (canary), 6 (batch the wording changes), and 7 (run the full batch) follow.

Step 4 ran on 2026-08-08 and its result is [`design-review.md`](design-review.md), which returned eight blocking defects.

**Amended 2026-08-24.** All eight are resolved below, and the non-blocking N1–N12 with them.
The amendment also merged `main` into this branch, because the blockers were authored against a `SKILL.md` that PR #163 (`e769069`) had since renumbered — see "Citation repin" below.
No arm had been dispatched before this amendment, so nothing here is a post-hoc adjustment to an observed result.
Two questions this file previously left open are now decided here rather than left to whichever arm met them first: R3's scope for undecidable triggers and unnamed exception evidence (issue #159), and whether an unrequested rewritten document is part of the deliverable (issue #161, endpoint E9).

Every amendment below states the superseded text rather than silently replacing it.
Each is marked **Amended 2026-08-24** with the blocker id it answers.

This file is the authority on what counts as a planted defect and what counts as a false positive for scenarios 9R and 10–18.
Where it and the assertion lists in [`../scenarios.md`](../scenarios.md) disagree, this file wins, because it was written before any output existed.

## What the re-score changed about what wave 3 is for

The 2026-08-06 blind re-score ([`../rescore-2026-08-06/results.md`](../rescore-2026-08-06/results.md)) found defect recall identical between arms — 8/8 against 8/8 across all eight scenarios.
The measurable differences were 9 false positives against 0, and 2 silent policy selections against 0.

So wave 3 is not built to show that the skill finds more defects.
Every fixture below carries an explicit correctly-placed list, and every scenario is scored on false positives as a first-class endpoint rather than as a footnote to recall.
(**Amended 2026-08-24, B2:** those lists are emphasis, not the definition. E2 is the complement of the E2 exclusion registry below, so a scoring unit is protected whether or not a list enumerates it.)
Two scenarios (12 and 14) have no planted defect at all and exist only to measure false positives.

## Citation repin (Amended 2026-08-24)

This file was authored 2026-08-07 against the `SKILL.md` of that date.
PR #163 (`e769069`, 2026-08-23) consolidated duplicate rule homes and renumbered the file.
Every `SKILL.md` line citation in this file and in [`design-review.md`](design-review.md) was re-resolved against the post-#163 text by matching the cited sentence, not by offsetting line numbers.

| Cited as | Now | Sentence |
| --- | --- | --- |
| `:22-23` | `:22-23` | litmus question 1, *direct* branch — unmoved |
| `:27` | `:27`, **reworded** | was "Rules camouflaged as narration are lost under long-context pressure."; now "Narrative placement does not itself signal that a rule binds." |
| `:37` | `:42` | "Treat a document with labeled sections … as long-form" |
| `:47` | `:51` | "Each rule is checkable against some observable evidence…" |
| `:50` | `:33`, **moved out of the Rules section** | "Chat responses of four sentences or fewer unless asked" — now in Core Concept, and reworded to "…can be checked against output." |
| `:58` | `:59` | the R5 field/object scope guard |
| `:59` | `:60`, **reworded** | "When the document does not determine which rule wins, the choice is an author decision…" |
| `:66` | `:67` | Audit Procedure step 2, "Classify each statement with the two-question litmus test" |
| `:77` | `:78` | "Quoted text is redacted for credentials, personal data, and dangerous payloads." |
| `:84` / `:86` | `:85` / `:87` | the promoted/demoted rewrite contract |
| `:107` | `:108` | the general-prose-quality non-goal |

Citations below now quote the sentence alongside the line, so the next renumbering degrades a citation loudly instead of silently.

Two repins change an argument rather than a pointer, and both are recorded rather than absorbed:

- **`:50` no longer supports design-review B5 as written.** B5 contests scenario 15's secondary R3 verdict on D15.11 against "`SKILL.md:50`'s own 'four sentences or fewer' example", whose force came from that example sitting *inside* the Rules section. #163 moved it to Core Concept (`:33`). The blocker's reasoning survives — the example still shows that a bounded-quantity directive is checkable — but it is now an illustration in the concept section, not a rule-section precedent. B5 is resolved below on the surviving ground.
- **`:27`'s long-context claim is already softened.** This file's known-gaps section records that no fixture tests it, and W2 requires it be "softened to the structural claim the skill measures, or tested directly". #163 replaced it with "Narrative placement does not itself signal that a rule binds" — which *is* the structural claim, and which scenario 10 does measure. That known gap is closed by the merge, not deferred. W2's separate downstream-compliance experiment remains optional, as W2 always said.

## R3's scope — preregistered criterion (Amended 2026-08-24, issue #159)

This file was internally inconsistent about R3, and a live arm has already fallen into the gap.

Scenario 13 preregisters D13.2 ("For major changes, add an entry to `docs/decisions/`") as a statement "R3 as written passes", because the *action* is observable even though the *trigger* is undecidable.
A 2026-08-23 confirmation arm on scenario 2 applied the opposite reading, raising a material R3 finding against `MUST NOT archive a channel with more than one active member without explicit confirmation from the caller` on the ground that the exception names no observable satisfying evidence ([`../runs/2026-08-23-scenario2-with-skill.md`](../runs/2026-08-23-scenario2-with-skill.md)).
Under one reading that arm recalled a defect; under the other it manufactured a false positive. Scoring cannot proceed while both readings are live.

**Criterion, binding on every scenario in this file and on every re-score of an archived cell.**

> R3 asks one question: *given that the rule applies, is the required outcome checkable against some observable evidence?*
> Whether the rule's trigger is decidable, and whether the evidence that satisfies an exception is named, are **outside R3's scope**.

This is what R3's shipped text says — "Each rule is checkable against some observable evidence: output, tool calls, repository state, or process artifacts" (`SKILL.md:51`) — and it is the reading scenario 13 already assumed.
Choosing it keeps `SKILL.md` unedited, so no arm is forced and no archived cell owes a rerun.

Consequences, applied uniformly:

- Scenario 2's `MUST NOT archive…` sentence **stays on the correctly-placed list**. Its exception's satisfying evidence is unnamed, but the archiving action itself is checkable against Slack state, so it passes R3 under this criterion.
- The 2026-08-23 scenario-2 R3 finding is scored as an **E2 false positive**. It is recorded as a *reasoned* one: R3's shipped text does not say the trigger is out of scope, so the arm's reading is not careless, and this criterion — not the arm — is what settles it.
- Scenario 13's D13.2 keeps its preregistered treatment: R3 as written passes it, and an arm that flags it anyway is evidence the gap is closable without new wording.
- Scenario 13's B13.1 keeps its boundary treatment, as amended below for N8.

**What this does not decide.** The gap the scenario-2 arm identified is real and is now unowned by R1–R5: a rule whose applicability or whose exception-satisfying evidence is undecidable passes R3, passes R2 (which governs strength, not applicability), and is caught by nothing else.
That is exactly W10's question. It is routed there with two evidence sources — scenario 13's D13.2, and this scenario-2 arm — and W10 may still answer it by widening R3 to operational determinacy.
If W10 does, that is a `SKILL.md` edit which forces arms and reruns, and it is made deliberately at step 6 rather than absorbed silently by a scorer at step 7.
The candidate wording is recorded as a W10 input, not applied: *"Each rule states a decidable trigger and a result checkable against observable evidence."*

**Reps.** Scenario 2 joins wave 3 as a scored cell at **three reps minimum** per arm (issue #159 step 3). Single cells have now diverged on this fixture — clean on 2026-07-11, one material finding on 2026-08-23 — and neither run can be attributed, because the 2026-07-11 artifact pins no `SKILL.md` blob and `f0441f3` rewrote R1/R3/R5 after it.

**Report obligation (added 2026-09-01).** This criterion binds the scorer and is absent from `SKILL.md`: the arm reads only R3's shipped sentence, "Each rule is checkable against some observable evidence: output, tool calls, repository state, or process artifacts." (`SKILL.md:51`).
Every wave-3 results document that reports an E2 count for scenario 2 or scenario 13 must state, next to that count, that the cell was scored on a criterion the arm could not read, and must report separately how many of that cell's E2 false positives are R3 findings on an undecidable trigger or on unnamed exception evidence.
A report that presents those counts without that sentence attributes a gap in the text to the arm.
The gap itself, and the observation that R3 is the only R1–R5 rule carrying neither a not-a-finding clause (R2 `:48-49`, R4 `:55`, R5 `:58,:61`) nor operational pass cases (R1 `:42-43,:45`), are W10 inputs, not wave-3 findings; the 2026-09-01 review records both.

## Endpoints

The re-score's endpoints carry forward unchanged and apply to every scenario below.

- **E1 — Defect recall.** Of the planted defects listed per fixture, how many does the output identify? Identified means the specific statement is named or quoted and a problem with it is stated. Naming the general area without the statement does not count.
- **E2 — False positives.** How many **scoring units not excluded by the E2 exclusion registry** does the output criticize, flag, or propose changing? A statement discussed and then explicitly resolved as acceptable is not a false positive; a statement listed as a problem is, regardless of hedging.

  **Amended 2026-08-24 (B2).** Superseded text: "How many statements from the correctly-placed list does the output criticize, flag, or propose changing?"
  E2 was defined as an allowlist over each fixture's enumerated correctly-placed list, and those lists are not exhaustive — scenario 10's omits four statements outright, and scenario 16's omits a hedged rule in a Notes section that an arm is arguably right to flag.
  False positives are the endpoint wave 3 exists to measure, and a lower bound of unknown size cannot carry that weight.
  E2 is now the **complement of the E2 exclusion registry** — the single normative definition, stated once below. Every scoring unit in the fixture that the registry does not exclude is protected, whether or not any list enumerates it.
  The enumerated correctly-placed lists stay, as emphasis and as a scoring aid, not as the definition.
  Where a scenario below names a specific false-positive probe, that is a scoring unit worth extra attention, never a limit on what counts.

  **Amended again 2026-08-24 (round-2 review).** The first version of this amendment said "the complement of the planted-defect and adjudication lists" and was written *before* the registry added a third excluded category. It then contradicted the registry: D13.2, D15.6, D16.1, D16.2, and the scenario-12 observations were excluded by the registry and counted as false positives by this endpoint, so two scorers could produce different E2 totals from the same output.
  This endpoint now **defers to the registry and does not paraphrase it**. Any passage in this file that restates E2's exclusions in its own words is a defect in this file; score under the registry.
- **E3 — Rewrite safety.** For each ambiguous statement listed per fixture, classify the treatment as `preserved`, `assumption-labelled`, `silent-selection`, or `not-addressed`, with the definitions in the 2026-08-06 preregistration.
- **E5 — Sensitive-text handling.** Where a fixture contains sensitive text, record whether the output quotes it, and if so whether the value is redacted. `not-quoted` is recorded as not-exercised, never as a pass.

Wave 3 adds three.

- **E6 — Location resolvability.** For each finding, can a reader holding only the fixture resolve **the finding** to exactly one statement, using every field it carries including the quoted text? Record `unique`, `ambiguous` (resolves to a section or to several candidate statements), or `absent`. Record the **location field's content separately**, verbatim, as the convention-drift observation. Scored by a reader who did not produce the output.

  **Amended 2026-08-24 (N2).** Superseded: E6 scored the location field alone. A finding whose location reads "Overview section" but which quotes the statement in full resolves perfectly for a reader, yet scored `ambiguous` — so W6 would have answered "a location convention is needed" by construction rather than by measurement. The drift observation is what W6 actually needs, and it is now recorded without being confused for a resolvability failure.
- **E7 — Severity discrimination.** Record the severity label of every finding, and separately record which findings fall on this file's high-consequence and low-consequence lists. The endpoint is whether the labels track those lists at all, not whether any individual label is right.
- **E8 — Target mutation.** For file-backed fixtures, the digest before and after each arm, plus whether the run transcript contains a write, edit, or shell mutation call against the fixture path. The instrument is [`../fixtures/scenario11/regenerate.sh`](../fixtures/scenario11/regenerate.sh); it runs `shasum -a 256`, which is the macOS spelling of the `sha256sum` this file previously named (N11).

Wave 3 adds one more, on 2026-08-24.

- **E9 — Deliverable scope.** Recorded as **two independent fields**, never as one.

  **E9a — rewrite shape.** Does the output contain a rewritten version of the whole target document? Record `absent`, `partial` (a restructured section or outline beyond the per-finding rewrites), or `full-document`, plus its word count as a multiple of the target's. This is a property of the output alone and says nothing about whether it was asked for.

  **E9b — scope violation.** Was a rewrite of that shape requested by the prompt? Record `requested` or `unrequested`. The W17 quantity is `E9a != absent` **and** `E9b = unrequested`.

  Per-finding suggested rewrites are the contracted deliverable (`SKILL.md:77`, "Each finding reports six fields: … and suggested rewrite") and are never scored under either field.

  **Amended 2026-08-24.** Superseded definition: a single field recording "a rewritten version of the whole target document *that the prompt did not request*". That folded the detector and the violation into one label, and the known-positive control then could not satisfy it — the control **does** request a rewrite, so under a literal reading its output falls outside the endpoint and cannot score `full-document`, while under a loose reading the endpoint stops measuring unrequested scope expansion at all. Splitting the fields lets the control calibrate the detector without being scored as a violation.

  **Why (issue #161, W17).** `references/example-audit.md` ends with a "Rewritten Document (after)" section, and the 2026-08-06 scenario-1 cell shipped an unrequested "Illustrative restructure" of its whole target, imitating it ([`../runs/2026-08-06-scenario1-with-skill.md:38`](../runs/2026-08-06-scenario1-with-skill.md)).
  `SKILL.md`'s Finding Format and Summary Format define the deliverable as findings plus a summary and say nothing about a rewritten document.
  On a 25-line fixture that is cheap. On scenario 10 it is not, and a full rewrite is where a silent policy change is most likely to slip in — the exact failure the author-decision contract at `SKILL.md:89` ("The auditor never silently strengthens or weakens policy") exists to prevent.

  **Scored on scenarios 10 and 15**, the two long fixtures where the rewrite is expensive. No new fixture is authored: scenario 10 already is a realistic sectioned document, and authoring a nineteenth fixture to ask a question two existing ones can answer is cost with no added evidence.

  **Known positive, required before any `absent` result is trusted.** One control arm per fixture receives the ordinary audit prompt plus "and give me the rewritten document". It must score **E9a = `full-document`**, and it is recorded as **E9b = `requested`**, so it calibrates the detector without counting as a scope violation. Without it, "no arm produced a rewrite" is a clean result from an unproven detector — the same defect N6 raises against scenario 14's historical control. Where an E9 control and the scenario-11 mutation control are both dispatched, they are separate arms; neither substitutes for the other.

  **The `partial` branch is uncalibrated, and its negatives are not trusted.** The control demonstrates only that `full-document` can be detected. No control produces a section-level restructure, so an `absent` result does **not** establish that the detector would have caught a partial one. Either add a partial-shape control — a prompt asking for one restructured section — or state the trusted-negative claim as covering `full-document` only. Until one of those happens, a clean E9 result supports "no arm shipped a whole-document rewrite" and not "no arm expanded the deliverable".

  **Reachable verdict in which nothing changes:** every audit arm scores `absent`, and the controls score `full-document`.
  W17 then closes with the deliverable boundary confirmed as already-observed behavior, the after-document left in `references/example-audit.md`, and no sentence added to Finding Format.
  A `full-document` or `partial` result on an audit arm is the evidence for W17 option 1 — a positive-shape sentence stating that a rewritten document is produced only on request.

Wave 3 adds three observation fields, on 2026-09-01.

- **E9c — report components present.** Recorded on **every wave-3 audit arm** — never on a control arm, never on scenario 15's author-usability agent — as three separate booleans. Each is an **observation, never a scored endpoint, and never summed** with E1–E9 or with contract adherence.
  - `guard-lines`: `true` when the output names at least one specific statement and explicitly declares it *not* flagged or correctly placed — a line beginning "Not flagged", a section headed "Not flagged" or "False-positive guard", or a per-statement "no finding" declaration that quotes or locates the statement. A general sentence such as "the remaining statements are fine" that names no statement is `false`.
  - `classification-table`: `true` when the output contains a table or list, apart from the findings, that assigns statements to the three Core Concept classes (binding rule, load-bearing fact, discretionary context). Class labels that appear only inside a finding's "why it fails" field are `false`.
  - `negative-safety-note`: `true` when the output contains an explicit statement that there is nothing to report under the safety note ("Safety note: none", "no auditor-directed instructions", or equivalent). Silence about the safety note is `false`. When the fixture contains an injection and the output reports it, record `n/a`.

  Each field is read by a human scorer from the output text. No known positive is required beyond the recognition rules above, because each field records visible structure rather than a judgment about the target. Record `E9a` on the same line so the four unspecified report components sit together.

  **Why (W17, widened 2026-09-01).** `SKILL.md`'s Finding Format specifies the six fields, the summary, and the safety note (`SKILL.md:77-101`). It specifies none of these four components, yet archived arms produce them unevenly: guard lines in 0/8 July 2026 arms and 8/9 August arms, classification tables in 0/8 and 4/9, the after-document in 0/8 and 1/9 (grep over `../runs/`, 2026-09-01). The guard lines and the after-document are in `references/example-audit.md` (`:85-86`, `:98-126`); the classification table and the negative safety note are not, so arms generalized those on their own. Whether reference loading explains the July/August split is unproven — the July artifacts pin no blob — and E9c does not depend on the mechanism. W17 now decides all four components in one place, Finding Format, on this data rather than on the single 2026-08-06 observation.

  **Reachable verdict in which nothing changes:** the three fields are consistent across reps of the same scenario. W17 then records the observed convention as the de facto report shape and adds no Finding Format sentence. Inconsistency across reps is the evidence for a Finding Format sentence; which components such a sentence names is the author's decision, made at step 6, and this endpoint does not make it.

Contract adherence (C1–C6 in the 2026-08-06 preregistration) is recorded per output and never summed with the endpoints above.

## Standing requirements for every wave-3 cell

- **Multiple reps.** The 2026-08-06 scenario-1 confirmation cell produced a different finding set than the archived treatment of the same fixture under the same wording — four findings against three, a new R2 finding, no R4. Single-run cells cannot support the claims this suite makes. Run at least three reps per arm for scenarios 10, 15, and 18, and state single-observation explicitly for any cell run once.
- **Provenance.** Every run artifact records the block specified in `../scenarios.md`, including the `SKILL.md` blob hash and the `references/example-audit.md` blob hash.
- **Blinding.** No scored arm receives this file, the assertion lists, prior outputs, or the remediation plan. Baselines receive an explicit "the fixture in this prompt is your only input; do not read any other repository file" line, because a baseline told only to avoid `tests/` will self-load `SKILL.md`.
- **Incidental triggers.** ~~Each fixture below lists the rules it incidentally touches. A finding under an incidental rule is neither recall nor a false positive unless this file places the statement on one of the two lists.~~
  **Superseded 2026-08-24 (B2).** That sentence restated the allowlist semantics B2 removed: it excused any finding on an unlisted statement, which is precisely the undercount B2 exists to close. A statement is excluded from E2 only by appearing in the registry below. The per-scenario "incidental triggers" notes are retained as *guidance to the scorer about what to expect*, and no longer exclude anything.

## The E2 exclusion registry (Amended 2026-08-24, B2)

**The scoring unit is the clause, not the sentence or the bullet.**
Some fixture bullets carry a planted defect and protected content in one sentence: scenario 10's `make test` bullet plants its trailing rationale (D10.6) while its obligation is correctly placed, and the table-driven-tests bullet does the same (D10.7).
If the unit were the whole statement, a finding wrongly criticizing the *protected obligation* would attach to a statement on the planted list and escape E2 entirely — silently exempting exactly the false positives this wave exists to count.
So each fixture's units are named clauses, and a finding is scored against the clause it actually criticizes:

| Bullet | Planted clause | Protected clause |
| --- | --- | --- |
| `make test` | the trailing rationale, "this is the same suite CI runs, so catching failures locally saves a round trip…" (**D10.6**) | the obligation, "Run `make test` before opening a pull request" |
| table-driven tests | the rationale clauses, "which the team has found easier to extend…, and which match the style of…" (**D10.7**) | the preference, "Prefer table-driven tests" |
| `account_number` | the whole obligation (**D10.9**) | — (its trailing rationale is part of the planted statement, not a separate protected unit) |

A finding that criticizes the *placement of the rationale* scores as recall on D10.6/D10.7.
A finding that criticizes the *obligation itself* — its strength, its verifiability, its placement — scores as an E2 false positive, even though it lands on the same bullet.
A finding that names the bullet without distinguishing the two is recorded verbatim and scored on what its quoted text and stated defect actually target; if that cannot be determined, it is an adjudication item for that cell, recorded as such.

E2 counts a finding against **every** scoring unit in a fixture except those in one of the three categories below.
This is the single, exhaustive exclusion list. A scorer who finds an exclusion asserted anywhere else in this file should treat that as a defect in this file and score under the registry.

| Category | Effect on E1 | Effect on E2 | Effect on totals |
| --- | --- | --- | --- |
| **Planted defect** | counted as recall | never a false positive | scored |
| **Adjudication item** | not counted | not counted | recorded verbatim, excluded from totals |
| **Observation item** | **not counted** | **not counted** | recorded verbatim, excluded from totals |

Every statement in every fixture belongs to exactly one of: planted defect, adjudication item, observation item, or protected. Protected is the default and needs no list.

**Observation items, in full** — statements where a finding is evidence about the *ruleset* rather than about the arm, so counting it either way would publish a known gap as a skill result:

- **D13.2** — "For major changes, add an entry to `docs/decisions/`." R3 as scoped passes it; no other rule reaches it. (W10 gap.)
- **D15.6** — "Where possible, tag the affected component." Hedges the trigger, not the strength. (W10 gap.)
- **D16.1** and **D16.2** — the force-push contradiction and the worked example omitting its own `Test plan:` line. R5 is scoped to rule-versus-rule, and an example is not a rule. (W13 gap.)
- **Scenario 12a and 12c R1-section findings** — a finding demanding a dedicated rules section, which the shipped R1 text licenses. (W9 verdict; see B3.)
- **Scenario 12b, an R1 finding grounded in retrieval pressure** — the number of distinct obligations packed into one unbroken block, rather than the absence of a section. A legitimate different answer to W9's question, which the scenario text already said; it was exempted there but not registered. **Added 2026-08-24 (round-2 review).**
- **Scenario 12b, R4 findings against the seat-count sentences.** The fixture genuinely contains compound obligations there, so an R4 finding is correct and is evidence about neither R1's compact/long criterion nor false-positive discipline. Exempted in the scenario text but not registered. **Added 2026-08-24 (round-2 review).**

**Adjudication items, in full:**

- **D15.8** — "Avoid promising a fix date in the first reply."
- **B13.1** — "Read the linked design document in full before proposing an approach." **Registered by treatment, not unconditionally (amended 2026-08-24, round-2 review):** leaving it alone, or escalating it to the author, is adjudicated and counted under neither endpoint. A **definitive rewrite inventing an artifact the author never asked for is an E2 false positive.** The earlier entry excluded the statement globally while scenario 13 said one treatment of it counts as a false positive, so registry and scenario disagreed; the split is by treatment because that is where the two documents actually differed.
- **A16.1** — "Reviewers should reject a pull request that force-pushes over `main`." (scenario 16, Notes section). **Added 2026-08-24.** B2 named this statement specifically: it is itself a hedged rule ("should") sitting in a Notes section, so an arm raising an R2 or R1 finding against it is arguably right, and B2 says it should score as "neither recall nor a false positive". The complement definition alone would have made it protected by default and scored such a finding as a false positive — reintroducing the defect B2 raised, in the fix for B2. It is an adjudication item: recorded verbatim, counted under neither endpoint.

Scenario 10's adjudication list is empty (B1). No other scenario has adjudication items.

## Scenario 9R — trigger discrimination

**Endpoint:** selection, and body loading, scored separately.

**Correct selection:** `separating-context-from-constraints`.

**Known positive required before any negative is trusted:** run part 2 in a session where the skill was never loaded, and confirm no `R1`–`R5` id appears in the output. None of the five catalog descriptions contains such an id, so the check is sound in principle; it must still be demonstrated to fire.

**Amended 2026-08-24 (B8) — the body-loading detector is narrowed to its one calibrated branch.**

Superseded: assertion 4 passed on an R1–R5 id, *or* the six-field finding format, *or* an explicit "clean — no findings" verdict.
A three-way disjunction cannot be trusted when the control demonstrates only one branch.
An unloaded model can readily emit six finding-like fields, and "clean — no findings" is a phrase any auditor might reach for unprompted, so the detector could pass with the body never loaded — which would report W12 as closed on no evidence.

Body loading is now scored on **the appearance of an `R1`–`R5` id and nothing else**, because that is the artifact the known positive demonstrably rules out.
The other two branches are still **recorded**, as observations, and never as evidence that the body loaded:

- `six-field-format-without-id` — the output uses the finding format but names no rule id.
- `clean-verdict-without-id` — the output states a clean outcome but names no rule id.

Either observation on an arm whose selection was correct means the detector is uninformative for that arm, not that the body failed to load; record it and re-run that rep.
If a future cell wants those branches as evidence, each needs its own known positive: an unloaded session that produces the artifact, demonstrating the branch can fire without the body.

**Reachable verdict in which nothing changes:** selection correct and body loading confirmed by an R1–R5 id. W12 then closes with the catalog rebuilt.
~~W12 then closes with the catalog rebuilt and `m12` — the `openai.yaml` short-description deviation — left alone, since it is only changed if this test shows a selection failure.~~
**Superseded 2026-09-01** — `m12` is no longer conditional on 9R in either direction; see the amended sequencing below.

**Sequencing (issue #162). Amended 2026-09-01.**
Superseded text, retained in full because it stated the sequence this file was executing:

> `agents/openai.yaml`'s `short_description` ("Audit agent instructions for ambiguous rules") covers R2 only, while the skill also audits buried (R1), unverifiable (R3), compound (R4), and conflicting (R5) rules; under-triggering is the plausible effect.
> It is not edited until 9R has run, because 9R is the only valid trigger instrument this skill has — scenario 9 measured a hand-written catalog line that is not the shipped frontmatter, so its 3/3 result measured a string no agent will ever see.
> Revising routing metadata before a valid trigger test exists is the untested-edit pattern this skill's history keeps punishing.
> Order: run 9R, record the arm, then revise the yaml, then re-run 9R against the revised catalog and record that arm separately.

Two facts retire that sequence, and the second retires its premise.
First, 9R's catalog is the five verbatim frontmatter descriptions (`../scenarios.md`, "Scenario 9R", and `../bin/check-9r-catalog.py`); `agents/openai.yaml` is not in it, so a yaml edit changes nothing 9R reads, and the planned re-run would have validated the edit with an instrument that never traverses it (found by Codex, 2026-09-01, job `ac8bcdbe5d364458b59cd93f648dad79`).
Second, `short_description` is not a model-visible trigger surface in either harness.
OpenAI's skill documentation (learn.chatgpt.com/docs/build-skills, fetched 2026-09-01) lists it under `interface` as "Optional user-facing description" and states that "ChatGPT and Codex start with each skill's name and description, then load the full `SKILL.md` instructions when they decide to use that skill"; Codex's own bundled `skill-creator` calls `agents/openai.yaml` "UI-facing metadata such as `display_name`, `short_description`, and `default_prompt`".
Claude Code's documentation (code.claude.com/docs/en/skills, fetched 2026-09-01) says of the frontmatter `description`: "Claude uses this to decide when to apply the skill", and "skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked".
So the frontmatter description is the selection surface in both harnesses, 9R measures the one surface that exists, and `agents/openai.yaml` is a human-facing label.

Consequences: `m12` is reclassified **text-only** — a UI-label wording choice that owes no arm and supports no trigger claim in either direction; the "re-run 9R against the revised catalog" step is struck; issue #162 keeps its first half (retire scenario 9, run 9R) and loses its second (re-measure triggering after the yaml edit).
`../bin/check-9r-catalog.py` needs no change: frontmatter is the right surface.

**Part 1n — negative control (added 2026-09-01, review finding F5).**
Scenario 9 and 9R test only that this skill is selected when it should be.
Nothing tests that it is *not* selected when it should not be, and the frontmatter's opening clause — "Use when auditing or reviewing a skill" — fires on any skill review.
Two requests are added to `../scenarios.md`'s 9R section, each against the same verbatim catalog and each with a preregistered correct alternative: **1n-a**, a README that has grown to thousands of words and is re-read by every agent session → `agent-friendly-docs`; **1n-b**, an MCP server whose agents keep calling the wrong tool among many → `agent-friendly-mcp`.
Both are deliberately easy: the point is a calibrated over-selection detector, not a hard discrimination.

Each request is scored on **two separate fields**, never merged: `over-selection` — `true` when `separating-context-from-constraints` is selected — and `correct-alternative` — `true` when the preregistered alternative is selected.
A run that selects neither this skill nor the alternative is recorded as `over-selection = false, correct-alternative = false`; it is not a pass, because it shows nothing about routing.

**Gating.** Part 1n's results are void unless part 1 selected this skill in the same model, harness, and catalog condition.
Part 1 is the known positive: it demonstrates that the instrument can select this skill at all, so a `false` on `over-selection` comes from an instrument that can fire.
Part 1 has not run, so 1n has no known positive until it does.

**Reachable verdict in which nothing changes:** `over-selection = false` on both requests.
W21 then has no over-triggering evidence, and its description decision rests on part 1 and body loading alone.
That verdict closes review finding F5; it does not close W21.

## Scenario 10 — ledger-service (long sectioned document)

Planted defects, high-consequence:

- D10.1 — "any change touching the `postings` package must be accompanied by a migration plan reviewed by the data team before it is merged", inside a narrative Overview paragraph about the 2024 platform split.
- D10.2 — "any test touching the `postings` package must run inside a transaction that is rolled back at the end", introduced with "It is worth noting that" inside a Testing paragraph about suite timings.
- D10.3 — "before adding a currency you must open an issue tagged `finance-review` and get sign-off from the finance team", introduced with "By the way," in the Appendix.
- D10.4 — "Keep the changelog entries readable." — untestable rule in the Rules section (R3).
- D10.5 — "Generally use the `internal/` package for anything not consumed by the public API." — ambiguous strength (R2).
- D10.8 — "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`." A self-contained mandatory prohibition in the Appendix (R1). **Added 2026-08-24 (B1); previously on the correctly-placed list.**
- D10.9 — "Log lines must never include the raw `account_number` field — the log pipeline is replicated to a lower-trust analytics store." A self-contained mandatory prohibition in the Observability section (R1). **Added 2026-08-24 (B1); previously adjudication item A10.2.**
- D10.10 — "Never construct a `Money` value from a floating-point literal." A self-contained mandatory prohibition in the Working-with-money section (R1). **Added 2026-08-24 (B1, second pass); previously adjudication item A10.1, then briefly protected.**
- D10.11 — "Adding a currency: update `fx/currencies.go` and the `currency_code` enum migration together." A co-update obligation in the Appendix (R1). **Added 2026-08-24 (B1, second pass); previously on the correctly-placed list.**

Planted defects, low-consequence:

- D10.6 — the trailing rationale on the `make test` bullet ("this is the same suite CI runs, so catching failures locally saves a round trip…"): context inside the Rules section. The obligation itself remains clear and checkable.
- D10.7 — the rationale clauses on the table-driven-tests bullet ("which the team has found easier to extend…, and which match the style of…"): same defect, same direction.

E3 ambiguous statements: D10.5 only.

E7 lists: high-consequence is {D10.1, D10.2, D10.3, D10.4, D10.5, D10.8, D10.9, D10.10, D10.11}; low-consequence is {D10.6, D10.7}. **Amended 2026-08-24 (B1):** D10.8, D10.9, and D10.10 are high-consequence — mandatory prohibitions whose loss permits a prohibited action, the same consequence class as D10.1–D10.3. D10.11 is high-consequence because a half-applied currency update is the failure its own Appendix warns about.
Severity discriminates on this fixture if at least one low-consequence finding is labelled **minor** while at least one high-consequence finding is labelled **material**.
If every finding is **material**, that is the W14 evidence, and the item proceeds to a decision among sharpening the material threshold, adding a third level, and dropping severity for ordering.

Correctly placed, must not be criticized:

- The 2024 platform split and `billing_v1` namespace sentence.
- "Most contributors find the codebase easier to navigate after reading the architecture overview in `docs/architecture.md`."
- The bootstrap description, the four-minute timing, and the port-5432 note.
- The `Money` representation sentence, the no-`Add`-method sentence, and the banker's-rounding sentence. (The float-literal prohibition beside them is D10.10, not protected.)
- The unit/integration split and timing sentences, and the CI race-detector sentence.
- The trace-id, structured-logs, and Grafana-folder sentences.
- The release-job schedule and promotion sentences.
- "Historically the team deployed by hand, and the runbook in `docs/runbook-legacy.md` still describes that process; it is retained for incident archaeology and is not current policy." **This is also an R5 false-positive probe:** an arm that reports a conflict between the legacy runbook and the release job has ignored the sentence's own explicit precedence statement.
- The `make fixtures` line, and "Clone the repository and run `make bootstrap`." — both procedural how-tos, failing prong (a). **Amended 2026-08-24 (B1):** the `cmd/backfill` line is now D10.8 and the currency-file line is now D10.11; neither is protected.
- Every other statement in the fixture, per E2's complement definition (B2).

Adjudication required, scored but counted as neither recall nor false positive:

**None. Amended 2026-08-24 (B1):** this list is now empty for scenario 10. A10.1 is planted defect D10.10 and A10.2 is planted defect D10.9, both by the stated criterion.

*Superseded 2026-08-24 by the B1 amendment below; retained as the original reasoning.*
~~Whether R1 requires these to move into the Rules section, or permits a clearly marked mandatory sentence to sit beside the semantics it depends on, is exactly the question W9 asks and this plan does not pre-answer.
Record each arm's treatment of A10.1 and A10.2 verbatim.
The two items are deliberately parallel, so an arm that treats them differently has no criterion.~~

The last sentence was the defect B1 found: A10.1 and A10.2 are *not* parallel — one depends on its passage and one does not — and the criterion below is what makes the difference statable instead of leaving an arm to guess.

**Amended 2026-08-24 (B1) — one criterion for every locally scoped mandatory rule in this fixture.**

The lists as authored were incoherent. They protected two mandatory directives sitting outside `## Rules` — the `cmd/backfill` backfilling line and the port-5432 line — while planting D10.3, a mandatory directive sitting outside `## Rules` in the same Appendix, and leaving A10.1 and A10.2 undecided for the same shape a third time.
Three treatments of one structure means an arm can be scored inconsistently for structurally equivalent statements, and has no way to infer which answer is wanted.

**Criterion, restated 2026-08-24 after a cross-model review found the first prong was never actually defined.**

The first draft said "(a) mandatory in force and (b) not dependent on the surrounding passage", but never said what makes a statement mandatory *in force*. Applied literally to the fixture, prong (a) is satisfied by every imperative sentence, including "Clone the repository and run `make bootstrap`." — which the draft's table silently protected while planting structurally identical statements. That is the same defect B1 raised, surviving inside B1's own fix.

A statement outside the Rules section is a **planted defect** when **both** prongs hold:

- **(a) Binding in force.** It forecloses an option the reader could otherwise take — a prohibition, or an obligation whose omission is an error in itself. A statement that only answers *how do I do X* for a reader already committed to X is **procedural**, not binding, however imperative its grammar.
  **Operational test, added 2026-08-24 (round-2 review):** ask *what happens if a reader ignores this?* If the answer is "they have violated a policy", it is binding. If the answer is "they fail to accomplish the thing they were already trying to do, and find out immediately", it is procedural. A remedy for a failure the document itself describes is procedural under this test, because the failure is its own enforcement.
  Prong (a) was applied inconsistently without this test: the port-5432 remedy was marked *binding* and then protected via prong (b), which happened to reach the right category by the wrong route. A criterion whose ten rows a second scorer cannot reproduce is the defect B1 raised, so the route matters even where the verdict does not.
- **(b) Liftable.** Applying it does not require semantics stated only in the surrounding passage. A statement that cannot be obeyed without its neighbours stays where it is.

Every directive outside `## Rules` in the fixture, enumerated in document order — not a sample:

| Statement | (a) binding? | (b) liftable? | Verdict |
| --- | --- | --- | --- |
| "…must be accompanied by a migration plan reviewed by the data team…" | yes | yes | **D10.1** planted |
| "Clone the repository and run `make bootstrap`." | **no** — procedural how-to | — | protected |
| "If Postgres is already listening on port 5432 … stop the other instance first." | **no** — procedural: it tells a reader already committed to bootstrapping how to get past a stated failure | (not reached) | protected |
| "Never construct a `Money` value from a floating-point literal." | yes | **yes** | **D10.10** planted *(was A10.1)* |
| "…any test touching the `postings` package must run inside a transaction…" | yes | yes | **D10.2** planted |
| "Log lines must never include the raw `account_number` field…" | yes | yes | **D10.9** planted *(was A10.2)* |
| "Regenerating fixtures: `make fixtures`." | **no** — procedural how-to | — | protected |
| "Adding a currency: update `fx/currencies.go` and the `currency_code` enum migration together." | yes — "together" forecloses updating one alone | yes | **D10.11** planted |
| "By the way, before adding a currency you must open an issue tagged `finance-review`…" | yes | yes | **D10.3** planted |
| "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`." | yes | yes | **D10.8** planted |

**The enumeration above was checked mechanically, not by eye.** Every line of the scenario-10 fixture outside `## Rules` was extracted and filtered for directive shape (a modal, a mandatory word, or a sentence-initial imperative verb). That returned exactly ten statements, matching the ten rows above in document order. Two near-misses were inspected and are correctly protected as load-bearing facts rather than directives: the no-`Add`-method sentence ("conversion goes through `fx.Convert`, which **requires** an explicit rate source") and the release-job sentence ("promotes to production **only if** the smoke suite passes"). Both constrain what the system does, not what the reader must do.

Statements inside `## Rules` are outside this criterion's reach: it governs placement of rules that sit elsewhere. "Never commit directly to `main`." is inside `## Rules` and is protected, as are the other statements B2 named as omitted from the enumerated list — the Go/three-clusters sentence, the core obligation of the table-driven-tests bullet, and the integration-tests-are-slow sentence.

**A10.1's protection is withdrawn.** The draft claimed it "cannot be lifted into the Rules section without the `Money` representation sentence it sits beside". That claim does not survive contact with the fixture: "Never construct a `Money` value from a floating-point literal." is a complete prohibition in one sentence, and a reader can obey it without knowing how `Money` is represented internally. B1's original observation — that A10.1 and A10.2 are deliberately parallel — was right, and the draft's split between them was the error. Both are now planted defects, and the criterion no longer has to carry a distinction the fixture does not support.

**The adjudication list for this fixture is now empty**, and E2 is the complement of the E2 exclusion registry per B2.
This costs the fixture its "record how the arm treats a deliberately undecided pair" observation. That observation was worth less than a coherent E2, which is the endpoint the whole wave rests on.

**W9 can still fail this criterion, and that outcome is preregistered as reachable.** The live W9 probes are now the two procedural how-tos — "Clone the repository and run `make bootstrap`." and "Regenerating fixtures: `make fixtures`." — and the port-5432 remedy. An arm that flags any of them has applied "imperative sentences belong in the Rules section, full stop", ignoring prong (a) or prong (b). Under E2 that is a false positive, and it is simultaneously evidence for W9 that R1's compact/long sentence needs both prongs written into it. Record both readings; do not let the E2 count silently stand in for the W9 verdict.

**Reps (N5).** Three per arm, as the standing requirement already sets for this scenario.

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

**Amended 2026-08-24 (B3) — an R1 section finding on 12a and 12c is the W9 verdict, and is excluded from E2 by name.**

`SKILL.md:42` reads "Treat a document with labeled sections or rules distributed across multiple paragraphs as long-form, and place its rules in a dedicated labeled section."
12a has `## Purpose` and `## Usage`; 12c has `## Procedure` and `## Background`.
Both therefore have labeled sections, so under the shipped wording an arm that demands a dedicated rules section is applying R1 *correctly* — while this file declares that finding incorrect.

Scoring it as a false positive would punish a faithful application of the rule and corrupt E2, the endpoint the wave rests on.

- A finding on 12a or 12c grounded in **the absence of a dedicated rules section** is recorded as **`W9-verdict`** — neither recall nor a false positive, and excluded from the E2 count by name.
- Every `W9-verdict` observation is direct evidence that R1's compact/long sentence needs rewording, because it shows the shipped text producing the outcome this fixture was built to call wrong.
- A finding on 12a or 12c grounded in **anything else** — a manufactured R2/R3/R4/R5 defect in the prose — remains an ordinary E2 false positive.
- 12c's `--force` prohibition keeps its own treatment: a finding proposing to move it out of step 3, away from the step whose semantics it modifies, is an E2 false positive under the same dependency criterion B1 states for scenario 10.

This follows `../scenarios.md`'s standing rule that an assertion the with-skill run misses is "a finding against the skill, not against the agent". B3's contribution is that the finding must also be kept out of the false-positive arithmetic, not merely noted in prose.

**Reachable verdict in which nothing changes:** all three sub-cases clean, with no `W9-verdict` observations.
R1's compact/long sentence then stands as written and W9 closes with a documentation note rather than a rewording.
A run of `W9-verdict` observations is the opposite verdict, and the B1 dependency criterion — "a rule that cannot be lifted without its passage stays put" — is the candidate wording W9 would adopt.

**Reps (N5):** three per arm. Scenarios 12 and 14 are the pure false-positive probes, and a single stochastic manufactured finding would otherwise decide W9 or W4 on its own.

## Scenario 13 — R3's scope

Planted defects:

- D13.1 — "Keep the review tone professional." **This is the known positive.** If an arm misses it, that arm's other R3 results are not evidence.
**Observation item (moved out of "Planted defects" 2026-08-24, per the registry above):**

- D13.2 — "For major changes, add an entry to `docs/decisions/`." The action is observable and the trigger is undecidable, so R3 as scoped passes it and no other rule catches it. An arm that flags it — under any rule id, or under none — is evidence that the gap is closable without new wording; an arm that passes over it is **not** a recall miss.
  It was listed as a planted defect, which meant E1 counted it: an arm applying R3 correctly would have been scored as missing a defect, and the suite would have published a ruleset gap as a skill failure. This file wins over `../scenarios.md` on conflict, so leaving it here would have overridden that file's observation-only treatment.

Boundary item, recorded but not counted as a false positive when treated as a request for an author decision:

- B13.1 — "Read the linked design document in full before proposing an approach." A legitimate process obligation whose satisfaction is not reliably observable. A definitive rewrite inventing an artifact the author never asked for **is** a false positive; a request for an author decision is not.

  **Amended 2026-08-24 (N8).** Superseded phrase: "that leaves no artifact". R3 names tool calls as admissible evidence (`SKILL.md:51`, "output, tool calls, repository state, or process artifacts"), and reading a linked document leaves a tool trace, so "no artifact" overstates the case.
  What survives is weaker and is what the item now says: the obligation is to read *in full*, and a tool trace shows that a document was opened, not that it was read completely. So the rule is partially observable, which is the boundary this item probes.
  An arm that passes over B13.1 because a tool trace satisfies it has read R3 correctly and is not scored as a miss.

Correctly placed, must not be criticized: the single-pull-request-comment rule, the external-dependency approval rule, and the Context paragraph.

**Reachable verdict in which nothing changes:** D13.1 caught (it is the known positive and the only scored recall item here), D13.2 either flagged or passed over, and B13.1 left alone or escalated to the author.
(**Amended 2026-08-24:** this required D13.2 to be *flagged*, contradicting the same section's statement that R3 as written passes it.)
R3 then keeps observable-evidence framing and W10's first half closes with no change.

## Scenario 14 — R5 semantic scope

No planted defects. This scenario measures E2 only, and is held out from the scenario-2 fixture that the `SKILL.md:59` scope guard was fitted to — "A restriction on the representation of one field does not restrict unrelated fields unless the document explicitly restricts the whole input object." (Repinned 2026-08-24 from `:58`.)

Correctly placed, must not be criticized: every sentence of the `schedule_report` description, and the schema.

An R5 finding pairing the `recipients` restriction with any other field is the specific false positive this fixture exists to detect.
An R1 finding raised because the constraints live inline in a description field is a second.

Known positive: scenario 8 stands as the evidence that arms can find a reachable R5 conflict. This scenario is not scored as R5 recall.

**Amended 2026-08-24 (N6, issue #160) — the historical control is replaced, and the ablation runs in the same batch.**

Superseded: scenario 8's 2026-07-11 run was to stand as the known positive. That run was made under a different configuration, pins no `SKILL.md` blob, and predates `f0441f3`'s rewrite of R1/R3/R5 — so it cannot show that *these* arms, reading *this* wording, can still find a reachable R5 conflict. A clean result on scenario 14 measured against it would be a clean result from an unproven instrument.

This cell now requires three arms, dispatched together:

1. **Scenario 14, guard present.** The `schedule_report` fixture, current `SKILL.md`. Expected clean.
2. **Current known positive.** Scenario 8's fixture re-run under current `SKILL.md`, in the same batch, same model and harness. It must produce the R5 conflict finding. If it does not, arm 1's clean result carries no weight and the cell is void.
3. **Guard ablation.** Scenario 14's fixture against a `SKILL.md` variant with the scope-guard sentence (`:59`) deleted and nothing else changed. This is the arm that attributes the result to the sentence rather than to the fixture being easy.

The ablation variant is built by deleting exactly one line; its blob hash is recorded in the run artifact like any other arm's, and it is never committed to `main`.

**The decision this cell settles (issue #160).** The guard reads "A restriction on the representation of one field does not restrict unrelated fields unless the document explicitly restricts the whole input object" (`SKILL.md:59` — cited as `:58` in issue #160 and in `../scenarios.md`, both pre-#163 numbering).
A 2026-08-23 consolidation audit proposed deleting it as a special case of the preceding sentence; a Codex cross-review reversed that, because [`../runs/2026-07-11-scenario2-with-skill.md`](../runs/2026-07-11-scenario2-with-skill.md) records two treatment runs that misread "accepts only a channel_id" as banning the unrelated `confirmed` field, and the sentence was added to stop exactly that.
The sentence is nonetheless **fitted** to scenario 2 (`../scenarios.md` says so), and fitted evidence does not establish that it generalizes.

Reading the three arms:

| Arm 1 (guard) | Arm 3 (ablated) | Verdict |
| --- | --- | --- |
| clean | clean | the guard is doing no work on held-out input; demote it to a worked example under W4 |
| clean | R5 false positive | the guard generalizes beyond the fixture it was fitted to; **keep it as a rule** |
| R5 false positive | R5 false positive | the guard does not prevent the misreading it was written for; W4 reopens on stronger evidence than redundancy |
| R5 false positive | clean | incoherent; re-run before interpreting |

Do not delete the sentence on a redundancy argument alone — that argument was already made and already reversed.

**Reps (N5):** three per arm. This is a pure false-positive probe, and one stochastic manufactured finding would otherwise decide W4 on its own.

**Reachable verdict in which nothing changes:** arm 1 clean, arm 2 positive, arm 3 producing the false positive.
The guard is then kept as a rule on the strength of two independent fixtures plus an ablation, and W4 closes with `SKILL.md:59` untouched.

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

**Amended 2026-08-24 (B5) — the twelve are not uniformly R2 defects, and are adjudicated individually here.**

A 12/12 recall assertion would have marked semantically careful treatment as failed recall, and the usability endpoint would then measure an author resolving ambiguities the scorer created.
Each statement is adjudicated against R2 ("Only ambiguous strength is a finding — a hedge … that leaves the reader unable to tell whether the statement binds", `SKILL.md:49`) and R3 as scoped above.

| # | Statement | Verdict |
| --- | --- | --- |
| D15.1 | "Generally assign severity before assigning an owner." | R2 defect |
| D15.2 | "Try to reproduce the reported behavior before asking the reporter for more detail." | R2 defect |
| D15.3 | "Usually escalate to on-call when a ticket mentions data loss." | R2 defect |
| D15.4 | "It is preferable to link the ticket to an existing issue rather than opening a new one." | R2 defect |
| D15.5 | "Consider closing tickets with no reporter response after fourteen days." | R2 defect, **R3 secondary admissible** |
| D15.6 | "Where possible, tag the affected component." | **reclassified: W10-gap observation, not a scored defect** |
| D15.7 | "Tickets from enterprise accounts should normally be triaged first." | R2 defect |
| D15.8 | "Avoid promising a fix date in the first reply." | **reclassified: adjudication item** |
| D15.9 | "Ideally the reproduction steps are recorded in the ticket itself rather than in a linked document." | R2 defect |
| D15.10 | "Feel free to reassign a ticket if it lands in the wrong queue." | **reclassified: correctly placed — a false-positive probe** |
| D15.11 | "Aim to keep the triage note under a paragraph." | R2 defect, **secondary R3 verdict withdrawn** |
| D15.12 | "Duplicate tickets are typically closed in favor of the older one." | R2 defect |

Reasoning for the four that moved:

- **D15.10 is an explicit permission, not an unresolved strength.** "Feel free to" tells the reader clearly that the action is optional; nothing about whether it binds is in doubt. R2's own text says defaults and defeasible guidance are legitimate rules, not failed constraints. It joins the correctly-placed list, where it does useful work as a false-positive probe: an arm flagging every hedge-shaped phrase will flag it.
- **D15.8 is genuinely contestable.** "Avoid X" is a direct negative imperative and a careful auditor may read it as binding; another may read it as softer than "never". Neither reading is unreasonable, so it is scored as an adjudication item — recorded verbatim, counted as neither recall nor false positive.
- **D15.11's secondary R3 verdict is withdrawn.** "Under a paragraph" is a bounded quantity, and `SKILL.md:33` offers "Chat responses of four sentences or fewer unless asked" as its own example of a checkable directive. Holding D15.11 unverifiable while that example passes is a contradiction the fixture should not carry. Note the repin: that example now sits in Core Concept rather than in the Rules section, so it is an illustration, not a rule-section precedent — but as an illustration of checkability it is exactly on point. R2 only.
- **D15.6 exposes the R3 gap rather than an R2 defect.** "Where possible" hedges the *trigger*, not the strength: the statement binds whenever tagging is possible. R2 governs strength and does not reach it; R3 as scoped above explicitly does not reach undecidable triggers. So no rule in R1–R5 catches it. It is recorded as a **W10-gap observation**, alongside scenario 13's D13.2 and the 2026-08-23 scenario-2 arm, and excluded from both E1 and E2. An arm that flags it under any id is evidence the gap is closable without new wording; an arm that passes over it is not scored as a miss.

**E1 for this fixture is therefore 9, not 12.** The nine R2 defects are D15.1, D15.2, D15.3, D15.4, D15.5, D15.7, D15.9, D15.11, D15.12.

All nine, plus D15.8, are E3 ambiguous statements. D15.6 and D15.10 are not: neither leaves the reader unsure what was intended.

Correctly placed, must not be criticized: "Acknowledge every ticket within one business day.", "Never share another customer's ticket contents with a reporter.", the Context paragraph, and D15.10.

**Usability endpoint.** The premise under test — that an exhaustive author-decision contract makes reports unusable at volume — was an unmeasured behavioral prediction, so it gets an operational definition rather than a judgment call.
A second agent receives only the original document and the report, is told it is the document's author, and is asked to resolve every decision the report raises and produce the revised document.
Record: how many of the **nine** it resolves, whether it asks for clarification instead, how many it silently drops, and the report's word count as a multiple of the target's.
The author agent does not receive this file.

**Amended 2026-08-24 (B5, N1).** "Twelve" becomes "nine" throughout, per the adjudication above.
The measure is the report's **word count as a multiple of the target's word count** — not wall-clock output length, which `../scenarios.md` recorded and which is not a property of the report at all.
The **silent-drop count** is a first-class record, not a yes/no: a decision the author agent neither resolves nor asks about is the failure mode the usability premise predicts, and counting them is how "unusable at volume" becomes measurable rather than asserted.

**Reps (N9 note).** The usability endpoint runs three times, not once. A single author agent's resolution rate is a weak instrument, and this file's own variance evidence is the reason the standing requirement exists.

**Reachable verdict in which nothing changes:** recall 9/9, no silent selections, and the author agent resolves all nine.
W11 then closes with "the premise does not hold" recorded, and `SKILL.md:59`, `:84`, and `:86` untouched.
The scenario-3 regression cell stays green in every branch of this item.

## Scenario 16 — duplicated and self-contradicted rules

**Observation items (renamed from "Planted defects" 2026-08-24, per the registry above).**
Both were listed as planted defects while this same section said a run reporting neither "is evidence of the gap, not a failure of the arm".
E1 counts planted defects, so the two statements contradicted each other and the recall total would have mixed "the skill worked" with "R1–R5 has a known gap" — the exact defect N1 fixes in the assertion lists.
Neither is counted under E1 or E2. Both are recorded verbatim, with the rule id each arm attaches, because that is the W13 decision input.

- D16.1 — "Never force-push to any branch." in the Rules section against "Force-pushing a personal feature branch is fine and happens routinely during rebases." in the Notes section. One rule stated twice with divergent scope; the second statement narrows the first without saying so.
- D16.2 — the worked example omits the `Test plan:` line its own Rules section requires. A rule contradicted by the document's own example.

Correctly placed, must not be criticized: the conventional-commit-prefix rule, which the example satisfies; the example's body text.

**Adjudication item (added 2026-08-24):** A16.1 — "Reviewers should reject a pull request that force-pushes over `main`." See the registry above.

Both defects may be reported under R5, under a new id, or with no id.
A run that reports neither is evidence of the gap, not a failure of the arm — no rule in R1–R5 clearly reaches either.
(One qualification, from the design review's "considered and not carried": D16.1 *is* arguably reachable under R5's "two rules prescribe incompatible outcomes for the same decision", so "no rule detects either" overstates the case for D16.1 while holding for D16.2.)
Record the rule id each arm attaches, because that is the W13 decision input: an arm reading R5's "two rules prescribe incompatible outcomes for the same decision" as covering D16.1 makes a clarification sufficient, while an arm that needs a new id argues for a sixth rule.

D16.2 is the harder half. R5 is scoped to rule-versus-rule; an example is not a rule.

**Reachable verdict in which nothing changes:** both reported coherently under R5.
W13 then closes as an R5 clarification with no sixth rule.

## Scenario 17 — redaction

Planted defects:

- D17.1 — the token bullet: **a compound obligation (authenticate, and rotate quarterly)**, R4.
- D17.2 — the escalation bullet: **a compound obligation (escalate, and record the ticket id)**, R4.

**Amended 2026-08-24 (N7) — the inlined sensitive values are not structural defects.**

Superseded text: D17.1 and D17.2 each named "a credential value inlined in a rule" and "personal data … inlined in a rule" as part of the planted defect.
No rule in R1–R5 forbids a credential or personal data appearing in the *target*. `SKILL.md:78` governs only how the *auditor* quotes such text ("Quoted text is redacted for credentials, personal data, and dangerous payloads").
Scoring the target's content as a structural defect would have made E1 unreachable for an arm applying R1–R5 correctly, and would have counted a security observation toward a separation endpoint.

E1 for this fixture is therefore the two R4 compounds and nothing else.
Redaction is scored under E5 alone, where it belongs.
An arm that additionally *notes* the credential's presence is neither credited under E1 nor penalised under E2; record the observation.

**Also amended (N7, second half).** `not-quoted` means two different things and this file recorded only one.
For a **with-skill arm**, `not-quoted` is contract non-adherence: the finding format requires quoted text (`SKILL.md:77`), so an arm that raises the finding without quoting has skipped a contracted field.
For a **baseline**, `not-quoted` is genuinely unexercised behavior: no contract binds it, and the redaction path simply never ran.
Record which of the two applies. Filing both as "fixture failure" loses the distinction, and it was that conflation that let scenario 4's cell report a passed conditional assertion while redaction never ran at all.

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

- D18.1 — "Engineers submit batches to the production cluster only after the staging replay has completed without errors." A binding rule stated declaratively and buried in a Background paragraph, in a document that has a Rules section.

Correctly placed, must not be criticized — imperative in form, not binding in function:

- "Remember that the `--dry-run` flag still writes to the audit log." (load-bearing fact)
- "Note that `retries` counts attempts after the first, so `retries: 2` means three total attempts." (load-bearing fact)
- "`INGEST_ENV` holds the target cluster name, not a region." (load-bearing fact)
- "Feel free to skim `docs/ingest-overview.md` before making changes." (discretionary context)

**Amended 2026-08-24 (B4) — both probes are rewritten, because a careful auditor was punished in both directions.**

The fixture's endpoint rested on two classifications an auditor could legitimately have made the other way:

- D18.1 read "Batches are submitted to the production cluster only after the staging replay has completed without errors." It had no agent as its subject and sat beside "The pipeline was rebuilt in 2025…", so it read as a *description of what the pipeline does* — a load-bearing fact — at least as naturally as an obligation on the reader. An arm classifying it as a fact was scored as missing the only planted defect.
- The `INGEST_ENV` probe read "Read `INGEST_ENV` as the target cluster name, not as a region." That is an imperative directing how to interpret a variable, so it passes the litmus test's *direct* branch at `SKILL.md:22-23` ("Does this statement *direct* behavior or *inform* it?"). An arm flagging it was scored as a false positive for a defensible reading.

Superseded fixture text is the two sentences above; the replacements are in the lists.
D18.1 now names an agent — "**Engineers submit** batches…" — while keeping its declarative mood, so it is unambiguously an obligation on a reader and still not imperative in form. That preserves exactly the grammar/function mismatch the scenario exists to probe.
The `INGEST_ENV` probe is now a copular definition — "`INGEST_ENV` **holds** the target cluster name, not a region." — with no imperative verb to direct anything.

The remaining three protected statements keep their imperative-but-informing shape ("Remember", "Note", "Feel free"), so the asymmetry the scenario needs survives: three imperative non-rules against one declarative rule.
An arm sorting by grammatical mood still fails in both directions, which is what makes the endpoint diagnostic rather than a coin flip.

The alternative B4 offered — preregistering both as adjudication items and scoring the reasoning — was not taken. Scenario 18 has exactly one planted defect and four probes; moving two of the five to adjudication would leave the cell with too little scored surface to answer W16 at all.

**Reps:** three per arm, as the standing requirement already sets for this scenario.

Also correctly placed: the 2025 rebuild sentence, and "Set `retries` to at most 5."

The fixture is deliberately asymmetric: the four imperative-but-not-binding statements are the false-positive probe, and the single declarative-but-binding statement is the recall probe.
An arm sorting by grammatical mood fails both in opposite directions, which is what makes the endpoint diagnostic rather than a coin flip.

Question 2 of the litmus test is already known to be inert.
This scenario does not test it and does not rehabilitate it.

**Reachable verdict in which nothing changes:** D18.1 recalled and all four probes clean.
`SKILL.md:67` — "Classify each statement with the two-question litmus test" — then stands as written, along with the litmus test itself at `:20-24`, and W16 closes with the boundary confirmed rather than reworded. (Repinned 2026-08-24 from `:66`.)

## Non-blocking resolutions (Amended 2026-08-24)

N5, N6, N7, N8, and N11 are resolved in the scenarios above. The rest are resolved here.

**N1 — the assertion lists disagree with these endpoints in six places.**
`../scenarios.md` now cites endpoint ids instead of restating pass conditions, and observation-only items are kept out of the assertion totals.
This matters because the results table sums assertions, so wave 3 would otherwise publish X/Y totals mixing "the skill worked" with "the ruleset has a known gap".
Specifically: S10 assertion 6 accepted one of D10.6/D10.7 though both are planted; S10 assertion 9 asked only for non-uniform severity while E7 asks that severity track the two lists *in direction*; S13 assertion 2 required flagging D13.2 though this file says R3 as written passes it; S14 permitted "near-clean" though every statement is protected; S15 recorded wall-clock output length; S16 stated its two findings as pass/fail though reporting neither is evidence about the ruleset rather than a failure of the arm.

**N2 — E6 scores the finding, not the location field.**
Superseded: E6 scored the location field alone, so a finding reading "Overview section" plus a full quotation scored `ambiguous` even though it resolves perfectly for a reader — which would have answered W6 "yes, a convention is needed" by construction.
E6 now asks whether **the finding as a whole** resolves to exactly one statement, quoted text included.
The location field's content is recorded separately as the drift observation, which is the actual W6 input.
Note for W6: `references/example-audit.md:34` writes "Location: line 8." with no stated origin, and that example is the de facto convention today — it is where the invented "`---` frontmatter counts as line 1" rule came from.

**N3 — three assertions cannot fail, and are removed from the totals.**
S18's fifth begins "If the run states its classification", so silence passes it; it becomes an observation.
S12's "does not manufacture a finding elsewhere" has no operational definition; it is subsumed by E2, which now counts every statement outside the planted and adjudication lists.
9R's fifth is a scorer instruction, not an arm behavior; it moves to the scoring procedure.
A check that could not have failed is not evidence, and three of them inside a suite that publishes X/Y totals inflate every total they appear in.

**N4 — the scenario-11 transcript classifier needs its own known positive.**
The digest instrument is calibrated (see below); the "no write, edit, or shell mutation call in the transcript" check is not.
The control arm's transcript must be scored **positive** by the same classifier before any audit arm's negative is trusted. A classifier that cannot recognise the control's known mutation would return "clean" for every arm.

**N9 — the provenance enum cannot record two wave-3 arms.**
`Run:` took baseline, with-skill, or trigger "and nothing else", but scenario 11's control arm and scenario 15's author-usability agent are neither.
`../scenarios.md` now also accepts `control` and `author-usability`, and E9's rewrite-control arm is filed as `control`.

**N10 — every wave-3 defect class appears in the worked example.**
`references/example-audit.md` contains a rule buried in a Background paragraph, a "Generally try to" hedge, a context sentence inside `## Rules`, a compound obligation, and an unverifiable "Be careful with production."
A with-skill arm therefore has a template for all of it.
This does not invalidate the cells, but it **caps what they can attribute to R1–R5 transfer as opposed to imitation**, and no wave-3 result may be quoted as evidence of transfer without this caveat attached.
It also raises the value of E9: an arm imitating the example's structure is the same mechanism that would make it imitate the example's after-document.

**N12 — the synthetic credential and push protection.**
`sk_live_4Kd82hRnQm1PzVx7` (scenario 17's fixture) was pushed to `origin/separating-context-wave3` on 2026-08-24 and **was not blocked**.

That is a weak negative, and is recorded as one rather than as a clean result.
`GET /repos/briandconnelly/skills` reports `secret_scanning: null` and `secret_scanning_push_protection: null` — not `enabled` — so it is not established that push protection was armed for this push. A disabled scanner and a non-matching token produce the same outcome, which is the failure mode this file keeps flagging elsewhere.
What is known independently: the token body is 16 characters where Stripe's live-key pattern is longer, so a pattern miss is the likely explanation.
The practical question N12 raised — will the PR be blocked at push time — is answered: it was not.
The stronger claim, that the string cannot trip a secret scanner anywhere, is **not** established and should not be quoted from this.

**B6 and B7 — the fixture instrument.**
[`../fixtures/scenario11/regenerate.sh`](../fixtures/scenario11/regenerate.sh) was rewritten on 2026-08-24 and recalibrated.
`hash` is now the default subcommand; `regenerate` must be named explicitly (B6).
The target path now lives outside the repository, defaulting to `${TMPDIR}/scenario11-fixture` and overridable with `SCENARIO11_TARGET_DIR`, so the arm is not handed a path that names the skill and sits one traversal from this file (B7).
Recalibrated 2026-08-24, all six cases observed: missing target exits 1; `regenerate` prints a digest; a bare run on an unchanged target reprints it; **a bare run after a mutation prints a different digest**; a bad argument exits 2; the target resolves outside the repository.
The fourth case is the B6 regression, and it was confirmed against the *old* script first — the old script reprinted the pristine digest after a real mutation, so the fix rests on an observed difference rather than on the review's description of one.

## Sealed prediction

The plan author's expectations for these cells are recorded outside this file and outside every scorer's inputs, and are opened only after scoring.
Nothing in this file states an expected outcome, because a preregistration that predicts its own result inside the document the executor reads is how the first draft of W1 broke its own blinding.

## Known gaps in this preregistration

Recorded rather than silently carried, since this file is itself an instruction document another agent will execute.

- ~~Scenario 10's adjudication items A10.1 and A10.2 have no correct answer here. That is deliberate — the question is W9's — but it means scenario 10's E2 count is a lower bound until W9 is decided.~~ **Closed 2026-08-24 (B1):** the dependency criterion gives both a verdict, scenario 10's adjudication list is empty, and E2 is no longer a lower bound on that fixture.
- Scenario 16's D16.2 has no rule that could catch it, so a recall figure there would be uninformative about the arms and informative only about the ruleset. **Amended 2026-08-24:** superseded phrase — "It is scored anyway". It is now an observation item, recorded but counted under neither E1 nor E2. Recording which arms notice without a rule telling them to is still the point; putting that in a recall total was the error.
- ~~Scenario 15's usability endpoint uses one author agent.~~ **Closed 2026-08-24 (B5):** it runs three times.
- ~~No fixture here tests `SKILL.md:27`'s long-context claim directly.~~ **Closed 2026-08-24 by the merge, not by a fixture.** PR #163 replaced "Rules camouflaged as narration are lost under long-context pressure" with "Narrative placement does not itself signal that a rule binds" (`SKILL.md:27`) — which is the structural claim W2 asked for, and which scenario 10 does measure. W2's separate downstream-compliance experiment stays optional, as W2 always said. Recorded here because a gap that closes through an unrelated edit is easy to keep carrying by inertia.

Gaps this amendment opens, recorded in the same spirit:

- **The W10 gap now has three live instances and no owner in R1–R5.** Scenario 13's D13.2, scenario 15's D15.6, and the 2026-08-23 scenario-2 arm all describe a rule whose applicability or exception-satisfying evidence is undecidable. R3 as scoped here passes all three; R2 does not reach them. Wave 3 will therefore produce a coherent E2 while leaving a real defect class unmeasured, and no wave-3 result may be quoted as evidence that R1–R5 are complete.
- **E9's control is a new arm shape and is uncalibrated beyond its own known positive.** It shows that an arm *asked* for a rewritten document produces one. It does not establish the base rate at which arms produce one unasked, which is the quantity W17 wants; three reps per fixture is a small sample for a behavior observed once in the archive.
- **The B1 dependency criterion is itself untested.** It is applied to scenario 10 by the author's judgment of which statements need their passage. Scenario 12 tests the same criterion from the other direction, but nothing here validates the eight individual verdicts in that table, and a scorer who disagrees with one of them will score that statement the other way.
- **There is no citation checker in this repository at all.** Superseded text: "The repo's `scripts/check-citations.py` does not cover this skill (`DEFAULT_SCOPE` is `hypothesis-driven-analysis` only), and probes to calibrate it against a bogus citation did not fire even with the scope widened." That script left with the `01634d9` extraction (PR #155) and no longer exists here; `prek run --all-files` passes on this skill's files because **no hook covers this skill**, not because anything checked them.
  Every line and file reference in this file — including the 2026-08-24 repin — was resolved by reading `SKILL.md` and matching the cited sentence, by hand. A future renumbering has no automated guard, which is why the repinned citations now quote their sentences.
