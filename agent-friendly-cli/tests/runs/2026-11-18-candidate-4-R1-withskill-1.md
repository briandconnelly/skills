# Scenario R1 — with-skill arm 1 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1375
- **Scoring:** blinded packet, output id `o21`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/R1-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

## o21
## o21

## Verbatim final output

~~~~~~~~markdown
# Making `envctl` agent-safe: changes in priority order

Evidence: everything below comes from the `--help` text you pasted, which I treat as an `observed` capture.
I did not run `envctl` or read its source.
Where a finding depends on behavior the help does not show, I say so and label it `inferred` or `absence-of-evidence`.

Assumptions (correct me if any is wrong):

- Profiles hold secret values (tokens, passwords) as well as non-secret ones.
- `--profile-dir` is a local cache of profiles held by the shared service, and the service is the source of truth.
- CI agents run without a TTY and without a browser.
- `--verbose` is the only global flag, and there is no JSON output today.

## 1. Remove every prompt from non-interactive runs (blocks agents today)

Evidence: `create` "prompts for values", `delete` "asks 'are you sure?'", `login` opens a browser (`observed` in help; the CI hang is `inferred`).
In CI these either hang until the job times out or fail with an unclear error.

Changes:

- Add `--machine` as the single machine-profile flag. It implies `--format json`, no prompts, no color, no progress output, and no browser launch.
- Apply the same suppression whenever stdin is not a TTY, even without `--machine`. If a command would need input in that case, it fails at once with `INPUT_REQUIRED` (exit 2) and does not wait.
- `delete <name> --yes`: without `--yes` in machine or non-TTY mode, fail with `CONFIRMATION_REQUIRED` (exit 2, `temporary: false`, `field: "--yes"`).
- `create <name>`: take values without prompting, either as repeated `--set KEY=VALUE` for non-secret values or as `--from-file <path>` / `--from-file -` (stdin, a JSON object or dotenv format). Secret values must come through the file or stdin, never argv (see change 4). Declare the stdin contract: read only when you pass `--from-file -`, a size limit (for example 1 MiB), empty stdin rejected with `INVALID_INPUT`, and `--from-file` cannot be combined with `--set` for the same key.
- `login`: add a non-interactive bootstrap. Read a service token from the `ENVCTL_TOKEN` environment variable or from a credential file, with no login step needed in CI. Keep the browser flow for humans only. With `--machine`, `login` fails with `INTERACTIVE_ONLY` and does not open a browser.

## 2. Structured output on stdout, structured errors on stderr, a declared exit-code map

Evidence: the help names no output format, no exit codes, and no error codes (`absence-of-evidence`).
Without them, agents end up parsing English text.

Success payloads in machine mode (stdout only, with no banners or "Done!" lines):

- `list` (class `list`): `{"profiles":[{"name","updated_at","key_count"}],"has_more","next_cursor","limit"}`. Sort by `name` by default, timestamps in UTC RFC 3339. Support `--limit` and `--cursor` if the service pages results.
- `show <name>` (class `record`): `{"name","updated_at","variables":{KEY: VALUE}}`. Redact secret values as `"***"` unless the caller passes `--reveal`, and declare that flag as one that returns secrets.
- `create <name>` (class `record`): `{"name","created":true,"key_count","updated_at"}`. Never echo secret values back.
- `delete <name>` (class `scalar`): `{"name","deleted":true}`.

Errors: in machine mode, stderr contains exactly one JSON object and stdout is empty.
Declare the stderr framing as `single-error-object`.
Required fields are `code`, `message`, and `temporary`. Recommended fields are `hint`, `field`, `resource_id`, `request_id`, and `retry_after_ms`.

| code | exit | temporary | commands |
|---|---|---|---|
| `INVALID_INPUT` / `INPUT_REQUIRED` / `CONFIRMATION_REQUIRED` | 2 | false | all / create / delete |
| `PROFILE_NOT_FOUND` | 3 | false | show, delete |
| `UNAUTHENTICATED` | 4 | false | all networked |
| `FORBIDDEN` | 5 | false | all networked |
| `RATE_LIMITED` | 6 | true (+`retry_after_ms`) | all networked |
| `TIMEOUT` | 7 | true (create/delete: `reconcile_first: true`) | all networked |
| `PROFILE_EXISTS` | 8 | false | create |
| `SERVICE_UNAVAILABLE` (transport failure other than timeout) | 9 | true | all networked |
| `INTERNAL` (fallback for any unexpected failure) | 1 | false | all |

Agents branch on `code`. The exit code is the fallback for scripts that only see the shell status.
Add `--timeout-ms` to every networked command, and declare the default timeout and the retry policy.

## 3. Make mutations safe to replay and to preview

Evidence: the help shows no `--dry-run`, no idempotency controls, and nothing about what happens after an interrupt (`absence-of-evidence`).

- Add `--dry-run` to `create` and `delete`. The output adds `"dry_run": true` and describes the planned change, for example `{"dry_run":true,"name","would_create":true,"key_count"}`. Valid plans exit 0. Invalid plans return the same errors as a real run. A dry run makes no write to the service.
- Add `delete --if-exists`, which exits 0 with `"deleted":false` when the profile is absent.
- Add `create --if-not-exists`, which exits 0 with `"created":false` when the profile already exists.
- Declare retry safety for each mutation:
  - `delete --if-exists` is safe to repeat.
  - `create` is safe to retry only with `--if-not-exists` or an `--idempotency-key` the caller supplied on the first attempt.
  - Otherwise, after a `TIMEOUT` the caller must check with `show` before retrying. An empty `list` does not prove that the original create failed.
- Declare what an interrupt (Ctrl-C) leaves behind. Is a create atomic on the service? Are cache writes atomic, for example write to a temporary file and then rename?

## 4. Keep secrets out of argv and redact them everywhere

Evidence: `inferred` from the assumption that profiles hold secrets.

- Never accept a secret as a flag value. Use `--from-file`, stdin, or `ENVCTL_TOKEN`.
- Redact secrets in `show` by default, in `--verbose` and debug output, in error `details`, and in schema examples.

## 5. Declare and expose ambient state

Evidence: `--profile-dir` defaults to `~/.envctl` (`observed`). Where credentials live and which environment variables are read is not stated (`absence-of-evidence`).

- Document the precedence order: flags > `ENVCTL_*` environment variables > config file > cache.
- Add `envctl whoami` and `envctl config show --resolved`, which name each resolved value's source and redact secrets.
- Add `--isolated`, which ignores `~/.envctl` and the config file and uses only flags and environment variables. CI agents can then point `--profile-dir` at a per-job directory.
- State whether reads (`list`, `show`) write to the cache. That is a hidden write on a read path. Make concurrent CI jobs safe with atomic replacement or locking.
- Ensure no update check or telemetry runs in machine mode, and that none ever writes to stdout.

## 6. Publish a machine-readable contract

- Add `envctl schema`, `envctl schema <command>`, and `envctl schema --fingerprint` (with `fingerprint_scope: "schema-contract"`).
- The schema declares, for each command: flags and types, the stdin contract, read-only or mutating, auth requirement, output class and shape (as JSON Schema), the error catalog (code → exit, `retryable`, `reconcile_first`), latency class (`network` for all commands except the cached ones), and the default timeout.
- Declare `schema_version` compatibility: additive changes change the fingerprint, and breaking changes bump the major version.
- Keep `--help` and `schema` fast and offline, with no auth check.
- Support `--` before names so a profile named `-x` cannot be parsed as a flag.

## 7. Tidy the command surface and help text (lower priority)

- The verbs are fine. Keep `list`, `show`, `create`, and `delete`, and add `whoami`, `config`, and `schema`.
- Do not add a `-v` alias meaning anything else.
- Rename `--verbose` behavior so that in machine mode it emits structured diagnostics on stderr only.
- Rewrite help summaries rules-first. For example: `delete <name>  Delete a profile on the service (irreversible; requires --yes when non-interactive)`, and `create <name>  Create a profile; fails PROFILE_EXISTS if present`.

## Tests to ship with these changes

Ship these with the changes:

- schema snapshots
- the success payload of each command
- each error code mapped to its exit code
- non-TTY runs with no prompts, including empty stdin
- `--machine` suppressing color, progress, and browser launch
- dry-run output that differs from real output
- `--if-exists` and `--if-not-exists` behavior
- flag/env/config precedence, and `--isolated`
- two concurrent invocations sharing one `--profile-dir`
- interrupt behavior during `create`

## Open questions

- Does the service support idempotency keys or conditional create/delete? This decides whether retrying `create` can be made safe.
- Do reads write to `~/.envctl`, and is the cache ever shared between CI jobs?
- Is there a service-account or token path today, or is the browser login the only way to authenticate?
~~~~~~~~
