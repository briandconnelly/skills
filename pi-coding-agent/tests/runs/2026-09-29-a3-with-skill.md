# A3 with-skill, 2026-09-29

Prompt: "How do I set a spending limit in Pi so it stops a session once it has cost $5?"
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) could not find in installed docs | pass | "I could not find a spending limit or cost cap in the installed v0.99.1 docs" |
| (b) names pages checked | pass | lists seven pages |
| (c) does not claim a built-in limit | pass | whole answer |
| (d) labels outside material | pass | RPC and extension routes labelled "my inference" / "not a documented feature" |

## Transcript (the agent's final report, verbatim)

## Final answer to the user

Installed Pi is v0.99.1. This skill was verified against 0.99.1, so the versions match.

**I could not find a spending limit or cost cap in the installed v0.99.1 docs.** I checked `docs/settings.md` (all sections), `docs/cli.md`, `docs/usage.md`, `docs/sessions.md`, `docs/models.md`, `docs/extensions.md` and `docs/rpc-commands.md`. I also grepped every docs page and the bundled example headers. Nothing sets a dollar cap or stops a session at a cost. I did not confirm it is unsupported by running Pi. I did not consult the online docs or the changelog for a solution.

What the installed docs do cover:
- **Watching cost, not capping it.** The footer shows accumulated usage and cost (`docs/usage.md#use-pi-in-the-terminal`). `/session` shows token usage and cost (`docs/usage.md#continue-or-start-over`, `docs/sessions.md#continue-or-switch-sessions`). Cost includes tool-reported usage, compaction and branch-summary calls.
- **Reading cost from a script.** In RPC mode, `get_session_stats` returns tokens and cost (`docs/rpc-commands.md#get_session_stats`). A controlling program could poll it and send `abort`. That is my inference; the docs do not describe a cap.
- **Building your own cap as an extension (a possible route, not a documented feature).** `docs/extensions.md#events-and-concurrency` says `message_end` and `turn_end` events exist. `turn_end` handlers can end or continue a run, and `ExtensionContext` exposes an abort signal and context usage (`docs/extensions.md#follow-the-extension-contracts`). I did not verify that an extension can read session cost or stop a session on it. I did not build or gate one.
- **Settings that look related but are not cost limits.** `thinkingBudgets`, `codemode.inlineBudget` and `compaction.modelOverrides` are token budgets. `retry.provider.*` covers retries only.
- **Provider-side limits are out of scope for Pi's docs.** A spend cap set on the provider's account is outside what the installed docs cover.

I did not make a Pi feature request or build anything, so no gate was run.

## Commands run (all from `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/a3-with-skill`, with `PI_CODING_AGENT_DIR` exported to `.../a3-with-skill/pi-agent`)

1. `uv run <skill-dir>/scripts/pi_docs.py where` printed: "Pi 0.99.1 at /opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent ... Skill verified against 0.99.1 (matches installed)".
2. `pi_docs.py index` printed the full page and section list, including `settings.md`, `cli.md`, `usage.md`, `extensions.md` and `rpc-commands.md`.
3. `pi_docs.py grep budget | "spending limit" | "max cost" | cost` results:
   - `budget` matched only token budgets: `thinkingBudgets`, `codemode.inlineBudget` and compaction.
   - `spending limit` and `max cost` returned no matches.
   - `cost` matched reporting and display only: the footer, `/session`, `get_session_stats`, and session-format usage entries.
4. `pi_docs.py grep max-turns | maxTurns | "max turns" | "usage limit" | '$5' | quota` returned no matches, except `quota`. That matched only `docs/settings.md` on `retry.provider.maxRetries` and quota errors. The first run of this batch exited 1 from a shell quoting error on `==== changelog`, after the greps had already run.
5. `pi_docs.py changelog budget | "cost limit" | spend | maxCost` printed budget entries (token budgets, codemode) and `Ctrl+Z` suspend entries for `spend`. There were no lines for `cost limit` or `maxCost`.
6. `pi_docs.py grep turn_end` and `grep "ctx.abort"` were in a batch that ended with a shell error (`= not found`) from a quoting mistake, so I did not see their output. I reached the extension facts by reading `docs/extensions.md` in the next command.
7. `sed` and `grep -n -i limit` on `docs/settings.md` and `docs/cli.md` found only the codemode, retry and `maxRetryDelayMs` limits.
8. `grep -n -i -E "abort|turn_end|message_end|usage" docs/extensions.md` found the `message_end` and `turn_end` handler notes, the nested-model-call `usage` note, and the `ExtensionContext` abort signal and context usage.

I ran the greps against the installed docs directory. I did not run the negative-result known-positive check on the grep tool separately. The `cost` grep did surface known positives, so the tool does work.
