# 001 — the credential helper stays host-wide in every adapter

Date: 2026-10-10. Status: accepted. Context: issue #141, PR #180, review 2026-10-09 finding 7, plan critique 2026-10-09.

## Decision

Every adapter installs the bot credential helper for all of `https://github.com`, after a host-wide reset, under a bot identity.
Issue #141's proposal to scope the helper to each mapped account is declined.
The rule itself lives in the Phase 4 contract of [SKILL.md](../SKILL.md); this file records the decision behind it and what would reopen it.

## Why

Scoping restores the personal helper for every unmapped github.com HTTPS destination: an https fork upstream, an ad-hoc `git push https://github.com/other/x.git`, a mixed-case `https://github.com/Acme/x.git` remote, or an HTTPS remote in another organisation's repository reached by Claude Code's session-static Variant A environment.
Each of those would push with the personal credential under the bot's authorship, silently, where today each fails loudly at the installation boundary.
That silent outcome is the failure this skill exists to prevent, and the loud one is the documented "enroll me" signal.

#141's incident — an MCP server installed from a private repository failing to start — is a consequence of the session-wide environment of Claude Code's Variant A, which the harness process and its MCP children inherit.
The environment of Claude Code's Variant B exists only inside an agent Bash command where `bot-env` returns a bot verdict (a mapped remote, or one of the ambiguous cases the Claude Code adapter's decision table resolves to bot); MCP servers and other harness children never see it, so Variant B avoids the incident without weakening the guarantee.
The same holds for the OpenCode adapter, whose hook fires per shell command.

## Consequences

Inside an agent command in a mapped repository, every github.com HTTPS request — including a dependency install from another organisation's private repository — is answered with the bot credential and fails outside the installation list; the workaround is a personal terminal.
Users who launch MCP servers or installers from private repositories under Claude Code should prefer Variant B over Variant A.
#142's current-code diagnosis is wrong: `bot-token` has no cwd-based installation lookup; its uncontrolled-cwd point is kept as a hazard note only.

## What would reopen this

A git credential mechanism that can fall through to the personal helper for reads while keeping the bot helper for `receive-pack`; git cannot express that today.
