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

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

_CACHE_DIR = Path.home() / ".cache" / "vega-lite-skill"


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
    # (spec_text: str, fmt: str) -> bytes|str (svg returns str); may raise
    render_fn: Callable[[str, str], bytes | str]
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
    if out_path:
        try:
            fmt = infer_format(out_path)
        except ValueError as exc:
            results.append(StageResult("render", Status.FAIL, str(exc)))
            return results
    else:
        fmt = "png"
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
    # Any stage FAIL fails the run; a schema SKIP (offline / uncached) does not.
    return 1 if any(r.status is Status.FAIL for r in results) else 0


def load_schema(vl_version: str | None) -> dict | None:
    major = (vl_version or "6").lstrip("v").split(".")[0]
    cache = _CACHE_DIR / f"vega-lite-v{major}.json"
    if cache.exists():
        try:
            return json.loads(cache.read_text())
        except (OSError, ValueError):
            return None
    url = f"https://vega.github.io/schema/vega-lite/v{major}.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:  # fixed https host
            data = resp.read()
        schema = json.loads(data)  # parse BEFORE caching so we never cache garbage
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(data)
        return schema
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


def default_deps() -> Deps:
    import vl_convert as vlc  # noqa: PLC0415 - lazy load so stub tests don't need it installed

    return Deps(
        # vegalite_to_vega returns a dict; re-serialize to match compile_fn's str contract.
        compile_fn=lambda text: json.dumps(vlc.vegalite_to_vega(text)),
        render_fn=lambda text, fmt: (
            vlc.vegalite_to_png(text) if fmt == "png" else vlc.vegalite_to_svg(text)
        ),
        schema_fn=load_schema,
    )


def preflight() -> str:
    import vl_convert as vlc  # noqa: PLC0415 - lazy load so stub tests don't need it installed

    versions = vlc.get_vegalite_versions()
    # vl_convert's compiled-extension version stub omits __version__; it exists at runtime.
    vlc_version = getattr(vlc, "__version__", "unknown")
    return f"vl-convert {vlc_version} | embedded Vega-Lite {', '.join(versions)}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render a Vega-Lite spec.")
    parser.add_argument("spec", help="path to a Vega-Lite JSON spec, or '-' for stdin")
    parser.add_argument("out", nargs="?", help="output image path (.png or .svg)")
    parser.add_argument(
        "--vl-version",
        default=None,
        help=(
            "Vega-Lite schema version to validate against (e.g. '6'). "
            "Does not change the compile/render target (set by vl-convert)."
        ),
    )
    args = parser.parse_args(argv)

    if args.out is not None:
        try:
            infer_format(args.out)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    print(preflight(), file=sys.stderr)
    try:
        spec_text = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text()
    except OSError as exc:
        print(f"error: cannot read spec: {args.spec} ({exc})", file=sys.stderr)
        return 2
    results = run_all(spec_text, args.out, default_deps(), vl_version=args.vl_version)
    for r in results:
        suffix = f" — {r.detail}" if r.detail else ""
        print(f"[{r.status.value:4}] {r.name}{suffix}", file=sys.stderr)
    code = exit_code(results)
    print("OK" if code == 0 else "FAILED", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
