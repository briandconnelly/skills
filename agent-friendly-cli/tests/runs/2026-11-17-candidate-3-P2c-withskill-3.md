# Probe P2c — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 64,369 (final-turn context plus output, read from the transcript)
- **Output words:** 1,003
- **Transcript sha256:** `6dacfb0561aba5e16d090a0de64051a4da1a8748491894f19b6957ef701825d3` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P2c-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | ## Decision: keep delete one call, no prompt, no `--yes` |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: the tool's owning team (contract hardening for a CLI you own).
Assumptions, to confirm: notes live in a remote store reached over the network; `notectl` already has (or will adopt) a `--machine` profile and a `notectl schema` command.
If notes are local files, change `latency_class` to `local` and drop the network/transport items.

## Decision: keep delete one call, no prompt, no `--yes`

The verb `delete` is itself the explicit action trigger the checklist requires, so a confirmation flag or prompt is not needed.
Keeping it promptless is also correct for agents: a prompt would hang in CI.
What replaces the prompt as the safety net is `--dry-run` (preview), `--if-exists` (repeat-safe retry), and a declared reconciliation rule for unknown outcomes.
Declare "never prompts, in any mode or TTY state" in the schema so a future change that adds a prompt is a breaking change, caught by a test.

## Invocation

```
notectl note delete [--if-exists] [--dry-run] [--timeout-ms <int>] [--machine] [--] <id>
```

- `<id>`: one positional, the primary selector for notes (ID, not title). Use `notectl note find` to resolve titles to IDs first.
- `--` end-of-options supported, so an ID starting with `-` is safe; IDs are never passed to a shell.
- No stdin read (declared `stdin: {reads: false}`); never blocks on stdin.
- Single-item only. If bulk delete is needed later, add `--from-file` with a declared `bulk-result` alternate output; out of scope here.

## Schema entry

```json
{
  "note delete": {
    "canonical_invocation_path": "notectl note delete <id>",
    "aliases": [],
    "deprecations": [],
    "classification": "mutate",
    "read_only": false,
    "interactive": false,
    "description": "Permanently delete one note by ID. Never prompts. Fails with NOTE_NOT_FOUND unless --if-exists. Use --dry-run to preview.",
    "arguments": [
      {"name": "id", "type": "string", "cardinality": "one", "required": true, "examples": ["note_123"]}
    ],
    "end_of_options": true,
    "flags": [
      {"name": "--if-exists", "type": "boolean", "default": false, "description": "Treat an already-absent note as success (status: absent)."},
      {"name": "--dry-run", "type": "boolean", "default": false, "description": "Validate and report the planned delete without deleting."},
      {"name": "--timeout-ms", "type": "integer", "default": 5000, "unit": "ms"}
    ],
    "stdin": {"reads": false},
    "auth": "required; same credential sources as all notectl commands",
    "output": {
      "class": "record", "format": "json", "streaming": false, "size_mode": "small",
      "shape": {"id": "string", "title?": "string", "status": "deleted|absent"},
      "shape_description": "title is omitted and status is absent when --if-exists suppressed NOTE_NOT_FOUND"
    },
    "alternate_outputs": {
      "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small",
        "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"},
        "shape_description": "planned_action is none when --if-exists and the note is already absent"}
    },
    "side_effects": {"external_mutation": true, "writes": ["remote note store"],
      "dry_run": "no externally visible mutation; may refresh auth token (suppressed under --isolated)"},
    "latency_class": "network",
    "timeout_defaults_ms": 5000,
    "retry_defaults": {"retries": 0},
    "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists. A NOTE_NOT_FOUND from notectl note get shows the note is absent now, not which attempt removed it.",
    "signal_semantics": {"interrupt": "the remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
    "async": false, "pagination": false, "truncation": false, "artifact": false,
    "errors_possible": [
      {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
      {"code": "VALIDATION_ERROR", "exit": 2},
      {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": ["--if-exists"]},
      {"code": "UNAUTHENTICATED", "exit": 4},
      {"code": "FORBIDDEN", "exit": 5},
      {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
      {"code": "TIMEOUT", "exit": 7, "retryable": true, "reconcile_first": true},
      {"code": "CONFLICT", "exit": 8, "description": "note is locked or has a retention hold"},
      {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true, "reconcile_first": true}
    ]
  }
}
```

Tool-level items this relies on (declare once, not per command): numeric exit-code map, `fallback_error_code: INTERNAL`, `unknown_code_policy: "act on payload fields; reconcile first on mutations"`, error shape `{code, message, temporary, hint?, retry_after_ms?, reconcile_first?, details?, resource_id?, request_id?}`, shape dialect, machine-mode stderr framing `single-error-object`, schema version and fingerprint.

## Payloads (machine mode)

Success, exit 0, stdout:
```json
{"id":"note_123","title":"Standup notes","status":"deleted"}
```

Already absent with `--if-exists`, exit 0:
```json
{"id":"note_999","status":"absent"}
```

Dry run, exit 0 (never byte-identical to a real delete):
```json
{"dry_run":true,"planned_action":"delete","id":"note_123"}
```

Not found, exit 3, empty stdout, stderr:
```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_999","temporary":false,"hint":"Add --if-exists to treat an absent note as success."}
```

Timeout, exit 7, stderr:
```json
{"code":"TIMEOUT","message":"Delete did not complete within 5000 ms; outcome unknown.","temporary":true,"reconcile_first":true,"resource_id":"note_123","details":{"timeout_ms":5000}}
```

## Agent retry rule (put this in the description and docs)

- `deleted` or `absent` on exit 0: done.
- `temporary: true` with `reconcile_first: true` (TIMEOUT, TRANSPORT_ERROR): re-run the same command with `--if-exists`; that converges whether or not the first attempt committed.
- `RATE_LIMITED`: wait `retry_after_ms`, then retry.
- Anything else with `temporary: false`: do not retry; branch on `code`.
- Recommended canonical agent call: `notectl note delete --if-exists --machine -- note_123`.

## Checklist coverage

- Command model: `note delete <id>`, one selector (ID), noun-verb. ✔
- Machine schema: entry above. ✔
- Stdin: not read. ✔
- Shell safety: `--` supported; IDs never shelled; hint has no shell strings. ✔
- Agent-safe invocation: never prompts in any mode; caller-settable `--timeout-ms`. ✔
- Output: `record`, stdout success only, errors on stderr. ✔
- Errors: per-command catalog with retryable/reconcile_first/suppression. ✔
- Ambient state: inherits notectl's tool-level declaration; nothing delete-specific. N/A here.
- Mutations: explicit verb trigger, `--dry-run`, `--if-exists`, unknown-outcome rule, signal semantics. ✔ (Concurrency on local state: N/A, no local writes.)
- Side effects/telemetry: only the declared remote delete. ✔
- Prose surfaces: description is rules-first (never prompts, error behavior, dry-run). ✔

## Tests to ship

- Never prompts: run with a TTY stdin and with no stdin; assert no read and no hang.
- Exit-code map: 0 deleted, 0 absent with `--if-exists`, 3 without it, 7 on forced timeout.
- `--dry-run` leaves the note present and output carries `dry_run: true`.
- Machine mode: empty stdout on failure, single error object on stderr.
- `--` handling with an ID beginning with `-`.
- Interrupt mid-request: documented outcome holds; re-run with `--if-exists` converges.
- Schema snapshot for the `note delete` entry.

## Open question for the team

Is delete permanent, or soft (trash/restore)?
If soft, add `status: "trashed"` and a `note restore` command, and say so in the description; agents treat a recoverable delete very differently from a permanent one.
~~~~~~
