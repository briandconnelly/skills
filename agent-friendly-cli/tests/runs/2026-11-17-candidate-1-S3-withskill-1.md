# Scenario 3 (diagnosis) — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 55,054 (final-turn context plus output, read from the transcript)
- **Output words:** 530
- **Transcript sha256:** `5ce401253527fda6d3b7eb4dd1d49684b7db703af2450a072ce0625caf296573` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S3-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | evidence: `inferred` from the `--help` text you supplied, not run Parts: prompt blocking on stdin in non-TTY job as most likely = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | What to do now (pipeline side, smallest change first) 1. **Answer the prompt explicitly:** `depman sync --yes --quiet`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | To escalate to the depman owners (their side, not yours) Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | "Assume yes" auto-approves whatever the prompt was asking, such as rewriting the lockfile or removing entries. Parts: notes bypass = pass; states what was protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | "Confirming it (optional, cheap and safe)" probes given, but no permission requested first. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table; short escalation list. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | No `observed` label on the documented prompt; only `inferred` used. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI

## What's going on

**Most likely mechanism (evidence: `inferred` from the `--help` text you supplied, not run):** `depman sync` shows a confirmation prompt before it does anything, and it waits for terminal input even when nothing is attached to answer it.
`--quiet` only controls how much output it prints. It does not answer the prompt.
In a non-interactive job, stdin is either an open pipe that never sends anything or a stream that stays open, so the read never returns and the job sits there until the 60-minute timeout kills it.
`--quiet` may also be hiding the prompt text, which is why the log shows nothing.

## What to do now (pipeline side, smallest change first)

1. **Answer the prompt explicitly:** `depman sync --yes --quiet`.
   This is the documented non-interactive path, so it's the actual fix.
2. **Close stdin so any other prompt fails instead of hanging:** `depman sync --yes --quiet < /dev/null`.
   If some other prompt shows up (credentials, an overwrite check), it should hit EOF and fail fast instead of blocking.
3. **Put a short timeout around the step:** e.g. `timeout 10m depman sync --yes --quiet < /dev/null`, sized to how long a normal sync takes.
   A hang then costs minutes instead of an hour and gives you a clear exit code (124).
4. Optionally set `CI=true` and leave the job without a TTY (most CI runners already do both). Some tools change behavior based on these, but don't count on depman doing so.

Before you rely on `--yes`, check what it confirms.
"Assume yes" auto-approves whatever the prompt was asking, such as rewriting the lockfile or removing entries.
Make sure that's what you want unattended, for example by running sync on a branch or failing the job if the lockfile diff is unexpected.

## Confirming it (optional, cheap and safe)

Neither of these has been run. Do them in a disposable checkout:

- `depman sync < /dev/null; echo "exit=$?"` without `--quiet`: you should see the confirmation prompt, then a hang or an EOF error. That confirms the prompt is the cause.
- `depman sync --yes --quiet < /dev/null; echo "exit=$?"` should finish without hanging.

## To escalate to the depman owners (their side, not yours)

- **P0 (design-issue): it blocks on a prompt when not attached to a terminal.**
  When stdin isn't a TTY, it should fail right away with a symbolic error and a non-zero exit that names the fix (e.g. "confirmation required; pass `--yes`"), instead of waiting forever.
- **P2 (schema-gap): the help doesn't say how the prompt behaves without a terminal.**
  `--help` mentions the confirmation but not what happens with no terminal, and not that `--quiet` doesn't suppress it.
  The command's contract should say it asks for confirmation, which flag skips it, and what happens with no TTY.
- Suggest a non-interactive mode, like a `--no-input` or `--machine` flag, or honoring `CI`, that turns every prompt into an immediate error.

## Assumptions

- The hang is at the prompt and not somewhere later, like a network or lock wait. The first probe above tells these apart.
- The installed `depman` version is the one whose `--help` you quoted.
~~~~~~
