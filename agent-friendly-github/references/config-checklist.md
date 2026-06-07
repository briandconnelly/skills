# Configuration Checklist

This is the mechanical standard walked by both the Set up and Audit workflows.
Each item names the concrete GitHub mechanism where one exists, and otherwise states the policy to enforce; see `threat-model.md` for the rationale behind each control.
Public/private and monorepo/traditional variations are noted inline where the requirement differs.
Walk the sections in order; they are numbered §1–§4 and cited by that number elsewhere in the skill.

## §1 Issues & PRs

- Issue and PR templates are present and in use: `.github/ISSUE_TEMPLATE/` directory for issues and `.github/PULL_REQUEST_TEMPLATE.md` for pull requests. (productivity; closes T1 via reduced ambiguity)
- Label taxonomy covers type and priority labels; monorepos add `scope/<area>` labels so PRs and issues are routable per subtree. (productivity)
- `CODEOWNERS` uses explicit path prefixes, never a catch-all-only rule; owners on protected paths must be human users or teams, kept bot-free by membership hygiene — GitHub has no native "owners must be human" enforcement, so this is a repository policy you maintain; the goal is that a required CODEOWNERS review can never be satisfied by an agent. Monorepo: one prefix per owned subtree. (closes T3)
- Required reviews are enabled on protected branches and enforced through CODEOWNERS. (closes T3)
- Draft-first on owned paths: GitHub has no native "require draft by path" feature, so enforce it with a required status check that blocks merge while the PR is draft on owned paths; this is a supplementary signal — the human-judgment gate itself is the required CODEOWNERS review (§2), not the draft check, because any actor (including an agent) can promote a draft to ready. (closes T3)
- Canonical instruction file (`AGENTS.md`) is present; per-tool files are thin references to it; reusable procedures live as committed skills, not pasted into instruction files; monorepos add a nested `AGENTS.md` per subtree. (closes T1 via clear guidance)
- `CONTRIBUTING` is present and discoverable (`CONTRIBUTING.md` or `.github/CONTRIBUTING.md`) describing branch, PR, and review expectations that a contributor or agent must follow. (productivity; closes T1)
- `SECURITY.md` is present (required for public repos; cross-referenced in §4 with private vulnerability reporting). (closes T1)
- `.gitignore` is present and covers the language/framework's secret-bearing and noise paths (`.env*`, `*.pem`, `*.key`, `*.p12`, credential files, build output, caches, dependency dirs); it is the preventive layer in front of §3's secret scanning and push protection, and it keeps PR diffs reviewable; note it does NOT untrack already-committed files — a `git rm --cached` plus history rewrite is needed for those, and that rewrite is the force-push the branch guardrails otherwise warn against, which is why prevention via `.gitignore` matters. (closes T5)
- `.gitattributes` sets `* text=auto` (with `eol=lf`, or `eol=crlf` on Windows-primary repos) to prevent line-ending churn across agent platforms, and marks generated files (lockfiles, build output) with `linguist-generated=true` to keep PR diffs reviewable; note `linguist-generated` affects GitHub's diff display and language stats only — it does not enforce anything; also note that adding `* text=auto` to a repo that already has mixed line endings will produce a one-time normalization (churn) commit on first add/commit. (auditability)

## §2 Branch / Repo Guardrails

- Rulesets (or branch protection) are applied to the default and release branches for ALL actors with an empty bypass-actors list (no admins, apps, or PATs) so nothing can push past it.
  Merge queue operates through the ruleset's normal flow and does not require a bypass-actors entry. (closes T4)
- Required status checks are configured; in monorepos, use a single always-running gate check per relevant scope that detects changed paths internally and short-circuits (exits 0) when nothing relevant changed — do NOT use `paths:` filters on a required check, because a skipped workflow leaves the required check PENDING and blocks merge forever; per-directory rulesets are an alternative. (closes T4)
- `dismiss_stale_reviews` is enabled so a post-approval push invalidates the prior approval; this is the branch-protection or ruleset setting, not merely an agent convention. (closes T3)
- Linear history is required. (closes T8)
- Signed commits are required; define the accepted mechanism in your repo (GitHub App commit signing, GPG, or SSH) so audits know what evidence to check. (closes T8)
- Merge queue is configured where serialized merges matter. (productivity; closes T4)
- Force-push and branch deletion are blocked on protected refs. (closes T4)
- Auto-merge safety is a combination, not a single setting: required approving review count >= 1, self-approval not counted, and a CODEOWNERS-required human review — GitHub has no native "human-only approver" flag, so you assemble it from these three settings. (closes T3)
- Environment or deployment protection rules gate production via required reviewers or a wait timer on the environment. (closes T5)

## §3 Actions & Supply Chain

- Default `GITHUB_TOKEN` permissions are set to least privilege via a top-level `permissions:` block (read-only default; grant narrowly per job). (closes T5)
- Untrusted `github.event.*` strings are never interpolated directly into `run:` steps; bind them through `env:` and reference the environment variable. (closes T2)
- `pull_request_target` discipline: it runs privileged with repository secrets, so do not use it for untrusted PRs; gate it behind a protected environment or use plain `pull_request` from forks, which is read-only with no secrets by default. (closes T2)
- Third-party actions are pinned to a full commit SHA, not a mutable tag. (closes T6)
- OIDC is used for cloud authentication instead of stored long-lived secrets. (closes T5, T9)
- Secret handling: `ACTIONS_STEP_DEBUG` and `ACTIONS_RUNNER_DEBUG` are not enabled in production (debug logging can expose secrets). (closes T5)
- Dependabot is enabled for both version updates and security updates. (closes T6)
- Code scanning is enabled (CodeQL or an equivalent analyzer). (closes T6)
- Secret scanning is enabled with push protection. (closes T5)
- Dependency review is enabled on PRs; for agent-added packages, a scoped or private registry and a committed lockfile blunt dependency confusion. (closes T6, T7)

## §4 Auditability & Identity

- Distinct agent identity is provisioned, in preference order: GitHub App > fine-grained bot PAT > shared user account. (closes T8, T9)
- PATs, where used at all, are fine-grained and short-lived; classic broad PATs are never used. (closes T9)
- Commits are authored and signed with attribution preserved through squash and rebase; humans are co-authored when pairing. (closes T8)
- Audit-log retention is configured or explicitly considered for the org or repo plan. (closes T8)
- No mid-session privilege escalation: token scopes are provisioned up front; widening scope requires a human action. (closes T9)
- Private vulnerability reporting is enabled and `SECURITY.md` is present for public repos (see §1). (closes T1)
