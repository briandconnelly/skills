# Probe P4 — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 61,891 (final-turn context plus output, read from the transcript)
- **Output words:** 713
- **Transcript sha256:** `344a74b9d8961131a11d78ade200a96de5103acbfff9485074a4974a780af384` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note create` must accept a long body from standard input.
> Write that command's stdin contract.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P4.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P4-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** reading stdin requires an explicit opt-in (`-`, `--stdin`, or equivalent); or, if the contract auto-detects, it declares what happens when stdin is non-terminal but carries no data or never closes. | **PASS** | Explicit opt-in, no auto-detection. The body is read from stdin only when the caller passes `--body-file -`. |

## Verbatim final output

~~~~~~markdown
# Stdin contract: `notectl note create`

Scope: this is the stdin contract only (the § Stdin Contract items of the checklist), plus the error codes and tests it directly needs.
Assumption: you own `notectl`; other schema sections (output, ambient state, dry-run, etc.) are out of scope here.

## Design decisions

1. **Explicit opt-in, no auto-detection.** The body is read from stdin only when the caller passes `--body-file -`.
   Auto-detecting a piped stdin is unsafe for agents: harnesses often attach a non-TTY, never-closed stdin, so "is stdin piped?" is a guess that can hang or silently swallow unrelated input.
2. **One body source.** `--body "<text>"`, `--body-file <path>`, and `--body-file -` are mutually exclusive; exactly one is required.
3. **Never wait on a terminal.** If `--body-file -` is given and stdin is a TTY, fail immediately with `STDIN_IS_TTY` instead of prompting.
4. **Empty is an error, not an empty note.** Zero bytes (or whitespace only) fails with `EMPTY_BODY`, unless `--allow-empty-body` is passed.
5. **Bounded size, checked while reading.** Max 1 MiB (1,048,576 bytes); reading stops at the cap+1 byte and fails with `BODY_TOO_LARGE` — the note is not created and nothing is truncated silently.
6. **Bytes are validated before mutation.** Body must be valid UTF-8; a leading BOM is stripped; content is otherwise stored verbatim (no newline normalization, trailing newline preserved).
   The note is created only after stdin hits EOF and all checks pass, so an interrupted or failed read creates nothing.

## Schema fragment

```json
{
  "command": "note create",
  "mutating": true,
  "flags": {
    "--title": {"type": "string", "required": true},
    "--body": {"type": "string", "required": false, "description": "Inline body. Mutually exclusive with --body-file. Use --body-file - for long or multi-line bodies."},
    "--body-file": {"type": "path", "required": false, "description": "Read body from this path; '-' means stdin. Mutually exclusive with --body."},
    "--body-format": {"type": "enum", "values": ["markdown", "text"], "default": "markdown"},
    "--allow-empty-body": {"type": "boolean", "default": false},
    "--stdin-timeout-ms": {"type": "integer", "unit": "ms", "default": 30000, "description": "Max time to wait for stdin EOF after the read starts; 0 disables."}
  },
  "body_source": {"required": "exactly_one", "options": ["--body", "--body-file"]},
  "stdin_contract": {
    "reads": "conditional",
    "read_when": "--body-file is '-'",
    "auto_detected_when_piped": false,
    "accepted_formats": ["utf-8 text"],
    "format_interpretation": "per --body-format; bytes stored verbatim except a leading UTF-8 BOM is stripped",
    "encoding": "utf-8",
    "maximum_input_size": {"value": 1048576, "unit": "bytes"},
    "can_block": "only until EOF or --stdin-timeout-ms; never blocks on a TTY (fails with STDIN_IS_TTY)",
    "requires_eof": true,
    "mutually_exclusive_with": ["--body", "--body-file <path>"],
    "empty_stdin": "error EMPTY_BODY (exit 2) unless --allow-empty-body; whitespace-only counts as empty",
    "when_not_read": "stdin is never read and never consumed",
    "mutation_ordering": "note is created only after the full body is read and validated"
  },
  "errors_possible": [
    {"code": "BODY_SOURCE_REQUIRED", "exit": 2, "retryable": false, "field": "--body"},
    {"code": "BODY_SOURCE_CONFLICT", "exit": 2, "retryable": false, "field": "--body-file"},
    {"code": "STDIN_IS_TTY", "exit": 2, "retryable": false, "field": "--body-file"},
    {"code": "EMPTY_BODY", "exit": 2, "retryable": false, "field": "--body-file", "suppressed_by": ["--allow-empty-body"]},
    {"code": "BODY_TOO_LARGE", "exit": 2, "retryable": false, "field": "--body-file"},
    {"code": "INVALID_ENCODING", "exit": 2, "retryable": false, "field": "--body-file"},
    {"code": "STDIN_TIMEOUT", "exit": 7, "retryable": true, "field": "--stdin-timeout-ms"}
  ]
}
```

`STDIN_TIMEOUT` is retryable because nothing was created (mutation happens after EOF); the caller must re-supply the body since stdin was consumed.

## Canonical invocation

```sh
notectl note create --machine --title "Release notes" --body-file - < notes.md
generate_notes | notectl note create --machine --title "Release notes" --body-file -
```

## Example error (stderr, machine mode, exit 2)

```json
{"code": "BODY_TOO_LARGE", "message": "Body exceeds 1048576 bytes.", "temporary": false, "field": "--body-file", "details": {"max_bytes": 1048576, "read_bytes_at_least": 1048577}, "hint": "Shorten the body or split it into multiple notes."}
```

## Help text (rules first)

```
--body-file PATH   Read the note body from PATH; use '-' for stdin.
                   Exactly one of --body / --body-file is required.
                   stdin: UTF-8, max 1 MiB, read to EOF; empty fails (EMPTY_BODY)
                   unless --allow-empty-body; a TTY stdin fails (STDIN_IS_TTY).
```

## Tests to ship

- Piped body round-trips byte-for-byte (including trailing newline, non-ASCII, a body starting with `-`).
- Empty and whitespace-only stdin → `EMPTY_BODY`, exit 2; with `--allow-empty-body` → success.
- Exactly 1 MiB succeeds; 1 MiB + 1 byte → `BODY_TOO_LARGE`, no note created.
- Invalid UTF-8 → `INVALID_ENCODING`, no note created.
- `--body-file -` under a pseudo-TTY → `STDIN_IS_TTY` immediately, no prompt.
- Open-but-never-closed stdin → `STDIN_TIMEOUT`, exit 7, no note created.
- `--body` with piped stdin: stdin untouched; `--body` + `--body-file` → `BODY_SOURCE_CONFLICT`.
- No body flag with piped stdin → `BODY_SOURCE_REQUIRED` (proves no auto-detection).
~~~~~~
