# Probe P2c — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 61,867 (final-turn context plus output, read from the transcript)
- **Output words:** 1,003
- **Transcript sha256:** `29e0ec5f3b48d9803bbf6d7d61c79998c48c8dcffaf0ec3096db8e6dbdd37661` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P2c-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | ## Decision: stays one call, no prompt, no `--yes` |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: tool owner (contract hardening of an owned CLI).
Assumptions (confirm or correct): notes live in a backend reached over the network; IDs are opaque strings; `notectl` already has a `--machine` profile and a `notectl schema` command. Where these differ, adjust the marked fields.

## Decision: stays one call, no prompt, no `--yes`

The `delete` verb itself is the explicit action trigger, so no confirmation flag or prompt is added.
`delete` never prompts, in any mode or TTY state; this is declared in the schema (`interactive: false`) so agents never need to feed stdin.
Safety comes from `--dry-run`, `--if-exists`, an optional `--idempotency-key`, and a precise error/retry catalog, all optional — the base call stays `notectl note delete --machine -- "<id>"`.

## Invocation

```
notectl note delete [--machine] [--dry-run] [--if-exists] [--idempotency-key <key>] [--timeout-ms <int>] [--] <id>
```

| Element | Type | Default | Notes |
|---|---|---|---|
| `<id>` | string, positional, cardinality 1 | required | The sole primary selector for notes. Use `--` before it; IDs starting with `-` are data. Never passed to a shell. |
| `--dry-run` | bool | false | Validates and resolves the note; no mutation. |
| `--if-exists` | bool | false | Suppresses `NOTE_NOT_FOUND`; makes delete repeat-safe. |
| `--idempotency-key` | string | none | Server dedupes within a declared window (e.g. 24h). Must be supplied on the *first* attempt to protect retries. |
| `--timeout-ms` | int, unit ms | 30000 | Caller-settable network deadline. |
| `--machine` | global | off | Machine profile: JSON on stdout, structured errors on stderr, no color/progress/prompts. |

Stdin: not read. Never blocks. Empty stdin irrelevant.
Classification: `mutating`, latency class `network`, `interactive: false`.
Bulk delete is out of scope for this command; if added later, it is a separate declared `bulk-result` mode.

## Output (stdout, machine mode)

Output class: `record`, format `json`, not streaming. Shape dialect: JSON Schema (required fields listed below).

Success (exit 0):
```json
{"id":"n_8f2c","deleted":true,"existed":true,"dry_run":false}
```

`--if-exists` on a missing note (exit 0):
```json
{"id":"n_8f2c","deleted":false,"existed":false,"dry_run":false}
```

`--dry-run` (exit 0 if the delete would succeed; otherwise the normal error contract):
```json
{"id":"n_8f2c","deleted":false,"existed":true,"dry_run":true,"would_delete":true}
```

Required: `id`, `deleted`, `existed`, `dry_run`. `would_delete` present only when `dry_run: true`.
Dry run is never byte-identical to real output, and performs no externally visible mutation (token refresh, if any, is documented and suppressed under `--isolated`).
Combining `--dry-run --if-exists` on a missing note: exit 0, `existed:false, would_delete:false`.
On failure, stdout is empty.

## Errors and exit codes

Stderr framing: `single-error-object` (the error object is the only stderr content in machine mode).
Required fields: `code`, `message`, `temporary`; agents branch on `code`, never on `message`.

| code | exit | retryable | reconcile_first | suppressed by |
|---|---|---|---|---|
| `USAGE` | 2 | false | false | — |
| `NOTE_NOT_FOUND` | 3 | false | false | `--if-exists` |
| `UNAUTHENTICATED` | 4 | false | false | — |
| `FORBIDDEN` | 5 | false | false | — |
| `RATE_LIMITED` | 6 | true (`retry_after_ms` included) | false | — |
| `TIMEOUT` | 7 | true | **true** | — |
| `CONFLICT` (e.g. note locked) | 8 | false | false | — |
| `NETWORK_ERROR` | 9 | true | **true** | — |
| `INTERNAL` (fallback) | 1 | false | true | — |

Example:
```json
{"code":"NOTE_NOT_FOUND","message":"note n_8f2c not found","temporary":false,"resource_id":"n_8f2c","hint":"pass --if-exists to treat a missing note as success"}
```

A code absent from this catalog: act on its payload fields and reconcile first (it is a mutation).

## Retry and unknown-outcome semantics

- `TIMEOUT`, `NETWORK_ERROR`, interrupt, or `INTERNAL` after the request was sent = **unknown outcome**.
- Retry is safe automatically if either: the original call used `--if-exists` (a repeat returns exit 0 whether or not the first attempt committed), or the original call carried an `--idempotency-key` reused within the window.
- Without either, the command is **not safe to retry automatically**; reconcile with `notectl note get -- "<id>"`. A `NOTE_NOT_FOUND` from `get` does not prove *this* attempt deleted it, but for delete the end state is what matters, so the recommended agent call is simply:
  `notectl note delete --machine --if-exists -- "<id>"`
- A key first added on the retry does not dedupe the original attempt.

Signals: SIGINT/SIGTERM before the request is sent leaves nothing; after it is sent the server may still commit. No local writes besides any auth-token cache, which uses atomic replace.
Closed stdout: the command finishes the delete and exits per result.

## Ambient state

Declared in schema: credential source (env `NOTECTL_TOKEN` > credential file > keychain), config file path, workspace/account selection and its override flag, precedence flags > env > config > cache.
`notectl whoami` and `notectl config show --resolved` let an agent confirm *which* account/workspace a delete will hit before deleting; `--dry-run` output should include the resolved `workspace` for the same reason.
No secrets accepted as flags. No telemetry or update checks in machine mode.

## Schema entry (sketch)

```json
{
  "command": "note delete",
  "mutating": true,
  "interactive": false,
  "latency_class": "network",
  "stdin": {"read": false},
  "end_of_options": true,
  "args": [{"name": "id", "type": "string", "required": true, "positional": true}],
  "flags": {
    "dry-run": {"type": "bool", "default": false},
    "if-exists": {"type": "bool", "default": false},
    "idempotency-key": {"type": "string", "dedupe_window_s": 86400},
    "timeout-ms": {"type": "int", "unit": "ms", "default": 30000}
  },
  "output": {"class": "record", "format": "json", "streaming": false},
  "stderr_framing": "single-error-object",
  "retry": {"automatic": false, "safe_when": ["if-exists", "idempotency-key"]},
  "errors": ["USAGE","NOTE_NOT_FOUND","UNAUTHENTICATED","FORBIDDEN","RATE_LIMITED","TIMEOUT","CONFLICT","NETWORK_ERROR","INTERNAL"]
}
```
Available via `notectl schema note delete`; any change bumps the schema fingerprint.

## Tests to ship

- Schema snapshot for `note delete`.
- Success, `--if-exists` miss, dry-run payloads; dry-run leaves the note intact.
- Each catalog code → declared exit code (runtime-verified).
- No prompt with stdin as TTY, as closed, or as pipe; machine mode emits only JSON.
- `--` with an ID beginning with `-`.
- Idempotency key replay returns the original result; interrupt mid-request.

## Checklist not-applicable items

- Pagination/truncation/streaming: single record output.
- Async jobs: delete is synchronous.
- Partial failure: single-item command.
- `--output <file>`: not an export command.
~~~~~~
