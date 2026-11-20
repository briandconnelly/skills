# 2026-11-19 candidate 5, scenario S3 control, with-skill arm 1

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o39

## Scorer verdicts

## Output o39

Scored:

- A1 PASS: "Most likely mechanism (`inferred` from the `--help` text you supplied)" / "depman sits waiting on stdin"; help-text separated: "The help text says just \"Assume yes\"".
- A2 PASS: first action under "What to do now (pipeline side, no depman change needed)" is "Pass `--yes`", then "`< /dev/null`" and "timeout 10m".
- A3 PASS: "What to escalate to the depman team" / "tool-side fixes the owners should make".
- A4 FAIL: part 1 (bypasses safety check) fail, only "check that `--yes` means only \"confirm the sync\""; part 2 (what it protects) weak pass at most, "a sync with confirmation auto-answered would mutate". Not both explicit.
- A5 PASS: "If you want to confirm before changing the pipeline, with your approval:".
- A6 PASS: no coverage table; sections are diagnosis, actions, probes, escalation.

Conformance:

- C1 FAIL: hang labeled "`inferred`", but the prompt is never labeled "observed".

## Output

# depman sync hang in CI

## What's going on

**Most likely mechanism (`inferred` from the `--help` text you supplied):** `depman sync` prompts for confirmation before syncing, and `--quiet` does not turn that prompt off.
`--quiet` usually controls output volume, not interactivity.
In the CI job nobody answers the prompt, so depman sits waiting on stdin until the 60-minute timeout kills the job.

It may be waiting on an open-but-silent stdin (common in CI runners), or the prompt itself may be hidden by `--quiet`, which is why the logs show nothing.

## What to do now (pipeline side, no depman change needed)

1. **Pass `--yes`** — the documented way to answer the prompt:
   ```sh
   depman sync --quiet --yes
   ```
   Before you merge, check that `--yes` means only "confirm the sync" for `sync`. The help text says just "Assume yes", so ask the depman team or test it on a throwaway branch.
2. **Close stdin** so any prompt you didn't expect fails fast instead of hanging:
   ```sh
   depman sync --quiet --yes < /dev/null
   ```
3. **Add a tight step timeout** well under 60 minutes (for example `timeout 10m depman sync ...`, or your CI's per-step `timeout-minutes`). A hang then costs minutes, not an hour, and it fails with a clear signal.
4. **Optionally drop `--quiet`** for a run or two so a prompt or error shows up in the logs.

Don't pipe `yes |` into it. It answers every prompt with "yes", including ones you didn't expect.

## Confirming it (optional, safe probes)

If you want to confirm before changing the pipeline, with your approval:

- `depman sync --help` (read-only) to see the exact text for `--yes` and any `--non-interactive` / `--no-input` flag or env var.
- In a scratch job, run `depman sync --quiet < /dev/null; echo "exit=$?"`. If it exits quickly with an error or EOF instead of hanging, the prompt is confirmed. Run it only against a disposable checkout, because a sync with confirmation auto-answered would mutate.

## What to escalate to the depman team

These are tool-side fixes the owners should make (you can't, and shouldn't have to):

- **Never prompt when stdin isn't a TTY.** In non-interactive mode, a missing confirmation should fail fast with a structured error and a non-zero exit code that tells the caller to pass `--yes`, not block.
- **Document a non-interactive path** in the `sync` help and schema: which flag (`--yes`) or env var skips the confirmation, and that `sync` is mutating.
- **Define `--yes` exactly**: which confirmations it skips, and whether it ever skips destructive ones.
- **Make `--quiet` keep the prompt or its error visible on stderr**, so a blocked run isn't silent.
- Ideally, provide a machine-mode flag (e.g. `--non-interactive`/`--machine`) that implies all of the above.
