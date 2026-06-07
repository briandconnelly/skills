---
name: uv-python-baseline
description: >-
  Use when setting up, standardizing, or auditing the engineering baseline of a uv-managed Python project — especially a FastMCP server — covering packaging layout, ruff lint/format config, ty type checking, pytest + coverage gating, live/network-test isolation, prek pre-commit hooks, and GitHub Actions CI with OIDC publishing.
  Triggers include adding a coverage threshold, choosing a build backend or Python floor, wiring ruff/ty/prek, setting up a test matrix or trusted-publishing release, or bringing a repo in line with sibling projects' conventions.
  Scoped to repo-level tooling and CI — not MCP tool/resource/contract design (see agent-friendly-mcp) or MCPB packaging (see bundle-uv-mcp-server).
---

# uv Python Project Baseline

The shared engineering baseline for uv-managed Python projects (and the FastMCP servers built on them): how the repo is packaged, linted, type-checked, tested, hooked, and shipped.
This is the layer *beneath* the MCP contract — pair it with [agent-friendly-mcp](../agent-friendly-mcp/) for tool/resource/error-envelope design and [bundle-uv-mcp-server](../bundle-uv-mcp-server/) for `.mcpb` distribution.

Concrete, copy-pasteable config blocks live in [references/config-blocks.md](references/config-blocks.md).
This file is the standard and the rationale; reach for the reference when writing the actual files.

## Core standard

- **uv for everything.** `uv.lock` is committed; deps go in `pyproject.toml`, never `requirements.txt`.
  Dev tools live in a PEP 735 `[dependency-groups] dev`, not `[project.optional-dependencies]`.
- **One way to do each thing across repos.** When a convention is unsettled, survey the siblings, pick the strongest, and apply it everywhere — don't let each repo drift its own way.
- **The contract is enforced, not documented.** Lint, types, coverage, and lock freshness are gates that fail the build, not aspirations in a README.

## Packaging & layout

- **Build backend: `uv_build`** (Astral's native backend) — `requires = ["uv_build>=0.11,<0.12"]`, `build-backend = "uv_build"`, with `[tool.uv] package = true`.
  Consistent with the all-uv toolchain.
- **src layout** (`src/<pkg>/`), and **ship `py.typed`** so consumers get your types.
- **Python floor `>=3.11`** — broad enough for most consumers, modern enough for `StrEnum` and `X | Y` unions.
  Set `target-version = "py311"` in ruff and matrix-test 3.11–3.13.
- Single console entry point in `[project.scripts]`.
- For servers with a CLI + MCP surface, keep a dependency-inverted **`core/`** that never imports FastMCP, with `mcp/` and `cli/` as thin adapters over it (the cwms-tools pattern).

## Lint & format (ruff)

Adopt a **broad, opinionated rule set** rather than ruff defaults (defaults are only `E,F` — no import sorting, no bugbear, no pyupgrade):

```
select = ["E","F","W","I","B","UP","SIM","PIE","RUF","PL","PT","TID","TC","ARG","PTH"]
```

- `line-length = 100`, `target-version = "py311"`, `src = ["src","tests"]`.
- Justify global ignores inline (e.g. `PLR0913` for API wrappers, `PLR2004` for magic values in tests).
- Relax noisy rules under `tests/**` via `[tool.ruff.lint.per-file-ignores]` with a comment explaining why.
- Run **both** `ruff check` and `ruff format --check` in CI — the formatter is a separate gate.

## Type checking (ty)

- Use **ty** (Astral).
  Config: `[tool.ty.src] include = ["src","tests"]`; soften third-party noise narrowly (e.g. `unresolved-import = "warn"`), not globally.
- **Enforce in BOTH pre-commit and CI.** Pre-commit-only is a hole: a contributor without hooks (or a bot PR) merges type regressions.
  While ty is pre-1.0, CI may run it `continue-on-error: true` — but it must be present so the signal is visible, and tightened to blocking once stable.

## Testing

- **pytest** with `asyncio_mode = "auto"`, `testpaths = ["tests"]`, and `addopts` including **`--strict-markers --strict-config`** so typos and stray markers fail fast.
- **Coverage gate: `fail_under = 95` AND `branch = true`.** Threshold from the strongest sibling, branch coverage for real rigor.
  `source = ["src/<pkg>"]`, `show_missing = true`.
  Put `--cov` in `addopts` so the gate rides every `uv run pytest`; document that `--no-cov` bypasses it for single-file iteration.
- **Isolate live/network tests behind a marker** (the triple-gate pattern):
  1. register the marker (`markers = ["integration: ...", ...]`);
  2. exclude by default in `addopts` (`-m 'not integration'`);
  3. auto-skip when credentials are absent (`skipif` or a `pytest_collection_modifyitems` hook).
  Opt in with `uv run pytest -m integration --no-cov`, and keep live tests out of the sdist via `[tool.uv.build-backend] source-exclude`.
  This keeps the offline suite deterministic and the coverage gate honest, and stops the live CI job from tripping the gate.
- Prefer **mocked unit tests** for the offline suite (mock the upstream client / `httpx` / `requests`); reserve real calls for the opt-in marker.
- **Fingerprint snapshot test** (for servers exposing a capability fingerprint): assert the fingerprint's *shape* and *invariants* — adding a tool/error-code/resource MUST move it, editing internal-only code MUST NOT — rather than pinning a brittle literal digest.

## Pre-commit (prek)

Use **prek** (`prek.toml`), with `default_install_hook_types = ["pre-commit","pre-push"]`:

- builtins: `trailing-whitespace`, `end-of-file-fixer`, `mixed-line-ending`, `check-{toml,yaml,json}`, `check-merge-conflict`, `check-added-large-files`, `detect-private-key`.
  **Exclude `^\.github/workflows/`** from the whitespace fixers so workflow files stay byte-stable for OIDC.
- `astral-sh/uv-pre-commit` → `uv-lock` (keeps the lock synced with pyproject).
- `astral-sh/ruff-pre-commit` → `ruff-check --fix` + `ruff-format`.
- local `ty check` on the **pre-commit** stage.
- `pytest` gated to the **pre-push** stage (`pass_filenames = false`) — fast commits, full suite before sharing.

## CI (GitHub Actions)

- **Real matrix:** `ubuntu` × {3.11, 3.12, 3.13}, plus `macos-latest` and `windows-latest` on the top version, `fail-fast: false`.
- `setup-uv` with `enable-cache: true` and `cache-dependency-glob: uv.lock`; `uv python install` and `uv sync --locked --python` (the `--locked` is the lock-freshness gate — CI fails on a drifted lock, not just hookless contributors), then `ruff check` → `ruff format --check` → `ty check` → `uv run pytest` (gate inherited from `addopts`).
- A separate `build` job (`uv build`) to catch packaging breaks.
- **Release via OIDC trusted publishing** (`pypa/gh-action-pypi-publish`, `id-token: write`, `environment: pypi`) on `v*` tags — no stored PyPI token.
  **Gate the publish job on a passing lint/types/tests run** (`needs:`) so a red build can never reach PyPI — a tag push triggers CI and the release independently otherwise.
  Extract the matching `CHANGELOG` section into the GitHub Release notes, and fail the job if that section is empty.
- Pin actions to immutable refs (full release tags or commit SHAs); note `setup-uv` no longer publishes moving major tags (`@v8`) — pin the full version.
  Use `concurrency` with `cancel-in-progress` on PRs.
- For desktop-extension servers, gate the `.mcpb` bundle on a **manifest-drift check** and an explicit **secret/dev-file exclusion** assertion before upload (see bundle-uv-mcp-server).

## Docs

- **`CHANGELOG.md`** in Keep-a-Changelog + SemVer form, with explicit **Breaking** call-outs — and wire CI to extract release notes from it.
- README with an **environment-variable table** (name, purpose, default), a tool/resource inventory, and the error-code catalog.
- An **`AGENTS.md`** release runbook so the tag→publish flow is reproducible.

## Anti-patterns (seen across the siblings)

- Ruff on **defaults only** (no `I`/`B`/`UP`) — silently skips import sorting and easy safety lints.
- `pytest-cov` installed but **no coverage config** — coverage goes unmeasured despite a big suite.
- **ty in pre-commit only** — type regressions merge through hookless contributors and bots.
- **No CI matrix** while the manifest advertises multiple OSes/Pythons that are never tested.
- Live tests gated only by `skipif` (no marker) — they still run in the default suite when creds happen to exist, polluting the coverage measurement.
- `uvx <pkg>` shown as the primary install path with **no PyPI publish workflow** wired up.
- Design specs referenced from code but kept in a **gitignored** `docs/` — rationale unavailable to other contributors.
