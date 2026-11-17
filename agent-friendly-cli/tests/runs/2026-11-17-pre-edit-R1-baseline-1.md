# Scenario R1 (hardening) — baseline arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 3/5 scored
- **Tokens:** 49,691 (final-turn context plus output, read from the transcript)
- **Output words:** 529
- **Transcript sha256:** `a136a1d16e27fbe054ccd0ba37b808695926582d2bfdfc14e7eef83f82adfeef` (session-local copy; not committed)
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

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | `--output json` ... with a documented, stable schema -- no per-command fields Parts: machine-readable mode = pass; list shape = fail; show shape = fail; create shape = fail; delete shape = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | {"error":{"code":"not_found",...}} and exit codes 0..7 |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | Add `--dry-run` to `delete` and `create`; `--yes`; `ENVCTL_TOKEN` Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | document when `~/.envctl` is read, and add `--no-cache`; `envctl auth status` Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **FAIL** | Only prose `--help` with examples and `envctl help agents`; no schema command |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: proposed changes in priority order

## P0: Without these, agents hang or cause damage

1. **No interactive prompts when there is no TTY.**
   Add `--yes`/`--force` to `delete` and `--no-input` globally (also enabled by `ENVCTL_NO_INPUT=1` or by detecting a non-TTY stdin).
   In non-interactive mode, a prompt that would have appeared must fail fast with a clear error and a non-zero exit code, never block.
2. **Non-interactive `create`.**
   Accept values with `--set KEY=VALUE` (repeatable), `--from-file path` (`.env`/JSON), and `--from-stdin`, so secrets stay out of argv and shell history.
3. **Headless auth.**
   Browser login can't work in CI.
   Support a token from `ENVCTL_TOKEN` or a service-account credential file, add `envctl login --token-stdin`, and add `envctl auth status` (exit 0 if authenticated, a distinct code if not).
   Unauthenticated commands should fail immediately with an actionable message, without opening a browser.
4. **Make destructive operations safe.**
   Add `--dry-run` to `delete` and `create` that prints what would change.
   Have `create` fail if the profile exists unless `--overwrite` is given, rather than silently replacing it.
   Consider soft delete or `--if-exists` for idempotency.
   If the service supports it, scope CI credentials so they can't delete.

## P1: Reliable parsing and control flow

5. **Structured output.**
   Add `--output json` (or `--json`) to `list`, `show`, `create`, and `delete`, with a documented, stable schema.
   Write data to stdout and logs/progress to stderr.
6. **Documented exit codes.**
   For example: 0 success, 1 generic error, 2 usage error, 3 not found, 4 already exists/conflict, 5 auth required, 6 permission denied, 7 service unavailable (retryable).
7. **Structured errors.**
   With `--output json`, emit errors on stderr as `{"error":{"code":"not_found","message":"...","retryable":false,"hint":"..."}}`.
8. **Secret handling.**
   `show` should redact values by default and add `--reveal` (or `--keys-only`), because agent transcripts and CI logs are persisted and widely read.
   Never echo secrets in errors or `--verbose` output.

## P2: Ergonomics and discoverability

9. **Complete `--help` for each subcommand** with examples, including the non-interactive forms, so agents can learn the tool from help alone.
10. **Filtering and pagination for `list`**: `--prefix`, `--limit`, `--cursor`, and a stable sort order.
11. **Retries and timeouts**: `--timeout`, sensible retries with backoff on transient service errors, and the retryable status included in errors.
12. **Cache semantics**: document when `~/.envctl` is read, and add `--no-cache` or `--refresh` so agents don't act on stale data.
    Make `--profile-dir` settable through `ENVCTL_PROFILE_DIR` so it can be isolated per CI job.
13. **Version and stability**: add `envctl version --json`, and treat the JSON schema and exit codes as a versioned contract with a changelog.
14. **Quiet by default** in non-interactive mode: no spinners, colors, or update notices (respect `NO_COLOR`).

## P3: Guardrails and observability

15. **Audit trail**: record the caller identity (for example, `ENVCTL_ACTOR` or the token's subject) on server-side writes, so agent actions can be told apart from human ones.
16. **Optional confirmation by name** for production-tagged profiles (`--confirm <name>`), even with `--yes`.
17. **Agent documentation**: a short `AGENTS.md`-style section or `envctl help agents` that lists the safe, non-interactive invocation patterns.

## Suggested first milestone

Items 1 through 6 make the tool callable without hangs, unsafe defaults, or fragile text parsing.
Ship those before agents start calling it next quarter, and treat the rest as follow-ups.
~~~~~~
