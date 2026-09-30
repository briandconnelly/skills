# A3 confirmation: no built-in spending limit in Pi 0.99.1

Date: 2026-09-29
Pi: 0.99.1 at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`
Candidate feature: a built-in way to stop a session once it has cost a set amount.

## First reader (plan executor)

Read in full: `docs/settings.md`, `docs/usage.md`, `docs/sessions.md`, `docs/models.md`, `docs/cli.md`, and the "Events and concurrency" and "State" sections of `docs/extensions.md`.
Finding: absent.
Cost is displayed (the footer, and `/session` in `usage.md` and `sessions.md`), and the nearest settings (`thinkingBudgets`, `cacheWarming`, `retry.*`, `compaction.*` in `settings.md`) bound tokens, retries, or context, not spend.

## Second reader (fresh subagent, prompt as in the plan)

Read in full: all 39 pages under `docs/` plus `docs.json`, without relying on search.
Finding: absent ("None of the pages I read documents a setting, flag, or command that stops a session once it has cost a set amount").
Near-misses it listed: cost display (`usage.md`, `sessions.md`, `slash-commands.md`), `get_session_stats` returning `cost` (`rpc-commands.md`), `usage.cost.total` on messages (`message-types.md`), `warnings.anthropicExtraUsage` (warns only, `settings.md`), and stop mechanisms an extension could combine into a cap (`abort`, `ctx.shutdown()`, `turn_end`/`agent_before_settle` continuation in `extensions.md`).

## Verdict

Both readers agree the feature is absent from the installed version; A3 keeps its prompt.
A correct answer says it could not find the feature, names pages checked, and may point out that an extension could build one from the documented pieces.
