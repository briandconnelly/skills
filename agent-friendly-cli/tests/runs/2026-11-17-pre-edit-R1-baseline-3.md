# Scenario R1 (hardening) — baseline arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 50,352 (final-turn context plus output, read from the transcript)
- **Output words:** 814
- **Transcript sha256:** `7a940123f4e94e0d4ece76124986784cabe29566b16bd510a7350e8a6fcc4124` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o5`; the scorer received the assertions verbatim and no arm labels
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

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | `list` returns an array, `show` an object, mutations return the resulting resource -- classes only Parts: machine-readable mode = pass; list shape = fail; show shape = fail; create shape = fail; delete shape = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | 0 ok, 1 generic, 2 usage, 3 not found, 4 auth ... |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `--dry-run` on `create` and `delete`; require `--yes`; `ENVCTL_TOKEN` Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | cache in `~/.envctl` ... `--no-cache`; `envctl auth status` Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | a machine-readable capabilities/schema command (e.g. `envctl schema --json`) |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-ready: prioritized changes

Ordered by risk removed per unit of effort.
P0 items block safe agent use; P1 makes it reliable; P2 makes it pleasant.

## P0 — Must have before agents call it

### 1. Never block on a TTY: non-interactive mode for every command
Today `create` prompts for values and `delete` asks "are you sure?".
An agent with no TTY will hang until the CI job times out, or worse, pipe garbage into the prompt.

- Detect non-TTY stdin (and honor `--no-input` / `ENVCTL_NO_INPUT=1`, and `CI=true`); in that mode, any prompt becomes an immediate error with exit code and a message naming the flag that supplies the value.
- `create <name>`: accept values via `--set KEY=VALUE` (repeatable), `--from-file path.env|.json`, and `--from-file -` (stdin). Secrets should come from file/stdin, not argv (argv leaks into `ps` and CI logs).
- `delete <name>`: require `--yes` (or `--force`) when non-interactive; without it, exit non-zero with "refusing to delete without --yes".

### 2. Non-browser authentication
`login` via browser cannot work in CI.

- Accept a token via `ENVCTL_TOKEN` (and `--token-file`), ideally a scoped service/machine credential issued per CI agent.
- When unauthenticated in non-interactive mode, fail fast with a distinct exit code (e.g. 4) and the message "set ENVCTL_TOKEN" — never open a browser or wait.
- Add `envctl auth status` (machine-readable) so an agent can check credentials before acting.

### 3. Guardrails on destructive and mutating operations
Agents will occasionally call the wrong thing; make mistakes cheap.

- `--dry-run` on `create` and `delete`, printing exactly what would change.
- Least-privilege tokens: a read-only scope for agents that only `list`/`show`; write/delete scopes granted explicitly.
- Consider soft delete (tombstone + `envctl restore <name>` within N days) or at minimum printing the deleted profile's contents/version to an audit log.
- Audit log server-side tagging the caller identity (agent vs. human).

### 4. Don't leak secrets into agent context
`show` presumably prints values; whatever an agent prints ends up in transcripts, logs, and model-provider traffic.

- Redact secret values by default in `show` (`KEY=****`); require `--reveal` (and a scope permitting it) to print them.
- Offer `envctl exec <name> -- cmd` (inject env into a child process) so agents can *use* a profile without ever seeing values.

## P1 — Reliable, parseable automation

### 5. Structured output
- `--output json` (or `--json`) on every command, with a documented, versioned schema; `list` returns an array, `show` an object, mutations return the resulting resource.
- Data on stdout, diagnostics/progress on stderr — always. `-v` must never pollute stdout.
- Stable field names; no color/spinners when not a TTY (honor `NO_COLOR`).

### 6. Meaningful exit codes and structured errors
Document them in `--help`, e.g.: 0 ok, 1 generic, 2 usage, 3 not found, 4 auth, 5 conflict/already exists, 6 permission denied, 7 transient/network (retryable).
With `--json`, errors are emitted on stderr as `{"error": {"code": "not_found", "message": "...", "retryable": false, "hint": "envctl list"}}`.

### 7. Idempotency and safe retries
- `create` on an existing name: fail with "conflict" by default; offer `--if-not-exists` (no-op success) and/or an `apply`/`upsert` verb.
- `delete` on a missing name: `--ignore-missing` for success-if-absent.
- Optional optimistic concurrency (`--if-version N`) since the store is shared and humans and agents will edit concurrently.
- Built-in timeouts (`--timeout`) and bounded retries for transient errors.

### 8. Deterministic, scoped state
- Default cache in `~/.envctl` is shared mutable state between parallel CI jobs; make it safe for concurrency (atomic writes/locks) or allow `--no-cache` / `ENVCTL_PROFILE_DIR` per job.
- Document every env var the CLI reads; every flag should have an env-var equivalent.
- Clarify naming: `--profile-dir` is a cache dir, and "profile" is also the resource — rename to `--cache-dir` to avoid agents confusing the two.

## P2 — Discoverability and ergonomics

### 9. Self-describing help
- Per-command `envctl <cmd> --help` with all flags, examples (including a non-interactive example for each), exit codes, and output schema.
- `envctl --version` and a machine-readable capabilities/schema command (e.g. `envctl schema --json`) so agents can adapt to version drift.
- Fix wording ambiguities: `-v` is verbose (agents often guess `-v` = version); add `-q/--quiet`.

### 10. List ergonomics
- Filtering (`--filter`, `--prefix`), pagination (`--limit`, `--cursor`) with a truncation signal in output, and sorting — so agents don't dump huge lists into their context.

### 11. Agent-facing documentation
- A short `AGENTS.md`/skill snippet in the repo describing the safe invocation pattern: `ENVCTL_TOKEN=... envctl --no-input --json <cmd>`, which commands mutate, and that `delete` requires `--yes`.

## Suggested rollout
1. Ship P0 #1–#2 together (non-interactive + token auth) — without these agents can't run at all.
2. Ship #3–#4 before granting any agent write or reveal scope.
3. Ship #5–#7 before agents depend on output parsing; freeze the JSON schema with a version field.
4. Add contract tests that run every command with stdin closed and no TTY, asserting no hang, correct exit codes, and valid JSON.
~~~~~~
