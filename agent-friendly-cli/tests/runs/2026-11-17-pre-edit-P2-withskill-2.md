# Probe P2 — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 58,742 (final-turn context plus output, read from the transcript)
- **Output words:** 651
- **Transcript sha256:** `009540b50cfc5553dc51c20d7f245d8e3fb4ae3fc193016d39b688652005447c` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `envctl delete <name>` asks 'are you sure?' today.
> Specify exactly what `envctl delete prod` does when stdin is not a terminal and the caller passed no other flags.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it either fails with a branchable error naming the input that supplies the answer, or states that delete is prompt-free by declared design; it never proceeds on an unstated default. | **PASS** | {"code":"CONFIRMATION_REQUIRED",..."field":"--yes",..."hint":"Re-run with --yes to delete, or --dry-run to preview." Parts: fails with branchable error naming the input that supplies the answer (or prompt-free by declared design) = pass; never proceeds on an unstated default = pass |

## Verbatim final output

~~~~~~markdown
# `envctl delete prod` with non-TTY stdin and no flags

## Behavior

It refuses to delete, without prompting and without reading stdin.

1. **No prompt.** Prompting is controlled by stdin's TTY status. Because stdin is not a terminal, the CLI does not print "are you sure?" and does not block waiting for an answer, so a caller in CI or an agent never hangs.
2. **No stdin read.** `delete` does not read stdin at all. Piped input such as `yes | envctl delete prod` or `echo y | ...` is **not** treated as confirmation. Declare `stdin: {read: false}` in the schema.
3. **No mutation.** Removing the prompt does not remove the confirmation requirement. Running in non-TTY mode must never turn a guarded delete into a silent one. The environment `prod` is untouched, and nothing is contacted beyond what is needed to validate the arguments (see the note under "Check order").
4. **stdout is empty.** Nothing is written to stdout, because a failure produces no success payload.
5. **stderr carries the structured error and nothing else.** In machine mode, or whenever stderr is not a TTY, stderr contains exactly one JSON object (framing `single-error-object`):

   ```json
   {"code":"CONFIRMATION_REQUIRED","message":"Refusing to delete environment 'prod' without confirmation: stdin is not a terminal.","temporary":false,"field":"--yes","resource_id":"prod","hint":"Re-run with --yes to delete, or --dry-run to preview.","details":{"accepted_confirmations":["--yes"],"preview_flag":"--dry-run"}}
   ```

   If stderr is a TTY, the same facts are printed as one human-readable line. The exit code and the absence of any mutation stay the same.
6. **Exit code `2`** (usage/validation). The invocation is missing a required input, and nothing about the environment is wrong. Retrying unchanged will never succeed, so `temporary` is `false`. Callers branch on `code`. The exit code is only the fallback for shell scripts.

## Check order

Validation runs first and confirmation is checked last. This order lets the error tell the caller what is actually wrong:

- If `prod` does not exist, the command returns `NOT_FOUND` with exit `3`, not `CONFIRMATION_REQUIRED`. Otherwise a caller could add `--yes` and only then learn the target never existed.
  This requires a read-only lookup before the refusal. If you want zero network calls without `--yes`, declare that the existence check is skipped, and accept that the error ordering changes.
- Auth and permission failures (`4`, `5`) also take precedence over `CONFIRMATION_REQUIRED`.

## Ways to proceed (declared in the schema)

| Invocation | Effect |
|---|---|
| `envctl delete --yes -- prod` | Deletes `prod` without a prompt. Success payload on stdout, exit `0`. |
| `envctl delete --dry-run -- prod` | Deletes nothing and reports the planned effect with `"dry_run": true`. Exit `0` if the delete would be valid. |
| `envctl delete --machine -- prod` | The machine profile implies non-interactive mode, **not** `--yes`. The result is the same refusal as above. |
| interactive TTY, no flags | The current "are you sure?" prompt (unchanged). |

## Schema declarations this requires

- `delete.interactive`: prompts only when stdin is a TTY. With no TTY and no `--yes`, it fails with `CONFIRMATION_REQUIRED`.
- Per-command error catalog entry: `CONFIRMATION_REQUIRED → exit 2, retryable: false, reconcile_first: false, suppressed_by: ["--yes"]`.
- `delete` also lists `NOT_FOUND` (3), `UNAUTHENTICATED` (4), `FORBIDDEN` (5) and `CONFLICT` (8), each with its own exit code.
- `--yes` and `--dry-run` are documented flags. When both are passed, `--dry-run` wins and nothing is deleted. State this precedence in the schema.
- Interrupt and timeout semantics for the real delete (for example, `envctl get prod` to reconcile an unknown outcome) belong to the `--yes` path. They do not apply here, because this path never mutates.

## Contract test

Run `envctl delete prod </dev/null` with stderr captured, and assert all of the following:

- Exit code is `2`.
- stdout is empty.
- stderr parses as JSON with `code == "CONFIRMATION_REQUIRED"` and `temporary == false`.
- The process did not block.
- `prod` still exists.

Repeat the run with `yes |` piped in and assert the same results.
~~~~~~
