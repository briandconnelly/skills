# Trigger Cases for pi-coding-agent

Positive prompts that must trigger this skill and negative prompts that must not, checked against the frontmatter `description` in `SKILL.md`.
Run each prompt in a fresh subagent given the frontmatter of every skill in this repository and the prompt, asked which skill (if any) it would load; do not name the expected skill.
Store the results in `tests/runs/YYYY-MM-DD-trigger.md`.

## Positive cases (must trigger)

| Prompt | Expected | Reason |
| --- | --- | --- |
| "How do I give Pi a different system prompt just for this repo?" | trigger | A Pi feature question. |
| "What's the difference between a skill and a prompt template in Pi?" | trigger | A Pi feature question naming two Pi surfaces. |
| "My extension in `.pi/extensions/` isn't loading — why?" | trigger | A `.pi/` path. |
| "I'm calling `pi.registerTool` — how do I keep the tool out of the model's tool list but callable from codemode?" | trigger | A `pi.*` extension API. |
| "This file imports `@earendil-works/pi-ai`; how do I register my company's model gateway as a provider?" | trigger | An `@earendil-works/*` import. |
| "Build me a pi.dev extension that shows the git branch in the footer." | trigger | Building for Pi, named by its site. |

## Negative cases (must not trigger)

| Prompt | Expected | Reason |
| --- | --- | --- |
| "How do I set up a Raspberry Pi 5 as a headless server?" | don't-trigger | Raspberry Pi is excluded by name. |
| "Compute π to 50 digits in Python." | don't-trigger | The constant π is excluded by name. |
| "Write a Claude Code hook that blocks `rm -rf`." | don't-trigger | Claude Code extensions are excluded. |
| "Add a custom tool to my Codex CLI setup." | don't-trigger | Codex extensions are excluded. |
| "Review the tool descriptions of my MCP server so agents call the right tool." | don't-trigger | Generic MCP server design belongs to `agent-friendly-mcp`. |
