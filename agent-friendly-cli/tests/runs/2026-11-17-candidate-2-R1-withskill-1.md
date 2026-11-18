# Scenario R1 (hardening) — with-skill arm 1 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 62,985 (final-turn context plus output, read from the transcript)
- **Output words:** 1,055
- **Transcript sha256:** `613f31f0f99ac24a386328b1a217e04c859cd25cb7097bd2a56f779e1fc0f09d` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/R1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | `create` → `record`: the created profile metadata (`name`, `created_at`, `key_count`) Parts: machine-readable non-interactive mode = pass; list shape = pass; show shape = pass; create shape = pass; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Agents branch on `code`, never `message`. |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | Require `--yes` to delete when stdin is not a TTY or in machine mode Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | Add `envctl whoami`, `envctl config show --resolved` (secrets redacted), and `--isolated` to ignore config/cache. Parts: names ~/.envctl cache and credentials = pass; proposes inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | **`envctl schema`** (JSON) with the command tree, flags/types/defaults |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: you own the tool, so this is an owner-side change list.
Evidence: everything below comes from the `--help` you supplied (observed via verbatim capture); behavior beyond it is inferred and marked as such.
I did not run `envctl`.

## Priority 1 — Remove everything that can hang CI

1. **Non-interactive `create`.** Today it "prompts for values", which will hang a CI agent (inferred from help).
   Add explicit input channels: `--set KEY=VALUE` (repeatable) and `--from-file <path>` / `--from-file -` for stdin (format: JSON object or dotenv, declared).
   Declare the stdin contract: read only when `--from-file -` is passed, never auto-detected; empty stdin is a `VALIDATION` error, not a prompt.
   Because values may be secrets, prefer `--from-file`/stdin in canonical examples; `--set` puts values in argv, process listings, and agent transcripts.
2. **Non-interactive `delete`.** "Asks are you sure?" will hang. Require `--yes` to delete when stdin is not a TTY or in machine mode; without it, fail fast with `CONFIRMATION_REQUIRED` (exit 2), never prompt.
3. **Non-interactive login bootstrap.** `login` opens a browser, which an agent cannot do.
   Accept a credential from an env var (e.g. `ENVCTL_TOKEN`) or a credential file (`--credentials-file`), and document precedence.
   Do not add a `--token` flag value as the canonical path (argv leak).
   In non-TTY mode never launch a browser; return `UNAUTHENTICATED` (exit 4) with a `hint` naming the env var.
4. **Rule:** prompts, browser launch, pagers, color, spinners are suppressed per stream when non-TTY (stdin→prompts, stdout→rendering/pager, stderr→color/progress) and always in machine mode.

## Priority 2 — Machine mode and structured output

5. **Add a machine profile:** one global flag, `--machine` (or `--format json` plus implied non-interactive), that implies JSON on stdout, no prompts, no color/progress, structured errors on stderr.
6. **Stdout is payload only.** `-v/--verbose` output, banners, and "Created profile x" summaries go to stderr.
7. **Declare an output class and shape per command:**
   - `list` → `list`: `{"profiles":[{"name","updated_at","key_count"}], "has_more", "next_cursor", "limit"}`; deterministic sort by `name`; timestamps UTC RFC 3339.
   - `show` → `record`: `{"name","updated_at","vars":{KEY:VALUE}}`. Decide whether values are secret; if so, redact by default (`"value":"<redacted>"`, `redacted: true`) and require `--reveal` to return them.
   - `create` → `record`: the created profile metadata (`name`, `created_at`, `key_count`), never echoing secret values.
   - `delete` → `scalar`: `{"name","deleted":true}`.
8. **Structured errors** on stderr in machine mode, one object (`stderr_framing: single-error-object`), with required fields `code`, `message`, `temporary`, plus `hint`, `field`, `resource_id`, `request_id`, `retry_after_ms` (rate limit), `reconcile_first`.
   Agents branch on `code`, never `message`.
9. **Exit-code map** (declared in schema): `0` ok, `1` `INTERNAL` (fallback for anything uncaught), `2` `VALIDATION`/`CONFIRMATION_REQUIRED`, `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED`, `7` `TIMEOUT`, `8` `PROFILE_EXISTS`, `9` `NETWORK_ERROR` (transport failure other than timeout, `temporary: true`).
   Codes absent from a command's catalog are treated as non-retryable.

## Priority 3 — Safe mutations against a shared service

10. **`--dry-run` on `create` and `delete`:** validates and returns `{"dry_run": true, "planned": {...}}`, exit 0 if valid, using the normal error codes otherwise, with no remote write.
11. **Idempotency / replay safety:** `create --if-not-exists` and `delete --if-exists` so retries are safe; without them, `create` on an existing name returns `PROFILE_EXISTS` (exit 8), and `delete` of a missing one returns `PROFILE_NOT_FOUND`.
    Declare that a `create` that times out has an unknown outcome: it is safe to retry only with `--if-not-exists` or a caller-supplied `--idempotency-key`; otherwise the error carries `reconcile_first: true`, and a `list` that comes back empty does not prove it didn't commit.
12. **Optimistic concurrency** (recommended, since the store is shared): return a `revision` on `show`/`create`, accept `--if-revision <n>` on mutations, fail with `CONFLICT` (exit 8) on mismatch.
13. **Signal semantics:** declare what SIGINT/SIGTERM leaves behind for `create`/`delete` (remote call may still complete) and that local cache writes under `--profile-dir` are atomic (write-then-rename) and safe under concurrent CI jobs.
14. **Timeouts:** global `--timeout-ms` on every networked command, with declared default and retry behavior (e.g. no automatic retry of mutations).

## Priority 4 — Discoverability and ambient state

15. **`envctl schema`** (JSON) with the command tree, flags/types/defaults, read-only vs mutating classification, output class and shape (JSON Schema dialect), per-command error catalog (`code`, exit, `retryable`, `reconcile_first`, suppressing flag), latency class (`network` for all four commands, `local` for schema), auth requirements, `schema_version`, and `envctl schema --fingerprint` with `fingerprint_scope: schema-contract`. Support `envctl schema <command>`.
16. **Command model:** consider `envctl profile list|get|create|delete` (noun-verb), keeping `show` as a declared alias if you rename it. Keep `<name>` as the single positional selector and support `--` so a name starting with `-` isn't parsed as a flag; validate names, never pass them to a shell.
17. **Ambient state:** document credential sources, config files, env vars (`ENVCTL_*`), the `~/.envctl` cache, and precedence (flags > env > config > cache). Add `envctl whoami`, `envctl config show --resolved` (secrets redacted), and `--isolated` to ignore config/cache. Clarify whether `list`/`show` serve from the cache — a stale cache answer must be flagged (`"source":"cache"`, `cached_at`) or disabled in machine mode.
18. **`--profile-dir` naming:** "profile" here means the cache, not the profiles; rename to `--cache-dir` (keep old name as a deprecated alias declared in schema) and add `ENVCTL_CACHE_DIR`.
19. **Help text, rules first:** each summary should state binding constraints up front, e.g. `delete <name>  Delete a profile from the shared service. Irreversible. Requires --yes when non-interactive.`; `create <name>  Create a profile. Values via --from-file or --set; fails if <name> exists unless --if-not-exists.`
20. **No side effects on reads:** confirm `list`/`show` do no update checks, telemetry, or implicit cache writes beyond the declared cache; any telemetry is opt-in and off in machine mode.
21. **`version`** command reporting CLI version and `schema_version`; keep `--help`/`schema` fast and offline (no auth check).

## Priority 5 — Tests that pin it

Schema snapshot; success/failure payload and exit-code goldens for each command; non-TTY tests proving `create`, `delete`, and `login` never block; machine-mode suppression of prose/color; stdin (including empty) for `--from-file -`; `--dry-run` produces no remote write; `--if-exists`/`--if-not-exists` replay; interrupt behavior on mutations; concurrent writes to the cache dir; redaction of secret values in `show`, errors, and `--verbose`.

## Open questions

- Are profile values secrets? That decides default redaction in `show` and whether `--set` is acceptable at all.
- Is there pagination server-side for `list`, and how many profiles exist?
- What exactly does `~/.envctl` cache — credentials, profiles, or both — and do reads serve from it?
- Do CI agents need `login` at all, or will they use a service/machine credential?
~~~~~~
