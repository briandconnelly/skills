# 2026-11-19 candidate 5, scenario S1-rerun control, with-skill arm 2

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o25

## Scorer verdicts

## Output o25

Scored:

- A1 machine profile: PASS — `"canonical_machine_profile": ["--machine"]`; `{"name": "--machine", "type": "boolean", ...}` in `global_flags`.
- A2 exit + symbolic codes + mutating catalog: PASS — `"exit_codes": {"0": "success", ...}`, `"symbolic_error_codes": [...]`, delete `"errors_possible": [{"code": "INTERNAL", "exit": 1, ...`.
- A3 stdout/stderr: PASS — `"stderr_framing": "single-error-object"`; checklist "stdout payload only".
- A4 delete trigger + dry-run: PASS — explicit `notectl note delete <id>` verb; `"--dry-run": {... "shape": {"dry_run": true, "id": "string", ...`.
- A5 pagination: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6 export pointer: PASS — `{"path": "string", "byte_size": "integer", "content_hash": "string", ...}`.
- A7 duration units: PASS — `{"name": "--timeout-ms", "type": "integer", "unit": "ms", ...}`.
- A8 ambient state: PASS — `"ambient_state": {... "disable_with": {"all": "--isolated", ...}, "inspect_with": ["notectl auth whoami", ...`.
- A9 `--` placement: PASS — `notectl note delete --if-exists --machine -- 'note_8f2a'`; `notectl note get -- '-weird-id'`.
- A10 errors (per component): PASS
  - (a) unanticipated failure: PASS — `"fallback_error_code": "INTERNAL"`.
  - (b) transport failure in every networked catalog: PASS — `{"code": "TRANSPORT_ERROR", "exit": 9, ...}` in list/get/search/create/delete/export/whoami. (`auth login` appears only in `command_tree` with no entry and is not declared networked.)
  - (c) unlisted-code policy: PASS — `"unknown_code_policy": "act on payload fields (temporary, reconcile_first); ..."`.
- A11 multi-value flags: PASS — `"--tag", ... "cardinality": "many", "multi_value_syntax": "repeat"`.

Conformance (non-scored):

- C1 export only `--output`: PASS — `--output` appears only in `note export`.
- C2 one output class per command + switch declared: PASS — every command entry has `"class"`; `"alternate_outputs": {"--dry-run": {"class": "record", ...`.

## Output

# `notectl` — Agent-Facing CLI Contract

Audience: tool author designing a new CLI.
Task: new design, so this follows the design workflow and closes with a checklist walk.

## 1. Task Model

| Job | Class | Minimum input | Minimum output for the next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at`; paging token |
| Get a note | inspect | `id` | full note |
| Search notes | query | `--query` text | `id`, `title`, `tags`, `snippet`, `score`; paging token |
| Create a note | mutate | `--title`; body from flag or file/stdin; tags | created note `id` + fields |
| Delete a note | mutate | `id` | `id` + `status` (`deleted`/`absent`) |
| Export all notes | mutate (local file write only) | `--output <file>` | `path`, `byte_size`, `content_hash`, `note_count` |
| Discover the contract | discover | optional command name | schema / fingerprint |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

`search` and `list` stay separate verbs: `list` enumerates with exact filters and a deterministic order; `search` ranks by full-text relevance and returns a `score` and `snippet`.
A one-line summary distinguishes them, so they pass the sibling-pair test.

## 2. Command Surface

Pattern: `notectl <noun> <verb>`; primary selector for notes is the note `id` (positional, the only positional on any command).

```text
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <token>] [--sort updated_at|created_at|title] [--select <field>]...
notectl note get     <id> [--select <field>]...
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]...
notectl note create  --title <text> (--body <text> | --body-file <path|->) [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete  <id> [--if-exists] [--dry-run]
notectl note export  --output <path> [--format json|ndjson] [--overwrite] [--dry-run]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth sources
notectl config show --resolved
```

Global flags: `--machine`, `--json`, `--no-progress`, `--no-color`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`, `--debug`.
All commands accept `--` end-of-options; operands after it are data (e.g. `notectl note get -- '-weird-id'`).

Canonical examples (values quoted; options always precede `--`):

```sh
notectl note list --tag 'work' --limit 50 --machine
notectl note get 'note_8f2a' --machine
notectl note search --query 'quarterly plan' --limit 10 --machine
printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --body-file - --tag 'work' --idempotency-key 'a1c9e4' --machine
notectl note delete --if-exists --machine -- 'note_8f2a'
notectl note export --output './notes-export.ndjson' --format ndjson --machine
```

Prose summaries (rules first, then context):

- `note list` — Enumerate notes, exact tag filter, deterministic order, paginated. Use `search` for relevance-ranked text matching.
- `note get` — Fetch one note by `id`, including body. Fails `NOTE_NOT_FOUND` (exit 3) if absent.
- `note search` — Full-text, relevance-ranked match over title and body; requires `--query`. Returns snippets, not bodies; call `get` for the body.
- `note create` — Create one note. Remote mutation. Pass `--idempotency-key` to make retries safe. Body comes from `--body` or `--body-file` (`-` = stdin); stdin is never read otherwise.
- `note delete` — Delete one note by `id`. Remote mutation. Repeat-safe with `--if-exists`.
- `note export` — Write every note to a local file; stdout gets only path, size, hash, count. Remote read-only; refuses to replace an existing file without `--overwrite`.

## 3. Machine Schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum; trailing `?` marks an optional field; fields are required unless so marked or removed by a declared projection; `[T]` is an array of T; a string-valued shape describes an NDJSON record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7d41e09b",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this document excluding fingerprint; tool version is not an input",
  "compatibility": {
    "additive": ["new command", "new optional flag", "new optional output field", "new symbolic error code in a catalog"],
    "breaking": ["command or flag removal or rename", "type or meaning change", "exit-code remapping", "required output field removal"],
    "rule": "every contract change changes fingerprint; breaking changes bump the major schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b closed enum; trailing ? optional; fields required unless marked or removed by a declared projection; [T] array; string-valued shape = NDJSON record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode stderr is empty on success and holds exactly one JSON error object on failure; progress is suppressed",
  "encoding": "utf-8",
  "timestamps": "RFC 3339, UTC, Z suffix",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Non-interactive: no prompts, pager, browser, color, or progress; structured output only on every stream regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "JSON output on stdout and JSON errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Suppress ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the schema cache; credentials come only from NOTECTL_TOKEN; --api-url required if not default."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "Remote API base URL."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": null, "description": "Overrides the per-command network timeout default."},
    {"name": "--debug", "type": "boolean", "default": false, "description": "Opt-in redacted request/response diagnostics on stderr; ignored in machine mode unless also --json, in which case diagnostics go to error.details.debug only."}
  ],
  "auth": {
    "required_for": ["note list", "note get", "note search", "note create", "note delete", "note export", "auth whoami"],
    "not_required_for": ["schema", "auth sources", "config show"],
    "scopes": {"read": ["note list", "note get", "note search", "note export"], "write": ["note create", "note delete"]},
    "non_interactive_bootstrap": "set NOTECTL_TOKEN, or `notectl auth login --token-stdin < token.txt`; interactive browser login is never started in machine mode"
  },
  "ambient_state": {
    "credentials": ["NOTECTL_TOKEN env var", "OS keychain entry notectl/<profile>", "~/.config/notectl/credentials (0600)"],
    "config_files": ["~/.config/notectl/config.toml", "$NOTECTL_CONFIG"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "NO_COLOR"],
    "caches": [{"path": "~/.cache/notectl/schema.json", "purpose": "remote API capability cache", "reads": true, "writes": "atomic rename; last-writer-wins"}],
    "cwd_selects_context": false,
    "precedence": "flags > environment > config file > cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl auth whoami", "notectl auth sources", "notectl config show --resolved"],
    "secret_values": ["token"],
    "redaction": "tokens render as \"<redacted:sha256-prefix>\" in every output, debug dump, and error",
    "secret_intake": "env, keychain, credentials file, or --token-stdin; no flag accepts a token value"
  },
  "telemetry": {"default": "off", "update_checks": "off", "machine_mode": "always suppressed"},
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, including transport failure", "10": "output file exists (domain-specific)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "TRANSPORT_ERROR", "UPSTREAM_UNAVAILABLE", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, reconcile_first); on a mutating command reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "timestamp", "updated_at": "timestamp"},
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "sources": "notectl auth sources", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"},
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> (--body <text> | --body-file <path|->)",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    }
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "Enumerate notes with exact tag filters in deterministic order; paginated. Use note search for relevance-ranked text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "description": "Match notes carrying all given tags."},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "Descending for timestamps, ascending for title; ties broken by id ascending."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "size_mode": "paged",
        "shape": {"items": "[{id, title, tags, updated_at}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "next_cursor is present iff has_more is true; body is never included, use note get",
        "projection": {"flag": "--select", "rule": "only selected fields are present in each item; unselected fields are absent, not null; id is always present"},
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR", "UPSTREAM_UNAVAILABLE"], "backoff": "exponential from 250ms, honors retry_after_ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": "only via pagination", "artifact": false,
      "signal_semantics": {"interrupt": "exits 130, no output", "closed_stdout": "exits quietly", "local_writes": "none"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "description": "Fetch one note by id, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]+$", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "small (body up to 1 MiB)", "shape": "note_shape",
        "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent; id always present"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR", "UPSTREAM_UNAVAILABLE"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "signal_semantics": {"interrupt": "exits 130, no output", "closed_stdout": "exits quietly", "local_writes": "none"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "description": "Full-text relevance-ranked match over title and body; requires --query. Returns snippets, not bodies.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "snippet", "score"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "snippet", "score"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "size_mode": "paged",
        "shape": {"items": "[{id, title, tags, snippet, score}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "sorted by score descending, ties by id ascending; snippet is at most 200 characters; score is a float in [0,1]",
        "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent; id always present"},
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR", "UPSTREAM_UNAVAILABLE"]},
      "async": false, "streaming": false, "pagination": true, "truncation": "only via pagination", "artifact": false,
      "signal_semantics": {"interrupt": "exits 130, no output", "closed_stdout": "exits quietly", "local_writes": "none"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file -",
      "description": "Create one note (remote mutation). Pass --idempotency-key on the first attempt to make retries safe. Body from --body or --body-file; stdin is read only when --body-file is '-'.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "'-' reads the body from stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "max_count": 20, "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 64, "description": "Server dedupes identical keys for 24 hours; the same key with different inputs fails IDEMPOTENCY_CONFLICT."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "requires_one_of": [["--body", "--body-file"]],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--body-file -", "accepted_formats": ["UTF-8 text"], "maximum_input_size": "1 MiB", "can_block": "only with --body-file -; the caller must close stdin", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as an empty body"},
      "output": {"class": "record", "format": "json", "size_mode": "small", "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "timestamp", "updated_at": "timestamp", "replayed": "boolean"},
        "shape_description": "body is not echoed; replayed is true when the idempotency key matched an earlier committed create, in which case the original note is returned"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates locally and against the server's validate endpoint; no note is created; may refresh the schema cache unless --isolated"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "description": "notectl never retries create on its own"},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, UPSTREAM_UNAVAILABLE, or interrupt the outcome is unknown. Safe retry: re-run with the SAME --idempotency-key supplied on the original attempt within 24 hours (returns the original note with replayed: true if it committed). Without a key from the original attempt, the create is NOT safe to retry automatically; an empty search/list does not prove it did not commit.",
      "signal_semantics": {"interrupt": "remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Delete one note by id (remote mutation). Repeat-safe with --if-exists.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]+$", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "Exit 0 with status absent instead of NOTE_NOT_FOUND."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "small", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "absent only when --if-exists suppressed NOTE_NOT_FOUND"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "id": "string", "planned_action": "delete|none"}, "shape_description": "none when --if-exists would suppress NOTE_NOT_FOUND; without --if-exists a missing note fails NOTE_NOT_FOUND"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm it exists; no deletion"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, UPSTREAM_UNAVAILABLE, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists",
      "signal_semantics": {"interrupt": "remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "description": "Write every note to a local file; stdout gets only path, byte size, hash, and count. Remote read-only. Refuses to replace an existing file unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false, "remote_read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "'-' is not accepted; export always writes a file."},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "File format: ndjson = one note_shape per line; json = {notes: [note_shape], exported_at}."},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "Overall deadline for the whole export."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "size_mode": "small pointer; file grows with note count",
        "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "json|ndjson", "consistency": "best-effort"},
        "shape_description": "path is absolute, POSIX style; content_hash is sha256:<hex>; file notes are sorted by id ascending"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "write|overwrite", "path": "string", "estimated_note_count?": "integer"}}
      },
      "side_effects": {"external_mutation": false, "writes": ["--output file (local)"], "dry_run": "checks auth, path writability, and existing-file policy; writes nothing"},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "retry_defaults": {"retries": 2, "scope": "per page fetch", "on": ["RATE_LIMITED", "TRANSPORT_ERROR", "UPSTREAM_UNAVAILABLE"]},
      "progress": "suppressed in machine mode; human mode prints a page counter on stderr when stderr is a TTY",
      "reconciliation": "safe to retry: remote state is not modified and the file is written atomically; re-run with --overwrite if a prior run completed",
      "signal_semantics": {"interrupt": "temp file removed; target path untouched", "closed_stdout": "finishes the write", "local_writes": "atomic: write to <path>.notectl-tmp-<pid> then rename", "remote_continues": false, "concurrency": "two exports to the same path: last rename wins; each file is internally consistent"},
      "async": false, "streaming": false, "pagination": "internal; walks all pages", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "UPSTREAM_UNAVAILABLE", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>] [--fingerprint] [--summary]",
      "description": "Print this contract, one command's contract, a fingerprint, or a one-screen command index. No network, no auth.",
      "classification": "discover", "read_only": true, "latency_class": "local", "target_latency_ms": 100,
      "output": {"class": "record", "format": "json"},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown command name"}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "description": "Show the authenticated account and token scopes.",
      "classification": "admin", "read_only": true, "latency_class": "network", "timeout_defaults_ms": 5000,
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "[read|write]", "api_url": "string", "profile": "string"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl auth sources",
      "description": "Show which credential source would be used and which were found. No network; token values are redacted.",
      "classification": "admin", "read_only": true, "latency_class": "local",
      "output": {"class": "record", "format": "json", "shape": {"selected": "env|keychain|credentials_file|none", "found": "[{source, present, token_fingerprint?}]"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "description": "Show resolved config values with the source of each (flag, env, config, default). No network.",
      "classification": "admin", "read_only": true, "latency_class": "local",
      "output": {"class": "record", "format": "json", "shape": {"values": "{<key>: {value, source: flag|env|config|default}}", "config_files_read": "[string]"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "malformed config file"}]
    }
  ]
}
```

`notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7d41e09b", "fingerprint_scope": "schema-contract"}
```

`notectl schema 'note delete' --machine` returns that command's object from `commands` plus the tool-level `exit_codes`, `error_shape`, and `shape_dialect`.

## 4. Example Success Payloads (stdout, exit 0)

`notectl note list --tag 'work' --limit 2 --machine`

```json
{"items":[{"id":"note_8f2a","title":"Standup 2026-11-19","tags":["work"],"updated_at":"2026-11-19T15:02:11Z"},{"id":"note_7c10","title":"Quarterly plan","tags":["planning","work"],"updated_at":"2026-11-18T09:40:00Z"}],"has_more":true,"next_cursor":"c3Rk...Q2","limit":2,"estimated_total":37}
```

`notectl note get 'note_8f2a' --machine`

```json
{"id":"note_8f2a","title":"Standup 2026-11-19","body":"- shipped export\n- blocked on review","tags":["work"],"created_at":"2026-11-19T15:01:58Z","updated_at":"2026-11-19T15:02:11Z"}
```

`notectl note search --query 'quarterly plan' --limit 1 --machine`

```json
{"items":[{"id":"note_7c10","title":"Quarterly plan","tags":["planning","work"],"snippet":"…Q1 goals for the **quarterly plan** include…","score":0.91}],"has_more":false,"limit":1}
```

`printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --body-file - --tag 'work' --idempotency-key 'a1c9e4' --machine`

```json
{"id":"note_8f2a","title":"Standup 2026-11-19","tags":["work"],"created_at":"2026-11-19T15:01:58Z","updated_at":"2026-11-19T15:01:58Z","replayed":false}
```

`notectl note create --title 'Draft' --body 'x' --dry-run --machine`

```json
{"dry_run":true,"planned_action":"create","title":"Draft","tags":[],"body_bytes":1}
```

`notectl note delete --machine -- 'note_8f2a'`

```json
{"id":"note_8f2a","status":"deleted"}
```

`notectl note delete --if-exists --machine -- 'note_0000'`

```json
{"id":"note_0000","status":"absent"}
```

`notectl note export --output './notes-export.ndjson' --machine`

```json
{"path":"/home/agent/work/notes-export.ndjson","byte_size":48213,"content_hash":"sha256:9b74c9897bac770ffc029102a200c5de9b74c9897bac770ffc029102a200c5de","note_count":37,"format":"ndjson","consistency":"best-effort"}
```

## 5. Example Error Payloads (stderr, empty stdout)

In machine mode each object is the only stderr content.

Not found — `notectl note get 'note_404' --machine`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404","hint":"Check the id with notectl note list or notectl note search, or pass --if-exists on delete.","temporary":false,"request_id":"req_01HZX4"}
```

Validation — `notectl note create --title 'X' --body 'y' --tag 'Bad Tag!' --machine`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag value.","field":"--tag","details":{"value_index":0,"pattern":"^[a-z0-9][a-z0-9_-]{0,31}$","max_count":20},"hint":"Use lowercase letters, digits, '-' or '_', up to 32 characters; keep your other flags unchanged.","temporary":false}
```

Rate limited — `notectl note search --query 'plan' --machine` after built-in retries are exhausted, exit `6`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"details":{"retries_attempted":2},"temporary":true,"request_id":"req_01HZX9"}
```

Unknown outcome on a mutation — `notectl note create ... --idempotency-key 'a1c9e4' --machine` times out, exit `7`:

```json
{"code":"TIMEOUT","message":"Request timed out; the note may or may not have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key_supplied":true},"hint":"Re-run with the same --idempotency-key value 'a1c9e4' within 24 hours; the original note is returned with replayed: true if it committed.","request_id":"req_01HZXB"}
```

Unauthenticated — any networked command, exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credentials.","details":{"credential_source":"none","checked":["env","keychain","credentials_file"]},"hint":"Set NOTECTL_TOKEN or run notectl auth login --token-stdin; inspect with notectl auth sources.","temporary":false}
```

Export target exists — `notectl note export --output './notes-export.ndjson' --machine`, exit `10`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes-export.ndjson","hint":"Add --overwrite or choose a different --output path.","temporary":false}
```

## 6. Implementation and Tests

Result-then-render: typed inputs → typed result or typed error → separate human and machine renderers.
`schema`, `--help`, `auth sources`, and `config show` import no HTTP client and make no network calls (sub-100 ms target).

Ship automated tests for: schema snapshot and fingerprint stability; each success payload above; each error payload above with its exit code, plus a runtime check that every declared `exit` maps to the observed exit; TTY vs non-TTY per stream; `--machine` suppressing prompts, color, progress, and prose; `--body-file -` with empty and oversize stdin, and stdin ignored on every other command; pagination, `CURSOR_EXPIRED`, and `--select` projection; export artifact (hash matches file, atomic rename, `OUTPUT_EXISTS`); config/env/flag precedence and `--isolated`; dry-run for create, delete, and export (no mutation, `dry_run: true`); idempotency replay and `IDEMPOTENCY_CONFLICT`; SIGINT during create/delete/export; concurrent exports to one path; token redaction in all outputs.
Not applicable: deprecation tests (none in 1.0) and async cancellation (no async commands).

## 7. Checklist Walk

| Section | Answer |
|---|---|
| Command Model | `notectl note <verb>`; one positional (`id`); conventional flags `--limit`, `--format`, `--timeout-ms`, `--output`; no aliases. |
| Machine Schema | All items declared in §3, including dialect, catalogs with `retryable`/`reconcile_first`, latency classes, fingerprint + scope + compatibility policy, per-command `schema <command>`. |
| Stdin Contract | Declared per command; only `create --body-file -` reads stdin, explicitly. |
| Shell Safety | `--` supported and declared; examples quoted, options before `--`; hints use flag values, no shell built from input. |
| Agent-Safe Invocation | `--machine` profile distinct from `--isolated`; per-stream non-TTY; non-interactive `auth login --token-stdin`; metadata paths offline; `--timeout-ms` everywhere networked. |
| Output | stdout payload only; `single-error-object` stderr; classes declared (`list`, `record`, `artifact`); pagination with cursor contract; deterministic sort; projection rule; `--output` only on export with path/size/hash. |
| Errors And Exit Codes | Exit map 0–10; symbolic codes; `INTERNAL` fallback; `TRANSPORT_ERROR` in every network catalog; unknown-code policy; secrets redacted. Partial failure: not applicable — no multi-item mutation commands; export fails as a whole. |
| Ambient State | Credentials, config, env, cache, precedence, `--isolated`/`--no-config`, `whoami`/`auth sources`/`config show --resolved`, no token flags. |
| Mutations | `create`/`delete` explicit verbs with `--dry-run`; idempotency key for create, `--if-exists` for delete; unknown-outcome recovery and signal semantics declared; export writes atomically. Async jobs: not applicable — export is a foreground command with a declared deadline. |
| Side Effects And Telemetry | Reads have no writes except the declared schema cache (disabled by `--isolated`); telemetry and update checks off. |
| Prose Surfaces | Summaries in §2 and schema `description` lead with constraints and separate `list` from `search`. |
| Tests | §6. |
