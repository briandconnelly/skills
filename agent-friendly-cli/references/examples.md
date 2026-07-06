# Examples

Worked examples for a fictional CLI, `widgetctl`, that manages widgets (`id`, `name`, `status`).
Use these as concrete shapes to mimic; cross-reference [contract-checklist.md](contract-checklist.md) for the rules they instantiate.

## 1. Schema example
A minimal schema output for `widgetctl schema` is below, covering the `widget get` and `widget delete` commands.
Later sections also use `count`, `list`, `watch`, `update`, and `export`; their schema entries are omitted for brevity but follow the same per-command shape.
The machine profile is a single flag: `--machine` implies `--json` and `--no-progress`, so callers add one flag while the implied flags stay individually declared.
Shapes use a named compact notation, `widgetctl-compact-v1`, where `a|b` is a closed enum and fields are required unless marked optional; JSON Schema is the zero-explanation alternative.
```json
{
  "schema_version": "1.0",
  "fingerprint": "wgt-a1b2c3d4",
  "fingerprint_scope": "schema-contract",
  "canonical_machine_profile": ["--machine"],
  "isolation_profile": ["--isolated"],
  "shape_dialect": "widgetctl-compact-v1",
  "global_flags": [
    {"name": "--machine", "type": "boolean", "default": false, "implies": ["--json", "--no-progress"], "description": "non-interactive machine mode: no prompts, no color, no pager, structured output only"},
    {"name": "--json", "type": "boolean", "default": false, "description": "structured JSON output"},
    {"name": "--no-progress", "type": "boolean", "default": false, "description": "suppress progress output on stderr"},
    {"name": "--isolated", "type": "boolean", "default": false, "description": "ignore ambient config, credentials, and caches"},
    {"name": "--no-config", "type": "boolean", "default": false, "description": "ignore config files only"}
  ],
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "on failure in machine mode, the structured error object is the only stderr content",
  "end_of_options_supported": true,
  "command_tree": {
    "widget": {
      "get": "widgetctl widget get <id>",
      "delete": "widgetctl widget delete <id>"
    }
  },
  "exit_codes": {"0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient, not otherwise classified"},
  "symbolic_error_codes": ["VALIDATION_ERROR", "CURSOR_EXPIRED", "WIDGET_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSIENT"],
  "auth": "required",
  "environment": ["WIDGETCTL_TOKEN"],
  "config": {"reads": true, "disable_with": "--no-config"},
  "cache": {"reads": true, "writes": false},
  "credential_requirements": ["token"],
  "commands": [
    {
      "canonical_invocation_path": "widgetctl widget get <id>",
      "aliases": [],
      "deprecations": [],
      "classification": "inspect",
      "read_only": true,
      "arguments": [
        {"name": "id", "type": "string", "cardinality": "one", "examples": ["wgt_123"]}
      ],
      "flags": [
        {"name": "--select", "type": "enum", "enum": ["id", "name", "status"], "cardinality": "many", "default": ["id", "name", "status"]},
        {"name": "--timeout", "type": "integer", "unit": "ms", "default": 3000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "name": "string", "status": "active|inactive|deleted"}, "size_mode": "small"},
      "side_effects": {"external_mutation": false, "writes": []},
      "latency_class": "network",
      "timeout_defaults_ms": 3000,
      "retry_defaults": {"retries": 0},
      "async": false,
      "streaming": false,
      "pagination": false,
      "truncation": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "WIDGET_NOT_FOUND", "exit": 3},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true}
      ]
    },
    {
      "canonical_invocation_path": "widgetctl widget delete <id>",
      "aliases": [],
      "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [
        {"name": "id", "type": "string", "cardinality": "one", "required_unless": "--from-file", "examples": ["wgt_123"]}
      ],
      "flags": [
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--from-file", "type": "path", "default": null, "switches_output_class": "bulk-result"},
        {"name": "--allow-partial", "type": "boolean", "default": false, "requires": "--from-file"},
        {"name": "--timeout", "type": "integer", "unit": "ms", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "name": "string", "status": "deleted"}, "size_mode": "small"},
      "alternate_outputs": {
        "--from-file": {"class": "bulk-result", "format": "json", "shape": {"partial": "boolean", "results": "array of {id, name, status} or {id, error}"}, "size_mode": "grows with input"},
        "--dry-run": {"class": "record", "format": "json", "shape": {"dry_run": true, "planned_action": "delete", "id": "string"}, "size_mode": "small"},
        "--from-file --dry-run": {"class": "bulk-result", "format": "json", "shape": {"dry_run": true, "partial": "boolean", "results": "array of {id, planned_action} or {id, error}"}, "size_mode": "grows with input"}
      },
      "side_effects": {"external_mutation": true, "writes": ["remote widget store"], "description": "deletes the widget unless --dry-run is true", "dry_run": "no externally visible mutations; output includes \"dry_run\": true and the planned effect"},
      "latency_class": "network",
      "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "reconciliation": "on timeout or interrupt the outcome is unknown; run widgetctl widget get <id>: WIDGET_NOT_FOUND means the delete committed, and --if-exists makes a retry safe",
      "async": false,
      "streaming": false,
      "pagination": false,
      "truncation": false,
      "artifact": false,
      "errors_possible": [
        {"code": "VALIDATION_ERROR", "exit": 2},
        {"code": "WIDGET_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}
      ]
    }
  ]
}
```

## 2. Schema fingerprint example
The stable cache-key payload for `widgetctl schema --fingerprint` is below.
An additive change (a new optional flag or output field) bumps the minor version and changes the fingerprint; a breaking change (removal, rename, type or exit-code change) bumps the major version and changes the fingerprint.
A fingerprint change means re-fetch the schema; a major bump means existing call sites may break.
```json
{
  "schema_version": "1.0",
  "fingerprint": "wgt-a1b2c3d4",
  "fingerprint_scope": "schema-contract"
}
```

## 3. Success payloads, one per output class
Scalar success payload for `widgetctl widget count --machine`.
```json
3
```

Record success payload for `widgetctl widget get <id> --machine`.
```json
{
  "id": "wgt_123",
  "name": "Primary widget",
  "status": "active"
}
```

List success payload with pagination for `widgetctl widget list --machine`.
The omitted `list` schema entry declares the cursor contract: `next_cursor` is opaque, valid for 10 minutes, an expired cursor fails with `CURSOR_EXPIRED` (exit `2`), the restart action is re-running the command without a cursor, and page walks are best-effort rather than snapshot-consistent.
```json
{
  "items": [
    {"id": "wgt_123", "name": "Primary widget", "status": "active"},
    {"id": "wgt_124", "name": "Backup widget", "status": "inactive"}
  ],
  "has_more": true,
  "next_cursor": "cur_002",
  "limit": 2,
  "estimated_total": 5
}
```

Stream success payload for `widgetctl widget watch --machine`.
```ndjson
{"id":"wgt_123","name":"Primary widget","status":"active"}
{"id":"wgt_124","name":"Backup widget","status":"inactive"}
{"id":"wgt_125","name":"Old widget","status":"deleted"}
```

Bulk-result success payload for `widgetctl widget delete --from-file ids.txt --allow-partial --machine`, exit `0` because `--allow-partial` is set; without it any failed item makes the command exit nonzero.
```json
{
  "partial": true,
  "results": [
    {"id": "wgt_123", "name": "Primary widget", "status": "deleted"},
    {"id": "wgt_999", "error": {"code": "WIDGET_NOT_FOUND", "message": "Widget not found.", "resource_id": "wgt_999"}}
  ]
}
```

Dry-run success payload for `widgetctl widget delete wgt_123 --dry-run --machine`, exit `0`, distinguishable from a real deletion by the `dry_run` marker.
```json
{
  "dry_run": true,
  "planned_action": "delete",
  "id": "wgt_123"
}
```

Artifact success payload for `widgetctl widget export --output out.json --machine`.
```json
{
  "path": "out.json",
  "byte_size": 128,
  "content_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

## 4. Structured error payloads
Per the declared `stderr_framing` of `single-error-object`, in machine mode each error object below is the only stderr content for its failure; human mode may surround it with additional diagnostics.
Validation error for exit `2` from `widgetctl widget update wgt_123 --status bogus`, with JSON on stderr and empty stdout in machine mode.
`field` names the published `--status` flag, never an internal identifier, and the allowed values are machine-usable in `details` rather than only in `hint` prose.
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid widget status.",
  "field": "--status",
  "details": {"allowed_values": ["active", "inactive", "deleted"]},
  "hint": "Use one of: active, inactive, deleted."
}
```

Not-found error for exit `3`, with JSON on stderr and empty stdout in machine mode.
```json
{
  "code": "WIDGET_NOT_FOUND",
  "message": "Widget not found.",
  "resource_id": "wgt_404"
}
```

Rate-limited error for exit `6`, with JSON on stderr and empty stdout in machine mode.
```json
{
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded.",
  "retry_after_ms": 120000,
  "temporary": true
}
```

## 5. Review-finding example
Example finding for `gadgetctl`.
- severity: `P1`.
- type: `impl-bug`.
- location: command output from `gadgetctl gadget list --json`.
- impact: stdout includes progress before the JSON payload, so agents cannot parse the success payload deterministically.
- fix direction: keep stdout as success payload only and move progress or diagnostics to stderr.
