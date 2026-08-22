---
name: completion-gates
description: Use at the start of work whose completion needs explicit, command-verifiable proof — substantial multi-part deliverables, long autonomous runs, tasks at risk of silent scope narrowing, or tasks whose completion report rests on measured counts or figures. Also use when redoing work that previously came back half done or was reported done prematurely (gate the retry). Invoke via /completion-gates, "gate this work", or "do not stop until it is provably done".
license: MIT
---

# Completion Gates

The failure this skill kills is the unverified completion claim: the done report at 80 percent, the silently narrowed scope, the confident wrong number in a final summary. The countermeasure is a ledger: acceptance criteria and gates written to files before work starts, checks run as commands, and a final status that is computed, not felt.

**Honesty clause — read this first.** Every artifact here (gate files, manifest, hook state) is writable by you, the agent it constrains. This system is an auditable discipline, not enforcement: it cannot make cheating impossible, only visible. Deleting the manifest, weakening a CHECK, or hand-forging evidence all leave records a reviewer will see — and each is a worse outcome for your user than an honest INCOMPLETE.

The parser enforces: pending evidence is unmet; a changed CHECK/EXPECT/EXIT/FOR, a reworded criterion, an added gate, or an ABANDON naming no gate blocks `run` and `status` until amended; evidence from a run under an old spec never satisfies the amended one. It does not judge the *content* of attested evidence or whether you ran a control — those are trust, and the ledger labels them.

**Escape rule (the only permitted ways to change or drop a gate):**
- `ABANDON: <id> <reason>` — the gate stays in the ledger as surrendered.
- `amend --reason "<why>"` — revise, add, or remove gates or criteria; every change lands in the revision log.
- `reset --reason "<why>"` — replace the whole contract; the old contract is snapshotted into the revision log and prior revisions survive.

There is no silent path. `freeze` refuses to overwrite an existing manifest.

## Rule zero: criteria and gates before work

Before real work starts, write `GATES.md` in the working directory (format: [references/gates.md](references/gates.md), template: [templates/GATES.md](templates/GATES.md)):

1. **Criteria**: the user's acceptance criteria, restated faithfully — this is the contract the gates must cover. Don't paraphrase scope away.
2. **Gates**: one checkbox per required outcome, each with a `FOR:` line naming the criteria it proves. Wherever an outcome is checkable by a command, give it `CHECK:` and `EXPECT:` lines so passing is decided by a subprocess, not by your feeling of completion.

Then freeze the contract:

```
node <this-skill-dir>/scripts/gate-check.mjs freeze
```

Freeze validates the file (unique ids, every criterion covered, every gate has an evidence slot, regex EXPECTs compile) and records the specs in a manifest. From here on, changing a gate's CHECK/EXPECT/FOR, rewording a criterion, or adding a gate is *spec drift*: the runner refuses to run until you record the change with `amend --reason "<why>"`, which appends a visible revision. Scope changes are allowed; silent ones are not (see the escape rule above).

## The loop

Work, then prove:

```
node <this-skill-dir>/scripts/gate-check.mjs run       # executes open CHECK gates, records evidence
node <this-skill-dir>/scripts/gate-check.mjs status    # report only
```

Gate resolutions: **proven** (passing run, workspace unchanged since), **attested** (manual gate, checked by hand with evidence recorded), **stale** (workspace changed after the passing run — re-run), **abandoned** (visible surrender via `ABANDON: <id> <reason>`), **unmet** (everything else).

Overall status: **PROVEN** (every gate proven or attested), **INCOMPLETE-HANDOFF** (abandons present, everything else proven — an honest stop, never success), **INCOMPLETE**. Exit codes 0 / 3 / 1; only 0 is done.

Four rules while working:

- **When you feel finished, run `status` instead of concluding.** Composing a summary while gates are open is the failure this skill exists for.
- **Do not simulate work you can do.** If an action is cheap and reversible, do it and observe, rather than reasoning about what it would probably print.
- **When a gate's CHECK is new** (a new test, a bugfix probe), run `gate-check.mjs control <id>` after freezing and before implementing the fix, recording that the CHECK can fail — a check that cannot fail proves nothing. Controls are advisory: the ledger shows each runnable gate as `control: ok | insensitive | invalid | stale | none`, and nothing demotes a gate for a missing control. If the pre-fix state is already gone, say so in the report rather than skipping silently.
- **Manual gates need real evidence** on the `EVIDENCE:` line — a measurement, a quoted output line, a `file:line`. `pending` or a restated claim is unmet, whatever the checkbox says.

## Report rules

- No final report until `status` says PROVEN or you are explicitly handing off. Paste the ledger into the report.
- Re-measure every number you state at report time, or label it unverified. (A per-number gate with a CHECK that measures it is the reliable way to satisfy this.)
- Label attested gates as attested — they are trust, not proof.
- Label gates whose control is `none`, `insensitive`, `invalid`, or `stale` — their CHECK has not been shown to be able to fail.
- Surface every ABANDON with its reason.
- Surface every manifest revision (amend and reset) with its reason — `status` prints them under the ledger.

## Decomposition (large builds)

When the acceptance criteria contain two or more independently verifiable deliverables, split at natural joints into leaves — a leaf is one deliverable with its own gates file under `gates/`.

- **Write interfaces and file ownership into a plan before fanning out**, and freeze all gate files together (`freeze GATES.md gates/*.md`).
- **Dispatch a leaf to a fresh-context subagent when your remaining context cannot hold the leaf's brief, implementation, and verification; when leaves will run in parallel; or when a leaf must not see your in-progress changes.** Otherwise working leaves in-session is fine.
- **A dispatched leaf's brief is the plan's contract section plus that leaf's gates file — never your history.**
- **The driver re-runs every returned leaf's checks itself** (`run` or `run --gate <id>`) — self-certification by the same context that did the work is the weakest evidence there is.
- **Branch/integration outcomes get their own gates.** Locally perfect leaves can still compose into a broken product.

## Stop hook (Claude Code, optional)

`scripts/stop-hook.mjs` blocks ending the turn while gates are open, releases after 6 blocked stops without progress, and lets an all-abandoned state stop as a labeled handoff. It activates only in directories with a frozen manifest. It changes harness behavior, so never install it silently — when a task would clearly benefit, offer it once:

```
node <this-skill-dir>/scripts/install-hooks.mjs        # per-project; --global / --uninstall available
```

## What this skill is not

**Skip gates when the final response will contain no completion claims or completion-critical numbers** — a factual answer, a conversational reply, a single edit you show inline. Gates are for work the user needs *provably* done: substantial multi-part deliverables, long autonomous runs, work at risk of silent scope narrowing, or a completion report that rests on measured counts or figures.
