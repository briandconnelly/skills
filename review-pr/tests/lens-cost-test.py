#!/usr/bin/env python3
"""Offline checks for lens-cost.py against synthetic native output of both runners."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

COST = Path(__file__).resolve().parent / "lens-cost.py"
FAIL = []


def snapshot(root, runner, runs):
    root.mkdir(parents=True)
    (root / "run-config.json").write_text(json.dumps({"runner": runner, "runs": len(runs)}))
    for k, body in enumerate(runs, 1):
        (root / f"run-{k}.json").write_text(body)
    return root


def table(*args):
    out = subprocess.run(
        [sys.executable, str(COST), *map(str, args)], capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        FAIL.append(f"lens-cost exited {out.returncode}: {out.stderr}")
        return []
    header, *rows = [line.split("\t") for line in out.stdout.splitlines()]
    return [dict(zip(header, row, strict=True)) for row in rows]


def expect(label, got, want):
    if got != want:
        FAIL.append(f"{label}: got {got!r}, want {want!r}")


with tempfile.TemporaryDirectory() as tmp_name:
    tmp = Path(tmp_name)
    claude = snapshot(
        tmp / "claude",
        "claude",
        [
            json.dumps(
                {
                    "num_turns": 7,
                    "duration_ms": 1000,
                    "total_cost_usd": 0.1,
                    "usage": {
                        "input_tokens": 6,
                        "cache_read_input_tokens": 100,
                        "cache_creation_input_tokens": 50,
                        "output_tokens": 9,
                    },
                }
            ),
            json.dumps(
                {
                    "num_turns": 9,
                    "duration_ms": 3000,
                    "total_cost_usd": 0.3,
                    "usage": {
                        "input_tokens": 4,
                        "cache_read_input_tokens": 300,
                        "cache_creation_input_tokens": 10,
                        "output_tokens": 11,
                    },
                }
            ),
            "{}",
        ],
    )
    rows = table(claude, "--runs")
    expect("claude run 1 input", rows[0]["input_tokens"], "156")
    expect("claude run 1 cached", rows[0]["cached_tokens"], "100")
    expect("claude commands unavailable", rows[0]["commands"], "NA")
    expect("claude failed run", rows[2]["input_tokens"], "NA")
    (median,) = table(claude)
    expect("claude median input skips the failed run", median["input_tokens"], "235")
    expect("claude median cost", median["cost_usd"], "0.2000")

    events = [
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 1000, "cached_input_tokens": 800, "output_tokens": 20},
        },
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "cat .agents/skills/cli-flags/SKILL.md",
            },
        },
        {
            "type": "item.completed",
            "item": {"type": "command_execution", "command": "cat AGENTS.md"},
        },
        {"type": "item.completed", "item": {"type": "agent_message", "text": "SKILL.md"}},
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 500, "cached_input_tokens": 100, "output_tokens": 5},
        },
    ]
    codex = snapshot(tmp / "codex", "codex", ["\n".join(map(json.dumps, events)) + "\nnot json\n"])
    (row,) = table(codex, "--runs")
    expect("codex input sums turns", row["input_tokens"], "1500")
    expect("codex cached", row["cached_tokens"], "900")
    expect("codex turns", row["turns"], "2")
    expect("codex commands", row["commands"], "2")
    expect("codex skill commands ignore messages", row["skill_commands"], "1")
    expect("codex cost unavailable", row["cost_usd"], "NA")

    out = tmp / "cost.tsv"
    table(codex, "--tsv", out)
    expect("tsv written", out.is_file() and out.read_text().startswith("snapshot\trun\t"), True)

if FAIL:
    print("\n".join(f"FAIL: {f}" for f in FAIL))
    sys.exit(1)
print("lens-cost-test: OK")
