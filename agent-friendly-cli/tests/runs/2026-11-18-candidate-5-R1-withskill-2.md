# Scenario R1 — with-skill arm 2 (candidate-5 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `845ca99` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1140
- **Scoring:** blinded packet, output id `q49`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out2/R1-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

## Output q49
## Output q49

## Verbatim final output

~~~~~~~~markdown
# envctl: changes to make it agent-safe, in priority order

Based only on the `--help` you shared; I have not run `envctl` or read its source, so items marked "inferred" are worth confirming.

## 1. Remove every interactive block (prompts, confirmation, browser login)

Today `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser.
Under a CI agent with no TTY, each of these either hangs or fails unpredictably (inferred from the help text).

- Add a `--machine` flag (the machine profile) that implies: no prompts, no color/spinners/pager, no browser launch, JSON on stdout, structured errors on stderr.
  Also apply the same suppression automatically when stdin/stdout/stderr is not a TTY (per stream: stdin controls prompts, stdout controls rendering, stderr controls color/progress).
- `create <name>`: accept values non-interactively, via `--from-file <path>` (JSON or `.env`) or `--from-file -` for stdin.
  Never accept secret values as flag arguments (`--set KEY=secret` leaks into process lists and agent transcripts); stdin/file only.
  If no values are supplied in machine mode, fail with `MISSING_INPUT` (exit 2) instead of prompting.
- `delete <name>`: require `--yes` in machine mode; without it, fail with `CONFIRMATION_REQUIRED` (exit 2) rather than asking.
- `login`: add a non-interactive bootstrap — read a token from `ENVCTL_TOKEN` or a credential file (e.g. `--credentials-file`), or a CI-friendly device/OIDC flow that never opens a browser.
  In machine mode, a missing credential returns `UNAUTHENTICATED` (exit 4), not a browser launch.

## 2. Structured JSON output on stdout, nothing else

Add `--format json` (implied by `--machine`).
stdout carries only the payload; `--verbose` output, banners, and progress go to stderr.

- `list` (class `list`): `{"profiles": [{"name", "updated_at", "variable_count"}], "has_more", "next_cursor", "limit"}`.
  Deterministic sort by `name`; `updated_at` in UTC RFC 3339.
  Add `--limit` and `--cursor`; declare cursor opacity, lifetime, and the `CURSOR_EXPIRED` code.
- `show <name>` (class `record`): `{"name", "variables": [{"key", "value", "secret"}], "updated_at", "version"}`.
  Redact secret values by default (`"value": null, "redacted": true`); add an explicit `--reveal` for the case where returning the secret is the point.
  Add `--field <key>` to fetch one variable cheaply, with the projection rule declared.
- `create <name>` (class `record`): `{"name", "created": true, "version", "variable_count"}` — no secret values echoed back.
- `delete <name>` (class `scalar`): `{"name", "deleted": true}`.
- `login`: `{"identity", "expires_at", "credential_source"}`; no token in the output.

## 3. Structured errors with symbolic codes and declared exit codes

On failure in machine mode, stdout is empty and stderr holds exactly one JSON object (`single-error-object` framing):
`{"code", "message", "temporary", "hint", "field", "resource_id", "retry_after_ms", "request_id"}` — `code`, `message`, `temporary` always present.

Exit-code map (declare it in the schema):

| Exit | Codes | Commands |
|---|---|---|
| 0 | success | all |
| 1 | `INTERNAL` (fallback for anything uncaught) | all |
| 2 | `INVALID_ARGUMENT`, `MISSING_INPUT`, `CONFIRMATION_REQUIRED` | all / `create` / `delete` |
| 3 | `PROFILE_NOT_FOUND` | `show`, `delete` |
| 4 | `UNAUTHENTICATED` | all networked |
| 5 | `FORBIDDEN` | all networked |
| 6 | `RATE_LIMITED` (`temporary: true`, `retry_after_ms`) | all networked |
| 7 | `TIMEOUT` (`temporary: true`) | all networked |
| 8 | `PROFILE_EXISTS` | `create` |
| 9 | `SERVICE_UNAVAILABLE` / `NETWORK_ERROR` (`temporary: true`) | all networked |

Agents branch on `code`; `message` is for humans only.

## 4. Safe, retryable mutations

`create` and `delete` hit a shared service, so a CI retry after a timeout can double-act or fail confusingly.

- `create --if-not-exists`: return success with `"created": false` if the profile already exists with that name, instead of `PROFILE_EXISTS`.
- `delete --if-exists`: return success with `"deleted": false` if absent, instead of `PROFILE_NOT_FOUND`.
- `--dry-run` on both: payload with `"dry_run": true` and the planned effect (`would_create` / `would_delete`), never byte-identical to the real output, no remote change.
- Support an idempotency key (`--idempotency-key`) on `create` if the service can deduplicate; otherwise declare `create` without `--if-not-exists` as not safe to auto-retry after a `TIMEOUT` — the caller must `show` to reconcile, and the error payload carries `reconcile_first: true`.
- If profiles can be updated, consider `--if-version <n>` to prevent lost updates between concurrent agents.

## 5. Make ambient state explicit and controllable

`--profile-dir` (default `~/.envctl`) is a cache, and login state lives somewhere implicit.
Agents in CI need to know what is read and to start clean.

- Document credential sources and precedence: flags > env (`ENVCTL_TOKEN`, `ENVCTL_SERVER`, `ENVCTL_PROFILE_DIR`) > config file > cache.
- Add `envctl whoami` (identity, credential source, expiry; token redacted) and `envctl config show --resolved` (each resolved value plus where it came from).
- Add `--isolated` / `--no-config`: ignore `~/.envctl` and config files, require credentials from env/stdin.
- Clarify whether `list`/`show` read the cache or the service; if they can serve stale cache data, include `"source": "cache" | "service"` and `"fetched_at"` in the payload, and add `--no-cache`.
  Reads must not write to the cache as an undeclared side effect, or that must be declared; cache writes must be atomic so parallel CI jobs don't corrupt `~/.envctl`.
- Rename `--profile-dir` to `--cache-dir` — "profile" already means the managed resource, so the flag name is ambiguous.

## 6. Timeouts and no surprise network calls

- Add `--timeout-ms` to every networked command and declare the default and retry behavior.
- No update checks or telemetry by default; never in machine mode.
- `--help` and `schema` must not hit the network or validate auth.

## 7. A machine-readable schema

Add `envctl schema` (full contract as JSON), `envctl schema <command>`, and `envctl schema --fingerprint`.
Per command it declares: args/flags with types and defaults, read-only vs mutating, auth requirement, output class and JSON shape, error codes with exit code / `retryable` / `reconcile_first` / suppressing flag (e.g. `--if-exists`), stdin contract (`create --from-file -` only), latency class (`network` or `cached`), and support for `--` end-of-options so a profile name like `-prod` is not parsed as a flag.

## 8. Tighten the help text

Lead each command summary with what an agent needs to choose and call it correctly, e.g.:

- `create <name>  Create a profile; values from --from-file or stdin; fails if it exists unless --if-not-exists; mutating`
- `delete <name>  Delete a profile; requires --yes in non-interactive use; --if-exists for idempotent cleanup; mutating`

## 9. Tests that pin the contract

Add automated tests for: schema snapshot; JSON success and error payloads per command; declared exit codes matching observed exits; non-TTY and `--machine` never prompting or opening a browser (e.g. `create`/`delete`/`login` with stdin closed must exit non-zero quickly); `--dry-run`, `--if-exists`, `--if-not-exists`; env/flag precedence and `--isolated`; secret redaction in `show`, `login`, and errors; concurrent invocations against the cache dir.

## Suggested sequencing

Items 1–3 before agents start calling `envctl` — without them, CI agents will hang or have to parse English.
Items 4–5 before agents are allowed to run `create`/`delete` unattended.
Items 6–9 can follow, but the schema (7) and tests (9) are what keep the contract from drifting once agents depend on it.
~~~~~~~~
