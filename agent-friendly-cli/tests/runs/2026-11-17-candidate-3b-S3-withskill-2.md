# Scenario 3 (diagnosis) — with-skill arm 2 (candidate-3b wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` skill files (branch at `fca4a7f`); a second batch of three arms on the same wording, run to gauge variance
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 55,489 (final-turn context plus output, read from the transcript)
- **Output words:** 664
- **Transcript sha256:** `0c78deb01d3c637c321d057ff1c55dd1b192dd20d42c8ab7cd03e1e9b989e327` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/out/S3-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Evidence: `inferred` from the `--help` text you quoted (`asks for confirmation first`), not from a run. Parts: prompt blocking stdin in non-TTY job as likely cause = pass; distinguishes help text shown vs deduced hang = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. **Answer the prompt explicitly:** `depman sync --quiet --yes`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Suggested fixes to file with the owning team: Parts: separates operator vs owner fixes = pass; owner fixes framed as escalation to owning team = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | `--yes` accepts every confirmation that `sync` asks, including any that might later guard something destructive (for example overwriting local lockfile edits or deleting packages). Parts: notes --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | Offers two probes ("If you want to confirm before you change the pipeline, these two checks are cheap.") but no permission is requested first. Parts: one or two safe probes offered = pass; permission requested first = fail |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table; sections are cause, pipeline changes, probes, owner asks, assumptions. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Hang labeled `inferred`, but the documented prompt is never labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI: diagnosis

## Most likely cause

`depman sync` asks for confirmation before it writes the lockfile, and in your CI job nothing ever answers.
Evidence: `inferred` from the `--help` text you quoted (`asks for confirmation first`), not from a run.

- `--quiet` only reduces output. It does not answer or skip the prompt, so the prompt may not even be printed, and the job looks idle while it waits.
- The process blocks reading stdin. Many CI runners leave stdin open (a pipe or pseudo-TTY that never sends EOF), so the read never returns and never errors.
- depman doesn't seem to notice that it is running without a terminal, so it waits until your 60-minute timeout kills it.

## What to change in the pipeline (caller side, today)

1. **Answer the prompt explicitly:** `depman sync --quiet --yes`.
   This is the documented way to skip the confirmation.
   Before you rely on it, check what `sync` is asking about.
   `--yes` accepts every confirmation that `sync` asks, including any that might later guard something destructive (for example overwriting local lockfile edits or deleting packages).
   Run it only where an unconditional "yes" is what you want, such as a fresh CI checkout.
2. **Close stdin so any future prompt fails fast instead of hanging:** `depman sync --quiet --yes < /dev/null`.
   If a later depman version adds another prompt that `--yes` doesn't cover, the read gets EOF and the command exits (probably non-zero) instead of blocking.
   Depending on your runner, setting `CI=true` may also help, but don't rely on depman honoring it unless its docs say so.
3. **Put a short timeout on this step**, sized to a normal sync (for example `timeout 10m depman sync ...`, or a step-level `timeout-minutes`).
   A future hang then costs minutes, not an hour, and the step's own exit code shows it was killed.
4. **Stop using `--quiet` while you debug.**
   With it on, a hang leaves no clue in the logs.
   Without it, the prompt text should appear in the CI log and confirm the diagnosis.

## Optional confirmation probes

If you want to confirm before you change the pipeline, these two checks are cheap.
Run them in a disposable checkout or a scratch CI job, because `sync` writes the lockfile:

- `timeout 60 depman sync < /dev/null; echo "exit=$?"`. If you see the prompt text and then a fast exit (or exit 124 from `timeout` if it still blocks), the cause is the prompt.
- `timeout 60 depman sync --yes < /dev/null; echo "exit=$?"`. This should finish normally and shows that `--yes` alone clears the wait.

I haven't run either one, so the diagnosis is still `inferred` until one of them confirms it.

## What to ask the depman owners for (tool side)

Under agent/automation-friendliness standards this is a severity **P0** issue: a command that blocks on a prompt in non-interactive use hangs automation.
Suggested fixes to file with the owning team:

- **Don't prompt when stdin isn't a TTY.** In that case, fail right away with a non-zero exit, a clear error on stderr naming the missing flag (for example `confirmation required: rerun with --yes`), and a stable error code that callers can branch on.
- **Show the escape hatch on the command itself.** The `sync` help line should say `--yes` skips the confirmation. Right now that link has to be inferred from a separately listed global option.
- **Offer a machine/non-interactive mode** (a `--no-input` flag or similar, or honoring `CI`) that turns every prompt into an error, so callers aren't depending on a per-prompt `--yes`.
- **Document what the prompt guards against**, so callers can decide whether an unconditional `--yes` is safe.

## Assumptions

- I'm assuming the hang is the confirmation prompt and not a network or lock wait. Nothing you shared rules those out, and the probes above would tell them apart.
- I'm assuming `--yes` applies to `sync`. The help lists it, but doesn't explicitly tie it to `sync`'s prompt.
~~~~~~
