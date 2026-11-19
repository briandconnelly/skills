# Scenario S1 — with-skill arm 1 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 3784
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S1-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 Canonical machine profile, every implied flag declared
- o3 PASS: `"canonical_machine_profile": ["--machine"]`; implies `--json`, `--no-progress`, `--no-color`, and all three are in `global_flags`.
### A2 Numeric exit codes, symbolic codes, and a per-command catalog for the mutating command
- o3 PASS: `exit_codes` 0–10, `symbolic_error_codes`, and `errors_possible` on create and delete.
### A3 stdout carries the success payload only; failures go to stderr with declared framing
- o3 PASS: `"stderr_framing": "ndjson-typed"`; heading reads "Example error payloads (stderr, stdout empty)".
### A4 delete has an explicit trigger and `--dry-run` whose output includes `dry_run: true`
- o3 PASS: explicit `delete <id>` verb; the `--dry-run` alternate shape is `{"dry_run": true, ...}`.
### A5 List/search pagination declares `has_more` and a token
- o3 PASS: list and search both declare `has_more` and `next_cursor?`.
### A6 Export returns a pointer with path, size, and hash
- o3 PASS: `path`, `byte_size`, `content_hash` (sha256).
### A7 Duration flags declare units
- o3 PASS: every duration flag is `--timeout-ms` with `"unit": "ms"`.
### A8 Ambient state is declared with inspection and isolation affordances
- o3 PASS: `ambient_state` covers credentials, config, and cache; it has `inspect_with` and `disable_with` (`--isolated`).
### A9 Canonical examples that use `--` put options before it and operands after
- o3 PASS: the only example that uses `--` is `notectl note delete --if-exists --machine -- "-weird-id"`.
### A10 Fallback code / non-timeout transport code on each networked command / unknown-code policy
- o3 PASS.
  - Fallback: pass, `"fallback_error_code": "INTERNAL"`.
  - Transport code: pass. `NETWORK_ERROR` appears in list, get, search, create, delete, and export.
    Caveat: the `auth whoami` entry, which is networked, is omitted with "same per-command shape", so its catalog could not be checked.
  - Unknown-code policy: pass, `unknown_code_policy` is present.
### A11 Multi-value flags declare how values are passed
- o3 PASS: `--tag` and `--select` declare `"multi_value_syntax": "repeat"` on every command that has them.
### C1 Export is the only `--output <file>` command
- o3 PASS, o73 PASS, o1 PASS: `--output` appears only on `note export`.
### C2 Each command declares one output class, and any flag that switches the class declares the switch
- o3 PASS: every command shown declares a class, and `--dry-run` is declared in `alternate_outputs`.
  Caveat: the schema, auth, and config entries are omitted from the output, so they could not be checked.

## Verbatim final output

~~~~~~~~markdown
# `notectl` agent-facing CLI contract

## Assumptions

- The remote notes API exposes list (cursor-paginated), get, full-text search, create, and delete, authenticated with a bearer token.
- The API accepts an `Idempotency-Key` header on create, with a deduplication window of 24 hours.
  If it does not, `note create` must be declared not safe to retry automatically (see § Mutations).
- Export is a client-side page walk written to a local file; it is a foreground command, not a server-side async job.
- Audience: tool author.
  Task: new design.

## 1. Task model

| Agent job | Class | Minimum input | Minimum output for the next step |
|---|---|---|---|
| List notes | query | none (optional `--tag`, `--limit`, `--cursor`) | `id`, `title`, `tags`, `updated_at`; `has_more`, `next_cursor` |
| Get a note | inspect | `id` | full record |
| Search notes | query | query string | `id`, `title`, `tags`, `snippet`, `score`; paging |
| Create a note | mutate | `--title`, body (flag, file, or stdin) | full record with new `id` |
| Delete a note | mutate | `id` | `id`, `status` |
| Export all notes | query (artifact) | `--output` path | `path`, `byte_size`, `content_hash`, `note_count` |
| Discover contract | discover | none | schema / fingerprint |
| Inspect ambient state | admin | none | resolved config, credential source, identity |

`list` and `search` are separate because they differ in one fact an agent can select on without prose: `search` takes a query and returns relevance-ranked results with a `snippet`; `list` enumerates in a deterministic order with filters only.

## 2. Command surface

Pattern: `notectl <noun> <verb>`.
Primary selector for notes: the note ID as the single positional argument.
`--` end-of-options is supported everywhere.

```
notectl note list    [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--sort updated_at|-updated_at|title] [--timeout-ms <ms>]
notectl note get     <id> [--select <field>]... [--timeout-ms <ms>]
notectl note search  --query <text> [--tag <tag>]... [--limit <n>] [--cursor <c>] [--select <field>]... [--timeout-ms <ms>]
notectl note create  --title <text> (--body <text> | --body-file <path|->) [--tag <tag>]... [--idempotency-key <key>] [--dry-run] [--timeout-ms <ms>]
notectl note delete  <id> [--if-exists] [--dry-run] [--timeout-ms <ms>]
notectl note export  --output <path> [--format json|ndjson] [--overwrite] [--timeout-ms <ms>]

notectl schema [<command>] [--fingerprint] [--summary]
notectl auth whoami [--timeout-ms <ms>]
notectl auth status
notectl config show --resolved

Global: --machine  --json  --no-progress  --no-color  --isolated  --no-config  --profile <name>  --api-url <url>
```

Canonical examples (values that may contain spaces are quoted; options precede `--`):

```sh
notectl note search --query "quarterly review" --tag work --limit 20 --machine
printf '%s' "$BODY" | notectl note create --title "Standup 2026-11-18" --body-file - --tag meetings --idempotency-key "c7f2e0d1-4b8a-4e7a-9d1e-2a6f3c5b9e10" --machine
notectl note delete --if-exists --machine -- "-weird-id"
notectl note export --output "./notes-export.ndjson" --format ndjson --machine
```

Prose surfaces (help and `description` fields) are written rules-first, for example `note search`: "Requires --query. Returns notes ranked by relevance (score desc, then id). Use `note list` to enumerate without a query."

## 3. Machine schema (`notectl schema --machine`)

Shape dialect `notectl-compact-v1`: `a|b` is a closed enum, a trailing `?` marks an optional field, fields are required unless so marked or removed by a declared projection, `[T]` is an array of `T`, and a string-valued shape describes a record sequence.

```json
{
  "schema_version": "1.0",
  "fingerprint": "ntc-5e8f19a2",
  "fingerprint_scope": "schema-contract",
  "fingerprint_inputs": "canonical JSON of this schema excluding the fingerprint field; tool version is not an input",
  "compatibility": {
    "additive": ["new commands", "new optional fields in output", "new optional flags", "new symbolic error codes in a command catalog"],
    "breaking": ["command or flag removal or rename", "field removal or rename", "type or meaning change", "exit-code remapping", "required-field addition to input"],
    "rule": "any contract change changes the fingerprint; breaking changes bump the major component of schema_version"
  },
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "notectl-compact-v1",
  "shape_dialect_description": "a|b is a closed enum; trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; [T] is an array of T; a string-valued shape describes a record sequence",
  "end_of_options_supported": true,
  "stderr_framing": "ndjson-typed",
  "stderr_framing_description": "in machine mode every stderr line is one JSON object with type progress|warning|error; at most one error record, always last; free-form text is never written",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress", "--no-color"], "description": "Non-interactive: never prompts, never opens a pager or browser, structured output only on every stream regardless of TTY. --no-progress here suppresses human spinners only; declared progress records on export are still emitted."},
    {"name": "--json", "type": "boolean", "default": false, "description": "Structured JSON on stdout."},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "Suppress human progress rendering on stderr."},
    {"name": "--no-color", "type": "boolean", "default": false, "description": "Disable ANSI color."},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "Ignore config files and the local cache. Credentials are still read from NOTECTL_TOKEN only (credential file and keychain ignored)."},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "Ignore config files only."},
    {"name": "--profile", "type": "string", "default": "default", "description": "Config profile to resolve. Overrides NOTECTL_PROFILE."},
    {"name": "--api-url", "type": "url", "default": "https://api.notes.example.com", "description": "API base URL. Overrides NOTECTL_API_URL and config."}
  ],
  "ambient_state": {
    "credentials": {"sources_in_precedence": ["NOTECTL_TOKEN env var", "OS keychain entry notectl/<profile>", "~/.config/notectl/credentials (mode 0600)"], "secret": true, "redaction": "shown as source plus last 4 characters, e.g. \"****a1b2\""},
    "config_files": ["$XDG_CONFIG_HOME/notectl/config.toml (default ~/.config/notectl/config.toml)"],
    "environment": ["NOTECTL_TOKEN", "NOTECTL_PROFILE", "NOTECTL_API_URL", "NOTECTL_TIMEOUT_MS", "NO_COLOR"],
    "cache": {"path": "$XDG_CACHE_HOME/notectl/", "contents": "schema fingerprint only; note data is never cached", "reads": true, "writes": "only by `notectl schema`; atomic rename"},
    "cwd_selects_context": false,
    "precedence": "flags > env vars > config file > cache",
    "disable_with": {"all": "--isolated", "config_only": "--no-config"},
    "inspect_with": ["notectl config show --resolved", "notectl auth status", "notectl auth whoami"],
    "non_interactive_bootstrap": "set NOTECTL_TOKEN, or pipe a token to `notectl auth login --token-stdin`; interactive browser login is never started in machine mode",
    "secret_intake": "tokens are accepted only via env, keychain, credential file, or stdin; no --token flag exists"
  },
  "telemetry": {"default": "off", "update_checks": "off", "machine_mode": "always suppressed"},
  "exit_codes": {"0": "success", "1": "generic (INTERNAL)", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, including transport failures other than timeout", "10": "local output file error (export)"},
  "symbolic_error_codes": ["INTERNAL", "VALIDATION_ERROR", "CURSOR_EXPIRED", "NOTE_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "IDEMPOTENCY_CONFLICT", "OUTPUT_EXISTS", "NETWORK_ERROR", "TRANSIENT", "OUTPUT_WRITE_FAILED", "INPUT_TOO_LARGE"],
  "fallback_error_code": "INTERNAL",
  "unknown_code_policy": "act on payload fields (temporary, reconcile_first); on mutating commands reconcile before any retry",
  "error_shape": {"type": "error", "code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "reconcile_first?": "boolean", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "path?": "string", "docs_url?": "string"},
  "debug": {"flag": "--debug", "description": "opt-in; writes type=warning records with request/response metadata; Authorization headers and tokens redacted"},
  "note_shape": {"id": "string", "title": "string", "body": "string", "tags": "[string]", "created_at": "string (RFC 3339, UTC)", "updated_at": "string (RFC 3339, UTC)"},
  "command_tree": {
    "schema": "notectl schema [<command>] [--fingerprint] [--summary]",
    "auth": {"whoami": "notectl auth whoami", "status": "notectl auth status", "login": "notectl auth login --token-stdin"},
    "config": {"show": "notectl config show --resolved"},
    "note": {
      "list": "notectl note list",
      "get": "notectl note get <id>",
      "search": "notectl note search --query <text>",
      "create": "notectl note create --title <text> (--body <text> | --body-file <path|->)",
      "delete": "notectl note delete <id>",
      "export": "notectl note export --output <path>"
    }
  },
  "commands": [
    {
      "canonical_invocation_path": "notectl note list",
      "description": "Enumerate notes in a deterministic order, filtered by tag. No query; use note search for text matching.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "AND", "default": []},
        {"name": "--limit", "type": "integer", "min": 1, "max": 200, "default": 50},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--sort", "type": "enum", "enum": ["updated_at", "-updated_at", "title"], "default": "-updated_at", "tiebreak": "id ascending"},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "created_at", "updated_at", "body"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false, "size_mode": "paged; at most --limit items",
        "shape": {"items": "[{id, title, tags, updated_at} per --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "truncation": "body is excluded by default; when selected it is returned in full",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort; notes changed during a walk may be skipped or repeated"}
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"], "backoff": "honor retry_after_ms, else exponential from 250ms"},
      "signal_semantics": {"interrupt": "exits without output; no state", "closed_stdout": "exits 0 quietly"},
      "async": false, "pagination": true, "artifact": false,
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
      "description": "Return one note by ID, including body. Requires the exact ID; use note search or note list to find it.",
      "aliases": [], "deprecations": [],
      "classification": "inspect", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HZX3"]}],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "title", "body", "tags", "created_at", "updated_at"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "body", "tags", "created_at", "updated_at"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "size_mode": "small; body up to 1 MiB", "shape": "note_shape", "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"}, "truncation": "none"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "exits without output; no state", "closed_stdout": "exits 0 quietly"},
      "async": false, "pagination": false, "artifact": false,
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
      "description": "Requires --query. Full-text match over title and body, ranked by score desc then id asc; returns a snippet, not the body. Use note get for the full note.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--query", "type": "string", "required": true, "max_length": 512, "examples": ["\"quarterly review\""]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "semantics": "AND", "default": []},
        {"name": "--limit", "type": "integer", "min": 1, "max": 100, "default": 20},
        {"name": "--cursor", "type": "string", "default": null},
        {"name": "--select", "type": "enum", "enum": ["id", "title", "tags", "updated_at", "snippet", "score"], "cardinality": "many", "multi_value_syntax": "repeat", "default": ["id", "title", "tags", "snippet", "score"]},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {
        "class": "list", "format": "json", "streaming": false, "size_mode": "paged; at most --limit items",
        "shape": {"items": "[{id, title, tags, snippet, score} per --select]", "has_more": "boolean", "next_cursor?": "string", "limit": "integer", "estimated_total?": "integer"},
        "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null; id is always present"},
        "truncation": "snippet is at most 200 characters, marked by snippet_truncated: true when cut",
        "cursor": {"opacity": "opaque", "lifetime": "15 minutes", "expired_error": "CURSOR_EXPIRED", "restart_action": "re-run without --cursor", "consistency": "best-effort"},
        "empty_result": "items: [] with has_more: false and exit 0; not an error"
      },
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 2, "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "signal_semantics": {"interrupt": "exits without output; no state", "closed_stdout": "exits 0 quietly"},
      "async": false, "pagination": true, "artifact": false,
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
      "canonical_invocation_path": "notectl note create --title <text> --body-file <path|->",
      "description": "Creates one note. Requires --title and exactly one of --body or --body-file. Pass --idempotency-key on every attempt so a retry after an unknown outcome cannot create a duplicate.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [],
      "flags": [
        {"name": "--title", "type": "string", "required": true, "max_length": 200},
        {"name": "--body", "type": "string", "default": null, "mutually_exclusive_with": ["--body-file"]},
        {"name": "--body-file", "type": "path", "default": null, "description": "UTF-8 text; '-' reads stdin", "mutually_exclusive_with": ["--body"]},
        {"name": "--tag", "type": "string", "cardinality": "many", "multi_value_syntax": "repeat", "pattern": "^[a-z0-9][a-z0-9_-]{0,31}$", "default": []},
        {"name": "--idempotency-key", "type": "string", "default": null, "description": "Caller-generated, 8-128 chars; reuse the same key on every retry of one logical create; deduplicated by the API for 24 hours"},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": true, "auto_detected_when_piped": false, "explicit_flag": "--body-file -", "accepted_formats": ["text/plain; charset=utf-8"], "maximum_input_size": "1 MiB (INPUT_TOO_LARGE above)", "can_block": "only when --body-file - is given and the writer has not closed stdin; never reads a TTY in machine mode (VALIDATION_ERROR instead)", "mutually_exclusive_with": ["--body"], "empty_stdin": "accepted as an empty body"},
      "output": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"id": "string", "title": "string", "tags": "[string]", "created_at": "string", "updated_at": "string", "body_bytes": "integer", "replayed": "boolean"}, "shape_description": "body is not echoed; body_bytes reports its size; replayed is true when the API returned the note from an earlier attempt with the same idempotency key"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "create", "title": "string", "tags": "[string]", "body_bytes": "integer"}, "shape_description": "validates input locally and checks auth/scope with a read-only API call; no note is created"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation; may refresh the auth token, which --isolated suppresses"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown. With --idempotency-key, retrying with the same key is safe within 24 hours. Without a key, do not retry automatically: an empty note list or search does not prove the create did not commit, and a key added only on the retry does not deduplicate the first attempt.",
      "safe_to_retry_automatically": "only with the same --idempotency-key",
      "signal_semantics": {"interrupt": "the remote create may still commit", "closed_stdout": "finishes the in-flight create", "local_writes": "none", "remote_continues": true},
      "async": false, "pagination": false, "artifact": false,
      "errors_possible": [
        {"code": "INTERNAL", "exit": 1},
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "INPUT_TOO_LARGE", "exit": 2},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
        {"code": "IDEMPOTENCY_CONFLICT", "exit": 8, "description": "same key reused with different title, body, or tags"},
        {"code": "NETWORK_ERROR", "exit": 9, "retryable": false, "reconcile_first": true},
        {"code": "TRANSIENT", "exit": 9, "retryable": false, "reconcile_first": true}
      ]
    },
    {
      "canonical_invocation_path": "notectl note delete <id>",
      "description": "Permanently deletes one note by ID. Fails with NOTE_NOT_FOUND unless --if-exists. Repeat-safe with --if-exists.",
      "aliases": [], "deprecations": [],
      "classification": "mutate", "read_only": false,
      "auth": "required", "scope": "notes:write",
      "arguments": [{"name": "id", "type": "string", "cardinality": "one", "examples": ["note_01HZX3"]}],
      "flags": [
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"id": "string", "status": "deleted|absent"}, "shape_description": "status is absent when --if-exists suppressed NOTE_NOT_FOUND"},
      "alternate_outputs": {
        "--dry-run": {"class": "record", "format": "json", "streaming": false, "size_mode": "small", "shape": {"dry_run": true, "planned_action": "delete|none", "id": "string"}, "shape_description": "performs a read-only get; planned_action is none when --if-exists would suppress NOTE_NOT_FOUND"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote note store"], "dry_run": "no externally visible mutation"},
      "latency_class": "network", "timeout_defaults_ms": 10000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on TIMEOUT, NETWORK_ERROR, TRANSIENT, or interrupt the outcome is unknown; delete is repeat-safe with --if-exists, so re-run with --if-exists",
      "safe_to_retry_automatically": "only with --if-exists",
      "signal_semantics": {"interrupt": "the remote delete may still commit", "closed_stdout": "finishes the in-flight delete", "local_writes": "none", "remote_continues": true},
      "async": false, "pagination": false, "artifact": false,
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
      "description": "Requires --output. Writes every note (full records) to a local file and prints a pointer, not the notes. Fails if the file exists unless --overwrite.",
      "aliases": [], "deprecations": [],
      "classification": "query", "read_only": true,
      "auth": "required", "scope": "notes:read",
      "arguments": [],
      "flags": [
        {"name": "--output", "type": "path", "required": true},
        {"name": "--format", "type": "enum", "enum": ["json", "ndjson"], "default": "ndjson", "description": "file format; json is one array, ndjson is one note per line"},
        {"name": "--overwrite", "type": "boolean", "default": false},
        {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 300000, "description": "deadline for the whole export"}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "artifact", "format": "json", "streaming": false, "size_mode": "small pointer; file size grows with note count", "shape": {"path": "string (absolute, POSIX separators)", "format": "json|ndjson", "byte_size": "integer", "content_hash": "string (sha256:<hex>)", "note_count": "integer"}, "file_order": "id ascending"},
      "progress": {"stream": "stderr", "record": {"type": "progress", "notes_written": "integer", "estimated_total?": "integer"}, "interval": "every 500 notes or 2 s"},
      "side_effects": {"external_mutation": false, "writes": ["the --output file only"], "local_write_atomicity": "writes <path>.notectl-tmp-<pid> then renames over <path>; concurrent exports to the same path are last-writer-wins and never interleave"},
      "latency_class": "slow", "timeout_defaults_ms": 300000,
      "retry_defaults": {"retries": 2, "per": "page request", "on": ["RATE_LIMITED", "TRANSIENT", "NETWORK_ERROR"]},
      "consistency": "best-effort page walk; notes changed during export may be missing or stale",
      "signal_semantics": {"interrupt": "temp file removed; --output untouched", "closed_stdout": "finishes the export", "local_writes": "atomic rename", "remote_continues": false},
      "async": false, "pagination": false, "artifact": true,
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
        {"code": "OUTPUT_WRITE_FAILED", "exit": 10}
      ]
    }
  ]
}
```

`notectl schema note create` returns that one command entry plus the tool-level `exit_codes`, `error_shape`, and `shape_dialect`.
`schema`, `schema --fingerprint`, `--help`, `auth status`, and `config show --resolved` are `local` latency, make no network call, and target under 100 ms (no auth validation, lazy-imported HTTP client).
Their entries follow the same per-command shape and are omitted here; `auth whoami` is `network`.

## 4. Example success payloads (stdout, exit 0)

`notectl schema --fingerprint --machine`

```json
{"schema_version":"1.0","fingerprint":"ntc-5e8f19a2","fingerprint_scope":"schema-contract"}
```

`notectl note list --tag work --limit 2 --machine`

```json
{"items":[{"id":"note_01HZX3","title":"Q4 planning","tags":["work","planning"],"updated_at":"2026-11-17T21:04:11Z"},{"id":"note_01HZW9","title":"Vendor call","tags":["work"],"updated_at":"2026-11-16T15:30:00Z"}],"has_more":true,"next_cursor":"c2:eyJvIjoyfQ","limit":2,"estimated_total":37}
```

`notectl note get note_01HZX3 --machine`

```json
{"id":"note_01HZX3","title":"Q4 planning","body":"Goals:\n- ship export\n- cut p95 latency","tags":["work","planning"],"created_at":"2026-11-10T09:00:00Z","updated_at":"2026-11-17T21:04:11Z"}
```

`notectl note search --query "export" --machine`

```json
{"items":[{"id":"note_01HZX3","title":"Q4 planning","tags":["work","planning"],"snippet":"Goals:\n- ship export\n- cut p95","score":0.91}],"has_more":false,"limit":20}
```

`notectl note create --title "Standup 2026-11-18" --body-file - --tag meetings --idempotency-key "c7f2e0d1-4b8a-4e7a-9d1e-2a6f3c5b9e10" --machine`

```json
{"id":"note_01J0AB","title":"Standup 2026-11-18","tags":["meetings"],"created_at":"2026-11-18T16:02:45Z","updated_at":"2026-11-18T16:02:45Z","body_bytes":142,"replayed":false}
```

`notectl note create ... --dry-run --machine`

```json
{"dry_run":true,"planned_action":"create","title":"Standup 2026-11-18","tags":["meetings"],"body_bytes":142}
```

`notectl note delete note_01HZW9 --machine`

```json
{"id":"note_01HZW9","status":"deleted"}
```

`notectl note delete note_01HZW9 --if-exists --machine` (already gone)

```json
{"id":"note_01HZW9","status":"absent"}
```

`notectl note export --output ./notes-export.ndjson --machine`

```json
{"path":"/home/agent/work/notes-export.ndjson","format":"ndjson","byte_size":48213,"content_hash":"sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08","note_count":37}
```

Export stderr during the run (`ndjson-typed`, not an error):

```ndjson
{"type":"progress","notes_written":500,"estimated_total":1200}
```

## 5. Example error payloads (stderr, stdout empty)

Under `ndjson-typed` framing the error record is the last stderr line.

Not found — `notectl note get note_404 --machine`, exit `3`:

```json
{"type":"error","code":"NOTE_NOT_FOUND","message":"Note not found.","resource_id":"note_404","hint":"Find the ID with note search --query or note list.","temporary":false,"request_id":"req_7b1e"}
```

Validation — `notectl note create --title "x" --body "a" --body-file b.txt --machine`, exit `2`:

```json
{"type":"error","code":"VALIDATION_ERROR","message":"--body and --body-file are mutually exclusive.","field":"--body-file","details":{"mutually_exclusive_with":["--body"]},"hint":"Keep --title and pass only one of --body or --body-file.","temporary":false}
```

Rate limited — any networked command, exit `6`:

```json
{"type":"error","code":"RATE_LIMITED","message":"Rate limit exceeded.","retry_after_ms":30000,"temporary":true,"request_id":"req_91ac"}
```

Unknown outcome on a mutation — `notectl note create ... --idempotency-key "c7f2..." --machine`, exit `7`:

```json
{"type":"error","code":"TIMEOUT","message":"Request timed out after 10000 ms; the note may have been created.","temporary":false,"reconcile_first":true,"details":{"timeout_ms":10000,"idempotency_key":"c7f2e0d1-4b8a-4e7a-9d1e-2a6f3c5b9e10"},"hint":"Retry with the same --idempotency-key value.","request_id":"req_c03d"}
```

Unauthenticated — exit `4`:

```json
{"type":"error","code":"UNAUTHENTICATED","message":"No credentials found.","details":{"sources_checked":["NOTECTL_TOKEN","keychain:notectl/default","~/.config/notectl/credentials"]},"hint":"Set NOTECTL_TOKEN or run auth login --token-stdin.","temporary":false}
```

## 6. Checklist coverage

| Checklist section | Answer in the contract |
|---|---|
| Command Model | `note <verb>`; one positional selector (ID); conventional flags (`--limit`, `--timeout-ms`, `--output`, `--format`); no aliases yet. |
| Machine Schema | All items declared above, including shape dialect, units, fingerprint scope, compatibility, per-command error catalogs, `schema <command>`. |
| Stdin Contract | Declared per command; only `note create --body-file -` reads stdin, explicitly. |
| Shell Safety | `--` supported and declared; values never passed to a shell; examples quoted; hints contain flag values, not shell strings built from input. |
| Agent-Safe Invocation | `--machine` profile; `--isolated` distinct; per-stream TTY detection; non-interactive bootstrap via env or `--token-stdin`; `<100ms` metadata paths; `--timeout-ms` on every networked command. |
| Output | stdout success only; `ndjson-typed` stderr; one class per command; projection rule; cursor contract; deterministic sorts; UTC RFC 3339; `--output` only on export with path, size, hash; closed-stdout behavior declared. |
| Errors And Exit Codes | Exit map 0–10; required `code`/`message`/`temporary`; `INTERNAL` fallback; `NETWORK_ERROR` transport code; unknown-code policy; redacted opt-in `--debug`. Partial failure: N/A — no multi-item mutating command; export fails as a whole. |
| Ambient State | Credential/config/env/cache sources, precedence, disable, inspection (`config show --resolved`, `auth status`, `auth whoami`), redaction; no secret flags. |
| Mutations And Long-Running Work | Explicit verbs; `--dry-run` on create and delete; idempotency key on create, `--if-exists` on delete; reconciliation and signal semantics declared; export writes atomically. Async jobs: N/A — export is foreground with deadline, progress framing, and interrupt behavior declared. |
| Side Effects And Telemetry | Reads have no writes except export's declared file and `schema`'s fingerprint cache; telemetry and update checks off. |
| Prose Surfaces | Descriptions rules-first and say how to choose between siblings (`list` vs `search`, `search` vs `get`). |
| Tests | See below. |

## 7. Contract tests to ship

- Snapshot of `notectl schema` and `schema --fingerprint`; fingerprint changes when the schema changes.
- Golden success payloads above per command, and the error payloads with their exit codes, run against a mock API.
- Runtime check that each catalog code produces its declared exit code.
- TTY vs non-TTY per stream; `--machine` emits no prompts, color, spinners, or prose on either stream.
- `--body-file -` with empty, oversized (`INPUT_TOO_LARGE`), and TTY stdin.
- Pagination, `CURSOR_EXPIRED`, `--select` projection, snippet truncation, export artifact hash matches the file.
- Precedence flags > env > config; `--isolated` and `--no-config`.
- `--dry-run` on create and delete makes no API write and output differs from real output.
- Interrupt during create/delete/export (temp file removed; output untouched); concurrent exports to one path.
- Idempotency replay returns `replayed: true` and the same `id`; key reuse with a different body returns `IDEMPOTENCY_CONFLICT`.
- Metadata paths complete under 100 ms with the network disabled.
~~~~~~~~
