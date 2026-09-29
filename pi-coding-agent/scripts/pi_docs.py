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

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

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
