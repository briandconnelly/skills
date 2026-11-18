# Probe P2 — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 59,398 (final-turn context plus output, read from the transcript)
- **Output words:** 588
- **Transcript sha256:** `668114ae6116c77a5fa7602aa132d037175811fd0f3460ab395a7ab3cce41aca` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `envctl delete <name>` asks 'are you sure?' today.
> Specify exactly what `envctl delete prod` does when stdin is not a terminal and the caller passed no other flags.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it either fails with a branchable error naming the input that supplies the answer, or states that delete is prompt-free by declared design; it never proceeds on an unstated default. | **PASS** | symbolic code: `CONFIRMATION_REQUIRED` ... "field":"--yes" Parts: fails with branchable error naming the input that supplies the answer (or prompt-free by declared design) = pass; never proceeds on an unstated default = pass |

## Verbatim final output

~~~~~~markdown
# `envctl delete prod` with non-TTY stdin and no flags

## Behavior (normative)

1. **No prompt.** stdin is not a terminal, so `envctl` must not prompt and must not read stdin at all (no waiting for a "y" line from a pipe; `delete` declares `stdin: not read`).
2. **No mutation.** Nothing is deleted, no remote call that changes state is made, and no local state (config, cache, lockfiles) is written. The environment `prod` is untouched.
3. **Fail fast with a usage error.** Because the confirmation that the prompt would have collected is missing, the command refuses:
   - exit code: `2` (usage/validation)
   - symbolic code: `CONFIRMATION_REQUIRED`
   - `temporary: false` (retrying the identical call will fail identically)
4. **stdout is empty.** Failure never writes to stdout.
5. **stderr carries the failure.**
   - Default (no `--json`/`--machine`): one human line, e.g.
     `error: refusing to delete environment "prod" without confirmation (stdin is not a terminal); re-run with --yes, or --dry-run to preview`
     No color, no spinner (stderr color/progress follow stderr's own TTY status).
   - In machine mode (`--machine`, or `--json`), the structured error object is the only stderr content (`stderr_framing: single-error-object`):

```json
{"code":"CONFIRMATION_REQUIRED","message":"refusing to delete environment \"prod\" without confirmation: stdin is not a terminal","temporary":false,"resource_id":"prod","field":"--yes","hint":"re-run with --yes to confirm, or --dry-run to preview the deletion","details":{"confirm_flag":"--yes","preview_flag":"--dry-run"}}
```

6. **Order of checks.** Argument validation and existence lookup may run first (read-only): if `prod` does not exist, the command fails with `NOT_FOUND` / exit `3` instead (or exits `0` with `--if-exists`). The confirmation check happens before any mutating call, never after.
7. **Evaluated per stream.** Only stdin's TTY status decides prompting. If stdin *is* a TTY but stdout/stderr are redirected, the prompt is still allowed (written to stderr, never stdout).

## How callers succeed

| Intent | Invocation | Result |
|---|---|---|
| Delete | `envctl delete --yes -- prod` | deletes, exit `0`, record on stdout |
| Preview | `envctl delete --dry-run -- prod` | exit `0`, `dry_run: true`, planned effect; nothing changed |
| Idempotent delete | `envctl delete --yes --if-exists -- prod` | exit `0` whether or not it existed |
| Agent mode | `envctl --machine delete --yes -- prod` | structured JSON on stdout/stderr |

`--yes` is the only bypass; there is no env var (e.g. `ENVCTL_ASSUME_YES`) that silently confirms deletions, so a stray ambient setting cannot turn a non-TTY call into a delete.

## Schema entries for `delete`

```json
{
  "command": "envctl delete",
  "mutating": true,
  "stdin": {"read": false, "can_block": false},
  "interactive": {"prompt": "confirm", "when": "stdin is a TTY and --yes absent",
                  "non_tty_behavior": "fail", "bypass_flag": "--yes"},
  "errors": [
    {"code": "CONFIRMATION_REQUIRED", "exit": 2, "retryable": false, "suppressed_by": ["--yes", "--dry-run"]},
    {"code": "NOT_FOUND", "exit": 3, "retryable": false, "suppressed_by": ["--if-exists"]}
  ]
}
```

## Why not the alternatives

- **Proceed without asking:** an agent or CI script piping output would delete `prod` silently — mutations require an explicit trigger.
- **Read "y" from stdin:** blocks or hangs when stdin is an open pipe, and `yes | envctl delete prod` becomes an accidental confirm path.
- **Exit `0` doing nothing / exit `1`:** hides that nothing happened, or forces callers to parse prose to branch.

## Tests to ship

- non-TTY stdin, no flags → exit `2`, empty stdout, `prod` still exists, stdin never read (test with an open pipe that never closes: must not hang).
- same with `--machine` → stderr is exactly one JSON object with `code: CONFIRMATION_REQUIRED`, `temporary: false`.
- `--yes` deletes; `--dry-run` exits `0` with `dry_run: true` and no mutation.
- missing env → `NOT_FOUND` / `3` takes precedence over the confirmation error.
~~~~~~
