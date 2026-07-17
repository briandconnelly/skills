# Scenario 12 — Causal question phrased as "how much" (re-run under the current routing table)

Date: 2026-07-17
Run: with the skill, at commit `8fe5863`. Model: dispatched `general-purpose` subagent inheriting the session model (Opus 4.8). Fixture: `tests/fixtures/s1-conversion/`.
Supersedes `2026-07-16-scenario12-causal-routing.md` and `-postfix.md` for carry-over: S12 is among the four that "scored the old table and do not carry over." Same fixture, same prompt, current table.
Clean-room: subagent given only the prompt and the skill.

Tests the precedence override: the phrasing ("how much did launching X improve Y") matches **estimation**, which precedes **full**, but the question asks the causal effect of an unidentified intervention. The rule must send it to `full` and stop it from manufacturing a causal number.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **full**, not estimation, and says why (causal claim overrides phrasing) | PASS | Route `full`; quoted the rule: "a causal question carrying a number, with no design behind it… 'Assigned by anything else… that is full.'" |
| 2 | Does not report a causal effect estimate as though identified | PASS | "How much… cannot be determined from this data — no lift figure is available." All quantities explicitly labeled "descriptively and associationally only." |
| 3 | Uses associative language, or states the causal question is unanswerable from observational data lacking a design | PASS | "the exposure-outcome contrast does not identify a causal effect"; conclusion and limitations are associative throughout. |
| 4 | Catches that the premise is wrong: the campaign is associated with *lower* blended conversion | PASS | "the blended rate fell from 3.12% (pre) to 2.51% (post)"; summer-sale page reached checkout at 0.57% vs 2.68% /home, 3.76% /product. |
| 5 | Leaves the causal campaign hypothesis `UNRESOLVED`; the observational contrast does not mark it `REFUTED` | PASS | Ledger: `H1 causal UNRESOLVED — "a non-identifying design can neither confirm nor refute the causal effect."` |

Total: 5/5.

Cost: 9 tool calls, ~58.1k subagent tokens, 342s.

## Notable: the ledger applied the status rules correctly under its own steam

The run built a full ledger with claim-typed rows and derived status mechanically. Two rules fired correctly without prompting:

- **H1 (causal) UNRESOLVED** rather than REFUTED, even though every observational contrast pointed to "no lift" — because a non-identifying design cannot refute a causal hypothesis. This is exactly the distinction S15 exists to enforce at the status level, reached here independently.
- **H4 (causal) REFUTED** via an *independent* necessary prediction — per-device checkout rates are near-equal (0.15pp gap), so the mild device-mix shift cannot confound — not via the unidentified exposure-outcome contrast. The run refuted a rival on evidence that does not lean on the contrast it is not allowed to use, which is the correct reading of the Conclusion rules.

Carry-over confirmed and then some: the override holds under the current table, and the downstream status discipline the override is supposed to protect also held.

Model caveat: ran on Opus 4.8 vs the 2026-07-16 Sonnet runs.
