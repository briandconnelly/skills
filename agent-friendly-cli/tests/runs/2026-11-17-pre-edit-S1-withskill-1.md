# Scenario 1 (design) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 10/11 scored; 2/2 conformance
- **Tokens:** 79,659 (final-turn context plus output, read from the transcript)
- **Output words:** 3,841
- **Transcript sha256:** `702154fff54e8bad87e5922bea45ff16f20ab9497e9bcd62af1b748a061fd360` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; --machine declared in global_flags Parts: profile declared in schema = pass; named flags declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {"0": "success", ...}; "symbolic_error_codes"; delete "errors_possible" Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object" Parts: stdout success only = pass; stderr structured failures with framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "confirmation": "the explicit delete verb is the trigger"; {"dry_run":true,"planned_action":"delete"...} Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": "boolean", "next_cursor?": "string" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size":48213,"content_hash":"sha256:9f86..." |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl auth whoami", ...], "disable_with": {"--isolated": ...} Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl --machine note delete --if-exists -- 'nt_01HX9' |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | INTERNAL listed and exit 1 "generic/internal", but no statement mapping unanticipated failures to it; API_UNAVAILABLE listed per networked command; no rule for unlisted codes Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = pass; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag <tag>]... (repeated flag); "cardinality": "many" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "`--output` only on export" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "output": {"class": "list"...}; "alternate_outputs": {"--dry-run": {"class": "record" |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design).
Task: new CLI design, so this follows the design workflow and is checked against every contract-checklist section (see "Checklist coverage" at the end).

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | ids, titles, tags, `updated_at`, pagination |
| Get a note | inspect | note id | full record |
| Search notes | query | query text | ids, titles, tags, match score, pagination |
| Create a note | mutate | title, body (stdin or file), tags | created record (with id) |
| Delete a note | mutate | note id | deleted id + status |
| Export all notes | mutate (local file write) | output path | path, byte size, content hash, count |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

`list` and `find` are distinguishable without prose: `list` enumerates by exact filters (tag), `find` ranks by free-text relevance.
No `update` verb is requested, so none is designed (it would be an additive change later).

## 2. Command surface

Pattern: `notectl <noun> <verb>`, shallow tree, one primary selector per resource (note id, positional).

```text
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <token>] [--sort updated_at|created_at|title] [--select <field>]...
notectl note get    [--select <field>]... [--] <id>
notectl note find   --query <text> [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]...
notectl note create --title <text> [--tag <tag>]... [--body-file <path> | --body-stdin] [--idempotency-key <key>] [--dry-run]
notectl note delete [--if-exists] [--dry-run] [--] <id>
notectl note export --output <path> [--format json|ndjson] [--overwrite] [--dry-run]

notectl schema [<command path>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth status          # credential source, never the secret
notectl config show --resolved
```

Global flags: `--machine` (canonical machine profile; implies `--json --no-input --no-color --no-progress`), `--json`, `--no-input`, `--no-color`, `--no-progress`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`, `--debug`.

Canonical machine invocations (values quoted; options before `--`):

```sh
notectl --machine note list --tag 'work' --limit 50
notectl --machine note get -- 'nt_01HX9'
notectl --machine note find --query 'quarterly plan' --limit 20
printf '%s' "$BODY" | notectl --machine note create --title 'Standup 2026-11-17' --tag 'work' --body-stdin --idempotency-key 'run-42-note-1'
notectl --machine note delete --if-exists -- 'nt_01HX9'
notectl --machine note export --output './notes-export.ndjson' --format ndjson
```

Prose surfaces (help/summary/`description`) are written rules-first:

- `note list`: "Lists notes filtered by exact tag; deterministic order (default `updated_at` desc, then `id`). Use `note find` for free-text search."
- `note find`: "Ranks notes by relevance to `--query` (title and body). Requires `--query`. Use `note list` for exact tag filtering."
- `note create`: "Creates one note. Body comes from `--body-file` or `--body-stdin` only; never waits on a terminal. Retry-safe only with `--idempotency-key`."
- `note delete`: "Permanently deletes one note by id. Not reversible. `--if-exists` makes a missing note a success."
- `note export`: "Writes all notes to `--output`; refuses to overwrite unless `--overwrite`. Returns path, byte size, hash, count — never note content on stdout."

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, a string-valued shape describes an NDJSON record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7f3e91a0",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "full command contract; tool version is NOT an input",
  "compatibility": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes on existing exits"],
    "breaking": ["removals", "renames", "type or meaning changes", "exit-code remapping", "required-field changes"],
    "rule": "any contract change changes the fingerprint; breaking changes bump the major version"
  },
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields are required unless so marked or removed by a declared projection; a string-valued shape describes an NDJSON record sequence",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode on failure, the structured error object is the only stderr content and stdout is empty (except export/list partial cases declared per command); on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC 3339 UTC (Z)", "numbers": "locale-independent JSON numbers", "paths": "as given by the caller, plus absolute_path in POSIX style"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-input", "--no-color", "--no-progress"], "description": "Machine mode: no prompts, color, progress, pager, or browser; structured output only. Also implied by none of TTY detection — pass it explicitly."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Structured JSON output on stdout, structured errors on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config file and cache. Credentials are then read only from NOTECTL_TOKEN; authenticated commands still work when it is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore the config file only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "Remote API base URL."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "minimum": 100, "maximum": 600000, "default": "per command (see timeout_defaults_ms)", "description": "Per-request network timeout."},
    {"name": "--debug", "type": "boolean", "default": false, "description": "Opt-in redacted request/response diagnostics on stderr. Machine mode wraps them under ndjson-typed framing only when combined; without --debug, framing is single-error-object."}
  ],
  "auth": {
    "required_for": ["note list", "note get", "note find", "note create", "note delete", "note export", "auth whoami"],
    "not_required_for": ["schema", "auth status", "config show"],
    "credential_requirements": ["API token with scope notes:read (reads, export) or notes:write (create, delete)"],
    "sources_precedence": ["NOTECTL_TOKEN env var", "credential file ~/.config/notectl/credentials (mode 0600)", "OS keychain entry notectl/<profile>"],
    "secret_intake": "env var, credential file, keychain, or `notectl auth login --token-stdin`; no flag accepts a token value",
    "non_interactive_bootstrap": "printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine, or set NOTECTL_TOKEN",
    "redaction": "tokens never appear in stdout, stderr, debug output, or examples; auth status reports source and last-4 only"
  },
  "ambient_state": {
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (fallback ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "NO_COLOR"],
    "caches": [{"path": "$XDG_CACHE_HOME/notectl/schema.json", "purpose": "none for data; only server capability metadata", "writes_on_read_commands": false}],
    "precedence": "flags > environment variables > config file > cache",
    "disable_with": {"--isolated": "config file and cache", "--no-config": "config file only"},
    "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"],
    "secret_values": ["token"],
    "local_writes": "auth login writes the credential file by atomic rename; concurrent writes are last-writer-wins"
  },
  "side_effects_policy": {"telemetry": "none", "update_checks": "none", "network": "only the declared API calls for each command"},
  "exit_codes": {"0": "success", "1": "generic/internal", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified", "10": "output file write failed (domain-specific)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "OUTPUT_EXISTS", "IDEMPOTENCY_CONFLICT", "TRANSIENT", "API_UNAVAILABLE", "OUTPUT_WRITE_FAILED", "EXPORT_INCOMPLETE"],
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "string[]", "created_at": "string", "updated_at": "string"},
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "find": "notectl note find --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command path>]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Lists notes filtered by exact tag; deterministic order. Use note find for free-text search.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "Match notes having ALL given tags (exact, case-sensitive).", "examples": ["work"]},
        {"name": "--limit", "type": "integer", "minimum": 1, "maximum": 200, "default": 50},
        {"name": "--cursor", "type": "string", "default": null, "description": "Opaque next_cursor from a previous page."},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "updated_at/created_at sort descending, title ascending; ties broken by id ascending."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "note_shape[] (projected)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "size_mode": "paged; body excluded by default to bound size",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort, not snapshot-consistent"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "API_UNAVAILABLE", "TIMEOUT"], "backoff": "exponential from 200ms with jitter", "honors_retry_after": true},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Returns one note by id, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[0-9A-Z]{5,}$", "cardinality": "one", "examples": ["nt_01HX9"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "small (body max 1 MiB)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "API_UNAVAILABLE", "TIMEOUT"], "honors_retry_after": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note find --query <text>",
      "summary": "Ranks notes by relevance to --query over title and body. Use note list for exact tag filtering.",
      "aliases": [{"name": "note search", "status": "migration-only, not canonical"}], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "Restrict to notes having ALL given tags."},
        {"name": "--limit", "type": "integer", "minimum": 1, "maximum": 100, "default": 20},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "(note_shape projected) + {score: number, snippet?: string}", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected note fields are present; id and score are always present"},
        "sort": "score descending, ties by id ascending",
        "size_mode": "paged; snippet max 200 chars",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "API_UNAVAILABLE", "TIMEOUT"], "honors_retry_after": true},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text>",
      "summary": "Creates one note. Body from --body-file or --body-stdin only. Retry-safe only with --idempotency-key.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_items": 20},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Server deduplicates for 24h: a retry with the same key and same input returns the original note; different input fails IDEMPOTENCY_CONFLICT."},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "body_default": "empty string when neither --body-file nor --body-stdin is given",
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["UTF-8 text"], "maximum_input_size": 1048576, "can_block": "only if --body-stdin is given and the writer never closes; a TTY stdin with --body-stdin in machine mode fails VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body-file"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": {"note": "note_shape", "idempotent_replay": "boolean"}, "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "create", "note": {"title": "string", "tags": "string[]", "body_bytes": "integer"}}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates input locally and via the API's validate endpoint; no note is created; output carries dry_run: true"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "description": "never auto-retried without --idempotency-key; with a key, retries 2 on TRANSIENT/API_UNAVAILABLE/TIMEOUT"},
      "reconciliation": "on TIMEOUT or interrupt the outcome is unknown. With --idempotency-key, re-run the identical command (safe). Without one, run notectl note find --query <title> to check for the note before retrying.",
      "signals": "SIGINT/SIGTERM abort the client; a request already sent may still commit server-side; no local state is written",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently deletes one note by id. Not reversible. --if-exists makes a missing note a success.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[0-9A-Z]{5,}$", "cardinality": "one", "examples": ["nt_01HX9"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "confirmation": "the explicit delete verb is the trigger; never prompts",
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|already_absent"}, "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "size_mode": "small"}
      },
      "flag_combinations": {"--dry-run --if-exists": "missing note yields {dry_run: true, planned_action: \"none\", id} with exit 0"},
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "performs a read (GET) only"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT or interrupt run notectl note get <id>: NOTE_NOT_FOUND means the delete committed. Retrying with --if-exists is always safe.",
      "signals": "SIGINT/SIGTERM abort the client; a request already sent may commit server-side; no local state",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Writes all notes to --output. Refuses to overwrite unless --overwrite. Stdout carries only path, size, hash, and count.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "remote_read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "examples": ["./notes-export.ndjson"]},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "File format. ndjson: one note_shape per line, sorted by id; json: {notes: note_shape[], exported_at}."},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "absolute_path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "json|ndjson", "exported_at": "string", "consistency": "best-effort"}, "size_mode": "small pointer; file grows with data"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "export", "path": "string", "would_overwrite": "boolean", "estimated_note_count?": "integer"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": false, "writes": ["local file at --output"], "dry_run": "one count request; no file is created"},
      "atomicity": "writes to <path>.notectl-tmp-<pid> in the same directory, fsyncs, then renames; on failure or interrupt the temp file is removed and <path> is untouched",
      "latency_class": "slow", "timeout_defaults_ms": 30000,
      "timeout_scope": "per page request; whole export has no global cap",
      "retry_defaults": {"retries": 3, "on": ["TRANSIENT", "API_UNAVAILABLE", "TIMEOUT", "RATE_LIMITED"], "honors_retry_after": true, "description": "page fetches are reads, so retries are safe"},
      "reconciliation": "safe to re-run; the output file exists only if the export completed",
      "signals": "SIGINT/SIGTERM delete the temp file; no partial output file is left",
      "progress": "human mode only, on stderr; suppressed by --machine",
      "async": false, "streaming": false, "pagination": "internal (walks all pages)", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "API_UNAVAILABLE", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10},
        {"code": "EXPORT_INCOMPLETE", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command path>]",
      "summary": "Prints this contract. --fingerprint prints only {schema_version, fingerprint, fingerprint_scope}. --summary prints command names and summaries only.",
      "classification": "discover", "read_only": true,
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "full schema ~20 KB; per-command or --summary for less"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "performance": "target <100ms; no network, no auth validation, no plugin loading",
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Returns the authenticated account for the resolved credential. Network call.",
      "classification": "admin", "read_only": true,
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "string[]", "api_url": "string"}},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "errors_possible": [{"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "API_UNAVAILABLE", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl auth status",
      "summary": "Reports where the credential comes from, without contacting the API or printing the secret.",
      "classification": "admin", "read_only": true,
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"credential_present": "boolean", "source": "env:NOTECTL_TOKEN|file|keychain|none", "token_last4?": "string", "profile": "string"}},
      "latency_class": "local",
      "errors_possible": []
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Prints the resolved configuration with the source of each value. Secrets redacted.",
      "classification": "admin", "read_only": true,
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"values": "{<key>: {value: any, source: flag|env|config|default}}", "config_file?": "string", "isolated": "boolean"}},
      "latency_class": "local",
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

`notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a0", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, `--machine`)

`notectl --machine note list --tag 'work' --limit 2` (exit 0):

```json
{"items":[{"id":"nt_01HXB","title":"Standup 2026-11-17","tags":["standup","work"],"updated_at":"2026-11-17T16:02:11Z"},{"id":"nt_01HX9","title":"Q4 plan","tags":["planning","work"],"updated_at":"2026-11-15T09:40:00Z"}],"has_more":true,"next_cursor":"c2Vjb25k","limit":2,"estimated_total":14}
```

`notectl --machine note get -- 'nt_01HX9'` (exit 0):

```json
{"id":"nt_01HX9","title":"Q4 plan","body":"Ship v2 of the importer.\nHire one SRE.","tags":["planning","work"],"created_at":"2026-10-02T18:11:05Z","updated_at":"2026-11-15T09:40:00Z"}
```

`notectl --machine note find --query 'importer' --limit 1` (exit 0):

```json
{"items":[{"id":"nt_01HX9","title":"Q4 plan","tags":["planning","work"],"updated_at":"2026-11-15T09:40:00Z","score":0.91,"snippet":"Ship v2 of the importer."}],"has_more":false,"limit":1}
```

`printf '%s' 'Notes from standup' | notectl --machine note create --title 'Standup 2026-11-17' --tag 'work' --body-stdin --idempotency-key 'run-42-note-1'` (exit 0):

```json
{"note":{"id":"nt_01HXB","title":"Standup 2026-11-17","body":"Notes from standup","tags":["work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:02:11Z"},"idempotent_replay":false}
```

`notectl --machine note delete --dry-run -- 'nt_01HX9'` (exit 0):

```json
{"dry_run":true,"planned_action":"delete","id":"nt_01HX9","title":"Q4 plan"}
```

`notectl --machine note delete -- 'nt_01HX9'` (exit 0):

```json
{"id":"nt_01HX9","status":"deleted"}
```

`notectl --machine note export --output './notes-export.ndjson'` (exit 0, artifact):

```json
{"path":"./notes-export.ndjson","absolute_path":"/home/agent/work/notes-export.ndjson","byte_size":48213,"content_hash":"sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08","note_count":137,"format":"ndjson","exported_at":"2026-11-17T16:05:00Z","consistency":"best-effort"}
```

## 5. Example error payloads (stderr only, stdout empty, `--machine`)

Not found — `notectl --machine note get -- 'nt_404XX'`, exit 3:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"nt_404XX","hint":"Check the id with note list or note find.","request_id":"req_8c1f2","temporary":false}
```

Validation — `notectl --machine note create --title '' --body-stdin`, exit 2:

```json
{"code":"VALIDATION_ERROR","message":"Title must be 1-200 characters.","field":"--title","details":{"min_length":1,"max_length":200,"received_length":0},"hint":"Pass a non-empty --title; other inputs are unchanged.","temporary":false}
```

Rate limited — any networked command, exit 6:

```json
{"code":"RATE_LIMITED","message":"API rate limit exceeded.","retry_after_ms":15000,"request_id":"req_77ab0","temporary":true}
```

Unauthenticated — no credential resolved, exit 4:

```json
{"code":"UNAUTHENTICATED","message":"No API token found.","details":{"sources_checked":["env:NOTECTL_TOKEN","file:~/.config/notectl/credentials","keychain:notectl/default"]},"hint":"Set NOTECTL_TOKEN or pipe a token to auth login --token-stdin.","temporary":false}
```

Unknown-outcome mutation — `note create` without an idempotency key times out, exit 7:

```json
{"code":"TIMEOUT","message":"Request timed out after 10000 ms; the note may or may not have been created.","details":{"timeout_ms":10000,"reconcile_with":{"command":"note find","flags":{"--query":"Standup 2026-11-17"}}},"hint":"Check for the note before retrying, or retry with --idempotency-key.","temporary":false}
```

Export target exists — exit 8:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"./notes-export.ndjson","hint":"Pass --overwrite or choose a different --output.","temporary":false}
```

## 6. Behavior notes and tests

- Machine mode never prompts; non-TTY is evaluated per stream (stdout: rendering/pager, stderr: color/progress, stdin: prompts).
  Machine mode still surfaces deprecations, retries exhausted, and version mismatch — as structured fields or as the error — never as hidden prose.
- Architecture: typed inputs → typed result/error → separate human and machine renderers; `schema`, `--help` load no network/auth code (sub-100ms target).
- No telemetry or update checks; reads do no writes.
- Contract tests to ship: schema snapshot and fingerprint stability; canonical success payloads per command; each declared error payload and its exit code observed at runtime; TTY vs non-TTY and `--machine` suppression; `--body-stdin` with empty stdin and with TTY stdin; pagination and `CURSOR_EXPIRED`; export artifact hash/size and atomic rename under SIGINT; flag/env/config precedence and `--isolated`; `note search` alias resolution; dry-run output for create/delete/export; interrupt behavior of create/delete; concurrent `auth login` writes to the credential file.

## Checklist coverage

- Command Model: `notectl note <verb>`, conventional verbs (`list/get/find/create/delete`), positional id as sole selector, conventional flags (`--limit`, `--output`, `--format`, `--timeout-ms`); `note search` declared as migration alias only.
- Machine Schema: all items declared above, including shape dialect, units (`--timeout-ms`), latency classes, per-command error catalogs, fingerprint + scope + compatibility policy.
- Stdin Contract: declared per command; only `note create --body-stdin` reads stdin, explicitly flagged.
- Shell Safety: `--` supported and declared; examples quoted with options before `--`; hints carry no shell strings built from caller input (repairs expressed as flag values).
- Agent-Safe Invocation: single `--machine` profile; `--isolated` distinct and still allows authenticated reads via `NOTECTL_TOKEN`; non-interactive bootstrap via `auth login --token-stdin`; caller-settable timeout.
- Output: stdout payload only; `single-error-object` stderr framing; one output class per command with declared alternates; pagination/cursor contract; `--select` projection rule; deterministic sorts; UTC timestamps; `--output` only on export, returning path/size/hash.
- Errors And Exit Codes: 0–10 declared; required `code/message/temporary` on every error; `retry_after_ms` on rate limit; `field` names published flags; repair data in `details`.
  Partial failure: not applicable — no multi-item command; export is all-or-nothing (`EXPORT_INCOMPLETE`, no file written).
- Ambient State: sources, precedence, disable flags, inspection (`auth whoami`, `auth status`, `config show --resolved`), redaction, no secrets via argv.
- Mutations And Long-Running Work: explicit verbs, `--dry-run` on all mutations with distinct output, `--if-exists`, `--idempotency-key`, reconciliation paths, signal semantics, atomic local writes.
  Job IDs/polling/cancel: not applicable — no command is async; export is synchronous and safely re-runnable.
- Side Effects And Telemetry: none beyond declared API calls and the export file.
- Prose Surfaces: summaries rules-first and sibling-selective (`list` vs `find`).
- Tests: listed in §6.
~~~~~~
