# pi Adapter

Core setup — App registration, token minting, the credential helper, and `as-me` (Phases 1–3) — is harness-neutral and lives in the [agent-bot-identity SKILL](../../SKILL.md).
This reference is the pi implementation of the SKILL's Phase 4 routing contract.
Mechanism claims trace to the pi 1.1.0 package source (`dist/core/tools/bash.js`, `dist/core/tools/powershell.js`, `dist/core/agent-session.js`, `dist/core/bash-executor.js`, `dist/core/extensions/runner.js`, `dist/modes/interactive/interactive-mode.js`, `dist/modes/rpc/rpc-mode.js`, `dist/utils/shell.js`, `dist/core/resolve-config-value.js`, `dist/modes/interactive/session-share.js`), read on 2026-10-10, to pi's bundled docs, and to the runs recorded under Verification; where something is untested, this doc says so.

## Status

Variant A (per-project opt-in) and Variant B (user-level automatic) are the same artifact in different locations.
As of 2026-10-10 the extension has passed its unit suite and pi's own loader gate (see Verification), but no live end-to-end run against a real install is recorded yet; until one is, treat both variants as untested end-to-end.
Variant B differs only in where the forwarder is installed; its live load through the real pi loader has not run.
Multi-account installation selection (SKILL Phase 3's `BOT_INSTALL_ID` contract) works here with no extra code: the routing decision is delegated to `bot-env`, which implements it.
`as-me` is available under pi (there is no sandbox wrapper around commands), so the SKILL's collaborated-work path applies.

## Mechanism

pi runs shell commands through these paths; the table covers every path found in the 1.1.0 source that runs a shell command or `gh` in the session, and is not claimed exhaustive beyond that trace.

| Surface | Path in pi 1.1.0 | Adapter coverage |
| --- | --- | --- |
| `bash` tool — model calls, codemode `tools.bash`, nested `ctx.executeTool` | `dist/core/tools/bash.js` `createShellToolDefinition` → `ops.exec(command, ctx.cwd \|\| cwd, {env})` | Re-registered `bash` tool with wrapped operations |
| TUI `!` / `!!` | `dist/modes/interactive/interactive-mode.js` `handleBashCommand` → `emitUserBash` → `executeBash(…, {operations})` | `user_bash` handler returning wrapped operations |
| RPC `bash` command | `dist/modes/rpc/rpc-mode.js` → `emitUserBash` → `executeBash(…, {operations})` | Same handler |
| `powershell` tool | `dist/core/tools/powershell.js` | Not routed; blocked by the extension's `tool_call` handler |
| `!`-prefixed config values (API keys, headers) | `dist/core/resolve-config-value.js` `executeCommand` | Not routed; runs personal (out of scope) |
| `/share` GitHub fallback | `dist/modes/interactive/session-share.js` (`gh auth status`, `gh gist create`) | Not routed; runs as the personal `gh` login (out of scope) |
| `pi.exec` from other extensions | extension API | Not routed; personal (out of scope; see audit smells) |

Identity is resolved inside `operations.exec`, once per command, in the cwd the command actually runs in, for both the `bash` tool and `user_bash`.
A throw from `exec` fails the command with no local fallback (`dist/core/bash-executor.js`), which is this adapter's fail-closed path: every undetermined-identity outcome throws before the command runs.
The replacement `bash` tool builds its definition on each call from the effective settings, so a configured `shellCommandPrefix` and a `~`-expanded `shellPath` behave as with the built-in (`dist/core/agent-session.js` `_buildRuntime` passes them to the built-in explicitly; a replacement does not inherit them).

One difference from the OpenCode adapter to be plain about: this extension hands pi's shell a complete env, built from the env pi would have used (agent `bash`: pi's shell env plus `PI_*` session variables; `!`/RPC: pi's shell env as `dist/utils/shell.js` builds it).
A personal verdict therefore removes identity variables inherited from the launching shell, because `bot-env` sees the routed env and enumerates its `unset` lines from it.
This holds only on routed surfaces; see Fail direction for the rest.

## Glue scripts

One pi glue file sits on top of the shared scripts:

- `scripts/pi/agent-bot-identity.ts` is the extension: it re-registers `bash`, handles `user_bash`, and blocks `powershell`, spawning the shared `bot-env` per command in the command's cwd.
  The routing verdict, the ambiguity table, the `insteadOf` derivation, and installation selection all live in `bot-env` alone; this file owns no decision logic.
- `scripts/bot-env-block.ts` is the shared parser the extension imports (through a symlink in `scripts/pi/`): it owns the parse and the contract check.
  The Fail direction table below is the one list of undetermined-identity outcomes and of what the deadline does.

It also needs the shared `bot-env` installed; see the SKILL Phase 3 layout and its reinstall-together rule.

Install everything flat in the same directory as the shared scripts (`~/.config/acme-agent/bin/` recommended), then wire activation:

```bash
cp agent-bot-identity/scripts/bot-env ~/.config/acme-agent/bin/bot-env && chmod +x ~/.config/acme-agent/bin/bot-env
cp agent-bot-identity/scripts/bot-env-block.ts ~/.config/acme-agent/bin/bot-env-block.ts
cp agent-bot-identity/scripts/pi/agent-bot-identity.ts ~/.config/acme-agent/bin/agent-bot-identity-pi.ts
# set DEFAULT_BOT_ENV in agent-bot-identity-pi.ts to the absolute path of the installed bot-env
mkdir -p <repo>/.pi/extensions
printf '%s\n' 'export { default } from "/Users/<you>/.config/acme-agent/bin/agent-bot-identity-pi.ts"' > <repo>/.pi/extensions/agent-bot-identity.ts
printf '%s\n' '.pi/extensions/agent-bot-identity.ts' >> <repo>/.git/info/exclude
```

- **Variant A — per-project opt-in**: the per-repo forwarder above.
  pi loads project extensions only for trusted projects (pi docs: `docs/security.md` "Understand project trust", `docs/cli.md` `-a`/`--approve`); an untrusted project runs personal.
  Trust a project interactively at the trust prompt or with `/trust`, or for one process with `--approve`.
- **Variant B — user-level automatic**: put the same forwarder at `~/.pi/agent/extensions/agent-bot-identity.ts`; the org gate in `bot-env` decides per command.

Restart pi after installing or editing the extension, or use `/reload` and then re-run the activation check (see the reload row under Fail direction).

## `gh` auth and token dynamics

`GH_TOKEN` is minted per command by `bot-env` (via the shared cached `bot-token`), so the one-hour expiry never surfaces mid-session.
A `ghs_` prefix echoed by an agent bash command is the correct proof here; see the SKILL's Phase 5 token check for adapters that inject `GH_TOKEN` into the command env.
Mint failure produces the non-empty `BOT-TOKEN-MINT-FAILED` sentinel from `bot-env`, so `gh` and pushes fail loudly instead of falling back to personal credentials.

## Fail direction

| Situation | Result |
| --- | --- |
| `bot-env` missing, non-executable, crashing, malformed, truncated (no completeness line) or partial output, or not finished at the 20 s deadline | Agent bash: failed tool result, command not run. `!`/RPC: the command fails and does not run. At the deadline the extension kills the script and releases its own pipe ends. Covered by the unit suite; not yet observed live |
| Token mint fails | Bot env with `BOT-TOKEN-MINT-FAILED`; `gh` and pushes fail loudly |
| Command cwd is a non-mapped or non-git directory | Personal env for that command, inherited identity variables stripped |
| `powershell` tool called | Blocked with a message pointing here. The tool is off by default (`docs/settings.md` `defaultTools`); keep it disabled |
| An earlier-loaded extension's `user_bash` handler returns a result | `!`/RPC commands bypass routing and run with the inherited env; agent bash is unaffected. pi uses the first handler result that is not `undefined` and calls no later handler (`dist/core/extensions/runner.js` `emitUserBash`; `docs/extensions.md`) |
| Forwarder target missing at startup (stale path, typo, moved install) | Fatal at startup: observed on pi 1.1.0 for a project forwarder with `--approve` — `Failed to load extension … Cannot find module …` on stderr and exit code 1 in RPC mode; a valid sibling extension did not rescue startup. `-p` mode printed the same error (its exit code was not captured). The Variant B location was not tested |
| Extension fails to load on `/reload` | Per the source (`dist/core/agent-session.js` `reload` rebuilds the runtime with whatever loaded; not observed live): pi reports the error and continues with the remaining extensions and the built-in `bash`, so routing silently stops for the rest of the session. An unloaded extension cannot enforce its own presence; re-run the activation check after every reload |
| Extension not loaded: untrusted project (Variant A), `-na`/`--no-approve`, or `-ne`/`--no-extensions` | Personal. Observed on pi 1.1.0: in RPC mode without `--approve` (non-TTY) and with `--no-approve`, project extensions were skipped silently; `-ne` also skipped them |
| Config `!`-commands, `/share` gist fallback, other extensions' `pi.exec` | Personal (out of scope; see Mechanism). Identity variables exported in the launching shell reach these surfaces unchanged |

The `bash` tool has no `workdir` parameter (`dist/core/tools/bash.js` schema: `command`, `timeout`); each call runs in the session cwd.
A compound command that crosses repos (`cd <org-repo> && git commit` from a personal cwd) keeps the starting cwd's verdict, so set the session cwd to the target repo instead.

## Verification

Run these together with the SKILL's Phase 5 checks in an enrolled repo.
Launch rules for headless pi, observed on pi 1.1.0 on 2026-10-10:

- Pass `--approve` (`-a`) for a Variant A run: print, JSON, and RPC modes cannot show the trust prompt, and without an override or a saved decision they skip project extensions silently, so the run is personal with no error.
- For a load check that must not reach a model, `pi --offline --approve --mode rpc --no-session` with a `get_state` request exercises startup only.

Score every check from the recorded tool state (the tool call's input and result in the session or RPC events), never from the model's summary of it.

Recorded on 2026-10-10, pi 1.1.0, without a model provider or a real install:

- Unit suite: `bash agent-bot-identity/tests/pi-extension-test.sh` from the repo root, 20 pass, 0 fail, covering every refusal path before the inner `exec`, the deadline, the personal-verdict strip, delayed `user_bash` resolution in the `exec` cwd, `shellCommandPrefix`/`shellPath`, the `powershell` block, and co-installation with the OpenCode master.
- pi loader gate (`tests/pi-gate/`, a scripted faux model and a fixture `bot-env`): the gate self-test passed, then the extension loaded with no extension error, `bash` registered from the artifact, and the routed `bash` result carried the fixture `ghs_` token and the command-scope helper; the same gate passed through a one-line forwarder, and the import of `./bot-env-block` resolved through the symlink under pi's loader.
- Startup behavior: the forwarder loaded with `--approve`; a missing forwarder target, an untrusted project, and `-ne` behaved as the Fail direction table records.

The live end-to-end run against a real install has not yet been recorded; its checks, to be scored and dated here, are:

1. Agent bash: `echo "${GH_TOKEN:0:4}"` → `ghs_`.
2. `git config --show-scope credential.helper` → bot helper at `command` scope.
3. `GIT_SSH_COMMAND=/usr/bin/false git ls-remote origin HEAD` → succeeds.
4. SKILL Phase 5 membership assertion → prints the repo.
5. Bot test commit → author and committer are the bot, `%G?` is `N`.
6. `as-me` commit → author is the human, and `GH_TOKEN` still reads `ghs_`.
7. Fail-closed: `chmod -x` the installed `bot-env` → the next command does not run; restore the bit.
8. Personal verdict in a non-mapped repo → no `GH_TOKEN`, human author, even when pi was launched with a stale `GH_TOKEN` exported.
9. `!` routing via RPC `bash` → bot env; with `bot-env` broken → the command fails.
10. `powershell` blocked, if the tool can be enabled on macOS.
11. Variant B location load through the real pi loader and forwarder.
12. Failed reload: break the extension, `/reload`, and observe that routing stops.
13. A non-default `shellCommandPrefix` applies to agent bash.

Audit smells specific to this adapter:

- A pi upgrade taken on trust: re-run check 1 after every upgrade; `piShellEnv` in the extension mirrors pi's internal `getShellEnv` (`dist/utils/shell.js`), which is not exported and can change without notice.
- Another extension with a `user_bash` handler that loads earlier: handlers run in extension load and registration order (`docs/extensions.md`), and the startup header lists the loaded resources (`docs/usage.md`) unless `quietStartup` hides it (`docs/settings.md`; `--verbose` overrides).
- The `powershell` tool enabled in `defaultTools` or `--tools`.
- A session that ran `/reload` without re-running the activation check afterwards (see the reload row under Fail direction).
- Identity variables exported in the shell that launches pi: personal verdicts strip them only on routed surfaces, so the non-routed surfaces under Mechanism still see them.
- A committed `.pi/extensions/agent-bot-identity.ts` (machine-local routing config belongs in `.git/info/exclude`, and a teammate without the install who trusts the project would hit the fatal startup error under Fail direction).
- A copy of the extension edited per repo instead of the one-line forwarder (divergent copies drift; the customized values belong in exactly one file).
- `bot-env`, `bot-env-block.ts`, and the extension not reinstalled together: see the SKILL's Phase 3 install note, the one home of that rule.

## Common Mistakes — pi mechanisms

| Mistake | Reality |
| --- | --- |
| Using the bash tool's `spawnHook` for routing | It is synchronous (`dist/core/tools/bash.js` `resolveSpawnContext`); `bot-env` must be awaited, so routing lives in `operations.exec` |
| Adding the command prefix in the `user_bash` operations | `executeBash` already applies it to user commands; adding it again doubles the prefix |
| Precomputing the env in the `user_bash` handler | That binds identity to `event.cwd`; RPC requests run concurrently, so a `switch_session` in between could run the command in another cwd with the first cwd's identity — resolve inside `exec` |
| Treating handler registration as unconditional coverage | The first `user_bash` handler result wins — see Fail direction |
| Assuming a failed `/reload` keeps routing | pi continues without the extension — see Fail direction |
| Expecting a project forwarder to load in a headless run | Without `--approve` or a saved trust decision it is skipped silently — see Verification |
