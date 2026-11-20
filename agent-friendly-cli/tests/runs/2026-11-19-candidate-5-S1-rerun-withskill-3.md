# 2026-11-19 candidate 5, scenario S1-rerun control, with-skill arm 3

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o74

## Scorer verdicts

## Output o74

Scored:

- A1: PASS — `"canonical_machine_profile": ["--machine"]`; `--machine` in `global_flags`.
- A2: PASS — `"exit_codes"`, `"symbolic_error_codes"`, delete `"errors_possible": [...]`.
- A3: PASS — `"stderr_framing": "single-error-object"`; "Example error payloads (stderr, stdout empty)".
- A4: PASS — `notectl note delete <id>`; `"--dry-run": {... "shape": {"dry_run": true, "planned_action": "delete|none", ...`.
- A5: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6: PASS — `{"path": "string", "absolute_path": "string", "byte_size": "integer", "content_hash": "string", ...}`.
- A7: PASS — `{"name": "--timeout-ms", "type": "integer", "unit": "ms", ...}`.
- A8: PASS — `"ambient_state": {... "disable_with": {"--isolated": ..., "--no-config": ...}, "inspect_with": [...]`.
- A9: PASS — `notectl note delete --if-exists --machine -- 'note_01HV3K9Z'`.
- A10: PASS
  - (a): PASS — `"fallback_error_code": "INTERNAL"`.
  - (b): PASS — `{"code": "NETWORK_UNREACHABLE", "exit": 9, ...}` in list/get/search/create/delete/export/whoami/auth login.
  - (c): PASS — `"unknown_code_policy": "act on payload fields ..."`.
- A11: PASS — `"--tag", ... "multi_value_syntax": "repeat"`.

Conformance (non-scored):

- C1: PASS — `--output` only on `note export`.
- C2: PASS — every command entry declares `"class"`; create/delete `"alternate_outputs": {"--dry-run": {"class": "record", ...`.

## Output

# `notectl` agent-facing CLI contract

Audience: tool author (designing a new CLI).
Task: new design, following the design workflow; every contract-checklist section is answered in the schema or marked not-applicable at the end.

## 1. Task model

| Job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at` per note + paging |
| Get a note | inspect | note `id` | full note |
| Search notes | query | query text | `id`, `title`, `tags`, `snippet`, `score` + paging |
| Create a note | mutate | `title`; optional body, tags | created note (with `id`) |
| Delete a note | mutate | note `id` | `id`, `status` |
| Export all notes | query (writes local artifact) | output path | `path`, `byte_size`, `content_hash`, `count` |
| Discover contract | discover | none / command name | schema, fingerprint |
| Inspect identity/state | admin | none | identity, resolved config, credential source |

`list` vs `search`: `list` enumerates with exact filters and a deterministic order; `search` ranks by relevance to free text.
They differ in input (no query vs required query) and order, so the summaries separate them without prose beyond one line.

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for notes: the note `id` (positional, only on `get` and `delete`).
All commands support `--` end-of-options.

```
notectl note list    [--tag TAG]... [--limit N] [--cursor CURSOR] [--select FIELD]...
notectl note get     <id> [--select FIELD]...
notectl note search  --query TEXT [--tag TAG]... [--limit N] [--cursor CURSOR]
notectl note create  --title TEXT [--body TEXT | --body-file PATH|-] [--tag TAG]... [--idempotency-key KEY] [--dry-run]
notectl note delete  <id> [--if-exists] [--dry-run]
notectl note export  --output PATH [--format json|ndjson] [--overwrite]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth status          # which credential source is in effect (redacted)
notectl auth login --token-stdin   # non-interactive bootstrap
notectl config show --resolved
```

Global flags: `--machine`, `--json`, `--no-progress`, `--no-color`, `--isolated`, `--no-config`, `--profile NAME`, `--api-url URL`, `--timeout-ms N`.

Canonical machine-mode examples (values quoted):

```sh
notectl note list --tag 'work' --limit 50 --machine
notectl note get --machine -- 'note_01HV3K9Z'
notectl note search --query 'quarterly plan' --machine
printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --body-file - --tag 'meetings' --idempotency-key 'b1f0c2e4-standup-1119' --machine
notectl note delete --if-exists --machine -- 'note_01HV3K9Z'
notectl note export --output 'notes-export.ndjson' --format ndjson --machine
notectl schema --fingerprint
```

Help summaries (rules first, then context):

- `note list` — List notes in `updated_at desc, id asc` order; filter by exact tag; paginated (default 50, max 500). Use `note search` for text matching.
- `note get` — Return one note by id, including body. Fails `NOTE_NOT_FOUND` (exit 3) if absent.
- `note search` — Rank notes by relevance to `--query` (required); returns snippets, not full bodies. Use `note get` for the body.
- `note create` — Create one note. Not safe to retry without `--idempotency-key`. Body from `--body` or `--body-file` (`-` = stdin).
- `note delete` — Permanently delete one note. Use `--if-exists` for repeat-safe deletes.
- `note export` — Write all notes to a local file atomically; prints path, size, hash. Refuses to overwrite unless `--overwrite`.

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7f3e91a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "schema contract only; tool version is not an input",
  "compatibility": {
    "additive": ["new commands", "new optional output fields", "new optional flags", "new symbolic error codes in a command catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "default changes"],
    "rule": "any contract change changes the fingerprint; breaking changes bump the major schema_version"
  },
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode stderr is empty on success and holds exactly one JSON error object on failure; no progress or warnings are written to stderr in machine mode (warnings appear in the stdout payload's warnings array)",
  "encoding": {"charset": "utf-8", "timestamps": "RFC 3339 UTC (Z)", "numbers": "locale-independent JSON numbers", "paths": "as given by the caller, plus absolute_path in POSIX style"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Non-interactive: never prompts, no pager, no color, no browser, structured output only, regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit structured JSON/NDJSON on stdout and JSON errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the response cache; credentials come only from NOTECTL_TOKEN. Normal authenticated commands still work when NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to use. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL. Overrides NOTECTL_API_URL and config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": "per command", "description": "Overall deadline for the command, including retries."},
    {"name": "--debug", "type": "boolean", "default": false, "description": "Opt-in redacted request diagnostics on stderr; not allowed with --machine (VALIDATION_ERROR)."}
  ],
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, including transport failures other than timeout", "10": "export destination problem (domain-specific)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "IDEMPOTENCY_KEY_REUSED", "TRANSIENT", "NETWORK_UNREACHABLE", "OUTPUT_EXISTS", "OUTPUT_NOT_WRITABLE"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before retrying",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env var", "OS keychain entry notectl/<profile>", "~/.config/notectl/credentials.json (0600)"], "secret": true, "redaction": "never printed; inspection shows source and last 4 characters only", "argv_secrets": "not accepted; use NOTECTL_TOKEN or auth login --token-stdin"},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "NO_COLOR"],
    "cache": {"path": "$XDG_CACHE_HOME/notectl/", "contents": "schema fingerprint only; note data is never cached", "reads": true, "writes": "atomic rename; last-writer-wins"},
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config files > cache",
    "disable_with": {"--isolated": "config + cache + keychain/credential file", "--no-config": "config files only"},
    "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"],
    "auth": "required for note commands; not required for schema, --help, config show"
  },
  "telemetry": {"enabled_by_default": false, "update_checks": false, "machine_mode": "always suppressed"},
  "metadata_paths": {"commands": ["--help", "notectl schema", "notectl schema --fingerprint"], "target_ms": 100, "network": false, "auth_validation": false},
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"},
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    }
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes ordered by updated_at desc, id asc. Exact tag filter, cursor pagination. For text matching use note search.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must have all given tags", "examples": ["work"]},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false,
        "shape": {"items": "[{id, title, tags, updated_at}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "items contain only selected fields; unselected fields are absent, not null; id is always present"},
        "body_included": false,
        "sort": "updated_at desc, id asc (deterministic)",
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "size_mode": "bounded by --limit"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_UNREACHABLE"], "backoff": "exponential, honors Retry-After, within --timeout-ms"},
      "signal_semantics": {"interrupt": "exits 130 by signal; no state changed", "closed_stdout": "exits quietly"},
      "async": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "description": "Return one note by id, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HV3K9Z"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields absent, not null"}, "truncation": "none; body max size is 1 MiB server-side", "size_mode": "small (<= ~1 MiB)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_UNREACHABLE"]},
      "signal_semantics": {"interrupt": "no state changed", "closed_stdout": "exits quietly"},
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
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "description": "Rank notes by relevance to --query (required). Returns snippets, not bodies; use note get for the body.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "restrict to notes with all given tags"},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false,
        "shape": {"items": "[{id, title, tags, updated_at, score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "sort": "score desc, id asc (deterministic for a given index state)",
        "snippet": "max 200 characters, plain text",
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "empty_result": "items [] with has_more false; exit 0",
        "size_mode": "bounded by --limit"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_UNREACHABLE"]},
      "signal_semantics": {"interrupt": "no state changed", "closed_stdout": "exits quietly"},
      "async": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text>",
      "description": "Create one note. Not safe to retry unless the original attempt carried --idempotency-key. Body from --body or --body-file (- reads stdin).",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "UTF-8 text file; '-' reads stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_count": 20},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Server deduplicates attempts with the same key for 24 hours."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--body-file -", "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": "1 MiB", "can_block": "only until EOF of an explicitly requested pipe; never waits on a TTY in machine mode (VALIDATION_ERROR if stdin is a TTY)", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"note": "note_shape", "replayed": "boolean"}, "shape_description": "replayed is true when the server returned an earlier result for the same --idempotency-key", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "create", "note": "{title, body_bytes: integer, tags}"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth with a read-only API call; no externally visible mutation; may refresh the token (suppressed under --isolated)"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": "2 only when --idempotency-key is set (on RATE_LIMITED, TRANSIENT, NETWORK_UNREACHABLE, TIMEOUT); otherwise 0, except RATE_LIMITED which is rejected before commit"},
      "reconciliation": "on TIMEOUT, TRANSIENT, NETWORK_UNREACHABLE, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24h. Without a key the create is not safe to retry automatically: an empty note list/search does not prove the create did not commit.",
      "signal_semantics": {"interrupt": "remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "note": "retryable only with the same --idempotency-key"},
        {"code": "IDEMPOTENCY_KEY_REUSED", "exit": 8, "description": "key already used with different inputs"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Permanently delete one note. --if-exists makes it repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HV3K9Z"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action is none when --if-exists would suppress NOTE_NOT_FOUND", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note; no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSIENT, NETWORK_UNREACHABLE, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so re-run with --if-exists",
      "signal_semantics": {"interrupt": "remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
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
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "description": "Write all notes to a local file, atomically. Refuses an existing path unless --overwrite. Prints path, size, hash, count.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "remote_read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "destination file; '-' is not accepted"},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "file format: ndjson = one note_shape per line; json = {notes: [note_shape], exported_at}"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "streaming": false, "shape": {"path": "string", "absolute_path": "string", "byte_size": "integer", "content_hash": "string", "count": "integer", "format": "json|ndjson", "exported_at": "string", "consistency": "best-effort"}, "file_order": "id asc", "size_mode": "small pointer; file grows with note count"},
      "side_effects": {"external_mutation": false, "writes": ["--output path (temp file in same directory, then atomic rename)"]},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "retry_defaults": {"retries": "2 per page request on RATE_LIMITED, TRANSIENT, NETWORK_UNREACHABLE"},
      "long_running": {"mode": "foreground", "deadline": "--timeout-ms", "progress": "human mode: progress bar on stderr when stderr is a TTY; machine mode: none"},
      "consistency": "best-effort page walk; notes changed during export may be missed or duplicated-free by id dedupe",
      "signal_semantics": {"interrupt": "temp file removed; destination untouched", "closed_stdout": "finishes the export (only the pointer is lost)", "local_writes": "atomic rename; concurrent exports to the same path are last-writer-wins", "remote_continues": false},
      "async": false, "pagination": false, "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_NOT_WRITABLE", "exit": 10}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>] [--fingerprint] [--summary]",
      "description": "Print this contract, one command's contract, a fingerprint, or a one-screen summary. No network, no auth.",
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command", "type": "string", "cardinality": "zero-or-one", "examples": ["note create"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape_description": "full schema; or {schema_version, fingerprint, fingerprint_scope} with --fingerprint; or one command entry with <command>"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown command name"}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "description": "Show the authenticated account. Makes one API call.",
      "classification": "admin", "read_only": true,
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "api_url": "string", "credential_source": "env|keychain|credentials_file"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl auth status",
      "description": "Show which credential source would be used and whether each source is present. No network; token values redacted.",
      "classification": "admin", "read_only": true,
      "output": {"class": "record", "format": "json", "shape": {"active_source": "env|keychain|credentials_file|none", "sources": "[{source, present: boolean, token_suffix?: string}]"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}]
    },
    {
      "canonical_invocation_path": "notectl auth login --token-stdin",
      "description": "Store an API token read from stdin in the OS keychain for the active profile. Non-interactive bootstrap; there is no browser flow in machine mode.",
      "classification": "admin", "read_only": false,
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--token-stdin", "accepted_formats": ["token text, trailing newline stripped"], "maximum_input_size": "4 KiB", "can_block": "until EOF of the pipe; VALIDATION_ERROR if stdin is a TTY in machine mode", "mutually_exclusive_with": [], "empty_stdin": "VALIDATION_ERROR"},
      "output": {"class": "record", "format": "json", "shape": {"stored": true, "profile": "string", "credential_source": "keychain|credentials_file", "token_suffix": "string"}},
      "side_effects": {"external_mutation": false, "writes": ["OS keychain or credentials file (atomic, 0600)"]},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "NETWORK_UNREACHABLE", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "description": "Show every resolved setting with its source (flag, env, config, default). Secrets redacted. No network.",
      "classification": "admin", "read_only": true,
      "output": {"class": "record", "format": "json", "shape": {"settings": "[{key, value, source: flag|env|config|default, secret: boolean}]", "config_files_read": "[string]"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "malformed config file"}]
    }
  ]
}
```

Fingerprint endpoint (`notectl schema --fingerprint`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --tag 'work' --limit 2 --machine`

```json
{
  "items": [
    {"id": "note_01HV3K9Z", "title": "Q4 planning", "tags": ["planning", "work"], "updated_at": "2026-11-18T21:04:11Z"},
    {"id": "note_01HV2A7Q", "title": "Vendor call notes", "tags": ["work"], "updated_at": "2026-11-17T15:30:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c2V0OjI6MTczMTg2",
  "limit": 2,
  "estimated_total": 37
}
```

`notectl note get --machine -- 'note_01HV3K9Z'`

```json
{
  "id": "note_01HV3K9Z",
  "title": "Q4 planning",
  "body": "Goals:\n- ship notectl 1.0\n- migrate tags",
  "tags": ["planning", "work"],
  "created_at": "2026-11-02T09:12:45Z",
  "updated_at": "2026-11-18T21:04:11Z"
}
```

`notectl note search --query 'quarterly plan' --limit 1 --machine`

```json
{
  "items": [
    {"id": "note_01HV3K9Z", "title": "Q4 planning", "tags": ["planning", "work"], "updated_at": "2026-11-18T21:04:11Z", "score": 0.92, "snippet": "Goals: ship notectl 1.0, migrate tags"}
  ],
  "has_more": false,
  "limit": 1
}
```

`printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --body-file - --tag 'meetings' --idempotency-key 'b1f0c2e4-standup-1119' --machine`

```json
{
  "note": {
    "id": "note_01HV5M2C",
    "title": "Standup 2026-11-19",
    "body": "Blocked on API review.",
    "tags": ["meetings"],
    "created_at": "2026-11-19T16:00:02Z",
    "updated_at": "2026-11-19T16:00:02Z"
  },
  "replayed": false
}
```

`notectl note create --title 'Draft' --tag 'ideas' --dry-run --machine`

```json
{"dry_run": true, "planned_action": "create", "note": {"title": "Draft", "body_bytes": 0, "tags": ["ideas"]}}
```

`notectl note delete --machine -- 'note_01HV2A7Q'`

```json
{"id": "note_01HV2A7Q", "status": "deleted"}
```

`notectl note delete --if-exists --machine -- 'note_01HV2A7Q'` (already gone)

```json
{"id": "note_01HV2A7Q", "status": "absent"}
```

`notectl note export --output 'notes-export.ndjson' --machine`

```json
{
  "path": "notes-export.ndjson",
  "absolute_path": "/home/agent/work/notes-export.ndjson",
  "byte_size": 48213,
  "content_hash": "sha256:9f2c4b1e0a7d3c6b5e8f1a2d4c7b0e3f6a9d2c5b8e1f4a7d0c3b6e9f2a5d8c1b",
  "count": 37,
  "format": "ndjson",
  "exported_at": "2026-11-19T16:05:40Z",
  "consistency": "best-effort"
}
```

## 5. Example error payloads (stderr, stdout empty)

Per `stderr_framing: single-error-object`, each object is the only stderr content in machine mode.

Not found — `notectl note get --machine -- 'note_404'`, exit `3`:

```json
{
  "code": "NOTE_NOT_FOUND",
  "message": "Note not found.",
  "resource_id": "note_404",
  "request_id": "req_8c1d2e",
  "temporary": false
}
```

Validation — `notectl note create --title 'X' --tag 'Bad Tag!' --machine`, exit `2`:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid tag.",
  "field": "--tag",
  "details": {"value": "Bad Tag!", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$"},
  "hint": "Use lowercase letters, digits, '-' or '_', up to 32 characters; keep the other flags unchanged.",
  "temporary": false
}
```

Unauthenticated — any note command with no token, exit `4`:

```json
{
  "code": "UNAUTHENTICATED",
  "message": "No API token found.",
  "details": {"checked_sources": ["env:NOTECTL_TOKEN", "keychain:notectl/default", "file:~/.config/notectl/credentials.json"]},
  "hint": "Set NOTECTL_TOKEN, or pipe a token to auth login with --token-stdin.",
  "temporary": false
}
```

Rate limited — `notectl note search --query 'plan' --machine`, exit `6` (after built-in retries exhausted):

```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 30000,
  "details": {"retries_attempted": 2},
  "request_id": "req_4f77aa",
  "temporary": true
}
```

Unknown outcome on a mutation — `notectl note create ... --idempotency-key 'b1f0c2e4-standup-1119' --machine`, exit `7`:

```json
{
  "code": "TIMEOUT",
  "message": "Create did not complete within 10000 ms; outcome unknown.",
  "reconcile_first": true,
  "details": {"timeout_ms": 10000, "idempotency_key_present": true},
  "hint": "Re-run with the same --idempotency-key within 24 hours; a replay returns the original note with replayed: true.",
  "temporary": false
}
```

Export destination exists — `notectl note export --output 'notes-export.ndjson' --machine`, exit `10`:

```json
{
  "code": "OUTPUT_EXISTS",
  "message": "Output file already exists.",
  "path": "notes-export.ndjson",
  "field": "--output",
  "hint": "Add --overwrite or choose another --output path.",
  "temporary": false
}
```

## 6. Checklist walk

| Section | Answer |
|---|---|
| Command Model | `notectl note <verb>`, one canonical op per task, id is the one positional selector, conventional flags (`--limit`, `--timeout-ms`, `--output`, `--format`), no aliases. |
| Machine Schema | All items in §3: tree, flags with types/defaults/enums/cardinality, units, machine + isolation profiles, stdin, read-only flag, auth/env/config/cache, output classes, shape dialect, exit + symbolic codes, per-command catalogs, side effects, latency, timeouts/retries, pagination/artifact, version + fingerprint + compatibility policy; `schema <command>` for one command. |
| Stdin Contract | Declared per command; only `note create --body-file -` and `auth login --token-stdin` read stdin, explicitly. |
| Shell Safety | `--` supported and declared; examples quote values and put options before `--`; values never reach a shell; hints carry no shell strings. |
| Agent-Safe Invocation | `--machine` profile; `--isolated` separate and still works with `NOTECTL_TOKEN`; per-stream TTY detection; non-interactive login bootstrap; metadata paths offline <100 ms; `--timeout-ms` on every networked command. |
| Output | stdout payload only; `single-error-object` stderr; declared classes (list, record, artifact); pagination with cursor contract; deterministic sort; `--select` projection; UTC timestamps; `--output` only on export, returns path/size/hash. |
| Errors And Exit Codes | Codes 0–10 declared; required `code`/`message`/`temporary`; `INTERNAL` fallback; `NETWORK_UNREACHABLE` transport code; unknown-code policy; `--debug` opt-in and redacted, refused in machine mode. |
| Ambient State | Credential/config/env/cache sources, precedence, `--isolated`/`--no-config`, `auth whoami`, `auth status`, `config show --resolved`; no secrets in argv. |
| Mutations And Long-Running Work | `create`/`delete` explicit verbs with `--dry-run`; idempotency key on create, `--if-exists` on delete; reconciliation and signal semantics declared; export is a foreground command with deadline, atomic write, last-writer-wins. |
| Side Effects And Telemetry | Reads have no writes except export's declared file; no telemetry or update checks. |
| Prose Surfaces | Summaries in §2 lead with constraints and separate siblings (`list` vs `search`, `get` vs `search`). |
| Tests | Ship: schema snapshot + fingerprint; each success payload above; each error payload + exit code checked against observed exits; TTY vs non-TTY and `--machine` suppression; stdin (piped, empty, TTY refusal); pagination + `CURSOR_EXPIRED`; export artifact hash/size and atomicity under interrupt; env > config precedence and `--isolated`; dry-run for create/delete; interrupt of create/delete; concurrent exports and cache writes. |
| Not applicable | Async jobs (no operation outlives the process: no job IDs, `wait`, or cancel). Streaming/NDJSON stdout and bulk-result (no multi-item command; export writes NDJSON to a file, not stdout). Partial-failure codes and `--allow-partial` (no multi-item mutation). Deprecations (v1.0, none yet). |
