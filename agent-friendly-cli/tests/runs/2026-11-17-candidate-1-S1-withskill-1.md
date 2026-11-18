# Scenario 1 (design) — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 1/2 conformance
- **Tokens:** 80,069 (final-turn context plus output, read from the transcript)
- **Output words:** 3,454
- **Transcript sha256:** `fa2e7abc64e08de3b4fa9c4cf4eb52b34b1d3892a5d0102cc7d2b4c75a2570e0` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; global_flags {"name": "--machine", "type": "boolean" |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {"0": "success", ...}, "symbolic_error_codes": [...]; create/delete "errors_possible" lists |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object"; "Example error payloads (stderr only, stdout empty, `single-error-object` framing)" |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | explicit `note delete` verb; "dry_run": "reads the note to confirm it exists; no mutation; output includes dry_run: true" |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": "boolean", "next_cursor?": "string" in list and search shapes |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size": "integer", "content_hash": "string (sha256:<hex>)" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000 |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "ambient_state": {"credentials": ..., "cache": {...}, "disable_with": {"all": "--isolated"}, "inspect_with": ["notectl whoami", ...] |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note delete --if-exists --machine -- "nt_8f2a" |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL", "unknown_code_policy": "non-retryable"; note command catalogs list {"code": "NETWORK_ERROR", "exit": 10} (whoami has no declared error list at all) Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unlisted-code handling = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | {"name": "--tag", ... "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "`--output` only on export" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **FAIL** | schema, whoami, config show appear only in "metadata_commands" with prose, no output class declared |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design). Task: new CLI design.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| List notes | query | none (optional `--tag`, `--limit`, `--cursor`) | page of `{id, title, tags, updated_at}` + `has_more`/`next_cursor` |
| Get a note | inspect | `id` | full record `{id, title, body, tags, created_at, updated_at}` |
| Search notes | query | `--query` text | ranked page of `{id, title, tags, updated_at, score}` |
| Create a note | mutate | `--title`, body (file or stdin), tags | created record (with `id`) |
| Delete a note | mutate | `id` | `{id, status}` |
| Export all notes | admin | `--output` path | `{path, byte_size, content_hash, note_count}` |
| Discover contract | discover | none | schema / fingerprint |

`list` and `search` stay separate: `list` is a deterministic, filter-only enumeration; `search` is relevance-ranked full-text over title and body.
One-line summaries are enough to tell them apart (see `description` fields).
`search` uses the verb the user named rather than `find`.

## 2. Command surface

Shape: `notectl <noun> <verb>`, shallow tree, primary selector for `note` is the ID (positional), everything else is a named flag.

```text
notectl note list    [--tag <tag>]... [--sort updated_at|created_at|title] [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note get     [--select <field>]... [--] <id>
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create  --title <text> (--body-file <path> | --body-stdin) [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete  [--if-exists] [--dry-run] [--] <id>
notectl note export  --output <path> [--overwrite] [--tag <tag>]...

notectl schema [<command path>] [--fingerprint] [--summary]
notectl whoami
notectl config show --resolved
```

Global flags: `--machine` (implies `--json --no-progress --no-color --no-input`), `--json`, `--no-progress`, `--no-color`, `--no-input`, `--isolated`, `--no-config`, `--profile <name>`, `--timeout-ms <n>`, `--api-url <url>`.
`--` end-of-options is supported everywhere; IDs and query strings are passed as data, never to a shell.
Credentials come from `NOTECTL_TOKEN`, a credential file, or the OS keychain; there is no `--token` flag.
Non-interactive bootstrap: set `NOTECTL_TOKEN` (or write the credential file); `notectl auth login` is the interactive human path and is not in the machine contract.

Canonical machine invocations:

```sh
notectl note list --tag "work" --limit 50 --machine
notectl note get --machine -- "nt_8f2a"
notectl note search --query "quarterly plan" --limit 20 --machine
printf '%s' "$BODY" | notectl note create --title "Standup 2026-11-17" --body-stdin --tag "work" --idempotency-key "c0a8-01" --machine
notectl note delete --if-exists --machine -- "nt_8f2a"
notectl note export --output "./notes-export.ndjson" --machine
```

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum, trailing `?` marks optional, fields are required unless so marked or removed by a declared projection, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes added to a catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping"],
    "rule": "any contract change changes the fingerprint; breaking changes also bump the major version"
  },
  "fingerprint": "ntc-5e91c07a",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "encoding": {"charset": "utf-8", "timestamps": "RFC 3339 UTC (Z)", "numbers": "JSON numbers, locale-independent"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--no-input"], "description": "Machine mode: structured output only, never prompts, no color, progress, pager, or browser launch."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit success payloads as JSON on stdout and errors as JSON on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color on all streams."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required input fails with VALIDATION_ERROR."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the cache; credentials only from NOTECTL_TOKEN. Normal authenticated commands still work when NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to read; overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "API base URL; overrides NOTECTL_API_URL and config."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "Per-request network timeout. Per-command defaults below override the global default."}
  ],
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified", "10": "network transport failure (domain-specific)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED", "TRANSIENT", "NETWORK_ERROR"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "non-retryable",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "auth": {"required": true, "commands_exempt": ["schema", "config show"], "scopes": {"notes:read": ["note list", "note get", "note search", "note export"], "notes:write": ["note create", "note delete"]}},
  "ambient_state": {
    "credentials": ["NOTECTL_TOKEN env var", "~/.config/notectl/credentials (mode 0600)", "OS keychain entry notectl/<profile>"],
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "NO_COLOR"],
    "cache": {"reads": true, "writes": true, "path": "$XDG_CACHE_HOME/notectl/", "contents": "schema fingerprint and API capability metadata only; never note content", "write_safety": "atomic replace (write temp + rename)"},
    "cwd_selects_context": false,
    "precedence": "flags > environment variables > config file > cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl whoami", "notectl config show --resolved"],
    "secret_values": ["token"],
    "secret_redaction": "token is shown only as {source, last4} in every output, error, and debug dump"
  },
  "telemetry": {"default": "off", "update_check": "off", "machine_mode": "suppressed"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes, newest-updated first by default. Filter by exact tag; does not match text. Use note search for text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": []},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "created_at", "title"], "default": "updated_at", "description": "updated_at and created_at sort descending, title ascending; ties broken by id ascending"},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "array of note summaries (fields per --select)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "size_mode": "paged; body excluded by default"},
      "pagination": {"cursor_opaque": true, "cursor_lifetime_ms": 900000, "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential from 250ms, honors retry_after_ms"},
      "async": false, "streaming": false, "truncation": false, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 10, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "description": "Fetch one note by id, including body. Reads the primary store (read-your-writes).",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[a-z0-9]+$", "cardinality": "one", "examples": ["nt_8f2a"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "body": "string", "tags": "array of string (sorted ascending)", "created_at": "string", "updated_at": "string"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "small; body capped at 1 MiB by the API"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 10, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "description": "Full-text search over title and body, ranked by relevance. Index lags writes by up to 30s; absence from results does not prove absence.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body", "score"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at", "score"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "list", "format": "json", "shape": {"items": "array of note summaries with score (fields per --select)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"}, "sort": "score descending, ties by id ascending", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "size_mode": "paged"},
      "pagination": {"cursor_opaque": true, "cursor_lifetime_ms": 900000, "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "async": false, "streaming": false, "truncation": false, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 10, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file <path>",
      "description": "Create one note. Pass --idempotency-key on every attempt you might retry; without it a timed-out create is not safe to retry.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "max_length": 200},
        {"name": "--body-file", "type": "path", "default": null, "exclusive_group": "body"},
        {"name": "--body-stdin", "type": "boolean", "default": false, "exclusive_group": "body"},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "default": []},
        {"name": "--idempotency-key", "type": "string", "max_length": 64, "default": null, "description": "Server deduplicates creates with the same key for 24h; reuse the same key on retry."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "required_groups": [{"group": "body", "rule": "exactly one of --body-file or --body-stdin"}],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["text/plain; charset=utf-8", "text/markdown"], "maximum_input_size": 1048576, "can_block": "only when --body-stdin is given and the writer has not closed stdin; never waits on a TTY in machine mode (fails VALIDATION_ERROR instead)", "mutually_exclusive_with": ["--body-file"], "empty_stdin": "accepted as an empty body"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "body": "string", "tags": "array of string", "created_at": "string", "updated_at": "string", "replayed": "boolean"}, "shape_description": "replayed is true when the idempotency key matched an earlier create and the original note is returned", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "note": {"title": "string", "body_bytes": "integer", "tags": "array of string"}}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "description": "creates a note unless --dry-run", "dry_run": "validates inputs locally and against the API's validate endpoint; no note is created; output includes dry_run: true"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "description": "no automatic retries; the caller decides using the reconciliation rule"},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key used on the original attempt. A key added only on the retry does not deduplicate. Without a key the create is not safe to retry automatically; note search cannot prove absence (index lag).",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "closed_stdout": "finishes the create, then exits",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "description": "rejected before the write; safe to retry"},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "same key reused with different title/body/tags"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 10, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Delete one note by id. Permanent. Use --if-exists to make it repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[a-z0-9]+$", "cardinality": "one", "examples": ["nt_8f2a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "planned_action is none only with --if-exists when the note does not exist", "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm it exists; no mutation; output includes dry_run: true"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the declared recovery is to re-run with --if-exists. note get reads the primary store and shows current absence, not which attempt removed it.",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "closed_stdout": "finishes the delete, then exits",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 10, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "description": "Write all notes (optionally tag-filtered) to a local NDJSON file; stdout gets only a pointer to the file. Fails if the file exists unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "admin", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "examples": ["./notes-export.ndjson"]},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "deadline for the whole export, not per request"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string (absolute, POSIX separators)", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "note_count": "integer", "format": "ndjson", "consistency": "best-effort"}, "size_mode": "small pointer; file size grows with notes"},
      "artifact_contract": {"file_format": "NDJSON, one full note record per line, sorted by id ascending, then one trailer line {\"type\":\"summary\",\"note_count\":integer}", "completion_record": "summary", "write": "streamed to <path>.tmp-<pid>, fsynced, then atomically renamed; <path> is never partially written"},
      "side_effects": {"external_mutation": false, "writes": ["local file at --output"]},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "progress": "with --no-progress unset and a TTY stderr, a human progress bar; in machine mode, none",
      "retry_defaults": {"retries": 2, "scope": "per page request", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "temp file removed; <path> untouched", "local_writes": "atomic rename", "remote_continues": false},
      "async": false, "streaming": false, "pagination": "internal; walks all pages", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2, "description": "export outran the cursor lifetime; re-run"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 1},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 10, "retryable": true}
      ]
    }
  ],
  "metadata_commands": {
    "notectl schema": "full contract (this document); local, no network, no auth",
    "notectl schema <command path>": "one command's entry, e.g. notectl schema note create",
    "notectl schema --fingerprint": "{schema_version, fingerprint, fingerprint_scope}",
    "notectl schema --summary": "one line per command: path, classification, description",
    "notectl whoami": "{user_id, account, token: {source, last4}, scopes}; network",
    "notectl config show --resolved": "every resolved setting with its source (flag|env|config|default); token redacted; local"
  },
  "metadata_latency_target_ms": 100
}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --tag "work" --limit 2 --machine`

```json
{"items":[{"id":"nt_8f2a","title":"Standup 2026-11-17","tags":["standup","work"],"updated_at":"2026-11-17T16:02:11Z"},{"id":"nt_7c19","title":"Quarterly plan","tags":["planning","work"],"updated_at":"2026-11-15T09:40:00Z"}],"has_more":true,"next_cursor":"cur_eyJvIjoyfQ","limit":2,"estimated_total":37}
```

`notectl note get --machine -- "nt_8f2a"`

```json
{"id":"nt_8f2a","title":"Standup 2026-11-17","body":"- shipped export\n- blocked on review","tags":["standup","work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:02:11Z"}
```

`notectl note search --query "quarterly plan" --limit 1 --machine`

```json
{"items":[{"id":"nt_7c19","title":"Quarterly plan","tags":["planning","work"],"updated_at":"2026-11-15T09:40:00Z","score":0.93}],"has_more":false,"limit":1}
```

`printf '%s' "$BODY" | notectl note create --title "Standup 2026-11-17" --body-stdin --tag "work" --idempotency-key "c0a8-01" --machine`

```json
{"id":"nt_8f2a","title":"Standup 2026-11-17","body":"- shipped export\n- blocked on review","tags":["work"],"created_at":"2026-11-17T16:02:11Z","updated_at":"2026-11-17T16:02:11Z","replayed":false}
```

`notectl note create --title "Draft" --body-file "./draft.md" --dry-run --machine`

```json
{"dry_run":true,"planned_action":"create","note":{"title":"Draft","body_bytes":412,"tags":[]}}
```

`notectl note delete --machine -- "nt_8f2a"` / with `--if-exists` on an already-deleted note

```json
{"id":"nt_8f2a","status":"deleted"}
```

```json
{"id":"nt_8f2a","status":"absent"}
```

`notectl note export --output "./notes-export.ndjson" --machine`

```json
{"path":"/home/agent/work/notes-export.ndjson","byte_size":48213,"content_hash":"sha256:9b1f0c3e5a7d2b4c6e8f0a1b3c5d7e9f1a2b3c4d5e6f708192a3b4c5d6e7f809","note_count":37,"format":"ndjson","consistency":"best-effort"}
```

`notectl schema --fingerprint --machine`

```json
{"schema_version":"1.0","fingerprint":"ntc-5e91c07a","fingerprint_scope":"schema-contract"}
```

## 5. Example error payloads (stderr only, stdout empty, `single-error-object` framing)

Not found — `notectl note get --machine -- "nt_404"`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"nt_404","temporary":false,"request_id":"req_01HZX3"}
```

Validation — `notectl note create --title "x" --body-file "./a.md" --tag "Work Items" --machine`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag.","field":"--tag","details":{"value":"Work Items","pattern":"^[a-z0-9][a-z0-9_-]{0,31}$"},"hint":"Use lowercase letters, digits, '-' or '_', max 32 chars; other flags were valid.","temporary":false}
```

Rate limited — `notectl note search --query "plan" --machine`, exit `6`:

```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_01HZX4"}
```

Unknown-outcome create — `notectl note create ... --idempotency-key "c0a8-01" --machine`, exit `7`:

```json
{"code":"TIMEOUT","message":"Request timed out after 10000 ms; the note may have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key":"c0a8-01"},"hint":"Re-run with the same --idempotency-key value.","request_id":"req_01HZX5"}
```

Unauthenticated — any networked command, exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No valid credentials.","details":{"sources_checked":["flag:none","env:NOTECTL_TOKEN","file:~/.config/notectl/credentials","keychain:notectl/default"]},"hint":"Set NOTECTL_TOKEN or write the credentials file; see notectl config show --resolved.","temporary":false}
```

Export target exists — `notectl note export --output "./notes-export.ndjson" --machine`, exit `8`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes-export.ndjson","hint":"Add --overwrite or choose another --output path.","temporary":false}
```

## 6. Checklist walk (design done criteria)

| Checklist section | Answer |
|---|---|
| Command Model | `notectl note <verb>`; ID is the single positional selector; conventional `--limit`, `--output`, `--timeout-ms`; no aliases. |
| Machine Schema | §3: tree, flags with types/defaults/enums/cardinality/repeat syntax, units, profiles, read-only flags, auth/scopes, output classes, shape dialect, exit + symbolic codes, per-command catalogs, side effects, latency, timeouts/retries, pagination/artifact, version policy + fingerprint; `schema <command>` and `--fingerprint` exposed. |
| Stdin Contract | Declared per command; only `note create --body-stdin` reads stdin, explicit flag, 1 MiB cap, empty accepted. |
| Shell Safety | `--` supported and declared; examples quote values, options before `--`; hints contain no shell strings built from input. |
| Agent-Safe Invocation | `--machine` profile; per-stream non-TTY suppression; `--isolated` distinct and still works with `NOTECTL_TOKEN`; env-var bootstrap; metadata paths local, <100ms target; caller-settable `--timeout-ms`. |
| Output | stdout success only; `single-error-object` stderr; one class per command (`list`, `record`, `artifact`); deterministic sorts; cursor contract; `--select` projection rule; UTC timestamps; `--output` only on export, returns path/size/hash. |
| Errors And Exit Codes | Exit map 0–10 declared; `temporary` always present; `INTERNAL` fallback; `NETWORK_ERROR` transport code; unknown codes non-retryable; token redacted. No multi-item mutation exists, so partial-failure rules are N/A (export fails whole or succeeds). |
| Ambient State | Credential/config/env/cache sources, precedence, `--isolated`/`--no-config`, `whoami`, `config show --resolved`, redaction; no secret flags. |
| Mutations And Long-Running Work | `create`/`delete` are explicit verbs with `--dry-run`; create uses caller-supplied idempotency key, delete uses `--if-exists`; reconciliation and signal semantics declared; cache writes atomic; export declares deadline, no machine-mode progress, interrupt cleanup. Async jobs N/A: nothing outlives the process. |
| Side Effects And Telemetry | Reads write nothing (cache holds metadata only, declared); export writes only `--output`; telemetry and update checks off. |
| Prose Surfaces | Descriptions lead with constraints (e.g., search index lag, create retry rule) and separate `list` vs `search`. |
| Tests | Ship: schema snapshot + fingerprint stability; each payload above as golden; declared-vs-observed exit codes; TTY vs non-TTY; machine-mode suppression; `--body-stdin` incl. empty stdin; pagination/cursor expiry; export atomicity + hash; config/env precedence and `--isolated`; dry-run for create/delete; interrupt during create/delete/export; concurrent cache writes. Deprecations: N/A in 1.0 (none exist), add when first alias ships. |
~~~~~~
