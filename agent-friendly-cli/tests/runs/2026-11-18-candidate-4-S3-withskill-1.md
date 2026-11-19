# Scenario S3 — with-skill arm 1 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 474
- **Scoring:** blinded packet, output id `o41`; the scorer received the assertion block verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S3-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Prompt blocking stdin named; help text vs deduction distinguished
- o41: PASS — "Mechanism (`inferred` from the `--help` text you quoted, not from a run)"; part1 pass, part2 pass.
### A2 Leads with smallest caller-side mitigation
- o41: PASS — "1. Answer the prompt explicitly: `depman sync --yes --quiet`."
### A3 Operator vs owner split; owner fixes framed as escalation
- o41: PASS — "file them with the team that owns depman"; both parts pass.
### A4 `--yes` bypasses safety check AND states what it protected
- o41: FAIL — bypass pass ("`--yes` approves whatever `sync` was going to ask about"); protection fail (never says what the confirmation guards against).
### A5 Safe probes with permission requested first (or why not useful)
- o41: FAIL — probes offered ("two safe probes would settle it") but no permission request, only "I haven't run these".
### A6 Diagnosis-sized, no audit coverage table
- o41: PASS — no checklist table.
### C1 Prompt labeled `observed`, mechanism `inferred`
- o41: FAIL — only "`inferred`" appears; no "observed" label.

## Verbatim final output

~~~~~~~~markdown
## What's going on

`depman sync` is waiting on a confirmation prompt that nobody in CI will ever answer.

- **Mechanism** (`inferred` from the `--help` text you quoted, not from a run): the help says `sync` "asks for confirmation first", and `--quiet` only reduces output; it does not answer the prompt.
  With `--quiet` the prompt text itself is likely suppressed too, which is why the job log shows nothing before it hangs.
  depman apparently doesn't detect that stdin is not a terminal, so instead of failing fast it blocks on stdin until the 60-minute timeout.
- If the runner leaves stdin attached to an open pipe rather than `/dev/null`, the read never gets EOF, so it waits forever instead of erroring.

## What to do now (pipeline side)

In priority order:

1. **Answer the prompt explicitly:** `depman sync --yes --quiet`.
   This is the documented, non-interactive path.
   Before you ship it, check that a plain "yes" is what you actually want for a lockfile sync in CI.
   `--yes` approves whatever `sync` was going to ask about.
2. **Close stdin so any future prompt fails fast instead of hanging:** `depman sync --yes --quiet < /dev/null`.
   That covers a new prompt added in a later depman release, or one that `--yes` doesn't cover.
3. **Put a short step timeout on it**, sized to a normal sync time plus margin (e.g. `timeout 10m depman sync ...` or the CI step's own `timeout-minutes`), so a hang costs minutes rather than an hour.
4. Optionally set `CI=true` (most CI systems already do) and pin the depman version, so a release can't quietly change the prompt behavior under you.

## What to ask the depman owners to fix

You can't change these, but they're the root cause; file them with the team that owns depman:

- In non-TTY mode, a command that needs confirmation should fail immediately with a non-zero exit and a structured error naming the flag to pass (e.g. "confirmation required; rerun with `--yes`"), not block on stdin.
- Add a single machine profile flag (e.g. `--non-interactive` or `--machine`) that disables all prompts, and document which prompts `--yes` does and doesn't cover.
- Make `--quiet` keep error and prompt text on stderr, so a blocked or failed run is visible in logs.
- Consider a `--dry-run` for `sync` so the pipeline can preview changes before it confirms them.

## Confirming the hypothesis (optional)

If you want proof before changing the pipeline, two safe probes would settle it.
Run them against a scratch checkout, since `sync` modifies the lockfile:

- `depman sync --quiet < /dev/null; echo "exit=$?"`: if it exits quickly with an error, or hangs, that confirms the prompt is the cause.
- `depman sync --yes --quiet < /dev/null; echo "exit=$?"`: it should finish without blocking.

I haven't run these; everything above comes from the help text you supplied.
~~~~~~~~
