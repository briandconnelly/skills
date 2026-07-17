# Scenario 11 — Mini route (re-run under the current routing table)

Date: 2026-07-17
Run: with the skill, at commit `8fe5863`. Model: dispatched `general-purpose` subagent inheriting the session model (Opus 4.8). Fixture: `tests/fixtures/s11-mini/`.
Supersedes `2026-07-16-scenario11-mini.md` for carry-over purposes: that run scored the *old* routing table (`scenarios.md` records S11 among the four that "scored the old table and do not carry over"). This re-run scores the current table. Same fixture, same prompt.
Clean-room: subagent given only the prompt and the skill; no assertions, ground truth, or prior runs.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **mini**: one-paragraph ledger, not the full loop | PASS | Route `mini`; reason keyed to the current table — "a single non-causal claim with no rival explanation competing for it — the skill's routing section names this exact case." Record is the one-paragraph ledger. |
| 2 | No hypothesis table, no Sources/Tests/Amendments sections | PASS | Output carries only the mini ledger block. |
| 3 | Answers correctly that the claim is false, reporting the measured p95 | PASS (window-scoped) | "the claim is not true… p95 = 392.2ms," matching fixture ground truth (p95 ≈ 392). The `>500ms` bar is far from 392, so the verdict is not sensitive to percentile convention. The fixture covers only 00:00–19:59 (a pre-existing, deliberately-retained 20-of-24-hour gap; see `generate.py`), so this is a false verdict over the *covered window*; the run flagged the gap and noted a full-day breach would need an unindicated spike. Read as a pass on the available data, not a verified full calendar day. |

Total: 3/3 (assertion 3 scoped to the covered window, per the note).

Cost: 4 tool calls, ~39.5k subagent tokens, 49s.

Carry-over confirmed: `mini` still fires on its stated condition under the rewritten table, and the run reproduced the 20-of-24-hour coverage caveat that the 2026-07-16 run first surfaced ("the file covers only 00:00–19:59… so this is the p95 over the available window, not a verified full-day figure"). The coverage rule fired again, unprompted, on the current text.

Model caveat: ran on Opus 4.8 vs the 2026-07-16 Sonnet run; both reached `mini` and the same answer.
