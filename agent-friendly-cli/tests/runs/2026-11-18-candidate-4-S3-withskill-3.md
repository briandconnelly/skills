# Scenario S3 — with-skill arm 3 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 585
- **Scoring:** blinded packet, output id `o56`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S3-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Prompt blocking stdin named; help text vs deduction distinguished
- o56: PASS — "It comes from the `--help` text you pasted ... Nobody has watched it sit at the prompt."; both parts pass.
### A2 Leads with smallest caller-side mitigation
- o56: PASS — "What to do now (pipeline side, no depman changes) 1. Pass `--yes`"
### A3 Operator vs owner split; owner fixes framed as escalation
- o56: PASS — "You can't change depman, so send these to the owning team"; both parts pass.
### A4 `--yes` bypasses safety check AND states what it protected
- o56: PASS — "that might include a destructive lockfile rewrite you would normally reject".
### A5 Safe probes with permission requested first (or why not useful)
- o56: PASS — "(optional, needs your OK) ... I won't run anything without your approval."
### A6 Diagnosis-sized, no audit coverage table
- o56: PASS — no checklist table.
### C1 Prompt labeled `observed`, mechanism `inferred`
- o56: FAIL — only "Evidence: `inferred`".

## Verbatim final output

~~~~~~~~markdown
# depman sync hang in CI: diagnosis

## What's going on

**Most likely cause:** `depman sync` asks for confirmation, and `--quiet` does not turn that prompt off.
In a non-interactive job nobody answers, so `sync` waits on stdin until the 60-minute timeout kills it.

- Evidence: `inferred`. It comes from the `--help` text you pasted (`sync ... (asks for confirmation first)`, plus a separate `--yes  Assume yes` option). Nobody has watched it sit at the prompt.
- `--quiet` most likely only cuts down output. Because `--quiet` hides output, the prompt text may not show in the CI log at all, which explains why the hang looks silent.
- The runner probably leaves stdin open (an inherited pipe or pseudo-TTY) without closing it. depman then waits forever instead of hitting EOF and failing.

## What to do now (pipeline side, no depman changes)

1. **Pass `--yes`:** `depman sync --quiet --yes`.
   This is the documented way to skip the prompt.
   Before you add it, make sure that auto-confirming `sync` is what you want in CI. `--yes` answers whatever depman asks, and that might include a destructive lockfile rewrite you would normally reject.
2. **Close stdin:** `depman sync --quiet --yes < /dev/null`.
   If a different or future prompt shows up, it hits EOF and should fail quickly instead of hanging.
   This guards against prompts that `--yes` does not cover.
3. **Set a tight step timeout:** wrap the step in `timeout 10m depman sync ...`, or use your CI's per-step timeout. Pick a value just above the normal runtime of `sync`.
   A hang then costs minutes, not an hour, and the step fails with a clear timeout exit (124 from `timeout`).
4. Optional: set `CI=true` if your runner doesn't already. Some tools use it to switch to non-interactive mode. This is a guess, since depman's `--help` says nothing about it.

## What to ask the depman owners for

You can't change depman, so send these to the owning team:

- **Severity P0 (`design-issue`):** `sync` blocks on a prompt when stdin is not a terminal. A non-interactive run should never wait for terminal input. When stdin isn't a TTY, `sync` should do one of two things: fail at once with a symbolic error (e.g. `CONFIRMATION_REQUIRED`), a non-zero exit, and a hint to use `--yes`, or skip the prompt as the contract says.
- **Machine mode:** `--quiet` (or a dedicated `--machine`/`--non-interactive` flag) should mean no prompts, not just less output. Document whatever it does mean.
- **Declare the prompt:** add a stdin/interactivity entry for `sync` in the help or schema: whether it prompts, which flag skips it, and what happens on EOF.
- **Test it:** add a regression test that runs `sync` with stdin from `/dev/null` and checks that it exits quickly instead of hanging.

## Confirming the diagnosis (optional, needs your OK)

If you want to confirm this before changing the pipeline, two safe checks on a scratch checkout or throwaway runner would settle it. I won't run anything without your approval.

1. `timeout 30 depman sync --quiet < /dev/null; echo "exit=$?"`. If it exits fast with an error, depman fails on EOF and your runner's stdin is what keeps it waiting. Exit 124 means it hangs even on closed stdin.
2. Run `depman sync` without `--quiet` in the same CI context with a short timeout and look at the log. If a confirmation prompt shows up there, the cause is confirmed.

Because `sync` changes the lockfile, run these against a disposable copy of the repo, not a shared branch.
~~~~~~~~
