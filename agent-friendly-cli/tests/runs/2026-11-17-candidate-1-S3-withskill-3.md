# Scenario 3 (diagnosis) — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 58,585 (final-turn context plus output, read from the transcript)
- **Output words:** 548
- **Transcript sha256:** `f6ffc77a371a23978a89cc5b5a169e6a12a9e8a2a2229e4d1bfa04748854b617` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S3-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | `inferred` — deduced from the help text you supplied ... nobody has yet observed the blocked read. Parts: prompt blocking on stdin in non-TTY job as most likely = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. Pass the explicit confirmation flag: `depman sync --yes --quiet`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | What to ask the depman owners for (tool-side fixes) ... These are for the owning team Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | `--yes` means the sync mutates the lockfile without a human look. Parts: notes bypass = pass; states what was protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | Probe offered ("it's yours to run if you want certainty") but no permission requested first. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table; bullet list of owner asks only. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Only `inferred` label used; documented prompt never labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang: diagnosis

## Most likely mechanism (inferred)

`depman sync` prompts for confirmation before writing the lockfile, and `--quiet` does not answer that prompt.
`--quiet` almost certainly only reduces output; it is not a "non-interactive" or "assume yes" switch.
In CI there is no human, and stdin is either an open-but-silent pipe or inherited, so depman blocks on its read forever, until your 60-minute job timeout kills it.
Because `--quiet` suppresses output, the prompt text itself is probably hidden too, which is why the log shows nothing.

Evidence label: `inferred` — deduced from the help text you supplied (`asks for confirmation first`, `--yes  Assume yes`); nobody has yet observed the blocked read.

## What to do today (caller-side, in your pipeline)

1. Pass the explicit confirmation flag: `depman sync --yes --quiet`.
   This is the documented way to supply the answer; it is the actual fix on your side.
2. Close stdin so any future prompt fails fast instead of hanging: `depman sync --yes --quiet < /dev/null`.
   If depman ever adds another prompt, it hits EOF and (hopefully) errors out instead of waiting.
3. Put a short step-level timeout around it, well under 60 minutes, sized to a normal sync (e.g. `timeout 10m depman sync --yes --quiet < /dev/null`).
   Exit `124` from `timeout(1)` then tells you "hung", distinct from a depman failure.
4. Consider dropping `--quiet` in CI, or at least for the next few runs, so a prompt or error is visible in the log instead of silent.

Caution: `--yes` means the sync mutates the lockfile without a human look.
That is what you want in a pipeline that is meant to sync, but make sure this job is the one that should be writing the lockfile (e.g. not a read-only verification job, where you would want a check/dry-run mode instead if depman has one).

## Optional confirming probe

If you want to confirm before changing the pipeline, one safe probe on a throwaway checkout (not a shared branch): run `depman sync --quiet < /dev/null; echo "exit=$?"` with a short `timeout 60`.
If it hangs or exits 124 there, and `depman sync --yes --quiet < /dev/null` completes, the hypothesis is confirmed.
I have not run this; it's yours to run if you want certainty.

## What to ask the depman owners for (tool-side fixes)

These are for the owning team; you don't need them to unblock.

- **Never prompt when stdin is not a TTY.** Without `--yes` in non-TTY mode, `sync` should fail immediately with a structured error (e.g. code `CONFIRMATION_REQUIRED`, exit `2`, `hint: "re-run with --yes"`) instead of blocking (contract-checklist § Agent-Safe Invocation: non-TTY mode suppresses prompts; § Mutations And Long-Running Work: explicit action triggers).
- **Provide a machine/non-interactive profile** (e.g. `--non-interactive` or `--machine`) that guarantees no prompts on any stream, and document that `--quiet` is output-only (§ Agent-Safe Invocation).
- **Make `--help` say it plainly**: the `sync` summary should name `--yes` as the way to skip the prompt and state the non-TTY behaviour (§ Prose Surfaces).
- **Support `--dry-run` on `sync`** so pipelines can preview lockfile changes without a mutation (§ Mutations And Long-Running Work).
- **Declare a deadline / interrupt behaviour** for `sync`, including what a killed run leaves behind in the lockfile (§ Mutations And Long-Running Work: signal semantics, atomic local writes).
~~~~~~
