# A1 with-skill, 2026-09-29

Prompt: "How do I set a custom system prompt in Pi?"
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) CLI flags | pass | item 1, `docs/cli.md#prompts-and-process` |
| (b) both scopes, precedence | pass | item 2, precedence and trust bullets |
| (c) before_agent_start | pass | item 4 |
| (d) when to use each layer | pass | "Which to use" paragraph |
| (e) anchored citations and version | pass | header states 0.99.1; every item cites an anchor |

## Transcript (the agent's final report, verbatim)

**Answer (Pi 0.99.1 installed; skill verified against 0.99.1, matches)**

Pi has several ways to set a custom system prompt. Each one either replaces the default prompt or appends to it.

1. **CLI flags, for a single run** (docs/cli.md#prompts-and-process)
   - `--system-prompt <text|path>` replaces the default system prompt. It takes literal text or the path of an existing file.
   - `--append-system-prompt <text|path>` adds text or a file to the prompt. It can be repeated.
   - Example from the docs: `pi --append-system-prompt ./instructions.md`.

2. **Saved files** (docs/configuration.md#agent-directory and docs/configuration.md#project-pi-directory)
   - Replace the default prompt with `<agent-dir>/SYSTEM.md` (user level) or `.pi/SYSTEM.md` (project).
   - Add to the default prompt with `<agent-dir>/APPEND_SYSTEM.md` (user level) or `.pi/APPEND_SYSTEM.md` (project).
   - **Precedence:** for `SYSTEM.md` and `APPEND_SYSTEM.md`, the trusted project file takes precedence over the agent-directory file of the same name. The two are not combined.
   - **Project trust:** `.pi/SYSTEM.md` and `.pi/APPEND_SYSTEM.md` are among the resources protected by project trust (docs/security.md#understand-project-trust). The project file only takes effect when the project is trusted.

3. **Context files, when you only need extra instructions** (docs/configuration.md#context-files, docs/how-pi-works.md#context)
   - Pi builds the system prompt from its base instructions plus discovered context files (`AGENTS.md`, `CLAUDE.md`, `AGENTS.override.md`). These load from the agent directory, the working directory, and its parents.
   - This adds to the prompt and does not replace Pi's base instructions.

4. **Extensions, for dynamic changes** (docs/extensions.md#events-and-concurrency)
   - The `before_agent_start` event exposes the current prompt and `systemPromptOptions`.
   - The docs prefer changing prompt sections, tools, or guidelines. Returning `systemPrompt`, or setting `forceSystemPrompt`, replaces the whole prompt for that run.
   - Bundled examples: `examples/extensions/pirate.ts` (modifies the prompt in `before_agent_start`) and `examples/extensions/claude-rules.ts`.

5. **SDK** (docs/sdk.md#examples)
   - `examples/sdk/03-custom-prompt.ts` shows how to replace or append to the system prompt.
   - `session.systemPrompt` is read-only.

**Which to use:** use `--append-system-prompt` or `APPEND_SYSTEM.md` to add rules. Use `--system-prompt` or `SYSTEM.md` only if you want to discard Pi's defaults. Use an extension if the prompt has to change per run.

I did not run `pi` itself. This was a docs question, so no gate or build step applied.

**Commands run** (each with `PI_CODING_AGENT_DIR` exported to the a1-with-skill `pi-agent` directory, from the a1-with-skill directory):
1. `pi_docs.py where` printed:
   - `Pi 0.99.1 at /opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`
   - `Skill verified against 0.99.1 (matches installed)`
2. `pi_docs.py index` printed the full page and section list. I picked configuration.md, cli.md, extensions.md, sdk.md and how-pi-works.md from it.
3. A `sed` on `configuration.md` and `cli.md`, with a `grep` for `=====`. It exited 1 because zsh treated `=====` as a command. It still printed the "Context files" section.
4. `grep -n -i "system prompt|systemPrompt|SYSTEM.md|before_agent_start"` over `docs/*.md`, plus `pi_docs.py grep "system prompt"`. These found the hits listed above, including cli.md:228-230, configuration.md:19-20 and 32-39, extensions.md:103, and the examples.
5. `sed -n 222,232p cli.md` and `sed -n 10,40p configuration.md` printed the exact flag text and the configuration tables.

I also read `/Users/bdc/projects/skills/pi-coding-agent/SKILL.md` with the Read tool.
