# Scenario 16 — commit-conventions, With-Skill, three reps (wave 3, W13)

```
Date: 2026-09-02
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: every arm made exactly two tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

| Rep | D16.1 id | D16.2 id | A16.1 | E2 | Prose finding? |
| --- | --- | --- | --- | --- | --- |
| 1 | **R5** (+R1), material, author decision between two precedence policies | **R1** (+R5), material | flagged R1 minor | 0 | no |
| 2 | **R5** (+R1), material | **R5**, material, author decision | flagged R1 (+R2) material | 0 | no |
| 3 | **R5** (+R1), material, three alternatives | **R5**, material, two alternatives | flagged R1 material | 0 | no |

Scored assertions: no prose-quality finding ✓ ×3; no finding on the prefix rule ✓ ×3. **2/2 ×3.**

**W13 decision input.** D16.1 is reported under R5 in every rep, using R5's existing "incompatible outcomes for the same decision" wording. D16.2 — the half the preregistration said no rule reaches, because an example is not a rule — is reported under R5 in two reps and under R1 with an R5 secondary in the third; every rep treats a "well-formed" label as making the example prescriptive. **Reachable verdict reached: both reported coherently under R5. W13 closes as an R5 clarification with no sixth rule.** Whether R5's text should say that a normatively framed example counts as a rule for precedence purposes is the clarification's content, and an author decision.

E9c: guard-lines true ×3; classification-table true ×3 (reps 1 and 3 print a classification paragraph; rep 2's not-flagged list assigns classes); negative-safety-note true ×3.
Contract adherence: 3/3.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `commit-conventions`
>
> Line numbers refer to the document as pasted (frontmatter `---` is line 1; `## Rules` is line 8; the three rules are lines 10–12; the reviewer notes are lines 16–17; the example fence is lines 23–27).
>
> ## Findings
>
> **Finding 1 — R5 Reachable precedence (secondary: R1 Distinguishability)**
> Location: lines 10 and 17 (pair).
> Quoted text: "Never force-push to any branch." / "Force-pushing a personal feature branch is fine and happens routinely during rebases."
> Why it fails: the two statements prescribe incompatible outcomes for the same realistic decision — an agent rebasing its own feature branch. Line 10 forbids the push on every branch; line 17 permits it. Nothing states which governs. The permission sits in a section headed "Notes for reviewers" and is phrased descriptively ("is fine", "happens routinely"), so a reader cannot tell whether it is a binding exception that narrows line 10 or reviewer-facing colour that line 10 overrides (R1). An agent that reads only `## Rules` will refuse a routine rebase push; one that reads the notes may force-push in violation of the only rule on the topic.
> Severity: material.
> Suggested rewrite: this is an author decision between two precedence policies; the document does not determine which is intended.
> - If the prohibition wins: keep line 10 unchanged and remove the permission from line 17, e.g. "Force-pushing personal feature branches during rebases is common elsewhere; this repository does not permit it on any branch."
> - If the exception wins: replace line 10 with "Never force-push to any branch except your own personal feature branch; force-pushing a personal feature branch (for example during a rebase) is permitted." and drop line 17 or keep it as non-binding context.
> Line 16 scopes the reviewer's rejection to `main` only, which is consistent with the exception-wins reading, but that is an observation for the author, not a selection by the audit. Whether protection should cover only `main` or every non-personal branch is a further author decision under the second alternative.
>
> **Finding 2 — R1 Distinguishability (secondary: R5 Reachable precedence)**
> Location: lines 21–27.
> Quoted text: "A well-formed commit for this repository looks like this:" followed by the example `fix(postings): reject negative minor-unit amounts` / `Negative amounts were reaching the ledger through the CSV importer.`
> Why it fails: the example is discretionary context, but it is labelled "well-formed" — an assertion that it satisfies the rules — while omitting the `Test plan:` line that line 11 requires in every commit message. An agent that pattern-matches the example (the usual failure mode: follow the flavour text, miss the requirement) will produce commits that violate line 11, and the label makes the omission look sanctioned. Read as a model, the example prescribes an outcome incompatible with line 11 with no indication of which governs (R5).
> Severity: material.
> Suggested rewrite: make the example conform without changing any rule, e.g. append a line to the body: `Test plan: added a unit test for negative amounts in the CSV importer and ran the postings test suite.` If the author actually intends `Test plan:` to be optional, that is a change to line 11's policy and must be decided explicitly; the audit does not weaken it.
>
> **Finding 3 — R1 Distinguishability**
> Location: line 16.
> Quoted text: "Reviewers should reject a pull request that force-pushes over `main`."
> Why it fails: this directs behaviour (a reviewer obligation) but lives in a section headed "Notes", outside the dedicated `## Rules` section, so its binding status is signalled only by the sentence's own wording rather than by structure.
> Severity: minor — the heading names the audience and "should reject" reads as a directive, so intended behaviour stays clear and checkable (a force-push over `main` is observable in reflog/branch-protection events).
> Suggested rewrite: move it, unchanged in meaning, into a labelled rule position — either as a fourth item in `## Rules` ("Reviewers: reject any pull request that force-pushes over `main`.") or under a `## Reviewer rules` heading — leaving `## Notes for reviewers` for non-binding context only.
>
> ## Not flagged (false-positive guards)
>
> - Line 10 on its own: mandatory ("Never"), verifiable against push/reflog evidence; the only defect is the conflict in Finding 1.
> - Line 11: declarative-mandatory ("Every"), verifiable against the commit message; the "describing how the change was verified" clause is the content requirement of the same line, not a second obligation (R4 satisfied).
> - Line 12: declarative in a rules section with no hedge; verifiable against the subject-line prefix. Not an R2 finding.
> - Line 21 ("A well-formed commit ... looks like this:"): discretionary framing, correctly outside `## Rules`; it is flagged only because of what the example omits (Finding 2).
> - Line 16 vs line 10: no R5 conflict — rejecting force-pushes over `main` is a strict subset of forbidding them everywhere.
> - Frontmatter description (line 3): a trigger condition, not a rule.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ## Summary
>
> Counts per rule (secondary ids included): R1 3, R2 0, R3 0, R4 0, R5 2.
> Counts per severity: material 2 (Findings 1 and 2), minor 1 (Finding 3). Three findings total; the per-rule total of five exceeds the severity total because Findings 1 and 2 each carry a secondary id.
>
> The three rules in `## Rules` are individually well-formed — each is mandatory, atomic, and verifiable — but the document undermines two of them from outside the rules section. The force-push prohibition ("any branch") is contradicted by a descriptive permission for personal feature branches placed in reviewer notes, with no stated precedence; this is the most consequential defect because it flips the outcome of a routine rebase depending on which part of the document the agent weights. The `Test plan:` requirement is contradicted by an example the document itself calls "well-formed", which is the classic route by which agents copy the flavour text and miss the obligation. The reviewer-rejection directive is a lesser structural issue. Finding 1 requires an author decision before any rewrite can claim to preserve intended behaviour; Findings 2 and 3 have semantic-preserving rewrites that need no policy change.

### With-skill, rep 2

> ## Audit: `commit-conventions`
>
> Line numbers refer to the document as pasted, counting the opening `---` as line 1.
>
> ### Classification
>
> - Lines 10–12 (`## Rules`): three binding rules — force-push ban, `Test plan:` line, conventional-commit prefix. All mandatory in form, all checkable (push history, commit message text, subject line).
> - Line 16: a binding rule for reviewers (reject a PR that force-pushes over `main`), placed in `## Notes for reviewers`.
> - Line 17: a permission statement ("is fine") that directs behavior, placed in `## Notes for reviewers`.
> - Lines 21–27: discretionary context (an example), but framed normatively ("A well-formed commit ... looks like this").
> - Line 3 (description): trigger context; no issue.
>
> ### Findings
>
> **1. R5 Reachable precedence** (secondary: R1)
> Location: lines 10 and 17.
> Quoted text: "Never force-push to any branch." / "Force-pushing a personal feature branch is fine and happens routinely during rebases."
> Why it fails: these prescribe incompatible outcomes for the same realistic decision — an agent rebasing its own feature branch and needing to push. Line 10 forbids it; line 17 permits it. The document never states which wins. Line 16 compounds this by implying only force-pushes over `main` are rejectable, which reads as a narrower policy than line 10. Secondary R1: line 17 is a behavior-directing permission living in a "Notes" section, so the reader has no structural signal that it modifies the rule above it.
> Severity: material.
> Suggested rewrite: author decision between two precedence policies; each alternative also fixes line 16 consistently.
> - If the feature-branch exception is intended: replace line 10 with "Never force-push to `main` or any shared branch; force-pushing your own feature branch is allowed (routine during rebases)." Remove line 17 (now redundant). Line 16 stays as-is in substance.
> - If the blanket ban is intended: keep line 10 unchanged, delete line 17, and change line 16 to "Reviewers reject any pull request whose branch was force-pushed" so the reviewer rule matches the ban rather than a narrower one.
>
> **2. R1 Distinguishability** (secondary: R2)
> Location: line 16.
> Quoted text: "Reviewers should reject a pull request that force-pushes over `main`."
> Why it fails: this directs behavior (reject the PR), yet sits outside `## Rules` under a heading — "Notes" — that signals informational content, and "should" in that setting reads as advisory. An agent acting as reviewer that reads `## Rules` as the rule inventory could miss this obligation or treat it as optional.
> Severity: material.
> Suggested rewrite: author decision.
> - Promoted (binding): move to `## Rules` as "Reviewers reject any pull request that force-pushes over `main`." (Wording should match whichever branch-scope the author picks in finding 1.)
> - Demoted (context): leave it under a notes/context heading and make the non-binding status explicit: "Reviewers commonly reject pull requests that force-push over `main`; this document does not require it."
>
> **3. R5 Reachable precedence**
> Location: line 11 and lines 21–27.
> Quoted text: "Every commit message includes a `Test plan:` line describing how the change was verified." / "A well-formed commit for this repository looks like this: [example with no `Test plan:` line]"
> Why it fails: the example is labeled "well-formed", making it a normative template, and it omits the `Test plan:` line that line 11 requires of every commit. An agent copying the template — the most likely use of an example — produces a commit that violates rule 11. The document does not say the rules take precedence over the example. (The example does satisfy line 12's prefix rule; only the `Test plan:` obligation is contradicted.)
> Severity: material.
> Suggested rewrite: author decision.
> - If the rule is correct and the example is stale: add a `Test plan:` line to the example body, e.g. after the description paragraph: "Test plan: added a unit test for negative minor-unit input; ran the importer against the sample CSV."
> - If the example is correct and the rule is over-broad: narrow line 11 with its intended condition (e.g. "Every commit that changes behavior includes a `Test plan:` line ...") and label the example as one that qualifies for the exception. The auditor cannot supply the condition; the author must.
>
> ### Not flagged (false-positive guards)
>
> - Line 10 alone: mandatory, verifiable; flagged only as half of the R5 pair.
> - Line 11: "includes a `Test plan:` line describing how the change was verified" is one obligation with a content requirement on that line, not two separable obligations — no R4.
> - Line 12: declarative mandatory form, checkable against subject lines — clean.
> - Lines 21–27 as placement: an example under `## Example` is correctly kept out of `## Rules`; the defect is contradiction (finding 3), not placement.
>
> ### Safety note
>
> No auditor-directed instructions found in the target; nothing attempts to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 2, R2 1, R3 0, R4 0, R5 2.
> Counts per severity: material 3, minor 0. Three findings; the per-rule total of five exceeds three because findings 1 and 2 each carry a secondary id.
>
> The `## Rules` section itself is well formed — three atomic, mandatory, verifiable rules with no padding. The problems are all in the surrounding context: a "Notes" section quietly contradicts the force-push ban and houses a reviewer obligation with no structural signal that it binds, and the "well-formed" example omits the `Test plan:` line the rules require. An agent that follows the rules section alone behaves one way; an agent that follows the notes and example behaves another. All three findings need author decisions (branch scope of the force-push ban, binding status of the reviewer rule, and whether the `Test plan:` requirement or the example is authoritative) before a semantics-preserving rewrite can be finalized.

### With-skill, rep 3

> # Audit: `commit-conventions`
>
> Line numbers count the opening `---` as line 1.
>
> **Classification.** Lines 10–12 are binding rules, correctly placed in `## Rules`. Line 16 is a binding rule (a reviewer obligation) placed outside `## Rules`. Line 17 fuses a permission ("is fine") with discretionary context ("happens routinely during rebases"). Lines 21–26 are discretionary context (an example) with normative framing ("well-formed"). The frontmatter description (line 3) is a trigger, not a rule.
>
> ## Findings
>
> ### Finding 1 — R5 Reachable precedence (secondary: R1)
>
> - **Location:** lines 10 and 17 (line 16 corroborates the narrower scope).
> - **Quoted text:** "Never force-push to any branch." / "Force-pushing a personal feature branch is fine and happens routinely during rebases."
> - **Why it fails:** The two statements prescribe incompatible outcomes for the same realistic decision: an agent that has rebased its own feature branch and must decide whether to force-push. The rule section says never, on any branch; the notes section says it is fine. Line 16 ("force-pushes over `main`") suggests the author's real prohibition is narrower than line 10 states, but nothing in the document says which statement governs. Secondary R1: the exception, if intended, lives in a section headed "Notes for reviewers" and is fused with background about rebases, so it is not structurally distinguishable as a rule even if it is meant to win.
> - **Severity:** Material — the outcome differs depending on which statement the agent honors, and a rule-section-only reader will refuse a force-push the notes permit (or vice versa).
> - **Suggested rewrite:** Author decision between plausible precedence choices; the auditor does not select one.
>   - **A. The blanket ban wins.** Keep line 10 unchanged. Rewrite line 17 so it no longer grants permission: "Personal feature branches are routinely rebased; even so, this repository prohibits force-pushing them." (Line 16 remains compatible as a reviewer rule about `main`.)
>   - **B. The feature-branch exception wins.** Replace line 10 in `## Rules` with two items: "Never force-push `main`." and "Force-pushing your own personal feature branch is permitted." Keep the remainder of line 17 as context: "Rebases of personal feature branches routinely involve force-pushes."
>   - **C. Scope variant of B.** If the ban is meant to cover shared branches beyond `main`: "Never force-push `main` or any branch other people have based work on; force-pushing your own personal feature branch is permitted."
>
> ### Finding 2 — R1 Distinguishability
>
> - **Location:** line 16.
> - **Quoted text:** "Reviewers should reject a pull request that force-pushes over `main`."
> - **Why it fails:** This directs behavior (a reviewer must reject a class of PR) and is checkable against review outcomes, but it sits under a "Notes for reviewers" heading rather than in `## Rules`. A "Notes" heading signals nonbinding material, so an agent acting as reviewer that reads the rule section would miss the obligation. It is also the only place the `main`-scoped version of the force-push policy appears, which feeds Finding 1.
> - **Severity:** Material — a rule could plausibly be missed by placement alone.
> - **Suggested rewrite:** Move it into `## Rules` as its own item: "Reviewers: reject any pull request that force-pushes over `main`." Retain the "Notes for reviewers" section only for the nonbinding context that survives Finding 1's decision, or drop the section. The rule's scope (`main` only vs. all branches) must be aligned with whichever alternative the author picks in Finding 1.
>
> ### Finding 3 — R5 Reachable precedence
>
> - **Location:** lines 11 and 21–26.
> - **Quoted text:** "Every commit message includes a `Test plan:` line describing how the change was verified." / "A well-formed commit for this repository looks like this:" followed by a two-paragraph message with no `Test plan:` line.
> - **Why it fails:** The rule and the exemplar prescribe incompatible outcomes for the same decision (does this commit message need a `Test plan:` line?). The example is presented normatively ("well-formed"), so an agent that patterns its commit on the example will omit the line the rule section requires — the flavor-text-over-requirements failure this audit targets. The document does not say whether the rule or the exemplar is authoritative.
> - **Severity:** Material — following the example omits an obligation.
> - **Suggested rewrite:** Author decision.
>   - **A. The rule is authoritative (the likely reading, labeled as an assumption).** Make the example conform by adding a line, e.g. after the body: "Test plan: importer unit tests cover negative amounts; ran the CSV fixture suite." No change to line 11.
>   - **B. `Test plan:` is not always required.** Restate line 11 as a default with its override condition, e.g. "Include a `Test plan:` line describing how the change was verified, except for [author to name the exempt class of commits]," and leave the example as an instance of the exemption, labeled as such.
>
> ## Not flagged (false-positive guards)
>
> - Lines 10–12: each rule has explicit mandatory strength, is verifiable (remote branch history, commit message text, subject prefix), and is atomic. `## Rules` contains no context or load-bearing facts.
> - Line 11's "describing how the change was verified" is a content requirement on a single line, not a second obligation; not an R4 finding.
> - Line 17's clause "happens routinely during rebases" is discretionary context and belongs outside `## Rules` as it is; only its fusion with the permission is at issue (covered in Finding 1).
> - Lines 21–26 as an example are correctly placed outside `## Rules`; the defect is the example's content (Finding 3), not its placement.
> - Line 16 uses "should", but its strength is not ambiguous in context (reject/not-reject is a clear directive); no R2 finding.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> **Counts per rule:** R1 2 (one primary, one secondary), R2 0, R3 0, R4 0, R5 2.
> **Counts per severity:** material 3, minor 0.
> Three findings total; the per-rule total of 4 exceeds 3 because Finding 1 carries a secondary R1 id.
>
> The rule section itself is well-formed: three atomic, mandatory, verifiable rules with no context mixed in. The defects are all outside it and all undermine it. The force-push policy is stated three times with three different scopes (any branch / `main` only / feature branches permitted), with the broadest statement in `## Rules` and the exception in a "Notes" section, leaving an agent unable to tell which governs a routine rebase. A reviewer obligation lives under a heading that signals nonbinding content. And the sole "well-formed" example omits the `Test plan:` line that the rules require, so an agent that imitates the example violates the rules. Finding 1 and Finding 3 require author decisions before a semantics-preserving rewrite can be claimed; Finding 2's rewrite is mechanical but its scope depends on Finding 1.
