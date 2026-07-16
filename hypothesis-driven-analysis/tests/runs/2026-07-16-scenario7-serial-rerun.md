# Scenario 7 — Serial degradation, RERUN against the fixed skill

Date: 2026-07-16
Run: with the skill at commit `e55ba78` (coverage rule rewritten, orientation phase defined, necessary-prediction column added). Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.
Supersedes `2026-07-16-scenario7-serial.md`, which exercised the old wording.
Prompt: as recorded in `scenarios.md` S1, plus the "this harness has NO subagent capability" declaration and the standard execution constraints.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 5 | On a harness without subagents, the same tests run serially with the same ledger | PASS | Full inline ledger; same conclusion as the fan-out-capable run. |
| 4 (S1's) | Mobile undercount caught by the validity check | **FAIL — 4th consecutive miss** | "Data is complete (no nulls), covers both full weeks (4200 and 4971 sessions)." |

Cost: 13 tool calls, ~56.2k subagent tokens, 203s.
Conclusion correctness: **correct** — composition effect; H1 (deploy) refuted on its timing prediction.

## The coverage fix did not work here

This run is the direct test of the F1 gap, and the honest result is negative.

The rewritten rule requires comparing "row counts per period and per segment, and the population rate of each field you rely on", across the periods being contrasted. The run did the *period* half — it reported per-week session totals — and stopped there. It never compared counts per segment per day, which is the only comparison that surfaces a 40% mobile dropout confined to 06-13/06-14.

Worse, the run walked right past the symptom. It observed the mobile share moving 56% → 51% and entered it as H3 (device-mix shift), then refuted H3 by reweighting — treating the share change as a real-world mix effect rather than asking whether the denominator was intact. The undercount is *the reason* mobile share fell, and it was analyzed as though it were signal.

So the rule's new wording bought a partial application: "coverage" now gets mentioned and period totals get compared, but "per segment" is still read as optional. Four with-skill runs against this fixture have now missed the planted defect (S1, S7-fanout, S7-serial on the old wording; S7-serial on the new). The skill-less baseline remains the only run that caught it.

**Do not describe the coverage rule as fixed.** It is changed, and measured, and still insufficient. The `scenarios.md` finding must say so.

## What the fixes did buy

Two other review findings show working evidence in this same run:

- **F5 (orientation phase)** — the run opened with an explicit "Orientation/metric identification" step establishing the join keys, the metric definition, and row counts *before* writing hypotheses, then wrote them without labeling any retrospective. Under the old wording this discovery work was the thing S5 had to log as an amendment.
- **F6 (necessary prediction)** — the hypothesis table carries a "Necessary prediction" column, and H1's refutation cites it directly: "rate drop must begin at/after the deploy timestamp, not before" → REFUTED. Status is now traceable to a declared prediction rather than asserted at conclusion time.
