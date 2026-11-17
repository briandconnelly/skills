"""Adversarial cases for check_fences.py: each bad input must be reported."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_fences", Path(__file__).with_name("check_fences.py")
)
check_fences = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_fences)


def _problems(tmp_path: Path, text: str) -> list[str]:
    doc = tmp_path / "doc.md"
    doc.write_text(text)
    return check_fences.check_file(doc)


def test_clean_document_has_no_problems(tmp_path):
    (tmp_path / "other.md").write_text("x\n")
    text = (
        "See [other](other.md#anchor) and [web](https://example.com).\n"
        '```json\n{"a": 1}\n```\n'
        '```ndjson\n{"a": 1}\n\n{"b": 2}\n```\n'
    )
    assert _problems(tmp_path, text) == []


def test_json_trailing_comma_is_reported_with_its_line(tmp_path):
    problems = _problems(tmp_path, 'intro\n```json\n{"a": 1,}\n```\n')
    assert len(problems) == 1
    assert problems[0].startswith(f"{tmp_path / 'doc.md'}:2: ")


def test_bad_ndjson_line_is_reported(tmp_path):
    problems = _problems(tmp_path, '```ndjson\n{"a": 1}\n{oops}\n```\n')
    assert len(problems) == 1
    assert ":3: " in problems[0]


def test_missing_link_target_is_reported(tmp_path):
    problems = _problems(tmp_path, "See [gone](nope.md).\n")
    assert len(problems) == 1
    assert "nope.md" in problems[0]


def test_link_inside_a_fence_is_not_checked(tmp_path):
    assert _problems(tmp_path, "```text\n[gone](nope.md)\n```\n") == []


def test_indented_and_blockquoted_fences_are_parsed(tmp_path):
    text = '  ```json\n  {"a": 1,}\n  ```\n> ```json\n> {"b": 2,}\n> ```\n'
    lines = [problem.split(":")[1] for problem in _problems(tmp_path, text)]
    assert lines == ["1", "4"]


def test_tilde_fences_are_parsed_and_shield_links(tmp_path):
    problems = _problems(tmp_path, '~~~json\n{"a": 1,}\n~~~\n~~~text\n[gone](nope.md)\n~~~\n')
    assert [problem.split(":")[1] for problem in problems] == ["1"]


def test_fence_closes_only_on_its_own_character(tmp_path):
    text = "~~~~text\n```json\n{bad}\n```\n[gone](nope.md)\n~~~~\n"
    assert _problems(tmp_path, text) == []


def test_nonstandard_json_constants_are_rejected(tmp_path):
    text = '```json\n{"v": NaN}\n```\n```ndjson\n{"v": Infinity}\n```\n'
    assert [problem.split(":")[1] for problem in _problems(tmp_path, text)] == ["1", "5"]


def test_unclosed_fence_is_reported(tmp_path):
    problems = _problems(tmp_path, '```json\n{"a": 1}\n')
    assert len(problems) == 1
    assert "unclosed" in problems[0]


def test_main_exit_codes(tmp_path):
    good = tmp_path / "good.md"
    good.write_text('```json\n{"a": 1}\n```\n')
    bad = tmp_path / "bad.md"
    bad.write_text('```json\n{"a": 1,}\n```\n')
    assert check_fences.main([str(good)]) == 0
    assert check_fences.main([str(good), str(bad)]) == 1
