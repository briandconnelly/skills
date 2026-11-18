# Scenario R1 (hardening) — with-skill arm 2 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/5 scored
- **Tokens:** 63,536 (final-turn context plus output, read from the transcript)
- **Output words:** 976
- **Transcript sha256:** `a8309cc827a1c14d4cd07e53be9639835ba78173f6c0b026bba8bf176bda173d` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels
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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/R1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **PASS** | `create` and `delete` are class `record` and return `{"name","action":"created"\|"deleted","version"}`. Parts: machine-readable non-interactive mode = pass; list shape = pass; show shape = pass; create shape = pass; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | `PROFILE_NOT_FOUND`: exit 3 |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | read the token from an `ENVCTL_TOKEN` env var or a credential file Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `--isolated` / `--no-cache`, so CI runs do not share hidden state Parts: names ~/.envctl cache and credentials = pass; proposes inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | returns a JSON contract that covers |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Basis: only the `--help` you pasted (no runs, no source), so each gap below is inferred from that help or is something the help leaves out.
Priority follows the rule that anything that blocks automation comes first, then anything agents cannot parse or branch on, then contract polish.

## Priority 1: remove anything that blocks (fix before agents call it)

1. **`create` prompts for values, so it hangs in CI.**
   Add non-interactive input: repeated `--set KEY=VALUE` flags, plus `--from-file <path>` / `--from-file -` (stdin) accepting JSON `{"KEY":"VALUE"}` or dotenv.
   Secret values come only through the file or stdin channels, never through argv (argv shows up in `ps`, shell history, and agent transcripts).
   If stdin is not a TTY and no values were given, fail right away with `{"code":"MISSING_VALUES","message":"...","temporary":false,"field":"--set"}` and exit `2`. Never prompt.
2. **`delete` asks "are you sure?", so it hangs.**
   Add `--yes`.
   When stdin is not a TTY, or machine mode is on, and `--yes` is missing, fail with `CONFIRMATION_REQUIRED` and exit `2` without blocking.
3. **`login` only works through a browser.**
   Add a non-interactive bootstrap: read the token from an `ENVCTL_TOKEN` env var or a credential file (path declared in the schema).
   Optionally add `login --with-token`, which reads the token from stdin.
   Do not add a `--token <value>` flag.
   Never launch a browser when stdout or stdin is not a TTY.
   If a command has no credentials, fail with `UNAUTHENTICATED` and exit `4`; do not start the login flow.
4. **Add a machine profile.**
   Add one `--machine` flag that implies JSON output, no prompts, no color, no progress, and no browser.
   Apply the same suppression automatically per stream when that stream is not a TTY.

## Priority 2: give agents something to parse and branch on

5. **Structured output on stdout.**
   Add `--format json` (implied by `--machine`).
   Per-command output classes:
   - `list` is class `list` and returns `{"items":[{"name","updated_at","key_count"}],"has_more","next_cursor"}`. Add `--limit`, sort by `name` by default, and use UTC timestamps.
   - `show` is class `record` and returns `{"name","vars":{...},"updated_at","version"}`. Redact secret values by default, and require an explicit `--reveal` to show them.
   - `create` and `delete` are class `record` and return `{"name","action":"created"|"deleted","version"}`.
   - stdout carries the payload only. Banners and `--verbose` text go to stderr.
6. **Structured errors and an exit-code map.**
   In machine mode, a failure writes exactly one JSON object to stderr (declared framing `single-error-object`), and stdout stays empty.
   Required fields are `code`, `message`, and `temporary`.
   Use `hint`, `field`, `resource_id`, `retry_after_ms`, and `request_id` where they apply.
   Declare these codes and exits:
   - `INVALID_ARGUMENT` / `MISSING_VALUES` / `CONFIRMATION_REQUIRED`: exit 2
   - `PROFILE_NOT_FOUND`: exit 3
   - `UNAUTHENTICATED`: exit 4
   - `FORBIDDEN`: exit 5
   - `RATE_LIMITED`: exit 6, with `retry_after_ms`
   - `TIMEOUT`: exit 7
   - `PROFILE_EXISTS` (conflict): exit 8
   - `NETWORK_ERROR`: exit 9, `temporary: true`
   - `INTERNAL`: exit 1, the fallback for anything unanticipated
7. **Make mutations safe to retry against the shared service.**
   - Add `create --if-not-exists` and `delete --if-exists`, so a repeated call succeeds and returns `"action":"unchanged"` instead of failing.
   - Add `--dry-run` to `create` and `delete`. Its output includes `"dry_run":true` and the planned diff, and it makes no remote write.
   - Declare what a retry may do after a timeout. With `--if-not-exists` or `--if-exists`, retrying is safe. Without either, the caller must reconcile first by calling `show` (catalog field `reconcile_first: true`). An empty `list` does not prove the write did not land.
   - If profiles can be updated concurrently, consider `--if-version <n>` (conflict maps to `PROFILE_EXISTS`/`CONFLICT`, exit 8).
8. **Network timeout.**
   Add `--timeout-ms` to every command that calls the service, and declare the default and the retry behavior.

## Priority 3: discovery, ambient state, contract

9. **`envctl schema` (and `envctl schema <command>`, `envctl schema --fingerprint`)** returns a JSON contract that covers:
   - commands
   - arguments and flags, with types and defaults
   - read-only vs mutating classification (`list`/`show` read-only; `create`/`delete` mutating; `login` writes credentials)
   - output classes and shapes
   - the error catalog for each command, with `retryable` and `reconcile_first`
   - auth requirements
   - latency class (`network`)
   - `schema_version`, `fingerprint`, and `fingerprint_scope`

   `--help` and `schema` must not make network calls or validate auth.
10. **Ambient state.**
    `--profile-dir` is a cache in `~/.envctl`, so declare whether reads come from the cache or the service, whether reads write to the cache, and how stale the cache can get.
    Declare where the credentials live and which env vars are read.
    Precedence is flags > env > config > cache.
    Add:
    - `envctl whoami`
    - `envctl config show --resolved`, which redacts secrets
    - `--isolated` / `--no-cache`, so CI runs do not share hidden state
    - atomic writes to the cache directory, so concurrent CI jobs are safe
11. **Shell safety and naming.**
    - Support `--`, so profile names that start with `-` work.
    - Validate profile names, and declare the allowed character set.
    - Declare the `-v/--verbose` output: stderr only, never mixed with the payload.
    - Rename `--profile-dir` to `--cache-dir`, because "profile" already means the resource, or document it clearly.
12. **Help text.**
    Put constraints first in the help text, for example: "create <name>: mutating; requires auth; non-interactive with --set/--from-file; fails if exists unless --if-not-exists."
    Also add read-only/mutating markers.
13. **No telemetry or update checks** by default. Confirm this and declare it.
14. **Tests** that pin:
    - the schema snapshot
    - JSON success and error payloads
    - exit codes
    - that non-TTY mode never prompts (run `create`/`delete` with `</dev/null` and assert an immediate exit 2)
    - `--dry-run` making no write
    - `--if-exists`/`--if-not-exists` idempotency
    - redaction

## Open questions

- Are profile values secrets? If so, `show` should redact them by default, and an agent should see a value only through an explicit flag.
- Does `list`/`show` read the service or the `~/.envctl` cache? The answer decides whether staleness and cache writes on reads need fixing.
- Can CI use a service account or token? That decides the shape of the login bootstrap.
~~~~~~
