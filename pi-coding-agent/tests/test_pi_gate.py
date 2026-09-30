from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from _scripts import load_script

pi_gate = load_script("pi_gate")

GATE_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "gate"


# gate.json validation (R3.6, R3.7)


def _gate_file(tmp_path, body):
    path = tmp_path / "x.gate.json"
    path.write_text(body)
    return path


@pytest.mark.parametrize(
    ("body", "code"),
    [
        ("", "empty-gate"),
        ("{}", "empty-gate"),
        ('{"kind": "extension"}', "empty-gate"),
        ('{"kind": "extension", "expect": {"tools": []}}', "empty-gate"),
        ('{"kind": "widget", "expect": {"tools": ["t"]}}', "bad-gate"),
        ('{"kind": "extension", "expect": {"tool": ["t"]}}', "bad-gate"),
        ('{"kind": "extension", "scope": "user", "expect": {"tools": ["t"]}}', "bad-gate"),
        ('{"kind": "extension", "expect": ["tools"]}', "bad-gate"),
        ('{"kind": "extension", "tier2": ["hi"]}', "bad-gate"),
        ("[1]", "bad-gate"),
        ("{not json", "bad-gate"),
    ],
)
def test_invalid_gate_files_are_rejected_with_their_reason(tmp_path, body, code):
    with pytest.raises(pi_gate.GateError) as caught:
        pi_gate.load_gate(_gate_file(tmp_path, body))
    assert caught.value.code == code


def test_missing_gate_file_names_the_expected_path(tmp_path):
    with pytest.raises(pi_gate.GateError) as caught:
        pi_gate.load_gate(tmp_path / "absent.gate.json")
    assert caught.value.code == "no-gate"
    assert "absent.gate.json" in str(caught.value)


def test_tier2_prompts_alone_count_as_a_declaration(tmp_path):
    data = pi_gate.load_gate(
        _gate_file(tmp_path, '{"kind": "extension", "tier2": {"prompts": ["hi"]}}')
    )
    assert data["kind"] == "extension"


def test_default_gate_path_sits_next_to_the_artifact(tmp_path):
    (tmp_path / "pkg").mkdir()
    assert pi_gate.default_gate_path(tmp_path / "pkg") == tmp_path / "pkg" / "gate.json"
    assert pi_gate.default_gate_path(tmp_path / "tool.ts") == tmp_path / "tool.gate.json"


def test_artifact_for_gate_finds_the_one_sibling(tmp_path):
    (tmp_path / "tool.ts").write_text("")
    (tmp_path / "pkg").mkdir()
    assert pi_gate.artifact_for_gate(tmp_path / "tool.gate.json") == tmp_path / "tool.ts"
    assert pi_gate.artifact_for_gate(tmp_path / "pkg" / "gate.json") == tmp_path / "pkg"
    (tmp_path / "tool.js").write_text("")
    with pytest.raises(pi_gate.GateError) as caught:
        pi_gate.artifact_for_gate(tmp_path / "tool.gate.json")
    assert caught.value.code == "bad-gate"


# Real agent directory snapshot (R3.2.0)


def test_snapshot_sees_file_symlink_and_directory_changes(tmp_path):
    root = tmp_path / "agent"
    (root / "sessions").mkdir(parents=True)
    (root / "settings.json").write_text("{}")
    (root / "current").symlink_to("settings.json")
    before = pi_gate.snapshot(root)
    assert pi_gate.snapshot_diff(before, pi_gate.snapshot(root)) == []
    (root / "settings.json").write_text('{"changed": true}')
    (root / "current").unlink()
    (root / "current").symlink_to("sessions")
    (root / "new-dir").mkdir()
    changed = {line.split(":")[0] for line in pi_gate.snapshot_diff(before, pi_gate.snapshot(root))}
    assert changed == {"settings.json", "current", "new-dir"}


def test_snapshot_of_a_missing_directory_is_empty(tmp_path):
    assert pi_gate.snapshot(tmp_path / "absent") == {}


# Isolation, arguments, and provenance


def test_subset_matching():
    event = {"type": "message_end", "message": {"customType": "note", "content": "x"}}
    assert pi_gate.matches({"type": "message_end", "message": {"customType": "note"}}, event)
    assert not pi_gate.matches({"message": {"customType": "other"}}, event)
    assert pi_gate.matches([{"a": 1}], [{"a": 1, "b": 2}, {"c": 3}])
    assert not pi_gate.matches([{"a": 2}], [{"a": 1}])


def test_origin_classes(tmp_path):
    target = tmp_path / "pkg"
    assert pi_gate.origin_of("builtin:read", target) == "builtin"
    assert pi_gate.origin_of(str(pi_gate.HARNESS), target) == "harness"
    assert pi_gate.origin_of(str(target / "extensions" / "a.ts"), target) == "target"
    assert pi_gate.origin_of(str(tmp_path / "pkg-other" / "a.ts"), target) == "other"


def test_project_scope_keeps_its_own_discovery_and_approves(tmp_path):
    data = {"kind": "prompt", "scope": "project", "expect": {"prompts": ["p"]}}
    args = pi_gate.pi_args(data, tmp_path / "p.md", approve=True)
    assert "-np" not in args
    assert {"-ne", "-ns", "--no-themes", "-nc", "--no-session", "--approve"} <= set(args)
    assert "--prompt-template" not in args
    assert "--approve" not in pi_gate.pi_args(data, tmp_path / "p.md", approve=False)


def test_temporary_scope_loads_explicitly_and_adds_builtin_mcp_for_servers(tmp_path):
    data = {"kind": "extension", "expect": {"mcpServers": ["s"]}}
    args = pi_gate.pi_args(data, tmp_path / "e.ts", approve=True)
    assert args[args.index("-e") + 1] == str(tmp_path / "e.ts")
    assert args[-2:] == ["-e", "builtin:mcp"]
    assert args.count("-ne") == 1


def test_gate_env_strips_pi_settings_and_provider_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    monkeypatch.setenv("PI_CODING_AGENT_SESSION_DIR", "/real/sessions")
    monkeypatch.setenv("KEEP_ME", "yes")
    tmp_path.joinpath("ws").mkdir()
    env = pi_gate.gate_env(pi_gate.Workspace.create(tmp_path / "ws"))
    assert "ANTHROPIC_API_KEY" not in env
    assert "PI_CODING_AGENT_SESSION_DIR" not in env
    assert env["KEEP_ME"] == "yes"
    assert env["PI_OFFLINE"] == env["PI_SKIP_VERSION_CHECK"] == "1"
    assert env["PI_CODING_AGENT_DIR"] == str(tmp_path / "ws" / "agent")


# Live runs against the installed Pi: RPC surfaces


def _install():
    if shutil.which("pi") is None:
        pytest.skip("no `pi` on PATH; live gate runs not run")
    return pi_gate.pi_docs.find_installs(None, Path.cwd())[0]


def _run(tmp_path, artifact, gate=None):
    install = _install()
    real = tmp_path / "real-agent"
    real.mkdir(exist_ok=True)
    (real / "settings.json").write_text("{}")
    artifact = GATE_FIXTURES / artifact
    gate_path = GATE_FIXTURES / gate if gate else pi_gate.default_gate_path(artifact)
    return pi_gate.gate(artifact, gate_path, install, pi_gate.GateOptions(real))


def _fails(checks):
    return sorted({check.code for check in checks if check.status == "FAIL"})


def _unchecked(checks):
    return {check.name for check in checks if check.status == "UNCHECKED"}


POSITIVE_RPC = [
    ("tool/word-count.ts", {"tool word_count", "tool result word_count", "script consumed"}),
    ("command/note.ts", {"command note", "event message_end"}),
    ("hook/system-marker.ts", {"transcript"}),
    ("skill/gate-skill", {"skill skill:gate-skill", "transcript"}),
    ("prompt/gate-prompt.md", {"prompt gate-prompt", "transcript"}),
    ("project/.pi/prompts/project-prompt.md", {"prompt project-prompt", "transcript"}),
    ("virtual-model/router.ts", {"model router/auto", "physical models"}),
    ("tui/shortcut.ts", {"load"}),
    ("mcp/register.ts", {"MCP server gate-docs"}),
]


@pytest.mark.parametrize(("artifact", "must_pass"), POSITIVE_RPC)
def test_rpc_surface_fixture_passes(tmp_path, artifact, must_pass):
    checks = _run(tmp_path, artifact)
    assert _fails(checks) == [], [c for c in checks if c.status == "FAIL"]
    assert must_pass <= {check.name for check in checks if check.status == "PASS"}


@pytest.mark.parametrize(
    ("artifact", "unchecked"),
    [
        ("tui/shortcut.ts", {"shortcut ctrl+alt+g", "message renderer gate-status", "Tier 2"}),
        ("mcp/register.ts", {"MCP connection"}),
        ("virtual-model/router.ts", {"model provenance"}),
        ("tool/word-count.ts", {"late registration"}),
    ],
)
def test_report_names_what_rpc_runs_could_not_check(tmp_path, artifact, unchecked):
    assert unchecked <= _unchecked(_run(tmp_path, artifact))


NEGATIVE_RPC = [
    ("negative/broken.ts", None, "load-error"),
    ("negative/start-throws.ts", None, "extension-error"),
    ("tool/word-count.ts", "negative/wrong-exposure.gate.json", "exposure"),
    ("tool/word-count.ts", "negative/unconsumed.gate.json", "unconsumed-steps"),
    ("command/note.ts", "negative/event-mismatch.gate.json", "event-mismatch"),
    ("skill/gate-skill", "negative/transcript-miss.gate.json", "transcript"),
]


@pytest.mark.parametrize(("artifact", "gate", "code"), NEGATIVE_RPC)
def test_rpc_negative_fixture_fails_with_its_reason(tmp_path, artifact, gate, code):
    assert code in _fails(_run(tmp_path, artifact, gate))


def test_tier_1_only_skips_tier_2_and_says_so(tmp_path):
    install = _install()
    artifact = GATE_FIXTURES / "tool" / "word-count.ts"
    options = pi_gate.GateOptions(tmp_path, tier=pi_gate.TIER_1)
    checks = pi_gate.gate(artifact, pi_gate.default_gate_path(artifact), install, options)
    assert not [check for check in checks if check.tier == "2"]
    assert "Tier 2" in _unchecked(checks)


def test_no_install_refuses_and_says_not_verified(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    monkeypatch.chdir(tmp_path)
    assert pi_gate.main([str(tmp_path / "tool.ts")]) == pi_gate.EXIT_NO_INSTALL
    assert "not verified" in capsys.readouterr().err


def test_json_report_is_machine_readable(tmp_path, capsys):
    _install()
    artifact = GATE_FIXTURES / "tool" / "word-count.ts"
    code = pi_gate.main([str(artifact), "--json", "--real-agent-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert code == pi_gate.EXIT_PASS
    assert payload["ok"] is True
    assert {"status", "tier", "name", "detail", "code"} == set(payload["checks"][0])


# Live runs: surfaces checked without an RPC turn


POSITIVE_STATIC = [
    ("flag/verbose.ts", {"flag --gate-verbose"}),
    ("mcp-config/mcp.json", {"MCP server filesystem", "MCP server docs"}),
    ("theme/gate-theme.json", {"theme gate-theme"}),
    (
        "package/team-kit",
        {"tool word_count", "skill skill:kit-skill", "prompt kit-prompt", "theme kit-theme"},
    ),
]


@pytest.mark.parametrize(("artifact", "must_pass"), POSITIVE_STATIC)
def test_static_surface_fixture_passes(tmp_path, artifact, must_pass):
    checks = _run(tmp_path, artifact)
    assert _fails(checks) == [], [c for c in checks if c.status == "FAIL"]
    assert must_pass <= {check.name for check in checks if check.status == "PASS"}


@pytest.mark.parametrize(
    ("artifact", "unchecked"),
    [
        ("flag/verbose.ts", {"flag behavior", "Tier 2"}),
        ("mcp-config/mcp.json", {"MCP connection"}),
        ("theme/gate-theme.json", {"theme"}),
        ("package/team-kit", {"theme"}),
    ],
)
def test_report_names_what_static_checks_could_not_check(tmp_path, artifact, unchecked):
    assert unchecked <= _unchecked(_run(tmp_path, artifact))


@pytest.mark.parametrize(
    ("artifact", "code"),
    [("negative/bad-theme.json", "schema"), ("negative/sse-mcp.json", "mcp-config")],
)
def test_static_negative_fixture_fails_with_its_reason(tmp_path, artifact, code):
    assert code in _fails(_run(tmp_path, artifact))
