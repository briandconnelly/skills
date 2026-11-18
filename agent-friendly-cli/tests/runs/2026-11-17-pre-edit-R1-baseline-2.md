# Scenario R1 (hardening) — baseline arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 3/5 scored
- **Tokens:** 49,951 (final-turn context plus output, read from the transcript)
- **Output words:** 645
- **Transcript sha256:** `c6949089f0c8afd340f60c7d6640b2241f734207336c6b69b2d56fad34f6b207` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertions verbatim and no arm labels
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
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | only `list` gets fields (name, updated time, key count); show/create/delete have none Parts: machine-readable mode = pass; list shape = pass; show shape = fail; create shape = fail; delete shape = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | 0 success, ... 3 not found, 4 auth ... `{"error":{"code":"not_found"...}}` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `delete` requires `--yes` ... `--dry-run` ... `ENVCTL_TOKEN` Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `--profile-dir` cache is shared state ... add `--no-cache`; `envctl auth status` Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **FAIL** | Only per-command prose `--help` with JSON shape; no schema/--help --json command |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-ready: proposed changes, in priority order

## P0: Unblock agents and keep them safe

1. **Non-interactive auth.**
   `login` via browser cannot work in CI.
   Accept a token from `ENVCTL_TOKEN` (or `--token-file`), with workload identity/OIDC from CI as the preferred path.
   Add `envctl auth status` so an agent can check whether it is authenticated without starting a login flow.
   If credentials are missing, fail fast with a clear error and a distinct exit code; never open a browser or block.

2. **No prompts, ever, when not on a TTY.**
   Detect a non-TTY stdin (or `--no-input` / `ENVCTL_NO_INPUT=1`) and fail with a usage error instead of prompting.
   `create` takes values through flags: `--set KEY=VALUE` (repeatable), `--from-file vars.env|json`, or `--from-stdin`.
   Secret values come from a file or stdin, not argv, so they stay out of process listings and shell history.

3. **Explicit, guarded destructive operations.**
   `delete` requires `--yes` (or `--force`) when non-interactive; without it, exit non-zero and say which flag is needed.
   Add `--dry-run` to `create` and `delete` that prints exactly what would change.
   Consider `--if-exists` / `--if-not-exists` so retries are idempotent (deleting an already-deleted profile is success with that flag, not an error).
   Optionally gate deletion of protected profiles (e.g. `prod-*`) behind server-side policy, so a misbehaving agent cannot do it with a flag alone.

4. **Secrets redacted by default.**
   `show` masks values unless `--reveal` is passed, since agent output often lands in logs and model context.
   Never print tokens in `--verbose` output or error messages.

## P1: Make output reliable to parse

5. **Machine-readable output.**
   `--output json` (or `--json`) on every command, with a stable, documented, versioned schema.
   Data goes to stdout, logs and progress to stderr.
   No colour or spinners when not on a TTY, and honour `NO_COLOR`.
   `list` output should include fields agents need without a second call (name, updated time, key count), and support `--limit`/pagination if the list can be large.

6. **Meaningful exit codes.**
   Document a small set, for example: 0 success, 1 general error, 2 usage error, 3 not found, 4 auth required/denied, 5 conflict (already exists), 6 confirmation required, 7 transient/network (safe to retry).
   With `--output json`, errors also go to stderr as JSON: `{"error":{"code":"not_found","message":"...","hint":"..."}}`.

7. **Actionable errors.**
   Each error says what went wrong and the next command to run (e.g. "profile `foo` not found; run `envctl list`").
   Suggest close matches for typos.

## P2: Make it easy to discover and operate

8. **Better help.**
   Per-command `--help` with every flag, examples, the exit codes, and the JSON shape.
   Document every env var (`ENVCTL_TOKEN`, `ENVCTL_PROFILE_DIR`, `ENVCTL_NO_INPUT`, ...).
   `--help` must work without auth or network.

9. **Predictable state and concurrency.**
   `--profile-dir` cache is shared state: parallel CI jobs can race on it.
   Make cache writes atomic, add `--no-cache` (or default to no cache when non-interactive), and let `ENVCTL_PROFILE_DIR` point at a per-job dir.
   For `create`/update, support optimistic concurrency (`--if-match <version>`) so agents do not overwrite each other.

10. **Timeouts and retries.**
    `--timeout` with a sane default so a hung service does not stall a CI job; retry transient errors with backoff internally and report them via the transient exit code.

11. **Version and stability contract.**
    `envctl version --output json`, and a stated policy that flags, exit codes, and JSON fields are not changed without a deprecation period.

## P3: Nice to have

12. Least-privilege tokens for agents (read-only token for `list`/`show`; separate scope for `create`/`delete`).
13. Audit log on the service recording the caller identity (agent vs human) for every mutation.
14. A short `AGENTS.md`-style usage note or a Claude Code / Codex skill that shows the canonical non-interactive invocations.

## Example target usage

```sh
export ENVCTL_TOKEN="$(cat /run/secrets/envctl)"
envctl list --output json
envctl show staging --output json            # values masked
envctl create ci-123 --from-file vars.env --if-not-exists --output json
envctl delete ci-123 --yes --if-exists
echo $?   # 0 ok, 3 not found, 4 auth, 6 needs --yes, 7 retry
```
~~~~~~
