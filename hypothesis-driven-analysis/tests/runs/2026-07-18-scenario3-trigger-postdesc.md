# Scenario 3 — Debugging-discrimination guard after the description edit, Trigger Scoring

Date: 2026-07-18
Run: guard arm dispatched after the description edit (`aa1470e`), testing that the broadened description still yields to a dedicated debugging skill on a reproducible test failure.
Model: Sonnet.
Prompt: Scenario 3's failing test (`test_parse_dates`, `ValueError: unconverted data remains: Z`, reproducible since commit abc123) with the same three-skill catalog stated (amended description verbatim in the transcript's prompt), fix to be described without modifying the repository.
Fixture: `tests/fixtures/s3-bug/test_dateutils.py` (sha256 in the 2026-07-18 S17 evidence artifact).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The debugging skill (or plain debugging) handles it; hypothesis-driven-analysis does not activate | PASS | Opening statement: "I am using the **systematic-debugging** skill (not hypothesis-driven-analysis), because this is a reproducible test failure with a specific error message, and hypothesis-driven-analysis explicitly excludes that case in favor of a dedicated debugging skill." The manifest shows no read of `SKILL.md`. |
| 2 | No investigation ledger is created for a reproducible software failure | PASS | Zero Write/Edit tool_use in the manifest (machine-checked); reproduction and fix verification ran as scratchpad python one-liners, and the answer states "I did not modify anything in the repository." |

Total: 2/2.

The diagnosis itself was sound work: the error signature was reproduced in scratch before being explained (strptime format missing `%z` for the trailing `Z`), and three candidate fixes were executed, not asserted, with the Python-version constraint on `fromisoformat` stated.
One guard run is consistency, not proof, that the S3 carve-out held through the edit.
Cost: 3 tool calls, ~34.0k subagent tokens (harness-reported).
Evidence: `tests/runs/artifacts/2026-07-18-scenario17-trigger-evidence.md`.
