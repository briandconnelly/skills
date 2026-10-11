# Scenario 1 (Design) — with-skill run (wording before commit 4)

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set). Ran against the skill text of commit c154b17, before the Codex implementation-review fixes in commit 4; the final-wording validation run is recorded separately.
- **Score:** 9/9 scored
- **Subagent tokens:** 109,083 (harness-reported total for the run)
- **Transcript sha256:** `cd1cc0a223bd45bf692de46a7da66e933d99d7eedd446a4ad85d7168afca0d5d` (session-local copy; not committed)

## Exact prompt given

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files or run git.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; two `python3 -I` JSON-validity checks of its own output; nothing under `tests/`; no other file.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| A1 | A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema). | **PASS** | `canonical_machine_profile: ["--machine"]`, `implies` four flags, all four present in `global_flags`. |
| A2 | The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes). | **PASS** | `exit_codes` 0–12, `symbolic_error_codes`, `errors_possible` on every command with `retryable`, `reconcile_first`, `suppressed_by`. |
| A3 | stdout is success payload only; structured failures go to stderr with declared framing (Output). | **PASS** | `stderr_framing: "single-error-object"` with description; §5 "stdout empty; the object is the only stderr content". |
| A4 | `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work). | **PASS** | "the verb is the action trigger, no confirmation prompt exists"; `alternate_outputs["--dry-run"]` shape has `dry_run: true`. |
| A5 | List/search output declares pagination with `has_more` and a navigation token (Output). | **PASS** | `has_more`, `next_cursor`, `limit`, `estimated_total`, full cursor contract (opacity, lifetime, expiry code, restart, consistency). |
| A6 | Export is the only `--output <file>` command and returns path, byte size, and content hash (Output). | **PASS** | `--output` on `note export` only; artifact shape `path`, `byte_size`, `content_hash`, plus `note_count`. |
| A7 | Duration flags declare units in the name or a `unit` field (Machine Schema). | **PASS** | `--timeout-ms` with `"unit": "ms"`; `timeout_defaults_ms` per command. |
| A8 | Each command declares one output class; any flag that switches the class declares the switch (Output). | **PASS** | One `output.class` per command; `--dry-run` declared under `alternate_outputs`. |
| A9 | Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State). | **PASS** | `ambient_state` block; `whoami`, `config show --resolved`, `token_source`; `--isolated` and `--no-config`. |

**Set:** challenge.
**Regression vs 2026-06-09 baseline (1/9):** none (prompt unchanged since that baseline).
**Overhead:** 109,083 subagent tokens; no same-day baseline (prompt unchanged), the run took 8.7 minutes.
**Notes:** the run organically used the items this PR added: a `projection` rule for `--select`, `temporary` as the one payload retryability field with `reconcile_first` mirrored in the catalog, and `retry_after_ms` on the rate-limit payload; it stated explicitly that no streaming or bulk command is in scope, so the completion-record rule did not apply.
It also validated its own JSON with `python3 -I`, which the skill does not ask for.

## Full final output

Verbatim final message returned by the subagent:

# `notectl` agent-facing CLI contract

Designed per `/Users/bdc/projects/skills/agent-friendly-cli/SKILL.md` and its four references (`contract-checklist.md`, `design-workflow.md`, `examples.md`, `review-workflow.md`), all read in full; nothing under `tests/` or elsewhere in the repo was read, no file was modified, and git was not run.
Audience: tool author (new design), so the output leads with the contract itself and ends with checklist coverage per the Design done criteria.
Verification I actually ran: the schema JSON and all 17 example payloads below were piped through `python3 -I` `json.load` and parsed (output: `valid JSON; 11 commands; 14 codes` and `all 17 payloads valid`).
Nothing here has been executed as a real CLI; behaviour claims are design declarations, not observed runs.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for the next step |
|---|---|---|---|
| enumerate notes | query | nothing | ids + titles + tags, page token |
| fetch one note | inspect | id | full record |
| find a note without its id | query | free-text query | ids + titles + tags, page token |
| create a note | mutate | title, body source | the created record with its id |
| delete a note | mutate | id | id + deleted flag |
| back up everything to disk | query (artifact) | output path | path, byte size, content hash, count |

Supporting jobs the checklist requires: `schema` / `schema --fingerprint` / `version` (discover, local, no network), `whoami` + `config show --resolved` (ambient-state inspection), `auth login --token-stdin` (non-interactive bootstrap; optional because `NOTECTL_TOKEN` alone suffices).
No bulk or async operations are in scope, so the `stream` and `bulk-result` output classes are intentionally unused in v1.

## 2. Command surface

One noun, conventional verbs, shallow tree, one primary selector per command (positional `<id>` for get/delete, positional `<query>` for search, named flags elsewhere).
`--` end-of-options is supported everywhere; values are quoted in every canonical example because titles, bodies, queries, and tags are untrusted data.

```
notectl note list   [--limit N] [--cursor TOKEN] [--tag TAG]... [--sort id|title] [--select FIELD]...
notectl note get    <id> [--select FIELD]...
notectl note search <query> [--limit N] [--cursor TOKEN] [--tag TAG]... [--select FIELD]...
notectl note create --title TITLE (--body TEXT | --body-file PATH | --body-stdin) [--tag TAG]... [--idempotency-key KEY] [--dry-run]
notectl note delete <id> [--if-exists] [--dry-run]
notectl note export --output PATH [--format ndjson|json] [--overwrite]

notectl schema [--fingerprint | --summary | <command>]
notectl version
notectl whoami
notectl config show --resolved
notectl auth login --token-stdin

global: --machine (implies --json --no-progress --no-color --non-interactive)
        --json --no-progress --no-color --non-interactive
        --isolated --no-config --api-url URL --timeout-ms N --debug-log PATH
```

Canonical machine-mode examples:

```sh
notectl schema --fingerprint
notectl note list --machine --limit 100 --tag 'work'
notectl note get --machine -- 'note_8f2k3jd9a1qz'
notectl note search --machine -- 'quarterly planning'
printf '%s' "$BODY" | notectl note create --machine --title 'Standup 2026-10-11' --body-stdin --tag 'work' --idempotency-key 'standup-2026-10-11'
notectl note create --machine --title 'Standup 2026-10-11' --body 'Blocked on API review.' --dry-run
notectl note delete --machine --if-exists -- 'note_9h1m4kq2b7rt'
notectl note export --machine --output 'notes-backup.ndjson'
NOTECTL_TOKEN="$TOKEN" notectl whoami --machine --isolated
```

Design decisions worth flagging:

- `note delete` has no confirmation prompt in any mode; the verb is the explicit action trigger and `--dry-run` is the preview, so there is nothing that can block in CI.
- `--body-stdin` is an explicit flag, not auto-detected, so an agent that forgets to redirect stdin never hangs.
- Body is excluded from the default `list`/`search` projection for token cost; `--select body` adds it.
- No `--token` flag exists at all; secrets enter only via `NOTECTL_TOKEN`, the 0600 credential file, or `auth login --token-stdin`.
- `notectl` never retries internally; `temporary`, `reconcile_first`, and the per-command catalog tell the caller what to do.
- `--debug-log` writes to a file rather than stderr so debug detail can never interleave with the single error object.

## 3. Machine schema (`notectl schema`)

```json
{
  "schema_version": "1.0.0",
  "fingerprint": "nct-7f3a9c21",
  "fingerprint_scope": "schema-contract",
  "fingerprint_input": "every key in this document except tool_version; the tool version is not an input, so version-only releases keep the fingerprint",
  "compatibility": {
    "additive_minor_bump": ["new commands", "new optional flags", "new optional output fields", "new symbolic codes on new commands"],
    "breaking_major_bump": ["removals", "renames", "type or meaning changes", "exit-code remapping", "new required flags or arguments", "changes to a default sort, default projection, or stderr framing"],
    "rule": "any contract change, additive or breaking, changes fingerprint; breaking changes also bump the major component"
  },
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum of literals; string[] is an array of strings; [S] is an array of records shaped S; a field is required unless its name ends in ? or a declared projection removes it; absent means absent, never null",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "in machine mode, on failure the structured error object is the only stderr content and stdout is empty; on success stderr is empty",
  "end_of_options_supported": true,
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color", "--non-interactive"], "description": "non-interactive machine mode: structured output only; no prompts, color, progress, or pager"},
    {"name": "--json", "type": "boolean", "default": false, "description": "render success payloads as JSON or NDJSON per the command's output class"},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "suppress progress output on stderr"},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "suppress ANSI color on both streams; also honored via NO_COLOR env"},
    {"name": "--non-interactive", "type": "boolean", "default": false, "description": "never prompt; a path that would prompt fails with VALIDATION_ERROR instead"},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "ignore config file and credential file; token comes only from NOTECTL_TOKEN, api_url only from --api-url or NOTECTL_API_URL"},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "ignore the config file only; credential file still read"},
    {"name": "--api-url", "type": "string", "default": null, "description": "remote API base URL; overrides NOTECTL_API_URL and config api_url"},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": null, "description": "per-invocation deadline; overrides the command's declared timeout_defaults_ms"},
    {"name": "--debug-log", "type": "path", "default": null, "description": "opt-in: append redacted request/response traces to this file; never written to stdout or stderr"}
  ],
  "command_tree": {
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search <query>",
      "create": "notectl note create --title <title> (--body <text> | --body-file <path> | --body-stdin)",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    },
    "schema": "notectl schema [--fingerprint | --summary | <command>]",
    "version": "notectl version",
    "whoami": "notectl whoami",
    "config": {"show": "notectl config show --resolved"},
    "auth": {"login": "notectl auth login --token-stdin"}
  },
  "exit_codes": {
    "0": "success",
    "1": "generic",
    "2": "usage or validation",
    "3": "not found",
    "4": "unauthenticated",
    "5": "forbidden",
    "6": "rate limited",
    "7": "timeout",
    "8": "conflict",
    "9": "transient, not otherwise classified",
    "10": "output file exists (domain-specific)",
    "11": "output file write failed (domain-specific)",
    "12": "remote API version unsupported (domain-specific)"
  },
  "exit_code_note": "codes 3-12 are notectl conventions, not sysexits.h; INTERRUPTED has no numeric code: notectl cleans up, writes the error object to stderr, then re-raises the signal so the shell reports its usual 128+n",
  "symbolic_error_codes": ["VALIDATION_ERROR", "CURSOR_EXPIRED", "CONFIG_INVALID", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSIENT", "OUTPUT_EXISTS", "OUTPUT_WRITE_FAILED", "API_VERSION_UNSUPPORTED", "INTERRUPTED"],
  "error_shape": {"code": "string", "message": "string", "hint?": "string", "field?": "string", "details?": "object", "resource_id?": "string", "conflict_with?": "string", "path?": "string", "retry_after_ms?": "integer", "temporary": "boolean", "reconcile_first?": "boolean", "request_id?": "string", "docs_url?": "string"},
  "auth": {
    "required_for": ["note list", "note get", "note search", "note create", "note delete", "note export", "whoami"],
    "not_required_for": ["schema", "version", "config show", "auth login"],
    "credential": "bearer token",
    "scopes": {"notes:read": ["note list", "note get", "note search", "note export", "whoami"], "notes:write": ["note create", "note delete"]},
    "non_interactive_bootstrap": "set NOTECTL_TOKEN in the environment (no login step), or pipe the token to notectl auth login --token-stdin --machine"
  },
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["env NOTECTL_TOKEN", "credential file $XDG_CONFIG_HOME/notectl/credentials.json (mode 0600)"], "flag_intake": "none; no --token flag exists", "disabled_by": "--isolated disables the credential file"},
    "config_files": {"path": "$XDG_CONFIG_HOME/notectl/config.toml (override with NOTECTL_CONFIG)", "keys": ["api_url", "timeout_ms", "default_limit"], "disabled_by": ["--no-config", "--isolated"]},
    "environment_variables": ["NOTECTL_TOKEN", "NOTECTL_API_URL", "NOTECTL_CONFIG", "NO_COLOR", "XDG_CONFIG_HOME"],
    "caches": {"reads": false, "writes": false},
    "precedence": "flags > environment variables > config file",
    "inspection": {"identity": "notectl whoami", "resolved_config": "notectl config show --resolved", "credential_source": "token_source field of notectl config show --resolved"},
    "secrets": {"values": ["token"], "redaction": "rendered as [redacted] in config show, debug logs, and all error payloads"}
  },
  "non_tty_behavior": {"stdout": "no pager, no color; human text unless --json", "stderr": "no color, no progress or spinners", "stdin": "no prompts; a path that needs terminal input fails with VALIDATION_ERROR"},
  "telemetry": {"enabled": false, "update_checks": false, "network_calls": "only to the configured api_url, only for commands whose auth.required_for lists them"},
  "metadata_paths": {"commands": ["--help", "schema", "schema --fingerprint", "version"], "target_ms": 100, "guarantees": "no network, no auth validation, no config read, HTTP client imported lazily"},
  "signals": {
    "note create, note delete": "single HTTP request; SIGINT/SIGTERM after the request is sent leaves the remote outcome unknown and the server completes independently; no local writes; follow the command's reconciliation",
    "note export": "the temp file <output>.notectl-tmp-<pid> in the destination directory is removed; destination untouched; remote state unaffected",
    "auth login": "credential file replaced atomically by rename; an interrupt leaves the previous file intact"
  },
  "local_state_concurrency": {"credential_file": "write to temp then rename; last writer wins (documented)", "export_output": "write to temp then rename; without --overwrite the final step is a no-replace rename so a concurrent writer gets OUTPUT_EXISTS instead of clobbering; with --overwrite last writer wins"},
  "retry_policy": "notectl never retries internally; retries: 0 for every command; callers branch on temporary and reconcile_first",
  "async_jobs": "none; no command outlives its process, so job IDs, polling, wait, and cancel are not applicable",
  "api_version_negotiation": "requests carry Accept: application/vnd.notectl.v1+json; a server that cannot serve v1 yields API_VERSION_UNSUPPORTED (exit 12, not retryable)",
  "note_shape": {"id": "string (pattern ^note_[a-z0-9]{12}$)", "title": "string (1-200 chars)", "body": "string (0-1048576 bytes UTF-8)", "tags": "string[] (0-32 items, each ^[a-z0-9][a-z0-9_-]{0,63}$)"},
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "summary": "page through all notes; default projection omits body; filter by --tag, order by --sort",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null, "description": "opaque token from a previous page's next_cursor"},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "description": "only notes carrying every given tag (AND)"},
        {"name": "--sort", "type": "enum", "enum": ["id", "title"], "default": "id", "description": "ascending; ties broken by id"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags"], "cardinality": "many", "default": ["id", "title", "tags"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": [{"id": "string", "title": "string", "tags": "string[]", "body?": "string"}], "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present on each item; unselected fields are absent, not null; id is always present"},
        "pagination": {"has_more": "always present", "next_cursor": "present iff has_more is true", "cursor_opacity": "opaque", "cursor_lifetime_ms": 600000, "expired_cursor_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort, not snapshot-consistent"},
        "size_mode": "paged"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CURSOR_EXPIRED", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl note get <id>",
      "summary": "fetch one note by exact id, body included",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]{12}$", "examples": ["note_8f2k3jd9a1qz"]}],
      "flags": [{"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags"], "cardinality": "many", "default": ["id", "title", "body", "tags"]}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "body": "string", "tags": "string[]"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "size_mode": "small (body bounded at 1 MiB by validation)"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl note search <query>",
      "summary": "full-text search over title and body when the id is unknown; same page shape as list, ranked by relevance then id",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [{"name": "query", "type": "string", "cardinality": "one", "min_length": 1, "max_length": 1024, "untrusted": true, "examples": ["quarterly planning"]}],
      "flags": [
        {"name": "--limit", "type": "integer", "default": 50, "min": 1, "max": 500},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": []},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags"], "cardinality": "many", "default": ["id", "title", "tags"]}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json",
        "shape": {"items": [{"id": "string", "title": "string", "tags": "string[]", "body?": "string"}], "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "sort": "relevance descending, ties broken by id ascending; deterministic for a fixed corpus",
        "projection": {"flag": "--select", "rule": "same as note list"},
        "pagination": "same contract as note list",
        "size_mode": "paged"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "async": false, "streaming": false, "pagination": true, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CURSOR_EXPIRED", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl note create --title <title> (--body <text> | --body-file <path> | --body-stdin)",
      "summary": "create one note; exactly one body source; pass --idempotency-key to make retry after timeout safe",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "min_length": 1, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "exactly_one_of": ["--body", "--body-file", "--body-stdin"]},
        {"name": "--body-file", "type": "path", "default": null, "exactly_one_of": ["--body", "--body-file", "--body-stdin"]},
        {"name": "--body-stdin", "type": "boolean", "default": false, "exactly_one_of": ["--body", "--body-file", "--body-stdin"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "default": [], "max_items": 32, "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"},
        {"name": "--idempotency-key", "type": "string", "default": null, "max_length": 128, "description": "server-side replay guard; the same key with the same payload returns the original note; a different payload yields CONFLICT"},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": "only with --body-stdin", "auto_detected_when_piped": false, "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": 1048576, "can_block": "yes, only when --body-stdin is given and the pipe is open", "mutually_exclusive_with": ["--body", "--body-file"], "empty_stdin": "accepted as an empty body"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "title": "string", "body": "string", "tags": "string[]"}, "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "body_bytes": "integer", "tags": "string[]", "idempotency_key?": "string"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "local validation only: no network request, no token refresh, no file writes; exit 0 when the planned create is valid, else the declared error contract"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown; with --idempotency-key, re-run the identical command: the server returns the existing note; without it, run notectl note search with the title and compare before re-creating",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true, "note": "rejected before processing; safe to retry"},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "retryable_with": "--idempotency-key"},
        {"code": "CONFLICT", "exit": 8, "retryable": false, "note": "--idempotency-key reused with a different payload"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true, "retryable_with": "--idempotency-key"},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "summary": "permanently delete one note by id; the verb is the action trigger, no confirmation prompt exists; --if-exists makes it idempotent",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "pattern": "^note_[a-z0-9]{12}$", "examples": ["note_8f2k3jd9a1qz"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false, "description": "exit 0 with deleted: false when the note is already gone"},
        {"name": "--dry-run", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "deleted": "boolean"}, "deleted_semantics": "true when this invocation removed the note; false only with --if-exists when it was already absent", "size_mode": "small"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete", "id": "string", "title": "string"}, "size_mode": "small"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "one read (GET note) to confirm existence; no mutation, no file writes; exit 0 if the note exists, NOTE_NOT_FOUND otherwise (suppressed to deleted: false by --if-exists)"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, TRANSIENT, or interrupt the outcome is unknown; run notectl note get <id>: NOTE_NOT_FOUND means the delete committed; re-running with --if-exists is always safe",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "NOTE_NOT_FOUND", "exit": 3, "retryable": false, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true, "retryable_with": "--if-exists"},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true, "retryable_with": "--if-exists"},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl note export --output <path>",
      "summary": "write every note, body included, to one local file and return a pointer; refuses to overwrite unless --overwrite",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true, "description": "destination file; parent directory must exist; '-' is not accepted"},
        {"name": "--format", "type": "enum", "enum": ["ndjson", "json"], "default": "ndjson", "description": "ndjson: one full note per line; json: a single array"},
        {"name": "--overwrite", "type": "boolean", "default": false}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "shape": {"path": "string (as given)", "format": "ndjson|json", "note_count": "integer", "byte_size": "integer", "content_hash": "string (sha256:<hex>)"}, "size_mode": "pointer only; the artifact grows with the corpus", "artifact_content": "notes ordered by id ascending with all four fields, so identical corpora produce identical content_hash"},
      "side_effects": {"external_mutation": false, "writes": ["local file at --output via temp file plus rename in the same directory"]},
      "latency_class": "slow", "timeout_defaults_ms": 120000, "retry_defaults": {"retries": 0},
      "internal_pagination": "walks the list endpoint at limit 500; an internal CURSOR_EXPIRED is surfaced as TRANSIENT with temporary true because a restart is the repair",
      "progress": "human mode: one stderr line per page; machine mode: none (--no-progress implied)",
      "async": false, "streaming": false, "pagination": false, "truncation": false, "artifact": true,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "FORBIDDEN", "exit": 5, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true, "note": "temp file removed; destination untouched"},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_EXISTS", "exit": 10, "retryable": false, "suppressed_by": "--overwrite"},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 11, "retryable": false},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl schema [--fingerprint | --summary | <command>]",
      "summary": "print this contract; --fingerprint prints only the cache key; <command> prints one command entry",
      "classification": "discover", "read_only": true,
      "arguments": [{"name": "command", "type": "string", "cardinality": "zero-or-one", "examples": ["note create"]}],
      "flags": [{"name": "--fingerprint", "type": "boolean", "default": false}, {"name": "--summary", "type": "boolean", "default": false}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": "this document, or {schema_version, fingerprint, fingerprint_scope} with --fingerprint", "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "timeout_defaults_ms": null, "retry_defaults": {"retries": 0},
      "errors_possible": [{"code": "VALIDATION_ERROR", "exit": 2, "retryable": false, "note": "unknown <command>"}]
    },
    {
      "canonical_invocation_path": "notectl version",
      "summary": "tool version plus the schema version, fingerprint, and supported API version; no network",
      "classification": "discover", "read_only": true,
      "arguments": [], "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"tool_version": "string", "schema_version": "string", "fingerprint": "string", "api_version": "v1"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "timeout_defaults_ms": null, "retry_defaults": {"retries": 0},
      "errors_possible": []
    },
    {
      "canonical_invocation_path": "notectl whoami",
      "summary": "confirm which account the resolved token authenticates as",
      "classification": "inspect", "read_only": true,
      "arguments": [], "flags": [],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"user_id": "string", "email?": "string", "scopes": "string[]", "api_url": "string", "token_source": "env:NOTECTL_TOKEN|file"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "errors_possible": [
        {"code": "CONFIG_INVALID", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "API_VERSION_UNSUPPORTED", "exit": 12, "retryable": false}
      ]
    },
    {
      "canonical_invocation_path": "notectl config show --resolved",
      "summary": "print every resolved setting with its source; token value is redacted; no network",
      "classification": "inspect", "read_only": true,
      "arguments": [], "flags": [{"name": "--resolved", "type": "boolean", "required": true}],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"api_url": {"value": "string", "source": "flag|env|config|default"}, "timeout_ms": {"value": "integer", "source": "flag|env|config|default"}, "token": {"present": "boolean", "value": "[redacted]", "source": "env:NOTECTL_TOKEN|file|none"}, "config_file": {"path": "string", "loaded": "boolean"}, "isolated": "boolean"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "local", "timeout_defaults_ms": null, "retry_defaults": {"retries": 0},
      "errors_possible": [{"code": "CONFIG_INVALID", "exit": 2, "retryable": false}]
    },
    {
      "canonical_invocation_path": "notectl auth login --token-stdin",
      "summary": "store a token in the credential file; optional, since NOTECTL_TOKEN alone suffices; --token-stdin is the only non-interactive intake",
      "classification": "admin", "read_only": false,
      "arguments": [],
      "flags": [{"name": "--token-stdin", "type": "boolean", "default": false, "description": "read the token from stdin (trailing newline stripped); without it a TTY stdin is prompted with hidden input and a non-TTY or --non-interactive stdin fails with VALIDATION_ERROR"}],
      "stdin_contract": {"reads": "only with --token-stdin, or when prompting on a TTY", "auto_detected_when_piped": false, "accepted_formats": ["text/plain, single line"], "maximum_input_size": 4096, "can_block": "yes, only with --token-stdin or an interactive TTY prompt", "mutually_exclusive_with": [], "empty_stdin": "VALIDATION_ERROR"},
      "output": {"class": "record", "format": "json", "shape": {"credential_file": "string", "user_id": "string"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": ["credential file, mode 0600, atomic rename"], "network": "one whoami call to validate the token before writing"},
      "latency_class": "network", "timeout_defaults_ms": 10000, "retry_defaults": {"retries": 0},
      "dry_run": "not applicable: the only effect is a local file write validated by whoami; use --isolated with NOTECTL_TOKEN to test a token without storing it",
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2, "retryable": false},
        {"code": "UNAUTHENTICATED", "exit": 4, "retryable": false},
        {"code": "TIMEOUT", "exit": 7, "retryable": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": true},
        {"code": "OUTPUT_WRITE_FAILED", "exit": 11, "retryable": false}
      ]
    }
  ]
}
```

### `notectl schema --fingerprint`

```json
{"schema_version": "1.0.0", "fingerprint": "nct-7f3a9c21", "fingerprint_scope": "schema-contract"}
```

## 4. Example success payloads (stdout, machine mode, exit 0, stderr empty)

`notectl note list --machine --limit 2` (list; body absent by default projection):

```json
{
  "items": [
    {"id": "note_8f2k3jd9a1qz", "title": "Quarterly planning", "tags": ["work", "planning"]},
    {"id": "note_9h1m4kq2b7rt", "title": "Reading list", "tags": ["personal"]}
  ],
  "has_more": true,
  "next_cursor": "c1QyMDI2LTEwLTExfG5vdGVfOWgxbTRrcTJiN3J0",
  "limit": 2,
  "estimated_total": 143
}
```

`notectl note get --machine -- 'note_8f2k3jd9a1qz'` (record):

```json
{
  "id": "note_8f2k3jd9a1qz",
  "title": "Quarterly planning",
  "body": "Agenda:\n- headcount\n- roadmap review\n",
  "tags": ["work", "planning"]
}
```

`notectl note search --machine -- 'quarterly planning'` (list, one hit):

```json
{
  "items": [{"id": "note_8f2k3jd9a1qz", "title": "Quarterly planning", "tags": ["work", "planning"]}],
  "has_more": false,
  "limit": 50,
  "estimated_total": 1
}
```

`notectl note search --machine -- 'nothing matches this'` (list, empty; still exit 0, still the full envelope):

```json
{"items": [], "has_more": false, "limit": 50, "estimated_total": 0}
```

`notectl note create --machine --title 'Standup 2026-10-11' --body 'Blocked on API review.' --tag 'work' --tag 'standup'` (record):

```json
{
  "id": "note_2c7d9e1f4g6h",
  "title": "Standup 2026-10-11",
  "body": "Blocked on API review.",
  "tags": ["work", "standup"]
}
```

Same command with `--dry-run --idempotency-key 'standup-2026-10-11'` (no network call; never byte-identical to a real create):

```json
{
  "dry_run": true,
  "planned_action": "create",
  "title": "Standup 2026-10-11",
  "body_bytes": 23,
  "tags": ["work", "standup"],
  "idempotency_key": "standup-2026-10-11"
}
```

`notectl note delete --machine -- 'note_9h1m4kq2b7rt'` (record):

```json
{"id": "note_9h1m4kq2b7rt", "deleted": true}
```

Same with `--dry-run` (one GET, no mutation):

```json
{"dry_run": true, "planned_action": "delete", "id": "note_9h1m4kq2b7rt", "title": "Reading list"}
```

`notectl note export --machine --output 'notes-backup.ndjson'` (artifact pointer; the file itself holds one full note per line, id-ascending):

```json
{
  "path": "notes-backup.ndjson",
  "format": "ndjson",
  "note_count": 143,
  "byte_size": 48213,
  "content_hash": "sha256:3b7e1a9c0d4f2e8b6a5c1d9e7f3a2b4c6d8e0f1a2b3c4d5e6f7a8b9c0d1e2f3a"
}
```

## 5. Example error payloads (stderr, machine mode; stdout empty; the object is the only stderr content)

Agents branch on `code`; `message` is the human rendering and may be rewritten without a contract bump.

Failure mode 1, validation error on create, exit 2.
`field` names the published flag and the machine-usable repair data (pattern, bad value) is in `details`, not only in `hint`.

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid tag value.",
  "field": "--tag",
  "details": {"invalid_value": "Work Notes", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$", "max_items": 32},
  "hint": "Tags are lowercase letters, digits, hyphen, or underscore; use work-notes.",
  "temporary": false
}
```

Failure mode 2, not found on get or delete, exit 3:

```json
{
  "code": "NOTE_NOT_FOUND",
  "message": "Note not found.",
  "resource_id": "note_0000000000zz",
  "hint": "Search for the note by title with note search, or pass --if-exists to delete when it may already be gone.",
  "temporary": false
}
```

Failure mode 3, timeout on create without an idempotency key, exit 7.
`temporary` is false and `reconcile_first` is true because a blind retry could duplicate the note; this mirrors the catalog entry.

```json
{
  "code": "TIMEOUT",
  "message": "No response within 10000 ms; the create may or may not have committed.",
  "details": {"timeout_ms": 10000, "idempotency_key": null},
  "hint": "Run note search with the same title before re-creating, or re-run with --idempotency-key to make the retry safe.",
  "temporary": false,
  "reconcile_first": true,
  "request_id": "req_01HZX7N3K9"
}
```

Failure mode 4, export destination already exists, exit 10 (domain-specific, declared):

```json
{
  "code": "OUTPUT_EXISTS",
  "message": "Output file already exists.",
  "field": "--output",
  "path": "notes-backup.ndjson",
  "hint": "Choose a different --output path or pass --overwrite.",
  "temporary": false
}
```

Failure mode 5, rate limited on any network command, exit 6 (`temporary` is the authoritative retry signal, not the exit code):

```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 30000,
  "temporary": true,
  "request_id": "req_01HZX7P8Q2"
}
```

Failure mode 6, no credential resolved under `--isolated`, exit 4 (sources are named, the token value never appears):

```json
{
  "code": "UNAUTHENTICATED",
  "message": "No credential resolved.",
  "details": {"checked_sources": ["env:NOTECTL_TOKEN", "file:/Users/me/.config/notectl/credentials.json"], "isolated": true},
  "hint": "Set NOTECTL_TOKEN in the environment; --isolated disables the credential file.",
  "temporary": false
}
```

Failure mode 7, expired cursor on list or search, exit 2:

```json
{
  "code": "CURSOR_EXPIRED",
  "message": "Cursor is no longer valid.",
  "field": "--cursor",
  "details": {"cursor_lifetime_ms": 600000},
  "hint": "Re-run note list without --cursor to start a new page walk.",
  "temporary": false
}
```

## 6. Tests to ship (checklist § Tests)

- schema snapshot and `schema --fingerprint` stability across a version-only bump
- golden success payload per command, including empty `search` and `list` results
- golden error payload plus observed exit for every `errors_possible` entry, including `OUTPUT_EXISTS` under a concurrent-writer race and `INTERRUPTED` re-raising the signal
- stdout/stderr captured separately in every run; assert stdout empty on failure and stderr empty on success in machine mode
- TTY vs non-TTY per stream; `--machine` suppresses prompts, color, progress, pager
- `--body-stdin` with piped, empty, and over-limit input; `--body-stdin` absent with a piped stdin does not block or read
- `auth login` without `--token-stdin` on non-TTY stdin fails with `VALIDATION_ERROR` rather than hanging
- cursor walk, expired cursor, `--select` projection (unselected fields absent, not null)
- export: temp-then-rename, no-replace rename without `--overwrite`, SIGINT leaves no temp file and an untouched destination, deterministic `content_hash` for a fixed corpus
- flag > env > config precedence; `--isolated` and `--no-config` ignore the right sources; `config show --resolved` redacts the token
- `--dry-run` for create (zero network calls asserted via a mock transport) and delete (exactly one GET)
- `--idempotency-key` replay returns the original note; different payload yields `CONFLICT`
- metadata paths (`--help`, `schema`, `version`) make no network call and finish under 100 ms

## 7. Checklist coverage (Design done criteria)

| Checklist section | Where it is answered |
|---|---|
| Command Model | §2: one noun, conventional verbs, shallow tree, no aliases in 1.0, consistent `--limit/--cursor/--tag/--select` across list and search, no flag changes meaning across commands |
| Machine Schema | §3: every listed item present; `fingerprint_input` and `compatibility` declared; `--timeout-ms` carries its unit in the name; latency class, timeouts, retries, async, pagination, truncation, artifact, version negotiation per command |
| Stdin Contract | per-command `stdin_contract`; only `create --body-stdin` and `auth login --token-stdin` read stdin, both explicit, never auto-detected |
| Shell Safety | `end_of_options_supported: true`; `query` argument marked `untrusted`; values quoted in canonical examples; hints carry flag names, never shell strings |
| Agent-Safe Invocation | single `--machine` profile with declared implications; `--isolated` distinct and still completes authenticated reads via `NOTECTL_TOKEN`; `non_tty_behavior` per stream; `metadata_paths` sub-100 ms; `non_interactive_bootstrap` declared |
| Output | stdout success-only; `stderr_framing` closed enum `single-error-object`; one output class per command with `alternate_outputs` for `--dry-run`; pagination with `has_more`/`next_cursor`/`limit`/`estimated_total` and a full cursor contract; deterministic default sort; projection rule declared; `--output` restricted to export and returns path/byte_size/content_hash; no `message` field in success payloads. Truncation: not applicable, body is bounded at 1 MiB by validation and lists are paged, so nothing is ever silently cut |
| Errors And Exit Codes | tool-level numeric and symbolic codes; `3`–`12` declared as conventions; per-command catalog with `retryable`, `reconcile_first`, `suppressed_by`, `retryable_with`; `error_shape` with required `code`/`message`; secrets redacted. Partial failure / `--allow-partial`: not applicable, no multi-item command exists in 1.0 |
| Ambient State | `ambient_state` block: sources, precedence, env list, no caches, disable flags, `whoami` + `config show --resolved` + `token_source` inspection, redaction; no `--token` flag |
| Mutations And Long-Running Work | `create`/`delete` are explicit triggers with `--dry-run`, idempotency (`--idempotency-key`, `--if-exists`), reconciliation paths, signal semantics, and local-state concurrency rules. Job IDs / polling / `wait` / cancel: not applicable, no command outlives its process (`async_jobs`). `auth login --dry-run`: not applicable, justified in its entry |
| Side Effects And Telemetry | `telemetry` block: none, no update checks; reads declare `writes: []`; `delete --dry-run` declares its single read; network only to `api_url` |
| Prose Surfaces | every `summary` is rules-then-context and task-selective (e.g. `search` says "when the id is unknown", `delete` says "no confirmation prompt exists") |
| Tests | §6 |

## 8. Assumptions to confirm with the API owner

- The remote API supports server-side idempotency keys, opaque cursor pagination with a ~10 minute lifetime, full-text search with deterministic tie-breaking, and `notes:read` / `notes:write` scopes; if any is missing, the corresponding catalog entries (`CONFLICT`, `CURSOR_EXPIRED`, `retryable_with`) must change and the fingerprint with them.
- Notes carry exactly `id`, `title`, `body`, `tags`; because there is no timestamp field, `--sort` offers only `id|title`. Adding `updated_at` later is an additive change.
- The fingerprint value `nct-7f3a9c21` and the id pattern are placeholders for the implementation to compute and confirm.
- No bulk operations are in scope; if `delete --from-file` or bulk create is added later, follow the `widgetctl` bulk-result shape in the skill's `examples.md` (NDJSON per item plus a `summary` completion record, `PARTIAL_FAILURE` at a declared exit code, `--allow-partial`).
