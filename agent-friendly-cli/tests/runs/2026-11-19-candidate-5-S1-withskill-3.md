# 2026-11-19 candidate 5, scenario S1 control, with-skill arm 3

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o17

## Scorer verdicts

## o17

Scored:
- A1 Machine profile: PASS — `"canonical_machine_profile": ["--machine"]`; `--machine` and its implied `--json`, `--no-progress`, `--no-input` all in `global_flags`.
- A2 Exit + symbolic codes + mutating catalog: PASS — `"exit_codes": {...}`, `"symbolic_error_codes": [...]`, delete `"errors_possible": [...]`.
- A3 stdout/stderr: PASS — `"stderr_framing": "single-error-object"`; "Example error payloads (stderr only, stdout empty)".
- A4 delete trigger + dry-run: PASS — explicit `notectl note delete <id>` verb; `"--dry-run": {... "shape": {"dry_run": true, ...}}`.
- A5 pagination: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6 export pointer: PASS — `"byte_size": "integer", "content_hash": "string (sha256:<hex>)"`.
- A7 duration units: PASS — `{"name": "--timeout-ms", "type": "integer", "unit": "ms", ...}`.
- A8 ambient state: PASS — `"inspect_with": ["notectl auth whoami", "notectl config show --resolved"]`, `"disable_with": {"all": "--isolated", ...}`.
- A9 `--` placement: PASS — `notectl note get --machine -- 'nt_01H8X'`, `notectl note delete --if-exists --machine -- 'nt_01H8X'`.
- A10: PASS
  - (a) unanticipated failure: PASS — `"fallback_error_code": "INTERNAL"`.
  - (b) transport error per networked command: PASS — `TRANSPORT_ERROR` exit 9 in list/get/search/create/delete/export and `auth whoami`.
  - (c) unknown code policy: PASS — `"unknown_code_policy": "act on payload fields (temporary, reconcile_first); ..."`.
- A11 multi-value flags: PASS — `"--tag", ... "cardinality": "many", "multi_value_syntax": "repeat"`.

Conformance:
- C1 export only `--output`: PASS — only export has `{"name": "--output", ...}`.
- C2 output class per command: PASS — every command incl. schema/whoami/config has `"output": {"class": ...}`; `"alternate_outputs": {"--dry-run": {"class": "record", ...}}`.

## Output

# `notectl` agent-facing CLI contract

## 1. Task model

| Job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at` + paging |
| Get a note | inspect | `id` | full note |
| Search notes | query | `--query` | `id`, `title`, `tags`, `score` + paging |
| Create a note | mutate | `--title`, body (flag, file, or stdin), `--tag` | full note incl. new `id` |
| Delete a note | mutate | `id` | `id`, `status` |
| Export all notes | query (writes local file) | `--output` | `path`, `byte_size`, `content_hash`, `note_count` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

`list` vs `search` separate by one rule: `list` enumerates with exact filters in deterministic order; `search` ranks by relevance to free text.

## 2. Command surface

Pattern `notectl <noun> <verb>`; the primary selector for a note is its `id` (positional).
All commands support `--` end-of-options.

```
notectl schema [<command>] [--fingerprint] [--summary]
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--timeout-ms <ms>]
notectl note get    <id> [--select <field>]... [--timeout-ms <ms>]
notectl note search --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--timeout-ms <ms>]
notectl note create --title <text> (--body <text> | --body-file <path> | --body-file -) [--tag <tag>]... [--idempotency-key <key>] [--dry-run] [--timeout-ms <ms>]
notectl note delete <id> [--if-exists] [--dry-run] [--timeout-ms <ms>]
notectl note export --output <path> [--format ndjson|json] [--overwrite] [--timeout-ms <ms>]
notectl auth whoami
notectl config show --resolved
```

Global flags: `--machine` (implies `--json --no-progress --no-input`), `--json`, `--no-progress`, `--no-input`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`.

Canonical examples:

```sh
notectl note list --tag 'work' --limit 50 --machine
notectl note get --machine -- 'nt_01H8X'
notectl note search --query 'quarterly plan' --machine
printf '%s' "$BODY" | notectl note create --title 'Standup 2026-11-19' --tag 'meetings' --body-file - --idempotency-key 'a1f3c9e0-standup' --machine
notectl note delete --if-exists --machine -- 'nt_01H8X'
notectl note export --output 'notes.ndjson' --machine
```

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7f3e91a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this schema excluding fingerprint; tool version is not an input",
  "compatibility": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes on a command"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "output class changes"],
    "rule": "every contract change changes the fingerprint; breaking changes bump the major schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input"], "description": "Machine mode: structured output only, never prompts, no color, pager, spinner, or browser launch, on every stream."},
    {"name": "--json", "type": "boolean", "default": false, "description": "JSON success output on stdout."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the token cache; credentials come only from NOTECTL_TOKEN. Network reads still work."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to read; overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "API base URL; overrides NOTECTL_API_URL and config."}
  ],
  "exit_codes": {
    "0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found",
    "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout",
    "8": "conflict", "9": "transient, including transport failures other than timeout",
    "10": "export partially written (domain-specific)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "TRANSPORT_ERROR", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED", "EXPORT_INCOMPLETE"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, reconcile_first); on a mutating command reconcile before retrying",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string (RFC 3339, UTC)", "updated_at": "string (RFC 3339, UTC)"},
  "output_conventions": {"encoding": "UTF-8", "timestamps": "RFC 3339 UTC", "numbers": "locale-independent", "paths": "as given by caller, POSIX separators", "closed_stdout": "read commands exit quietly; mutating commands finish the in-flight request"},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env var", "token cache ~/.cache/notectl/token.json (written by `notectl auth login --token-stdin`)"], "secret": true, "redaction": "shown only as source name and last 4 characters", "argv_secrets_accepted": false},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NO_COLOR"],
    "caches": [{"path": "~/.cache/notectl/token.json", "reads": true, "writes": "only by auth login; atomic rename"}],
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file > token cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl auth whoami", "notectl config show --resolved"],
    "non_interactive_bootstrap": "export NOTECTL_TOKEN, or pipe a token to `notectl auth login --token-stdin`; no browser flow in machine mode"
  },
  "side_effects_policy": {"telemetry": "none", "update_checks": "none", "reads_write_nothing": true},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes with exact tag filters, newest-updated first. Use search for free-text relevance.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "[note projection]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "sort": "updated_at desc, then id asc", "size_mode": "paged; body excluded by default"},
      "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"], "backoff": "exponential, honors retry_after_ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Fetch one note by id, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["nt_01H8X"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"}, "size_mode": "small; body up to 1 MiB, never truncated"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Rank notes by full-text relevance to --query over title and body. Use list for exact tag enumeration.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "restrict to notes carrying all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body", "snippet", "score"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "snippet", "score"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "[{id, title, tags, snippet, score} projection]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"}, "sort": "score desc, then id asc", "size_mode": "paged; snippet capped at 200 characters"},
      "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort; index is eventually consistent with writes"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "pagination": true, "truncation": "snippet only, declared", "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file -",
      "summary": "Create one note. Not repeat-safe unless --idempotency-key is supplied on the first attempt.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "'-' reads the body from stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "description": "server deduplicates on this key for 24 hours"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": "only with --body-file -", "auto_detected_when_piped": false, "accepted_formats": ["UTF-8 text"], "maximum_input_size": "1 MiB", "can_block": "only with --body-file -; reads to EOF", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "note": "{title, body_bytes: integer, tags}"}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth server-side; no externally visible mutation; output carries dry_run: true"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0, "description": "no automatic retry; with --idempotency-key the caller may retry with the same key"},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24 hours. Without a key, retry is not safe automatically; a list or search lookup that finds nothing does not prove the create did not commit.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "closed_stdout": "finishes the in-flight request", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "same key reused with different inputs"},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by id. Repeat-safe with --if-exists.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["nt_01H8X"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "planned_action is none when --if-exists would suppress NOTE_NOT_FOUND", "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence and permission; no mutation"},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, or interrupt the outcome is unknown; the declared recovery is re-running with --if-exists, which is repeat-safe",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "closed_stdout": "finishes the in-flight request", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write every note to a local file and return a pointer to it. Fails if the file exists unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": "remote read-only; writes one local file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "file format: one note per line, or one JSON array"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "total deadline for the whole export"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "format": "ndjson|json", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "note_count": "integer", "exported_at": "string (RFC 3339, UTC)"}, "size_mode": "pointer only; file size unbounded"},
      "progress": {"stream": "stderr", "suppressed_by": "--no-progress", "machine_mode": "suppressed"},
      "side_effects": {"external_mutation": false, "writes": ["--output path"], "description": "writes to <path>.partial then renames atomically; no file at <path> on failure"},
      "latency_class": "slow", "timeout_defaults_ms": 300000, "retry_defaults": {"retries": 2, "per_page": true, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "consistency": "best-effort page walk; notes changed during export may be missed or duplicated by id",
      "signal_semantics": {"interrupt": "removes <path>.partial; <path> untouched", "local_writes": "atomic rename", "remote_continues": false},
      "async": false, "streaming": false, "pagination": "internal", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "EXPORT_INCOMPLETE", "exit": 10, "retryable": true, "description": "page fetch failed after retries; no file written"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 1, "description": "local filesystem error"}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>] [--fingerprint] [--summary]",
      "summary": "Print the contract, one command's contract, a fingerprint, or a one-screen index. No network, no auth.",
      "classification": "discover", "read_only": true, "latency_class": "local", "output": {"class": "record", "format": "json"},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Show the authenticated account and credential source (token redacted).",
      "classification": "admin", "read_only": true, "latency_class": "network",
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "credential_source": "env:NOTECTL_TOKEN|cache", "token_suffix": "string"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show each resolved setting with its source. No network.",
      "classification": "admin", "read_only": true, "latency_class": "local",
      "output": {"class": "record", "format": "json", "shape": {"settings": "[{name, value, source: flag|env|config|default, secret: boolean}]"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

`notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit `0`)

`notectl note list --tag 'work' --limit 2 --machine`

```json
{"items":[{"id":"nt_01H8X","title":"Q4 plan","tags":["work","planning"],"updated_at":"2026-11-18T21:04:11Z"},{"id":"nt_01H7Q","title":"Vendor call","tags":["work"],"updated_at":"2026-11-17T15:30:00Z"}],"has_more":true,"next_cursor":"c_9aZk","limit":2,"estimated_total":37}
```

`notectl note get --machine -- 'nt_01H8X'`

```json
{"id":"nt_01H8X","title":"Q4 plan","body":"Ship v2 by Dec 15.\nHire one SRE.","tags":["work","planning"],"created_at":"2026-10-02T09:12:00Z","updated_at":"2026-11-18T21:04:11Z"}
```

`notectl note search --query 'quarterly plan' --limit 1 --machine`

```json
{"items":[{"id":"nt_01H8X","title":"Q4 plan","tags":["work","planning"],"snippet":"…the quarterly plan: ship v2 by Dec 15…","score":0.91}],"has_more":false,"limit":1}
```

`... | notectl note create --title 'Standup 2026-11-19' --tag 'meetings' --body-file - --idempotency-key 'a1f3c9e0-standup' --machine`

```json
{"id":"nt_01HA2","title":"Standup 2026-11-19","body":"Blocked on review.","tags":["meetings"],"created_at":"2026-11-19T16:00:02Z","updated_at":"2026-11-19T16:00:02Z"}
```

Same command with `--dry-run`:

```json
{"dry_run":true,"planned_action":"create","note":{"title":"Standup 2026-11-19","body_bytes":17,"tags":["meetings"]}}
```

`notectl note delete --machine -- 'nt_01H7Q'`

```json
{"id":"nt_01H7Q","status":"deleted"}
```

`notectl note delete --if-exists --machine -- 'nt_01H7Q'` (already gone)

```json
{"id":"nt_01H7Q","status":"absent"}
```

`notectl note export --output 'notes.ndjson' --machine`

```json
{"path":"notes.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:3b7f0c2e9a41d58e6f0a1c2b3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60","note_count":37,"exported_at":"2026-11-19T16:05:44Z"}
```

## 5. Example error payloads (stderr only, stdout empty)

Not found — `notectl note get --machine -- 'nt_404'`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"nt_404","temporary":false,"request_id":"req_5f2a"}
```

Validation — `notectl note create --title 'x' --tag 'Bad Tag' --body 'y' --machine`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag.","field":"--tag","details":{"value":"Bad Tag","pattern":"^[a-z0-9][a-z0-9_-]{0,63}$"},"hint":"Use lowercase letters, digits, '-' or '_'; keep the other flags unchanged.","temporary":false}
```

Rate limited — any networked command, exit `6`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_77c1"}
```

Unknown outcome — `notectl note create ... --machine` timed out, exit `7`:

```json
{"code":"TIMEOUT","message":"Request timed out after 10000 ms; the note may have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key":"a1f3c9e0-standup"},"hint":"Re-run with the same --idempotency-key value.","request_id":"req_9e03"}
```

Unauthenticated — exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credentials.","details":{"checked_sources":["env:NOTECTL_TOKEN","cache"]},"hint":"Set NOTECTL_TOKEN or pipe a token to auth login --token-stdin.","temporary":false}
```

Export target exists — exit `8`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"notes.ndjson","hint":"Pass --overwrite or choose a different --output value.","temporary":false}
```

## 6. Checklist coverage

| Section | Answer |
|---|---|
| Command Model | `notectl note <verb>`, positional `id` only for get/delete, conventional flags |
| Machine Schema | §3: profile, isolation, dialect, catalogs, latency, fingerprint, compatibility, per-command `schema <command>` |
| Stdin Contract | declared per command; only `create --body-file -` reads stdin, never auto-detected |
| Shell Safety | `--` supported; values never reach a shell; hints carry flag values, not command strings |
| Agent-Safe Invocation | `--machine` profile, per-stream non-TTY rules, `--isolated` still allows authenticated reads via env token, sub-100ms `schema`, `--timeout-ms` everywhere networked |
| Output | stdout success only; `single-error-object` stderr; deterministic sorts; pagination + cursor contract; `--select` projection; export is the only `--output` |
| Errors And Exit Codes | tool-level map, per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`, `INTERNAL` fallback, `TRANSPORT_ERROR`, unknown-code policy |
| Partial failure | N/A for bulk output (no multi-item mutation); export is all-or-nothing (`EXPORT_INCOMPLETE`, no file) |
| Ambient State | sources, precedence, `whoami`, `config show --resolved`, redaction, no argv secrets |
| Mutations | explicit verbs, `--dry-run`, `--if-exists`, `--idempotency-key`, reconciliation and signal semantics declared |
| Async | N/A: no operation outlives the process; export is a foreground command with a declared deadline, progress framing, and interrupt behavior |
| Side Effects/Telemetry | none on reads; no telemetry or update checks |
| Prose Surfaces | summaries lead with the binding rule and distinguish list vs search |
| Tests | schema snapshot; every payload above as golden output; exit-code mapping; TTY vs non-TTY and `--machine`; empty stdin on `create --body-file -`; pagination and `CURSOR_EXPIRED`; export atomicity and interrupt cleanup; env/config precedence and `--isolated`; dry-run non-mutation; create/delete interrupt; concurrent `auth login` cache writes |
