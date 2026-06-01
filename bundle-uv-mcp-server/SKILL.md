---
name: bundle-uv-mcp-server
description: Use when packaging, validating, or distributing a uv-managed Python MCP server (new or existing) as an MCPB bundle (.mcpb) for Claude Desktop or another MCPB host. Triggers include creating an MCPB manifest.json, setting server.type to uv, bundling a uv + pyproject.toml stdio server, running mcpb pack or mcpb validate, preparing one-click install, and exposing API tokens or install-time settings through user_config. Scoped to the MCPB packaging step (manifest_version 0.4+); not for authoring the server's tools or handlers, designing/reviewing/auditing MCP tool/resource/prompt schemas, Node servers, or cloud-only remote HTTP servers.
---

# Bundle a uv MCP Server as MCPB

## Overview

MCPB packages a local MCP server as a single `.mcpb` file (a zip) that installs into Claude Desktop in one click.
For a uv project the modern path is `server.type: "uv"`: the bundle ships your `manifest.json`, `pyproject.toml`, `uv.lock`, and `src/`, and the host runs `uv run --directory ${__dirname} …` to fetch Python and resolve dependencies at install time.
This keeps the bundle tiny and avoids the legacy `python` path's need to vendor compiled dependencies.

## When to use

- Distributing a uv + `pyproject.toml` Python MCP server that runs locally over stdio.
- Producing a `.mcpb` for one-click install in Claude Desktop / an MCPB host.

## When not to use

- Cloud-only servers with no local execution — ship a remote HTTP server instead.
- Node servers, or Python projects that are not uv/`pyproject.toml` based.
- The legacy vendored `server.type: "python"` path (dependencies in `server/lib`) — out of scope; see the [mcpb repo](https://github.com/modelcontextprotocol/mcpb/) `examples/file-manager-python`.

## Prerequisites

- The MCPB CLI: `npm install -g @anthropic-ai/mcpb` (needs Node/npm).
- A working uv project where `uv run` already starts the server.
- `uv` must be on PATH for the host (the bundle's `command` is `uv`).

## Procedure

1. Read `pyproject.toml`. Note `[project]` `name`, `version`, `description`, `requires-python`, and `[project.scripts]`.
2. Determine the launch invocation and **verify it locally** before writing the manifest:
   `uv run --directory <repo> --frozen [--extra <group>] <console-script | command subcommand>`.
   The server should start and wait on stdio. `--frozen` runs against the bundled `uv.lock` without re-resolving. See [references/entry-point-patterns.md](references/entry-point-patterns.md) for mapping `[project.scripts]` to `mcp_config.args`.
3. Write `manifest.json` at the repo root from [references/manifest-template.json](references/manifest-template.json):
   set `manifest_version` `"0.4"`; `name`/`version`/`description` from `[project]`; `author.name`; `server.type` `"uv"`; `server.entry_point` (the server module file, e.g. `src/<pkg>/server.py`); `server.mcp_config` (the verified invocation from step 2); `compatibility.runtimes.python` from `requires-python`, and `compatibility.platforms` trimmed to the OSes you actually test (the template lists all three).
4. For every config/secret env var the server reads, add a `user_config` entry and map it in `mcp_config.env`, e.g. `"MY_API_TOKEN": "${user_config.api_token}"`. Mark secrets `sensitive: true`.
5. Add a `.mcpbignore` so dev cruft stays out of the zip (see Quick reference).
6. `mcpb validate .` → `mcpb pack .`. Unzip the result and confirm it contains `manifest.json`, `pyproject.toml`, `uv.lock`, and `src/` but no `.venv/` or caches. For local signing use `mcpb sign --self-signed <bundle.mcpb>`.

## Release consistency

To ship the same code for `1.0.0` as the `1.0.0` git tag and PyPI release: pack from a clean checkout at the release tag, include `uv.lock`, and confirm the manifest's `version` == `[project].version` == the tag.
The bundle runs `--frozen` (use the lockfile as-is); run `uv run --locked …` once before packing to assert the lock still matches `pyproject.toml`.
To pin the published PyPI package instead of bundling source, see the alternative in [references/entry-point-patterns.md](references/entry-point-patterns.md).

## Quick reference

Manifest field ← source:

| Manifest field | Source |
| --- | --- |
| `name`, `version`, `description` | `pyproject.toml` `[project]` |
| `compatibility.runtimes.python` | `[project]` `requires-python` |
| `server.entry_point` | the server module file |
| `server.mcp_config.args` | `uv run --directory ${__dirname} --frozen …`, derived from `[project.scripts]` (see references) |
| `user_config.*` + `mcp_config.env` | env vars the server reads |

`.mcpbignore` (one pattern per line; `.git` is excluded automatically):

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
tests/
```

CLI: `mcpb init` (interactive manifest), `mcpb validate .`, `mcpb pack .`, `mcpb sign`, `mcpb verify`, `mcpb info`.

Optional manifest fields (add as needed): `icon` (ship the PNG in the bundle too, or omit the line), `long_description`, `homepage`, `documentation`, `support`, `privacy_policies`; `tools`/`prompts` arrays or the `tools_generated`/`prompts_generated` booleans; `mcp_config.platform_overrides` for per-OS command/args/env. Beyond `string`, `user_config` entries can be `number` (`min`/`max`), `boolean`, or `directory`/`file` (`multiple`).

## Caveats

- The MCPB examples only demonstrate the bare-script form `args: ["run","--directory","${__dirname}","src/server.py"]`.
  The console-script, CLI-subcommand, and `--extra <group>` forms this skill uses are standard **uv** invocations, not shapes shown in the MCPB spec — so step 2's local verification is mandatory, not optional.
- The v0.4 schema requires both `entry_point` and `mcp_config` under `server`; include both even though MANIFEST.md prose calls `mcp_config` optional.
- `uv.lock` and `--frozen` are not required by the MCPB spec; this skill recommends them for release reproducibility (see Release consistency). `--frozen` installs from the lockfile without updating or re-resolving it; `--locked` instead asserts the lock is up to date with `pyproject.toml`.

## Common mistakes

- Logging to stdout: stdio transport reserves stdout for JSON-RPC, so the server must log to stderr (general MCP practice, not MCPB-specific).
- Choosing `server.type: "python"` and trying to vendor pydantic/compiled deps — use the uv runtime instead.
- Omitting `--extra <group>` when MCP deps live in `[project.optional-dependencies]` — the server then fails to import at install time.
- Hardcoding API tokens instead of exposing them via `user_config` + `mcp_config.env`.
- Assuming the host can find `uv`: GUI hosts like Claude Desktop do not inherit your shell `PATH`, so the user may need `uv` on the system PATH (or an absolute `command`) for the bundle to launch.
