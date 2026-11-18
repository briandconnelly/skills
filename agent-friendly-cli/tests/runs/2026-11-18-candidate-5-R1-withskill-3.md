# Scenario R1 — with-skill arm 3 (candidate-5 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `845ca99` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 863
- **Scoring:** blinded packet, output id `q26`; the scorer received the assertion block verbatim and no arm labels

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
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree2/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree2/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree2/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out2/R1-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

## Output q26
## Output q26

## Verbatim final output

~~~~~~~~markdown
# Making `envctl` agent-callable: prioritized changes

Based only on the `--help` you pasted (I have not run `envctl` or read its source), so behavior beyond what the help states is inferred.

## 1. Remove every blocking prompt (do first)

`create` prompts for values and `delete` asks "are you sure?"; in CI with no TTY these hang or fail unpredictably, and `login` opens a browser.

- Add `--machine` (one flag that implies non-interactive, JSON output, no color/progress); also suppress prompts, pagers, color, and browser launch automatically when stdin/stdout/stderr is not a TTY (evaluated per stream).
- `create <name>`: take values non-interactively via `--set KEY=VALUE` (repeatable) and `--from-file <path>` / `--from-file -` (stdin, declared format: `.env` or JSON object, max size declared). Never prompt in machine mode; missing values fail with `MISSING_VALUES` (exit 2).
- `delete <name>`: require `--yes` in machine/non-TTY mode; without it, fail fast with `CONFIRMATION_REQUIRED` (exit 2) instead of waiting.
- `login`: add a non-interactive bootstrap — read a token from `ENVCTL_TOKEN` or a credential file (`--credentials-file`), never from a flag value. In machine mode `login` without these fails with `INTERACTIVE_LOGIN_REQUIRED` rather than launching a browser.

## 2. Structured output on stdout, structured errors on stderr

- `--format json` (implied by `--machine`): stdout carries only the payload; banners, `--verbose` chatter, and progress go to stderr.
- Per-command success payloads:
  - `list` (list): `{"profiles":[{"name","updated_at","key_count"}], "has_more", "next_cursor", "limit"}`; deterministic sort by `name`; `--limit`, `--cursor`, `--filter`.
  - `show <name>` (record): `{"name","updated_at","variables":{KEY: VALUE}}`; secret values redacted by default (`"***"`) with `--reveal` to return them, since this command's purpose may be to return secrets — declare which.
  - `create <name>` (record): `{"name","created":true,"key_count","updated_at"}`.
  - `delete <name>` (record): `{"name","deleted":true}`.
  - `login` (record): `{"identity","expires_at"}` (no token in output).
- Errors (machine mode): a single JSON object on stderr, stdout empty: `{"code","message","temporary", "hint","field","resource_id","retry_after_ms","request_id"}`; `code`, `message`, `temporary` always present.
- Exit codes and symbolic codes, declared per command:
  - `0` success; `1` `INTERNAL` (fallback for anything unanticipated); `2` `USAGE` / `MISSING_VALUES` / `CONFIRMATION_REQUIRED`; `3` `PROFILE_NOT_FOUND` (`show`, `delete`); `4` `UNAUTHENTICATED` / `INTERACTIVE_LOGIN_REQUIRED` (all service commands); `5` `FORBIDDEN`; `6` `RATE_LIMITED` (`temporary: true`, `retry_after_ms`); `7` `TIMEOUT` (`temporary: true`); `8` `PROFILE_EXISTS` (`create`); `9` `SERVICE_UNAVAILABLE` (network failure other than timeout, `temporary: true`).

## 3. Safe mutations and retries

- `--dry-run` on `create` and `delete`: validates and returns `{"dry_run":true,"name","action":"create"|"delete","key_count"}`, exit 0 if valid, no write to the service.
- Idempotency: `create --if-not-exists` and `delete --if-exists` (suppress `PROFILE_EXISTS` / `PROFILE_NOT_FOUND`), so a retried agent step is repeat-safe.
- Declare that a `create` or `delete` that hits `TIMEOUT` has an unknown outcome: it is safe to retry automatically only with `--if-not-exists` / `--if-exists`; otherwise the error carries `reconcile_first: true` and the agent should `show` before retrying. (An empty `list` right after does not prove the write didn't land.)
- Declare whether `create` on an existing name replaces or fails (recommend fail with `PROFILE_EXISTS`; add `update` if replace is needed).

## 4. Make ambient state visible and controllable

- Document credential source (token env var, credential file, browser-login cache), config files, env vars (`ENVCTL_*`), and precedence: flags > env > config > cache.
- `--profile-dir` is a cache: say what's cached, whether `list`/`show` can serve stale data, and whether reads write to it (reads should not write unexpectedly; if they warm the cache, declare it). Concurrent CI jobs sharing `~/.envctl` need atomic writes or locking.
- Add `envctl whoami` (`{"identity","service_url","token_source","expires_at"}`) and `envctl config show --resolved` (secrets redacted).
- Add `--isolated` to ignore `~/.envctl` and config files, using only explicit flags/env.
- Add `--timeout-ms` on all service commands and declare retry behavior.
- No update checks or telemetry by default; never on stdout.

## 5. Publish a machine schema

- `envctl schema` (JSON): commands, args/flags with types and defaults, stdin contract per command, read-only vs mutating, output class and shape (JSON Schema), per-command error catalog (code → exit, `retryable`, `reconcile_first`, suppressing flags), auth requirements, latency class (`network` for service commands), `schema_version`.
- `envctl schema --fingerprint` returning `{"fingerprint","fingerprint_scope":"schema-contract"}`; `envctl schema <command>` for one command. These paths must not hit the network or validate auth.
- Support `--` so a profile name beginning with `-` is not parsed as a flag; never pass names to a shell.

## 6. Tidy the prose and flags

- Rewrite help summaries rules-first, e.g. `delete <name>  Delete a profile. Mutating; requires --yes in non-interactive mode.` and `create <name>  Create a profile from --set/--from-file; fails if it exists.`
- Give `-v/--verbose` a clear contract: stderr only, never changes stdout shape.
- Consider `show` → `get` only if you want conventional verbs; otherwise keep the existing ones (developers already use them) and just declare them.

## 7. Lock it in with tests

Contract tests for: schema snapshot; JSON payload and error snapshots with exit codes; non-TTY and `--machine` never prompt or open a browser (run with stdin closed); `create` via stdin incl. empty stdin; `--dry-run` writes nothing; `--if-exists`/`--if-not-exists`; pagination; env/config precedence and `--isolated`; concurrent invocations on `--profile-dir`; interrupt of `create`/`delete`.

## Assumptions to confirm

- Do profile values include secrets? This decides `show` redaction defaults.
- Does the shared service support idempotency keys? If so, prefer `--idempotency-key` for `create` over relying only on `--if-not-exists`.
- How do CI agents authenticate today (service account token?) — this shapes the `login` bootstrap.
~~~~~~~~
