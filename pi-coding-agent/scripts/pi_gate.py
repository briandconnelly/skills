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

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jsonschema

if TYPE_CHECKING:
    from collections.abc import Callable
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
MCP_VALIDATOR_MODULE = Path("dist/extensions/mcp/config.js")
MCP_VALIDATOR = SCRIPTS / "mcp-validator.mjs"
EXTENSION_FLAGS_HEADING = "Extension CLI Flags:"
DEFAULT_TIMEOUT = 60.0
# Pi honours HTTP(S)_PROXY for its model requests; a dead proxy makes any provider call fail
# at once, whatever credentials the environment or the user's files hold.
DEAD_PROXY = "http://127.0.0.1:9"
CREDENTIAL_SUFFIXES = ("_API_KEY", "_TOKEN")
CREDENTIAL_PREFIXES = ("PI_", "AWS_", "CLOUDSDK_", "GOOGLE_APPLICATION_")
PROXY_NAMES = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")
TIER_1, TIER_2 = 1, 2
# expect keys whose resources carry no provenance, so they cannot show the target loaded
PROVENANCE_FREE = frozenset({"unobservable", "flags", "themes", "models"})

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
    "mcp_exports": ["loadMcpConfig"],
    "files": [THEME_SCHEMA.as_posix(), MCP_VALIDATOR_MODULE.as_posix()],
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


_STRINGS = {"type": "array", "items": {"type": "string"}}
_TOOL = {
    "oneOf": [
        {"type": "string"},
        {
            "type": "object",
            "properties": {"name": {"type": "string"}, "exposure": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False,
        },
    ]
}
_STEP = {
    "type": "object",
    "properties": {
        "provider": {"type": "string"},
        "text": {"type": "string"},
        "expectTranscript": {"type": "string"},
        "toolCall": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "arguments": {"type": "object"}},
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}
_TOOL_RESULT = {
    "type": "object",
    "properties": {
        "toolName": {"type": "string"},
        "isError": {"type": "boolean"},
        "contains": {"type": "string"},
    },
    "required": ["toolName"],
    "additionalProperties": False,
}
# The only definition of gate.json's shape; references/gate-recipes.md explains the fields.
GATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "kind": {"enum": list(KINDS)},
        "scope": {"enum": ["temporary", "project"]},
        "expect": {
            "type": "object",
            "properties": {
                **{key: _STRINGS for key in EXPECT_KEYS},
                "tools": {"type": "array", "items": _TOOL},
            },
            "additionalProperties": False,
        },
        "tier2": {
            "type": "object",
            "properties": {
                "prompts": _STRINGS,
                "steps": {"type": "array", "items": _STEP},
                "model": {"type": "string"},
                "assistantModels": _STRINGS,
                "providers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"provider": {"type": "string"}, "models": _STRINGS},
                        "required": ["provider", "models"],
                        "additionalProperties": False,
                    },
                },
                "expect": {
                    "type": "object",
                    "properties": {
                        "toolResults": {"type": "array", "items": _TOOL_RESULT},
                        "events": {
                            "type": "array",
                            "items": {"type": "object", "required": ["type"]},
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


def _objects(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    item = {"type": "object", "properties": properties, "required": required}
    return {"type": "array", "items": item}


_STR = {"type": "string"}
_SOURCE_INFO = {"type": "object", "properties": {"path": _STR, "origin": _STR}}
# What the gate reads from Pi's output, and nothing more. A reply that lacks one of these
# fields fails as pi-shape naming the path, instead of raising (MAINTAINING.md: run
# check_drift.py against the new Pi). Extra fields are allowed.
PI_SHAPES: dict[str, dict[str, Any]] = {
    "response": {
        "type": "object",
        "properties": {"success": {"type": "boolean"}, "error": _STR},
        "required": ["success"],
        "if": {"properties": {"success": {"const": False}}},
        "then": {"required": ["error"]},
    },
    "prompt": {
        "type": "object",
        "properties": {"data": {"type": "object", "required": ["disposition"]}},
        "required": ["data"],
    },
    "get_commands": {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "commands": _objects(
                        {"name": _STR, "source": _STR, "sourceInfo": _SOURCE_INFO},
                        ["name", "source"],
                    )
                },
                "required": ["commands"],
            }
        },
        "required": ["data"],
    },
    "get_available_models": {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "models": _objects({"provider": _STR, "id": _STR}, ["provider", "id"])
                },
                "required": ["models"],
            }
        },
        "required": ["data"],
    },
    "inventory": {
        "type": "object",
        "properties": {
            "tools": _objects(
                {"name": _STR, "exposure": _STR, "sourceInfo": _SOURCE_INFO}, ["name", "exposure"]
            ),
            "activeTools": {"type": "array", "items": _STR},
            "mcpServers": _objects(
                {"name": _STR, "extensionPath": _STR}, ["name", "extensionPath"]
            ),
            "faux": _objects(
                {"provider": _STR, "pending": {"type": "integer"}}, ["provider", "pending"]
            ),
            "transcriptMisses": {"type": "array", "items": _STR},
        },
        "required": ["tools", "activeTools", "mcpServers", "faux", "transcriptMisses"],
    },
    "message_end": {
        "type": "object",
        "properties": {"message": {"type": "object"}},
        "required": ["message"],
    },
    "pi mcp list": {
        "type": "object",
        "properties": {
            "errors": {"type": "array", "items": _STR},
            "servers": _objects({"name": _STR}, ["name"]),
        },
        "required": ["errors", "servers"],
    },
    "MCP validation": {
        "type": "object",
        "properties": {
            "errors": {"type": "array", "items": _STR},
            "servers": _objects(
                {"name": _STR, "override": {"type": "boolean"}}, ["name", "override"]
            ),
        },
        "required": ["errors", "servers"],
    },
}


class PiShapeError(Exception):
    """Pi's output lacks a field the gate reads."""


def require_shape(name: str, value: Any) -> Any:
    """Return value if it has the shape the gate reads from Pi's `name` output; else raise."""
    error = jsonschema.exceptions.best_match(
        jsonschema.Draft7Validator(PI_SHAPES[name]).iter_errors(value)
    )
    if error is not None:
        where = "/".join(str(part) for part in error.absolute_path) or "(top level)"
        raise PiShapeError(f"{name} output at {where}: {error.message}")
    return value


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
    error = jsonschema.exceptions.best_match(
        jsonschema.Draft7Validator(GATE_SCHEMA).iter_errors(data)
    )
    if error is not None:
        where = "/".join(str(part) for part in error.absolute_path) or "(top level)"
        raise GateError("bad-gate", f"{path}: {where}: {error.message}")
    if not _declares_something(data):
        raise GateError(
            "empty-gate", f"{path} declares no resource and no Tier 2 prompt; nothing to check"
        )
    if data.get("kind") not in KINDS:
        raise GateError("bad-gate", f"{path}: kind must be one of {', '.join(KINDS)}")
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
    pi: tuple[str, ...]  # how to launch the Pi being gated

    @classmethod
    def create(cls, root: Path, pi: tuple[str, ...] = ("pi",)) -> Workspace:
        agent, work = root / "agent", root / "work"
        agent.mkdir()
        work.mkdir()
        return cls(root, agent, work, root / "harness-spec.json", root / "inventory.json", pi)


def pi_command(root: Path) -> tuple[str, ...]:
    """The installed package's own `pi` entry point, so a project-local install works too."""
    bin_field = json.loads((root / "package.json").read_text(encoding="utf-8")).get("bin")
    entry = bin_field.get("pi") if isinstance(bin_field, dict) else bin_field
    return (str(root / entry),) if isinstance(entry, str) else ("pi",)


def _credential_or_proxy(key: str) -> bool:
    upper = key.upper()
    return (
        upper.endswith(CREDENTIAL_SUFFIXES)
        or upper.startswith(CREDENTIAL_PREFIXES)
        or upper in PROXY_NAMES
    )


def gate_env(workspace: Workspace) -> dict[str, str]:
    """The caller's environment minus Pi settings, credentials, and proxies, plus isolation.

    Every HTTP(S) request Pi makes goes to a dead proxy, so a model request that is not
    answered by a faux provider fails instead of reaching (and billing) a real provider.
    """
    env = {key: value for key, value in os.environ.items() if not _credential_or_proxy(key)}
    env.update(
        PI_CODING_AGENT_DIR=str(workspace.agent),
        PI_OFFLINE="1",
        PI_SKIP_VERSION_CHECK="1",
        PI_GATE_SPEC=str(workspace.spec),
        HTTP_PROXY=DEAD_PROXY,
        HTTPS_PROXY=DEAD_PROXY,
        http_proxy=DEAD_PROXY,
        https_proxy=DEAD_PROXY,
        AWS_SHARED_CREDENTIALS_FILE=str(workspace.root / "aws-credentials"),
        AWS_CONFIG_FILE=str(workspace.root / "aws-config"),
        CLOUDSDK_CONFIG=str(workspace.root / "gcloud"),
    )
    return env


def _pi_directory(artifact: Path, real: Path) -> Path | None:
    """The real `.pi` directory holding the artifact, found by name among its unresolved or
    resolved parents (a symlinked `.pi` keeps its name only in the unresolved path), and
    accepted only if the artifact really lives inside it (so `.pi/../x` does not count)."""
    for parent in [*artifact.parents, *real.parents]:
        if parent.name == ".pi":
            candidate = parent.resolve()
            if real.is_relative_to(candidate) and real != candidate:
                return candidate
    return None


def stage(artifact: Path, scope: str, workspace: Workspace) -> tuple[Path, Path]:
    """Return (path Pi loads the artifact from, working directory for the run).

    `artifact` is absolute but unresolved; the file loaded is the one the OS opens for it.
    """
    real = artifact.resolve()
    if scope != "project":
        return real, workspace.work
    pi_dir = _pi_directory(artifact, real)
    if pi_dir is None:
        raise GateError(
            "bad-gate", f"scope is project but {artifact} is not under a .pi/ directory"
        )
    project = workspace.root / "project"
    target = project / ".pi" / real.relative_to(pi_dir)
    artifact = real
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


# Running Pi


class RpcSession:
    """A `pi --mode rpc` child: JSONL on stdin/stdout, split on LF only (docs/rpc.md)."""

    def __init__(self, command: list[str], env: dict[str, str], cwd: Path, stderr: Path) -> None:
        self._stderr = stderr.open("wb")
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr,
            env=env,
            cwd=cwd,
        )
        self.records: list[dict[str, Any]] = []
        self.exited_early = False
        self.timeout = DEFAULT_TIMEOUT
        self._buffer = b""
        self._next_id = 0

    def _write(self, command: dict[str, Any]) -> bool:
        assert self.proc.stdin is not None
        try:
            self.proc.stdin.write((json.dumps(command) + "\n").encode())
            self.proc.stdin.flush()
        except BrokenPipeError:
            self.exited_early = True
            return False
        return True

    def _buffered(self) -> dict[str, Any] | None:
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            text = line.decode("utf-8", errors="replace").rstrip("\r")
            if text.strip():
                try:
                    record = json.loads(text)
                except json.JSONDecodeError:
                    return {"type": "pi-gate-unparsed", "line": text}
                if not isinstance(record, dict):
                    raise PiShapeError(f"RPC record is not a JSON object: {text[:200]}")
                return record
        return None

    def _answer_dialog(self, record: dict[str, Any]) -> None:
        if record.get("type") == "extension_ui_request" and record.get("method") in DIALOG_METHODS:
            self._write({"type": "extension_ui_response", "id": record["id"], "cancelled": True})

    def wait_for(self, predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any] | None:
        """Read records until one matches; None if Pi exits first. Raises TimeoutError."""
        assert self.proc.stdout is not None
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            record = self._buffered()
            if record is not None:
                self.records.append(record)
                self._answer_dialog(record)
                if predicate(record):
                    return record
                continue
            ready, _, _ = select.select([self.proc.stdout], [], [], 0.2)
            if ready:
                chunk = os.read(self.proc.stdout.fileno(), 65536)
                if not chunk:
                    self.exited_early = True
                    return None
                self._buffer += chunk
        raise TimeoutError

    def request(self, command: dict[str, Any]) -> dict[str, Any] | None:
        self._next_id += 1
        request_id = f"gate-{self._next_id}"
        if not self._write({"id": request_id, **command}):
            return None
        return self.wait_for(lambda r: r.get("type") == "response" and r.get("id") == request_id)

    def prompt(self, message: str) -> dict[str, Any] | None:
        response = self.request({"type": "prompt", "message": message})
        if response is not None:
            require_shape("response", response)
        if response is not None and response["success"]:
            require_shape("prompt", response)
        started = (
            response and response.get("success") and response["data"]["disposition"] != "handled"
        )
        if started and self.wait_for(lambda r: r.get("type") == "agent_settled") is None:
            return None
        return response

    def close(self) -> int:
        assert self.proc.stdin is not None
        with contextlib.suppress(BrokenPipeError):
            self.proc.stdin.close()
        try:
            code = self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = self.proc.wait()
        self._stderr.close()
        return code


@dataclass
class Observation:
    records: list[dict[str, Any]] = field(default_factory=list)
    tier2_start: int | None = None
    commands: list[dict[str, Any]] = field(default_factory=list)
    models: list[dict[str, Any]] = field(default_factory=list)
    inventory: dict[str, Any] | None = None
    tier2_inventory: dict[str, Any] | None = None
    set_model_error: str | None = None
    shape_error: str | None = None
    unscripted_model: str | None = None
    prompt_errors: list[str] = field(default_factory=list)
    load_error: str | None = None
    timed_out: bool = False


def _read_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _inventory(session: RpcSession, workspace: Workspace) -> dict[str, Any] | None:
    workspace.inventory.unlink(missing_ok=True)
    session.prompt(INVENTORY_COMMAND)
    try:
        inventory = _read_json(workspace.inventory)
    except (OSError, ValueError) as error:  # ValueError covers bad JSON and bad UTF-8
        raise PiShapeError(f"inventory could not be read as JSON: {error}") from error
    return None if inventory is None else require_shape("inventory", inventory)


def _run_tier2(session: RpcSession, data: dict[str, Any], obs: Observation, ws: Workspace) -> None:
    tier2 = data["tier2"]
    obs.tier2_start = len(session.records)
    declared = set(_names((data.get("expect") or {}).get("models", [])))
    if tier2.get("model") and tier2["model"] not in _harness_models(data) | declared:
        obs.unscripted_model = tier2["model"]
        return
    if tier2.get("model"):
        provider, _, model_id = tier2["model"].partition("/")
        response = session.request({"type": "set_model", "provider": provider, "modelId": model_id})
        if response is not None and not require_shape("response", response)["success"]:
            obs.set_model_error = f"{tier2['model']}: {response['error']}"
            return
    for message in tier2.get("prompts", []):
        response = session.prompt(message)
        if response is not None and not response.get("success"):
            obs.prompt_errors.append(f"{message!r}: {response.get('error')}")
    obs.tier2_inventory = _inventory(session, ws)


def observe(
    data: dict[str, Any], args: list[str], ws: Workspace, cwd: Path, *, tier: int
) -> Observation:
    """One Pi process: Tier 1 turn, inventory, command and model lists, then Tier 2."""
    ws.spec.write_text(json.dumps(harness_spec(data, ws)), encoding="utf-8")
    stderr = ws.root / "pi-stderr.txt"
    full = [*args, "-e", str(HARNESS), "--provider", FAUX_PROVIDER, "--model", FAUX_MODEL]
    session = RpcSession([*ws.pi, "--mode", "rpc", *full], gate_env(ws), cwd, stderr)
    obs = Observation()
    try:
        if session.request({"type": "set_auto_retry", "enabled": False}) is not None:
            session.prompt(TIER1_PROMPT)
            obs.inventory = _inventory(session, ws)
            commands = session.request({"type": "get_commands"})
            models = session.request({"type": "get_available_models"})
            if commands is not None:
                obs.commands = require_shape("get_commands", commands)["data"]["commands"]
            if models is not None:
                obs.models = require_shape("get_available_models", models)["data"]["models"]
            if tier == TIER_2 and data.get("tier2"):
                _run_tier2(session, data, obs, ws)
            for record in session.records:
                if record.get("type") == "message_end":
                    require_shape("message_end", record)
    except TimeoutError:
        obs.timed_out = True
    except PiShapeError as error:
        obs.shape_error = str(error)
    finally:
        code = session.close()
    obs.records = session.records
    if session.exited_early:
        text = stderr.read_text(encoding="utf-8", errors="replace").strip()
        obs.load_error = text or f"pi exited with code {code} before answering"
    return obs


# Tier 1 checks


def _tool_checks(expected: list[Any], inventory: dict[str, Any], target: Path) -> list[Check]:
    checks: list[Check] = []
    tools = {tool["name"]: tool for tool in inventory["tools"]}
    for entry in expected:
        name = entry if isinstance(entry, str) else entry["name"]
        tool = tools.get(name)
        if tool is None:
            checks.append(failed("1", "missing-resource", f"tool {name} is not registered"))
            continue
        path = (tool.get("sourceInfo") or {}).get("path", "")
        exposure = entry.get("exposure") if isinstance(entry, dict) else None
        if origin_of(path, target) != "target":
            checks.append(failed("1", "provenance", f"tool {name} comes from {path}, not {target}"))
        elif exposure and tool["exposure"] != exposure:
            detail = f"tool {name} has exposure {tool['exposure']}, gate.json expects {exposure}"
            checks.append(failed("1", "exposure", detail))
        elif tool["exposure"] in ACTIVE_EXPOSURES and name not in inventory["activeTools"]:
            detail = f"tool {name} ({tool['exposure']}) is not active (getActiveTools)"
            checks.append(failed("1", "inactive", detail))
        else:
            detail = f"registered, exposure {tool['exposure']}, from {path}"
            checks.append(passed("1", f"tool {name}", detail))
    return checks


def _command_checks(
    data: dict[str, Any], commands: list[dict[str, Any]], target: Path
) -> list[Check]:
    checks: list[Check] = []
    expect = data.get("expect") or {}
    package = data["kind"] == "package"
    by_key = {(command["source"], command["name"]): command for command in commands}
    wanted = [("extension", name, "command") for name in _names(expect.get("commands", []))]
    wanted += [("skill", f"skill:{name}", "skill") for name in _names(expect.get("skills", []))]
    wanted += [("prompt", name, "prompt") for name in _names(expect.get("prompts", []))]
    trust = " (project resources load only when trusted; docs/security.md)"
    hint = trust if data.get("scope") == "project" else ""
    for source, name, label in wanted:
        command = by_key.get((source, name))
        if command is None:
            checks.append(
                failed("1", "missing-resource", f"{label} {name} is not in get_commands{hint}")
            )
            continue
        info = command.get("sourceInfo") or {}
        if origin_of(info.get("path", ""), target) != "target":
            detail = f"{label} {name} comes from {info.get('path')}, not {target}"
            checks.append(failed("1", "provenance", detail))
        elif package and source == "prompt" and info.get("origin") != "package":
            detail = f"prompt {name} has origin {info.get('origin')}, expected package"
            checks.append(failed("1", "provenance", detail))
        else:
            checks.append(
                passed("1", f"{label} {name}", f"in get_commands, from {info.get('path')}")
            )
    return checks


def _model_checks(
    expected: list[str], models: list[dict[str, Any]], harness: set[str]
) -> list[Check]:
    """A declared model must be available and must not be one the gate's harness supplies."""
    available = {f"{model['provider']}/{model['id']}" for model in models}
    checks: list[Check] = []
    for name in expected:
        if name in harness:
            detail = f"model {name} is a faux model the gate supplies (tier2.providers)"
            checks.append(failed("1", "provenance", detail))
        elif name in available:
            checks.append(passed("1", f"model {name}", "in get_available_models"))
        else:
            checks.append(
                failed("1", "missing-resource", f"model {name} is not in get_available_models")
            )
    return checks


def _mcp_checks(expected: list[str], inventory: dict[str, Any], target: Path) -> list[Check]:
    checks: list[Check] = []
    servers = {server["name"]: server for server in inventory["mcpServers"]}
    for name in expected:
        server = servers.get(name)
        if server is None:
            checks.append(failed("1", "missing-resource", f"MCP server {name} is not registered"))
        elif origin_of(server["extensionPath"], target) != "target":
            detail = f"MCP server {name} registered by {server['extensionPath']}, not {target}"
            checks.append(failed("1", "provenance", detail))
        else:
            checks.append(
                passed("1", f"MCP server {name}", f"registered by {server['extensionPath']}")
            )
    return checks


def _harness_models(data: dict[str, Any]) -> set[str]:
    providers = [{"provider": FAUX_PROVIDER, "models": [FAUX_MODEL]}]
    providers += (data.get("tier2") or {}).get("providers", [])
    return {f"{entry['provider']}/{model}" for entry in providers for model in entry["models"]}


def _provenance_sweep(data: dict[str, Any], obs: Observation, target: Path) -> list[Check]:
    """R3.8.5: nothing from outside the artifact, and something from the artifact."""
    assert obs.inventory is not None
    paths = [
        (f"tool {t['name']}", (t.get("sourceInfo") or {}).get("path", ""))
        for t in obs.inventory["tools"]
    ]
    paths += [
        (f"command {c['name']}", (c.get("sourceInfo") or {}).get("path", "")) for c in obs.commands
    ]
    paths += [(f"MCP server {s['name']}", s["extensionPath"]) for s in obs.inventory["mcpServers"]]
    origins = [(label, path, origin_of(path, target)) for label, path in paths]
    checks = [
        failed("1", "unexpected-resource", f"{label} loaded from {path}, outside the artifact")
        for label, path, origin in origins
        if origin == "other"
    ]
    if any(origin == "target" for _, _, origin in origins):
        checks.append(passed("1", "target loaded", "the artifact contributed observed resources"))
    elif {key for key, value in (data.get("expect") or {}).items() if value} - PROVENANCE_FREE:
        detail = "only harness and built-in resources were observed; the artifact did not load"
        checks.append(failed("1", "target-not-loaded", detail))
    else:
        checks.append(unchecked("target loaded", "the artifact declares nothing Pi reports"))
    return checks


def _errors(records: list[dict[str, Any]], tier: str) -> list[Check]:
    return [
        failed(
            tier,
            "extension-error",
            f"{r.get('extensionPath')} ({r.get('event')}): {r.get('error')}",
        )
        for r in records
        if r.get("type") == "extension_error"
    ]


def _dialogs(records: list[dict[str, Any]]) -> list[Check]:
    return [
        unchecked(
            f"dialog {r['method']}",
            f"{r.get('title', '')!r} was answered cancelled; other answers were not exercised",
        )
        for r in records
        if r.get("type") == "extension_ui_request" and r.get("method") in DIALOG_METHODS
    ]


def _assistant_messages(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record["message"]
        for record in records
        if record.get("type") == "message_end" and record["message"].get("role") == "assistant"
    ]


def tier1_checks(data: dict[str, Any], obs: Observation, target: Path) -> list[Check]:
    if obs.shape_error:
        detail = f"{obs.shape_error}; this Pi's output changed shape, run check_drift.py"
        return [failed("1", "pi-shape", detail)]
    if obs.load_error:
        return [failed("1", "load-error", obs.load_error)]
    if obs.timed_out or obs.inventory is None:
        return [failed("1", "timeout", "Pi did not finish the Tier 1 run in time")]
    records = obs.records[: obs.tier2_start]
    checks = _errors(records, "1") + _dialogs(records)
    turn = _assistant_messages(records)
    if not turn or turn[0].get("provider") != FAUX_PROVIDER or turn[0].get("stopReason") == "error":
        detail = f"the Tier 1 turn was not answered by {FAUX_PROVIDER}: {turn[:1]}"
        checks.append(failed("1", "harness", detail))
    expect = data.get("expect") or {}
    checks += _tool_checks(expect.get("tools", []), obs.inventory, target)
    checks += _command_checks(data, obs.commands, target)
    checks += _model_checks(_names(expect.get("models", [])), obs.models, _harness_models(data))
    checks += _mcp_checks(_names(expect.get("mcpServers", [])), obs.inventory, target)
    checks += _provenance_sweep(data, obs, target)
    if not checks or all(check.status != "FAIL" for check in checks):
        checks.insert(0, passed("1", "load", "Pi loaded the artifact with no extension_error"))
    return checks


# Tier 2 checks


def _model_sequence_checks(data: dict[str, Any], records: list[dict[str, Any]]) -> list[Check]:
    tier2 = data["tier2"]
    messages = _assistant_messages(records)
    faux = _harness_models(data)
    actual = [f"{m.get('provider')}/{m.get('model')}" for m in messages]
    checks = [
        failed("2", "provider-error", f"{name} answered with an error: {m.get('errorMessage')}")
        for name, m in zip(actual, messages, strict=True)
        if m.get("stopReason") == "error"
    ]
    strangers = [name for name in actual if name not in faux]
    if strangers:
        checks.append(failed("2", "wrong-provider", f"answered by {strangers}, not a faux model"))
    expected = tier2.get("assistantModels")
    if expected is None:
        expected = [f"{FAUX_PROVIDER}/{FAUX_MODEL}"] * len(actual)
    if actual != expected:
        checks.append(
            failed(
                "2", "wrong-model", f"assistant messages came from {actual}, expected {expected}"
            )
        )
    elif actual and not checks:
        checks.append(passed("2", "physical models", f"{actual}"))
    return checks


def _result_text(result: Any) -> str:
    """The tool result's text parts, as the model sees them; JSON only for non-text results."""
    content = result.get("content") if isinstance(result, dict) else None
    parts = [
        c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text"
    ]
    return "\n".join(parts) if parts else json.dumps(result, ensure_ascii=False)


def _tool_result_checks(
    expected: list[dict[str, Any]], records: list[dict[str, Any]]
) -> list[Check]:
    """Match each expectation, in order, to the next unused result of that tool."""
    checks: list[Check] = []
    ends = [r for r in records if r.get("type") == "tool_execution_end"]
    for entry in expected:
        name = entry["toolName"]
        end = next((r for r in ends if r.get("toolName") == name), None)
        if end is None:
            checks.append(failed("2", "tool-result", f"no unmatched tool_execution_end for {name}"))
            continue
        ends.remove(end)
        text = _result_text(end.get("result"))
        want_error = entry.get("isError", False)
        if end.get("isError") != want_error:
            detail = (
                f"{name} returned isError={end.get('isError')}, expected {want_error}: {text[:300]}"
            )
            checks.append(failed("2", "tool-result", detail))
        elif entry.get("contains") and entry["contains"] not in text:
            detail = f"{name} result lacks {entry['contains']!r}: {text[:300]}"
            checks.append(failed("2", "tool-result", detail))
        else:
            checks.append(passed("2", f"tool result {name}", text[:120]))
            if not entry.get("contains"):
                checks.append(
                    unchecked(
                        f"tool result content {name}",
                        "only error status was asserted; result content was not checked",
                    )
                )
    checks += [
        failed(
            "2",
            "tool-result",
            f"{r.get('toolName')} failed and gate.json does not expect it: "
            f"{json.dumps(r.get('result'))[:300]}",
        )
        for r in ends
        if r.get("isError")
    ]
    checks += [
        unchecked(
            f"unasserted tool call {r.get('toolName')} #{index}",
            "call succeeded but no result assertion matched it",
        )
        for index, r in enumerate(
            (r for r in records if r.get("type") == "tool_execution_end"), start=1
        )
        if any(r is remaining for remaining in ends)
        if not r.get("isError")
    ]
    return checks


def _event_checks(expected: list[dict[str, Any]], records: list[dict[str, Any]]) -> list[Check]:
    seen = sorted({str(r.get("type")) for r in records})
    return [
        passed("2", f"event {pattern.get('type')}", json.dumps(pattern)[:120])
        if any(matches(pattern, record) for record in records)
        else failed(
            "2", "event-mismatch", f"no event matches {json.dumps(pattern)}; saw types {seen}"
        )
        for pattern in expected
    ]


def _script_checks(tier2: dict[str, Any], inventory: dict[str, Any]) -> list[Check]:
    """Every scripted step consumed; every expectTranscript seen by the model."""
    checks: list[Check] = []
    for entry in inventory["faux"]:
        if entry["pending"]:
            detail = f"{entry['provider']} has {entry['pending']} scripted step(s) never requested"
            checks.append(failed("2", "unconsumed-steps", detail))
    if tier2.get("steps") and not checks:
        checks.append(passed("2", "script consumed", f"all {len(tier2['steps'])} scripted steps"))
    misses = inventory["transcriptMisses"]
    for step in tier2.get("steps", []):
        text = step.get("expectTranscript")
        if text and text in misses:
            checks.append(
                failed("2", "transcript", f"{text!r} did not reach the model's transcript")
            )
        elif text:
            checks.append(passed("2", "transcript", f"{text!r} reached the model's transcript"))
    return checks


def tier2_checks(data: dict[str, Any], obs: Observation) -> list[Check]:
    if obs.shape_error or obs.load_error or obs.tier2_start is None:
        return []
    if obs.unscripted_model:
        detail = (
            f"tier2.model {obs.unscripted_model} is neither a faux model (tier2.providers) nor "
            "declared in expect.models; the gate does not select a model it cannot account for"
        )
        return [failed("2", "unscripted-model", detail)]
    if obs.set_model_error:
        return [failed("2", "set-model", f"could not select {obs.set_model_error}")]
    if obs.timed_out or obs.tier2_inventory is None:
        return [failed("2", "timeout", "Pi did not finish the Tier 2 run in time")]
    records = obs.records[obs.tier2_start :]
    expect = data["tier2"].get("expect") or {}
    checks = _errors(records, "2") + _dialogs(records)
    checks += [failed("2", "prompt-rejected", error) for error in obs.prompt_errors]
    if not _assistant_messages(records) and not (expect.get("toolResults") or expect.get("events")):
        detail = (
            "Tier 2 ran no model turn and declares no tool result or event; nothing was checked"
        )
        checks.append(failed("2", "tier2-empty", detail))
    checks += _model_sequence_checks(data, records)
    if any(r.get("type") == "auto_retry_start" for r in records):
        checks.append(
            failed("2", "retry", "Pi retried a request; every scripted step must succeed once")
        )
    checks += _script_checks(data["tier2"], obs.tier2_inventory)
    checks += _tool_result_checks(expect.get("toolResults", []), records)
    checks += _event_checks(expect.get("events", []), records)
    return checks


# What each surface leaves unchecked (R3.10)


def has_behavior_assertions(tier2: dict[str, Any]) -> bool:
    expect = tier2.get("expect") or {}
    return bool(
        tier2.get("assistantModels")
        or expect.get("toolResults")
        or expect.get("events")
        or any(step.get("expectTranscript") for step in tier2.get("steps", []))
    )


def behavior_coverage(data: dict[str, Any], obs: Observation, target: Path) -> list[Check]:
    """Report observed artifact resources not exercised by the declared Tier 2."""
    if obs.shape_error or obs.load_error or obs.prompt_errors or obs.inventory is None:
        return []
    records = obs.records[obs.tier2_start :] if obs.tier2_start is not None else []
    inventory = obs.tier2_inventory or obs.inventory
    called = {r.get("toolName") for r in records if r.get("type") == "tool_execution_end"}
    checks = [
        unchecked(f"tool behavior {tool['name']}", "registered but not called in Tier 2")
        for tool in inventory["tools"]
        if origin_of((tool.get("sourceInfo") or {}).get("path", ""), target) == "target"
        and tool["name"] not in called
    ]
    tier2 = data.get("tier2") or {}
    invoked = {prompt.split()[0] for prompt in tier2.get("prompts", []) if prompt.split()}
    transcript_asserted = any(step.get("expectTranscript") for step in tier2.get("steps", []))
    for command in obs.commands:
        if origin_of((command.get("sourceInfo") or {}).get("path", ""), target) != "target":
            continue
        source, name = command["source"], command["name"]
        label = {"extension": "command", "skill": "skill", "prompt": "prompt"}.get(source, source)
        if obs.tier2_start is None or f"/{name}" not in invoked:
            checks.append(
                unchecked(f"{label} behavior {name}", "registered but not invoked in Tier 2")
            )
        elif source in ("skill", "prompt") and not transcript_asserted:
            checks.append(
                unchecked(f"{label} expansion {name}", "invoked without a transcript assertion")
            )
        elif source == "extension" and not has_behavior_assertions(tier2):
            checks.append(
                unchecked(f"command behavior {name}", "invoked without a behavior assertion")
            )
    return checks


def unchecked_items(data: dict[str, Any], tier: int) -> list[Check]:
    """The surface table's unchecked cells that apply to this gate.json (R3.10)."""
    expect = data.get("expect") or {}
    tier2 = data.get("tier2")
    items: list[Check] = []
    if data["kind"] in RPC_KINDS:
        detail = "resources registered after a run settles (e.g. in agent_settled) are not observed"
        items.append(unchecked("late registration", detail))
    if tier2 and tier == TIER_1:
        items.append(unchecked("Tier 2", "not run (--tier 1)"))
    elif tier2 and not has_behavior_assertions(tier2):
        items.append(
            unchecked("Tier 2 behavior", "scripted turns declare no artifact behavior assertions")
        )
    elif not tier2 and data["kind"] not in ("theme", "mcp-config"):
        items.append(unchecked("Tier 2", "gate.json declares no tier2 block; no behavior was run"))
    if expect.get("models"):
        items.append(unchecked("model provenance", "models carry no sourceInfo"))
    if expect.get("mcpServers"):
        items.append(unchecked("MCP connection", "connection and tool discovery were not run"))
    if expect.get("flags"):
        items.append(unchecked("flag behavior", "flag provenance and effect are not checked"))
    if expect.get("themes") or data["kind"] == "theme":
        detail = "theme loading, variable resolution, rendering, and package theme provenance"
        items.append(unchecked("theme", detail))
    items += [
        unchecked(str(item), "loaded without extension_error; behavior not checked")
        for item in expect.get("unobservable", [])
    ]
    return items


# Checks that do not use the RPC run


def flag_checks(expected: list[str], args: list[str], ws: Workspace, cwd: Path) -> list[Check]:
    try:
        result = subprocess.run(
            [*ws.pi, *args, "--help"],
            env=gate_env(ws),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [failed("1", "timeout", "pi --help did not finish in time")]
    _, _, section = result.stdout.partition(EXTENSION_FLAGS_HEADING)
    listed = set(re.findall(r"^\s+--([\w-]+)", section, flags=re.MULTILINE))
    return [
        passed("1", f"flag --{name}", "listed by pi --help under Extension CLI Flags")
        if name in listed
        else failed("1", "missing-resource", f"flag --{name} is not listed by pi --help")
        for name in expected
    ]


def _theme_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        path
        for path in target.rglob("*.json")
        if "node_modules" not in path.relative_to(target).parts
        and path.name != "package.json"
        and not path.name.endswith("gate.json")
    )


def theme_checks(expected: list[str], target: Path, install_root: Path) -> list[Check]:
    validator = jsonschema.Draft7Validator(json.loads((install_root / THEME_SCHEMA).read_text()))
    themes: dict[str, tuple[Path, Any]] = {}
    for path in _theme_files(target):
        with contextlib.suppress(json.JSONDecodeError):
            theme = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(theme, dict) and isinstance(theme.get("name"), str):
                themes[theme["name"]] = (path, theme)
    checks: list[Check] = []
    for name in expected:
        if name not in themes:
            checks.append(failed("1", "missing-resource", f"no theme named {name} under {target}"))
            continue
        path, theme = themes[name]
        errors = sorted(validator.iter_errors(theme), key=lambda e: list(e.absolute_path))
        if errors:
            where = "/".join(str(part) for part in errors[0].absolute_path) or "(root)"
            detail = f"{path.name} fails the installed theme schema at {where}: {errors[0].message}"
            checks.append(failed("1", "schema", detail))
        else:
            checks.append(
                passed("1", f"theme {name}", f"{path.name} validates against {THEME_SCHEMA}")
            )
    return checks


@dataclass(frozen=True)
class ProjectLayer:
    """A project mcp.json loads on top of the user-level file; `user_config` is that file's text."""

    user_config: str | None


def original_mcp_checks(
    config: Any,
    target: Path,
    ws: Workspace,
    install_root: Path,
    project: ProjectLayer | None = None,
) -> tuple[list[Check], list[dict[str, Any]]]:
    """Load the original entries with Pi's own config loader, without starting any server.

    Returns the artifact's errors as checks and the servers the loader kept from it.
    """
    servers = config.get("mcpServers") if isinstance(config, dict) else None
    if not isinstance(servers, dict):
        detail = f"{target} must be a JSON object with an mcpServers object (docs/mcp.md)"
        return [failed("1", "mcp-config", detail)], []
    root = ws.root / "mcp-validation"
    root.mkdir(exist_ok=True)
    payload = {
        "config": config,
        "scope": "project" if project else "user",
        "base": project.user_config if project else None,
    }
    try:
        validation = subprocess.run(
            ["node", str(MCP_VALIDATOR), str(install_root / MCP_VALIDATOR_MODULE), str(root)],
            env=gate_env(ws),
            cwd=ws.work,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [failed("1", "timeout", "installed Pi MCP validator did not finish in time")], []
    except OSError as error:
        detail = (
            f"could not start installed Pi MCP validator: {error}; "
            "see MAINTAINING.md#gate-failure-recovery"
        )
        return [failed("1", "gate-environment", detail)], []
    if validation.returncode:
        detail = f"installed Pi validator failed: {validation.stderr.strip()}; run check_drift.py"
        return [failed("1", "gate-dependency", detail)], []
    try:
        result = require_shape("MCP validation", json.loads(validation.stdout))
    except (json.JSONDecodeError, PiShapeError) as error:
        detail = f"installed Pi validator: {error}; run check_drift.py"
        return [failed("1", "pi-shape", detail)], []
    return [failed("1", "mcp-config", error) for error in result["errors"]], result["servers"]


def _user_mcp_config(real_agent_dir: Path | None) -> str | None:
    """The user-level mcp.json that project overrides merge onto; read only, never written."""
    path = real_agent_dir / "mcp.json" if real_agent_dir else None
    try:
        return path.read_text(encoding="utf-8") if path else None
    except FileNotFoundError:
        return None


def _loaded_mcp_checks(
    expected: list[str], loaded: list[dict[str, Any]], real_agent_dir: Path | None
) -> list[Check]:
    """Project servers as Pi's config loader kept them, overrides merged."""
    by_name = {server["name"]: server for server in loaded}
    return [
        passed(
            "1",
            f"MCP server {name}",
            f"valid override of the user-level server in {real_agent_dir}/mcp.json"
            if by_name[name]["override"]
            else "valid and loaded as a project server by Pi's MCP config loader",
        )
        if name in by_name
        else failed("1", "missing-resource", f"MCP server {name} is not loaded by Pi")
        for name in expected
    ]


def _listed_mcp_checks(expected: list[str], config: dict[str, Any], ws: Workspace) -> list[Check]:
    """List a user-level copy with every server disabled, so nothing connects."""
    for server in config["mcpServers"].values():
        if isinstance(server, dict):
            server["enabled"] = False
    (ws.agent / "mcp.json").write_text(json.dumps(config), encoding="utf-8")
    try:
        result = subprocess.run(
            [*ws.pi, "mcp", "list", "--json"],
            env=gate_env(ws),
            cwd=ws.work,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [failed("1", "timeout", "pi mcp list did not finish in time")]
    try:
        listing = require_shape("pi mcp list", json.loads(result.stdout))
    except json.JSONDecodeError:
        return [failed("1", "load-error", f"pi mcp list gave no JSON: {result.stderr.strip()}")]
    except PiShapeError as error:
        return [failed("1", "pi-shape", f"{error}; this Pi's output changed shape")]
    checks = [failed("1", "mcp-config", error) for error in listing["errors"]]
    names = {server["name"] for server in listing["servers"]}
    checks += [
        passed("1", f"MCP server {name}", "valid and listed by pi mcp list")
        if name in names
        else failed("1", "missing-resource", f"MCP server {name} is not listed by pi mcp list")
        for name in expected
    ]
    return checks


def mcp_config_checks(expected: list[str], ws: Workspace, run: Staged, scope: str) -> list[Check]:
    """Validate original entries, then list the servers without starting any.

    `pi mcp list` reads a project file only once Pi's trust store trusts the project, so project
    files are listed from Pi's config loader, which also merges their overrides.
    """
    try:
        config = json.loads(run.loaded.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [failed("1", "load-error", f"{run.loaded} is not valid JSON: {error}")]
    project = ProjectLayer(_user_mcp_config(run.real_agent_dir)) if scope == "project" else None
    checks, loaded = original_mcp_checks(config, run.loaded, ws, run.install_root, project)
    if checks:
        return checks
    if project:
        return _loaded_mcp_checks(expected, loaded, run.real_agent_dir)
    return _listed_mcp_checks(expected, config, ws)


# Orchestration


@dataclass(frozen=True)
class GateOptions:
    real_agent_dir: Path
    tier: int | None = None  # None: Tier 2 when gate.json has a tier2 block, else Tier 1
    approve: bool = True  # False only for the self-test's trust-skipped control


@dataclass(frozen=True)
class Staged:
    loaded: Path  # where Pi loads the artifact from (a copy for project scope)
    cwd: Path
    tier: int
    approve: bool
    install_root: Path
    real_agent_dir: Path | None = None  # read only, for the user-level mcp.json


def gate(artifact: Path, gate_path: Path, install: Any, options: GateOptions) -> list[Check]:
    """Run every check gate.json asks for; artifact problems become FAIL checks."""
    try:
        data = load_gate(gate_path)
    except GateError as error:
        return [failed("-", error.code, str(error))]
    tier = options.tier or (TIER_2 if data.get("tier2") else TIER_1)
    before = snapshot(options.real_agent_dir)
    with tempfile.TemporaryDirectory(prefix="pi-gate-") as tmp:
        ws = Workspace.create(Path(tmp), pi_command(install.root))
        try:
            loaded, cwd = stage(artifact.absolute(), data.get("scope", "temporary"), ws)
        except GateError as error:
            return [failed("-", error.code, str(error))]
        run = Staged(loaded, cwd, tier, options.approve, install.root, options.real_agent_dir)
        checks = _run_checks(data, ws, run)
    if not any(check.status in ("PASS", "FAIL") for check in checks):
        detail = f"no check ran: gate.json's expect declares nothing a {data['kind']} gate checks"
        checks.append(failed("-", "nothing-checked", detail))
    changes = snapshot_diff(before, snapshot(options.real_agent_dir))
    if changes:
        # Kept strict (R3.2.0): the gate cannot tell its own leak from another writer, so it
        # fails either way and says which is the likely cause.
        detail = (
            f"{options.real_agent_dir} changed during the gate run: {'; '.join(changes)}. "
            "If another Pi process was running (a session finishing a turn, a token refresh), "
            "close it and rerun the gate; otherwise the artifact or the gate wrote there."
        )
        checks.append(failed("-", "agent-dir-changed", detail))
    return checks + unchecked_items(data, tier)


def _run_checks(data: dict[str, Any], ws: Workspace, run: Staged) -> list[Check]:
    expect = data.get("expect") or {}
    kind = data["kind"]
    if kind == "theme":
        return theme_checks(_names(expect.get("themes", [])), run.loaded, run.install_root)
    if kind == "mcp-config":
        return mcp_config_checks(
            _names(expect.get("mcpServers", [])), ws, run, data.get("scope", "temporary")
        )
    args = pi_args(data, run.loaded, approve=run.approve)
    obs = observe(data, args, ws, run.cwd, tier=run.tier)
    checks = tier1_checks(data, obs, run.loaded) + tier2_checks(data, obs)
    checks += behavior_coverage(data, obs, run.loaded)
    if expect.get("flags") and not obs.load_error and not obs.timed_out:
        checks += flag_checks(_names(expect["flags"]), args, ws, run.cwd)
    if expect.get("themes"):
        checks += theme_checks(_names(expect["themes"]), run.loaded, run.install_root)
    return checks


# Self-test (R3.12)


@dataclass(frozen=True)
class SelfTestCase:
    name: str
    artifact: str  # relative to self-test/, or "<hello>" for Pi's bundled hello.ts
    gate: str
    expected: str | None  # the failure code a negative case must produce; None must pass
    approve: bool = True
    also: tuple[str, ...] = ()  # other failure codes the control is known to produce


SELF_TEST_CASES = (
    SelfTestCase("bundled hello.ts passes", "<hello>", "hello.gate.json", None),
    SelfTestCase("tool whose execute() throws", "throws.ts", "throws.gate.json", "tool-result"),
    SelfTestCase("misspelled tool name", "<hello>", "misspelled.gate.json", "missing-resource"),
    SelfTestCase("empty gate.json", "<hello>", "empty.gate.json", "empty-gate"),
    SelfTestCase(
        "target not loaded",
        "inert.ts",
        "inert.gate.json",
        "target-not-loaded",
        also=("missing-resource",),
    ),
    SelfTestCase(
        "project artifact without --approve",
        "project/.pi/prompts/trust-probe.md",
        "trust-probe.gate.json",
        "missing-resource",
        approve=False,
        also=("target-not-loaded",),
    ),
    SelfTestCase(
        "faux provider not answering",
        "not-faux.ts",
        "not-faux.gate.json",
        "wrong-provider",
        also=("provider-error", "wrong-model"),
    ),
    SelfTestCase(
        "invalid MCP enabled value", "invalid-mcp.json", "invalid-mcp.gate.json", "mcp-config"
    ),
)


def case_passes(case: SelfTestCase, codes: list[str]) -> bool:
    """A control passes only with its own code and the codes it is known to add, nothing else."""
    if case.expected is None:
        return not codes
    return case.expected in codes and set(codes) <= {case.expected, *case.also}


def self_test(install: Any, real_agent_dir: Path) -> tuple[bool, list[str]]:
    lines: list[str] = []
    ok = True
    hello = install.root / "examples" / "extensions" / "hello.ts"
    for case in SELF_TEST_CASES:
        artifact = hello if case.artifact == "<hello>" else SELF_TEST_DIR / case.artifact
        options = GateOptions(real_agent_dir, approve=case.approve)
        checks = gate(artifact, SELF_TEST_DIR / case.gate, install, options)
        codes = sorted({check.code for check in checks if check.status == "FAIL"})
        good = case_passes(case, codes)
        ok = ok and good
        want = "pass" if case.expected is None else f"fail with {case.expected}"
        status = "PASS" if good else "FAIL"
        lines.append(f"{status} self-test {case.name}: must {want}; got {codes or 'pass'}")
    return ok, lines


# Report and CLI


def report(artifact: Path, version: str, checks: list[Check]) -> tuple[bool, list[str]]:
    failures = [check for check in checks if check.status == "FAIL"]
    lines = [f"pi-gate {artifact} (Pi {version})"]
    lines += [f"{c.status:<9} [tier {c.tier}] {c.name}: {c.detail}" for c in checks]
    lines.append(
        "NOTE      isolation limits what Pi reads and writes; the artifact's own code ran with "
        "your permissions and was not sandboxed (docs/security.md)"
    )
    counts = {
        status: sum(c.status == status for c in checks) for status in ("PASS", "FAIL", "UNCHECKED")
    }
    verdict = "FAIL" if failures else "PASS"
    lines.append(
        f"RESULT    {verdict}: {counts['FAIL']} failed, {counts['PASS']} passed, "
        f"{counts['UNCHECKED']} unchecked. A pass covers only the checks listed as PASS."
    )
    return not failures, lines


def _find_install() -> Any:
    try:
        return pi_docs.find_installs(os.environ.get("PATH"), Path.cwd())[0]
    except pi_docs.NoInstallError as error:
        print(error, file=sys.stderr)
        print("pi-gate cannot run without Pi; report build work as not verified.", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pi-gate", description=(__doc__ or "").splitlines()[0])
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--gate", type=Path, help="gate file (default: next to the artifact)")
    parser.add_argument("--tier", type=int, choices=(TIER_1, TIER_2))
    parser.add_argument("--self-test", action="store_true", help="run the gate's own controls")
    parser.add_argument("--json", action="store_true", help="print the checks as JSON")
    default_real = Path(os.environ.get("PI_CODING_AGENT_DIR") or Path.home() / ".pi" / "agent")
    parser.add_argument("--real-agent-dir", type=Path, default=default_real, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not args.self_test and args.artifact is None:
        parser.error("give an artifact path or --self-test")
    install = _find_install()
    if install is None:
        return EXIT_NO_INSTALL
    if args.self_test:
        ok, lines = self_test(install, args.real_agent_dir)
        print("\n".join(lines))
        print(f"RESULT    self-test {'PASS' if ok else 'FAIL'} (Pi {install.version})")
        return EXIT_PASS if ok else EXIT_FAIL
    gate_path = args.gate or default_gate_path(args.artifact)
    checks = gate(args.artifact, gate_path, install, GateOptions(args.real_agent_dir, args.tier))
    ok, lines = report(args.artifact, install.version, checks)
    if args.json:
        payload = {"ok": ok, "piVersion": install.version, "checks": [asdict(c) for c in checks]}
        print(json.dumps(payload, indent=2))
    else:
        print("\n".join(lines))
    return EXIT_PASS if ok else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
