# Scenario 1 (design) — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 2/2 conformance
- **Tokens:** 81,984 (final-turn context plus output, read from the transcript)
- **Output words:** 4,177
- **Transcript sha256:** `0d4006a009bc0e64669e4d9f358a4348a80d8f1d1ed158e81ec7d7189a0d3320` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; --machine in global_flags Parts: profile declared in schema = pass; every flag it names declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes" 0-11; "symbolic_error_codes"; create/delete "errors_possible" Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object" Parts: stdout success only = pass; stderr structured with declared framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | delete "alternate_outputs": {"--dry-run": {... "dry_run": "true", "planned_action": "delete\|none" Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more":true,"next_cursor":"c1.eyJvIjoyfQ" Parts: has_more = pass; navigation token = pass |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size":48213,"content_hash":"sha256:9c1185a5... Parts: pointer to file = pass; size = pass; hash = pass |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl config show --resolved", "notectl auth status", "notectl auth whoami"]; "disable_with": {"all": "--isolated" Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note delete --if-exists --machine -- note_8f2kq1x0ab3c Parts: options before -- = pass; only operands after = pass |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL"; NETWORK_ERROR exit 9 in every declared networked catalog incl. whoami; "unknown_code_policy" (auth status/login "omitted for length", not declared networked) Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unknown-code policy = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | "cardinality": "many", "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "--output only on export with path/size/hash" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "alternate_outputs": {"--dry-run": {"class": "record" Parts: one output class per command = pass; switching flag declares switch = pass |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design). Task: new CLI design.
The design follows the design workflow (task model → command surface → schema → safe defaults → output/errors → tests), and the checklist walk at the end lists every section as answered or not-applicable.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for the next step |
|---|---|---|---|
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at`; pagination fields |
| Get a note | inspect | `id` | full note |
| Search notes | query | `--query` text, optional `--tag` | `id`, `title`, `tags`, `score`, `snippet` |
| Create a note | mutate | `--title`, body (stdin or file), optional `--tag` | created note `id` plus fields |
| Delete a note | mutate | `id` | `id`, `status` |
| Export all notes | admin (bulk read to file) | `--output` path | `path`, `byte_size`, `content_hash`, `note_count` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | discover | none | resolved config, credential source, identity |

`list` and `search` are kept separate because they differ in one sentence: `list` enumerates in a deterministic order with no relevance ranking; `search` ranks by full-text match on `title` and `body`.
No `update` command: it was not requested; adding it later is an additive change.

## 2. Command surface

Pattern: `notectl <noun> <verb>`; the primary selector for a note is its `id`, positional, used only by `get` and `delete`.

```text
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort updated_at|created_at|title] [--select <field>]...
notectl note get     <id> [--select <field>]...
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create  --title <text> [--body-file <path> | --body-stdin] [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete  <id> [--if-exists] [--dry-run]
notectl note export  --output <path> [--format json|ndjson] [--tag <tag>]... [--overwrite] [--dry-run]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami
notectl auth status          # credential source, never the secret
notectl config show --resolved
```

Global flags: `--machine` (implies `--json --no-progress --no-color --no-input`), `--json`, `--no-progress`, `--no-color`, `--no-input`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <ms>`.
All commands accept `--` end-of-options, so an id or query beginning with `-` is safe: `notectl note get --machine -- -abc123`.

Command summaries (rules first, then context):

- `note list` — Read-only. Returns notes in deterministic order (default `updated_at` desc, ties by `id`), paginated by cursor. Use when you want every note or every note with a tag; use `note search` for text matching.
- `note get` — Read-only. Returns one note by exact `id`, including `body`. Fails `NOTE_NOT_FOUND` (exit 3) if absent.
- `note search` — Read-only. Requires `--query`. Ranks notes by full-text relevance over `title` and `body`; returns `snippet`, not full `body`. Use `note get` for the full body.
- `note create` — Mutates remote store. Requires `--title`; body comes only from `--body-file` or `--body-stdin` (never a flag value, so long or shell-hostile text is safe). Pass `--idempotency-key` to make retries safe.
- `note delete` — Mutates remote store; irreversible. `--if-exists` makes it repeat-safe.
- `note export` — Reads all notes and writes them to `--output`; never writes the notes to stdout. Writes atomically; refuses to replace an existing file without `--overwrite`.

## 3. Machine-readable schema

Output of `notectl schema --machine`.
Shape dialect is `notectl-compact-v1`, defined in the schema itself.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new command", "new optional flag", "new optional output field", "new symbolic error code in a catalog"],
    "breaking": ["command or flag removal or rename", "type or meaning change", "required field removal", "exit-code remapping", "output class change"],
    "rule": "every contract change changes the fingerprint; breaking changes bump the major component"
  },
  "fingerprint": "ntc-7f3e91a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_tool_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; [T] is an array of T; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC 3339, UTC, Z suffix", "numbers": "locale-independent", "paths": "as given by caller, absolute in artifact output"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--no-input"], "description": "Machine mode: no prompts, no color, no pager, no browser, structured output only on every stream regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON success payloads on stdout and JSON errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails VALIDATION_ERROR instead."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files, the profile cache, and the OS keychain; credentials come only from NOTECTL_TOKEN or stdin via --token-stdin."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only; still uses keychain and env."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to use. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL. Overrides NOTECTL_API_URL and config."},
    {"name": "--token-stdin", "type": "boolean", "default": false, "description": "Read the API token from the first line of stdin. Mutually exclusive with --body-stdin."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": "per command", "description": "Per-request network timeout; overrides each command's default."}
  ],
  "non_tty_behavior": {"stdout": "non-TTY disables human tables and pager", "stderr": "non-TTY disables color and progress", "stdin": "non-TTY disables prompts"},
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
    "10": "partial failure (export)",
    "11": "local filesystem error (export output)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "TRANSIENT", "NETWORK_ERROR", "PARTIAL_FAILURE", "OUTPUT_WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "a code absent from a command's catalog: act on its payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "debug": {"flag": "--debug", "default": false, "description": "Opt-in structured debug records on stderr; Authorization headers and tokens are redacted. Not part of machine profile."},
  "auth": {
    "required": true,
    "scopes": {"read": ["note list", "note get", "note search", "note export"], "write": ["note create", "note delete"]},
    "credential_sources_precedence": ["--token-stdin", "NOTECTL_TOKEN", "OS keychain entry notectl/<profile>", "credential file ~/.config/notectl/credentials (mode 0600)"],
    "non_interactive_bootstrap": "printf '%s\\n' \"$TOKEN\" | notectl auth login --token-stdin --machine",
    "secret_flags": "none; tokens are never accepted as flag values"
  },
  "ambient_state": {
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN (secret)", "NOTECTL_PROFILE", "NOTECTL_API_URL", "NOTECTL_TIMEOUT_MS", "NO_COLOR"],
    "caches": [],
    "cwd_selects_context": false,
    "precedence": "flags > environment > config file > built-in defaults",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl config show --resolved", "notectl auth status", "notectl auth whoami"],
    "secret_redaction": "resolved token is shown as {source, present: true, last4} only"
  },
  "telemetry": {"default": "off", "update_checks": "off", "opt_in": "config key telemetry=true", "machine_mode": "always suppressed"},
  "local_writes": {"config_and_credentials": "atomic rename; last-writer-wins", "export_output": "write to temp file in the same directory, fsync, atomic rename"},
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"},
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> --body-stdin",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    }
  },
  "aliases": [],
  "deprecations": [],
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "Read-only. Lists notes in deterministic order with cursor pagination. Use note search for text matching.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "min": 1, "max": 200, "default": 50},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "updated_at and created_at sort descending, title ascending; ties broken by id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "examples": ["notectl note list --tag 'work' --limit 20 --machine"],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list",
        "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], created_at: string, updated_at: string, body?: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields appear in each item; unselected fields are absent, not null; id is always present"},
        "size_mode": "paged; body omitted by default",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort, not snapshot-consistent"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "honors retry_after_ms, else exponential from 200ms"},
      "closed_stdout": "exits quietly with 0",
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
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
      "description": "Read-only. Returns one note by exact id, including body.",
      "classification": "inspect",
      "read_only": true,
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[A-Za-z0-9]{12}$", "cardinality": "one", "examples": ["note_8f2kq1x0ab3c"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 3000}
      ],
      "examples": ["notectl note get --machine -- note_8f2kq1x0ab3c"],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "record",
        "format": "json",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"},
        "size_mode": "small; body up to 1 MiB, never truncated"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 3000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
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
      "description": "Read-only. Requires --query. Ranks notes by full-text relevance over title and body; returns snippet, not body.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "description": "Plain text, not a query language; matched case-insensitively."},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "min": 1, "max": 100, "default": 20},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "score", "snippet"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at", "score", "snippet"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "examples": ["notectl note search --query 'quarterly plan' --tag 'work' --machine"],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list",
        "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], updated_at: string, score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "ordering": "score descending, ties by id ascending",
        "projection": {"flag": "--select", "rule": "only selected fields appear; id is always present"},
        "size_mode": "paged; snippet capped at 200 characters, declared by snippet_truncated: true on the item when cut",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "index_lag": "search index is eventually consistent; a note created in the last ~5 s may be missing"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "async": false, "streaming": false, "pagination": true, "truncation": "snippet only, flagged per item", "artifact": false,
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
      "description": "Mutates remote store. Requires --title. Body only from --body-file or --body-stdin. Pass --idempotency-key to make retries safe.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body-file", "--token-stdin"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_count": 20, "default": []},
        {"name": "--idempotency-key", "type": "string", "max_length": 64, "default": null, "description": "Server deduplicates creates with the same key for 24 h and returns the original note with created: false."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "examples": ["printf '%s' \"$BODY\" | notectl note create --title 'Standup notes' --tag 'work' --body-stdin --idempotency-key 'run-42-standup' --machine"],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["text/plain; charset=utf-8", "text/markdown"], "maximum_input_size": 1048576, "can_block": false, "can_block_description": "with --body-stdin and a TTY stdin in machine mode, fails VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body-file", "--token-stdin"], "empty_stdin": "accepted as empty body"},
      "output": {
        "class": "record",
        "format": "json",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "created": "boolean"},
        "shape_description": "created is false when an earlier attempt with the same --idempotency-key already created the note",
        "size_mode": "small"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "size_mode": "small", "description": "validates input and auth scope locally and against the API's validate endpoint; creates nothing"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation; may refresh an expired OAuth token, suppressed under --isolated"},
      "latency_class": "network",
      "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "description": "with --idempotency-key, retries RATE_LIMITED, TIMEOUT, TRANSIENT, NETWORK_ERROR up to 2 times reusing the key; without a key never retries"},
      "reconciliation": "on timeout, interrupt, or transport failure the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24 h. Without a key, the create is not safe to retry automatically; an empty note search or list does not prove the note was not created (index and read lag).",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the create, exits 0"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1, "reconcile_first": true},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "key reused with different title/body/tags"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Mutates remote store; irreversible. --if-exists makes it repeat-safe.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[A-Za-z0-9]{12}$", "cardinality": "one", "examples": ["note_8f2kq1x0ab3c"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "examples": ["notectl note delete --if-exists --machine -- note_8f2kq1x0ab3c"],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action is none when the note is absent and --if-exists is set", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm it exists; no mutation"},
      "latency_class": "network",
      "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "description": "with --if-exists, retries RATE_LIMITED, TIMEOUT, TRANSIENT, NETWORK_ERROR up to 2 times"},
      "reconciliation": "on timeout, interrupt, or transport failure the outcome is unknown; re-run with --if-exists, which is repeat-safe. NOTE_NOT_FOUND from note get shows the note is absent now, not which attempt removed it.",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the delete, exits 0"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
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
      "description": "Reads all notes (optionally filtered by --tag) and writes them to --output atomically. Never writes notes to stdout. Refuses to replace an existing file without --overwrite.",
      "classification": "admin",
      "read_only": true,
      "read_only_description": "no remote mutation; writes only the --output file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "file format: ndjson is one note per line; json is one array"},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--allow-partial", "type": "boolean", "default": false, "description": "keep the file and exit 0 when some notes could not be fetched; output carries partial: true"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 120000, "description": "deadline for the whole export"}
      ],
      "examples": ["notectl note export --output './backup/notes.ndjson' --machine"],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "artifact",
        "format": "json",
        "shape": {"path": "string", "format": "json|ndjson", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "exported_at": "string", "partial": "boolean", "failed_ids?": "[string]"},
        "shape_description": "path is absolute; content_hash is sha256:<hex>; failed_ids present only when partial is true",
        "size_mode": "constant-size pointer; file size grows with note count",
        "file_record_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "consistency": "best-effort page walk; notes changed during export may appear in either state"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "export", "path": "string", "estimated_note_count?": "integer", "would_overwrite": "boolean"}, "size_mode": "small"}
      },
      "progress": {"machine_mode": "none", "human_mode": "stderr progress bar when stderr is a TTY"},
      "side_effects": {"external_mutation": false, "writes": ["--output path", "temp file <output>.notectl-tmp-<pid> in same directory, removed on success or failure"]},
      "latency_class": "slow",
      "timeout_defaults_ms": 120000,
      "retry_defaults": {"retries": 2, "scope": "per page fetch", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "temp file removed; --output untouched (old contents preserved)", "local_writes": "atomic rename", "remote_continues": false, "closed_stdout": "completes the export"},
      "concurrency": "two exports to the same --output: last rename wins; each file is internally complete",
      "async": false, "streaming": false, "pagination": "internal", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "PARTIAL_FAILURE", "exit": 10, "suppressed_by": "--allow-partial", "description": "on_item_failure: continue; file is not written unless --allow-partial"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 11}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>]",
      "description": "Metadata only; no network, no auth. Prints the full schema, one command's entry, --summary index, or --fingerprint.",
      "classification": "discover",
      "read_only": true,
      "latency_class": "local",
      "latency_target_ms": 100,
      "output": {"class": "record", "format": "json"},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown command name; details.known_commands lists valid ones"}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "description": "Read-only, local. Shows each resolved setting with its source; secrets redacted.",
      "classification": "discover", "read_only": true, "latency_class": "local",
      "output": {"class": "record", "format": "json", "shape": {"profile": "{value: string, source: flag|env|config|default}", "api_url": "{value: string, source: flag|env|config|default}", "timeout_ms": "{value: integer, source: flag|env|config|default}", "token": "{present: boolean, source: stdin|env|keychain|credential-file|none, last4?: string}", "config_files_read": "[string]", "isolated": "boolean"}}
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "description": "Read-only, network. Returns the account the resolved token belongs to and its scopes.",
      "classification": "discover", "read_only": true, "latency_class": "network",
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "[read|write]", "token_source": "stdin|env|keychain|credential-file"}},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}]
    }
  ]
}
```

`auth status` and `auth login` follow the same per-command shape and are omitted for length; `auth login --token-stdin` is the non-interactive bootstrap, and interactive browser login is never started in machine mode.

Fingerprint endpoint, `notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads

All on stdout, exit `0`, with empty stderr in machine mode.

`notectl note list --tag 'work' --limit 2 --machine` (list):

```json
{"items":[{"id":"note_8f2kq1x0ab3c","title":"Standup notes","tags":["work"],"created_at":"2026-11-16T15:02:11Z","updated_at":"2026-11-17T09:14:03Z"},{"id":"note_2bz7rr91mm0d","title":"Quarterly plan","tags":["planning","work"],"created_at":"2026-10-01T18:40:00Z","updated_at":"2026-11-12T22:01:45Z"}],"has_more":true,"next_cursor":"c1.eyJvIjoyfQ","limit":2,"estimated_total":17}
```

`notectl note get --machine -- note_8f2kq1x0ab3c` (record):

```json
{"id":"note_8f2kq1x0ab3c","title":"Standup notes","body":"- shipped export\n- blocked on API quota","tags":["work"],"created_at":"2026-11-16T15:02:11Z","updated_at":"2026-11-17T09:14:03Z"}
```

`notectl note search --query 'quota' --machine` (list):

```json
{"items":[{"id":"note_8f2kq1x0ab3c","title":"Standup notes","tags":["work"],"updated_at":"2026-11-17T09:14:03Z","score":0.91,"snippet":"…blocked on API quota"}],"has_more":false,"limit":20}
```

`printf '%s' "$BODY" | notectl note create --title 'Retro' --tag 'work' --body-stdin --idempotency-key 'run-42-retro' --machine` (record):

```json
{"id":"note_q93hd0v1pp7e","title":"Retro","body":"What went well…","tags":["work"],"created_at":"2026-11-17T10:00:00Z","updated_at":"2026-11-17T10:00:00Z","created":true}
```

`notectl note create --title 'Retro' --body-file ./retro.md --dry-run --machine` (dry run, never byte-identical to a real create):

```json
{"dry_run":true,"planned_action":"create","title":"Retro","tags":[],"body_bytes":412}
```

`notectl note delete --machine -- note_q93hd0v1pp7e`:

```json
{"id":"note_q93hd0v1pp7e","status":"deleted"}
```

`notectl note delete --if-exists --machine -- note_q93hd0v1pp7e` on retry after the note is already gone:

```json
{"id":"note_q93hd0v1pp7e","status":"absent"}
```

`notectl note export --output './backup/notes.ndjson' --machine` (artifact):

```json
{"path":"/home/agent/backup/notes.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:9c1185a5c5e9fc54612808977ee8f548b2258d31f2b1c2c4e9a6c6d5b8e3f0a1","note_count":17,"exported_at":"2026-11-17T10:05:31Z","partial":false}
```

## 5. Example error payloads

Machine mode: stdout empty, the error object is the only stderr content.

**Not found** — `notectl note get --machine -- note_000000000000`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_000000000000","temporary":false,"request_id":"req_7Hc2"}
```

**Validation** — `notectl note create --title '' --body-stdin --machine`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Title must be 1-200 characters.","field":"--title","details":{"min_length":1,"max_length":200,"received_length":0},"hint":"Pass a non-empty --title.","temporary":false}
```

**Rate limited** — `notectl note search --query 'quota' --machine`, exit `6`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_9Kd1"}
```

**Timeout on a create without an idempotency key** — exit `7`; outcome unknown, so not retryable and reconcile first:

```json
{"code":"TIMEOUT","message":"Request timed out after 5000 ms; the note may have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":5000,"idempotency_key":null},"hint":"Retry only with an --idempotency-key on future creates; reconcile this attempt before retrying.","request_id":"req_3Lm8"}
```

**Unauthenticated** — any networked command with no token, exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No API token found.","details":{"sources_checked":["env:NOTECTL_TOKEN","keychain:notectl/default","file:~/.config/notectl/credentials"]},"hint":"Set NOTECTL_TOKEN or run notectl auth login with --token-stdin.","temporary":false}
```

**Export target exists** — `notectl note export --output './backup/notes.ndjson' --machine`, exit `8`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/backup/notes.ndjson","hint":"Add --overwrite or choose a different --output.","temporary":false}
```

## 6. Checklist walk

| Section | Answer |
|---|---|
| Command Model | `note <verb>`, shallow; `id` positional is the one selector; conventional `--limit`, `--output`, `--timeout-ms`, `--format`; `search` kept as the user's verb. |
| Machine Schema | §3: tree, flags with types/defaults/enums/cardinality, units in `--timeout-ms`, machine and isolation profiles, shape dialect, exit and symbolic codes, per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`, latency classes, versioning policy, fingerprint + scope, `schema <command>`. |
| Stdin Contract | Declared per command; only `create --body-stdin` and global `--token-stdin` read stdin, both explicit, mutually exclusive, never block in machine mode. |
| Shell Safety | `--` supported and declared; examples quote values and put options before `--`; body never passed as a flag value; hints contain no shell strings built from input. |
| Agent-Safe Invocation | `--machine` bundle; per-stream non-TTY rules; `--isolated` distinct; `auth login --token-stdin` bootstrap; `schema` is local, no auth, <100 ms; every networked command has `--timeout-ms`. |
| Output | stdout payload only; `single-error-object` stderr framing as an enum; classes declared (list, record, artifact); cursor contract; `--select` projection; deterministic sort; UTC timestamps; `--output` only on `export` with path/size/hash. |
| Errors And Exit Codes | Codes 0-11 declared; `INTERNAL` fallback; `NETWORK_ERROR` transport code; `temporary` on every error; `unknown_code_policy`; debug opt-in and redacted. Partial failure: export continues, exits `10` unless `--allow-partial`. |
| Ambient State | Sources, precedence, `--isolated`/`--no-config`, `config show --resolved`, `auth status`, `auth whoami`; no secret flags; token shown only as `last4`. |
| Mutations And Long-Running Work | `create`/`delete` explicit verbs with `--dry-run`; idempotency key for create, `--if-exists` for delete; unknown-outcome and reconciliation declared; signal semantics; atomic export writes. Async jobs: not applicable — no operation outlives the process; export is a foreground command with a declared deadline. |
| Side Effects And Telemetry | Reads have no writes (export writes only its declared file); telemetry and update checks off by default and suppressed in machine mode. |
| Prose Surfaces | Summaries and `description` fields lead with read-only/mutating, requirements, and defaults, then context; `list` vs `search` separated in one clause. |
| Tests | Ship: schema snapshot and fingerprint stability; each success and error payload above as golden output; declared-vs-observed exit codes; TTY vs non-TTY per stream; `--machine` suppression; `--body-stdin` with empty, oversized, and TTY stdin; cursor paging and `CURSOR_EXPIRED`; `--select` projection; env/config precedence and `--isolated`; dry-run for create, delete, export; SIGINT during export leaves `--output` untouched; concurrent exports to one path; idempotent create retry returns `created: false`. Deprecation tests and async cancellation: not applicable at 1.0 (no deprecations, no async jobs). |
~~~~~~
