# Claude runner adapter

The Claude adapter is the only currently supported runner.

## Prerequisites

- CA1: The adapter requires Claude Code 2.1.251 or newer.
- CA2: The supported review levels are `low`, `medium`, `high`, `xhigh`, and `max`.

## Policy isolation

- CA3: `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `.claude/`, and `.mcp.json` are reviewer-policy paths restored from the base commit.
- CA4: `.claude/settings.json`, `.claude/settings.local.json`, and `.mcp.json` are removed after restoration because they can register hooks, permissions, or MCP servers.
- CA5: `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, Claude skill instructions, and Claude agent definitions are passive context listed in the policy manifest.

## Child controls

- CA6: The child runs through `claude -p` with restricted mode, JSON output, no session persistence, noninteractive permission handling, and strict MCP configuration.
- CA7: Claude tools that write, execute shell commands, access the network, or start subagents are denied.
- CA8: The exact child tool set is `Read`, `Grep`, and `Glob`, and file access is confined to the clone and its private evidence directory.
- CA9: `REVIEW_PR_BUDGET`, `REVIEW_PR_MAX_TURNS`, and an optional review level map to Claude's budget, turn, and effort flags.

## Output mapping

- CA10: Claude's result text, error state, duration, USD cost, subtype, errors, and permission denials map to the normalized runner envelope.

## Verification

Run `bash review-pr/tests/adapter-contract-test.sh` for the offline adapter interface gate.

Run `bash review-pr/tests/hostile-fixture-test.sh` for the runner-backed tool and policy isolation gate.

Run `bash review-pr/tests/lens-fixture-test.sh` for the runner-backed review-quality gate.

Run `bash review-pr/tests/checkout-pr-test.sh` for the authenticated GitHub checkout gate.
