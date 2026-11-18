# Probe P2c — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 72,171 (final-turn context plus output, read from the transcript)
- **Output words:** 1,200
- **Transcript sha256:** `5c4780119fe925948187ae19f6cd452b8321709495e20b297a0c2d514bbbabc6` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P2c-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | so no `--yes` or confirmation step is added. |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent contract

Audience: tool owner (the team).
Task: contract hardening, and you asked for a contract, so this is a schema entry plus payloads.
Delete stays one call and never prompts: the explicit verb `delete` is the action trigger (checklist § Mutations And Long-Running Work), so no `--yes` or confirmation step is added.
Safety comes from `--dry-run`, `--if-exists`, a declared error catalog, and a declared retry and reconciliation rule.

## Assumptions (please confirm)

1. Notes live in a remote store reached over the network. If they are local files, change `latency_class` to `local`, drop `RATE_LIMITED`/`TRANSIENT`/`NETWORK_ERROR`, and replace the reconciliation rule with "atomic local delete; retry is safe".
2. Delete is a hard delete. If there is a trash or soft delete, add `"status": "trashed"` and a `restore` command, and say so in `side_effects`.
3. `notectl` already has (or will get) the tool-level pieces this entry relies on: `--machine`, `--json`, `notectl schema`, `notectl schema note delete`, `schema --fingerprint`, `stderr_framing`, the exit-code map, and `INTERNAL` as fallback code.
   If not, those are the first gaps to close; they are not delete-specific.
4. Note IDs look like `note_…`; one ID per call. Bulk delete is out of scope (add `--from-file` with a `bulk-result` alternate output later, per examples.md, if needed).

## Behavior rules

- **One call, no prompt, ever.** No TTY check gates the delete; human mode and machine mode delete identically. stdin is never read, so the command cannot block.
- **Default is strict.** Deleting a missing note fails with `NOTE_NOT_FOUND` (exit 3). This keeps typos visible.
- **`--if-exists` makes it repeat-safe.** A missing note returns success with `"status": "absent"`, exit 0. This is the flag agents should use for retries and cleanup.
- **`--dry-run` validates without mutating.** It resolves the note, checks auth and permissions, exits 0 if the delete would succeed, and otherwise returns the same error the real delete would. Output carries `"dry_run": true`.
- **Retries.** The CLI performs no automatic retries (`retries: 0`). On `TIMEOUT`, `TRANSIENT`, `NETWORK_ERROR`, or an interrupt, the outcome is unknown; the declared recovery is to re-run with `--if-exists`. Don't treat `note list`/`search` as proof the delete did not happen (it may lag); `note get` must read the primary store if you document it as a check.
- **`RATE_LIMITED`** is rejected before any mutation, so it is retryable after `retry_after_ms`.
- **`--` is supported**, so an ID beginning with `-` cannot be parsed as a flag. The ID is never passed to a shell.

## Schema entry

Shape dialect follows the tool-level declaration (example uses a compact notation: `a|b` closed enum, trailing `?` optional).

```json
{
  "canonical_invocation_path": "notectl note delete <id>",
  "aliases": [],
  "deprecations": [],
  "classification": "mutate",
  "read_only": false,
  "summary": "Permanently delete one note by ID. Never prompts. Fails with NOTE_NOT_FOUND unless --if-exists. Use --dry-run to validate first.",
  "arguments": [
    {"name": "id", "type": "string", "cardinality": "one", "required": true, "examples": ["note_8f3a2c"]}
  ],
  "flags": [
    {"name": "--dry-run", "type": "boolean", "default": false, "description": "validate and report the planned delete without mutating"},
    {"name": "--if-exists", "type": "boolean", "default": false, "description": "succeed with status absent if the note does not exist; makes the call repeat-safe"},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
  ],
  "end_of_options_supported": true,
  "interactive": false,
  "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
  "auth": "required; same credential sources as the rest of notectl",
  "output": {
    "class": "record",
    "format": "json",
    "shape": {"id": "string", "status": "deleted|absent", "title?": "string"},
    "shape_description": "title is present only when status is deleted",
    "size_mode": "small"
  },
  "alternate_outputs": {
    "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action is none only with --if-exists when the note is absent", "size_mode": "small"}
  },
  "flag_combinations": {"--dry-run --if-exists": "dry-run shape; a missing note yields planned_action none and exit 0"},
  "side_effects": {
    "external_mutation": true,
    "writes": ["remote note store"],
    "description": "permanently deletes the note unless --dry-run; no other writes, no telemetry",
    "dry_run": "no externally visible mutations; output includes dry_run: true"
  },
  "latency_class": "network",
  "timeout_defaults_ms": 5000,
  "retry_defaults": {"retries": 0},
  "retry_safety": "re-running with --if-exists is repeat-safe and is the declared recovery after TIMEOUT, TRANSIENT, NETWORK_ERROR, or interrupt",
  "reconciliation": "outcome after timeout or interrupt is unknown; re-run with --if-exists. status absent means the note is gone now, not which attempt removed it",
  "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true},
  "closed_stdout": "finishes the delete; output is lost, re-run with --if-exists to confirm",
  "async": false,
  "streaming": false,
  "pagination": false,
  "truncation": false,
  "artifact": false,
  "errors_possible": [
    {"code": "INTERNAL", "exit": 1},
    {"code": "VALIDATION_ERROR", "exit": 2},
    {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
    {"code": "UNAUTHENTICATED", "exit": 4},
    {"code": "FORBIDDEN", "exit": 5},
    {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
    {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
    {"code": "CONFLICT", "exit": 8, "description": "note is locked or being modified"},
    {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
    {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
  ]
}
```

`TIMEOUT`, `TRANSIENT`, and `NETWORK_ERROR` are `retryable: false, reconcile_first: true` because the delete may have committed; the reconciliation *is* a repeat-safe retry with `--if-exists`, so an agent can always recover in one more call.
Drop `CONFLICT` if notes cannot be locked.

## Payloads (`--machine`)

Success, exit 0:

```json
{"id": "note_8f3a2c", "status": "deleted", "title": "Q3 planning"}
```

Already gone with `--if-exists`, exit 0:

```json
{"id": "note_8f3a2c", "status": "absent"}
```

Dry run, exit 0:

```json
{"dry_run": true, "planned_action": "delete", "id": "note_8f3a2c", "title": "Q3 planning"}
```

Not found (no `--if-exists`), exit 3, stderr only, empty stdout:

```json
{"code": "NOTE_NOT_FOUND", "message": "Note not found.", "resource_id": "note_8f3a2c", "hint": "Pass --if-exists to treat a missing note as success.", "temporary": false}
```

Timeout, exit 7:

```json
{"code": "TIMEOUT", "message": "Delete did not complete within 5000 ms; outcome unknown.", "resource_id": "note_8f3a2c", "temporary": false, "reconcile_first": true, "hint": "Re-run with --if-exists."}
```

## Canonical agent invocation

```sh
notectl note delete --machine --if-exists -- "note_8f3a2c"
```

Branch on the stderr `code`, never on `message`; exit code is the shell fallback.

## Tests to ship for this command

- schema snapshot for the entry above
- success, absent, and dry-run payloads (dry-run never byte-identical to real output)
- each catalog code produces its declared exit code
- no prompt with stdin closed and with stdin a TTY; nothing read from stdin
- dry run performs no mutation
- `--if-exists` on a missing note exits 0
- an ID starting with `-` after `--`
- interrupt mid-request followed by `--if-exists` re-run converges

## Checklist coverage (for this command)

- Command Model: `note delete <id>`, noun-verb, one positional selector.
- Machine Schema: entry above; tool-level items assumed (assumption 3).
- Stdin Contract: declared, never read.
- Shell Safety: `--` supported; ID never shelled; hints carry no shell strings built from input.
- Agent-Safe Invocation: never interactive; `--timeout-ms` settable; metadata paths are tool-level.
- Output: `record` plus declared dry-run alternate and combination rule; closed-stdout behavior declared.
- Errors And Exit Codes: per-command catalog with retryable/reconcile_first; transport code `NETWORK_ERROR`; fallback `INTERNAL`.
- Ambient State: N/A at command level — inherits notectl's credential/config contract.
- Mutations And Long-Running Work: explicit verb, dry run, `--if-exists`, reconciliation, signal semantics; not async.
- Side Effects And Telemetry: one declared remote write, nothing else.
- Prose Surfaces: summary leads with the binding rules (permanent, never prompts, strict by default).
- Tests: listed above.
~~~~~~
