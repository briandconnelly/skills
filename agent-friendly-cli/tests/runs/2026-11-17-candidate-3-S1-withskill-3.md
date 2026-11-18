# Scenario 1 (design) — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 2/2 conformance
- **Tokens:** 81,848 (final-turn context plus output, read from the transcript)
- **Output words:** 4,203
- **Transcript sha256:** `7e6f0ee7b2c651999dbf99c8313471677174dd03250d3a3879fee7e22b5834a4` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; --machine in global_flags Parts: profile declared in schema = pass; every flag it names declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {"0": "success", ... "symbolic_error_codes" ...; delete "errors_possible" Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object" Parts: stdout success only = pass; stderr structured with declared framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "--dry-run": {... "shape": {"dry_run": true, "planned_action": "delete\|none" Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more":true,"next_cursor":"c2NhbjpwYWdlMg" Parts: has_more = pass; navigation token = pass |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | {"path":"/home/agent/work/notes-export.ndjson","byte_size":48213,"content_hash":"sha256:... Parts: pointer to file = pass; size = pass; hash = pass |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--deadline-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl config show --resolved", "notectl auth whoami"]; "disable_with": {"all": "--isolated" Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note delete --machine --if-exists -- 'note_8f2a' Parts: options before -- = pass; only operands after = pass |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL"; TRANSIENT exit 9 "transport failures other than timeout" in every networked catalog; "unknown_code_policy" (auth login listed in command_tree only, not declared networked) Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unknown-code policy = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | "cardinality": "many", "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | `--output` only on export |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "alternate_outputs": {"--dry-run": {"class": "record" Parts: one output class per command = pass; switching flag declares switch = pass |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design).
Task: new CLI design, so this follows the design workflow and is checked against every contract-checklist section at the end.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | ids, titles, tags, `updated_at`, paging token |
| Get a note | inspect | note id | full record |
| Search notes | query | query text, optional `--tag` | ids, titles, tags, match snippet, paging token |
| Create a note | mutate | title; body (flag, file, or stdin); tags | created record (id) |
| Delete a note | mutate | note id | id + `deleted`/`absent` status |
| Export all notes | mutate (local file) | output path | path, byte size, content hash, count |
| Discover contract | discover | none | schema / fingerprint |
| Inspect identity/config | admin | none | resolved identity and config sources |

`list` and `search` stay separate: `list` is a deterministic enumeration with filters and no ranking; `search` is relevance-ranked full-text over title and body.
One-line summaries are enough to tell them apart (see command summaries below).

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for notes: the note ID, as the single positional argument where one exists.
All commands accept `--` end-of-options; only operands follow it.

```text
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]... [--sort <key>]
notectl note get     <id> [--select <field>]...
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]...
notectl note create  --title <text> [--body <text> | --body-file <path|->] [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete  <id> [--if-exists] [--dry-run]
notectl note export  --output <path> [--format json|ndjson] [--tag <tag>]... [--overwrite] [--dry-run]
notectl schema       [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl config show  --resolved
```

Global flags on every command: `--machine`, `--json`, `--no-progress`, `--no-color`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`.

Command summaries (rules first, then context):

- `note list`: Enumerate notes in deterministic order (default `--sort updated_at_desc`, ties by `id`); exact tag filters only, no text matching. Use `note search` for text queries.
- `note get`: Fetch one note by exact ID, including body. Fails `NOTE_NOT_FOUND` (exit 3) if absent.
- `note search`: Relevance-ranked full-text search over title and body; requires `--query`. Results omit `body` by default; fetch it with `note get`.
- `note create`: Creates a new note on the remote API. Not idempotent unless `--idempotency-key` is supplied; supply one whenever you may retry.
- `note delete`: Permanently deletes one note by ID. Use `--if-exists` to make it repeat-safe.
- `note export`: Writes all (or tag-filtered) notes to a local file atomically; prints path, size, hash. Read-only on the remote API.
- `schema`: Prints the machine contract; `--fingerprint` prints only the cache key. Local, no network, no auth.

Canonical examples (values quoted; options before `--`):

```sh
notectl note list --machine --tag 'work' --limit 50
notectl note get --machine -- 'note_8f2a'
notectl note search --machine --query 'quarterly plan' --limit 20
printf '%s' "$BODY" | notectl note create --machine --title 'Standup 2026-11-17' --tag 'work' --body-file - --idempotency-key 'c0ffee-01'
notectl note delete --machine --if-exists -- 'note_8f2a'
notectl note export --machine --output './notes-export.ndjson' --format ndjson
notectl schema --fingerprint
```

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum; a trailing `?` marks an optional field; fields are required unless so marked or removed by a declared projection; `[T]` is an array of T; a string-valued shape describes an NDJSON record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-7e41c09b",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this document minus the fingerprint field; tool version is not an input",
  "compatibility": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes on a command's catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "changed defaults that alter output"],
    "rule": "any contract change changes the fingerprint; breaking changes bump the major schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields required unless so marked or removed by a declared projection; [T] is an array; a string-valued shape describes an NDJSON record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC 3339 UTC with Z suffix", "numbers": "locale-independent JSON numbers"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Non-interactive: never prompts, no pager, no browser launch, structured output only on every stream regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Structured JSON (or NDJSON where declared) on stdout."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config file, keychain, and cache. Credentials must then come from NOTECTL_TOKEN or NOTECTL_TOKEN_FILE; API URL from --api-url or NOTECTL_API_URL."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore the config file only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to use. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "Remote API base URL. Overrides NOTECTL_API_URL and config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "Per-request network timeout. Per-command defaults below override the global default."}
  ],
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"whoami": "notectl auth whoami", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"}
  },
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
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "IDEMPOTENCY_KEY_REUSED", "TRANSIENT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "debug": {"flag": "--debug", "default": false, "description": "Adds request/response metadata as a details.debug object on errors; Authorization headers and tokens are always redacted as \"[REDACTED]\"."},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
  "ambient_state": {
    "credentials": {
      "sources_in_precedence": ["NOTECTL_TOKEN env", "NOTECTL_TOKEN_FILE env (path to file)", "OS keychain entry notectl/<profile>", "none"],
      "isolated_mode_sources": ["NOTECTL_TOKEN", "NOTECTL_TOKEN_FILE"],
      "secret_values": ["token"],
      "redaction": "never printed; config show and whoami report source and a fingerprint (last 4 chars), never the value",
      "argv_secrets_accepted": false,
      "non_interactive_bootstrap": "printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine  (stores in keychain); or set NOTECTL_TOKEN with no login step"
    },
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_TOKEN_FILE", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "NO_COLOR"],
    "caches": [{"path": "$XDG_CACHE_HOME/notectl/schema-fingerprint", "purpose": "none in v1 — notectl keeps no data cache; listed for completeness", "reads": false, "writes": false}],
    "cwd_selects_context": false,
    "precedence": "flags > environment variables > config file > built-in defaults",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl config show --resolved", "notectl auth whoami"],
    "local_state_writes": "only auth login writes (keychain); config file is never written by notectl in v1"
  },
  "telemetry": {"enabled_by_default": false, "update_checks": false, "description": "No telemetry or update checks exist in v1."},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes in deterministic order with exact tag filters; no text matching (use note search).",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "description": "Notes must carry all given tags (AND).", "examples": ["work"]},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null, "description": "Opaque next_cursor from a previous page; other flags must match the original call."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "created_at", "updated_at"]},
        {"name": "--sort", "type": "enum", "enum": ["updated_at_desc", "updated_at_asc", "created_at_desc", "title_asc"], "default": "updated_at_desc", "description": "Ties broken by id ascending."},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present on each item; unselected fields are absent, not null; id is always present"},
        "body_default": "body is excluded by default to bound size; request it with --select body",
        "size_mode": "bounded by --limit (max 500)",
        "pagination": {"token": "next_cursor", "present_when": "has_more is true", "opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run the same command without --cursor", "consistency": "best-effort; notes created or deleted during a walk may be missed or skipped"},
        "truncation": "none; paging only"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "backoff": "exponential from 500ms, honors retry_after_ms"},
      "async": false, "streaming": false, "artifact": false,
      "signal_semantics": {"interrupt": "exits 130 with no output; no state", "closed_stdout": "exits quietly"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
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
      "summary": "Fetch one note by exact ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent, not null; id always present"}, "size_mode": "small; body capped by API at 1 MiB"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "signal_semantics": {"interrupt": "exits 130 with no output; no state", "closed_stdout": "exits quietly"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
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
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Relevance-ranked full-text search over title and body; body omitted by default (fetch with note get).",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at", "score", "snippet"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at", "score", "snippet"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[note projected by --select, plus score: number and snippet: string]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields present; unselected absent, not null; id always present"},
        "sort": "score descending, ties by id ascending (deterministic for a fixed index state)",
        "size_mode": "bounded by --limit (max 100); snippet capped at 200 characters",
        "pagination": {"token": "next_cursor", "opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "truncation": "snippet is truncated with a trailing … at 200 chars; never the item list"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"]},
      "async": false, "streaming": false, "artifact": false,
      "signal_semantics": {"interrupt": "exits 130 with no output; no state", "closed_stdout": "exits quietly"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
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
      "canonical_invocation_path": "notectl note create --title <text>",
      "summary": "Create a note on the remote API. Not idempotent unless --idempotency-key is supplied on the first attempt.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-file"], "description": "Inline body; prefer --body-file for multi-line or large content."},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body"], "description": "Read body from a file, or from stdin when the value is -."},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Server deduplicates creates with the same key for 24 hours; a reused key with different inputs fails IDEMPOTENCY_KEY_REUSED."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 15000}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--body-file -", "accepted_formats": ["utf-8 text"], "maximum_input_size": 1048576, "can_block": "only if the caller passes --body-file - with an open, unwritten stdin; never waits on a TTY in machine mode (a TTY stdin with --body-file - fails VALIDATION_ERROR)", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "idempotent_replay": "boolean"}, "shape_description": "body is not echoed; idempotent_replay is true when the server returned the note created by an earlier attempt with the same key", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "streaming": false, "size_mode": "small", "description": "validated locally and via the API's validate endpoint; no note is created"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation; calls POST /notes:validate, which may refresh the access token (suppressed under --isolated, where an expired token fails UNAUTHENTICATED instead)"},
      "latency_class": "network", "timeout_defaults_ms": 15000,
      "retry_defaults": {"retries": 0, "description": "notectl never auto-retries create; a create without --idempotency-key is not safe to retry automatically"},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key used on the original attempt within 24 hours. Without a key from the original attempt, no lookup proves the note was not created (list/search can lag the write); do not retry automatically — surface to the user or accept a possible duplicate.",
      "signal_semantics": {"interrupt": "remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "description": "the API rejects before processing, so retry is safe"},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_KEY_REUSED", "exit": 8},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by ID; --if-exists makes it repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "Treat an absent note as success (status absent)."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action none only with --if-exists when the note is absent", "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm it exists; no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists",
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
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write all (or tag-filtered) notes to a local file atomically; print path, size, and hash. Remote API is read only.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "read_only_description": "read-only against the remote API; writes one local file",
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "Destination file. - is rejected: export always writes a file."},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one note_shape record per line. json: {\"notes\": [note_shape]}."},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--overwrite", "type": "boolean", "default": false, "description": "Replace an existing file; otherwise fail OUTPUT_EXISTS."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "Per page request."},
        {"name": "--deadline-ms", "type": "integer", "unit": "ms", "default": 600000, "description": "Whole-command deadline; exceeding it fails TIMEOUT and leaves no partial file."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "ndjson|json", "exported_at": "string"}, "shape_description": "path is absolute; content_hash is sha256:<hex> of the file bytes", "size_mode": "small pointer; file size grows with note count"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "export", "path": "string", "estimated_note_count?": "integer", "would_overwrite": "boolean"}, "streaming": false, "size_mode": "small"}
      },
      "progress": {"framing": "none on stderr in machine mode (stderr_framing single-error-object); human mode shows a page counter on a TTY stderr"},
      "consistency": "best-effort page walk; notes changed during export may appear in either state or be missed",
      "side_effects": {"external_mutation": false, "writes": ["file at --output"], "atomicity": "written to <output>.tmp-<pid> in the same directory, fsynced, then renamed over the target; concurrent exports to the same path are last-writer-wins with no torn files", "dry_run": "no file written; checks write permission on the target directory"},
      "latency_class": "slow", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "scope": "per page request"},
      "reconciliation": "safe to retry automatically: remote side is read-only and the local write is atomic",
      "signal_semantics": {"interrupt": "temp file removed; target untouched; exit 130", "closed_stdout": "finishes the export (pointer is written last)", "local_writes": "atomic rename", "remote_continues": false},
      "async": false, "streaming": false, "pagination": "internal; walks all pages", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>]",
      "summary": "Print the machine contract, one command's contract, or (--fingerprint) only the cache key. Local; no network or auth.",
      "classification": "discover", "read_only": true, "auth": "none",
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false, "description": "One line per command: path and summary."}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "small"},
      "latency_class": "local", "target_latency_ms": 100,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown <command>"}]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Show the authenticated account and which credential source was used; never prints the token.",
      "classification": "admin", "read_only": true, "auth": "required",
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "[string]", "credential_source": "env:NOTECTL_TOKEN|env:NOTECTL_TOKEN_FILE|keychain", "token_suffix": "string"}},
      "latency_class": "network",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show each resolved setting with its value and source; secrets shown only as source and suffix.",
      "classification": "admin", "read_only": true, "auth": "none",
      "output": {"class": "record", "format": "json", "shape": {"settings": "[{name: string, value: string|null, source: flag|env|config|keychain|default, secret: boolean}]", "config_file": "string|null", "isolated": "boolean"}},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "malformed config file; field names the file path in details.path"}]
    }
  ]
}
```

Fingerprint endpoint (`notectl schema --fingerprint`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-7e41c09b", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --machine --tag 'work' --limit 2`

```json
{"items":[{"id":"note_8f2a","title":"Standup 2026-11-17","tags":["work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:05:40Z"},{"id":"note_77c1","title":"Q4 roadmap","tags":["planning","work"],"created_at":"2026-11-10T09:12:00Z","updated_at":"2026-11-16T21:44:03Z"}],"has_more":true,"next_cursor":"c2NhbjpwYWdlMg","limit":2,"estimated_total":37}
```

`notectl note get --machine -- 'note_8f2a'`

```json
{"id":"note_8f2a","title":"Standup 2026-11-17","body":"- shipped export\n- blocked on review","tags":["work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:05:40Z"}
```

`notectl note search --machine --query 'roadmap' --limit 1`

```json
{"items":[{"id":"note_77c1","title":"Q4 roadmap","tags":["planning","work"],"updated_at":"2026-11-16T21:44:03Z","score":0.92,"snippet":"…the Q4 roadmap prioritizes export and search…"}],"has_more":false,"limit":1}
```

`printf '%s' "$BODY" | notectl note create --machine --title 'Standup 2026-11-17' --tag 'work' --body-file - --idempotency-key 'c0ffee-01'`

```json
{"id":"note_8f2a","title":"Standup 2026-11-17","tags":["work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:02:11Z","idempotent_replay":false}
```

`notectl note create --machine --title 'Draft' --dry-run`

```json
{"dry_run":true,"planned_action":"create","title":"Draft","tags":[],"body_bytes":0}
```

`notectl note delete --machine -- 'note_8f2a'`

```json
{"id":"note_8f2a","status":"deleted"}
```

`notectl note delete --machine --if-exists -- 'note_404'`

```json
{"id":"note_404","status":"absent"}
```

`notectl note export --machine --output './notes-export.ndjson'`

```json
{"path":"/home/agent/work/notes-export.ndjson","byte_size":48213,"content_hash":"sha256:9b74c9897bac770ffc029102a200c5de4f3c8e4b7e0a1c5d2f6e8a9b0c1d2e3f","note_count":37,"format":"ndjson","exported_at":"2026-11-17T16:10:02Z"}
```

## 5. Example error payloads (stderr only, stdout empty, machine mode)

Not found — `notectl note get --machine -- 'note_404'`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404","temporary":false,"request_id":"req_01HZX3"}
```

Validation — `notectl note create --machine --title '' --tag 'Work Items'`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid value for --tag.","field":"--tag","details":{"value":"Work Items","pattern":"^[a-z0-9][a-z0-9_-]{0,31}$","other_errors":[{"field":"--title","reason":"min_length","min_length":1}]},"hint":"Use lowercase letters, digits, '_' or '-' in --tag, and a non-empty --title.","temporary":false}
```

Rate limited — `notectl note search --machine --query 'roadmap'`, exit `6` (after the declared 2 internal retries are exhausted):

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"details":{"retries_attempted":2},"request_id":"req_01HZX9"}
```

Timeout on a mutation — `notectl note create --machine --title 'X' --idempotency-key 'k-77'`, exit `7`:

```json
{"code":"TIMEOUT","message":"Create request timed out; outcome unknown.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":15000,"idempotency_key":"k-77"},"hint":"Re-run with the same --idempotency-key value to complete or replay the create.","request_id":"req_01HZXA"}
```

Unauthenticated — any networked command, exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credentials.","temporary":false,"details":{"credential_sources_checked":["env:NOTECTL_TOKEN","env:NOTECTL_TOKEN_FILE","keychain:notectl/default"]},"hint":"Set NOTECTL_TOKEN or run auth login with --token-stdin.","docs_url":"https://docs.notes.example.com/cli/auth"}
```

Export target exists — `notectl note export --machine --output './notes-export.ndjson'`, exit `10`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","path":"/home/agent/work/notes-export.ndjson","field":"--output","hint":"Pass --overwrite, or choose a different --output path.","temporary":false}
```

## 6. Implementation and test notes

- Result-then-render: typed inputs, typed success/error payloads, separate human and machine renderers.
- `--help`, `schema`, and `schema --fingerprint` load no HTTP client, read no credentials, and target <100ms.
- Error boundary catches everything and emits `INTERNAL` (exit 1) in the declared framing; `--debug` adds redacted detail.
- Contract tests: schema snapshot + fingerprint stability; every example payload above as a golden; declared exit code vs observed exit for every catalog entry; TTY vs non-TTY per stream; `--machine` suppresses prompts/color/progress/prose; `--body-file -` with empty, oversized, and TTY stdin; pagination and `CURSOR_EXPIRED`; export atomicity and interrupt (no partial file); concurrent exports to one path; env > config precedence and `--isolated`; dry-run for create/delete/export never byte-identical to real output and makes no mutation; interrupt behavior of create/delete.

## 7. Checklist walk

| Section | Answer |
|---|---|
| Command Model | `note <verb>`, shallow, ID as sole positional, conventional flags, no aliases. |
| Machine Schema | All items declared above (tree, flags, units, profiles, stdin, classification, auth/scope, classes, dialect, exits, catalogs, side effects, latency, timeouts/retries, pagination/artifact, version + fingerprint + compatibility). Deprecations: none in v1 (empty arrays). Async/version negotiation: N/A — no command outlives the process; single API version pinned by the CLI. |
| Stdin Contract | Declared per command; only `create` reads stdin, via explicit `--body-file -`. |
| Shell Safety | `--` declared; values quoted in examples; IDs/queries never shelled; hints carry flag values, not commands built from input. |
| Agent-Safe Invocation | `--machine` profile distinct from `--isolated`; per-stream non-TTY; non-interactive bootstrap via `NOTECTL_TOKEN` or `auth login --token-stdin`; fast metadata path; `--timeout-ms` everywhere networked. |
| Output | stdout payload only; `single-error-object` framing; classes declared; pagination with cursor contract; projection rule; deterministic sort; UTC; `--output` only on export, returning path/size/hash. Streaming: N/A (no stream command; export writes NDJSON to a file, not stdout). |
| Errors And Exit Codes | Required fields on every example; per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`; fallback `INTERNAL`; `TRANSIENT` for transport failures; unknown-code policy; redacted debug. Partial failure: N/A — no multi-item mutation; export is all-or-nothing. |
| Ambient State | Credential/config/env/cache sources, precedence, `--isolated`/`--no-config`, `config show --resolved`, `auth whoami`, no secrets in argv. |
| Mutations And Long-Running Work | Explicit verbs; `--dry-run` on all three writers; create retry-safety via caller key only; delete via `--if-exists`; signal semantics; atomic local write; export deadline. Async jobs: N/A. |
| Side Effects And Telemetry | Reads have no writes; dry-run token refresh documented and suppressed by `--isolated`; no telemetry or update checks. |
| Prose Surfaces | Summaries lead with constraints and separate `list` from `search` without examples. |
| Tests | Listed in §6. |
~~~~~~
