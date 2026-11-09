"""Worked examples in references/examples.md must obey the checklist rules they illustrate."""

import contextlib
import json
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent / "references" / "examples.md"
# Known positives: an instrument that parsed nothing would pass every other test vacuously.
MIN_JSON_BLOCKS = 38
MIN_TOOL_DEFINITIONS = 5
LISTEN_REQUEST_ID = 7  # ex§5b's subscriptions/listen JSON-RPC id


def json_blocks(text: str) -> list[tuple[int, object]]:
    """Return (1-based opening-fence line, parsed value) for each ```json block that parses."""
    blocks: list[tuple[int, object]] = []
    start: int | None = None
    body: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if start is None:
            if stripped == "```json":
                start, body = lineno, []
        elif stripped == "```":
            with contextlib.suppress(json.JSONDecodeError):
                blocks.append((start, json.loads("\n".join(body))))
            start = None
        else:
            body.append(line)
    return blocks


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def tool_definitions(blocks: list[tuple[int, object]]) -> list[dict]:
    """Every dict, at any nesting depth, that has both `name` and `inputSchema`."""
    return [
        node
        for _, block in blocks
        for node in _walk(block)
        if isinstance(node, dict) and "name" in node and "inputSchema" in node
    ]


def _json_equal(a: object, b: object) -> bool:
    # Compare by JSON type: Python's True == 1 must not pass.
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        assert isinstance(b, dict)
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        assert isinstance(b, list)
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b, strict=True))
    return a == b


def fallback_comparisons(blocks: list[tuple[int, object]]) -> list[tuple[int, bool]]:
    """(opening-fence line, equal?) for each serialized text copy compared to structuredContent."""
    compared: list[tuple[int, bool]] = []
    for line, block in blocks:
        for node in _walk(block):
            if not (
                isinstance(node, dict)
                and "structuredContent" in node
                and isinstance(node.get("content"), list)
            ):
                continue
            for item in node["content"]:
                if not (isinstance(item, dict) and item.get("type") == "text"):
                    continue
                try:
                    parsed = json.loads(item.get("text", ""))
                except (json.JSONDecodeError, TypeError):
                    continue
                if not isinstance(parsed, (dict, list)):
                    continue  # a scalar is prose, not a serialized copy
                compared.append((line, _json_equal(parsed, node["structuredContent"])))
    return compared


def fallback_mismatches(blocks: list[tuple[int, object]]) -> list[int]:
    """Opening-fence lines of blocks whose serialized text copy differs from structuredContent."""
    return sorted({line for line, equal in fallback_comparisons(blocks) if not equal})


def test_block_inventory_is_not_empty():
    blocks = json_blocks(EXAMPLES.read_text())
    assert len(blocks) >= MIN_JSON_BLOCKS
    assert len(tool_definitions(blocks)) >= MIN_TOOL_DEFINITIONS


def test_every_tool_definition_publishes_an_output_schema():
    missing = [
        d["name"]
        for d in tool_definitions(json_blocks(EXAMPLES.read_text()))
        if "outputSchema" not in d
    ]
    assert missing == []


def test_serialized_text_fallback_equals_structured_content():
    # any dict holding both `structuredContent` and a `content` list: each text block that
    # parses as a JSON object or array must equal structuredContent ([3.content-types])
    blocks = json_blocks(EXAMPLES.read_text())
    assert fallback_comparisons(blocks), "no text block was compared; the check is vacuous"
    assert fallback_mismatches(blocks) == []


def test_fallback_status_tool_mirrors_expiry_and_result_location():
    statuses = [
        b["status"]
        for _, b in json_blocks(EXAMPLES.read_text())
        if isinstance(b, dict)
        and isinstance(b.get("status"), dict)
        and b["status"].get("tool") == "slack_get_export_status"
    ]
    assert all("expires_at" in s for s in statuses)
    assert any(s.get("terminal") is True and "result_uri" in s for s in statuses)
    assert any(s.get("terminal") is False for s in statuses)


def test_listen_example_acknowledges_before_notifying():
    methods = [
        (line, b["method"], b["params"])
        for line, b in json_blocks(EXAMPLES.read_text())
        if isinstance(b, dict) and "method" in b
    ]
    ack = [m for m in methods if m[1] == "notifications/subscriptions/acknowledged"]
    upd = [m for m in methods if m[1] == "notifications/resources/updated"]
    assert len(ack) == 1
    assert upd
    assert ack[0][0] < upd[0][0]
    assert ack[0][2]["_meta"]["io.modelcontextprotocol/subscriptionId"] == LISTEN_REQUEST_ID
    assert ack[0][2]["notifications"] == {
        "resourcesListChanged": True,
        "resourceSubscriptions": ["slack://workspace/T0123/flags"],
    }
