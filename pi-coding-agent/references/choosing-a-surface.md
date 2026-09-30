# Choosing a surface where Pi's docs are silent

Pi's own chooser, docs/quickstart.md#choose-how-to-customize-pi, is the normative cross-surface chooser; start there and do not reproduce its mapping.
Pi's pages also carry in-page choosers (docs/extensions.md#choose-an-integration-point, docs/models.md#choose-a-connection, docs/custom-provider.md#choose-the-smallest-integration, docs/tui.md#choose-an-integration-point).
This file covers only choices no installed page makes.
MAINTAINING.md says when each entry is re-checked; delete an entry once Pi's docs make its choice, and point to that page instead.

## Extension tool or MCP server

Pi supports both: extension tools (docs/extensions.md#tools) and MCP servers configured in `mcp.json` or registered by an extension (docs/mcp.md#configure-servers, docs/mcp.md#servers-from-extensions).
No installed page says when to prefer one.

- Choose an MCP server when the capability should also work in other harnesses, or already exists as an MCP server.
- Choose an extension tool when the capability needs Pi's session, UI, or event APIs.

## Adding to or replacing the system prompt

Five layers change what the model is told: context files such as `AGENTS.md`, `APPEND_SYSTEM.md`, `SYSTEM.md`, the `--system-prompt`/`--append-system-prompt` flags, and an extension's `before_agent_start` handler.
Their locations and precedence live in docs/configuration.md#context-files, docs/configuration.md#project-pi-directory, docs/cli.md#prompts-and-process, and docs/extensions.md#events-and-concurrency; read them there.
No installed page chooses among them.

- Choose a context file for instructions about a folder's work that any agent may read.
- Choose `APPEND_SYSTEM.md` to add Pi-specific instructions while keeping Pi's own prompt.
- Choose `SYSTEM.md` only to replace Pi's prompt entirely.
- Choose a flag for one invocation, such as a script or a one-off run.
- Choose a `before_agent_start` handler only when the prompt must change from turn to turn or depend on session state.

## User or project scope

Every surface can live at user level (the agent directory) or project level (`.pi/`) (docs/configuration.md#agent-directory, docs/configuration.md#project-pi-directory).
Project resources are subject to project trust (docs/security.md#project-trust).
Choose project scope for resources a repository's collaborators should share, and user scope for personal ones.
