#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4",
# ]
# ///
"""Validate an agent-friendly-mcp wire fixture against the skill's contract.

Checks the corrected outputSchema/error contract (contract-checklist.md
§3 output rules and §6 "one error envelope, two carriers"):

  * the success result's structuredContent conforms to the tool's outputSchema;
  * the error result sets isError: true and carries the §6 envelope in
    structuredContent (or, only when wire.degraded_text_carrier is declared,
    as JSON text in content[0].text);
  * the error envelope conforms to its own schema, NOT to outputSchema.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator


@dataclass
class Issue:
    where: str
    message: str

    def format(self, fixture_path: str) -> str:
        return f"{fixture_path}: {self.where}: {self.message}"


def _schema_errors(instance, schema, where: str) -> list[Issue]:
    validator = Draft202012Validator(schema)
    return [
        Issue(where, f"schema violation at {list(e.path)}: {e.message}")
        for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    ]


def validate(fixture: dict) -> list[Issue]:
    issues: list[Issue] = []
    wire = fixture.get("wire")
    if not isinstance(wire, dict):
        return [Issue("wire", "fixture has no 'wire' object")]

    output_schema = wire.get("output_schema")
    error_schema = wire.get("error_schema")
    success = wire.get("success_result")
    error = wire.get("error_result")

    # --- success path: structuredContent conforms to outputSchema ---
    if not isinstance(success, dict):
        issues.append(Issue("success_result", "missing success_result"))
    else:
        if success.get("isError") is True:
            issues.append(Issue("success_result", "success_result must not set isError: true"))
        sc = success.get("structuredContent")
        if sc is None:
            issues.append(Issue("success_result", "success_result missing structuredContent"))
        elif isinstance(output_schema, dict):
            issues += _schema_errors(sc, output_schema, "success_result.structuredContent vs output_schema")
        else:
            issues.append(Issue("wire.output_schema", "missing output_schema"))

    # --- error path: isError + envelope in structuredContent vs error_schema ---
    if not isinstance(error, dict):
        issues.append(Issue("error_result", "missing error_result"))
        return issues

    if error.get("isError") is not True:
        issues.append(Issue("error_result", "error_result must set isError: true"))

    degraded = bool(wire.get("degraded_text_carrier"))
    envelope = error.get("structuredContent")

    if envelope is None and not degraded:
        issues.append(
            Issue(
                "error_result",
                "error envelope must be in structuredContent (native carrier); "
                "a content[0].text carrier is allowed only when wire.degraded_text_carrier is declared",
            )
        )
    if envelope is None and degraded:
        # disclosed degraded mode: envelope rides as JSON text in content[0].text
        content = error.get("content") or []
        text = content[0].get("text") if content and isinstance(content[0], dict) else None
        if text is None:
            issues.append(Issue("error_result", "degraded_text_carrier declared but content[0].text is missing"))
        else:
            try:
                envelope = json.loads(text)
            except (ValueError, TypeError):
                issues.append(Issue("error_result", "degraded_text_carrier content[0].text is not valid envelope JSON"))
                envelope = None

    if envelope is not None:
        if isinstance(error_schema, dict):
            issues += _schema_errors(envelope, error_schema, "error_result envelope vs error_schema")
        else:
            issues.append(Issue("wire.error_schema", "missing error_schema"))

    return issues


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: validate_fixture.py FIXTURE.json | DIR ...", file=sys.stderr)
        return 2

    paths: list[Path] = []
    for arg in argv:
        p = Path(arg)
        paths.extend(sorted(p.glob("*.json")) if p.is_dir() else [p])

    errors = 0
    for path in paths:
        try:
            fixture = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"{path}: load: {exc}", file=sys.stderr)
            errors += 1
            continue
        for issue in validate(fixture):
            print(issue.format(str(path)))
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
