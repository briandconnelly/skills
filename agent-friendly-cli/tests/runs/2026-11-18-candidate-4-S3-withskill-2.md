# Scenario S3 — with-skill arm 2 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 432
- **Scoring:** blinded packet, output id `o29`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S3-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Prompt blocking stdin named; help text vs deduction distinguished
- o29: PASS — "evidence: `inferred`, from the `--help` text you supplied verbatim ... blocks waiting on stdin"; both parts pass.
### A2 Leads with smallest caller-side mitigation
- o29: PASS — "What to do now (pipeline side, smallest change first) 1. ... `--quiet --yes`"
### A3 Operator vs owner split; owner fixes framed as escalation
- o29: PASS — "What to ask the depman owners for (tool side)"; both parts pass.
### A4 `--yes` bypasses safety check AND states what it protected
- o29: PASS — bypass ("accepts whatever `sync` was going to ask about") and protection ("make sure the job runs against the intended lockfile/workspace").
### A5 Safe probes with permission requested first (or why not useful)
- o29: FAIL — probe offered, "I haven't run anything", no permission request.
### A6 Diagnosis-sized, no audit coverage table
- o29: PASS — no checklist table.
### C1 Prompt labeled `observed`, mechanism `inferred`
- o29: FAIL — only "`inferred`".

## Verbatim final output

~~~~~~~~markdown
# depman sync hangs in CI

## What's going on

Most likely mechanism (evidence: `inferred`, from the `--help` text you supplied verbatim): `depman sync` prompts for confirmation before syncing, and `--quiet` only suppresses output — it does not answer the prompt.
In a non-interactive job there is no one to type "y", so the process blocks waiting on stdin until the 60-minute timeout kills it.
`--quiet` likely makes it worse: the prompt text itself may be suppressed, so the log shows nothing at all.

This is a tool-side defect (blocking on terminal input in non-TTY mode is a P0 for automation), but you can work around it today.

## What to do now (pipeline side, smallest change first)

1. Pass the documented bypass flag: `depman sync --quiet --yes`.
   Only do this if auto-confirming is what you actually want — `--yes` accepts whatever `sync` was going to ask about, so make sure the job runs against the intended lockfile/workspace.
2. Close stdin so any future prompt fails fast instead of hanging: `depman sync --quiet --yes < /dev/null`.
   Depending on how depman reads input, this yields an EOF error or a default answer rather than a hang — either is better than 60 minutes.
3. Put a tight step-level timeout on this command (e.g. a few minutes, via your CI's step timeout or `timeout 300 depman sync ...`), so a new prompt introduced in a later depman release costs minutes, not an hour.
4. Optionally drop `--quiet` in CI (or keep logs verbose on failure) so that if it does block, the prompt text appears in the job log and the cause is obvious.

## Confirming the hypothesis

One cheap, safe probe, if you want certainty before changing the pipeline (I haven't run anything): in a scratch checkout, run `depman sync --quiet < /dev/null; echo "exit=$?"`.
If it exits immediately with an error or EOF message (or hangs, under a short `timeout`), the prompt is the cause.
Avoid running it without `< /dev/null` and a timeout against a real lockfile, since `sync` mutates.

## What to ask the depman owners for (tool side)

- Never prompt when stdin is not a TTY; instead fail fast with a non-zero exit and a symbolic error (e.g. `CONFIRMATION_REQUIRED`) that names `--yes` as the fix.
- Provide a non-interactive / machine flag (or honor `CI=true`) that disables all prompts, and document in `--help` which commands prompt.
- Consider a `--dry-run` for `sync` so pipelines can preview changes before confirming with `--yes`.
- Add a test that runs `sync` with stdin closed and asserts it exits rather than blocks.
~~~~~~~~
