# Wave 3 design review — 2026-08-08

Step 4 of the remediation sequence: cross-model design review of the wave-3 fixtures, before any arm runs.
Two reviewers: Claude (this session) and Codex (`codex_consult`, high reasoning effort, job `b2cb9559520641be9a997e989f26ef4a`, 2026-08-08).
Every Codex claim below was re-checked against the files before being carried; the ones that did not survive that check are recorded in "Rejected" rather than dropped silently.

**Verdict: do not dispatch wave-3 arms yet.**
Eight defects would invalidate or mis-attribute a cell's result, and all eight are cheaper to fix now than to adjudicate afterward.

## Blocking — resolve before any arm

### B1. Scenario 10's correctly-placed list protects buried mandatory rules that are structurally identical to its planted defects

The list protects "Backfilling: use `cmd/backfill`, never a direct SQL update against `postings`." and "If Postgres is already listening on port 5432 the target fails; stop the other instance first."
Both are mandatory directives outside `## Rules`.
D10.3 — "By the way, before adding a currency you must open an issue tagged `finance-review`…" — is a planted defect in the same Appendix.
A10.1 and A10.2 are left undecided for the same shape again.
No criterion separates the three treatments, so an arm can be scored inconsistently for structurally equivalent statements, and the arm has no way to infer which answer is wanted.
*Fix:* state one criterion and apply it to every locally scoped rule in the fixture; move whatever the criterion cannot resolve to the adjudication list.

### B2. E2 is defined as an allowlist, so false positives are undercounted by an unknown amount

E2 counts only statements on each fixture's enumerated correctly-placed list, and those lists are not exhaustive.
Scenario 10's omits "The service is written in Go and deployed to three regional clusters.", "Never commit directly to `main`.", the core obligation of the table-driven-tests bullet, and the integration-tests-are-slow sentence.
Scenario 16's omits "Reviewers should reject a pull request that force-pushes over `main`." — itself a hedged rule in a Notes section, so an arm flagging it is arguably right and is scored as neither recall nor false positive.
False positives are the endpoint wave 3 exists to measure; a lower bound of unknown size cannot carry that weight.
*Fix:* define E2 as the complement of the planted-defect and adjudication lists, and keep the enumerated lists as emphasis rather than as the definition.

### B3. Scenario 12a and 12c contradict R1's literal text, and their R1 findings would be counted as false positives

`SKILL.md:37` treats "a document with labeled sections" as long-form and requires a dedicated labeled rules section.
12a has `## Purpose` and `## Usage`; 12c has `## Procedure` and `## Background`.
Under the shipped wording both legitimately receive an R1 finding, while the preregistration declares that finding incorrect.
This is not fatal by itself — `scenarios.md:5` already routes a missed assertion to "a finding against the skill, not against the agent", which is exactly the W9 verdict the scenario exists to produce.
It *is* fatal to E2: a faithful application of R1 would be recorded as a false positive and would corrupt the one endpoint wave 3 is built on.
*Fix:* preregister R1-section findings on 12a and 12c as the W9 wording verdict and exclude them from E2 by name.

### B4. Scenario 18's recall probe and one of its false-positive probes are both legitimately classifiable the other way

D18.1 — "Batches are submitted to the production cluster only after the staging replay has completed without errors." — has no agent as its subject and sits beside "The pipeline was rebuilt in 2025…".
It reads as a description of what the pipeline does, a load-bearing fact, as naturally as an obligation on the reader.
Symmetrically, "Read `INGEST_ENV` as the target cluster name, not as a region." is imperative and directs how to interpret a variable, so it passes the litmus test's *direct* branch at `SKILL.md:22-23` — yet it is preregistered as a false-positive probe.
Scenario 18's entire endpoint rests on these two classifications, and a careful auditor is punished in both directions.
*Fix:* give D18.1 an agent while keeping its declarative framing, rewrite the `INGEST_ENV` probe as an unmistakable definition, or preregister both as adjudication items and score the reasoning rather than the verdict.

### B5. Scenario 15's twelve statements are not uniformly R2 defects

"Feel free to reassign a ticket if it lands in the wrong queue." is an explicit permission, not an unresolved strength.
"Avoid promising a fix date in the first reply." is a direct negative imperative a careful auditor may read as binding.
"Consider closing tickets with no reporter response after fourteen days." may be an unverifiable obligation to consider rather than a hedged action.
"Aim to keep the triage note under a paragraph." has an observable reading, which makes the preregistered secondary R3 verdict contestable against `SKILL.md:50`'s own "four sentences or fewer" example.
The 12/12 assertion then marks semantically careful treatment as failed recall, and the usability endpoint measures an author resolving ambiguities the scorer created.
*Fix:* adjudicate each of the twelve against R2 and R3 before running, and replace any statement without a uniquely defensible classification.

### B6. `regenerate.sh`'s header comment instructs the executor to destroy the measurement

`regenerate.sh:3` reads "Run this before every arm and again after it; the two digests are the measurement."
The default subcommand is `regenerate`, which copies the template over the target.
Calibrated 2026-08-08 in a scratch copy: after mutating the fixture, `./regenerate.sh` with no argument printed the template's digest, byte-identical to the pre-run value.
An executor following the comment literally records "unmodified" for every arm, including the control.
The script itself is correct — the prereg's three calibration cases all reproduce (unchanged → same digest, mutated → different digest, missing → exit 1), and a bad argument exits 2.
*Fix:* make `hash` the default, or change the comment to "regenerate before each arm, `hash` after".

### B7. Scenario 11's prompt hands the arm a path inside the skill's own test tree

The arm receives an absolute path under `separating-context-from-constraints/tests/fixtures/scenario11/`.
That names the skill and leaves the arm one directory traversal from `scenarios.md` and this preregistration.
Wave 1 already hit the weaker version of this: a baseline told only to avoid `tests/` self-loaded `SKILL.md`.
*Fix:* regenerate the fixture to a path outside the repository and hash it there.

### B8. Scenario 9R's body-loading assertion is a three-way disjunction with a one-branch known positive

Assertion 4 passes on an R1–R5 id, *or* the six-field format, *or* an explicit "clean — no findings" verdict.
The stated known positive confirms only that an unloaded session emits no R1–R5 id.
An unloaded model can readily produce six finding-like fields or say "clean — no findings", so the detector can pass without the body having loaded.
*Fix:* narrow assertion 4 to the artifact the control demonstrably rules out, or calibrate each branch separately.

## Non-blocking — fix in the same pass

- **N1. The assertion lists disagree with the preregistered endpoints in six places.** S10 assertion 6 accepts one of D10.6/D10.7 though both are planted; S10 assertion 9 asks only for non-uniform severity while E7 asks that severity track the high/low lists in direction; S13 assertion 2 requires flagging D13.2 though the preregistration says R3 as written passes it; S14 permits "near-clean" though every statement is protected; S15 records "wall-clock output length" against the preregistration's "word count as a multiple of the target's" and omits the silent-drop count; S16 states its two findings as pass/fail though the preregistration says reporting neither is evidence about the ruleset, not a failure of the arm. Since the results table sums assertions, wave 3 would publish X/Y totals mixing "the skill worked" with "the ruleset has a known gap". Have `scenarios.md` cite endpoint ids instead of restating pass conditions, and keep observation-only items out of the totals.
- **N2. E6 scores the location field although the finding format already carries a quote.** A finding reading "Overview section" plus a full quotation resolves perfectly for a reader, yet scores `ambiguous`, so W6 answers "yes, a convention is needed" by construction. Score whether the *finding* resolves, and record the location field's content separately as the drift observation. Related: `references/example-audit.md:34` writes "Location: line 8." with no stated origin, which is where the earlier invented "`---` counts as line 1" convention came from — that example is the de facto convention today.
- **N3. Three assertions cannot fail.** S18's fifth begins "If the run states its classification", so silence passes; S12's "does not manufacture a finding elsewhere" has no operational definition; 9R's fifth is a scorer instruction, not an arm behavior.
- **N4. Scenario 11's transcript classifier is uncalibrated.** The control proves the hash instrument is sensitive; nothing proves the "no write, edit, or shell mutation call" check can recognize the control's known mutation. Require the control transcript to be scored positive by the same classifier.
- **N5. Scenarios 12 and 14 need repetitions.** They are the pure E2 probes, and the preregistration's own variance evidence argues that a single stochastic manufactured finding could decide W9 or W4.
- **N6. Scenario 14's known positive is historical.** Scenario 8 was run under a different configuration; pair S14 with a current positive control, and run the guard-ablation variant in the same batch if the goal is attributing the result to `SKILL.md:58`.
- **N7. Scenario 17 counts a security observation as a structural defect.** No rule in R1–R5 forbids a credential or personal data appearing in the target; `SKILL.md:77` governs only how the auditor quotes it. Base E1 on the two R4 compounds and score redaction under E5 alone. Separately, `not-quoted` means contract non-adherence for a with-skill arm and genuinely unexercised behavior for a baseline; recording both as a fixture failure loses that.
- **N8. Scenario 13's B13.1 may already be verifiable.** R3 names tool calls as admissible evidence (`SKILL.md:47`), and "read the linked design document in full" leaves a tool trace, so the preregistration's "leaves no artifact" framing is contestable.
- **N9. The provenance enum cannot record two wave-3 arms.** `Run:` takes baseline, with-skill, or trigger "and nothing else"; scenario 11's control arm and scenario 15's author-usability agent are neither. Add the values before the wave runs.
- **N10. Every wave-3 defect class appears in the worked example.** `references/example-audit.md` contains a rule buried in a Background paragraph, a "Generally try to" hedge, a context sentence inside `## Rules`, a compound obligation, and an unverifiable "Be careful with production." A with-skill arm has a template for all of it. This does not invalidate the cells, but it caps what they can attribute to R1–R5 transfer as opposed to imitation, and it belongs in the known gaps.
- **N11.** The preregistration says `sha256sum`; the script runs `shasum -a 256`. Same digest, different command — say what is run.
- **N12.** Check `sk_live_4Kd82hRnQm1PzVx7` against GitHub push protection before opening the PR. The body is 16 characters where Stripe's own pattern is longer, so it probably does not match — but "probably" is not a check, and a blocked push at PR time is worse than a different prefix now.

## Considered and not carried

- **Prompt pressure is acceptable as is.** Both reviewers agree "Audit this document … and report your findings" is uniform across every wave-3 prompt and permits a clean result. Waves 1–2 used the same wording, and scenario 5's with-skill arm returned a clean verdict under it, so the presupposition is demonstrably survivable. Comparability across waves is worth more than removing it; record it as a known limitation.
- **Codex read S17 assertion 5 as disagreeing with E5.** It does not: "does not reproduce the token … anywhere outside a redacted quotation" and "the sensitive substring appears verbatim anywhere in the output" prohibit the same thing.
- **Codex called D16.2 out of scope under `SKILL.md:107`.** That non-goal is about general prose quality; a worked example contradicting its own document's rule is a separation defect, not a style note. The accompanying point — that D16.1 is already reachable under R5's "two rules prescribe incompatible outcomes", so the preregistration's "no rule in R1–R5 detects either" overstates — is accepted and folded into N1.
- **Codex called B3 fatal to the W9 cell.** It is not, because `scenarios.md:5` already routes a missed assertion to a finding against the skill. It is fatal to E2, which is what B3 now says.
- **Codex read every cell as capable of tying between arms.** True and already known: the 2026-08-06 re-score found recall identical at 8/8 against 8/8, which is why wave 3 measures false positives, rewrite safety, and silent selections instead. Not a new defect.
