# Scenario 11 — Mini route

Date: 2026-07-16
Run: with the skill, at commit `e55ba78` (post-review-fix skill). Model: Sonnet. Fixture: `tests/fixtures/s11-mini/`.
Exact prompt: as recorded in `scenarios.md` S11, plus the standard execution constraints (read-only fixtures, no git, no reading `tests/` outside the named fixture directory).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **mini**: one-paragraph ledger, not the full loop | PASS | "Route selected: mini — Single stated non-causal claim... testable with at most two bounded read-only probes... not `direct`, since it requires computing a statistic and checking data coverage rather than a pure lookup; not `full`, since there's one claim and no competing causal explanations needed." |
| 2 | No hypothesis table, no Sources/Tests/Amendments sections | PASS | Output carries only the mini ledger block (claim, prediction, probes, outcome, answer). |
| 3 | Answers correctly that the claim is false, reporting the measured p95 | PASS | "The claim is false. Checkout p95 latency on 2026-07-15 was 392.2ms, not >500ms." Matches fixture ground truth. |

Total: 3/3.

Cost: 5 tool calls, ~39.7k subagent tokens, 37s.

Closes the reviewer's "no mini-route test" gap. The route exists, fires on its stated condition, and produces the ceremony it promises — one paragraph, no table.

## The coverage rule found a defect I had not planted

The run reported, unprompted:

> "the file covers only 00:00–19:59Z (20 of 24 hours) for 2026-07-15... the claim cannot be fully verified for the entire calendar day, only for the covered window."

Verified: the fixture spans exactly 19:59:00, i.e. 20 hours of the day the claim is about. I built it that way by accident (1200 one-minute rows, not 1440). No prior run of this suite caught a coverage gap; this one did, on the first outing of the rewritten rule that requires comparing row counts per period rather than scanning for nulls.

That is a real, if small, piece of evidence that the rewritten check does something the old wording did not — the old wording produced three consecutive "no nulls, no dupes, clean" reports against a fixture with a 40% hole in it.

The gap is retained rather than padded to a full day: it is now a live secondary coverage probe, documented as such in `generate.py`. It is labeled honestly as discovered-not-designed.

## Also notable

The run applied the sensitivity rule correctly without being asked to: "p99 (505.7ms) and max (708.7ms) both clear 500ms, so the probe is not saturated/incapable of registering values above the threshold — a true p95 breach would have been detectable by this method." That is a known-positive check on a negative result, which is exactly what the rule demands and what a lazier run would skip.
