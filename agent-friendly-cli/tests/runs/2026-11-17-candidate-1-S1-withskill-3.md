# Scenario 1 (design) — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 11/11 scored; 2/2 conformance
- **Tokens:** 81,940 (final-turn context plus output, read from the transcript)
- **Output words:** 4,216
- **Transcript sha256:** `51a875c4177f9298e6fb7051e6fdeced0962c69ba21d9fd451a9339eb7580f4e` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | "canonical_machine_profile": ["--machine"] ... {"name": "--machine", "type": "boolean" |
| A2 | scored | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | "error_code_exits": {"INTERNAL": 1, ...}; delete "errors_possible": [... {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"} |
| A3 | scored | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | "stderr_framing": "single-error-object"; "Example error payloads (stderr, empty stdout, machine mode)" |
| A4 | scored | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | explicit verb `notectl note delete <id>`; "--dry-run": {... "shape": {"dry_run": true, "planned_action": "delete\|none" |
| A5 | scored | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | "has_more": "boolean", "next_cursor?": "string" |
| A6 | scored | Export returns a structured pointer to the written file with its size and an integrity hash (Output). | **PASS** | "shape": {"path": "string", "byte_size": "integer", "content_hash": "string" |
| A7 | scored | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | {"name": "--timeout-ms", "type": "integer", "unit": "ms" |
| A8 | scored | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | "cache": {"reads": false, ...}, "config": {... "disable_with": ["--no-config", "--isolated"]}, "ambient_inspection": {"identity": "notectl whoami" |
| A9 | scored | Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row dated before 2026-11-17 except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored without it. | **PASS** | notectl note delete --machine --if-exists -- "note_7f3a" |
| A10 | scored | The contract says what an unanticipated failure emits (a declared symbolic code), each networked command's error list includes a non-timeout transport failure, and the contract says how a caller treats an error code it does not list (Errors And Exit Codes). Added 2026-11-17; scored per component, and it passes only if all three do. | **PASS** | "fallback_error_code": "INTERNAL", "unknown_code_policy": "non-retryable"; every networked command lists {"code": "NETWORK_ERROR", "exit": 9} Parts: unanticipated failure emits declared code = pass; each networked command lists non-timeout transport failure = pass; unlisted-code handling = pass |
| A11 | scored | Any flag that takes several values declares how they are passed (repeated flag or delimiter) (Machine Schema). Added 2026-11-17. | **PASS** | {"name": "--tag", ... "cardinality": "many", "multi_value_syntax": "repeat" |
| C1 | conformance | Export is the only `--output <file>` command. | **PASS** | only export has --output: "notectl note export --output <path>" |
| C2 | conformance | Each command declares one output class from the skill's set; any flag that switches the class declares the switch. | **PASS** | per-command "output": {"class": ...}; switch declared: "alternate_outputs": {"--dry-run": {"class": "record" |

## Verbatim final output

~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author (new design). Task: new CLI design, following the design workflow and the contract checklist.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| Discover the contract | discover | none | schema / fingerprint |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | page of `{id, title, tags, updated_at}` + cursor |
| Get a note | inspect | `id` | full note record |
| Search notes | query | `--query` text | page of matches `{id, title, tags, updated_at, score}` + cursor |
| Create a note | mutate | `--title`, body (flag, file, or stdin), optional `--tag` | created record incl. `id` |
| Delete a note | mutate | `id` | `{id, status}` |
| Export all notes | mutate (local file write) | `--output <file>` | `{path, byte_size, content_hash, note_count}` |
| Inspect identity / config | admin | none | resolved identity, config, credential source |

`list` and `search` are distinct by input: `list` enumerates/filters by exact tag; `search` ranks by free-text relevance. No other sibling pairs need prose to separate.

## 2. Command surface

Pattern: `notectl noun verb`, shallow tree. Primary selector for notes: ID (positional, the only positional argument anywhere). `--` end-of-options is supported.

```text
notectl note list    [--tag <tag>]... [--limit N] [--cursor C] [--sort updated_at|-updated_at|title] [--select f]... [--timeout-ms N]
notectl note get     <id> [--select f]... [--timeout-ms N]
notectl note search  --query <text> [--tag <tag>]... [--limit N] [--cursor C] [--timeout-ms N]
notectl note create  --title <text> (--body <text> | --body-file <path> | --body-stdin) [--tag <tag>]... [--idempotency-key K] [--dry-run] [--timeout-ms N]
notectl note delete  <id> [--if-exists] [--dry-run] [--timeout-ms N]
notectl note export  --output <path> [--format json|ndjson] [--overwrite] [--dry-run] [--timeout-ms N]

notectl schema [<command path>] [--fingerprint] [--summary]
notectl whoami
notectl config show --resolved
notectl auth status
```

Global flags: `--machine` (implies `--json --no-progress --no-input`), `--json`, `--no-progress`, `--no-input`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`.

Canonical examples (quoted, options before `--`):

```sh
notectl note get --machine -- "note_7f3a"
notectl note search --machine --query "quarterly plan" --limit 20
printf '%s' "$BODY" | notectl note create --machine --title "Standup 2026-11-17" --tag "meetings" --body-stdin --idempotency-key "c0a1e6b2-2f1b-4f0e-9d0a-5b7a6f3e9e11"
notectl note delete --machine --if-exists -- "note_7f3a"
notectl note export --machine --output "./notes-export.ndjson" --format ndjson
```

Help/summary text (rules-then-context):

- `note list` — List notes, newest-updated first; exact tag filter; paginated (default 50, max 200). Use `search` for free-text matching.
- `note get` — Get one note by ID, including body.
- `note search` — Rank notes by free-text relevance over title and body; paginated. Use `list` to enumerate or filter by tag only.
- `note create` — Create a note. Requires `--title` and exactly one body source. Not idempotent unless `--idempotency-key` is given.
- `note delete` — Permanently delete a note by ID. Fails with `NOTE_NOT_FOUND` unless `--if-exists`.
- `note export` — Write all notes to a local file; returns path, size, hash. Fails if the file exists unless `--overwrite`.

## 3. Machine schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` closed enum; trailing `?` optional field; fields required unless so marked or removed by a declared projection; `[T]` array of T; a string-valued shape describes an NDJSON record sequence.

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new error codes in a command catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping", "default changes"],
    "rule": "any contract change changes the fingerprint; breaking changes bump the major version"
  },
  "fingerprint": "ntc-5e9a71c0",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; [T] is an array of T; a string-valued shape describes an NDJSON record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "output_encoding": {"charset": "utf-8", "timestamps": "RFC 3339 UTC (Z)", "numbers": "locale-independent JSON numbers"},
  "telemetry": {"default": "off", "update_checks": "off", "machine_mode": "always suppressed"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input"], "description": "Machine mode: structured output only; never prompts, colors, pages, opens a browser, or prints banners on any stream."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON (or NDJSON where declared) on stdout."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress and spinners on stderr."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; a missing required value fails with VALIDATION_ERROR."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and caches; credentials only from NOTECTL_TOKEN; API URL only from --api-url or NOTECTL_API_URL."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config/credential profile to use. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "Remote API base URL. Overrides NOTECTL_API_URL and config."}
  ],
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> (--body <text>|--body-file <path>|--body-stdin)",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [<command path>] [--fingerprint] [--summary]",
    "whoami": "notectl whoami",
    "config": {"show": "notectl config show --resolved"},
    "auth": {"status": "notectl auth status"}
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
    "9": "transient (network/transport/5xx), not otherwise classified"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "OUTPUT_EXISTS", "IDEMPOTENCY_CONFLICT", "NETWORK_ERROR", "TRANSIENT", "LOCAL_IO_ERROR"],
  "error_code_exits": {"INTERNAL": 1, "VALIDATION_ERROR": 2, "CURSOR_EXPIRED": 2, "NOTE_NOT_FOUND": 3, "UNAUTHENTICATED": 4, "FORBIDDEN": 5, "RATE_LIMITED": 6, "TIMEOUT": 7, "OUTPUT_EXISTS": 8, "IDEMPOTENCY_CONFLICT": 8, "NETWORK_ERROR": 9, "TRANSIENT": 9, "LOCAL_IO_ERROR": 1},
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "non-retryable",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "debug": {"flag": "--debug", "description": "Opt-in request/response diagnostics on stderr; Authorization headers and tokens are redacted. Not allowed with --machine (VALIDATION_ERROR)."},
  "auth": "required for note commands; not required for schema, config show, auth status",
  "credential_sources": {
    "precedence": ["NOTECTL_TOKEN env var", "OS keychain entry 'notectl/<profile>'", "credentials file ~/.config/notectl/credentials.toml [<profile>]"],
    "flag_intake": "none; tokens are never accepted as flag or argument values",
    "non_interactive_bootstrap": "set NOTECTL_TOKEN, or pipe a token to `notectl auth login --token-stdin`",
    "redaction": "resolved token is shown as source + last 4 characters only"
  },
  "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG"],
  "config": {"reads": true, "paths": ["$NOTECTL_CONFIG", "~/.config/notectl/config.toml"], "disable_with": ["--no-config", "--isolated"]},
  "cache": {"reads": false, "writes": false, "description": "notectl keeps no cache."},
  "cwd_selects_context": false,
  "precedence": "flags > env vars > config file > built-in defaults",
  "ambient_inspection": {"identity": "notectl whoami", "resolved_config": "notectl config show --resolved", "credential_source": "notectl auth status"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "List notes, newest-updated first; exact tag filter; paginated. Use `note search` for free-text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "description": "Notes must carry all given tags.", "examples": ["meetings"]},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null, "description": "Opaque next_cursor from a previous page."},
        {"name": "--sort", "type": "enum", "enum": ["-updated_at", "updated_at", "title"], "default": "-updated_at", "description": "Ties broken by id ascending."},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "created_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], updated_at: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "next_cursor is present iff has_more is true; body is never included in list items",
        "projection": {"flag": "--select", "rule": "only selected fields are present in each item; unselected fields are absent, not null; id is always present"},
        "size_mode": "paged"
      },
      "pagination": {"cursor_opacity": "opaque", "cursor_lifetime": "15 minutes", "expired_cursor_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential from 500 ms, honoring retry_after_ms"},
      "closed_stdout": "exit quietly",
      "async": false, "streaming": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Get one note by ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect",
      "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]+$", "examples": ["note_7f3a"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "record", "format": "json",
        "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "size_mode": "small; body up to 1 MiB, never truncated"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential from 500 ms, honoring retry_after_ms"},
      "closed_stdout": "exit quietly",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Rank notes by free-text relevance over title and body; paginated. Use `note list` to enumerate or filter by tag only.",
      "aliases": [], "deprecations": [],
      "classification": "query",
      "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["quarterly plan"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], updated_at: string, score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "sorted by score descending, ties by id ascending; snippet is at most 200 characters of body around the best match",
        "size_mode": "paged"
      },
      "pagination": {"cursor_opacity": "opaque", "cursor_lifetime": "15 minutes", "expired_cursor_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort; index may lag writes by up to 30 s"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "exponential from 500 ms, honoring retry_after_ms"},
      "closed_stdout": "exit quietly",
      "async": false, "streaming": false, "truncation": {"field": "snippet", "max_chars": 200}, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-stdin",
      "summary": "Create a note. Requires --title and exactly one of --body, --body-file, --body-stdin. Not safe to retry unless --idempotency-key was given on the first attempt.",
      "aliases": [], "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "exclusive_group": "body_source"},
        {"name": "--body-file", "type": "path", "default": null, "exclusive_group": "body_source"},
        {"name": "--body-stdin", "type": "boolean", "default": false, "exclusive_group": "body_source"},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "max_count": 32},
        {"name": "--idempotency-key", "type": "string", "default": null, "description": "Caller-generated key (UUID recommended), retained server-side 24 h. Reuse the same key on retries of the same create."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "exclusive_groups": {"body_source": {"required": "exactly_one"}},
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": 1048576, "can_block": false, "can_block_description": "with --body-stdin, reads until EOF from a pipe or file; if stdin is a TTY in machine mode it fails with VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body", "--body-file"], "empty_stdin": "accepted as empty body"},
      "output": {
        "class": "record", "format": "json",
        "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "replayed": "boolean"},
        "shape_description": "body is omitted to save tokens; replayed is true when an earlier request with the same --idempotency-key already created this note",
        "size_mode": "small"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates locally and with the API's validate endpoint; no note is created; no local writes"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "description": "notectl never auto-retries create"},
      "reconciliation": "On TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt, the create may have committed. Safe retry: re-run with the same --idempotency-key supplied on the original attempt. Without a key the create is not safe to retry automatically; note search/list may lag and cannot prove the note was not created.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true},
      "closed_stdout": "finishes the mutation, then exits 0",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "description": "rejected before processing; safe to retry"},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "key reused with a different title/body/tags"},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "LOCAL_IO_ERROR", "exit": 1, "description": "--body-file unreadable"}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Permanently delete a note by ID. Fails with NOTE_NOT_FOUND unless --if-exists. Repeat-safe with --if-exists.",
      "aliases": [], "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]+$", "examples": ["note_7f3a"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "planned_action is none when the note is absent and --if-exists is set", "streaming": false, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence and permission; no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "On TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so the recovery is to re-run with --if-exists.",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true},
      "closed_stdout": "finishes the mutation, then exits 0",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write all notes to a local file and return its path, byte size, content hash, and note count. Fails if the file exists unless --overwrite. No remote mutation.",
      "aliases": [], "deprecations": [],
      "classification": "query",
      "read_only": true,
      "read_only_description": "no remote mutation; writes only the --output file",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "examples": ["./notes-export.ndjson"]},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "File format: ndjson writes one full note per line; json writes {\"notes\": [...]}."},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "Deadline for the whole export."}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "artifact", "format": "json",
        "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "ndjson|json"},
        "shape_description": "path is absolute, POSIX style; content_hash is sha256:<hex> of the written file",
        "size_mode": "small pointer; file grows with note count"
      },
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "export", "path": "string", "estimated_note_count?": "integer", "would_overwrite": "boolean"}, "streaming": false, "size_mode": "small"}
      },
      "progress": {"stderr": "suppressed in machine mode; human mode shows a progress bar on a TTY stderr only"},
      "side_effects": {"external_mutation": false, "writes": ["--output file"], "dry_run": "checks auth, path writability, and existence; writes nothing"},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "retry_defaults": {"retries": 2, "scope": "per page fetch", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "consistency": "best-effort page walk; notes changed during export may be missing or duplicated-by-id-never",
      "atomicity": "writes to <path>.tmp-<pid> in the same directory, fsyncs, then renames; the target file is either the complete export or untouched",
      "signal_semantics": {"interrupt": "temp file removed; target untouched", "local_writes": "atomic rename", "remote_continues": false},
      "concurrency": "concurrent exports to the same path: last rename wins; each result's content_hash describes its own write",
      "retry_safety": "safe to retry automatically (idempotent local overwrite with --overwrite)",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "LOCAL_IO_ERROR", "exit": 1}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [<command path>]",
      "summary": "Print the machine schema, one command's contract, a one-screen summary, or the fingerprint. No network, no auth.",
      "classification": "discover", "read_only": true,
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "the schema object, one command object, or {schema_version, fingerprint, fingerprint_scope}", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "performance_target_ms": 100,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl whoami",
      "summary": "Show the authenticated account and profile.",
      "classification": "admin", "read_only": true,
      "flags": [{"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "profile": "string", "api_url": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2},
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "NETWORK_ERROR", "exit": 9, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show resolved configuration with the source of each value. Secrets redacted. No network.",
      "classification": "admin", "read_only": true,
      "flags": [{"name": "--resolved", "type": "boolean", "default": true}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"profile": "{value: string, source: flag|env|config|default}", "api_url": "{value: string, source: flag|env|config|default}", "config_files_read": "[string]", "isolated": "boolean", "token": "{present: boolean, source?: env|keychain|credentials_file, redacted?: string}"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl auth status",
      "summary": "Show where the credential comes from and whether one is present, without contacting the API. Use `whoami` to validate it.",
      "classification": "admin", "read_only": true,
      "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"present": "boolean", "source?": "env|keychain|credentials_file", "redacted?": "string", "profile": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}]
    }
  ]
}
```

(`notectl auth login` is the interactive/bootstrap command; its non-interactive path is `--token-stdin`. Its entry is omitted here for brevity but follows the same per-command shape: mutate, writes keychain or credentials file atomically, last-writer-wins.)

### Fingerprint (`notectl schema --fingerprint --machine`)

```json
{"schema_version": "1.0", "fingerprint": "ntc-5e9a71c0", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --machine --tag meetings --limit 2`

```json
{
  "items": [
    {"id": "note_7f3a", "title": "Standup 2026-11-17", "tags": ["meetings"], "updated_at": "2026-11-17T16:02:11Z"},
    {"id": "note_7e91", "title": "Planning review", "tags": ["meetings", "q4"], "updated_at": "2026-11-16T21:40:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c_eyJvIjoyfQ",
  "limit": 2,
  "estimated_total": 14
}
```

`notectl note get --machine -- "note_7f3a"`

```json
{
  "id": "note_7f3a",
  "title": "Standup 2026-11-17",
  "body": "- shipped export\n- blocked on API rate limits",
  "tags": ["meetings"],
  "created_at": "2026-11-17T16:00:03Z",
  "updated_at": "2026-11-17T16:02:11Z"
}
```

`notectl note search --machine --query "rate limits" --limit 1`

```json
{
  "items": [
    {"id": "note_7f3a", "title": "Standup 2026-11-17", "tags": ["meetings"], "updated_at": "2026-11-17T16:02:11Z", "score": 0.87, "snippet": "...blocked on API rate limits"}
  ],
  "has_more": false,
  "limit": 1
}
```

`notectl note create --machine --title "Standup 2026-11-17" --tag "meetings" --body-stdin --idempotency-key "c0a1e6b2-..."`

```json
{"id": "note_7f3a", "title": "Standup 2026-11-17", "tags": ["meetings"], "created_at": "2026-11-17T16:00:03Z", "updated_at": "2026-11-17T16:00:03Z", "replayed": false}
```

`notectl note create --machine --title "Draft" --body "x" --dry-run`

```json
{"dry_run": true, "planned_action": "create", "title": "Draft", "tags": [], "body_bytes": 1}
```

`notectl note delete --machine -- "note_7f3a"`

```json
{"id": "note_7f3a", "status": "deleted"}
```

`notectl note delete --machine --if-exists -- "note_0000"`

```json
{"id": "note_0000", "status": "absent"}
```

`notectl note export --machine --output "./notes-export.ndjson"`

```json
{
  "path": "/home/agent/work/notes-export.ndjson",
  "byte_size": 48213,
  "content_hash": "sha256:9f2c4e0b7a1d3c5e8f6a2b4d0c9e7f1a3b5d7c9e0f2a4b6c8d0e1f3a5b7c9d0e",
  "note_count": 142,
  "format": "ndjson"
}
```

## 5. Example error payloads (stderr, empty stdout, machine mode)

Stderr framing is `single-error-object`: each object below is the only stderr content.

**Not found** — `notectl note get --machine -- "note_404"`, exit `3`:

```json
{"code": "NOTE_NOT_FOUND", "message": "Note not found.", "resource_id": "note_404", "temporary": false, "request_id": "req_01HZX3"}
```

**Validation** — `notectl note create --machine --title "x" --body "a" --body-stdin`, exit `2`:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Exactly one body source is allowed.",
  "field": "--body-stdin",
  "conflict_with": "--body",
  "details": {"exclusive_group": ["--body", "--body-file", "--body-stdin"], "required": "exactly_one"},
  "hint": "Remove either --body or --body-stdin.",
  "temporary": false
}
```

**Rate limited** — any networked command, exit `6`:

```json
{"code": "RATE_LIMITED", "message": "Rate limit exceeded.", "retry_after_ms": 30000, "temporary": true, "request_id": "req_01HZX4"}
```

**Unknown outcome on mutation** — `notectl note create ...` without an idempotency key, exit `7`:

```json
{
  "code": "TIMEOUT",
  "message": "Request timed out after 10000 ms; the note may have been created.",
  "temporary": false,
  "reconcile_first": true,
  "hint": "Retry only with the same --idempotency-key as the original attempt; this attempt had none, so do not retry automatically.",
  "details": {"timeout_ms": 10000, "idempotency_key_supplied": false}
}
```

**Unauthenticated** — exit `4`:

```json
{"code": "UNAUTHENTICATED", "message": "No credential found.", "temporary": false, "hint": "Set NOTECTL_TOKEN or pipe a token to `notectl auth login --token-stdin`.", "details": {"sources_checked": ["env", "keychain", "credentials_file"]}}
```

**Export target exists** — exit `8`:

```json
{"code": "OUTPUT_EXISTS", "message": "Output file already exists.", "field": "--output", "path": "/home/agent/work/notes-export.ndjson", "hint": "Add --overwrite or choose a different --output.", "temporary": false}
```

**Expired cursor** — exit `2`:

```json
{"code": "CURSOR_EXPIRED", "message": "Cursor expired.", "field": "--cursor", "hint": "Re-run without --cursor to restart the page walk.", "temporary": false}
```

## 6. Checklist walk

| Section | Answer |
|---|---|
| Command Model | `note <verb>`, one canonical op per task, ID positional selector, conventional flags (`--limit`, `--timeout-ms`, `--output`, `--format`). |
| Machine Schema | All items declared above; `schema <command>` and `--fingerprint` endpoints; version policy declared. |
| Stdin Contract | Declared per command; only `create --body-stdin` reads stdin, explicit flag, never waits on a TTY. |
| Shell Safety | `--` supported and declared; examples quoted with options before `--`; hints express repairs as flag values; values never reach a subshell. |
| Agent-Safe Invocation | `--machine` profile distinct from `--isolated`; per-stream non-TTY suppression; non-interactive bootstrap via env or `--token-stdin`; metadata paths local and <100 ms; `--timeout-ms` everywhere networked. |
| Output | stdout payload only; `single-error-object` stderr; output class per command; pagination with cursor contract; deterministic sort; `--select` projection; export returns path/size/hash; closed-stdout behavior declared. |
| Errors And Exit Codes | Exit map 0–9; per-command catalogs with `retryable`/`reconcile_first`/`suppressed_by`; `INTERNAL` fallback; `NETWORK_ERROR` transport code; unknown-code policy non-retryable; `--debug` opt-in, redacted. |
| Partial failure | Not applicable: no multi-item commands (export is all-or-nothing via atomic rename). |
| Ambient State | Credentials, config, env, precedence, `--isolated`/`--no-config`, `whoami`, `config show --resolved`, `auth status`; no cache; cwd does not select context; no token flags. |
| Mutations | `create`/`delete` explicit verbs, `--dry-run` on all mutating/writing commands, `--if-exists`, `--idempotency-key`, reconciliation and signal semantics declared, export atomic. Async jobs: not applicable — nothing outlives the process; export declares deadline and interrupt behavior. |
| Side Effects And Telemetry | Reads never write; no telemetry or update checks. |
| Prose Surfaces | Summaries rules-first and sibling-selective (`list` vs `search`). |
| Tests | Ship: schema snapshot + fingerprint stability; canonical payload snapshots; each catalog code produces its declared exit; TTY vs non-TTY and `--machine` suppression; `--body-stdin` incl. empty and TTY stdin; pagination and `CURSOR_EXPIRED`; export artifact hash and atomicity under interrupt and concurrent runs; env/config precedence and `--isolated`; dry-run outputs differ from real ones and make no remote call that mutates; interrupt during create/delete. Deprecation tests: not applicable until an alias exists. |
~~~~~~
