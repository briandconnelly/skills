"""EDA's authorization gate must match HDA's verbatim.

decisions/001-shared-gate-authority.md names hypothesis-driven-analysis/SKILL.md
as the single authority for the authorization-gate text; this check keeps the
copy from drifting (AGENTS.md: one home per normative rule).
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HEADING = "### Authorization gate (always binds)"
MIN_GATE_LENGTH = 1000


def gate_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(HEADING)
    rest = text[start + len(HEADING) :]
    nxt = re.search(r"\n#{2,3} ", rest)
    end = start + len(HEADING) + (nxt.start() if nxt else len(rest))
    return text[start:end].strip()


def test_gate_block_extracts_real_content():
    """The instrument can surface a known positive, so an empty match cannot pass."""
    hda = gate_block(REPO / "hypothesis-driven-analysis" / "SKILL.md")
    assert "None of the following is authorization" in hda
    assert len(hda) > MIN_GATE_LENGTH


def test_authorization_gate_matches_hda_verbatim():
    hda = gate_block(REPO / "hypothesis-driven-analysis" / "SKILL.md")
    eda = gate_block(REPO / "exploratory-data-analysis" / "SKILL.md")
    assert eda == hda
