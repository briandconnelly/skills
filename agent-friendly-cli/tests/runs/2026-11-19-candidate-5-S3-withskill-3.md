# 2026-11-19 candidate 5, scenario S3 control, with-skill arm 3

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o38

## Scorer verdicts

## Output o38

Scored:

- A1 PASS: "Most likely mechanism (`inferred` from the `--help` text you supplied, not observed)" / "depman blocks forever on a read waiting for \"y\""; help vs deduction: "`--help` says it \"asks for confirmation first\" ... it does not say it detects a non-TTY stdin ... so assume it doesn't."
- A2 PASS: "What to do now (caller-side, you control these)" leads with "`depman sync --quiet --yes < /dev/null`", then "timeout 10m".
- A3 PASS: "What to ask the depman owners for (tool-side)".
- A4 PASS: part 1 "`--yes` answers whatever the prompt asks, so check what it is confirming"; part 2 "(e.g. rewriting the lockfile)".
- A5 FAIL: "If you want to confirm before changing the pipeline (safe, nothing is synced)" offers probes but does not request permission first.
- A6 PASS: no coverage table.

Conformance:

- C1 FAIL: "`inferred` ... not observed" uses "observed" only negatively; the documented prompt is not labeled `observed`.

## Output

# depman sync hang in CI

## What's going on

Most likely mechanism (`inferred` from the `--help` text you supplied, not observed): `depman sync` prompts for confirmation, `--quiet` only suppresses output and does not answer the prompt, and the CI job's stdin is an open-but-idle pipe (or inherited handle) rather than EOF.
So depman blocks forever on a read waiting for "y", and you see nothing because `--quiet` (and maybe the prompt going to a non-TTY stream) hides the question.
`--help` says it "asks for confirmation first" and offers `--yes`; it does not say it detects a non-TTY stdin and refuses or fails fast, so assume it doesn't.

## What to do now (caller-side, you control these)

1. Add `--yes` to the call, and close stdin so any other prompt fails instead of hangs:
   ```sh
   depman sync --quiet --yes < /dev/null
   ```
   Only do this if auto-confirming the sync is actually what you want in CI; `--yes` answers whatever the prompt asks, so check what it is confirming (e.g. rewriting the lockfile) before you assume it is safe.
2. Bound the step so a future hang costs minutes, not an hour:
   ```sh
   timeout 10m depman sync --quiet --yes < /dev/null
   ```
   or set a step-level timeout in your CI config. Treat exit 124 from `timeout` as "depman hung", distinct from a depman failure.
3. Optionally drop `--quiet` (or keep stderr) while you validate the fix, so a prompt or error is visible in the job log.

## What to ask the depman owners for (tool-side)

- When stdin is not a TTY, never prompt: fail fast with a non-zero exit and a clear error naming `--yes`, instead of blocking.
- A documented non-interactive / machine mode (e.g. `--non-interactive` or `--machine`) that implies no prompts, and an env var such as `DEPMAN_YES=1` / `CI` detection is a nice-to-have.
- Document in `--help` which commands prompt, what `--yes` confirms, and that `--quiet` does not suppress prompts.
- A distinct exit code for "confirmation required but no TTY" so callers can branch on it.

## Optional confirming probes

If you want to confirm before changing the pipeline (safe, nothing is synced):

- `depman sync --quiet < /dev/null; echo "exit=$?"` locally or in a scratch job against a throwaway checkout: if it exits immediately (likely with an EOF/abort error) instead of hanging, the open-stdin-plus-prompt hypothesis is confirmed.
- Run the CI step once without `--quiet` and with a short `timeout`; the log should show the confirmation prompt text before the kill.
