#!/usr/bin/env python3
"""Check cross-file citations in agent-read skill prose.

Two rules, both chosen because they only inspect text an author explicitly
formatted as a citation, so a clean run means something and a flag is rarely
noise:

1. A line-number citation (``SKILL.md line 164``, ``SKILL.md:164``) into a file
   that is still being edited is rejected. Line numbers rot silently: the prose
   keeps reading correctly while pointing at the wrong line, and nothing fails.
   Cite the section, or quote the sentence and let rule 2 hold it. Citations
   into an archived run under ``tests/runs/`` are allowed — those files are
   frozen evidence, so their line numbers do not move.

2. A quoted span of at least MIN_QUOTE characters that is *explicitly
   attributed* to a markdown file must appear in that file. This is the
   replacement for rule 1: a quote is a citation that reports its own staleness.
   Attribution means the filename sits within ATTRIBUTION_WINDOW characters of
   the quote — ``SKILL.md's "…"``, ``SKILL.md — "…"``, ``"…" (SKILL.md)``. A
   file merely mentioned elsewhere on the line is not an attribution: prose
   quotes run output and prompt text beside a filename all the time, and
   checking those would flag ordinary writing.

A dated finding that quotes wording since revised cites the pinned version it
actually read — ``SKILL.md@1cc7bd9`` — and the quote is then checked against
that commit rather than the working tree. This is deliberately not an escape
hatch: a pin is checked, not trusted, so a wrong pin fails like a wrong quote.

Exit non-zero on any violation. Pass files to check as arguments (pre-commit
does this); with no arguments, checks the default scope below.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Where these rules bind. Agent-read skill prose plus the live test catalog:
# files an agent or a maintainer reads as current instruction. Archived runs,
# fixtures, and point-in-time implementation plans under docs/ are excluded --
# they are records of what was true when written, not claims about now.
#
# Widening to the other skills is a follow-up, not an oversight:
# agent-friendly-mcp/tests/scenarios.md carries 7 line-number citations into
# live reference files, and those need converting before the rule can bind
# there without failing on work this check was not part of.
DEFAULT_SCOPE = ("hypothesis-driven-analysis",)
SCOPE_PATTERNS = ("SKILL.md", "references/*.md", "tests/scenarios.md")

# Citations into these directories are frozen and may carry line numbers.
FROZEN_DIRS = ("tests/runs",)

MIN_QUOTE = 40

# How close a filename must sit to a quote to count as attributing it. Sized
# from the real corpus: genuine attributions in this repo run 3-12 characters
# ("SKILL.md's \"…\"", "SKILL.md's purpose (\"…\")"), while the nearest
# incidental mention beside an unrelated quote was 45.
ATTRIBUTION_WINDOW = 24

# "foo.md line 164" or "foo.md:164" (optionally a range), where the ".md" is
# not part of a longer path segment.
LINE_CITATION = re.compile(
    r"(?<![\w/.-])([\w.-]+\.md)(?:\s+lines?\s+|:)(\d+)(?:[-–]\d+)?\b"  # noqa: RUF001
)
MD_MENTION = re.compile(r"(?<![\w/.-])([\w.-]+\.md)(?:@([0-9a-f]{7,40}))?\b")
QUOTED = re.compile(rf'"([^"]{{{MIN_QUOTE},}})"')

# A quote may be reflowed or re-punctuated between the citing prose and the
# source; normalize the differences that carry no meaning. The ambiguous
# characters here are the point of the table, not an accident.
DASHES = {"—": "-", "–": "-", "‒": "-"}  # noqa: RUF001
QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"'}  # noqa: RUF001


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for src, dst in {**DASHES, **QUOTES}.items():
        text = text.replace(src, dst)
    text = text.replace("`", "")
    # Case-folded: a quote lifted from mid-sentence legitimately capitalizes,
    # and that is not the drift this checks for.
    return " ".join(text.split()).casefold()


def shallow() -> bool:
    """Whether this checkout lacks full history.

    A pinned citation is verified with `git show`, so a shallow clone -- the
    default for CI checkouts -- cannot check it. That must fail loudly rather
    than pass quietly: a check that silently stops checking in the environment
    where it matters most is worse than no check.
    """
    return (REPO_ROOT / ".git" / "shallow").exists()


def read_at(path: Path, sha: str | None) -> str:
    """Read a file from the working tree, or from a pinned commit."""
    if sha is None:
        return path.read_text()
    rel = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{sha}:{rel}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FileNotFoundError(f"{rel}@{sha}")
    return result.stdout


def in_frozen(path: Path) -> bool:
    """Whether a cited file lives in a frozen directory, matched on path segments.

    Segment-wise rather than by substring: `docs/nottests/runs/x.md` contains
    the string "tests/runs/" without being under one.
    """
    parts = path.relative_to(REPO_ROOT).parts
    for frozen in FROZEN_DIRS:
        segments = tuple(frozen.split("/"))
        window = len(segments)
        if any(parts[i : i + window] == segments for i in range(len(parts) - window + 1)):
            return True
    return False


_RESOLVED: dict[tuple[str, Path], Path | None] = {}


def resolve(name: str, citing: Path) -> Path | None:
    """Resolve a cited markdown filename by walking up from the citing file.

    Skill prose cites bare names -- `SKILL.md`, `ledger-template.md` -- and
    means the nearest one that its own skill owns. Falls back to a unique
    match anywhere under the repo, which is how citations reach archived runs
    and artifacts without spelling out their directory.
    """
    key = (name, citing.parent)
    if key in _RESOLVED:
        return _RESOLVED[key]

    found: Path | None = None
    directory = citing.parent
    while found is None:
        for candidate in (directory / name, directory / "references" / name):
            if candidate.is_file():
                found = candidate
                break
        if directory == REPO_ROOT:
            break
        directory = directory.parent

    if found is None:
        matches = [p for p in REPO_ROOT.rglob(name) if p.is_file() and ".git" not in p.parts]
        if len(matches) == 1:
            found = matches[0]

    _RESOLVED[key] = found
    return found


def scope_files() -> list[Path]:
    found: list[Path] = []
    for root in DEFAULT_SCOPE:
        for pattern in SCOPE_PATTERNS:
            found.extend(sorted((REPO_ROOT / root).glob(pattern)))
    return found


def in_scope(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return False
    if rel.parts[0] not in DEFAULT_SCOPE:
        return False
    return any(rel.match(pattern) for pattern in SCOPE_PATTERNS)


def check(path: Path) -> list[str]:
    violations: list[str] = []
    cache: dict[tuple[Path, str | None], str | None] = {}

    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        for match in LINE_CITATION.finditer(line):
            name, target_line = match.group(1), match.group(2)
            target = resolve(name, path)
            # An unresolvable name is left alone: prose legitimately cites files
            # this repo does not own, and the rot this rule exists to catch is
            # rot in files we edit.
            if target is None or in_frozen(target):
                continue
            violations.append(
                f"{path.relative_to(REPO_ROOT)}:{lineno}: line-number citation "
                f"'{match.group(0)}' into a live file — line {target_line} moves "
                f"when {name} is edited and nothing here fails. Cite the section, "
                f"or quote the sentence."
            )

        mentions = [(m.start(), m.end(), m.group(1), m.group(2)) for m in MD_MENTION.finditer(line)]
        for quote_match in QUOTED.finditer(line):
            for start, end, name, sha in mentions:
                before = quote_match.start() - end
                after = start - quote_match.end()
                attributed = 0 <= before <= ATTRIBUTION_WINDOW or 0 <= after <= ATTRIBUTION_WINDOW
                if not attributed:
                    continue
                target = resolve(name, path)
                if target is None or (target == path and sha is None):
                    continue
                key = (target, sha)
                if key not in cache:
                    try:
                        cache[key] = normalize(read_at(target, sha))
                    except FileNotFoundError:
                        detail = (
                            " (a shallow clone cannot see it — fetch full history)"
                            if shallow()
                            else ""
                        )
                        violations.append(
                            f"{path.relative_to(REPO_ROOT)}:{lineno}: citation pins "
                            f"{name}@{sha}, which git cannot resolve{detail}."
                        )
                        cache[key] = None
                content = cache[key]
                if content is None:
                    # Unresolvable pin already reported; do not also report the
                    # quote as missing from a file that was never read.
                    continue
                where = f"{name}@{sha}" if sha else name
                if normalize(quote_match.group(1)) not in content:
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)}:{lineno}: quoted text is "
                        f"attributed to {where} but does not appear there: "
                        f'"{quote_match.group(1)[:70]}…"'
                    )
    return violations


def main(argv: list[str]) -> int:
    paths = [Path(a).resolve() for a in argv] if argv else scope_files()
    targets = [p for p in paths if p.is_file() and in_scope(p)]

    violations = [v for target in targets for v in check(target)]
    for violation in violations:
        print(violation, file=sys.stderr)
    if violations:
        print(f"\n{len(violations)} citation violation(s).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
