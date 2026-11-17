# Probe P3 — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 62,905 (final-turn context plus output, read from the transcript)
- **Output words:** 694
- **Transcript sha256:** `bbb7bdcad3c5082b16c99740f3b101520110e57f8df325f5fa8689bb5e1123d3` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P3-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** the help text names the schema command and the machine flag. | **FAIL** | Names "pass --machine" but no schema command; notes: "No schema/fingerprint command appears in `command_tree`" Parts: names the schema command = fail; names the machine flag = pass |

## Verbatim final output

~~~~~~markdown
```text
widgetctl - inspect and delete widgets in the remote widget store

USAGE
  widgetctl [GLOBAL FLAGS] widget <command> [FLAGS] [--] <id>

REQUIREMENTS
  Auth required: set WIDGETCTL_TOKEN. Tokens are never accepted as flags.
  Agents and scripts: pass --machine (implies --json --no-progress; no prompts,
  color, or pager). On failure in machine mode, stderr holds exactly one JSON
  error object and stdout is empty.
  Branch on the error's "code", never its "message". Retry only when
  "temporary" is true; honor "retry_after_ms" when present.
  Use -- before an <id> that may begin with "-".

COMMANDS
  widget get <id>       Read one widget (read-only, no side effects).
  widget delete <id>    Delete one widget, or many with --from-file (mutates).

GLOBAL FLAGS
  --machine       Machine mode; implies --json and --no-progress. Default: off.
  --json          Structured JSON output on stdout. Default: off.
  --no-progress   Suppress progress output on stderr. Default: off.
  --isolated      Ignore ambient config, credentials, and caches. Default: off.
  --no-config     Ignore config files only. Default: off.

widget get <id>
  Output: one JSON record {id, name, status}; status is active|inactive|deleted.
  --select <field>...   Fields to return: id, name, status (repeatable).
                        Default: all three. Unselected fields are absent, not null.
  --timeout <ms>        Network timeout in milliseconds. Default: 3000.
  Retries: none by default.
  Errors: VALIDATION_ERROR (2), WIDGET_NOT_FOUND (3), UNAUTHENTICATED (4),
          RATE_LIMITED (6, retryable), TIMEOUT (7, retryable).

widget delete <id>
  Mutates the remote widget store unless --dry-run is given.
  Requires <id> unless --from-file is given.
  Output: one JSON record {id, name, status: "deleted"}.
  --dry-run             Make no changes; print the planned action with
                        "dry_run": true. Default: off.
  --if-exists           Exit 0 instead of WIDGET_NOT_FOUND when the widget is
                        already gone; makes retries safe. Default: off.
  --from-file <path>    Delete every id listed in <path>. Output switches to
                        NDJSON: one record per item ({id, name, status} or
                        {id, error: {code, message, temporary}}), then a final
                        {"type": "summary", partial, succeeded, failed} record.
                        A missing summary record means the run did not finish.
  --allow-partial       With --from-file only: exit 0 when some items fail;
                        the summary carries "partial": true. Default: off
                        (any item failure exits 10, PARTIAL_FAILURE).
  --timeout <ms>        Network timeout in milliseconds. Default: 5000.
  Retries: none by default.
  On TIMEOUT (7) the outcome is unknown. Do not retry blindly: run
  "widgetctl widget get <id>"; WIDGET_NOT_FOUND means the delete committed.
  Retry with --if-exists.
  Errors: VALIDATION_ERROR (2), WIDGET_NOT_FOUND (3, suppressed by --if-exists),
          UNAUTHENTICATED (4), FORBIDDEN (5), RATE_LIMITED (6, retryable),
          TIMEOUT (7, reconcile first), PARTIAL_FAILURE (10, --from-file only,
          suppressed by --allow-partial).

EXIT CODES
  0 success           4 unauthenticated   8 conflict
  1 generic           5 forbidden         9 transient
  2 usage/validation  6 rate limited     10 partial failure
  3 not found         7 timeout

EXAMPLES
  widgetctl --machine widget get -- wgt_123
  widgetctl --machine widget get --select id --select status -- wgt_123
  widgetctl --machine widget delete --dry-run -- wgt_123
  widgetctl --machine widget delete --if-exists -- wgt_123
  widgetctl --machine widget delete --from-file ids.txt --dry-run

Schema: version 1.0, fingerprint wgt-a1b2c3d4 (scope: schema-contract).
Ambient state: reads config files (disable with --no-config) and a read-only
cache; --isolated disables both plus ambient credentials.
```

Notes on choices (help text was written from the schema only; nothing invented):

- Rules-then-context ordering: auth, machine mode, error branching, and `--` come before the command list; rationale is omitted.
- Command summaries are written to distinguish siblings (read-only vs mutating, single vs bulk).
- The `--from-file` id file format is not declared in the schema, so the help does not claim one.

Schema gaps that showed up while writing this (owner-side, not reflected as invented help content):

1. `--timeout` declares its unit only in a `unit` field; the conventional name is `--timeout-ms`, which makes the unit visible at the call site.
2. No schema/fingerprint command appears in `command_tree`, so the help cannot tell agents how to fetch the schema.
3. No ambient-state inspection command (resolved config, credential source) is declared, although the tool reads config, env, and cache.
4. Precedence among flags, `WIDGETCTL_TOKEN`, and config files is not declared.
5. `--from-file` input format, maximum size, and empty-file behavior are undeclared; `--from-file` with an `<id>` (mutual exclusion) is also undeclared.
6. Signal/interrupt semantics for `delete --from-file` (which items committed) are undeclared beyond the single-id reconciliation note.
7. `CONFLICT`, `TRANSIENT`, and `CURSOR_EXPIRED` are declared at tool level but no command can return them; `CURSOR_EXPIRED` has no paginated command.
~~~~~~
