# Scenario 16 — commit-conventions, Baseline, three reps (wave 3, W13)

```
Date: 2026-09-02
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: all three arms made zero tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Observation items D16.1 (rule vs. note) and D16.2 (rule vs. example) — recorded with the id each arm attaches, counted under neither endpoint. A16.1 (the "should reject" reviewer note) — adjudication. Protected: the conventional-commit-prefix rule, the example's body text, and everything else.

| Rep | D16.1 reported? id | D16.2 reported? id | A16.1 | Protected units criticized | E2 | Prose-quality finding on the example or the note? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | yes (#1 HIGH), no id, "self-contradictory; the author must choose" | yes (#2 HIGH), no id | flagged (#3 Low) | rule 3 (#4, under-specified) | 1 | no |
| 2 | yes (B1), no id | yes (B2), no id | flagged (B3 Blocking) | rule 3 (A1); rule 2 (A2 placement, A3 mood) | 2 | no |
| 3 | yes (F1), no id, options A/B | yes (F2), no id | flagged (F3) | rule 3 (F4); rule 2 (F5) | 2 | no |

Scored assertions: no prose-quality finding ✓ ×3; no finding on the prefix rule **FAIL ×3**.
E9a not recorded (scope: 10 and 15); every rep shipped a revised document.
E9c: guard-lines true ×3; classification-table false ×3; negative-safety-note false ×3.

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `commit-conventions` — separation of context from constraints
>
> Overall: the `## Rules` section itself is well-formed (three imperative, bulleted, individually testable statements with no padding). The problems are all in the surrounding material, which carries binding content that contradicts or undermines the rules. Two findings are high severity; two are low.
>
> ## Findings
>
> ### 1. HIGH — A rule's exemption lives in "Notes for reviewers" and contradicts the rule
>
> - Rule: "Never force-push to any branch."
> - Notes: "Force-pushing a personal feature branch is fine and happens routinely during rebases."
>
> The rule is absolute; the note grants a permission that the rule forbids. An agent has no way to tell which binds. Most readers will resolve it in favor of the section labeled "Rules" and refuse a routine rebase-and-force-push on a feature branch, which is the opposite of what the note says the repository does. The note is not context; it is the actual scope of the rule, placed where an agent is least likely to treat it as binding.
>
> The document cannot be rewritten semantic-preservingly because it is self-contradictory. The author must choose. The most likely intended reading, given both statements together, is that only `main` is protected. Suggested rewrite (flag for author confirmation):
>
> ```
> - Never force-push to `main`.
> - Force-pushing your own feature branch is permitted.
> ```
>
> If the author instead intends "never force-push anywhere", the second note sentence must be deleted rather than left as an implicit override.
>
> ### 2. HIGH — The "well-formed" example violates Rule 2
>
> - Rule: "Every commit message includes a `Test plan:` line describing how the change was verified."
> - Example: has a subject and a body, but no `Test plan:` line, and is explicitly labeled "A well-formed commit for this repository looks like this."
>
> Examples are copied more reliably than rules are read. Labeling a non-compliant message "well-formed" tells the agent the `Test plan:` requirement is optional. Suggested rewrite:
>
> ````
> ```
> fix(postings): reject negative minor-unit amounts
>
> Negative amounts were reaching the ledger through the CSV importer.
>
> Test plan: added a unit test for a negative minor-unit CSV row; ran the postings test suite.
> ```
> ````
>
> ### 3. LOW — A reviewer directive is hedged and located outside `## Rules`
>
> "Reviewers should reject a pull request that force-pushes over `main`."
>
> This is an obligation ("reject"), softened with "should" and placed in a section named "Notes", so its binding status is unclear. It also addresses a different audience (reviewers) than the frontmatter description targets ("Use when writing commits"), so a reviewing agent is unlikely to load this skill and encounter it at all. Two options:
>
> - If it is meant to bind: move it under `## Rules` as "Reviewers reject any pull request whose branch was force-pushed over `main`." and widen the description to "Use when writing or reviewing commits in this repository."
> - If it is merely explanatory background for commit authors: keep it out of the rules, but then finding 1 must be resolved first so the note no longer carries the rule's real scope.
>
> ### 4. LOW — Rule 3 is under-specified relative to its own example
>
> "Subject lines use a conventional-commit type prefix."
>
> Testable as written (a prefix is present or not), but the accepted type set and whether a scope is required are not stated, while the example shows `fix(postings):` with a scope. An agent will infer "scope required" from the example and cannot check "type is allowed" against anything. If the repository has a constraint here, state it: e.g. "Subject lines start with a conventional-commit type (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`) and an optional scope in parentheses." If any conventional-commit type is acceptable, say "any type from the Conventional Commits spec" so the example's scope reads as illustrative rather than mandatory.
>
> ## Suggested revised document (pending author's decision on finding 1)
>
> ```markdown
> ---
> name: commit-conventions
> description: Use when writing or reviewing commits in this repository.
> ---
>
> # commit-conventions
>
> ## Rules
>
> - Never force-push to `main`.
> - Force-pushing your own feature branch is permitted.
> - Every commit message includes a `Test plan:` line describing how the change was verified.
> - Subject lines start with a conventional-commit type prefix (scope optional).
> - Reviewers reject any pull request whose branch was force-pushed over `main`.
>
> ## Context
>
> Feature branches are routinely rebased and force-pushed; only `main` is protected.
>
> ## Example
>
> A well-formed commit for this repository looks like this:
>
>     fix(postings): reject negative minor-unit amounts
>
>     Negative amounts were reaching the ledger through the CSV importer.
>
>     Test plan: added a unit test for a negative minor-unit CSV row; ran the postings test suite.
> ```
>
> ## Summary
>
> | # | Severity | Issue | Location |
> |---|----------|-------|----------|
> | 1 | High | Rule 1's real scope (only `main`) is stated as an exemption in the notes, contradicting the absolute rule | Rules / Notes for reviewers |
> | 2 | High | "Well-formed" example omits the mandatory `Test plan:` line | Example |
> | 3 | Low | Reviewer obligation is hedged ("should"), placed in notes, and not reachable via the description's trigger | Notes for reviewers / frontmatter |
> | 4 | Low | Rule 3 leaves type set and scope requirement to be inferred from the example | Rules |
>
> Findings 1 and 2 are the ones that will change agent behavior in practice; both should be fixed before this skill is relied on.

### Baseline, rep 2

> # Audit: `commit-conventions` — separation of context from constraints
>
> Two-level severity: **Blocking** (an agent following this document will do the wrong thing or cannot tell what binds) and **Advisory** (works, but the constraint is weaker or less locatable than it should be).
>
> ## Blocking
>
> ### B1. The "Notes for reviewers" section silently overrides Rule 1
>
> Rule 1 says "Never force-push to any branch." The Notes section then says "Force-pushing a personal feature branch is fine and happens routinely during rebases." That second sentence is not context — it is a permission that narrows the rule, and it lives in a section whose heading ("Notes") signals non-binding prose addressed to a different audience. The reviewer directive in the same section ("reject a pull request that force-pushes over `main`") also enforces only `main`, so the enforcement scope disagrees with the stated rule as well.
>
> Consequence: an agent that reads the Rules section as authoritative will refuse to rebase-and-force-push its own branch; an agent that reads the Notes will treat Rule 1 as loosened but has no stated boundary for how far (is `develop` a "personal feature branch"?). Two readers of the same document reach opposite behaviour.
>
> Fix: state the real scope once, in Rules, and remove the contradiction. The Notes sentence and the reviewer criterion both point to `main` as the protected branch, so the most likely intended rule is:
>
> > - Never force-push to `main`. Force-pushing your own feature branch is permitted.
>
> The rationale ("happens routinely during rebases") can stay as a trailing clause or be dropped; it is not load-bearing. **This is the one place the author must confirm intent** — the document as written cannot be rewritten without choosing between "any branch" and "`main`".
>
> ### B2. The example contradicts Rule 2
>
> Rule 2: "Every commit message includes a `Test plan:` line." The Example section presents a commit with no `Test plan:` line and labels it "well-formed." Examples are context, but agents imitate examples more reliably than they parse rules; a template that omits a required element teaches the omission. As written, the document's only concrete artifact violates its own constraint.
>
> Fix (semantic-preserving — add the required line, change nothing else):
>
> ```
> fix(postings): reject negative minor-unit amounts
>
> Negative amounts were reaching the ledger through the CSV importer.
>
> Test plan: added a unit test for a negative amount; ran the importer against the fixture CSV.
> ```
>
> ### B3. A binding reviewer rule is buried in a notes section and hedged
>
> "Reviewers should reject a pull request that force-pushes over `main`" is a directive with a specific audience and a specific action, but it is (a) in a section named "Notes," (b) hedged with "should," and (c) addressed to an audience the frontmatter description ("Use when writing commits") does not cover, so a reviewer agent will never load this document to find it. It is also not testable as stated: a pull request does not force-push; a force-push is a branch operation. The reviewer cannot tell from a PR what event this refers to.
>
> Fix: either move it into Rules with an explicit audience and a checkable condition, e.g.
>
> > - Reviewers: reject a pull request whose branch history shows `main` was force-pushed.
>
> and widen the description to "Use when writing or reviewing commits in this repository" — or, if the reviewer directive is not meant to be owned by this skill, delete it here and relocate it to the reviewing skill. Either way, do not leave a rule under a "Notes" heading.
>
> ## Advisory
>
> ### A1. Rule 3 names a spec but not its parameters
>
> "Subject lines use a conventional-commit type prefix" is testable against the Conventional Commits spec, but the document does not say whether a scope (`fix(postings)`) is required or optional, or whether the full type list is allowed. The example implies a scope is expected. If a scope is required, say so; if not, say "scope optional."
>
> ### A2. Rule 2 does not say where the `Test plan:` line goes
>
> Body? Footer? Any line? Presence is testable; placement is not specified. A one-word addition ("...includes a `Test plan:` line in the body...") removes the ambiguity, and the corrected example (B2) then shows it.
>
> ### A3. Mixed mood in Rules
>
> Rule 1 is an imperative ("Never"), Rules 2–3 are declaratives ("Every commit message includes...", "Subject lines use..."). Under a "Rules" heading declaratives are conventionally read as binding, so this is not a failure, but consistent imperatives ("Include a `Test plan:` line...", "Prefix the subject line with...") make bindingness unmistakable.
>
> ## What is already right
>
> - Rules are in a dedicated, labelled section, one obligation per bullet, no compound rules.
> - Rule 2 is mechanically checkable (presence of a literal line).
> - No hedged language ("generally", "try to") in the Rules section itself.
>
> ## Summary
>
> Three blocking findings, all the same shape: material that binds (a scope exception, a reviewer directive, an implicit template) sits in sections framed as context, while the Rules section states something the rest of the document contradicts. Resolve B1 by choosing and stating the real force-push scope in Rules; resolve B2 by adding the `Test plan:` line to the example; resolve B3 by promoting or relocating the reviewer rule and aligning the description with the document's actual audiences.

### Baseline, rep 3

> # Audit: `commit-conventions` — separation of context from constraints
>
> Scope: the document as pasted, nothing else. Severity uses two levels: **Blocking** (an agent following the document as written will do the wrong thing or cannot tell which statement binds) and **Advisory** (clarity or placement issue; behaviour is probably still correct).
>
> ## Summary
>
> The `## Rules` section itself is in good shape: three short, imperative, individually testable rules. The problems are all outside it. Two pieces of context — a sentence in "Notes for reviewers" and the "Example" — directly contradict rules in the Rules section, so the document's context undercuts its constraints rather than supporting them. A third item is a binding directive hiding in a section titled as notes.
>
> ## Findings
>
> ### F1 — Blocking: context contradicts Rule 1 (force-push)
>
> **Location:** `## Rules`, bullet 1, versus `## Notes for reviewers`, sentence 2.
>
> - Rule: "Never force-push to any branch."
> - Context: "Force-pushing a personal feature branch is fine and happens routinely during rebases."
>
> These cannot both be true. An agent that reads only the Rules section will refuse to force-push a feature branch after a rebase; an agent that reads the whole document has to guess whether the note is an exception to the rule or the rule is a typo. Exceptions to a rule must live in the rule, not in narrative prose elsewhere.
>
> The correct rewrite depends on which statement reflects the author's intent, so the author must choose. Both options are semantic-preserving for one of the two sentences:
>
> *Option A (the note is right; the rule is over-broad):*
> ```
> - Never force-push to `main`. Force-pushing your own feature branch (for example after a rebase) is permitted.
> ```
> and delete the second sentence of "Notes for reviewers".
>
> *Option B (the rule is right; the note is wrong):*
> Keep the rule as written and delete "Force-pushing a personal feature branch is fine and happens routinely during rebases."
>
> ### F2 — Blocking: the "well-formed" example violates Rule 2 (Test plan line)
>
> **Location:** `## Rules`, bullet 2, versus `## Example`.
>
> Rule 2 says every commit message includes a `Test plan:` line. The example is introduced as "a well-formed commit for this repository" and has no `Test plan:` line. Examples are the strongest imitation signal in a document like this; an agent will copy the example's shape and omit the line, and the rule will be silently lost.
>
> Suggested rewrite (adds the missing element; no other change to the example):
> ```
> fix(postings): reject negative minor-unit amounts
>
> Negative amounts were reaching the ledger through the CSV importer.
>
> Test plan: added an importer unit test for a negative amount; ran the full ledger test suite.
> ```
> If the `Test plan:` line is in fact optional, the fix is instead to delete Rule 2 — but one of the two must change.
>
> ### F3 — Advisory: a binding directive is placed in a section titled as notes and hedged with "should"
>
> **Location:** `## Notes for reviewers`, sentence 1: "Reviewers should reject a pull request that force-pushes over `main`."
>
> This is a rule, not background: it tells a reviewer what to do. It is outside `## Rules`, under a heading ("Notes") that signals non-binding content, and softened with "should", so an agent acting as reviewer cannot tell whether it is required or merely customary. It is also outside the skill's stated trigger ("Use when writing commits"), so a reviewing agent may never load this document.
>
> Suggested rewrite: move it into the Rules section under its own audience heading and make it imperative:
> ```
> ## Rules
>
> ### For commit authors
> - ...
>
> ### For reviewers
> - Reject any pull request that force-pushes over `main`.
> ```
> Alternatively, if this skill is meant only for authors, remove the reviewer rule and put it in a review-focused document. Either way, note that once F1 is resolved via Option A this reviewer rule is the enforcement counterpart of the author rule and the two should be worded to match ("`main`" in both).
>
> ### F4 — Advisory: Rule 3 is testable but under-specified
>
> **Location:** `## Rules`, bullet 3: "Subject lines use a conventional-commit type prefix."
>
> Testable in principle, but the document does not say which types are accepted, whether a scope in parentheses is required (the example uses one), or whether the `!` breaking-change marker is permitted. An agent will infer the answer from the single example. Suggested rewrite:
> ```
> - Subject lines use a Conventional Commits prefix: `<type>(<scope>): <summary>`. Accepted types: feat, fix, docs, chore, refactor, test. Scope is optional.
> ```
> (Fill in the actual accepted-type list and scope policy; the values above are placeholders.)
>
> ### F5 — Advisory: Rule 2 mixes a checkable requirement with an uncheckable quality judgement
>
> **Location:** `## Rules`, bullet 2: "...a `Test plan:` line describing how the change was verified."
>
> Presence of the line is mechanically checkable; "describing how the change was verified" is a judgement about adequacy that no reviewer or hook can test consistently. This is acceptable as written if the intent is only to require the line, but if there is a minimum standard (for example, "must name the command run"), state it. Suggested rewrite if a standard exists:
> ```
> - Every commit message includes a `Test plan:` line naming the command(s) or manual steps used to verify the change.
> ```
>
> ## Items checked and found clean
>
> - Frontmatter `description` is a single trigger condition with no embedded rules.
> - Rules 1–3 are each one obligation per bullet; no compound rules.
> - No rules are buried mid-paragraph inside the Rules section; no padding or explanation there.
> - The note "happens routinely during rebases" is genuine context (it explains why, not what to do) and is fine as context once F1 is resolved.
>
> ## Recommended order of fixes
>
> 1. Resolve F1 — the author must decide which of the two statements is true; nothing else in the document is coherent until this is settled.
> 2. Fix F2 by adding the `Test plan:` line to the example (or dropping Rule 2).
> 3. Relocate the reviewer directive per F3, aligned with the F1 decision.
> 4. F4 and F5 at the author's discretion.
