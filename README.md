# Skills

Opinionated skills for designing systems that AI agents will invoke directly.

Each skill ships as a `SKILL.md` plus reference files.
Agent harnesses load a skill when its description matches the task at hand.

## Available skills

| Skill | What it covers |
| --- | --- |
| [agent-friendly-cli](agent-friendly-cli/) | Best practices for designing CLIs that AI agents invoke directly. |
| [agent-friendly-mcp](agent-friendly-mcp/) | Best practices for designing MCP (Model Context Protocol) servers that AI agents invoke directly. |

## Installation

Pick whichever tool fits your agent and host — both read this repo's structure directly.

### `gh skill` (GitHub CLI v2.90+)

```bash
# install every skill in this repo for Claude Code at user scope
gh skill install briandconnelly/skills --agent claude-code --scope user

# interactive picker (choose a single skill, agent, and scope)
gh skill install briandconnelly/skills
```

See `gh skill install --help` for the full flag set.
`--agent` covers Claude Code, Cursor, Copilot, Codex, Gemini CLI, and others; `--scope` covers user vs project.

### `npx skills` (Vercel Labs)

```bash
# list available skills in this repo
npx skills add briandconnelly/skills --list

# install a specific skill
npx skills add briandconnelly/skills --skill agent-friendly-mcp

# target multiple agents at once
npx skills add briandconnelly/skills --skill agent-friendly-mcp -a claude-code -a opencode
```

### Manual

```bash
git clone https://github.com/briandconnelly/skills.git
cp -r skills/agent-friendly-mcp ~/.claude/skills/
```

In Claude Code, run `/reload-plugins` after a manual install to pick up the new skill without restarting.
