# Scenario R1 (hardening) — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 62,937 (final-turn context plus output, read from the transcript)
- **Output words:** 1,330
- **Transcript sha256:** `40533fb109d91925ca429eca4356ea3971cad567c83ca35ba990960569a518fc` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels
- **Checklist coverage table present:** no

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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/R1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | `show`: class `record`: `{"name","vars":[{"key","value"\|null,"redacted"}],"updated_at","version"}`; create/delete: "return the resulting resource or `{"name","deleted":true}`" Parts: machine-readable mode = pass; list fields = pass; show fields = pass; create fields = pass; delete fields = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Exit codes: `0` ok, ... `3` `PROFILE_NOT_FOUND`; Callers branch on `code` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `create` accepts values via stdin (`--from-file -`...); `delete` requires `--yes`; `--dry-run` on `create` and `delete`; `ENVCTL_TOKEN` env var and/or `--credentials-file <path>` Parts: create non-interactive = pass; delete trigger + dry-run = pass; login non-browser = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | that `~/.envctl` is a cache; `envctl config show --resolved`; `--isolated` disables config file and cache; `envctl auth status` ... credential source Parts: names ~/.envctl and credentials = pass; inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | `envctl schema` (full contract, JSON), `envctl schema <command>` |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: tool author (you own `envctl`). Task: contract hardening of an existing CLI with no machine contract yet, so this is a design proposal.
Everything below is based only on the `--help` you pasted; I have not run `envctl`, so behaviors like "does `list` refresh the cache" are open questions you should answer in the schema.

## P0 — Blockers (agents will hang, leak, or mis-mutate without these)

### 1. Remove every interactive path in machine mode
Today `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser. Each one hangs a CI agent.
- Add a machine profile: a single `--machine` flag (also `ENVCTL_MACHINE=1`) that implies `--format json`, no prompts, no color/spinners, no browser launch.
- Independently, when stdin is not a TTY, never prompt; when stdout is not a TTY, no color/pager; when stderr is not a TTY, no progress.
- `delete` requires `--yes` in machine/non-TTY mode; without it, fail fast with `CONFIRMATION_REQUIRED` (exit 2), never wait.
- `create` takes values non-interactively (see #3). A missing value is `VALIDATION_FAILED` (exit 2) with `field`, never a prompt.

### 2. Non-interactive authentication bootstrap
`login` via browser is the only documented auth. Add:
- `ENVCTL_TOKEN` env var and/or `--credentials-file <path>` (service-account / CI token). Never a `--token <value>` flag: argv leaks into process lists and agent transcripts.
- `envctl auth status` (whoami): prints identity, credential source (`env`, `file`, `keychain`, `browser-session`), expiry — never the token itself.
- Unauthenticated calls fail with `UNAUTHENTICATED` (exit 4), `hint` naming `ENVCTL_TOKEN`, and never launch a browser in machine mode.

### 3. Secret handling for profile values
Profiles hold environment variables, which are often secrets.
- `create` accepts values via stdin (`--from-file -`, JSON object or dotenv, declared max size) or `--from-file <path>`; not via `--set KEY=VALUE` for secrets by default (if you add `--set` for convenience, document the argv exposure and keep it out of canonical examples).
- `show` redacts values by default (`"value": null, "redacted": true`); revealing requires an explicit `--reveal` (secret-returning purpose made explicit). Same redaction in `--verbose`/debug output and error payloads.
- Empty stdin with `--from-file -` is `VALIDATION_FAILED`, not an empty profile.

### 4. Structured output and errors with stable exit codes
- `--format json|text` (machine mode = json). stdout is success payload only; banners/"Created!" lines go away or to stderr in human mode only.
- On failure in machine mode: stdout empty, stderr holds exactly one JSON error object (framing: `single-error-object`).
- Error object: `code` (symbolic), `message`, `temporary` (always present), plus `hint`, `field`, `resource_id`, `retry_after_ms`, `request_id`, `details` where relevant.
- Exit codes: `0` ok, `1` `INTERNAL` (fallback for any uncaught failure), `2` usage/validation, `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED` (with `retry_after_ms`), `7` `TIMEOUT`, `8` `PROFILE_EXISTS`/conflict, `9` `UNAVAILABLE` (transport failures other than timeout).
- Callers branch on `code`; the numeric exit is the shell fallback. A code absent from a command's catalog: act on its payload fields; on `create`/`delete`, reconcile (`show`) first.

### 5. Safe, retryable mutations
- `create --if-not-exists` and `delete --if-exists` make replays repeat-safe (suppress `PROFILE_EXISTS` / `PROFILE_NOT_FOUND`).
- `--dry-run` on `create` and `delete`: validates and returns `{"dry_run": true, "planned": {...}}`, exit 0 if valid, no remote write.
- Accept `--idempotency-key <key>` on `create` if the shared service can deduplicate; declare its window.
- Declare: a `create`/`delete` that times out or is interrupted has an unknown outcome. Safe automatic retry only with the original idempotency key or the `--if-*` flag; an empty `list` does not prove the write didn't commit. Mark `reconcile_first: true` on `TIMEOUT`/`UNAVAILABLE` for mutating commands.
- Signal semantics: SIGINT/SIGTERM after the request is sent leaves the remote outcome unknown; local cache writes are atomic (write temp + rename) and safe under concurrent invocations.

## P1 — Discoverability and contract

### 6. Machine-readable schema
- `envctl schema` (full contract, JSON), `envctl schema <command>`, `envctl schema --fingerprint` (returns `schema_version`, `fingerprint`, `fingerprint_scope: "schema-contract"`).
- Contents per command: invocation path, args/flags with types/defaults/enums, read-only vs mutating, auth requirement, output class + JSON Schema shape + example, stdin contract, error catalog (`code` → exit, `retryable`, `reconcile_first`, suppressing flag), side effects, latency class (`network` for all service calls; `local` for schema/help), timeout/retry defaults, pagination.
- Declare compatibility: additive changes change the fingerprint; breaking changes also bump the major `schema_version`.
- `--help`, `schema`, and `--fingerprint` must not touch the network or validate auth (target <100ms).

### 7. Command model and naming
Keep the existing verbs (users already know them); align the shape:
- `envctl profile list | show <name> | create <name> | delete <name>`; keep the current top-level verbs as declared migration aliases.
- `login` → `envctl auth login` (interactive, human only) + `auth status` + `auth logout`.
- Profile name is the one positional selector; support `--` so names starting with `-` are safe. Treat names as data (never interpolated into a shell).
- Rewrite help summaries rules-first, e.g. `delete <name>  Delete a profile. Mutating; requires --yes in non-interactive mode. Supports --dry-run, --if-exists.`

### 8. Output shapes
- `list`: class `list`. JSON `{"items":[{"name","updated_at","var_count","owner"}], "has_more", "next_cursor", "limit"}`; default sort by `name`; `--limit`, `--filter` (name prefix), `--field`. Declare cursor opacity, lifetime, and `CURSOR_EXPIRED` behavior. Timestamps UTC RFC 3339.
- `show`: class `record`: `{"name","vars":[{"key","value"|null,"redacted"}],"updated_at","version"}`; vars sorted by key.
- `create`/`delete`: class `record` / `scalar` — return the resulting resource or `{"name","deleted":true}`; no `message` duplicating fields.
- Closed stdout (`| head`) ends `list`/`show` quietly.

## P2 — Ambient state and hygiene

### 9. Make ambient state explicit and disableable
- Document: credential sources and precedence (flags > env > config file > cache), config file location, env vars read (`ENVCTL_TOKEN`, `ENVCTL_MACHINE`, `ENVCTL_PROFILE_DIR`, server URL), and that `~/.envctl` is a cache.
- `envctl config show --resolved` shows each resolved value with its source; secrets redacted.
- `--isolated` disables config file and cache (credentials only from env/explicit file). Rename `--profile-dir` to `--cache-dir` so "profile" means one thing.
- Declare whether reads are served from the cache and how stale they can be (`cached` vs `network` latency class, `--no-cache` / `--refresh`). A stale cached `show` silently returning old values is a correctness bug for CI.
- Does the current working directory select anything? If yes, declare it and add an override flag; if no, say so.

### 10. Timeouts, retries, side effects
- `--timeout-ms` on every networked command, with declared default and built-in retry policy (e.g. retries only on `temporary: true`, max N).
- No implicit writes on read verbs beyond declared cache refresh; no telemetry or update checks in machine mode (opt-in only, never on stdout).
- `--verbose`: diagnostics to stderr only; in machine mode emit NDJSON-typed or suppress — never interleave with the error object. (If you want verbose diagnostics in machine mode, switch stderr framing to `ndjson-typed` and declare it.)

## P3 — Tests to ship (contract enforcement)
Schema snapshot; canonical success and failure payloads per command; declared exit codes match observed; TTY vs non-TTY (no prompt/browser with stdin not a TTY); `--machine` suppresses prompts/color/prose; stdin create incl. empty stdin; pagination and cursor expiry; config/env precedence and `--isolated`; alias deprecation; `--dry-run` produces no remote write and differs from real output; redaction of values in `show`, `--verbose`, and errors; interrupt during `create`/`delete`; concurrent invocations writing the cache.

## Not applicable
- Async jobs/polling/cancel: all operations are single request-response; declare deadlines via `--timeout-ms` instead.
- Streaming/NDJSON and `bulk-result`: no bulk commands today; revisit if you add multi-profile create/delete (then declare per-item results and stop-vs-continue).
- `--output <file>`: no export command.

## Example canonical agent calls
```sh
export ENVCTL_TOKEN=...   # from CI secret store
envctl --machine profile list --limit 50
envctl --machine profile show -- "staging-api"
envctl --machine profile create --if-not-exists --from-file - -- "staging-api" < vars.json
envctl --machine profile delete --yes --if-exists -- "old-profile"
```

## Open questions for you
1. Does the shared service support idempotency keys or optimistic versions (for update/conflict detection)?
2. Is `~/.envctl` only a read cache, or does it hold credentials/sessions?
3. Do you want an `update`/`set` verb, or is delete+create the intended replace path (non-atomic — risky for agents)?
~~~~~~
