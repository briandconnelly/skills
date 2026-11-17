# Probe P2c — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 60,875 (final-turn context plus output, read from the transcript)
- **Output words:** 853
- **Transcript sha256:** `8073f157d9e2eabd012eeb8b8db759444480469049119d7b948d48cdb03f1066` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2c-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | do **not** add a prompt or a mandatory `--yes` |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: tool author (your team owns notectl).
Task: contract hardening of an existing mutating command.

## Decision: one call stays one call

The checklist requires mutations to have an *explicit action trigger*, and lists `delete` itself as one (§ Mutations And Long-Running Work).
So `notectl note delete <id>` already satisfies the trigger rule; do **not** add a prompt or a mandatory `--yes`.
Adding a required `--yes` now would be a breaking change (existing call sites start failing), so it would need a major `schema_version` bump — not worth it.

What delete *does* need is everything that makes a one-shot destructive call safe to retry, preview, and branch on.

Assumption (state it in the schema; confirm): notes live in a remote service, so delete is `network` latency.
If notes are local files, change `latency_class` to `local`, drop `--timeout-ms`, and the unknown-outcome section reduces to atomic-write semantics.

## Schema entry

```json
{
  "command": "note delete",
  "canonical": "notectl note delete --machine -- \"<id>\"",
  "description": "Permanently delete one note by ID. Never prompts. Mutating; not reversible. Use --dry-run to preview, --if-exists to make repeat calls succeed.",
  "classification": "mutating",
  "arguments": [
    {"name": "id", "type": "string", "required": true, "cardinality": "1", "selector": "id",
     "description": "Note ID as returned by `note list`/`note find`. Names are not accepted."}
  ],
  "flags": [
    {"name": "--dry-run", "type": "bool", "default": false},
    {"name": "--if-exists", "type": "bool", "default": false,
     "description": "Treat an already-absent note as success (deleted: false)."},
    {"name": "--if-revision", "type": "string", "required": false,
     "description": "Delete only if the note's current revision matches; otherwise fail with NOTE_REVISION_MISMATCH."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
  ],
  "end_of_options": true,
  "stdin": {"read": false, "blocks": false},
  "interactive": false,
  "output_class": "record",
  "format": "json",
  "streaming": false,
  "latency_class": "network",
  "retry": {"automatic_retries": 0, "safe_to_retry": "with --if-exists",
            "description": "Retry after a timeout or interrupt only with --if-exists, or after `note get` confirms state."},
  "side_effects": ["removes the note and its content from the store"],
  "signals": {
    "SIGINT/SIGTERM": "outcome unknown if the request was sent; the server may still commit the delete. Reconcile with `note get <id>` or re-run with --if-exists."
  },
  "errors": [
    {"code": "NOTE_NOT_FOUND",         "exit": 3, "retryable": false, "suppressed_by": ["--if-exists"]},
    {"code": "NOTE_REVISION_MISMATCH", "exit": 8, "retryable": false, "reconcile_first": true},
    {"code": "INVALID_ARGUMENT",       "exit": 2, "retryable": false},
    {"code": "UNAUTHENTICATED",        "exit": 4, "retryable": false},
    {"code": "FORBIDDEN",              "exit": 5, "retryable": false},
    {"code": "RATE_LIMITED",           "exit": 6, "retryable": true},
    {"code": "TIMEOUT",                "exit": 7, "retryable": true, "reconcile_first": true},
    {"code": "TRANSIENT",              "exit": 9, "retryable": true, "reconcile_first": true}
  ]
}
```

Omitted `retryable`/`reconcile_first` mean `false`.
Exit codes follow the tool-level map; declare it once at tool level, not per command.

## Payloads

Success (stdout, exit 0):

```json
{"id": "n_8f2c", "deleted": true, "revision": "r41"}
```

Already absent with `--if-exists` (exit 0):

```json
{"id": "n_8f2c", "deleted": false, "reason": "not_found"}
```

`deleted` is the branch key: an agent can tell "I deleted it" from "it was already gone" without parsing anything.

Dry run (exit 0 if the delete would succeed; otherwise the same error contract as a real run):

```json
{"dry_run": true, "id": "n_8f2c", "would_delete": true, "revision": "r41", "title": "Q3 planning"}
```

Dry run must make no externally visible change and is never byte-identical to real output.
Returning `revision` lets the agent follow up with `--if-revision r41` so it deletes exactly what it previewed.

Failure (stderr, single-error-object framing, empty stdout, exit 3):

```json
{"code": "NOTE_NOT_FOUND", "message": "No note with id n_8f2c.", "temporary": false,
 "field": "id", "resource_id": "n_8f2c", "hint": "Pass --if-exists to treat a missing note as success."}
```

`temporary` is present on every error, `false` included.
The `hint` names a flag, never a shell string built from the caller's ID.

## Unknown outcome and retry

A timed-out or interrupted delete may have committed.
The declared reconciliation path is: retry with `--if-exists` (idempotent — returns `deleted: false` if the first attempt landed), or check with `notectl note get <id>`.
Plain retry without `--if-exists` is not safe: it can turn a successful delete into a spurious `NOTE_NOT_FOUND`.
notectl does not retry deletes internally.

## Agent-safe invocation

- Never prompts, in any mode — this is now a declared guarantee, so a future "are you sure?" is a breaking change.
- `--machine`: JSON only, no color/progress/pager; stdout empty on failure.
- `--` supported so IDs beginning with `-` are data; the ID is never passed to a shell.
- No telemetry or update check on this path.

## Not applicable

- Stdin: not read (single positional ID).
- Bulk delete / partial failure: out of scope; if a multi-ID form is added later, it switches to `bulk-result` and must declare aggregate exit semantics.
- Long-running jobs: delete is synchronous.
- Pagination, truncation, artifacts, `--output`: single small record.
- Ambient state: inherits the tool-level credential/config contract; nothing delete-specific.

## Tests to ship

- Schema snapshot of this entry.
- Success, `--if-exists` absent, and dry-run payloads; dry run leaves the note intact.
- Each declared error code maps to its declared exit code at runtime.
- No prompt with stdin as non-TTY *and* as a TTY (guarantees "never prompts").
- `--` with an ID starting with `-`.
- `--if-revision` mismatch returns exit 8 and does not delete.
- Interrupt mid-request: subsequent `--if-exists` retry succeeds either way.
~~~~~~
