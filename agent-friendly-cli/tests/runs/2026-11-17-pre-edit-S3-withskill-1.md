# Scenario 3 (diagnosis) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 55,428 (final-turn context plus output, read from the transcript)
- **Output words:** 488
- **Transcript sha256:** `677e884f2c617efc01ae5275095d42284d8090f3f25fb62791dbcdb68f3e983e` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S3-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Most likely mechanism (evidence: `inferred` from the `--help` text you supplied, not run by me) Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. Pass the documented flag: `depman sync --yes --quiet`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## To escalate to the depman owners (tool-side fixes) Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | "Assume yes" accepts every confirmation, and that could include destructive ones — does not state what the sync confirmation protects. Parts: --yes bypasses safety check = pass; states what confirmation protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | ## Optional probes to confirm (ask before running; safe, read-only) |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Hang labeled `inferred`; prompt never labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang: diagnosis

## What's going on

Most likely mechanism (evidence: `inferred` from the `--help` text you supplied, not run by me): `depman sync` shows a confirmation prompt and waits for an answer on stdin.
`--quiet` only cuts down output; nothing in the help says it skips the prompt.
Since `--quiet` hides output, the prompt may never even show in the job log.
The CI job has no one to answer, so the prompt waits until the 60-minute timeout kills the job.
Depending on the runner, stdin may be an open pipe that never closes, or depman may open `/dev/tty` itself.
Either way it blocks and never fails.

## What to do now (pipeline side, you control this)

1. Pass the documented flag: `depman sync --yes --quiet`.
   This is the fix that matches what depman says it supports.
2. Close stdin so a prompt can't wait forever, e.g. `depman sync --yes --quiet < /dev/null`.
   If some other prompt is still left, it should hit EOF and fail fast instead of hanging.
   Caveat: if depman reads `/dev/tty` directly, this won't help, which is why step 3 matters.
3. Set a short step-level timeout well under 60 minutes (e.g. `timeout 10m depman sync --yes --quiet < /dev/null`, or your CI system's per-step timeout).
   A hang then becomes a quick, clearly labeled failure.
4. Before using `--yes` in CI, check what it agrees to.
   "Assume yes" accepts every confirmation, and that could include destructive ones the help text doesn't list.
   Pin the depman version so new prompts don't get auto-approved without you knowing.

## Optional probes to confirm (ask before running; safe, read-only)

- In a throwaway checkout, run `depman sync --quiet < /dev/null` with a short timeout and capture stdout and stderr separately.
  If it hangs, or exits on EOF with a prompt on stderr, that confirms the hypothesis.
- If it still hangs with `/dev/null` on stdin, it is reading `/dev/tty` or blocking on something else, like a lock or the network.
  Then run it with `--yes` under `timeout` to tell those apart.

## To escalate to the depman owners (tool-side fixes)

- **P0 (design-issue, inferred):** `sync` blocks on a confirmation prompt when stdin isn't a TTY.
  Prompts should be skipped in non-TTY mode, failing fast with a symbolic error and non-zero exit such as `CONFIRMATION_REQUIRED`, plus a hint to pass `--yes`.
  They should never wait.
- **P1/P2 (schema-gap, absence-of-evidence):** no machine/non-interactive profile is documented, and `--quiet` doesn't imply non-interactive.
  Ask for a documented machine mode (e.g. `--non-interactive`/`--machine`) that turns off all prompts.
  The contract should also say which commands prompt and what `--yes` approves.
- **P2 (schema-gap, absence-of-evidence):** `sync` doesn't document its own timeout.
  Ask for a caller-settable timeout and a declared retry behavior.

## Assumptions

- The hang is the prompt, not network or lock contention; the probes above would tell these apart.
- The CI runner leaves stdin open or gives depman a pseudo-TTY.
~~~~~~
