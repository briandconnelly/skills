# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check Markdown files: json/ndjson fences parse and relative links resolve.

Usage: uv run check_fences.py FILE.md [FILE.md ...]
Exits 0 when every file is clean, 1 otherwise, printing `file:line: reason`.
"""

import json
import re
import sys
from pathlib import Path

_PREFIX = re.compile(r"^[ \t>]*")
_FENCE = re.compile(r"^(`{3,})\s*([A-Za-z0-9_-]*)\s*$")
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#)", re.IGNORECASE)


def _strip(line: str) -> str:
    """Drop leading indentation and blockquote markers."""
    return _PREFIX.sub("", line.rstrip("\n"))


def _check_fence(path: Path, lang: str, start: int, body: list[str]) -> list[str]:
    if lang == "json":
        try:
            json.loads("\n".join(body))
        except json.JSONDecodeError as exc:
            return [f"{path}:{start}: json fence does not parse: {exc.msg}"]
    elif lang == "ndjson":
        problems = []
        for offset, text in enumerate(body, start=1):
            if not text.strip():
                continue
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                problems.append(f"{path}:{start + offset}: ndjson line does not parse: {exc.msg}")
        return problems
    return []


def check_file(path: Path) -> list[str]:
    """Return one `file:line: reason` string per problem found in `path`."""
    problems: list[str] = []
    fence: tuple[str, str, int] | None = None  # (ticks, lang, opening line)
    body: list[str] = []
    for number, raw in enumerate(path.read_text().splitlines(), start=1):
        line = _strip(raw)
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = (match.group(1), match.group(2).lower(), number)
                body = []
                continue
            for target in _LINK.findall(line):
                if _EXTERNAL.match(target):
                    continue
                relative = target.split("#", 1)[0]
                if relative and not (path.parent / relative).exists():
                    problems.append(f"{path}:{number}: link target does not exist: {target}")
        elif match and not match.group(2) and len(match.group(1)) >= len(fence[0]):
            problems.extend(_check_fence(path, fence[1], fence[2], body))
            fence = None
        else:
            body.append(line)
    if fence is not None:
        problems.append(f"{path}:{fence[2]}: unclosed fence")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    problems = [problem for name in argv for problem in check_file(Path(name))]
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
