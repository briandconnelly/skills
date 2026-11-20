# 2026-11-19 candidate 5, scenario S1 control, with-skill arm 1

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o88

## Scorer verdicts

## o88

Scored:
- A1: PASS — `"canonical_machine_profile": ["--machine"]`; implied `--json`, `--no-progress`, `--no-input`, `--no-color` all declared.
- A2: PASS — `"exit_codes"`, `"symbolic_error_codes"`, delete `"errors_possible"`.
- A3: PASS — `"stderr_framing": "single-error-object"`; "Example error payloads (stderr only, stdout empty)".
- A4: PASS — explicit `notectl note delete [--if-exists] [--dry-run] [--] <id>` verb; `"shape": {"dry_run": true, "planned_action": "delete|none", ...}`.
- A5: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6: PASS — `"byte_size": "integer", "content_hash": "string"`, "content_hash is sha256:<hex> of the written file".
- A7: PASS — `--timeout-ms` and `--deadline-ms` with `"unit": "ms"`.
- A8: PASS — `"inspect_with": [...]`, `"disable_with": "--isolated (config + cache), --no-config (config only)"`.
- A9: PASS — `notectl note get --machine -- 'note_01HX7Q'`, `notectl note delete --if-exists --machine -- 'note_01HX7Q'`.
- A10: FAIL
  - (a): PASS — `"fallback_error_code": "INTERNAL"`.
  - (b): FAIL — note commands list `NETWORK_ERROR`, but networked `auth whoami` ("`whoami`, which is `network`") has its entry "omitted here for length", so no error list.
  - (c): PASS — `"unknown_code_policy": "a code absent from a command's catalog: act on payload fields ..."`.
- A11: PASS — `"multi_value_syntax": "repeat"` on `--tag`/`--select`.

Conformance:
- C1: PASS — only export declares `--output`.
- C2: FAIL — schema/auth/config entries "omitted here for length"; no output class declared for them.

## Output

# `notectl` agent-facing CLI contract

## 1. Task model

| Agent job | Class | Minimum input | Minimum success output |
|---|---|---|---|
| List notes | query | none (optional `--tag`, `--limit`, `--cursor`) | page of note summaries + `has_more`/`next_cursor` |
| Get a note | inspect | note `id` | one full note record |
| Search notes | query | query text | page of ranked note summaries with ids |
| Create a note | mutate | `--title` (body/tags optional) | created note record with server `id` |
| Delete a note | mutate | note `id` | `{id, status}` |
| Export all notes | query (writes a local file only) | `--output <path>` | `{path, byte_size, content_hash, note_count}` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

Summaries in `list`/`search` omit `body` so pages stay small; `get` returns the full note.
`list` vs `search`: `list` enumerates in a deterministic order with exact filters; `search` ranks by relevance to free text.
That is the one sibling distinction, and the summaries below state it in their first clause.

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for notes: the note ID (`note_…`), positional, the only positional argument anywhere.
Every command accepts `--` end-of-options.

```text
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort <key>] [--select <field>]...
notectl note get     [--select <field>]... [--] <id>
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>]
notectl note create  --title <text> [--body <text> | --body-file <path|->] [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete  [--if-exists] [--dry-run] [--] <id>
notectl note export  --output <path> [--format json|ndjson] [--tag <tag>]... [--overwrite]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth status          # credential source, never the secret
notectl config show --resolved
```

Global flags: `--machine` (canonical machine profile; implies `--json --no-progress --no-input --no-color`), `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`.

Canonical agent invocations:

```sh
notectl note list --tag 'work' --limit 50 --machine
notectl note get --machine -- 'note_01HX7Q'
notectl note search --query 'quarterly plan' --machine
notectl note create --title 'Standup 2026-11-19' --body-file - --tag 'meetings' --idempotency-key '7f3c1e2a-standup' --machine < body.md
notectl note delete --if-exists --machine -- 'note_01HX7Q'
notectl note export --output './notes-export.ndjson' --format ndjson --machine
```

Not-applicable items (with justification):

- `update` is out of scope; not requested.
- Async jobs/`wait`/`cancel`: N/A — every command finishes in the foreground; export pages through the API synchronously and declares a deadline, progress framing, and interrupt behavior instead.
- Aliases/deprecations: N/A at 1.0; declared as empty arrays so future migrations have a home.
- Streaming output class: N/A on stdout — export writes to a file (artifact) so stdout stays one small object even for large note sets.

## 3. Machine schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, `[T]` is an array of `T`.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes in a command catalog"],
    "breaking": ["removing or renaming commands, flags, or fields", "changing a type, enum, or meaning", "exit-code remapping"],
    "rule": "any contract change changes fingerprint; breaking changes bump the major version"
  },
  "fingerprint": "ntc-5e1f09a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; [T] is an array of T",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; on success stderr is empty",
  "output_encoding": {"charset": "UTF-8", "numbers": "locale-independent JSON numbers", "timestamps": "RFC 3339 UTC (Z)", "paths": "absolute POSIX-style in output"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input", "--no-color"], "description": "Non-interactive machine mode: structured output only, no prompts, color, pager, spinner, or browser launch, on every stream regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON success payloads on stdout and JSON errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress human progress on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the local cache; credentials then come only from NOTECTL_TOKEN or stdin via auth flags. Normal authenticated reads still work when NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve; overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "API base URL; overrides NOTECTL_API_URL and config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": "per command", "description": "Per-request network timeout; overrides each command's default."}
  ],
  "exit_codes": {
    "0": "success",
    "1": "generic (INTERNAL)",
    "2": "usage or validation",
    "3": "not found",
    "4": "unauthenticated",
    "5": "forbidden",
    "6": "rate limited",
    "7": "timeout",
    "8": "conflict",
    "9": "transient, including transport failures other than timeout",
    "10": "local output file error (domain-specific)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "TRANSIENT", "NETWORK_ERROR", "OUTPUT_WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "a code absent from a command's catalog: act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "debug": {"flag": "--debug", "description": "Adds redacted request/response metadata to stderr in human mode only; in machine mode it is added as details.debug inside the error object. Authorization headers and tokens are always redacted."},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env var", "OS keychain entry for the profile", "credential file ~/.config/notectl/credentials (mode 0600)"], "secret_values": ["token"], "redaction": "never printed; auth status reports source and last-4 fingerprint only", "argv_secrets_accepted": false, "non_interactive_bootstrap": "printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine"},
    "config_files": ["$NOTECTL_CONFIG or ~/.config/notectl/config.toml"],
    "environment_variables": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "NO_COLOR"],
    "caches": [{"path": "~/.cache/notectl/schema.json", "purpose": "server capability cache for api version negotiation", "disabled_by": "--isolated"}],
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file > cache",
    "disable_with": "--isolated (config + cache), --no-config (config only)",
    "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"]
  },
  "telemetry": {"enabled_by_default": false, "update_checks": false, "machine_mode": "always suppressed"},
  "api_version_negotiation": "sends Accept-Version: 1; a server that cannot serve it fails with VALIDATION_ERROR details.reason=unsupported_api_version (exit 2)",
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"}
  },
  "metadata_paths": {"commands": ["--help", "notectl schema", "notectl schema --fingerprint"], "network": false, "auth_validation": false, "target_latency_ms": 100},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes in a deterministic order, optionally filtered by exact tag. For relevance-ranked free-text lookup use note search.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "description": "Match notes carrying all given tags."},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["updated_at_desc", "created_at_desc", "title_asc"], "default": "updated_at_desc", "tiebreak": "id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false, "size_mode": "paged (max 200 items)",
        "shape": {"items": "[{id: string, title: string, tags: [string], created_at: string, updated_at: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "next_cursor is present iff has_more is true; body is never included, use note get",
        "projection": {"flag": "--select", "rule": "only selected fields are present in each item; unselected fields are absent, not null; id is always present"},
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential from 250ms, honors retry_after_ms"},
      "signal_semantics": {"interrupt": "exits 130 with no output; no state", "closed_stdout": "exits quietly", "local_writes": "none"},
      "async": false, "pagination": true, "truncation": "only via declared pagination", "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Return one full note, including body, by note ID.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["note_01HX7Q"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "record", "format": "json", "streaming": false, "size_mode": "small (body max 1 MiB)",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "exits 130 with no output", "closed_stdout": "exits quietly", "local_writes": "none"},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Rank notes by relevance to free text over title, body, and tags. For exact-filter enumeration use note list.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false, "size_mode": "paged (max 100 items)",
        "shape": {"items": "[{id: string, title: string, tags: [string], updated_at: string, score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "sorted by score descending, then id ascending; snippet is at most 200 characters of body; zero matches returns items: [] with exit 0",
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "exits 130 with no output", "closed_stdout": "exits quietly", "local_writes": "none"},
      "async": false, "pagination": true, "truncation": "only via declared pagination", "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text>",
      "summary": "Create one note. Pass --idempotency-key to make retries safe; without it a failed-in-flight create must be reconciled before retrying.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "Read body from a file; '-' reads stdin.", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "max_items": 32},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Server deduplicates creates with the same key for 24 hours; reuse the same key on retry."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--body-file -", "accepted_formats": ["UTF-8 text"], "maximum_input_size": 1048576, "can_block": "only until EOF of a piped stdin; with --no-input/--machine and a TTY stdin, fails with VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {
        "class": "record", "format": "json", "streaming": false, "size_mode": "small",
        "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "body_bytes": "integer", "replayed": "boolean"},
        "shape_description": "body is not echoed; replayed is true when an earlier create with the same --idempotency-key is returned instead of a new note"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth with a read-only server call; no note is created; no local writes"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "description": "with --idempotency-key, notectl itself retries RATE_LIMITED/TRANSIENT/NETWORK_ERROR up to 2 times reusing the key; without a key it never retries"},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24h. Without a key, retry is NOT safe automatically: a search or list that finds no matching note does not prove the create did not commit; escalate or accept a possible duplicate.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by ID. --if-exists makes it repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["note_01HX7Q"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "record", "format": "json", "streaming": false, "size_mode": "small",
        "shape": {"id": "string", "status": "deleted|absent"},
        "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "planned_action is none when --if-exists would suppress NOTE_NOT_FOUND"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence; no deletion"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write every note (optionally tag-filtered) to a local file and print a pointer to it. Does not modify remote notes.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "json writes {notes: [...]}; ndjson writes one full note per line"},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "per page request"},
        {"name": "--deadline-ms", "type": "integer", "unit": "ms", "default": 600000, "description": "whole-export deadline"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "artifact", "format": "json", "streaming": false, "size_mode": "small pointer; file size unbounded",
        "shape": {"path": "string", "format": "json|ndjson", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "exported_at": "string", "consistency": "best-effort"},
        "file_record_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "file_order": "created_at ascending, then id ascending",
        "shape_description": "content_hash is sha256:<hex> of the written file; consistency is best-effort because notes created or deleted during the page walk may be missed or included"
      },
      "progress": {"machine_mode": "none", "human_mode": "spinner on stderr when stderr is a TTY"},
      "side_effects": {"external_mutation": false, "writes": ["--output path (written to <path>.tmp then atomically renamed)"]},
      "latency_class": "slow", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 3, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "scope": "per page"},
      "signal_semantics": {"interrupt": "temp file removed; destination untouched", "closed_stdout": "finishes the export", "local_writes": "atomic rename; concurrent exports to the same path are last-writer-wins", "remote_continues": false},
      "async": false, "pagination": "internal; walks all pages", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2, "description": "export exceeded the cursor lifetime; restart"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    }
  ]
}
```

`schema`, `auth whoami|status|login`, and `config show --resolved` follow the same per-command shape (all `local` latency except `whoami`, which is `network`); omitted here for length.
`notectl schema note.create` returns one command's entry; `notectl schema --summary` returns `[{command, summary, read_only}]`.

Fingerprint endpoint (`notectl schema --fingerprint --machine`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-5e1f09a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --tag work --limit 2 --machine`

```json
{"items":[{"id":"note_01HX7Q","title":"Q4 plan","tags":["work","planning"],"created_at":"2026-11-02T16:04:11Z","updated_at":"2026-11-18T09:12:40Z"},{"id":"note_01HX2B","title":"Standup 2026-11-17","tags":["work","meetings"],"created_at":"2026-11-17T15:00:02Z","updated_at":"2026-11-17T15:20:44Z"}],"has_more":true,"next_cursor":"c1.eyJvIjoyfQ","limit":2,"estimated_total":37}
```

`notectl note get --machine -- note_01HX7Q`

```json
{"id":"note_01HX7Q","title":"Q4 plan","body":"Ship export v2.\nHire one SRE.","tags":["work","planning"],"created_at":"2026-11-02T16:04:11Z","updated_at":"2026-11-18T09:12:40Z"}
```

`notectl note search --query 'export' --limit 1 --machine`

```json
{"items":[{"id":"note_01HX7Q","title":"Q4 plan","tags":["work","planning"],"updated_at":"2026-11-18T09:12:40Z","score":0.91,"snippet":"Ship export v2."}],"has_more":false,"limit":1}
```

`notectl note create --title 'Standup 2026-11-19' --body-file - --tag meetings --idempotency-key 7f3c1e2a-standup --machine < body.md`

```json
{"id":"note_01HXB4","title":"Standup 2026-11-19","tags":["meetings"],"created_at":"2026-11-19T15:01:07Z","updated_at":"2026-11-19T15:01:07Z","body_bytes":412,"replayed":false}
```

`notectl note create --title 'Draft' --dry-run --machine`

```json
{"dry_run":true,"planned_action":"create","title":"Draft","tags":[],"body_bytes":0}
```

`notectl note delete --machine -- note_01HX2B`

```json
{"id":"note_01HX2B","status":"deleted"}
```

`notectl note delete --if-exists --machine -- note_01HX2B` (already gone)

```json
{"id":"note_01HX2B","status":"absent"}
```

`notectl note export --output ./notes.ndjson --machine`

```json
{"path":"/home/agent/work/notes.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:9f2c4e0a7b1d3e5f60718293a4b5c6d7e8f9012345678901234567890abcdef","note_count":37,"exported_at":"2026-11-19T15:03:55Z","consistency":"best-effort"}
```

## 5. Example error payloads (stderr only, stdout empty)

Not found — `notectl note get --machine -- note_404XYZ`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404XYZ","hint":"Find the ID with note search or note list.","request_id":"req_8c1d","temporary":false}
```

Validation — `notectl note create --title 'x' --tag 'Bad Tag' --machine`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag.","field":"--tag","details":{"value":"Bad Tag","expected_pattern":"^[a-z0-9][a-z0-9_-]{0,63}$"},"hint":"Use lowercase letters, digits, '-' or '_' with no spaces; keep the other flags unchanged.","temporary":false}
```

Rate limited — `notectl note list --machine`, exit `6`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"request_id":"req_19fa","temporary":true}
```

Timeout during create without an idempotency key — exit `7`, outcome unknown:

```json
{"code":"TIMEOUT","message":"Request timed out; the note may or may not have been created.","reconcile_first":true,"details":{"timeout_ms":5000,"idempotency_key":null},"hint":"Re-run only with an --idempotency-key supplied on the original attempt; an empty search does not prove nothing was created.","temporary":false}
```

Unauthenticated — exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credentials.","details":{"credential_sources_checked":["NOTECTL_TOKEN","keychain:default","~/.config/notectl/credentials"]},"hint":"Set NOTECTL_TOKEN or pipe a token to notectl auth login --token-stdin.","temporary":false}
```

Export destination exists — `notectl note export --output ./notes.ndjson --machine`, exit `8`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes.ndjson","hint":"Pass --overwrite or choose a different --output.","temporary":false}
```

## 6. Contract tests to ship

Schema snapshot + fingerprint stability; each success payload above as a golden; each error payload with observed exit code matching the catalog; TTY vs non-TTY and `--machine` suppression (no prompts, color, spinner); `--body-file -` with empty and oversized stdin, and TTY stdin under `--machine` failing instead of blocking; pagination and `CURSOR_EXPIRED`; export atomic write, hash correctness, and interrupt leaving no partial file; flag > env > config precedence and `--isolated`; `--dry-run` output never byte-identical to real output and no remote mutation; create retry with the same idempotency key returning `replayed: true`; `--` handling with an ID starting with `-`; metadata paths make no network call.
