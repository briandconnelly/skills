"""Tests for validate_fixture.validate — run with:
uv run --with pytest --with jsonschema pytest agent-friendly-mcp/tests/test_validate_fixture.py -v
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from validate_fixture import validate  # noqa: E402

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "github_issues.json").read_text()
)


def test_conforming_fixture_has_no_issues():
    assert validate(copy.deepcopy(FIXTURE)) == []


def test_success_structuredcontent_must_match_output_schema():
    bad = copy.deepcopy(FIXTURE)
    bad["wire"]["success_result"]["structuredContent"]["state"] = "reopened"
    issues = validate(bad)
    assert any("output_schema" in i.where for i in issues)


def test_error_result_must_set_iserror_true():
    bad = copy.deepcopy(FIXTURE)
    bad["wire"]["error_result"]["isError"] = False
    issues = validate(bad)
    assert any("isError" in i.message for i in issues)


def test_error_envelope_must_live_in_structuredcontent():
    bad = copy.deepcopy(FIXTURE)
    del bad["wire"]["error_result"]["structuredContent"]
    issues = validate(bad)
    assert any("structuredContent" in i.message for i in issues)


def test_error_envelope_must_match_error_schema():
    bad = copy.deepcopy(FIXTURE)
    del bad["wire"]["error_result"]["structuredContent"]["temporary"]
    issues = validate(bad)
    assert any("error_schema" in i.where for i in issues)


def test_disclosed_degraded_text_carrier_is_accepted():
    ok = copy.deepcopy(FIXTURE)
    err = ok["wire"]["error_result"]
    envelope = err.pop("structuredContent")
    err["content"] = [{"type": "text", "text": json.dumps(envelope)}]
    ok["wire"]["degraded_text_carrier"] = True
    assert validate(ok) == []
