# Probe P2c — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 67,498 (final-turn context plus output, read from the transcript)
- **Output words:** 1,011
- **Transcript sha256:** `5679b2c29d26655b70cf3b985dfb811f7e9449c73857c0c6a50f79268716600e` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2c-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | Do **not** add a `--yes`/`--force` requirement |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: tool author (your team owns `notectl`).
Task: contract hardening of an existing command, so this specifies the schema entry and behavior; it does not redesign the CLI.

## Decision: keep one call, no prompt, no `--yes`

The explicit verb `delete` is the action trigger.
The command never prompts, in any mode, so it cannot hang in CI or when stdin is a pipe.
Do **not** add a `--yes`/`--force` requirement: that would break every existing caller and turn deletes into two concepts.
Safety comes instead from three opt-in controls that keep it a single call:

- `--dry-run` — preview the effect with zero mutation.
- `--if-exists` — make a retry after an unknown outcome safe (idempotent delete).
- A declared reconciliation path for timeouts and interrupts.

If deletes are destructive and unrecoverable, say so in the schema (`recoverable: false`); if notes go to a trash, declare that and the restore command instead.
I assume hard delete below; swap if wrong.

## Invocation

```sh
notectl note delete --machine -- "<id>"
notectl note delete --machine --dry-run -- "<id>"
notectl note delete --machine --if-exists -- "<id>"
```

- `<id>` is the single positional primary selector (note ID, not title); title-based lookup belongs in `notectl note find`, not in delete.
- `--` end-of-options is supported, so an ID starting with `-` is never parsed as a flag; all options precede `--`.
- The ID is treated as data — never passed to a shell or `eval`.
- `--machine` is the tool's canonical machine profile (implies JSON output, no color/progress/pager/prompts).

## Schema entry

Shape dialect: `notectl-compact-v1` (`a|b` closed enum, trailing `?` optional, all else required).

```json
{
  "canonical_invocation_path": "notectl note delete <id>",
  "aliases": [],
  "deprecations": [],
  "description": "Permanently delete one note by ID. Never prompts. Fails with NOTE_NOT_FOUND (exit 3) unless --if-exists. Use --dry-run to preview. On TIMEOUT or interrupt, reconcile with `notectl note get <id>` before retrying.",
  "classification": "mutate",
  "read_only": false,
  "interactive": false,
  "recoverable": false,
  "end_of_options_supported": true,
  "arguments": [
    {"name": "id", "type": "string", "cardinality": "one", "required": true, "examples": ["note_8f3a2c"]}
  ],
  "flags": [
    {"name": "--dry-run", "type": "boolean", "default": false, "description": "Validate and report the planned deletion; no mutation."},
    {"name": "--if-exists", "type": "boolean", "default": false, "description": "Treat an already-absent note as success (exit 0, \"deleted\": false)."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
  ],
  "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
  "output": {
    "class": "record",
    "format": "json",
    "streaming": false,
    "size_mode": "small",
    "shape": {"id": "string", "deleted": "boolean", "deleted_at?": "string (RFC 3339, UTC)"}
  },
  "alternate_outputs": {
    "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small",
      "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "exists": "boolean"}},
    "--dry-run --if-exists": {"precedence": "--dry-run governs output; --if-exists turns a missing note into planned_action \"none\" with exit 0 instead of NOTE_NOT_FOUND"}
  },
  "side_effects": {"external_mutation": true, "writes": ["note store"], "dry_run": "no externally visible mutation; output carries \"dry_run\": true"},
  "latency_class": "network",
  "timeout_defaults_ms": 5000,
  "retry_defaults": {"retries": 0},
  "reconciliation": "On TIMEOUT or interrupt the outcome is unknown. Run `notectl note get <id>`: NOTE_NOT_FOUND means the delete committed. Retrying with --if-exists is always safe.",
  "signal_semantics": "SIGINT/SIGTERM before the request is sent: nothing deleted, exit 130/143. After it is sent: the server may still commit; outcome unknown, reconcile as above. No local state is written.",
  "async": false, "pagination": false, "truncation": false, "artifact": false,
  "errors_possible": [
    {"code": "VALIDATION_ERROR", "exit": 2},
    {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
    {"code": "UNAUTHENTICATED", "exit": 4},
    {"code": "FORBIDDEN", "exit": 5},
    {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
    {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
    {"code": "CONFLICT", "exit": 8},
    {"code": "TRANSIENT", "exit": 9, "retryable": true}
  ]
}
```

Note on `TRANSIENT` retryability: mark it `retryable: true` only if the server guarantees it was raised before any commit; otherwise set `reconcile_first: true` like `TIMEOUT`.
`CONFLICT` covers e.g. a locked or concurrently edited note; drop it if notectl has no such state.

## Payloads

Success (exit 0, stdout):

```json
{"id": "note_8f3a2c", "deleted": true, "deleted_at": "2026-11-17T18:04:11Z"}
```

`--if-exists` on an absent note (exit 0) — distinguishable from a real deletion, so the agent knows whether it did anything:

```json
{"id": "note_8f3a2c", "deleted": false}
```

`--dry-run` (exit 0 if the delete would succeed; otherwise the normal error contract, e.g. NOTE_NOT_FOUND exit 3):

```json
{"dry_run": true, "planned_action": "delete", "id": "note_8f3a2c", "exists": true}
```

Error (stderr only, stdout empty, stderr framing `single-error-object`):

```json
{"code": "NOTE_NOT_FOUND", "message": "Note not found.", "resource_id": "note_8f3a2c", "hint": "Pass --if-exists to treat a missing note as success.", "temporary": false}
```

```json
{"code": "TIMEOUT", "message": "Delete request timed out; outcome unknown.", "resource_id": "note_8f3a2c", "hint": "Check with note get before retrying, or retry with --if-exists.", "temporary": false}
```

`temporary` is present on every error; agents branch on `code`, never `message`.

## Agent retry rule (for docs / skill text)

1. Exit 0 → done.
2. `RATE_LIMITED` → wait `retry_after_ms`, retry.
3. `TIMEOUT` or interrupted → retry with `--if-exists` (safe), or `note get` first.
4. `NOTE_NOT_FOUND` without `--if-exists` → stop; the ID is wrong or already gone.
5. Anything else with `temporary: false` → stop and report.

## Out of scope (not applicable here)

- Bulk delete (`--from-file`, `bulk-result`, `--allow-partial`): not requested; if added later, declare the alternate class and `PARTIAL_FAILURE` per the checklist.
- Long-running job/poll/cancel: delete is a single synchronous request.
- Pagination, truncation, artifact output, `--output`: single small record.
- Stdin: not read.
- Ambient state (credential source, config, `--isolated`, resolved-config inspection) is tool-level, not per-command; delete inherits whatever notectl's global contract declares.

## Contract tests to ship

- Schema snapshot for this entry; fingerprint changes when it changes (adding `--if-exists`/`--dry-run` is additive: minor bump).
- Success, `--if-exists`-absent, and dry-run payloads; dry-run output is never byte-identical to real output and performs no mutation.
- Each `errors_possible` code produces its declared exit code and a stderr-only error object with empty stdout.
- Never prompts: run with a TTY stdin and with closed stdin; both complete without waiting.
- `--` handling: an ID like `-x` is treated as an operand.
- Interrupt test: SIGINT mid-request yields the documented exit and leaves no local state.
- Retry with `--if-exists` after a successful delete exits 0 with `"deleted": false`.
~~~~~~
