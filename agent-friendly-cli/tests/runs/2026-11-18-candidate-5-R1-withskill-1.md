# Scenario R1 — with-skill arm 1 (candidate-5 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `845ca99` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1058
- **Scoring:** blinded packet, output id `q52`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out2/R1-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

## Output q52

- A1 Output: PASS. Machine mode: "Add one global `--machine` flag ... implies JSON output" (pass). Shapes for all four: list `{"profiles":[{"name","updated_at","key_count"}]...}`, show `{"name","updated_at","variables":{KEY:VALUE}}`, create `{"name","created": true,"keys":[...]}`, delete `{"name","deleted": true}` (pass).
- A2 Errors: PASS. "Exit codes: `0` ok, `1` `INTERNAL` ... `3` `PROFILE_NOT_FOUND`".
- A3 Agent-safe invocation: PASS. create: "repeated `--set KEY=VALUE` flag or with `--from-file`" (pass); delete: "explicit `--yes`" + "Add `--dry-run` to `create` and `delete`" (pass); login: "Read a service/CI token from `ENVCTL_TOKEN` or `--token-file`" (pass).
- A4 Ambient state: PASS. Names: "`--no-cache` / `--isolated` so CI can bypass `~/.envctl`" and "`envctl whoami` (identity, token source, expiry...)" (pass); inspect/disable: `config show --resolved`, `--no-cache` (pass).
- A5 Machine schema: PASS. "`envctl schema` returns, as JSON, the command tree, flags...".
- Checklist coverage section: no. Sections are numbered priority changes ("## 1. Remove every interactive block ..."); no table/list mapping to a standard's sections.

## Verbatim final output

~~~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

This is based only on the `--help` you pasted (I haven't run envctl).
Anything I say about runtime behavior is inferred from that text.
Changes are ordered by how badly each gap breaks an unattended CI agent.

## 1. Remove every interactive block (hangs CI today)

- **`create <name>`**: stop prompting for values.
  Accept values with a repeated `--set KEY=VALUE` flag or with `--from-file <path>` / `--from-file -` (stdin, `KEY=VALUE` lines or a JSON object; declare the format, max size, and that an empty stdin is a `VALIDATION` error).
  For values that are secrets, use stdin or a file, never argv.
  Never fall back to a prompt when stdin is not a TTY.
  If no values are supplied in machine mode, fail fast with `MISSING_INPUT` (exit 2).
- **`delete <name>`**: replace "are you sure?" with an explicit `--yes`.
  Without `--yes` in machine or non-TTY mode, fail with `CONFIRMATION_REQUIRED` (exit 2) instead of waiting.
- **`login`**: add a non-interactive bootstrap.
  Read a service/CI token from `ENVCTL_TOKEN` or `--token-file <path>`, never as a flag value.
  Never launch a browser when stdout or stdin is not a TTY.
  Unauthenticated commands fail with `UNAUTHENTICATED` (exit 4) and a `hint` that names `ENVCTL_TOKEN`.
- Decide TTY status separately for each stream: stdin controls prompts, stdout controls human rendering and pagers, and stderr controls color and progress.

## 2. Add a machine profile and structured output

- Add one global `--machine` flag (and/or `ENVCTL_MACHINE=1`). It implies JSON output, no prompts, no color or progress, and no browser.
- stdout carries only the success payload. Banners, `--verbose` chatter, and progress go to stderr.
- Per-command success shapes:
  - `list` (class `list`): `{"profiles":[{"name","updated_at","key_count"}], "has_more", "next_cursor", "limit"}`. Sort by `name` by default, add `--limit`, `--cursor`, and `--filter`, and use UTC RFC3339 timestamps.
  - `show <name>` (class `record`): `{"name","updated_at","variables":{KEY:VALUE}}`. Values are redacted by default (`"***"` plus `"redacted": true`). Return plaintext only behind an explicit `--reveal`, because returning secrets is not the default purpose.
  - `create <name>` (class `record`): `{"name","created": true,"keys":[...]}` without echoing values.
  - `delete <name>` (class `scalar`): `{"name","deleted": true}`.
- Rename `-v/--verbose` so its meaning is clear. Debug detail goes to stderr only and is redacted.

## 3. Structured errors and a declared exit-code map

- In machine mode, write a failure as exactly one JSON object on stderr (framing `single-error-object`) and leave stdout empty.
  Required fields are `code`, `message`, and `temporary`. Add `hint`, `field`, `resource_id`, `retry_after_ms`, and `request_id` where relevant.
- Exit codes: `0` ok, `1` `INTERNAL` (fallback), `2` `VALIDATION`/`MISSING_INPUT`/`CONFIRMATION_REQUIRED`, `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED` (with `retry_after_ms`), `7` `TIMEOUT`, `8` `PROFILE_EXISTS`, `9` `SERVICE_UNAVAILABLE` (network or transport failure, `temporary: true`).
- Per-command catalog:
  - `show` and `delete` can return `PROFILE_NOT_FOUND`.
  - `create` can return `PROFILE_EXISTS`.
  - Every command that touches the service can return `UNAUTHENTICATED`, `FORBIDDEN`, `RATE_LIMITED`, `TIMEOUT`, and `SERVICE_UNAVAILABLE`.

## 4. Make mutations safe to retry and preview

- `create`: add `--if-not-exists` so the call succeeds with `"created": false` when the profile is already there. Also accept `--idempotency-key` if the service can deduplicate.
- `delete`: add `--if-exists` so a missing profile returns success with `"deleted": false`, which suppresses `PROFILE_NOT_FOUND`.
- Add `--dry-run` to `create` and `delete`. It returns `"dry_run": true` plus the planned effect (`would_create` with key names, or `would_delete`), and it exits 0 when the mutation is valid.
- Declare retry safety. Without an idempotency key or the `--if-*` flags, a `create` or `delete` that times out has an unknown outcome, so it gets `reconcile_first: true` and should not be retried automatically.
  Declare what Ctrl-C leaves behind.
- Add `--timeout-ms` to every networked command and declare the default retry behavior.

## 5. Make ambient state visible and controllable

- `--profile-dir` is a cache, and today the help gives it no units, precedence, or isolation. Document that `list` and `show` read and write it.
  It must not hold credentials in plaintext unless that is declared.
  Writes to it must be atomic, because parallel CI jobs share it.
- Declare precedence (flags > env vars > config > cache) and every env var you read (`ENVCTL_TOKEN`, `ENVCTL_SERVER`, ...).
- Add `envctl whoami` (identity, token source, expiry, never the token itself) and `envctl config show --resolved`, which shows the resolved server, profile dir, and the source of each value, with secrets redacted.
- Add `--no-cache` / `--isolated` so CI can bypass `~/.envctl`, or declare in the schema that it can't be disabled.
- No update checks or telemetry by default, and none ever in machine mode.

## 6. Publish a machine-readable contract

- `envctl schema` returns, as JSON, the command tree, flags (types, defaults, repeat syntax), the machine profile, the stdin contract for `create`, read-only vs mutating, auth and ambient state, the output class and shape (as JSON Schema), the exit-code map, the per-command error catalog, the latency class (`network` for all four data commands), and `schema_version`.
- `envctl schema <command>` returns one command's contract, and `envctl schema --fingerprint` returns `{"fingerprint","fingerprint_scope":"schema-contract","schema_version"}`. These metadata paths stay fast and do no network or auth checks.
- Support `--` so a profile name that starts with `-` is not parsed as a flag. Declare the allowed name characters.

## 7. Tighten the help text

- Lead each summary with constraints, e.g. `delete <name>  Delete a profile from the shared service (irreversible; requires --yes in non-interactive use)`.
- Note in `list`/`show` that they read from the shared service (or the cache?), and in `login` that CI should use `ENVCTL_TOKEN` instead.
- Keep `list`/`show`/`create`/`delete`; the verbs are already guessable. If you add more resources later, consider moving to `envctl profile <verb>`, and keep the current verbs as declared aliases.

## 8. Pin it with tests before agents arrive

Add tests for:
- schema snapshots
- success and error payloads with their exit codes
- non-TTY runs of `create`, `delete`, and `login`, which must never block (run with stdin closed)
- empty stdin to `create`
- `--dry-run` making no change
- `--if-exists`/`--if-not-exists`
- secret redaction in `show`, errors, and debug output
- concurrent use of the cache dir

## Open questions

- Is `--profile-dir` purely a cache, or can it be stale relative to the shared service, so `show` might return outdated values?
- Can the service deduplicate creates (idempotency keys) and issue scoped CI tokens?
- Should agents ever see plaintext values, or only inject them (e.g., a future `envctl exec <name> -- cmd`)?
~~~~~~~~
