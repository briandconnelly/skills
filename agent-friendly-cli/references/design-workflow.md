# Design Workflow

Use this workflow when creating a new CLI, redesigning a CLI surface, or writing a contract for a tool that agents will call.

## 1. Model Tasks First

Define the smallest useful task model before choosing names, framework, or flags.

1. List the agent jobs the CLI must support.
2. Classify each job as `discover`, `inspect`, `query`, `mutate`, or `admin`.
3. Define the minimum input needed for each operation.
4. Define the minimum successful output needed for the next machine step.
5. Remove convenience wrappers around shell pipelines unless they provide a real contract advantage.

Prefer a few high-value verbs over a wide surface area.
If two commands require long prose to explain the difference, the command model is not ready.

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
- Support `--` end-of-options so operands beginning with `-` parse as data, and never pass argument values to a subshell or generated shell string.

Write `--help` text and command summaries rules-then-context: binding constraints, defaults, and prerequisites first; background after.

## 3. Write The Schema Before Behavior

Treat the schema as the authoritative design artifact.
The schema should declare:

- command tree, canonical invocation path, aliases, and deprecations
- arguments, flags, types, defaults, enums, cardinality, and examples
- canonical machine profile, preferring a single flag that implies the rest
- optional isolation profile, kept separate from machine mode unless the CLI can still complete normal authenticated reads without ambient state
- read-only vs mutating classification
- stdin contract: read behavior, formats, size limits, blocking, empty input, and exclusivity
- output class, output format, field shape, and example payloads
- shape dialect for output and error shapes: JSON Schema or an equivalently precise named notation
- numeric exit codes and symbolic error codes
- structured error fields and retryability
- auth, environment, config, cache, and credential requirements
- side effects, including dry-run semantics for mutations
- expected latency class and timeout/retry defaults
- reconciliation path for unknown-outcome mutations: an idempotency key or a lookup/status command
- async, streaming, pagination, truncation, artifact, and version-negotiation behavior
- cursor lifetime, expiry error, restart action, and page-walk consistency for paginated commands

Expose:

- `tool schema`: the authoritative full contract
- `tool schema --fingerprint`: a small stable cache key that changes when the schema contract changes; if version-only releases also change it, declare that explicitly, and pair it with `fingerprint_scope` as defined in [contract-checklist.md](contract-checklist.md)
- optionally `tool schema --summary` or `tool schema <command>` for compact partial loading

## 4. Choose Agent-Safe Defaults

Make the safe path the default path.

- Machine mode must never prompt, page, launch browsers, emit ANSI color, show spinners, or wait for terminal input.
- Non-TTY mode should evaluate each stream separately and conservatively suppress color, spinners, pagers, browser launch, and prompts.
- Mutating commands should require explicit action verbs and support `--dry-run`; dry-run output carries `dry_run: true` and the planned effect, never a payload identical to a real mutation result.
- Replay-sensitive mutations should support idempotency: `--if-not-exists`, `--if-exists`, or idempotency keys.
- Reads should avoid side effects by default and declare any unavoidable network, cache, or token-refresh effects.
- Accept secrets via environment variables, credential files, or stdin; do not accept them as flag values by default, because argv leaks into process listings, shell history, and agent transcripts.
- A mutation that times out has an unknown outcome; give callers a reconciliation path (idempotency key or lookup command) before they retry.
- Declare signal semantics for mutations and keep local state writes atomic under concurrent invocations.
- Long-running operations need a pollable async pattern with job ID, status, `wait --timeout`, and a cancel operation.

Design for partial information:

- Provide `find` or `search` when exact identifiers are unrealistic.
- Provide cheap inspection commands for identity (when the tool has an identity concept), resolved configuration, and credential/environment sources; `whoami` and `config show --resolved` are conventional names, not requirements.
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
Each command declares one output class; a flag that switches the class (bulk input, watch modes) must declare the alternate class in the schema.

Output rules:

- stdout contains only the success payload.
- stderr contains diagnostics, warnings, progress, debug detail, and structured failures.
- Declare machine-mode stderr framing as a closed enum value (`single-error-object` or `ndjson-typed`): on failure the structured error object is the only stderr content, or stderr is NDJSON records typed `progress`, `warning`, or `error`, so agents never fish a JSON payload out of free-form text.
- JSON should be shallow, stable, deterministic, and free of human summaries.
- In machine-mode success payloads, avoid prose `message` fields that duplicate structured payload data; if a `message` field exists, it should add non-duplicative context only.
- In error payloads, `message` is the human rendering of `code` and may restate it; agents branch on `code`.
- Pagination, truncation, omitted fields, partial failure, retries exhausted, and version mismatch must be structured.
- NDJSON is for streams and large result sets; arrays are for small finite lists.
- Machine output uses UTF-8, locale-independent numbers, stable path style, and UTC or explicitly declared timezones for timestamps.
- `--output <file>` should be restricted to explicit export commands and return path, byte size, and content hash.

Error rules:

- Reserve numeric exit codes `0-9` for the cross-tool meanings suggested in [contract-checklist.md](contract-checklist.md); beyond `0`-`2` they are a skill convention, so declare them in the schema.
- Use symbolic JSON error codes as the authoritative branch key.
- Include required error fields `code` and `message`.
- Prefer useful optional fields: `hint`, `retry_after_ms`, `details`, `field`, `resource_id`, `conflict_with`, `temporary`, `request_id`, `docs_url`, `path`.
- `field` names a published flag or argument, never an internal identifier.
- `hint` names the smallest concrete correction; put machine-usable repair data such as allowed values in structured fields like `details`.
- Stack traces and raw request/response dumps are opt-in under `--debug` and must redact secrets.
- Secrets must not appear in stdout, stderr, schema examples, request/response dumps, or artifact metadata unless the command's explicit purpose is to return a secret.

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
- Test interrupt behavior for mutations and concurrent invocations against local state.
