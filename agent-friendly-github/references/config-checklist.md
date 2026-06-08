# Configuration Checklist

This is the mechanical standard walked by both the Set up and Audit workflows.
Each item names the concrete GitHub mechanism where one exists, and otherwise states the policy to enforce; see `threat-model.md` for the rationale behind each control.
Public/private and monorepo/traditional variations are noted inline where the requirement differs.
Walk the sections in order; they are numbered §1–§4 and cited by that number elsewhere in the skill.

## Plan & Visibility Caveats

Several controls are gated by repository visibility and GitHub plan.
Any control the repo's plan does not provide is marked N/A with the plan reason in an audit, and an external alternative is used where one exists.

| Control | Public repos | Private / internal repos |
| --- | --- | --- |
| Rulesets / branch protection, CODEOWNERS, Dependabot | All plans | All plans |
| Environment required reviewers & wait timers | All plans | GitHub Pro, Team, or Enterprise |
| Code scanning (CodeQL), secret scanning + push protection, dependency review | Free | GitHub Advanced Security |

## §1 Issues & PRs

- Issue and PR templates are present and in use: `.github/ISSUE_TEMPLATE/` directory for issues and `.github/PULL_REQUEST_TEMPLATE.md` for pull requests. (productivity; closes T1 via reduced ambiguity)
- Label taxonomy covers type and priority labels; monorepos add `scope/<area>` labels so PRs and issues are routable per subtree. (productivity)
- `CODEOWNERS` uses explicit path prefixes, never a catch-all-only rule; owners on protected paths must be human users or teams, kept bot-free by membership hygiene — GitHub has no native "owners must be human" enforcement, so this is a repository policy you maintain.
  The goal is that a required CODEOWNERS review can never be satisfied by an agent.
  Monorepo: one prefix per owned subtree.
  A human-owned last-resort catch-all is acceptable only after explicit path rules. (closes T3)
- Required reviews are enabled on protected branches and enforced through CODEOWNERS. (closes T3)
- Draft-first on owned paths is an operate convention, not a CI gate: open a protected-path change as a draft and wait for a human to promote it to ready; there is no robust required status check for "opened as draft" — a check that fails while the PR is ready-for-review blocks merge permanently, and one that only inspects the `opened` action is cleared by the next push; the enforcement for protected-path changes is the required CODEOWNERS review (§2), which requires a CODEOWNERS-listed human to approve. (closes T3)
- Canonical instruction file (`AGENTS.md`) is present; per-tool files are thin references to it; reusable procedures live as committed artifacts, not pasted into instruction files; monorepos add a nested `AGENTS.md` per subtree. (closes T1 via clear guidance)
- `CONTRIBUTING` is present and discoverable (`CONTRIBUTING.md` or `.github/CONTRIBUTING.md`) describing branch, PR, and review expectations that a contributor or agent must follow. (productivity; closes T1)
- `SECURITY.md` is present (required for public repos; cross-referenced in §4 with private vulnerability reporting). (closes T1)
- `.gitignore` is present and covers the language/framework's secret-bearing and noise paths (`.env*`, `*.pem`, `*.key`, `*.p12`, credential files, build output, caches, dependency dirs); it is the preventive layer in front of §3's secret scanning and push protection, and it keeps PR diffs reviewable; note it does NOT untrack already-committed files — a `git rm --cached` plus history rewrite is needed for those, and that rewrite is the force-push the branch guardrails otherwise warn against, which is why prevention via `.gitignore` matters. (closes T5)
- `.gitattributes` sets `* text=auto` (with `eol=lf`, or `eol=crlf` on Windows-primary repos) to prevent line-ending churn across agent platforms, and marks true generated build output with `linguist-generated=true` to keep PR diffs reviewable.
  Do not mark lockfiles as generated, because lockfile diffs are part of dependency review.
  Note `linguist-generated` affects GitHub's diff display and language stats only — it does not enforce anything.
  Adding `* text=auto` to a repo that already has mixed line endings will produce a one-time normalization commit on first add/commit. (auditability)
- Metadata a PR template prompts for that matters for safety or correctness (a linked issue, a changelog entry, a migration note) is verified by a CI check that is marked REQUIRED in the §2 ruleset — a check enforces nothing until it is required, and a template's prose or checkboxes are never treated as evidence the property holds. (closes T3)

## §2 Branch / Repo Guardrails

- Rulesets (or branch protection) are applied to the default and release branches for ALL actors with an empty bypass-actors list (no admins, apps, or PATs) so nothing can push past it.
  Merge queue operates through the ruleset's normal flow and does not require a bypass-actors entry. (closes T4)
- Required status checks are configured; in monorepos, use a single always-running gate check per relevant scope that detects changed paths internally and short-circuits (exits 0) when nothing relevant changed — do NOT use `paths:` filters on a required check, because a skipped workflow leaves the required check PENDING and blocks merge forever; there is no ruleset condition that scopes a required status check to changed file paths (branch rulesets target refs, not changed files), so the always-running aggregate gate or an external check app are the correct alternatives. (closes T4)
- `dismiss_stale_reviews` is enabled so a post-approval push invalidates the prior approval; this is the branch-protection field (`dismiss_stale_reviews_on_push` in the rulesets API), not merely an agent convention. (closes T3)
- `require_last_push_approval` is enabled so the most recent push must be approved by someone other than its author, preventing an author from pushing after approval and merging unreviewed code; this is the strongest anti-approval-laundering control because it directly closes the "approve then sneak a commit" gap. (closes T3)
- Linear history is required. (closes T8)
- Signed commits are required; define the accepted mechanism in your repo (GitHub App commit signing, GPG, or SSH) so audits know what evidence to check. (closes T8)
- Merge queue is configured where serialized merges matter. (productivity; closes T4)
- Force-push and branch deletion are blocked on protected refs. (closes T4)
- Auto-merge safety is a combination, not a single setting: required approving review count >= 1, self-approval not counted, and a CODEOWNERS-required human review — GitHub has no native "human-only approver" flag, so you assemble it from these three settings. (closes T3)
- Environment or deployment protection rules gate production via required reviewers or a wait timer on the environment.
  Caveat: environment required reviewers and wait timers are available on public repos on all plans, but on private/internal repos they require GitHub Pro, Team, or Enterprise; if the plan does not provide them, use an external deployment-approval mechanism and mark this item N/A with the plan reason. (closes T5)

## §3 Actions & Supply Chain

- `GITHUB_TOKEN` permissions are least-privilege at both layers: the repository/org Actions "Workflow permissions" setting sets the DEFAULT `GITHUB_TOKEN` permission — set it to read-only so workflows that declare nothing start least-privilege; it is a default, not a hard ceiling, because a workflow can still elevate permissions via its own top-level or job `permissions:` block, so the per-workflow least-privilege `permissions:` declaration is the actual control — declare it in every workflow.
  Additionally, for workflows triggered by fork PRs the `GITHUB_TOKEN` is read-only with no repository secrets by default unless explicitly enabled. (closes T5)
- Untrusted `github.event.*` strings are never interpolated directly into `run:` steps; bind them through `env:` and reference it as a quoted shell variable (e.g. `"$PR_TITLE"`), never via `eval`. (closes T2)
- `pull_request_target` and `workflow_run` discipline: both run privileged with repository secrets and a write-capable token even when the triggering workflow could not, so prefer plain `pull_request` for untrusted fork PRs because it is read-only with no repository secrets by default.
  If `pull_request_target` is unavoidable, no job checks out or executes untrusted head code, and any job with secrets or write scopes is gated behind a protected environment with human approval.
  For `workflow_run`, do not trust artifacts, caches, or other inputs downloaded from the triggering run (they are attacker-controlled when the triggering run came from a fork), and do not check out untrusted head code in any `workflow_run` job that holds secrets or write scope. (closes T2)
- Third-party actions are pinned to a full commit SHA, not a mutable tag. (closes T6)
- OIDC is used for cloud authentication instead of stored long-lived secrets. (closes T5, T9)
- Secret handling: `ACTIONS_STEP_DEBUG` and `ACTIONS_RUNNER_DEBUG` are not enabled in production (debug logging can expose secrets). (closes T5)
- Dependabot is enabled for both version updates and security updates. (closes T6)
- Dependency-update PRs (Dependabot or version bumps) pass through the same required reviews and status checks as any other change; where auto-merge is used it is limited to non-major updates with green checks and never bypasses the required review assembled in §2. (closes T6)
- Code scanning is enabled (CodeQL or an equivalent analyzer); on private/internal repos this requires GitHub Advanced Security (free on public repos) — configure where available, otherwise mark N/A with the plan reason. (closes T6)
- Secret scanning is enabled with push protection; on private/internal repos this requires GitHub Advanced Security (free on public repos) — configure where available, otherwise mark N/A with the plan reason. (closes T5)
- Dependency review is enabled on PRs; for agent-added packages, a scoped or private registry and a committed lockfile blunt dependency confusion; on private/internal repos dependency review requires GitHub Advanced Security (free on public repos) — configure where available, otherwise mark N/A with the plan reason. (closes T6, T7)

## §4 Auditability & Identity

- Distinct agent identity is provisioned, in preference order: GitHub App > fine-grained bot PAT > shared user account. (closes T8, T9)
- PATs, where used at all, are fine-grained and short-lived; classic broad PATs are never used. (closes T9)
- Commits are authored and signed with attribution preserved through squash and rebase; humans are co-authored when pairing. (closes T8)
- Audit-log retention is configured or explicitly considered for the org or repo plan. (closes T8)
- No mid-session privilege escalation: token scopes are provisioned up front; widening scope requires a human action. (closes T9)
- Private vulnerability reporting is enabled and `SECURITY.md` is present for public repos (see §1). (closes T1)
