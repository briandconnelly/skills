# Probe P2c — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 64,789 (final-turn context plus output, read from the transcript)
- **Output words:** 838
- **Transcript sha256:** `27e14d9ec8eb0df5fbd180d9d6c0fc236c90028f6ad4c84d41c88d60772a7f61` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P2c-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | Decision: keep delete one call, no prompt, no `--yes` |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: tool author (the team owns `notectl`).
Task: contract hardening of an existing command, so this is a design deliverable.

## Decision: keep delete one call, no prompt, no `--yes`

- The `delete` verb is the explicit action trigger the checklist requires (§ Mutations: "`create`, `apply`, `delete`, or `--yes`").
  A second confirmation flag is not needed and would break every existing caller.
- `note delete` never prompts, in any mode, TTY or not.
  This must be a declared, tested guarantee, not an accident: a future "Are you sure?" prompt would hang agents in CI.
- Safety comes from `--dry-run`, `--if-exists`, a typed error catalog, and a declared reconciliation path instead of interactive confirmation.

Assumption (state to the team; changes the reconciliation and latency fields if wrong): notes live in a remote store reached over the network, and delete is a hard delete.
If notes are local files, set `latency_class: local`, drop `TIMEOUT`/`RATE_LIMITED`, and make the write atomic (rename-based).

## Schema entry

```json
{
  "canonical_invocation_path": "notectl note delete [--dry-run] [--if-exists] [--timeout-ms <int>] [--] <id>",
  "aliases": [],
  "deprecations": [],
  "classification": "mutate",
  "read_only": false,
  "description": "Permanently delete one note by ID. Never prompts. Not reversible. Use --dry-run to check first; use --if-exists to make retries safe.",
  "interactive": false,
  "arguments": [
    {"name": "id", "type": "string", "cardinality": "one", "required": true, "examples": ["note_8f3a2c"], "description": "Note ID as returned by `notectl note list` or `notectl note get`."}
  ],
  "flags": [
    {"name": "--dry-run", "type": "boolean", "default": false},
    {"name": "--if-exists", "type": "boolean", "default": false, "description": "Treat an already-absent note as success (status \"absent\") instead of NOTE_NOT_FOUND."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
  ],
  "end_of_options": true,
  "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
  "output": {
    "class": "record", "format": "json", "streaming": false, "size_mode": "small",
    "shape_dialect": "JSON Schema (2020-12); all listed fields required",
    "shape": {"id": "string", "status": "deleted|absent"}
  },
  "alternate_outputs": {
    "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "exists": "boolean"}}
  },
  "flag_combination_rules": "--dry-run --if-exists: absent note yields exit 0 with planned_action \"none\"; without --if-exists an absent note yields NOTE_NOT_FOUND.",
  "side_effects": {"external_mutation": true, "writes": ["note store"], "description": "Hard-deletes the note unless --dry-run.", "dry_run": "no externally visible mutation; may refresh the auth token (suppressed under --isolated)"},
  "latency_class": "network",
  "timeout_defaults_ms": 5000,
  "retry_defaults": {"retries": 0},
  "reconciliation": "On TIMEOUT or interrupt the outcome is unknown. Either re-run with --if-exists (safe: absent => status \"absent\", exit 0), or run `notectl note get <id>`: NOTE_NOT_FOUND means the delete committed.",
  "signal_semantics": "SIGINT/SIGTERM after the request is sent: server-side delete may still commit; no local state is written.",
  "async": false, "pagination": false, "truncation": false, "artifact": false,
  "errors_possible": [
    {"code": "VALIDATION_ERROR", "exit": 2},
    {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
    {"code": "UNAUTHENTICATED", "exit": 4},
    {"code": "FORBIDDEN", "exit": 5},
    {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
    {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
    {"code": "NOTE_LOCKED", "exit": 8}
  ]
}
```

Drop `NOTE_LOCKED` if notes have no lock/conflict concept.

## Payloads

Success, exit 0 (stdout):

```json
{"id":"note_8f3a2c","status":"deleted"}
```

`--if-exists` on an absent note, exit 0:

```json
{"id":"note_8f3a2c","status":"absent"}
```

`--dry-run`, exit 0 — never byte-identical to the real result:

```json
{"dry_run":true,"planned_action":"delete","id":"note_8f3a2c","exists":true}
```

Not found, exit 3, stdout empty, stderr is the single error object:

```json
{"code":"NOTE_NOT_FOUND","message":"Note note_8f3a2c not found.","temporary":false,"field":"id","resource_id":"note_8f3a2c","hint":"Pass --if-exists to treat an absent note as success."}
```

Rate limited, exit 6:

```json
{"code":"RATE_LIMITED","message":"Rate limited.","temporary":true,"retry_after_ms":2000}
```

## Agent calling pattern

1. Optional preflight: `notectl note delete --dry-run --machine -- note_8f3a2c`.
2. Delete: `notectl note delete --if-exists --machine -- note_8f3a2c` (one call, idempotent).
3. Branch on stderr `code`, not on `message`; on `TIMEOUT`, re-run step 2 — `--if-exists` makes that the reconciliation.

## Checklist walk

| Section | Answer |
|---|---|
| Command Model | `note delete <id>`; ID is the one positional selector; verbs match `list`/`get`. |
| Machine Schema | Entry above; tool-level schema version + fingerprint must change with this addition (additive: new optional flags). |
| Stdin Contract | Not read; declared. |
| Shell Safety | `--` supported and declared; ID never passed to a shell; hint carries no shell string built from input. |
| Agent-Safe Invocation | `interactive: false` in every mode; `--machine` profile applies; `--timeout-ms` caller-settable. |
| Output | `record` JSON on stdout; dry-run alternate declared; combination rule declared; stderr framing `single-error-object` (tool-level). |
| Errors And Exit Codes | Per-command catalog above; `temporary` on every error. |
| Ambient State | Inherits tool-level credential/config declarations; no delete-specific state. |
| Mutations | Verb is the trigger; `--dry-run`; `--if-exists`; reconciliation and signal semantics declared; no local writes. |
| Side Effects | Declared; no telemetry. |
| Prose Surfaces | Description is rules-first (never prompts, irreversible) then guidance. |
| Long-running work | N/A: single synchronous request. |
| Bulk / partial failure | N/A: one ID per call; add `--from-file` with `bulk-result` later if needed. |
| Tests | No-prompt test under TTY and non-TTY stdin (assert exits without reading stdin); success, dry-run, not-found, `--if-exists` payload snapshots; exit-code mapping; dry-run performs no mutation; interrupt mid-request; schema snapshot. |
~~~~~~
