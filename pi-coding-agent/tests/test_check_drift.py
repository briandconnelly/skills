from __future__ import annotations

from _scripts import load_script

check_drift = load_script("check_drift")


def _skill(tmp_path, body, name="SKILL.md"):
    skill = tmp_path / "skill"
    (skill / "references").mkdir(parents=True, exist_ok=True)
    (skill / name).write_text(body)
    return skill


def _run(skill, pi_install, tmp_path, capsys):
    bin_dir, _ = pi_install
    code = check_drift.main(["--skill-dir", str(skill)], path_env=str(bin_dir), cwd=tmp_path)
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
