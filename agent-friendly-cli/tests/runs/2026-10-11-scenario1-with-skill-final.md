# Scenario 1 (Design) — with-skill run (final wording, after Copilot round 1)

- **Date:** 2026-10-11
- **Tree:** `d64e535` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill wording after commit d64e535)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set). Third scenario 1 arm of the day: run because commit d64e535 changed the checklist (required `temporary`, option ordering around `--`, Command Model bullets) after the previous validation run, and because it is the first arm scored against assertion A10.
- **Score:** 10/10 scored
- **Subagent tokens:** 91,041 (harness-reported total for the run; 5.9 minutes)
- **Transcript sha256:** `e5e9bf04f228fa14963fbdaac491b822e881396e305083855a5ca20951f51704` (session-local copy; not committed)

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify any repository file or run git.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; nothing under `tests/`; no other file; tracked tree verified clean afterwards.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| A1 | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | `canonical_machine_profile: ["--machine"]` implying `--json`, `--no-progress`, `--no-color`, `--no-pager`, each present in `global_flags`. |
| A2 | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | `exit_codes` 0–10, `symbolic_error_codes`, `errors_possible` on every command with `retryable`, `reconcile_first`, `suppressed_by`. |
| A3 | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | `stderr_framing: "single-error-object"`; "stderr is exactly this object, stdout empty". |
| A4 | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "no confirmation prompt in any mode, the verb is the trigger"; `--dry-run` alternate `{dry_run: true, planned_action: "delete", id, title}`. |
| A5 | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | `has_more`, `next_cursor?`, `limit`, `estimated_total?` plus a full cursor contract on `list` and `find`. |
| A6 | Export is the only `--output <file>` command and returns path, byte size, and content hash (Output). | **PASS** | `--output` declared only on `note export`; artifact shape `{path, byte_size, content_hash, note_count, file_format}`. |
| A7 | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | `--timeout-ms` with `"unit": "ms"` globally and per command. |
| A8 | Each command declares one output class; any flag that switches the class declares the switch (Output). | **PASS** | One `output.class` per command; `alternate_outputs` for `--dry-run` on `create`, `delete`, `export`, each with its own `streaming` value. |
| A9 | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | `ambient_state` block with sources, precedence, `--isolated`/`--no-config`, `auth whoami`, `config show --resolved`, redaction rule. |
| A10 | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). | **PASS** | Six examples use `--` (`get`, `find`, three `delete`, one error example); in every one the options precede `--` and only the id or quoted query follows. The run also states the rule in §2: "canonical examples quote values and put all options before `--`". |

**Set:** challenge.
**Regression vs 2026-06-09 baseline (1/9 on the first nine assertions):** none.
**Overhead:** 91,041 subagent tokens; no same-day baseline (prompt unchanged).
**Notes:** the option-ordering rule added in d64e535 landed on its first measured run; the previous final-wording run (`2026-10-11-scenario1-with-skill.md`) had shipped `-- "query" --machine`.
Side effect of moving the conventional verb set into the checklist as a rule: this run renamed the requested `search` command to `find` ("the checklist's conventional verb set is ... so the canonical command is `note find`"), flagged it as an owner decision, and offered no alias.
That is a defensible reading of the rule, but it shows the verb list now binds harder than it did as design guidance; worth watching in later runs.
Alternate outputs each declare `streaming: false` but no completion behavior; under the rule as first written in a4da656 that was a gap, and under the rule as narrowed after Copilot round 2 (completion behavior is required only for streaming alternates) they conform.

## Full final output

Verbatim final message returned by the subagent:

# `notectl` agent-facing CLI contract

Files read, in full: `/Users/bdc/projects/skills/agent-friendly-cli/SKILL.md`, `references/contract-checklist.md`, `references/design-workflow.md`, `references/examples.md`, `references/review-workflow.md`. Nothing under `tests/` or elsewhere was read; no repository file was modified; git was not run.

Routing per SKILL.md Workflow: audience = **tool author**; task = **new CLI design** → design-workflow.md, with contract-checklist.md as the standard and examples.md for shapes.

## 0. Assumptions

- The remote API exposes `id`, `title`, `body`, `tags`, plus `created_at`/`updated_at` timestamps (needed for a deterministic default sort). If it does not, default sort falls back to `id` ascending; nothing else changes.
- The API is token-authenticated and has a single-user identity (so `whoami` applies).
- No API operation is asynchronous; export is a synchronous, bounded page walk.
- The task said "search notes"; the checklist's conventional verb set is `list, get, find, create, update, delete, validate`, so the canonical command is `note find`. No `search` alias (aliases are for migration only). If the owner prefers `search`, make *it* canonical rather than adding an alias.

## 1. Task model (design-workflow §1)

| Agent job | Class | Minimum input | Minimum output for the next machine step |
|---|---|---|---|
| list notes | query | none | `id`, `title`, `tags`, `updated_at` per item + paging fields |
| get a note | inspect | `id` | full record |
| search notes | query | query string | `id`, `title`, `tags`, `snippet` per item + paging fields |
| create a note | mutate | `title` (body/tags optional) | created record (with server `id`) |
| delete a note | mutate | `id` | `{id, status: "deleted"}` |
| export all notes | query + local write | `--output <path>` | `{path, byte_size, content_hash, note_count}` |
| discover contract | discover | none | `schema`, `schema --fingerprint`, `version` |
| inspect ambient state | admin | none | `auth whoami`, `config show --resolved` |
| non-interactive bootstrap | admin | token on stdin | `auth login --token-stdin` |

No convenience wrappers (no `note count`, no `note open`, no bulk delete in v1); each is a one-line shell composition over `list`/`find`.

## 2. Command surface

```
notectl note list     [--tag <t>]... [--sort updated_at|created_at|title] [--limit N] [--cursor C] [--select f,...]
notectl note get      [--select f,...] [--] <id>
notectl note find     [--tag <t>]... [--sort relevance|updated_at] [--limit N] [--cursor C] [--select f,...] [--] <query>
notectl note create   --title <s> [--body <s> | --body-file <path|->] [--tag <t>]... [--idempotency-key <k>] [--dry-run]
notectl note delete   [--if-exists] [--dry-run] [--] <id>
notectl note export   --output <path> [--file-format ndjson|json] [--force] [--dry-run]

notectl auth login    --token-stdin          # non-interactive bootstrap; reads token from stdin
notectl auth logout
notectl auth whoami
notectl config show   --resolved
notectl schema        [--fingerprint] [<command path>]
notectl version
```

Global flags: `--machine` (canonical machine profile; implies `--json --no-progress --no-color --no-pager`), `--json`, `--no-progress`, `--no-color`, `--no-pager`, `--isolated`, `--no-config`, `--timeout-ms <int>`, `--retries <int>`, `--api-url <url>`, `--debug-log <path>`, `--help`.

Design decisions tied to checklist § Command Model / § Shell Safety:
- Tree depth is 2 (`noun verb`); one noun (`note`) for the data, `auth`/`config`/`schema`/`version` for admin and discovery.
- Primary selector per resource: `<id>` positional for `note`; `<query>` positional for `find`. Every other input is a named flag.
- `--` end-of-options is supported and declared; canonical examples quote values and put all options before `--`.
- Resource ids, titles, queries and paths are never interpolated into a shell or passed to a subshell.
- No confirmation prompts anywhere: the verbs `create`/`delete`/`export` are the explicit action triggers, so there is no `--yes`.
- Secrets never arrive via argv: no `--token` flag exists. Channels are `NOTECTL_TOKEN`, the credentials file, or `auth login --token-stdin`.

### `--help` summaries (rules-then-context, task-selective)

```
note list    List notes, newest-updated first. Paginated; body omitted unless --select body. Read-only.
note get     Fetch one note by id, including body. Read-only.
note find    Full-text search over title and body, relevance-ranked. Paginated. Read-only.
note create  Create a note. Requires --title. Body from --body or --body-file (use - for stdin). Mutates remote store.
note delete  Delete a note by id. Exit 3 if missing unless --if-exists. Mutates remote store.
note export  Write every note to --output as NDJSON (default) or JSON. Fails if the file exists unless --force. Writes local disk only.
auth login   Store an API token read from stdin (--token-stdin). Non-interactive. Writes credentials file.
auth whoami  Show the authenticated identity and where the token came from.
config show  Show resolved configuration with --resolved; secrets redacted.
schema       Print the machine contract; --fingerprint prints only the cache key. Local, no network, no auth.
```

## 3. Machine schema (`notectl schema --machine`)

Shape dialect is `notectl-compact-v1`: `a|b` is a closed enum; a trailing `?` marks an optional field; `[T]` is an array of `T`; fields are required unless marked `?` or removed by a declared projection; a string-valued `shape` describes a record sequence. JSON Schema is the zero-explanation alternative if the owner prefers verbosity over compactness.

```json
{
  "tool": "notectl",
  "schema_version": "1.0",
  "fingerprint": "nct-7f3a9c21",
  "fingerprint_scope": "schema-contract",
  "fingerprint_input": "this document excluding schema_version and the tool's release version; any additive or breaking contract change changes it",
  "compatibility": {
    "additive_minor_bump": ["new commands", "new optional flags", "new optional output fields", "new symbolic codes on new commands"],
    "breaking_major_bump": ["removals", "renames", "type or meaning changes", "exit-code remapping", "default-sort or projection-rule changes"]
  },
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_definition": "a|b closed enum; trailing ? optional; [T] array; fields required unless ? or removed by declared projection; string-valued shape = record sequence",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; no command declares an exception",
  "non_tty_behavior": {
    "stdout_not_tty": "structured output (same as --json), no pager",
    "stderr_not_tty": "no color, no progress, no spinners",
    "stdin_not_tty": "never waits for terminal input; --body-file - reads the pipe to EOF"
  },
  "machine_mode_guarantees": "no prompts, no color, no progress, no pager, no browser launch; deprecations, truncation, version mismatch and ambient-state warnings appear only as structured fields, never as free text",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--no-pager"], "description": "non-interactive machine mode; structured output only"},
    {"name": "--json", "type": "boolean", "default": false, "description": "structured JSON/NDJSON on stdout instead of human tables"},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "suppress progress on stderr"},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "suppress ANSI color on stderr; NO_COLOR env also honored"},
    {"name": "--no-pager", "type": "boolean", "default": false, "description": "never launch a pager"},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "ignore config files and the credentials file; environment variables are still read, so authenticated reads work with NOTECTL_TOKEN set"},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "ignore config files only"},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": "per command", "description": "whole-command deadline for network commands"},
    {"name": "--retries", "type": "integer", "default": "per command", "description": "retries on RATE_LIMITED/TRANSIENT within the deadline; honors retry_after_ms"},
    {"name": "--api-url", "type": "string", "default": "https://notes.example.com/v1", "description": "API base URL; precedence flag > NOTECTL_API_URL > config"},
    {"name": "--debug-log", "type": "path", "default": null, "description": "append redacted request/response traces to this file; never written to stdout or stderr"}
  ],
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "find": "notectl note find <query>",
      "create": "notectl note create --title <title>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"login": "notectl auth login --token-stdin", "logout": "notectl auth logout", "whoami": "notectl auth whoami"},
    "config": {"show": "notectl config show --resolved"},
    "schema": "notectl schema [--fingerprint] [<command path>]",
    "version": "notectl version"
  },
  "aliases": [],
  "deprecations": [],
  "exit_codes": {
    "0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated",
    "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified",
    "10": "local output write failed (domain-specific)"
  },
  "symbolic_error_codes": [
    "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN",
    "RATE_LIMITED", "TIMEOUT", "CONFLICT", "OUTPUT_EXISTS", "TRANSIENT", "OUTPUT_WRITE_FAILED"
  ],
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "field?": "string", "details?": "object", "resource_id?": "string", "retry_after_ms?": "integer", "request_id?": "string", "path?": "string", "conflict_with?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string(rfc3339,utc)", "updated_at": "string(rfc3339,utc)"},
  "field_limits": {"title": "1-200 chars", "body": "<= 1048576 bytes UTF-8", "tags": "<= 32 tags, each 1-50 chars, lowercase [a-z0-9-]"},
  "auth": "required for all note and auth whoami commands; not required for schema, version, config show, auth login/logout",
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env", "$XDG_CONFIG_HOME/notectl/credentials.json (mode 0600)"], "secret_intake": ["env", "credentials file", "auth login --token-stdin"], "argv_token_flag": false},
    "config_files": ["$NOTECTL_CONFIG or $XDG_CONFIG_HOME/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_CONFIG", "NO_COLOR"],
    "caches": [],
    "precedence": "flags > environment variables > config file",
    "disable_with": {"all_files": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl auth whoami", "notectl config show --resolved"],
    "redaction": "token rendered as \"***redacted***\" with token_source reported; applies to stdout, stderr, --debug-log and schema examples",
    "local_write_safety": "credentials and config are written via temp file + atomic rename; concurrent invocations are last-writer-wins at file granularity"
  },
  "telemetry": {"enabled": false, "update_checks": false},
  "metadata_paths": {"commands": ["--help", "schema", "schema --fingerprint", "version"], "target_latency_ms": 100, "network": false, "auth": false, "plugin_loading": false},
  "signals": {
    "read_only_commands": "SIGINT/SIGTERM: exit immediately via default signal disposition; nothing is left behind",
    "note create / note delete": "remote outcome is unknown after interrupt; follow the command's reconciliation entry",
    "note export": "temp file <output>.notectl-tmp-<pid> is removed, any pre-existing --output file is untouched, then the signal is re-raised; no structured error is written"
  },
  "long_running": {"async_operations": false, "justification": "no operation returns a job id; export is a synchronous bounded page walk under --timeout-ms"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "include only notes carrying every given tag (AND)"},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "updated_at/created_at descending, title ascending; id ascending is always the final tiebreaker"},
        {"name": "--limit", "type": "integer", "default": 50, "minimum": 1, "maximum": 500},
        {"name": "--cursor", "type": "string", "default": null, "description": "opaque token from a previous page's next_cursor"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000},
        {"name": "--retries", "type": "integer", "default": 2}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note_shape projected]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present on each item; unselected fields are absent, not null"},
        "size_mode": "bounded by --limit; body excluded by default"
      },
      "pagination": {"navigation": "next_cursor", "has_more": true, "cursor_opaque": true, "cursor_lifetime_s": 600, "expired_cursor_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort; notes created or deleted mid-walk may appear or be skipped"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "within_deadline": true},
      "async": false, "streaming": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HZX4Q8K2M9"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000},
        {"name": "--retries", "type": "integer", "default": 2}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape projected", "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent, not null"}, "size_mode": "small; body up to 1 MiB"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "within_deadline": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note find <query>",
      "classification": "query", "read_only": true,
      "arguments": [{"name": "query", "type": "string", "cardinality": "one", "description": "full-text query over title and body; treated as literal text, no operator syntax", "examples": ["quarterly budget"]}],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--sort", "type": "enum", "enum": ["relevance", "updated_at"], "default": "relevance", "description": "relevance descending then id ascending; deterministic for a fixed index state"},
        {"name": "--limit", "type": "integer", "default": 20, "minimum": 1, "maximum": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "updated_at", "snippet"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at", "snippet"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000},
        {"name": "--retries", "type": "integer", "default": 2}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note_shape projected + snippet: string(<=200 chars, plain text)]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer", "query": "string"},
        "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent, not null"},
        "empty_result": "{items: [], has_more: false, limit, query} with exit 0",
        "size_mode": "bounded by --limit"
      },
      "pagination": {"navigation": "next_cursor", "has_more": true, "cursor_opaque": true, "cursor_lifetime_s": 600, "expired_cursor_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "within_deadline": true},
      "async": false, "streaming": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <title>",
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "description": "1-200 chars"},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "read body from this file; '-' reads stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--idempotency-key", "type": "string", "default": null, "description": "caller-chosen key, 1-128 chars; the API returns the existing note for a repeated key with the same payload and CONFLICT for a repeated key with a different payload; makes retry after TIMEOUT safe"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 15000},
        {"name": "--retries", "type": "integer", "default": 0, "description": "automatically raised to 2 when --idempotency-key is set"}
      ],
      "stdin_contract": {"reads": "only when --body-file -", "auto_detected_when_piped": false, "accepted_formats": ["text/plain; UTF-8"], "maximum_input_size": 1048576, "can_block": "reads piped stdin to EOF; if stdin is a TTY the command fails with VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body"], "empty_stdin": "body is the empty string"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "note": {"title": "string", "body_bytes": "integer", "tags": "[string]"}}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates title/body/tag limits locally and makes no network call; no cache or token refresh occurs because tokens are static", "description": "creates one note unless --dry-run"},
      "latency_class": "network", "timeout_defaults_ms": 15000,
      "retry_defaults": {"retries": 0, "with_idempotency_key": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TIMEOUT"]}},
      "reconciliation": "after TIMEOUT or interrupt the outcome is unknown; with --idempotency-key re-run the identical command (safe); without it, run notectl note find with the exact title and compare created_at before retrying",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "description": "retryable: true when --idempotency-key is set"},
        {"code": "CONFLICT", "exit": 8, "description": "--idempotency-key reused with a different payload; conflict_with carries the existing note id"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HZX4Q8K2M9"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "exit 0 with status already_absent when the note does not exist"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 15000},
        {"name": "--retries", "type": "integer", "default": 0}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|already_absent"}, "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete", "id": "string", "title": "string"}, "streaming": false, "size_mode": "small", "description": "performs a read (note get) to confirm existence and echo the title; NOTE_NOT_FOUND applies unless --if-exists"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "one read-only API call; no externally visible mutation", "description": "deletes one note unless --dry-run; no confirmation prompt in any mode, the verb is the trigger"},
      "latency_class": "network", "timeout_defaults_ms": 15000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "delete is idempotent in effect: after TIMEOUT or interrupt run notectl note get <id>; NOTE_NOT_FOUND means it committed; re-running with --if-exists is always safe",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "classification": "query", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "destination file; written atomically via temp file + rename"},
        {"name": "--file-format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one note_shape per line; json: {\"notes\": [note_shape], \"exported_at\": rfc3339}"},
        {"name": "--force", "type": "boolean", "default": false, "description": "replace an existing --output file"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 120000, "description": "whole-command deadline across all pages"},
        {"name": "--retries", "type": "integer", "default": 2, "description": "per page fetch"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string(absolute)", "byte_size": "integer", "content_hash": "string(sha256:<hex>)", "note_count": "integer", "file_format": "ndjson|json"}, "size_mode": "small pointer; file size unbounded"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "export", "path": "string(absolute)", "file_format": "ndjson|json", "estimated_note_count?": "integer", "would_replace_existing": "boolean"}, "streaming": false, "size_mode": "small", "description": "checks the directory is writable and whether the file exists, fetches one page for estimated_note_count, writes nothing"}
      },
      "side_effects": {"external_mutation": false, "writes": ["local file at --output"], "dry_run": "no local write; one read-only API call", "description": "walks every page of note list with body included and writes them to --output"},
      "latency_class": "slow", "timeout_defaults_ms": 120000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "within_deadline": true},
      "reconciliation": "on TIMEOUT or interrupt the temp file is removed and any pre-existing --output is untouched; simply re-run",
      "async": false, "streaming": false, "pagination": "internal page walk, best-effort consistency: the export is not a point-in-time snapshot", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--force"},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10, "retryable": false, "description": "permission denied, disk full, or directory missing; path names the offending path"}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth login --token-stdin",
      "classification": "admin", "read_only": false,
      "flags": [{"name": "--token-stdin", "type": "boolean", "required": true, "description": "the only intake channel; there is no --token flag"}, {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "accepted_formats": ["text/plain; single line, trailing newline stripped"], "maximum_input_size": 4096, "can_block": "reads piped stdin to EOF; TTY stdin fails with VALIDATION_ERROR", "mutually_exclusive_with": [], "empty_stdin": "VALIDATION_ERROR"},
      "output": {"class": "record", "format": "json", "shape": {"user_id": "string", "credentials_path": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": ["credentials file, atomic rename, mode 0600"], "description": "verifies the token with one whoami request, then stores it"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}, {"code": "OUTPUT_WRITE_FAILED", "exit": 10}]
    },
    {
      "canonical_invocation_path": "notectl auth logout",
      "classification": "admin", "read_only": false,
      "stdin_contract": {"reads": false}, "output": {"class": "record", "format": "json", "shape": {"removed": "boolean", "credentials_path": "string"}},
      "side_effects": {"external_mutation": false, "writes": ["removes credentials file"]}, "latency_class": "local",
      "errors_possible": [{"code": "OUTPUT_WRITE_FAILED", "exit": 10}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "classification": "inspect", "read_only": true,
      "flags": [{"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}],
      "stdin_contract": {"reads": false},
      "output": {"class": "record", "format": "json", "shape": {"user_id": "string", "token_source": "env:NOTECTL_TOKEN|file:<path>|none", "api_url": "string"}},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "network",
      "errors_possible": [{"code": "UNAUTHENTICATED", "exit": 4}, {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "classification": "inspect", "read_only": true,
      "flags": [{"name": "--resolved", "type": "boolean", "required": true}],
      "stdin_contract": {"reads": false},
      "output": {"class": "record", "format": "json", "shape": {"api_url": {"value": "string", "source": "flag|env:NOTECTL_API_URL|config:<path>|default"}, "token": {"value": "***redacted***|null", "source": "env:NOTECTL_TOKEN|file:<path>|none"}, "config_path": "string|null", "isolated": "boolean"}},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local",
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl schema",
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command path", "type": "string", "cardinality": "zero-or-one", "description": "e.g. \"note get\" returns only that command's entry plus top-level fields", "examples": ["note get"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false, "description": "print only {schema_version, fingerprint, fingerprint_scope}"}],
      "stdin_contract": {"reads": false},
      "output": {"class": "record", "format": "json", "shape": "this document, or its fingerprint subset"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local",
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown command path"}]
    },
    {
      "canonical_invocation_path": "notectl version",
      "classification": "discover", "read_only": true,
      "stdin_contract": {"reads": false},
      "output": {"class": "record", "format": "json", "shape": {"version": "string(semver)", "schema_version": "string", "fingerprint": "string"}},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local",
      "errors_possible": []
    }
  ]
}
```

## 4. Fingerprint payload (`notectl schema --fingerprint --machine`)

```json
{"schema_version": "1.0", "fingerprint": "nct-7f3a9c21", "fingerprint_scope": "schema-contract"}
```

Fingerprint change → re-fetch schema. Major bump → existing call sites may break. Version-only releases do not change the fingerprint (release version is excluded from the fingerprint input, declared above).

## 5. Example success payloads (stdout, machine mode, exit 0)

`notectl note list --tag work --limit 2 --machine` (list; body absent by projection default):
```json
{
  "items": [
    {"id": "note_01HZX4Q8K2M9", "title": "Q3 budget review", "tags": ["work", "finance"], "updated_at": "2026-10-10T14:02:11Z"},
    {"id": "note_01HZX3P1N7D4", "title": "1:1 agenda", "tags": ["work"], "updated_at": "2026-10-09T08:30:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c3VwZXItb3BhcXVl",
  "limit": 2,
  "estimated_total": 37
}
```

`notectl note get --machine -- note_01HZX4Q8K2M9` (record):
```json
{
  "id": "note_01HZX4Q8K2M9",
  "title": "Q3 budget review",
  "body": "Headcount flat. Cloud spend +12% QoQ; revisit reserved instances.",
  "tags": ["work", "finance"],
  "created_at": "2026-09-30T17:45:02Z",
  "updated_at": "2026-10-10T14:02:11Z"
}
```

`notectl note find --limit 1 --machine -- "reserved instances"` (list with snippet):
```json
{
  "items": [
    {"id": "note_01HZX4Q8K2M9", "title": "Q3 budget review", "tags": ["work", "finance"], "updated_at": "2026-10-10T14:02:11Z", "snippet": "Cloud spend +12% QoQ; revisit reserved instances."}
  ],
  "has_more": false,
  "limit": 1,
  "query": "reserved instances"
}
```

Empty search result, still exit 0:
```json
{"items": [], "has_more": false, "limit": 20, "query": "zzyzx"}
```

`printf '%s' "Call vendor re: renewal" | notectl note create --title "Renewal follow-up" --tag work --body-file - --idempotency-key "agent-7f2c-001" --machine` (record):
```json
{
  "id": "note_01HZX5R2T8W1",
  "title": "Renewal follow-up",
  "body": "Call vendor re: renewal",
  "tags": ["work"],
  "created_at": "2026-10-11T19:04:33Z",
  "updated_at": "2026-10-11T19:04:33Z"
}
```

`notectl note create --title "Renewal follow-up" --tag work --dry-run --machine` (never byte-identical to a real create):
```json
{"dry_run": true, "planned_action": "create", "note": {"title": "Renewal follow-up", "body_bytes": 0, "tags": ["work"]}}
```

`notectl note delete --machine -- note_01HZX5R2T8W1` (record):
```json
{"id": "note_01HZX5R2T8W1", "status": "deleted"}
```

`notectl note delete --if-exists --machine -- note_01HZX5R2T8W1` run a second time:
```json
{"id": "note_01HZX5R2T8W1", "status": "already_absent"}
```

`notectl note delete --dry-run --machine -- note_01HZX4Q8K2M9`:
```json
{"dry_run": true, "planned_action": "delete", "id": "note_01HZX4Q8K2M9", "title": "Q3 budget review"}
```

`notectl note export --output ./notes.ndjson --machine` (artifact):
```json
{
  "path": "/Users/bdc/work/notes.ndjson",
  "byte_size": 48213,
  "content_hash": "sha256:9b1c6e0f3a7d2c4e8f5a1b3d7c9e2f4a6b8d0c1e3f5a7b9d1c3e5f7a9b1d3c5e",
  "note_count": 37,
  "file_format": "ndjson"
}
```

`notectl auth whoami --machine`:
```json
{"user_id": "usr_8k2m", "token_source": "env:NOTECTL_TOKEN", "api_url": "https://notes.example.com/v1"}
```

`notectl config show --resolved --machine` (secret redacted, source kept):
```json
{
  "api_url": {"value": "https://notes.example.com/v1", "source": "config:/Users/bdc/.config/notectl/config.toml"},
  "token": {"value": "***redacted***", "source": "file:/Users/bdc/.config/notectl/credentials.json"},
  "config_path": "/Users/bdc/.config/notectl/config.toml",
  "isolated": false
}
```

## 6. Example error payloads (stderr is exactly this object, stdout empty, per `single-error-object`)

**Validation**, exit 2, from `notectl note create --title "" --tag "Not A Slug" --machine`. `field` names a published flag; machine-usable constraints are in `details`, not only in `hint`:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid value for --tag.",
  "field": "--tag",
  "details": {"rejected_value": "Not A Slug", "pattern": "^[a-z0-9-]{1,50}$", "max_tags": 32},
  "hint": "Use lowercase letters, digits and hyphens, e.g. --tag not-a-slug.",
  "temporary": false
}
```

**Not found**, exit 3, from `notectl note get --machine -- note_01HZXDOESNOTEXIST`:
```json
{
  "code": "NOTE_NOT_FOUND",
  "message": "Note not found.",
  "resource_id": "note_01HZXDOESNOTEXIST",
  "request_id": "req_4f8a2c",
  "temporary": false
}
```

**Unauthenticated**, exit 4, with the non-interactive bootstrap as the repair (no shell string, no secret):
```json
{
  "code": "UNAUTHENTICATED",
  "message": "No API token found.",
  "details": {"checked_sources": ["env:NOTECTL_TOKEN", "file:/Users/bdc/.config/notectl/credentials.json"]},
  "hint": "Set NOTECTL_TOKEN, or run notectl auth login --token-stdin with the token on stdin.",
  "temporary": false
}
```

**Rate limited**, exit 6, `retry_after_ms` present and `temporary: true`:
```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 30000,
  "request_id": "req_91be70",
  "temporary": true
}
```

**Timeout on a mutation without an idempotency key**, exit 7, `temporary: false` because the caller must reconcile first (catalog: `reconcile_first: true`):
```json
{
  "code": "TIMEOUT",
  "message": "Request exceeded 15000 ms; the create may or may not have committed.",
  "details": {"timeout_ms": 15000, "reconcile": {"command": "note find", "query": "Renewal follow-up"}, "safe_retry_requires": "--idempotency-key"},
  "hint": "Run notectl note find with the exact title; if absent, retry with --idempotency-key so a second timeout is safely retryable.",
  "temporary": false
}
```

**Export conflict with existing file**, exit 8, suppressed by `--force`:
```json
{
  "code": "OUTPUT_EXISTS",
  "message": "Output file already exists.",
  "path": "/Users/bdc/work/notes.ndjson",
  "hint": "Pass --force to replace it, or choose a different --output path.",
  "temporary": false
}
```

**Expired cursor**, exit 2:
```json
{
  "code": "CURSOR_EXPIRED",
  "message": "Cursor is no longer valid.",
  "field": "--cursor",
  "details": {"cursor_lifetime_s": 600, "restart_action": "re-run without --cursor"},
  "temporary": false
}
```

## 7. Checklist coverage (SKILL.md Done Criteria for design tasks)

| contract-checklist.md section | Where answered |
|---|---|
| Command Model | §2: `noun verb`, depth 2, conventional verbs (`find` not `search`), one positional selector per resource, named flags, conventional flag names (`--limit`, `--timeout-ms`, `--output`, `--select`), no aliases |
| Machine Schema | §3: every listed item present (tree, flags with types/defaults/enums/cardinality/examples, units in flag name, profile + implied flags, isolation profile, stdin, read-only flag, auth/env/config, output class/shape/projection/size, dialect, exit + symbolic codes, per-command catalog with `retryable`/`reconcile_first`/`suppressed_by`, side effects, latency class, timeout/retry defaults, pagination/cursor, artifact, version + fingerprint + scope + compatibility) |
| Stdin Contract | Per command; only `note create --body-file -` and `auth login --token-stdin` read stdin, both explicit, size-capped, TTY-stdin fails fast |
| Shell Safety | `end_of_options_supported: true`; examples quote and place `--` after options; no subshell; hints express repairs as flag values |
| Agent-Safe Invocation | `--machine` single flag; `--isolated` distinct and still allows env-token reads; `non_tty_behavior` per stream; `machine_mode_guarantees`; `auth login --token-stdin` bootstrap; `metadata_paths` local/no-auth/<100 ms; `--timeout-ms` on every network command with declared retries |
| Output | stdout = payload only; stderr framing `single-error-object` declared as enum; one output class per command with alternates declared for `--dry-run`; deterministic default sort with id tiebreaker; pagination with `has_more`/`next_cursor`/`limit`/`estimated_total` and full cursor contract; `--select` projection rule; UTC RFC3339; `--output` only on export, returning path/byte_size/content_hash. **Not applicable**: `stream`/`bulk-result` classes and `completion_record` — no command streams or takes multi-item input in v1; `message` never duplicates success data because no success payload carries `message` |
| Errors And Exit Codes | Exit map 0–10 with 10 declared domain-specific; required fields `code`/`message`/`temporary` on every error; `retry_after_ms` on RATE_LIMITED; `field` always a published flag; `--debug-log` opt-in and redacted. **Not applicable**: partial failure / `--allow-partial` — no multi-item commands in v1 |
| Ambient State | `ambient_state` block: sources, precedence, `--isolated`/`--no-config`, `auth whoami` + `config show --resolved`, redaction rule, no argv token flag, no caches |
| Mutations And Long-Running Work | `--dry-run` on all three mutating commands with distinguishable output; `--idempotency-key` and `--if-exists`; reconciliation entries for create/delete/export; `signals` block; atomic local writes. **Not applicable**: job ids/polling/cancel — no async operations (`long_running` block carries the justification) |
| Side Effects And Telemetry | Reads declare `writes: []`; `telemetry.enabled: false`, no update checks; export's only write is the declared `--output` |
| Prose Surfaces | §2 help summaries are rules-then-context and sibling-selective; schema descriptions lead with constraints |
| Tests | §8 below |

## 8. Tests to ship (checklist § Tests)

- Schema snapshot and fingerprint stability: fingerprint unchanged across a version-only bump; changed on any contract edit.
- Canonical success payload snapshots for all 12 commands (§5) and the three `--dry-run` alternates.
- Failure payloads + exit codes for every row of every `errors_possible` catalog, with a runtime assertion that observed exit == declared exit.
- TTY vs non-TTY on each of stdout/stderr/stdin independently; `--machine` suppresses prompts (none exist — assert no TTY read), color, progress, pager.
- Stdin: `--body-file -` with piped content, empty pipe (empty body), >1 MiB (VALIDATION_ERROR), and TTY stdin (fails without blocking, under a timeout harness).
- Pagination walk to `has_more: false`; expired cursor → `CURSOR_EXPIRED`; `--select` projection omits rather than nulls.
- Export: atomic write (kill mid-walk leaves pre-existing file intact and no temp file), `OUTPUT_EXISTS` without `--force`, `content_hash` matches the file, `OUTPUT_WRITE_FAILED` on a read-only directory.
- Config/env/flag precedence; `--isolated` ignores files but honors `NOTECTL_TOKEN`; `config show --resolved` never prints the token.
- Dry-run of create makes zero network calls; dry-run of delete makes exactly one GET; neither output is byte-identical to the real mutation.
- Interrupt create/delete mid-request and confirm the documented reconciliation path recovers.
- Concurrent `auth login` invocations leave a valid credentials file.
- Metadata paths (`--help`, `schema`, `schema --fingerprint`, `version`) complete under 100 ms with the network blackholed and no credentials present.

## Open items for the owner

1. Confirm the API exposes `created_at`/`updated_at`; otherwise drop them from `note_shape` and make the default sort `id` ascending.
2. Confirm `find` vs `search` as the canonical verb (see Assumptions); pick one, no alias.
3. If a bulk delete or stdout-streaming export is wanted later, add them as declared `bulk-result`/`stream` alternates with `completion_record`, per the checklist; they are intentionally out of v1.
