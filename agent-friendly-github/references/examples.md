# Examples

Copy-adaptable artifacts implementing the controls in `config-checklist.md`; each is labeled with the §N section and threat class (Tn) it implements.
Adapt names, paths, org slugs, and SHAs to your repository before use.
Action SHAs and version comments throughout this file are illustrative examples only — verify and re-pin each SHA against the release you actually intend to use before deploying.

## Hardened Ruleset JSON

Implements: §2 (T3, T4, T8)

Apply via the GitHub Rulesets REST API (illustrative — substitute your owner and repo):

```sh
gh api --method POST repos/{owner}/{repo}/rulesets --input hardened-ruleset.json
```

JSON has no comment syntax; all caveats are in this prose.
The `bypass_actors` array is intentionally empty — no admins, apps, or PATs are exempted.
`non_fast_forward` blocks force-push to the protected ref.
`dismiss_stale_reviews_on_push` invalidates approvals after any new push, closing the post-approval-push gap (T3).
`require_code_owner_review: true` requires a human CODEOWNERS review (T3).
`required_signatures` requires signed commits (T8).
`required_linear_history` prevents merge commits (T8).
Replace `"context"` values under `required_status_checks` with the exact check names your CI jobs report.

```json
{
  "name": "default-branch-hardened",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "bypass_actors": [],
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "required_linear_history"
    },
    {
      "type": "required_signatures"
    },
    {
      "type": "pull_request",
      "parameters": {
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "required_approving_review_count": 1,
        "require_last_push_approval": true,
        "allowed_merge_methods": ["squash", "rebase"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          {
            "context": "CI / test",
            "integration_id": 0
          },
          {
            "context": "draft-gate / check",
            "integration_id": 0
          }
        ]
      }
    }
  ]
}
```

## Monorepo CODEOWNERS

Implements: §1 (T3)

```text
# Owners on protected paths must be human users or teams — never bot or agent accounts.
# A required CODEOWNERS review can only be satisfied by a listed owner,
# so listing a bot here would allow agent self-approval (T3).

# Per-package ownership — explicit path prefixes, no overlapping catch-all-only rules
/packages/auth/          @org/auth-team
/packages/billing/       @org/billing-team
/packages/core/          @org/platform-team

# Shared infrastructure owned by platform
/.github/                @org/platform-team
/infra/                  @org/infra-team

# Documentation owned by docs team
/docs/                   @org/docs-team

# Last-resort catch-all: any path not matched above goes to platform-team.
# Must be a human team, not a bot.
*                        @org/platform-team
```

## Issue and PR Templates

Implements: §1

Place the issue form at `.github/ISSUE_TEMPLATE/bug.yml` and the PR template at `.github/PULL_REQUEST_TEMPLATE.md`.

**`.github/ISSUE_TEMPLATE/bug.yml`** — a structured bug-report form that reduces ambiguity and prompt-injection surface (T1):

```yaml
name: Bug report
description: Report a reproducible defect
title: "[bug] "
labels:
  - bug
body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug.
        Fill in every section; incomplete reports will be closed.
  - type: textarea
    id: description
    attributes:
      label: Description
      description: What happened, and what did you expect?
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to reproduce
      description: Minimal steps that reliably trigger the bug.
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, runtime version, package version.
    validations:
      required: true
  - type: checkboxes
    id: existing
    attributes:
      label: Existing issues
      options:
        - label: I searched open issues and this is not a duplicate.
          required: true
```

**`.github/PULL_REQUEST_TEMPLATE.md`** — requires a linked issue, a test plan, and a security note:

```markdown
## Summary

<!-- One paragraph describing what this PR does and why. -->

Closes #

## Test plan

- [ ] Unit tests added or updated
- [ ] Integration tests pass locally (`uv run pytest`)
- [ ] Manual verification steps (list them):

## Security considerations

<!-- Does this change touch auth, secrets, permissions, or CI? Note it here. -->
None / see below:

## Checklist

- [ ] Branch is up to date with `main`
- [ ] Commit messages follow conventional commits
- [ ] CODEOWNERS paths updated if new owned paths were added
- [ ] PR is in draft until all checks pass and human review is requested
```

## Least-Privilege, Injection-Safe Actions Workflow

Implements: §3 (T2, T5, T6)

Key points enforced in this workflow:

- Top-level `permissions: {contents: read}` defaults the token to read-only; jobs that need more grant it narrowly.
- `github.event.pull_request.title` (untrusted input) is bound to an `env:` variable `PR_TITLE`; the `run:` step references `"$PR_TITLE"` — never `${{ github.event.pull_request.title }}` directly in a shell command (T2).
- The third-party action is pinned to a 40-hex commit SHA with a version comment (T6).
- `pull_request_target` is not used; this workflow uses `pull_request` which runs with a read-only token and no repository secrets for fork PRs (T2).

```yaml
# WARNING: never use pull_request_target for workflows that check out untrusted code
# or interpolate github.event.* into run: steps — it runs with repo secrets and
# write scope regardless of what it checks out. Use pull_request instead.
name: CI

on:
  pull_request:
    branches:
      - main

# Default token is read-only for all jobs in this workflow.
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout
        # Third-party action pinned to a full 40-hex commit SHA, not a mutable tag (T6).
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      - name: Log PR title safely
        # Bind the untrusted PR title via env: — NEVER interpolate ${{ github.event.* }}
        # directly into a run: script (T2 / injection-safe).
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: |
          echo "PR title: $PR_TITLE"

      - name: Set up Python
        uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2f  # v5.3.0
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@887a942a15af3a7626099df99e897a18d9e5ab3a  # v5.3.1

      - name: Run tests
        run: uv run pytest
```

## Agent Instruction File Pattern

Implements: §1

A canonical `AGENTS.md` at the repo root holds all agent guidance.
Per-tool files are thin pointers to it — they do not duplicate content.
For Claude Code, `CLAUDE.md` contains exactly one line (`@AGENTS.md`) and nothing else; Claude Code resolves the reference automatically.
Other tools use their own include or reference mechanism (for example, Gemini's `GEMINI.md` may use a different syntax — check the tool's documentation).
In a monorepo, add a nested `AGENTS.md` per subtree that has meaningfully different branching, testing, or off-limits rules; the root `AGENTS.md` sets defaults and the nested file overrides only the differences.

**`AGENTS.md`** — canonical agent instruction file at the repo root:

```markdown
# Agent Instructions

## Identity and attribution

- Use a distinct GitHub App identity or fine-grained PAT for automated commits.
- Every commit must carry a `Co-authored-by:` trailer when pairing with a human.
- Do not use classic broad PATs.

## Branching strategy

- Branch off `main` for all work: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`.
- Never commit directly to `main` or a release branch.
- Never force-push a remote ref without explicit human instruction.

## Commit format

- Follow Conventional Commits: `type(scope): short description`.
- Keep the subject line under 72 characters.
- Reference the issue number in the commit body: `Closes #<n>`.

## Pull requests

- Open all PRs as drafts; only mark ready for review after all checks pass.
- Never approve or auto-merge your own PR.
- Re-request human review after any post-approval push.
- CODEOWNERS paths require a human team review — do not attempt to satisfy it yourself.

## Testing

- Run `uv run pytest` before marking a PR ready.
- Do not merge if any required check is red.

## Off-limits paths

- `.github/workflows/` — do not edit CI workflows without explicit human instruction.
- `CODEOWNERS` — do not edit without explicit human instruction.
- `infra/` — do not edit production infrastructure files.

## Security

- Never interpolate `github.event.*` values directly into shell commands.
- Never enable `ACTIONS_STEP_DEBUG` or `ACTIONS_RUNNER_DEBUG` in production.
- Pin any third-party action you add to a full 40-hex SHA with a version comment.
```

**`CLAUDE.md`** — the complete file for Claude Code; a single line that references the canonical instruction file:

```text
@AGENTS.md
```

## Path-Filtered Required Checks

Implements: §2 (monorepo)

In a monorepo, each package's CI job should run only when that package changes.
Configure the workflow with `on: pull_request: paths:` so GitHub only triggers the job — and therefore only reports the status check — when the relevant paths are modified.
Then, in the branch ruleset, add that status check as a required check scoped to the same path filter.
A change in `packages/auth/` will not block a PR that touches only `packages/billing/`, because the `auth-ci` check will not run (and therefore will not be required) for that PR.

```yaml
name: auth-ci

on:
  pull_request:
    branches:
      - main
    paths:
      - "packages/auth/**"
      - ".github/workflows/auth-ci.yml"

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      - name: Set up Python
        uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2f  # v5.3.0
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@887a942a15af3a7626099df99e897a18d9e5ab3a  # v5.3.1

      - name: Run auth tests
        working-directory: packages/auth
        run: uv run pytest
```

After deploying this workflow, add `auth-ci / test` as a required status check in the ruleset for PRs touching `packages/auth/**`.
The GitHub UI under **Settings → Rules → Rulesets** lets you add required checks by name; the check name is `<workflow-name> / <job-id>` as GitHub reports it (here: `auth-ci / test`).

## Draft-First Enforcement Check

Implements: §1 (T3)

GitHub has no native "require draft by path" feature.
This required status check fills that gap: it runs on every PR targeting CODEOWNERS-owned paths and fails (exits non-zero) if the PR is marked ready for review without passing the draft-first gate.
Add `draft-gate / check` as a required status check in the branch ruleset so the PR cannot be merged while this check is red.

The check reads `github.event.pull_request.draft` (a boolean) and the list of changed files.
If the PR touches a protected path and is not in draft state — meaning no human explicitly promoted it from draft to ready — the step exits 1 and leaves the required check red.
Any untrusted PR fields (title, body) are bound via `env:` and never interpolated directly into `run:` scripts (T2).

```yaml
name: draft-gate

on:
  pull_request:
    types:
      - opened
      - ready_for_review
      - synchronize
    branches:
      - main

permissions:
  contents: read
  pull-requests: read

jobs:
  check:
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      - name: Enforce draft-first on protected paths
        # Bind untrusted PR fields via env: — never interpolate ${{ github.event.* }}
        # directly in a run: script (T2 / injection-safe).
        env:
          PR_DRAFT: ${{ github.event.pull_request.draft }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          GH_TOKEN: ${{ github.token }}
        run: |
          # Collect changed files for this PR
          changed=$(gh pr view "$PR_NUMBER" --json files --jq '[.files[].path] | join("\n")')

          # Protected path prefixes that require draft-first promotion
          protected_prefixes=(
            "packages/auth/"
            "packages/billing/"
            ".github/"
            "infra/"
          )

          touches_protected=false
          for prefix in "${protected_prefixes[@]}"; do
            if echo "$changed" | grep -q "^${prefix}"; then
              touches_protected=true
              break
            fi
          done

          if [ "$touches_protected" = "true" ] && [ "$PR_DRAFT" = "false" ]; then
            echo "ERROR: This PR touches a CODEOWNERS-protected path."
            echo "Open it as a draft first, complete all checks and human review,"
            echo "then have a human promote it to ready-for-review."
            exit 1
          fi

          echo "Draft-first gate passed."
```

## Supporting Files (CONTRIBUTING.md, SECURITY.md)

Implements: §1 (T1)

**`CONTRIBUTING.md`** — points contributors and agents at the canonical instruction file and sets process expectations:

```markdown
# Contributing

Agent guidance lives in [`AGENTS.md`](AGENTS.md); read it before opening any PR.

- Branch off `main`: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`.
- Open all PRs as drafts; mark ready for review only after all required checks pass.
- At least one human reviewer must approve before merge — agents may not self-approve.
- Run `uv run pytest` locally before marking a PR ready.
- Follow [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages.
```

**`SECURITY.md`** — directs security reporters away from public issues:

```markdown
# Security Policy

**Do not file security vulnerabilities as public GitHub issues.**

Report security issues privately using [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
or email the security contact listed in the repository's package metadata.

We will acknowledge reports within 5 business days and aim to resolve critical issues within 30 days.
```
