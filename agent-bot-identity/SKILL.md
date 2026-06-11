---
name: agent-bot-identity
description: Use when giving a local coding agent a distinct GitHub App bot identity — the agent's commits, pushes, and PRs attribute to the bot by default while manual git operations on the same machine keep the personal account untouched — when splitting attribution in a repo where the human and agent both contribute (collaborated work authored as the human, autonomous work as the bot), or when auditing such a dual-identity setup. Covers App registration and scopes, installation tokens, credential injection per project or user-wide (automatic across all org repos via a per-command guard), per-task personal authorship, verification, and what the isolation does and does not enforce. The App/token/credential-helper core is harness-neutral; the worked per-project wiring is a Claude Code adapter, with an explicit contract for what any other harness's adapter must provide.
---

# Agent Bot Identity

## Overview

Give a local coding agent its own GitHub App identity so the commits, pushes, and PRs it makes attribute to a bot by default, while the human's git setup (SSH key, GPG signing, keychain credentials) stays untouched on the same machine.
Attribution is per unit of work: autonomous agent work carries the bot identity, and in repos where the human also contributes through the agent, collaborated commits can carry the human's authorship via the `as-me` wrapper (Phase 3) while auth still rides the bot token.
The isolation mechanism is per-project configuration that injects the bot's credentials only into the agent's sessions in opted-in repos — without editing any shell dotfiles.

Core principle: **this buys attribution, not containment.**
The per-project scoping makes the well-behaved default path use the bot identity; the only hard boundaries are the App's installation list and the server-side rulesets of the repos it touches.
Never present this setup as a sandbox.

## When to Use

- Setting up Claude Code (or a similar local agent) to commit, push, and open PRs as a bot on a developer machine, with personal git operations unchanged.
- Splitting attribution in a repo where you contribute both directly and via the agent — collaborated work authored as you, autonomous work as the bot, without separate checkouts or settings toggles.
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
| Local routing | Env/hook adapter — the contract is "inject the git env and a dynamic `GH_TOKEN` only in enrolled repos, no shell-dotfile edits"; Claude Code adapters: per-project `.claude/settings.local.json` (Variant A) or a user-level per-command guard gated on the org remote (Variant B) | Bot identity activates only in enrolled repos; no shell dotfiles change |
| git auth | `insteadOf` SSH→HTTPS rewrite + git credential helper (`GIT_CONFIG_*`) | Pushes use the installation token, not the personal SSH key or keychain |
| gh auth | `GH_TOKEN` written to `$CLAUDE_ENV_FILE` by a SessionStart hook | `gh` calls use the installation token; sourced before every Bash command |
| Collaborated work | `as-me` wrapper unsets the author/committer env per command | Human authorship on collaborated commits; pushes and PRs still ride the bot token |
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

All four live in `~/.claude/bot-shims/`, all `chmod +x`.
Only `session-env.sh` is Claude Code-specific; `bot-token`, `git-credential-bot`, and `as-me` are harness-neutral, and the directory is a convention, not a dependency — a neutral location such as `~/.config/acme-agent/bin/` works identically if the paths below are adjusted to match.
Phase 4's Variant B replaces `session-env.sh` with two further scripts (`bot-env-hook.sh` and `bot-env`), shown there.

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
if [ -z "${CLAUDE_ENV_FILE:-}" ]; then
  echo "session-env.sh: CLAUDE_ENV_FILE not provided — GH_TOKEN not injected; gh would fall back to personal auth" >&2
  exit 1
fi
line='export GH_TOKEN="$($HOME/.claude/bot-shims/bot-token || echo BOT-TOKEN-MINT-FAILED)"'
grep -qxF -- "$line" "$CLAUDE_ENV_FILE" 2>/dev/null || printf '%s\n' "$line" >> "$CLAUDE_ENV_FILE"
```

The single-quoted `line` keeps both `$HOME` and the `$(...)` substitution unevaluated in the env file, so the token is minted *each* time Claude sources the file — i.e. before every Bash command — not frozen once at session start (and the line stays portable instead of baking in an absolute path).
`set -euo pipefail` (and no silent exit path) makes every failure loud: an unwritable env file fails the hook, and a missing `CLAUDE_ENV_FILE` — an unsupported hook event or a harness that does not provide it — exits 1 with a message instead of quietly skipping injection.
Either way Claude Code surfaces the hook failure rather than silently leaving `GH_TOKEN` unset — which would fall back to the personal stored credentials; Phase 5's `ghs_` check catches the same condition.
The `|| echo` fallback makes this path fail closed, matching `git-credential-bot`: a failed mint substitutes a non-empty invalid token, so `gh` fails with an auth error instead of silently using the human account — an *empty* `GH_TOKEN` is treated by `gh` as unset, and that fallback to the personal stored credentials is exactly this skill's headline failure mode.
The `>>` append (not `>`) keeps the line from clobbering anything another hook wrote to `$CLAUDE_ENV_FILE`, and the `grep -qxF` guard makes re-runs idempotent — SessionStart fires on resume and clear as well as startup, and without the guard each duplicated line would mint a token (subprocess, ~100 ms on a cache hit) per Bash command.

### `as-me` — personal authorship for collaborated work

```bash
#!/usr/bin/env bash
# as-me — run a command with personal commit authorship (auth stays the bot token)
exec env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL "$@"
```

Unsetting the four identity variables lets git fall back to the global `user.*` config, so nothing personal is hardcoded in the shim.
Everything else in the bot env stays active — credential helper, `insteadOf` rewrite, `gpgsign false`, `GH_TOKEN` — so `as-me git commit -m "..."` authors the commit as the human while pushes and `gh` calls still ride the bot token.
These commits are unsigned (`gpgsign false` stays in effect) and show no Verified badge once pushed (App-token pushes are never auto-verified) — the two visible differences from terminal-made personal commits; amend from a personal terminal if a signature matters.
Forgot the wrapper and committed as the bot? `as-me git commit --amend --reset-author` fixes the last commit.
When to use it is a policy question, not a mechanism question — see Mixed Contribution below.

## Phase 4 — Local routing: choose a variant

Two Claude Code adapters satisfy the routing contract; pick one, never both (two sources of truth drift).

- **Variant A — per-project opt-in**: a hand-created `.claude/settings.local.json` in each enrolled repo.
  Choose it when enrollment should be an explicit, visible, per-repo act — e.g. the agent also works in org repos that are deliberately not enrolled.
- **Variant B — user-level, automatic in org repos**: one user-level hook installs a per-command guard that activates the bot in any repo whose remotes match the org.
  Choose it to eliminate the per-repo step entirely — Variant A's failure mode is forgetting the file in an enrolled repo, which silently attributes agent work to the human (the headline failure); Variant B inverts that to a loud push failure in repos not yet on the installation list.

### Variant A — per-project opt-in

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

### Variant B — user-level guard, automatic in org repos

One mechanism fact makes this variant work, verified on Claude Code 2.1.172 (probe: an env file exporting `"$PWD"` matched each command's own `pwd`): **the contents of `$CLAUDE_ENV_FILE` are evaluated before every Bash command, in that command's shell and working directory** — not once at session start.
So instead of static per-repo env, a user-level SessionStart hook installs a single *unevaluated* guard line, and the guard re-decides bot-vs-personal per command from the directory the command actually runs in.
Mid-session directory changes flip identity on the next command; there is no session-level verdict to go stale, and no `CwdChanged` plumbing is needed.

Do **not** centralize by moving the Variant A `env` block into user-level `~/.claude/settings.json`: settings `env` values are static strings and cannot be conditional, so the bot identity would activate in every project — other orgs, OSS, personal repos — which is exactly the ungated-global antipattern.

Register the hook in `~/.claude/settings.json` (applies to all projects; replace `<you>`, keep the path absolute):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "/Users/<you>/.claude/bot-shims/bot-env-hook.sh" } ] }
    ]
  }
}
```

`bot-env-hook.sh` — installs the guard line, fail-closed:

```bash
#!/usr/bin/env bash
# SessionStart hook (user-level): install the per-command identity guard into
# $CLAUDE_ENV_FILE. The guard line stays UNEVALUATED in the file, so bot-env
# re-decides bot-vs-personal before every Bash command, in that command's
# shell and working directory — no session-level verdict to go stale.
set -euo pipefail
if [ -z "${CLAUDE_ENV_FILE:-}" ]; then
  echo "bot-env-hook.sh: CLAUDE_ENV_FILE not provided — identity guard not installed; sessions would run with personal credentials" >&2
  exit 1
fi
if [ ! -x "$HOME/.claude/bot-shims/bot-env" ]; then
  echo "bot-env-hook.sh: bot-env missing or not executable — refusing to install a guard that would fail open" >&2
  exit 1
fi
line='__bot_env="$("$HOME/.claude/bot-shims/bot-env")" || { echo "bot-env failed — refusing to run with undetermined identity" >&2; exit 1; }; eval "$__bot_env"; unset __bot_env'
grep -qxF -- "$line" "$CLAUDE_ENV_FILE" 2>/dev/null || printf '%s\n' "$line" >> "$CLAUDE_ENV_FILE"
```

The capture-then-eval shape of the guard line is load-bearing: a bare `eval "$(bot-env)"` fails **open** — a crashed or missing script substitutes the empty string, the eval succeeds, and the session silently runs personal in an enrolled repo, the headline failure mode.
Capturing the output lets a script failure abort the command (`exit 1` in the preamble) loudly instead.
The `grep -qxF` guard keeps re-fires idempotent (SessionStart fires on resume and clear too), and `>>` preserves other hooks' lines, both as in `session-env.sh` — which this variant replaces; do not also run the per-repo hook.

`bot-env` — the per-command decision, also in `~/.claude/bot-shims/`, `chmod +x`:

```bash
#!/usr/bin/env bash
# bot-env — decide bot vs personal for the current directory and print exports
# for the guard line to eval. Personal verdict prints nothing. Runs before
# every Bash command: stay fast and deterministic — no network calls here.
set -euo pipefail
ORG="acme"
BOT_NAME="${ORG}-agent[bot]"
BOT_EMAIL="<BOT_UID>+${ORG}-agent[bot]@users.noreply.github.com"

verdict=personal
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if remotes="$(git remote -v 2>/dev/null)"; then
    if printf '%s' "$remotes" | grep -Eq "github\.com[:/]${ORG}/"; then
      verdict=bot
    elif [ -z "$remotes" ]; then
      verdict=bot
      echo "bot-env: no remotes in $PWD — ambiguous, using the bot identity" >&2
    fi
  else
    verdict=bot
    echo "bot-env: git remote query failed in $PWD — using the bot identity" >&2
  fi
fi
[ "$verdict" = bot ] || exit 0

token="$("$HOME/.claude/bot-shims/bot-token")" || token="BOT-TOKEN-MINT-FAILED"

cat <<EOF
export GIT_AUTHOR_NAME='${BOT_NAME}'
export GIT_AUTHOR_EMAIL='${BOT_EMAIL}'
export GIT_COMMITTER_NAME='${BOT_NAME}'
export GIT_COMMITTER_EMAIL='${BOT_EMAIL}'
export GIT_CONFIG_COUNT=4
export GIT_CONFIG_KEY_0='credential.helper'
export GIT_CONFIG_VALUE_0=''
export GIT_CONFIG_KEY_1='credential.helper'
export GIT_CONFIG_VALUE_1='!${HOME}/.claude/bot-shims/git-credential-bot'
export GIT_CONFIG_KEY_2='url.https://github.com/${ORG}/.insteadOf'
export GIT_CONFIG_VALUE_2='git@github.com:${ORG}/'
export GIT_CONFIG_KEY_3='commit.gpgsign'
export GIT_CONFIG_VALUE_3='false'
export GH_TOKEN='${token}'
EOF
```

The emitted block is the Variant A env verbatim (same `insteadOf` nuance: add a pair and bump the count if any remote uses the `ssh://` form), so everything Variant A's bullets explain applies unchanged.
`GH_TOKEN` carries the freshly minted value because `bot-env` itself runs per command — same freshness as Variant A's unevaluated mint line, same `BOT-TOKEN-MINT-FAILED` fail-closed sentinel, same sub-100 ms cache-hit cost; personal-repo commands pay only the two local git queries (milliseconds).

The decision rules and their fail direction:

| Situation | Verdict | Why |
| --- | --- | --- |
| Not a git repo | Personal | Unambiguous — nothing to attribute |
| Remotes exist, none in the org | Personal | Unambiguous |
| Any remote in the org | Bot | The remote is the repo-intrinsic signal: travels with clones and worktrees, no per-repo state, no network |
| Git repo with zero remotes | Bot, stderr warning | Ambiguous — could be org work just initialized |
| Remote query fails | Bot, stderr warning | Ambiguous — cannot rule out org work |
| Token mint fails | Bot env with invalid sentinel | `gh` and pushes fail loudly; never fall through to personal credentials |

Every ambiguous case resolves toward the bot because the two wrong outcomes are not symmetric: wrong-way-bot fails loudly (bot-authored commits are amendable, pushes 403 against the installation boundary) while wrong-way-personal is silent misattribution in the human's name.
For the same reason, do not gate on a local repo allowlist (an enrolled repo missing from the list silently works as the human) and do not check the installation list per command over the network (slow, flaky, and redundant — the token already enforces it server-side; a not-yet-installed org repo simply fails at first push, which is the "enroll me" signal).

Migrating from Variant A: delete the bot stanza from every per-repo `.claude/settings.local.json` (the whole file if that is all it held) and retire the per-repo `session-env.sh` hook registration — leftovers would pin a stale static identity regardless of what the guard decides.

**Why a hook and not a PATH-shimmed `gh`.**
The obvious approach — drop a `gh` wrapper on `PATH` via a shell rc file — fails under Claude Code and wastes hours.
Claude Code builds a *shell snapshot* at session start by sourcing `$HOME/.zshrc` from a **non-login** shell, then **freezes `PATH`** into that snapshot and replays it for every Bash command.
Consequences that defeat the rc-file approach: `.zprofile` is never sourced (non-login); `ZDOTDIR` is ignored (it hardcodes `$HOME/.zshrc`, not `$ZDOTDIR/.zshrc`); and even a correctly-placed `PATH` prepend is frozen at snapshot time, before the per-project `env` (and any marker it sets) is applied.
`CLAUDE_ENV_FILE` is the supported escape hatch: Claude Code provides it to `SessionStart`/`CwdChanged`/`Setup`/`FileChanged` hooks and sources the file's contents before every Bash command, *after* the snapshot — so an `export GH_TOKEN=...` there reliably reaches `gh`.
**Adapter contract for other harnesses.**
Phases 1–3's App, token, and credential-helper layers are harness-neutral (only `session-env.sh` is Claude Code glue); what an adapter for another local agent (e.g. Codex) must supply is this phase's routing, without editing shell dotfiles: per-repo activation (explicit opt-in or a gated automatic equivalent), the static git identity env, command-scope `GIT_CONFIG_*`, a dynamic `GH_TOKEN` re-minted across hour-plus sessions, and a fail-closed substitute when minting fails.
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
- Collaborated path: `~/.claude/bot-shims/as-me git commit --allow-empty -m "as-me test"` → author is you, unsigned (`git log -1 --format='%an <%ae> %G?'`), while `echo "${GH_TOKEN:0:4}"` still prints `ghs_`.
  Once pushed, this commit also shows no Verified badge — App-token pushes are never auto-verified, same as bot commits.
- Branch push + `gh pr create` → PR and commits authored by the bot on GitHub.
- `gh pr checks` → returns status (proves Checks and Actions read).
- Negative: `git ls-remote https://github.com/acme/<private-non-enrolled-repo>.git` → fails, proving the installation boundary.
  The probe repo must be private — public repos are readable over unauthenticated HTTPS, so a success there proves nothing.

Variant B additionally (the gate and its fail direction):

- Agent session in a non-org repo → `echo "${GH_TOKEN:-unset}"` → `unset`; `git config --show-scope credential.helper` → osxkeychain at `global` scope; test commit authored as you and signed — the guard emitted nothing.
- Zero-setup enrollment regression (the incident class Variant B exists for): enroll a fresh repo on the App, clone it, and run the opted-in checks above in a first-ever session there — they must pass with no per-repo file of any kind.
- Ambiguity direction: in a scratch `git init` repo with no remotes, the next command warns on stderr and `git var GIT_AUTHOR_IDENT` shows the bot — ambiguity resolved toward the bot, never silently personal.
- Mid-session flip: move the session's working directory from a personal repo to an org repo — the very next command shows `ghs_` and the bot author; the reverse direction shows them gone.

In a personal terminal (and any agent session outside the opted-in repos):

- `git config credential.helper` → still osxkeychain; `git config commit.gpgsign` → still true.
- `gh auth status` → personal account; commits signed and authored as the human; SSH push works.
- Because no shell dotfile was modified, personal shells are unaffected by construction — there is nothing project-specific on `PATH` or in the rc files to leak.

## Mixed Contribution — Collaborated Work as You

In repos where the human contributes both directly and through the agent, attribution is per unit of work, not per repo or per process: work the human collaborated on is authored as the human via `as-me` (Phase 3); work the agent did alone stays the bot's.

- **The bot stays the session default.**
  Do not invert to personal-credentials-by-default with a bot-credentialed subagent for autonomous work: forgetting that switch attributes autonomous agent work to the human — this skill's headline failure mode — whereas forgetting `as-me` merely attributes your work to the bot, recoverable with `as-me git commit --amend --reset-author`.
  Subagents also inherit the session environment, so a subagent cannot cleanly carry different credentials; per-command wrapping is the granularity that actually exists, and it is also the only granularity that covers mixing within a single interactive session.
- **Explicit direction only.**
  The agent uses `as-me` only when the user explicitly marks a piece of work as collaborative; it never self-decides.
  Subagents, headless runs, and scheduled agents never receive that direction, so their work is bot-attributed by construction.
- **Authorship only.**
  Pushes, `gh` calls, and PRs always ride the bot token; never bring personal credentials (SSH key, personal `gh` token) into agent sessions to make PRs "fully yours" — that reintroduces the approval-laundering surface the mitigations below remove.
- Optional convention: when the agent did substantial work on a collaborated commit, add a `Co-authored-by: acme-agent[bot] <<BOT_UID>+acme-agent[bot]@users.noreply.github.com>` trailer.

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
- Mitigations for approval laundering, strongest first:
  - Structural: remove approval capability from the human credentials resident on the agent's machine — re-auth the personal `gh` with a fine-grained PAT that lacks Pull requests write (or log it out entirely; agent sessions use the bot's `GH_TOKEN` regardless), and approve in the browser.
    The agent then cannot run `gh pr review --approve` as the human; it would have to drive the browser or steal its session, a far louder escalation.
    Personal pushes are unaffected — they ride the SSH key, not `gh`.
  - Server-side: the agent-friendly-github §2 controls close the adjacent vectors — the human-only-approvals required check keeps the bot's own approval from counting on anyone's PR, and `require_last_push_approval` (small-team/org profiles) closes approve-then-push; neither can tell an agent-driven human approval from a real one.
  - Detection: on org repos, alert on the audit-log pattern of the App's operator approving the App's PRs, especially within seconds of PR creation.
  - Procedural: never approve a bot-authored PR from inside an agent session; approvals happen in the GitHub UI or a personal terminal, after reading the diff.
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
| Leaving the personal `gh` OAuth login on the agent's machine | Its token carries PR write, so the agent can approve bot PRs as the human in one command; auth personal `gh` with a fine-grained PAT lacking Pull requests write and approve in the browser |
| Centralizing by moving the static env block to user-level `settings.json` | Static env cannot be conditional — the bot activates in every project including other orgs and personal repos; centralize with the per-command guard (Variant B) |
| A bare `eval "$(bot-env)"` guard line | Fails open: a crashed or missing script evals the empty string and the session silently runs personal in an enrolled repo; capture the output and abort the command on script failure |
| Gating user-level activation on a local repo allowlist | An enrolled repo missing from the list silently works as the human — the headline failure; gate on the org remote and let the installation boundary fail loudly for stragglers |
| Re-deciding identity with `CwdChanged`/stdin-cwd plumbing | Unneeded — `$CLAUDE_ENV_FILE` contents run before every Bash command in that command's shell and cwd, so a per-command guard tracks directory changes by construction |
| Running Variant A and Variant B together | The per-repo static env pins a stale identity regardless of what the guard decides; pick one and migrate by deleting the per-repo stanzas |
| Defaulting agent sessions to personal credentials, with a bot subagent for autonomous work | Fails open — a forgotten switch attributes agent work to the human, the headline failure mode; keep the bot as the default and escape per task with `as-me` |
| Letting the agent decide when to use `as-me` | Explicit user direction only; subagents and scheduled runs then stay bot-attributed by construction |
| Extending `as-me` to pushes and PRs with personal credentials | Reintroduces the approval-laundering surface; the escape is commit authorship only — auth stays the bot token |
| Expecting `as-me` commits to be signed or Verified | `gpgsign false` stays in effect and App-token pushes are never auto-verified; amend from a personal terminal if a signature is required |

## Done Criteria

- Phase 5 verification passes in both directions, including the negative tests.
- Phase 6 audit recorded for every installed repo, with gaps filed rather than bypassed.
- Any document describing the setup states the attribution-not-containment boundary explicitly.
