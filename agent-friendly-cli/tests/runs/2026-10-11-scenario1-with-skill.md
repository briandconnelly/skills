# Scenario 1 (Design) — with-skill run (final wording)

- **Date:** 2026-10-11
- **Tree:** `9fa4763` (branch `fix/agent-friendly-cli-review-2026-10-11`, final skill wording after commit 4)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set). Final-wording validation run; the earlier run against commit 3's wording is in `2026-10-11-scenario1-with-skill-prefix.md`.
- **Score:** 9/9 scored
- **Subagent tokens:** 131,146 (harness-reported total for the run; 13.0 minutes)
- **Transcript sha256:** `e4333a2b460dd3126e26d60e22abc32eab2e77330b96f25c9cafcde1d3c57a93` (session-local copy; not committed)

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files or run git.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; five `Bash` calls that wrote and validated its own schema and payload JSON in the session scratchpad (outside the repository); nothing under `tests/`; no repository write (tracked tree verified clean afterwards).

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| A1 | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | `canonical_machine_profile: ["--machine"]`; `--machine` `implies` `--json`, `--no-progress`, `--no-color`, each declared once in `global_flags`. |
| A2 | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | Tool-level `exit_codes` map with symbolic codes per exit; `errors_possible` on every command (13 occurrences), with `retryable`, `reconcile_first`, `suppressed_by`. |
| A3 | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | `stderr_framing: "ndjson-typed"` with a description of the closed `progress\|warning\|error` type set; stdout declared payload-only. |
| A4 | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "No confirmation prompt; the verb is the trigger"; `alternate_outputs["--dry-run"]` shape `{dry_run: true, planned_action: "delete", id, title}`. |
| A5 | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | `list` shape `{items, has_more, next_cursor?, limit, estimated_total?}`; `--cursor` declared opaque. |
| A6 | Export is the only `--output <file>` command and returns path, byte size, and content hash (Output). | **PASS** | `--output` declared once (on `note export`); artifact shape `{path, absolute_path, byte_size, content_hash, ...}`; atomic temp-then-rename write. |
| A7 | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | `--timeout-ms` with `"unit": "ms"`. |
| A8 | Each command declares one output class; any flag that switches the class declares the switch (Output). | **PASS** | One `output.class` per command; `alternate_outputs` on `create`, `delete`, and `export` for `--dry-run`. |
| A9 | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | `auth whoami`, `config show --resolved`, `--isolated` and `--no-config` declared; ambient-state block in the schema. |

**Set:** challenge.
**Regression vs 2026-06-09 baseline (1/9):** none (prompt unchanged since that baseline).
**Overhead:** 131,146 subagent tokens; no same-day baseline (prompt unchanged). This run and the pre-commit-4 run (109,083) are the two most expensive arms of the day; design scenarios produce long schemas.
**Defect the assertions did not catch (found by Copilot review):** the canonical examples at `notectl note search -- "quarterly budget" --machine --select id,title,score` and `notectl note search -- "budget" --machine` place options after `--`, so a conforming parser treats `--machine` and `--select` as operands.
The pre-commit-4 run put `--machine` before `--` in every example.
Recorded here as a finding against the skill (no rule said where options go relative to `--`); the checklist Shell Safety section now states it and scenario 1 gained assertion A10; this record's verbatim output is unchanged and the 9/9 score stands for the nine assertions in force when it ran.
**Notes:** same 9/9 as the pre-commit-4 run; no regression from the wording change.
This run chose `ndjson-typed` stderr framing where the earlier run chose `single-error-object`; both are the checklist's closed-enum values, so the choice is design latitude, not drift.
The run also self-validated its JSON in the scratchpad, which the skill does not ask for.

## Full final output

Verbatim final message returned by the subagent:

# `notectl` agent-facing CLI contract

Skill routing (SKILL.md Workflow): audience = **tool author** (you are designing the tool), task = **new CLI design** → followed `references/design-workflow.md` §1–§6 with `references/contract-checklist.md` as the standard and `references/examples.md` for shapes. Nothing in the repo was modified and git was not run. The schema and payloads below were written to the scratchpad and validated (details under "Verification performed").

---

## 1. Task model (design-workflow §1)

| Agent job | Class | Minimum input | Minimum output for the next step |
|---|---|---|---|
| enumerate notes | `query` | none (optional tag filter, cursor) | ids + titles + tags + `has_more`/`next_cursor` |
| fetch one note | `inspect` | `id` | full record incl. `body` |
| find notes by text | `query` | `query` string | ids + titles + score, paginated |
| create a note | `mutate` | `title` | full record incl. server-assigned `id` |
| delete a note | `mutate` | `id` | `{id, deleted}` |
| export all notes to a file | `query` (remote read-only, local write) | `--output` path | `{path, byte_size, content_hash, note_count}` |
| discover the contract | `discover` | none | schema / fingerprint / version |
| inspect identity and resolved state | `inspect`/`admin` | none | `whoami`, `config show --resolved` |
| non-interactive credential bootstrap | `admin` | token on stdin | `{account_id, credential_path}` |

Decisions that fall out of the model:

- One primary selector per resource: `id` positional for `get`/`delete`; free-text positional for `search`; `create` takes named flags because `title` is not a selector.
- `list` vs `search` is the one sibling pair that needs a crisp split: **list = enumerate by metadata (tag), search = full-text on title/body**. Summaries say exactly that and nothing else.
- `--filter tag=<tag>` is the filter flag on `list`/`search`/`export`; `--tag <tag>` on `create` *assigns* a tag. Kept as two different names so one flag does not change meaning across commands (checklist § Command Model).
- `body` is excluded from the default `--select` on `list`/`search` (token cost); `get` returns everything.
- No bulk/multi-item commands, no async jobs, no stream class in 1.0 (declared as not-applicable in the schema with justification).
- No interactive prompts in **any** mode, so there is no `--yes`; the verb `delete` is the trigger.

## 2. Command surface

```
notectl note list      [--filter tag=<t>]... [--limit N] [--cursor C] [--sort S] [--select F,...]
notectl note get       <id> [--select F,...]
notectl note search    <query> [--filter tag=<t>]... [--limit N] [--cursor C] [--sort S] [--select F,...]
notectl note create    --title <title> [--body <text> | --body-file <path> | --body-stdin] [--tag <t>]... [--idempotency-key K] [--dry-run]
notectl note delete    <id> [--if-exists] [--dry-run]
notectl note export    --output <path> [--format ndjson|json] [--filter tag=<t>]... [--overwrite] [--dry-run]

notectl auth login     --token-stdin
notectl auth whoami
notectl config show    --resolved
notectl schema         [<command>] [--fingerprint]
notectl version

Global: --machine (implies --json --no-progress --no-color) | --json | --no-progress | --no-color
        --isolated | --no-config | --api-url URL | --timeout-ms N | --retries N | --debug-log PATH | --help | --
```

### `--help` text (prose surfaces, rules-then-context)

```
notectl — manage notes (id, title, body, tags) in the remote notes API.

Machine use: add --machine. JSON success payload on stdout; stderr is NDJSON records
typed progress|warning|error; on failure stdout is empty and the last stderr line is the
error record. Branch on its "code" field, never on "message". Exit 0 success, 2 validation,
3 not found, 4 unauthenticated, 5 forbidden, 6 rate limited, 7 timeout, 8 conflict, 9 transient.
Auth: NOTECTL_TOKEN, or `printf '%s' "$TOKEN" | notectl auth login --token-stdin`. No prompts in any mode.
Full contract: notectl schema   Cache key: notectl schema --fingerprint

Commands
  note list      Enumerate notes, newest-updated first, optionally filtered by exact tag;
                 body omitted unless selected. Use `note search` for text matching.
  note get       Fetch one note by id with every field, including body.
  note search    Full-text match on title and body, best match first; body omitted unless
                 selected. Use `note list` to enumerate by tag without a text query.
  note create    Create one note and return it in full. --title required; body from --body,
                 --body-file, or --body-stdin (at most one). Pass --idempotency-key so a
                 retry after a timeout cannot create a duplicate.
  note delete    Permanently delete one note by id. No confirmation prompt; the verb is the
                 trigger. --if-exists makes a repeat call succeed.
  note export    Write every note (optionally filtered by tag) to one local file; returns
                 path, byte size, sha256. Refuses to overwrite without --overwrite.
  auth login     Store a token read from stdin after verifying it. Not needed if NOTECTL_TOKEN is set.
  auth whoami    Account for the resolved token and where the token came from.
  config show    Every resolved setting with its source; token redacted. Local, no network.
  schema         This contract as JSON. Local, <100 ms, no auth. `--fingerprint` for the cache key.
  version        Tool, schema, and API version. Local.

Values beginning with "-" (e.g. a search query) go after `--`: notectl note search -- "-draft"
```

Canonical examples (quoted where values may contain spaces/metacharacters):

```sh
notectl note list --machine --filter tag=work --limit 50
notectl note get note_8f2k1q --machine
notectl note search -- "quarterly budget" --machine --select id,title,score
printf '%s' "$BODY" | notectl note create --machine --title "Vendor call follow-ups" --body-stdin --tag vendors --tag work --idempotency-key "agent-run-7731-step-4"
notectl note delete note_3bx9m2 --machine --if-exists
notectl note export --machine --output "backups/notes.ndjson"
```

## 3. Machine-readable schema — output of `notectl schema`

Shape dialect is `notectl-compact-v1` (rules are declared inside the schema under `shape_dialect_rules`; JSON Schema would be the zero-explanation alternative). The stderr framing is `ndjson-typed` rather than `single-error-object` so that deprecations, API-version drift, retries and credential-permission warnings have a structured channel on *successful* runs, which the checklist requires machine mode not to hide.

```json
{
  "schema_version": "1.0",
  "fingerprint": "nct-7f3a9c21",
  "fingerprint_scope": "schema-contract",
  "fingerprint_input": "sha256 over this document with the fingerprint field removed; the tool's release version is not an input, so version-only releases keep the fingerprint",
  "compatibility": {
    "additive_minor_bump": ["new commands", "new optional flags", "new optional output fields", "new filter keys", "new warning codes"],
    "breaking_major_bump": ["removing or renaming a command, flag, field, or code", "changing a type or meaning", "remapping an exit code", "changing a default sort, limit, or projection"],
    "rule": "any contract change, additive or breaking, changes the fingerprint; breaking changes also bump the major component of schema_version. Callers must ignore unknown fields in success payloads."
  },
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_rules": "A shape is a JSON object whose values are type expressions. Primitives: string, integer, number, boolean, object. string:rfc3339-utc is an RFC 3339 timestamp in UTC with a Z suffix. a|b|c is a closed enum of string literals. A quoted literal (\"deleted\") or bare true/false is a constant. [T] is an array of T. A bare name from resource_shapes (note, search_hit) inlines that shape. A field name ending in ? is optional and is absent, never null, when not present; every other field is required. A projection rule may remove unselected fields. When format is ndjson, the shape describes each line.",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "end_of_options_supported": true,
  "shell_safety": "operands and flag values (ids, queries, titles, tags, paths) are passed to the HTTP client and filesystem as data; notectl never spawns a shell. Error hint fields contain flag and argument values, never executable shell text.",
  "stderr_framing": "ndjson-typed",
  "stderr_framing_description": "When --json is set (implied by --machine) every stderr line is one JSON object with a type field from the closed set progress|warning|error. progress records are suppressed by --no-progress. On failure exactly one error record is written, it is the last stderr line, stdout is empty, and the process exits nonzero. warning records may precede a success payload. Without --json stderr is free-form human text.",
  "stderr_record_shapes": {
    "progress": {"type": "\"progress\"", "stage": "string", "done?": "integer", "total?": "integer"},
    "warning": {"type": "\"warning\"", "code": "DEPRECATED_FLAG|API_VERSION_DRIFT|CREDENTIAL_FILE_PERMISSIONS|RETRYING", "message": "string", "details?": "object"},
    "error": {"type": "\"error\"", "code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"}
  },
  "error_semantics": "code is the authoritative branch key and is stable across platforms; the numeric exit is the shell fallback. message is the human rendering of code and may restate it; never parse it. temporary is authoritative for retry decisions. field always names a published flag or argument. hint names the smallest correction and preserves the caller's valid inputs; machine-usable repair data (allowed values, limits) is in details.",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Canonical machine profile: JSON on stdout, typed NDJSON on stderr, no progress, no color, no pager. notectl has no prompts in any mode."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Structured JSON success payload on stdout; stderr becomes ndjson-typed."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress records and spinners on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color on both streams. Also honored via NO_COLOR."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Isolation profile: ignore the config file and the credential file. Environment variables remain in effect because the caller set them explicitly; supply NOTECTL_TOKEN to authenticate."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore the config file only; the credential file is still read."},
    {"name": "--api-url", "type": "string", "default": "https://notes.example.com/v1", "description": "Remote API base URL. Precedence: this flag > NOTECTL_API_URL > config file api_url > default."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "minimum": 100, "description": "Per-HTTP-request timeout. Commands that make several requests (export) are bounded per request, not in total."},
    {"name": "--retries", "type": "integer", "default": null, "minimum": 0, "maximum": 10, "description": "Override the per-command retry default. Retries honor retry_after_ms when present, else exponential backoff from 500 ms. Each retry emits a RETRYING warning record."},
    {"name": "--debug-log", "type": "path", "default": null, "description": "Append redacted request/response dumps to this file. Authorization header values are replaced with [redacted]. Never writes to stdout or stderr."},
    {"name": "--help", "type": "boolean", "default": false, "description": "Print help and exit 0. Local, no network, no auth."}
  ],
  "auth": {"required_for": ["note list", "note get", "note search", "note create", "note delete", "note export", "auth whoami"], "not_required_for": ["schema", "version", "config show", "auth login", "--help"], "mechanism": "bearer token", "non_interactive_bootstrap": "printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine, or set NOTECTL_TOKEN and skip login entirely", "roles": "a token is scoped to one account; FORBIDDEN is returned when a token lacks write scope for create/delete"},
  "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_CONFIG", "NO_COLOR", "XDG_CONFIG_HOME"],
  "config": {"reads": true, "path": "$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml), overridable with NOTECTL_CONFIG", "keys": ["api_url"], "disable_with": ["--no-config", "--isolated"]},
  "cache": {"reads": false, "writes": false},
  "credential_requirements": ["bearer token from NOTECTL_TOKEN or the credential file"],
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN", "$XDG_CONFIG_HOME/notectl/credentials.json (mode 0600, written by notectl auth login --token-stdin)"], "secret": true, "redaction": "the token is never written to stdout, stderr, schema examples, or --debug-log; config show --resolved prints [redacted] and the source name"},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml"],
    "environment_variables": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_CONFIG", "NO_COLOR", "XDG_CONFIG_HOME"],
    "caches": [],
    "precedence": "flags > environment variables > config file > built-in defaults",
    "disable": {"--isolated": "ignore config file and credential file", "--no-config": "ignore config file only"},
    "inspect": {"identity": "notectl auth whoami", "resolved_configuration": "notectl config show --resolved", "credential_source": "notectl config show --resolved (token.source)"},
    "secret_intake": "secrets are accepted only via NOTECTL_TOKEN or stdin (auth login --token-stdin). There is no --token flag.",
    "local_write_concurrency": "the credential file is written to a temp file in the same directory and renamed into place; concurrent logins are last-writer-wins. Export uses the same temp-and-rename pattern with the pid in the temp name."
  },
  "telemetry": {"usage_telemetry": "none", "update_check": "none", "network_calls": "only the declared API requests for the invoked command"},
  "non_tty": {"stdout": "not a TTY: no pager, no color; human table still rendered unless --json", "stderr": "not a TTY: no color, no spinners; progress is one record or line per stage", "stdin": "never read unless a command declares a --*-stdin flag; notectl has no prompts in any mode, so a non-TTY stdin changes nothing"},
  "metadata_paths": {"commands": ["--help", "schema", "schema --fingerprint", "schema <command>", "version", "config show --resolved"], "target_latency_ms": 100, "network": false, "auth_validation": false},
  "api_version_negotiation": "requests go to the /v1 path. A 410 or 426 from the server maps to API_VERSION_UNSUPPORTED (exit 1, hint: upgrade notectl). When the server's X-Notes-Api-Minor header exceeds the client's known minor, an API_VERSION_DRIFT warning record is emitted and unknown fields are passed through.",
  "exit_codes": {"0": "success", "1": "generic (IO_ERROR, API_VERSION_UNSUPPORTED)", "2": "usage or validation (VALIDATION_ERROR, CURSOR_EXPIRED)", "3": "not found (NOTE_NOT_FOUND)", "4": "unauthenticated (UNAUTHENTICATED)", "5": "forbidden (FORBIDDEN)", "6": "rate limited (RATE_LIMITED)", "7": "timeout (TIMEOUT)", "8": "conflict (OUTPUT_EXISTS, IDEMPOTENCY_CONFLICT)", "9": "transient, not otherwise classified (TRANSIENT)"},
  "symbolic_error_codes": ["IO_ERROR", "API_VERSION_UNSUPPORTED", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "OUTPUT_EXISTS", "IDEMPOTENCY_CONFLICT", "TRANSIENT"],
  "resource_shapes": {
    "note": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string:rfc3339-utc", "updated_at": "string:rfc3339-utc"},
    "search_hit": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string:rfc3339-utc", "updated_at": "string:rfc3339-utc", "score": "number"}
  },
  "resource_limits": {"id": "^note_[a-z0-9]{6,32}$", "title": "1..200 characters", "body": "0..1048576 bytes UTF-8", "tags": "0..50 tags, each ^[a-z0-9][a-z0-9_-]{0,63}$, deduplicated, stored sorted"},
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search <query>",
      "create": "notectl note create --title <title>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {
      "login": "notectl auth login --token-stdin",
      "whoami": "notectl auth whoami"
    },
    "config": {
      "show": "notectl config show --resolved"
    },
    "schema": "notectl schema [<command>] [--fingerprint]",
    "version": "notectl version"
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes, newest-updated first, optionally filtered by exact tag; body is omitted unless selected. Use note search for text matching.",
      "aliases": [],
      "deprecations": [],
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--filter", "type": "string", "pattern": "^tag=[a-z0-9][a-z0-9_-]{0,63}$", "cardinality": "many", "default": [], "description": "Only notes carrying every given tag (AND). The only filter key in 1.0 is tag.", "examples": ["--filter tag=work --filter tag=urgent"]},
        {"name": "--limit", "type": "integer", "default": 50, "minimum": 1, "maximum": 200},
        {"name": "--cursor", "type": "string", "default": null, "description": "Opaque next_cursor from the previous page."},
        {"name": "--sort", "type": "enum", "enum": ["updated_at:desc", "updated_at:asc", "created_at:desc", "created_at:asc", "title:asc", "title:desc", "id:asc"], "default": "updated_at:desc", "description": "Ties are always broken by id ascending, so the order is total and deterministic."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "[note]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "projection": {"flag": "--select", "rule": "only selected fields are present on each item; unselected fields are absent, not null. id is always present."}, "size_mode": "bounded by --limit; body only when selected"},
      "pagination": {"style": "cursor", "cursor_opaque": true, "cursor_lifetime_ms": 600000, "expired_code": "CURSOR_EXPIRED", "restart": "re-run without --cursor", "consistency": "best-effort; a note created or deleted mid-walk may appear twice or not at all", "next_cursor_present": "only when has_more is true"},
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": ["GET /v1/notes"]},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"], "backoff": "retry_after_ms when present, else exponential from 500 ms"},
      "async": false,
      "streaming": false,
      "artifact": false,
      "signals": "SIGINT/SIGTERM: exit 130/143 with no error record; nothing to clean up",
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Fetch one note by id with every field, including body.",
      "aliases": [],
      "deprecations": [],
      "classification": "inspect",
      "read_only": true,
      "arguments": [
        {"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]{6,32}$", "examples": ["note_8f2k1q"]}
      ],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null. id is always present."}, "size_mode": "small; body up to 1 MiB"},
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": ["GET /v1/notes/{id}"]},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"], "backoff": "retry_after_ms when present, else exponential from 500 ms"},
      "async": false,
      "streaming": false,
      "artifact": false,
      "signals": "SIGINT/SIGTERM: exit 130/143 with no error record; nothing to clean up",
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search <query>",
      "summary": "Full-text match on title and body, best match first; body is omitted unless selected. Use note list to enumerate by tag without a text query.",
      "aliases": [],
      "deprecations": [],
      "classification": "query",
      "read_only": true,
      "arguments": [
        {"name": "query", "type": "string", "cardinality": "one", "minimum_length": 1, "maximum_length": 256, "description": "Free text; server-side tokenized, case-insensitive. Quote it; use -- before a query that begins with -.", "examples": ["\"quarterly budget\"", "-- \"-draft\""]}
      ],
      "flags": [
        {"name": "--filter", "type": "string", "pattern": "^tag=[a-z0-9][a-z0-9_-]{0,63}$", "cardinality": "many", "default": [], "description": "Only hits carrying every given tag (AND)."},
        {"name": "--limit", "type": "integer", "default": 20, "minimum": 1, "maximum": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["relevance:desc", "updated_at:desc", "updated_at:asc"], "default": "relevance:desc", "description": "Ties broken by id ascending. Relevance scores are stable for an unchanged index."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at", "score"], "cardinality": "many", "default": ["id", "title", "tags", "updated_at", "score"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "[search_hit]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "projection": {"flag": "--select", "rule": "only selected fields are present on each item; unselected fields are absent, not null. id is always present."}, "size_mode": "bounded by --limit; body only when selected"},
      "pagination": {"style": "cursor", "cursor_opaque": true, "cursor_lifetime_ms": 600000, "expired_code": "CURSOR_EXPIRED", "restart": "re-run without --cursor", "consistency": "best-effort", "next_cursor_present": "only when has_more is true"},
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": ["GET /v1/notes/search"]},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"], "backoff": "retry_after_ms when present, else exponential from 500 ms"},
      "async": false,
      "streaming": false,
      "artifact": false,
      "signals": "SIGINT/SIGTERM: exit 130/143 with no error record; nothing to clean up",
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <title>",
      "summary": "Create one note and return it in full. --title is required; body comes from --body, --body-file, or --body-stdin (at most one); pass --idempotency-key so a retry after a timeout cannot create a duplicate.",
      "aliases": [],
      "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "minimum_length": 1, "maximum_length": 200, "examples": ["--title \"Q4 budget notes\""]},
        {"name": "--body", "type": "string", "default": "", "mutually_exclusive_with": ["--body-file", "--body-stdin"], "description": "Inline body. For bodies with newlines or over a few hundred bytes prefer --body-file or --body-stdin."},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body", "--body-stdin"], "description": "Read the body from this UTF-8 file (max 1048576 bytes)."},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body", "--body-file"], "description": "Read the body from stdin until EOF (max 1048576 bytes). Empty stdin yields an empty body."},
        {"name": "--tag", "type": "string", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "cardinality": "many", "default": [], "maximum_count": 50, "description": "Tag to attach; repeatable. Duplicates are collapsed; stored sorted."},
        {"name": "--idempotency-key", "type": "string", "default": null, "minimum_length": 1, "maximum_length": 128, "description": "Server deduplicates creates with the same key for 24 h and returns the original note (exit 0). The same key with a different title/body/tags fails with IDEMPOTENCY_CONFLICT."},
        {"name": "--dry-run", "type": "boolean", "default": false, "description": "Validate inputs locally and report the planned note without any network call."}
      ],
      "stdin_contract": {"reads": "only when --body-stdin is set", "auto_detected_when_piped": false, "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": 1048576, "can_block": "yes, until EOF, only when --body-stdin is set; never otherwise", "mutually_exclusive_with": ["--body", "--body-file"], "empty_stdin": "accepted; body is the empty string"},
      "output": {"class": "record", "format": "json", "shape": "note", "size_mode": "small; echoes body up to 1 MiB"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": "true", "planned_action": "\"create\"", "title": "string", "body_bytes": "integer", "tags": "[string]", "idempotency_key?": "string"}, "size_mode": "small", "note": "never byte-identical to real output: has dry_run and no id"}
      },
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "network": ["POST /v1/notes"], "dry_run": "no network calls and no writes; validates title, body size, tag format, and flag exclusivity locally. Cannot detect UNAUTHENTICATED or FORBIDDEN; latency class local."},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "note": "when --idempotency-key is set, retries default to 2 on TRANSIENT, RATE_LIMITED, and TIMEOUT because the server deduplicates"},
      "reconciliation": "On TIMEOUT or interrupt the outcome is unknown: the server may have committed the note after the client gave up. With --idempotency-key, re-run the identical command; the server returns the existing note or creates it once. Without a key, run notectl note search \"<title>\" --sort updated_at:desc --select id,title,created_at and look for a note whose created_at is after the attempt before retrying.",
      "signals": "SIGINT/SIGTERM during the request: the client exits 130/143 with no error record; a request already received by the server completes. Follow the reconciliation path. No local state is written.",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "note": "retryable without reconciliation only when --idempotency-key was set"},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true, "note": "retryable without reconciliation only when --idempotency-key was set"},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete one note by id. No confirmation prompt in any mode; the verb is the trigger. --if-exists makes a repeat call succeed.",
      "aliases": [],
      "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [
        {"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]{6,32}$", "examples": ["note_8f2k1q"]}
      ],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "Exit 0 with deleted: false when the note does not exist instead of NOTE_NOT_FOUND."},
        {"name": "--dry-run", "type": "boolean", "default": false, "description": "Confirm the note exists with a read-only GET and report the planned deletion; nothing is deleted."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "deleted": "boolean"}, "size_mode": "small", "note": "deleted is false only with --if-exists when the note was already absent"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": "true", "planned_action": "\"delete\"", "id": "string", "title": "string"}, "size_mode": "small"}
      },
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "network": ["DELETE /v1/notes/{id}"], "dry_run": "one read-only GET /v1/notes/{id}; no writes, no cache, no token refresh"},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "note": "when --if-exists is set, retries default to 2 on TRANSIENT, RATE_LIMITED, and TIMEOUT because a repeated delete is then idempotent"},
      "reconciliation": "On TIMEOUT or interrupt the outcome is unknown. Run notectl note get <id>: NOTE_NOT_FOUND means the delete committed; a note means it did not. Re-running with --if-exists is safe in either case.",
      "signals": "SIGINT/SIGTERM during the request: the client exits 130/143 with no error record; a request already received by the server completes. Follow the reconciliation path. No local state is written.",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "note": "retryable without reconciliation when --if-exists is set"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true, "note": "retryable without reconciliation when --if-exists is set"},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write every note (optionally filtered by tag) to one local file and return a pointer with size and hash. Refuses to overwrite without --overwrite. Read-only against the API.",
      "aliases": [],
      "deprecations": [],
      "classification": "query",
      "read_only": true,
      "read_only_scope": "remote; the only write is the declared local output file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "Destination file. Written atomically: data goes to <path>.tmp-<pid> in the same directory, then renamed. The parent directory must exist."},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one full note per line, no trailer. json: {\"schema_version\",\"exported_at\",\"notes\":[...]}."},
        {"name": "--filter", "type": "string", "pattern": "^tag=[a-z0-9][a-z0-9_-]{0,63}$", "cardinality": "many", "default": [], "description": "Only notes carrying every given tag (AND)."},
        {"name": "--overwrite", "type": "boolean", "default": false, "description": "Replace an existing file at --output instead of failing with OUTPUT_EXISTS."},
        {"name": "--dry-run", "type": "boolean", "default": false, "description": "Check the destination and count matching notes with one read-only request; write nothing."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "absolute_path": "string", "byte_size": "integer", "content_hash": "string", "format": "ndjson|json", "note_count": "integer", "exported_at": "string:rfc3339-utc"}, "size_mode": "small pointer; the file grows with the collection", "path_style": "path is echoed exactly as given; absolute_path is resolved with forward slashes on every platform; content_hash is sha256:<hex> of the file bytes"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": "true", "planned_action": "\"export\"", "path": "string", "absolute_path": "string", "format": "ndjson|json", "estimated_note_count": "integer", "would_overwrite": "boolean"}, "size_mode": "small"}
      },
      "file_contents": {"ndjson": "one note record per line, full shape, ordered id:asc", "json": {"schema_version": "\"1.0\"", "exported_at": "string:rfc3339-utc", "notes": "[note]"}},
      "pagination": {"internal": true, "style": "cursor, 200 per page, ordered id:asc", "consistency": "best-effort; not a snapshot. An internal CURSOR_EXPIRED restarts the walk once, then surfaces as TRANSIENT", "exposed_to_caller": false},
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": ["local file at --output (atomic temp-and-rename)"], "network": ["GET /v1/notes (repeated per page)"], "dry_run": "one GET /v1/notes?limit=1 to read estimated_total plus local stat of --output; no file is written or created"},
      "latency_class": "slow",
      "timeout_defaults_ms": 10000,
      "timeout_note": "--timeout-ms bounds each page request; total wall time scales with note count. Progress records report done/total pages when enabled.",
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"], "backoff": "retry_after_ms when present, else exponential from 500 ms", "scope": "per page request"},
      "signals": "SIGINT/SIGTERM: the temp file is removed, the destination is untouched (an existing file is never partially overwritten), exit 130/143. Safe to re-run from scratch.",
      "local_write_concurrency": "two concurrent exports to the same --output each write their own pid-named temp file; the last rename wins (documented last-writer-wins); both files are complete",
      "async": false,
      "streaming": false,
      "artifact": true,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "IO_ERROR", "exit": 1},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth login --token-stdin",
      "summary": "Store a bearer token in the credential file after verifying it with one read-only request. The token is read from stdin only; there is no --token flag. Not needed if NOTECTL_TOKEN is set.",
      "aliases": [],
      "deprecations": [],
      "classification": "admin",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--token-stdin", "type": "boolean", "required": true, "description": "Read the token from stdin until EOF; trailing newline is stripped."}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "accepted_formats": ["text/plain; one token"], "maximum_input_size": 4096, "can_block": "yes, until EOF", "mutually_exclusive_with": [], "empty_stdin": "VALIDATION_ERROR with field --token-stdin"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "credential_path": "string"}, "size_mode": "small"},
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": ["$XDG_CONFIG_HOME/notectl/credentials.json, mode 0600, atomic temp-and-rename"], "network": ["GET /v1/me"], "dry_run": "not-applicable: the only effect is the local credential write, which is atomic and reversible by deleting the file; an invalid token already fails before any write"},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"]},
      "signals": "SIGINT/SIGTERM: temp file removed; existing credential file untouched",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "note": "empty stdin, token over 4096 bytes, or --isolated set (nowhere to write)"},
        {"code": "IO_ERROR", "exit": 1},
        {"code": "UNAUTHENTICATED", "exit": 4, "note": "the supplied token was rejected; nothing is written"},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Report the account the resolved token belongs to and where the token came from.",
      "aliases": [],
      "deprecations": [],
      "classification": "inspect",
      "read_only": true,
      "arguments": [],
      "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "token_source": "env|credential-file", "api_url": "string"}, "size_mode": "small"},
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": ["GET /v1/me"]},
      "latency_class": "network",
      "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["TRANSIENT", "RATE_LIMITED", "TIMEOUT"]},
      "signals": "SIGINT/SIGTERM: exit 130/143; nothing to clean up",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Print every resolved setting with the source it came from; the token value is redacted. Local only, no network, no auth.",
      "aliases": [],
      "deprecations": [],
      "classification": "inspect",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--resolved", "type": "boolean", "default": true, "description": "Always on in 1.0; accepted for forward compatibility with a future raw view."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"api_url": {"value": "string", "source": "flag|env|config-file|default"}, "token": {"value": "\"[redacted]\"|null", "source": "env|credential-file|none"}, "config_path": "string", "config_read": "boolean", "credential_path": "string", "credential_read": "boolean", "isolated": "boolean", "timeout_ms": "integer"}, "size_mode": "small"},
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": []},
      "latency_class": "local",
      "timeout_defaults_ms": null,
      "retry_defaults": {"retries": 0},
      "signals": "SIGINT/SIGTERM: exit 130/143; nothing to clean up",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "note": "config file present but unparseable; details.path names it"}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>] [--fingerprint]",
      "summary": "Print this contract (or one command's entry, or only the fingerprint) as JSON. Local, under 100 ms, no network, no auth.",
      "aliases": [],
      "deprecations": [],
      "classification": "discover",
      "read_only": true,
      "arguments": [
        {"name": "command", "type": "string", "cardinality": "zero-or-one", "description": "A canonical path such as \"note create\" to print only that command entry plus the top-level fields.", "examples": ["\"note create\""]}
      ],
      "flags": [
        {"name": "--fingerprint", "type": "boolean", "default": false, "description": "Print only schema_version, fingerprint, and fingerprint_scope."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "this document", "size_mode": "medium (tens of KiB); use --fingerprint or <command> for compact loads"},
      "alternate_outputs": {
        "--fingerprint": {"class": "record", "format": "json", "shape": {"schema_version": "string", "fingerprint": "string", "fingerprint_scope": "\"schema-contract\""}, "size_mode": "small"}
      },
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": []},
      "latency_class": "local",
      "timeout_defaults_ms": null,
      "retry_defaults": {"retries": 0},
      "signals": "SIGINT/SIGTERM: exit 130/143; nothing to clean up",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "note": "unknown command path; details.known_commands lists valid paths"}
      ]
    },
    {
      "canonical_invocation_path": "notectl version",
      "summary": "Print the tool version, schema version, and pinned API version. Local, no network.",
      "aliases": [],
      "deprecations": [],
      "classification": "discover",
      "read_only": true,
      "arguments": [],
      "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"version": "string", "schema_version": "string", "api_version": "\"v1\""}, "size_mode": "small"},
      "pagination": false,
      "truncation": false,
      "side_effects": {"external_mutation": false, "writes": [], "network": []},
      "latency_class": "local",
      "timeout_defaults_ms": null,
      "retry_defaults": {"retries": 0},
      "signals": "SIGINT/SIGTERM: exit 130/143; nothing to clean up",
      "async": false,
      "streaming": false,
      "artifact": false,
      "errors_possible": []
    }
  ],
  "not_applicable": {
    "long_running_jobs": "no command is async: every command is one request or a bounded page walk, so there are no job IDs, polling, wait, or cancel operations",
    "partial_failure": "no command accepts multiple items in 1.0; export is all-or-nothing (no file on failure), so there is no --allow-partial or partial: true",
    "streaming_output": "no stream-class command in 1.0; whole-collection access is the export artifact",
    "aliases_and_deprecations": "none in 1.0; the fields are present and empty so a future alias is declared, not improvised"
  },
  "tests_to_ship": [
    "schema snapshot and fingerprint stability across a version-only bump",
    "canonical success payload per command including each --select projection and each --dry-run shape",
    "representative failure payload and exit code per catalog entry, with a runtime assertion that the observed exit equals the declared exit",
    "stdout is empty on every failure in --machine mode; the error record is the last stderr line and parses as JSON",
    "TTY vs non-TTY per stream: no pager or color on non-TTY stdout, no spinner on non-TTY stderr",
    "--machine suppresses progress, color, and prose; no prompt in any mode (stdin closed)",
    "stdin: --body-stdin with empty, 1 MiB, and 1 MiB + 1 byte inputs; create without --body-stdin never reads stdin; auth login empty stdin is VALIDATION_ERROR",
    "pagination: has_more/next_cursor presence rules, CURSOR_EXPIRED mapping, restart without cursor",
    "export: atomic write, OUTPUT_EXISTS vs --overwrite, content_hash matches file, SIGINT leaves no temp file and an untouched destination, two concurrent exports both produce complete files",
    "config/env precedence: flag > env > file > default; --isolated ignores file and credential file but honors NOTECTL_TOKEN; --no-config ignores only the config file",
    "secret redaction in config show --resolved and --debug-log",
    "dry-run for create (no network socket opened), delete (only a GET), export (no file created)",
    "interrupt during create/delete: exit 130, no error record, no local writes",
    "--idempotency-key: same key same payload returns the same id; same key different payload is IDEMPOTENCY_CONFLICT exit 8",
    "metadata paths (--help, schema, schema --fingerprint, version, config show) complete under 100 ms with no network and no credential read except config show",
    "-- end-of-options: note search -- -draft treats -draft as the query",
    "deprecations and replacements: placeholder test asserting aliases and deprecations arrays are empty, to be replaced when the first alias lands"
  ]
}
```

`notectl schema --fingerprint`:

```json
{"schema_version": "1.0", "fingerprint": "nct-7f3a9c21", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, `--machine`, exit 0)

`notectl note list --machine --limit 2` (list class; `body` absent by default projection; `next_cursor` present only because `has_more` is true):

```json
{
  "items": [
    {"id": "note_8f2k1q", "title": "Q4 budget notes", "tags": ["finance", "work"], "updated_at": "2026-10-11T18:42:07Z"},
    {"id": "note_3bx9m2", "title": "Standup 2026-10-10", "tags": ["work"], "updated_at": "2026-10-10T16:05:51Z"}
  ],
  "has_more": true,
  "next_cursor": "c1q9ZXk3Lm5vdGVfM2J4OW0y",
  "limit": 2,
  "estimated_total": 47
}
```

Last page of the same walk (`next_cursor` absent, not null):

```json
{"items": [{"id": "note_zz01aa", "title": "Reading list", "tags": [], "updated_at": "2026-09-30T09:12:00Z"}], "has_more": false, "limit": 2, "estimated_total": 47}
```

`notectl note get note_8f2k1q --machine` (record class, full shape):

```json
{
  "id": "note_8f2k1q",
  "title": "Q4 budget notes",
  "body": "Travel line is over by 12%.\nAsk finance about the reallocation window.",
  "tags": ["finance", "work"],
  "created_at": "2026-10-09T14:03:22Z",
  "updated_at": "2026-10-11T18:42:07Z"
}
```

`notectl note search -- "budget" --machine` (list of `search_hit`, relevance order, id tie-break):

```json
{
  "items": [
    {"id": "note_8f2k1q", "title": "Q4 budget notes", "tags": ["finance", "work"], "updated_at": "2026-10-11T18:42:07Z", "score": 0.91},
    {"id": "note_7hq2pd", "title": "Budget retro", "tags": ["finance"], "updated_at": "2026-08-02T11:20:45Z", "score": 0.44}
  ],
  "has_more": false,
  "limit": 20,
  "estimated_total": 2
}
```

`printf '%s' "Send the revised SOW by Friday." | notectl note create --machine --title "Vendor call follow-ups" --body-stdin --tag vendors --tag work --idempotency-key "agent-run-7731-step-4"`:

```json
{
  "id": "note_k2p8wn",
  "title": "Vendor call follow-ups",
  "body": "Send the revised SOW by Friday.",
  "tags": ["vendors", "work"],
  "created_at": "2026-10-11T19:04:12Z",
  "updated_at": "2026-10-11T19:04:12Z"
}
```

Same command with `--dry-run` (no network; never byte-identical to the real result):

```json
{"dry_run": true, "planned_action": "create", "title": "Vendor call follow-ups", "body_bytes": 31, "tags": ["vendors", "work"], "idempotency_key": "agent-run-7731-step-4"}
```

`notectl note delete note_3bx9m2 --machine`:

```json
{"id": "note_3bx9m2", "deleted": true}
```

`notectl note delete note_3bx9m2 --machine --if-exists` when already gone (exit 0):

```json
{"id": "note_3bx9m2", "deleted": false}
```

`notectl note delete note_3bx9m2 --machine --dry-run` (one GET, nothing deleted):

```json
{"dry_run": true, "planned_action": "delete", "id": "note_3bx9m2", "title": "Standup 2026-10-10"}
```

`notectl note export --machine --output "backups/notes.ndjson"` (artifact class):

```json
{
  "path": "backups/notes.ndjson",
  "absolute_path": "/home/agent/work/backups/notes.ndjson",
  "byte_size": 18204,
  "content_hash": "sha256:9c1e8a0f5b7d2c4e6a8b0d2f4c6e8a0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c",
  "format": "ndjson",
  "note_count": 47,
  "exported_at": "2026-10-11T19:06:40Z"
}
```

Same with `--dry-run`:

```json
{"dry_run": true, "planned_action": "export", "path": "backups/notes.ndjson", "absolute_path": "/home/agent/work/backups/notes.ndjson", "format": "ndjson", "estimated_note_count": 47, "would_overwrite": false}
```

`notectl auth whoami --machine`:

```json
{"account_id": "acct_41d9", "token_source": "env", "api_url": "https://notes.example.com/v1"}
```

`notectl config show --resolved --machine` (token redacted, source retained):

```json
{
  "api_url": {"value": "https://notes.example.com/v1", "source": "default"},
  "token": {"value": "[redacted]", "source": "env"},
  "config_path": "/home/agent/.config/notectl/config.toml",
  "config_read": false,
  "credential_path": "/home/agent/.config/notectl/credentials.json",
  "credential_read": false,
  "isolated": false,
  "timeout_ms": 10000
}
```

Non-error stderr records that may precede a success payload under `--json` (suppressed progress with `--machine`):

```ndjson
{"type":"progress","stage":"fetch","done":3,"total":12}
{"type":"warning","code":"RETRYING","message":"Retrying after TRANSIENT (attempt 2 of 3).","details":{"code":"TRANSIENT","attempt":2,"max_attempts":3,"backoff_ms":1000}}
```

## 5. Example error payloads (stderr, `--machine`; stdout empty; the error record is the last stderr line)

**Not found** — `notectl note get note_404xyz --machine`, exit **3**:

```json
{"type": "error", "code": "NOTE_NOT_FOUND", "message": "Note not found.", "resource_id": "note_404xyz", "temporary": false, "hint": "Check the id with notectl note search <query>, or pass --if-exists to notectl note delete.", "request_id": "req_01HZXK3Q"}
```

**Validation (bad tag)** — `notectl note create --machine --title "x" --tag work --tag "Work Items"`, exit **2**. `field` names the published flag; allowed pattern and offending position are machine-usable in `details`, not only in `hint`:

```json
{"type": "error", "code": "VALIDATION_ERROR", "message": "Invalid tag.", "field": "--tag", "details": {"value": "Work Items", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "position": 2}, "hint": "Tags are lowercase letters, digits, _ or -; try --tag work-items.", "temporary": false}
```

**Validation (mutually exclusive flags)** — `--body` with `--body-stdin`, exit **2**:

```json
{"type": "error", "code": "VALIDATION_ERROR", "message": "Flags --body and --body-stdin cannot be combined.", "field": "--body-stdin", "details": {"mutually_exclusive": ["--body", "--body-file", "--body-stdin"]}, "hint": "Remove --body or remove --body-stdin.", "temporary": false}
```

**Rate limited** — any networked command after retries are exhausted, exit **6** (`retry_after_ms` always present; `temporary: true` is the retry signal):

```json
{"type": "error", "code": "RATE_LIMITED", "message": "Rate limit exceeded.", "retry_after_ms": 30000, "details": {"attempts": 3}, "temporary": true, "request_id": "req_01HZXK9A"}
```

**Timeout on a mutation** — `note create` without an idempotency key, exit **7**. `temporary: false` because the catalog marks it `reconcile_first`; the hint carries the reconciliation command as flag/argument values, not a shell string:

```json
{"type": "error", "code": "TIMEOUT", "message": "No response within 10000 ms; the note may or may not have been created.", "details": {"timeout_ms": 10000, "attempts": 1, "idempotency_key": null}, "hint": "Reconcile first: notectl note search \"Vendor call follow-ups\" --sort updated_at:desc --select id,title,created_at. Pass --idempotency-key on the retry.", "temporary": false}
```

**Conflict** — `note export --output backups/notes.ndjson` onto an existing file, exit **8**:

```json
{"type": "error", "code": "OUTPUT_EXISTS", "message": "Output file already exists.", "field": "--output", "path": "backups/notes.ndjson", "hint": "Pass --overwrite or choose another --output path.", "temporary": false}
```

**Unauthenticated** — no token resolvable, exit **4** (lists what was checked; never echoes a token):

```json
{"type": "error", "code": "UNAUTHENTICATED", "message": "No valid credential.", "details": {"token_source": "none", "checked": ["NOTECTL_TOKEN", "/home/agent/.config/notectl/credentials.json"]}, "hint": "Set NOTECTL_TOKEN, or run: printf '%s' \"$TOKEN\" | notectl auth login --token-stdin --machine", "temporary": false}
```

**Expired cursor** — `note list --cursor <stale>`, exit **2**:

```json
{"type": "error", "code": "CURSOR_EXPIRED", "message": "Cursor expired.", "field": "--cursor", "details": {"cursor_lifetime_ms": 600000}, "hint": "Re-run notectl note list without --cursor to restart the walk.", "temporary": false}
```

## 6. Checklist coverage (SKILL.md Done Criteria for design tasks)

| Checklist section | Where answered |
|---|---|
| Command Model | `tool noun verb`, shallow tree, conventional verbs (`list/get/search/create/delete/export`), domain noun `note`; `--filter` vs `--tag` split so no flag changes meaning; `aliases`/`deprecations` present and empty (N/A, justified in `not_applicable`) |
| Machine Schema | Every bullet has a field: tree, flags with types/defaults/enums/cardinality/examples, `--timeout-ms` unit in name, `canonical_machine_profile` with `implies`, `isolation_profile`, per-command `stdin_contract`, `read_only`, `auth`/`environment`/`config`/`cache`/`credential_requirements`, `output` (class/format/shape/size_mode), `shape_dialect` + rules, `exit_codes` + `symbolic_error_codes`, per-command `errors_possible` with `retryable`/`reconcile_first`/`suppressed_by`, `side_effects`, `latency_class`, `timeout_defaults_ms`, `retry_defaults`, `pagination`/`truncation`/`artifact`/`async`/`streaming`, `api_version_negotiation`, `schema_version` + `fingerprint` + `fingerprint_scope` + `fingerprint_input` + `compatibility` |
| Stdin Contract | Declared per command; only `create --body-stdin` and `auth login --token-stdin` read stdin, explicit flag, never auto-detected; limits, blocking, exclusivity and empty-stdin handling declared |
| Shell Safety | `end_of_options_supported: true`, `shell_safety` statement, quoted canonical examples, hints carry flag values not shell strings |
| Agent-Safe Invocation | `--machine` single flag; `--isolated` distinct (env token still works, so authenticated reads complete); no prompts in any mode; `non_tty` per stream; warnings have a structured channel (`ndjson-typed`); `auth.non_interactive_bootstrap`; `metadata_paths` <100 ms, no network; `--timeout-ms` caller-settable with declared retries |
| Output | stdout = payload only; stderr framing declared as closed enum + description; no `message` in success payloads; one output class per command, alternates declared for `--dry-run`; cursor contract (opaque, 10 min, `CURSOR_EXPIRED`, restart, best-effort); `--select` projection rule; deterministic sort with id tie-break; UTC RFC 3339; `--output` only on export, returns path/size/hash |
| Errors And Exit Codes | 0–9 declared with meanings; symbolic `code` authoritative, `temporary` authoritative for retry; required `code`/`message`, recommended fields used; `retry_after_ms` on `RATE_LIMITED`; `field` always a published flag; debug via `--debug-log` opt-in and redacted; partial failure N/A (no multi-item commands) |
| Ambient State | `ambient_state` block: sources, precedence, disable flags, `auth whoami` + `config show --resolved` inspection, redaction, secret intake via env/stdin only (no `--token` flag), atomic local writes |
| Mutations And Long-Running Work | Verb is the trigger; `--dry-run` on create/delete/export with declared internal effects; `auth login` dry-run marked N/A with justification; `--idempotency-key`, `--if-exists`; `reconciliation` on every external mutation; `signals` on every command; long-running jobs N/A with justification |
| Side Effects And Telemetry | `telemetry` block: none, no update checks; each command lists its exact network calls; reads have no writes |
| Prose Surfaces | `--help` text and every `summary` written rules-then-context and task-selective (`list` vs `search` disambiguated in both summaries). A separating-context-from-constraints skill was not available in this run's permitted reading set, so no separate audit lens was applied |
| Tests | `tests_to_ship` enumerates every item in checklist § Tests, each mapped to this tool's commands; cancellation of long-running ops N/A (none exist), interrupt and concurrency tests included |

## 7. Verification performed

- Read `SKILL.md` and all four files under `references/` in full; did not read `tests/` or any other repo file; modified nothing in the repo; ran no git commands.
- Wrote the schema and all 25 payloads to the scratchpad and parsed both with `python3 -I -m json.tool`: both valid. Confirmed the validator rejects a deliberately malformed file before trusting the clean result.
- Ran a cross-consistency script over the schema: every `errors_possible` code is in `symbolic_error_codes` and its `exit` matches the `exit_codes` table; every `command_tree` leaf has a `commands` entry; every external mutation has `reconciliation`; every mutating command has `--dry-run` or an N/A justification; machine/isolation profile flags and all `implies` targets are declared global flags; every error payload has `type`/`code`/`message`/`temporary` and `RATE_LIMITED` carries `retry_after_ms`. Result: no problems (11 commands, 12 codes, 25 payloads). Then planted a wrong exit and an orphan tree leaf in a copy and confirmed the same checks reported both.
- Not verified (nothing to run): latency targets, runtime exit mapping, TTY behavior — these are design claims that the `tests_to_ship` list exists to pin once there is an implementation.

## 8. Assumptions and open decisions for the owner

- The remote API is assumed to offer cursor pagination with `estimated_total`, a full-text search endpoint with stable scores, an idempotency-key header on `POST /v1/notes`, and a `/v1/me` endpoint; if any is missing, the corresponding contract items (`estimated_total?`, `score`, `--idempotency-key`, `auth whoami`) need to be removed or re-specified, and that is a breaking change to the fingerprint.
- `created_at`/`updated_at` were added to the note shape (beyond the four fields in the brief) because the default sort needs a deterministic key that is not `id`; drop them and change the default sort to `id:asc` if the API does not return timestamps.
- `--isolated` intentionally keeps environment variables in effect; if you want the stricter reading of the Vocabulary definition (env ignored too), add a `--no-env` flag rather than changing `--isolated`, so `--isolated` can still complete authenticated reads.
- `ndjson-typed` stderr framing was chosen over `single-error-object`; if you prefer the simpler framing, warnings on successful runs need another declared home (e.g. a `warnings?` field in every success payload), which widens every output shape.
- Export streaming to stdout (`--output -`) and a bulk `delete --from-file` were considered and deferred to keep 1.0 narrow; both are additive (minor bump) if added later, and the schema already reserves `completion_record`/`bulk-result` semantics via the checklist.
