# Probe P3 — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 61,021 (final-turn context plus output, read from the transcript)
- **Output words:** 356
- **Transcript sha256:** `1b83fd4d248ee901aa952fdde38ecf91cb96024bb546e9881e923732730ca908` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Here is the schema for `widgetctl`.
> Write the output of `widgetctl --help`.
>
> ```json
> {
>   "schema_version": "1.0",
>   "fingerprint": "wgt-a1b2c3d4",
>   "fingerprint_scope": "schema-contract",
>   "canonical_machine_profile": ["--machine"],
>   "isolation_profile": ["--isolated"],
>   "shape_dialect": "widgetctl-compact-v1",
>   "shape_dialect_description": "a|b is a closed enum; a trailing ? marks an optional field; fields are required unless so marked or removed by a declared projection; a string-valued shape describes a record sequence",
>   "global_flags": [
>     {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress"], "description": "non-interactive machine mode: no prompts, no color, no pager, structured output only"},
>     {"name": "--json", "type": "boolean", "default": false, "description": "structured JSON output"},
>     {"name": "--no-progress", "type": "boolean", "default": false, "description": "suppress progress output on stderr"},
>     {"name": "--isolated", "type": "boolean", "default": false, "description": "ignore ambient config, credentials, and caches"},
>     {"name": "--no-config", "type": "boolean", "default": false, "description": "ignore config files only"}
>   ],
>   "stderr_framing": "single-error-object",
>   "stderr_framing_description": "on failure in machine mode, the structured error object is the only stderr content",
>   "end_of_options_supported": true,
>   "command_tree": {
>     "widget": {
>       "get": "widgetctl widget get <id>",
>       "delete": "widgetctl widget delete <id>"
>     }
>   },
>   "exit_codes": {"0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified", "10": "partial failure (domain-specific)"},
>   "symbolic_error_codes": ["VALIDATION_ERROR", "CURSOR_EXPIRED", "WIDGET_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSIENT", "PARTIAL_FAILURE"],
>   "error_shape": {"code": "string", "message": "string", "temporary": "boolean", "hint?": "string", "retry_after_ms?": "integer", "details?": "object", "field?": "string", "resource_id?": "string", "conflict_with?": "string", "request_id?": "string", "docs_url?": "string", "path?": "string"},
>   "auth": "required",
>   "environment": ["WIDGETCTL_TOKEN"],
>   "config": {"reads": true, "disable_with": "--no-config"},
>   "cache": {"reads": true, "writes": false},
>   "credential_requirements": ["token"],
>   "commands": [
>     {
>       "canonical_invocation_path": "widgetctl widget get <id>",
>       "aliases": [],
>       "deprecations": [],
>       "classification": "inspect",
>       "read_only": true,
>       "arguments": [
>         {"name": "id", "type": "string", "cardinality": "one", "examples": ["wgt_123"]}
>       ],
>       "flags": [
>         {"name": "--select", "type": "enum", "enum": ["id", "name", "status"], "cardinality": "many", "default": ["id", "name", "status"]},
>         {"name": "--timeout", "type": "integer", "unit": "ms", "default": 3000}
>       ],
>       "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
>       "output": {"class": "record", "format": "json", "shape": {"id": "string", "name": "string", "status": "active|inactive|deleted"}, "projection": {"flag": "--select", "rule": "only selected fields are present; unselected fields are absent, not null"}, "size_mode": "small"},
>       "side_effects": {"external_mutation": false, "writes": []},
>       "latency_class": "network",
>       "timeout_defaults_ms": 3000,
>       "retry_defaults": {"retries": 0},
>       "async": false,
>       "streaming": false,
>       "pagination": false,
>       "truncation": false,
>       "artifact": false,
>       "errors_possible": [
>         {"code": "VALIDATION_ERROR", "exit": 2},
>         {"code": "WIDGET_NOT_FOUND", "exit": 3},
>         {"code": "UNAUTHENTICATED", "exit": 4},
>         {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
>         {"code": "TIMEOUT", "exit": 7, "retryable": true}
>       ]
>     },
>     {
>       "canonical_invocation_path": "widgetctl widget delete <id>",
>       "aliases": [],
>       "deprecations": [],
>       "classification": "mutate",
>       "read_only": false,
>       "arguments": [
>         {"name": "id", "type": "string", "cardinality": "one", "required_unless": "--from-file", "examples": ["wgt_123"]}
>       ],
>       "flags": [
>         {"name": "--dry-run", "type": "boolean", "default": false},
>         {"name": "--if-exists", "type": "boolean", "default": false},
>         {"name": "--from-file", "type": "path", "default": null, "switches_output_class": "bulk-result"},
>         {"name": "--allow-partial", "type": "boolean", "default": false, "requires": "--from-file"},
>         {"name": "--timeout", "type": "integer", "unit": "ms", "default": 5000}
>       ],
>       "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
>       "output": {"class": "record", "format": "json", "shape": {"id": "string", "name": "string", "status": "deleted"}, "size_mode": "small"},
>       "alternate_outputs": {
>         "--from-file": {"class": "bulk-result", "format": "ndjson", "shape": "one record per item: {id, name, status} or {id, error: {code, message, temporary}}; then one trailer record {type: \"summary\", partial: boolean, succeeded: integer, failed: integer}", "streaming": true, "completion_record": "summary", "size_mode": "grows with input"},
>         "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete", "id": "string"}, "streaming": false, "size_mode": "small"},
>         "--from-file --dry-run": {"class": "bulk-result", "format": "ndjson", "shape": "one record per item: {dry_run: true, id, planned_action} or {dry_run: true, id, error: {code, message, temporary}}; then one trailer record {type: \"summary\", dry_run: true, partial: boolean, succeeded: integer, failed: integer}", "streaming": true, "completion_record": "summary", "size_mode": "grows with input"}
>       },
>       "side_effects": {"external_mutation": true, "writes": ["remote widget store"], "description": "deletes the widget unless --dry-run is true", "dry_run": "no externally visible mutations; output includes \"dry_run\": true and the planned effect"},
>       "latency_class": "network",
>       "timeout_defaults_ms": 5000,
>       "retry_defaults": {"retries": 0},
>       "reconciliation": "on timeout or interrupt the outcome is unknown; run widgetctl widget get <id>: WIDGET_NOT_FOUND means the delete committed, and --if-exists makes a retry safe",
>       "async": false,
>       "streaming": false,
>       "pagination": false,
>       "truncation": false,
>       "artifact": false,
>       "errors_possible": [
>         {"code": "VALIDATION_ERROR", "exit": 2},
>         {"code": "WIDGET_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
>         {"code": "UNAUTHENTICATED", "exit": 4},
>         {"code": "FORBIDDEN", "exit": 5},
>         {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
>         {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true},
>         {"code": "PARTIAL_FAILURE", "exit": 10, "retryable": false, "requires": "--from-file", "suppressed_by": "--allow-partial"}
>       ]
>     }
>   ]
> }
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P3-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** the help text names the schema command and the machine flag. | **FAIL** | Names "always pass --machine" but notes "I did not reference a `widgetctl schema` command" Parts: names the schema command = fail; names the machine flag = pass |

## Verbatim final output

~~~~~~markdown
# `widgetctl --help`

```text
widgetctl - inspect and delete widgets in the remote widget store

USAGE
  widgetctl [GLOBAL FLAGS] <noun> <verb> [FLAGS] [--] <args>

REQUIREMENTS
  Auth required: set WIDGETCTL_TOKEN (token). Do not pass tokens as flags.
  Agents: always pass --machine (implies --json --no-progress; no prompts,
  no color, no pager, structured output only).
  Use -- before operands that may begin with "-".

COMMANDS
  widget get <id>       Read one widget (id, name, status). Read-only.
  widget delete <id>    Delete one widget, or many with --from-file. MUTATES
                        the remote widget store; use --dry-run to preview.

GLOBAL FLAGS
  --machine       Canonical machine profile. Implies --json, --no-progress.
                  Default: false.
  --json          Structured JSON output. Default: false.
  --no-progress   Suppress progress output on stderr. Default: false.
  --isolated      Ignore ambient config, credentials, and caches. Default: false.
                  Note: auth is required, so supply credentials explicitly.
  --no-config     Ignore config files only. Default: false.

OUTPUT
  stdout: success payload only.
  stderr (machine mode): on failure, one structured error object and nothing
  else: {code, message, temporary, hint?, retry_after_ms?, details?, field?,
  resource_id?, conflict_with?, request_id?, docs_url?, path?}.
  Branch on "code", not "message". Retry only when "temporary" is true.

EXIT CODES
  0 success            4 unauthenticated    8 conflict
  1 generic            5 forbidden          9 transient
  2 usage/validation   6 rate limited      10 partial failure
  3 not found          7 timeout

AMBIENT STATE
  Reads: WIDGETCTL_TOKEN, config files (disable: --no-config),
  caches (read-only; disable all with --isolated).

Run 'widgetctl widget <verb> --help' for per-command flags, output shapes,
and errors. Schema version 1.0, fingerprint wgt-a1b2c3d4 (schema-contract).
```

## Notes

- Rules-then-context ordering per the skill's Prose Surfaces rule: auth, machine profile, and `--` come before the command list.
- Summaries are task-selective: the read-only vs mutating split is what separates the two siblings.
- I did not reference a `widgetctl schema` command, because the schema declares none; if one exists, add it to COMMANDS so agents can fetch the contract.
- Schema gaps surfaced while writing (not fixable in help text): `--timeout` declares its unit via a `unit` field but the conventional name is `--timeout-ms`; no command `description`/summary fields exist, so the summaries above are derived from classification and side effects; no resolved-config or credential-source inspection command; no signal semantics declared for `delete`.
~~~~~~
