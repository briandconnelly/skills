# Scenario R1 — with-skill arm 2 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 919
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertion block verbatim and no arm labels

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
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/R1-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

## o6
- A1 Output: PASS. "Add one `--machine` flag (alias for `--format json ...`)"; list "`{\"profiles\":[{\"name\",\"updated_at\",\"key_count\"}], ...}`"; show "`{\"name\",\"updated_at\",\"values\":{...}}`"; create "`{\"name\",\"created\":true,\"key_count\"}`"; delete "`{\"name\",\"deleted\":true}`".
- A2 Errors: PASS. "Exit-code map (declare it): 0 ok, 1 `INTERNAL`, ... 3 `PROFILE_NOT_FOUND`".
- A3 Prompts: PASS. create "`--from-file <path>` ... `--set KEY=VALUE`" (pass); delete "require `--yes`" + "`--dry-run` on `create` and `delete`" (pass); login "`ENVCTL_TOKEN` env var or `--token-file <path>`" (pass).
- A4 Ambient: PASS. "`--profile-dir` (default `~/.envctl`) ... login credentials are presumably stored there"; "Add `envctl whoami`", "Add `--isolated` / `--no-cache`".
- A5 Schema: PASS. "`envctl schema` (whole tree) and `envctl schema <command>`".
- Checklist coverage section: no. Numbered changes, tests, assumptions only.

## Verbatim final output

~~~~~~~~markdown
# Making `envctl` safe for CI agents — changes in priority order

All findings below come from the `--help` text you pasted; I have not run `envctl` or read its source.
Where I say "assumed", I am inferring behavior from help wording and you should confirm it.

## 1. Remove every interactive block (prompts, browser login)

Today three paths wait on a human: `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser.
In CI there is no TTY, so these either hang or fail unpredictably (assumed: the Go prompt reads stdin and blocks).

Changes:

- **`create <name>`**: accept values non-interactively.
  - `--from-file <path>` (JSON or `.env`, declared) and `--from-file -` for stdin; `--set KEY=VALUE` (repeatable) for small cases.
  - Declare the stdin contract: read only with explicit `-`, accepted formats, max size, empty stdin = `VALIDATION_ERROR` (exit 2).
  - Values are secrets: never accept them only via argv in canonical examples (argv lands in process lists and agent transcripts); prefer the file/stdin path.
  - Prompting happens only when stdin is a TTY **and** machine mode is off; otherwise missing values fail with `MISSING_VALUES` (exit 2), `field: "--from-file"`.
- **`delete <name>`**: require `--yes` when stdin is not a TTY or in machine mode; without it, fail fast with `CONFIRMATION_REQUIRED` (exit 2, `field: "--yes"`), never prompt.
- **`login`**: add a documented non-interactive bootstrap, e.g. `ENVCTL_TOKEN` env var or `--token-file <path>` / service-account credential file. Never launch a browser when stdout/stdin is non-TTY or in machine mode; return `UNAUTHENTICATED` (exit 4) with a `hint` naming `ENVCTL_TOKEN`.

## 2. Add a machine mode with structured output and errors

Agents must not parse "List profiles"-style prose.

- Add one `--machine` flag (alias for `--format json --no-input --no-color`) and honor `ENVCTL_MACHINE=1`.
- stdout = payload only; stderr = diagnostics and the single structured error object (declare framing `single-error-object`). `--verbose` output goes to stderr, never stdout.
- Success payloads per command:
  - `list` → output class `list`: `{"profiles":[{"name","updated_at","key_count"}], "has_more", "next_cursor"}`, sorted by `name`; add `--limit`, `--filter`.
  - `show <name>` → `record`: `{"name","updated_at","values":{...}}`; values redacted by default (`"***"`), with an explicit `--reveal` because returning secrets is the purpose only when asked.
  - `create <name>` → `record`: `{"name","created":true,"key_count"}`.
  - `delete <name>` → `scalar`: `{"name","deleted":true}`.
  - Timestamps in UTC RFC 3339.
- Error object on stderr for every command: `{"code","message","temporary"}` required, plus `hint`, `field`, `resource_id`, `retry_after_ms`, `request_id` where relevant.
- Exit-code map (declare it): 0 ok, 1 `INTERNAL`, 2 usage/validation, 3 `PROFILE_NOT_FOUND`, 4 `UNAUTHENTICATED`, 5 `FORBIDDEN`, 6 `RATE_LIMITED` (with `retry_after_ms`), 7 `TIMEOUT`, 8 `PROFILE_EXISTS` (conflict), 9 `UNAVAILABLE` (transport failure, `temporary:true`).

## 3. Make mutations safe to retry and preview

`create`/`delete` talk to a shared service, so a timeout leaves an unknown outcome.

- `--dry-run` on `create` and `delete`: no remote write, exit 0 if valid, output includes `"dry_run": true` and the planned effect.
- `create --if-not-exists` and `delete --if-exists` so replays are idempotent (suppressing `PROFILE_EXISTS` / `PROFILE_NOT_FOUND`).
- Optionally `--idempotency-key` on `create` if the service can dedupe.
- Declare per command which errors are `retryable` and which need `reconcile_first` (e.g. `create` timeout without an idempotency key: reconcile with `show` is not sufficient proof of non-commit — declare it not safe to auto-retry).
- `--timeout-ms` on every networked command, with declared default and retry behavior.

## 4. Make ambient state explicit and inspectable

`--profile-dir` (default `~/.envctl`) is a cache shared across CI jobs; login credentials are presumably stored there too (assumed).

- Document credential source, config file, env vars (`ENVCTL_*`), cache, and precedence (flags > env > config > cache).
- Add `envctl whoami` (identity, service endpoint, token source — redacted) and `envctl config show --resolved`.
- Add `--isolated` / `--no-cache` so a CI agent does not read stale cached profiles from a reused runner.
- Declare whether `list`/`show` serve from cache or the service (latency class `cached` vs `network`), and make cache writes atomic for concurrent jobs.
- Confirm reads (`list`, `show`) do no implicit writes, update checks, or telemetry.

## 5. Publish a machine-readable contract

- `envctl schema` (whole tree) and `envctl schema <command>`, plus `envctl schema --fingerprint` with `fingerprint_scope: "schema-contract"` and a `schema_version` with declared compatibility rules.
- For each command declare: args/flags with types and defaults, read-only vs mutating, auth requirement, stdin contract, output class and shape (JSON Schema), error catalog with exit codes and `retryable`/`reconcile_first`, side effects, latency class.
- Support `--` so profile names beginning with `-` are not parsed as flags.
- Keep `--help`, `schema`, and `--fingerprint` free of network and auth calls.

## 6. Tighten the command surface and help text (lower priority)

- `show` vs `get`: fine to keep `show` since your team uses it; just be consistent.
- Rewrite help summaries rules-first, e.g. `delete <name>  Delete a profile from the shared service; requires --yes in non-interactive use`.
- `--verbose`: define what it adds and that it goes to stderr.

## 7. Pin it with tests

Before agents start calling it next quarter, add automated tests for: schema snapshot; success and error payloads with exit codes for each command; non-TTY behavior (no prompt, no browser — the hang is the costliest failure); `--dry-run`; `--if-exists`/`--if-not-exists`; empty-stdin to `create`; env/flag precedence and `--isolated`; secret redaction in `show` and in errors.

## Assumptions to confirm

- Whether prompts currently read stdin or `/dev/tty` (affects whether they hang or error in CI).
- Where `login` stores the token, and whether the service supports service-account tokens for CI.
- Whether `list`/`show` read the `~/.envctl` cache or always hit the service.
- Whether the service can deduplicate `create` with an idempotency key.
~~~~~~~~
