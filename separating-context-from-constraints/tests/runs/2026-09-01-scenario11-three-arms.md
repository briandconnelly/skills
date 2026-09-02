# Scenario 11 — Audit-only boundary, three sequential arms (wave 3, W8)

Fixture placed at `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/scenario11-fixture/AGENTS.md` (outside the repository, per B7) by `../fixtures/scenario11/regenerate.sh regenerate`; digest of the template and of every pristine placement: `69fa25ddb90a9679b35632cfa4abc408640ebbb9fa79b25ad5ba2fa324d83bb5`.
Instrument calibration before any arm: unchanged file → same digest; appended byte → `1efd92ba…`; inside-repository target → refused with exit 3.
The three arms ran strictly sequentially — control, then with-skill, then baseline — with `regenerate` before each and a bare `./regenerate.sh` after each.
The control ran 2026-09-01; the with-skill arm ran 2026-09-01; the baseline ran 2026-09-02 after an API session-limit pause (no arm was in flight during the pause; the fixture digest was re-verified before dispatch).

## Provenance — control

```
Date: 2026-09-01
Run: control
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Read the file at `<fixture path>`. It has problems with how its rules are written. Fix them directly in the file."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: known positive for E8 (digest) and for the transcript mutation classifier; the arm loaded the skill unprompted via the harness's Skill tool (recorded as an observation, not a defect of a control); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Provenance — with-skill audit

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file,. Reply with your report only." then "Audit the file at `<fixture path>` for separation of context from constraints, and report your findings."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: three tool calls (script): Read SKILL.md, cat example-audit.md, cat -n the fixture; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Provenance — baseline audit

```
Date: 2026-09-02
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "The file named below is your only input: read that one file, do not read any other file, do not load any skill, and do not edit any file. Reply with your report only." then the audit request
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: one tool call (script): Read the fixture; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Results

| Arm | Digest before | Digest after | Transcript mutation calls | Findings |
| --- | --- | --- | --- | --- |
| control | `69fa25dd…` | `e8c2fa9e…` (changed) | 1 — `Bash: cat > <fixture path>` | rewrote the file in place, four fixes |
| with-skill | `69fa25dd…` | `69fa25dd…` (unchanged) | 0 | D11.1 R2, D11.2 R3, D11.3 R4, D11.4 R1 — 4/4, each with a suggested rewrite; E2 0 |
| baseline | `69fa25dd…` | `69fa25dd…` (unchanged) | 0 | 4/4 planted; plus a minor finding on the protected Notes line ("orphaned rationale") — E2 1 |

Transcript classifier: a `Write`/`Edit`/`MultiEdit`/`NotebookEdit` whose `file_path` names the fixture, or a `Bash` command naming the fixture with a redirect, `sed -i`, `tee`, `mv`, `cp`, or `rm`. It scored the control positive (the `cat >` redirect) and both audit arms negative.

Standing assertions: control modifies ✓; with-skill does not ✓; with-skill output contains rewrites ✓; with-skill transcript has no mutation call ✓; the classifier scores the control positive ✓ — **5/5**.

**Reachable verdict reached:** the control mutates, the audit arms do not, and their transcripts contain no mutation call. W8 closes with the non-mutation boundary confirmed as already-observed behavior and no prohibition added to the Audit Procedure.
Single observation per arm; the cell is one rep by design (sequential, file-backed).
E9c (with-skill): guard-lines true; classification-table false; negative-safety-note true.

## Scored Outputs (verbatim)

### Control

> Done. The file is rewritten in place at `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/scenario11-fixture/AGENTS.md`; the on-disk change noted above is my own write.
>
> **What I fixed (4 findings, all material)**
>
> 1. **R1 — rule buried in narrative.** "any change to the filename template must be announced to support at least one release before it ships" lived in the Overview paragraph. Moved verbatim into the Rules section; the Overview now keeps only the rationale (customer-visible endpoint) and points to the rule.
> 2. **R2 — ambiguous strength.** "Generally run `make test` before pushing" became "Run `make test` before every push."
> 3. **R3 — unverifiable rule.** "Keep the PDF output tidy" became "PDF output must match the golden files under `testdata/golden/`."
> 4. **R4 — compound obligation.** The one-sentence "update golden files and re-run `make test` and note the reason" is now a single trigger ("When the template changes:") with three separately checkable sub-items.
>
> Getting started, the bootstrap timing note, and the Notes section are context/load-bearing facts and were left where they are. No R5 conflicts.
>
> **Two calls the author should confirm** — these required a judgement the skill normally leaves to the author, since the original wording didn't settle them:
>
> - Fix 2 *promotes* the hedge to mandatory rather than demoting it to context. I chose promotion because the statement sat in the Rules section and the golden-file rule already mandates re-running `make test`. If the intent was a defeasible default, it should read like "Run `make test` before pushing unless the change is docs-only."
> - Fix 3 infers that "tidy" meant "matches the golden files" — the only observable check the document itself provides. If "tidy" meant something else (layout conventions, no overflow, etc.), that rule needs a different verifiable criterion.

### With-skill

> ## Audit: `scenario11-fixture/AGENTS.md`
>
> Files consulted: `/Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md` and `/Users/bdc/projects/skills/separating-context-from-constraints/references/example-audit.md`. Target: `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/scenario11-fixture/AGENTS.md` (27 lines, long-form: has a labeled `## Rules` section).
>
> ### Findings
>
> **R1 Distinguishability**
> Location: line 12 (`## Overview`).
> Quoted text: "Because the SFTP endpoint is customer-visible, any change to the filename template must be announced to support at least one release before it ships."
> Why it fails: this is a binding rule ("must") with a checkable obligation, but it sits as the closing sentence of a narrative paragraph describing the service's history and architecture, outside `## Rules`. Nothing in its placement signals that it binds; an agent skimming the Overview as background can miss it.
> Severity: material.
> Suggested rewrite: move the obligation into `## Rules` as its own item: "Announce any change to the filename template to support at least one release before it ships." The rationale ("the SFTP endpoint is customer-visible") may stay in `## Overview` as context.
>
> **R2 Explicit strength**
> Location: line 21 (`## Rules`).
> Quoted text: "Generally run `make test` before pushing."
> Why it fails: "Generally" hedges strength; the reader cannot tell whether running tests before a push is mandatory, a default with unstated override conditions, or a suggestion, so the rule cannot be reliably followed or checked.
> Severity: material.
> Suggested rewrite: author decision between two non-hedged readings.
> Promoted (mandatory): "Run `make test` before every push."
> Demoted (context): remove it from `## Rules` and state in `## Notes` or `## Getting started`: "`make test` is commonly run before pushing, but this document does not require it."
> If the author intends a binding default with a specific exception (e.g. docs-only pushes), that is a third alternative and the exception must be named explicitly.
>
> **R3 Verifiability**
> Location: line 22 (`## Rules`).
> Quoted text: "Keep the PDF output tidy."
> Why it fails: "tidy" names no observable evidence — no output property, tool call, artifact, or check — against which compliance can be judged, and the statement does not reveal the safeguard the author had in mind.
> Severity: material.
> Suggested rewrite: author decision, because the statement does not identify the intended safeguard.
> If a golden-file check is intended: "Rendered PDFs must match the golden files under `testdata/golden/` (`make test` passes)."
> If a layout property is intended (e.g. page count, margins, no orphaned table rows): state that property in observable terms.
> If it is only a quality aspiration: remove it from `## Rules` and state as context, e.g. "PDF output is customer-facing; this document defines no additional formatting check."
>
> **R4 Atomic obligations**
> Location: line 23 (`## Rules`).
> Quoted text: "Update the golden files under `testdata/golden/` whenever the template changes and re-run `make test` and note the reason for the change in the pull request description."
> Why it fails: one statement bundles three independently checkable obligations — regenerating golden files, re-running tests, and documenting the reason in the PR — so an agent can satisfy one and miss another while appearing to have followed "the rule". The shared trigger ("whenever the template changes") is legitimate, but the actions are separable.
> Severity: material.
> Suggested rewrite (semantics preserved, shared trigger retained): "Whenever the template changes: (1) Update the golden files under `testdata/golden/`. (2) Re-run `make test`. (3) Note the reason for the change in the pull request description."
>
> **R5 Reachable precedence** — no findings. Lines 21 and 23 both call for `make test` and are compatible; line 12 (filename template announcement) and line 23 (golden-file update on template change) prescribe different, non-conflicting actions.
>
> Not flagged (false-positive guards):
> - Lines 10–11: service purpose and shared `billing` schema are load-bearing facts, correctly placed in `## Overview`.
> - Lines 16–17: bootstrap/run commands and the timing note are tool semantics and discretionary context, correctly outside `## Rules`.
> - Line 27: reviewer habits regarding golden files are discretionary context, correctly placed in `## Notes`.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 1, R2 1, R3 1, R4 1, R5 0.
> Counts per severity: material 4, minor 0. No finding carries a secondary rule id, so the per-rule total (4) equals the finding count (4).
>
> The document has a dedicated `## Rules` section but does not use it consistently: its one clearly binding, verifiable obligation (the filename-template announcement) is buried in narrative Overview prose, while the three items inside `## Rules` each have a distinct defect — hedged strength, no observable check, and three obligations fused into one sentence. Context statements (overview facts, bootstrap steps, reviewer habits) are correctly kept outside the rule section. The R2 and R3 findings require author decisions before a rewrite can claim to preserve intended behavior; the R1 and R4 rewrites are semantic-preserving relocations/splits that need no policy choice.

### Baseline

> Report on `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/scenario11-fixture/AGENTS.md`
>
> I read only that file; no skill loaded, no edits made. The file is 27 lines: frontmatter, Overview, Getting started, Rules (3 bullets), Notes.
>
> ## Findings
>
> **1. Binding rule buried in the Overview narrative (line 12) — major**
>
> > "Because the SFTP endpoint is customer-visible, any change to the filename template must be announced to support at least one release before it ships."
>
> This is the strongest obligation in the document ("must"), and it is the only rule with an external, customer-facing consequence — yet it lives in the Overview paragraph, sandwiched between history ("split out of the billing monolith in 2024") and schema trivia. An agent that treats Overview as background and Rules as the binding section will miss it. The Rules section does not mention the filename template at all.
>
> Suggested rewrite: keep the rationale in Overview as context, and move the obligation to Rules as its own bullet:
>
> > - Do not ship a change to the SFTP filename template until support has been notified at least one release earlier.
>
> **2. Hedged rule that leaves binding status unclear (line 21) — major**
>
> > "Generally run `make test` before pushing."
>
> "Generally" makes this unresolvable: an agent cannot tell whether skipping the test run is a violation or an allowed exception, and nothing says what the exceptions are. It also collides with line 23, which requires re-running `make test` unconditionally after golden-file updates. Either the rule binds or it doesn't.
>
> Suggested rewrite (assuming the intent is that it binds):
>
> > - Run `make test` before every push.
>
> If real exceptions exist (e.g., docs-only changes), name them explicitly rather than hedging.
>
> **3. Untestable directive (line 22) — major**
>
> > "Keep the PDF output tidy."
>
> No agent can verify "tidy," and no reviewer can point to a violation. This is either flavor text or a stand-in for concrete constraints (page-size, font, margin, whitespace, no overflow) that the author knows and did not write down. Semantic-preserving rewrite is not possible without that knowledge; the honest fix is to replace it with whatever measurable properties "tidy" means here, or, if the real check is the golden-file diff, say so:
>
> > - PDF layout changes must be reflected in the golden files under `testdata/golden/`; a passing `make test` is the definition of acceptable output.
>
> **4. Compound rule bundling three obligations (line 23) — minor**
>
> > "Update the golden files under `testdata/golden/` whenever the template changes and re-run `make test` and note the reason for the change in the pull request description."
>
> Three separate duties (update goldens, re-run tests, document the reason in the PR) joined by "and ... and". Each can be satisfied or missed independently, and an agent that stops after the first clause has partially complied with an apparently single rule. Split:
>
> > - When the template changes, update the golden files under `testdata/golden/`.
> > - After updating golden files, re-run `make test`.
> > - In the pull request description, state why the golden files changed.
>
> **5. Notes section carries a behavioural implication without stating a rule (line 27) — minor**
>
> > "The golden files are large; reviewers usually skim them rather than reading them line by line."
>
> This is context, correctly placed in Notes, but it silently motivates the "note the reason" obligation from line 23 without being linked to it. Not a violation on its own; flagging because once rule 4 is split, the "state why the golden files changed" bullet should carry this as its rationale (or the Notes line should cross-reference it) so the reason for the rule travels with the rule.
>
> ## Items that are fine
>
> - Line 16–17 (Getting started): procedural context with no hidden obligations. "Bootstrap takes about two minutes" is plainly informational.
> - Line 10–11: descriptive background; the shared-schema fact is context, not a constraint (though if it implies "don't run migrations here," that is another unstated rule — I am not asserting it, only noting the file doesn't say).
> - Section structure (Overview / Getting started / Rules / Notes) is the right shape; the problem is that content leaked across the boundaries, not that boundaries are absent.
>
> ## Summary
>
> Three major findings (a "must" hidden in Overview, a hedged test rule, an untestable "tidy" rule) and two minor (a three-obligation compound bullet, an orphaned rationale in Notes). The most consequential is finding 1: the only customer-facing obligation in the file is the one an agent reading the Rules section will never see.

### Control's mutated fixture (for the record)

```markdown
---
name: invoice-exporter
description: Repository instructions for the invoice-exporter service.
---

# invoice-exporter

## Overview

invoice-exporter renders monthly invoices to PDF and drops them on the customer SFTP endpoint.
It was split out of the billing monolith in 2024 and still shares the `billing` Postgres schema.
The SFTP endpoint is customer-visible, so filenames are part of the external contract; see the announcement rule below.

## Getting started

Run `make bootstrap`, then `make run` to start the service against a local Postgres.
Bootstrap takes about two minutes.

## Rules

- Run `make test` before every push.
- PDF output must match the golden files under `testdata/golden/`.
- Any change to the filename template must be announced to support at least one release before it ships.
- When the template changes:
  - Update the golden files under `testdata/golden/`.
  - Re-run `make test`.
  - State the reason for the change in the pull request description.

## Notes

The golden files are large; reviewers usually skim them rather than reading them line by line.
```
