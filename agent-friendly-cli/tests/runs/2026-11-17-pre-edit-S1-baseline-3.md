# Scenario 1 (design) — baseline arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/11 scored; 1/2 conformance
- **Tokens:** 51,248 (final-turn context plus output, read from the transcript)
- **Output words:** 876
- **Transcript sha256:** `6d614832fdeeb71ca5ae3f0650c24e801148bbce7e664bebd3ca28fe563bb6de` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

## Arm instructions

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **FAIL** | No canonical machine profile declared; schema is only an output envelope Parts: profile declared in schema = fail; named flags declared = fail |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **FAIL** | Exit code table and "code": {"enum": [...]}, but no per-command error catalog Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = fail |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **FAIL** | "Diagnostics and progress go to stderr only" — error envelopes are not routed to stderr; no framing declared Parts: stdout success only = fail; stderr structured failures with framing = fail |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | notectl delete ID (--yes \| --dry-run); delete data {"id", "deleted", "dry_run": bool} Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "next_cursor": "eyJvZmZzZXQiOjJ9", "truncated": true (has_more equivalent) |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "path": "/home/u/notes.jsonl", ..., "bytes": 88412, "sha256": "9b1f...e2" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **FAIL** | "--timeout SECONDS" — unit only in metavar, not in name or a unit field |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **FAIL** | Only --token-env/NOTECTL_TOKEN mentioned; no inspection or isolation affordance Parts: declared = fail; inspection = fail; isolation = fail |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | No example uses --; vacuously satisfied |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | "internal_error" in enum, exit 1 "Unexpected internal error" but no per-command lists and no rule for unlisted codes Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = fail; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag TAG]... (repeated); --fields F1,F2 (comma) |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | notectl export --output PATH is the only --output command |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **FAIL** | No output class declared per command |

## Verbatim final output

~~~~~~markdown
# notectl: agent-facing CLI contract

## Principles

- Output on stdout is always exactly one JSON document when `--json` is set (default when stdout is not a TTY).
- Diagnostics and progress go to stderr only.
- Exit codes are stable and documented; errors carry a stable machine `code`.
- Non-interactive: never prompts; destructive commands require `--yes` or `--dry-run`.
- Every response carries `schema_version`.

## Command surface

```
notectl list   [--tag TAG]... [--limit N] [--cursor C] [--fields F1,F2]
notectl get    ID [--fields F1,F2]
notectl search QUERY [--tag TAG]... [--limit N] [--cursor C]
notectl create --title T [--body B | --body-file PATH|-] [--tag TAG]... [--idempotency-key K]
notectl delete ID (--yes | --dry-run)
notectl export --output PATH [--format json|jsonl] [--overwrite]
notectl schema [COMMAND]          # emits JSON Schema for a command's output
notectl --version
```

Global flags: `--json` / `--human`, `--api-url URL` (env `NOTECTL_API_URL`), `--token-env NAME` (default `NOTECTL_TOKEN`), `--timeout SECONDS` (default 30), `--quiet`.

Defaults: `--limit 50` (max 500). `list` and `search` paginate via opaque `next_cursor`; `null` means no more pages.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Usage error (bad flags/args) |
| 3 | Not found |
| 4 | Authentication/authorization failure |
| 5 | Conflict (e.g. export target exists, idempotency mismatch) |
| 6 | Remote API unavailable / timeout (retryable) |
| 7 | Rate limited (retryable) |
| 8 | Local I/O error |
| 1 | Unexpected internal error |

## Machine-readable schema

Envelope (JSON Schema, draft 2020-12):

```json
{
  "$id": "https://notectl.dev/schema/v1/envelope.json",
  "type": "object",
  "required": ["schema_version", "ok", "command"],
  "properties": {
    "schema_version": {"const": "1"},
    "ok": {"type": "boolean"},
    "command": {"enum": ["list", "get", "search", "create", "delete", "export"]},
    "data": {},
    "error": {"$ref": "#/$defs/error"},
    "meta": {"$ref": "#/$defs/meta"}
  },
  "oneOf": [
    {"properties": {"ok": {"const": true}}, "required": ["data"]},
    {"properties": {"ok": {"const": false}}, "required": ["error"]}
  ],
  "$defs": {
    "note": {
      "type": "object",
      "required": ["id", "title", "body", "tags"],
      "properties": {
        "id": {"type": "string", "pattern": "^n_[A-Za-z0-9]{12}$"},
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "body": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": true}
      }
    },
    "page": {
      "type": "object",
      "required": ["items", "next_cursor"],
      "properties": {
        "items": {"type": "array", "items": {"$ref": "#/$defs/note"}},
        "next_cursor": {"type": ["string", "null"]},
        "truncated": {"type": "boolean"}
      }
    },
    "error": {
      "type": "object",
      "required": ["code", "message", "retryable"],
      "properties": {
        "code": {"enum": ["usage_error", "not_found", "auth_failed", "forbidden", "conflict", "api_unavailable", "timeout", "rate_limited", "io_error", "internal_error"]},
        "message": {"type": "string"},
        "retryable": {"type": "boolean"},
        "retry_after_ms": {"type": ["integer", "null"]},
        "details": {"type": "object"},
        "hint": {"type": "string", "description": "Concrete next action, e.g. a corrected command"}
      }
    },
    "meta": {
      "type": "object",
      "properties": {
        "request_id": {"type": "string"},
        "duration_ms": {"type": "integer"}
      }
    }
  }
}
```

`data` per command:

| Command | `data` |
|---------|--------|
| list, search | `page` (search items add `score: number`) |
| get, create | `note` (create adds `created: true`, or `false` on idempotent replay) |
| delete | `{"id": string, "deleted": bool, "dry_run": bool}` |
| export | `{"path": string, "format": string, "count": int, "bytes": int, "sha256": string}` |

`notectl schema list` prints the resolved schema so agents need not hardcode it.

## Example success payloads

`notectl list --tag work --limit 2`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "list",
  "data": {
    "items": [
      {"id": "n_a1B2c3D4e5F6", "title": "Q4 plan", "body": "Draft goals...", "tags": ["work", "planning"]},
      {"id": "n_Z9y8X7w6V5u4", "title": "1:1 notes", "body": "Discussed...", "tags": ["work"]}
    ],
    "next_cursor": "eyJvZmZzZXQiOjJ9",
    "truncated": true
  },
  "meta": {"request_id": "req_7f3a", "duration_ms": 142}
}
```

`notectl create --title "Groceries" --body "milk, eggs" --tag home --idempotency-key 5c1e`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "create",
  "data": {"id": "n_Q1w2E3r4T5y6", "title": "Groceries", "body": "milk, eggs", "tags": ["home"], "created": true},
  "meta": {"request_id": "req_81bc", "duration_ms": 210}
}
```

`notectl delete n_Q1w2E3r4T5y6 --yes`

```json
{"schema_version": "1", "ok": true, "command": "delete", "data": {"id": "n_Q1w2E3r4T5y6", "deleted": true, "dry_run": false}}
```

`notectl export --output notes.jsonl --format jsonl`

```json
{
  "schema_version": "1",
  "ok": true,
  "command": "export",
  "data": {"path": "/home/u/notes.jsonl", "format": "jsonl", "count": 312, "bytes": 88412, "sha256": "9b1f...e2"}
}
```

Export writes to a temp file and renames atomically, so a failed export never leaves a partial file at `PATH`.

## Example error payloads

Not found — `notectl get n_doesnotexist0` (exit 3):

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "get",
  "error": {
    "code": "not_found",
    "message": "No note with id 'n_doesnotexist0'.",
    "retryable": false,
    "retry_after_ms": null,
    "details": {"id": "n_doesnotexist0"},
    "hint": "Run `notectl search <text>` or `notectl list` to find valid ids."
  },
  "meta": {"request_id": "req_90de"}
}
```

Rate limited — `notectl search "budget"` (exit 7):

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "search",
  "error": {
    "code": "rate_limited",
    "message": "Remote API rate limit exceeded.",
    "retryable": true,
    "retry_after_ms": 4000,
    "details": {"limit": 60, "window_s": 60}
  },
  "meta": {"request_id": "req_a12f"}
}
```

Auth failure — any command with missing/invalid token (exit 4):

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "list",
  "error": {
    "code": "auth_failed",
    "message": "Token in NOTECTL_TOKEN was rejected (401).",
    "retryable": false,
    "retry_after_ms": null,
    "details": {"token_env": "NOTECTL_TOKEN", "status": 401},
    "hint": "Set a valid token in NOTECTL_TOKEN; do not pass it as a flag."
  }
}
```

Conflict — `notectl export --output notes.json` when file exists (exit 5):

```json
{
  "schema_version": "1",
  "ok": false,
  "command": "export",
  "error": {
    "code": "conflict",
    "message": "Output file already exists.",
    "retryable": false,
    "retry_after_ms": null,
    "details": {"path": "/home/u/notes.json"},
    "hint": "Re-run with --overwrite or choose a different --output path."
  }
}
```

Usage errors (exit 2) use the same envelope with `code: "usage_error"` and a `hint` showing the corrected invocation.
~~~~~~
