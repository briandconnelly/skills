#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""Validate SKILL.md frontmatter against the agentskills.io specification.

Reference: https://agentskills.io/specification
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_DELIM = "---"
STR_TAG = "tag:yaml.org,2002:str"

# Field length limits from the agentskills.io specification.
NAME_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 1024
COMPATIBILITY_MAX_LEN = 500

KNOWN_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

Fields = dict[str, tuple[yaml.Node, yaml.Node]]


@dataclass
class Issue:
    path: str
    line: int
    level: str  # "error" or "warning"
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.level}: {self.message}"


def _extract_frontmatter(text: str) -> tuple[str | None, int]:
    """Return (yaml_text, file_line_for_yaml_line_1) or (None, 0) if missing."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            return "\n".join(lines[1:i]), 2
    return None, 0


def _line(node: yaml.Node | None, offset: int) -> int:
    if node is None:
        return offset
    return node.start_mark.line + offset


def _string(node: yaml.Node) -> str | None:
    """Return the scalar's value only if it resolves to a YAML string."""
    if not isinstance(node, yaml.ScalarNode):
        return None
    if node.tag != STR_TAG:
        return None
    return node.value


def _collect_fields(
    p: str, node: yaml.MappingNode, offset: int
) -> tuple[list[Issue], dict[str, int], Fields]:
    issues: list[Issue] = []
    seen: dict[str, int] = {}
    fields: Fields = {}
    for key_node, value_node in node.value:
        key = _string(key_node)
        line = _line(key_node, offset)
        if key is None:
            issues.append(Issue(p, line, "error", "frontmatter keys must be scalar strings"))
            continue
        if key in seen:
            issues.append(
                Issue(
                    p,
                    line,
                    "error",
                    f"duplicate key {key!r} (first seen at line {seen[key]})",
                )
            )
            continue
        seen[key] = line
        fields[key] = (key_node, value_node)
    return issues, seen, fields


def _check_name(p: str, fields: Fields, offset: int, expected_name: str) -> list[Issue]:
    if "name" not in fields:
        return [Issue(p, offset, "error", "missing required field 'name'")]
    key_node, value_node = fields["name"]
    line = _line(key_node, offset)
    value = _string(value_node)
    if value is None:
        return [Issue(p, line, "error", "'name' must be a string")]
    issues: list[Issue] = []
    if not (1 <= len(value) <= NAME_MAX_LEN):
        issues.append(
            Issue(
                p,
                line,
                "error",
                f"'name' must be 1-{NAME_MAX_LEN} characters (got {len(value)})",
            )
        )
    if not NAME_RE.match(value):
        issues.append(
            Issue(
                p,
                line,
                "error",
                "'name' must be lowercase alphanumeric with hyphens; "
                "no leading, trailing, or consecutive hyphens",
            )
        )
    if value != expected_name:
        issues.append(
            Issue(
                p,
                line,
                "error",
                f"'name' ({value!r}) must equal parent directory name ({expected_name!r})",
            )
        )
    return issues


def _check_description(p: str, fields: Fields, offset: int) -> list[Issue]:
    if "description" not in fields:
        return [Issue(p, offset, "error", "missing required field 'description'")]
    key_node, value_node = fields["description"]
    line = _line(key_node, offset)
    value = _string(value_node)
    if value is None:
        return [Issue(p, line, "error", "'description' must be a string")]
    issues: list[Issue] = []
    if not value.strip():
        issues.append(Issue(p, line, "error", "'description' must be non-empty"))
    if len(value) > DESCRIPTION_MAX_LEN:
        issues.append(
            Issue(
                p,
                line,
                "error",
                f"'description' must be at most {DESCRIPTION_MAX_LEN} characters "
                f"(got {len(value)})",
            )
        )
    return issues


def _check_string_field(p: str, fields: Fields, offset: int, key: str) -> list[Issue]:
    if key not in fields:
        return []
    key_node, value_node = fields[key]
    if _string(value_node) is None:
        return [Issue(p, _line(key_node, offset), "error", f"'{key}' must be a string")]
    return []


def _check_compatibility(p: str, fields: Fields, offset: int) -> list[Issue]:
    if "compatibility" not in fields:
        return []
    key_node, value_node = fields["compatibility"]
    line = _line(key_node, offset)
    value = _string(value_node)
    if value is None:
        return [Issue(p, line, "error", "'compatibility' must be a string")]
    if not (1 <= len(value) <= COMPATIBILITY_MAX_LEN):
        return [
            Issue(
                p,
                line,
                "error",
                f"'compatibility' must be 1-{COMPATIBILITY_MAX_LEN} characters (got {len(value)})",
            )
        ]
    return []


def _check_metadata(p: str, fields: Fields, offset: int) -> list[Issue]:
    if "metadata" not in fields:
        return []
    key_node, value_node = fields["metadata"]
    line = _line(key_node, offset)
    if not isinstance(value_node, yaml.MappingNode):
        return [Issue(p, line, "error", "'metadata' must be a mapping")]
    issues: list[Issue] = []
    meta_seen: dict[str, int] = {}
    for k_node, v_node in value_node.value:
        k_str = _string(k_node)
        k_line = _line(k_node, offset)
        if k_str is None:
            issues.append(Issue(p, k_line, "error", "'metadata' keys must be strings"))
        elif k_str in meta_seen:
            issues.append(
                Issue(
                    p,
                    k_line,
                    "error",
                    f"'metadata' has duplicate key {k_str!r} "
                    f"(first seen at line {meta_seen[k_str]})",
                )
            )
        else:
            meta_seen[k_str] = k_line
        if _string(v_node) is None:
            issues.append(
                Issue(
                    p,
                    _line(v_node, offset),
                    "error",
                    f"'metadata' values must be strings (key {k_str!r})",
                )
            )
    return issues


def _check_unknown_fields(p: str, fields: Fields, seen: dict[str, int]) -> list[Issue]:
    return [
        Issue(
            p,
            seen[key],
            "warning",
            f"unknown field {key!r} (not in agentskills.io spec)",
        )
        for key in fields
        if key not in KNOWN_FIELDS
    ]


def validate(path: str | Path) -> list[Issue]:
    p = Path(path)

    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        return [Issue(str(p), 1, "error", f"could not read file: {exc}")]

    yaml_text, offset = _extract_frontmatter(text)
    if yaml_text is None:
        return [
            Issue(
                str(p),
                1,
                "error",
                "missing YAML frontmatter (file must start with '---' line)",
            )
        ]

    try:
        node = yaml.compose(yaml_text)
    except yaml.YAMLError as exc:
        line = offset
        if getattr(exc, "problem_mark", None) is not None:
            line = exc.problem_mark.line + offset
        msg = getattr(exc, "problem", None) or str(exc)
        return [Issue(str(p), line, "error", f"invalid YAML: {msg}")]

    if node is None:
        return [Issue(str(p), offset, "error", "frontmatter is empty")]

    if not isinstance(node, yaml.MappingNode):
        return [
            Issue(
                str(p),
                _line(node, offset),
                "error",
                "frontmatter must be a YAML mapping",
            )
        ]

    issues, seen, fields = _collect_fields(str(p), node, offset)
    issues += _check_name(str(p), fields, offset, p.parent.name)
    issues += _check_description(str(p), fields, offset)
    issues += _check_string_field(str(p), fields, offset, "license")
    issues += _check_compatibility(str(p), fields, offset)
    issues += _check_metadata(str(p), fields, offset)
    issues += _check_string_field(str(p), fields, offset, "allowed-tools")
    issues += _check_unknown_fields(str(p), fields, seen)
    return issues


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: check-skill-frontmatter.py SKILL.md [SKILL.md ...]", file=sys.stderr)
        return 2

    errors = 0
    for arg in argv:
        for issue in validate(arg):
            stream = sys.stdout if issue.level == "error" else sys.stderr
            print(issue.format(), file=stream)
            if issue.level == "error":
                errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
