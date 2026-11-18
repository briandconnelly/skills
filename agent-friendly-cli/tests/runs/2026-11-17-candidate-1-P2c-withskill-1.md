# Probe P2c — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 64,882 (final-turn context plus output, read from the transcript)
- **Output words:** 921
- **Transcript sha256:** `86d52aa632d806bbaa3970bd6240f1a8a902acb9603a4ddefb61d740569bb4e7` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P2c-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | The constraint holds: delete stays one call with no prompt. |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent contract

Audience: tool author (your team owns `notectl`).
Task: contract hardening for one existing command.
The constraint holds: delete stays one call with no prompt.
The explicit `delete` verb is the action trigger, so a `--yes` flag is not needed (checklist § Mutations And Long-Running Work).

## Assumptions (confirm or correct)

- Notes live behind a network API (if they are a local store, drop the `NETWORK_ERROR`/`TIMEOUT` codes and `--timeout-ms`, and set latency class to `local`).
- Delete is a hard delete with no trash or undo.
- Note IDs are opaque strings; the ID is the one primary selector.

## Invocation

```
notectl note delete [--if-exists] [--dry-run] [--idempotency-key <key>] [--timeout-ms <int>] [--machine] -- <id>
```

| Item | Contract |
| --- | --- |
| Positional | `id` (string, required, exactly 1). `--` supported so IDs beginning with `-` are data. |
| Classification | `mutating`, destructive, irreversible |
| Interactivity | Never prompts, in any mode or TTY state. This is now a declared guarantee, not an accident; a test pins it. |
| stdin | Not read. Never blocks. |
| Output class | `record` (single JSON object on stdout) |
| Latency class | `network` |
| Timeout | `--timeout-ms`, default 10000; no automatic retries by the CLI (declared `retries: 0`) |
| Side effects | Removes the note on the server; no local writes except none-or-declared cache invalidation |
| Signal semantics | SIGINT/SIGTERM after the request is sent leaves the outcome unknown; the server finishes or rejects independently of the process. |
| Concurrency | Two concurrent deletes of the same ID: one gets `deleted`, the other `NOT_FOUND` (or `already_absent` with `--if-exists`). |

### Flags

- `--if-exists` — makes delete repeat-safe: a missing note returns success with `"status": "already_absent"` instead of `NOT_FOUND`. Suppresses `NOT_FOUND`.
- `--dry-run` — resolves the note and checks permission, mutates nothing. Exits `0` if the delete would succeed, otherwise the same error contract as a real call.
- `--idempotency-key <key>` — optional; the server deduplicates attempts with the same key for a declared window (e.g. 24h). Only protects a retry if the key was supplied on the *original* attempt.
- `--timeout-ms <int>` — caller-settable network deadline.

## Success payloads (stdout, exit 0)

Real delete:

```json
{"id": "n_7f3a", "status": "deleted", "dry_run": false}
```

With `--if-exists`, note missing:

```json
{"id": "n_7f3a", "status": "already_absent", "dry_run": false}
```

Dry run (never byte-identical to the real output):

```json
{"id": "n_7f3a", "status": "would_delete", "dry_run": true, "title": "Q3 planning"}
```

`status` is a closed enum: `deleted`, `already_absent`, `would_delete`, `would_be_absent`.
Stdout is empty on failure.

## Errors (stderr, `single-error-object` framing in machine mode)

Shape: `{"code", "message", "temporary", "hint"?, "retry_after_ms"?, "reconcile_first"?, "resource_id"?, "field"?, "request_id"?}`.
`temporary` is always present.

| code | exit | retryable | reconcile_first | suppressed by |
| --- | --- | --- | --- | --- |
| `INVALID_ARGUMENT` | 2 | false | false | — |
| `NOT_FOUND` | 3 | false | false | `--if-exists` |
| `UNAUTHENTICATED` | 4 | false | false | — |
| `FORBIDDEN` | 5 | false | false | — |
| `RATE_LIMITED` | 6 | true | false | — (includes `retry_after_ms`) |
| `TIMEOUT` | 7 | true | **true** | — |
| `NETWORK_ERROR` | 9 | true | **true** | — |
| `INTERNAL` | 1 | false | false | — (fallback for anything uncaught) |

Codes absent from this catalog are treated as non-retryable.

Example:

```json
{"code": "NOT_FOUND", "message": "Note n_7f3a not found", "temporary": false, "resource_id": "n_7f3a", "hint": "Pass --if-exists to treat a missing note as success"}
```

## Retry rule (the part agents get wrong)

A `TIMEOUT` or `NETWORK_ERROR` (or a killed process) means the delete may or may not have committed.
A retry is safe only if one of these holds:

1. The retry uses `--if-exists` — the canonical agent path. A re-run returns `deleted` or `already_absent`, both success.
2. The original attempt carried `--idempotency-key` and the retry reuses it.

A plain retry without either can return `NOT_FOUND` for a delete that actually succeeded; agents must not read that as failure.
Checking `notectl note list` afterwards does not prove the delete failed if listing can lag.

**Canonical agent call:** `notectl note delete --machine --if-exists -- "$ID"`.

## Schema entry (excerpt)

```json
{
  "command": "note delete",
  "mutating": true,
  "destructive": true,
  "interactive": false,
  "stdin": {"read": false},
  "args": [{"name": "id", "type": "string", "required": true, "positional": true}],
  "flags": {
    "if-exists": {"type": "bool", "default": false},
    "dry-run": {"type": "bool", "default": false},
    "idempotency-key": {"type": "string", "required": false},
    "timeout-ms": {"type": "int", "default": 10000, "unit": "ms"}
  },
  "end_of_options": true,
  "output": {"class": "record", "format": "json", "streaming": false},
  "latency_class": "network",
  "retries": 0,
  "retry_safe_with": ["if-exists", "idempotency-key"],
  "stderr_framing": "single-error-object",
  "errors": ["INVALID_ARGUMENT", "NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "NETWORK_ERROR", "INTERNAL"]
}
```

Adding this to the schema changes the fingerprint; it is additive unless existing exit codes change (then bump major).

## Tests to ship

- No prompt: run under a TTY and non-TTY; assert it completes without reading stdin.
- Exit code ↔ symbolic code for each catalog row.
- `--if-exists` on a missing ID → exit 0, `already_absent`.
- `--dry-run` leaves the note intact and output differs from a real delete.
- Retry after simulated timeout with `--if-exists` → success.

## Open questions

- Is there server-side trash/undo? If so, return a `restore` handle in the success record.
- Should bulk delete (multiple IDs) exist? If yes it becomes a `bulk-result` command with its own aggregate exit code; keep it out of this one.
~~~~~~
