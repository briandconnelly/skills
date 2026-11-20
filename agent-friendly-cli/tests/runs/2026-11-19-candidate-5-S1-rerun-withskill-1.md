# 2026-11-19 candidate 5, scenario S1-rerun control, with-skill arm 1

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o50

## Scorer verdicts

## Output o50

Scored:

- A1: PASS — `"canonical_machine_profile": ["--machine"]`; `{"name": "--machine", "type": "boolean", ... "implies": [..., "--no-input"]}` and `--no-input` declared.
- A2: PASS — `"exit_codes"`, `"symbolic_error_codes"`, delete `"errors_possible": [{"code": "INTERNAL", "exit": 1}, ...`.
- A3: PASS — `"stderr_framing": "single-error-object"`; "Machine mode: stdout empty, the object below is the only stderr content."
- A4: PASS — `notectl note delete <id>`; example `{"dry_run":true,"planned_action":"delete",...}`.
- A5: PASS — `"has_more": "boolean", "next_cursor?": "string"`.
- A6: PASS — `{"path": ..., "byte_size": "integer", "content_hash": "string (sha256:<hex>)", ...}`.
- A7: PASS — `{"name": "--timeout-ms", "type": "integer", "unit": "ms", ...}`.
- A8: PASS — `"ambient_state": {... "disable_with": {"all": "--isolated", ...}, "inspect_with": ["notectl whoami", ...`.
- A9: PASS — `notectl note get --machine -- 'n_-01HX'`.
- A10: FAIL
  - (a): PASS — `"fallback_error_code": "INTERNAL"`.
  - (b): FAIL — note commands carry `NETWORK_ERROR` via `common.network_read_errors` and create/delete lists, but `whoami` is declared networked ("`whoami` is `network`") and its entry is "elided here for length", so no error list with a transport failure is shown for it.
  - (c): PASS — `"unknown_code_policy": "act on payload fields ..."`.
- A11: PASS — `"--tag", ... "multi_value_syntax": "repeat"`.

Conformance (non-scored):

- C1: PASS — "`export` is the only command that accepts `--output`".
- C2: FAIL — metadata commands (`schema`, `whoami`, `config show`, `auth status`, `auth login`) "entries are elided here for length", so no output class is declared for them.

## Output

# `notectl` agent-facing CLI contract

Audience: tool author designing a new CLI.
Task: new design, so the contract below follows the design workflow and is walked against the contract checklist at the end.

## 1. Task model

| Job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | none (optional `--tag`, `--limit`, `--cursor`) | page of `{id,title,tags,updated_at}` + `has_more`/`next_cursor` |
| Get a note | inspect | `id` | full note record |
| Search notes | query | `--query` text | ranked page of `{id,title,tags,score,snippet}` |
| Create a note | mutate | `--title`, body (file or stdin), optional tags | created record with `id` |
| Delete a note | mutate | `id` | `{id,status}` |
| Export all notes | query (writes a local artifact) | `--output <path>` | `{path,byte_size,content_hash,note_count}` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

`list` vs `search`: `list` is an unranked, deterministic enumeration with exact filters; `search` is ranked full-text matching.
They differ in input (no query vs required query) and output (no score vs score), so they are separate verbs that need no prose to tell apart.

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for a note is its ID, given as the single positional argument.
`--` end-of-options is supported on every command.

```text
notectl note list    [--tag <tag>]... [--sort updated_at|created_at|title] [--select <field>]... [--limit <n>] [--cursor <c>] [--timeout-ms <ms>]
notectl note get     <id> [--select <field>]... [--timeout-ms <ms>]
notectl note search  --query <text> [--tag <tag>]... [--select <field>]... [--limit <n>] [--cursor <c>] [--timeout-ms <ms>]
notectl note create  --title <text> (--body-file <path> | --body-stdin) [--tag <tag>]... [--idempotency-key <key>] [--dry-run] [--timeout-ms <ms>]
notectl note delete  <id> [--if-exists] [--dry-run] [--timeout-ms <ms>]
notectl note export  --output <path> [--format ndjson|json] [--overwrite] [--timeout-ms <ms>]

notectl schema [<command>] [--fingerprint] [--summary]
notectl whoami [--timeout-ms <ms>]
notectl config show --resolved
notectl auth status
notectl auth login --token-stdin

Global: --machine (implies --json --no-progress --no-color --no-input), --json, --no-progress, --no-color, --no-input, --isolated, --no-config, --profile <name>, --api-url <url>
```

Notes on choices:

- Body is never a flag value, so long or multi-line bodies and shell metacharacters cannot break the command line; body comes from `--body-file` or explicitly requested stdin (`--body-stdin`), never auto-detected.
- `--tag` is a repeated flag (no delimiter), so a tag containing `,` is unambiguous.
- `export` is the only command that accepts `--output`, per the artifact rule.
- Secrets are never accepted as argv: the token comes from `NOTECTL_TOKEN`, the credential file, or `auth login --token-stdin`.
- Canonical examples quote values: `notectl note search --query 'release plan' --machine`, `notectl note get --machine -- 'n_-01HX'`.

## 3. Machine schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, and a string-valued shape describes a record sequence.
Commands share common blocks; each command entry lists only what it declares.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7f3a91c2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this schema excluding tool_version; version-only releases keep the fingerprint",
  "tool_version": "1.0.0",
  "compatibility": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes on a command (covered by unknown_code_policy)"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "required-field additions to input"],
    "rule": "every contract change changes the fingerprint; breaking changes also bump the major version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--no-input"], "description": "Machine mode: structured output only, never prompts, no pager, no browser launch, regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Structured JSON (or NDJSON where declared) on stdout."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress and spinners on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Suppress ANSI color on every stream."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a prompt that would be needed fails with VALIDATION_ERROR or UNAUTHENTICATED instead."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config file and token cache; credentials only from NOTECTL_TOKEN. Authenticated commands still work when NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore the config file only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL. Overrides NOTECTL_API_URL and config."}
  ],
  "non_tty_behavior": {
    "evaluated_per_stream": true,
    "stdout_not_tty": "no human tables, no pager",
    "stderr_not_tty": "no color, no progress",
    "stdin_not_tty": "no prompts"
  },
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env", "credential file ~/.config/notectl/credentials.json (mode 0600, per profile)"], "secret_values": ["token"], "redaction": "shown only as source plus last 4 characters, everywhere including debug output"},
    "config_files": ["$NOTECTL_CONFIG or ~/.config/notectl/config.toml"],
    "environment_variables": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG"],
    "caches": [{"name": "token-cache", "path": "~/.cache/notectl/", "contents": "none in 1.0; reserved"}],
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl whoami", "notectl config show --resolved", "notectl auth status"]
  },
  "non_interactive_bootstrap": "export NOTECTL_TOKEN, or pipe the token to `notectl auth login --token-stdin`",
  "telemetry": "none; no update checks",
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, including transport failures other than timeout", "10": "output file already exists (export)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "TRANSIENT", "NETWORK_ERROR", "OUTPUT_EXISTS", "WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string (RFC 3339 UTC)", "updated_at": "string (RFC 3339 UTC)"},
  "auth": "required for all note commands, whoami; not for schema, config show, auth status",
  "credential_requirements": ["token with notes:read (reads, export) or notes:write (create, delete)"],
  "cursor_contract": {"opacity": "opaque; do not parse or construct", "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run the same command without --cursor", "consistency": "best-effort, not snapshot-consistent"},
  "redaction": "tokens never appear in stdout, stderr, schema examples, or debug output",
  "debug": {"flag": "--debug", "default": false, "description": "Opt-in redacted request/response diagnostics on stderr; not allowed with --machine stderr framing, so --debug with --machine emits ndjson-typed stderr instead.", "stderr_framing_when_set": "ndjson-typed"},
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> --body-file <path>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "whoami": "notectl whoami",
    "config": {"show": "notectl config show --resolved"},
    "auth": {"status": "notectl auth status", "login": "notectl auth login --token-stdin"}
  },
  "common": {
    "no_stdin": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
    "network_read_errors": [
      {"code": "INTERNAL", "exit": 1},
      {"code": "VALIDATION_ERROR", "exit": 2},
      {"code": "UNAUTHENTICATED", "exit": 4},
      {"code": "FORBIDDEN", "exit": 5},
      {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
      {"code": "TIMEOUT", "exit": 7, "retryable": true},
      {"code": "TRANSIENT", "exit": 9, "retryable": true},
      {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}
    ],
    "read_retry_defaults": {"retries": 2, "backoff": "exponential from 250 ms, honors Retry-After", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "exhausted": "the final error is emitted with details.attempts"},
    "read_signal_semantics": {"interrupt": "no effect; nothing written", "closed_stdout": "exit quietly with status 0 for remaining output", "local_writes": "none"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "List notes in deterministic order with exact tag filters. No ranking; use note search for text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "description": "Only notes carrying every given tag (AND)."},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "Descending for timestamps, ascending for title; ties broken by id ascending."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": "common.no_stdin",
      "output": {"class": "list", "format": "json", "shape": {"items": "[note projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "shape_description": "next_cursor is present iff has_more is true", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "paged; body excluded by default", "truncation": "none within a page; paging is the only cap"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": "common.read_retry_defaults",
      "signal_semantics": "common.read_signal_semantics",
      "async": false, "streaming": false, "pagination": "cursor_contract", "artifact": false,
      "errors_possible": ["common.network_read_errors", {"code": "CURSOR_EXPIRED", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Return one note by ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["n_01HXR3Q8"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": "common.no_stdin",
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "small; body up to 1 MiB, never truncated"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": "common.read_retry_defaults",
      "signal_semantics": "common.read_signal_semantics",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": ["common.network_read_errors", {"code": "NOTE_NOT_FOUND", "exit": 3}]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Ranked full-text search over title and body. Requires --query. Use note list for unranked enumeration.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["release plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "score", "snippet"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "score", "snippet"]},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": "common.no_stdin",
      "output": {"class": "list", "format": "json", "shape": {"items": "[{id, title, tags, updated_at, score: number 0..1, snippet: string <=200 chars}] projected by --select", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "sort": "score descending, then id ascending", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "paged", "truncation": "snippet truncated to 200 chars, marked by snippet_truncated: true"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000, "retry_defaults": "common.read_retry_defaults",
      "signal_semantics": "common.read_signal_semantics",
      "async": false, "streaming": false, "pagination": "cursor_contract", "artifact": false,
      "errors_possible": ["common.network_read_errors", {"code": "CURSOR_EXPIRED", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file <path>",
      "summary": "Create one note. Body comes from --body-file or --body-stdin (exactly one). Pass --idempotency-key to make retries safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "max_count": 20, "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 64, "description": "Server deduplicates for 24 hours; reuse the same key on retry."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["UTF-8 text"], "maximum_input_size": 1048576, "can_block": "only while the writer keeps the pipe open; never waits on a TTY (stdin TTY with --body-stdin fails VALIDATION_ERROR)", "mutually_exclusive_with": ["--body-file"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "size_mode": "small"}
      },
      "dry_run": "validates inputs locally and checks auth/scope with a read-only API call; no note is created",
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "automatic_retry_safe": "only with --idempotency-key supplied on the first attempt"},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. With --idempotency-key: re-run with the same key; the server returns the original note if it committed. Without a key: not safe to retry automatically; an empty note list or search does not prove the create did not commit.",
      "signal_semantics": {"interrupt": "request may still commit remotely", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "key reused with different title, body, or tags"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Delete one note by ID. Permanent. Add --if-exists to treat an absent note as success.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["n_01HXR3Q8"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": "common.no_stdin",
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action is none when --if-exists would suppress NOTE_NOT_FOUND; title is present when the note exists", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note; no mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "automatic_retry_safe": "only with --if-exists"},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so re-run with --if-exists",
      "signal_semantics": {"interrupt": "remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
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
      "summary": "Write every note to a local file and return its path, size, and hash. Refuses to overwrite unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": "remote read-only; writes one local file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "'-' is not accepted; export always writes a file."},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one note_shape per line; json: {\"notes\": [note_shape]}"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "Deadline for the whole export, not per page."}
      ],
      "stdin_contract": "common.no_stdin",
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string (absolute, POSIX style)", "format": "ndjson|json", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "note_count": "integer", "exported_at": "string (RFC 3339 UTC)"}, "size_mode": "constant pointer; file size grows with notes"},
      "ordering": "notes in file sorted by id ascending",
      "consistency": "best-effort page walk; notes changed during export may appear in either state",
      "progress": "stderr human progress only outside machine mode; suppressed by --no-progress and --machine",
      "side_effects": {"external_mutation": false, "writes": ["--output path"]},
      "local_write_semantics": "writes <path>.tmp-<pid> then atomic rename; concurrent exports to one path are last-writer-wins; on failure or interrupt the temp file is removed and <path> is untouched",
      "latency_class": "slow", "timeout_defaults_ms": 300000, "retry_defaults": "common.read_retry_defaults applied per page",
      "signal_semantics": {"interrupt": "temp file removed; no partial file at --output", "closed_stdout": "finishes the file write", "local_writes": "atomic rename", "remote_continues": false},
      "dry_run": "not-applicable: export does not mutate remote state; the only local effect is the declared output file",
      "async": false, "streaming": false, "pagination": "internal; caller sees one artifact", "truncation": false, "artifact": true,
      "errors_possible": ["common.network_read_errors", {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"}, {"code": "WRITE_FAILED", "exit": 1}]
    }
  ]
}
```

The metadata commands `schema`, `whoami`, `config show --resolved`, `auth status`, and `auth login` follow the same per-command shape; their entries are elided here for length.
`schema`, `schema --fingerprint`, `config show`, and `auth status` are `local` latency, make no network call, and target under 100 ms; `whoami` is `network`.
`auth login --token-stdin` reads one line from piped stdin (max 4 KiB, never a TTY), writes the credential file atomically (mode 0600, last-writer-wins), and outputs `{"profile": "...", "credential_source": "file", "token_suffix": "...a1b2"}`.

Fingerprint endpoint (`notectl schema --fingerprint --machine`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3a91c2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads

`notectl note list --tag work --limit 2 --machine` (exit 0):

```json
{"items":[{"id":"n_01HXR3Q8","title":"Release plan","tags":["work","q4"],"updated_at":"2026-11-18T16:02:11Z"},{"id":"n_01HXQZ7M","title":"Standup notes","tags":["work"],"updated_at":"2026-11-17T09:15:40Z"}],"has_more":true,"next_cursor":"c_9fKx2","limit":2,"estimated_total":14}
```

`notectl note get n_01HXR3Q8 --machine` (exit 0):

```json
{"id":"n_01HXR3Q8","title":"Release plan","body":"Ship 1.0 on Dec 2.\nFreeze Nov 28.","tags":["work","q4"],"created_at":"2026-11-10T12:00:00Z","updated_at":"2026-11-18T16:02:11Z"}
```

`notectl note search --query 'freeze date' --machine` (exit 0):

```json
{"items":[{"id":"n_01HXR3Q8","title":"Release plan","tags":["work","q4"],"score":0.92,"snippet":"...Freeze Nov 28."}],"has_more":false,"limit":20,"estimated_total":1}
```

`notectl note create --title 'Retro' --body-file retro.md --tag work --idempotency-key 'retro-2026-11-19' --machine` (exit 0):

```json
{"id":"n_01HXS0AB","title":"Retro","body":"What went well...","tags":["work"],"created_at":"2026-11-19T10:00:03Z","updated_at":"2026-11-19T10:00:03Z"}
```

`notectl note delete n_01HXQZ7M --dry-run --machine` (exit 0):

```json
{"dry_run":true,"planned_action":"delete","id":"n_01HXQZ7M","title":"Standup notes"}
```

`notectl note delete n_01HXQZ7M --if-exists --machine` after it was already removed (exit 0):

```json
{"id":"n_01HXQZ7M","status":"absent"}
```

`notectl note export --output ./notes.ndjson --machine` (exit 0):

```json
{"path":"/home/agent/work/notes.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:3b7e0c9f5a1d2e4b6c8a0f1e3d5b7a9c2e4f6a8b0d1c3e5f7a9b2c4d6e8f0a1b","note_count":14,"exported_at":"2026-11-19T10:05:44Z"}
```

## 5. Example error payloads

Machine mode: stdout empty, the object below is the only stderr content.

Not found, `notectl note get n_404 --machine`, exit 3:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"n_404","temporary":false,"request_id":"req_8c1f"}
```

Validation, `notectl note create --title 'X' --body-file a.md --tag 'Bad Tag' --machine`, exit 2:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag.","field":"--tag","details":{"value":"Bad Tag","pattern":"^[a-z0-9][a-z0-9_-]{0,31}$"},"hint":"Use lowercase letters, digits, '_' or '-' in --tag; keep --title and --body-file unchanged.","temporary":false}
```

Rate limited, `notectl note search --query 'q' --machine` after retries exhausted, exit 6:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"details":{"attempts":3},"temporary":true,"request_id":"req_77aa"}
```

Unknown outcome on a mutation, `notectl note create ... --machine` timed out, exit 7:

```json
{"code":"TIMEOUT","message":"Request timed out; the note may have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key_supplied":false},"hint":"Do not retry blindly; next time pass --idempotency-key so a retry with the same key is safe."}
```

Unauthenticated, any note command with no token, exit 4:

```json
{"code":"UNAUTHENTICATED","message":"No credentials found.","details":{"sources_checked":["NOTECTL_TOKEN","credential file"]},"hint":"Set NOTECTL_TOKEN or pipe a token to auth login --token-stdin.","temporary":false}
```

Export target exists, `notectl note export --output notes.ndjson --machine`, exit 10:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes.ndjson","hint":"Add --overwrite or choose a different --output.","temporary":false}
```

## 6. Implementation and tests

Result-then-render: typed inputs, typed success and error payloads, separate human and machine renderers; `schema`/`--help` load no HTTP client or auth.
Ship tests for every item in the checklist § Tests that applies: schema snapshot and fingerprint stability, canonical payloads above, error payloads and declared-vs-observed exit codes, TTY vs non-TTY per stream, machine-mode suppression, `--body-stdin` incl. empty stdin and TTY rejection, pagination and `CURSOR_EXPIRED`, export artifact hash/atomicity, env/config precedence and `--isolated`, dry-run for create/delete, interrupt during create/delete/export, concurrent `auth login` and export to one path.
Deprecations and async cancellation: not-applicable in 1.0 (none exist), tests added when they do.

## 7. Checklist walk

| Section | Answer |
|---|---|
| Command Model | `noun verb`, shallow, ID positional selector, repeated `--tag`, conventional flag names |
| Machine Schema | §3; per-command entry via `notectl schema <command>`; fingerprint + scope + compatibility |
| Stdin Contract | declared per command; only `create --body-stdin` and `auth login --token-stdin` read stdin, explicitly |
| Shell Safety | `--` supported; body never in argv; hints carry flag names, not shell strings; examples quoted |
| Agent-Safe Invocation | `--machine` profile; `--isolated` separate and still authenticates via env; per-stream non-TTY; non-interactive bootstrap; caller timeouts everywhere |
| Output | stdout payload only; `single-error-object` framing; classes declared; pagination, cursor contract, projection, deterministic sort, UTC; `--output` only on export with path/size/hash |
| Errors And Exit Codes | tool-level codes 0–10; per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`; `INTERNAL` fallback; `NETWORK_ERROR` transport code; unknown-code policy |
| Partial failure | not-applicable: no multi-item command (export is all-or-nothing atomic) |
| Ambient State | sources, precedence, `--isolated`/`--no-config`, `whoami`/`config show --resolved`/`auth status`, secrets only via env/file/stdin |
| Mutations And Long-Running Work | `--dry-run` on create/delete; `--idempotency-key` and `--if-exists`; retry safety and reconciliation declared; signal semantics; atomic local writes; async not-applicable (export is a foreground command with declared deadline, progress, interrupt behavior) |
| Side Effects And Telemetry | reads have no side effects; no telemetry or update checks |
| Prose Surfaces | summaries lead with constraints and separate siblings (`list` vs `search`) |
| Tests | §6 |
