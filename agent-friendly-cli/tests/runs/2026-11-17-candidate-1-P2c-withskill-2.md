# Probe P2c — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 63,764 (final-turn context plus output, read from the transcript)
- **Output words:** 1,044
- **Transcript sha256:** `6dca44cb1583345d07e42c7a96cca2e91266660f78cb5f9ef7a6195fc6adbf98` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P2c-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | deletes, in every mode, with no prompt and no confirmation flag. |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent contract

Audience: tool owners (you own notectl). Task: contract specification for one mutating command.

## Key decision: no prompt, no `--yes`

The explicit verb `delete` *is* the action trigger (checklist § Mutations: "explicit action triggers such as `create`, `apply`, `delete`, or `--yes`").
So the contract stays one call: `notectl note delete <id>` deletes, in every mode, with no prompt and no confirmation flag.
Declare that explicitly so agents never wait for, or try to answer, a prompt:

- `interactive: false` in all modes; stdin is never read for confirmation.
- Safety comes from `--dry-run` (preview) and `--if-exists` (repeat-safe), not from a confirmation step.
- Do not add a TTY-only prompt later: that would be a breaking contract change (major `schema_version` bump), because it changes behavior agents rely on.

Assumptions (correct these if wrong): notes live in a remote store reached over the network; IDs are opaque strings like `note_123`; deletion is hard (not trash). If notectl is local-only, change `latency_class` to `local`, drop the network error codes, and make the write atomic (see signal semantics).

## Invocation

```
notectl note delete [--dry-run] [--if-exists] [--timeout-ms <int>] [--machine] [--] <id>
```

| Element | Contract |
|---|---|
| `<id>` | Required, positional, exactly one. Primary selector for notes everywhere in notectl (ID, not title). |
| `--` | Supported; anything after it is the operand, so IDs beginning with `-` are safe. |
| `--dry-run` | Validate and resolve, report the planned effect, mutate nothing. |
| `--if-exists` | Suppresses `NOTE_NOT_FOUND`: an absent note returns success with `status: "absent"`. |
| `--timeout-ms` | Integer milliseconds, default `5000`. |
| `--machine` | Machine profile: implies `--json --no-color --no-progress`; non-interactive (this command already is). |
| stdin | Not read. Never blocks. Bulk delete is out of scope for this contract (add `--from-file` later as a declared `bulk-result` alternate output). |

Classification: `mutate`. Latency class: `network`. Async: no. Pagination/streaming: no.

## Output (stdout, success only)

Output class: `record`, format JSON, small.

Deleted, exit `0`:
```json
{"id":"note_123","title":"Standup notes","status":"deleted"}
```

Already absent with `--if-exists`, exit `0`:
```json
{"id":"note_999","status":"absent"}
```

Dry run, exit `0` when the delete would succeed (otherwise the normal error contract applies):
```json
{"dry_run":true,"planned_action":"delete","id":"note_123","title":"Standup notes"}
```

`--dry-run --if-exists` on a missing note: `{"dry_run":true,"planned_action":"none","id":"note_999","status":"absent"}`, exit `0`.

No `message` field on success, no banners. Empty stdout on failure.

## Errors (stderr)

Framing: `single-error-object` — in machine mode the structured error is the only stderr content.
Required fields `code`, `message`, `temporary`; optional `hint`, `resource_id`, `field`, `retry_after_ms`, `reconcile_first`, `request_id`.

| Code | Exit | `temporary` | `reconcile_first` | Suppressed by |
|---|---|---|---|---|
| `USAGE` (missing/extra id, bad flag) | 2 | false | false | — |
| `NOTE_NOT_FOUND` | 3 | false | false | `--if-exists` |
| `UNAUTHENTICATED` | 4 | false | false | — |
| `FORBIDDEN` | 5 | false | false | — |
| `RATE_LIMITED` | 6 | true (with `retry_after_ms`) | false | — |
| `TIMEOUT` | 7 | true | **true** | — |
| `NOTE_CONFLICT` (e.g. note locked) | 8 | false | false | — |
| `NETWORK_ERROR` (transport, not timeout) | 9 | true | **true** | — |
| `INTERNAL` (fallback for anything uncaught) | 1 | false | false | — |

Codes not in this catalog are treated as non-retryable.
Agents branch on `code`; `message` is human-only.

Example, exit `3`:
```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_999","hint":"Re-run with --if-exists to treat an absent note as success.","temporary":false}
```

## Retry and unknown outcomes

- Retries: `0` by default (the CLI does not retry the delete internally).
- On `TIMEOUT`, `NETWORK_ERROR`, or interrupt, the outcome is unknown: the remote delete may have committed.
- Declared safe recovery: re-run with `--if-exists`. Delete is repeat-safe under that flag, so either result (`deleted` or `absent`) means the note is gone.
- Do not use `note list`/search to decide whether the delete committed; a lagging index cannot prove the note still exists or was not removed.
- `RATE_LIMITED` is safe to retry as-is after `retry_after_ms` (the request was rejected before executing).

## Signal semantics

- SIGINT/SIGTERM: the remote delete may still commit; reconcile with `--if-exists` as above.
- Local writes: none (or, if notectl caches notes locally, cache eviction is atomic and last-writer-wins).
- Closed stdout: the command finishes the delete and exits per the result.

## Ambient state

Declared requirements: credentials from the documented source (env var / credential file / keychain, never a flag), the config file path, and precedence flags > env > config. Same as the rest of notectl; `--isolated` must not silently change which store a delete targets.

## Schema entry (fragment)

```json
{
  "note delete": {
    "canonical_invocation_path": "notectl note delete <id>",
    "classification": "mutate",
    "interactive": false,
    "confirmation": "none; the delete verb is the explicit action trigger",
    "arguments": [{"name": "id", "type": "string", "required": true, "cardinality": 1, "position": 0}],
    "flags": {
      "--dry-run": {"type": "boolean", "default": false},
      "--if-exists": {"type": "boolean", "default": false},
      "--timeout-ms": {"type": "integer", "default": 5000, "unit": "ms"}
    },
    "end_of_options": true,
    "stdin": {"read": false, "blocks": false},
    "output": {"class": "record", "format": "json", "shape": {"id": "string", "title?": "string", "status": "deleted|absent"}, "size_mode": "small"},
    "alternate_outputs": {
      "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string", "status?": "absent"}, "streaming": false}
    },
    "stderr_framing": "single-error-object",
    "errors": {
      "USAGE": {"exit": 2},
      "NOTE_NOT_FOUND": {"exit": 3, "suppressed_by": ["--if-exists"]},
      "UNAUTHENTICATED": {"exit": 4},
      "FORBIDDEN": {"exit": 5},
      "RATE_LIMITED": {"exit": 6, "retryable": true},
      "TIMEOUT": {"exit": 7, "retryable": true, "reconcile_first": true},
      "NOTE_CONFLICT": {"exit": 8},
      "NETWORK_ERROR": {"exit": 9, "retryable": true, "reconcile_first": true},
      "INTERNAL": {"exit": 1}
    },
    "unknown_code_policy": "non-retryable",
    "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation"},
    "latency_class": "network",
    "timeout_defaults_ms": 5000,
    "retry_defaults": {"retries": 0},
    "reconciliation": "on timeout, transport error, or interrupt the outcome is unknown; re-run with --if-exists",
    "signal_semantics": {"interrupt": "remote delete may still commit", "local_writes": "none", "remote_continues": true},
    "async": false
  }
}
```

The `shape` notation here is the tool-level declared dialect (`?` = optional); declare it once at schema top level alongside `schema_version` and the fingerprint.

## Tests to ship

- Success, `--if-exists` absent, and dry-run payload snapshots; dry-run output never byte-identical to real output.
- Each catalog code produces its declared exit code.
- Non-TTY and TTY runs with stdin attached never prompt (regression guard for "one call").
- Dry run performs no mutation.
- Interrupt mid-delete, then `--if-exists` re-run reconciles.
~~~~~~
