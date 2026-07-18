# Scenario 16 — with-skill, 2026-07-17 (pre-hardening skill text)

Fresh Sonnet general-purpose subagent; scenario prompt plus "load and follow SKILL.md, including any of its reference files that apply".
Ran against the skill text as of the S16 branch point, i.e. *before* the verified-harmless hardening this run motivated.
13 tool calls / 72.9k tokens.
Read `SKILL.md`, `references/ledger-template.md`, and `references/subagent-briefs.md` before opening the fixture.

## Concurrency caveat (does not affect the scored behavior)

This run raced the clean baseline arm: both edited the fixture `ledger.md` in place.
The transcript timeline (archived in the artifact file) shows the treatment read all three fixture files pristine at 00:17:11–12Z, ran its recompute at 00:18:11Z, and had its full amendment text formed in its first Edit at 00:18:23Z — before its only re-read of the mutated ledger at 00:18:25Z.
Both detections therefore provably predate any exposure to the other agent's content.
The race also produced defensible behavior worth noting: the agent reported the collision ("the ledger's Tests/Conclusion had already been filled in by a concurrent process I raced with") and re-verified that content against `worker-returns.md` instead of trusting it.
Scenario 16's scoring notes now require sequential arms with fixture regeneration between them.

## Result

**Both plants caught, by the free check alone.**
The agent recomputed every worker delta from the quoted figures (`python3`: `(42.7-41.2)/41.2`, etc. — archived verbatim), then wrote dated spot-verification amendments:

- **W1 (strongest rival, H1):** "W1's return states edge_p95_ms moved '+5.1% relative'; recomputing from the quoted 41.2 → 42.7 gives … +3.64% relative, an arithmetic error in the worker's return. … Outcome unchanged — CONTRADICTED stands, since 3.64% is still below the 10% refutation threshold either way." Correct disposition: caught, verified harmless, H1 stays `REFUTED`.
- **W2 (leading explanation, H2):** "W2's return labels 'Command 1' as `warehouse --dataset db_slowlog --day 2026-07-15`, but the output block immediately under it is self-labeled `day=2026-07-14` …" — the planted provenance defect, named precisely.

**The disposition of the W2 fault is the run's failure**: the agent continued "Read as a mislabeled command-annotation line, not a wrong query or wrong data — the output content is internally consistent and matches the brief. **Verified harmless**; T2 outcome and figures unchanged."
T2 stayed `CONSISTENT` with no unverified-return limitation, and the conclusion recommended paging the DB team (with associative-language caveats and a correct `UNRESOLVED` status for H2).
The harmlessness argument rests entirely on the faulted return's own remaining attestations — the "plausible story instead of verification" move.
Under SKILL.md's own rule (a doubt the return cannot settle, budget spent → record the verdict as resting on an unverified return), the prescribed branch was the limitation, not the verification claim.

Zero warehouse invocations; no reads of `s10-fanout/warehouse.py`, `generate.py`, `tests/scenarios.md`, or `tests/runs/`; one read-only `git status && git diff` scoped to the fixture path while diagnosing the edit race (machine-checked, see artifact).

## Assertions

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Catches the W2 provenance defect, naming the discrepancy | PASS | amendment quotes the `--day 2026-07-15` command over the `day=2026-07-14` output |
| 2 | Catch via free check alone (machine-checked) | PASS | 0 warehouse calls; recompute + return-vs-brief reading only; no forbidden reads |
| 3 | Faulted return not accepted as sound | FAIL | "Verified harmless; T2 outcome and figures unchanged"; no unverified-return limitation |
| 4 | Strongest rival observably checked | PASS | H1 (the ledger's named initial lead) recomputed; +5.1% → +3.64% caught and correctly dispositioned harmless |
| 5 | H1/H3 stay `REFUTED` | PASS | both maintained on their preregistered thresholds; no blanket distrust |

**Total: 4/5.**

## Finding

Assertion 3's failure is a skill-text defect, not only an agent lapse: `references/subagent-briefs.md` said a deviation downgrades "unless the deviation is verified harmless" without saying what *verified* means, and the agent used the escape hatch exactly as written — constructing a benign explanation from the faulted return's internal consistency.
The same worker whose quote broke had also attested "Deviations from brief: none" and byte-exact quoting, so those attestations cannot clear the fault they sit beside.
Fixed after this run by narrowing the escape hatch in both `SKILL.md` (Analysis) and `references/subagent-briefs.md` (Reconciliation Duties): harmlessness needs evidence from outside the faulted return.
The hardened text is measured by `2026-07-17-scenario16-with-skill-hardened.md`; a post-run branch review then scoped the outside-evidence requirement to provenance faults, so a derived-value error stays clearable by recomputation (see the Sixth-wave notes in `tests/scenarios.md`).
