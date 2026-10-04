from __future__ import annotations

import json

import pytest
from _scripts import load_script

drift_report = load_script("drift_report")

OUTPUT = "PASS citations: 18 checked\nREVIEW changelog: 1.0.1 -> 1.0.2, 12 lines\n"
LINKS = "Run: https://example.invalid/run"


def _decide(installed="1.0.2", verified="1.0.1", exit_code=0, issues=(), output=OUTPUT):
    run = drift_report.DriftRun(installed, verified, exit_code, output)
    return drift_report.decide(run, list(issues), LINKS)


def _issue(number, version, status="update review owed"):
    return {"number": number, "title": f"pi-coding-agent: Pi {version} — {status}"}


def test_verified_and_passing_closes_open_issues():
    plan = _decide(installed="1.0.1", issues=[_issue(7, "1.0.1")])
    assert [(op.kind, op.number) for op in plan.ops] == [("close", 7)]
    assert "verified" in plan.ops[0].body
    assert plan.fail is False


def test_verified_and_passing_with_no_issues_does_nothing():
    plan = _decide(installed="1.0.1")
    assert plan.ops == []
    assert plan.fail is False


def test_new_release_that_passes_opens_a_review_issue_without_failing():
    plan = _decide()
    assert [op.kind for op in plan.ops] == ["create"]
    assert plan.ops[0].title == "pi-coding-agent: Pi 1.0.2 — update review owed"
    assert OUTPUT in plan.ops[0].body
    assert "MAINTAINING.md#update-procedure" in plan.ops[0].body
    assert LINKS in plan.ops[0].body
    assert plan.fail is False


def test_drift_failure_titles_the_issue_and_fails_the_job():
    plan = _decide(exit_code=1)
    assert plan.ops[0].title == "pi-coding-agent: Pi 1.0.2 — drift found"
    assert plan.fail is True


def test_drift_failure_on_the_verified_version_still_opens_an_issue():
    plan = _decide(installed="1.0.1", exit_code=1)
    assert [op.kind for op in plan.ops] == ["create"]
    assert plan.ops[0].title == "pi-coding-agent: Pi 1.0.1 — drift found"
    assert plan.fail is True


def test_existing_issue_for_the_version_is_edited_not_duplicated():
    plan = _decide(exit_code=1, issues=[_issue(9, "1.0.2")])
    assert [(op.kind, op.number) for op in plan.ops] == [("edit", 9)]
    assert plan.ops[0].title.endswith("drift found")


def test_issues_for_other_versions_are_closed_as_superseded():
    plan = _decide(installed="1.0.3", issues=[_issue(9, "1.0.2"), _issue(10, "1.0.3")])
    assert [(op.kind, op.number) for op in plan.ops] == [("edit", 10), ("close", 9)]
    assert "1.0.3" in plan.ops[1].body


def test_version_prefix_does_not_match_a_longer_version():
    plan = _decide(installed="1.0.1", exit_code=1, issues=[_issue(11, "1.0.10")])
    assert [(op.kind, op.number) for op in plan.ops] == [("create", None), ("close", 11)]


def test_long_output_is_truncated_to_fit_an_issue_body():
    plan = _decide(output="x" * 100_000)
    body = plan.ops[0].body
    assert len(body) <= drift_report.MAX_BODY
    assert "truncated" in body


def test_dry_run_prints_the_plan_and_calls_no_gh_write(tmp_path, monkeypatch, capsys):
    output = tmp_path / "drift.txt"
    output.write_text(OUTPUT)
    calls = []

    def run(command, **_kwargs):
        calls.append(command)
        return drift_report.subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr(drift_report.subprocess, "run", run)
    code = drift_report.main(
        [
            "--output", str(output), "--exit-code", "0", "--installed", "1.0.2",
            "--verified", "1.0.1", "--dry-run",
        ]
    )  # fmt: skip
    assert code == 0
    assert all(command[:3] == ["gh", "issue", "list"] for command in calls)
    printed = json.loads(capsys.readouterr().out)
    assert printed["ops"][0]["kind"] == "create"


def test_apply_runs_gh_for_each_operation(tmp_path, monkeypatch):
    output = tmp_path / "drift.txt"
    output.write_text(OUTPUT)
    calls = []
    issues = json.dumps([_issue(9, "1.0.1")])

    def run(command, **_kwargs):
        calls.append(command)
        stdout = issues if command[:3] == ["gh", "issue", "list"] else ""
        return drift_report.subprocess.CompletedProcess(command, 0, stdout, "")

    monkeypatch.setattr(drift_report.subprocess, "run", run)
    code = drift_report.main(
        ["--output", str(output), "--exit-code", "1", "--installed", "1.0.2", "--verified", "1.0.1"]
    )
    assert code == 1
    verbs = [command[1:3] for command in calls]
    assert verbs == [
        ["issue", "list"],
        ["label", "create"],
        ["issue", "create"],
        ["issue", "close"],
    ]
    create = calls[2]
    assert create[create.index("--label") + 1] == drift_report.LABEL


@pytest.mark.parametrize("failing", ["list", "create"])
def test_gh_failure_fails_the_run(tmp_path, monkeypatch, failing):
    output = tmp_path / "drift.txt"
    output.write_text(OUTPUT)

    def run(command, **_kwargs):
        code = 1 if command[2] == failing else 0
        stdout = "[]" if command[2] == "list" else ""
        return drift_report.subprocess.CompletedProcess(command, code, stdout, "boom")

    monkeypatch.setattr(drift_report.subprocess, "run", run)
    code = drift_report.main(
        ["--output", str(output), "--exit-code", "0", "--installed", "1.0.2", "--verified", "1.0.1"]
    )
    assert code == drift_report.EXIT_GH
