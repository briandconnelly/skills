# 2026-11-19 candidate 5, scenario R2, with-skill arm 3

- Issue: #264 (round 3, P5 revision 2)
- Tree: `1a30fc1` (candidate 5 wording from `845ca99`), read from a detached worktree
- Model: `claude-opus-5-5`
- Words (`wc -w`): 1436; median limit 973, per-arm ceiling 1,298 (reference 649 words)
- Blind label: o60

## Scorer verdicts

## Output o60

- Output: PASS. "Add one flag, such as `--json` or `--machine`". status "`service`, `env`, `cluster`, `version`, ..."; deploy "`service`, `env`, `env_source`, `deployment_id`, ..."; rollback "`service`, `env`, `env_source`, `deployment_id`, `from_version`, `to_version`..."; logs "NDJSON ... `timestamp`, `pod`, `container`, `stream`, `message`".
- Errors And Exit Codes: PASS. "`code` (a stable symbolic name)"; "Publish an exit-code map" table.
- Agent-Safe Invocation, Mutations: PASS.
  - deploy trigger: pass. "`deploy <service> --yes`: deploys with no confirmation prompt."
  - deploy preview: pass. "`deploy <service> --dry-run`: returns the diff as data".
  - rollback target arg: pass. "`rollback <service> --to <version> --yes`".
  - logs ends without Ctrl-C: pass. "Default to a bounded read ... with `--follow` as explicit opt-in."
- Ambient State: PASS. "`--env` falls back to `~/.shipctl/config` or `$SHIPCTL_ENV`"; "Add `shipctl config show --resolved --json`"; "Add `--no-config`".
- Machine Schema: PASS. "Add `shipctl schema --json` to list each command's arguments and flags".
- Coverage section: no. Ends with "Suggested rollout"; no mapping to a standard's sections.

## Output

# Making `shipctl` agent-drivable: prioritized changes

This is based only on the `--help` you pasted.
I have not run `shipctl` or read its source.
Where a point depends on behavior the help only implies (for example, that `deploy` blocks on a prompt when no terminal is attached), I say so.
A quick check of those points against the code before you start would be worthwhile.

The priority order follows one question: what will make an unattended deploy or rollback hang, hit the wrong target, or leave an agent unsure what happened?

## 1. Remove every interactive step from deploy and rollback

Today `deploy` shows a diff and asks for confirmation, and `rollback` makes you pick a version from a menu (inferred from the help).
An agent with no terminal will hang at the prompt or crash, and in CI that hang lasts until a job timeout.

Change:

- `deploy <service> --yes`: deploys with no confirmation prompt.
  Without `--yes`, and with no terminal on stdin or in machine mode (item 3), it exits nonzero with `CONFIRMATION_REQUIRED` and never waits for input.
- `deploy <service> --dry-run`: returns the diff as data and changes nothing.
  This replaces "show diff, then confirm" for agents: run a dry run, inspect it, then run with `--yes`.
- `rollback <service> --to <version> --yes`: takes the target version as a flag.
  If `--to` is missing in a non-interactive run, exit with `MISSING_ARGUMENT` (`field: "--to"`) and do not open the menu.
- `rollback <service> --to <version> --dry-run`: returns the plan, including the current version and the target version, and changes nothing.
- Add `history <service>` (or `versions <service>`) so an agent can find valid `--to` values.
  The menu is currently the only way to discover them.
- Keep the confirmation prompt and the menu for humans, but show them only when stdin is a terminal and machine mode is off.

## 2. Make the target environment explicit and checkable

`--env` falls back to `~/.shipctl/config` or `$SHIPCTL_ENV`.
An agent that inherits a stray `SHIPCTL_ENV=prod` deploys to production without having asked to.

Change:

- Require `--env` on `deploy` and `rollback` in machine mode, or at least echo the resolved environment and where it came from in every output (see `env` and `env_source` below).
- Document the precedence: `--env` flag first, then `$SHIPCTL_ENV`, then `~/.shipctl/config`.
- Add `shipctl config show --resolved --json` to report the resolved env, cluster/kube context, config file path, and the source of each value.
  It must never print secrets.
- Add `whoami` (or include identity in `config show`) so an agent can see which account or role it will deploy as.
- Add `--no-config` to ignore `~/.shipctl/config` and the environment variables, so a run uses only its explicit flags.
- Use the same treatment for the Kubernetes context.
  If `shipctl` picks up the ambient kubeconfig or current context, report it and accept a flag (`--context`) that overrides it.

## 3. Add a machine mode with JSON on stdout

`status` prints a "pretty table", and `--quiet` only means "less output".
That leaves an agent scraping prose.

Change:

- Add one flag, such as `--json` or `--machine`, that turns on all of the following:
  - JSON on stdout
  - no prompts
  - no color, spinners, or progress bars
  - diagnostics on stderr only
- Also apply the no-prompt, no-color, no-progress behavior automatically when the relevant stream is not a terminal.
- Keep stdout for the result payload only.
  Banners, the diff preview, "Deploying..." lines, and summaries go to stderr, or into the payload as fields.
- Deprecate `-q/--quiet` as a way to get parsable output.
  If you keep it, it should only reduce human output.

Success payloads (JSON, stable key order, UTC timestamps):

- `status <service>`: `service`, `env`, `cluster`, `version`, `image`, `replicas_desired`, `replicas_ready`, `health` (an enum such as `healthy`, `progressing`, `degraded`), `deployed_at`, `deployed_by`.
- `deploy <service>`: `service`, `env`, `env_source`, `deployment_id`, `previous_version`, `new_version`, `status` (enum: `succeeded`, `failed`, `in_progress`), `started_at`, `finished_at`.
  With `--dry-run`, also `dry_run: true` and a structured `changes` list (for example, `resource`, `field`, `from`, `to`) in place of the text diff.
- `rollback <service>`: `service`, `env`, `env_source`, `deployment_id`, `from_version`, `to_version`, `status`, `started_at`, `finished_at`.
  With `--dry-run`, also `dry_run: true`.
- `history <service>`: an array of `version`, `image`, `deployed_at`, `deployed_by`, `deployment_id`, `is_current`, newest first.
  Use `--limit` plus `has_more` and `next_cursor` if the list can be long.

## 4. Give errors stable codes and exit codes

An agent has to tell "service not found" apart from "auth expired" and "rollout timed out" without parsing English.

Change:

- In machine mode, write a single JSON error object to stderr, leave stdout empty, and exit nonzero.
- Error fields: `code` (a stable symbolic name), `message`, `temporary` (true or false, on every error), and where relevant `hint`, `field`, `service`, `env`, `deployment_id`, `retry_after_ms`, and `reconcile_first`.
- Publish an exit-code map, for example:

  | Exit | Meaning |
  | --- | --- |
  | 0 | Success |
  | 1 | Internal error |
  | 2 | Usage or validation error |
  | 3 | Not found |
  | 4 | Not authenticated |
  | 5 | Forbidden |
  | 7 | Timeout |
  | 8 | Conflict |
  | 9 | Transient failure |
  | 10 and up | Your own codes |

- Codes each command can return:
  - All commands: `INTERNAL`, `UNAUTHENTICATED`, `FORBIDDEN`, `CLUSTER_UNREACHABLE` (temporary), `ENV_NOT_FOUND`, `SERVICE_NOT_FOUND`.
  - `deploy`: also `CONFIRMATION_REQUIRED`, `BUILD_NOT_FOUND` (no current build to deploy), `DEPLOY_IN_PROGRESS` (conflict, temporary), `ROLLOUT_FAILED`, `ROLLOUT_TIMEOUT` (`reconcile_first: true`).
  - `rollback`: also `CONFIRMATION_REQUIRED`, `MISSING_ARGUMENT`, `VERSION_NOT_FOUND`, `DEPLOY_IN_PROGRESS`, `ROLLOUT_FAILED`, `ROLLOUT_TIMEOUT` (`reconcile_first: true`).
- Put repair data, such as the valid versions for `VERSION_NOT_FOUND`, in structured `details` fields rather than only in `hint` prose.

## 5. Make deploys and rollbacks safe to retry and reconcile

Agents time out and get interrupted.
After a lost `deploy`, the agent needs to know whether it took effect before trying again.

Change:

- Return a `deployment_id` from every deploy and rollback, and add `shipctl deployment get <id> --json` with a terminal status.
- Accept `--idempotency-key <key>` on `deploy` and `rollback`, so a retry with the same key cannot start a second rollout.
  Alternatively, declare the operations idempotent by target version: deploying the version that is already running is a no-op that returns `status: "unchanged"`.
- Write down what Ctrl-C or SIGTERM does mid-rollout: whether the Kubernetes rollout continues, and what the agent should check afterward.
- Add `--timeout-ms` to wait for rollout completion, plus `--no-wait` to return right after submitting with the `deployment_id`.
  Agents can then poll with `deployment get`, or block with `deployment wait <id> --timeout-ms`.
- Report a concurrent deploy to the same service as `DEPLOY_IN_PROGRESS`.
  Do not queue it silently or race it.

## 6. Bound `logs`

`logs` tails until Ctrl-C, so an agent that calls it never gets control back.

Change:

- Default to a bounded read: `logs <service> --since 10m --limit 500`, with `--follow` as explicit opt-in.
- In machine mode, emit NDJSON on stdout, one record per line: `timestamp`, `pod`, `container`, `stream`, `message`.
- Report truncation explicitly, either in a final record or on stderr: `truncated: true` with the limit that was hit.
- Exit quietly when the reader closes the pipe (for example, `| head`).

## 7. Publish a machine-readable contract

Change:

- Add `shipctl schema --json` to list each command's arguments and flags (types, defaults, required flags), whether it changes anything, its output shape, its error codes with exit codes, and the environment variables and config it reads.
- Add `shipctl schema --fingerprint`, so agents can cache the schema and notice when it changes.
- Keep `--help` and `schema` fast and offline: no cluster calls and no auth check.
- Rewrite the `--help` summaries so the rules come first.
  For example, "deploy: changes the cluster; needs `--yes` or `--dry-run`; target env from `--env` (required in machine mode)".
- Support `--` before service names that start with `-`, and never pass service names to a shell.

## 8. Pin the behavior with tests

Add CLI tests that assert:

- `deploy` and `rollback` never prompt when stdin is not a terminal.
- stdout is valid JSON, with no banner lines, in machine mode.
- Each error code produces the exit code you declared.
- `--dry-run` changes nothing and returns `dry_run: true`.
- Environment precedence and `--no-config` work as documented.
- `logs` without `--follow` exits on its own.

## Suggested rollout

- Ship items 1–3 together first.
  They are the minimum for an agent to deploy unattended without hanging or hitting the wrong environment.
- Ship items 4–5 before letting agents act on production without supervision.
- Items 6–8 can follow.

Until item 1 ships, agents should run only `status`, and should not run `deploy` or `rollback` unattended.
