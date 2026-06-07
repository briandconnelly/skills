# Entry-point patterns → `mcp_config`

The host launches the server by running `mcp_config.command` with `mcp_config.args`.
For a bundled-source uv bundle (Approach A) that is `uv run --directory ${__dirname} …`; the tail depends on how the project starts its server.
`--frozen` runs against the bundled `uv.lock` without re-resolving (see SKILL.md → Release consistency); drop it only if you are not shipping a lockfile.
(The PyPI-pinned Approach B uses `uvx` instead — see the last section.)

## Mapping table

| Pattern | `[project.scripts]` / how it starts | `mcp_config.args` |
| --- | --- | --- |
| Bare script (the only form shown in MCPB examples) | a runnable `src/server.py` | `["run","--directory","${__dirname}","src/server.py"]` |
| Console script | `my-mcp-server = "my_mcp_server.server:mcp.run"` | `["run","--directory","${__dirname}","--frozen","my-mcp-server"]` |
| Console script + optional extra | `my-mcp-server = "my_mcp_server.server:main"` with MCP deps in `[project.optional-dependencies] mcp` | `["run","--directory","${__dirname}","--frozen","--extra","mcp","my-mcp-server"]` |
| Module execution (`__main__.py`) | package has `src/my_mcp_server/__main__.py`; no console script needed, or `--no-dev` would skip the console-script shim | `["run","--directory","${__dirname}","--frozen","--no-dev","python","-m","my_mcp_server"]` |
| CLI subcommand | `my-tool = "my_tool.cli:app"`, server behind `my-tool mcp serve` | `["run","--directory","${__dirname}","--frozen","my-tool","mcp","serve"]` |

The Bare script row matches the MCPB spec example verbatim and omits `--frozen`; add it (as in the other rows) whenever you ship a `uv.lock`.

For Approach A, `command` is `"uv"`.
Set `entry_point` to the module file that defines the server (e.g. `src/my_mcp_server/server.py`, or `src/my_mcp_server/__main__.py` for the module-execution form); the schema requires the field, while `mcp_config.args` is the command the host runs (per the `hello-world-uv` example).

## Mandatory local verification

Only the bare-script form appears in the MCPB spec/examples; the other rows are ordinary uv invocations.
Before writing the manifest, run the exact tail locally from the repo root and confirm the server starts and blocks on stdio:

```bash
# console script
uv run --directory . --frozen my-mcp-server
# console script needing an optional extra
uv run --directory . --frozen --extra mcp my-mcp-server
# module execution
uv run --directory . --frozen --no-dev python -m my_mcp_server
# CLI subcommand
uv run --directory . --frozen my-tool mcp serve
```

Ctrl-C to stop. If it starts cleanly, copy that exact tail into `mcp_config.args` (replacing `.` with `${__dirname}`).

## Notes

- `--extra <group>` installs an `[project.optional-dependencies]` group. Use it whenever `fastmcp`/`mcp` (or other runtime deps) live under an extra rather than `[project].dependencies`.
- `--frozen` installs from the bundled `uv.lock` without updating or re-resolving it, pinning dependency versions for reproducible installs. Use `--locked` to assert the lock is up to date with `pyproject.toml`.
- `--no-dev` is an optional optimization to skip `[dependency-groups]` dev tooling for a leaner install; verify the server still starts with it, since some projects place runtime deps in a dev group.
- Module execution (`python -m my_mcp_server`) runs the package's `__main__.py` directly. It's interchangeable with a console script, but prefer it when you pass `--no-dev` (a console script may be installed as a shim that `--no-dev` skips) or when you want the invocation independent of the console-script name. Point `entry_point` at `src/my_mcp_server/__main__.py`.

## Alternative: pin the published PyPI package

Not preferred when you want the `.mcpb` itself to carry the tagged source (this skill's default); use only if you specifically want the runtime to fetch the published package.
To fetch exactly the published `X.Y.Z` instead of bundling source, set `command` to `"uvx"` and `args` to e.g. `["--from","my-mcp-server[mcp]==1.0.0","my-mcp-server"]`.
Still ship a `pyproject.toml` (uv server type) and point the required `entry_point` at a thin entry file you include, since the schema requires the field even though `uvx` runs the published package.
The bundle then carries no source, requires the package on PyPI, and needs network on first launch.
See SKILL.md → Release consistency for the trade-off.
