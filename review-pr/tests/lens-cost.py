#!/usr/bin/env python3
"""Report what each run of a lens snapshot cost, from the native runner output beside it.

Outside the quality gate: cost informs a reading-procedure change (lens-rubric.md), and never
passes or fails one.

    python3 review-pr/tests/lens-cost.py SNAPSHOT... [--runs] [--tsv PATH]

Columns (whitespace-separated; NA where the runner does not expose a value):
  input_tokens   every input token the model was sent, cached or not (Claude: input + cache
                 read + cache creation; Codex: turn.completed input_tokens, which already
                 includes cached ones)
  cached_tokens  the cached share of input_tokens
  output_tokens  output tokens, reasoning included
  cost_usd       Claude's reported cost; Codex reports none
  turns          Claude num_turns; Codex turn.completed count
  duration_ms    Claude duration; Codex reports none
  commands       Codex command executions; Claude's JSON output has no tool transcript
  skill_commands Codex command executions whose command text names a SKILL.md path: a proxy for body
                 reads, since one command can read many files and a glob names none
Per-snapshot rows give the median over runs; --runs gives one row per run.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

# A native output of "{}" or less is the collector's placeholder for a run that left none.
PLACEHOLDER_BYTES = 2

COLUMNS = [
    "input_tokens",
    "cached_tokens",
    "output_tokens",
    "cost_usd",
    "turns",
    "duration_ms",
    "commands",
    "skill_commands",
]


def claude_cost(path):
    doc = json.loads(path.read_text())
    usage = doc.get("usage") or {}
    parts = [
        usage.get(k)
        for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    ]
    return {
        "input_tokens": sum(p for p in parts if isinstance(p, int))
        if any(isinstance(p, int) for p in parts)
        else None,
        "cached_tokens": usage.get("cache_read_input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cost_usd": doc.get("total_cost_usd"),
        "turns": doc.get("num_turns"),
        "duration_ms": doc.get("duration_ms"),
        "commands": None,
        "skill_commands": None,
    }


def codex_cost(path):
    totals = {"input_tokens": 0, "cached_tokens": 0, "output_tokens": 0}
    turns = commands = skill_commands = 0
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed":
            turns += 1
            usage = event.get("usage") or {}
            totals["input_tokens"] += usage.get("input_tokens") or 0
            totals["cached_tokens"] += usage.get("cached_input_tokens") or 0
            totals["output_tokens"] += usage.get("output_tokens") or 0
        elif (
            event.get("type") == "item.completed"
            and (event.get("item") or {}).get("type") == "command_execution"
        ):
            commands += 1
            if "SKILL.md" in str(event["item"].get("command", "")):
                skill_commands += 1
    if turns == 0:
        totals = dict.fromkeys(totals)
    return {
        **totals,
        "cost_usd": None,
        "turns": turns,
        "duration_ms": None,
        "commands": commands,
        "skill_commands": skill_commands,
    }


def snapshot_rows(snapshot):
    config = json.loads((snapshot / "run-config.json").read_text())
    parse = {"claude": claude_cost, "codex": codex_cost}.get(config.get("runner"))
    if parse is None:
        raise ValueError(f"{snapshot}: unsupported runner {config.get('runner')!r}")
    rows = []
    for k in range(1, int(config["runs"]) + 1):
        native = snapshot / f"run-{k}.json"
        rows.append(
            (
                k,
                parse(native)
                if native.is_file() and native.stat().st_size > PLACEHOLDER_BYTES
                else dict.fromkeys(COLUMNS),
            )
        )
    return rows


def median(values):
    present = [v for v in values if v is not None]
    return statistics.median(present) if present else None


def fmt(value):
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}" if not value.is_integer() else str(int(value))
    return str(value)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("snapshots", type=Path, nargs="+")
    parser.add_argument("--runs", action="store_true")
    parser.add_argument("--tsv", type=Path)
    args = parser.parse_args()
    lines = ["\t".join(["snapshot", "run", *COLUMNS])]
    for snapshot in args.snapshots:
        try:
            rows = snapshot_rows(snapshot)
        except (OSError, ValueError, KeyError) as exc:
            print(f"lens-cost: {exc}", file=sys.stderr)
            return 1
        if args.runs:
            lines += [
                "\t".join([str(snapshot), str(k), *(fmt(row[c]) for c in COLUMNS)])
                for k, row in rows
            ]
        else:
            lines.append(
                "\t".join(
                    [
                        str(snapshot),
                        "median",
                        *(fmt(median([row[c] for _, row in rows])) for c in COLUMNS),
                    ]
                )
            )
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if args.tsv:
        args.tsv.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
