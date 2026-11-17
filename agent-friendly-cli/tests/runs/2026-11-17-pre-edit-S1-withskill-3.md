# Scenario 1 (design) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 10/11 scored; 2/2 conformance
- **Tokens:** 78,342 (final-turn context plus output, read from the transcript)
- **Output words:** 3,667
- **Transcript sha256:** `323e1e3af4a59ec92d6a8ebc908dfff46b9487ceaedfe269aaf306267fe21d11` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o4`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; {"name": "--machine", "type": "boolean" Parts: profile declared in schema = pass; named flags declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {"0": "success", ...}; delete "errors_possible": [...] Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object" ... "stdout is empty" Parts: stdout success only = pass; stderr structured failures with framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "summary": "Permanently delete one note by ID"; {"dry_run": true, "planned_action": "delete", ...} Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": true, "next_cursor": "c_eyJvIjoyfQ" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size": 48213, "content_hash": "sha256:9b74..." |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl whoami", "notectl config show --resolved"]; "disable_with": {"all": "--isolated" Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note get --machine -- -n_weird |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | INTERNAL in symbolic codes, exit 1 "generic", but no statement of what unanticipated failures emit; TRANSIENT in each networked list; no rule for unlisted codes Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = pass; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag <tag>]... ; "cardinality": "many" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "`--output` only on export, returning path/size/hash" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "output": {"class": "artifact", ...}; "alternate_outputs": {"--dry-run": {"class": "record" |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (designing a new CLI).
Task: new design, so this follows the design workflow and is checked against the contract checklist at the end.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | ids, titles, tags, paging cursor |
| Get a note | inspect | note id | full note |
| Search notes | query | query string | ids, titles, tags, match snippet, paging cursor |
| Create a note | mutate | title, body (stdin or file), tags | created note with id |
| Delete a note | mutate | note id | deleted id |
| Export all notes | query (writes local file) | output path | path, byte size, content hash, count |
| Discover contract | discover | none | schema / fingerprint |
| Inspect identity and config | admin | none | account, resolved config with sources |

No `update` verb: not requested.
`list` and `find` are distinct by input alone: `list` enumerates with structured filters, `find` ranks by a free-text query.

## 2. Command surface

Pattern: `notectl note <verb>`; primary selector for a note is its ID (positional, one only).

```
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort created_at|updated_at|title] [--select <field>]...
notectl note get    <id> [--select <field>]...
notectl note find   --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create --title <text> [--tag <tag>]... (--body-file <path> | --body-file -) [--idempotency-key <key>] [--dry-run]
notectl note delete <id> [--if-exists] [--dry-run]
notectl note export --output <path> [--format json|ndjson] [--tag <tag>]... [--overwrite]

notectl schema [<command path>] [--fingerprint]
notectl whoami
notectl config show --resolved
```

Global flags: `--machine`, `--json`, `--no-color`, `--no-progress`, `--no-input`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`.
Every command accepts `--` end-of-options; all options precede it, only operands follow (e.g. `notectl note get --machine -- -n_weird`).

Help summaries (rules first, task-selective):

- `note list`: Enumerate notes, newest first, filtered by exact tag; paginated. Use `find` for text search.
- `note get`: Return one note by ID, including body.
- `note find`: Full-text search over title and body, ranked by relevance; paginated. Use `list` to enumerate without a query.
- `note create`: Create one note; body is read from `--body-file` (`-` for stdin); returns the created note.
- `note delete`: Permanently delete one note by ID; `--if-exists` makes a missing note a success.
- `note export`: Write every matching note to a local file and return its path, size, and hash; never writes note data to stdout.

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect: JSON Schema would be the zero-explanation choice; this contract uses the compact named notation `notectl-compact-v1` declared inside the schema.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7f3e91a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "compatibility": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes on existing exit codes"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping"],
    "rule": "any contract change changes the fingerprint; breaking changes also bump the major schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; [T] is an array of T; fields are required unless so marked or removed by a declared projection; a string-valued shape describes an NDJSON record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC3339 UTC with Z suffix", "numbers": "locale-independent", "paths": "as given by caller, absolute in export output"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-color", "--no-progress", "--no-input"], "description": "Non-interactive machine mode: structured output only, no prompts, color, progress, pager, or browser launch."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit structured JSON on stdout and structured errors on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color on all streams."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress spinners and progress on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files, the credential file, and the cache; only flags and NOTECTL_* env vars are read. Authenticated commands then require NOTECTL_TOKEN."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only; credentials and cache still apply."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to read."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "Remote API base URL."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": null, "description": "Per-request network timeout; null means the command's declared default."}
  ],
  "non_tty_behavior": "evaluated per stream: non-TTY stdout disables human tables and pager; non-TTY stderr disables color and progress; non-TTY stdin disables prompts",
  "exit_codes": {"0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified", "10": "local output file error"},
  "symbolic_error_codes": ["VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED", "TRANSIENT", "INTERNAL"],
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["env NOTECTL_TOKEN", "credential file ~/.config/notectl/credentials.json (mode 0600)"], "secret": true, "redaction": "never printed; config show reports source and last 4 chars only", "argv_accepted": false},
    "config_files": ["$NOTECTL_CONFIG", "~/.config/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "NO_COLOR"],
    "cache": {"path": "~/.cache/notectl/", "contents": "schema fingerprint only; note data is never cached", "reads": true, "writes": "atomic replace (write temp + rename)"},
    "precedence": "flags > env vars > config file > cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl whoami", "notectl config show --resolved"],
    "bootstrap": "non-interactive: export NOTECTL_TOKEN, or write the credential file; no login prompt or browser flow exists"
  },
  "telemetry": {"enabled": false, "update_checks": false},
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "find": "notectl note find --query <text>",
      "create": "notectl note create --title <text> --body-file <path|->",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command path>] [--fingerprint]",
    "whoami": "notectl whoami",
    "config": {"show": "notectl config show --resolved"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes, newest first, filtered by exact tag; paginated. Use note find for text search.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "Return notes having all given tags (exact match)."},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null, "description": "Opaque next_cursor from a previous page."},
        {"name": "--sort", "type": "enum", "enum": ["created_at", "updated_at", "title"], "default": "updated_at", "description": "Descending for timestamps, ascending for title; ties broken by id ascending."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "size_mode": "paged; body omitted by default",
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "TIMEOUT"], "backoff": "exponential from 200ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
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
      "summary": "Return one note by ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[A-Za-z0-9]{12}$", "examples": ["note_8Kq2vX9mLp0a"]}],
      "flags": [{"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "small; body up to 1 MiB, never truncated"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "TIMEOUT"], "backoff": "exponential from 200ms"},
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
      "canonical_invocation_path": "notectl note find --query <text>",
      "summary": "Full-text search over title and body, ranked by relevance; paginated. Use note list to enumerate without a query.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["\"quarterly plan\""]},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at", "score", "snippet"], "cardinality": "many", "default": ["id", "title", "tags", "score", "snippet"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id, title?, body?, tags?, created_at?, updated_at?, score?: number, snippet?: string} projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; id always present"},
        "sort": "score descending, ties by id ascending",
        "size_mode": "paged; snippet capped at 200 chars, marked by snippet ending in U+2026 when cut",
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "TIMEOUT"], "backoff": "exponential from 200ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": "snippet only, declared above", "artifact": false,
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
      "canonical_invocation_path": "notectl note create --title <text> --body-file <path|->",
      "summary": "Create one note; body is read from --body-file (- for stdin); returns the created note.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body-file", "type": "path", "required": true, "description": "Path to UTF-8 body text, or - to read stdin."},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_count": 20},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 64, "description": "Same key within 24h returns the original note instead of creating a duplicate."},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": "only when --body-file -", "auto_detected_when_piped": false, "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": "1 MiB (bytes)", "can_block": "only if stdin is an open TTY; with --no-input/--machine a TTY stdin fails with VALIDATION_ERROR instead of blocking", "mutually_exclusive_with": ["--body-file <path>"], "empty_stdin": "accepted: creates a note with empty body"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "note": "{title, body_bytes: integer, tags}"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth with a read-only API call; no externally visible mutation; may refresh nothing locally"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "automatic_retry_safe": "only with --idempotency-key"},
      "reconciliation": "on TIMEOUT or interrupt the outcome is unknown; re-run with the same --idempotency-key (returns the original if committed), or without a key use note find --query <title> to check before retrying",
      "signals": "SIGINT/SIGTERM aborts the request; the remote create may already have committed; no local writes occur",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "key reused with different title/body/tags"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by ID; --if-exists makes a missing note a success.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[A-Za-z0-9]{12}$", "examples": ["note_8Kq2vX9mLp0a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "deleted": "true|false", "reason?": "not_found"}, "size_mode": "small", "description": "deleted is false only when --if-exists suppressed NOTE_NOT_FOUND"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "delete|none", "id": "string", "title?": "string"}, "size_mode": "small", "description": "planned_action none appears only with --if-exists when the note is missing"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "performs a read of the note only; no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "automatic_retry_safe": "only with --if-exists"},
      "reconciliation": "on TIMEOUT or interrupt the outcome is unknown; retry with --if-exists (safe), or run note get <id>: NOTE_NOT_FOUND means the delete committed",
      "signals": "SIGINT/SIGTERM aborts the request; the remote delete may already have committed; no local writes occur",
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
      "summary": "Write every matching note to a local file and return its path, size, and hash; never writes note data to stdout.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": "remote read-only; writes one local file",
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "Destination file; - is rejected (stdout is reserved for the result record)."},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "File format: ndjson writes one note_shape per line sorted by id; json writes {notes: [note_shape]}."},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--overwrite", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "format": "json|ndjson", "note_count": "integer", "exported_at": "string"}, "size_mode": "small pointer; file size unbounded"},
      "side_effects": {"external_mutation": false, "writes": ["--output path"], "description": "writes to <path>.tmp-<pid> then atomically renames; partial file never left at <path>"},
      "latency_class": "slow", "timeout_defaults_ms": 10000, "timeout_scope": "per page request; total runtime unbounded",
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "TIMEOUT"], "scope": "per page request"},
      "consistency": "best-effort page walk; notes changed during export may be missing or duplicated-by-id-never",
      "signals": "SIGINT/SIGTERM removes the temp file; <path> is unchanged",
      "concurrency": "two exports to the same path: last rename wins (documented last-writer-wins)",
      "async": false, "streaming": false, "pagination": "internal", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema",
      "summary": "Print this contract; schema <command path> prints one command; --fingerprint prints only version and fingerprint.",
      "classification": "discover", "read_only": true, "auth": "none",
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "full ~20 KB; per-command ~3 KB; fingerprint <200 B"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "latency_target_ms": 100, "network": false,
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl whoami",
      "summary": "Show the authenticated account and the source of its credential.",
      "classification": "admin", "read_only": true, "auth": "required",
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "[string]", "credential_source": "env:NOTECTL_TOKEN|file|none", "api_url": "string"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 3000, "retry_defaults": {"retries": 0},
      "errors_possible": [{"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show every resolved setting with its source; secrets redacted. No network.",
      "classification": "admin", "read_only": true, "auth": "none",
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"settings": "[{key, value, source: flag|env|config|default, secret: boolean}]", "config_files_read": "[string]", "isolated": "boolean"}},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

`notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, machine mode)

`notectl note list --tag work --limit 2 --machine`, exit `0`:

```json
{
  "items": [
    {"id": "note_8Kq2vX9mLp0a", "title": "Q3 planning", "tags": ["planning", "work"], "updated_at": "2026-11-16T18:04:11Z"},
    {"id": "note_3Zr7tB1cNw5e", "title": "Standup notes", "tags": ["work"], "updated_at": "2026-11-15T09:30:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c_eyJvIjoyfQ",
  "limit": 2,
  "estimated_total": 14
}
```

`notectl note get note_8Kq2vX9mLp0a --machine`, exit `0`:

```json
{
  "id": "note_8Kq2vX9mLp0a",
  "title": "Q3 planning",
  "body": "Goals:\n- ship export\n- cut p95 latency",
  "tags": ["planning", "work"],
  "created_at": "2026-11-01T12:00:00Z",
  "updated_at": "2026-11-16T18:04:11Z"
}
```

`notectl note find --query "p95 latency" --machine`, exit `0`:

```json
{
  "items": [
    {"id": "note_8Kq2vX9mLp0a", "title": "Q3 planning", "tags": ["planning", "work"], "score": 0.91, "snippet": "…ship export\n- cut p95 latency"}
  ],
  "has_more": false,
  "limit": 20
}
```

`printf 'Call the vendor' | notectl note create --machine --title "Follow-ups" --tag work --idempotency-key 2f6c1d --body-file -`, exit `0`:

```json
{
  "id": "note_Yt4pQ0sW2kLm",
  "title": "Follow-ups",
  "body": "Call the vendor",
  "tags": ["work"],
  "created_at": "2026-11-17T14:22:05Z",
  "updated_at": "2026-11-17T14:22:05Z"
}
```

`notectl note delete note_3Zr7tB1cNw5e --dry-run --machine`, exit `0`:

```json
{"dry_run": true, "planned_action": "delete", "id": "note_3Zr7tB1cNw5e", "title": "Standup notes"}
```

`notectl note delete note_3Zr7tB1cNw5e --machine`, exit `0`:

```json
{"id": "note_3Zr7tB1cNw5e", "deleted": true}
```

`notectl note export --output /home/agent/notes.ndjson --machine`, exit `0`:

```json
{
  "path": "/home/agent/notes.ndjson",
  "byte_size": 48213,
  "content_hash": "sha256:9b74c9897bac770ffc029102a200c5de4d1b5d5a4f3c8e7f6a5b4c3d2e1f0a9b",
  "format": "ndjson",
  "note_count": 37,
  "exported_at": "2026-11-17T14:25:40Z"
}
```

## 5. Example error payloads (stderr, machine mode; stdout empty)

Not found — `notectl note get note_000000000000 --machine`, exit `3`:

```json
{
  "code": "NOTE_NOT_FOUND",
  "message": "Note not found.",
  "resource_id": "note_000000000000",
  "hint": "Use note find or note list to locate the ID.",
  "request_id": "req_5a1f",
  "temporary": false
}
```

Validation — `notectl note create --title "" --body-file b.txt --machine`, exit `2`:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Title must be 1-200 characters.",
  "field": "--title",
  "details": {"min_length": 1, "max_length": 200, "received_length": 0},
  "hint": "Pass a non-empty --title; other flags are valid.",
  "temporary": false
}
```

Rate limited — any networked command, exit `6`:

```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 30000,
  "request_id": "req_9c2e",
  "temporary": true
}
```

Unauthenticated — `notectl note list --isolated --machine` with no `NOTECTL_TOKEN`, exit `4`:

```json
{
  "code": "UNAUTHENTICATED",
  "message": "No credential found.",
  "details": {"sources_checked": ["env:NOTECTL_TOKEN"], "skipped_by_isolated": ["file"]},
  "hint": "Set NOTECTL_TOKEN in the environment.",
  "temporary": false
}
```

Timeout on a mutation — `notectl note create ... --machine` without an idempotency key, exit `7`:

```json
{
  "code": "TIMEOUT",
  "message": "Request timed out; the note may have been created.",
  "details": {"timeout_ms": 10000, "outcome": "unknown"},
  "hint": "Before retrying, check with note find using the same title, or retry with --idempotency-key.",
  "temporary": false
}
```

Export target exists — exit `8`:

```json
{
  "code": "OUTPUT_EXISTS",
  "message": "Output file already exists.",
  "field": "--output",
  "path": "/home/agent/notes.ndjson",
  "hint": "Add --overwrite or choose a different --output.",
  "temporary": false
}
```

## 6. Implementation and tests

Result-then-render: typed inputs, typed success and error payloads, separate human and machine renderers.
`--help`, `schema`, and `schema --fingerprint` load no HTTP client, read no credentials, and target <100 ms.
Ship tests for: schema snapshot and fingerprint change on any contract diff; each success payload above; each error payload with its declared exit code (runtime check that catalog exits match observed exits); TTY vs non-TTY per stream; `--machine` suppressing prompts/color/progress; `--body-file -` with empty, oversized, and TTY stdin; pagination and `CURSOR_EXPIRED`; export atomicity, interrupt cleanup, and concurrent same-path exports; env/config precedence and `--isolated`; dry-run output differs from real output and causes no remote write; interrupt during create/delete.

## 7. Checklist walk

- Command Model: `noun verb`, shallow, conventional verbs (`list/get/find/create/delete`) plus `export`; ID is the single positional selector; conventional flag names.
- Machine Schema: all items declared above, including units (`--timeout-ms`), shape dialect, per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`, latency classes, compatibility promise, fingerprint scope.
- Stdin Contract: declared per command; only `create --body-file -` reads stdin, explicitly, never blocking in machine mode.
- Shell Safety: `--` supported and declared; IDs, titles, queries never reach a shell; hints carry no shell strings built from input; examples quote values.
- Agent-Safe Invocation: single `--machine` profile; `--isolated` distinct; per-stream non-TTY; non-interactive bootstrap via env/credential file; fast metadata paths; `--timeout-ms` and retry defaults declared.
- Output: stdout payload only; `single-error-object` stderr framing; classes declared; pagination with cursor contract; deterministic sorts; projection rule; UTC timestamps; `--output` only on export, returning path/size/hash.
- Errors And Exit Codes: required fields on every error; `temporary` always present; `retry_after_ms` on rate limits; secrets redacted.
  Partial failure: not applicable — no multi-item mutating command (export fails atomically as a whole).
- Ambient State: sources, precedence, disabling, `whoami` and `config show --resolved`, no secrets in argv.
- Mutations And Long-Running Work: explicit verbs, `--dry-run` on create/delete, `--if-exists`, idempotency key, reconciliation and signal semantics, atomic local writes.
  Job IDs/polling/cancel: not applicable — no async operation; export is synchronous and interruptible with cleanup.
- Side Effects And Telemetry: reads never write remotely; no telemetry or update checks.
- Prose Surfaces: summaries are rules-first and name the sibling to use instead (`list` vs `find`).
- Tests: listed in §6.
~~~~~~
