# Scenario R1 — with-skill arm 3 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1156
- **Scoring:** blinded packet, output id `o28`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/R1-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

## o28
- A1 Output: PASS. "Add `--machine`, which turns on `--json`"; list "`{\"profiles\":[{\"name\",\"updated_at\",\"owner\"}], ...}`"; show "`{\"name\",\"variables\":{KEY: value},\"updated_at\",\"secret_keys\":[...]}`"; create "`{\"name\",\"created\":true,\"keys\":[...]}`"; delete "`{\"name\",\"status\":\"deleted|absent\"}`".
- A2 Errors: PASS. Exit table "| 3 | not found | `PROFILE_NOT_FOUND` |".
- A3 Prompts: PASS. create "repeated `--set KEY=VALUE` ... `--from-file <path>` or `--stdin`" (pass); delete "require `--yes`" + "`delete`: Add `--dry-run`" (pass); login "Read a token from `ENVCTL_TOKEN` or from a credential file" (pass).
- A4 Ambient: PASS. "`--profile-dir` (default `~/.envctl`) is a cache, and login stores credentials somewhere"; "Add a `--isolated` flag", "`envctl whoami`".
- A5 Schema: PASS. "Add `envctl schema` and `envctl schema <command>`".
- Checklist coverage section: no. Numbered changes, tests, assumptions only.

## Verbatim final output

~~~~~~~~markdown
# Making `envctl` agent-safe: changes in priority order

**Basis.** I worked only from the `--help` you pasted (I ran nothing).
Each item says whether its problem is *inferred* (deduced from the help text) or *absent* (a contract piece the help doesn't show).
Assumptions you should confirm are listed at the end.

## 1. Remove every interactive block from `create`, `delete`, and `login`

*Inferred from "prompts for values", "asks 'are you sure?'", "Log in via browser".* An agent in CI will hang on any of these.

- `envctl create <name>`: take values non-interactively.
  - Use repeated `--set KEY=VALUE` for non-secret values.
  - Use `--from-file <path>` or `--stdin` (JSON object or dotenv, declared) for bulk or secret values.
  - Secrets must never go in argv, so `--set` is for non-secret values only.
  - With no TTY on stdin, or in machine mode, never prompt. Missing values fail with `VALIDATION_ERROR` (exit 2).
- `envctl delete <name>`: require `--yes` when stdin is not a TTY or in machine mode.
  - Without `--yes`, fail with `CONFIRMATION_REQUIRED` (exit 2, `temporary: false`). Do not prompt.
- `envctl login`: add a non-interactive bootstrap.
  - Read a token from `ENVCTL_TOKEN` or from a credential file such as a CI secret mount.
  - Never take the token as a flag value.
  - Never launch a browser when stdout or stdin is not a TTY.
  - Every command needing auth fails fast with `UNAUTHENTICATED` (exit 4) instead of starting login.

## 2. Add a machine mode with structured stdout and structured errors

*Absent: no output format flag, no exit codes, no error shape.*

- Add `--machine`, which turns on `--json` and `--no-color` and suppresses the pager, prompts, and progress output. It must work the same whether or not a terminal is attached.
- stdout carries only the success payload. On failure, stdout is empty and stderr holds exactly one JSON error object (`stderr_framing: single-error-object`).
- Every error object carries `code`, `message`, and `temporary`. Add `hint`, `field`, `resource_id`, `request_id`, and `retry_after_ms` where they apply.
- Exit codes:

| Exit | Meaning | Symbolic codes |
|---|---|---|
| 0 | success | |
| 1 | unexpected failure (fallback) | `INTERNAL` |
| 2 | usage or validation error | `VALIDATION_ERROR`, `CONFIRMATION_REQUIRED` |
| 3 | not found | `PROFILE_NOT_FOUND` |
| 4 | not logged in | `UNAUTHENTICATED` |
| 5 | forbidden | `FORBIDDEN` |
| 6 | rate limited | `RATE_LIMITED` |
| 7 | timed out | `TIMEOUT` |
| 8 | conflict | `PROFILE_EXISTS` |
| 9 | transient or transport failure | `TRANSIENT` |

- Fields per command:
  - `list`: output class `list` — `{"profiles":[{"name","updated_at","owner"}], "has_more", "next_cursor?"}`.
    - Sort by `name` by default. Add `--limit` and `--cursor`.
    - Can return `UNAUTHENTICATED`, `FORBIDDEN`, `RATE_LIMITED`, `TIMEOUT`, `TRANSIENT`, `INTERNAL`.
  - `show <name>`: output class `record` — `{"name","variables":{KEY: value},"updated_at","secret_keys":[...]}`.
    - Secret values are redacted (`"***"`) unless the caller passes `--reveal`.
    - Same errors as `list`, plus `PROFILE_NOT_FOUND`.
  - `create <name>`: output class `record` — `{"name","created":true,"keys":[...]}`.
    - Never echo values back.
    - Same errors as `list`, plus `VALIDATION_ERROR` and `PROFILE_EXISTS`.
  - `delete <name>`: output class `record` — `{"name","status":"deleted|absent"}`.
    - Same errors as `list`, plus `PROFILE_NOT_FOUND` and `CONFIRMATION_REQUIRED`.
- `-v` writes only to stderr. In machine mode, either make it emit typed NDJSON or declare that it is ignored.

## 3. Make mutations safe to retry and preview

*Absent: there is no `--dry-run`, no conditional flags, and no retry contract.*

- `create`:
  - Add `--dry-run`. It outputs `{"dry_run":true,"planned_action":"create|none",...}`, which never looks identical to a real result.
  - Add `--if-not-exists`, which suppresses `PROFILE_EXISTS`.
  - Add `--idempotency-key` if the service supports one.
- `delete`:
  - Add `--dry-run`.
  - Add `--if-exists`, which suppresses `PROFILE_NOT_FOUND` and returns `status:"absent"`.
- When a mutation hits `TIMEOUT` or `TRANSIENT`, the outcome is unknown, so it is not safe to retry blindly. Mark those errors `retryable:false, reconcile_first:true`.
  - `delete` with `--if-exists` is safe to repeat. Declare that as the recovery path.
  - For `create`, an empty `show` result doesn't prove the create failed, because the read can lag the write. Only an idempotency key on the original call, or `--if-not-exists`, makes a retry safe.
- Declare what Ctrl-C (SIGINT/SIGTERM) does mid-request. The remote write may still commit.

## 4. Make ambient state explicit and possible to turn off

*Inferred: `--profile-dir` (default `~/.envctl`) is a cache, and login stores credentials somewhere.*

- Document where envctl gets credentials, and which config files, environment variables, and caches it reads. Use the precedence flags > env > config > cache.
- Add a `--isolated` flag that ignores the cache and config. Keep it separate from `--machine`.
- Add inspection commands: `envctl whoami` and `envctl config show --resolved`. Both redact secrets.
- Declare whether `list` and `show` write to the cache. If they do, writes are atomic (temp file plus rename) so parallel CI jobs can share `~/.envctl` safely, and the schema says so.
- Rename `--profile-dir` to `--cache-dir`. "Profile" already means the remote resource, and the overlap will confuse agents.
- Add `--timeout-ms` to all networked commands and declare the default retry policy.
- No update checks or telemetry by default, and none ever in machine mode.

## 5. Publish a machine-readable contract

*Absent: nothing to read except prose help.*

- Add `envctl schema` and `envctl schema <command>`.
  - Together they declare commands, flags (types, defaults, units), the stdin contract, read-only versus mutating, output class and shape, each command's error catalog, side effects, latency class (all `network`), and the machine profile.
- Add `envctl schema --fingerprint`, returning `{schema_version, fingerprint, fingerprint_scope}` so agents can cache the schema.
- Make `--help` and `schema` respond fast and never hit the network or check auth.
- Support `--` (end of options) so a profile name starting with `-` is never read as a flag, and pass names to the service as data only.
- Rewrite help summaries so the constraint comes first. For example: "delete <name> — deletes a profile; requires --yes when non-interactive; supports --dry-run, --if-exists."
- Optionally migrate to `envctl profile list|show|create|delete`. Keep the current verbs as declared aliases.

## 6. Lock it in with tests

Add tests for:

- schema snapshots
- success and error payloads with their exit codes, verified at runtime
- the no-prompt behavior with no TTY and in machine mode
- missing `--yes` and an empty stdin to `create`
- `--dry-run`
- `--isolated` and env-versus-config precedence
- concurrent cache writes
- interrupting a mutation (SIGINT)

## Assumptions to confirm

- Profile values can include secrets. If they never do, the redaction work in item 2 shrinks.
- The service may or may not support idempotency keys or conditional create. This decides whether item 3 can make `create` safe to retry automatically.
- I'm guessing what `~/.envctl` holds (cached profiles, the token, or both).
- I don't know whether `list` can return enough profiles to need paging.
- CI agents should have a scoped token (for example, read-only for `list` and `show`) and should not use a developer's login.
~~~~~~~~
