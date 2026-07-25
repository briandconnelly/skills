"""Tests for check-citations.py.

Run: uv run --with pytest pytest scripts/test_check_citations.py

The point of these is the known-positive discipline the skills in this repo
preach: a checker that reports nothing and a checker that cannot report
anything look identical from the outside. Each rule here has a case that must
fail and a case that must pass.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_citations", Path(__file__).parent / "check-citations.py"
)
assert SPEC is not None
assert SPEC.loader is not None
cc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cc)

SENTENCE = "An absent record does not by itself establish the absence of the event."


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A miniature skill tree rooted at tmp_path, with cc pointed at it."""
    (tmp_path / "skill" / "tests" / "runs").mkdir(parents=True)
    (tmp_path / "skill" / "SKILL.md").write_text(f"# Skill\n\n## Analysis\n\n{SENTENCE}\n")
    (tmp_path / "skill" / "tests" / "runs" / "archive.md").write_text("frozen evidence\n")
    monkeypatch.setattr(cc, "REPO_ROOT", tmp_path)
    return tmp_path


def write(repo: Path, text: str) -> Path:
    path = repo / "skill" / "tests" / "scenarios.md"
    path.write_text(text + "\n")
    return path


def test_line_citation_into_live_file_is_flagged(repo):
    violations = cc.check(write(repo, "See SKILL.md line 164 for the rule."))
    assert len(violations) == 1
    assert "line-number citation" in violations[0]


def test_line_citation_colon_form_is_flagged(repo):
    assert cc.check(write(repo, "See SKILL.md:164 for the rule."))


def test_line_citation_into_frozen_archive_is_allowed(repo):
    assert cc.check(write(repo, "Measured in archive.md:253 and :257.")) == []


def test_attributed_quote_that_matches_passes(repo):
    assert cc.check(write(repo, f'SKILL.md\'s "{SENTENCE}" governs this.')) == []


def test_attributed_quote_that_does_not_match_is_flagged(repo):
    stale = "An absent record proves the event did not happen, which is what we assumed."
    violations = cc.check(write(repo, f'SKILL.md\'s "{stale}" governs this.'))
    assert len(violations) == 1
    assert "does not appear there" in violations[0]


def test_unattributed_quote_is_ignored(repo):
    """A filename far from the quote is a mention, not a citation."""
    stale = "An absent record proves the event did not happen, which is what we assumed."
    line = f'The run read SKILL.md and then wrote, in its own words, "{stale}"'
    assert cc.check(write(repo, line)) == []


def test_short_quote_is_ignored(repo):
    assert cc.check(write(repo, 'SKILL.md\'s "not in there" is short.')) == []


def test_quote_matches_across_reflowed_whitespace_and_dashes(repo):
    (repo / "skill" / "SKILL.md").write_text("# Skill\n\nThe rule — stated once —\nspans lines.\n")
    assert cc.check(write(repo, 'SKILL.md\'s "the rule - stated once - spans lines" holds.')) == []


class TestPinnedCitations:
    """A pin is checked against git, not trusted."""

    @pytest.fixture
    def pinned(self, repo):
        run = lambda *a: subprocess.run(  # noqa: E731
            ["git", "-C", str(repo), *a], check=True, capture_output=True, text=True
        )
        run("init", "-q")
        run("config", "user.email", "t@example.com")
        run("config", "user.name", "T")
        run("add", "-A")
        run("commit", "-qm", "initial")
        sha = run("rev-parse", "--short", "HEAD").stdout.strip()
        (repo / "skill" / "SKILL.md").write_text("# Skill\n\nThe rule was rewritten entirely.\n")
        return repo, sha

    def test_quote_stale_in_working_tree_passes_when_pinned(self, pinned):
        repo, sha = pinned
        assert cc.check(write(repo, f'SKILL.md@{sha}\'s "{SENTENCE}" was the wording then.')) == []

    def test_same_quote_without_the_pin_is_flagged(self, pinned):
        """The known positive: the pin is what makes the passing case pass."""
        repo, _ = pinned
        assert cc.check(write(repo, f'SKILL.md\'s "{SENTENCE}" was the wording then.'))

    def test_quote_absent_from_the_pinned_commit_is_flagged(self, pinned):
        repo, sha = pinned
        never = "A sentence that no commit of this file has ever contained anywhere."
        violations = cc.check(write(repo, f'SKILL.md@{sha}\'s "{never}" was the wording.'))
        assert len(violations) == 1
        assert "does not appear there" in violations[0]

    def test_unresolvable_pin_is_flagged_once(self, pinned):
        """One violation, not two.

        A pin git cannot resolve means the quote was never checked; also
        reporting it as absent would describe a comparison that never ran.
        """
        repo, _ = pinned
        violations = cc.check(write(repo, f'SKILL.md@abc1234\'s "{SENTENCE}" was the wording.'))
        assert len(violations) == 1
        assert "git cannot resolve" in violations[0]
