# Scenario R1 (hardening) — with-skill arm 3 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 62,817 (final-turn context plus output, read from the transcript)
- **Output words:** 1,033
- **Transcript sha256:** `c7f22002afac518b617a2aefd8c4b26cb03c30d07539ef133ddb8675997c0e78` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/R1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | `delete` → `scalar`: `{"name","deleted": true}` Parts: machine-readable non-interactive mode = pass; list shape = pass; show shape = pass; create shape = pass; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Exit codes: 0 ok, 1 `INTERNAL` ... 3 `PROFILE_NOT_FOUND` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `--dry-run` on `create` and `delete`: no service write Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | Add `--isolated` (no config, no cache; credentials only from env) for CI. Parts: names ~/.envctl cache and credentials = pass; proposes inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | `envctl schema` (and `envctl schema <command>`) emits JSON |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

All findings come from the `--help` you pasted; I have not run `envctl`.
Items marked *inferred* follow from the help text (e.g., "prompts for values" means a CI run will hang); items marked *absent* are contract pieces the help does not show.
Each change cites the section of the agent-friendly-cli contract checklist it satisfies.

## 1. Remove every prompt and browser launch from non-interactive runs (blocks CI)

Today `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser (*inferred*: all three will hang or fail with no TTY).
Checklist: § Agent-Safe Invocation, § Stdin Contract, § Mutations.

- Add `--yes` to `delete`; without it, in non-TTY or machine mode, fail immediately with `CONFIRMATION_REQUIRED` (exit 2) instead of prompting.
- `create` takes values non-interactively: repeated `--set KEY=VALUE`, and `--from-file <path>` / `--from-file -` for stdin (format: dotenv or JSON, declared).
  Secret values come only via file or stdin, never `--set`, because argv leaks to process lists and agent transcripts.
  Declare: stdin read only with explicit `--from-file -`, max size, empty stdin = `VALIDATION_ERROR`.
- Decide prompts per stream: prompt only when stdin is a TTY; never open a browser when stdout/stderr is not a TTY.
- Provide a non-interactive bootstrap for auth: read a token from `ENVCTL_TOKEN` or a credential file (e.g., a CI service-account token); `login --device-code` for headless humans. No `--token` flag.

## 2. Add a machine mode with JSON on stdout only

Checklist: § Output, § Agent-Safe Invocation.

- Add one `--machine` flag (also `--format json`) that implies: JSON output, no prompts, no color/progress/pager/browser.
- stdout = payload only; all diagnostics go to stderr. No banners or "Created profile X" summaries on stdout.
- Declared output class per command:
  - `list` → `list`: `{"items":[{"name","updated_at","var_count"}], "has_more", "next_cursor"}`, deterministic sort by `name`, timestamps UTC RFC 3339. Add `--limit`, `--filter`.
  - `show <name>` → `record`: `{"name","updated_at","vars":{KEY: value}}`. Secret values redacted as `"***"` by default; add `--reveal` (explicit purpose: return secrets) and declare it.
  - `create` → `record`: the created profile (redacted), plus `"created": true`.
  - `delete` → `scalar`: `{"name","deleted": true}`.
- `-v/--verbose` writes only to stderr and never changes stdout shape.

## 3. Structured errors and a declared exit-code map

Checklist: § Errors And Exit Codes. Today there is no error contract (*absent*).

- In machine mode, failures print one JSON object to stderr (framing `single-error-object`), stdout empty:
  `{"code","message","temporary", "hint","field","resource_id","retry_after_ms","request_id"}`; `code`, `message`, `temporary` always present.
- Exit codes: 0 ok, 1 `INTERNAL` (fallback for anything unanticipated), 2 `VALIDATION_ERROR` / `CONFIRMATION_REQUIRED`, 3 `PROFILE_NOT_FOUND`, 4 `UNAUTHENTICATED`, 5 `FORBIDDEN`, 6 `RATE_LIMITED` (with `retry_after_ms`), 7 `TIMEOUT`, 8 `PROFILE_EXISTS`, 9 `NETWORK_ERROR`.
- Agents branch on `code`; `temporary` decides retries, not the exit code.
- Never echo secret values in `message`, `details`, or `-v` output.

## 4. Make mutations safe to retry and preview

Checklist: § Mutations And Long-Running Work.

- `create --if-not-exists` and `delete --if-exists` so replays are no-ops (return `"created": false` / `"deleted": false` rather than an error).
- `--dry-run` on `create` and `delete`: no service write, output includes `"dry_run": true` and the planned effect (e.g., `{"dry_run":true,"action":"delete","name":...,"var_count":...}`), exit 0 when valid.
- Declare retry safety: with `--if-exists`/`--if-not-exists`, a timed-out call can be retried; without them, `PROFILE_EXISTS` / `PROFILE_NOT_FOUND` after a timeout means "reconcile with `show`", and the catalog marks the timeout code `reconcile_first`.
- Add `--timeout-ms` on every networked command and declare the default and retry behavior.
- Declare interrupt behavior (does a SIGINT mid-`create` leave a partial profile?) and make it atomic server-side if possible.

## 5. Declare and isolate ambient state

Checklist: § Ambient State, § Side Effects.

- Document where the token, config, and the `~/.envctl` cache come from, plus env vars (`ENVCTL_TOKEN`, `ENVCTL_PROFILE_DIR`, service URL) and precedence (flags > env > config > cache).
- `show`/`list` must state whether they read from the cache or the service; a stale cached profile silently served to CI is a correctness bug. Prefer: always hit the service, or include `"source":"cache"|"service"` and `"fetched_at"`.
- Read commands must not write the cache unexpectedly, or must declare it; make cache writes atomic (concurrent CI jobs share it).
- Add `--isolated` (no config, no cache; credentials only from env) for CI.
- Add `whoami` and `config show --resolved` (redacted) so agents can check identity and the service endpoint before mutating.
- No update checks or telemetry by default.

## 6. Publish a machine-readable schema

Checklist: § Machine Schema. Today only prose help exists (*absent*).

- `envctl schema` (and `envctl schema <command>`) emits JSON: commands, args/flags with types and defaults, read-only vs mutating, output class and shape (JSON Schema), per-command error catalog (`code`, exit, `retryable`, `reconcile_first`), auth needs, latency class (`network`), and `schema_version`.
- `envctl schema --fingerprint` returns a hash plus `fingerprint_scope: "schema-contract"` so agents cache cheaply.
- Keep `--help` and `schema` fast and offline (no auth check).

## 7. Tighten the command surface and help text

Checklist: § Command Model, § Prose Surfaces, § Shell Safety.

- Consider `envctl profile list|get|create|delete` (keep `show` as a declared alias if you rename); this leaves room for `auth login` / `auth whoami`.
- Rewrite help summaries rules-first: e.g., `delete <name>  Delete a profile. Mutating; requires --yes when non-interactive.`
- `--profile-dir` should state whether it's the source of truth or only a cache, and take a value placeholder (`--profile-dir <path>`).
- Support `--` so a profile name beginning with `-` is not parsed as a flag; never pass names into a shell.

## 8. Pin it with tests

Checklist: § Tests.

- Schema snapshot; golden JSON for each command's success and each error code; declared exit codes match observed exits.
- Non-TTY run of `create`/`delete` without `--yes`/values fails fast instead of hanging (the regression that matters most).
- `--machine` produces no stray stdout; secrets never appear in output unless `--reveal`.
- Dry run does not mutate; `--if-exists`/`--if-not-exists` replay is a no-op; concurrent cache writes stay consistent.

## Open questions

- Do profiles hold secrets? If so, `show` redaction and `--reveal` move up to priority 1.
- Is `~/.envctl` a cache of the shared service or a local store? That decides how strict item 5 must be.
- What auth will CI agents use (service account token, OIDC)? That shapes the non-interactive bootstrap in item 1.
~~~~~~
