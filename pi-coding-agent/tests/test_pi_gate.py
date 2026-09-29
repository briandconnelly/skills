from __future__ import annotations

import pytest
from _scripts import load_script

pi_gate = load_script("pi_gate")


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
