# Scenario 3 (diagnosis) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 6/6 scored; 0/1 conformance
- **Tokens:** 55,864 (final-turn context plus output, read from the transcript)
- **Output words:** 702
- **Transcript sha256:** `5555071261479793eec0799ab8bb1939316c9aaf23ec7fb42f278be3360cf1b7` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S3-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Evidence: `inferred`. This comes from the help text you quoted Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. **Pass the documented non-interactive flag.** |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## What to ask the depman owners (tool-side fixes) Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | "Assume yes" accepts every prompt ... guards something destructive (like dropping or rewriting lockfile entries) Parts: --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | ## Confirming it (optional, needs your OK to run) |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Hang labeled `inferred` but documented prompt never labeled `observed`. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hangs in CI

## What's going on

**Most likely mechanism:** `depman sync` shows a confirmation prompt and waits for an answer on stdin.
Nobody in the CI job can answer it, so the job blocks until the 60-minute timeout kills it.

- Evidence: `inferred`.
  This comes from the help text you quoted (`sync ... (asks for confirmation first)` and the `--yes  Assume yes` option).
  I have not seen it hang myself, and you have not sent a capture of the hang.
- `--quiet` only cuts down output.
  Nothing you quoted says it skips the prompt, and the prompt may well be one of the things it hides, which is why the job looks silent.
- The CI runner probably leaves stdin open: an inherited pipe or a pseudo-TTY, not a closed `/dev/null`.
  depman also apparently doesn't detect non-interactive mode.
  So a read on stdin blocks forever instead of failing fast.
- Severity, if you raise it with the owners: **P0**.
  A command that blocks on a prompt in non-TTY or automation mode hangs pipelines, and the caller can't recover from that reliably.

## What to do now (pipeline side, no depman changes)

1. **Pass the documented non-interactive flag.**

   ```sh
   depman sync --quiet --yes
   ```

   One caution: "Assume yes" accepts every prompt `sync` might show, not only the one you expect.
   If any of those prompts guards something destructive (like dropping or rewriting lockfile entries), CI will now accept it silently.
   Check with the depman owners or the source what `sync` asks before you rely on `--yes`.
   Also check whether a `--dry-run` or a check-only mode exists for CI jobs that only verify.

2. **Close stdin so any future prompt fails fast instead of hanging.**

   ```sh
   depman sync --quiet --yes < /dev/null
   ```

   If a later depman version adds a prompt that `--yes` doesn't cover, the read hits EOF.
   The command then errors out, or at worst takes a default, instead of blocking.

3. **Put a tight timeout on the step,** sized to how long a normal sync takes, not the 60-minute job ceiling.

   ```sh
   timeout 10m depman sync --quiet --yes < /dev/null
   ```

   Treat exit code `124` (from `timeout`) as "depman hung" and say so in the job log, so a regression shows up as a clear failure.

4. **Optional hardening:** drop `--quiet` (or keep stderr) in CI so a prompt or error message lands in the log.
   An actual question in the output makes the next hang easy to diagnose.

## Confirming it (optional, needs your OK to run)

Two cheap probes would turn this from `inferred` to `observed`.
Run them only in a scratch checkout, because `sync` changes the lockfile.

```sh
# 1. Does it block on stdin? Expect: hits EOF quickly and exits non-zero, or prints a prompt to stderr.
timeout 30s depman sync --quiet < /dev/null; echo "exit=$?"

# 2. Does --yes remove the wait? Expect: completes, exit 0.
timeout 30s depman sync --quiet --yes < /dev/null; echo "exit=$?"
```

Capture stdout and stderr separately so you can see which stream the prompt goes to.
If probe 1 exits `124`, depman is waiting on something other than stdin, such as `/dev/tty`, a lock, or the network.
In that case the prompt hypothesis is wrong and needs another look.

## What to ask the depman owners (tool-side fixes)

- **Never prompt when stdin isn't a TTY.**
  If confirmation is required and can't be obtained, exit right away with a non-zero code, a symbolic error (for example `CONFIRMATION_REQUIRED`), and a hint naming `--yes`.
- **Offer a machine/non-interactive mode** (a `--machine`/`--no-input` flag or honoring `CI=true`) that turns off all prompts, pagers, and progress output.
- **Document in `--help` and the schema** exactly what `sync` confirms, what `--yes` approves, and whether `--quiet` affects prompting.
- **Provide `--dry-run`** for `sync` so CI can preview changes without mutating anything.
- **Add a test** that runs `sync` with no TTY on stdin and asserts it exits instead of blocking.

## Assumptions / open questions

- I'm assuming the hang is the confirmation prompt rather than a network or lock wait.
  The probes above would separate the two.
- What does `sync`'s confirmation actually guard, and is blanket `--yes` acceptable for your pipeline?
~~~~~~
