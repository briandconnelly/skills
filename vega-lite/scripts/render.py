#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vl-convert-python==1.9.0",
#   "jsonschema>=4.21",
# ]
# ///
"""Staged validator/renderer for static Vega-Lite v6 specs.

Stages, in order: parse -> schema -> compile -> render.
A clean render is evidence of compatibility, not proof of correctness;
inspect the produced image before trusting the chart.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class Status(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class StageResult:
    name: str
    status: Status
    detail: str = ""


@dataclass
class Deps:
    compile_fn: Callable[[str], str]  # (spec_text: str) -> str (Vega JSON); may raise
    render_fn: Callable[[str, str], bytes]  # (spec_text: str, fmt: str) -> bytes; may raise
    schema_fn: Callable[[str | None], dict | None]  # (vl_version: str | None) -> dict | None


def infer_format(out_path: str) -> str:
    lower = out_path.lower()
    if lower.endswith(".png"):
        return "png"
    if lower.endswith(".svg"):
        return "svg"
    raise ValueError(f"unsupported output extension: {out_path!r} (use .png or .svg)")


def _schema_stage(spec: dict, schema_fn, vl_version) -> StageResult:
    schema = schema_fn(vl_version)
    if schema is None:
        return StageResult("schema", Status.SKIP, "schema unavailable (offline / not cached)")
    import jsonschema  # noqa: PLC0415 - lazy load to avoid dependency on schema_fn

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda e: e.path)
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "<root>"
        return StageResult("schema", Status.FAIL, f"{loc}: {first.message}")
    return StageResult("schema", Status.PASS)


def run_all(
    spec_text: str, out_path: str | None, deps: Deps, vl_version: str | None = None
) -> list[StageResult]:
    results: list[StageResult] = []

    # Stage 1: parse
    try:
        spec = json.loads(spec_text)
    except json.JSONDecodeError as exc:
        results.append(StageResult("parse", Status.FAIL, str(exc)))
        return results
    results.append(StageResult("parse", Status.PASS))

    # Stage 2: schema
    results.append(_schema_stage(spec, deps.schema_fn, vl_version))
    if results[-1].status is Status.FAIL:
        return results

    # Stage 3: compile
    try:
        deps.compile_fn(spec_text)
    except Exception as exc:
        results.append(StageResult("compile", Status.FAIL, str(exc)))
        return results
    results.append(StageResult("compile", Status.PASS))

    # Stage 4: render
    fmt = infer_format(out_path) if out_path else "png"
    try:
        image = deps.render_fn(spec_text, fmt)
    except Exception as exc:
        results.append(StageResult("render", Status.FAIL, str(exc)))
        return results
    if out_path:
        with Path(out_path).open("wb") as fh:
            fh.write(image if isinstance(image, (bytes, bytearray)) else image.encode())
    results.append(StageResult("render", Status.PASS))
    return results


def exit_code(results: list[StageResult]) -> int:
    fatal = {"parse", "schema", "compile", "render"}
    return 1 if any(r.name in fatal and r.status is Status.FAIL for r in results) else 0
