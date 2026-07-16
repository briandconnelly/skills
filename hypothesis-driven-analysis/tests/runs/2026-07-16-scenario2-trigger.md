# Scenario 2 — Non-trigger (bounded descriptive query), trigger run

Date: 2026-07-16
Run: skill catalog offered (`hypothesis-driven-analysis`, `agent-friendly-cli`), expected selection not named. Model: Sonnet.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes direct: computes the median and answers | PASS | "The median order value in June was $76.36"; explicitly cited the **direct** route. |
| 2 | No ledger, no hypothesis language, no PPDAC ceremony | PASS | "This is a bounded descriptive query... so it falls under the skill's direct route, which prescribes answering directly with no ledger/ceremony." |

Total: 2/2.

Cost: 3 tool calls, ~33.6k subagent tokens, 20s.

Guardrail scenario: the point is that the skill must *not* add ceremony here, so a passing baseline is expected and is not evidence the scenario is too easy.
The skill was read and then correctly declined its own loop — the routing table did the work it exists to do.
