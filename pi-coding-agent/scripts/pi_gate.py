#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4"]
# ///
"""Prove that a Pi artifact loads and runs, and report exactly which checks ran.

Pi runs isolated (throwaway agent directory, discovery off, offline) against a scripted faux
model. A pass is a pass of the checks the report lists as PASS, nothing more. Isolation limits
what Pi reads and writes; the artifact's own code runs with your permissions and is not
sandboxed (docs/security.md).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

SCRIPTS = Path(__file__).resolve().parent
HARNESS = SCRIPTS / "faux-harness.ts"
SELF_TEST_DIR = SCRIPTS / "self-test"
EXIT_PASS, EXIT_FAIL, EXIT_NO_INSTALL = 0, 1, 2

FAUX_PROVIDER, FAUX_MODEL = "gate-faux", "scripted"
TIER1_PROMPT = "pi-gate tier 1"
INVENTORY_COMMAND = "/pi-gate-inventory"
KINDS = ("extension", "package", "skill", "prompt", "theme", "mcp-config")
RPC_KINDS = ("extension", "package", "skill", "prompt")
LOAD_FLAG = {"extension": "-e", "package": "-e", "skill": "--skill", "prompt": "--prompt-template"}
DISCOVERY_OFF = {"extension": "-ne", "package": "-ne", "skill": "-ns", "prompt": "-np"}
ALWAYS_OFF = ("-nc", "--no-session", "--no-themes")
EXPECT_KEYS = (
    "tools",
    "commands",
    "skills",
    "prompts",
    "models",
    "mcpServers",
    "flags",
    "themes",
    "unobservable",
)
ACTIVE_EXPOSURES = ("direct", "model-only")
DIALOG_METHODS = ("select", "confirm", "input", "editor")
THEME_SCHEMA = Path("dist/modes/interactive/theme/theme-schema.json")
EXTENSION_FLAGS_HEADING = "Extension CLI Flags:"
DEFAULT_TIMEOUT = 60.0
TIER_1, TIER_2 = 1, 2
# expect keys whose resources carry no provenance, so they cannot show the target loaded
PROVENANCE_FREE = frozenset({"unobservable", "flags", "themes"})

# Every Pi interface the gate depends on. check_drift.py verifies each one against the
# installed Pi (MAINTAINING.md); this dictionary is their only list.
GATE_DEPENDENCIES: dict[str, list[str]] = {
    "cli_flags": [
        "--extension",
        "--no-extensions",
        "--skill",
        "--no-skills",
        "--prompt-template",
        "--no-prompt-templates",
        "--no-themes",
        "--no-context-files",
        "--no-session",
        "--mode",
        "--provider",
        "--model",
        "--approve",
    ],
    # EXTENSION_FLAGS_HEADING appears only when an extension registers a flag; the
    # tests/fixtures/gate/flag fixture, run by check_drift.py's gate stage, covers it.
    "cli_docs": ["builtin:mcp", "pi mcp list"],
    "env": ["PI_CODING_AGENT_DIR", "PI_OFFLINE", "PI_SKIP_VERSION_CHECK"],
    "rpc_commands": [
        "prompt",
        "get_commands",
        "get_available_models",
        "set_model",
        "set_auto_retry",
    ],
    "events": [
        "agent_settled",
        "tool_execution_end",
        "extension_error",
        "auto_retry_start",
        "message_end",
        "extension_ui_request",
        "extension_ui_response",
    ],
    "extension_api": [
        "getAllTools",
        "getActiveTools",
        "getMcpServers",
        "registerProvider",
        "registerCommand",
    ],
    "faux_exports": [
        "fauxProvider",
        "fauxText",
        "fauxToolCall",
        "fauxAssistantMessage",
        "getPendingResponseCount",
    ],
    "files": [THEME_SCHEMA.as_posix()],
}


def _load_pi_docs() -> ModuleType:
    if "pi_docs" in sys.modules:
        return sys.modules["pi_docs"]
    spec = importlib.util.spec_from_file_location("pi_docs", SCRIPTS / "pi_docs.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["pi_docs"] = module
    spec.loader.exec_module(module)
    return module


pi_docs = _load_pi_docs()


class GateError(Exception):
    """A gate.json or artifact problem found before Pi runs."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class Check:
    status: str  # PASS, FAIL, or UNCHECKED
    tier: str  # "1", "2", or "-" for checks outside the tiers
    name: str
    detail: str
    code: str = ""


def passed(tier: str, name: str, detail: str) -> Check:
    return Check("PASS", tier, name, detail)


def failed(tier: str, code: str, detail: str) -> Check:
    return Check("FAIL", tier, code, detail, code)


def unchecked(name: str, detail: str) -> Check:
    return Check("UNCHECKED", "-", name, detail)


# gate.json


def default_gate_path(artifact: Path) -> Path:
    if artifact.is_dir():
        return artifact / "gate.json"
    return artifact.with_name(f"{artifact.stem}.gate.json")


def artifact_for_gate(gate_path: Path) -> Path:
    """Inverse of default_gate_path: the one artifact a gate file sits next to."""
    if gate_path.name == "gate.json":
        return gate_path.parent
    stem = gate_path.name.removesuffix(".gate.json")
    siblings = [
        path
        for path in gate_path.parent.iterdir()
        if path.name.startswith(f"{stem}.") and not path.name.endswith("gate.json")
    ]
    if len(siblings) != 1:
        raise GateError("bad-gate", f"{gate_path} matches {len(siblings)} artifacts, not one")
    return siblings[0]


def _declares_something(data: dict[str, Any]) -> bool:
    expect = data.get("expect") or {}
    tier2 = data.get("tier2") or {}
    return any(expect.get(key) for key in EXPECT_KEYS) or bool(tier2.get("prompts"))


def load_gate(path: Path) -> dict[str, Any]:
    """Read and validate gate.json; raise GateError with a named reason."""
    if not path.is_file():
        raise GateError("no-gate", f"no gate file at {path} (references/gate-recipes.md)")
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError as error:
        raise GateError("bad-gate", f"{path} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise GateError("bad-gate", f"{path} must hold a JSON object")
    for key in ("expect", "tier2"):
        if not isinstance(data.get(key) or {}, dict):
            raise GateError("bad-gate", f"{path}: {key} must be a JSON object")
    unknown = set(data.get("expect") or {}) - set(EXPECT_KEYS)
    if unknown:
        raise GateError("bad-gate", f"{path}: unknown expect keys {sorted(unknown)}")
    if not _declares_something(data):
        raise GateError(
            "empty-gate", f"{path} declares no resource and no Tier 2 prompt; nothing to check"
        )
    if data.get("kind") not in KINDS:
        raise GateError("bad-gate", f"{path}: kind must be one of {', '.join(KINDS)}")
    if data.get("scope", "temporary") not in ("temporary", "project"):
        raise GateError("bad-gate", f"{path}: scope must be temporary or project")
    return data


# Real agent directory snapshot (R3.2.0)


def _entry(path: Path) -> str:
    if path.is_symlink():
        return f"symlink -> {path.readlink()}"
    if path.is_dir():
        return "dir"
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return f"file {digest.hexdigest()}"
    return "other"


def snapshot(root: Path) -> dict[str, str]:
    """Every entry under root: type, content hash for files, target for symlinks."""
    if not root.exists():
        return {}
    entries: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in [*dirnames, *filenames]:
            path = Path(dirpath) / name
            entries[path.relative_to(root).as_posix()] = _entry(path)
    return entries


def snapshot_diff(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changed = sorted(
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    )
    return [f"{key}: {before.get(key, 'absent')} => {after.get(key, 'absent')}" for key in changed]


# Isolation, arguments, and provenance


@dataclass
class Workspace:
    root: Path
    agent: Path
    work: Path
    spec: Path
    inventory: Path

    @classmethod
    def create(cls, root: Path) -> Workspace:
        agent, work = root / "agent", root / "work"
        agent.mkdir()
        work.mkdir()
        return cls(root, agent, work, root / "harness-spec.json", root / "inventory.json")


def gate_env(workspace: Workspace) -> dict[str, str]:
    """The caller's environment minus Pi settings and provider API keys, plus isolation."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("PI_") and not key.endswith("_API_KEY")
    }
    env.update(
        PI_CODING_AGENT_DIR=str(workspace.agent),
        PI_OFFLINE="1",
        PI_SKIP_VERSION_CHECK="1",
        PI_GATE_SPEC=str(workspace.spec),
    )
    return env


def stage(artifact: Path, scope: str, workspace: Workspace) -> tuple[Path, Path]:
    """Return (path Pi loads the artifact from, working directory for the run)."""
    if scope != "project":
        return artifact, workspace.work
    pi_dir = next((parent for parent in artifact.parents if parent.name == ".pi"), None)
    if pi_dir is None:
        raise GateError(
            "bad-gate", f"scope is project but {artifact} is not under a .pi/ directory"
        )
    project = workspace.root / "project"
    target = project / ".pi" / artifact.relative_to(pi_dir)
    target.parent.mkdir(parents=True)
    if artifact.is_dir():
        shutil.copytree(artifact, target)
    else:
        shutil.copy2(artifact, target)
    return target, project


def pi_args(data: dict[str, Any], loaded: Path, *, approve: bool) -> list[str]:
    kind = data["kind"]
    project = data.get("scope") == "project"
    skip = DISCOVERY_OFF[kind] if project else None
    args = [flag for flag in dict.fromkeys(DISCOVERY_OFF.values()) if flag != skip]
    args += ALWAYS_OFF
    if project:
        if approve:
            args.append("--approve")
    else:
        args += [LOAD_FLAG[kind], str(loaded)]
    if (data.get("expect") or {}).get("mcpServers") and not project:
        args += ["-e", "builtin:mcp"]
    return args


def harness_spec(data: dict[str, Any], workspace: Workspace) -> dict[str, Any]:
    tier2 = data.get("tier2") or {}
    providers = [{"provider": FAUX_PROVIDER, "models": [FAUX_MODEL]}, *tier2.get("providers", [])]
    steps = [{"provider": FAUX_PROVIDER, "text": "pi-gate tier 1 done"}]
    steps += [{"provider": FAUX_PROVIDER, **step} for step in tier2.get("steps", [])]
    return {"inventoryPath": str(workspace.inventory), "providers": providers, "steps": steps}


def _real(path: str | Path) -> str:
    return os.path.realpath(path)


def origin_of(path: str, target: Path) -> str:
    """builtin, harness, target, or other — the provenance classes R3.8.5 separates."""
    if path.startswith("builtin:"):
        return "builtin"
    if _real(path) == _real(HARNESS):
        return "harness"
    real, root = _real(path), _real(target)
    return "target" if real == root or real.startswith(root + os.sep) else "other"


def _names(entries: list[Any]) -> list[str]:
    return [entry if isinstance(entry, str) else entry["name"] for entry in entries]


def matches(pattern: Any, value: Any) -> bool:
    """Subset match: every key in a pattern object, and every item in a pattern list, is found."""
    if isinstance(pattern, dict):
        return isinstance(value, dict) and all(
            key in value and matches(item, value[key]) for key, item in pattern.items()
        )
    if isinstance(pattern, list):
        return isinstance(value, list) and all(any(matches(p, v) for v in value) for p in pattern)
    return pattern == value
