# 006 — Server `instructions` delivered as a prefix

Decided 2026-09-26.
Triggered by issue #184, which reported that Claude Code delivers only a fixed-length prefix of a server's `instructions` string and proposed rules for laying the string out around that cut.

## Question

`[2.instructions-advisory]` covered a client that never surfaces `instructions`.
It did not cover a client that surfaces the head and drops the rest, which leaves the agent holding a plausible partial contract.
Which rules does that failure need, and should the skill state a length budget?

## Evidence

These are dated observations of client behavior, not protocol facts.
Each figure can change with a client release, and at least one is configurable per session.

| Client | Observation | Source |
| --- | --- | --- |
| Claude Code | First 2,048 characters of a 13.9 KB string reached the model, followed by a client-rendered `… [truncated]` marker; earlier readings on the same client landed near 2,041 bytes and 2,058 characters. | Issue #184, citing runpod/snowpod#463, #437, #299 (2026-09-26 and earlier) |
| Claude Code 2.1.283 | The amicus 0.7.0 server's instructions reached the model through character 2,046, followed by `… [truncated]`; characters 2,047–2,048 are `\n\n`, consistent with a 2,048-character cut. That prefix holds two em dashes, so it is 2,052 UTF-8 bytes, and the visible text runs past byte 2,048: the cut is in characters, not bytes. `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` was unset. | This PR's session, 2026-09-26, comparing the text the model received against the server's `manifest_snapshot.all.json` fixture |
| Claude Code (changelog) | 2.1.280 "Added `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` to change the 2,048-character cap on MCP tool descriptions and server instructions for every MCP server in the session." The cap is a documented default the user can raise or lower, so a server cannot know the prefix a given Claude Code session delivers. | <https://code.claude.com/docs/en/changelog.md>, read 2026-09-26 |
| Codex CLI 0.157.1 | An 11,682-character ASCII string reached the model whole: a fresh run repeated a sentinel starting at offset 11,661. This is a lower bound for that CLI path, not a maximum, and says nothing about other Codex surfaces. | The maintainer's run, 2026-09-26, reported while this PR was drafted |
| Codex (docs) | "Keep the first 512 characters self-contained so the most important guidance is available when Codex is deciding how to use the server." No truncation limit is documented. | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> and <https://developers.openai.com/plugins/build/mcp-server>, read 2026-09-26 |

Issue #184 also reported a cold-start observation (runpod/snowpod#462): with a truncation self-test at the head, the agent followed the rules inside the prefix and went straight to the resource it needed, without acting on the self-test.

## Decision

Add two rules and extend one.

- `[2.instructions-advisory]` names the prefix case alongside the never-surfaced case, so both route to the same "never the sole carrier" requirement.
- `[2.instructions-prefix]` owns the layout: order by what the agent needs before its first call, keep the binding contract inside the shortest prefix measured on the clients a server targets, and tie any length test to a measurement.
- `[2.truncation-signal]` owns the self-check the agent can run on its own copy, and states that it is a floor, per the cold-start observation above.
- `review-workflow.md` gains a measurement step in the cold-start probe and a Major example for binding rules past a measured prefix.

The rules state no number.
The two measured clients differ by at least 5.7× on the paths measured, Claude Code's figure is a user-adjustable default, the documented Codex figure is guidance rather than a limit, and a skill meant for many clients would be wrong for most of them if it bound one client's figure.
The figures live in this record so a reader can see where a budget came from and when it was last measured.

## Rejected

A fixed 2,048-character budget in the rule, as issue #184 proposed.
It is one client's current behavior; applied to Codex CLI it would cut a server's usable head to under a fifth of what that path delivered, and it is not stable even within Claude Code, where a session can change it.

A separate rule for digests over glossaries (issue #184's proposed `2.instructions-digest-not-glossary`).
It is one consequence of ordering by what the agent needs first, so it lives as a sentence in `[2.instructions-prefix]` rather than as a third rule with its own id.

Measuring in both characters and UTF-8 bytes until the unit is known, as the issue proposed.
The Claude Code measurement above settles the unit for that client, and the rule already asks for the unit each target client cuts in, which covers clients whose unit is still unknown.
