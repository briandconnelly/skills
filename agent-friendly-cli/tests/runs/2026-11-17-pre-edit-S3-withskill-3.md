# Scenario 3 (diagnosis) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 54,322 (final-turn context plus output, read from the transcript)
- **Output words:** 467
- **Transcript sha256:** `9a31459ef4dc61945824938c1711ce6d8ad3a02975006c4d07cdc3dff653dc91` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o4`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S3-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Most likely mechanism (evidence: `inferred`, from the `--help` text you supplied verbatim) Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. Pass the documented flag: `depman sync --quiet --yes`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## Ask the depman owners for (tool-side, P0 for agents/automation) Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | `--yes` accepts whatever `sync` was going to ask about, so check what the prompt actually confirms (e.g., rewriting the lockfile) Parts: --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | 'Confirming probes (optional, safe)' offered but no permission requested. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Hang labeled `inferred`; prompt never labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hangs in CI — diagnosis

## What's going on

Most likely mechanism (evidence: `inferred`, from the `--help` text you supplied verbatim): `depman sync` prompts for confirmation ("asks for confirmation first"), and in a non-interactive CI job there is no one to answer, so it blocks reading stdin until the 60-minute timeout.
`--quiet` only reduces output; nothing in the help says it suppresses the prompt, so it doesn't help, and may even hide the prompt text so the log shows nothing.
The tool doesn't detect a non-TTY stdin and fail fast, which is the real defect.

## What to do now (caller-side, you control these)

1. Pass the documented flag: `depman sync --quiet --yes`.
   Only do this if auto-confirming is the intended behavior for that job; `--yes` accepts whatever `sync` was going to ask about, so check what the prompt actually confirms (e.g., rewriting the lockfile) before blanket-approving it.
2. Close stdin so any prompt that remains fails instead of waiting: `depman sync --quiet --yes < /dev/null`.
   This turns a future hang into a fast failure (most prompt libraries error or take the default on EOF).
3. Put a short step-level timeout on it (e.g., `timeout 10m depman sync ...` or the CI step's own `timeout-minutes`) so a regression costs minutes, not an hour.
4. Optionally set `CI=true` if your runner doesn't already; some tools key non-interactive behavior off it, though depman's help doesn't say it does.

## Confirming probes (optional, safe)

If you want to confirm rather than rely on inference, two cheap checks in a throwaway checkout:

- `depman sync --quiet < /dev/null; echo "exit=$?"` — expect it to exit (likely non-zero, or print a prompt) instead of hanging, confirming the prompt is the cause.
- `depman sync --quiet --yes < /dev/null; echo "exit=$?"` — expect success with no wait.

Note `sync` mutates the lockfile, so run these somewhere disposable.

## Ask the depman owners for (tool-side, P0 for agents/automation)

- **Never block when stdin isn't a TTY**: fail immediately with a symbolic error (e.g., `CONFIRMATION_REQUIRED`) and a distinct exit code naming `--yes` as the fix, instead of waiting for input.
- **A machine/non-interactive mode** (e.g., `--non-interactive` or `--machine`) that guarantees no prompts, color, or pagers, declared in a machine-readable schema.
- **Document the prompt and `--yes` together** in `--help` (e.g., "requires `--yes` when non-interactive") and add a `--dry-run` so callers can see what `sync` would change before approving it.
- **A test** that runs `sync` with stdin closed and asserts it exits rather than hangs.

## Assumptions

- I haven't run depman; the diagnosis rests on the help text you quoted.
- If `--yes` plus `< /dev/null` still hangs, the block is something else (e.g., a lock wait, network, or credential prompt from a sub-tool) and is worth capturing with stdout/stderr separated.
~~~~~~
