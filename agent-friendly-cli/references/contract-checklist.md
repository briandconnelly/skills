# Contract Checklist

Use this as the detailed standard for both design and review tasks.

## Command Model

- Prefer one canonical operation per task.
- Prefer `tool noun verb` for new tools.
- Keep command trees shallow.
- Use stable domain nouns from APIs, docs, database objects, and error payloads.
- Use aliases only for migration; declare aliases in schema and avoid them in canonical examples.
- Use full words unless an abbreviation is dominant in the domain.
- Reuse verbs consistently where semantics match.
- Avoid flags whose meanings change across commands.

## Machine Schema

The schema is the primary contract. It should include:

- command tree and canonical invocation path
- aliases, deprecations, and replacements
- arguments, flags, types, defaults, enums, cardinality, and examples
- canonical machine profile
- stdin contract
- read-only vs mutating classification
- auth, role, scope, environment, config, cache, and credential requirements
- output class, shape, format, examples, and size mode
- numeric exit codes and symbolic error codes (declared at tool level)
- per-command error catalog: which symbolic codes that command can return, which exit code they map to, and which flags suppress them (e.g., `--if-exists`)
- side effects
- expected latency class: `local` (filesystem only), `cached` (cache-served), `network` (one network round trip), `slow` (multi-step or known >1s), `async` (must poll)
- timeout and retry defaults
- async, polling, streaming, pagination, truncation, artifact, and version-negotiation behavior
- schema version and stable fingerprint

Expose a compact fingerprint endpoint so agents can cache the schema cheaply. The fingerprint should be stable across version-only releases unless the schema contract changed; if version is part of the fingerprint input, declare that explicitly.

## Stdin Contract

For every command, declare:

- whether stdin is read
- whether stdin is auto-detected when piped or requires an explicit flag
- accepted formats
- maximum input size
- whether stdin can block
- whether stdin is mutually exclusive with positional args or flags
- how empty stdin is handled

Reading explicitly piped stdin is fine when declared. Waiting for terminal input in machine mode is not.

## Agent-Safe Invocation

- Define one canonical machine profile.
- Machine mode is non-interactive.
- Non-TTY mode conservatively suppresses color, progress, spinners, pagers, browser launch, and prompts.
- Machine mode must not hide deprecations, truncation, partial failure, retries exhausted, version mismatch, or unsafe ambient-state warnings unless those facts appear in structured output.
- Every interactive setup or login flow needs a documented non-interactive bootstrap.

## Output

- stdout is success payload only.
- stderr carries diagnostics and machine-readable failures.
- Streaming success output still goes to stdout as NDJSON; stderr may emit periodic structured progress objects when the schema declares them.
- Default output is the requested payload, not banners or summaries.
- JSON is shallow, stable, deterministic, and compact.
- If JSON includes a `message` field, it must not duplicate structured data that is already present elsewhere in the payload.
- NDJSON is used for streaming and large per-record result sets.
- Arrays are used for small finite lists.
- Pagination includes `has_more`; if `has_more` is `true`, include a navigation token such as `next_cursor` or `offset`. Include `limit` and `estimated_total` when available.
- Truncation, omitted fields, and size caps are explicit.
- `--filter`, `--field` or `--select`, and `--sort` are first-class when the data shape supports them.
- Default sort is deterministic.
- `--output <file>` is restricted to export commands and returns path, byte size, and content hash.

## Errors And Exit Codes

Reserved numeric exit-code meanings (skill convention; codes `0`, `1`, `2` follow common Unix usage but `3`-`9` are not POSIX or `sysexits.h` — declare them in schema):

- `0`: success
- `1`: generic
- `2`: usage or validation
- `3`: not found
- `4`: unauthenticated
- `5`: forbidden
- `6`: rate limited
- `7`: timeout
- `8`: conflict
- `9`: transient or retryable
- `10+`: domain-specific, declared in schema

The symbolic JSON `code` is the authoritative branch key for agents; the numeric exit code is the shell-branching fallback.

Structured errors:

- Required fields: `code`, `message`.
- Recommended fields: `hint`, `retry_after_ms`, `details`, `field`, `resource_id`, `conflict_with`, `temporary`, `request_id`, `docs_url`, `path`.
- In JSON mode, `code` is symbolic and stable across platforms.
- Numeric codes are only the shell-branching fallback.
- Retryability is explicit.
- Debug detail is opt-in and redacted.

Partial failure:

- Multi-item commands exit nonzero by default if any item fails.
- `--allow-partial` may permit exit `0`, but output must include `partial: true` and failed item errors.
- Bulk operations should report per-item results in NDJSON when result size can grow.

## Ambient State

Document:

- where credentials come from
- which config files are read
- which environment variables are read
- which caches are used
- precedence rules, preferably flags > env vars > config files > local caches
- how to disable ambient state
- how to inspect resolved state

Required inspection affordances for tools that read ambient state (config files, env vars, credentials, caches — not the tool's own primary data store):

- `whoami`
- `config show --resolved`
- `env`

Provide `--no-config` or `--isolated` for tools that read ambient config, credentials, or caches. If state cannot be disabled, expose that fact in schema and machine output.

## Mutations And Long-Running Work

- Mutations require explicit action triggers such as `create`, `apply`, `delete`, or `--yes`.
- Every mutating command should support `--dry-run`.
- Dry runs must avoid externally visible mutations.
- Internal effects during dry runs, such as cache warming or token refresh, must be documented and suppressible in isolated mode.
- Replay-sensitive mutations should support `--if-not-exists`, `--if-exists`, or idempotency keys.
- Long-running operations need job IDs, machine-readable status, polling, and `wait --timeout`.

## Side Effects And Telemetry

- No surprise side effects on reads.
- No implicit writes on read verbs.
- No network calls beyond the command's declared purpose.
- No telemetry, update checks, or phone-home behavior by default.
- Telemetry and update checks must be opt-in, suppressed in machine mode, and never prepended to stdout.

## Tests

Ship tests for:

- schema snapshots
- canonical success payloads
- representative failure payloads and exit codes
- runtime verification that declared exit codes map to observed exits
- TTY vs non-TTY behavior
- machine mode suppression of prompts, color, progress, and prose
- stdin behavior, including empty stdin
- truncation, pagination, artifact output, and streaming
- config/env precedence and isolation flags
- deprecations and replacements
- dry-run behavior for mutations

If behavior matters to an agent, cover it with an automated test.
