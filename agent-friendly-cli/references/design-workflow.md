# Design Workflow

Use this workflow when creating a new CLI, redesigning a CLI surface, or writing a contract for a tool that agents will call.

## 1. Model Tasks First

Define the smallest useful task model before choosing names, framework, or flags.

1. List the agent jobs the CLI must support.
2. Classify each job as `discover`, `inspect`, `query`, `mutate`, or `admin`.
3. Define the minimum input needed for each operation.
4. Define the minimum successful output needed for the next machine step.
5. Remove convenience wrappers around shell pipelines unless they provide a real contract advantage.

Prefer a few high-value verbs over a wide surface area. If two commands require long prose to explain the difference, the command model is not ready.

## 2. Design A Guessable Command Surface

Use a consistent grammar:

- Prefer `tool noun verb` for new tools.
- Keep the tree shallow; use deeper nesting only for genuinely distinct sub-resources.
- Keep nouns stable and few.
- Reuse verbs where semantics match: `list`, `get`, `find`, `create`, `update`, `delete`, `validate`.
- Avoid stylistic duplicates like `list` vs `show-all` or `remove` vs `delete`.

Keep argument shapes uniform:

- Pick one primary selector pattern per resource type: name, ID, path, query, or stdin.
- Use consistent flags such as `--format`, `--limit`, `--filter`, `--timeout`, `--output`.
- Prefer named flags; reserve positional arguments for one obvious primary selector.
- Do not let the same flag mean different things across commands.

## 3. Write The Schema Before Behavior

Treat the schema as the authoritative design artifact. The schema should declare:

- command tree, canonical invocation path, aliases, and deprecations
- arguments, flags, types, defaults, enums, cardinality, and examples
- canonical machine profile
- read-only vs mutating classification
- stdin contract: read behavior, formats, size limits, blocking, empty input, and exclusivity
- output class, output format, field shape, and example payloads
- numeric exit codes and symbolic error codes
- structured error fields and retryability
- auth, environment, config, cache, and credential requirements
- side effects, including dry-run semantics for mutations
- expected latency class and timeout/retry defaults
- async, streaming, pagination, truncation, artifact, and version-negotiation behavior

Expose:

- `tool schema`: the authoritative full contract
- `tool schema --fingerprint`: a small stable cache key that changes when the schema contract changes; if version-only releases also change it, declare that explicitly
- optionally `tool schema --summary` or `tool schema <command>` for compact partial loading

## 4. Choose Agent-Safe Defaults

Make the safe path the default path.

- Machine mode must never prompt, page, launch browsers, emit ANSI color, show spinners, or wait for terminal input.
- Non-TTY mode should conservatively suppress color, spinners, pagers, browser launch, and prompts.
- Mutating commands should require explicit action verbs and support `--dry-run`.
- Replay-sensitive mutations should support idempotency: `--if-not-exists`, `--if-exists`, or idempotency keys.
- Reads should avoid side effects by default and declare any unavoidable network, cache, or token-refresh effects.
- Long-running operations need a pollable async pattern with job ID, status, and `wait --timeout`.

Design for partial information:

- Provide `find` or `search` when exact identifiers are unrealistic.
- Provide cheap inspection commands such as `whoami`, `config show --resolved`, and `env`.
- Return enough IDs, names, and disambiguating fields for the next refinement step.

## 5. Design Output And Errors Up Front

Standardize on a small number of output classes:

- `scalar`: one value or status
- `record`: one resource
- `list`: finite collection
- `stream`: NDJSON records
- `bulk-result`: per-item results plus aggregate exit-code semantics
- `artifact`: large result written to disk with structured pointer

Custom output classes are acceptable when the built-in set does not fit cleanly, but they must be explicitly named in the schema and have a stable shape, paging behavior, and examples.

Output rules:

- stdout contains only the success payload.
- stderr contains diagnostics, warnings, progress, debug detail, and structured failures.
- JSON should be shallow, stable, deterministic, and free of human summaries.
- In machine mode, avoid prose `message` fields that duplicate structured payload data; if a `message` field exists, it should add non-duplicative context only.
- Pagination, truncation, omitted fields, partial failure, retries exhausted, and version mismatch must be structured.
- NDJSON is for streams and large result sets; arrays are for small finite lists.
- `--output <file>` should be restricted to explicit export commands and return path, byte size, and content hash.

Error rules:

- Reserve numeric exit codes `0-9` for cross-tool meanings.
- Use symbolic JSON error codes as the authoritative branch key.
- Include required error fields `code` and `message`.
- Prefer useful optional fields: `hint`, `retry_after_ms`, `details`, `field`, `resource_id`, `conflict_with`, `temporary`, `request_id`, `docs_url`, `path`.
- Stack traces and raw request/response dumps are opt-in under `--debug` and must redact secrets.

## 6. Build For Testability

Use a result-then-render architecture:

- typed command inputs
- typed success payloads
- typed error payloads
- separate human renderer
- separate machine renderer

Keep metadata paths fast:

- Target sub-100ms for `--help`, `tool schema`, and `tool schema --fingerprint`.
- Avoid eager network calls, auth validation, plugin loading, and heavy imports on metadata-only paths.

Ship contract tests:

- Snapshot the machine schema.
- Snapshot canonical success payloads for each output class.
- Snapshot representative failure payloads and exit codes.
- Verify that each declared exit code can be triggered at runtime by at least one scenario.
- Test TTY vs non-TTY behavior.
- Test machine mode suppression of prompts, color, progress, and prose.
- Test truncation, pagination, artifact output, and streaming.
- Test config/env precedence and isolation flags.
- Test deprecated paths and replacements.
