# Scenario 3 (diagnosis) — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 54,693 (final-turn context plus output, read from the transcript)
- **Output words:** 352
- **Transcript sha256:** `e0a67dab8b253e04a97ab28125e470a5b04e571cbb71521e5589bbedc199d682` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S3-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Most likely mechanism (`inferred`, from the `--help` text you quoted) Parts: prompt blocking stdin in non-TTY as likely path = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. Pass the documented flag: `depman sync --quiet --yes`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Ask the depman owners for (tool side) Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | "`--yes` auto-approves whatever it was asking about" — asks the user to find out what sync changes rather than stating what the confirmation protects. Parts: notes bypass = pass; states what it protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | I haven't run anything, and would only do so with your OK |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | These map to the Agent-Safe Invocation and Mutations sections (no coverage table) |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | No `observed` label; only `inferred`. Parts: prompt labeled observed = fail; mechanism labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI

## What's going on

**Most likely mechanism (`inferred`, from the `--help` text you quoted):** `depman sync` prompts for confirmation before syncing, and `--quiet` only suppresses output — it does not answer or skip the prompt.
In a non-interactive CI job there is no one to answer, so depman waits on stdin until the 60-minute timeout kills the job.
`--quiet` may even make it worse: it can hide the prompt text, so the log shows nothing at all.

Severity: `P0` (blocking behavior in non-TTY mode), type `design-issue`/`schema-gap` on depman's side — the tool should detect the missing TTY and fail fast instead of waiting.

## What to do today (pipeline side, you control this)

1. Pass the documented flag: `depman sync --quiet --yes`.
2. Close stdin so any *other* prompt fails fast instead of hanging: `depman sync --quiet --yes < /dev/null`.
3. Put a short step-level timeout on it (e.g. `timeout 10m depman sync ...`, or the CI step's own timeout) so a regression costs minutes, not an hour.
4. Before relying on `--yes`, confirm what "sync" changes (lockfile only? network? installs?) — `--yes` auto-approves whatever it was asking about.

## Confirming the hypothesis (optional)

One or two safe probes would settle it; I haven't run anything, and would only do so with your OK:

- In a throwaway checkout, run `depman sync --quiet < /dev/null; echo "exit=$?"` with a short `timeout` — if it hangs or errors on EOF, the prompt is the cause.
- Run `depman sync` (no `--quiet`) in a terminal on the same commit to see the prompt text it's waiting on.

## Ask the depman owners for (tool side)

- Never prompt when stdin isn't a TTY: fail fast with a non-zero exit and a symbolic error (e.g. `CONFIRMATION_REQUIRED`) naming `--yes` as the fix.
- Document in help/schema that `sync` is a mutating, confirming command and which flag makes it non-interactive; consider a `--non-interactive`/machine mode that implies it.
- Keep `--quiet` meaning output only, and say so.

These map to the Agent-Safe Invocation and Mutations sections of the agent-friendly CLI contract checklist.
~~~~~~
