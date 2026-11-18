# Scenario R1 (hardening) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 64,466 (final-turn context plus output, read from the transcript)
- **Output words:** 1,916
- **Transcript sha256:** `20fc86bb503c27d5341f7e521175cf9ec41ba49419186e76862a89a57bc14f40` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels
- **Checklist coverage table present:** yes

## Exact prompt given

> Our team owns `envctl`, an internal Go CLI that lists, shows, creates, and deletes environment-variable profiles stored in a shared service.
> Developers use it interactively today; our CI agents (Claude Code and Codex) will start calling it next quarter.
> Propose the changes that would make it safe and easy for agents to call, in priority order.
> Here is the current help:
>
> ```text
> $ envctl --help
> envctl — manage environment profiles
>
> Usage: envctl <command> [flags]
>
> Commands:
>   list              List profiles
>   show <name>       Show a profile
>   create <name>     Create a profile (prompts for values)
>   delete <name>     Delete a profile (asks "are you sure?")
>   login             Log in via browser
>
> Flags:
>   -v, --verbose     More output
>   --profile-dir     Where profiles are cached (default ~/.envctl)
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/R1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | create: output_class `record` only, no fields; list/get/delete have shapes Parts: machine-readable mode = pass; list shape = pass; show shape = pass; create shape = fail; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | `3` not found, `4` unauthenticated ... Agents branch on `code` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `delete`: require `--yes`; `--dry-run` on create, update, delete; `ENVCTL_TOKEN` + device-code Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `envctl config show --resolved` ... `--isolated`: ignore config file and cache Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | Add `envctl schema` (full JSON), `envctl schema <command>` |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: tool author (you own `envctl`).
Task: redesign / contract hardening of an existing CLI with no machine contract yet.
Below, changes are ordered by how badly the current behavior breaks an agent in CI; a draft schema excerpt and a per-section checklist coverage table follow.

## P0 — blockers (agents hang, or mutate unsafely)

### 1. Remove every interactive path from machine mode

Today `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser. In CI each of these hangs or fails unpredictably.

- Add a single machine profile flag, `--machine`, that implies: `--format json`, no prompts, no color, no progress/spinner, no pager, no browser launch. Also honor `ENVCTL_MACHINE=1`.
- Non-TTY detection per stream: stdin not a TTY → never prompt (fail with `code: "INPUT_REQUIRED"`, exit 2); stdout not a TTY → no human tables/pager; stderr not a TTY → no color/progress.
- `create`: accept values non-interactively, via stdin (`--from-stdin`, JSON object or `KEY=VALUE` lines, explicit flag, never auto-detected) or `--from-file <path>`. Never accept secret values as `--set KEY=VALUE` argv by default (leaks into process listings and agent transcripts); if a `--set` flag is kept for convenience, restrict it to non-secret values and document the exposure.
- `delete`: require `--yes` in machine mode; without it, exit 2 with `code: "CONFIRMATION_REQUIRED"`, `field: "--yes"`. Never prompt.
- `login`: add a documented non-interactive bootstrap — credentials from `ENVCTL_TOKEN` (or a credential file / OS keychain), plus a device-code flow (`envctl auth login --device`) that prints the URL and code as structured output instead of launching a browser. Never accept the token as a flag value.

### 2. Structured output and errors

- Add `--format json|text` (default `text` on TTY, `json` under `--machine`).
- stdout carries only the success payload; banners, `--verbose` chatter, and diagnostics go to stderr.
- On failure in machine mode: empty stdout, stderr framing `single-error-object` with a structured error: required `code` (symbolic, stable), `message`, `temporary`; recommended `hint`, `field`, `resource_id`, `request_id`, `retry_after_ms`, `details`.
- Declared exit codes: `0` success, `1` generic, `2` usage/validation (incl. `INPUT_REQUIRED`, `CONFIRMATION_REQUIRED`), `3` not found, `4` unauthenticated, `5` forbidden, `6` rate limited, `7` timeout, `8` conflict (profile already exists), `9` transient. Agents branch on `code`; exit code is the shell fallback; `temporary` decides retry.

### 3. Secret redaction

Profiles hold environment variables, which routinely contain secrets.

- `show` and `list` redact values by default (`"value": null, "redacted": true`), with an explicit `--reveal` (or a separate `get-value` / `export` command) as the only path that returns plaintext, and only for the named keys.
- Redact in stderr, `--verbose`/debug output, error `details`, and schema examples.
- Mark per-variable `secret: true` metadata on create so redaction isn't guesswork.

### 4. Safe mutations

- `--dry-run` on `create`, `update`, `delete`: no remote writes, output includes `dry_run: true` and the planned effect (keys to add/change/remove, values redacted), exits 0 if valid, otherwise uses the normal error contract.
- Idempotency: `create --if-not-exists` and `delete --if-exists` (suppress `CONFLICT` / `NOT_FOUND`), and accept `--idempotency-key` on `create`/`update` so a retry after a timeout is safe.
- Unknown outcome: a mutation that times out returns `code: "TIMEOUT"`, `temporary: true`, `reconcile_first: true` unless an idempotency key was supplied; reconciliation path is `envctl profile get <name>`.
- Optimistic concurrency for updates to shared profiles: `--if-match <revision>` returning `CONFLICT` (exit 8) with `conflict_with` on mismatch — two CI agents editing one profile is a realistic race.
- Signals: SIGINT/SIGTERM during a mutation leaves the server-side request in an unknown state (reconcile via `get`); local cache writes use atomic replace.

## P1 — contract and discovery

### 5. Machine-readable schema

Add `envctl schema` (full JSON), `envctl schema <command>` (one command), and `envctl schema --fingerprint` (`{"fingerprint": "...", "fingerprint_scope": "schema-contract", "schema_version": "1.0.0"}`). These metadata paths must not hit the network, validate auth, or touch the cache, and should return in <100ms. The schema declares everything in the draft below. Additive changes change the fingerprint; breaking changes (removals, renames, exit-code remaps) also bump the major version.

### 6. Command model

Move to `noun verb`, with conventional verbs and one selector (profile name, positional):

| Current | Proposed | Class | Output class |
| --- | --- | --- | --- |
| `list` | `envctl profile list` | read | `list` |
| `show <name>` | `envctl profile get <name>` | read | `record` |
| `create <name>` | `envctl profile create <name>` | mutate | `record` |
| — | `envctl profile update <name>` | mutate | `record` |
| `delete <name>` | `envctl profile delete <name>` | mutate | `scalar` |
| — | `envctl profile find --filter …` (only if profile counts make exact names impractical) | read | `list` |
| `login` | `envctl auth login [--device]` | admin | `record` |
| — | `envctl auth whoami` | read | `record` |
| — | `envctl config show --resolved` | read | `record` |
| — | `envctl schema` | discover | `record` |

Keep the old verbs (`show`, top-level `list` etc.) as declared aliases for migration only, marked deprecated with replacements, and absent from canonical examples. Support `--` end-of-options so a profile named `-x` can't be parsed as a flag; never pass profile names or values to a shell.

### 7. Ambient state made explicit

- Document and expose precedence: flags > env vars (`ENVCTL_TOKEN`, `ENVCTL_SERVER`, `ENVCTL_PROFILE_DIR`, `ENVCTL_MACHINE`) > config file > `~/.envctl` cache.
- Rename `--profile-dir` to what it is — a cache — e.g. `--cache-dir`, and declare whether reads are served from it (latency class `cached` vs `network`). Stale cache served to an agent is a silent correctness bug: either always read through to the service in machine mode, or include `source: "cache"` and `cached_at` in output.
- `envctl config show --resolved` (each value with its source; secrets redacted) and `envctl auth whoami` (identity, credential source, expiry).
- `--isolated`: ignore config file and cache; credentials only from env. Because authenticated reads still work with an env token, document that `--isolated` and `--machine` are distinct and composable.
- Concurrent CI invocations writing `~/.envctl`: atomic file replacement or a lockfile.

### 8. Output details

- `list`: JSON array of `{name, variable_count, updated_at, revision}`, deterministic sort by `name`, with `--limit` and cursor pagination (`has_more`, `next_cursor`; cursors opaque, declared lifetime, `CURSOR_EXPIRED` error, restart from no cursor) if profile counts can grow.
- `get`: `{name, revision, updated_at, variables: [{key, secret, value|null, redacted}]}`, keys sorted, timestamps UTC RFC 3339.
- `--field`/`--select` projection on `get` if variable lists get large; declare the projection rule.
- No `message` field in success payloads duplicating data.

### 9. Network behavior

- `--timeout-ms` on every networked command (default declared, e.g. 10000), declared retry policy (e.g. no automatic retries on mutations without an idempotency key; up to 2 retries with backoff on reads), and `RATE_LIMITED` with `retry_after_ms`.
- `--verbose` stays, but in machine mode it emits NDJSON-typed records only if you switch stderr framing to `ndjson-typed`; otherwise verbose is suppressed. Pick one framing and declare it.

## P2 — hygiene

### 10. Help text and prose surfaces

Rewrite summaries rules-first and task-selective, e.g. `delete <name>  Delete a profile. Requires --yes when non-interactive. Irreversible.` and `create <name>  Create a profile from --from-file or --from-stdin; fails with CONFLICT if it exists unless --if-not-exists.` State prerequisites (auth) and defaults before background.

### 11. Side effects and telemetry

Reads never write to the service; cache refreshes on reads are documented and disabled under `--isolated`. No update checks or telemetry by default; never on stdout.

### 12. Architecture and tests

Refactor to result-then-render (typed inputs, typed success/error structs, separate human and JSON renderers) — straightforward in Go with a `Result` struct per command. Keep `--help`/`schema` free of client initialization. Ship the tests listed below.

## Draft schema excerpt

Shape dialect: JSON Schema 2020-12 (`required` arrays mark required fields).

```json
{
  "schema_version": "1.0.0",
  "fingerprint": "sha256:…",
  "fingerprint_scope": "schema-contract",
  "shape_dialect": "json-schema-2020-12",
  "machine_profile": {"flag": "--machine", "env": "ENVCTL_MACHINE", "implies": ["--format=json", "no-prompt", "no-color", "no-progress", "no-pager", "no-browser"]},
  "isolation_profile": {"flag": "--isolated", "disables": ["config_file", "cache"], "credentials_from": ["ENVCTL_TOKEN"]},
  "end_of_options": true,
  "stderr_framing": "single-error-object",
  "stderr_framing_description": "On failure in machine mode, stderr contains exactly one JSON error object; stdout is empty.",
  "global_flags": {
    "--machine": {"type": "boolean", "default": false},
    "--format": {"type": "string", "enum": ["json", "text"], "default": "text"},
    "--isolated": {"type": "boolean", "default": false},
    "--timeout-ms": {"type": "integer", "default": 10000, "unit": "ms"},
    "--cache-dir": {"type": "string", "default": "~/.envctl"}
  },
  "exit_codes": {"0": "success", "1": "generic", "2": "usage", "3": "not_found", "4": "unauthenticated", "5": "forbidden", "6": "rate_limited", "7": "timeout", "8": "conflict", "9": "transient"},
  "ambient_state": {
    "precedence": ["flags", "env", "config_file", "cache"],
    "env": ["ENVCTL_TOKEN", "ENVCTL_SERVER", "ENVCTL_MACHINE", "ENVCTL_CACHE_DIR"],
    "config_files": ["~/.config/envctl/config.toml"],
    "credentials": ["ENVCTL_TOKEN", "os-keychain"],
    "secret_values": ["ENVCTL_TOKEN", "profile variables with secret=true"],
    "inspect": ["envctl auth whoami", "envctl config show --resolved"]
  },
  "commands": {
    "profile delete": {
      "mutating": true,
      "args": {"name": {"type": "string", "positional": true, "required": true}},
      "flags": {"--yes": {"type": "boolean", "required_in_machine_mode": true}, "--if-exists": {"type": "boolean"}, "--dry-run": {"type": "boolean"}},
      "stdin": {"read": false},
      "output_class": "scalar",
      "latency_class": "network",
      "retry": {"automatic": false},
      "side_effects": ["deletes profile on shared service", "invalidates local cache entry"],
      "signals": "Interrupt leaves remote outcome unknown; reconcile with `envctl profile get`.",
      "errors": [
        {"code": "CONFIRMATION_REQUIRED", "exit": 2},
        {"code": "NOT_FOUND", "exit": 3, "suppressed_by": ["--if-exists"]},
        {"code": "UNAUTHENTICATED", "exit": 4},
        {"code": "FORBIDDEN", "exit": 5},
        {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
        {"code": "TIMEOUT", "exit": 7, "retryable": true, "reconcile_first": true}
      ],
      "examples": [
        {"argv": ["envctl", "--machine", "profile", "delete", "--yes", "--", "ci-staging"], "stdout": {"deleted": "ci-staging"}},
        {"argv": ["envctl", "--machine", "profile", "delete", "--dry-run", "--", "ci-staging"], "stdout": {"dry_run": true, "would_delete": "ci-staging", "variable_count": 12}}
      ]
    },
    "profile create": {
      "mutating": true,
      "stdin": {"read": true, "requires_flag": "--from-stdin", "formats": ["json-object", "dotenv"], "max_bytes": 1048576, "blocks": false, "exclusive_with": ["--from-file"], "empty": "error INPUT_REQUIRED"},
      "flags": {"--from-stdin": {"type": "boolean"}, "--from-file": {"type": "string"}, "--if-not-exists": {"type": "boolean"}, "--idempotency-key": {"type": "string"}, "--dry-run": {"type": "boolean"}},
      "output_class": "record",
      "errors": [
        {"code": "INPUT_REQUIRED", "exit": 2},
        {"code": "CONFLICT", "exit": 8, "suppressed_by": ["--if-not-exists"]},
        {"code": "TIMEOUT", "exit": 7, "retryable": true, "reconcile_first": true}
      ]
    }
  }
}
```

Example error (stderr):

```json
{"code": "CONFIRMATION_REQUIRED", "message": "delete requires --yes in non-interactive mode", "temporary": false, "field": "--yes", "hint": "add --yes", "resource_id": "ci-staging"}
```

## Checklist coverage

| Section | Answer |
| --- | --- |
| Command Model | §6 |
| Machine Schema | §5 and draft schema |
| Stdin Contract | `create` declares stdin; all other commands `"stdin": {"read": false}` |
| Shell Safety | §6 (`--`, no shell interpolation), quoted/`--` examples |
| Agent-Safe Invocation | §1, §5 (metadata path), §9 (timeout) |
| Output | §2, §8 |
| Errors And Exit Codes | §2, error catalog in schema; partial failure N/A — no multi-item commands today (add `bulk-result` rules if a bulk delete is ever added) |
| Ambient State | §7, `login` bootstrap in §1, secret intake in §1 and §3 |
| Mutations And Long-Running Work | §4; long-running jobs/polling/cancel N/A — all operations are single synchronous requests |
| Side Effects And Telemetry | §11 |
| Prose Surfaces | §10 |
| Tests | schema snapshot; canonical success/error payloads; declared-vs-observed exit codes; TTY vs non-TTY (no prompt/browser when stdin is not a TTY); `--machine` suppression; `create --from-stdin` incl. empty stdin; list pagination; env/config/cache precedence and `--isolated`; deprecated alias behavior; `--dry-run` makes no remote write and output differs from real output; SIGINT during create/delete; concurrent cache writes; secret redaction in all outputs. Cancellation tests N/A (no long-running ops). |

## Suggested rollout order

1. P0 items 1–4 before any agent calls it (each is a hang, a leak, or an unsafe mutation).
2. Schema + `noun verb` with legacy aliases in the same release so agents learn the canonical form from day one.
3. Ambient-state inspection, cache semantics, timeouts.
4. Help-text rewrite and test suite hardening.
~~~~~~
