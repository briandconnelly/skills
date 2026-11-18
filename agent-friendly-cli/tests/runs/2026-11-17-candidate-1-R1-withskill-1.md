# Scenario R1 (hardening) — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 63,773 (final-turn context plus output, read from the transcript)
- **Output words:** 1,094
- **Transcript sha256:** `8b35d10f76d1180ea1b8d28acfc00e97d5d13fdad60894fd3a518c61d6b72df0` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/R1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | Output classes: `list` -> `list` (JSON array...), `show` -> `record`, `create`/`delete` -> `record` describing the affected profile — no fields or shape for show/create/delete. Parts: non-interactive machine-readable mode = pass; fields/shape for each of list, show, create, delete = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Suggested map: `0` ok, `1` `INTERNAL` (fallback), `2` `USAGE`/`CONFIRMATION_REQUIRED`, `3` `PROFILE_NOT_FOUND` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `--from-file <path>`...`--from-stdin`; `delete <name>` requires `--yes`; `--dry-run` for `create` and `delete`; accept a token from an env var (e.g. `ENVCTL_TOKEN`) Parts: create non-interactive = pass; delete non-prompting trigger plus preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | document credential sources, config files, env vars, the cache... Add `--no-cache` / `--isolated`... `envctl whoami` and `envctl config show --resolved` Parts: names ambient state (cache, credentials) = pass; how agent inspects or disables it = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | `envctl schema` and `envctl schema --fingerprint`... Support `envctl schema <command>` |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: tool author (you own `envctl`).
Task: contract hardening of an existing CLI.
Evidence: only the `--help` text above; I have not run `envctl`.
Each item is labeled `inferred` (deduced from documented behavior) or `absence-of-evidence` (a required contract piece missing from the help).
Severity follows P0 (blocks automation / unsafe) through P3 (polish); P0 and P1 should land before agents start calling it next quarter.

## P0 — must fix before any agent calls it

### 1. Remove the prompts from `create` and `delete` in non-interactive use
- Evidence: inferred from "prompts for values" and "asks 'are you sure?'". In CI with no TTY these either hang or read EOF and do something undefined.
- Fix:
  - `create <name>` takes values non-interactively: `--from-file <path>` (JSON or dotenv, declared) and/or `--from-stdin`, plus `--set KEY=VALUE` (repeatable). Never accept secret values as flags by default (argv leaks into process lists and agent transcripts); prefer stdin or file for values.
  - `delete <name>` requires `--yes` when stdin is not a TTY or in machine mode; without it, fail fast with a structured `CONFIRMATION_REQUIRED` error (exit 2) instead of prompting.
  - Per-stream non-TTY detection: stdin not a TTY ⇒ never prompt; stdout not a TTY ⇒ no color/pager.

### 2. Non-interactive auth bootstrap to replace browser `login`
- Evidence: inferred; "Log in via browser" is the only documented auth path, so a CI agent either hangs waiting for a browser or tries to launch one.
- Fix: accept a token from an env var (e.g. `ENVCTL_TOKEN`) or a credential file path (`ENVCTL_CREDENTIALS_FILE`); `login` must never launch a browser in non-TTY or machine mode and should fail with `UNAUTHENTICATED` (exit 4) and a hint naming the env var.
  Do not add a `--token` flag for this; if one exists for compatibility, document the exposure.

## P1 — agents cannot reliably parse, branch, or recover without these

### 3. A machine profile with JSON output
- Evidence: absence-of-evidence; no `--format`/`--json` flag, so agents would parse human tables.
- Fix: a single `--machine` flag (or `ENVCTL_MACHINE=1`) that implies `--format json`, no color, no prompts, no browser, no progress.
  stdout carries only the payload; diagnostics go to stderr.
  Output classes: `list` → `list` (JSON array, deterministic sort by name), `show` → `record`, `create`/`delete` → `record` describing the affected profile.

### 4. Structured errors and a declared exit-code map
- Evidence: absence-of-evidence; no error or exit-code contract in help.
- Fix: in machine mode, on failure stdout is empty and stderr holds exactly one JSON object `{code, message, temporary, hint?, field?, resource_id?, request_id?, retry_after_ms?}` (framing `single-error-object`).
  Suggested map: `0` ok, `1` `INTERNAL` (fallback), `2` `USAGE`/`CONFIRMATION_REQUIRED`, `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED` (with `retry_after_ms`), `7` `TIMEOUT`, `8` `PROFILE_EXISTS`, `9` `NETWORK_ERROR` (transient transport failure).
  Agents branch on `code`; `temporary` (always present, `false` included) decides retry.

### 5. Secret handling in `show` (and `list`)
- Evidence: inferred; profiles are environment variables, which commonly hold secrets, and nothing in help says values are redacted.
- Fix: `show` redacts secret values by default in all output, with an explicit `--reveal` (declared as returning secrets) for callers that need them; `list` returns names and metadata only.
  Redact in errors, `--verbose` output, and debug dumps too.

### 6. Safe retries for mutations against a shared service
- Evidence: absence-of-evidence; nothing says what happens if `create`/`delete` time out mid-request.
- Fix: `create --if-not-exists`, `delete --if-exists` (repeat-safe), and/or `--idempotency-key` the caller supplies on the first attempt.
  Declare per command whether a retry after timeout is safe or requires reconciling first (`show <name>` against a strongly consistent read); mark the error `reconcile_first: true` where it applies.
  Add a caller-settable `--timeout-ms` on all networked commands and declare retry defaults.

### 7. Ambient state declared and controllable, including the cache
- Evidence: inferred from `--profile-dir` (default `~/.envctl`): `list`/`show` likely read and write a local cache, a hidden side effect on read paths, and an agent cannot tell cached from live data.
- Fix: document credential sources, config files, env vars, the cache, and precedence (flags > env > config > cache).
  Add `--no-cache` / `--isolated`, report `source: "cache" | "service"` (and age) in output, and add inspection commands: `envctl whoami` and `envctl config show --resolved` (secrets redacted).
  Make cache writes atomic so parallel CI jobs sharing a home dir don't corrupt it.

## P2 — important contract gaps

### 8. `envctl schema` and `envctl schema --fingerprint`
- Evidence: absence-of-evidence.
- Fix: a machine-readable contract covering commands, flags (types, defaults, enums), stdin per command, read-only vs mutating, auth needs, output class/shape (JSON Schema), per-command error catalog (`retryable`, `reconcile_first`, suppressing flags such as `--if-exists`), latency class (`network`/`cached`), `schema_version`, and a fingerprint with `fingerprint_scope`.
  Support `envctl schema <command>`. Keep `--help`/`schema` fast and offline (no auth check, no network).

### 9. `--dry-run` for `create` and `delete`
- Evidence: absence-of-evidence.
- Fix: validate inputs and permissions, report the planned effect with `dry_run: true`, no service writes; exit 0 if the mutation would succeed, otherwise the normal error contract.

### 10. Shell safety
- Support and declare `--` so a profile named `-foo` cannot be parsed as a flag; never pass names or values to a shell.

### 11. `list` pagination and filtering
- If profile counts can grow: `--limit`, `--filter`, cursor with `has_more`/`next_cursor`, deterministic default sort.

## P3 — polish

### 12. Command model and prose
- Rename the `--profile-dir` flag to something like `--cache-dir` (it names a cache, and "profile" already means the resource).
- Keep `envctl <verb> <name>` (shallow tree, one noun) but consider `get` as an alias-free canonical name only if your users already say it; `show` is fine.
- Rewrite help rules-first: state that `create`/`delete` mutate the shared service, require auth, and list non-interactive flags before the description.
- Define what `--verbose` adds and send it to stderr only.

## Tests to add alongside
Schema snapshot; canonical success payloads; each error code ⇒ declared exit; non-TTY run of `create`/`delete`/`login` never blocks (run with `</dev/null`); `--dry-run` writes nothing; redaction of secrets in `show`/errors/verbose; env/config/cache precedence and `--isolated`; concurrent invocations against the shared cache dir.

## Assumptions / open questions
- Do profile values include secrets? (Drives the default for item 5.)
- Does `list`/`show` hit the service, the cache, or both? (Drives item 7 severity.)
- Is the shared service eventually consistent? If so, `show` can't confirm a timed-out `create` didn't commit; an idempotency key becomes necessary.
- If you can share source or allow me to run `envctl --help`, a harmless `list`, and an invalid-input case with stdout/stderr captured separately, I can turn the inferred items into observed ones.
~~~~~~
