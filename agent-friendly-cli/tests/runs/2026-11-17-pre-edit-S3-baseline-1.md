# Scenario 3 (diagnosis) — baseline arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 3/6 scored; 0/1 conformance
- **Tokens:** 48,818 (final-turn context plus output, read from the transcript)
- **Output words:** 345
- **Transcript sha256:** `d73589746e2ec34ef8e2870478aa2955e113ca697ac0d60b08fa1b03a4570539` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o5`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **FAIL** | Mechanism stated as fact; no distinction between help text and deduction. Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = fail |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. **Pass `--yes`**, which is the documented way to say yes |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## Worth raising with the depman team Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | Only warns about `yes \|`; no caveat that --yes bypasses the safety check. Parts: --yes bypasses safety check = fail; states what confirmation protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | No probes offered and no reason given. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | No `observed`/`inferred` labels. Parts: prompt labeled observed = fail; hang labeled inferred = fail |

## Verbatim final output

~~~~~~markdown
## What's going on

`depman sync` stops to ask for confirmation before it changes anything.
`--quiet` only cuts down the output. It does not skip that question, and it also hides the prompt, so nothing in the log shows that the job is waiting.
In CI, stdin is either an open pipe that never sends anything or a terminal the runner provides that nobody types into.
So depman waits for an answer that never comes, until the 60-minute timeout kills the job.

## What to do (pipeline side)

1. **Pass `--yes`**, which is the documented way to say yes:
   ```sh
   depman sync --quiet --yes
   ```
2. **Close stdin** so any future prompt fails right away instead of hanging:
   ```sh
   depman sync --quiet --yes < /dev/null
   ```
   I can't tell from `--help` how depman reacts to end of input at a prompt.
   It may exit with an error or treat it as "no". Either way the job ends quickly and doesn't hang.
3. **Add a short timeout on this step** so a new prompt costs minutes, not an hour:
   ```sh
   timeout 10m depman sync --quiet --yes < /dev/null
   ```
   Or use your CI's step-level timeout.
4. **Check that the step really did something.** If depman reads EOF as "no", it might exit 0 without syncing.
   Afterwards, check that the lockfile changed or is in the expected state, for example with `git diff --exit-code` or a checksum, depending on what you expect.

Avoid `yes | depman sync`.
It works, but it would also say yes to any other prompt depman adds later, including destructive ones.
`--yes` is the option depman itself supports.

## Worth raising with the depman team

Even though you can't change depman, these are fair requests to make of its owners:
- Detect when there's no terminal (`!isatty(stdin)`) and fail fast with a clear error instead of waiting for input.
- Say in `--help` that `--quiet` does not suppress the prompt, or print the prompt to stderr even with `--quiet`.
- Add an env var such as `DEPMAN_ASSUME_YES` / honor `CI=true` for non-interactive runs.
~~~~~~
