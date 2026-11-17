# Decision-Point Probes for agent-friendly-cli

A probe hands an arm the one decision a rule governs, so a wording change can be measured without waiting for a free-form run to reach that decision on its own.
Scenarios in [scenarios.md](scenarios.md) measure whole tasks; probes measure single rules.

## How to run

1. Every probe arm has the skill loaded and is told not to read `tests/`.
2. Run each probe on the old wording first, then on the candidate wording, with the identical prompt; only the skill files differ.
3. Each cell is three arms, reported as x/3.
4. No prompt names the check under test; a prompt that asks for the check suppresses the failure it is meant to find.
5. Score with a fresh scorer that receives the pass criterion verbatim and the output without its arm label.
   A criterion with several parts gets a cited pass or fail per part and passes only if every part does.
6. Archive each arm under `tests/runs/<date>-<probe>-<wording>-<n>.md` in the run-record format scenarios use.

## Probes

### P1: Recovery after an unkeyed create times out

Rule under test: the reconciliation rule in `references/contract-checklist.md` § Mutations And Long-Running Work.

**Prompt:**

> `notectl note create --title T` timed out after 15 s.
> The caller passed no idempotency key.
> The API's search index lags writes by up to 30 s.
> Write the error payload and tell the caller how to recover.

**Passes when** all three hold:

- It does not present an empty lookup as proof the create did not commit.
- It does not offer a key first added on the retry as making that retry safe.
- Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry.

### P2: A confirmation that cannot be asked

Rule under test: what a command does when it needs an answer it cannot prompt for (§ Agent-Safe Invocation).

**Prompt:**

> `envctl delete <name>` asks 'are you sure?' today.
> Specify exactly what `envctl delete prod` does when stdin is not a terminal and the caller passed no other flags.

**Passes when** it either fails with a branchable error naming the input that supplies the answer, or states that delete is prompt-free by declared design; it never proceeds on an unstated default.

### P2c: Control for P2

A tool whose deletes never prompted must not gain a confirmation step.

**Prompt:**

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

**Passes when** it does not add a mandatory confirmation step.

### P3: What root help says

Rule under test: whether root `--help` leads a caller to the contract (§ Prose Surfaces).

**Prompt:**

> Here is the schema for `widgetctl`.
> Write the output of `widgetctl --help`.
>
> [the schema JSON from `references/examples.md` §1, pasted from the tree under test]

**Passes when** the help text names the schema command and the machine flag.

### P4: A command that reads standard input

Rule under test: explicit opt-in versus auto-detection (§ Stdin Contract).

**Prompt:**

> `notectl note create` must accept a long body from standard input.
> Write that command's stdin contract.

**Passes when** reading stdin requires an explicit opt-in (`-`, `--stdin`, or equivalent); or, if the contract auto-detects, it declares what happens when stdin is non-terminal but carries no data or never closes.

### P5: Deliverable fit on a hardening request

Rule under test: Done Criteria for hardening tasks in `SKILL.md`.

**Prompt:** scenario R1's prompt in [scenarios.md](scenarios.md), unchanged; P5 reuses the R1 with-skill arms.

**Fit** is met when the response has no checklist coverage table and its word count is at most 1.5 times the median word count of the same wave's R1 baseline arms.
R1's scored assertions are scored as usual.

## Verdict procedure

Preregistered on 2026-11-17, before any arm ran.
Stage 1, eligibility, uses the old-wording arms and decides whether a candidate edit is written at all.
Stage 2, acceptance, uses the candidate-wording arms and decides whether the candidate stays.

| Probe | Old wording | Stage 1 | Candidate wording | Stage 2 |
| --- | --- | --- | --- | --- |
| P2, P3, P4 | at least 1/3 fails | eligible: write the candidate edit | 3/3 pass and its control holds | accept |
| P2, P3, P4 | at least 1/3 fails | eligible | under 3/3, or control fails | revise once and rerun that cell; still failing: revert the edit and open an issue |
| P2, P3, P4 | 3/3 pass | declined: no edit; record "current text already induces this" | not run | — |
| P1 | any result | eligible regardless: the failure is archived at `runs/2026-10-11-scenario1-with-skill-final.md` lines 616–623; a 3/3 old-wording pass is recorded as "one archived instance, not reproduced" | 3/3 pass | accept |
| P1 | any result | eligible | under 3/3 | revise once and rerun; still failing: revert and open an issue |
| P5 | any arm misses Fit | eligible | 3/3 meet Fit and no R1 scored assertion drops below its old-wording x/3 | accept |
| P5 | any arm misses Fit | eligible | otherwise | revise once and rerun; still failing: revert and open an issue |
| P5 | 3/3 meet Fit | declined | not run | — |
| Scenario 1 error-fallback assertion | any component under 3/3 | eligible | every component 3/3 | accept; otherwise revise once, then revert and open an issue |
| Scenario 1 error-fallback assertion | all components 3/3 | declined | not run | — |

Controls: P2c is P2's control and must be 3/3 on the candidate wording.
Scenario 2b is the control for every edit to § Severity or § Agent-Safe Invocation and must be 3/3 on the candidate wording.

## Results

| Date | Probe | Wording | Tree | Passed | Stage | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-17 | P1 | old | `b6958e0` | 0/3 | Stage 1: eligible | Fails the criterion as written in all three arms: each treats an empty lookup as establishing that the create did not commit and recommends retrying on it. All three first wait out the stated 30 s index lag, which is safer than the archived instance (retry on an immediate empty lookup) but still rests the retry on a search, not on the original attempt's outcome. Records: `runs/2026-11-17-pre-edit-P1-withskill-{1,2,3}.md`. |
| 2026-11-17 | P2 | old | `b6958e0` | 3/3 | Stage 1: declined | Current text already induces this: every arm fails closed with a branchable error naming the confirming input. No edit for the unanswerable-prompt rule. Records: `runs/2026-11-17-pre-edit-P2-withskill-{1,2,3}.md`. |
| 2026-11-17 | P2c | old | `b6958e0` | 3/3 | Stage 1: control baseline | No arm adds a mandatory confirmation step. Records: `runs/2026-11-17-pre-edit-P2c-withskill-{1,2,3}.md`. |
| 2026-11-17 | P3 | old | `b6958e0` | 0/3 | Stage 1: eligible | Every arm names `--machine` and none names a schema command. Probe limitation: the pasted schema's `command_tree` lists no schema command, and all three arms say they omitted it for that reason, so the failure is partly the fixture's; read the candidate-wording result with that in mind. Records: `runs/2026-11-17-pre-edit-P3-withskill-{1,2,3}.md`. |
| 2026-11-17 | P4 | old | `b6958e0` | 3/3 | Stage 1: declined | Current text already induces this: every arm requires an explicit opt-in to read stdin. No edit for the stdin-preference rule. Records: `runs/2026-11-17-pre-edit-P4-withskill-{1,2,3}.md`. |
| 2026-11-17 | P5 | old | `b6958e0` | 0/3 meet Fit | Stage 1: eligible | With-skill responses run 1,334, 1,827, and 1,916 words against a baseline median of 645 (limit 968), and 2 of 3 contain a checklist coverage table. R1 scored assertions for the same arms: A1 1/3 A2 3/3 A3 3/3 A4 3/3 A5 3/3. Records: `runs/2026-11-17-pre-edit-R1-withskill-{1,2,3}.md`. |
| 2026-11-17 | Scenario 1 error-fallback assertion | old | `b6958e0` | unanticipated-failure code 0/3; transport failure per networked command 3/3; unlisted-code handling 0/3 | Stage 1: eligible | Records: `runs/2026-11-17-pre-edit-S1-withskill-{1,2,3}.md`. |
