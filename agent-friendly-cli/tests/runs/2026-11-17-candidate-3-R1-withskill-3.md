# Scenario R1 (hardening) — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 64,449 (final-turn context plus output, read from the transcript)
- **Output words:** 1,390
- **Transcript sha256:** `845e76de2977d73703bff517545f3eaa76da16b82c0e5afdc548674c28a5b3a0` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels
- **Checklist coverage table present:** yes

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/R1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | Only list has a shape (`{"items": [...], "has_more"...}`); "`show` → `record`, `create`/`delete` → `record` describing the result" gives classes without fields for create/delete/show Parts: machine-readable mode = pass; list fields = pass; show fields = fail; create fields = fail; delete fields = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | \| 3 \| `PROFILE_NOT_FOUND` \|; Agents branch on `code`, never on `message`. |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `--from-file -`; `delete`: require `--yes`; `delete` and `create` get `--dry-run`; read a token from `ENVCTL_TOKEN` Parts: create non-interactive = pass; delete trigger + dry-run = pass; login non-browser = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `--profile-dir` (default `~/.envctl`) is a cache...; Add `envctl whoami` (... token source — redacted) and `envctl config show --resolved`; Add `--isolated` ... and `--no-cache`. Parts: names ~/.envctl and credentials = pass; inspect/disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | `envctl schema` (full), `envctl schema <command>` (one command), and `envctl schema --fingerprint` |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized changes

Audience: tool author (your team owns `envctl`), so this leads with contract gaps that would block agent use and gives concrete redesign guidance.
Task type: contract hardening of an owned CLI with no existing machine contract, so this is a design pass.
Everything below is inferred from the `--help` text only; I have not run `envctl`, so behaviour claims (e.g. what `list` prints today) are assumptions to check.

## Priority 0 — blockers (an agent will hang, fail silently, or do damage)

### 1. Remove every prompt from the non-interactive path

Today `create` prompts for values, `delete` asks "are you sure?", and `login` opens a browser.
In CI, each of these either hangs until timeout or reads EOF and does something undefined.

- `create`: take values without prompting, from repeated `--set KEY=VALUE` or from a file/stdin (`--from-file <path>`, `--from-file -`), JSON or dotenv format.
  Values are often secrets, so prefer stdin/file over argv in canonical examples (argv leaks into process lists and agent transcripts).
- `delete`: require `--yes` to skip confirmation; in machine mode or when stdin is not a TTY, a missing `--yes` fails fast with `CONFIRMATION_REQUIRED` (exit 2), never a prompt.
- `login`: add a non-interactive bootstrap — read a token from `ENVCTL_TOKEN` or a credential file (`--token-file`), or a CI-friendly device/OIDC flow that doesn't need a browser.
  In non-TTY mode, never launch a browser; fail with `UNAUTHENTICATED` (exit 4) and a `hint` naming the env var.
- Non-TTY is evaluated per stream: stdin controls prompts, stdout controls human rendering/pager, stderr controls colour/progress.

### 2. Add a machine profile and structured output

Add one global flag, `--machine`, that implies `--json`, no prompts, no colour, no pager, no progress, and no browser launch.

- stdout carries only the success payload; stderr carries diagnostics.
- On failure in machine mode, stderr contains exactly one JSON error object (`stderr_framing: "single-error-object"`) and stdout is empty.
- Output classes: `list` → `list` (array, with pagination fields below), `show` → `record`, `create`/`delete` → `record` describing the result.
- Deterministic default sort for `list` (by name), UTF-8, UTC timestamps.

### 3. Stable exit codes and symbolic error codes

Every structured error carries `code`, `message`, `temporary` (always present, `false` included), plus `hint`, `field`, `resource_id`, `request_id`, `retry_after_ms` where relevant.
Agents branch on `code`, never on `message`.

| Exit | Code(s) |
| --- | --- |
| 0 | success |
| 1 | `INTERNAL` (fallback for anything the error boundary catches) |
| 2 | `VALIDATION_ERROR`, `CONFIRMATION_REQUIRED` |
| 3 | `PROFILE_NOT_FOUND` |
| 4 | `UNAUTHENTICATED` |
| 5 | `FORBIDDEN` |
| 6 | `RATE_LIMITED` (`temporary: true`, `retry_after_ms`) |
| 7 | `TIMEOUT` (`temporary: true`) |
| 8 | `PROFILE_EXISTS` / `CONFLICT` |
| 9 | `TRANSIENT` (transport failures other than timeout, `temporary: true`) |

Declare per command which codes it can return, and the policy for unknown codes: act on payload fields; on mutations, reconcile first.

### 4. Make the destructive and replay-sensitive paths safe

- `delete` and `create` get `--dry-run` (output includes `dry_run: true` and the planned effect; no remote change; exit 0 if the mutation is valid).
- `create --if-not-exists` and `delete --if-exists` make retries idempotent; alternatively accept `--idempotency-key` if the service can deduplicate.
- Declare retry safety: `create` without `--if-not-exists` or an idempotency key is **not** safe to retry automatically after a timeout — an empty `list` does not prove it didn't commit.
  Catalog entries for `TIMEOUT` on mutations carry `reconcile_first: true`.
- Declare interrupt semantics (SIGINT/SIGTERM): whether the remote request may still complete, and that local cache writes are atomic.
- Add `update` only if agents need to change values; otherwise agents will compose `delete` + `create`, which is non-atomic.

### 5. Secrets in output

Profiles are environment variables and likely contain secrets.
`show` should redact values by default (e.g. `"value": null, "redacted": true`) and return them only with an explicit flag such as `--reveal`, declared as the command's purpose in the schema.
Never echo values in errors, `--verbose` output, or schema examples.

## Priority 1 — reliable, cheap calls

### 6. Publish a machine schema

`envctl schema` (full), `envctl schema <command>` (one command), and `envctl schema --fingerprint` (compact, cacheable), all sub-100 ms with no network or auth.
The schema declares: command tree, flags with types/defaults/enums, the machine profile, isolation profile, stdin contract per command, read-only vs mutating, auth requirements, output class and shape (named shape dialect, e.g. JSON Schema), exit codes and per-command error catalog, side effects, latency class (`network` for everything but `schema`), timeouts/retries, pagination, `end_of_options_supported: true`, `schema_version` with its compatibility promise, and `fingerprint` with `fingerprint_scope: "schema-contract"`.

### 7. Ambient state: make it visible and disableable

`--profile-dir` (default `~/.envctl`) is a cache that `show`/`list` might silently serve stale data from — dangerous when several CI jobs share a runner.

- Document credential source, config files, env vars (`ENVCTL_TOKEN`, `ENVCTL_PROFILE_DIR`, service URL), cache, and precedence flags > env > config > cache.
- Add `envctl whoami` (identity, service URL, token source — redacted) and `envctl config show --resolved`.
- Add `--isolated` (ignore config and cache; credentials only from env) and `--no-cache`.
- Make the cache writes concurrency-safe (atomic rename or lock).
- Say in output whether a read came from cache (`"source": "cache"|"service"`, `fetched_at`).
- Rename `--profile-dir` to `--cache-dir`: "profile" is already the resource noun, and the flag holds a cache, not profiles.

### 8. Networked commands: timeouts and retries

Add `--timeout-ms` to every networked command with a declared default, and declare built-in retry behaviour (e.g. reads retry transient errors twice; mutations never retry without an idempotency guard).

### 9. Pagination and selection for `list`

Return `{"items": [...], "has_more": bool, "next_cursor": "..."}` with `--limit` and `--cursor`; declare cursor lifetime and the `CURSOR_EXPIRED` code.
Add `--filter` (name prefix) and `--select` (fields) with the projection rule declared.
`list` returns names and metadata only, never values.

## Priority 2 — clarity and hygiene

### 10. Command surface

- Move to `envctl profile <verb>` (`list`, `get`, `create`, `delete`) and `envctl auth login` / `envctl auth whoami`; keep the current verbs as declared aliases for the interactive users during migration.
  `show` vs `get` is your call — a verb your team already uses wins; just keep one.
- One primary selector: profile name as the single positional; support `--` so a name starting with `-` isn't parsed as a flag.
- Never pass profile names or values to a subshell or `eval`; quote values in canonical examples.

### 11. `--verbose`

Keep it human-only; in machine mode, diagnostics go to stderr only, and debug detail is opt-in and redacted.
Machine mode must still surface deprecations, cache staleness, and retries-exhausted as structured fields, not suppress them.

### 12. Help text as a contract surface

Rewrite summaries rules-first, e.g. `delete <name>  Delete a profile. Requires --yes in non-interactive use. Irreversible.` and `create <name>  Create a profile from --set or --from-file; fails if it exists unless --if-not-exists.`
State the prerequisite (auth) and the non-interactive path in `--help`, not just in docs.

### 13. No surprise side effects

Reads do no implicit writes beyond the declared cache; no telemetry or update checks by default, and never on stdout.

### 14. Tests

Ship contract tests: schema snapshot; canonical success and error payloads; declared exit codes match observed; TTY vs non-TTY (no prompt, no browser, no colour); machine-mode suppression; empty stdin on `create --from-file -`; pagination; env/config precedence and `--isolated`; `--dry-run` makes no change; interrupt during `create`/`delete`; concurrent cache writes; secret redaction in every output path.

## Checklist coverage

| Checklist section | Covered by |
| --- | --- |
| Command Model | §10 |
| Machine Schema | §6 |
| Stdin Contract | §1 (`create --from-file -`); all other commands declare `reads: false` |
| Shell Safety | §10 |
| Agent-Safe Invocation | §1, §2, §7, §8 |
| Output | §2, §9 |
| Errors And Exit Codes | §3; partial failure N/A — no multi-item commands today |
| Ambient State | §7 |
| Mutations And Long-Running Work | §4; async jobs N/A — all operations are single request/response |
| Side Effects And Telemetry | §13 |
| Prose Surfaces | §12 |
| Tests | §14 |

## Suggested first sprint

Items 1–5 plus a minimal `envctl schema`: they are what turns a CI hang or an unconfirmed delete into a clean, branchable failure.
~~~~~~
