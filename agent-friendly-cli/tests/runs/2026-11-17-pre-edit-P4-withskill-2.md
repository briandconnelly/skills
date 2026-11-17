# Probe P4 — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 61,887 (final-turn context plus output, read from the transcript)
- **Output words:** 1,246
- **Transcript sha256:** `9ef5d67845365b30ef38746251dad8f30c90481e5372dceec45186ac09f09a2e` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note create` must accept a long body from standard input.
> Write that command's stdin contract.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P4.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P4-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** reading stdin requires an explicit opt-in (`-`, `--stdin`, or equivalent); or, if the contract auto-detects, it declares what happens when stdin is non-terminal but carries no data or never closes. | **PASS** | Explicit opt-in, no auto-detection. Stdin is read only when the caller passes `--body-file -`. |

## Verbatim final output

~~~~~~markdown
# Stdin contract: `notectl note create`

Audience assumed: the tool author (you own `notectl`).
Task: contract hardening of one command, so this is the stdin slice of that command's schema plus the error, output, and test entries it requires.

## Design decisions

- **Explicit opt-in, no auto-detection.** Stdin is read only when the caller passes `--body-file -`.
  Auto-detecting a piped stdin is the most common way agents hang: harnesses often leave stdin attached to an open, never-closed pipe, so "is stdin a pipe?" is true and the read blocks forever.
  An explicit flag makes the read intentional and makes the hang impossible when the flag is absent.
- **One body source per call.** `--body "<text>"`, `--body-file <path>`, and `--body-file -` are mutually exclusive.
- **Never read a terminal.** If `--body-file -` is given and stdin is a TTY, fail immediately with a usage error instead of waiting for typed input.
- **Bounded read.** A declared size cap, and a declared idle timeout so a pipe that is open but silent cannot block forever.
- **Bytes in, bytes stored.** UTF-8 text, stored verbatim (no trimming, no newline normalization), so the caller can predict the stored body exactly.

## Schema fragment

Shape dialect: JSON Schema 2020-12 for payloads; the fragment below is the command's schema entry.

```json
{
  "command": "note create",
  "classification": "mutating",
  "latency_class": "network",
  "flags": {
    "--title":      { "type": "string", "required": true, "description": "Note title. Required. Max 200 characters." },
    "--body":       { "type": "string", "required": false, "description": "Inline body. Mutually exclusive with --body-file. Use --body-file - for bodies longer than a few KB or containing arbitrary bytes." },
    "--body-file":  { "type": "string", "required": false, "description": "Path to a UTF-8 file holding the body, or '-' to read the body from stdin. Mutually exclusive with --body." },
    "--stdin-timeout-ms": { "type": "integer", "unit": "ms", "default": 30000, "minimum": 0, "description": "Abort if no stdin bytes arrive for this long. 0 disables the idle timeout. Applies only with --body-file -." },
    "--idempotency-key": { "type": "string", "required": false, "description": "Makes retry after an unknown outcome safe." },
    "--dry-run":    { "type": "boolean", "default": false }
  },
  "end_of_options": true,
  "stdin": {
    "read": "conditional",
    "trigger": "explicit-flag",
    "trigger_flag": "--body-file -",
    "auto_detect_pipe": false,
    "formats": ["text/plain; charset=utf-8", "text/markdown; charset=utf-8"],
    "encoding": "utf-8",
    "bom": "stripped-if-present",
    "normalization": "none; bytes stored verbatim, including trailing newlines",
    "max_bytes": 10485760,
    "read_mode": "read-to-eof-then-commit",
    "can_block": true,
    "blocking_bounds": {
      "tty_stdin": "never waits; fails with STDIN_IS_TTY",
      "idle_timeout_flag": "--stdin-timeout-ms",
      "idle_timeout_default_ms": 30000
    },
    "mutually_exclusive_with": ["--body", "--body-file <path>"],
    "empty": {
      "behavior": "error",
      "error_code": "EMPTY_BODY",
      "description": "Zero bytes before EOF is rejected. To create a note with no body, omit --body and --body-file."
    },
    "when_not_triggered": "stdin is never read, never checked, and may be left open"
  }
}
```

### The seven required declarations, in plain terms

| Item | Contract |
|---|---|
| Is stdin read? | Only with `--body-file -`. Otherwise never touched. |
| Auto-detected or explicit? | Explicit flag only. A piped stdin without the flag is ignored. |
| Accepted formats | UTF-8 text (plain or Markdown). A leading BOM is stripped; invalid UTF-8 is rejected. Body is stored verbatim. |
| Maximum size | 10 MiB (10,485,760 bytes). Exceeding it fails without creating the note. |
| Can it block? | Yes, while waiting for EOF on a pipe. Bounded by `--stdin-timeout-ms` (default 30000 ms of no input). A TTY stdin is never waited on. |
| Mutual exclusion | `--body`, `--body-file <path>`, and `--body-file -` are mutually exclusive; passing more than one is a usage error. |
| Empty stdin | Rejected with `EMPTY_BODY` (exit 2). An empty body is expressed by omitting body flags, not by an empty pipe, so an upstream producer that crashed and wrote nothing cannot silently create a blank note. |

### Ordering and atomicity

The full body is read to EOF and validated (size, UTF-8) before any network call.
A failure during the read leaves no note behind.
SIGINT/SIGTERM during the read: nothing was sent, exit 130/143, no reconciliation needed.
Interrupt after the request was sent: outcome unknown; reconcile with `notectl note find --title "<title>"` or retry with the same `--idempotency-key`.

## Error catalog entries (stdin-related)

Stderr framing in machine mode: `single-error-object`.
Stdout is empty on every failure.

| `code` | exit | `retryable` | `reconcile_first` | When |
|---|---|---|---|---|
| `BODY_SOURCE_CONFLICT` | 2 | false | false | More than one of `--body`, `--body-file` given. `field: "--body-file"`. |
| `STDIN_IS_TTY` | 2 | false | false | `--body-file -` given but stdin is a terminal. |
| `EMPTY_BODY` | 2 | false | false | Zero bytes before EOF. |
| `BODY_TOO_LARGE` | 2 | false | false | Input exceeds `max_bytes`. `details.max_bytes`, `details.read_bytes` (bytes read before stopping). |
| `INVALID_ENCODING` | 2 | false | false | Input is not valid UTF-8. `details.byte_offset` of the first bad sequence. |
| `STDIN_TIMEOUT` | 7 | true | false | No bytes for `--stdin-timeout-ms`. Nothing was sent, so retry is safe. |

Example failure (stderr, exit 2):

```json
{"code":"BODY_TOO_LARGE","message":"Body exceeds the 10485760-byte limit.","temporary":false,"field":"--body-file","details":{"max_bytes":10485760,"read_bytes":10485761},"hint":"Shorten the body or split it into several notes."}
```

Example failure (stderr, exit 2):

```json
{"code":"STDIN_IS_TTY","message":"--body-file - requires piped or redirected stdin; stdin is a terminal.","temporary":false,"field":"--body-file","hint":"Redirect the body into stdin, or pass --body-file with a file path."}
```

## Success output

Output class `record`, stdout, JSON.
The body is not echoed back (it can be 10 MiB); its size and hash are, so the caller can verify what was stored.

```json
{"id":"note_01J9ZK3","title":"Release notes","body_bytes":48213,"body_sha256":"9f2c…","created_at":"2026-11-17T18:04:11Z"}
```

With `--dry-run`, stdin is still read and validated, nothing is created, and the payload adds `"dry_run": true` with no `id`.

## Canonical examples

```sh
# Body from a file, via stdin
notectl note create --title "Release notes" --body-file - < notes.md

# Body from another command
generate-report | notectl note create --title "Weekly report" --body-file -

# Retry-safe creation
generate-report | notectl note create --title "Weekly report" --idempotency-key "weekly-2026-46" --body-file -
```

## Help text (rules first)

```
--body-file <path|->   Read the note body from <path>, or from stdin when <path> is '-'.
                       Stdin is read ONLY with '-'; it is never auto-detected.
                       Max 10 MiB, UTF-8. Empty input is an error (EMPTY_BODY).
                       Fails immediately if stdin is a terminal.
                       Exclusive with --body.
```

## Tests to ship

- `--body-file -` with piped body: stored body is byte-identical (round-trip hash).
- Piped stdin without `--body-file -`: stdin is not read (body empty or from `--body`), command does not block.
- Open, silent pipe without the flag: command completes (no hang).
- Open, silent pipe with the flag: `STDIN_TIMEOUT`, exit 7, after `--stdin-timeout-ms`.
- TTY stdin with `--body-file -`: `STDIN_IS_TTY`, exit 2, no wait (run under a pty).
- Empty stdin: `EMPTY_BODY`, exit 2, no note created.
- Exactly `max_bytes` succeeds; `max_bytes + 1` returns `BODY_TOO_LARGE` and no note.
- Invalid UTF-8: `INVALID_ENCODING` with correct `byte_offset`.
- BOM is stripped; trailing newlines are preserved.
- `--body` with `--body-file -`: `BODY_SOURCE_CONFLICT`, exit 2.
- `--dry-run` with stdin: validates, returns `dry_run: true`, creates nothing.
- SIGINT during read: no note created.
- Schema snapshot includes the `stdin` block above.

## Out of scope here

The rest of the `notectl` contract (machine profile, ambient state and auth, fingerprint, other commands) is not covered by this request; this document is only the stdin slice of `note create` and the entries it forces in the error catalog, output, and tests.
The `notectl note find` reconciliation lookup is assumed to exist; if it does not, `--idempotency-key` becomes the only safe retry path and should be made required for scripted use.
~~~~~~
