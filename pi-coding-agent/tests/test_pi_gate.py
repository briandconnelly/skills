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
        ('{"kind": "extension", "tier2": {"prompts": [null]}}', "bad-gate"),
        ('{"kind": "extension", "tier2": {"prompts": "hi"}}', "bad-gate"),
        (
            '{"kind": "extension", "expect": {"tools": ["t"]}, "teir2": {"prompts": ["hi"]}}',
            "bad-gate",
        ),
        ('{"kind": "extension", "expect": {"tools": true}}', "bad-gate"),
        ('{"kind": "extension", "expect": {"tools": [1]}}', "bad-gate"),
        ('{"kind": "extension", "tier2": {"prompts": ["hi"], "stpes": []}}', "bad-gate"),
        (
            '{"kind": "extension", "tier2": {"prompts": ["hi"], "steps": [{"txt": "a"}]}}',
            "bad-gate",
        ),
        ('{"kind": "extension", "tier2": {"prompts": ["hi"], "steps": ["a"]}}', "bad-gate"),
        ('{"kind": "extension", "tier2": {"prompts": ["hi"], "expect": {"tool": []}}}', "bad-gate"),
        ('{"kind": "extension", "tier2": {"prompts": ["hi"], "model": 3}}', "bad-gate"),
        (
            '{"kind": "extension", "tier2": {"prompts": ["hi"], "providers": [{"provider": "p"}]}}',
            "bad-gate",
        ),
        (
            '{"kind": "extension", "tier2": {"prompts": ["hi"], "expect": {"events": [{}]}}}',
            "bad-gate",
        ),
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
    ("project/.pi/mcp.json", {"MCP server project-docs"}),
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


# Self-test and review-focus inputs


def test_self_test_passes_and_covers_every_control(tmp_path):
    install = _install()
    ok, lines = pi_gate.self_test(install, tmp_path)
    assert ok, lines
    assert len(lines) == len(pi_gate.SELF_TEST_CASES)
    assert {case.expected for case in pi_gate.SELF_TEST_CASES} == {
        None,
        "tool-result",
        "missing-resource",
        "empty-gate",
        "target-not-loaded",
        "wrong-provider",
        "mcp-config",
    }


POSITIVE_REVIEW = [
    ("review/dialog.ts", {"event message_end"}),
    ("review/dir-ext", {"tool word_count"}),
    ("review/two-lines.ts", {"tool result two_lines"}),
    ("review/quoted-skill", {"transcript"}),
]


@pytest.mark.parametrize(("artifact", "must_pass"), POSITIVE_REVIEW)
def test_review_fixture_passes(tmp_path, artifact, must_pass):
    checks = _run(tmp_path, artifact)
    assert _fails(checks) == [], [c for c in checks if c.status == "FAIL"]
    assert must_pass <= {check.name for check in checks if check.status == "PASS"}


def test_dialog_is_answered_and_reported_unchecked(tmp_path):
    assert "dialog confirm" in _unchecked(_run(tmp_path, "review/dialog.ts"))


def test_symlinked_path_with_a_space_keeps_provenance(tmp_path):
    install = _install()
    real_dir = tmp_path / "with space"
    real_dir.mkdir()
    for name in ("word-count.ts", "word-count.gate.json"):
        shutil.copy(GATE_FIXTURES / "tool" / name, real_dir / name)
    link = tmp_path / "link"
    link.symlink_to(real_dir)
    artifact = link / "word-count.ts"
    checks = pi_gate.gate(
        artifact,
        pi_gate.default_gate_path(artifact),
        install,
        pi_gate.GateOptions(tmp_path / "real"),
    )
    assert _fails(checks) == []


POSITIVE = POSITIVE_RPC + POSITIVE_STATIC + POSITIVE_REVIEW


def test_every_positive_fixture_is_listed_once():
    """check_drift.py runs every gate file outside negative/; keep these lists in step with it."""
    found = {
        pi_gate.artifact_for_gate(gate).relative_to(GATE_FIXTURES).as_posix()
        for gate in GATE_FIXTURES.rglob("*gate.json")
        if "negative" not in gate.relative_to(GATE_FIXTURES).parts
    }
    assert found == {artifact for artifact, _ in POSITIVE}


# Codex checkpoint 1 findings (job 216e3992), each pinned before its fix


@pytest.mark.parametrize(
    ("artifact", "gate", "code"),
    [
        ("command/note.ts", "negative/no-assertion.gate.json", "tier2-empty"),
        ("negative/flaky.ts", "negative/flaky-reuse.gate.json", "tool-result"),
        ("negative/flaky.ts", "negative/flaky-unexpected.gate.json", "tool-result"),
    ],
)
def test_checkpoint_1_negative_fails_with_its_reason(tmp_path, artifact, gate, code):
    assert code in _fails(_run(tmp_path, artifact, gate))


def test_no_model_turn_is_not_reported_as_a_pass(tmp_path):
    checks = _run(tmp_path, "command/note.ts")
    assert "physical models" not in {check.name for check in checks if check.status == "PASS"}


def test_rejected_prompt_fails(tmp_path):
    install = _install()
    artifact = GATE_FIXTURES / "tool" / "word-count.ts"
    data = {"kind": "extension", "expect": {"tools": ["word_count"]}, "tier2": {"prompts": [None]}}
    (tmp_path / "ws").mkdir()
    ws = pi_gate.Workspace.create(tmp_path / "ws")
    run = pi_gate.Staged(artifact, ws.work, pi_gate.TIER_2, True, install.root)
    codes = {check.code for check in pi_gate._run_checks(data, ws, run) if check.status == "FAIL"}
    assert "prompt-rejected" in codes


def test_unattributed_models_do_not_show_the_target_loaded(tmp_path):
    obs = pi_gate.Observation(
        inventory={"tools": [], "activeTools": [], "mcpServers": []},
        models=[{"provider": "someone-else", "id": "m"}],
    )
    data = {"kind": "extension", "expect": {"models": ["someone-else/m"]}}
    checks = pi_gate._provenance_sweep(data, obs, tmp_path / "artifact.ts")
    assert [(check.status, check.name) for check in checks] == [("UNCHECKED", "target loaded")]


@pytest.mark.parametrize(
    ("codes", "good"),
    [
        (["target-not-loaded"], True),
        (["missing-resource", "target-not-loaded"], True),
        (["target-not-loaded", "timeout"], False),
        (["missing-resource"], False),
    ],
)
def test_self_test_control_rejects_unrelated_failures(codes, good):
    case = next(c for c in pi_gate.SELF_TEST_CASES if c.expected == "target-not-loaded")
    assert pi_gate.case_passes(case, codes) is good


# Final review findings (fresh reviewer and Codex job 4402bbb7), each pinned before its fix


def test_gate_env_blocks_every_route_to_a_paid_provider(tmp_path, monkeypatch):
    for name in ("ANTHROPIC_OAUTH_TOKEN", "AWS_ACCESS_KEY_ID", "GOOGLE_APPLICATION_CREDENTIALS"):
        monkeypatch.setenv(name, "secret")
    monkeypatch.setenv("NO_PROXY", "*")
    (tmp_path / "ws").mkdir()
    ws = pi_gate.Workspace.create(tmp_path / "ws")
    env = pi_gate.gate_env(ws)
    assert not {
        "ANTHROPIC_OAUTH_TOKEN",
        "AWS_ACCESS_KEY_ID",
        "GOOGLE_APPLICATION_CREDENTIALS",
    } & set(env)
    assert "NO_PROXY" not in env
    assert env["HTTPS_PROXY"] == env["HTTP_PROXY"] == pi_gate.DEAD_PROXY
    assert env["AWS_SHARED_CREDENTIALS_FILE"].startswith(str(ws.root))


@pytest.mark.parametrize(
    ("gate", "code"),
    [
        ("negative/unscripted-model.gate.json", "unscripted-model"),
        ("negative/declared-real-model.gate.json", None),
    ],
)
def test_a_real_provider_is_never_reached(tmp_path, monkeypatch, gate, code):
    monkeypatch.setenv("ANTHROPIC_OAUTH_TOKEN", "sk-ant-oat-fake-gate-test")
    checks = _run(tmp_path, "tool/word-count.ts", gate)
    details = " ".join(check.detail for check in checks)
    assert "401" not in details
    assert "authentication_error" not in details
    assert _fails(checks)
    if code:
        assert code in _fails(checks)


def test_structural_json_text_does_not_satisfy_contains(tmp_path):
    codes = _fails(_run(tmp_path, "tool/word-count.ts", "negative/structural-contains.gate.json"))
    assert "tool-result" in codes


def test_a_gate_that_checks_nothing_fails(tmp_path):
    codes = _fails(_run(tmp_path, "theme/gate-theme.json", "negative/theme-no-themes.gate.json"))
    assert "nothing-checked" in codes


def test_a_hanging_extension_times_out_with_a_report(tmp_path, monkeypatch):
    monkeypatch.setattr(pi_gate, "DEFAULT_TIMEOUT", 3.0)
    assert "timeout" in _fails(_run(tmp_path, "negative/hang.ts"))


def test_a_project_local_install_without_pi_on_path_is_gated(tmp_path, monkeypatch, capsys):
    install = _install()
    project = tmp_path / "project"
    local = project / "node_modules" / "@earendil-works"
    local.mkdir(parents=True)
    (local / "pi-coding-agent").symlink_to(install.root)
    node_only = tmp_path / "bin"
    node_only.mkdir()
    node = shutil.which("node")
    assert node is not None
    (node_only / "node").symlink_to(node)
    monkeypatch.setenv("PATH", str(node_only))
    monkeypatch.chdir(project)
    artifact = GATE_FIXTURES / "tool" / "word-count.ts"
    code = pi_gate.main([str(artifact), "--real-agent-dir", str(tmp_path / "real")])
    assert code == pi_gate.EXIT_PASS, capsys.readouterr().out


def test_every_gate_fixture_and_recipe_passes_strict_validation():
    for gate in list(GATE_FIXTURES.rglob("*gate.json")) + list(
        pi_gate.SELF_TEST_DIR.glob("*gate.json")
    ):
        if gate.name in {"empty.gate.json"}:
            continue
        pi_gate.load_gate(gate)


# Codex critical review after Copilot round 1 (job 0ff2c949), pinned before its fix


@pytest.mark.parametrize(
    ("artifact", "gate", "code"),
    [
        ("negative/inert.ts", "negative/harness-model.gate.json", "provenance"),
        ("skill/gate-skill", "negative/transcript-echo.gate.json", "transcript"),
    ],
)
def test_gate_supplied_content_does_not_count_for_the_artifact(tmp_path, artifact, gate, code):
    checks = _run(tmp_path, artifact, gate)
    assert code in _fails(checks)


# Copilot review round 2 (PR #188), pinned before its fix


def test_malformed_mcp_config_fails_without_a_traceback(tmp_path):
    assert "mcp-config" in _fails(_run(tmp_path, "negative/mcp-list.json"))


# Deferred minors (M2 to M4), designed with Codex (job fe89ee9d), pinned before each fix


def _project_prompt(root):
    source = GATE_FIXTURES / "project" / ".pi" / "prompts"
    shutil.copytree(source, root, dirs_exist_ok=True)


def test_symlinked_pi_directory_is_gated(tmp_path):
    install = _install()
    _project_prompt(tmp_path / "real-pi" / "prompts")
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / ".pi").symlink_to(tmp_path / "real-pi")
    artifact = tmp_path / "project" / ".pi" / "prompts" / "project-prompt.md"
    options = pi_gate.GateOptions(tmp_path / "real-agent")
    checks = pi_gate.gate(artifact, pi_gate.default_gate_path(artifact), install, options)
    assert _fails(checks) == []


def test_symlinked_parent_above_pi_directory_is_gated(tmp_path):
    install = _install()
    _project_prompt(tmp_path / "elsewhere" / ".pi" / "prompts")
    (tmp_path / "link").symlink_to(tmp_path / "elsewhere")
    artifact = tmp_path / "link" / ".pi" / "prompts" / "project-prompt.md"
    options = pi_gate.GateOptions(tmp_path / "real-agent")
    checks = pi_gate.gate(artifact, pi_gate.default_gate_path(artifact), install, options)
    assert _fails(checks) == []


def test_dot_dot_out_of_pi_directory_is_not_project_scoped(tmp_path):
    (tmp_path / "ws").mkdir()
    ws = pi_gate.Workspace.create(tmp_path / "ws")
    (tmp_path / "project" / ".pi").mkdir(parents=True)
    (tmp_path / "project" / "outside.md").write_text("x")
    artifact = tmp_path / "project" / ".pi" / ".." / "outside.md"
    with pytest.raises(pi_gate.GateError) as caught:
        pi_gate.stage(artifact.absolute(), "project", ws)
    assert caught.value.code == "bad-gate"


def test_a_concurrent_write_still_fails_and_says_why(tmp_path, monkeypatch):
    install = _install()
    real = tmp_path / "real-agent"
    (real / "sessions").mkdir(parents=True)
    original = pi_gate._run_checks

    def run_then_write(*args):
        checks = original(*args)
        (real / "sessions" / "other-pi-session.jsonl").write_text("{}")
        return checks

    monkeypatch.setattr(pi_gate, "_run_checks", run_then_write)
    artifact = GATE_FIXTURES / "tool" / "word-count.ts"
    checks = pi_gate.gate(
        artifact, pi_gate.default_gate_path(artifact), install, pi_gate.GateOptions(real)
    )
    changed = [check for check in checks if check.code == "agent-dir-changed"]
    assert len(changed) == 1
    assert "sessions/other-pi-session.jsonl" in changed[0].detail
    assert "another Pi process" in changed[0].detail


def test_pi_shape_errors_name_the_offending_path():
    with pytest.raises(pi_gate.PiShapeError) as caught:
        pi_gate.require_shape("get_commands", {"data": {"commands": [{"source": "prompt"}]}})
    assert "data/commands/0" in str(caught.value)
    assert "name" in str(caught.value)


@pytest.mark.parametrize(
    ("command_type", "reply"),
    [
        ("get_commands", {"data": {"commands": [{"nope": 1}]}}),
        ("prompt", {"data": {}}),
        (
            "get_commands",
            {"data": {"commands": [{"name": "x", "source": "prompt", "sourceInfo": "bad"}]}},
        ),
    ],
)
def test_malformed_rpc_reply_fails_as_pi_shape_and_closes_pi(
    tmp_path, monkeypatch, command_type, reply
):
    original_request = pi_gate.RpcSession.request
    original_close = pi_gate.RpcSession.close
    closed = []

    def request(self, command):
        response = original_request(self, command)
        if command["type"] == command_type and response is not None:
            return {**response, **reply}
        return response

    def close(self):
        closed.append(True)
        return original_close(self)

    monkeypatch.setattr(pi_gate.RpcSession, "request", request)
    monkeypatch.setattr(pi_gate.RpcSession, "close", close)
    checks = _run(tmp_path, "tool/word-count.ts")
    assert "pi-shape" in _fails(checks)
    assert closed == [True]


def test_malformed_mcp_list_output_fails_as_pi_shape(tmp_path, monkeypatch):
    real_run = pi_gate.subprocess.run

    def run(command, **kwargs):
        if "mcp" in command:
            return pi_gate.subprocess.CompletedProcess(command, 0, '{"servers": {}}', "")
        return real_run(command, **kwargs)

    monkeypatch.setattr(pi_gate.subprocess, "run", run)
    assert "pi-shape" in _fails(_run(tmp_path, "mcp-config/mcp.json"))


# Codex review of the M2 to M4 diff (job d2a12940), pinned before each fix


def test_symlink_then_dot_dot_gates_the_file_the_os_opens(tmp_path):
    install = _install()
    (tmp_path / "other" / "dir").mkdir(parents=True)
    for name in ("word-count.ts", "word-count.gate.json"):
        shutil.copy(GATE_FIXTURES / "tool" / name, tmp_path / "other" / name)
    shutil.copy(GATE_FIXTURES / "negative" / "broken.ts", tmp_path / "word-count.ts")
    (tmp_path / "link").symlink_to(tmp_path / "other" / "dir")
    artifact = tmp_path / "link" / ".." / "word-count.ts"
    options = pi_gate.GateOptions(tmp_path / "real-agent")
    checks = pi_gate.gate(artifact, pi_gate.default_gate_path(artifact), install, options)
    assert _fails(checks) == []


@pytest.mark.parametrize(
    "error",
    [
        json.JSONDecodeError("Expecting value", "", 0),
        PermissionError("inventory unreadable"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
    ],
)
def test_unreadable_inventory_fails_as_pi_shape(tmp_path, monkeypatch, error):
    def broken(_path):
        raise error

    monkeypatch.setattr(pi_gate, "_read_json", broken)
    assert "pi-shape" in _fails(_run(tmp_path, "tool/word-count.ts"))


# Copilot review on PR #189, pinned before each fix


def test_malformed_set_model_reply_fails_as_pi_shape(tmp_path, monkeypatch):
    original_request = pi_gate.RpcSession.request

    def request(self, command):
        response = original_request(self, command)
        if command["type"] == "set_model" and response is not None:
            return {**response, "success": "yes"}
        return response

    monkeypatch.setattr(pi_gate.RpcSession, "request", request)
    assert "pi-shape" in _fails(_run(tmp_path, "virtual-model/router.ts"))


@pytest.mark.parametrize("line", [b"[]\n", b"null\n", b'"text"\n'])
def test_non_object_rpc_record_is_a_pi_shape_error(line):
    session = pi_gate.RpcSession.__new__(pi_gate.RpcSession)
    session._buffer = line
    with pytest.raises(pi_gate.PiShapeError):
        session._buffered()


# Critical review: validate original configs and report missing behavior assertions.


@pytest.mark.parametrize("enabled", ["false", 0, None, [], {}])
def test_mcp_enabled_is_validated_before_disabling_servers(tmp_path, enabled):
    artifact = tmp_path / "mcp.json"
    config = {"mcpServers": {"docs": {"url": "https://example.com/mcp", "enabled": enabled}}}
    artifact.write_text(json.dumps(config))
    gate = tmp_path / "mcp.gate.json"
    gate.write_text(json.dumps({"kind": "mcp-config", "expect": {"mcpServers": ["docs"]}}))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert "mcp-config" in _fails(checks)
    assert any("enabled must be a boolean" in check.detail for check in checks)
    assert json.loads(artifact.read_text()) == config


@pytest.mark.parametrize("enabled", [True, False, "absent"])
def test_valid_mcp_configs_are_checked_without_starting_servers(tmp_path, enabled):
    marker = tmp_path / "server-started"
    server = {
        "command": "node",
        "args": ["-e", f"require('node:fs').writeFileSync({json.dumps(str(marker))}, 'started')"],
    }
    if enabled != "absent":
        server["enabled"] = enabled
    artifact = tmp_path / "mcp.json"
    config = {"mcpServers": {"docs": server}}
    artifact.write_text(json.dumps(config))
    gate = tmp_path / "mcp.gate.json"
    gate.write_text(json.dumps({"kind": "mcp-config", "expect": {"mcpServers": ["docs"]}}))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert _fails(checks) == []
    assert not marker.exists()
    assert json.loads(artifact.read_text()) == config


def _broken_word_count(tmp_path, *, result_expect=None, calls=1):
    artifact = tmp_path / "word-count.ts"
    source = (GATE_FIXTURES / "tool/word-count.ts").read_text()
    artifact.write_text(
        source.replace(
            "const words = params.text.split(/\\s+/).filter(Boolean).length;", "const words = 999;"
        )
    )
    data = json.loads((GATE_FIXTURES / "tool/word-count.gate.json").read_text())
    tier2 = data["tier2"]
    call, reply = tier2["steps"]
    tier2["steps"] = [call] * calls + [reply]
    tier2.pop("expect")
    if result_expect is not None:
        tier2["expect"] = {"toolResults": result_expect}
    gate = tmp_path / "word-count.gate.json"
    gate.write_text(json.dumps(data))
    return pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))


def test_wrong_tool_output_without_an_assertion_is_reported_unchecked(tmp_path):
    checks = _broken_word_count(tmp_path)
    assert _fails(checks) == []
    assert "unasserted tool call word_count #1" in _unchecked(checks)
    assert not any(
        check.status == "PASS" and check.name == "tool result word_count" for check in checks
    )


def test_wrong_tool_output_with_an_assertion_fails(tmp_path):
    checks = _broken_word_count(
        tmp_path, result_expect=[{"toolName": "word_count", "contains": "3 words"}]
    )
    assert "tool-result" in _fails(checks)


def test_error_status_assertion_leaves_tool_result_content_unchecked(tmp_path):
    checks = _broken_word_count(
        tmp_path, result_expect=[{"toolName": "word_count", "isError": False}]
    )
    assert _fails(checks) == []
    assert "tool result content word_count" in _unchecked(checks)


def test_one_result_assertion_does_not_cover_two_calls(tmp_path):
    checks = _broken_word_count(
        tmp_path, result_expect=[{"toolName": "word_count", "contains": "999 words"}], calls=2
    )
    assert _fails(checks) == []
    assert "unasserted tool call word_count #2" in _unchecked(checks)
    assert any(
        check.status == "PASS" and check.name == "tool result word_count" for check in checks
    )


def test_package_prompt_does_not_cover_other_registered_resources(tmp_path):
    checks = _run(tmp_path, "package/team-kit")
    assert _fails(checks) == []
    assert {"tool behavior word_count", "skill behavior skill:kit-skill"} <= _unchecked(checks)
    assert "prompt behavior kit-prompt" not in _unchecked(checks)


def test_load_only_tool_is_reported_as_unexercised(tmp_path):
    install = _install()
    artifact = GATE_FIXTURES / "tool/word-count.ts"
    checks = pi_gate.gate(
        artifact,
        pi_gate.default_gate_path(artifact),
        install,
        pi_gate.GateOptions(tmp_path / "real", tier=pi_gate.TIER_1),
    )
    assert _fails(checks) == []
    assert "tool behavior word_count" in _unchecked(checks)


def test_prompt_without_transcript_assertion_is_reported_unchecked(tmp_path):
    artifact = GATE_FIXTURES / "prompt/gate-prompt.md"
    data = json.loads(pi_gate.default_gate_path(artifact).read_text())
    del data["tier2"]["steps"][0]["expectTranscript"]
    gate = tmp_path / "prompt.gate.json"
    gate.write_text(json.dumps(data))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert _fails(checks) == []
    assert "prompt expansion gate-prompt" in _unchecked(checks)


def test_hook_smoke_turn_without_assertions_is_reported_unchecked(tmp_path):
    artifact = GATE_FIXTURES / "hook/system-marker.ts"
    data = json.loads(pi_gate.default_gate_path(artifact).read_text())
    del data["tier2"]["steps"][0]["expectTranscript"]
    gate = tmp_path / "hook.gate.json"
    gate.write_text(json.dumps(data))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert _fails(checks) == []
    assert "Tier 2 behavior" in _unchecked(checks)


def test_empty_expectation_lists_do_not_cover_command_behavior(tmp_path):
    artifact = GATE_FIXTURES / "command/note.ts"
    data = json.loads(pi_gate.default_gate_path(artifact).read_text())
    data["tier2"]["expect"] = {"events": [], "toolResults": []}
    gate = tmp_path / "command.gate.json"
    gate.write_text(json.dumps(data))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert "command behavior note" in _unchecked(checks)
    assert "Tier 2 behavior" in _unchecked(checks)


@pytest.mark.parametrize(
    ("mode", "code"),
    [
        ("missing-node", "gate-environment"),
        ("blocked-node", "gate-environment"),
        ("failed-import", "gate-dependency"),
        ("timeout", "timeout"),
        ("malformed-output", "pi-shape"),
    ],
)
def test_mcp_validator_infrastructure_failures_are_not_artifact_errors(
    tmp_path, monkeypatch, mode, code
):
    install = _install()
    (tmp_path / "ws").mkdir()
    ws = pi_gate.Workspace.create(tmp_path / "ws")

    def run(command, **_kwargs):
        if mode == "missing-node":
            raise FileNotFoundError("node")
        if mode == "blocked-node":
            raise PermissionError("node")
        if mode == "timeout":
            raise pi_gate.subprocess.TimeoutExpired(command, 1)
        if mode == "failed-import":
            return pi_gate.subprocess.CompletedProcess(command, 1, "", "ERR_MODULE_NOT_FOUND")
        return pi_gate.subprocess.CompletedProcess(command, 0, '[{"error":"changed contract"}]', "")

    monkeypatch.setattr(pi_gate.subprocess, "run", run)
    checks, servers = pi_gate.original_mcp_checks(
        {"mcpServers": {"docs": {"url": "https://example.com/mcp"}}},
        tmp_path / "mcp.json",
        ws,
        install.root,
    )
    assert _fails(checks) == [code]
    assert servers == []


def test_self_test_detects_validator_drift_that_accepts_invalid_enabled(tmp_path, monkeypatch):
    install = _install()
    real_run = pi_gate.subprocess.run

    def run(command, **kwargs):
        if str(pi_gate.MCP_VALIDATOR) in command:
            output = '{"errors": [], "servers": [{"name": "docs", "override": false}]}'
            return pi_gate.subprocess.CompletedProcess(command, 0, output, "")
        return real_run(command, **kwargs)

    monkeypatch.setattr(pi_gate.subprocess, "run", run)
    ok, lines = pi_gate.self_test(install, tmp_path / "real")
    assert not ok
    assert any(line.startswith("FAIL self-test invalid MCP enabled value") for line in lines)


def test_explicit_model_sequence_counts_as_router_behavior_assertion(tmp_path):
    checks = _run(tmp_path, "virtual-model/router.ts")
    assert _fails(checks) == []
    assert "Tier 2 behavior" not in _unchecked(checks)


# Pi 1.0.1: project mcp.json files load on top of the user-level file, with their own rules.


def _project_mcp(tmp_path, servers, *, user=None):
    """Gate a project .pi/mcp.json; `user` is the real user-level mcp.json, if any."""
    real = tmp_path / "real-agent"
    real.mkdir()
    if user is not None:
        (real / "mcp.json").write_text(json.dumps({"mcpServers": user}))
    pi_dir = tmp_path / "repo" / ".pi"
    pi_dir.mkdir(parents=True)
    artifact = pi_dir / "mcp.json"
    artifact.write_text(json.dumps({"mcpServers": servers}))
    gate = pi_dir / "mcp.gate.json"
    names = list(servers)
    gate.write_text(
        json.dumps({"kind": "mcp-config", "scope": "project", "expect": {"mcpServers": names}})
    )
    before = (real / "mcp.json").read_text() if user is not None else None
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(real))
    after = (real / "mcp.json").read_text() if user is not None else None
    assert before == after
    return checks


USER_DOCS = {"docs": {"url": "https://example.com/mcp", "headers": {"X-Team": "a"}}}


@pytest.mark.parametrize(
    "override", [{"enabled": False}, {"exposure": "direct"}, {"toolExposure": {"*": "hidden"}}]
)
def test_project_override_of_a_user_level_server_passes(tmp_path, override):
    checks = _project_mcp(tmp_path, {"docs": override}, user=USER_DOCS)
    assert _fails(checks) == [], [c for c in checks if c.status == "FAIL"]
    assert any("valid override" in c.detail for c in checks if c.status == "PASS")


@pytest.mark.parametrize(
    ("servers", "user", "message"),
    [
        ({"docs": {"enabled": False}}, None, "a global server to override"),
        ({"docs": {"enabled": "no"}}, USER_DOCS, "enabled must be a boolean"),
        ({"docs": {"enabled": False, "headers": {}}}, USER_DOCS, "an override can only set"),
        (
            {"gh": {"url": "https://example.com/mcp", "auth": {"provider": "anthropic"}}},
            None,
            "auth is only allowed in the global mcp.json",
        ),
    ],
)
def test_project_mcp_rules_fail(tmp_path, servers, user, message):
    checks = _project_mcp(tmp_path, servers, user=user)
    assert "mcp-config" in _fails(checks)
    assert any(message in check.detail for check in checks if check.status == "FAIL")


def test_override_entry_in_a_user_level_file_fails(tmp_path):
    artifact = tmp_path / "mcp.json"
    artifact.write_text(json.dumps({"mcpServers": {"docs": {"enabled": False}}}))
    gate = tmp_path / "mcp.gate.json"
    gate.write_text(json.dumps({"kind": "mcp-config", "expect": {"mcpServers": ["docs"]}}))
    checks = pi_gate.gate(artifact, gate, _install(), pi_gate.GateOptions(tmp_path / "real"))
    assert "mcp-config" in _fails(checks)
