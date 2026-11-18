# Scenario S1 — with-skill arm 3 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 3939
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S1-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Canonical machine profile, every implied flag declared
- o1 PASS: `--machine` implies `--json --no-progress --no-input --no-color`, and all four are declared.
### A2 Numeric exit codes, symbolic codes, and a per-command catalog for the mutating command
- o1 PASS: `exit_codes` 0–10, `symbolic_error_codes`, and `errors_possible` on create and delete.
### A3 stdout carries the success payload only; failures go to stderr with declared framing
- o1 PASS: `"stderr_framing": "single-error-object"`; heading reads "stderr, `--machine`, stdout empty".
### A4 delete has an explicit trigger and `--dry-run` whose output includes `dry_run: true`
- o1 PASS: explicit `delete` verb; the alternate shape is `"dry_run": "true"`, and the create dry-run example prints `"dry_run": true`.
### A5 List/search pagination declares `has_more` and a token
- o1 PASS: list and search both declare `has_more` and `next_cursor?`.
### A6 Export returns a pointer with path, size, and hash
- o1 PASS: `path`, `byte_size`, `content_hash`.
### A7 Duration flags declare units
- o1 PASS: every duration flag, including the global `--timeout-ms`, carries `"unit": "ms"`.
### A8 Ambient state is declared with inspection and isolation affordances
- o1 PASS: `ambient_state` covers credentials, config, and caches; it has `inspect_with` and `disable_with`.
### A9 Canonical examples that use `--` put options before it and operands after
- o1 PASS: all three examples that use `--` are options-first: `note get --machine -- 'nt_...'`, `note delete --machine -- nt_...`, and `note delete --machine --if-exists -- nt_...`.
### A10 Fallback code / non-timeout transport code on each networked command / unknown-code policy
- o1 PASS.
  - Fallback: pass, `INTERNAL`.
  - Transport code: pass. `TRANSPORT_ERROR` appears in list, get, search, create, delete, export, and auth whoami.
  - Unknown-code policy: pass, `unknown_code_policy` is present.
### A11 Multi-value flags declare how values are passed
- o1 PASS: `--tag` and `--select` declare `"multi_value_syntax": "repeat"` on every command that has them.
### C1 Export is the only `--output <file>` command
- o3 PASS, o73 PASS, o1 PASS: `--output` appears only on `note export`.
### C2 Each command declares one output class, and any flag that switches the class declares the switch
- o1 PASS: every command declares a class, and `--dry-run` alternates are declared.

## Verbatim final output

~~~~~~~~markdown
# `notectl` agent-facing CLI contract

Audience: tool author designing a new CLI. Task: new design (design workflow).

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for next step |
|---|---|---|---|
| Discover contract | discover | none | schema / fingerprint |
| List notes | query | optional `--tag`, `--limit`, `--cursor` | `id`, `title`, `tags`, `updated_at` per note + paging |
| Get a note | inspect | note `id` | full note |
| Search notes | query | `--query` text | matching notes (summary fields) + paging |
| Create a note | mutate | `--title`, body (flag, file, or stdin), optional `--tag` | created note incl. `id` |
| Delete a note | mutate | note `id` | `id` + `status` |
| Export all notes | query (writes local artifact) | `--output <file>` | path, byte size, content hash, count |
| Inspect ambient state | admin | none | identity, resolved config, credential source |

No wrappers around shell pipelines; `search` is kept separate from `list` because it takes free text and returns relevance-ranked results, while `list` is a deterministic, filterable enumeration (one-line summaries distinguish them).

## 2. Command surface

Pattern: `notectl <noun> <verb>`. Primary selector for notes: ID (positional). All other inputs are named flags. `--` end-of-options is supported.

```
notectl schema [<command>] [--fingerprint] [--summary]
notectl note list   [--tag <tag>]... [--limit <n>] [--cursor <c>] [--sort updated_at|-updated_at|title] [--select <field>]...
notectl note get    <id> [--select <field>]...
notectl note search --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]...
notectl note create --title <text> (--body <text> | --body-file <path> | --body-file -) [--tag <tag>]... [--idempotency-key <key>] [--dry-run]
notectl note delete <id> [--if-exists] [--dry-run]
notectl note export --output <path> [--format json|ndjson] [--overwrite]
notectl auth whoami
notectl config show --resolved
```

Global flags: `--machine` (implies `--json --no-progress --no-input --no-color`), `--json`, `--no-progress`, `--no-input`, `--no-color`, `--isolated`, `--no-config`, `--profile <name>`, `--api-url <url>`, `--timeout-ms <n>`.

Command summaries (rules first):

- `note list` — Enumerate notes, newest-updated first; filter by exact tag. Use when you need everything matching a filter, not free-text matching.
- `note get` — Return one note by ID, including body. Fails with `NOTE_NOT_FOUND` (exit 3) if absent.
- `note search` — Free-text search over title and body, relevance-ranked; returns summaries without body. Use `note get` for the body.
- `note create` — Create one note; returns the new note's ID. Not idempotent unless `--idempotency-key` is given.
- `note delete` — Delete one note by ID; `--if-exists` makes it repeat-safe.
- `note export` — Write all notes to a local file; stdout reports path, size, hash. Only command that accepts `--output`.

Canonical examples (quoted):

```sh
notectl note create --machine --title 'Q3 plan' --tag work --body-file - < body.md
notectl note get --machine -- 'nt_01HZ...'
notectl note search --machine --query 'deploy rollback' --limit 20
```

## 3. Machine schema (`notectl schema --machine`)

Shape dialect: `notectl-compact-v1` (`a|b` closed enum; trailing `?` optional; fields required unless so marked or removed by a declared projection; string-valued shape describes a record sequence).

```json
{
  "schema_version": "1.0",
  "schema_version_policy": {
    "additive": ["new commands", "new optional flags", "new optional output fields", "new symbolic error codes on a command (callers apply unknown_code_policy)"],
    "breaking": ["command or flag removal or rename", "type or meaning change", "required-field removal", "exit-code remapping", "default change"],
    "rule": "every contract change changes the fingerprint; breaking changes bump the major version"
  },
  "fingerprint": "ntc-7f3a91c2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_includes_version": false,
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content; on success stderr is empty",
  "encoding": "utf-8",
  "timestamps": "RFC 3339, UTC (Z suffix)",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-input", "--no-color"], "description": "Non-interactive machine mode on every stream regardless of TTY: no prompts, color, pager, spinners, or browser launch; structured output only."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Emit structured JSON on stdout and structured errors on stderr."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress progress output."},
    {"name": "--no-input", "type": "boolean", "default": false, "description": "Never prompt; fail with VALIDATION_ERROR when input is missing."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the token cache; credentials come only from NOTECTL_TOKEN and endpoint from --api-url or NOTECTL_API_URL. Authenticated reads still work if NOTECTL_TOKEN is set."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve; ignored under --isolated / --no-config."},
    {"name": "--api-url", "type": "string", "default": "https://api.notes.example.com", "description": "Remote API base URL."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "description": "Per-request network timeout; default is per command."}
  ],
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> --body-file <path|->",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "auth": {"whoami": "notectl auth whoami"},
    "config": {"show": "notectl config show --resolved"}
  },
  "exit_codes": {
    "0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found",
    "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout",
    "8": "conflict", "9": "transient, including transport failures other than timeout",
    "10": "local file error (export destination)"
  },
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSPORT_ERROR", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED", "STREAM_INTERRUPTED"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, retry_after_ms, reconcile_first); on a mutating command, reconcile before retrying",
  "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
  "debug": {"flag": "--debug", "default": false, "description": "Opt-in; writes redacted request/response diagnostics to stderr; not allowed with --machine (VALIDATION_ERROR)."},
  "telemetry": {"enabled_by_default": false, "update_checks": false, "machine_mode": "always suppressed"},
  "auth": {"required_for": ["note *", "auth whoami"], "not_required_for": ["schema", "config show"], "scopes": {"read": ["note list", "note get", "note search", "note export"], "write": ["note create", "note delete"]}},
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env", "token cache ~/.cache/notectl/token.json (written by `notectl auth login`)"], "argv_secrets": "not accepted", "redaction": "token values are never printed; config show reports source and last 4 chars"},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (fallback ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_PROFILE", "NOTECTL_CONFIG", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "NO_COLOR"],
    "caches": [{"path": "~/.cache/notectl/token.json", "purpose": "credential cache", "writes": "atomic rename; last-writer-wins"}],
    "cwd_selects_context": false,
    "precedence": "flags > environment variables > config file > token cache",
    "disable_with": {"--isolated": "config and cache", "--no-config": "config only"},
    "inspect_with": ["notectl auth whoami", "notectl config show --resolved"],
    "non_interactive_bootstrap": "set NOTECTL_TOKEN; `notectl auth login` (browser flow) is human-only and fails with VALIDATION_ERROR under --machine"
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "Enumerate notes, newest-updated first; filter by exact tag. Use for filtered enumeration, not free-text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "note must have all given tags", "examples": ["work"]},
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 200},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["-updated_at", "updated_at", "title"], "default": "-updated_at", "tie_break": "id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], created_at?: string, updated_at: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "body is never included; use note get. next_cursor present iff has_more is true.",
        "projection": {"flag": "--select", "rule": "only selected fields are present in each item; unselected fields are absent, not null; id is always present"},
        "size_mode": "bounded by --limit"
      },
      "pagination": {"style": "cursor", "cursor_opaque": true, "cursor_lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT 5xx", "TRANSPORT_ERROR"], "backoff": "exponential, honors Retry-After"},
      "async": false, "streaming": false, "truncation": "only via pagination; has_more is authoritative", "artifact": false,
      "closed_stdout": "exits quietly",
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "Return one note by ID, including body.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^nt_[0-9A-Z]{26}$", "examples": ["nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string", "updated_at": "string"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected absent, not null; id always present"}, "size_mode": "small (body ≤ 1 MiB)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "NOTE_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search --query <text>",
      "summary": "Free-text search over title and body, relevance-ranked; returns summaries without body.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "min_length": 1, "max_length": 512, "examples": ["deploy rollback"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "restrict to notes having all given tags"},
        {"name": "--limit", "type": "integer", "default": 20, "min": 1, "max": 100},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "score", "snippet"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at", "score", "snippet"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 8000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": "[{id: string, title: string, tags: [string], updated_at: string, score: number, snippet: string}]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "shape_description": "sorted by score descending, tie-break id ascending; snippet ≤ 200 chars; zero matches is success with items []",
        "projection": {"flag": "--select", "rule": "only selected fields present; id always present"},
        "size_mode": "bounded by --limit"
      },
      "pagination": {"style": "cursor", "cursor_opaque": true, "cursor_lifetime": "15 minutes", "expired_code": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 8000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "async": false, "streaming": false, "truncation": "only via pagination", "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}, {"code": "CURSOR_EXPIRED", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <text> --body-file <path|->",
      "summary": "Create one note; returns its ID. Not idempotent unless --idempotency-key is supplied.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "'-' reads body from stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "max_count": 20},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 64, "description": "Server deduplicates creates with the same key for 24 hours and returns the original note."},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "constraints": ["exactly one of --body or --body-file is required; empty body allowed via --body ''"],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "requires_flag": "--body-file -", "accepted_formats": ["UTF-8 text"], "maximum_input_size": 1048576, "can_block": "only until EOF of explicitly piped stdin; if stdin is a TTY under --machine, fails with VALIDATION_ERROR instead of waiting", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as empty body"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "deduplicated": "boolean"}, "shape_description": "body is not echoed; deduplicated is true when --idempotency-key matched a prior create", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "size_mode": "small", "description": "validates input locally and checks auth/write scope with a read-only API call; never creates"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation; may refresh nothing locally (token cache is not written)"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0, "automatic_retry": "only with --idempotency-key, on RATE_LIMITED/TIMEOUT/TRANSPORT_ERROR"},
      "retry_safety": "safe to retry only if --idempotency-key was set on the original attempt and is reused within 24h; without it the outcome after timeout/interrupt is unknown and an empty search/list does not prove no note was created, so it is not safe to retry automatically",
      "signal_semantics": {"interrupt": "the remote create may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the create"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "CONFLICT", "exit": 8, "description": "idempotency key reused with different content"},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ],
      "error_catalog_note": "with --idempotency-key, TIMEOUT and TRANSPORT_ERROR payloads carry temporary: true and reconcile_first: false"
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "Delete one note by ID. --if-exists makes it repeat-safe.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^nt_[0-9A-Z]{26}$"}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "absent only when --if-exists suppressed NOTE_NOT_FOUND", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "shape": {"dry_run": "true", "planned_action": "delete|none", "id": "string"}, "shape_description": "none when --if-exists would suppress NOTE_NOT_FOUND", "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "performs a read to confirm existence; no mutation"},
      "latency_class": "network", "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "after TIMEOUT/TRANSPORT_ERROR/interrupt the outcome is unknown; recovery is to re-run with --if-exists (repeat-safe)",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "local_writes": "none", "remote_continues": true, "closed_stdout": "finishes the delete"},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "Write all notes (with bodies) to a local file; stdout reports path, byte size, content hash, and count. Fails if the file exists unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "'-' is not accepted; destination must be a file path"},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "file format: ndjson = one note per line sorted by id; json = {notes: [...], exported_at}"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 120000, "description": "deadline for the whole export"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string", "byte_size": "integer", "content_hash": "string", "note_count": "integer", "format": "ndjson|json", "exported_at": "string"}, "shape_description": "path is absolute; content_hash is sha256:<hex> of the file bytes", "size_mode": "small (data is on disk)"},
      "progress": {"machine_mode": "none on stderr (stderr_framing single-error-object)", "human_mode": "progress bar on stderr when stderr is a TTY"},
      "side_effects": {"external_mutation": false, "writes": ["--output path (local)"], "description": "writes to <path>.tmp-<pid> then atomically renames; remote data unchanged"},
      "latency_class": "slow", "timeout_defaults_ms": 120000,
      "retry_defaults": {"retries": 2, "scope": "per page fetch", "on": ["RATE_LIMITED", "TRANSPORT_ERROR"]},
      "consistency": "best-effort page walk; notes changed during export may be missing or stale",
      "signal_semantics": {"interrupt": "temp file removed; destination untouched", "local_writes": "atomic rename", "remote_continues": false},
      "concurrency": "concurrent exports to the same path: last rename wins; each result is a complete file",
      "async": false, "streaming": false, "pagination": "internal", "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}, {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    },
    {
      "canonical_invocation_path": "notectl auth whoami",
      "summary": "Show the authenticated identity and where the credential came from (never the token).",
      "classification": "admin", "read_only": true, "arguments": [], "flags": [{"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 3000}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"user_id": "string", "email": "string", "scopes": "[read|write]", "credential_source": "env:NOTECTL_TOKEN|cache", "api_url": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "network",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "TIMEOUT", "exit": 7, "retryable": true}, {"code": "TRANSPORT_ERROR", "exit": 9, "retryable": true}]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "Show resolved configuration with the source of each value; secrets redacted. No network.",
      "classification": "admin", "read_only": true, "arguments": [], "flags": [{"name": "--resolved", "type": "boolean", "default": true}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"values": "{<key>: {value: string, source: flag|env|config|cache|default}}", "config_files_read": "[string]", "isolated": "boolean"}, "shape_description": "token value rendered as ****<last4>", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    },
    {
      "canonical_invocation_path": "notectl schema [<command>] [--fingerprint] [--summary]",
      "summary": "Print this contract, one command's contract, a one-screen index (--summary), or the fingerprint only. No network, no auth, target <100ms.",
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command", "type": "string", "cardinality": "optional", "examples": ["note create"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "size_mode": "medium (full) / small (--fingerprint, --summary)"},
      "side_effects": {"external_mutation": false, "writes": []}, "latency_class": "local",
      "errors_possible": [{"code": "INTERNAL", "exit": 1}, {"code": "VALIDATION_ERROR", "exit": 2}]
    }
  ]
}
```

Fingerprint endpoint (`notectl schema --fingerprint`):

```json
{"schema_version": "1.0", "fingerprint": "ntc-7f3a91c2", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, `--machine`)

`notectl note list --machine --tag work --limit 2`:

```json
{
  "items": [
    {"id": "nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8", "title": "Q3 plan", "tags": ["planning", "work"], "updated_at": "2026-11-17T21:04:11Z"},
    {"id": "nt_01HZX1A2B3C4D5E6F7G8H9J0K1", "title": "Deploy checklist", "tags": ["ops", "work"], "updated_at": "2026-11-15T09:30:00Z"}
  ],
  "has_more": true,
  "next_cursor": "c2VxPTI",
  "limit": 2,
  "estimated_total": 37
}
```

`notectl note get --machine -- nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8`:

```json
{
  "id": "nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8",
  "title": "Q3 plan",
  "body": "1. Ship export\n2. Migrate search index",
  "tags": ["planning", "work"],
  "created_at": "2026-10-02T16:00:00Z",
  "updated_at": "2026-11-17T21:04:11Z"
}
```

`notectl note search --machine --query 'deploy rollback' --limit 1`:

```json
{
  "items": [
    {"id": "nt_01HZX1A2B3C4D5E6F7G8H9J0K1", "title": "Deploy checklist", "tags": ["ops", "work"], "updated_at": "2026-11-15T09:30:00Z", "score": 0.92, "snippet": "…if health checks fail, rollback with the previous image tag…"}
  ],
  "has_more": false,
  "limit": 1
}
```

`notectl note create --machine --title 'Q3 plan' --tag work --tag planning --idempotency-key 'k-2026-11-18-001' --body-file - < body.md`:

```json
{
  "id": "nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8",
  "title": "Q3 plan",
  "tags": ["planning", "work"],
  "created_at": "2026-11-18T10:12:03Z",
  "updated_at": "2026-11-18T10:12:03Z",
  "deduplicated": false
}
```

`notectl note create --machine --dry-run --title 'Q3 plan' --body 'draft'`:

```json
{"dry_run": true, "planned_action": "create", "title": "Q3 plan", "tags": [], "body_bytes": 5}
```

`notectl note delete --machine -- nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8`:

```json
{"id": "nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8", "status": "deleted"}
```

`notectl note delete --machine --if-exists -- nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8` (already gone, exit 0):

```json
{"id": "nt_01HZX3K8Q2M4N6P8R0T2V4W6Y8", "status": "absent"}
```

`notectl note export --machine --output ./notes.ndjson`:

```json
{
  "path": "/home/agent/work/notes.ndjson",
  "byte_size": 48213,
  "content_hash": "sha256:9f2c4e1a7b3d5f6081a2c3e4d5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718",
  "note_count": 37,
  "format": "ndjson",
  "exported_at": "2026-11-18T10:15:42Z"
}
```

## 5. Example error payloads (stderr, `--machine`, stdout empty)

Each object is the only stderr content (`single-error-object`).

Not found — `notectl note get --machine -- nt_01HZZZZZZZZZZZZZZZZZZZZZZZ`, exit `3`:

```json
{
  "code": "NOTE_NOT_FOUND",
  "message": "Note not found.",
  "resource_id": "nt_01HZZZZZZZZZZZZZZZZZZZZZZZ",
  "request_id": "req_8c1d2e",
  "temporary": false
}
```

Validation — `notectl note create --machine --title 'x' --body 'y' --tag 'Bad Tag'`, exit `2`:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid tag value.",
  "field": "--tag",
  "details": {"value": "Bad Tag", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$"},
  "hint": "Use lowercase letters, digits, '-' or '_', max 32 chars; other inputs are valid.",
  "temporary": false
}
```

Rate limited — `notectl note search --machine --query 'deploy'`, exit `6` (after built-in retries exhausted):

```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 30000,
  "details": {"retries_attempted": 2},
  "request_id": "req_41aa09",
  "temporary": true
}
```

Timeout on a non-idempotent create — `notectl note create --machine --title 'Q3 plan' --body-file plan.md`, exit `7`:

```json
{
  "code": "TIMEOUT",
  "message": "Request timed out; the note may or may not have been created.",
  "reconcile_first": true,
  "details": {"timeout_ms": 10000, "idempotency_key_supplied": false},
  "hint": "Do not retry automatically; next time pass --idempotency-key so retries are safe.",
  "temporary": false
}
```

Unauthenticated — any `note` command with no credential, exit `4`:

```json
{
  "code": "UNAUTHENTICATED",
  "message": "No credential found.",
  "details": {"checked_sources": ["env:NOTECTL_TOKEN", "cache"]},
  "hint": "Set NOTECTL_TOKEN.",
  "temporary": false
}
```

Export destination exists — `notectl note export --machine --output ./notes.ndjson`, exit `10`:

```json
{
  "code": "OUTPUT_EXISTS",
  "message": "Output file already exists.",
  "field": "--output",
  "path": "/home/agent/work/notes.ndjson",
  "hint": "Add --overwrite or choose a different --output path.",
  "temporary": false
}
```

## 6. Checklist coverage

| Checklist section | Answer |
|---|---|
| Command Model | `notectl note <verb>`, shallow; ID positional selector; conventional flags (`--limit`, `--timeout-ms`, `--output`, `--format`); no aliases. |
| Machine Schema | §3; per-command `notectl schema <command>`; fingerprint + scope + version policy. |
| Stdin Contract | Declared per command; only `note create --body-file -` reads stdin, explicit, 1 MiB cap, never waits on a TTY in machine mode. |
| Shell Safety | `--` supported and declared; values never shelled out; examples quoted; hints contain no executable strings. |
| Agent-Safe Invocation | `--machine` profile distinct from `--isolated`; per-stream TTY detection; `NOTECTL_TOKEN` bootstrap; schema/help are local and lazy; all networked commands take `--timeout-ms`. |
| Output | stdout payload only; `single-error-object` stderr; deterministic sort with tie-break; cursor contract; projections; UTC; `--output` only on export with path/size/hash. |
| Errors And Exit Codes | Tool-level map + per-command catalog with `retryable`/`reconcile_first`/`suppressed_by`; `INTERNAL` fallback; `TRANSPORT_ERROR`; unknown-code policy; opt-in redacted `--debug`. |
| Partial failure | Not applicable: no multi-item command; export is all-or-nothing (atomic rename). |
| Ambient State | Sources, precedence, `--isolated`/`--no-config`, `auth whoami`, `config show --resolved`, redaction; no argv secrets; cwd does not select context. |
| Mutations | `create`/`delete` explicit verbs, `--dry-run` with `dry_run: true`; `--idempotency-key` for create, `--if-exists` for delete; retry safety and signal semantics declared. Async jobs: not applicable — all commands complete in the foreground (export declares deadline and interrupt behavior). |
| Side Effects And Telemetry | Reads write nothing (export writes only its declared `--output`); no telemetry/update checks. |
| Prose Surfaces | Summaries are rules-first and separate sibling commands (`list` vs `search`, `get` vs `search`). |
| Tests | Ship: schema snapshot + fingerprint stability; golden success payloads above; error payload + observed exit-code mapping for every catalog entry; TTY vs non-TTY and `--machine` suppression; `--body-file -` with empty/oversize/TTY stdin; pagination and `CURSOR_EXPIRED`; export atomicity, hash correctness, interrupt cleanup, concurrent exports; env/config precedence and `--isolated`; dry-run non-mutation for create/delete; create idempotency-key replay; interrupt during create/delete. Deprecation tests and async cancellation: not applicable yet (none declared). |
~~~~~~~~
