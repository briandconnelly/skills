# Examples

Worked examples for a fictional CLI, `widgetctl`, that manages widgets (`id`, `name`, `status`).
Use these as concrete shapes to mimic; cross-reference [contract-checklist.md](contract-checklist.md) for the rules they instantiate.

## 1. Schema example
The complete minimal schema output for `widgetctl schema` is below.
```json
{
  "schema_version": "1.0",
  "fingerprint": "wgt-a1b2c3d4",
  "fingerprint_scope": "schema-contract",
  "canonical_machine_profile": ["--json", "--machine", "--no-config", "--no-progress"],
  "command_tree": {
    "widget": {
      "get": "widgetctl widget get <id>",
      "delete": "widgetctl widget delete <id>"
    }
  },
  "exit_codes": {"0": "success", "1": "generic", "2": "usage or validation", "3": "not found", "4": "unauthenticated", "5": "forbidden", "6": "rate limited", "7": "timeout", "8": "conflict", "9": "transient or retryable"},
  "symbolic_error_codes": ["VALIDATION_ERROR", "WIDGET_NOT_FOUND", "UNAUTHENTICATED", "FORBIDDEN", "RATE_LIMITED", "TIMEOUT", "CONFLICT", "TRANSIENT"],
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
        {"name": "--json", "type": "boolean", "default": false},
        {"name": "--select", "type": "enum", "enum": ["id", "name", "status"], "cardinality": "many", "default": ["id", "name", "status"]},
        {"name": "--timeout", "type": "integer", "default": 3000}
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
      "artifact": false
    },
    {
      "canonical_invocation_path": "widgetctl widget delete <id>",
      "aliases": [],
      "deprecations": [],
      "classification": "mutate",
      "read_only": false,
      "arguments": [
        {"name": "id", "type": "string", "cardinality": "one", "examples": ["wgt_123"]}
      ],
      "flags": [
        {"name": "--json", "type": "boolean", "default": false},
        {"name": "--dry-run", "type": "boolean", "default": false},
        {"name": "--if-exists", "type": "boolean", "default": false},
        {"name": "--timeout", "type": "integer", "default": 5000}
      ],
      "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "accepted_formats": [], "maximum_input_size": 0, "can_block": false, "mutually_exclusive_with": [], "empty_stdin": "ignored"},
      "output": {"class": "record", "format": "json", "shape": {"id": "string", "name": "string", "status": "deleted"}, "size_mode": "small"},
      "side_effects": {"external_mutation": "deletes widget unless --dry-run is true", "dry_run": "no externally visible mutations"},
      "latency_class": "network",
      "timeout_defaults_ms": 5000,
      "retry_defaults": {"retries": 0},
      "async": false,
      "streaming": false,
      "pagination": false,
      "truncation": false,
      "artifact": false,
      "errors_possible": [
        {"code": "WIDGET_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true}
      ]
    }
  ]
}
```

## 2. Schema fingerprint example
The stable cache-key payload for `widgetctl schema --fingerprint` is below.
```json
{
  "schema_version": "1.0",
  "fingerprint": "wgt-a1b2c3d4",
  "fingerprint_scope": "schema-contract"
}
```

## 3. Success payloads, one per output class
Scalar success payload for `widgetctl widget count --json`.
```json
3
```

Record success payload for `widgetctl widget get <id> --json`.
```json
{
  "id": "wgt_123",
  "name": "Primary widget",
  "status": "active"
}
```

List success payload with pagination for `widgetctl widget list --json`.
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

Stream success payload for `widgetctl widget watch --json`.
```ndjson
{"id":"wgt_123","name":"Primary widget","status":"active"}
{"id":"wgt_124","name":"Backup widget","status":"inactive"}
{"id":"wgt_125","name":"Old widget","status":"deleted"}
```

Bulk-result success payload for `widgetctl widget delete --from-file ids.txt --allow-partial --json`.
```json
{
  "partial": true,
  "results": [
    {"id": "wgt_123", "name": "Primary widget", "status": "deleted"},
    {"id": "wgt_999", "error": {"code": "WIDGET_NOT_FOUND", "message": "Widget not found.", "resource_id": "wgt_999"}}
  ]
}
```

Artifact success payload for `widgetctl widget export --output out.json --json`.
```json
{
  "path": "out.json",
  "byte_size": 128,
  "content_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

## 4. Structured error payloads
Validation error for exit `2`, with JSON on stderr and empty stdout in machine mode.
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid widget status.",
  "field": "status",
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
