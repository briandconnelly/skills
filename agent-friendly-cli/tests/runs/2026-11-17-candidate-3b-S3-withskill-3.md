# Scenario 3 (diagnosis) — with-skill arm 3 (candidate-3b wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` skill files (branch at `fca4a7f`); a second batch of three arms on the same wording, run to gauge variance
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 56,498 (final-turn context plus output, read from the transcript)
- **Output words:** 635
- **Transcript sha256:** `64b5902a0b9d185ee48451b6848fbd816c9fcba1fe71896536f8e5d9102533c5` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/out/S3-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Evidence: `inferred`. It comes from the `--help` text you pasted (`asks for confirmation first`, plus a separate `--yes Assume yes`). Nobody has watched the hang happen. Parts: prompt blocking stdin in non-TTY job as likely cause = pass; distinguishes help text shown vs deduced hang = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | timeout 10m depman sync --yes --quiet < /dev/null |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Report these to the team that owns depman. You don't need to wait on them. Parts: separates operator vs owner fixes = pass; owner fixes framed as escalation to owning team = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | It approves whatever the prompt was guarding. If the prompt shows a diff or warns about a destructive change, CI will now accept it without anyone seeing it. Parts: notes --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | Offers probes ("I have not run anything; these are suggestions for you to run.") but does not request permission first. Parts: one or two safe probes offered = pass; permission requested first = fail |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table; owner asks are a short bullet list. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Only `inferred` used; documented prompt not labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# `depman sync --quiet` hangs in CI

## What's going on

**Most likely cause:** `sync` asks for confirmation before it writes the lockfile.
In your CI job nobody can answer, so it waits on stdin until the 60-minute timeout kills it.
`--quiet` only cuts down output. It does not make the command non-interactive, and the prompt may be one of the things it hides, so the log shows no hint of what the job is waiting for.

- Evidence: `inferred`. It comes from the `--help` text you pasted (`asks for confirmation first`, plus a separate `--yes  Assume yes`). Nobody has watched the hang happen.
- Severity: by agent-friendly-CLI standards this is a `P0` defect in depman, because a CLI must never block on a prompt when it isn't running in a terminal.
  It is depman's bug, but the fix you control is in the pipeline.

## What to do now (pipeline side, in order)

1. **Pass `--yes` and feed it an empty stdin:**
   ```sh
   timeout 10m depman sync --yes --quiet < /dev/null
   ```
   - `--yes` answers the confirmation, so it removes the cause.
   - `< /dev/null` makes any other prompt hit end-of-file instead of waiting. The command then fails or proceeds quickly instead of hanging. Many CI runners already close stdin, but some leave it open.
   - `timeout 10m` (or a job/step timeout at about 2x a normal sync) means that if it does hang again, the job fails in minutes instead of 60.
2. **Confirm `--yes` is what you want.** It approves whatever the prompt was guarding. If the prompt shows a diff or warns about a destructive change, CI will now accept it without anyone seeing it. If that's not OK, run a check or dry-run step first, if depman has one, and fail the job on unexpected changes.
3. **Keep stdout and stderr separate in the logs** (drop `--quiet` while debugging) so that any further prompt or error shows up.

## Confirm the diagnosis (optional, cheap, safe)

If you want proof before you change the pipeline, one or two probes would settle it. Run them on a disposable checkout, not a shared lockfile:

- `depman sync --quiet < /dev/null; echo "exit=$?"`: if it exits quickly (likely with an EOF or "aborted" error) instead of hanging, the prompt is confirmed as the cause.
- Run it once without `--quiet` in an interactive shell to see the prompt text, which tells you what `--yes` would be approving.

I have not run anything; these are suggestions for you to run.

## What to ask the depman owners (tool side)

Report these to the team that owns depman. You don't need to wait on them.

- **Never prompt when stdin isn't a terminal.** When there is no TTY, fail fast with a non-zero exit and a structured error (e.g. code `CONFIRMATION_REQUIRED`) that names `--yes` as the fix, instead of waiting forever. (`P0`, `design-issue`.)
- **Offer a single machine/non-interactive mode** (e.g. `--non-interactive` / `--machine`, or honoring `CI=true`) that turns off every prompt and is listed in the schema/help, so callers don't need to know which commands prompt.
- **Document in `--help` exactly what `--quiet` turns off,** and make sure it never hides a pending prompt.
- **Add a test** that runs `sync` with stdin closed and no TTY, and checks that it exits promptly.

## Assumptions / open questions

- I'm assuming `--yes` applies to `sync`. Help lists it as an option, but it doesn't show whether it's a global or per-command flag. `depman sync --help` would tell you.
- If the job still hangs with `--yes` and `< /dev/null`, the cause is something else: a network call with no timeout, a lock held by another process, or a credential/login prompt that reads from `/dev/tty` directly. Next, capture a stack trace or `strace`/process state while it hangs.
~~~~~~
