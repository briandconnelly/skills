# Scenario 1 (design) — baseline arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/11 scored; 1/2 conformance
- **Tokens:** 51,162 (final-turn context plus output, read from the transcript)
- **Output words:** 904
- **Transcript sha256:** `d3c77e74f5f32a3864730dcf3cb1d7e11431aeef341efffa183aa1c847b46caf` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

## Arm instructions

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **FAIL** | No canonical machine profile in schema Parts: profile declared in schema = fail; named flags declared = fail |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **FAIL** | Exit code table and error code enum, but no per-command error catalog Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = fail |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **FAIL** | "stdout carries only the result envelope" — error envelopes not routed to stderr; no framing declared Parts: stdout success only = fail; stderr structured failures with framing = fail |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "destructive actions require `--yes`"; envelope "dry_run": { "type": "boolean" }; notectl delete ID --yes [--dry-run] Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "page": { "returned": 2, "truncated": true, "next_cursor": "eyJvZmZzZXQiOjJ9" } |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **FAIL** | export data {"path", "format", "count", "bytes"} — no integrity hash |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **FAIL** | "--timeout SECONDS (default 30)" — no unit in name or unit field |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **FAIL** | "Auth via NOTECTL_TOKEN" only; no inspection or isolation Parts: declared = fail; inspection = fail; isolation = fail |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | No example uses --; vacuously satisfied |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | "INTERNAL" in enum, exit 1 "Unexpected internal error", but no per-command lists or unknown-code rule Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = fail; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag TAG]... repeated; --fields id,title,tags comma |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | notectl export --output PATH is the only --output command |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **FAIL** | No output class declared per command |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

## Principles

- Every command accepts `--json`; when stdout is not a TTY, JSON is the default.
- stdout carries only the result envelope; diagnostics and progress go to stderr.
- Exit codes are stable and map to error codes.
- No interactive prompts: destructive actions require `--yes`, otherwise they fail with `CONFIRMATION_REQUIRED`.
- `--dry-run` is supported on `create`, `delete`, and `export`.
- Auth via `NOTECTL_TOKEN`; endpoint via `NOTECTL_API_URL`.

## Command surface

```
notectl list   [--tag TAG]... [--limit N] [--cursor C] [--fields id,title,tags]
notectl get    ID [--fields ...]
notectl search QUERY [--tag TAG]... [--limit N] [--cursor C]
notectl create --title TITLE [--body TEXT | --body-file PATH|-] [--tag TAG]... [--idempotency-key KEY] [--dry-run]
notectl delete ID --yes [--dry-run]
notectl export --output PATH [--format json|jsonl] [--overwrite] [--dry-run]
notectl schema [COMMAND]     # prints JSON Schema for a command's output
notectl --version
```

Global flags: `--json`, `--quiet`, `--timeout SECONDS` (default 30), `--api-url URL`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Unexpected internal error |
| 2 | Usage / validation error |
| 3 | Not found |
| 4 | Auth error |
| 5 | Conflict / precondition (e.g. file exists, confirmation required) |
| 6 | Remote API unavailable / timeout (retryable) |
| 7 | Rate limited (retryable) |

## Machine-readable schema

All output uses one envelope (JSON Schema 2020-12):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://notectl.dev/schema/v1/envelope.json",
  "type": "object",
  "required": ["schema_version", "ok", "command"],
  "properties": {
    "schema_version": { "const": "1" },
    "ok": { "type": "boolean" },
    "command": { "enum": ["list", "get", "search", "create", "delete", "export"] },
    "data": {},
    "page": {
      "type": "object",
      "properties": {
        "next_cursor": { "type": ["string", "null"] },
        "returned": { "type": "integer" },
        "truncated": { "type": "boolean" }
      }
    },
    "error": { "$ref": "#/$defs/error" },
    "dry_run": { "type": "boolean" }
  },
  "oneOf": [
    { "properties": { "ok": { "const": true } }, "required": ["data"] },
    { "properties": { "ok": { "const": false } }, "required": ["error"] }
  ],
  "$defs": {
    "note": {
      "type": "object",
      "required": ["id", "title", "body", "tags"],
      "properties": {
        "id": { "type": "string", "pattern": "^n_[a-z0-9]{10}$" },
        "title": { "type": "string", "minLength": 1, "maxLength": 200 },
        "body": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" }, "uniqueItems": true }
      }
    },
    "error": {
      "type": "object",
      "required": ["code", "message", "retryable"],
      "properties": {
        "code": {
          "enum": ["VALIDATION_ERROR", "NOT_FOUND", "AUTH_REQUIRED", "AUTH_INVALID",
                   "CONFIRMATION_REQUIRED", "FILE_EXISTS", "API_UNAVAILABLE",
                   "TIMEOUT", "RATE_LIMITED", "INTERNAL"]
        },
        "message": { "type": "string" },
        "retryable": { "type": "boolean" },
        "retry_after_ms": { "type": ["integer", "null"] },
        "details": { "type": "object" },
        "hint": { "type": "string", "description": "Concrete next command or fix" },
        "request_id": { "type": "string" }
      }
    }
  }
}
```

Per-command `data` shapes:

| Command | `data` |
|---|---|
| list, search | `{"notes": [note]}` (search adds `score` per note); `body` omitted unless `--fields` includes it |
| get | `{"note": note}` |
| create | `{"note": note, "created": true}` (`created: false` on idempotent replay) |
| delete | `{"id": string, "deleted": true}` |
| export | `{"path": string, "format": string, "count": integer, "bytes": integer}` |

## Example success payloads

`notectl list --tag work --limit 2`
```json
{
  "schema_version": "1", "ok": true, "command": "list",
  "data": { "notes": [
    { "id": "n_a1b2c3d4e5", "title": "Q4 planning", "tags": ["work", "planning"] },
    { "id": "n_f6g7h8i9j0", "title": "1:1 notes", "tags": ["work"] }
  ]},
  "page": { "returned": 2, "truncated": true, "next_cursor": "eyJvZmZzZXQiOjJ9" }
}
```

`notectl get n_a1b2c3d4e5`
```json
{
  "schema_version": "1", "ok": true, "command": "get",
  "data": { "note": { "id": "n_a1b2c3d4e5", "title": "Q4 planning",
            "body": "Goals: ship v2.", "tags": ["work", "planning"] } }
}
```

`notectl search "v2" --limit 1`
```json
{
  "schema_version": "1", "ok": true, "command": "search",
  "data": { "notes": [ { "id": "n_a1b2c3d4e5", "title": "Q4 planning", "tags": ["work","planning"], "score": 0.92 } ] },
  "page": { "returned": 1, "truncated": false, "next_cursor": null }
}
```

`notectl create --title "Groceries" --body "milk" --tag home --idempotency-key k1`
```json
{
  "schema_version": "1", "ok": true, "command": "create",
  "data": { "created": true, "note": { "id": "n_k9l8m7n6o5", "title": "Groceries", "body": "milk", "tags": ["home"] } }
}
```

`notectl delete n_k9l8m7n6o5 --yes`
```json
{ "schema_version": "1", "ok": true, "command": "delete", "data": { "id": "n_k9l8m7n6o5", "deleted": true } }
```

`notectl export --output notes.jsonl --format jsonl`
```json
{
  "schema_version": "1", "ok": true, "command": "export",
  "data": { "path": "/home/u/notes.jsonl", "format": "jsonl", "count": 142, "bytes": 58311 }
}
```

## Example error payloads

Not found (`notectl get n_zzzzzzzzzz`, exit 3):
```json
{
  "schema_version": "1", "ok": false, "command": "get",
  "error": { "code": "NOT_FOUND", "message": "No note with id n_zzzzzzzzzz",
    "retryable": false, "details": { "id": "n_zzzzzzzzzz" },
    "hint": "Run `notectl search <query>` or `notectl list` to find valid ids.",
    "request_id": "req_7f3a" }
}
```

Rate limited (exit 7):
```json
{
  "schema_version": "1", "ok": false, "command": "search",
  "error": { "code": "RATE_LIMITED", "message": "Remote API rate limit exceeded",
    "retryable": true, "retry_after_ms": 12000, "request_id": "req_91bc" }
}
```

Delete without confirmation (`notectl delete n_a1b2c3d4e5`, exit 5):
```json
{
  "schema_version": "1", "ok": false, "command": "delete",
  "error": { "code": "CONFIRMATION_REQUIRED", "message": "Refusing to delete without --yes",
    "retryable": false, "details": { "id": "n_a1b2c3d4e5" },
    "hint": "Re-run with --yes, or --dry-run to preview." }
}
```

Export target exists (exit 5):
```json
{
  "schema_version": "1", "ok": false, "command": "export",
  "error": { "code": "FILE_EXISTS", "message": "notes.jsonl already exists",
    "retryable": false, "details": { "path": "/home/u/notes.jsonl" },
    "hint": "Pass --overwrite or choose a different --output." }
}
```

Export writes atomically (temp file + rename), so a failed export never leaves a partial file.
~~~~~~
