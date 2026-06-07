# Config blocks

Copy-pasteable starting points for the baseline.
Replace `<pkg>` with the import name (e.g. `mcp_server_tempest`) and `<dist>` with the distribution name.

## `pyproject.toml`

```toml
[project]
name = "<dist>"
version = "0.1.0"
description = "..."
readme = "README.md"
license = "MIT"            # SPDX expression (PEP 639); replace with your license
license-files = ["LICENSE"]
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=3",
    "pydantic>=2",
]
classifiers = [
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.scripts]
<dist> = "<pkg>.cli:app"   # or "<pkg>.server:main"

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

[tool.uv]
package = true

[tool.uv.build-backend]
source-exclude = ["tests/**"]  # keep the test suite (incl. live tests) out of the sdist

[dependency-groups]
dev = [
    "prek>=0.4",
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "pytest-cov>=7",
    "ruff>=0.15",
    "ty>=0.0.1a7",
]

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E","F","W","I","B","UP","SIM","PIE","RUF","PL","PT","TID","TC","ARG","PTH"]
ignore = [
    "PLR0913",  # too-many-args: API wrappers legitimately take many
    "PLR2004",  # magic-value: noisy for literals
]

[tool.ruff.lint.per-file-ignores]
# Tests use asserts, fixtures-as-args, and inline literals by design.
"tests/**" = ["ARG", "PLR2004", "S101", "TC001", "TC002", "TC003", "PT018", "PLC0415"]

[tool.ty.src]
include = ["src", "tests"]

[tool.ty.rules]
unresolved-import = "warn"  # be strict on our code, lenient on untyped third-party shapes

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config --cov=<pkg> --cov-report=term-missing -m 'not integration'"
markers = [
    "integration: live tests hitting the real upstream/CLI; opt in with `pytest -m integration --no-cov`",
    "slow: long-running tests; deselect with -m 'not slow'",
]

[tool.coverage.run]
source = ["src/<pkg>"]
branch = true

[tool.coverage.report]
fail_under = 95
show_missing = true
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:", "raise NotImplementedError"]
```

Note: the live CI job runs `uv run pytest -m integration --no-cov` — the command-line `-m` overrides the `addopts` default (`-m 'not integration'`; last `-m` wins) and `--no-cov` keeps the small live subset from tripping the `fail_under` gate.

## `prek.toml`

```toml
default_install_hook_types = ["pre-commit", "pre-push"]

[[repos]]
repo = "https://github.com/pre-commit/pre-commit-hooks"
rev = "v5.0.0"
hooks = [
  { id = "trailing-whitespace", exclude = "^\\.github/workflows/" },
  { id = "end-of-file-fixer", exclude = "^\\.github/workflows/" },
  { id = "mixed-line-ending", exclude = "^\\.github/workflows/" },
  { id = "check-toml" },
  { id = "check-yaml" },
  { id = "check-json" },
  { id = "check-merge-conflict" },
  { id = "check-added-large-files" },
  { id = "detect-private-key" },
]

[[repos]]
repo = "https://github.com/astral-sh/uv-pre-commit"
rev = "0.9.7"
hooks = [
  { id = "uv-lock" },
]

[[repos]]
repo = "https://github.com/astral-sh/ruff-pre-commit"
rev = "v0.15.13"
hooks = [
  { id = "ruff-check", args = ["--fix"] },
  { id = "ruff-format" },
]

[[repos]]
repo = "local"

[[repos.hooks]]
id = "ty"
name = "ty check"
entry = "uv run ty check"
language = "system"
types = ["python"]
pass_filenames = false
stages = ["pre-commit"]  # without this, prek runs it on every configured stage (incl. pre-push)

[[repos.hooks]]
id = "pytest"
name = "pytest"
entry = "uv run pytest"
language = "system"
pass_filenames = false
always_run = true
stages = ["pre-push"]
```

`prek.toml` uses native TOML `[[repos]]` blocks; use `.pre-commit-config.yaml` only when upstream pre-commit compatibility is more important than the TOML format.

## `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push: { branches: ["main"], tags: ["v*"] }
  pull_request:
concurrency: { group: "ci-${{ github.ref }}", cancel-in-progress: true }
permissions: { contents: read }

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python: ["3.11", "3.12", "3.13"]
        include:
          - { os: macos-latest, python: "3.13" }
          - { os: windows-latest, python: "3.13" }
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.2.0
        with: { enable-cache: true, cache-dependency-glob: uv.lock }
      - run: uv python install ${{ matrix.python }}
      - run: uv sync --locked --python ${{ matrix.python }} --group dev
      - run: uv run ruff check src tests
      - run: uv run ruff format --check src tests
      - run: uv run ty check   # continue-on-error while ty is pre-1.0
        continue-on-error: true
      - run: uv run pytest

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv build
```

## `.github/workflows/publish.yml` (OIDC trusted publishing)

```yaml
name: Publish
on:
  push: { tags: ["v*"] }
permissions: { contents: read }

jobs:
  gate:                       # never ship a tag that can't pass lint/types/tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.2.0
        with: { enable-cache: true, cache-dependency-glob: uv.lock }
      - run: uv sync --locked
      - run: uv run ruff check src tests
      - run: uv run ruff format --check src tests
      - run: uv run pytest

  publish:
    needs: [gate]             # publish only after the gate job succeeds
    runs-on: ubuntu-latest
    permissions: { contents: write, id-token: write }
    environment: pypi
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv build
      # @release/v1 is PyPA's stable track; pin to a commit SHA for stricter supply-chain safety.
      - uses: pypa/gh-action-pypi-publish@release/v1   # OIDC: no token
      - name: Extract changelog notes
        run: |
          version="${GITHUB_REF_NAME#v}"
          awk -v version="$version" '
            $0 ~ "^## \\[" version "\\]" { capture = 1; next }
            capture && /^## \\[/ { exit }
            capture { print }
          ' CHANGELOG.md > release-notes.md
          test -s release-notes.md || { echo "::error::no CHANGELOG section for $version"; exit 1; }
      - uses: softprops/action-gh-release@v2
        with: { body_path: release-notes.md, files: dist/* }
```

## `.gitignore` essentials

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.coverage
.coverage.*
htmlcov/
dist/
*.egg-info/
.DS_Store
```
