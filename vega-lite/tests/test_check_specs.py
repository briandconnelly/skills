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


def test_composition_operator_specs_are_recognized(tmp_path):
    # Schema-less specs using any top-level composition operator must still be
    # extracted, so future repeat/concat examples can't silently escape validation.
    cs = _load_check_specs()
    for key in ("repeat", "concat", "hconcat", "vconcat", "facet", "layer", "mark"):
        md = tmp_path / f"{key}.md"
        md.write_text(f'```json\n{{"{key}": {{}}, "spec": {{}}}}\n```\n')
        assert len(cs.extract_specs(md)) == 1, key


def test_main_without_targets_is_usage_error():
    cs = _load_check_specs()
    usage_error = 2
    assert cs.main([]) == usage_error


def test_main_rejects_missing_target_cleanly(capsys):
    # A nonexistent target must produce a usage-style error, not an
    # unhandled FileNotFoundError traceback.
    cs = _load_check_specs()
    usage_error = 2
    assert cs.main(["/no/such/file.md"]) == usage_error
    assert "no such file or directory" in capsys.readouterr().err


def test_main_rejects_unsupported_file_type_cleanly(tmp_path, capsys):
    # An explicit non-.md/.vl.json target must be rejected up front: extract_specs
    # would read_text() it (an unhandled UnicodeDecodeError on binary content) and
    # then extract nothing from it anyway.
    cs = _load_check_specs()
    binary = tmp_path / "chart.png"
    binary.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x01\x02")
    usage_error = 2
    assert cs.main([str(binary)]) == usage_error
    assert "unsupported target" in capsys.readouterr().err


def test_main_fails_closed_when_no_specs_extracted(tmp_path):
    # A scan that finds nothing to validate must not exit green: an empty run and
    # an all-pass run would otherwise be indistinguishable.
    cs = _load_check_specs()
    (tmp_path / "prose-only.md").write_text("no fences here\n")
    assert cs.main([str(tmp_path)]) == 1
