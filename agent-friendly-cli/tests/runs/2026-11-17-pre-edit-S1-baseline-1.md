# Scenario 1 (design) — baseline arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/11 scored; 0/2 conformance
- **Tokens:** 52,359 (final-turn context plus output, read from the transcript)
- **Output words:** 1,056
- **Transcript sha256:** `68abea3af993dc654887b540537c7b2d1429f42802c54c2118b311acebbb836b` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o5`; the scorer received the assertions verbatim and no arm labels

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
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **FAIL** | Exit code table and Error "code" enum, but no per-command error catalog Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = fail |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **FAIL** | "stderr carries human diagnostics only" — structured errors go in the stdout envelope Parts: stdout success only = fail; stderr structured failures with framing = fail |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | notectl delete ID --yes [--dry-run]; delete data required "dry_run": {"type": "boolean"} Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "truncated": {"description": "true iff more results exist beyond this page"}, "next_cursor" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "path": "/home/agent/notes.jsonl", ..., "bytes": 183920, "sha256": "9b1c…e04" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **FAIL** | "--timeout SECONDS (default 30)" — no unit in name or unit field |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **FAIL** | "Auth: NOTECTL_TOKEN env var, else profile config" — no inspection or isolation Parts: declared = pass; inspection = fail; isolation = fail |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | No example uses --; vacuously satisfied |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | "INTERNAL" in enum and exit 1 "unexpected internal error" but no per-command lists or unknown-code rule Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = fail; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag TAG]... repeated; --fields id,title,tags comma |
| C1 | conformance | Export is the only `--output <file>` command. | **FAIL** | Export uses "--out PATH"; "--output json\|text" is a global format flag, so export is not the --output <file> command |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **FAIL** | No output class declared per command |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

## Principles

- stdout carries exactly one JSON document per invocation when `--output json` is set (the default when stdout is not a TTY); stderr carries human diagnostics only.
- Every response uses one envelope: `{"ok": true, "data": ...}` or `{"ok": false, "error": ...}`, with `schema_version`.
- Exit codes are stable and documented; agents branch on `error.code`, never on message text.
- Non-interactive: no prompts. Destructive commands require `--yes` (or `--dry-run` to preview).
- Lists are paginated with an opaque cursor; truncation is always explicit.
- `notectl schema [command]` prints the JSON Schema for any command's input and output.

## Command surface

```
notectl list   [--tag TAG]... [--limit N] [--cursor C] [--fields id,title,tags]
notectl get    ID [--fields ...]
notectl search QUERY [--tag TAG]... [--limit N] [--cursor C]
notectl create --title T [--body B | --body-file PATH|-] [--tag TAG]... [--idempotency-key K]
notectl delete ID --yes [--dry-run] [--if-exists]
notectl export --out PATH [--format json|jsonl|markdown] [--overwrite] [--tag TAG]...
notectl schema [COMMAND]
notectl version
```

Global flags: `--output json|text`, `--profile NAME`, `--api-url URL`, `--timeout SECONDS` (default 30), `--quiet`.
Auth: `NOTECTL_TOKEN` env var, else profile config. Never read from a prompt.

Defaults: `--limit` 50, max 500. `list` sorts by `updated_at` desc. `body` is omitted from `list`/`search` items unless `--fields` includes it (keeps output small).

### Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | usage / validation error (bad flags, invalid input) |
| 3 | not found |
| 4 | auth error (missing/invalid token, forbidden) |
| 5 | conflict (e.g. export target exists, idempotency mismatch) |
| 6 | rate limited |
| 7 | remote/network error (timeout, 5xx, unreachable) |
| 1 | unexpected internal error |

## Machine-readable schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://notectl.dev/schema/v1",
  "$defs": {
    "Note": {
      "type": "object",
      "required": ["id", "title", "tags", "created_at", "updated_at"],
      "properties": {
        "id": {"type": "string", "pattern": "^n_[A-Za-z0-9]{12}$"},
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "body": {"type": "string", "description": "Omitted in list/search unless requested via --fields"},
        "tags": {"type": "array", "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,31}$"}, "uniqueItems": true},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      },
      "additionalProperties": false
    },
    "Page": {
      "type": "object",
      "required": ["items", "count", "next_cursor", "truncated"],
      "properties": {
        "items": {"type": "array", "items": {"$ref": "#/$defs/Note"}},
        "count": {"type": "integer", "minimum": 0},
        "next_cursor": {"type": ["string", "null"]},
        "truncated": {"type": "boolean", "description": "true iff more results exist beyond this page"}
      }
    },
    "SearchHit": {
      "allOf": [{"$ref": "#/$defs/Note"}],
      "properties": {"score": {"type": "number"}, "snippet": {"type": "string"}}
    },
    "Error": {
      "type": "object",
      "required": ["code", "message", "retryable"],
      "properties": {
        "code": {"enum": ["USAGE", "VALIDATION", "NOT_FOUND", "AUTH_REQUIRED", "FORBIDDEN", "CONFLICT", "RATE_LIMITED", "REMOTE_UNAVAILABLE", "TIMEOUT", "INTERNAL"]},
        "message": {"type": "string"},
        "retryable": {"type": "boolean"},
        "retry_after_seconds": {"type": ["number", "null"]},
        "details": {"type": "object"},
        "hint": {"type": "string", "description": "Concrete next action, often a corrected command"},
        "request_id": {"type": ["string", "null"]}
      }
    },
    "Envelope": {
      "type": "object",
      "required": ["schema_version", "ok", "command"],
      "properties": {
        "schema_version": {"const": "1"},
        "ok": {"type": "boolean"},
        "command": {"type": "string"},
        "data": {},
        "error": {"$ref": "#/$defs/Error"}
      },
      "oneOf": [
        {"properties": {"ok": {"const": true}}, "required": ["data"]},
        {"properties": {"ok": {"const": false}}, "required": ["error"]}
      ]
    }
  },
  "commands": {
    "list":   {"data": {"$ref": "#/$defs/Page"}},
    "get":    {"data": {"$ref": "#/$defs/Note"}},
    "search": {"data": {"allOf": [{"$ref": "#/$defs/Page"}], "properties": {"query": {"type": "string"}, "items": {"type": "array", "items": {"$ref": "#/$defs/SearchHit"}}}}},
    "create": {"data": {"type": "object", "required": ["note", "created"], "properties": {"note": {"$ref": "#/$defs/Note"}, "created": {"type": "boolean", "description": "false if an idempotency key replayed an earlier create"}}}},
    "delete": {"data": {"type": "object", "required": ["id", "deleted", "dry_run"], "properties": {"id": {"type": "string"}, "deleted": {"type": "boolean"}, "dry_run": {"type": "boolean"}}}},
    "export": {"data": {"type": "object", "required": ["path", "format", "count", "bytes", "complete"], "properties": {"path": {"type": "string"}, "format": {"enum": ["json", "jsonl", "markdown"]}, "count": {"type": "integer"}, "bytes": {"type": "integer"}, "sha256": {"type": "string"}, "complete": {"type": "boolean"}}}}
  }
}
```

## Example success payloads

`notectl list --tag work --limit 2`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "list",
  "data": {
    "items": [
      {"id": "n_a1B2c3D4e5F6", "title": "Q4 planning", "tags": ["work", "planning"], "created_at": "2026-11-01T09:12:00Z", "updated_at": "2026-11-15T17:40:03Z"},
      {"id": "n_Z9y8X7w6V5u4", "title": "1:1 notes", "tags": ["work"], "created_at": "2026-10-20T14:00:00Z", "updated_at": "2026-11-10T14:31:55Z"}
    ],
    "count": 2,
    "next_cursor": "eyJvZmZzZXQiOjJ9",
    "truncated": true
  }
}
```

`notectl get n_a1B2c3D4e5F6`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "get",
  "data": {"id": "n_a1B2c3D4e5F6", "title": "Q4 planning", "body": "Goals:\n- ship v2\n- hire 2", "tags": ["work", "planning"], "created_at": "2026-11-01T09:12:00Z", "updated_at": "2026-11-15T17:40:03Z"}
}
```

`notectl search "ship v2"`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "search",
  "data": {
    "query": "ship v2",
    "items": [{"id": "n_a1B2c3D4e5F6", "title": "Q4 planning", "tags": ["work", "planning"], "created_at": "2026-11-01T09:12:00Z", "updated_at": "2026-11-15T17:40:03Z", "score": 0.92, "snippet": "Goals:\n- **ship v2**"}],
    "count": 1,
    "next_cursor": null,
    "truncated": false
  }
}
```

`notectl create --title "Groceries" --body-file - --tag home --idempotency-key 7f3c`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "create",
  "data": {
    "note": {"id": "n_Qw3Er4Ty5Ui6", "title": "Groceries", "body": "eggs, milk", "tags": ["home"], "created_at": "2026-11-17T08:00:00Z", "updated_at": "2026-11-17T08:00:00Z"},
    "created": true
  }
}
```

`notectl delete n_Qw3Er4Ty5Ui6 --yes`

```json
{"schema_version": "1", "ok": true, "command": "delete", "data": {"id": "n_Qw3Er4Ty5Ui6", "deleted": true, "dry_run": false}}
```

`notectl export --out notes.jsonl --format jsonl`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "export",
  "data": {"path": "/home/agent/notes.jsonl", "format": "jsonl", "count": 412, "bytes": 183920, "sha256": "9b1c…e04", "complete": true}
}
```

Export writes to a temp file and renames atomically, so a failed export never leaves a partial file at `--out`.

## Example error payloads

Not found — `notectl get n_doesnotexist0` (exit 3)

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "get",
  "error": {
    "code": "NOT_FOUND",
    "message": "No note with id 'n_doesnotexist0'.",
    "retryable": false,
    "retry_after_seconds": null,
    "details": {"id": "n_doesnotexist0"},
    "hint": "Run `notectl search <text>` or `notectl list` to find valid ids.",
    "request_id": "req_8d2f61"
  }
}
```

Validation — `notectl create --body "x"` (exit 2)

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "create",
  "error": {
    "code": "VALIDATION",
    "message": "Missing required option --title.",
    "retryable": false,
    "retry_after_seconds": null,
    "details": {"field": "title", "constraint": "required"},
    "hint": "notectl create --title \"<title>\" --body \"x\"",
    "request_id": null
  }
}
```

Rate limited — remote API returned 429 (exit 6)

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "list",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Remote API rate limit exceeded.",
    "retryable": true,
    "retry_after_seconds": 12,
    "details": {"http_status": 429},
    "hint": "Retry the same command after 12 seconds.",
    "request_id": "req_41aa09"
  }
}
```

Conflict — export target exists (exit 5)

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "export",
  "error": {
    "code": "CONFLICT",
    "message": "Output file already exists: notes.jsonl",
    "retryable": false,
    "retry_after_seconds": null,
    "details": {"path": "/home/agent/notes.jsonl"},
    "hint": "Pass --overwrite or choose a different --out path.",
    "request_id": null
  }
}
```

Partial export failure (network drop mid-pagination) returns `REMOTE_UNAVAILABLE`, exit 7, `retryable: true`, with `details.notes_fetched` and no file written.
~~~~~~
