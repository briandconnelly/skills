"""Executable tests for check_prereg.py (issue #76) — run with:

    uv run --with pytest pytest hypothesis-driven-analysis/tests/test_check_prereg.py -v

check_prereg.py is the instrument behind the skill's central promise: predictions
written before cause/outcome data is inspected. Before #76 it was verified only by
manual `uv run ...` commands — a procedure that never executes verifies nothing
(the repo's own principle).

#76: a pre-write (or same-timestamp) Bash row that reads the fixture *inside* an
executed script (`python analysis.py`) never names the fixture on its command
line, so the data-pattern scan could not see it and dropped it from the
mandatory-classification list — a fail-open that produced a false CLEAN. These
tests pin the fix: `looks_like_script_execution` (the conservative detector) and
`report_ordering` listing such rows under CLASSIFY / SAME-BATCH, while the
existing direct-data-match and true-negative behavior is unchanged (the known
positive/negative controls the suite's discipline requires).

We load the module by path with importlib (as test_score_ledger.py does) so no
sys.path mutation is needed; check_prereg imports only the standard library.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("check_prereg", HERE / "check_prereg.py")
assert _spec is not None
assert _spec.loader is not None
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)


DATA = re.compile(r"data\.csv")


def row(ordinal: int, tool: str, target: str, *, status: str = "ok", ts: str = "T0") -> cp.Row:
    return cp.Row(ordinal, ts, tool, status, target)


# --------------------------------------------------------------------------- #
# looks_like_script_execution — the conservative detector
# --------------------------------------------------------------------------- #
SCRIPT_POSITIVES = [
    "python analysis.py",
    "python3 analysis.py",
    "python3.12 analysis.py",
    "uv run analysis.py",
    "uv run python analysis.py",
    "uvx ruff check",
    "bash run.sh",
    "sh ./run.sh",
    "./analysis.py",
    "scripts/run.sh --flag",
    "/usr/bin/python /tmp/a.py",
    "env python s.py",
    "PYTHONPATH=. python s.py",
    "time python s.py",
    "cat data.csv | python summarize.py",  # data.csv named, but detector fires on `python` too
    "source setup.sh",
    ". ./env.sh",
    "Rscript model.R",
    "node app.js",
    "perl x.pl",
    "(cd d && python y.py)",
    "cd d\\npython y.py",  # flattened newline (extract_evidence._flatten)
    # option-bearing wrappers — the wrapped interpreter sits behind wrapper
    # options/option-args (Codex review of the #76 branch)
    "env -i python analysis.py",
    "env -u TOKEN python analysis.py",
    "sudo -- python analysis.py",
    "nice -n 5 python analysis.py",
    "time -p python analysis.py",
    # analysis runtimes beyond the python/node core (Codex review)
    "ipython analysis.py",
    "julia analysis.jl",
    "R -f analysis.R",
    "lua analysis.lua",
    # resource/timing prefixes and control-flow heads (Fable review)
    "timeout 60 python analysis.py",
    "stdbuf -o0 python analysis.py",
    "watch -n1 python a.py",
    "if python analysis.py; then echo ok; fi",
    "if python check.py\\nthen echo ok\\nfi",  # flattened compound command
    "while python poll.py; do :; done",
    # quoted env-assignment values (split() fragments the quote — Fable review)
    'GREETING="hello world" python analysis.py',
    "FOO='a b' python analysis.py",
    # notebook runners — canonical hidden-data path (Fable review)
    "papermill analysis.ipynb out.ipynb",
    "jupyter nbconvert --execute analysis.ipynb",
    # uv global flags before `run` (Fable review)
    "uv --directory sub run analysis.py",
    # legacy backtick command substitution (Fable review)
    "echo `python get_stats.py`",
]

SCRIPT_NEGATIVES = [
    "ls -la",
    "git status",
    "head -5 data.csv",
    "wc -l data.csv",
    "cat data.csv",
    "echo python",
    "grep python README.md",
    "cat > analysis.py",  # creating the script, not running it
    "chmod +x analysis.py",
    "rm old.py",
    "mkdir scripts",
    "sudo -v",  # a wrapper with no wrapped command must not fire
    "env",
    # documented heuristic gaps — pinned False so a future extension is a
    # conscious change, not an accident (Fable review)
    "make test",
    "npm run build",
    "if [ -f x ]; then echo hi; fi",  # control-flow head, but no interpreter
    "",
]


@pytest.mark.parametrize("cmd", SCRIPT_POSITIVES)
def test_detector_positives(cmd: str) -> None:
    assert cp.looks_like_script_execution(cmd) is True, cmd


@pytest.mark.parametrize("cmd", SCRIPT_NEGATIVES)
def test_detector_negatives(cmd: str) -> None:
    assert cp.looks_like_script_execution(cmd) is False, cmd


# --------------------------------------------------------------------------- #
# report_ordering — pre-write CLASSIFY listing (#76 core)
# --------------------------------------------------------------------------- #
def test_prewrite_hidden_script_is_listed(capsys: pytest.CaptureFixture[str]) -> None:
    """The #76 known positive: a script whose fixture access is invisible on the
    command line must still be listed for classification (not a silent CLEAN)."""
    rows = [
        row(1, "Bash", "python analysis.py"),  # reads data.csv internally; not named
        row(2, "Write", "report/ledger.md"),
    ]
    ledger = rows[1]
    code = cp.report_ordering(rows, ledger, DATA)
    out = capsys.readouterr().out
    assert code == 1
    assert "ordinal 1" in out
    assert "CLEAN" not in out
    assert cp.SCRIPT_EXEC_NOTE in out  # the row must carry the script-exec note, not just appear


def test_prewrite_data_match_takes_precedence_over_script_note(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """classification_note precedence: a command that both names the fixture AND
    runs a script is listed plainly (direct match), not with the script note."""
    rows = [
        row(1, "Bash", "python analysis.py data.csv"),  # names data.csv AND runs a script
        row(2, "Write", "report/ledger.md"),
    ]
    code = cp.report_ordering(rows, rows[1], DATA)
    out = capsys.readouterr().out
    assert code == 1
    assert "ordinal 1" in out
    assert cp.SCRIPT_EXEC_NOTE not in out


def test_prewrite_direct_data_match_still_listed(capsys: pytest.CaptureFixture[str]) -> None:
    """Control: the pre-existing direct data-pattern match path is unchanged."""
    rows = [
        row(1, "Bash", "head -5 data.csv"),
        row(2, "Write", "report/ledger.md"),
    ]
    code = cp.report_ordering(rows, rows[1], DATA)
    out = capsys.readouterr().out
    assert code == 1
    assert "ordinal 1" in out


def test_prewrite_irrelevant_bash_stays_clean(capsys: pytest.CaptureFixture[str]) -> None:
    """Negative control: a non-script, non-data Bash row must NOT be over-listed."""
    rows = [
        row(1, "Bash", "ls -la"),
        row(2, "Write", "report/ledger.md"),
    ]
    code = cp.report_ordering(rows, rows[1], DATA)
    out = capsys.readouterr().out
    assert code == 0
    assert "CLEAN" in out


# --------------------------------------------------------------------------- #
# report_ordering — SAME-BATCH listing (the twin blindness Codex flagged)
# --------------------------------------------------------------------------- #
def test_same_batch_hidden_script_is_listed(capsys: pytest.CaptureFixture[str]) -> None:
    """A post-write script sharing the ledger write's timestamp cannot be proven
    to have run after preregistration; it must appear under SAME-BATCH."""
    rows = [
        row(1, "Write", "report/ledger.md", ts="T5"),
        row(2, "Bash", "python analysis.py", ts="T5"),
    ]
    code = cp.report_ordering(rows, rows[0], DATA)
    out = capsys.readouterr().out
    assert code == 1
    assert "SAME-BATCH" in out
    assert "ordinal 2" in out
    assert cp.SCRIPT_EXEC_NOTE in out  # SAME-BATCH lines carry the note too (parity with CLASSIFY)
