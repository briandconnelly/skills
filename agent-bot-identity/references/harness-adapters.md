# Harness Adapters — Mechanism Detail and Contract

## Why a hook and not a PATH-shimmed `gh` (Claude Code)

The obvious approach — drop a `gh` wrapper on `PATH` via a shell rc file — fails under Claude Code and wastes hours.
Claude Code builds a *shell snapshot* at session start by sourcing `$HOME/.zshrc` from a **non-login** shell, then **freezes `PATH`** into that snapshot and replays it for every Bash command.

Consequences that defeat the rc-file approach:

- `.zprofile` is never sourced (non-login shell).
- `ZDOTDIR` is ignored — the snapshot hardcodes `$HOME/.zshrc`, not `$ZDOTDIR/.zshrc`.
- Even a correctly-placed `PATH` prepend is frozen at snapshot time, before the per-project `env` (and any marker it sets) is applied.

`CLAUDE_ENV_FILE` is the supported escape hatch: Claude Code provides it to `SessionStart`/`CwdChanged`/`Setup`/`FileChanged` hooks and sources the file's contents before every Bash command, *after* the snapshot — so an `export GH_TOKEN=...` there reliably reaches `gh`.
This per-command evaluation is now documented in the Claude Code hooks reference ("Persist environment variables"); it was originally verified empirically on Claude Code 2.1.172 with an env file exporting `"$PWD"`, which matched each command's own `pwd`.

Only fall back to a PATH shim if the harness sources a predictable rc file without freezing `PATH`.

## Adapter contract for other harnesses

Phases 1–3's App, token, and credential-helper layers are harness-neutral; the Claude Code glue is only the activation layer (`session-env.sh` in Variant A, `bot-env-hook.sh` plus the `bot-env` guard in Variant B).
An adapter for another local agent (e.g. Codex) must supply Phase 4's routing, without editing shell dotfiles:

- Per-repo activation: explicit opt-in, or a gated automatic equivalent keyed on a repo-intrinsic signal such as the org remote.
- The static git identity env (`GIT_AUTHOR_*`/`GIT_COMMITTER_*`).
- Command-scope `GIT_CONFIG_*` (credential-helper reset plus bot helper, org-scoped `insteadOf`, `commit.gpgsign false`).
- A dynamic `GH_TOKEN` re-minted across hour-plus sessions.
- A fail-closed substitute when minting fails (a non-empty invalid token, never an empty value).

This skill ships only the Claude Code adapter.
If a harness lacks one of these capabilities, treat its support as pending rather than approximating with partial steps — a half-wired adapter fails open to the personal identity.
