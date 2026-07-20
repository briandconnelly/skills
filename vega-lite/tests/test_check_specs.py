import importlib.util
import sys
from pathlib import Path


def _load_check_specs():
    p = Path(__file__).parent / "check_specs.py"
    spec = importlib.util.spec_from_file_location("check_specs", p)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_specs"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_malformed_json_fence_is_surfaced(tmp_path):
    # A ```json fence with invalid JSON (trailing comma) must be surfaced, not skipped,
    # so run_all's parse stage can fail it.
    cs = _load_check_specs()
    md = tmp_path / "doc.md"
    md.write_text('intro\n```json\n{"mark": "bar",}\n```\nmore\n')
    specs = cs.extract_specs(md)
    assert any("malformed" in label for label, _ in specs)


def test_valid_json_spec_is_extracted(tmp_path):
    cs = _load_check_specs()
    md = tmp_path / "doc.md"
    md.write_text('```json\n{"mark": "bar", "encoding": {}}\n```\n')
    specs = cs.extract_specs(md)
    assert len(specs) == 1
    assert "malformed" not in specs[0][0]


def test_jsonc_fence_is_ignored(tmp_path):
    # Intentionally-broken / illustrative snippets use ```jsonc, which the fence regex
    # never matches, so they are neither rendered nor flagged.
    cs = _load_check_specs()
    md = tmp_path / "doc.md"
    md.write_text('```jsonc\n{"mark": "bar",}\n```\n')
    specs = cs.extract_specs(md)
    assert specs == []
