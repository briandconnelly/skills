from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from _scripts import load_script

check_drift = load_script("check_drift")


def _skill(tmp_path, body, name="SKILL.md"):
    skill = tmp_path / "skill"
    (skill / "references").mkdir(parents=True, exist_ok=True)
    (skill / name).write_text(body)
    return skill


def _run(skill, pi_install, tmp_path, capsys):
    bin_dir, _ = pi_install
    code = check_drift.main(
        ["--skill-dir", str(skill), "--stages", "citations"], path_env=str(bin_dir), cwd=tmp_path
    )
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_resolving_citations_pass(pi_install, tmp_path, capsys):
    skill = _skill(
        tmp_path,
        "See docs/quickstart.md#choose-how-to-customize-pi "
        "and docs/extensions.md#error-handling.\n",
    )
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_PASS
    assert "PASS citations: 2 checked against Pi 0.99.1, 0 broken" in out


def test_trailing_sentence_punctuation_is_not_part_of_the_anchor(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "Start at docs/quickstart.md#choose-how-to-customize-pi.\n")
    code, _, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_PASS


def test_broken_anchor_fails_with_reason(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "Line one\nSee docs/quickstart.md#choose-how-to-customise-pi\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "FAIL SKILL.md:2 docs/quickstart.md#choose-how-to-customise-pi" in out
    assert "no heading or <a id> 'choose-how-to-customise-pi' in docs/quickstart.md" in out


def test_missing_page_fails_with_reason(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/gone.md for details.\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "docs/gone.md does not exist in Pi 0.99.1" in out


def test_reference_files_are_scanned(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/cli.md\n")
    (skill / "references" / "choosing-a-surface.md").write_text("See docs/mcp.md#exposure\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "FAIL references/choosing-a-surface.md:1 docs/mcp.md#exposure" in out


def test_no_citations_fails_rather_than_passing_vacuously(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "No citations here.\n")
    code, _, err = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "nothing was checked" in err


def test_no_install_exits_2(tmp_path, capsys):
    empty = tmp_path / "bin"
    empty.mkdir()
    skill = _skill(tmp_path, "See docs/cli.md\n")
    code = check_drift.main(["--skill-dir", str(skill)], path_env=str(empty), cwd=tmp_path)
    assert code == check_drift.EXIT_NO_INSTALL
    assert "No Pi install found" in capsys.readouterr().err


# Review 3 (Codex, job c9f53a7b) findings, each pinned before its fix.


def test_valid_anchor_prefix_with_extra_fragment_text_fails(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/quickstart.md#choose-how-to-customize-pi%2Dmissing\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "'choose-how-to-customize-pi%2Dmissing'" in out


def test_page_name_case_must_match_exactly(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/cli.md and DOCS/QUICKSTART.md\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert (
        "FAIL SKILL.md:1 DOCS/QUICKSTART.md: DOCS/QUICKSTART.md does not exist in Pi 0.99.1" in out
    )


def test_hosted_page_link_fails_and_points_at_installed_docs(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/cli.md and https://pi.dev/docs/latest/quickstart\n")
    code, out, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_FAIL
    assert "FAIL SKILL.md:1 https://pi.dev/docs/latest/quickstart" in out
    assert "cite the installed docs/<page>.md instead" in out


def test_bare_hosted_docs_root_is_allowed(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "Fallback: https://pi.dev/docs/latest. See docs/cli.md.\n")
    code, _, _ = _run(skill, pi_install, tmp_path, capsys)
    assert code == check_drift.EXIT_PASS


# Gate dependencies, gate, and changelog stages (R8.3, R8.4)


def _dependency_tree(tmp_path, *, hoisted=False):
    """A minimal install whose files mention every gate dependency, laid out like Homebrew's."""
    root = tmp_path / "node_modules" / "@earendil-works" / "pi-coding-agent"
    deps = check_drift.pi_gate.GATE_DEPENDENCIES
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "cli.md").write_text("\n".join(deps["cli_docs"]) + "\n")
    (root / "docs" / "environment-variables.md").write_text(" ".join(deps["env"]) + "\n")
    headings = "".join(f"### {name}\n\n" for name in deps["rpc_commands"])
    (root / "docs" / "rpc-commands.md").write_text(headings)
    (root / "docs" / "json.md").write_text(" ".join(deps["events"]) + "\n")
    types = root / "dist" / "core" / "extensions" / "types.d.ts"
    types.parent.mkdir(parents=True)
    types.write_text(" ".join(f"{name}()" for name in deps["extension_api"]) + "\n")
    pi_ai = (root.parent if hoisted else root / "node_modules" / "@earendil-works") / "pi-ai"
    faux = pi_ai / check_drift.FAUX_DTS
    faux.parent.mkdir(parents=True)
    faux.write_text(" ".join(deps["faux_exports"]) + "\n")
    for name in deps["files"]:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text("{}")
    return root, "\n".join(f"  {flag} <x>" for flag in deps["cli_flags"])


@pytest.mark.parametrize("hoisted", [False, True])
def test_dependencies_pass_when_every_interface_exists(tmp_path, hoisted):
    root, help_text = _dependency_tree(tmp_path, hoisted=hoisted)
    checked, problems = check_drift.check_dependencies(root, "0.99.1", help_text)
    assert problems == []
    assert checked == sum(len(names) for names in check_drift.pi_gate.GATE_DEPENDENCIES.values())


def test_missing_flag_fails_with_its_reason(tmp_path):
    root, help_text = _dependency_tree(tmp_path)
    help_text = help_text.replace("--approve", "--approval")
    _, problems = check_drift.check_dependencies(root, "0.99.1", help_text)
    assert [p.reason for p in problems] == [
        "gate depends on cli_flags --approve, absent from pi --help (Pi 0.99.1)"
    ]


def test_flag_prefix_does_not_count_as_the_flag(tmp_path):
    root, help_text = _dependency_tree(tmp_path)
    help_text = help_text.replace("  --no-session <x>", "  --no-session-dir <x>")
    _, problems = check_drift.check_dependencies(root, "0.99.1", help_text)
    assert [p.citation for p in problems] == ["--no-session"]


def test_missing_rpc_command_and_source_file_fail(tmp_path):
    root, help_text = _dependency_tree(tmp_path)
    (root / "docs" / "rpc-commands.md").write_text("### prompt\n")
    (root / "docs" / "environment-variables.md").unlink()
    _, problems = check_drift.check_dependencies(root, "0.99.1", help_text)
    reasons = [p.reason for p in problems]
    assert (
        "gate depends on rpc_commands set_model, absent from docs/rpc-commands.md (Pi 0.99.1)"
        in reasons
    )
    assert "docs/environment-variables.md missing from Pi 0.99.1" in reasons


def test_changelog_delta_spans_verified_to_installed(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [0.99.1] - x\n- new a\n\n## [0.99.0] - x\n- new b\n\n"
        "## [0.87.1] - x\n- old\n"
    )
    install = SimpleNamespace(version="0.99.1", changelog=changelog)
    lines = check_drift.changelog_delta(install, "0.87.1")
    assert "## [0.99.0] - x" in lines
    assert "- new a" in lines
    assert "- old" not in lines
    assert check_drift.changelog_delta(install, None) == []


def test_unknown_stage_is_a_usage_error(pi_install, tmp_path):
    bin_dir, _ = pi_install
    with pytest.raises(SystemExit):
        check_drift.main(["--stages", "citations,typo"], path_env=str(bin_dir), cwd=tmp_path)


def test_skipped_stages_are_named(pi_install, tmp_path, capsys):
    skill = _skill(tmp_path, "See docs/cli.md\n")
    _run(skill, pi_install, tmp_path, capsys)
    code = check_drift.main(
        ["--skill-dir", str(skill), "--stages", "citations"],
        path_env=str(pi_install[0]),
        cwd=tmp_path,
    )
    assert code == check_drift.EXIT_PASS
    assert "NOT RUN: dependencies, gate, changelog" in capsys.readouterr().out


def _live():
    if shutil.which("pi") is None:
        pytest.skip("no `pi` on PATH; live drift stages not run")
    return check_drift.pi_docs.find_installs(None, Path.cwd())[0]


def test_live_dependencies_all_exist():
    install = _live()
    _, problems = check_drift.check_dependencies(
        install.root, install.version, check_drift.pi_help(install)
    )
    assert problems == []


def test_live_gate_stage_passes():
    install = _live()
    assert check_drift.check_gate(check_drift.DEFAULT_SKILL_DIR, install) == []


def test_live_gate_stage_reports_a_failing_fixture(tmp_path):
    install = _live()
    fixtures = tmp_path / "skill" / "tests" / "fixtures" / "gate" / "moved"
    fixtures.mkdir(parents=True)
    negative = check_drift.DEFAULT_SKILL_DIR / "tests" / "fixtures" / "gate" / "negative"
    for name in ("broken.ts", "broken.gate.json"):
        shutil.copy(negative / name, fixtures / name)
    failures = check_drift.check_gate(tmp_path / "skill", install)
    assert any("load-error" in failure for failure in failures)


# Codex checkpoint 2 findings (job 423f2a2d), each pinned before its fix


def test_gate_stage_fails_with_no_positive_fixtures(tmp_path, capsys):
    install = _live()
    (tmp_path / "skill").mkdir()
    assert check_drift._stage_gate(tmp_path / "skill", install) is False
    assert "no positive fixtures" in capsys.readouterr().out


def test_dependency_stage_fails_when_nothing_is_checked(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(check_drift.pi_gate, "GATE_DEPENDENCIES", {})
    install = SimpleNamespace(root=tmp_path, version="0.99.1")
    assert check_drift._stage_dependencies(install, "") is False
    assert "nothing was checked" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("recorded", "changelog", "ok"),
    [
        ("0.87.1", "## [0.99.1] - x\n- new\n\n## [0.87.1] - x\n- old\n", True),
        ("0.87.1", None, False),
        ("0.87.1", "no version headings here\n", False),
        ("0.99.1", None, True),
    ],
)
def test_changelog_stage_fails_without_a_reviewable_delta(tmp_path, recorded, changelog, ok):
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "verified-against").write_text(f"{recorded}\n")
    path = tmp_path / "CHANGELOG.md"
    if changelog is not None:
        path.write_text(changelog)
    install = SimpleNamespace(version="0.99.1", changelog=path)
    assert check_drift._stage_changelog(skill, install) is ok


# Copilot review (PR #188), pinned before its fix


def test_pi_help_uses_the_selected_install_not_path(tmp_path, monkeypatch):
    install = _live()
    node = shutil.which("node")
    assert node is not None
    node_only = tmp_path / "bin"
    node_only.mkdir()
    (node_only / "node").symlink_to(node)
    monkeypatch.setenv("PATH", str(node_only))
    _, problems = check_drift.check_dependencies(
        install.root, install.version, check_drift.pi_help(install)
    )
    assert problems == []
