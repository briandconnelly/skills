---
name: agent-bot-identity
description: Use when giving a local coding agent (e.g. Claude Code) a distinct GitHub App bot identity — commits, pushes, and PRs attribute to the bot while manual git operations on the same machine keep the personal account untouched — or when auditing such a dual-identity setup. Covers App registration and scopes, installation tokens, per-project env isolation, shell activation, verification, and what the isolation does and does not enforce.
---

# Agent Bot Identity

## Overview

Give a local coding agent its own GitHub App identity so every commit, push, and PR it makes attributes to a bot, while the human's git setup (SSH key, GPG signing, keychain credentials) stays untouched on the same machine.
The isolation mechanism is environment variables that exist only inside the agent's shell sessions, scoped per-project.

Core principle: **this buys attribution, not containment.**
The env scoping makes the well-behaved default path use the bot identity; the only hard boundaries are the App's installation list and the server-side rulesets of the repos it touches.
Never present this setup as a sandbox.

## When to Use

- Setting up Claude Code (or a similar local agent) to commit, push, and open PRs as a bot on a developer machine, with personal git operations unchanged.
- Auditing an existing dual-identity setup for over-trust — e.g. a review gate assumed to bind the agent, or local scoping treated as a security boundary.
- Symptoms: agent commits show the human as author; "have the agent open PRs as a bot"; bot PRs need human approval but the agent runs on the human's laptop.

## When Not to Use

- Repo-side configuration — rulesets, CODEOWNERS, required checks, Actions hardening — is the agent-friendly-github skill; this skill is the local-machine implementation of its §4 identity step, and Phase 7 here hands back to that skill's checklist.
- CI or hosted runners: mint the App token directly in the workflow (e.g. `actions/create-github-app-token`); there is no personal identity to isolate from.
- Hard security isolation: run the agent as a separate OS user, container, or VM; this skill does not provide that.

## Design at a Glance

| Layer | Mechanism | What it buys |
| --- | --- | --- |
| Identity | Org-owned GitHub App, webhook disabled | True `[bot]` attribution, fine-grained scopes, short-lived tokens, audit trail |
| Blast radius | App installed on "Only select repositories" | Token cannot touch non-enrolled repos, even if the env leaks |
| Local routing | Per-project env vars (`.claude/settings.local.json`) | Bot identity activates only in opted-in repos; personal config files never change |
| Credentials | `insteadOf` SSH→HTTPS rewrite + custom credential helper + `gh` shim | Agent pushes/API calls use the installation token, not the personal SSH key or keychain |
| Enforcement | Repo rulesets (Phase 7) | The only controls that bind a misbehaving agent |

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
   Hardening option: store the PEM in the login keychain (`security add-generic-password`, base64-wrapped) and delete the file, accepting the extra moving parts.

## Phase 2 — Install the App

1. App settings → Install App → choose the org.
   Installation itself needs an org owner — the App manager role can register Apps but not install them; non-owners file an installation request for an owner to approve.
2. Choose **"Only select repositories"** and pick the target repos.
   This list is the real blast-radius limit; enrolling a repo in the program means adding it here.
3. Note the **Installation ID** from the post-install URL (`.../settings/installations/<id>`), via `gh api orgs/{org}/installations` with an org-admin user token, or via app JWT (`gh api /app/installations` — a normal user token will not work on `/app/*` endpoints).
4. Get the bot's user ID for commit attribution: `gh api 'users/acme-agent%5Bbot%5D' --jq .id`.
   The bot's commit email is `<BOT_UID>+acme-agent[bot]@users.noreply.github.com`; using it makes commits render with the bot's avatar.

## Phase 3 — Helper scripts

All three live in `~/.claude/bot-shims/`, all `chmod +x`.

### `bot-token` — mints and caches installation tokens

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyjwt[crypto]", "httpx"]
# ///
import datetime, json, os, sys, time
from pathlib import Path
import httpx, jwt

APP_ID = "REPLACE"
INSTALL_ID = "REPLACE"
KEY = Path.home() / ".config/acme-agent/key.pem"
CACHE = Path.home() / ".config/acme-agent/token.json"

if CACHE.exists():
    c = json.loads(CACHE.read_text())
    if c["exp"] - time.time() > 300:
        print(c["token"]); sys.exit()

now = int(time.time())
app_jwt = jwt.encode({"iat": now - 60, "exp": now + 540, "iss": APP_ID}, KEY.read_text(), algorithm="RS256")
r = httpx.post(
    f"https://api.github.com/app/installations/{INSTALL_ID}/access_tokens",
    headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"},
    timeout=10,
)
r.raise_for_status()
data = r.json()
exp = datetime.datetime.fromisoformat(data["expires_at"]).timestamp()
# Create with 0600 from the start; write-then-chmod leaves a umask window.
fd = os.open(CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    json.dump({"token": data["token"], "exp": exp}, f)
print(data["token"])
```

Two details that are easy to get wrong: parse the token expiry from the response's `expires_at` rather than assuming one hour, and create the cache file with `0600` atomically rather than writing then chmodding.
The request timeout matters too — a hung token mint hangs every `git push` that goes through the credential helper.
The `uv run` shebang requires `uv` on PATH in non-interactive contexts (credential-helper invocations); use an absolute path to `uv` if needed.
Optional hardening: pass a `"repositories"` field in the token request to scope each token to the repo being worked, at the cost of the shared cache.

### `git-credential-bot` — git credential helper

```bash
#!/usr/bin/env bash
[[ $1 == get ]] || exit 0
echo username=x-access-token
echo "password=$("$HOME/.claude/bot-shims/bot-token")"
```

### `gh` — shim so the gh CLI uses the bot token

```bash
#!/usr/bin/env bash
set -euo pipefail
token="$("$HOME/.claude/bot-shims/bot-token")"
GH_TOKEN="$token" exec /opt/homebrew/bin/gh "$@"
```

Hardcode the real gh path (`/usr/local/bin/gh` on Intel Homebrew) so the shim cannot recurse into itself.
The shim must fail closed: `set -e` aborts when the token mint fails, because an empty `GH_TOKEN` would silently fall back to the personal keychain auth — the agent acting as the human is the exact failure this setup exists to prevent.

## Phase 4 — Project-scoped environment

Create `.claude/settings.local.json` in each target repo; it affects only local agent sessions in that project.
Claude Code auto-gitignores this file only when it creates it itself — if you create it by hand, gitignore it yourself so the bot config never lands in the repo.
Replace `<BOT_UID>` with the user ID from Phase 2.

```json
{
  "env": {
    "CLAUDE_BOT_IDENTITY": "1",
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
  }
}
```

What each entry does:

- `GIT_AUTHOR_*` / `GIT_COMMITTER_*` override global `user.*` so commits attribute to the bot.
- The empty `credential.helper` resets the inherited helper list (osxkeychain, gh helpers); the next entry installs the bot helper as the only one.
- `insteadOf` rewrites SSH remotes to HTTPS inside agent sessions only, so pushes use the bot token instead of the personal SSH key; scoping it to the org prefix leaves other remotes alone.
  The colon form covers `git@github.com:acme/` remotes; if any remote uses the `ssh://git@github.com/acme/` form, add a second `insteadOf` pair and bump the count.
- `commit.gpgsign false` prevents bot-authored commits being signed with the personal GPG key — a signature from the human on a bot-authored commit is an attribution mismatch.

## Phase 5 — Shell activation for the gh shim

Add to `~/.zshenv` — **not** `~/.zshrc` or `~/.zprofile`:

```zsh
[[ -n $CLAUDE_BOT_IDENTITY ]] && path=($HOME/.claude/bot-shims $path)
```

Agent shell sessions are typically non-interactive and non-login; non-interactive zsh sources only `~/.zshenv`, so a guard in `.zshrc` (interactive) or `.zprofile` (login) silently never fires.
Harness shell behavior varies by version, so treat the `which gh` canary as authoritative rather than the file placement.
Keyed on the settings env var, the shim activates only in agent sessions in opted-in projects; personal terminals get the normal `gh`.
`which gh` inside an agent session is the canary: the Homebrew path means the guard is not being sourced.

## Phase 6 — Verify both directions

In a fresh agent session in an opted-in repo:

- `git config --show-scope credential.helper` → bot helper at `command` scope (proves env-scoped, no file changed).
- `which gh` → the shim path.
- `GIT_SSH_COMMAND=/usr/bin/false git ls-remote origin` → succeeds, proving the HTTPS-rewrite-plus-token path is in use (SSH is disabled for that invocation).
- Test commit → author `acme-agent[bot]`, unsigned (`git log -1 --format='%an <%ae> %G?'`).
  Once pushed, the commit shows no Verified badge — expected, because local commits pushed with an App token are never auto-verified; only commits created through the App's API path (e.g. GraphQL `createCommitOnBranch`) get the badge.
- Branch push + `gh pr create` → PR and commits authored by the bot on GitHub.
- `gh pr checks` → returns status (proves Checks and Actions read).
- Negative: `git ls-remote https://github.com/acme/<private-non-enrolled-repo>.git` → fails, proving the installation boundary.
  The probe repo must be private — public repos are readable over unauthenticated HTTPS, so a success there proves nothing.

In a personal terminal in the same repo:

- `git config credential.helper` → still osxkeychain; `git config commit.gpgsign` → still true.
- `which gh` → Homebrew path; `gh auth status` → personal account.
- Commits signed and authored as the human; SSH push works.

## Phase 7 — Audit repo-side guardrails

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

- The agent runs as the human's OS user: it can read `key.pem`, run `bot-token` directly, call the real `gh` by full path, read `~/.ssh`, unset the injected env vars, or simply edit `~/.zshenv` and the shims themselves.
- It therefore holds **both identities**, which enables approval laundering: author a PR as the bot, approve it as the human from a non-opted-in session.
  GitHub's block on author self-approval does not close this.
- A required-review rule binds the **bot token**, not the agent; treat it as enforcement against the bot identity and a convention for the agent.
- Procedural mitigation: never approve a bot-authored PR from inside an agent session; approvals happen in the GitHub UI or a personal terminal, after reading the diff.
- If containment is actually required, change the architecture (separate OS user, container, or VM), not the env vars.

## Common Mistakes

| Mistake | Reality |
| --- | --- |
| PATH guard in `~/.zshrc` or `~/.zprofile` | Non-interactive shells never source them; use `~/.zshenv`; `which gh` is the canary |
| Granting Checks read without Actions read | Under an App token `gh pr checks` needs both — the status rollup traverses each check suite's workflow run |
| Granting Workflows: write "to be safe" | Hands a prompt-injected agent the ability to rewrite CI |
| Write token cache, then chmod | umask window exposes the token; create `0600` atomically |
| Assuming one-hour token life | Parse `expires_at` from the response |
| Treating `settings.local.json` scoping as a security boundary | It is routing for the well-behaved path; the App installation list is the boundary |
| Leaving the personal GPG key signing bot commits | Attribution mismatch — human signature on bot-authored work; set `commit.gpgsign false` |
| Expecting the Verified badge on bot commits | Local commits pushed with an App token are not auto-verified; only API-path commits (e.g. GraphQL `createCommitOnBranch`) get the badge |
| Calling the review gate "enforced against the agent" | The agent holds both identities; the gate binds the bot token (see approval laundering above) |

## Done Criteria

- Phase 6 verification passes in both directions, including the negative tests.
- Phase 7 audit recorded for every installed repo, with gaps filed rather than bypassed.
- Any document describing the setup states the attribution-not-containment boundary explicitly.
