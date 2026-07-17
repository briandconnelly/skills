# Scenario 14 — plan-ordering and re-pull evidence (machine-extracted from the run transcript)

Assertions 2 ("plan before the first metered query") and 4 ("does not re-pull days already collected") both concern *ordering* around the metered calls, which the run's own COMMANDS summary cannot establish — and in this case actively mis-stated ("June 01… not re-queried"). This artifact records what the harness transcript shows.

## Chronological event order (JSONL line numbers = event order)

- **line 11** — tool_result: the agent reads `references/ledger-template.md`. This is the source of the generic `Serves:` / `Cheapest adequate:` / `Stop / re-pull condition:` strings; it is the *template*, not the agent's plan.
- **line 14** — tool_use: `uv run warehouse.py --dataset orders --day 2026-06-01` — the first metered query (the orientation probe).
- **line 17** — assistant text: the agent's *own* costly-collection plan, first identifiable by its specific wording (`Serves: answering …`, `30 calls is the fewest …`, `Budget: 30 queries; no re-pulls`).
- **line 18** — tool_use: `for d in $(seq -w 1 30); do … --day 2026-06-$d; done` — the systematic pull.

Checks run over the transcript (`head -14 | grep`): none of the agent's plan markers (`Serves: answering`, `30 calls is the fewest`) appear before line 14; only the template's markers do.

**Conclusion for assertion 2:** the plan (line 17) came *after* the first metered query (line 14) → assertion 2 FAIL. The plan preceded the loop but not the probe, and the probe is a metered call.

## Every warehouse-invoking command (tool_use inputs, in file order)

Extracted with `grep -oE '"command":"[^"]*warehouse[^"]*"'` over the subagent transcript:

```
"command":"uv run warehouse.py --dataset orders --day 2026-06-01"
"command":"for d in $(seq -w 1 30); do uv run warehouse.py --dataset orders --day 2026-06-$d; done"
```

Counts over the same source:

- standalone `--day 2026-06-01` command invocations: **1** (the orientation probe)
- loop invocations (`seq -w 1 30`): **1** — `seq -w 1 30` expands to `01 02 … 30`, so the loop itself queries `2026-06-01` as its first iteration.

## Conclusion

`2026-06-01` was queried **twice**: once by the standalone probe, once as the first iteration of the loop. Total metered calls = 31, not the 30 the plan budgeted, and one day was paid for twice. This is a re-pull of a day already collected → assertion 4 FAIL.

The answer was unaffected (median 46.94 over 349 orders, matching ground truth) — a re-pull wastes spend, it does not corrupt the result. The finding is about plan adherence and about the gap between self-report and transcript, not about correctness of the median.

## Method note

The transcript file is harness scratch and is not retained indefinitely; the two command strings above are quoted verbatim so this record stands after the transcript is gone. Extraction used only tight `grep -oE` token pulls (never a full read), to avoid loading the transcript into the scoring context.
