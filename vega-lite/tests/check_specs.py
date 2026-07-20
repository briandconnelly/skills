#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vl-convert-python==1.9.0",
#   "jsonschema>=4.21",
# ]
# ///
"""Extract Vega-Lite specs from .vl.json files and fenced ```json blocks in
markdown, then run each through render.py's staged validator. Fails if any
spec does not pass parse/compile/render (schema SKIP is allowed offline)."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("render", _HERE.parent / "scripts" / "render.py")
assert _spec is not None
render = importlib.util.module_from_spec(_spec)
sys.modules["render"] = render
assert _spec.loader is not None
_spec.loader.exec_module(render)

_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def _looks_like_spec(obj: object) -> bool:
    if not isinstance(obj, dict):
        return False
    schema = str(obj.get("$schema", ""))
    return "vega-lite" in schema or any(k in obj for k in ("mark", "layer", "facet"))


def extract_specs(path: Path) -> list[tuple[str, str]]:
    text = path.read_text()
    if path.name.endswith(".vl.json"):
        return [(path.name, text)]
    if path.suffix == ".md":
        out = []
        for i, block in enumerate(_FENCE.findall(text)):
            try:
                obj = json.loads(block)
            except json.JSONDecodeError:
                # A ```json fence is asserted to be a real spec by convention
                # (illustrative or intentionally-broken snippets use ```jsonc, which
                # this regex never matches). A malformed one must surface as a failure,
                # not be silently skipped — hand it to run_all so its parse stage fails.
                out.append((f"{path.name}#json[{i}] (malformed JSON)", block))
                continue
            if _looks_like_spec(obj):
                out.append((f"{path.name}#json[{i}]", block))
        return out
    return []


def check_path(path: Path) -> int:
    deps = render.default_deps()
    failures = 0
    for label, spec_text in extract_specs(path):
        results = render.run_all(spec_text, out_path=None, deps=deps)
        code = render.exit_code(results)
        summary = " ".join(f"{r.name}:{r.status.value}" for r in results)
        print(f"[{'OK ' if code == 0 else 'FAIL'}] {label}  {summary}")
        failures += code
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    targets: list[Path] = []
    for arg in argv:
        p = Path(arg)
        targets += sorted(p.rglob("*.vl.json")) + sorted(p.rglob("*.md")) if p.is_dir() else [p]
    rc = 0
    for t in targets:
        rc |= check_path(t)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
