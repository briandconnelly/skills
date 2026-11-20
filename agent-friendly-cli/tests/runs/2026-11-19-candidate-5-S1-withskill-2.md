# 2026-11-19 candidate 5, scenario S1 control, with-skill arm 2

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o81

## Scorer verdicts

## o81

Scored:
- A1: PASS — `"canonical_machine_profile": ["--machine"]`; `--machine` implies `["--json", "--no-progress"]`, both declared.
- A2: PASS — `"exit_codes"`, `"symbolic_error_codes"`, delete `"errors_possible"`.
- A3: PASS — `"stderr_framing": "single-error-object"`; "each error object is the only stderr content and stdout is empty".
- A4: PASS — `"confirmation": "the explicit delete verb is the trigger; no prompt in any mode"`; `"shape": {"dry_run": true, "planned_action": "delete|none", ...}`.
- A5: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6: PASS — `"byte_size": "integer", "content_hash": "string"`; example `"content_hash": "sha256:5d41..."`.
- A7: PASS — `{"name": "--timeout-ms", "type": "integer", "unit": "ms", ...}`.
- A8: PASS — `"inspect_with": [...]`, `"disable_with": {"all": "--isolated", "config_only": "--no-config"}`.
- A9: PASS — `notectl note get --machine -- 'nt_01HZX3'`, `notectl note delete --if-exists --machine -- 'nt_01HZX3'`.
- A10: FAIL
  - (a): PASS — `"fallback_error_code": "INTERNAL"`.
  - (b): FAIL — note commands list `TRANSPORT_ERROR`, but networked `notectl auth whoami` (`"latency_class": "network"`) has no error list at all.
  - (c): PASS — `"unknown_code_policy": "act on payload fields ..."`.
- A11: PASS — `"multi_value_syntax": "repeat"` on `--tag`/`--select`.

Conformance:
- C1: PASS — only export declares `--output`.
- C2: FAIL — note commands declare `"class"`, but `metadata_commands`/`inspection_commands` (schema, auth whoami/status, config show) declare only shapes, no output class.

## Output

# `notectl` agent-facing CLI contract

Audience: tool author designing a new CLI.
Task: new design.

## 1. Task model

| Job | Class | Minimum input | Minimum output for the next step |
| --- | --- | --- | --- |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at` per note + paging |
| Get a note | inspect | `id` | full note record |
| Search notes | query | `--query` | ranked `id`, `title`, `tags`, `snippet` + paging |
| Create a note | mutate | `--title`, body (stdin or file), optional `--tag` | created record with `id` |
| Delete a note | mutate | `id` | `id` + `status` |
| Export all notes | query (local write) | `--output <file>` | `path`, `byte_size`, `content_hash`, `note_count` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect identity and resolved state | admin | none | account, endpoint, credential source (redacted) |

`list` and `search` are distinct by task: `list` enumerates with exact filters in a deterministic order; `search` is full-text and relevance-ranked.
No other sibling pair needs prose to tell apart.

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for a note is its `id` (positional, the only positional argument anywhere).

```text
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort updated_at|created_at|title] [--select <field>]...
notectl note get     [--select <field>]... [--] <id>
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create  --title <text> [--tag <tag>]... [--body-file <path> | --body-stdin] [--idempotency-key <key>] [--if-not-exists] [--dry-run]
notectl note delete  [--if-exists] [--dry-run] [--] <id>
notectl note export  --output <path> [--format json|ndjson] [--overwrite]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth status          # credential source, never the secret
notectl config show --resolved
```

Global flags (all commands): `--machine`, `--json`, `--no-progress`, `--isolated`, `--no-config`, `--profile <name>`, `--endpoint <url>`, `--timeout-ms <n>`.

Canonical machine profile: `--machine`, which implies `--json --no-progress`, disables prompts, color, pager, and browser launch on every stream regardless of TTY.
Isolation profile: `--isolated` (ignore config files and cache; credentials only from `NOTECTL_TOKEN`), distinct from `--machine` because normal reads still need a credential.

Canonical examples:

```sh
notectl note list --tag 'work' --limit 50 --machine
notectl note get --machine -- 'nt_01HZX3'
notectl note search --query 'quarterly plan' --limit 10 --machine
printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --tag 'meetings' --body-stdin --idempotency-key 'create-standup-1119' --machine
notectl note delete --if-exists --machine -- 'nt_01HZX3'
notectl note export --output './notes-export.json' --machine
```

## 3. Machine schema (`notectl schema`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, a string-valued shape describes an NDJSON record sequence.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes in a command catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "changed defaults"],
    "rule": "every contract change changes the fingerprint; breaking changes bump the major version"
  },
  "fingerprint": "ntc-7f3a91c2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this schema excluding fingerprint; tool release version is not an input",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields required unless so marked or removed by a declared projection; a string-valued shape describes an NDJSON record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC3339 UTC (Z)", "numbers": "locale-independent JSON numbers"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress"], "description": "Non-interactive: no prompts, color, pager, browser, or human prose on any stream. Structured output only."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON on stdout and structured errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and cache; read credentials only from NOTECTL_TOKEN."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "env": "NOTECTL_PROFILE", "description": "Config profile to use."},
    {"name": "--endpoint", "type": "url", "default": "https://api.notes.example/v1", "env": "NOTECTL_ENDPOINT", "description": "API base URL."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "Per-request network timeout. Overrides the command default."}
  ],
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get [--] <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete [--] <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status"},
    "config": {"show": "notectl config show --resolved"}
  },
  "aliases": [],
  "deprecations": [],
  "exit_codes": {
    "0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found",
    "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict",
    "9": "transient, including transport failures other than timeout", "10": "local file error (export)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "NOTE_EXISTS", "IDEMPOTENCY_KEY_REUSED", "TRANSPORT_ERROR", "TRANSIENT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "path?": "string", "docs_url?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env var", "OS keychain entry notectl/<profile>", "~/.config/notectl/credentials (mode 0600)"], "secret": true, "redaction": "never printed; auth status shows source and last 4 chars only"},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_ENDPOINT", "NOTECTL_PROFILE", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "NO_COLOR"],
    "cache": {"path": "$XDG_CACHE_HOME/notectl/schema.json", "contents": "nothing but OAuth token refresh metadata", "reads": true, "writes": "token refresh only, atomic rename"},
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file > cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"],
    "secret_intake": "env var, keychain, credential file, or `notectl auth login --token-stdin`; no token flag exists",
    "non_interactive_bootstrap": "printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine"
  },
  "telemetry": {"default": "off", "update_checks": "off", "machine_mode": "always suppressed"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes in a deterministic order, optionally filtered by exact tag. Read-only. Use note search for full-text queries.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must have all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "descending for timestamps, ascending for title; ties broken by id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "truncation": "none within a page; body is never truncated",
        "size_mode": "small (paged)"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"], "backoff": "exponential from 250ms, honors retry_after_ms"},
      "async": false, "streaming": false, "pagination": true, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get [--] <id>",
      "description": "Return one note by id, including body. Read-only. Fails with NOTE_NOT_FOUND (exit 3) if absent.",
      "classification": "inspect",
      "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^nt_[0-9A-Z]{6,26}$", "examples": ["nt_01HZX3"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"}, "truncation": "none", "size_mode": "small (body max 1 MiB)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "pagination": false, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "description": "Full-text search over title and body, ranked by relevance. Read-only. Use note list for exact tag filtering without a query.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "snippet", "score"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "snippet", "score"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id, title, tags, updated_at?, snippet, score}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "ordering": "score descending, ties by id ascending",
        "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"},
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "truncation": "snippet is at most 200 characters; full body via note get",
        "empty_result": "items: [], has_more: false, exit 0",
        "size_mode": "small (paged)"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "pagination": true, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text>",
      "description": "Create one note. Mutating. Body comes from --body-stdin or --body-file (exactly one, or neither for an empty body). Pass --idempotency-key so a timed-out create can be retried safely.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 300},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "max_count": 32, "default": []},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Server deduplicates creates with the same key for 24 hours; same key with different input returns IDEMPOTENCY_KEY_REUSED."},
        {"name": "--if-not-exists", "type": "boolean", "default": false, "description": "Succeed without creating if a note with the identical title already exists; returns it with status existing."},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": "only with --body-stdin", "auto_detected_when_piped": false, "accepted_formats": ["utf-8 text"], "maximum_input_size": "1 MiB", "can_block": "blocks until EOF only when --body-stdin is given; never reads a TTY in machine mode (VALIDATION_ERROR if stdin is a TTY)", "mutually_exclusive_with": ["--body-file"], "empty_stdin": "empty body"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "status": "created|existing"}, "shape_description": "status existing is returned for --if-not-exists matches and for idempotent replays; body is not echoed", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "create|none", "title": "string", "tags": "[string]", "body_bytes": "integer", "existing_id?": "string"}, "shape_description": "planned_action is none and existing_id is set when --if-not-exists matches", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates input and checks --if-not-exists remotely; no externally visible mutation"},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": "1 automatic retry only when --idempotency-key is set; otherwise 0"},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24h. Without a key, the create is not safe to retry automatically; a search returning nothing does not prove the create did not commit.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_KEY_REUSED", "exit": 8},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete [--] <id>",
      "description": "Permanently delete one note by id. Mutating, not undoable. Use --if-exists to make it repeat-safe.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^nt_[0-9A-Z]{6,26}$", "examples": ["nt_01HZX3"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "confirmation": "the explicit delete verb is the trigger; no prompt in any mode",
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action none when --if-exists would suppress NOTE_NOT_FOUND", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note; no externally visible mutation"},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": "1 automatic retry only when --if-exists is set; otherwise 0"},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so re-run with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "description": "Write every note, with body, to a local file and print a pointer to it. Read-only on the remote store; writes one local file. Fails with OUTPUT_EXISTS unless --overwrite.",
      "classification": "query",
      "read_only": "remote read-only; local file write",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "json", "description": "file format: json is {notes: [...]}; ndjson is one note per line"},
        {"name": "--overwrite", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "json|ndjson", "exported_at": "string"}, "path_style": "absolute POSIX path", "file_ordering": "id ascending", "consistency": "best-effort (paged walk, not a snapshot)", "size_mode": "artifact on disk; stdout pointer is small"},
      "progress": "with --machine none; otherwise human progress on stderr only when stderr is a TTY",
      "side_effects": {"external_mutation": false, "writes": ["--output path"], "local_write": "writes to a temp file in the same directory, then atomic rename; concurrent exports to the same path are last-writer-wins"},
      "latency_class": "slow",
      "timeout_defaults_ms": 10000,
      "timeout_description": "--timeout-ms applies per page request; no overall deadline",
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"], "scope": "per page"},
      "signal_semantics": {"interrupt": "temp file removed; --output is untouched", "closed_stdout": "export completes; pointer is lost", "local_writes": "atomic", "remote_continues": false},
      "async": false, "streaming": false, "pagination": "internal", "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    }
  ],
  "metadata_commands": {
    "notectl schema": "full schema; local, no network, no auth",
    "notectl schema <command>": "one command's entry, e.g. notectl schema 'note create'",
    "notectl schema --fingerprint": "{schema_version, fingerprint, fingerprint_scope}",
    "notectl schema --summary": "one line per command: path, classification, read_only",
    "latency_class": "local", "target_ms": 100
  },
  "inspection_commands": {
    "notectl auth whoami": {"latency_class": "network", "shape": {"account_id": "string", "email": "string", "endpoint": "string"}},
    "notectl auth status": {"latency_class": "local", "shape": {"credential_source": "env|keychain|file|none", "profile": "string", "token_suffix?": "string"}},
    "notectl config show --resolved": {"latency_class": "local", "shape": {"endpoint": {"value": "string", "source": "flag|env|config|default"}, "profile": {"value": "string", "source": "flag|env|config|default"}, "timeout_ms": {"value": "integer", "source": "flag|env|config|default"}, "isolated": "boolean"}}
  }
}
```

## 4. Example success payloads

`notectl schema --fingerprint`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3a91c2", "fingerprint_scope": "schema-contract"}
```

`notectl note list --tag 'work' --limit 2 --machine` (exit 0):

```json
{
  "items": [
    {"id": "nt_01HZX3", "title": "Q4 planning", "tags": ["planning", "work"], "updated_at": "2026-11-18T16:02:11Z"},
    {"id": "nt_01HZW9", "title": "Vendor call notes", "tags": ["work"], "updated_at": "2026-11-17T09:40:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c_9f2e1a",
  "limit": 2,
  "estimated_total": 37
}
```

`notectl note get --machine -- 'nt_01HZX3'` (exit 0):

```json
{
  "id": "nt_01HZX3",
  "title": "Q4 planning",
  "body": "Goals:\n- ship v2\n- hire 2",
  "tags": ["planning", "work"],
  "created_at": "2026-11-02T14:00:00Z",
  "updated_at": "2026-11-18T16:02:11Z"
}
```

`notectl note search --query 'ship v2' --limit 10 --machine` (exit 0):

```json
{
  "items": [
    {"id": "nt_01HZX3", "title": "Q4 planning", "tags": ["planning", "work"], "snippet": "Goals:\n- ship v2\n- hire 2", "score": 0.92}
  ],
  "has_more": false,
  "limit": 10,
  "estimated_total": 1
}
```

`printf '%s' 'Blocked on review.' | notectl note create --title 'Standup 2026-11-19' --tag 'meetings' --body-stdin --idempotency-key 'create-standup-1119' --machine` (exit 0):

```json
{"id": "nt_01J0A7", "title": "Standup 2026-11-19", "tags": ["meetings"], "created_at": "2026-11-19T15:30:04Z", "updated_at": "2026-11-19T15:30:04Z", "status": "created"}
```

Same command with `--dry-run` (exit 0):

```json
{"dry_run": true, "planned_action": "create", "title": "Standup 2026-11-19", "tags": ["meetings"], "body_bytes": 18}
```

`notectl note delete --machine -- 'nt_01HZW9'` (exit 0):

```json
{"id": "nt_01HZW9", "status": "deleted"}
```

`notectl note delete --if-exists --machine -- 'nt_01HZW9'` when already gone (exit 0):

```json
{"id": "nt_01HZW9", "status": "absent"}
```

`notectl note export --output './notes-export.json' --machine` (exit 0):

```json
{
  "path": "/home/agent/work/notes-export.json",
  "byte_size": 48213,
  "content_hash": "sha256:5d41402abc4b2a76b9719d911017c5925d41402abc4b2a76b9719d911017c592",
  "note_count": 37,
  "format": "json",
  "exported_at": "2026-11-19T15:31:10Z"
}
```

## 5. Example error payloads

In machine mode each error object is the only stderr content and stdout is empty.

Not found — `notectl note get --machine -- 'nt_404404'`, exit 3:

```json
{"code": "NOTE_NOT_FOUND", "message": "Note not found.", "resource_id": "nt_404404", "temporary": false, "request_id": "req_8c1f"}
```

Validation — `notectl note create --title '' --machine`, exit 2:

```json
{"code": "VALIDATION_ERROR", "message": "Title must not be empty.", "field": "--title", "details": {"min_length": 1, "max_length": 300}, "hint": "Pass a non-empty --title; other inputs are valid.", "temporary": false}
```

Rate limited — `notectl note search --query 'ship' --machine`, exit 6:

```json
{"code": "RATE_LIMITED", "message": "Rate limit exceeded.", "retry_after_ms": 30000, "temporary": true, "request_id": "req_91aa"}
```

Unknown-outcome create — `notectl note create ... --idempotency-key 'create-standup-1119' --machine`, exit 7:

```json
{"code": "TIMEOUT", "message": "Request timed out after 10000 ms; the note may have been created.", "temporary": false, "reconcile_first": true, "details": {"timeout_ms": 10000, "idempotency_key": "create-standup-1119"}, "hint": "Re-run with the same --idempotency-key.", "request_id": "req_a03d"}
```

Unauthenticated — any networked command, exit 4:

```json
{"code": "UNAUTHENTICATED", "message": "No valid credential.", "temporary": false, "details": {"credential_sources_checked": ["env", "keychain", "file"]}, "hint": "Set NOTECTL_TOKEN or run notectl auth login --token-stdin."}
```

Export target exists — `notectl note export --output './notes-export.json' --machine`, exit 8:

```json
{"code": "OUTPUT_EXISTS", "message": "Output file already exists.", "path": "/home/agent/work/notes-export.json", "field": "--output", "hint": "Add --overwrite or choose another --output.", "temporary": false}
```

## 6. Remaining checklist items

- **Command Model**: `noun verb`, one level deep, one positional (`id`) per resource, conventional flag names (`--limit`, `--output`, `--timeout-ms`, `--format`); no aliases.
- **Shell Safety**: `--` supported and declared; ids, titles, queries, and paths are never passed to a shell; body enters via stdin or file rather than argv; hints name flags, not shell strings built from input.
- **Agent-Safe Invocation**: non-TTY suppression evaluated per stream; `schema`, `--help`, and `auth status` touch no network and load no plugins; every networked command honors `--timeout-ms`.
- **Partial failure**: not applicable — no multi-item mutating command; export is all-or-nothing (atomic rename).
- **Async jobs**: not applicable — every command finishes in the foreground; export declares per-page timeout and interrupt behavior instead.
- **Debug and secrets**: `--debug` (opt-in, not in machine profile) writes redacted request/response traces to stderr; tokens never appear in any output, example, or artifact.
- **Prose surfaces**: each `description` leads with constraint and side effect, then the sibling-selection cue.

## 7. Contract tests to ship

- Snapshot of `notectl schema` and fingerprint stability across a version-only release.
- Golden success payloads above; golden error payloads with observed exit codes matching `errors_possible`.
- `--machine` with a TTY and without: no prompts, color, or prose; empty stdout on failure; single error object on stderr.
- `--body-stdin` with empty stdin, with >1 MiB, and with a TTY stdin; `--body-file` + `--body-stdin` rejected.
- Pagination: `has_more`/`next_cursor`, `CURSOR_EXPIRED` restart.
- `--select` projection: unselected fields absent.
- Env/config precedence and `--isolated`/`--no-config`.
- `--dry-run` for create and delete: no remote mutation, `dry_run: true`.
- Idempotent create replay returns `status: existing`; `--if-exists` delete returns `absent`.
- Export: atomic write under SIGINT leaves `--output` untouched; concurrent exports to one path; `OUTPUT_EXISTS` without `--overwrite`; `content_hash` matches file.
- Closed stdout (`| head -c1`) on list exits quietly.
