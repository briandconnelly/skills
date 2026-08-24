# OpenCode Adapter

Core setup — App registration, token minting, the credential helper, and `as-me` (Phases 1–3) — is harness-neutral and lives in the [agent-bot-identity SKILL](../../SKILL.md).
This reference is the OpenCode implementation of the SKILL's Phase 4 routing contract.
Mechanism claims trace to the opencode 1.18.22 source (`packages/opencode/src/tool/shell.ts`, `packages/opencode/src/plugin/index.ts`) and to the live verification run recorded below; where something is untested, this doc says so.

## Status

Variant A (per-project opt-in) and Variant B (user-level automatic) are the same artifact in different locations.
Variant A is **tested end-to-end on 1.18.22**, including the GitHub write path (push and PR creation) — see Verification.
Variant B differs only in where the plugin file is installed; its org-gated behavior is the same code path as Variant A's, so it inherits everything except a live run of the global install location — that one delta is untested.
Multi-account installation selection (SKILL Phase 3's `BOT_INSTALL_ID` contract) works here with no extra code: the routing decision is delegated to `bot-env`, which implements it.
`as-me` works under OpenCode (there is no sandbox wrapper around commands), so the SKILL's collaborated-work path is fully available.

## Mechanism

OpenCode fires a `shell.env` plugin hook before every shell-tool command with that command's `cwd`, and builds the command's env fresh each time as `{...process.env, ...hookEnv}`.
Identity is therefore re-decided per command, in the directory the command actually runs in, and a personal-verdict command carries no bot variables — there is no persistent shell to scrub, so this adapter needs no guard line and emits no unsets of its own.
The hook fires for tool commands only: PTY spawns (interactive terminal surfaces) pass no `sessionID`/`callID`, and the plugin returns empty env for them, keeping user-facing terminals personal — the same invariant the other adapters' verification enforces.
A throwing hook fails the shell command before it runs (`Plugin.trigger` does not swallow `shell.env` errors), which is this adapter's fail-closed path: every undetermined-identity outcome raises, and the command never executes.

One difference from the Claude Code adapter to be plain about: the hook can only add or override variables, never delete ones exported by the *server* process env.
Do not launch opencode from a shell that exports `GH_TOKEN`, `GIT_AUTHOR_*`, `GIT_COMMITTER_*`, `GIT_CONFIG_*`, or `BOT_INSTALL_ID`; a personal-verdict command would still inherit those.

## Glue scripts

One OpenCode glue file sits on top of the shared scripts:

- `scripts/opencode/agent-bot-identity.ts` is the plugin: it spawns the shared `bot-env` in the command's cwd per command and translates its emitted shell (`export KEY='value'`, `export KEY=value`, `unset ...`) into the hook's env map.
  The routing verdict, the ambiguity table, the `insteadOf` derivation, and installation selection all live in `bot-env` alone; this file owns no decision logic.
  It fails closed on: uncustomized path constant, missing/non-executable `bot-env`, non-zero exit, empty output, an unrecognized line, a timeout (20 s), or a partial identity block (identity vars without a non-empty `GH_TOKEN`).

It also needs the shared `bot-env` installed (the Claude Variant B script) — Variant A installs that lack it must add it; see the SKILL Phase 3 layout.

Install everything flat in the same directory as the shared scripts (`~/.config/acme-agent/bin/` recommended), then wire activation:

```bash
cp agent-bot-identity/scripts/bot-env ~/.config/acme-agent/bin/bot-env
chmod +x ~/.config/acme-agent/bin/bot-env
# customize bot-env per the Claude adapter (bot name, noreply email, ORG_INSTALLS map)

cp agent-bot-identity/scripts/opencode/agent-bot-identity.ts ~/.config/acme-agent/bin/agent-bot-identity.ts
# set DEFAULT_BOT_ENV to the absolute path of the installed bot-env
```

Per enrolled repo, install a one-line forwarder and keep it out of git:

```bash
mkdir -p <repo>/.opencode/plugin
printf '%s\n' 'export { default } from "/Users/<you>/.config/acme-agent/bin/agent-bot-identity.ts"' > <repo>/.opencode/plugin/agent-bot-identity.ts
printf '%s\n' '.opencode/plugin/agent-bot-identity.ts' >> <repo>/.git/info/exclude
```

Restart opencode (plugins load at startup; config is not hot-reloaded).

- **Variant A — per-project opt-in**: the forwarder above, present or absent per repo, exactly the posture of Claude Code's `.claude/settings.local.json` opt-in.
  `.git/info/exclude` is used rather than the tracked `.gitignore` because the file is machine-local.
- **Variant B — user-level automatic**: put the same forwarder at `~/.config/opencode/plugin/agent-bot-identity.ts`; the org gate in `bot-env` activates the bot in any clone whose remotes match a mapped account.
  The usual Variant B blast radius applies: a broken `bot-env` aborts every shell command in every opencode session machine-wide until fixed (verified live).

The forwarder indirection keeps one customized file per machine; the per-repo copies carry no values of their own.

## `gh` auth and token dynamics

`GH_TOKEN` is minted per shell command by `bot-env` (via the shared cached `bot-token`), so the one-hour expiry never surfaces mid-session — this adapter has no SessionStart hook and no static token anywhere.
A `ghs_` prefix echoed by an agent bash command *is* the correct proof here (unlike Codex, where a session-level `GH_TOKEN` is an audit smell): the token is injected per command, not per invocation of a shim.
Mint failure produces the non-empty `BOT-TOKEN-MINT-FAILED` sentinel from `bot-env`, so `gh` 401s loudly instead of falling back to personal stored credentials.

## Fail direction

| Situation | Result |
| --- | --- |
| `bot-env` missing, non-executable, crashing, timing out, or emitting garbage/partial output | Shell command aborts with the error; nothing runs |
| Token mint fails | Bot env with `BOT-TOKEN-MINT-FAILED`; `gh` and pushes fail loudly |
| Command cwd is a non-mapped or non-git directory | Personal env for that command only |
| opencode started with `--pure` or `OPENCODE_PURE=1` | Plugin never loads; commands run personal (documented escape hatch) |

There is one nuance versus Claude's Variant B worth stating: the verdict binds to the bash tool's `workdir` parameter.
A compound command that crosses repos (`cd <org-repo> && git commit` issued with a personal workdir) carries the starting directory's identity into the target repo, same as Claude's per-command guard.
Change directory in one command and commit in the next.

## Verification

Run these together with the SKILL's Phase 5 checks through a headless `opencode run --auto` in an enrolled repo (or an interactive session after a restart).
The 2026-08-24 run on opencode 1.18.22 exercised all of the following against a two-installation App (org + personal account); every item passed.

1. Agent bash: `echo "${GH_TOKEN:0:4}"` → `ghs_`. (PASS)
2. `git config --show-scope credential.helper` → bot helper at `command` scope. (PASS)
3. `GIT_SSH_COMMAND=/usr/bin/false git ls-remote origin HEAD` → succeeds, proving the HTTPS-rewrite-plus-token path. (PASS)
4. SKILL Phase 5 membership assertion: `gh api --paginate installation/repositories --jq '.repositories[].full_name' | grep -iFx '<org>/<repo>'` → prints the repo. (PASS)
5. Test commit on a scratch branch → author and committer are the bot, `%G?` is `N`. (PASS)
6. `as-me git commit --allow-empty ...` → author is the human, unsigned, and `GH_TOKEN` still reads `ghs_` in the same session. (PASS — `as-me` is fully supported here.)
7. Negative boundary: `git ls-remote https://github.com/<org>/<private-non-enrolled-repo>.git` → `Repository not found`. (PASS)
8. Fail-closed: `chmod -x` the installed `bot-env` → the next agent shell command aborts with `agent-bot-identity: failed to spawn bot-env ... EACCES`; nothing executes; restore the bit. (PASS)
9. Per-command flip: same session, bash call with `workdir` pointed at a repo with a non-GitHub remote → `GH_TOKEN` unset, author is the human; default-workdir calls in the same session remain bot. (PASS)
10. `bun test tests/opencode-hook.test.ts` → the parse/fail-closed suite passes, with `BOT_ENV` + `BOT_ENV_CWD` set for the live integration case. (PASS)
11. Write path: a branch push and `gh pr create` executed from a headless opencode session in an enrolled personal-account repo attribute to the bot. (PASS — this adapter's own pull request)

Audit smells specific to this adapter:

- A customized `DEFAULT_BOT_ENV` pointing into a repo or a directory on the personal `PATH`.
- A committed `.opencode/plugin/agent-bot-identity.ts` (machine-local routing config belongs in `.git/info/exclude`, and teammates without the install would hit fail-closed shell aborts).
- Identity variables exported in the shell profile that launches opencode (the hook cannot remove server-process env on personal verdicts).
- A static `GH_TOKEN` anywhere in opencode config: tokens here are minted per command and nothing should pin one.
- A copy of the plugin edited per repo instead of the one-line forwarder (divergent copies drift; the customized values belong in exactly one file).

## Common Mistakes — OpenCode mechanisms

| Mistake | Reality |
| --- | --- |
| Expecting config to inject env for bash | opencode has no env block for shell commands; the `shell.env` plugin hook is the injection surface |
| Treating a plugin install as immediate | Plugins load at startup; restart opencode after installing or editing the plugin (config is not hot-reloaded) |
| Scrubbing a reused shell on personal verdicts | Each command's env is built fresh from the server env; nothing persists across commands, so nothing needs unsetting |
| Launching opencode with `GH_TOKEN` exported | The hook overlays but never deletes; every command would inherit the stale personal token — export identity vars only inside the plugin's env map |
| Forking the plugin per repo with customized values | Ten customized copies drift; install one customized master and forward to it |
| Committing the forwarder | It is machine-local (absolute path inside); exclude it via `.git/info/exclude` — committing also subjects teammates to fail-closed aborts |
| Expecting interactive terminal surfaces to follow PTY-less routing | PTY spawns get no session/call id and stay personal deliberately; an hour-long-lived PTY could not honor the token's 1h lifetime anyway |
| Reading a hook throw as a bug report against the repo | It is the fail-closed path: fix `bot-env` (or set `OPENCODE_PURE=1` to bypass the plugin entirely in an emergency) |
