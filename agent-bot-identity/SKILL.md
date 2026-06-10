---
name: agent-bot-identity
description: Use when giving a local coding agent a distinct GitHub App bot identity — commits, pushes, and PRs attribute to the bot while manual git operations on the same machine keep the personal account untouched — or when auditing such a dual-identity setup. Covers App registration and scopes, installation tokens, per-project credential injection, verification, and what the isolation does and does not enforce. The App/token/credential-helper core is harness-neutral; the worked per-project wiring is a Claude Code adapter, with an explicit contract for what any other harness's adapter must provide.
---

# Agent Bot Identity

## Overview

Give a local coding agent its own GitHub App identity so every commit, push, and PR it makes attributes to a bot, while the human's git setup (SSH key, GPG signing, keychain credentials) stays untouched on the same machine.
The isolation mechanism is per-project configuration that injects the bot's credentials only into the agent's sessions in opted-in repos — without editing any shell dotfiles.

Core principle: **this buys attribution, not containment.**
The per-project scoping makes the well-behaved default path use the bot identity; the only hard boundaries are the App's installation list and the server-side rulesets of the repos it touches.
Never present this setup as a sandbox.

## When to Use

- Setting up Claude Code (or a similar local agent) to commit, push, and open PRs as a bot on a developer machine, with personal git operations unchanged.
- Auditing an existing dual-identity setup for over-trust — e.g. a review gate assumed to bind the agent, or local scoping treated as a security boundary.
- Symptoms: agent commits show the human as author; "have the agent open PRs as a bot"; bot PRs need human approval but the agent runs on the human's laptop.

## When Not to Use

- Repo-side configuration — rulesets, CODEOWNERS, required checks, Actions hardening — is the agent-friendly-github skill; this skill is the local-machine implementation of its §4 identity step, and Phase 6 here hands back to that skill's checklist.
- CI or hosted runners: mint the App token directly in the workflow (e.g. `actions/create-github-app-token`); there is no personal identity to isolate from.
- Hard security isolation: run the agent as a separate OS user, container, or VM; this skill does not provide that.

## Design at a Glance

| Layer | Mechanism | What it buys |
| --- | --- | --- |
| Identity | Org-owned GitHub App, webhook disabled | True `[bot]` attribution, fine-grained scopes, short-lived tokens, audit trail |
| Blast radius | App installed on "Only select repositories" | Token cannot touch non-enrolled repos, even if config leaks |
| Local routing | Per-project env/hook adapter — the contract is "inject the git env and a dynamic `GH_TOKEN` only in opted-in repos, no shell-dotfile edits"; Claude Code adapter: `.claude/settings.local.json` (env + SessionStart hook) | Bot identity activates only in opted-in repos; no shell dotfiles change |
| git auth | `insteadOf` SSH→HTTPS rewrite + git credential helper (`GIT_CONFIG_*`) | Pushes use the installation token, not the personal SSH key or keychain |
| gh auth | `GH_TOKEN` written to `$CLAUDE_ENV_FILE` by a SessionStart hook | `gh` calls use the installation token; sourced before every Bash command |
| Enforcement | Repo rulesets (Phase 6) | The only controls that bind a misbehaving agent |

## Phase 1 — Register the GitHub App

1. Register at the org level: Settings → Developer settings → GitHub Apps → New GitHub App.
   This needs org owner or "GitHub App manager" role; otherwise register under the personal account and have an org admin approve installation.
2. Name it for the agent (e.g. `acme-agent`); the actor becomes `acme-agent[bot]`.
   Homepage URL can be anything.
3. **Uncheck "Active" under Webhook** — this is a pure identity App; it receives no events.
4. Repository permissions (exact grants, nothing else):
   - Contents: **Read and write** (fetch, push branches)
   - Issues: **Read and write** (file and update issues, cross-link PRs)
   - Pull requests: **Read and write** (open, update, comment)
   - Checks: **Read-only** — required for the agent to read check-run status on its own PRs
   - Actions: **Read-only** — also required when CI runs on GitHub Actions: `gh pr checks` resolves the status rollup through each check suite's workflow run, and an App token lacking `actions: read` fails with "Resource not accessible by integration"
   - Metadata: Read-only (automatic)
   - Optional: Commit statuses Read-only (legacy status contexts)
   - **Never Workflows: Read and write** — a prompt-injected agent could rewrite CI; the absence is also a server-side control, because pushes touching `.github/workflows/` get rejected
5. Note the **App ID** from the settings page (GitHub also issues a client ID and now recommends it as the JWT `iss`; the App ID continues to work).
6. Generate a private key; store at `~/.config/acme-agent/key.pem`, `chmod 600`.
   Hardening option: store the PEM in the login keychain (`security add-generic-password`, base64-wrapped).
   This only works if you also change `bot-token` to read the key from the keychain instead of `KEY.read_text()` — deleting `key.pem` while the script still reads from disk breaks token minting.
   Either rewrite the read or keep the file; don't delete it on the strength of the keychain copy alone.

## Phase 2 — Install the App

1. App settings → Install App → choose the org.
   Installation needs an org owner — the App manager role can register Apps but not install them.
   An org member who is admin of the target repos can install an App that requests no organization permissions (this App requests none); otherwise it files an installation request for an owner to approve.
2. Choose **"Only select repositories"** and pick the target repos.
   This list is the real blast-radius limit; enrolling a repo in the program means adding it here.
3. Note the **Installation ID** from the post-install URL (`.../settings/installations/<id>`), via `gh api orgs/{org}/installations` with an org-admin user token, or via app JWT (`gh api /app/installations` — a normal user token will not work on `/app/*` endpoints).
4. Get the bot's user ID for commit attribution: `gh api 'users/acme-agent%5Bbot%5D' --jq .id`.
   The bot's commit email is `<BOT_UID>+acme-agent[bot]@users.noreply.github.com`; using it makes commits render with the bot's avatar.

## Phase 3 — Helper scripts

All three live in `~/.claude/bot-shims/`, all `chmod +x`.
Only `session-env.sh` is Claude Code-specific; `bot-token` and `git-credential-bot` are harness-neutral, and the directory is a convention, not a dependency — a neutral location such as `~/.config/acme-agent/bin/` works identically if the paths below are adjusted to match.

### `bot-token` — mints and caches installation tokens

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyjwt[crypto]", "httpx"]
# ///
import datetime, json, os, sys, tempfile, time
from pathlib import Path
import httpx, jwt

APP_ID = "REPLACE"
INSTALL_ID = "REPLACE"
KEY = Path.home() / ".config/acme-agent/key.pem"
CACHE = Path.home() / ".config/acme-agent/token.json"

if CACHE.exists():
    try:
        c = json.loads(CACHE.read_text())
        if c["exp"] - time.time() > 300:
            print(c["token"]); sys.exit()
    except (ValueError, KeyError, TypeError, OSError):
        pass  # partial/corrupt cache (e.g. an interrupted write) — treat as a miss and re-mint

now = int(time.time())
app_jwt = jwt.encode({"iat": now - 60, "exp": now + 540, "iss": APP_ID}, KEY.read_text(), algorithm="RS256")
r = httpx.post(
    f"https://api.github.com/app/installations/{INSTALL_ID}/access_tokens",
    headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"},
    timeout=10,
)
r.raise_for_status()
data = r.json()
exp = datetime.datetime.fromisoformat(data["expires_at"]).timestamp()  # fromisoformat parses the trailing Z on >=3.11
# Phase 1 already created this dir for key.pem; ensure it so the script is self-contained.
CACHE.parent.mkdir(parents=True, exist_ok=True)
# mkstemp = exclusive-create, 0600, random name; os.replace() swaps it in atomically — never truncate the live cache.
fd, tmp = tempfile.mkstemp(dir=CACHE.parent, suffix=".tmp")
with os.fdopen(fd, "w") as f:
    json.dump({"token": data["token"], "exp": exp}, f)
os.replace(tmp, CACHE)
print(data["token"])
```

Details that are easy to get wrong: parse the token expiry from the response's `expires_at` rather than assuming one hour; write the cache through an exclusively-created `0600` temp file (`mkstemp`) swapped in with `os.replace()` rather than truncating in place (a truncated write risks a partial file, so the read treats any parse error as a cache miss and re-mints; a predictable, non-exclusive temp name could inherit a pre-existing file's broader permissions); and set a request timeout, since a hung mint hangs every git push and gh call that waits on it.
The `uv run` shebang requires `uv` on PATH where the script is invoked; use an absolute path to `uv` if that is not guaranteed.
On a cache hit this runs in well under 100 ms, cheap enough to call before every Bash command (Phase 4).
Optional hardening: pass a `"repositories"` field in the token request to scope each token to the repo being worked, at the cost of the shared cache.

### `git-credential-bot` — git credential helper

```bash
#!/usr/bin/env bash
set -euo pipefail
[[ "${1:-}" == get ]] || exit 0
token="$("$HOME/.claude/bot-shims/bot-token")"  # set -e aborts here if the mint fails — nothing is printed
echo username=x-access-token
echo "password=$token"
```

This must fail closed: `set -e` plus capturing the token before printing means a failed mint aborts with no output, rather than emitting an empty `password=`.
A blank password would either attempt auth that fails confusingly or fall through to the personal keychain — the human-as-agent failure this setup prevents.

### `session-env.sh` — SessionStart hook that injects `GH_TOKEN`

```bash
#!/usr/bin/env bash
# SessionStart hook. Claude Code provides $CLAUDE_ENV_FILE and sources it before
# every Bash command, so writing the GH_TOKEN mint here makes `gh` authenticate as
# the bot with no PATH shim and no shell-dotfile edits. The command substitution
# stays UNEVALUATED in the file so it re-runs per command (bot-token caches, <100ms
# on a hit), keeping the 1h installation token fresh across long sessions.
set -euo pipefail
[ -n "${CLAUDE_ENV_FILE:-}" ] || exit 0
line='export GH_TOKEN="$($HOME/.claude/bot-shims/bot-token || echo BOT-TOKEN-MINT-FAILED)"'
grep -qxF -- "$line" "$CLAUDE_ENV_FILE" 2>/dev/null || printf '%s\n' "$line" >> "$CLAUDE_ENV_FILE"
```

The single-quoted `line` keeps both `$HOME` and the `$(...)` substitution unevaluated in the env file, so the token is minted *each* time Claude sources the file — i.e. before every Bash command — not frozen once at session start (and the line stays portable instead of baking in an absolute path).
`set -euo pipefail` (and no unconditional `exit 0`) makes a failed write loud: an unwritable env file fails the hook, which Claude Code surfaces, instead of silently leaving `GH_TOKEN` unset — which would fall back to the personal stored credentials; Phase 5's `ghs_` check catches the same condition.
The `|| echo` fallback makes this path fail closed, matching `git-credential-bot`: a failed mint substitutes a non-empty invalid token, so `gh` fails with an auth error instead of silently using the human account — an *empty* `GH_TOKEN` is treated by `gh` as unset, and that fallback to the personal stored credentials is exactly this skill's headline failure mode.
The `>>` append (not `>`) keeps the line from clobbering anything another hook wrote to `$CLAUDE_ENV_FILE`, and the `grep -qxF` guard makes re-runs idempotent — SessionStart fires on resume and clear as well as startup, and without the guard each duplicated line would mint a token (subprocess, ~100 ms on a cache hit) per Bash command.

## Phase 4 — Project-scoped configuration

Create `.claude/settings.local.json` in each target repo; it affects only the agent's sessions in that project, and no shell dotfile is touched.
Claude Code auto-gitignores this file only when it creates it itself — if you create it by hand, gitignore it yourself so the bot config never lands in the repo.
Replace `<BOT_UID>` with the user ID from Phase 2, `acme` with your org, and `<you>` in the hook command with your username — keep it an absolute path.

```json
{
  "env": {
    "GIT_AUTHOR_NAME": "acme-agent[bot]",
    "GIT_AUTHOR_EMAIL": "<BOT_UID>+acme-agent[bot]@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "acme-agent[bot]",
    "GIT_COMMITTER_EMAIL": "<BOT_UID>+acme-agent[bot]@users.noreply.github.com",
    "GIT_CONFIG_COUNT": "4",
    "GIT_CONFIG_KEY_0": "credential.helper",
    "GIT_CONFIG_VALUE_0": "",
    "GIT_CONFIG_KEY_1": "credential.helper",
    "GIT_CONFIG_VALUE_1": "!$HOME/.claude/bot-shims/git-credential-bot",
    "GIT_CONFIG_KEY_2": "url.https://github.com/acme/.insteadOf",
    "GIT_CONFIG_VALUE_2": "git@github.com:acme/",
    "GIT_CONFIG_KEY_3": "commit.gpgsign",
    "GIT_CONFIG_VALUE_3": "false"
  },
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "/Users/<you>/.claude/bot-shims/session-env.sh" } ] }
    ]
  }
}
```

What each part does:

- `GIT_AUTHOR_*` / `GIT_COMMITTER_*` override global `user.*` so commits attribute to the bot.
- The empty `credential.helper` resets the inherited helper list (osxkeychain, gh helpers); the next entry installs the bot helper as the only one.
- `insteadOf` rewrites SSH remotes to HTTPS inside agent sessions only, so pushes use the bot token instead of the personal SSH key; scoping it to the org prefix leaves other remotes alone.
  The colon form covers `git@github.com:acme/` remotes; if any remote uses the `ssh://git@github.com/acme/` form, add a second `insteadOf` pair and bump the count.
- `commit.gpgsign false` prevents bot-authored commits being signed with the personal GPG key — a signature from the human on a bot-authored commit is an attribution mismatch.
- The `SessionStart` hook injects `GH_TOKEN` for `gh` (Phase 3's `session-env.sh`). The first time it runs, Claude Code prompts to approve the hook; approve it.

These env keys are static, so they live in `settings.local.json`. `GH_TOKEN` is dynamic (1h expiry), so it cannot be a static value here — that is why it goes through the hook + `$CLAUDE_ENV_FILE` instead.

**Why a hook and not a PATH-shimmed `gh`.**
The obvious approach — drop a `gh` wrapper on `PATH` via a shell rc file — fails under Claude Code and wastes hours.
Claude Code builds a *shell snapshot* at session start by sourcing `$HOME/.zshrc` from a **non-login** shell, then **freezes `PATH`** into that snapshot and replays it for every Bash command.
Consequences that defeat the rc-file approach: `.zprofile` is never sourced (non-login); `ZDOTDIR` is ignored (it hardcodes `$HOME/.zshrc`, not `$ZDOTDIR/.zshrc`); and even a correctly-placed `PATH` prepend is frozen at snapshot time, before the per-project `env` (and any marker it sets) is applied.
`CLAUDE_ENV_FILE` is the supported escape hatch: Claude Code provides it to `SessionStart`/`CwdChanged`/`Setup`/`FileChanged` hooks and sources the file's contents before every Bash command, *after* the snapshot — so an `export GH_TOKEN=...` there reliably reaches `gh`.
**Adapter contract for other harnesses.**
Phases 1–3's App, token, and credential-helper layers are harness-neutral (only `session-env.sh` is Claude Code glue); what an adapter for another local agent (e.g. Codex) must supply is this phase's routing, without editing shell dotfiles: per-project activation, the static git identity env, command-scope `GIT_CONFIG_*`, a dynamic `GH_TOKEN` re-minted across hour-plus sessions, and a fail-closed substitute when minting fails.
This skill ships only the Claude Code adapter; if a harness lacks one of these capabilities, treat its support as pending rather than approximating with the steps above — a half-wired adapter fails open to the personal identity.
Only fall back to a PATH shim if the harness sources a predictable rc file without freezing `PATH`.

## Phase 5 — Verify both directions

In a fresh agent session in an opted-in repo (the hook approval prompt appears on first run):

- `echo "${GH_TOKEN:0:4}"` → `ghs_`, proving the SessionStart hook injected the installation token via `$CLAUDE_ENV_FILE`.
- `gh api installation/repositories --jq '.total_count'` → the count of enrolled repos, proving `gh` acts as the bot. Use this, not `gh api user` — an installation token has no user and 403s on `/user`.
- `git config --show-scope credential.helper` → bot helper at `command` scope (proves env-scoped, no file changed).
- `GIT_SSH_COMMAND=/usr/bin/false git ls-remote origin` → succeeds, proving the HTTPS-rewrite-plus-token path is in use (SSH is disabled for that invocation).
- Test commit → author `acme-agent[bot]`, unsigned (`git log -1 --format='%an <%ae> %G?'`).
  Once pushed, the commit shows no Verified badge — expected, because local commits pushed with an App token are never auto-verified; only commits created through the App's API path (e.g. GraphQL `createCommitOnBranch`) get the badge.
- Branch push + `gh pr create` → PR and commits authored by the bot on GitHub.
- `gh pr checks` → returns status (proves Checks and Actions read).
- Negative: `git ls-remote https://github.com/acme/<private-non-enrolled-repo>.git` → fails, proving the installation boundary.
  The probe repo must be private — public repos are readable over unauthenticated HTTPS, so a success there proves nothing.

In a personal terminal (and any agent session outside the opted-in repos):

- `git config credential.helper` → still osxkeychain; `git config commit.gpgsign` → still true.
- `gh auth status` → personal account; commits signed and authored as the human; SSH push works.
- Because no shell dotfile was modified, personal shells are unaffected by construction — there is nothing project-specific on `PATH` or in the rc files to leak.

## Phase 6 — Audit repo-side guardrails

Identity is Step 1 of the agent-friendly-github setup workflow; enforcement lives in each repo's ruleset, not in the App.
For every repo the App is installed on, walk that skill's checklist §2; the items this setup specifically depends on:

- Required approving reviews ≥ 1 with self-approval not counted.
- `dismiss_stale_reviews_on_push` enabled.
- Force-push and branch deletion blocked; required status checks strict.
- Bypass-actors list contains no automation identity — including this App and any other bot App already installed (verify; never assume an existing bot's posture is clean).
- No `required_signatures` rule, or a dedicated bot signing key is provisioned first — `gpgsign false` plus an App-token push means every bot commit is unsigned, and a `required_signatures` ruleset rejects the push outright.

Run the audit from a personal terminal — never through the bot token, and note that some checks (Actions settings, secret scanning) need admin access — and file gaps with the repo's admins rather than working around them.

## What This Enforces — and What It Does Not

Enforced, server-side:

- The installation token authenticates only to enrolled repos, only with the granted scopes, and expires in one hour; public repos stay world-readable regardless, so the boundary governs authenticated and write access.
- No Workflows permission means GitHub rejects bot pushes that add or modify files under `.github/workflows/`; CI logic living elsewhere — scripts the workflows invoke, composite actions, Makefiles — is still reachable with Contents write, which is part of why the human review gate matters.
- Everything done through the bot path is attributable and filterable in the audit log.

Not enforced — the part everyone overstates:

- The agent runs as the human's OS user: it can read `key.pem`, run `bot-token` directly, call the real `gh` by full path, read `~/.ssh`, or edit the shims and `settings.local.json` themselves.
- It therefore holds **both identities**, which enables approval laundering: author a PR as the bot, approve it as the human from a non-opted-in session.
  GitHub's block on author self-approval does not close this.
- A required-review rule binds the **bot token**, not the agent; treat it as enforcement against the bot identity and a convention for the agent.
- Procedural mitigation: never approve a bot-authored PR from inside an agent session; approvals happen in the GitHub UI or a personal terminal, after reading the diff.
- If containment is actually required, change the architecture (separate OS user, container, or VM), not the config.

## Common Mistakes

| Mistake | Reality |
| --- | --- |
| Activating `gh` via a PATH shim in shell dotfiles | Claude Code freezes PATH into a snapshot built from a non-login `$HOME/.zshrc` (ignores `.zprofile` and `ZDOTDIR`); inject `GH_TOKEN` via a SessionStart hook writing `$CLAUDE_ENV_FILE` instead |
| Putting `GH_TOKEN` directly in `settings.local.json` `env` | It is a static field; the token expires hourly — mint it per command via the hook + `$CLAUDE_ENV_FILE` |
| Letting a failed mint leave `GH_TOKEN` empty | `gh` treats empty as unset and silently falls back to the personal stored credentials; substitute a non-empty invalid token so the failure surfaces as an auth error |
| Probing identity with `gh api user` | Installation tokens have no user and 403 there; use `gh api installation/repositories` |
| Granting Checks read without Actions read | Under an App token `gh pr checks` needs both — the status rollup traverses each check suite's workflow run |
| Granting Workflows: write "to be safe" | Hands a prompt-injected agent the ability to rewrite CI |
| Write token cache, then chmod | umask window exposes the token; create `0600` atomically |
| Assuming one-hour token life | Parse `expires_at` from the response |
| Treating `settings.local.json` scoping as a security boundary | It is routing for the well-behaved path; the App installation list is the boundary |
| Leaving the personal GPG key signing bot commits | Attribution mismatch — human signature on bot-authored work; set `commit.gpgsign false` |
| Expecting the Verified badge on bot commits | Local commits pushed with an App token are not auto-verified; only API-path commits (e.g. GraphQL `createCommitOnBranch`) get the badge |
| Calling the review gate "enforced against the agent" | The agent holds both identities; the gate binds the bot token (see approval laundering above) |

## Done Criteria

- Phase 5 verification passes in both directions, including the negative tests.
- Phase 6 audit recorded for every installed repo, with gaps filed rather than bypassed.
- Any document describing the setup states the attribution-not-containment boundary explicitly.
