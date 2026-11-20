# 2026-11-19 candidate 5, scenario S3 control, with-skill arm 2

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o76

## Scorer verdicts

## Output o76

Scored:

- A1 PASS: "Most likely mechanism (`inferred` from the `--help` text you quoted): ... the job blocks waiting for an answer to that prompt"; help text cited separately: "`--yes  Assume yes` is the documented way to skip the prompt".
- A2 PASS: "What to do in the pipeline (caller-side, smallest first)" starts "Pass `--yes`."
- A3 PASS: "Escalate to the depman owners (tool-side; you can't change these)".
- A4 FAIL: part 1 pass, "it means \"accept whatever it would have asked about\""; part 2 fail, never states what the confirmation protects (only asks owners: "`--help` should say what the prompt is confirming").
- A5 PASS: "Probes that would confirm it (only if you approve; I haven't run anything)".
- A6 PASS: no coverage table.

Conformance:

- C1 FAIL: only "`inferred`" appears; no `observed` label on the prompt.

## Output

# depman sync hang in CI: diagnosis

## What's going on

**Most likely mechanism (`inferred` from the `--help` text you quoted):** `depman sync` asks for confirmation before it acts, and the job blocks waiting for an answer to that prompt that never arrives.

- `--quiet` controls how much output it prints. It does not answer the prompt, so the prompt still runs (and may not even be printed, which would explain why the log looks idle).
- `--yes  Assume yes` is the documented way to skip the prompt, and the pipeline doesn't pass it.
- The CI job's stdin is probably left open (an inherited pipe, or a pseudo-TTY that some runners allocate) instead of closed. The read never gets EOF, so it waits until the 60-minute timeout kills the job.

## What to do in the pipeline (caller-side, smallest first)

1. **Pass `--yes`.**
   Only do this after you've confirmed that "yes" is what you want sync to do unattended, since it means "accept whatever it would have asked about":
   ```sh
   depman sync --yes --quiet
   ```
2. **Close stdin** so any prompt `--yes` doesn't cover fails fast instead of hanging:
   ```sh
   depman sync --yes --quiet < /dev/null
   ```
3. **Put a timeout on the step that's much shorter than the 60-minute job limit**, so a regression costs minutes, not an hour:
   ```sh
   timeout 10m depman sync --yes --quiet < /dev/null
   ```
   Pick a limit based on how long a normal sync takes.
4. **Keep the output visible while you're debugging.** Run it once without `--quiet`, so a prompt or other message shows up in the log instead of being hidden.
5. **Don't allocate a TTY for this step** (for example, `docker run` without `-t`, and no `script`/`unbuffer` wrappers), so depman can tell it isn't running interactively.

## Probes that would confirm it (only if you approve; I haven't run anything)

Both are safe in a scratch checkout or a disposable runner:

- `depman sync --quiet < /dev/null; echo "exit=$?"`: if it exits right away, or prints an EOF or "confirmation required" error instead of hanging, that confirms the prompt is the cause.
- Run the same CI step once without `--quiet`, with a short `timeout`: the log should show the confirmation prompt right before the hang.

## Escalate to the depman owners (tool-side; you can't change these)

Prioritized:

1. **It should never wait for input when stdin isn't a terminal.**
   When stdin isn't a TTY and `--yes` wasn't passed, `sync` should exit right away with a non-zero exit code and a structured error such as `{"code": "CONFIRMATION_REQUIRED", "message": ..., "hint": "pass --yes"}`, not block.
2. **`--help` should say what the prompt is confirming** (what sync changes or overwrites), so callers can decide whether `--yes` is safe without reading the source.
3. **Document how `--quiet` and the prompt interact.** At the moment the prompt may run with no visible output.
4. **Add a non-interactive mode** (for example, `--non-interactive` or a `--machine` flag) that fails instead of prompting, and document `sync`'s exit codes.
5. **Consider a `--dry-run` flag for `sync`**, so CI can preview changes before applying them with `--yes`.
