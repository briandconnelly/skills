# Scenario 3 (diagnosis) — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 54,811 (final-turn context plus output, read from the transcript)
- **Output words:** 441
- **Transcript sha256:** `0d33256dada0910176cbad62a790e5b4fe76f548bae13c6f5e32656a444b1ef6` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S3-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Most likely mechanism (evidence: `inferred` from the `--help` text you supplied, not run) Parts: prompt blocking stdin in non-TTY as likely path = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | Pass the documented flag: `depman sync --quiet --yes`. This is the fix |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Ask the depman owners for (tool side) Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | "yes" means the sync proceeds unconditionally — does not state what the confirmation protects. Parts: notes bypass = pass; states what it protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | with your approval run in a throwaway checkout |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | Severity if this were an audit: `P0` (no coverage table) |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | No `observed` label anywhere; only `inferred`. Parts: prompt labeled observed = fail; mechanism labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI

## What's going on

Most likely mechanism (evidence: `inferred` from the `--help` text you supplied, not run): `depman sync` prompts for confirmation before syncing, and `--quiet` only suppresses output — it does not answer the prompt.
In a non-interactive CI job there is no terminal to answer, so the process waits on stdin (an open-but-silent pipe, or a pty the runner allocates) until the 60-minute timeout kills it.
`--quiet` likely makes this worse: it may also hide the prompt text, so the log shows nothing.

Severity if this were an audit: `P0` — blocking on a prompt in non-TTY mode is a hang in automation.

## Do this today (caller side, you control it)

1. Pass the documented flag: `depman sync --quiet --yes`.
   This is the fix; it is what `--yes  Assume yes` exists for.
   Note that "yes" means the sync proceeds unconditionally — confirm that is what you want in CI (it almost certainly is, since that's what the job intends).
2. Close stdin so any future prompt fails fast instead of hanging: `depman sync --quiet --yes < /dev/null`.
   Many prompt libraries error out on EOF; some may still block or treat EOF as "no", so this is defense in depth, not a guarantee.
3. Put a short step-level timeout on this step (e.g. a few minutes, or `timeout 300 depman sync ...`), so a regression costs minutes, not an hour of runner time.
4. If you can, drop `--quiet` for this step (or capture stderr) so a prompt or error is visible in the log next time.

## Ask the depman owners for (tool side)

- Never prompt when stdin is not a TTY; instead fail immediately with a non-zero exit and a symbolic error such as `CONFIRMATION_REQUIRED` naming `--yes` as the fix.
- Document in `--help` / schema that `sync` requires confirmation and that `--yes` (or a machine-mode flag) is required non-interactively.
- Consider a `--no-input` / machine-mode flag that disables all prompts globally.

## Confirm (optional, two safe probes)

If you want to confirm before changing the pipeline, with your approval run in a throwaway checkout:

- `depman sync --quiet < /dev/null; echo "exit=$?"` — if it exits quickly with an error, or hangs, the prompt is confirmed as the cause.
- `timeout 60 depman sync --quiet --yes < /dev/null; echo "exit=$?"` — should complete without hanging.

Note the first probe may perform the sync if EOF is read as "yes", so only run it against a disposable lockfile.
If the hang persists with `--yes`, the cause is something else (network/lock wait, credential prompt) and worth a stack/strace or verbose run.
~~~~~~
