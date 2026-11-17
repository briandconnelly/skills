# Scenario 1 (design) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 10/11 scored; 2/2 conformance
- **Tokens:** 79,019 (final-turn context plus output, read from the transcript)
- **Output words:** 3,660
- **Transcript sha256:** `7348ae15c18b6398dae0e13063fa4a3d4d987e1afbec0c92c43a49e03daf8911` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; {"name": "--machine", "type": "boolean" Parts: profile declared in schema = pass; named flags declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {...}; "symbolic_error_codes": [...]; delete "errors_possible" Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object"; "stderr contains exactly one JSON error object" Parts: stdout success only = pass; stderr structured failures with framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "classification": "mutate" explicit delete verb; {"dry_run":true,"planned_action":"delete",...} Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": "boolean", "next_cursor?": "string" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "path": "string (absolute, POSIX)", "byte_size": "integer", "content_hash": "string (sha256:<hex>)" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl config show --resolved", "notectl auth whoami"], "disable_with": {"--isolated": "config and cache" Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note delete --if-exists --machine -- 'note_01HZX3' |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **FAIL** | INTERNAL_ERROR listed and exit 1 "generic" but not stated as the unanticipated-failure code; TRANSIENT listed per networked command; no rule for unlisted codes Parts: unanticipated failure emits declared symbolic code = fail; each networked command lists non-timeout transport failure = pass; says how caller treats unlisted code = fail |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | [--tag <tag>]... repeated; "cardinality": "many" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "`--output` only on `export` returning path/size/hash" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "one class per command (`list`, `record`, `artifact`); dry-run alternates declared" |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (designing a new CLI). Task: new design.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| Discover contract | discover | none | schema / fingerprint |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | ids + titles + tags, paging |
| Get a note | inspect | note id | full note |
| Search notes | query | query string | ids + titles + tags + match score, paging |
| Create a note | mutate | title, body (stdin or flag), tags | created note incl. id |
| Delete a note | mutate | note id | deleted id |
| Export all notes | mutate (local file write) | `--output` path | path, byte size, content hash, count |
| Inspect auth/config | admin | none | resolved identity / config (redacted) |

`list` vs `find`: `list` enumerates with exact filters (tag); `find` ranks by full-text relevance over title and body. One sentence separates them, so both stay.

## 2. Command surface

```text
notectl schema [--fingerprint] [<command path>]
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort created_at|-created_at|title] [--select <field>]...
notectl note get    <id> [--select <field>]...
notectl note find   --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create --title <text> [--body <text> | --body-stdin] [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete <id> [--if-exists] [--dry-run]
notectl note export --output <path> [--format json|ndjson] [--overwrite] [--dry-run]
notectl auth whoami
notectl auth login --token-stdin
notectl config show --resolved
```

Global flags: `--machine`, `--json`, `--no-progress`, `--no-color`, `--isolated`, `--no-config`, `--profile <name>`, `--timeout-ms <n>`, `--`.

- Pattern is `notectl noun verb`; verbs reuse the conventional set (`list`, `get`, `find`, `create`, `delete`) plus `export`.
- Primary selector for a note is the ID, as the single positional argument; everything else is a named flag.
- `--` ends options; operands that begin with `-` are safe after it.
- Canonical machine profile: `--machine` (implies `--json --no-progress --no-color`, disables prompts, pager, and browser).
- Isolation profile: `--isolated` (ignores config files and cache; credentials only from `NOTECTL_TOKEN`). Kept distinct from `--machine` because normal authenticated use relies on the config-file credential.
- Non-interactive bootstrap: `printf '%s' "$TOKEN" | notectl auth login --token-stdin --machine`, or just set `NOTECTL_TOKEN`. Secrets are never accepted as flag values.

Canonical examples:

```sh
notectl note list --tag 'work' --limit 20 --machine
notectl note get 'note_01HZX3' --machine
notectl note find --query 'quarterly plan' --machine
printf '%s' 'Body text' | notectl note create --title 'Q3 plan' --body-stdin --tag 'work' --idempotency-key 'k-7f3a' --machine
notectl note delete --if-exists --machine -- 'note_01HZX3'
notectl note export --output 'notes.ndjson' --format ndjson --machine
```

## 3. Machine-readable schema (`notectl schema`)

Shape dialect: JSON Schema is the alternative; here `notectl-compact-v1` is used and defined inside the schema.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-9f2e41c7",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this document excluding fingerprint and tool_version; tool_version is not an input",
  "compatibility": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes on a command"],
    "breaking": ["removals", "renames", "type or meaning changes", "exit-code remapping", "making an optional field required"],
    "rule": "any contract change changes fingerprint; breaking changes bump the major component of schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? on a key marks an optional field; all other fields are required unless removed by a declared projection; T[] is an array of T; a string-valued shape describes an NDJSON record sequence",
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode on failure, stderr contains exactly one JSON error object and nothing else; on success stderr is empty",
  "end_of_options_supported": true,
  "encoding": {"charset": "UTF-8", "timestamps": "RFC 3339 UTC with Z suffix", "numbers": "locale-independent"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Non-interactive machine mode: never prompts; no color, progress, pager, or browser; structured output only."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit structured JSON on stdout and structured errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the cache; credentials come only from NOTECTL_TOKEN. Suppresses token refresh writes."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to use; ignored under --isolated or --no-config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "minimum": 100, "default": "per command (see timeout_defaults_ms)", "description": "Per-request network timeout."}
  ],
  "exit_codes": {"0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified", "10": "local file error (export output path)"},
  "symbolic_error_codes": ["INTERNAL_ERROR", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSIENT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED"],
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "error_rules": "agents branch on code, never message; temporary is authoritative for retry; secrets are redacted from all output",
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "string[]", "created_at": "string", "updated_at": "string"},
  "auth": {"required": true, "except": ["schema", "auth login", "config show"], "scopes": {"read": ["note list", "note get", "note find", "note export", "auth whoami"], "write": ["note create", "note delete"]}},
  "ambient_state": {
    "credentials": ["NOTECTL_TOKEN env var", "token in ~/.config/notectl/credentials (mode 0600, written by auth login)"],
    "config_files": ["~/.config/notectl/config.toml ($XDG_CONFIG_HOME respected)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "NO_COLOR"],
    "cache": {"path": "~/.cache/notectl/", "contents": "refreshed access tokens only; note data is never cached", "writes": "atomic rename; last-writer-wins"},
    "precedence": "flags > env vars > config file > cache",
    "disable_with": {"--isolated": "config and cache", "--no-config": "config only"},
    "inspect_with": ["notectl config show --resolved", "notectl auth whoami"],
    "secret_values": ["token"],
    "redaction": "tokens render as \"<redacted:last4>\" in all output"
  },
  "telemetry": {"enabled_by_default": false, "update_checks": false},
  "command_tree": {
    "schema": "notectl schema [--fingerprint] [<command path>]",
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "find": "notectl note find --query <text>",
      "create": "notectl note create --title <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"whoami": "notectl auth whoami", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl schema",
      "description": "Print this contract. No network, no auth; target <100ms.",
      "aliases": [], "deprecations": [],
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command_path", "type": "string", "cardinality": "zero-or-more", "examples": ["note get"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false, "description": "Print only {schema_version, fingerprint, fingerprint_scope}."}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "this document, or one command entry when command_path is given", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "timeout_defaults_ms": null, "retry_defaults": {"retries": 0},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes by exact filters (tag), newest first. For relevance-ranked text search use note find. Returns summaries without body unless --select body.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "Match notes having all given tags."},
        {"name": "--limit", "type": "integer", "minimum": 1, "maximum": 200, "default": 50},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["-created_at", "created_at", "title"], "default": "-created_at", "tiebreak": "id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "object[] (note_shape projected by --select)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "cursor": {"opaque": true, "lifetime_s": 900, "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "size_mode": "paged"
      },
      "side_effects": {"external_mutation": false, "writes": ["token cache on refresh (suppressed by --isolated)"]},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED"], "backoff": "exponential, honors retry_after_ms"},
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
      "description": "Fetch one note by ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["note_01HZX3"]}],
      "flags": [{"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "size_mode": "small (body capped at 1 MiB by the API)"},
      "side_effects": {"external_mutation": false, "writes": ["token cache on refresh (suppressed by --isolated)"]},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED"]},
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
      "description": "Full-text search over title and body, ranked by relevance (score desc, then id). For exact tag filtering without ranking use note list.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--limit", "type": "integer", "minimum": 1, "maximum": 100, "default": 20},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at", "score", "snippet"], "cardinality": "many", "default": ["id", "title", "tags", "score", "snippet"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "object[] (note_shape plus score: number, snippet: string, projected by --select)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "cursor": {"opaque": true, "lifetime_s": 900, "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "empty_result": "items: [], has_more: false, exit 0",
        "size_mode": "paged"
      },
      "side_effects": {"external_mutation": false, "writes": ["token cache on refresh (suppressed by --isolated)"]},
      "latency_class": "network", "timeout_defaults_ms": 8000, "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED"]},
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
      "canonical_invocation_path": "notectl note create --title <text>",
      "description": "Create one note. Body comes from exactly one of --body or --body-stdin (default empty). Pass --idempotency-key so a retry after TIMEOUT cannot create a duplicate.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "description": "Read body as UTF-8 text from stdin."},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "pattern": "^[a-z0-9][a-z0-9-]{0,39}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 64, "description": "Server deduplicates creates with the same key for 24h and returns the original note."},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": "only with --body-stdin", "auto_detected_when_piped": false, "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": "1 MiB", "can_block": "only if --body-stdin is given and stdin is an open pipe; with --machine and a TTY stdin, fails VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": "note_shape", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "note": {"title": "string", "body_bytes": "integer", "tags": "string[]"}}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates input locally and checks auth/scope with a read-only API call; no note is created"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "description": "automatic retries only when --idempotency-key is set"},
      "reconciliation": "on TIMEOUT or interrupt the outcome is unknown; re-run with the same --idempotency-key (safe), or without a key run note find --query <title> to check before retrying",
      "signals": "SIGINT/SIGTERM abort the client; a request already sent may still commit server-side; no local writes",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "CONFLICT", "exit": 8, "description": "idempotency key reused with different content"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Permanently delete one note by ID. Fails NOTE_NOT_FOUND unless --if-exists. Not recoverable.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "pattern": "^note_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["note_01HZX3"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "Exit 0 with deleted: false when the note does not exist."},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "deleted": "boolean"}, "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string", "title?": "string"}, "streaming": false, "size_mode": "small"},
        "--dry-run --if-exists": {"precedence": "same --dry-run shape; planned_action is none when the note is absent, exit 0"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "performs a read (GET) only"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0, "description": "safe to retry automatically only with --if-exists"},
      "reconciliation": "on TIMEOUT or interrupt run notectl note get <id>: NOTE_NOT_FOUND means the delete committed; or retry with --if-exists",
      "signals": "SIGINT/SIGTERM abort the client; a request already sent may still commit; no local writes",
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
      "description": "Write every note to a local file and print a pointer to it, not the notes. Fails OUTPUT_EXISTS unless --overwrite. Reads the remote store; writes only the output file.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": "remote read-only; writes one local file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one note_shape per line; json: a single array."},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string (absolute, POSIX)", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "format": "ndjson|json", "note_count": "integer", "exported_at": "string"}, "size_mode": "small pointer; file size grows with data"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "export", "path": "string", "format": "ndjson|json", "estimated_note_count": "integer", "would_overwrite": "boolean"}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": false, "writes": ["<path>, via temp file in the same directory then atomic rename"], "dry_run": "no file is created"},
      "latency_class": "slow", "timeout_defaults_ms": 5000, "timeout_semantics": "--timeout-ms applies per page request",
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED"], "scope": "per page"},
      "consistency": "best-effort page walk; notes changed during export may be missing or duplicated-by-id-free (ids are deduplicated)",
      "signals": "SIGINT/SIGTERM delete the temp file; <path> is either untouched or fully written",
      "async": false, "streaming": false, "pagination": "internal", "truncation": false, "artifact": true,
      "errors_possible": [
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
      "canonical_invocation_path": "notectl auth whoami",
      "description": "Show the authenticated account and where the credential came from.",
      "aliases": [], "deprecations": [],
      "classification": "admin", "read_only": true, "arguments": [], "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "scopes": "string[]", "credential_source": "env|credentials_file", "token": "string (redacted)"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 3000, "retry_defaults": {"retries": 1},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl auth login --token-stdin",
      "description": "Store a token read from stdin in the credentials file. Non-interactive; never opens a browser.",
      "aliases": [], "deprecations": [],
      "classification": "admin", "read_only": false, "arguments": [],
      "flags": [{"name": "--token-stdin", "type": "boolean", "required": true}],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "accepted_formats": ["text/plain token, trailing newline trimmed"], "maximum_input_size": "4 KiB", "can_block": "no: a TTY stdin fails VALIDATION_ERROR in machine mode", "mutually_exclusive_with": [], "empty_stdin": "VALIDATION_ERROR"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "credentials_path": "string", "token": "string (redacted)"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": ["credentials file (atomic rename, mode 0600)"]},
      "latency_class": "network", "timeout_defaults_ms": 3000, "retry_defaults": {"retries": 0},
      "dry_run_applicability": "not applicable: the only effect is a local credential write that the validating call already proves",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "description": "Show each resolved setting with its source (flag, env, config, default). Secrets redacted. No network.",
      "aliases": [], "deprecations": [],
      "classification": "admin", "read_only": true, "arguments": [],
      "flags": [{"name": "--resolved", "type": "boolean", "required": true}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"settings": "{name: string, value: string|null, source: flag|env|config|cache|default, secret: boolean}[]", "config_files_read": "string[]", "isolated": "boolean"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "timeout_defaults_ms": null, "retry_defaults": {"retries": 0},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

`notectl schema --fingerprint`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-9f2e41c7", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --tag 'work' --limit 2 --machine`

```json
{"items":[{"id":"note_01HZX3","title":"Q3 plan","tags":["work","planning"],"updated_at":"2026-11-15T09:12:00Z"},{"id":"note_01HZW9","title":"Standup notes","tags":["work"],"updated_at":"2026-11-14T16:40:00Z"}],"has_more":true,"next_cursor":"c1.eyJvIjoyfQ","limit":2,"estimated_total":37}
```

`notectl note get 'note_01HZX3' --machine`

```json
{"id":"note_01HZX3","title":"Q3 plan","body":"Ship export; deprecate v0 API.","tags":["work","planning"],"created_at":"2026-11-10T08:00:00Z","updated_at":"2026-11-15T09:12:00Z"}
```

`notectl note find --query 'export' --limit 1 --machine`

```json
{"items":[{"id":"note_01HZX3","title":"Q3 plan","tags":["work","planning"],"score":0.92,"snippet":"Ship export; deprecate…"}],"has_more":false,"limit":1}
```

`printf '%s' 'Draft' | notectl note create --title 'Ideas' --body-stdin --tag 'misc' --idempotency-key 'k-7f3a' --machine`

```json
{"id":"note_01HZY1","title":"Ideas","body":"Draft","tags":["misc"],"created_at":"2026-11-17T10:00:00Z","updated_at":"2026-11-17T10:00:00Z"}
```

`notectl note delete --if-exists --machine -- 'note_01HZW9'`

```json
{"id":"note_01HZW9","deleted":true}
```

`notectl note delete 'note_01HZW9' --dry-run --machine`

```json
{"dry_run":true,"planned_action":"delete","id":"note_01HZW9","title":"Standup notes"}
```

`notectl note export --output 'notes.ndjson' --machine`

```json
{"path":"/home/agent/notes.ndjson","byte_size":48213,"content_hash":"sha256:9b74c9897bac770ffc029102a200c5de9b74c9897bac770ffc029102a200c5de","format":"ndjson","note_count":37,"exported_at":"2026-11-17T10:05:00Z"}
```

## 5. Example error payloads (stderr is only this object; stdout empty)

Not found, exit 3, from `notectl note get 'note_404XYZ' --machine`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404XYZ","hint":"Use note find or note list to locate the ID.","temporary":false,"request_id":"req_8c1d"}
```

Validation, exit 2, from `notectl note create --title '' --machine`:

```json
{"code":"VALIDATION_ERROR","message":"Title must be 1 to 200 characters.","field":"--title","details":{"min_length":1,"max_length":200,"actual_length":0},"hint":"Pass a non-empty --title.","temporary":false}
```

Rate limited, exit 6, from `notectl note list --machine`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_91aa"}
```

Unauthenticated, exit 4:

```json
{"code":"UNAUTHENTICATED","message":"No valid credential found.","details":{"sources_checked":["flag","env:NOTECTL_TOKEN","credentials_file"]},"hint":"Set NOTECTL_TOKEN or pipe a token to auth login --token-stdin.","temporary":false}
```

Timeout during create, exit 7 (outcome unknown, reconcile first):

```json
{"code":"TIMEOUT","message":"Request timed out after 5000 ms; the note may have been created.","details":{"timeout_ms":5000,"idempotency_key":"k-7f3a"},"hint":"Re-run with the same --idempotency-key.","temporary":false}
```

Export target exists, exit 10:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","path":"/home/agent/notes.ndjson","field":"--output","hint":"Add --overwrite or choose another --output.","temporary":false}
```

## 6. Checklist walk

- **Command Model**: `noun verb`, shallow, conventional verbs, ID positional, named flags otherwise, conventional `--limit`/`--output`/`--format`/`--timeout-ms`; `--tag` and `--select` mean the same on every command. No aliases.
- **Machine Schema**: all items declared above, incl. units, shape dialect, per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`, latency classes, compatibility rules, fingerprint + scope.
- **Stdin Contract**: declared per command; only `create --body-stdin` and `auth login --token-stdin` read stdin, both explicit-flag only, never auto-detected.
- **Shell Safety**: `--` supported and declared; examples quote values with options before `--`; hints contain no shell strings; values are never passed to a shell.
- **Agent-Safe Invocation**: single `--machine` profile; distinct `--isolated`; per-stream TTY detection (stdout→rendering/pager, stderr→color/progress, stdin→prompts); `auth login --token-stdin` bootstrap; `schema`/`--help` do no network, auth, or plugin loading (<100ms target, lazy imports); `--timeout-ms` on all networked commands with declared retries; deprecations/truncation surfaced in structured output.
- **Output**: stdout payload only; `single-error-object` framing; one class per command (`list`, `record`, `artifact`); dry-run alternates declared; cursor contract declared; deterministic sort with id tiebreak; `--select` projection rule; UTC timestamps; `--output` only on `export` returning path/size/hash. No streaming commands, so `completion_record` is not applicable.
- **Errors And Exit Codes**: codes 0–10 declared; required `code`/`message`/`temporary` on every error; `retry_after_ms` on rate limit; `field` names published flags; repair data in `details`. Partial failure: not applicable — no multi-item mutation commands (export is all-or-nothing via atomic rename).
- **Ambient State**: credential/config/env/cache sources, precedence, disable flags, `config show --resolved`, `auth whoami`, redaction, no secret flags.
- **Mutations And Long-Running Work**: explicit verbs; `--dry-run` on create/delete/export (not applicable to `auth login`, justified); `--idempotency-key` and `--if-exists`; reconciliation and signal semantics declared; atomic local writes. Long-running jobs: not applicable — no async server-side operations; export is synchronous and bounded by per-page timeouts.
- **Side Effects And Telemetry**: reads perform no writes except declared, `--isolated`-suppressible token-cache refresh; no telemetry or update checks.
- **Prose Surfaces**: every `description` leads with the binding constraint, and sibling pairs (`list`/`find`) are separated in one sentence.
- **Tests**: ship schema snapshot, canonical payload, and failure payload/exit tests; declared-vs-observed exit code check; TTY vs non-TTY and `--machine` suppression; stdin incl. empty stdin and TTY-stdin refusal; pagination and `CURSOR_EXPIRED`; export artifact hash/size and atomic write on SIGINT; config/env precedence and `--isolated`; dry-run non-mutation; interrupt during create/delete; concurrent cache writes. Deprecation and cancellation tests are not applicable until deprecations or async jobs exist.
~~~~~~
