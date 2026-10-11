---
name: agent-bot-identity
description: Use when giving a local coding agent a distinct GitHub App bot identity — its commits, pushes, and PRs attribute to the bot while manual git operations on the same machine keep the personal account untouched — when splitting attribution in a repo where the human and agent both contribute, or when auditing such a dual-identity setup for over-trust. The App/token/credential-helper core is harness-neutral, with adapters for Claude Code, Codex CLI, and OpenCode.
---

# Agent Bot Identity

Core is harness-neutral; adapters ship for Claude Code, Codex CLI, and OpenCode, each with a dated verification record in its adapter doc's Status section (the Phase 4 table points at them).

## Overview

Give a local coding agent its own GitHub App identity so the commits, pushes, and PRs it makes attribute to a bot by default, while the human's git setup (SSH key, GPG signing, keychain credentials) stays untouched on the same machine.
Attribution is per unit of work: autonomous agent work carries the bot identity, and in repos where the human also contributes through the agent, collaborated commits can carry the human's authorship via the `as-me` wrapper (Phase 3) while auth still rides the bot token.
The isolation mechanism is local routing that injects the bot's credentials only into the agent's sessions where the bot belongs — either per-project opt-in or automatic org-gated routing, depending on the harness adapter (Phase 4) — without editing any shell dotfiles.

Core principle: **this buys attribution, not containment.**
The per-project scoping makes the well-behaved default path use the bot identity; the only hard boundaries are the App's installation list — which bounds git/content access and all access to private repos, not everything (see What This Enforces) — and the server-side rulesets of the repos it touches.
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
| Blast radius | App installed on "Only select repositories" | Token cannot touch non-enrolled **private** repos or push to any non-enrolled repo, even if config leaks; public-repo surfaces open to any actor (e.g. filing issues) stay open |
| Local routing | harness adapter — see Phase 4 | Bot identity activates only where the adapter routes it — per-project opt-in or org-gated automatic; no shell dotfiles change |
| git auth | `insteadOf` + `pushInsteadOf` SSH→HTTPS rewrites + git credential helper (`GIT_CONFIG_*`) | Pushes use the installation token, not the personal SSH key or keychain |
| gh auth | harness adapter — see Phase 4 | `gh` calls use the installation token, minted fresh per session/command rather than the personal login |
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
3. Note the **Installation ID** from the post-install URL (`.../settings/installations/<id>`), via `gh api orgs/{org}/installations` with an org-admin user token, or via app JWT (a normal user token will not work on app-JWT endpoints).
   The accessible app-JWT route is `gh api repos/{owner}/{repo}/installation`: it needs no org role, answers the question that matters when debugging — which installation covers this repo — and 404s when the repo is not enrolled anywhere; `gh api /app/installations` lists every installation of the App.
   Installations are per account, not per App: an App installed on an org and on a personal account has two installation IDs, and `bot-token` must be configured with the one whose account owns the repos being worked.
4. Get the bot's user ID for commit attribution: `gh api 'users/acme-agent%5Bbot%5D' --jq .id`.
   The bot's commit email is `<BOT_UID>+acme-agent[bot]@users.noreply.github.com`; using it makes commits render with the bot's avatar.

## Phase 3 — Helper scripts

Rules:

- Install only the glue for the adapter(s) you actually use.
- **Never put the install directory on your personal `PATH`.**
- Keep the install path free of spaces and shell metacharacters.
- A cache entry must be keyed by every input that changes what its token can reach; a token minted for one installation must never be served to a caller working under another.
- If you scope tokens with a `"repositories"` field (the optional hardening below), extend the cache key with a digest of the scoping fields, per the keying rule above: a cache keyed only by installation silently serves a token minted for one repo's scope to a caller needing another — no error, for the whole cache-validity window.
- A consumer of the token must parse `expires_at` from the mint response, never assume a one-hour life.
- Keep `git-credential-bot` host-gated.
- For an eligible `https://github.com` request, a crashed or empty mint must return the complete invalid credential `username=x-access-token` and `password=BOT-TOKEN-MINT-FAILED` so Git cannot fall through to askpass, terminal prompting, or a personal credential source.
- For a wrong-host request it must stay silent so a typosquatted or mis-rewritten remote cannot coax out the installation token.
- Normalize hostnames case-insensitively and strip any credential-protocol port suffix before comparing to `github.com`.
- Do not globally override `GIT_ASKPASS`, `SSH_ASKPASS`, or terminal-prompt variables in Variant B because a personal verdict cannot safely reconstruct IDE-provided values that the guard inherited.
- Always run `as-me` with a command — the script refuses zero arguments, because bare `env` would print the entire environment, `GH_TOKEN` included.
- When and for what `as-me` may be used is set by Mixed Contribution.

The helper scripts are bundled under `scripts/`; copy the needed files into a single flat directory, customize their placeholders, and `chmod +x` each copied file.
`~/.config/acme-agent/bin/` is the recommended neutral location.
Install everything flat in that one directory — including each harness adapter's glue scripts, which live under `scripts/claude/`, `scripts/codex/`, and `scripts/opencode/` in this repo but sit next to the shared scripts once installed.
An unused adapter's scripts are extra attack surface with no benefit.
The install directory contains a `gh` shim (the Codex adapter's) that would route your own terminal through the bot token, and the whole design rests on your personal shells never resolving it.
The scripts self-locate, so existing `~/.claude/bot-shims/` installs keep working unchanged; for a new install prefer the neutral directory, and adjust every path in the settings examples consistently.
The install path matters because `bot-env` emits a `!`-prefixed credential helper that git re-parses through `sh -c`, and both it and the Claude glue refuse to install from an unsafe path rather than emit a line that breaks or executes.

Use these resources:

- `scripts/bot-token` mints and caches installation tokens.
- `scripts/git-credential-bot` feeds installation tokens to git and answers only `https://github.com`, accepting case-insensitive hostnames and an optional port suffix from git's credential protocol.
- `scripts/as-me` provides personal authorship for collaborated commits.

Each harness adapter (Phase 4) adds its own glue scripts on top of these; see the adapter doc.

Customize `bot-token` with the App ID, the default installation ID, the key path, and the cache location.
`bot-token` mints for its default installation unless the environment carries `BOT_INSTALL_ID`, the numeric id of another installation of the same App — the selection contract adapters use when one machine serves more than one GitHub account (installations are per account, Phase 2).
It refuses a non-numeric id — including the unreplaced placeholder — rather than minting, because the id reaches both the API URL and the cache filename.
An adapter that sets `BOT_INSTALL_ID` must resolve it from the repo's raw remotes and fail closed: an unmapped account gets a hard error or the personal verdict, never a fallback to another entry's id — a fallback mints a *valid* token for the wrong installation, which 404s on the repo instead of failing at auth.
The Claude adapter's Variant B implements this resolution inside `bot-env`'s existing remote parse and clears the variable on personal and ambiguous verdicts so a selection never leaks from a previously visited repo; Variant A can pin a per-project value in its static env; the Codex adapter performs no selection (single-installation — see its doc).
The cache lives at `~/.cache/acme-agent/token-<installation id>.json`, deliberately outside the key-and-scripts directory: a sandboxed harness can then grant write access to the cache without also granting it to `key.pem` and the fail-closed scripts (see the Codex adapter's sandbox profile).
The cache filename is keyed by the installation id, per the keying rule above.
Upgrading from a pre-keying install: delete the old unkeyed `token.json` once — nothing reads it.
It parses `expires_at`, writes the token cache through a `0600` temp file swapped in with `os.replace()`, and sets a request timeout so a hung mint does not hang git or `gh` indefinitely.
It refuses to print an empty token — from the cache or from the API — because an empty `GH_TOKEN` is the fail-open case every caller here guards against.
The `uv run` shebang requires `uv` on PATH where the script is invoked; use an absolute path to `uv` if that is not guaranteed.
On a cache hit this runs in well under 100 ms, cheap enough to call before every Bash command.
There is no lock around the mint: concurrent cold-cache invocations may each mint a token — duplicate API work, not a correctness problem, since both tokens are valid and the last cache write wins.
Optional hardening: pass a `"repositories"` field in the token request to scope each token to the repo being worked.

Host-gating `git-credential-bot` matters most under an automatic-activation adapter that installs the helper in any org-matching repo (e.g. Claude Code's Variant B — see the adapter doc).

`as-me` unsets the four identity variables, so git falls back to the global `user.*` config while pushes, `gh` calls, and PRs still ride the bot token.
These commits are unsigned because `gpgsign false` stays in effect, and they show no Verified badge once pushed.
Forgot the wrapper and committed as the bot? `as-me git commit --amend --reset-author` fixes the last commit.
When to use it is a policy question, not a mechanism question; see Mixed Contribution below.

## Phase 4 — Local routing: the adapter contract

Phases 1–3 are harness-neutral; local routing is the only harness-specific layer.
An adapter for a local agent harness must supply all of the following, without editing shell dotfiles:

- Per-repo activation: explicit opt-in, or a gated automatic equivalent keyed on a repo-intrinsic signal such as the org remote.
- The static git identity env (`GIT_AUTHOR_*`/`GIT_COMMITTER_*`).
- Command-scope `GIT_CONFIG_*`: an unscoped credential-helper reset (it empties the helper list for every host) plus the host-gated bot helper, which answers all of `https://github.com` and nothing else (never scoped to an account — [`decisions/001`](decisions/001-credential-helper-scope.md)) with `GIT_CONFIG_PARAMETERS` set empty so an inherited `git -c` value cannot follow the reset, SSH→HTTPS rewrites for the bot's GitHub remotes emitted as both `insteadOf` and `pushInsteadOf` and including identity pairs on the https prefix (so a user's global force-SSH rewrite cannot undo them), `commit.gpgsign false`.
- A dynamic `GH_TOKEN` re-minted across hour-plus sessions.
- A fail-closed substitute when minting fails: a non-empty invalid token, never an empty value.
- When the machine serves more than one GitHub account: installation selection per Phase 3's `BOT_INSTALL_ID` contract.

A harness missing one of these capabilities is pending, not approximated — a half-wired adapter fails open to the personal identity.
Do not port an adapter mechanically: Claude Code's per-command env-file evaluation has no assumed equivalent elsewhere.

Implemented adapters:

- [Claude Code](references/adapters/claude-code.md) — Variant A (per-project opt-in) and Variant B (user-level automatic, per-command re-decision).
- [Codex CLI](references/adapters/codex.md) — Variant A through the `codex-bot` launcher; Variant B pending.
- [OpenCode](references/adapters/opencode.md) — one plugin file; Variant A per repo, Variant B at user level.

| Capability | Claude Code | Codex CLI | OpenCode |
| --- | --- | --- | --- |
| Static identity env | ✅ settings/env or guard | ✅ `shell_environment_policy.set` via named profile | ✅ per-command `shell.env` hook |
| Dynamic `GH_TOKEN` | ✅ SessionStart hook, per command | ✅ PATH-shimmed `gh`, minted per invocation | ✅ minted per command by `bot-env` |
| Per-command redecision | ✅ Variant B guard | ❌ pending | ✅ hook fires per command with cwd |
| Fail-closed routing | ✅ guard aborts / sentinel token | ✅ sentinel token (routing only) | ✅ hook throw aborts command / sentinel token |
| Automatic user-level routing | ✅ Variant B | ❌ pending | ✅ global plugin dir |
| `as-me` authorship escape | ✅ | ❌ (sandbox denies non-literal-git `.git` writes) | ✅ |
| Installation selection (multi-account, Phase 3) | ✅ Variant B map / Variant A pinned env | ❌ pending (default installation only) | ✅ delegated to `bot-env` |
| Verification record | [claude-code.md Status](references/adapters/claude-code.md#status) | [codex.md Status](references/adapters/codex.md#status) | [opencode.md Status](references/adapters/opencode.md#status) |

("Fail-closed" is scoped to routing, never containment.)

## Phase 5 — Verify both directions

Rules:

- Do not begin git or `gh` work until your adapter's token check and the command-scope credential-helper check pass — see the adapter doc for which token check applies.
- Run the negative private-repo probe only after the membership check has passed.
- The app-JWT lookup is an out-of-band diagnostic: run it from a personal terminal with explicit JWT auth, never through the adapter's `gh` path, which replaces the JWT with the installation token.

In a fresh agent session in an opted-in repo:

- Run your adapter's activation checks first — see the adapter doc.
- If the adapter injects `GH_TOKEN` into the command env (Claude Code, OpenCode): `echo "${GH_TOKEN:0:4}"` → `ghs_`, proving the adapter injected *an* installation token — which installation it came from is what the membership check below establishes.
  This check does not port to a per-invocation shim adapter (Codex CLI), where a session-level `GH_TOKEN` is an audit *smell*, not a pass — the shim exports it per invocation.
- Membership: `gh api --paginate installation/repositories --jq '.repositories[].full_name' | grep -iFx 'acme/<this-repo>'` → prints the repo, proving the token belongs to the installation that covers this session's repo.
  Match case-insensitively (`-i`): GitHub's namespace is case-insensitive and `full_name` returns canonical casing, so a hand-written expected name that differs only in case would otherwise false-negative.
  Write the expected `owner/repo` from what you know the session repo to be; deriving it through the token under test (e.g. `gh repo view`) can fail before the assertion runs.
  This is the harness-neutral token check every adapter shares, and the only check here that a wrong-installation token fails: the `ghs_` prefix, an enrolled-repo *count*, and a direct `gh api repos/{owner}/{repo}` read on a public repo all pass for any valid installation token of the App — a count is a diagnostic, never a pass (`--paginate` matters: the endpoint pages at 30 repos).
  Use this, not `gh api user` — an installation token has no user and 403s on `/user`.
- `git config --show-scope credential.helper` → bot helper at `command` scope (proves env-scoped, no file changed).
- `GIT_SSH_COMMAND=/usr/bin/false git ls-remote origin` → succeeds, proving the HTTPS-rewrite-plus-token path is in use (SSH is disabled for that invocation).
- Competing HTTP credentials, the two shapes `bot-env` refuses (see the Claude Code adapter's decision table) and the static adapters cannot: `git config --get-regexp '^http\.(.*\.)?extraheader$' | awk 'tolower($2) ~ /^authorization:/ {print $1}' | while read -r k; do s=${k#http.}; s=${s%.extraheader}; a=${s#*://}; a=${a%%/*}; u=${a%@*}; if [ "$u" = "$a" ]; then u=; else u="$u@"; fi; o=${a##*@}; o=${o##*:}; case $o in ''|*[!0-9]*) o=;; *) o=:$o;; esac; c=$(printf %s "${s%%://*}" | tr '[:upper:]' '[:lower:]'); [ "$c" = http ] || c=https; p=${s#*://}; p=${p#*/}; if [ "$s" = extraheader ] || [ "$(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.$s.botenvprobe" GIT_CONFIG_VALUE_0=yes git config --get-urlmatch http.botenvprobe "$c://${u}github.com$o/$p")" = yes ]; then echo "$k"; fi; done` → prints nothing, and `[ -f ~/.netrc ] && tr -s '[:space:]' '\n' < ~/.netrc | tr -d '"' | awk 'tolower($0)=="default"{f=1} p=="machine"&&tolower($0)=="github.com"{f=1} {p=tolower($0)} END{exit !f}' && echo COMPETING-NETRC` → prints nothing (an absent `~/.netrc` is a pass).
  The header probe prints the matching key only, never its value.
  The header probe rejects every Authorization scope that git's own URL matcher would apply to any `https://github.com/` destination, not only this repository's, because a static adapter's environment covers every GitHub command in the session; the netrc probe is a token scan that reads `~/.netrc` only (`bot-env` also scans `~/_netrc`, the Windows name) and does not parse `macdef` bodies.
- `for r in $(git remote); do git remote get-url --all --push "$r"; done` → every `github.com` line is `https://github.com/...`, and, on a branch with at least one commit, `GIT_SSH_COMMAND=/usr/bin/false git push --dry-run origin HEAD` → succeeds.
  `ls-remote` resolves the fetch URL only; a push-side rule or an SSH `pushurl` passes it and then pushes over the personal key under the bot's authorship, and GitHub-side authorship cannot tell the two apart.
- Test commit → author `acme-agent[bot]`, unsigned (`git log -1 --format='%an <%ae> %G?'`).
  Once pushed, the commit shows no Verified badge — expected, because local commits pushed with an App token are never auto-verified; only commits created through the App's API path (e.g. GraphQL `createCommitOnBranch`) get the badge.
- If the adapter supports `as-me` (see the Phase 4 support matrix) — collaborated path: `~/.config/acme-agent/bin/as-me git commit --allow-empty -m "as-me test"` → author is you, unsigned (`git log -1 --format='%an <%ae> %G?'`), while `echo "${GH_TOKEN:0:4}"` still prints `ghs_`.
  Once pushed, this commit also shows no Verified badge — App-token pushes are never auto-verified, same as bot commits.
- Branch push + `gh pr create` → PR and commits authored by the bot on GitHub.
- `gh pr checks` → returns status (proves Checks and Actions read).
- Negative: `git ls-remote https://github.com/acme/<private-non-enrolled-repo>.git` → fails, proving the installation boundary.
  The probe repo must be private — public repos are readable over unauthenticated HTTPS, so a success there proves nothing.
  A wrong-installation or under-scoped token also fails here, so without the positive assertion this failure cannot distinguish the working boundary from a broken setup.

When a Phase 5 check or a later bot operation fails, triage before changing config — the failure statuses overlap:

| Symptom | Distinguish with | Cause |
| --- | --- | --- |
| 401 and the credential is `BOT-TOKEN-MINT-FAILED` | — | Mint failed; the fail-closed sentinel is working as designed — debug `bot-token` |
| 404 on a repo you believe is enrolled | `gh api repos/{owner}/{repo}/installation` under an app JWT (Phase 2) vs the configured Installation ID | IDs differ → token minted from the wrong installation |
| ↳ that lookup also 404s | — | Repo not enrolled in any installation of this App |
| Membership check passes but a call 403s with `Resource not accessible by integration` | The App's granted permissions (Phase 1) | Missing permission (e.g. `actions: read` for `gh pr checks`) |

Run your adapter's own routing checks in addition to these — for an automatic adapter, that includes the gate's fail direction (ambiguity resolves to bot, broken guard aborts, mid-session flips). See the adapter doc.

In a personal terminal (and any agent session the routing leaves personal — see the adapter doc for which sessions those are):

- `git config credential.helper` → still osxkeychain; `git config commit.gpgsign` → still true.
- `gh auth status` → personal account; commits signed and authored as the human; SSH push works.
- Because no shell dotfile was modified, personal shells are unaffected by construction — there is nothing project-specific on `PATH` or in the rc files to leak.
  This holds only while the install directory stays off your personal `PATH` (Phase 3); adding it there puts the Codex adapter's `gh` shim in front of the real `gh` in your own terminal.

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

Rules:

- Run the audit from a personal terminal, never through the bot token — not because the bot token fails loudly, but because it does not fail at all.
- Positive control: before recording "no bypass actors on any ruleset", prove the reading identity could have seen one — a redacted view and a clean result are otherwise identical.
- `gh api user` returning your personal login rules out the bot token (installation tokens 403 there) but is not sufficient: a personal account without admin access to the repo also gets `bypass_actors` omitted from the read, the same false-clean shape (verified 2026-07-12).
- List each ruleset with its source first: `gh api --paginate repos/OWNER/REPO/rulesets --jq '.[] | [.id, .source_type, .source] | @tsv'`.
- For a `Repository` source confirm `gh api repos/OWNER/REPO --jq .permissions.admin` is `true`; for an `Organization` source (`ORG` is that ruleset's `source` from the listing command) confirm `gh api orgs/ORG/memberships/$(gh api user --jq .login) --jq .role` is `admin`.
- A ruleset whose source is `Enterprise` (or any other source) is unverified unless the reader is an owner of that enterprise.
- Then read each ruleset with `gh api repos/OWNER/REPO/rulesets/ID --jq '.bypass_actors | type'` and treat anything other than `array` as unverified, never as empty, since an empty array is a legitimate clean result.
- File gaps with the repo's admins rather than working around them.

Identity is Step 1 of the agent-friendly-github setup workflow; enforcement lives in each repo's ruleset, not in the App.
For every repo the App is installed on, walk that skill's checklist §2; the items this setup specifically depends on:

- Required approving reviews ≥ 1 with self-approval not counted.
- `dismiss_stale_reviews_on_push` enabled.
- Force-push and branch deletion blocked; required status checks strict.
- Bypass-actors list contains no automation identity — including this App and any other bot App already installed (verify; never assume an existing bot's posture is clean).
- No `required_signatures` rule, or a dedicated bot signing key is provisioned first — `gpgsign false` plus an App-token push means every bot commit is unsigned, and a `required_signatures` ruleset rejects the push outright.

An installation-token ruleset read succeeds with `bypass_actors` silently withheld — `--jq '.bypass_actors'` prints `null` instead of the request failing with 403 — so a bot-token audit reports "no bypass actors" while blind to exactly the item most likely to be non-clean.
A bot-token audit is therefore not merely incomplete; it is affirmatively misleading.
Some checks (Actions settings, secret scanning) also need repo admin access.

## What This Enforces — and What It Does Not

Enforced, server-side:

- The installation token carries only the granted scopes and expires in one hour; the installation list bounds git/content access and **all** access to private repos.
  It does not bound issue creation on public repos: any authenticated actor — an App installation token included — can open an issue on any public repo with Issues enabled, even one the App is not installed on, so a misdirected agent can post far outside the enrolled set, attributed to the operator's App.
  That is a reputational and spam surface rather than a code-integrity one, but treat the enrolled set as the bot's *git* reach, not its *write* reach.
- No Workflows permission means GitHub rejects bot pushes that add or modify files under `.github/workflows/`; CI logic living elsewhere — scripts the workflows invoke, composite actions, Makefiles — is still reachable with Contents write, which is part of why the human review gate matters.
- Supported GitHub-side events such as `pull_request.create` and `pull_request_review.submit` record actors and can support the approval-laundering detection pattern; local commits, most reads, and every local action are not automatically organization audit-log events.
- On GitHub Enterprise Cloud, [Git transport events](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/audit-log-events-for-your-enterprise#git) (`git.clone`, `git.fetch`, and `git.push`) are available through the REST API, export, or audit-log streaming rather than the web interface, and GitHub retains them for [seven days](https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization#using-the-audit-log-api).

Not enforced — the part everyone overstates:

- The agent runs as the human's OS user: it can read `key.pem`, run `bot-token` directly, call the real `gh` by full path, read `~/.ssh`, or edit the shims and `settings.local.json` themselves.
- It therefore holds **both identities**, which enables approval laundering: author a PR as the bot, approve it as the human from a non-opted-in session.
  GitHub's block on author self-approval does not close this.
- A required-review rule binds the **bot token**, not the agent; treat it as enforcement against the bot identity and a convention for the agent.
- Mitigations for approval laundering, strongest first: structural — strip Pull requests write from the personal `gh` credentials resident on the machine (fine-grained PAT, approve in the browser); server-side — agent-friendly-github §2's human-only-approvals check and `require_last_push_approval`; detection — audit-log alerts on the App's operator approving the App's PRs; procedural — never approve from inside an agent session.
  The worked list with rationale: [references/approval-laundering.md](references/approval-laundering.md).
- If containment is actually required, change the architecture (separate OS user, container, or VM), not the config.

## Common Mistakes

| Mistake | Reality |
| --- | --- |
| Letting a failed mint leave `GH_TOKEN` empty | `gh` treats empty as unset and silently falls back to the personal stored credentials — Phase 4 contract |
| Probing identity with `gh api user` | Installation tokens have no user and 403 there — Phase 5 membership check |
| Verifying the token with a repo count or the `ghs_` prefix | Both pass for any valid installation token of the App, including a wrong installation's — Phase 5 membership check |
| Self-assigning issues to signal the bot is working them | A GitHub App bot actor is not a valid assignee, so `gh issue edit --add-assignee` with the bot as target fails — and `Issues: write` is already the max grant, so no wider permission exists; signal work-in-progress with a claim label (e.g. `agent:in-progress`) via `--add-label` instead |
| Granting Checks read without Actions read | Under an App token `gh pr checks` needs both — the status rollup traverses each check suite's workflow run |
| Granting Workflows: write "to be safe" | Hands a prompt-injected agent the ability to rewrite CI — Phase 1 |
| Write token cache, then chmod | umask window exposes the token; create `0600` atomically |
| One shared token cache across installations or scopes | A cached token minted under one authority is silently served to callers needing another for the whole cache window — Phase 3 Rules |
| Assuming one-hour token life | A token's real lifetime is whatever the mint response reports — Phase 3 Rules |
| Leaving the personal GPG key signing bot commits | Attribution mismatch — a human signature on bot-authored work — Phase 4 contract |
| Expecting the Verified badge on bot commits | Local commits pushed with an App token are not auto-verified; only API-path commits (e.g. GraphQL `createCommitOnBranch`) get the badge |
| Calling the review gate "enforced against the agent" | The agent holds both identities; the gate binds the bot token (see approval laundering above) |
| Leaving the personal `gh` OAuth login on the agent's machine | Its token carries PR write, so the agent can approve bot PRs as the human in one command; auth personal `gh` with a fine-grained PAT lacking Pull requests write and approve in the browser |
| A credential helper that answers for any host | git invokes it for every host it authenticates to, so a host-blind helper hands the installation token to a typosquatted, mis-rewritten, or attacker-controlled remote — Phase 3 Rules |
| Deciding the org match by pattern-matching the raw remote line | Any boundary character you pick (`/`, `@`) also appears in URL *paths*, so `notgithub.com/acme/`, `example.com/@github.com/acme/`, or `github.com.evil.tld/acme/` can all spoof a bot verdict; parse each remote down to its authority (`[userinfo@]host[:port]`) and compare the host case-insensitively to `github.com`, then check the org path segment case-insensitively — don't regex the whole line, and for ssh aliases and `ssh.github.com` follow the Claude Code adapter's decision table |
| Emitting `insteadOf` pairs only for SSH-form remotes, or without `pushInsteadOf` twins | git resolves rewrites by longest matching prefix across every config scope and consults `pushInsteadOf` first for pushes, so a global force-SSH rewrite pulls an https org remote back onto the personal SSH key with the bot as author — Phase 4 contract |
| Treating git exit 128 as "not a repository" | git exits 128 on every fatal error (corrupt config, unsupported repository format, dubious ownership, malformed inherited `GIT_CONFIG_*`), so a guard that resolves personal on 128 alone silently attributes org work to the human — Claude Code adapter's decision table |
| Gating user-level activation on a local repo allowlist | An enrolled repo missing from the list silently works as the human — the headline failure — Phase 4 contract |
| Defaulting agent sessions to personal credentials, with a bot subagent for autonomous work | Fails open — a forgotten switch attributes agent work to the human, the headline failure mode — Mixed Contribution |
| Letting the agent decide when to use `as-me` | A self-deciding agent defeats the by-construction bot attribution of subagents and scheduled runs — Mixed Contribution |
| Extending `as-me` to pushes and PRs with personal credentials | Reintroduces the approval-laundering surface — Mixed Contribution |
| Expecting `as-me` commits to be signed or Verified | `gpgsign false` stays in effect and App-token pushes are never auto-verified; amend from a personal terminal if a signature is required |
| Auditing Phase 6 rulesets with the bot token | A bot-token ruleset read succeeds with `bypass_actors` withheld rather than failing with 403, so the audit looks clean while blind — Phase 6 Rules |
| Assuming the installation list bounds everything the bot can write | Issue creation on any public repo with Issues enabled is open to any authenticated actor, App tokens included — What This Enforces |
| Scoping the credential helper to the mapped account so unrelated private fetches keep working | Every unmapped github.com HTTPS push would then ride the personal credential under the bot's authorship — the headline failure — Phase 4 contract |

Harness-mechanism-specific pitfalls (PATH-shim snapshots, `settings.local.json` static env, the per-command guard, `CwdChanged` plumbing) live with each adapter — see the adapter doc.

## Done Criteria

- Phase 5 verification passes in both directions, including the negative tests, minus any check the adapter's support matrix marks unavailable.
- Phase 6 audit recorded for every installed repo, with gaps filed rather than bypassed.
- Any document describing the setup states the attribution-not-containment boundary explicitly.
