# Scenario R1 (hardening) — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 64,508 (final-turn context plus output, read from the transcript)
- **Output words:** 1,479
- **Transcript sha256:** `342487cdf0943651bb2ed062fcc7b852f8bfd4065cb73d273e1dec00c3bab4be` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/R1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | `show` returns a `record`. / `create` and `delete` return a `record` describing the result — class only, no fields or shape for show/create/delete. Parts: non-interactive machine-readable mode = pass; fields/shape for each of list, show, create, delete = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | \| `PROFILE_NOT_FOUND` \| 3 \| Profile does not exist \| |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `--from-file -` (stdin); Require `--yes`... Add `--dry-run`; Read a service token from an env var (for example `ENVCTL_TOKEN`) or a credential file Parts: create non-interactive = pass; delete non-prompting trigger plus preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `--profile-dir` (default `~/.envctl`) is a cache... names no credential source... Add `envctl whoami`... Add `--isolated` or `--no-cache` Parts: names ambient state (cache, credentials) = pass; how agent inspects or disables it = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | Add `envctl schema` and `envctl schema --fingerprint` (fast, no network or auth), plus `envctl schema <command>`. |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: you own the tool, so this is a prioritized change list for the owner.
Evidence: everything below comes from the `--help` text you pasted; I have not run `envctl`.
Labels: **inferred** means deduced from help text, and **absence** means a required contract piece the help does not show.
Priorities use P0 (blocks automation or risks data loss) through P3 (polish).
Each item cites the section of the agent-friendly CLI contract checklist it satisfies.

## P0: fix before agents call it (hangs and unsafe mutations)

### 1. Make `create` non-interactive
- **Problem (inferred):** "prompts for values" means a CI agent with no TTY either hangs or reads garbage from stdin.
- **Change:**
  - Accept values from repeated `--set KEY=VALUE` flags, or as JSON or `KEY=VALUE` lines through `--from-file <path>` or `--from-file -` (stdin).
  - Never prompt when stdin is not a TTY or machine mode is on. Fail with `code: "MISSING_VALUES"` and exit 2 instead.
  - Declare the stdin contract: an explicit flag rather than auto-detection, the accepted formats, a size cap, handling of empty stdin, and that it cannot be combined with `--set`.
  - Profile values are probably secrets. Recommend stdin or a file in canonical examples, since `--set` puts values in argv, and document that exposure.
- **Checklist:** Agent-Safe Invocation, Stdin Contract, Ambient State (Secret intake).

### 2. Make `delete` confirmable without a prompt
- **Problem (inferred):** the "are you sure?" prompt hangs in CI. If someone works around it with `yes |`, every safety check is gone.
- **Change:**
  - Require `--yes` to delete when there is no TTY. Without it, fail with `code: "CONFIRMATION_REQUIRED"` and exit 2. Never prompt.
  - Add `--dry-run`, which outputs `{"dry_run": true, "would_delete": "<name>", ...}` and exits 0 if the delete would succeed.
  - Add `--if-exists`, so deleting a missing profile is a no-op and an agent can safely re-run a cleanup.
- **Checklist:** Mutations And Long-Running Work, Agent-Safe Invocation.

### 3. Give `login` a non-interactive bootstrap
- **Problem (inferred):** a CI runner cannot complete a browser login. The command will hang or fail, and every networked command depends on it.
- **Change:**
  - Read a service token from an env var (for example `ENVCTL_TOKEN`) or a credential file.
  - Never launch a browser when there is no TTY or machine mode is on.
  - Do not add a `--token` flag (argv leaks).
  - Fail unauthenticated calls with `code: "UNAUTHENTICATED"` and exit 4.
- **Checklist:** Agent-Safe Invocation, Ambient State.

### 4. Add a single machine profile flag
- **Problem (absence):** no flag puts the tool into a predictable, non-interactive mode.
- **Change:** add `--machine` (or `--format json` plus implied non-interactive behavior). It should produce JSON on stdout, no prompts, color, spinners or browser, and structured errors on stderr.
- **Non-TTY default:** suppress the same things when the streams are not TTYs, evaluating each stream separately.
- **Checklist:** Agent-Safe Invocation.

## P1: agents can't parse or branch reliably

### 5. Machine-readable output per command
- **Problem (absence):** no output format is declared, so an agent would have to parse human tables.
- **Change:**
  - `list` returns a `list` class: a JSON array sorted by name, or paginated with `has_more` and `next_cursor` if lists can grow large.
  - `show` returns a `record`.
  - `create` and `delete` return a `record` describing the result.
  - stdout carries only the payload, with no banners and no `--verbose` chatter mixed in. Route `--verbose` to stderr.
- **Secrets:** decide whether `show` returns secret values by default. Prefer masked values with `--reveal`, since agent transcripts get logged.
- **Checklist:** Output, Errors And Exit Codes (redaction).

### 6. Structured errors with symbolic codes and an exit-code map
- **Problem (absence):** the help shows no error shape and no exit-code map.
- **Change:**
  - In machine mode, emit `{"code","message","temporary",...}` on stderr as the only stderr content (`single-error-object`).
  - Map errors to exit codes:

    | Code | Exit | Meaning |
    | --- | --- | --- |
    | `PROFILE_NOT_FOUND` | 3 | Profile does not exist |
    | `UNAUTHENTICATED` | 4 | No valid credentials |
    | `FORBIDDEN` | 5 | Not allowed |
    | `RATE_LIMITED` | 6 | Includes `retry_after_ms` |
    | `TIMEOUT` | 7 | Request timed out |
    | `PROFILE_EXISTS` | 8 | Conflict on `create` |
    | `NETWORK_ERROR` | 9 | Other transport failure |
    | `INTERNAL` | 1 | Fallback for anything unanticipated |
    | (usage errors) | 2 | Bad flags or arguments |

  - Agents branch on `code` and never on `message`.
- **Checklist:** Errors And Exit Codes.

### 7. Make `create` and `delete` safe to retry against the shared service
- **Problem (inferred):** a networked mutation that times out has an unknown outcome. A blind retry of `create` can fail with a conflict or overwrite another profile.
- **Change:**
  - Add `--if-not-exists` to `create`, or an `--idempotency-key` that the caller supplies on the first attempt and reuses on retries.
  - Declare in the schema which commands are safe to retry and which need reconciliation first. A `list` that lags the write does not prove a `create` failed.
  - Declare what SIGINT and SIGTERM leave behind.
- **Checklist:** Mutations And Long-Running Work.

### 8. Make ambient state visible and controllable
- **Problem (absence):** `--profile-dir` (default `~/.envctl`) is a cache. Stale cached profiles can silently differ from the shared service, and the help names no credential source, config file, env vars or precedence.
- **Change:**
  - Document each source and the precedence: flags > env > config > cache.
  - Add `envctl whoami` and `envctl config show --resolved`, with secrets redacted.
  - Add `--isolated` or `--no-cache` to bypass the cache.
  - State whether `list` and `show` read from the cache or the service, and report which one in the output. For example, `"source": "cache"` with a timestamp.
- **Unclear naming:** `--profile-dir` points to a *cache*, but the flag name makes it sound like the source of truth. Consider renaming it `--cache-dir` and keeping the old name as a declared alias.
- **Checklist:** Ambient State, Side Effects And Telemetry.

### 9. Ensure reads have no surprise side effects
- **Problem (inferred):** `list` and `show` probably write to `~/.envctl`.
- **Change:**
  - Declare that cache write.
  - Make the writes safe under concurrent runs, since parallel CI agents may share a home directory. Use atomic replace or a lock.
  - No update checks or telemetry by default.
- **Checklist:** Side Effects And Telemetry, Mutations And Long-Running Work (concurrent local state).

## P2: discovery and contract gaps

### 10. Publish a machine schema
- **Problem (absence):** agents have no machine-readable way to discover commands, flags or errors.
- **Change:**
  - Add `envctl schema` and `envctl schema --fingerprint` (fast, no network or auth), plus `envctl schema <command>`.
  - Include in it:
    - flags and their types
    - the read-only or mutating label for each command
    - output class and shape, in JSON Schema
    - the per-command error catalog, with `retryable` and `reconcile_first`
    - auth requirements
    - latency class (`network` or `cached`)
    - `schema_version`, `fingerprint` and `fingerprint_scope`
- **Checklist:** Machine Schema.

### 11. Add `--timeout-ms` to networked commands
- **Problem (absence):** no caller-settable timeout is shown.
- **Change:** add `--timeout-ms` to networked commands and declare the retry behavior.
- **Checklist:** Agent-Safe Invocation.

### 12. Harden the argument contract
- **Problem (inferred):** a profile name that starts with `-` can be parsed as a flag.
- **Change:**
  - Support `--` before operands and declare that in the schema.
  - Validate profile names.
  - Never pass names to a shell.
- **Checklist:** Shell Safety, Command Model.

### 13. Make the help text task-selective
- **Problem (inferred):** summaries like "Show a profile" do not tell an agent what the command needs or does.
- **Change:**
  - Put prerequisites and side effects first. For example: "`create <name>`: creates a profile in the shared service; requires auth; fails with PROFILE_EXISTS if present."
  - Say whether `list` hits the service or the cache.
- **Checklist:** Prose Surfaces.

## P3: polish

### 14. Command shape and versioning
- Keep the flat verbs: they are clear for a single resource.
- If more resources arrive, move to the `envctl profile list` form, keeping the old forms as declared aliases.
- Add `envctl version`.
- **Checklist:** Command Model.

## Tests to add alongside
- Non-TTY runs of `create`, `delete` and `login` never block.
- `--machine` stdout is pure JSON.
- Exit codes match the declared map.
- `--dry-run` and `--if-exists` behave as declared.
- Empty stdin is handled for `--from-file -`.
- Concurrent cache writes are safe.
- Schema snapshot.
- **Checklist:** Tests.

## Open questions
- Does `show` return secret values? That changes the redaction and default-output decisions in items 1 and 5.
- Does `list` and `show` data come from the service, the `~/.envctl` cache, or both?
- How should CI agents authenticate: a service account token, or a workload identity?
~~~~~~
