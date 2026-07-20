import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "render", Path(__file__).parent.parent / "scripts" / "render.py"
)
render = importlib.util.module_from_spec(_spec)
sys.modules["render"] = render
_spec.loader.exec_module(render)

Status, StageResult, Deps = render.Status, render.StageResult, render.Deps

OK = Deps(
    compile_fn=lambda s: '{"$schema": "https://vega.github.io/schema/vega/v5.json"}',  # noqa: ARG005
    render_fn=lambda s, fmt: b"\x89PNG\r\n" if fmt == "png" else b"<svg/>",  # noqa: ARG005
    schema_fn=lambda v: None,  # noqa: ARG005 - schema unavailable -> SKIP
)


def _by_name(results):
    return {r.name: r.status for r in results}


def test_invalid_json_fails_parse_and_stops():
    results = render.run_all("{ not json", out_path=None, deps=OK)
    status = _by_name(results)
    assert status["parse"] is Status.FAIL
    # later stages must not run once parse fails
    assert "compile" not in status


def test_valid_spec_passes_parse_compile_render_and_skips_schema():
    spec = '{"mark": "bar", "encoding": {}}'
    results = render.run_all(spec, out_path=None, deps=OK)
    status = _by_name(results)
    assert status["parse"] is Status.PASS
    assert status["schema"] is Status.SKIP
    assert status["compile"] is Status.PASS
    assert status["render"] is Status.PASS


def test_schema_violation_fails_schema_stage():
    schema = {
        "type": "object",
        "required": ["mark"],
        "additionalProperties": False,
        "properties": {"mark": {"type": "string"}},
    }
    deps = Deps(compile_fn=OK.compile_fn, render_fn=OK.render_fn, schema_fn=lambda v: schema)  # noqa: ARG005
    results = render.run_all('{"mark": "bar", "bogus": 1}', out_path=None, deps=deps)
    status = _by_name(results)
    assert status["schema"] is Status.FAIL
    assert "compile" not in status
    assert "render" not in status


def test_compile_error_fails_compile_and_skips_render():
    def boom(_):
        raise RuntimeError("Unknown field type")

    deps = Deps(compile_fn=boom, render_fn=OK.render_fn, schema_fn=lambda v: None)  # noqa: ARG005
    results = render.run_all('{"mark": "bar"}', out_path=None, deps=deps)
    status = _by_name(results)
    assert status["compile"] is Status.FAIL
    assert "render" not in status


def test_infer_format_and_exit_code():
    assert render.infer_format("out.png") == "png"
    assert render.infer_format("out.svg") == "svg"
    try:
        render.infer_format("out.pdf")
        msg = "expected ValueError"
        raise AssertionError(msg)
    except ValueError:
        pass
    passing = [
        StageResult("parse", Status.PASS),
        StageResult("schema", Status.SKIP),
        StageResult("compile", Status.PASS),
        StageResult("render", Status.PASS),
    ]
    assert render.exit_code(passing) == 0
    failing = [*passing[:2], StageResult("compile", Status.FAIL)]
    assert render.exit_code(failing) == 1
