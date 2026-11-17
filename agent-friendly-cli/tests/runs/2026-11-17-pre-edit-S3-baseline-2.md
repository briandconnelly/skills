# Scenario 3 (diagnosis) — baseline arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/6 scored; 0/1 conformance
- **Tokens:** 48,800 (final-turn context plus output, read from the transcript)
- **Output words:** 309
- **Transcript sha256:** `63bab6eefa81c01d6a0bfbf10201a8c89bf3e480b7badbebf3aeeddefb518653` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **FAIL** | States mechanism as fact ('Depman waits on stdin'); no separation of help text vs deduction. Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = fail |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. Pass the documented non-interactive flag |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## Upstream ask (to the depman team) Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | Check that `--yes` only confirms the sync and doesn't also allow ... deleting or overwriting extra files. Parts: --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | Verify steps given ('Run it once in CI with `--yes` dropped') without asking permission. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | No `observed`/`inferred` labels. Parts: prompt labeled observed = fail; hang labeled inferred = fail |

## Verbatim final output

~~~~~~markdown
## What's going on

`depman sync` asks for confirmation before it changes anything, and `--quiet` doesn't turn that off.
`--quiet` only cuts down on output, so it probably hides the prompt too.
In CI, nobody can type an answer.
Depman waits on stdin (an open pipe that never sends anything, or one that never closes) until the 60-minute timeout kills the job.

## Fix (pipeline-side)

1. Pass the documented non-interactive flag:

   ```sh
   depman sync --quiet --yes
   ```

2. Close stdin as a backstop, so any future prompt fails fast instead of hanging:

   ```sh
   depman sync --quiet --yes < /dev/null
   ```

3. Put a short timeout on the step so a regression costs minutes, not an hour:

   ```sh
   timeout 10m depman sync --quiet --yes < /dev/null
   ```

   You can also use your CI system's per-step timeout.

Don't use `yes | depman sync`.
If the tool ever asks something you don't expect, it silently answers "yes", and `--yes` already does the job explicitly.

## Verify

- Run it once in CI with `--yes` dropped and stdin closed (`< /dev/null`).
  It should exit quickly, probably with an error, which confirms the prompt was the cause.
  It may hang instead.
  That would mean depman reopens `/dev/tty` and only `--yes` helps, so keep the short timeout.
- Then run with `--yes` and check that the job completes and the lockfile result looks right.
- Check that `--yes` only confirms the sync and doesn't also allow something you didn't intend, like deleting or overwriting extra files.
  The help text only says "Assume yes".

## Upstream ask (to the depman team)

These are optional and nonblocking:
- Detect a non-TTY stdin and fail with a clear message instead of blocking.
- Document that `--quiet` doesn't suppress the prompt, or print the prompt to stderr even in quiet mode.
- Consider a `DEPMAN_ASSUME_YES` / `CI=true` env var.
~~~~~~
