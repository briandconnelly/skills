# Scenario 1 (design) — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 1/2 conformance
- **Tokens:** 80,044 (final-turn context plus output, read from the transcript)
- **Output words:** 3,604
- **Transcript sha256:** `e7b1a942d2112e5aa3d5f1fa9e92f942884d72e880e5a6e371f300195a8a8795` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"]; {"name": "--machine", "type": "boolean" |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "exit_codes": {..."10": "local file write failed (domain-specific)"}, "symbolic_error_codes"; delete errors_possible with NOTE_NOT_FOUND exit 3 |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object"; "Example error payloads (stderr only, stdout empty)" |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | explicit `note delete <id>`; "--dry-run": {... "shape": {"dry_run": true, "planned_action": "delete\|none" |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": "boolean", "next_cursor?": "string" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "byte_size": "integer", "content_hash": "string" ... "content_hash is sha256:<hex> over the file bytes" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 15000} |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "caches": [], "disable_with": {"--isolated": "config files and credential file"...}, "inspect_with": ["notectl whoami", "notectl config show --resolved"] |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note get --machine -- 'nt_01HZX4' |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL", "unknown_code_policy": "non-retryable"; each note command lists {"code": "NETWORK_ERROR", "exit": 9} (whoami entry omitted, no list shown) Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unlisted-code handling = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | {"name": "--tag", ... "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | "`export` is the only command that accepts `--output`." |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **FAIL** | "The `schema`, `whoami`, and `config show --resolved` entries are omitted above for brevity" — no output class declared for them |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design). Task: new CLI design, following the agent-friendly-cli design workflow.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| list notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at` + paging |
| get a note | inspect | `id` | full note record |
| search notes | query | `--query` | ranked hits with `id`, `title`, `tags`, `snippet` + paging |
| create a note | mutate | `--title`, body (stdin or `--body-file`), optional `--tag` | created note record (`id`) |
| delete a note | mutate | `id` | `{id, status}` |
| export all notes | query (writes a local artifact) | `--output <file>` | `{path, byte_size, content_hash, note_count}` |
| discover contract | discover | none | schema / fingerprint |
| inspect ambient state | admin | none | identity, resolved config |

`list` vs `search`: `list` is deterministic enumeration with exact filters (`--tag`); `search` is relevance-ranked full-text over title and body. One sentence separates them, so both stay.

## 2. Command surface

Pattern: `notectl <noun> <verb>`, one primary selector per resource (note `id`, positional). All other inputs are named flags.

```
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--timeout-ms <ms>]
notectl note get     <id> [--select <field>]... [--timeout-ms <ms>]
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--timeout-ms <ms>]
notectl note create  --title <text> (--body-file <path> | --body-stdin) [--tag <tag>]... [--idempotency-key <key>] [--dry-run] [--timeout-ms <ms>]
notectl note delete  <id> [--if-exists] [--dry-run] [--timeout-ms <ms>]
notectl note export  --output <path> [--format ndjson|json] [--overwrite] [--timeout-ms <ms>]

notectl schema [<command path>] [--summary] [--fingerprint]
notectl whoami
notectl config show --resolved

Global: --machine (implies --json --no-progress --no-input), --json, --no-progress, --no-input,
        --isolated, --no-config, --profile <name>, --api-url <url>, --  (end of options)
```

Canonical machine invocations (operands after `--`, options before it):

```sh
notectl note get --machine -- 'nt_01HZX4'
notectl note search --machine --query 'quarterly plan' --tag 'work' --limit 20
printf '%s' "$BODY" | notectl note create --machine --title 'Standup notes' --tag 'work' --body-stdin --idempotency-key 'c7a1e0d2-standup-2026-11-17'
notectl note delete --machine --if-exists -- 'nt_01HZX4'
notectl note export --machine --output './notes-export.ndjson'
```

Design notes:

- Body is never a flag value (it can be large and contain shell metacharacters); it comes from `--body-stdin` (explicit, no auto-detection) or `--body-file`.
- `export` is the only command that accepts `--output`.
- `create` is not naturally replay-safe, so it supports `--idempotency-key`; `delete` is repeat-safe via `--if-exists`.
- Credentials come only from `NOTECTL_TOKEN` or the credential file; there is no `--token` flag.
- Non-interactive bootstrap: `notectl` has no interactive login; setting `NOTECTL_TOKEN` or writing `~/.config/notectl/credentials` (mode 0600) is the bootstrap.

## 3. Machine schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` — `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, `[T]` is an array of `T`, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes in a command catalog"],
    "breaking": ["command or flag removal or rename", "field removal or rename", "type or meaning change", "exit-code remapping", "output class change"],
    "rule": "any contract change changes the fingerprint; breaking changes also bump the major version"
  },
  "fingerprint": "ntc-7f3e91b2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_tool_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; [T] is an array of T; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "timestamps": "RFC 3339 UTC with Z suffix",
  "encoding": "UTF-8",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input"], "description": "Machine mode: JSON on stdout, structured errors on stderr, no prompts, color, pager, progress, or banners."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit success payloads as JSON."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; fail with VALIDATION_ERROR when input is missing."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the credential file; only NOTECTL_TOKEN and NOTECTL_API_URL are read. Required for authenticated calls: NOTECTL_TOKEN."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only; credentials are still read."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config/credential profile to use."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL; overrides NOTECTL_API_URL and config."}
  ],
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
    "9": "transient, not otherwise classified",
    "10": "local file write failed (domain-specific)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "NETWORK_ERROR", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "TRANSIENT", "WRITE_FAILED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "non-retryable",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "path?": "string", "docs_url?": "string"},
  "ambient_state": {
    "credentials": {"sources": ["NOTECTL_TOKEN", "~/.config/notectl/credentials [profile]"], "secret": true, "redaction": "never printed; whoami and config show report source and last 4 chars only"},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "XDG_CONFIG_HOME", "NO_COLOR"],
    "caches": [],
    "cwd_selects_context": false,
    "precedence": "flags > environment > config file > defaults",
    "disable_with": {"--isolated": "config files and credential file", "--no-config": "config files"},
    "inspect_with": ["notectl whoami", "notectl config show --resolved"]
  },
  "auth": "required for all note commands; not required for schema, config show",
  "network_timeouts": "every networked command takes --timeout-ms (total deadline)",
  "telemetry": "none; no update checks",
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> (--body-file <path> | --body-stdin)",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command path>] [--summary] [--fingerprint]",
    "whoami": "notectl whoami",
    "config": {"show": "notectl config show --resolved"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes in deterministic order (updated_at desc, then id asc), optionally filtered by exact tag. Read-only. Use note search for full-text relevance search.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": [], "examples": ["work"]},
        {"name": "--limit", "type": "integer", "min": 1, "max": 200, "default": 50},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], created_at?: string, updated_at: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "body is never included; use note get. next_cursor is present iff has_more is true.",
        "projection": {"flag": "--select", "rule": "only selected fields are present in each item; unselected fields are absent, not null; id is always present"},
        "size_mode": "bounded by --limit",
        "cursor": {"opaque": true, "lifetime_ms": 600000, "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential, honors retry_after_ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "closed_stdout": "exits quietly",
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
      "description": "Fetch one note by id, including body. Read-only. Fails with NOTE_NOT_FOUND (exit 3) if the id does not exist.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["nt_01HZX4"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "record", "format": "json",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "size_mode": "bounded: body max 1 MiB"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
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
      "description": "Full-text search over title and body, ranked by relevance (score desc, then id asc). Read-only. Index lags writes by up to ~5 s, so absence from results does not prove a note does not exist. Use note list for exact enumeration.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must carry all given tags", "default": []},
        {"name": "--limit", "type": "integer", "min": 1, "max": 100, "default": 20},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "snippet is at most 200 characters of matching body text; body is never included",
        "size_mode": "bounded by --limit",
        "cursor": {"opaque": true, "lifetime_ms": 600000, "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "consistency": "eventually consistent with writes (lag up to ~5 s)",
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "closed_stdout": "exits quietly",
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
      "canonical_invocation_path": "notectl note create --title <text> (--body-file <path> | --body-stdin)",
      "description": "Create a note. Mutating. Exactly one of --body-file or --body-stdin is required. Pass --idempotency-key on the first attempt to make a retry after TIMEOUT safe; without one, reconcile before retrying.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 300},
        {"name": "--body-file", "type": "path", "default": null, "mutually_exclusive_with": ["--body-stdin"], "description": "Read body from a UTF-8 file; '-' is not accepted, use --body-stdin."},
        {"name": "--body-stdin", "type": "boolean", "default": false, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "max_count": 32, "default": []},
        {"name": "--idempotency-key", "type": "string", "max_length": 128, "default": null, "description": "Server deduplicates creates with the same key for 24 h and returns the original note."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 15000}
      ],
      "stdin_contract": {"reads": "only with --body-stdin", "auto_detected_when_piped": false, "accepted_formats": ["UTF-8 text"], "maximum_input_size": "1 MiB", "can_block": "blocks until EOF on the pipe; with --body-stdin and stdin a TTY in machine mode, fails with VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body-file"], "empty_stdin": "accepted as an empty body"},
      "output": {
        "class": "record", "format": "json",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "replayed": "boolean"},
        "shape_description": "replayed is true when --idempotency-key matched an earlier create and the original note is returned",
        "size_mode": "small"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth against the API (read-only validate endpoint); no note is created; output includes dry_run: true"},
      "latency_class": "network", "timeout_defaults_ms": 15000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "On TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key used on the original attempt. A key added only on the retry does not deduplicate the original, and note search/list lag writes, so without an original key the create is not safe to retry automatically.",
      "safe_to_retry_automatically": "only when --idempotency-key was supplied on the original attempt",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "closed_stdout": "finishes the create, then exits",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
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
      "description": "Permanently delete one note by id. Mutating and irreversible. Fails with NOTE_NOT_FOUND unless --if-exists, which makes the command repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "pattern": "^nt_[0-9A-Z]{6,26}$", "cardinality": "one", "examples": ["nt_01HZX4"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "planned_action is none when --if-exists is set and the note does not exist", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence and permission; no deletion"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "On TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. Declared recovery: re-run with --if-exists (repeat-safe). note get reads the primary store; NOTE_NOT_FOUND from it shows the note is absent now, not which attempt removed it.",
      "safe_to_retry_automatically": "only with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "closed_stdout": "finishes the delete, then exits",
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
      "description": "Export every note (all fields) to a local file and print a pointer to it. Read-only remotely; writes one local file. Refuses to overwrite an existing file unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "examples": ["./notes-export.ndjson"]},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one note per line, sorted by id asc; json: a single array, same order"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "total deadline for the whole export"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "artifact", "format": "json",
        "shape": {"path": "string", "format": "ndjson|json", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "exported_at": "string"},
        "shape_description": "path is absolute, POSIX style; content_hash is sha256:<hex> over the file bytes; file records have the note get shape",
        "size_mode": "stdout small; file grows with note count",
        "consistency": "best-effort page walk: notes created or deleted during export may or may not appear"
      },
      "side_effects": {"external_mutation": false, "writes": ["file at --output"], "description": "writes to <path>.tmp-<pid> in the same directory and renames atomically on success; on failure the temp file is removed and no file appears at --output"},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "retry_defaults": {"retries": 2, "scope": "per page request", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "progress": "with --no-progress unset and stderr a TTY, a progress bar on stderr; suppressed in machine mode",
      "signal_semantics": {"interrupt": "temp file removed; --output untouched", "local_writes": "atomic rename", "remote_continues": false},
      "concurrency": "concurrent exports to the same --output: last successful rename wins; never a torn file",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "WRITE_FAILED", "exit": 10}
      ]
    }
  ]
}
```

The `schema`, `whoami`, and `config show --resolved` entries are omitted above for brevity; they follow the same per-command shape with `latency_class: local` for `schema` and `config show` and `network` for `whoami`.
`notectl schema note create` returns one command's entry; `notectl schema --summary` returns `{command, description, read_only}` per command.

Fingerprint endpoint (`notectl schema --fingerprint`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91b2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --machine --tag work --limit 2`

```json
{"items":[{"id":"nt_01HZX4","title":"Standup notes","tags":["work"],"updated_at":"2026-11-17T15:02:11Z"},{"id":"nt_01HZW9","title":"Quarterly plan","tags":["planning","work"],"updated_at":"2026-11-16T22:40:03Z"}],"has_more":true,"next_cursor":"c_eyJvIjoyfQ","limit":2,"estimated_total":14}
```

`notectl note get --machine -- nt_01HZX4`

```json
{"id":"nt_01HZX4","title":"Standup notes","body":"- shipped export\n- blocked on API quota","tags":["work"],"created_at":"2026-11-17T15:02:11Z","updated_at":"2026-11-17T15:02:11Z"}
```

`notectl note search --machine --query 'quarterly plan' --limit 1`

```json
{"items":[{"id":"nt_01HZW9","title":"Quarterly plan","tags":["planning","work"],"score":12.41,"snippet":"Q1 goals: ship export, cut p95 latency…"}],"has_more":false,"limit":1}
```

`... | notectl note create --machine --title 'Standup notes' --tag work --body-stdin --idempotency-key c7a1e0d2-standup-2026-11-17`

```json
{"id":"nt_01HZX4","title":"Standup notes","body":"- shipped export\n- blocked on API quota","tags":["work"],"created_at":"2026-11-17T15:02:11Z","updated_at":"2026-11-17T15:02:11Z","replayed":false}
```

`notectl note create --machine --title 'Draft' --body-file ./draft.md --dry-run`

```json
{"dry_run":true,"planned_action":"create","title":"Draft","tags":[],"body_bytes":842}
```

`notectl note delete --machine -- nt_01HZX4`

```json
{"id":"nt_01HZX4","status":"deleted"}
```

`notectl note delete --machine --if-exists -- nt_01HZX4` (already gone)

```json
{"id":"nt_01HZX4","status":"absent"}
```

`notectl note export --machine --output ./notes-export.ndjson`

```json
{"path":"/home/agent/work/notes-export.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:9f2c4e0b7a1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f","note_count":14,"exported_at":"2026-11-17T15:10:44Z"}
```

## 5. Example error payloads (stderr only, stdout empty)

Per `stderr_framing: single-error-object`, each object is the only stderr content in machine mode.

**Not found** — `notectl note get --machine -- nt_01HZZZ`, exit `3`:

```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"nt_01HZZZ","request_id":"req_8c1f2a","temporary":false}
```

**Validation** — `notectl note create --machine --title 'x' --tag 'Work Stuff' --body-stdin`, exit `2`:

```json
{"code":"VALIDATION_ERROR","message":"Invalid tag value.","field":"--tag","details":{"value":"Work Stuff","expected_pattern":"^[a-z0-9][a-z0-9_-]{0,63}$"},"hint":"Use lowercase letters, digits, '-' or '_' with no spaces, e.g. --tag work-stuff.","temporary":false}
```

**Rate limited** — `notectl note search --machine --query plan`, exit `6`:

```json
{"code":"RATE_LIMITED","message":"API rate limit exceeded.","retry_after_ms":30000,"request_id":"req_77a0b3","temporary":true}
```

**Timeout on a mutation (unknown outcome)** — `notectl note create --machine ... --idempotency-key c7a1e0d2-standup-2026-11-17`, exit `7`:

```json
{"code":"TIMEOUT","message":"Request timed out; the note may or may not have been created.","reconcile_first":true,"details":{"timeout_ms":15000,"idempotency_key":"c7a1e0d2-standup-2026-11-17"},"hint":"Re-run with the same --idempotency-key value.","temporary":false}
```

**Unauthenticated** — any note command with no token, exit `4`:

```json
{"code":"UNAUTHENTICATED","message":"No credentials found.","details":{"checked_sources":["flag --profile=default","env NOTECTL_TOKEN","~/.config/notectl/credentials"]},"hint":"Set NOTECTL_TOKEN or add a token for profile 'default' to the credentials file.","temporary":false}
```

**Export target exists** — `notectl note export --machine --output ./notes-export.ndjson`, exit `8`:

```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","field":"--output","path":"/home/agent/work/notes-export.ndjson","hint":"Pass --overwrite or choose a different --output path.","temporary":false}
```

## 6. Checklist walk

| Checklist section | Answer |
|---|---|
| Command Model | `notectl note <verb>`, shallow; `id` positional selector; conventional `--limit`, `--output`, `--timeout-ms`; no aliases. |
| Machine Schema | All items declared above, incl. shape dialect, version policy, fingerprint + scope, per-command catalogs, latency classes. |
| Stdin Contract | Declared per command; only `create --body-stdin` reads stdin, explicit not auto-detected, never waits on a TTY in machine mode. |
| Shell Safety | `--` supported and declared; examples quoted, options before `--`; body never in argv; hints carry flag values, not shell strings. |
| Agent-Safe Invocation | `--machine` profile distinct from `--isolated`; non-TTY per-stream suppression; env/file bootstrap, no interactive login; `--timeout-ms` on every networked command; `schema` paths are local-only. |
| Output | stdout payload only; `single-error-object` stderr; classes record/list/artifact; pagination + cursor contract; deterministic sort; UTC; `--select` projection; `--output` only on export with path/size/hash. |
| Errors And Exit Codes | Exit map 0–10, symbolic codes, `INTERNAL` fallback, `NETWORK_ERROR` transport code, unknown → non-retryable, `temporary` always present, `retry_after_ms` on rate limit. |
| Partial failure | N/A: no multi-item command (export fails whole and atomically rather than writing a partial file). |
| Ambient State | Sources, precedence, `--isolated`/`--no-config`, `whoami`, `config show --resolved`, token redaction, no secret flags; no caches. |
| Mutations And Long-Running Work | `create`/`delete` explicit, `--dry-run`, `--if-exists`, `--idempotency-key`, reconciliation and signal semantics declared; export atomic, foreground with declared deadline. Async jobs N/A: nothing outlives the process. |
| Side Effects And Telemetry | Reads have no writes (export writes only its declared file); no telemetry or update checks. |
| Prose Surfaces | Descriptions lead with constraints (read-only/mutating, required inputs, failure mode), then context; `list` vs `search` distinguishable from summaries. |
| Tests | Ship: schema snapshot + fingerprint stability; canonical payload snapshots; error payload + exit-code mapping (incl. runtime check of declared exits); TTY vs non-TTY; machine-mode suppression; `--body-stdin` with empty and TTY stdin; pagination + `CURSOR_EXPIRED`; export atomicity, interrupt, and concurrent same-path writes; env/config precedence and `--isolated`; dry-run output not byte-identical to real output and no remote mutation; idempotency replay; interrupt during create/delete. Deprecation and cancellation tests N/A until a deprecation or async job exists. |

Implementation note: build result-then-render (typed inputs, typed success/error payloads, separate human and machine renderers), and keep `--help` / `schema` imports free of the HTTP client so the metadata path stays under 100 ms.
~~~~~~
