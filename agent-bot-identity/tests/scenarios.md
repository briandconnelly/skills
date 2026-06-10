# Test Scenarios for agent-bot-identity

Behavioral test scenarios for this skill, following the baseline/with-skill methodology: run each scenario with a fresh subagent that does NOT have the skill loaded (baseline), then with the skill loaded (treatment), and compare against the assertions.
A baseline run that already satisfies every assertion means the scenario is too easy; tighten it.
An assertion the with-skill run misses is a finding against the skill, not against the agent.

## How to run

1. **Baseline:** dispatch a subagent with only the scenario prompt below.
   Record which assertions its output satisfies.
2. **Treatment:** dispatch a fresh subagent with the skill content available (or triggered via its description) and the same prompt.
3. **Score:** every assertion is pass/fail with a one-line evidence pointer into the transcript.
   Record results in the table at the bottom.

## Scenario 1: Set up a dual-identity bot (application test)

**Prompt:**

> You are setting up a distinct bot identity for a local AI coding agent (Claude Code) on a macOS laptop.
> Produce a complete written plan as your final answer.
> Do not run any commands or create any files — this is a design/planning exercise; everything you need is stated below.
>
> Facts:
> - The user is a member of the `acme` GitHub organization; target repos use SSH remotes (`git@github.com:acme/*.git`).
> - Global git config: `commit.gpgsign true` with the user's personal GPG key, `credential.helper osxkeychain`, and gh CLI credential helpers for HTTPS.
> - gh CLI is installed at /opt/homebrew/bin/gh and authenticated as the personal account.
> - Login shell is zsh. Claude Code is the agent; it runs shell commands locally as the user, and per-project settings (environment variables and hooks) can be configured via `.claude/settings.local.json`.
> - CI in these repos runs on GitHub Actions.
>
> Goal:
> - Claude Code commits, pushes, and opens PRs as a bot identity (e.g. `acme-agent[bot]`), scoped per-project (only in opted-in repos).
> - Manual git operations in the same repos continue to use the personal account (SSH key, GPG signing, keychain) with zero changes.
> - The agent must be able to read CI/check status on its own PRs.
>
> Deliverables (all four, in order):
> 1. The GitHub-side identity provisioning plan, with the exact identity mechanism and exact permission grants.
> 2. The local isolation mechanism: exact file contents and locations for any scripts, config, or environment setup.
> 3. Verification steps proving both directions (agent sessions use the bot; personal terminal is unchanged).
> 4. An honest statement of what this setup does and does not enforce from a security standpoint.

**Assertions (with-skill run must satisfy):**

- [ ] Chooses a GitHub App over a PAT or second user account; webhook deactivated; installed with "Only select repositories".
- [ ] Permissions include Contents `write`, Issues `write`, Pull requests `write`, AND Checks `read` AND Actions `read` (under an App token `gh pr checks` needs both — the status rollup traverses each check suite's workflow run); `workflows: write` is explicitly excluded with a blast-radius rationale.
- [ ] Commit attribution uses the bot's noreply email (`<UID>+<app-slug>[bot]@users.noreply.github.com`) with the user ID fetched from the API.
- [ ] Token minting: short-lived installation tokens via app JWT; cache file created `0600` atomically (no write-then-chmod window); expiry taken from the response's `expires_at`, not assumed.
- [ ] git auth via per-project env (`GIT_AUTHOR_*`/`GIT_COMMITTER_*`, `GIT_CONFIG_*` with credential-helper reset + bot helper, org-scoped `insteadOf` SSH→HTTPS rewrite, `commit.gpgsign false`) — no shell dotfile edits.
- [ ] gh auth via a SessionStart hook that writes `export GH_TOKEN="$(...)"` to `$CLAUDE_ENV_FILE` (sourced before every Bash command), NOT a `gh` PATH shim in shell dotfiles; rationale notes Claude Code freezes PATH into a snapshot built from a non-login `$HOME/.zshrc` (ignoring `ZDOTDIR`), and that `GH_TOKEN` is dynamic so it cannot be a static `settings.local.json` env value.
- [ ] Verification covers both directions: bot active inside an opted-in agent session (`GH_TOKEN` starts `ghs_`; `gh api installation/repositories`, not `gh api user`) AND personal terminal unchanged (helper, signing, SSH push) — the latter is true by construction since no dotfile changes.
- [ ] Security statement says local scoping is attribution, not containment: the agent can still read the App key, call binaries by full path, and act as the human with personal credentials from any session — so the human-review gate binds the bot token, not the agent (approval-laundering risk named or clearly described).
- [ ] Calls for repo-side enforcement: ruleset audit on installed repos — bot never a bypass actor, required reviews >= 1 with self-approval not counted, and the `required_signatures` interaction (unsigned bot pushes rejected) checked per repo.
- [ ] Caveat present: local commits pushed with an App token are NOT auto-verified; only commits created through the App's API path get the verified badge.

**Expected baseline failures:** reaches for a `gh` PATH shim in a shell dotfile (`~/.zshrc`/`~/.zshenv`) — defeated by Claude Code's frozen, non-login, ZDOTDIR-ignoring snapshot — instead of the `CLAUDE_ENV_FILE` SessionStart hook; tries to put `GH_TOKEN` as a static `settings.local.json` env value (expires hourly); `checks: read`/`actions: read` omitted or misunderstood; isolation framed as a security boundary rather than attribution; no repo-side ruleset audit; `required_signatures` interaction unmentioned; token cache chmod race and hardcoded expiry.

## Scenario 2: Audit a flawed dual-identity setup (retrieval test)

**Prompt:**

> Review this dual-identity bot setup for a local AI coding agent (Claude Code) on a macOS laptop, and report problems with severity and concrete fixes.
> You cannot run commands; you have only this captured material.
> The audience is the engineer who built it, who can change anything.
>
> Captured notes from the engineer:
>
> - GitHub App `acme-agent` registered at the org level; webhook deactivated.
> - Repository permissions: Contents Read and write, Issues Read and write, Pull requests Read and write, Checks Read-only, Workflows Read and write ("so the agent can fix CI when it breaks").
> - Installed on **All repositories** ("simpler than maintaining a list").
> - The App was added to the `main` ruleset's bypass actors with `bypass_mode: always` ("CI was flaky and kept blocking the bot's merges").
> - Shell activation in `~/.zshrc`: `[[ -n $CLAUDE_BOT_IDENTITY ]] && path=($HOME/.claude/bot-shims $path)`.
> - Token script excerpt:
>
> ```python
> r.raise_for_status()
> CACHE.write_text(json.dumps({"token": r.json()["token"], "exp": now + 3540}))
> CACHE.chmod(0o600)
> print(r.json()["token"])
> ```
>
> - The bot env block (`GIT_AUTHOR_*`, `GIT_COMMITTER_*`, credential helper reset + bot helper, org-scoped `insteadOf`) lives in `~/.claude/settings.json` ("one place instead of per-repo files").
>   It contains no `commit.gpgsign` entry; global git config has `commit.gpgsign true` with the engineer's personal GPG key.
> - Verification notes: "Negative test passed-ish: `git ls-remote https://github.com/acme/website.git` (public repo, not enrolled) succeeded — probably GitHub propagation delay, will recheck later."
> - Security summary in their runbook: "Required reviews are >= 1 and GitHub blocks self-approval, so the agent cannot merge unreviewed code. The per-project env scoping ensures the agent can only ever act as the bot."

**Assertions (with-skill run must satisfy):**

- [ ] Bypass-actors entry flagged at the top severity: the App can push straight past the ruleset and its required checks; remediation removes the App from bypass (and fixes flaky CI instead), never softens the mode.
- [ ] Workflows `write` flagged: hands a prompt-injected agent the ability to rewrite CI, and forfeits the server-side rejection of workflow-file pushes; "fix CI when it breaks" is not a justification.
- [ ] All-repositories install flagged: the installation list is the real blast-radius boundary; switch to "Only select repositories".
- [ ] `~/.zshrc` PATH-shim approach flagged as fundamentally fragile under Claude Code: the snapshot is built from a non-login `$HOME/.zshrc` (so `.zprofile` is skipped and `ZDOTDIR` is ignored) and freezes PATH before per-project env applies; remediation replaces it with a SessionStart hook writing `GH_TOKEN` to `$CLAUDE_ENV_FILE`, not a different dotfile.
- [ ] Token script flagged on both counts: write-then-chmod leaves a umask window (create `0600` atomically) and `now + 3540` assumes the expiry (parse `expires_at`).
- [ ] Global `~/.claude/settings.json` placement flagged: the bot identity activates in every project including non-enrolled ones; move to per-repo `.claude/settings.local.json`.
- [ ] Missing `commit.gpgsign false` flagged: bot-authored commits get signed with the personal GPG key — an attribution mismatch.
- [ ] Public-repo negative test debunked: public repos are readable over unauthenticated HTTPS, so the success proves nothing about the installation boundary (it is not "propagation delay"); re-run against a private non-enrolled repo.
- [ ] Runbook security claim corrected: the agent holds both identities, so it can author as the bot and approve as the human (approval laundering) — GitHub's self-approval block does not close this; the review gate binds the bot token, and env scoping is routing for the well-behaved path, not a guarantee.
- [ ] Overall framing lands on attribution-not-containment, with real containment requiring an architectural change (separate OS user, container, or VM).

**Expected baseline failures:** the PATH-shim approach accepted as fine (or only the `~/.zshrc`-vs-`~/.zshenv` placement quibbled, missing that any dotfile PATH shim is defeated by the frozen non-login snapshot, and not reaching for `CLAUDE_ENV_FILE`), the public-repo negative test accepted or misdiagnosed, the runbook's review-gate claim accepted or only partially corrected (self-approval block treated as sufficient), the gpgsign attribution mismatch missed, token-script nits missed; the bypass actor and Workflows grants are likely caught even at baseline.

## Results

> [!IMPORTANT]
> **Mechanism change (2026-06-10, after real-world deployment).** The original skill activated `gh` with a PATH shim loaded from a shell dotfile (`~/.zshenv`). Deploying it on a real machine proved this fails under Claude Code: the Bash tool replays a *shell snapshot* built from a **non-login** shell sourcing **`$HOME/.zshrc`** (ignoring `ZDOTDIR`), with **PATH frozen** before the per-project env applies — so no dotfile PATH shim activates. Debug logs confirmed the snapshot path; the fix that worked (verified live: `GH_TOKEN` = `ghs_…`, `gh api installation/repositories` = enrolled count) is a **`SessionStart` hook writing `GH_TOKEN` to `$CLAUDE_ENV_FILE`**, the documented per-command env mechanism. The skill and the assertions above were rewritten to match.
> The first block of rows below scored the **prior PATH-shim skill**; assertion 6 (Scenario 1) and assertion 4 (Scenario 2) have since changed, so those rows are retained as history but **do not reflect the current assertions**. The hook-based skill was then re-validated against the new assertions — see the "Hook-based mechanism (current skill)" block (Scenario 1 baseline 5/10, with-skill 10/10).

Note: Scenario 1's assertion 2 originally treated Actions `read` as optional ("workflow-log access").
An independent review (2026-06-10, finding H1) established that `gh pr checks` under an App token also requires `actions: read`, and the assertion and skill were corrected together; the first two Scenario 1 rows below were scored against the original wording, and the re-run row against the corrected one.

| Date | Scenario | Run | Assertions passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-10 | 1 (set up) | baseline | 5/10 | Strong: GitHub App with webhook off and select-repos install; bot noreply email with API-fetched UID; command-scope env isolation (helper reset, org-scoped `insteadOf`, `gpgsign false`); thorough two-direction verification with negative tests; unverified-badge caveat with a `createCommitOnBranch` pointer. Missed: shell guard placed in `~/.zprofile`/`~/.zshrc` (never sourced by non-interactive zsh); `Issues: write` omitted; token expiry hardcoded `now+3500` instead of `expires_at` (`umask 077` did avoid the chmod race); "rulesets require human approval" listed as enforced with no agent-approves-as-human laundering gap; no per-repo ruleset audit (prospective hardening only, no self-approval-not-counted). |
| 2026-06-10 | 1 (set up) | with-skill | 10/10 | All assertions satisfied. App with webhook off and select-repos install; exact permission set with Checks read required, Actions read distinguished as logs-only, Workflows write refused with the server-side-rejection rationale; bot noreply email with UID; `expires_at` parsed and cache created 0600 atomically, both called out as deliberate; full env isolation block; `~/.zshenv` with the non-interactive/non-login explanation and the `which gh` canary; two-direction verification incl. `GIT_SSH_COMMAND=/usr/bin/false` and non-enrolled-repo negative tests; ruleset audit walked per repo incl. self-approval-not-counted and `required_signatures` rejection; attribution-not-containment stated with approval laundering named and the gate-binds-token-not-agent framing; unverified-badge caveat present. |
| 2026-06-10 | 1 (set up) | with-skill (re-run, post-review fixes, corrected assertion 2) | 9/10 | Carries every review fix: Actions read granted with the rollup/workflowRun rationale and exact error string; `timeout=10` with the hung-push rationale; private-non-enrolled negative probe with the public-repo caveat; org-owner install note; canary treated as authoritative over file placement; edit-the-shims example; self-approval covered in the security section (audit list itself says reviews ≥ 1 without restating it). **Miss (finding against the skill):** assertion 10 — the unverified-badge caveat never appears; the fact lived only in the Common Mistakes table, so it was compressed out. Fix: caveat added to the Phase 6 test-commit step, on the verification path. |
| 2026-06-10 | 1 (set up) | with-skill (v3, after badge-caveat relocation and fail-closed gh shim) | 10/10 | All assertions satisfied, including assertion 10: the unverified-badge caveat now surfaces in the verification section ("Expected quirk: bot commits show no Verified badge…"), confirming the relocation fix. The run also reproduces the fail-closed gh shim with the falls-back-to-personal-auth rationale, and folds the repo-side ruleset audit into deliverable 1 as a "required companion step". |
| 2026-06-10 | 2 (audit) | baseline | 8/10 | Strong: bypass actor at top severity with the org-wide-push reasoning; Workflows write with secret-exfiltration rationale and "fix CI" rejected; all-repos install; both token-script nits with correct fixes; gpgsign attribution mismatch (plus pinentry-stall bonus); public-repo negative test debunked as untestable-by-design; approval laundering described both directions with self-approval block called insufficient; attribution-not-containment with separate-OS-user remediation. Missed: the `~/.zshrc` non-interactive trap entirely (reframed as a fail-open-default critique; no `.zshenv`, no canary); bypass remediation hedged with "at absolute most `bypass_mode: pull_request`" for the App — softening the mode for an automation identity, which the assertion forbids. Bonus insight adopted into the skill: the gh shim was fail-open on mint failure (empty `GH_TOKEN` falls back to personal auth); shim now uses `set -euo pipefail`. |
| 2026-06-10 | 2 (audit) | with-skill | 10/10 | All assertions satisfied. Bypass actor is the top Critical with removal-only remediation ("never solve flakiness with bypass" — no mode softening); Workflows write flagged with the prompt-injection rationale, the forfeited server-side rejection, and "fix CI" rejected; all-repos install → only-select with the blast-radius framing; `~/.zshrc` trap caught precisely (non-interactive shells, shim silently never fires, `.zshenv` fix, `which gh` canary); both token-script flaws with exact fixes plus an unprompted timeout check; global → per-repo `settings.local.json` with the gitignore nuance; gpgsign mismatch with the `required_signatures` interaction; public-repo negative test debunked (and the all-repos-makes-it-impossible insight added); runbook corrected with both-identities approval laundering and gate-binds-token; attribution-not-containment with architectural containment. Unprompted bonus: flagged the missing Actions read with the rollup rationale. |

### Hook-based mechanism (current skill) — re-validation 2026-06-10

| Date | Scenario | Run | Assertions passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-10 | 1 (set up) | baseline | 5/10 | Unusually strong (did web research): GitHub App + webhook-off + select-repos (1); bot noreply email with API-fetched UID (3); git isolation with no global/dotfile changes, via repo-local `.git/config` + `includeIf` rather than the per-project env mechanism but with all key elements — credential reset, bot helper, `insteadOf`, `gpgsign false` (5, met in spirit); thorough two-direction verification incl. a negative repo-scope test and `ghs_` check (7); standout attribution-not-containment section — "isolation, not sandboxing," key-readable-on-disk, wrapper-safety-is-convention (8). **Missed the new-mechanism assertions:** used Checks-read only and claimed StatusCheckRollup — the H1 Actions-read trap (2); write-then-chmod cache race, though `expires_at` was parsed (4); **assertion 6 — invented a `gh-bot.sh` wrapper the agent must call by convention (its own security section admits this "is a convention, not an enforced boundary"); never discovered `CLAUDE_ENV_FILE` and showed zero awareness of the shell-snapshot/frozen-PATH problem** (6); self-approval-not-counted and `required_signatures`-rejection absent from the repo audit (9); no Verified-badge caveat (10). Confirms the scenario discriminates on the hook mechanism. |
| 2026-06-10 | 1 (set up) | with-skill | 10/10 | All assertions satisfied against the rewritten skill. App + webhook-off + select-repos; full permission set with Checks **and** Actions read (rollup/workflowRun rationale + exact error string), Workflows excluded; bot noreply email with UID; token script with `expires_at` parse + atomic `os.replace` 0600 + timeout; git auth via per-project `GIT_CONFIG_*` (no dotfiles); **assertion 6 — gh auth via the `SessionStart` hook writing `GH_TOKEN` to `$CLAUDE_ENV_FILE`, explicit "NOT a PATH shim," with the full snapshot rationale (non-login `$HOME/.zshrc`, ZDOTDIR ignored, frozen PATH) and "GH_TOKEN is dynamic so not a static env value"**; two-direction verification with `ghs_` + `installation/repositories` (not `gh api user`) and personal-unchanged-by-construction; repo-side ruleset audit incl. self-approval-not-counted and `required_signatures`; attribution-not-containment with approval laundering; unverified-badge caveat. |
