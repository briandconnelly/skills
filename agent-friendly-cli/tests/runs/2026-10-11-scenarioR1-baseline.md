# Scenario R1 (Hardening an internal CLI) — baseline run

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill files as of commit c154b17)
- **Mode:** baseline (fresh general-purpose subagent, prompt only; representative set, first run)
- **Score:** 4/5 scored
- **Subagent tokens:** 41,318 (harness-reported total for the run)
- **Transcript sha256:** `e7f1dfb9b1285ec230009ddd4d6f72d11e39d63101c9d49b0ee83e4176360417` (session-local copy; not committed)

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

Baseline wrapper: "Your only input is the task below. Do not read any file in this repository or anywhere on disk, do not run any command, and do not use any tool; answer from the task text alone."
Tool audit: 0 tool calls other than the final hand-back, so no skill access.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Proposes a non-interactive, machine-readable output mode and says what each command's output looks like in it (Output). | **FAIL** | `--output json\|text` on every command and "One stable JSON object per command (`list` can be an array or JSONL)"; the mode is proposed but no command's output shape is actually stated. |
| A2 | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Exit-code map 0–7 plus `{"code":"...","message":"...","hint":"..."}` on stderr. |
| A3 | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `create --set/--from-file/--from-stdin`; `delete --yes` refusing when non-TTY plus `--dry-run`; `login --token`/`ENVCTL_TOKEN`/device code; global `--non-interactive`. |
| A4 | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `~/.envctl` lock and `--no-cache`/`--refresh`; `ENVCTL_PROFILE_DIR`; `envctl auth status --json` for credentials. |
| A5 | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | "Optionally `envctl --help-json`/`envctl schema` for a machine-readable command/flag listing". |

**Set:** representative; never tightened in response to its own results.
**Notes:** a strong baseline, as the representative set is meant to detect.
The one miss (A1) is the skill's per-command output declaration; the discovery proposal (A5) is offered as optional rather than as the primary contract.

## Full final output

Verbatim final message returned by the subagent:

Proposed changes to make `envctl` safe and easy for Claude Code / Codex agents to call, in priority order. (Answered from the help text alone, per the task constraints; nothing was read or run.)

## P0 - Unblockers (today these commands hang or fail outright for an agent)

1. **Remove every interactive prompt from the non-TTY path.**
   - `create <name>`: accept values as flags and input instead of prompting: `--set KEY=VALUE` (repeatable), `--from-file <path>` (JSON/dotenv), `--from-stdin`. If values are missing and stdin is not a TTY, exit non-zero with "values required; use --set or --from-file", never prompt.
   - `delete <name>`: add `--yes` / `-y` (and `--force` if you also want to bypass soft guards). When stdin is not a TTY and `--yes` is absent, refuse with a clear error naming the flag rather than waiting on "are you sure?".
   - `login`: add a browser-free path: `--token <t>`, `ENVCTL_TOKEN` env var, and/or a device-code flow. Never try to open a browser when there is no TTY or `CI` is set.
   - Global: `--non-interactive` flag and `ENVCTL_NON_INTERACTIVE=1`; also auto-detect `!isatty(stdin)`. In that mode any would-be prompt becomes an error with a dedicated exit code. This is the single most important change: a hung prompt burns an agent's whole timeout and the agent cannot tell why.

2. **Machine-readable output.** `--output json|text` (short `--json`) on every command, including errors. One stable JSON object per command (`list` can be an array or JSONL). Guarantees: data only on stdout, diagnostics/progress only on stderr, no colour/spinners/pagers when not a TTY or when `NO_COLOR` is set, stable sorted ordering for `list`.

3. **Documented exit codes and structured errors.** Distinct codes an agent can branch on, e.g. 0 ok, 1 generic, 2 usage, 3 not found, 4 auth required/expired, 5 already exists/conflict, 6 service unreachable, 7 would-prompt (non-interactive refusal). With `--json`, errors go to stderr as `{"code":"...","message":"...","hint":"run envctl login --token ..."}`. Agents recover far better from "AUTH_REQUIRED, hint: ..." than from a stack trace or `exit 1`.

## P1 - Safety for mutating commands

4. **Dry run and idempotency.** `--dry-run` on `create`/`delete` that prints what would happen (in JSON too). `create --if-not-exists` and `delete --if-exists` so retries by an agent are safe; report `created: false` / `deleted: false` rather than failing. Make `delete --dry-run`/the confirmation message show exactly what is about to be removed (name, var count, last modified).

5. **Don't leak secrets into agent transcripts.** `show` should mask values by default (`KEY=***`) with `--reveal` to print them; `-v/--verbose` must never echo values or tokens. Agents routinely paste command output into logs, PR comments and context windows; this is the main data-exposure risk of letting them run the tool.

6. **CI-grade auth.** Scoped tokens (read-only vs read-write) so a CI agent that only needs `list`/`show` cannot `delete`. `envctl auth status --json` so an agent can check before acting. Clear, distinct exit code for expired/missing auth. Optional `--as`/`ENVCTL_CLIENT=claude-code` or a user-agent so service-side audit logs attribute agent actions.

## P2 - Discoverability and ergonomics

7. **Per-subcommand `--help` with non-interactive examples.** The top-level help currently advertises prompting behaviour ("prompts for values", "asks are you sure?") with no way around it. Each subcommand should list its flags and show the CI form, e.g. `envctl create staging --set DB_URL=... --json`. State explicitly which commands can prompt and how to suppress it. Optionally `envctl --help-json`/`envctl schema` for a machine-readable command/flag listing, and `envctl version --json` so agents can confirm feature availability.

8. **Mirror all flags as env vars.** `ENVCTL_PROFILE_DIR`, `ENVCTL_TOKEN`, `ENVCTL_OUTPUT`, `ENVCTL_SERVER`, `ENVCTL_TIMEOUT`. CI harnesses configure via environment far more easily than by threading flags through every call.

9. **Robustness under parallel, unattended use.** `--timeout` with a sane default (no infinite network waits), bounded retries with backoff on transient service errors, and a lock around the `~/.envctl` cache so concurrent agent invocations don't corrupt it. Make cache behaviour explicit (`list --refresh` / `--no-cache`) so an agent can tell stale local data from service truth.

10. **Stability promises.** Treat the JSON schema, exit codes and flag names as a versioned contract; add deprecation warnings on stderr rather than silent changes. Add a short "Using envctl from CI/agents" section to the README with the canonical login -> list -> show -> create/delete sequence.

## Sketch of the resulting help

```text
envctl - manage environment profiles

Usage: envctl <command> [flags]

Commands:
  list                      List profiles (sorted by name)
  show <name>               Show a profile (values masked; --reveal to print)
  create <name>             Create a profile from --set/--from-file/--from-stdin
  delete <name>             Delete a profile (requires --yes when non-interactive)
  login                     Authenticate (--token, ENVCTL_TOKEN, or browser if TTY)
  auth status               Report auth state
  version                   Print version

Global flags:
  --json | --output <fmt>   Machine-readable output (errors too, on stderr)
  --non-interactive         Never prompt; fail with exit 7 instead (auto when no TTY)
  --dry-run                 Show what would change without changing it
  -y, --yes                 Confirm destructive actions
  --timeout <dur>           Network timeout (default 30s)
  --profile-dir <path>      Cache location (default ~/.envctl, env ENVCTL_PROFILE_DIR)
  -v, --verbose             Diagnostics on stderr (never prints secret values)

Exit codes: 0 ok, 2 usage, 3 not found, 4 auth required, 5 conflict, 6 unreachable, 7 would prompt
```

## How to verify once implemented (not run here)

- Run every subcommand with `< /dev/null` under `timeout 10` in CI; any non-zero-from-timeout result means a prompt survived.
- Pipe each `--json` output through `jq -e .` and assert stderr is empty on success.
- Assert `show` output contains no profile values unless `--reveal` is passed, and `-v` output contains no token.
- Table-test exit codes against a fake service (404, 401, 409, connection refused).

The first three items are what actually stop agents from using the tool at all; items 4-6 are what make it safe to let them; the rest reduce friction.
