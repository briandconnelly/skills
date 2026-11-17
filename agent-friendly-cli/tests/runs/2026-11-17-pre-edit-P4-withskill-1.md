# Probe P4 — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 60,487 (final-turn context plus output, read from the transcript)
- **Output words:** 708
- **Transcript sha256:** `2414f830c783417c85f647c500fa68d0d34b24e99dd2fd3f439138c489f44b11` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note create` must accept a long body from standard input.
> Write that command's stdin contract.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P4.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P4-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** reading stdin requires an explicit opt-in (`-`, `--stdin`, or equivalent); or, if the contract auto-detects, it declares what happens when stdin is non-terminal but carries no data or never closes. | **PASS** | Stdin is never auto-detected ... `--body-file -` (stdin). |

## Verbatim final output

~~~~~~markdown
# `notectl note create` — stdin contract

Assumptions (unknown from the prompt, stated so they can be corrected): the body is UTF-8 text (Markdown or plain), the note also has a `--title`, and `notectl` has a machine profile `--machine`.

## Rules

1. **Stdin is read only when the caller asks for it.**
   The body comes from exactly one source: `--body <text>`, `--body-file <path>`, or `--body-file -` (stdin).
   Stdin is never auto-detected, so an agent whose harness leaves stdin attached to an inherited pipe or terminal cannot hang or silently ingest unrelated bytes.
2. **Sources are mutually exclusive.**
   Supplying more than one of `--body`, `--body-file` (including `-`) is a usage error: `BODY_SOURCE_CONFLICT`, exit `2`.
   Exactly one source is required; none is `BODY_REQUIRED`, exit `2`.
   No positional body argument exists.
3. **Format.**
   Raw UTF-8 bytes, read to EOF, stored verbatim (no trimming, no newline normalization; one leading UTF-8 BOM is stripped).
   Not JSON-wrapped; title and other fields come from flags.
   Invalid UTF-8 or a NUL byte is `BODY_INVALID_ENCODING`, exit `2`, `details.byte_offset` set.
4. **Maximum size.**
   10 MiB (10,485,760 bytes), declared in the schema as `max_bytes`.
   The CLI stops reading at limit+1 bytes and fails with `BODY_TOO_LARGE`, exit `2`, `details: {"max_bytes": 10485760}`; nothing is created.
5. **Blocking.**
   With `--body-file -`, the command blocks until EOF; the caller must close stdin.
   If stdin is a TTY and machine mode (`--machine`) is active or stdout/stderr is non-TTY, the command does not wait: it fails immediately with `STDIN_IS_TTY`, exit `2`, hint "pipe the body or use --body-file <path>".
   In an interactive human session (all TTYs, no `--machine`) it reads until Ctrl-D.
   `--timeout-ms` applies to the network create, not to stdin; stdin reading has no timeout because the caller controls EOF.
6. **Empty stdin.**
   Zero bytes at EOF is `BODY_EMPTY`, exit `2`, unless `--allow-empty-body` is passed, in which case a note with an empty body is created.
   Whitespace-only input is not empty; it is stored as given.
7. **Atomicity.**
   The body is fully read and validated before any request is sent; a read error, oversize, encoding failure, or interrupt (SIGINT/SIGTERM) while reading creates nothing.
   An interrupt after the create request is sent has an unknown outcome; reconcile with `--idempotency-key` (retry-safe) or `notectl note get` before retrying.

## Error catalog (stdin-related)

All errors are a single JSON object on stderr in machine mode (`stderr_framing: single-error-object`); stdout is empty.

| code | exit | retryable | when |
|---|---|---|---|
| `BODY_REQUIRED` | 2 | false | no body source given |
| `BODY_SOURCE_CONFLICT` | 2 | false | more than one body source |
| `STDIN_IS_TTY` | 2 | false | `--body-file -` with terminal stdin in machine/non-TTY mode |
| `BODY_EMPTY` | 2 | false | zero bytes, no `--allow-empty-body` |
| `BODY_TOO_LARGE` | 2 | false | over `max_bytes` |
| `BODY_INVALID_ENCODING` | 2 | false | non-UTF-8 or NUL |
| `STDIN_READ_ERROR` | 1 | false | I/O error reading stdin |

Example:

```json
{"code":"BODY_TOO_LARGE","message":"Note body exceeds 10485760 bytes.","temporary":false,"field":"--body-file","hint":"Shorten the body or split it into several notes.","details":{"max_bytes":10485760}}
```

## Schema fragment

```json
{
  "command": "note create",
  "mutating": true,
  "stdin": {
    "read": "explicit",
    "trigger": "--body-file -",
    "auto_detect": false,
    "format": "utf-8-text",
    "bom": "strip-leading",
    "max_bytes": 10485760,
    "blocks": "until-eof",
    "tty_in_machine_mode": "error:STDIN_IS_TTY",
    "exclusive_with": ["--body", "--body-file <path>"],
    "empty": "error:BODY_EMPTY unless --allow-empty-body",
    "read_before_side_effects": true
  },
  "flags": {
    "--body": {"type": "string", "description": "Body inline. Exclusive with --body-file. Prefer --body-file for long or untrusted text."},
    "--body-file": {"type": "path", "description": "Read body from file; '-' reads stdin to EOF. Exclusive with --body."},
    "--allow-empty-body": {"type": "boolean", "default": false},
    "--idempotency-key": {"type": "string"}
  }
}
```

## Canonical invocations

```sh
printf '%s' "$BODY" | notectl note create --machine --title 'Design notes' --body-file -
notectl note create --machine --title 'Design notes' --body-file - < ./body.md
```

`--` is supported; no option may follow it.

## Tests to ship

Piped body round-trips byte-for-byte; empty stdin with and without `--allow-empty-body`; exactly `max_bytes` succeeds and `max_bytes+1` fails with nothing created; TTY stdin in machine mode exits `2` immediately without blocking; source conflicts; invalid UTF-8 and NUL; SIGINT mid-read creates nothing; stdin is not read when `--body-file -` is absent even if a pipe is attached.

## Not covered here

Only this command's stdin contract was requested; output class (`record`), auth, and the rest of the command's schema are out of scope.
~~~~~~
