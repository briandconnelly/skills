# Scenario R1 (hardening) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 61,404 (final-turn context plus output, read from the transcript)
- **Output words:** 1,334
- **Transcript sha256:** `51ebc4c97942ed457000ccbcbb6475b689c29987649f56e56ada752ebeaadf70` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o4`; the scorer received the assertions verbatim and no arm labels
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/R1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | list: names + ids + updated_at; show payload example; create `"created": false`; delete `"deleted": false` / deleted id Parts: machine-readable mode = pass; list shape = pass; show shape = pass; create shape = pass; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | \| 3 \| `PROFILE_NOT_FOUND` \| false \| |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `delete` requires `--yes` ... `--dry-run` on create/delete ... `ENVCTL_TOKEN` Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | the cache at `--profile-dir` (`~/.envctl`) ... `envctl config show --resolved` ... `--isolated` Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | Machine schema: `envctl schema`, `envctl schema <command>`, `envctl schema --fingerprint` |

## Verbatim final output

~~~~~~markdown
# envctl: changes for agent callers, in priority order

Audience: tool author (your team owns envctl).
Task: contract hardening with no existing contract, so this is a design pass.
Everything below is based only on the help text; I have not run envctl, so the behavior I describe is inferred from the help, not observed.

## Task model

| Agent job | Class | Minimum input | Minimum output |
|---|---|---|---|
| Discover the contract | discover | none | schema / fingerprint |
| List profiles | query | optional filter, limit, cursor | names + ids + updated_at |
| Show a profile | inspect | name | profile record (secrets redacted by default) |
| Create a profile | mutate | name + values (stdin/file) | created record |
| Delete a profile | mutate | name + `--yes` | deleted id |
| Authenticate | admin | token via env/stdin | identity |
| Inspect resolved state | admin | none | identity, config sources, cache dir |

## P0: blockers (agents hang or do damage without these)

1. **Remove prompts from `create` and `delete`, and fail fast instead.**
   - `create` takes values from `--from-file <path>` or `--stdin` (JSON object or dotenv, declared max size, e.g. 1 MiB). Empty stdin is a usage error (exit 2, `EMPTY_INPUT`), never a wait.
   - `delete` requires `--yes` in machine mode or when stdin is not a TTY. Without it: exit 2, `CONFIRMATION_REQUIRED`, `temporary: false`. Never block.
   - Per-stream non-TTY detection: stdin non-TTY → no prompts; stdout non-TTY → no pager/human tables; stderr non-TTY → no color/spinners.
2. **Non-interactive login.**
   `login` opens a browser; CI has none.
   Add a bootstrap: read `ENVCTL_TOKEN` (env) or `envctl auth login --with-token` (token on stdin).
   Never accept a token as a flag value (it leaks into argv, shell history, agent transcripts).
   In machine mode/non-TTY, never launch a browser; if unauthenticated, exit 4 `UNAUTHENTICATED` with a hint naming `ENVCTL_TOKEN`.
3. **Machine profile: one `--machine` flag** (also `ENVCTL_MACHINE=1`) implying `--format json`, no prompts, no color, no progress, no pager, no browser, no update checks.
   Declare it in the schema with exactly what it implies.
4. **stdout = payload only; structured errors on stderr.**
   In machine mode stdout holds only the JSON success payload (empty on failure); stderr framing is declared as the enum `single-error-object`.
   `--verbose` output goes to stderr only, and never interleaves with the error object in machine mode.
5. **Secret redaction by default.**
   Profiles are env vars and likely contain secrets. `profile get` redacts values (`"value": null, "redacted": true`) unless `--reveal` is passed explicitly; redaction also applies to errors, `--verbose`, and schema examples.

## P1: contract (agents can branch reliably)

6. **Structured errors and declared exit codes.**
   Error object: `code`, `message`, `temporary` (always present), plus `hint`, `field`, `resource_id`, `request_id`, `retry_after_ms` where relevant.
   | Exit | Code(s) | temporary |
   |---|---|---|
   | 0 | success | — |
   | 1 | `INTERNAL` | false |
   | 2 | `USAGE`, `INVALID_VALUE`, `EMPTY_INPUT`, `CONFIRMATION_REQUIRED` | false |
   | 3 | `PROFILE_NOT_FOUND` | false |
   | 4 | `UNAUTHENTICATED` | false |
   | 5 | `FORBIDDEN` | false |
   | 6 | `RATE_LIMITED` (+`retry_after_ms`) | true |
   | 7 | `TIMEOUT` | true |
   | 8 | `PROFILE_EXISTS` | false |
   | 9 | `SERVICE_UNAVAILABLE` | true |
   Agents branch on `code`; exit codes are the shell fallback. 3–9 are a convention, declared in the schema.
7. **Machine schema: `envctl schema`, `envctl schema <command>`, `envctl schema --fingerprint`.**
   Declares: command tree, aliases/deprecations, args/flags with types/defaults/enums/examples, global flags and the machine profile, units (`--timeout-ms`), stdin contract per command, read-only vs mutating, auth requirements, output class + shape (JSON Schema, with required/optional), per-command error catalog (`code` → exit, `retryable`, `reconcile_first`, suppressing flag), side effects, latency class (`list`/`get`/`create`/`delete`: `network`; `schema`: `local`), timeout/retry defaults, pagination, `schema_version` + `fingerprint` + `fingerprint_scope: schema-contract`.
   Compatibility: additive = new commands/optional fields/optional flags; breaking = removals, renames, type/meaning or exit-code changes (bump major). Any contract change changes the fingerprint.
   Metadata paths (`--help`, `schema`) make no network or auth calls; target <100 ms.
8. **Command surface: `envctl profile <verb>`** with conventional verbs; old names kept as declared migration aliases.
   - `envctl profile list [--filter] [--limit] [--cursor] [--field ...]` — class `list`; deterministic sort by name; `has_more`, `next_cursor`, `limit`; cursor is opaque, declared lifetime, expired → exit 2 `CURSOR_EXPIRED`, restart from first page; page walk declared best-effort.
   - `envctl profile get <name>` (alias `show`) — class `record`.
   - `envctl profile create <name> --from-file|--stdin [--if-not-exists] [--dry-run]` — class `record`.
   - `envctl profile delete <name> --yes [--if-exists] [--dry-run]` — class `scalar`.
   - `envctl auth login|status` (`whoami`), `envctl config show --resolved`.
   Name is the one positional selector per command; support `--` so names starting with `-` are not parsed as flags.
9. **Mutation safety.**
   - `--dry-run` on create/delete: validates and resolves, no remote write, exit 0 if valid, output includes `"dry_run": true` and the planned effect (never identical to real output).
   - Idempotency: `create --if-not-exists` (exists → exit 0 with `"created": false`), `delete --if-exists` (missing → exit 0, `"deleted": false`); these suppress `PROFILE_EXISTS` / `PROFILE_NOT_FOUND` and the catalog says so.
   - Unknown outcome: on `TIMEOUT` during create/delete, `reconcile_first: true`; reconcile with `profile get <name>`, or make retry safe via the `--if-*` flags. Declare that reads are safe to retry automatically.
   - Signals: SIGINT/SIGTERM before the request is sent leaves nothing; after it is sent the server-side outcome is unknown (reconcile as above). No long-running/async work, so no job IDs needed.
   - Optimistic concurrency for updates later: if you add `update`, take `--if-match <revision>` → `CONFLICT` exit 8.
10. **Timeouts.** `--timeout-ms` (global, default e.g. 30000); declared retry policy (e.g. reads retry 2x on transient errors with backoff; mutations never auto-retry).

## P2: ambient state and hygiene

11. **Ambient state documented and inspectable.**
    Declare: credentials (`ENVCTL_TOKEN` > stored credential from `auth login`), config file path(s), env vars read, the cache at `--profile-dir` (`~/.envctl`), precedence flags > env > config > cache.
    `envctl config show --resolved` shows each value with its source; secrets redacted.
    `--isolated` ignores config and cache (credentials only from `ENVCTL_TOKEN`), so CI runs are not influenced by stale local caches.
    Rename `--profile-dir` to `--cache-dir` (alias kept) so it does not read like the source of truth; declare cache staleness, and say whether `list`/`get` may serve from cache (prefer: never in machine mode, or expose `"source": "cache"` in output).
    Cache writes are atomic (write temp + rename) so parallel CI jobs do not corrupt it.
12. **No surprise side effects.** `list`/`get` do not write anything except declared cache updates (suppressed by `--isolated`); no telemetry or update checks by default, never in machine mode, never on stdout.
13. **Output hygiene.** Compact deterministic JSON, UTF-8, UTC RFC 3339 timestamps, no banners; `--field` projection declared (selected present, others absent); truncation explicit. `--output <file>` not needed (no export command) — N/A.
14. **Prose surfaces.** Rewrite `--help` rules-first: e.g. `delete <name>  Delete a profile. Requires --yes when non-interactive; irreversible.` and `create <name>  Create a profile from --from-file or --stdin; fails if it exists unless --if-not-exists.` Replace "More output" with what `--verbose` adds and where it goes (stderr).

## P3: tests and architecture

15. Result-then-render in Go: typed inputs, typed result/error structs, separate human and JSON renderers.
16. Contract tests: schema snapshot + fingerprint; canonical success/error payloads; declared exit codes match observed; TTY vs non-TTY (no prompt/browser hang — run with stdin closed and a timeout); machine-mode suppression; empty stdin on create; pagination and cursor expiry; env/config precedence and `--isolated`; aliases; dry-run produces no remote write; interrupt during create/delete; concurrent cache writes; secret redaction in all outputs.

## Checklist coverage

- Command Model: item 8. Machine Schema: 7. Stdin: 1, 7. Shell Safety: 8 (`--`; names never passed to a shell; hints carry flag values, not shell strings). Agent-Safe Invocation: 1–3, 7, 10. Output: 4, 8, 13. Errors: 6. Ambient State: 2, 11. Mutations: 9 (long-running jobs N/A: all ops are single request/response). Side Effects: 12. Prose: 14. Tests: 16.

## Example payloads

```json
{"name":"ci-staging","id":"prf_8f2c","updated_at":"2026-11-17T18:04:00Z","vars":[{"key":"DB_URL","value":null,"redacted":true}]}
```

```json
{"code":"CONFIRMATION_REQUIRED","message":"delete requires --yes in non-interactive mode","temporary":false,"field":"--yes","resource_id":"ci-staging"}
```
~~~~~~
