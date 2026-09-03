#!/usr/bin/env python3
"""Verify scenario 9R's skill catalog reproduces shipped frontmatter verbatim.

Scenario 9 was retired because it measured a hand-written catalog line no agent
would ever see. 9R exists to fix that, and its claim to be built "from the
shipped descriptions" is only as good as the last time somebody checked. A
2026-08-24 cross-review found the `agent-friendly-github` entry had silently
lost its instruction-file-strategy clause -- the exact vocabulary that makes it
a competing candidate for an "audit my AGENTS.md" prompt, so its absence biased
the selection test toward this skill.

Exit 0 if every entry is verbatim, 1 otherwise.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCENARIOS = REPO / "separating-context-from-constraints" / "tests" / "scenarios.md"

SKILLS = [
    "agent-friendly-cli",
    "agent-friendly-docs",
    "agent-friendly-github",
    "agent-friendly-mcp",
    "separating-context-from-constraints",
]


def normalize(text: str) -> str:
    return " ".join(text.split())


def shipped_description(skill: str) -> str:
    frontmatter = (REPO / skill / "SKILL.md").read_text()
    match = re.search(r"^description:\s*(.+?)\n(?=[a-z-]+:|---)", frontmatter, re.S | re.M)
    if match is None:
        sys.exit(f"could not read a description from {skill}/SKILL.md")
    return normalize(match.group(1))


def catalog_entries(text: str) -> dict[str, str]:
    block = re.search(r"## Scenario 9R:.*?(?=\n## )", text, re.S)
    if block is None:
        sys.exit("scenario 9R section not found in scenarios.md")
    entries = {}
    for skill in SKILLS:
        match = re.search(rf"^> - `{re.escape(skill)}`: (.+)$", block.group(0), re.M)
        if match is not None:
            entries[skill] = normalize(match.group(1))
    return entries


def main() -> int:
    entries = catalog_entries(SCENARIOS.read_text())
    drifted = []
    for skill in SKILLS:
        if skill not in entries:
            drifted.append(f"{skill}: missing from the 9R catalog")
            continue
        shipped = shipped_description(skill)
        if entries[skill] != shipped:
            drifted.append(f"{skill}: catalog text differs from shipped frontmatter")

    if drifted:
        print("scenario 9R catalog is NOT verbatim:")
        for line in drifted:
            print(f"  - {line}")
        print("\nRegenerate the catalog from the shipped descriptions before running 9R.")
        return 1

    print(f"scenario 9R catalog is verbatim for all {len(SKILLS)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
