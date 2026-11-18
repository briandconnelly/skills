# Probe P2 — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 58,207 (final-turn context plus output, read from the transcript)
- **Output words:** 498
- **Transcript sha256:** `41b023595ac3cb24194245bc46a26e309c6e976d58789290e7b6725aaff30606` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `envctl delete <name>` asks 'are you sure?' today.
> Specify exactly what `envctl delete prod` does when stdin is not a terminal and the caller passed no other flags.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it either fails with a branchable error naming the input that supplies the answer, or states that delete is prompt-free by declared design; it never proceeds on an unstated default. | **PASS** | {"code":"confirmation_required",..."field":"--yes",..."details":{"retry_with":["--yes"] Parts: fails with branchable error naming the input that supplies the answer (or prompt-free by declared design) = pass; never proceeds on an unstated default = pass |

## Verbatim final output

~~~~~~markdown
# `envctl delete prod` with non-TTY stdin and no flags

Audience: tool author. Task: contract hardening of one command.

## Specified behavior

1. **No prompt, no stdin read.**
   stdin is not a terminal, so per contract-checklist § Agent-Safe Invocation ("stdin controls prompts"; non-TTY suppresses prompts) the confirmation prompt is suppressed.
   `delete` does not read stdin at all (declared in its stdin contract: `reads_stdin: false`), so a piped `y` or an empty/open pipe can never confirm or hang it.
2. **No deletion.**
   A suppressed prompt is not an implicit "yes".
   The mutation requires an explicit action trigger (§ Mutations): in non-interactive use that trigger is `--yes`.
   Without it, nothing is changed — no remote call that mutates, no local state write.
3. **Fail fast with a structured error.**
   - stdout: empty.
   - stderr: exactly one JSON error object (framing `single-error-object`), regardless of whether `--json`/`--machine` was passed, because stdout/stderr TTY status — not flags — governs this path; if stderr is a TTY, the same content may be rendered human-readably, but the exit code is identical.
   - exit code: `2` (usage/validation — a required confirmation flag is missing).

   ```json
   {"code":"confirmation_required","message":"Refusing to delete environment 'prod' without confirmation: stdin is not a terminal.","temporary":false,"field":"--yes","resource_id":"prod","hint":"Re-run with --yes to confirm, or --dry-run to preview.","details":{"retry_with":["--yes"],"preview_with":["--dry-run"]}}
   ```
4. **Ordering.**
   Argument validation happens first: an unknown/invalid name is not resolved remotely before the confirmation check, so the result is deterministic and offline — the command returns `confirmation_required` (exit 2) without network or auth calls.
   (Rationale: the outcome must not depend on whether `prod` exists; existence is checked only on the confirmed or `--dry-run` path, returning `not_found`, exit 3.)
5. **Duration.**
   Returns immediately; no timeout or wait.

## Schema declarations for `delete`

- `mutating: true`, `output_class: record` (the deleted env on success).
- `stdin: {reads: false, can_block: false}`.
- `interactive: {prompt: "confirmation", when: "stdin is a TTY and --yes absent", non_tty: "fail confirmation_required"}`.
- Error catalog: `confirmation_required` → exit 2, `retryable: false`, `reconcile_first: false`, suppressed by `--yes`; `not_found` → exit 3, suppressed by `--if-exists`.
- `--dry-run`: exits 0 with `{"dry_run":true,"would_delete":{...}}`, never byte-identical to real output; needs no `--yes`.
- `--machine` implies non-interactive; it does **not** imply `--yes`.

## Related flag combinations (for completeness)

| Invocation (stdin non-TTY) | Result |
|---|---|
| `envctl delete prod` | no change, `confirmation_required`, exit 2 |
| `envctl delete prod --dry-run` | no change, plan on stdout, exit 0 (or `not_found` exit 3) |
| `envctl delete prod --yes` | deletes; record on stdout, exit 0 |
| `envctl delete prod --yes --if-exists` (already gone) | exit 0, `{"deleted":false,...}` |
| TTY stdin, no flags | prompts as today; anything but `y`/`yes` aborts with `confirmation_declined`, exit 2 |

## Migration note

This changes behavior for any script that currently pipes `yes |` or `echo y |` into `delete`: those will now fail with exit 2 instead of deleting.
That is intended (piped stdin must not authorize a prod deletion), but call it out in the changelog and as a breaking change under `schema_version`.
~~~~~~
