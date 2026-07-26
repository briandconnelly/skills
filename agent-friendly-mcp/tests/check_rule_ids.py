#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Enforce the contract-checklist rule-id convention.

`contract-checklist.md` is the single home for this skill's normative rules
(AGENTS.md: "A normative rule has exactly one home"). Every rule carries a
stable id of the form `[section.slug]`, and other files cite ids rather than
paraphrasing the rule text.

Checks:

  * every rule bullet in contract-checklist.md declares an id;
  * ids are unique;
  * an id's section prefix matches the section it appears in;
  * every id cited anywhere in the skill resolves to a declared rule.

The last check is the one that earns its keep: a citation that stops resolving
is a rule that was removed or renamed, which should fail loudly instead of
rotting into a stale paraphrase.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CHECKLIST = SKILL_DIR / "references" / "contract-checklist.md"

# `- `[3.naming]` **Rule lead.** body`  (possibly indented for nested bullets)
RULE_RE = re.compile(r"^(\s*)- (?:`\[(?P<id>[^\]]+)\]` )?\*\*")
SECTION_RE = re.compile(r"^## (\d+)\.")
# Any `[N.slug]` in backticks, anywhere.
CITE_RE = re.compile(r"`\[(\d+\.[a-z0-9-]+)\]`")


def declared_ids(text: str) -> tuple[dict[str, int], list[str]]:
    """Return declared ids -> line number, plus problems found while reading."""
    ids: dict[str, int] = {}
    problems: list[str] = []
    section: str | None = None
    for lineno, line in enumerate(text.split("\n"), 1):
        if m := SECTION_RE.match(line):
            section = m.group(1)
            continue
        m = RULE_RE.match(line)
        if not m:
            continue
        rule_id = m.group("id")
        if rule_id is None:
            lead = line.strip()[:60]
            problems.append(f"{CHECKLIST.name}:{lineno}: rule has no id: {lead}")
            continue
        if rule_id in ids:
            problems.append(
                f"{CHECKLIST.name}:{lineno}: duplicate id '{rule_id}' "
                f"(first declared at line {ids[rule_id]})"
            )
            continue
        prefix = rule_id.split(".", 1)[0]
        if section is not None and prefix != section:
            problems.append(
                f"{CHECKLIST.name}:{lineno}: id '{rule_id}' declares section "
                f"{prefix} but appears in section {section}"
            )
        ids[rule_id] = lineno
    return ids, problems


def unresolved_citations(ids: dict[str, int]) -> list[str]:
    problems: list[str] = []
    for path in sorted(SKILL_DIR.rglob("*.md")):
        if any(part in {".pytest_cache", "runs"} for part in path.parts):
            continue
        rel = path.relative_to(SKILL_DIR)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if path == CHECKLIST and RULE_RE.match(line):
                continue  # the declaration itself
            for cited in CITE_RE.findall(line):
                if cited not in ids:
                    problems.append(f"{rel}:{lineno}: cites unknown rule id '{cited}'")
    return problems


def main() -> int:
    if not CHECKLIST.is_file():
        print(f"missing {CHECKLIST}", file=sys.stderr)
        return 2
    ids, problems = declared_ids(CHECKLIST.read_text(encoding="utf-8"))
    if not ids:
        print("no rule ids found — the convention is not in place", file=sys.stderr)
        return 2
    problems += unresolved_citations(ids)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"{len(ids)} rule ids declared; all citations resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
