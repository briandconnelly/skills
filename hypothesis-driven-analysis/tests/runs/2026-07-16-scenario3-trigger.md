# Scenario 3 — Trigger discrimination (debugging skill should win)

Date: 2026-07-16
Run: skill catalog offered (`hypothesis-driven-analysis`, `systematic-debugging`), expected selection not named. Model: Sonnet.
Fixture: `tests/fixtures/s3-bug/` — `test_parse_dates` fails with `ValueError: unconverted data remains: Z` on every run.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The debugging skill handles it; hypothesis-driven-analysis does not activate | PASS | "Skill invoked: systematic-debugging — the task is a failing test with an unclear root cause, exactly the trigger case for that skill... so I followed its four phases instead of guessing at a patch." |
| 2 | No investigation ledger is created for a reproducible software failure | PASS | No ledger, no PPDAC framing; went straight to reproduce → root cause → minimal fix → verify. |

Total: 2/2.

Fix was correct (`"%Y-%m-%dT%H:%M:%S"` → `"%Y-%m-%dT%H:%M:%SZ"`), verified by the test passing.
Cost: 5 tool calls, ~40.5k subagent tokens, 23s.

The declared non-goal ("reproducible software failures when the harness has a dedicated debugging skill — that skill wins") holds under test.
