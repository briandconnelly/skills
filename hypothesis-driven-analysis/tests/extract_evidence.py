#!/usr/bin/env python3
"""Extract machine-checkable evidence from harness JSONL transcripts.

SCOPE: this is the versioned extractor behind the transcript-evidence artifacts in
``tests/runs/artifacts/`` (issue #66). It normalizes a subagent transcript into a
stable event stream so that counts, orderings, and absence claims derive from one
deterministic tool rather than ad-hoc greps or the agent's own summary.

The unit of evidence is the ``tool_use`` block, in JSONL serialization order.
Ordinals — not timestamps — are the ordering authority: they are 1-based positions
in that order. Each tool_use is paired with its tool_result by ``tool_use_id``; a
tool_use proves an *attempt*, and only a paired non-error result proves execution.

Subcommands:

- ``identity``: per-file provenance — SHA-256, byte/line counts, tool_use totals
  by tool, and paired-result ok/error/missing tallies.
- ``manifest``: TSV, one line per tool_use: ordinal, timestamp, tool, result
  status, target (``file_path`` for file tools, full ``command`` for Bash,
  ``path``/``pattern``/``query``/``url`` for search-style tools such as Grep,
  Glob, WebSearch, and WebFetch, ``description`` for Agent dispatches).
  Embedded newlines are flattened to literal ``\\n``.
- ``events``: full canonical JSON per tool_use (complete input, result status),
  for recovering Write/Edit contents verbatim. ``--ordinal`` selects one;
  ``--with-result-text`` includes the paired result's text.
- ``text``: assistant text blocks in serialization order — the surface absence
  claims must also scan, since ceremony can be emitted in the reply rather than
  a file.

``--normalize-root`` replaces the repository root and harness scratch directories with
``<REPO_ROOT>`` and ``<SCRATCH>`` in emitted text; with newline flattening in
``manifest``, these are the only transformations ever applied to extracted text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRATCH_RE = re.compile(r"(?:/private)?/tmp/claude-[0-9]+/[^/\s\"']+/[0-9a-f-]{36}/scratchpad")


def _flatten(text: str) -> str:
    """Escape with jq @tsv semantics: backslash first, so ``\\n`` is unambiguous."""
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")


def _normalize(text: str, repo_root: str | None) -> str:
    if repo_root:
        text = text.replace(repo_root.rstrip("/"), "<REPO_ROOT>")
    return SCRATCH_RE.sub("<SCRATCH>", text)


def _load(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            stripped = raw_line.strip()
            if stripped:
                entries.append(json.loads(stripped))
    return entries


def _content_blocks(entry: dict[str, Any]) -> list[dict[str, Any]]:
    content = entry.get("message", {}).get("content")
    return content if isinstance(content, list) else []


def _tool_uses(entries: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any], dict[str, Any]]]:
    """Return (ordinal, jsonl entry, tool_use block) in serialization order.

    Fails closed on duplicate tool_use ids: a transcript that reuses an id
    cannot be paired unambiguously, so no evidence is extracted from it.
    """
    uses: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    seen_ids: set[str] = set()
    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        for block in _content_blocks(entry):
            if block.get("type") == "tool_use":
                use_id = block.get("id")
                if not isinstance(use_id, str) or not use_id:
                    msg = f"tool_use at position {len(uses) + 1} has no id; refusing to extract"
                    raise SystemExit(msg)
                if use_id in seen_ids:
                    msg = f"duplicate tool_use id {use_id!r}; refusing to extract"
                    raise SystemExit(msg)
                seen_ids.add(use_id)
                uses.append((len(uses) + 1, entry, block))
    return uses


def _results_by_id(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Pair tool_results to tool_uses by id, failing closed on ambiguity.

    A result whose id was not introduced by an earlier tool_use, or a second
    result for an id already paired, means the transcript cannot be trusted
    for attempt/execution claims — extraction aborts rather than guessing.
    """
    use_ids_so_far: set[str] = set()
    results: dict[str, dict[str, Any]] = {}
    for entry in entries:
        blocks = _content_blocks(entry)
        if entry.get("type") == "assistant":
            for block in blocks:
                if block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                    use_ids_so_far.add(block["id"])
            continue
        if entry.get("type") != "user":
            continue
        for block in blocks:
            if block.get("type") != "tool_result":
                continue
            result_id = block.get("tool_use_id")
            if not isinstance(result_id, str) or not result_id:
                msg = "tool_result with missing/empty tool_use_id; refusing to extract"
                raise SystemExit(msg)
            if result_id not in use_ids_so_far:
                msg = f"tool_result {result_id!r} precedes or lacks its tool_use; refusing"
                raise SystemExit(msg)
            if result_id in results:
                msg = f"duplicate tool_result for {result_id!r}; refusing to extract"
                raise SystemExit(msg)
            results[result_id] = block
    return results


def _result_status(use: dict[str, Any], results: dict[str, dict[str, Any]]) -> str:
    result = results.get(use.get("id", ""))
    if result is None:
        return "no-result"
    return "error" if result.get("is_error") else "ok"


def _result_text(result: dict[str, Any]) -> str:
    content = result.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(block.get("text", "") for block in content if isinstance(block, dict))
    return ""


def _target(block: dict[str, Any]) -> str:
    inp = block.get("input", {})
    if not isinstance(inp, dict):
        return "-"
    for key in (
        "file_path",
        "path",
        "notebook_path",
        "command",
        "pattern",
        "query",
        "url",
        "description",
        "prompt",
    ):
        value = inp.get(key)
        if isinstance(value, str) and value:
            return value
    return "-"


def cmd_identity(paths: list[Path]) -> None:
    for path in paths:
        raw = path.read_bytes()
        entries = _load(path)
        uses = _tool_uses(entries)
        results = _results_by_id(entries)
        by_tool = Counter(block.get("name", "?") for _, _, block in uses)
        statuses = Counter(_result_status(block, results) for _, _, block in uses)
        print(f"file: {path.name}")
        print(f"  sha256: {hashlib.sha256(raw).hexdigest()}")
        print(f"  bytes: {len(raw)}  jsonl_lines: {len(entries)}")
        by = ", ".join(f"{name}: {count}" for name, count in sorted(by_tool.items()))
        print(f"  tool_use: {len(uses)}  ({by})")
        st = ", ".join(f"{name}: {count}" for name, count in sorted(statuses.items()))
        print(f"  paired_results: {st}")


def cmd_manifest(path: Path, repo_root: str | None) -> None:
    entries = _load(path)
    results = _results_by_id(entries)
    for ordinal, entry, block in _tool_uses(entries):
        target = _normalize(_flatten(_target(block)), repo_root)
        row = [
            str(ordinal),
            str(entry.get("timestamp", "-")),
            str(block.get("name", "?")),
            _result_status(block, results),
            target,
        ]
        print("\t".join(row))


def cmd_events(
    path: Path, repo_root: str | None, ordinal: int | None, with_result_text: bool
) -> None:
    entries = _load(path)
    results = _results_by_id(entries)
    for num, entry, block in _tool_uses(entries):
        if ordinal is not None and num != ordinal:
            continue
        record: dict[str, Any] = {
            "ordinal": num,
            "timestamp": entry.get("timestamp"),
            "tool_use_id": block.get("id"),
            "tool": block.get("name"),
            "input": block.get("input"),
            "result_status": _result_status(block, results),
        }
        if with_result_text:
            result = results.get(block.get("id", ""))
            record["result_text"] = _result_text(result) if result else None
        print(_normalize(json.dumps(record, ensure_ascii=False), repo_root))


def cmd_text(path: Path, repo_root: str | None) -> None:
    entries = _load(path)
    _results_by_id(entries)  # same fail-closed validation as every other subcommand
    _tool_uses(entries)
    block_num = 0
    tools_seen = 0
    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        for block in _content_blocks(entry):
            if block.get("type") == "tool_use":
                tools_seen += 1
            elif block.get("type") == "text" and block.get("text"):
                block_num += 1
                print(f"=== text block {block_num} (after tool_use {tools_seen}) ===")
                print(_normalize(block["text"], repo_root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--normalize-root",
        metavar="PATH",
        default=None,
        help="replace this repository root with <REPO_ROOT> in emitted text",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_identity = sub.add_parser("identity", help="provenance and totals per transcript")
    p_identity.add_argument("files", nargs="+", type=Path)

    p_manifest = sub.add_parser("manifest", help="TSV: ordinal, timestamp, tool, status, target")
    p_manifest.add_argument("file", type=Path)

    p_events = sub.add_parser("events", help="full canonical JSON per tool_use")
    p_events.add_argument("file", type=Path)
    p_events.add_argument("--ordinal", type=int, default=None)
    p_events.add_argument("--with-result-text", action="store_true")

    p_text = sub.add_parser("text", help="assistant text blocks in order")
    p_text.add_argument("file", type=Path)

    args = parser.parse_args(argv)
    root = args.normalize_root
    if args.command == "identity":
        cmd_identity(args.files)
    elif args.command == "manifest":
        cmd_manifest(args.file, root)
    elif args.command == "events":
        cmd_events(args.file, root, args.ordinal, args.with_result_text)
    elif args.command == "text":
        cmd_text(args.file, root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
