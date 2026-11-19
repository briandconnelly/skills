# Scenario S1 — with-skill arm 2 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 3417
- **Scoring:** blinded packet, output id `o73`; the scorer received the assertion block verbatim and no arm labels

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S1-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Canonical machine profile, every implied flag declared
- o73 PASS: `--machine` implies `--json --no-progress --no-color --non-interactive`, and all four are declared in `global_flags`.
### A2 Numeric exit codes, symbolic codes, and a per-command catalog for the mutating command
- o73 PASS: `exit_codes` 0–9, `symbolic_error_codes`, and `errors_possible` on create, delete, and export.
### A3 stdout carries the success payload only; failures go to stderr with declared framing
- o73 PASS: `"stderr_framing": "single-error-object"`; heading reads "stderr only; stdout empty".
### A4 delete has an explicit trigger and `--dry-run` whose output includes `dry_run: true`
- o73 PASS: explicit `delete` verb; the alternate shape is `"dry_run": "true"`, an equivalent spelling of the literal `true`.
### A5 List/search pagination declares `has_more` and a token
- o73 PASS: list and search both declare `has_more` and `next_cursor?`.
### A6 Export returns a pointer with path, size, and hash
- o73 PASS: `path`, `byte_size`, `content_hash`.
### A7 Duration flags declare units
- o73 PASS: every duration flag is `--timeout-ms` with `"unit": "ms"`.
### A8 Ambient state is declared with inspection and isolation affordances
- o73 PASS: `ambient_state` covers credentials, config, and `caches: []`; it has `inspect_with` and `disable_with`.
### A9 Canonical examples that use `--` put options before it and operands after
- o73 PASS: the only example that uses `--` is `notectl note get --machine -- 'n_-weird'`.
  Note: the usage synopsis `note get [--] <id> [--select <field>]...` lists options after `--`, but it is a synopsis, not a canonical example.
### A10 Fallback code / non-timeout transport code on each networked command / unknown-code policy
- o73 PASS.
  - Fallback: pass, `INTERNAL`.
  - Transport code: pass. `TRANSIENT` is defined at exit 9 as "transient, incl. transport failures other than timeout", which counts as an equivalent name. It appears in list, get, search, create, delete, export, and auth status.
  - Unknown-code policy: pass, `unknown_code_policy` is present.
### A11 Multi-value flags declare how values are passed
- o73 PASS: `--tag` and `--select` declare `"multi_value_syntax": "repeat"` on every command that has them.
### C1 Export is the only `--output <file>` command
- o3 PASS, o73 PASS, o1 PASS: `--output` appears only on `note export`.
### C2 Each command declares one output class, and any flag that switches the class declares the switch
- o73 PASS: every command declares a class; export's `--dry-run` switches artifact to record and is declared in `alternate_outputs`.

## Verbatim final output

~~~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author designing a new CLI.
Task: new design, so this follows the design workflow: task model, command surface, schema, defaults, output and errors, tests.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| Discover the contract | discover | none | schema / fingerprint |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags` per note + paging |
| Get a note | inspect | note `id` | full note |
| Search notes | query | `--query` text | `id`, `title`, `tags`, `snippet` + paging |
| Create a note | mutate | `--title`, body (flag, file, or stdin), optional `--tag` | created note incl. `id` |
| Delete a note | mutate | note `id` | `id`, `status` |
| Export all notes | mutate (local file) | `--output <file>` | `path`, `byte_size`, `content_hash`, `note_count` |
| Check identity / resolved config | admin | none | account, API URL, credential source |

`list` vs `search`: `list` enumerates with exact filters (tag) in deterministic order; `search` ranks by full-text relevance over title and body.
That difference fits in one summary line each, so both stay.

## 2. Command surface

Pattern: `notectl <noun> <verb>`; primary selector for a note is its `id` (positional, the one obvious selector).

```
notectl schema [<command>] [--fingerprint] [--summary]
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--sort created_at|updated_at|title] [--timeout-ms <ms>]
notectl note get    [--] <id> [--select <field>]... [--timeout-ms <ms>]
notectl note search --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--timeout-ms <ms>]
notectl note create --title <text> (--body <text> | --body-file <path> | --body-stdin) [--tag <tag>]... [--idempotency-key <key>] [--dry-run] [--timeout-ms <ms>]
notectl note delete [--] <id> [--if-exists] [--dry-run] [--timeout-ms <ms>]
notectl note export --output <path> [--format ndjson|json] [--overwrite] [--timeout-ms <ms>]
notectl auth status [--timeout-ms <ms>]          # identity: who the token belongs to
notectl config show --resolved                   # resolved config + sources, secrets redacted
```

Global flags: `--machine` (implies `--json --no-progress --no-color --non-interactive`), `--isolated`, `--no-config`, `--api-url <url>`, `--profile <name>`.
`--` ends options on every command; canonical examples quote values: `notectl note get --machine -- 'n_-weird'`.

Non-interactive bootstrap: there is no interactive login; credentials come from `NOTECTL_TOKEN`, a credential file, or `notectl auth login --token-stdin` (reads the token from stdin, writes the credential file atomically).
No `--token` flag exists, so secrets never appear in argv.

## 3. Machine-readable schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, trailing `?` marks an optional field, fields are required unless so marked or removed by a declared `--select` projection, a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "compatibility": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new error codes in a catalog"],
    "breaking": ["removed or renamed commands, flags, or fields", "type or meaning changes", "exit-code remapping"],
    "rule": "every contract change changes the fingerprint; breaking changes bump the major version"
  },
  "fingerprint": "ntc-7f3e91a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks optional; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode on failure, the structured error object is the only stderr content; no progress is emitted in machine mode",
  "encoding": {"charset": "UTF-8", "timestamps": "RFC 3339 UTC", "numbers": "locale-independent"},
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--non-interactive"], "description": "Machine mode: structured output only, never prompts, no color, pager, or progress, regardless of TTY."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit JSON (or NDJSON where declared) on stdout and JSON errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--non-interactive", "type": "boolean", "default": false, "description": "Never prompt; fail with VALIDATION_ERROR when input is missing."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the cache. Credentials still come from NOTECTL_TOKEN only, so authenticated calls work when it is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL; overrides NOTECTL_API_URL and config."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to read; overrides NOTECTL_PROFILE."}
  ],
  "ambient_state": {
    "credentials": ["NOTECTL_TOKEN env var", "~/.config/notectl/credentials.json (mode 0600)"],
    "config_files": ["~/.config/notectl/config.toml"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE"],
    "caches": [],
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file > credential file",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl auth status", "notectl config show --resolved"],
    "secrets": {"values": ["token"], "redaction": "shown as source plus last 4 chars, e.g. \"****a9f2\""}
  },
  "telemetry": {"enabled_by_default": false, "update_checks": false},
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, incl. transport failures other than timeout"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "OUTPUT_EXISTS", "TRANSIENT"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, reconcile_first); on mutating commands reconcile before retrying",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "path?": "string"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "string[]", "created_at": "string", "updated_at": "string"},
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> --body <text>",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"}
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl schema",
      "description": "Print this contract. No network or auth. --fingerprint prints only version and fingerprint; <command> prints one command's entry.",
      "classification": "discover", "read_only": true, "aliases": [], "deprecations": [],
      "arguments": [{"name": "command", "type": "string", "cardinality": "zero-or-one", "examples": ["note get"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "target_ms": 100, "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl note list",
      "description": "List notes, optionally filtered by exact tag, in deterministic order. Use note search for text relevance.",
      "classification": "query", "read_only": true, "aliases": [], "deprecations": [],
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "notes must have all given tags", "default": []},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["created_at", "updated_at", "title"], "default": "created_at", "description": "ascending; ties broken by id"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "size_mode": "paged",
        "shape": {"items": "note[] (projected)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "backoff": "exponential, honors retry_after_ms"},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "closed_stdout": "exit quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "description": "Fetch one note by id, including body.",
      "classification": "inspect", "read_only": true, "aliases": [], "deprecations": [],
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["n_8f2k1"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "note (projected)", "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"}, "size_mode": "small; body up to 1 MiB"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "description": "Full-text search over title and body, ranked by relevance (ties by id). Use note list for exact tag filtering without a query.",
      "classification": "query", "read_only": true, "aliases": [], "deprecations": [],
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "max_length": 512},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": []},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "snippet", "score", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "snippet", "score"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "size_mode": "paged",
        "shape": {"items": "{id, title, tags, snippet, score, updated_at?}[] (projected)", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "snippet is at most 200 characters; score is a float in [0,1]",
        "projection": {"flag": "--select", "rule": "only selected fields are present; id is always present"},
        "cursor": {"opaque": true, "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"]},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body <text>",
      "description": "Create one note. Requires --title and exactly one body source. Pass --idempotency-key to make retries safe.",
      "classification": "mutate", "read_only": false, "aliases": [], "deprecations": [],
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "max_length": 300},
        {"name": "--body", "type": "string", "default": null},
        {"name": "--body-file", "type": "path", "default": null},
        {"name": "--body-stdin", "type": "boolean", "default": false},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "default": [], "pattern": "^[a-z0-9-]{1,40}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "description": "server deduplicates for 24 hours"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "mutually_exclusive": [["--body", "--body-file", "--body-stdin"]],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-stdin", "accepted_formats": ["UTF-8 text"], "maximum_input_size": "1 MiB", "can_block": "only until EOF of a pipe; with --body-stdin and a TTY stdin in machine mode, fails VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body", "--body-file"], "empty_stdin": "accepted as an empty body"},
      "output": {"class": "record", "format": "json", "shape": "note", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "note": "{title, body_bytes, tags}"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "validates inputs and auth with the API's validate-only endpoint; no note is created"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0, "description": "with --idempotency-key, retries 2 times on RATE_LIMITED, TIMEOUT, TRANSIENT reusing the same key"},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown. Safe retry: re-run with the same --idempotency-key within 24 hours. Without a key the create is not safe to retry automatically; a note search returning nothing does not prove the create did not commit.",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the create"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "CONFLICT", "exit": 8, "description": "idempotency key reused with different inputs"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ],
      "error_notes": "TIMEOUT and TRANSIENT become retryable (temporary: true, reconcile_first: false) when --idempotency-key was given"
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Permanently delete one note by id. --if-exists makes a missing note succeed with status absent.",
      "classification": "mutate", "read_only": false, "aliases": [], "deprecations": [],
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["n_8f2k1"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "absent only with --if-exists", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "id": "string", "planned_action": "delete|none"}, "shape_description": "none when --if-exists would suppress NOTE_NOT_FOUND", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "reads the note to confirm existence and permission; no deletion"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so re-run with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the delete"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "description": "Write every note to a local file and print its path, size, and hash. Fails if the file exists unless --overwrite.",
      "classification": "mutate", "read_only": false, "aliases": [], "deprecations": [],
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "file format; ndjson writes one note per line"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "whole-export deadline"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "format": "ndjson|json", "note_count": "integer", "exported_at": "string"}, "shape_description": "path is absolute; content_hash is sha256:<hex>", "size_mode": "small pointer; file size unbounded"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "write|overwrite", "path": "string", "estimated_note_count?": "integer"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": false, "writes": ["local file at --output"], "atomicity": "writes <path>.tmp-<pid> then renames; concurrent exports to the same path are last-writer-wins", "dry_run": "checks path writability and auth; writes nothing"},
      "latency_class": "slow", "timeout_defaults_ms": 300000, "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT"], "scope": "per page fetch"},
      "consistency": "best-effort: notes changed during export may or may not be included",
      "progress": "human mode only on stderr; none in machine mode",
      "signal_semantics": {"interrupt": "temp file removed; target unchanged", "local_writes": "atomic rename", "remote_continues": false, "closed_stdout": "finishes the export"},
      "reconciliation": "safe to retry: no remote mutation, and the target is replaced atomically (use --overwrite)",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 8, "suppressed_by": "--overwrite"},
        {"code": "TRANSIENT", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth status",
      "description": "Show the account the resolved token belongs to and where the token came from. Token is redacted.",
      "classification": "admin", "read_only": true,
      "output": {"class": "record", "format": "json", "shape": {"account_id": "string", "email": "string", "api_url": "string", "credential_source": "env:NOTECTL_TOKEN|file:<path>", "token": "string (redacted)", "scopes": "string[]"}},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSIENT", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "description": "Show each resolved setting with its source (flag, env, config, default). Local only; secrets redacted.",
      "classification": "admin", "read_only": true,
      "output": {"class": "record", "format": "json", "shape": {"settings": "{name, value, source: flag|env|config|default}[]", "isolated": "boolean"}},
      "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

`auth login --token-stdin` follows the same per-command shape (stdin required, explicit flag, max 4 KiB, atomic credential-file write); its entry is omitted here for length.

Fingerprint endpoint, `notectl schema --fingerprint --machine`:

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3e91a2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, exit 0)

`notectl note list --tag work --limit 2 --machine`
```json
{"items":[{"id":"n_8f2k1","title":"Q3 planning","tags":["work","planning"],"updated_at":"2026-11-02T17:04:11Z"},{"id":"n_8f2k7","title":"1:1 notes","tags":["work"],"updated_at":"2026-11-05T09:12:40Z"}],"has_more":true,"next_cursor":"c_eyJvIjoyfQ","limit":2,"estimated_total":14}
```

`notectl note get n_8f2k1 --machine`
```json
{"id":"n_8f2k1","title":"Q3 planning","body":"Goals:\n- ship export","tags":["work","planning"],"created_at":"2026-10-30T12:00:00Z","updated_at":"2026-11-02T17:04:11Z"}
```

`notectl note search --query 'export' --machine`
```json
{"items":[{"id":"n_8f2k1","title":"Q3 planning","tags":["work","planning"],"snippet":"Goals:\n- ship export","score":0.91}],"has_more":false,"limit":20,"estimated_total":1}
```

`printf 'Remember the milk' | notectl note create --title 'Groceries' --body-stdin --tag home --idempotency-key 3c1e-77 --machine`
```json
{"id":"n_9a0c3","title":"Groceries","body":"Remember the milk","tags":["home"],"created_at":"2026-11-18T10:21:05Z","updated_at":"2026-11-18T10:21:05Z"}
```

`notectl note create --title 'Groceries' --body 'Remember the milk' --dry-run --machine`
```json
{"dry_run":true,"planned_action":"create","note":{"title":"Groceries","body_bytes":17,"tags":[]}}
```

`notectl note delete n_9a0c3 --machine`
```json
{"id":"n_9a0c3","status":"deleted"}
```

`notectl note delete n_9a0c3 --if-exists --machine` (already gone)
```json
{"id":"n_9a0c3","status":"absent"}
```

`notectl note export --output ./notes.ndjson --machine`
```json
{"path":"/home/agent/work/notes.ndjson","byte_size":48213,"content_hash":"sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08","format":"ndjson","note_count":137,"exported_at":"2026-11-18T10:22:40Z"}
```

## 5. Example error payloads (stderr only; stdout empty)

Not found, exit `3`: `notectl note get n_404 --machine`
```json
{"code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"n_404","hint":"Find the id with notectl note search or notectl note list.","temporary":false,"request_id":"req_51c2"}
```

Validation, exit `2`: `notectl note create --title 'x' --body 'a' --body-file b.txt --machine`
```json
{"code":"VALIDATION_ERROR","message":"Only one body source may be given.","field":"--body-file","details":{"mutually_exclusive":["--body","--body-file","--body-stdin"]},"hint":"Keep --body and drop --body-file, or the reverse.","temporary":false}
```

Rate limited, exit `6`: `notectl note list --machine`
```json
{"code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_51c9"}
```

Unknown outcome on a mutation, exit `7`: `notectl note delete n_8f2k1 --timeout-ms 2000 --machine`
```json
{"code":"TIMEOUT","message":"Delete request timed out; outcome unknown.","resource_id":"n_8f2k1","reconcile_first":true,"hint":"Re-run with --if-exists.","details":{"timeout_ms":2000},"temporary":false}
```

Export target exists, exit `8`: `notectl note export --output ./notes.ndjson --machine`
```json
{"code":"OUTPUT_EXISTS","message":"Output file already exists.","path":"/home/agent/work/notes.ndjson","field":"--output","hint":"Add --overwrite or choose another --output path.","temporary":false}
```

## 6. Agent-safe defaults and behavior

- Machine mode (`--machine`) and non-TTY mode never prompt, color, page, spin, or open a browser; non-TTY is judged per stream (stdout: rendering/pager, stderr: color/progress, stdin: prompts).
- Machine mode never hides deprecations or partial results: they appear as fields in the structured output.
- `schema`, `schema --fingerprint`, and `--help` make no network or auth calls and target under 100 ms (lazy imports of the HTTP client).
- No telemetry or update checks; reads never write; the only local writes are `export --output` and `auth login`.
- Help text and `description` fields lead with constraints and defaults, then context.

## 7. Contract tests to ship

Schema snapshot and fingerprint stability; canonical success payloads above; each error payload above with its exit code verified against the catalog; TTY vs non-TTY and `--machine` suppression of prompts/color/progress; `--body-stdin` with empty stdin and with a TTY stdin; pagination and `CURSOR_EXPIRED`; `--select` projection; export artifact fields, atomic write, `OUTPUT_EXISTS`, and interrupt leaving no partial file; env/flag/config precedence and `--isolated`; dry-run output for create, delete, and export; idempotency-key replay for create; concurrent `auth login` writes.
Not applicable: deprecation tests (none declared in 1.0) and async cancellation (no async commands; export is a bounded foreground command with a declared deadline).

## 8. Checklist coverage

| Section | Where answered |
|---|---|
| Command Model | §2, `command_tree` |
| Machine Schema | §3 top-level keys, `schema <command>`, `--fingerprint`, `compatibility` |
| Stdin Contract | `stdin_contract` on every command; `create --body-stdin` |
| Shell Safety | `end_of_options_supported`, quoted examples, hints carry no shell built from caller input |
| Agent-Safe Invocation | `--machine`, `--isolated`, §6, `--timeout-ms` on every networked command, token-stdin bootstrap |
| Output | `stderr_framing`, per-command `output`, cursors, projection, artifact pointer, deterministic sort |
| Errors And Exit Codes | `exit_codes`, `error_shape`, per-command `errors_possible`, `fallback_error_code`, `unknown_code_policy`, TRANSIENT for transport. Partial failure: N/A, no multi-item mutating command |
| Ambient State | `ambient_state`, `auth status`, `config show --resolved`, no secrets in argv |
| Mutations And Long-Running Work | dry-run on create/delete/export, `--if-exists`, `--idempotency-key`, `reconciliation`, `signal_semantics`; async N/A (no job outlives the process) |
| Side Effects And Telemetry | `side_effects`, `telemetry` |
| Prose Surfaces | `description` fields written rules-first and sibling-selective (list vs search) |
| Tests | §7 |
~~~~~~~~
