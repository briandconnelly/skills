# Scenario 1 (design) — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 2/2 conformance
- **Tokens:** 83,560 (final-turn context plus output, read from the transcript)
- **Output words:** 4,469
- **Transcript sha256:** `dadcf5da67a95e0278b5e671f5bba537b25925497a0422fccf4cbcb11acbbe42` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; --machine in global_flags Parts: profile declared in schema = pass; every flag it names declared = pass |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "10": "output file already exists (domain-specific)"; create errors_possible incl. IDEMPOTENCY_KEY_REUSED Parts: numeric exit codes = pass; symbolic codes = pass; per-command catalog for mutating command = pass |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object" Parts: stdout success only = pass; stderr structured with declared framing = pass |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "confirmation": "the delete verb is the explicit trigger"; dry-run shape {"dry_run": "true", "planned_action": "delete\|none" Parts: explicit trigger = pass; --dry-run with dry_run: true = pass |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more":true,"next_cursor":"eyJvIjoyfQ" Parts: has_more = pass; navigation token = pass |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size":48213,"content_hash":"sha256:3b7f0c2e... Parts: pointer to file = pass; size = pass; hash = pass |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--deadline-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"] Parts: declared = pass; inspection = pass; isolation = pass |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note get --machine -- 'note_8f2a' Parts: options before -- = pass; only operands after = pass |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL"; {"code": "TRANSPORT_ERROR", "exit": 9} in every networked catalog; "unknown_code_policy" Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unknown-code policy = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | "cardinality": "many", "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "The only command that writes a local file." |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | "alternate_outputs": {"--dry-run": {"class": "record" Parts: one output class per command = pass; switching flag declares switch = pass |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design).
Task: new CLI design, following the agent-friendly-cli design workflow.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| Discover the contract | discover | none | schema / fingerprint |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | ids + titles + tags, paging token |
| Get a note | inspect | note id | full note |
| Search notes | query | query text | ids + titles + tags + match snippet, paging token |
| Create a note | mutate | title, body, tags | created note id |
| Delete a note | mutate | note id | id + outcome |
| Export all notes | query (local write) | output path | path, byte size, content hash, count |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

`list` and `search` stay separate because they differ in one fact an agent can see without prose: `search` requires `--query` and returns relevance-ordered results with `score`; `list` takes no query and is ordered by `updated_at`.

## 2. Command surface

Pattern: `notectl noun verb`, positional argument only for the note id.
All commands accept `--` end-of-options; `note get -- -weird-id` treats `-weird-id` as the id.

```text
notectl schema [<command>] [--fingerprint] [--summary]
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]... [--sort updated_at|-updated_at|created_at|-created_at|title]
notectl note get    <id> [--select <field>]...
notectl note search --query <text> [--tag <tag>]... [--limit <n>] [--cursor <token>] [--select <field>]...
notectl note create --title <text> (--body <text> | --body-file <path> | --body-file -) [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete <id> [--if-exists] [--dry-run]
notectl note export --output <path> [--format json|ndjson] [--overwrite] [--tag <tag>]...
notectl auth whoami
notectl auth status
notectl config show --resolved
```

Global flags: `--machine` (canonical machine profile: implies `--json --no-progress --no-input --no-color`), `--json`, `--no-progress`, `--no-input`, `--no-color`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <ms>` (networked commands), `--debug` (opt-in, redacted, stderr only).

Canonical agent invocations:

```sh
notectl note list --machine --tag 'work' --limit 50
notectl note get --machine -- 'note_8f2a'
notectl note search --machine --query 'quarterly plan' --limit 20
printf '%s' "$BODY" | notectl note create --machine --title 'Standup 2026-11-17' --tag 'meetings' --body-file - --idempotency-key 'b1c7e0e2-5f0a-4c55-9d1e-2f6c1a0f9e11'
notectl note delete --machine --if-exists -- 'note_8f2a'
notectl note export --machine --output './notes-export.ndjson' --format ndjson
```

## 3. Machine schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum, trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, `[T]` is an array of `T`, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes in a command catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "changed default sort or output class"],
    "rule": "any contract change changes the fingerprint; breaking changes also bump the major version"
  },
  "fingerprint": "ntc-5e91c0a7",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_tool_version": false,
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields required unless so marked or removed by a declared projection; [T] is an array of T; a string-valued shape describes a record sequence",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty, except note export, which never writes to stdout on failure and leaves no partial file",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input", "--no-color"], "description": "Non-interactive machine mode. Structured output only; never prompts, never pages, never opens a browser, regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON success payloads on stdout and JSON error objects on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress and spinners on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color on all streams."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the local cache. Credentials are still read from NOTECTL_TOKEN only (not from the credential file or keychain), so authenticated commands still work when NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Select a named profile from the config file. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "API base URL. Overrides NOTECTL_API_URL and config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "description": "Per-request network timeout for networked commands; default is per command."},
    {"name": "--debug", "type": "boolean", "default": false, "description": "Emit redacted request/response diagnostics to stderr. Not allowed with --machine; use NOTECTL_DEBUG_FILE to capture debug output in machine mode."}
  ],
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> --body-file -",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status"},
    "config": {"show": "notectl config show --resolved"}
  },
  "aliases": [],
  "deprecations": [],
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
    "10": "output file already exists (domain-specific)",
    "11": "local filesystem write failed (domain-specific)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "IDEMPOTENCY_KEY_REUSED", "TRANSPORT_ERROR", "TRANSIENT", "OUTPUT_EXISTS", "WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before any retry",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string (RFC 3339, UTC)", "updated_at": "string (RFC 3339, UTC)"},
  "timestamps": "RFC 3339 in UTC with Z suffix",
  "encoding": "UTF-8; numbers locale-independent; paths returned as absolute POSIX-style paths",
  "auth": {
    "required_for": ["note list", "note get", "note search", "note create", "note delete", "note export", "auth whoami"],
    "credential_sources_in_precedence": ["NOTECTL_TOKEN env var", "OS keychain entry notectl/<profile>", "credential file ~/.config/notectl/credentials.json (mode 0600)"],
    "secret_intake": "token never accepted as a flag or argument; non-interactive bootstrap is: set NOTECTL_TOKEN, or pipe the token to `notectl auth login --token-stdin`",
    "scopes": {"notes:read": ["note list", "note get", "note search", "note export"], "notes:write": ["note create", "note delete"]}
  },
  "ambient_state": {
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_PROFILE", "NOTECTL_API_URL", "NOTECTL_CONFIG", "NOTECTL_DEBUG_FILE", "NO_COLOR"],
    "cache": {"path": "$XDG_CACHE_HOME/notectl/", "contents": "schema fingerprint and API capability probe only; never note content", "reads": true, "writes": "atomic replace (write temp + rename); last writer wins"},
    "cwd_selects_context": false,
    "precedence": "flags > environment variables > config file > cache > built-in defaults",
    "disable_with": {"--isolated": "config + cache + credential file + keychain", "--no-config": "config only"},
    "inspect_with": ["notectl auth whoami", "notectl auth status", "notectl config show --resolved"],
    "secret_values": ["token"],
    "redaction": "tokens are shown as source plus last 4 characters (e.g. \"env:NOTECTL_TOKEN ...a9f2\") in every output, debug output, and error"
  },
  "telemetry": {"enabled_by_default": false, "update_check_by_default": false, "machine_mode": "always suppressed"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "List notes ordered by updated_at descending. Use note search instead when you have query text.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "notes must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["-updated_at", "updated_at", "-created_at", "created_at", "title"], "default": "-updated_at", "tiebreak": "id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false,
        "shape": {"items": "[note projected by --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "next_cursor is present exactly when has_more is true; body is excluded by default to save tokens",
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "size_mode": "bounded by --limit"
      },
      "pagination": {"token": "next_cursor", "opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort (notes changed mid-walk may be skipped or repeated; dedupe by id)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"], "backoff": "honors retry_after_ms, else exponential from 250ms"},
      "async": false, "truncation": false, "artifact": false,
      "signal_semantics": {"interrupt": "no effect", "closed_stdout": "exits quietly with 0"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Get one note by exact id, including body.",
      "classification": "inspect",
      "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[A-Za-z0-9]+$", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": "note projected by --select", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent; id is always present"}, "size_mode": "small (body up to 1 MiB)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"]},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "signal_semantics": {"interrupt": "no effect", "closed_stdout": "exits quietly with 0"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Full-text search over title, body, and tags; results ordered by score descending, then id. Requires --query; use note list to browse without a query.",
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "notes must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at", "score", "snippet"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "score", "snippet"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false,
        "shape": {"items": "[note projected by --select, plus score: number and snippet: string (max 200 chars, truncated: boolean)]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent; id is always present"},
        "size_mode": "bounded by --limit"
      },
      "pagination": {"token": "next_cursor", "opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "consistency": "search index is eventually consistent; a note created seconds ago may be absent from results",
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR"]},
      "async": false, "truncation": "snippet only, marked per item", "artifact": false,
      "signal_semantics": {"interrupt": "no effect", "closed_stdout": "exits quietly with 0"},
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file -",
      "summary": "Create one note. Pass --idempotency-key on every call so a retry after a timeout cannot create a duplicate.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "mutually_exclusive_with": ["--body-file"], "description": "Short inline body; prefer --body-file - for multi-line or untrusted text."},
        {"name": "--body-file", "type": "path", "default": null, "description": "Read the body from a file; '-' reads stdin.", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_count": 20, "default": []},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "Caller-generated unique key. Server deduplicates the same key for 24 hours."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "body_requirement": "exactly one of --body or --body-file is required; an empty body is allowed only via --body ''",
      "stdin_contract": {"reads": "only when --body-file -", "auto_detected_when_piped": false, "accepted_formats": ["UTF-8 text"], "maximum_input_size": "1 MiB", "can_block": "yes, until stdin reaches EOF; never reads from a TTY in machine mode (fails with VALIDATION_ERROR field --body-file if stdin is a terminal)", "mutually_exclusive_with": ["--body"], "empty_stdin": "VALIDATION_ERROR, field --body-file"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "body_bytes": "integer", "idempotent_replay": "boolean"}, "shape_description": "body is not echoed back; idempotent_replay is true when the server returned an earlier note created with the same key", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer", "idempotency_key?": "string"}, "size_mode": "small", "description": "validates input locally and against the server's validation endpoint; no note is created"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation; may refresh the access token (suppressed under --isolated)"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "description": "notectl never retries create on its own; the caller decides using the rules in reconciliation"},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, TRANSIENT, or interrupt the outcome is unknown. Safe to retry only by re-running with the same --idempotency-key that was on the original attempt, within 24 hours. Without a key on the original attempt, do not retry automatically: a search or list that does not show the note does not prove it was not created (search is eventually consistent and the request may still commit). Adding a key on the retry does not deduplicate the original attempt.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the in-flight create"},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "IDEMPOTENCY_KEY_REUSED", "exit": 8, "description": "same key previously used with different title/body/tags"},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "description": "server rejected before processing; safe to retry"},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by exact id. Use --if-exists to make the call repeat-safe.",
      "classification": "mutate",
      "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[A-Za-z0-9]+$", "examples": ["note_8f2a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "Treat an already-absent note as success (status: absent)."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "confirmation": "the delete verb is the explicit trigger; no prompt in any mode",
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "delete|none", "id": "string", "title?": "string"}, "shape_description": "planned_action is none when the note is absent and --if-exists is set; without --if-exists an absent note fails with NOTE_NOT_FOUND", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence; no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSPORT_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the in-flight delete"},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write every note (optionally filtered by --tag) to a local file and print a pointer to it. The only command that writes a local file.",
      "classification": "query",
      "read_only": "remote read-only; writes one local file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "Destination file. '-' is not accepted; use note list for stdout."},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one full note per line, sorted by id. json: {\"notes\": [note...]}, sorted by id."},
        {"name": "--overwrite", "type": "boolean", "default": false, "description": "Replace an existing file; without it an existing path fails with OUTPUT_EXISTS."},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 30000, "description": "Per-request timeout for each page fetch."},
        {"name": "--deadline-ms", "type": "integer", "unit": "ms", "default": 600000, "description": "Whole-command deadline."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "streaming": false, "shape": {"path": "string (absolute)", "format": "ndjson|json", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "note_count": "integer", "exported_at": "string"}, "size_mode": "small pointer; file size grows with note count"},
      "progress": {"stream": "stderr", "when": "human mode only, stderr is a TTY, and --no-progress not set; suppressed in machine mode"},
      "consistency": "best-effort: notes created, changed, or deleted during the export may or may not appear",
      "side_effects": {"external_mutation": false, "writes": ["--output path (atomic: written to <path>.notectl-tmp-<pid> then renamed)"]},
      "latency_class": "slow", "timeout_defaults_ms": 30000, "retry_defaults": {"retries": 3, "on": ["RATE_LIMITED", "TRANSIENT", "TRANSPORT_ERROR", "TIMEOUT"], "scope": "per page fetch; safe because reads are idempotent"},
      "signal_semantics": {"interrupt": "temp file removed; destination left untouched (previous contents preserved when --overwrite)", "local_writes": "atomic rename", "remote_continues": false, "closed_stdout": "file is still completed; pointer is not printed", "concurrency": "two exports to the same path: last rename wins, each file is complete"},
      "async": false, "pagination": "internal; not exposed", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "description": "only after internal retries are exhausted"},
        {"code": "TIMEOUT", "exit": 7, "retryable": true, "description": "a page fetch exceeded --timeout-ms after retries, or --deadline-ms was reached"},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"},
        {"code": "WRITE_FAILED", "exit": 11}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Show the authenticated account and token scopes. Validates the token with one API call.",
      "classification": "admin", "read_only": true, "arguments": [], "flags": [{"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"account_id": "string", "email": "string", "scopes": "[string]", "credential_source": "env|keychain|credential_file", "api_url": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 1},
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl auth status",
      "summary": "Show where credentials would be read from, without a network call.",
      "classification": "admin", "read_only": true, "arguments": [], "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"credential_present": "boolean", "credential_source?": "env|keychain|credential_file", "token_hint?": "string (last 4 chars)", "profile": "string", "isolated": "boolean"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local", "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show every resolved setting with the source that set it. Secrets are redacted.",
      "classification": "admin", "read_only": true, "arguments": [], "flags": [{"name": "--resolved", "type": "boolean", "default": true}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": {"settings": "[{key: string, value: string|integer|boolean|null, source: flag|env|config|cache|default, secret: boolean}]"}, "shape_description": "settings sorted by key; secret values are redacted", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local", "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "config file unparsable"}]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>]",
      "summary": "Print the machine contract for the whole tool or one command. No network, no auth.",
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command", "type": "string", "cardinality": "optional", "examples": ["note create"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "shape": "this document, or one entry of commands[] when <command> is given; --fingerprint returns {schema_version, fingerprint, fingerprint_scope}; --summary returns [{path, summary, read_only}]", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local", "latency_target_ms": 100,
      "async": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2, "description": "unknown command path"}]
    }
  ]
}
```

Fingerprint endpoint (`notectl schema --fingerprint`):

```json
{"schema_version":"1.0","fingerprint":"ntc-5e91c0a7","fingerprint_scope":"schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --machine --tag 'work' --limit 2`

```json
{"items":[{"id":"note_8f2a","title":"Q4 planning","tags":["planning","work"],"updated_at":"2026-11-16T21:04:11Z"},{"id":"note_7c11","title":"Vendor shortlist","tags":["work"],"updated_at":"2026-11-15T08:30:00Z"}],"has_more":true,"next_cursor":"eyJvIjoyfQ","limit":2,"estimated_total":37}
```

`notectl note get --machine -- 'note_8f2a'`

```json
{"id":"note_8f2a","title":"Q4 planning","body":"Goals:\n1. Ship sync\n2. Cut p95 latency","tags":["planning","work"],"created_at":"2026-10-02T17:12:45Z","updated_at":"2026-11-16T21:04:11Z"}
```

`notectl note search --machine --query 'latency' --limit 1`

```json
{"items":[{"id":"note_8f2a","title":"Q4 planning","tags":["planning","work"],"score":0.82,"snippet":"…2. Cut p95 latency","truncated":false}],"has_more":false,"limit":1}
```

`printf '%s' "$BODY" | notectl note create --machine --title 'Standup 2026-11-17' --tag 'meetings' --body-file - --idempotency-key 'b1c7e0e2-5f0a-4c55-9d1e-2f6c1a0f9e11'`

```json
{"id":"note_9d03","title":"Standup 2026-11-17","tags":["meetings"],"created_at":"2026-11-17T15:00:02Z","updated_at":"2026-11-17T15:00:02Z","body_bytes":412,"idempotent_replay":false}
```

Same command with `--dry-run`:

```json
{"dry_run":true,"planned_action":"create","title":"Standup 2026-11-17","tags":["meetings"],"body_bytes":412,"idempotency_key":"b1c7e0e2-5f0a-4c55-9d1e-2f6c1a0f9e11"}
```

`notectl note delete --machine -- 'note_8f2a'`

```json
{"id":"note_8f2a","status":"deleted"}
```

`notectl note delete --machine --if-exists -- 'note_8f2a'` (already gone)

```json
{"id":"note_8f2a","status":"absent"}
```

`notectl note export --machine --output './notes-export.ndjson'`

```json
{"path":"/home/agent/work/notes-export.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:3b7f0c2e9a41d8f6b5e2c1a0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0","note_count":37,"exported_at":"2026-11-17T15:02:40Z"}
```

## 5. Example error payloads (stderr is only this object; stdout empty)

Not found — `notectl note get --machine -- 'note_404'`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404","temporary":false,"request_id":"req_01HZX4"}
```

Validation — `notectl note create --machine --title '' --body-file - < /dev/null`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Title must be 1-200 characters.","field":"--title","details":{"min_length":1,"max_length":200,"received_length":0},"hint":"Pass a non-empty --title; keep the other flags unchanged.","temporary":false}
```

(Only the first validation failure is reported; empty stdin would be reported next as `field: "--body-file"`.)

Rate limited — `notectl note search --machine --query 'latency'`, exit `6` after built-in retries exhausted:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_01HZX9","details":{"retries_attempted":2}}
```

Unknown outcome on create — exit `7`:

```json
{"code":"TIMEOUT","message":"Create request timed out after 10000 ms; the note may or may not have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key":"b1c7e0e2-5f0a-4c55-9d1e-2f6c1a0f9e11","safe_retry":"rerun with the same --idempotency-key within 24h"},"request_id":"req_01HZXA"}
```

(Without an original idempotency key, `details.safe_retry` is `"none: do not retry automatically"`.)

Export target exists — exit `10`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes-export.ndjson","hint":"Add --overwrite, or choose a different --output path.","temporary":false}
```

Unauthenticated — exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credential found.","details":{"sources_checked":["env:NOTECTL_TOKEN","keychain:notectl/default","file:~/.config/notectl/credentials.json"]},"hint":"Set NOTECTL_TOKEN, or pipe a token to notectl auth login --token-stdin.","temporary":false}
```

## 6. Behavioural rules not captured as schema fields

- Human mode (no `--machine`): tables on stdout when stdout is a TTY, JSON otherwise; color/progress decided per stream by TTY status; prompts only when stdin is a TTY and `--no-input` is unset. No command ever prompts in machine mode.
- No banners, update checks, or telemetry; no network calls on `schema`, `--help`, `auth status`, or `config show`; these target sub-100ms with lazy imports.
- `--debug` is human-mode only; all debug output is redacted.
- Interactive `auth login` has a non-interactive twin: `--token-stdin`, or `NOTECTL_TOKEN`.
- `hint` text never echoes caller input as a shell string; repair data lives in `details`/`field`.
- Untrusted values (titles, queries, paths) are never passed to a shell.

## 7. Checklist walk (design Done Criteria)

| Checklist section | Answer |
|---|---|
| Command Model | `notectl note <verb>`; one selector (id positional); shared verbs; conventional flags (`--limit`, `--output`, `--timeout-ms`, `--format`). `--filter` N/A: tag filter is the only filter the API supports, exposed as `--tag`. |
| Machine Schema | §3: tree, flags, units, profiles, stdin, auth/scopes, classes, dialect, exit + symbolic codes, per-command catalogs, side effects, latency, timeouts/retries, pagination/artifact, version policy, fingerprint + scope, per-command `schema <command>`. Aliases/deprecations: none at 1.0 (declared empty). |
| Stdin Contract | Declared per command; only `note create --body-file -` reads stdin, explicit flag, 1 MiB, empty → error. |
| Shell Safety | `--` declared and used in examples; values quoted; no shell interpolation; hints carry no shell strings. |
| Agent-Safe Invocation | `--machine` profile; `--isolated` distinct and still works with `NOTECTL_TOKEN`; per-stream TTY rules; non-interactive login; fast metadata paths; `--timeout-ms` on all networked commands. |
| Output | stdout payload only; `single-error-object` framing; classes declared (`list`, `record`, `artifact`); `--dry-run` alternates declared; `--select` projection declared; deterministic sorts with id tiebreak; cursor contract; `--output` only on export with path/size/hash; UTC timestamps. Streaming/NDJSON stdout and `completion_record`: N/A — no command streams to stdout (export writes NDJSON to a file atomically, so no partial artifact). |
| Errors And Exit Codes | §3 exit map + domain 10/11; required fields on every error; `INTERNAL` fallback; `TRANSPORT_ERROR` on networked commands; unknown-code policy. Partial failure: N/A — no multi-item mutations; export is all-or-nothing. |
| Ambient State | Credential/config/env/cache sources, precedence, disable, inspect (`auth whoami`, `auth status`, `config show --resolved`), redaction; no token flag. CWD does not select context. |
| Mutations And Long-Running Work | `create`/`delete` explicit verbs; `--dry-run` on both; `--if-exists` on delete, `--idempotency-key` on create; reconciliation and retry safety declared; signal semantics declared; local writes atomic. Async jobs: N/A — nothing outlives the process; export declares `--deadline-ms` and interrupt behavior. |
| Side Effects And Telemetry | Reads never write (cache holds only schema/capability metadata, atomic writes); telemetry/update checks off. |
| Prose Surfaces | Summaries lead with constraints, and sibling summaries (`list` vs `search`) state the distinguishing fact. |
| Tests | Ship: schema snapshot + fingerprint stability; each success payload above; each error payload above with exit code asserted against the catalog; TTY vs non-TTY per stream; machine-mode suppression; `--body-file -` with empty, oversized, and TTY stdin; pagination and `CURSOR_EXPIRED`; `--select` projection; export artifact hash/size and atomicity under SIGINT and concurrent writers; flag > env > config precedence and `--isolated`; dry-run outputs differ from real ones and make no API mutation; create retry with same key returns `idempotent_replay: true`; delete interrupt behavior. Deprecation tests: N/A until the first deprecation. |
~~~~~~
