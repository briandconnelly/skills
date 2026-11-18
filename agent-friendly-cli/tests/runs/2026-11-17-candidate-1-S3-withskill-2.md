# Scenario 3 (diagnosis) — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 6/6 scored; 0/1 conformance
- **Tokens:** 56,459 (final-turn context plus output, read from the transcript)
- **Output words:** 605
- **Transcript sha256:** `3bf3fb658d541c2f682e234eadd295f64c97c3e8f51e207154d10efda9fce280` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S3-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | I haven't run depman, so this is a deduction from the help text, not an observed hang. Parts: prompt blocking on stdin in non-TTY job as most likely = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. **Pass `--yes`:** `depman sync --quiet --yes`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | What to ask the depman owners for (tool-side) Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | It agrees to whatever the confirmation was protecting, which is a lockfile write. Parts: notes bypass = pass; states what was protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | Probes that would confirm this (only with your OK) |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | Two-row findings table (F1, F2), not a full checklist coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Help line is not labeled `observed` ("not an observed hang" is not a label for the prompt). Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang: diagnosis

## What's going on

**Most likely mechanism (`inferred`, from the `--help` text you quoted):** `depman sync` prompts for confirmation before it changes anything, and in your CI job it is waiting for an answer on stdin that will never arrive.
`--quiet` almost certainly only turns down output.
It does not answer the prompt, so the prompt still blocks, and with `--quiet` you may not even see it in the log.
The job then sits there until the 60-minute timeout kills it.

The help line `sync    Sync the lockfile (asks for confirmation first)` documents the prompt, and the separate `--yes  Assume yes` option is how you skip it.
I haven't run depman, so this is a deduction from the help text, not an observed hang.

## What to do now (pipeline-side, you control this)

1. **Pass `--yes`:** `depman sync --quiet --yes`.
   This is the documented way to skip the prompt.
   Before you add it, confirm that "yes" is the answer you want.
   It agrees to whatever the confirmation was protecting, which is a lockfile write.
2. **Close stdin so a future prompt fails fast instead of hanging:** `depman sync --quiet --yes < /dev/null`.
   If depman later adds another prompt, it reads EOF, and it should error out instead of waiting.
   Some tools hang or loop on EOF too, so treat this as a safety net, not a guarantee.
3. **Put a short step-level timeout on this command** (for example `timeout 10m depman sync ...`, or your CI system's per-step timeout).
   A hang then costs minutes instead of 60, and the step fails in a recognizable way.
4. Optionally, set the common CI signal (`CI=true`) if your runner doesn't already.
   Some tools check it, but depman's help doesn't say it does, so don't rely on it.

Avoid `yes | depman sync`.
It answers "y" to every prompt, including ones you never reviewed.

## What to ask the depman owners for (tool-side)

| Finding | Severity / type | Evidence | Fix direction |
|---|---|---|---|
| F1: `sync` prompts even when stdin is not a TTY, so it hangs in CI. | P0 (blocking behavior in non-TTY mode) / design-issue | `inferred` from the help text | When stdin is not a TTY and no `--yes` was passed, fail immediately with a nonzero exit and a structured error, for example a `CONFIRMATION_REQUIRED` code that names `--yes` as the remedy (contract-checklist § Agent-Safe Invocation: non-TTY mode suppresses prompts). |
| F2: Nothing declares which commands can prompt or what `--quiet` does and doesn't suppress. | P2 / schema-gap | `absence-of-evidence` (the help text only) | Document per command whether it is interactive and which flag makes it non-interactive. Better still, add a machine profile flag (for example `--machine` or `--non-interactive`) that implies no prompts. |

## Probes that would confirm this (only with your OK)

I haven't run anything.
If you can try these safely, in a scratch checkout so a lockfile write doesn't matter:

- `depman sync --quiet < /dev/null; echo "exit=$?"`. It either exits (likely with an error about confirmation) or hangs, which confirms the prompt.
- Run `depman sync` without `--quiet` in an interactive terminal and look at the prompt text, to see exactly what you are agreeing to with `--yes`.

## Open assumptions

- I assumed `--quiet` only reduces output and doesn't imply `--yes`.
  The help you quoted doesn't say either way.
- If the job still hangs with `--yes`, the cause is something else, such as a network call with no timeout or a credential/login prompt.
  Run it with `< /dev/null` and without `--quiet` to see where it stops.
~~~~~~
