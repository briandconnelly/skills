# Scenario R1 (hardening) — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 62,889 (final-turn context plus output, read from the transcript)
- **Output words:** 1,264
- **Transcript sha256:** `9237b3edae712ca1128336ee08eaab44a1898110deb44dcb0c188388131889b3` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels
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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/R1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | `list` → class `list`: `{"items":[{"name","id","updated_at","key_count"}]...`; show: "keys, metadata; values redacted unless asked"; create: "created record id/name/version"; delete: "deleted name, `deleted: true`" Parts: machine-readable mode = pass; list fields = pass; show fields = pass; create fields = pass; delete fields = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | `0` ok, `1` `INTERNAL` ... `3` `PROFILE_NOT_FOUND`; Agents branch on `code`, never on `message`. |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `create <name>` reads values from `--from-file <path>`; `delete <name> --yes`; `--dry-run` on `create` and `delete`; Read a token from `ENVCTL_TOKEN` or `--token-file <path>` Parts: create non-interactive = pass; delete trigger + dry-run = pass; login non-browser = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | Add `envctl config show --resolved` ... and `--isolated` to ignore config and the `~/.envctl` cache. Parts: names ~/.envctl and credentials = pass; inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | `envctl schema` (full), `envctl schema <command>`, `envctl schema --fingerprint` |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: tool author (you own `envctl`).
Task: contract hardening of an existing CLI with no machine contract yet, so this is a design proposal.
Everything below is inferred from `--help` alone; I have not run `envctl`, so behaviors like "does `show` print secret values" or "does `list` write the cache" are assumptions you should confirm.

## Task model (what agents need)

| Job | Class | Minimum input | Minimum output |
|---|---|---|---|
| list profiles | query | optional `--filter`, `--limit` | names + ids + updated_at, paginated |
| show a profile | inspect | profile name | keys, metadata; values redacted unless asked |
| create a profile | mutate | name + key/value set (stdin/file) | created record id/name/version |
| delete a profile | mutate | name + `--yes` | deleted name, `deleted: true` |
| authenticate | admin | token from env/file | identity |
| discover contract | discover | none | schema, fingerprint |

## P0 — blockers (agents hang or leak secrets in CI today)

1. **Remove every prompt from non-interactive paths.**
   `create` prompts for values and `delete` asks "are you sure?"; in CI both hang until timeout.
   - `delete <name> --yes` is required when stdin is not a TTY or in machine mode; without it, fail fast with `CONFIRMATION_REQUIRED` (exit 2), never prompt.
   - `create <name>` reads values from `--from-file <path>` or stdin (`--from-file -`), format `json` or `dotenv` declared via `--input-format`. Declare max input size, that empty stdin is a `USAGE` error, and that stdin is never auto-read without the flag.
   - Prompts happen only when stdin is a TTY and machine mode is off.
2. **Non-interactive auth bootstrap.** `login` opens a browser; CI has none.
   Read a token from `ENVCTL_TOKEN` or `--token-file <path>` (never a `--token <value>` flag: argv leaks into process lists and agent transcripts).
   Non-TTY mode must never launch a browser; unauthenticated calls fail with `UNAUTHENTICATED` (exit 4) and a hint naming the env var.
   Add `envctl whoami` to show the resolved identity and its source.
3. **Secret redaction.** Profiles are environment variables, so `show` almost certainly prints secrets into agent transcripts and CI logs.
   Default `show` returns keys and metadata with values redacted (`"value": null, "redacted": true`); revealing values requires an explicit `--reveal` (or `--fields values`), declared in schema as the command's secret-returning purpose.
   Redact in `--verbose`/debug output, errors, and schema examples too.
4. **Machine profile with structured stdout.** Add one global `--machine` flag (and honour non-TTY) that implies: JSON output, no prompts, no color/spinner/pager/browser, no banners.
   stdout carries only the success payload; stderr carries only diagnostics and, on failure, a single structured error object (declare framing `single-error-object`).

## P1 — make calls branchable and retry-safe

5. **Exit codes and structured errors.** Declare at tool level:
   `0` ok, `1` `INTERNAL` (fallback for anything the error boundary catches), `2` `USAGE`/`CONFIRMATION_REQUIRED`, `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED`, `7` `TIMEOUT`, `8` `PROFILE_EXISTS`/`VERSION_CONFLICT`, `9` `SERVICE_UNAVAILABLE`/`NETWORK_ERROR`.
   Every error carries `code`, `message`, `temporary` (always present, `false` included), plus `hint`, `field`, `resource_id`, `request_id`, and `retry_after_ms` for rate limits.
   Agents branch on `code`, never on `message`.
   Example:
   ```json
   {"code":"PROFILE_NOT_FOUND","message":"profile 'staging' not found","temporary":false,"field":"name","resource_id":"staging","hint":"run 'envctl list' to see available names"}
   ```
   Callers treat a code absent from a command's catalog by acting on its payload fields, and on `create`/`delete` by reconciling first.
6. **Idempotent mutations and retry rules.** The service is shared and networked, so a timed-out `create`/`delete` has an unknown outcome.
   - `create --if-not-exists`, `delete --if-exists` make replays safe; also accept `--idempotency-key <key>` on `create` if the service can deduplicate.
   - Declare per command: `delete --if-exists` is safe to retry automatically; plain `create` without a reused idempotency key is not (`reconcile_first: true` on `TIMEOUT`/`NETWORK_ERROR`), because an empty `list` afterwards does not prove the write did not commit.
   - Add an `update` (or `create --replace` with `--if-version <n>`) so agents don't delete-then-create, which is a non-atomic window others can observe.
   - Declare SIGINT/SIGTERM semantics: whether the remote call continues after the process dies.
7. **`--dry-run` on `create` and `delete`.** Validates input, auth, and existence without mutating; output includes `dry_run: true` and the planned effect, exits `0` when valid.
8. **Caller-settable timeout.** `--timeout-ms` on all networked commands, with a declared default and declared retry behavior (e.g. 2 retries on `temporary` errors for reads only).

## P2 — discoverability and stable output

9. **Machine schema.** `envctl schema` (full), `envctl schema <command>`, `envctl schema --fingerprint` (with `fingerprint_scope: schema-contract`), `schema_version` with declared additive vs breaking rules.
   Per command declare: read-only vs mutating, output class, output shape (JSON Schema), stdin contract, error catalog (code → exit, `retryable`, `reconcile_first`, suppressing flags), latency class (`network` for list/show/create/delete, `local` for schema), auth requirement, side effects.
   Metadata paths (`--help`, `schema`) must not hit the network or validate auth.
10. **Output shapes.**
    - `list` → class `list`: `{"items":[{"name","id","updated_at","key_count"}],"has_more":bool,"next_cursor":...,"limit":n}`, deterministic sort by name, `--limit`, `--cursor`, `--filter`. Declare cursor opacity/lifetime and `CURSOR_EXPIRED`.
    - `show` → class `record`.
    - `create`/`delete` → class `scalar`/`record` with name, id, version.
    - Timestamps UTC RFC 3339; no `message` field duplicating structured data.
11. **Ambient state is explicit and inspectable.**
    Document credential sources, config files, env vars (`ENVCTL_TOKEN`, `ENVCTL_PROFILE_DIR`, service URL), precedence flags > env > config > cache.
    Add `envctl config show --resolved` (secrets redacted, with source of each value) and `--isolated` to ignore config and the `~/.envctl` cache.
    Declare whether `list`/`show` are served from the cache (latency `cached`) and how staleness is surfaced; a stale cache read that silently answers is a correctness bug for agents.
    Cache writes must be atomic (write-temp-then-rename or locking): parallel CI jobs share `~/.envctl`.
12. **Reads have no side effects.** `list`/`show` must not write beyond the declared cache, and no telemetry or update checks by default; never prepend notices to stdout.

## P3 — surface polish

13. **Command naming and help.** Rename `--profile-dir` to `--cache-dir` (it's a cache, and "profile" already means the resource — a collision agents will misread); keep the old name as a declared deprecated alias.
    Clarify `-v/--verbose` writes only to stderr and is redacted.
    Support `--` so names starting with `-` aren't parsed as flags; quote names in examples.
    Rewrite help rules-first, e.g. `delete <name>  Delete a profile. Requires --yes when non-interactive. Irreversible.`
    Consider `get` over `show` only if you want verb consistency with other internal tools; otherwise keep `show` (existing user vocabulary wins).
14. **Tests.** Schema snapshot; success/failure payloads; declared-exit-code-vs-observed; TTY vs non-TTY (no prompts, no browser); `create` from stdin incl. empty stdin; dry-run; `--if-exists`/`--if-not-exists` replays; env/config precedence and `--isolated`; concurrent cache writes; interrupt during `create`; redaction in all streams.

## Checklist coverage

- Command Model: P3 #13, task model above.
- Machine Schema: P2 #9.
- Stdin Contract: P0 #1 (`create`); all other commands declare "stdin not read".
- Shell Safety: P3 #13 (`--`, quoting); names are never passed to a shell; hints don't embed shell strings built from input.
- Agent-Safe Invocation: P0 #1, #2, #4; P1 #8; metadata paths in #9.
- Output: P0 #4, P2 #10.
- Errors And Exit Codes: P1 #5; partial failure not applicable (no multi-item commands) unless you add bulk create/delete, which would then need per-item results.
- Ambient State: P0 #2, P2 #11.
- Mutations And Long-Running Work: P1 #6, #7; async jobs not applicable (all operations are single synchronous calls).
- Side Effects And Telemetry: P2 #12.
- Prose Surfaces: P3 #13.
- Tests: P3 #14.

## Smallest first step

If you can ship only one release before next quarter: P0 #1–#4 plus the exit-code map in #5.
That removes the hangs, the browser dependency, and the secret leakage, and gives agents a code to branch on.
~~~~~~
