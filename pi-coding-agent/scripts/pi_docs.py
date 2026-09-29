#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Locate the installed Pi coding agent and navigate its bundled documentation.

This tool finds where the installed version documents something.
It never summarizes Pi's docs, which stay the single home of every Pi contract.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PACKAGE_NAME = "@earendil-works/pi-coding-agent"
LOCAL_INSTALL = Path("node_modules") / "@earendil-works" / "pi-coding-agent"
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ANCHOR_TAG = re.compile(r'<a\s+(?:id|name)="([^"]+)"')
HTML_TAG = re.compile(r"<[^>]+>")


class NoInstallError(Exception):
    """No Pi install was found; the message names every place searched."""


@dataclass(frozen=True)
class Install:
    root: Path
    version: str
    on_path: bool

    @property
    def docs(self) -> Path:
        return self.root / "docs"

    @property
    def examples(self) -> Path:
        return self.root / "examples"

    @property
    def changelog(self) -> Path:
        return self.root / "CHANGELOG.md"


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    line: int


def _package_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        manifest = candidate / "package.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and data.get("name") == PACKAGE_NAME:
            return candidate
    return None


def _version(root: Path) -> str:
    return str(json.loads((root / "package.json").read_text(encoding="utf-8"))["version"])


def find_installs(path_env: str | None, cwd: Path) -> list[Install]:
    """Every Pi install reachable from PATH or a node_modules above cwd; the PATH one first."""
    found: dict[Path, Install] = {}
    exe = shutil.which("pi", path=path_env)
    if exe:
        root = _package_root(Path(exe).resolve().parent)
        if root is not None:
            found[root] = Install(root, _version(root), on_path=True)
    for directory in (cwd, *cwd.parents):
        candidate = directory / LOCAL_INSTALL
        if (candidate / "package.json").is_file():
            root = candidate.resolve()
            if root not in found:
                found[root] = Install(root, _version(root), on_path=False)
    if not found:
        pi_state = f"found {exe}, but it is not inside {PACKAGE_NAME}" if exe else "not found"
        msg = (
            f"No Pi install found. Searched: `pi` on PATH ({pi_state}); "
            f"{LOCAL_INSTALL} in {cwd} and each ancestor."
        )
        raise NoInstallError(msg)
    return sorted(found.values(), key=lambda i: (not i.on_path, str(i.root)))


def headings(text: str) -> list[Heading]:
    """ATX headings outside fenced code blocks."""
    result: list[Heading] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            result.append(Heading(len(match.group(1)), match.group(2), number))
    return result


def slugify(text: str) -> str:
    """GitHub-style heading slug: lowercase, punctuation dropped, spaces to hyphens."""
    text = HTML_TAG.sub("", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(text: str) -> set[str]:
    """Every fragment a link into this page can target: heading slugs and explicit ids."""
    result: set[str] = set()
    seen: dict[str, int] = {}
    for heading in headings(text):
        slug = slugify(heading.text)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.add(slug if count == 0 else f"{slug}-{count}")
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            result.update(ANCHOR_TAG.findall(line))
    return result


DEFAULT_SKILL_DIR = Path(__file__).resolve().parent.parent
EXAMPLE_HEADER_END = re.compile(r"^\s*(import|export)\b")
INDEX_LEVELS = (2, 3)
EXIT_OK, EXIT_NOT_FOUND, EXIT_NO_INSTALL = 0, 1, 2


@dataclass(frozen=True)
class Hit:
    file: str
    section: str
    line: int
    text: str


def _page_headings(page: Path) -> list[dict[str, Any]]:
    text = page.read_text(encoding="utf-8")
    return [{"level": h.level, "text": h.text} for h in headings(text) if h.level in INDEX_LEVELS]


def build_index(install: Install) -> list[dict[str, Any]]:
    """The docs.json navigation with each page's ## and ### headings, then unlisted pages."""
    navigation = json.loads((install.docs / "docs.json").read_text(encoding="utf-8"))["navigation"]
    entries: list[dict[str, Any]] = []
    listed: set[str] = set()

    def walk(items: list[dict[str, Any]], depth: int) -> None:
        for item in items:
            if "items" in item:
                entries.append({"depth": depth, "title": item["title"], "group": True})
                walk(item["items"], depth + 1)
                continue
            path = str(item["path"])
            listed.add(path)
            page = install.docs / path
            exists = page.is_file()
            entries.append(
                {
                    "depth": depth,
                    "title": item["title"],
                    "path": path,
                    "missing": not exists,
                    "headings": _page_headings(page) if exists else [],
                }
            )

    walk(navigation, 0)
    for page in sorted(install.docs.glob("*.md")):
        if page.name not in listed:
            entries.append(
                {
                    "depth": 0,
                    "title": page.stem,
                    "path": page.name,
                    "unlisted": True,
                    "missing": False,
                    "headings": _page_headings(page),
                }
            )
    return entries


def _grep_markdown(path: Path, label: str, pattern: re.Pattern[str]) -> list[Hit]:
    hits: list[Hit] = []
    section = "(top)"
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and (match := HEADING.match(line)):
            section = match.group(2)
        if pattern.search(line):
            hits.append(Hit(label, section, number, line.strip()))
    return hits


def _grep_example_header(path: Path, label: str, pattern: re.Pattern[str]) -> list[Hit]:
    hits: list[Hit] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if EXAMPLE_HEADER_END.match(line):
            break
        if pattern.search(line):
            hits.append(Hit(label, "(header comment)", number, line.strip()))
    return hits


def grep(install: Install, terms: list[str]) -> list[Hit]:
    """Case-insensitive literal search of docs/*.md and example header comments; any term."""
    pattern = re.compile("|".join(re.escape(term) for term in terms), re.IGNORECASE)
    hits: list[Hit] = []
    for page in sorted(install.docs.glob("*.md")):
        hits.extend(_grep_markdown(page, f"docs/{page.name}", pattern))
    if install.examples.is_dir():
        for path in sorted(install.examples.rglob("*")):
            # Test the path below examples/, never the absolute path: Pi itself is
            # installed under a node_modules directory (e.g. Homebrew's lib/node_modules).
            if "node_modules" in path.relative_to(install.examples).parts or not path.is_file():
                continue
            label = path.relative_to(install.root).as_posix()
            if path.name == "README.md":
                hits.extend(_grep_markdown(path, label, pattern))
            elif path.suffix == ".ts":
                hits.extend(_grep_example_header(path, label, pattern))
    return hits


def changelog(install: Install, term: str) -> list[tuple[str, list[str]]]:
    """Changelog lines mentioning the term, grouped under their version heading."""
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    entries: list[tuple[str, list[str]]] = []
    version, lines = "(before first version heading)", []
    for line in install.changelog.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if lines:
                entries.append((version, lines))
            version, lines = line[3:].strip(), []
        elif pattern.search(line):
            lines.append(line.strip())
    if lines:
        entries.append((version, lines))
    return entries


def verified_against(skill_dir: Path) -> str | None:
    """The Pi version the skill was last fully checked against, or None if unrecorded."""
    marker = skill_dir / "verified-against"
    if not marker.is_file():
        return None
    value = marker.read_text(encoding="utf-8").strip().removeprefix("v")
    return value or None


def _print_where(installs: list[Install], recorded: str | None) -> None:
    primary = installs[0]
    runs = "runs as `pi` on PATH" if primary.on_path else "not on PATH; `pi` does not run it"
    print(f"Pi {primary.version} at {primary.root} ({runs})")
    print(f"  docs:      {primary.docs}")
    print(f"  examples:  {primary.examples}")
    print(f"  changelog: {primary.changelog}")
    if len(installs) > 1:
        print("Other installs:")
        for other in installs[1:]:
            print(f"  {other.version} at {other.root} (not on PATH)")
    if recorded is None:
        print("Skill verified against: unrecorded")
    elif recorded == primary.version:
        print(f"Skill verified against {recorded} (matches installed)")
    else:
        print(
            f"Skill verified against {recorded}; installed Pi is {primary.version}. "
            "The skill's citations and gap entries may be stale (see MAINTAINING.md); "
            "answers still come from the installed docs."
        )


def _print_index(entries: list[dict[str, Any]]) -> None:
    printed_unlisted = False
    for entry in entries:
        if entry.get("unlisted") and not printed_unlisted:
            print("Not in docs.json navigation:")
            printed_unlisted = True
        indent = "  " * (entry["depth"] + (1 if entry.get("unlisted") else 0))
        if entry.get("group"):
            print(f"{indent}{entry['title']}/")
            continue
        missing = " (missing)" if entry["missing"] else ""
        print(f"{indent}{entry['title']} — {entry['path']}{missing}")
        for heading in entry["headings"]:
            nested = "  " * (heading["level"] - INDEX_LEVELS[0])
            print(f"{indent}    {nested}{'#' * heading['level']} {heading['text']}")


def _cmd_where(installs: list[Install], args: argparse.Namespace, skill_dir: Path) -> int:
    primary = installs[0]
    recorded = verified_against(skill_dir)
    if not args.json:
        _print_where(installs, recorded)
        return EXIT_OK
    payload = {
        "installs": [
            {
                "root": str(i.root),
                "version": i.version,
                "on_path": i.on_path,
                "docs": str(i.docs),
                "examples": str(i.examples),
                "changelog": str(i.changelog),
            }
            for i in installs
        ],
        "verified_against": recorded,
        "verification_matches": None if recorded is None else recorded == primary.version,
    }
    print(json.dumps(payload, indent=2))
    return EXIT_OK


def _cmd_index(primary: Install, args: argparse.Namespace) -> int:
    entries = build_index(primary)
    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        _print_index(entries)
    return EXIT_OK


def _cmd_grep(primary: Install, args: argparse.Namespace) -> int:
    hits = grep(primary, args.terms)
    if not hits:
        print(
            f"no matches for {args.terms!r} in docs/*.md, example READMEs, "
            f"or example header comments of Pi {primary.version} at {primary.root}",
            file=sys.stderr,
        )
        return EXIT_NOT_FOUND
    if args.json:
        print(json.dumps([asdict(hit) for hit in hits], indent=2))
    else:
        for hit in hits:
            print(f"{hit.file}:{hit.line} [{hit.section}] {hit.text}")
    return EXIT_OK


def _cmd_changelog(primary: Install, args: argparse.Namespace) -> int:
    if not primary.changelog.is_file():
        print(f"no CHANGELOG.md at {primary.changelog}", file=sys.stderr)
        return EXIT_NOT_FOUND
    entries = changelog(primary, args.term)
    if not entries:
        print(f"no changelog lines mention {args.term!r} (Pi {primary.version})", file=sys.stderr)
        return EXIT_NOT_FOUND
    if args.json:
        print(json.dumps([{"version": v, "lines": ls} for v, ls in entries], indent=2))
    else:
        for version, lines in entries:
            print(f"## {version}")
            for line in lines:
                print(f"  {line}")
    return EXIT_OK


def main(
    argv: list[str] | None = None,
    *,
    path_env: str | None = None,
    cwd: Path | None = None,
    skill_dir: Path = DEFAULT_SKILL_DIR,
) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser = argparse.ArgumentParser(prog="pi-docs", description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("where", parents=[common], help="installed version, paths, skill status")
    sub.add_parser("index", parents=[common], help="docs.json navigation with page headings")
    grep_parser = sub.add_parser(
        "grep", parents=[common], help="literal, case-insensitive search; any term matches"
    )
    grep_parser.add_argument("terms", nargs="+")
    log_parser = sub.add_parser("changelog", parents=[common], help="changelog lines by version")
    log_parser.add_argument("term")
    args = parser.parse_args(argv)

    try:
        installs = find_installs(
            path_env if path_env is not None else os.environ.get("PATH"), cwd or Path.cwd()
        )
    except NoInstallError as error:
        print(error, file=sys.stderr)
        return EXIT_NO_INSTALL
    if args.command == "where":
        return _cmd_where(installs, args, skill_dir)
    handlers = {"index": _cmd_index, "grep": _cmd_grep, "changelog": _cmd_changelog}
    return handlers[args.command](installs[0], args)


if __name__ == "__main__":
    sys.exit(main())
