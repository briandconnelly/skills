# 2026-11-19 candidate 5, scenario R2, with-skill arm 1

- Issue: #264 (round 3, P5 revision 2)
- Tree: `1a30fc1` (candidate 5 wording from `845ca99`), read from a detached worktree
- Model: `claude-opus-5-5`
- Words (`wc -w`): 1368; median limit 973, per-arm ceiling 1,298 (reference 649 words)
- Blind label: o29

## Scorer verdicts

## Output o29

- Output: PASS. "Add `--format json` (implied by `--machine`)". status "`{\"service\", \"env\", \"version\", \"image\", \"replicas\"...}`"; deploy and rollback "`deploy` and `rollback` on success: `{\"operation_id\", \"service\", \"env\", \"from_version\", \"to_version\", ...}`"; logs "`{\"ts\", \"pod\", \"container\", \"line\"}`".
- Errors And Exit Codes: PASS. Code/exit table: "`CONFIRMATION_REQUIRED` | 2 ... `CLUSTER_UNREACHABLE` | 9".
- Agent-Safe Invocation, Mutations: PASS.
  - deploy trigger: pass. "Require `--yes` to actually deploy."
  - deploy preview: pass. "`deploy <service> --dry-run` ... change nothing."
  - rollback target arg: pass. "replace the menu with `--to-version VERSION`".
  - logs ends without Ctrl-C: pass. "by default, print a bounded set of lines and exit."
- Ambient State: PASS. "`--env` silently falls back to `$SHIPCTL_ENV` or `~/.shipctl/config`"; "Add `shipctl config show --resolved`"; "Add `--no-config`".
- Machine Schema: PASS. "Add `shipctl schema` to list every command, argument, and flag".
- Coverage section: no. "What I assumed" lists assumptions, not a standard-section mapping.

## Output

# Making `shipctl` safe for agents to run on their own

This is based only on the `--help` text you pasted.
I haven't run `shipctl` or read its source.
Where I say "probably", I'm guessing from that help text, and one quick test of each would confirm it.
The changes are listed in priority order.
Items 1–4 must ship before agents run deploys or rollbacks unattended.

## 1. Remove every prompt from deploy and rollback, and never wait on the terminal

Right now `deploy` asks to confirm and `rollback` shows a menu.
An agent, or anything without a terminal, will hang forever or quietly pick a default.

- Add a global `--machine` flag.
  It turns off prompts, menus, pagers, color, spinners, and tables.
  Also apply these rules whenever stdin is not a terminal, even without the flag.
- `deploy <service>`: never prompt.
  Require `--yes` to actually deploy.
  Without `--yes` in machine mode, fail with `CONFIRMATION_REQUIRED` (exit 2), and never fall back to a prompt.
- `rollback <service>`: replace the menu with `--to-version VERSION`.
  Without it in machine mode, fail with `VERSION_REQUIRED` (exit 2).
  Put the valid choices in `details.available_versions` so the agent can fix the call.
  Add `shipctl releases <service>` to list deployable versions as JSON: `version`, `image`, `deployed_at` (UTC, ISO 8601), `status`, and `current: bool`.
- `logs <service>`: by default, print a bounded set of lines and exit.
  Add `--limit N` and `--since DURATION`, and make following opt-in with `--follow --timeout-ms N`.
  Today "Ctrl-C to stop" means an agent can never get the command to finish.

## 2. Make the target environment explicit, and show what it resolved to

`--env` silently falls back to `$SHIPCTL_ENV` or `~/.shipctl/config`.
An agent can deploy to production without ever writing "prod".

- In machine mode, require `--env` for `deploy` and `rollback`.
  Fail with `ENV_REQUIRED` (exit 2) instead of using a default.
- Put the resolved environment in every output, along with where it came from: `env`, `env_source` (`flag`, `env_var`, or `config_file`), `cluster`, and `namespace`.
- Add `shipctl config show --resolved` to print the resolved env, cluster, kube context, and config path as JSON.
  Also add `shipctl whoami` to show the cluster identity the agent is acting as.
  Neither command should print secrets.
- Add `--no-config` to skip `~/.shipctl/config`, `$SHIPCTL_ENV`, and any default kube context, so every input has to come from flags.
- Document the precedence order: flags, then environment variables, then the config file.
  Also list every environment variable `shipctl` reads, including the kube ones.

## 3. Add a dry run that returns the plan as structured output

The diff that `deploy` shows before confirming should become its own non-mutating mode.

- `deploy <service> --dry-run` and `rollback <service> --to-version V --dry-run` change nothing.
  They exit 0 if the change is valid and use the normal error codes if not.
- Dry-run output is `{"dry_run": true, "service", "env", "from_version", "to_version", "changes": [{"kind", "name", "field", "before", "after"}]}`.
- Optionally add `--plan-id`: the dry run returns a `plan_id`, and `deploy --yes --plan-id ID` fails with `PLAN_STALE` (exit 8) if the cluster has changed since the plan was made.
  This way the agent applies exactly the change it reviewed.

## 4. Make deploys and rollbacks safe to retry after a timeout or crash

If the process dies partway through, the agent can't tell whether the deploy happened.
If it retries blindly, it may deploy twice or race a rollback.

- Accept `--idempotency-key KEY` on `deploy` and `rollback`.
  A repeat with the same key returns the original operation instead of starting a new one.
- Every mutation returns an `operation_id`.
  Add `shipctl operation status <id>`, which returns `operation_id`, `state` (`pending`, `progressing`, `succeeded`, `failed`, or `rolled_back`), `service`, `env`, `to_version`, `started_at`, `finished_at`, and `error`.
- Add `--wait --timeout-ms N` (wait for the rollout to finish), and default to returning as soon as the change is submitted.
  If the wait times out, return `ROLLOUT_TIMEOUT` (exit 7) with `operation_id` and set `reconcile_first: true`.
- Document what Ctrl-C or SIGTERM leaves behind.
  For example, the Kubernetes rollout keeps going after `shipctl` exits.
  Also say which retries are safe: only with the same idempotency key, or after `operation status` confirms the operation had no effect.
- If another deploy for the same service is already running, fail with `DEPLOY_IN_PROGRESS` (exit 8) instead of queuing behind it or overriding it.

## 5. Add JSON output, and keep stdout for the result only

Agents can't reliably parse a "pretty table", and it changes whenever someone tweaks the formatting.

- Add `--format json` (implied by `--machine`).
  Write the result to stdout and nothing else: no banners, progress messages, or diffs mixed in.
  Progress goes to stderr.
- `status <service>`: `{"service", "env", "version", "image", "replicas": {"desired", "ready", "updated"}, "rollout_state", "deployed_at"}`.
- `deploy` and `rollback` on success: `{"operation_id", "service", "env", "from_version", "to_version", "state", "rollout_state"}`.
- `logs` in machine mode: one JSON object per line, `{"ts", "pod", "container", "line"}`, ordered deterministically.
- Remove `-q/--quiet`, or define exactly what it hides.
  "Less output" doesn't tell an agent what it will still get.

## 6. Return errors as JSON with stable codes and distinct exit codes

Agents need to tell "the service doesn't exist" from "not authorized", "already deploying", and "the cluster is unreachable" without reading English sentences.

- In machine mode, write errors to stderr as one object: `{"code", "message", "temporary", "hint", "details", "field", "operation_id"}`.
- Assign exit codes per command.
  The table below is a proposal.
  Values 3–9 aren't a Unix standard, so publish whatever you choose in the schema (item 7).

  | Code | Exit |
  | --- | --- |
  | `USAGE` | 2 |
  | `CONFIRMATION_REQUIRED` | 2 |
  | `VERSION_REQUIRED` | 2 |
  | `ENV_REQUIRED` | 2 |
  | `SERVICE_NOT_FOUND` | 3 |
  | `VERSION_NOT_FOUND` | 3 |
  | `UNAUTHENTICATED` | 4 |
  | `FORBIDDEN` | 5 |
  | `ROLLOUT_TIMEOUT` | 7 |
  | `DEPLOY_IN_PROGRESS` | 8 |
  | `PLAN_STALE` | 8 |
  | `CLUSTER_UNREACHABLE` | 9 (`temporary: true`) |
  | `ROLLOUT_FAILED` | 10 |
  | `INTERNAL` | 1 (catch-all for unexpected failures) |

- Set `temporary` on every error, including `false`, so agents know whether retrying could help.
- If a command fails partway through, say so in the error.
  For example, a rollout that started and then failed should still include `operation_id`.

## 7. Publish a machine-readable schema

- Add `shipctl schema` to list every command, argument, and flag (with type, default, and allowed values), plus whether each command is read-only or makes changes.
  It should also list each command's output shape and error codes, the environment variables and config file it reads, and the schema's version.
- Add `shipctl schema --fingerprint`, a short value that changes whenever the schema changes, so agents can cache the schema and re-fetch it only when the fingerprint changes.
- Make `--help` and `schema` fast and work offline: no cluster calls and no auth check.
- Rewrite help summaries so the rules come first.
  For example: "`deploy <service>` — changes things; requires `--env` and `--yes` in machine mode; `--dry-run` shows the plan."

## 8. Lower priority

- Add `--timeout-ms` to every command that talks to the cluster, and document the retry behavior.
- If the CLI checks for updates or sends telemetry, turn that off in machine mode.
- Support `--` before arguments, and never pass service names to a shell.
- Add tests for:
  - non-TTY and `--machine` runs that never prompt
  - JSON snapshots for each command
  - the exit code for each error code
  - dry runs that change nothing
  - flags taking precedence over environment variables and the config file, plus `--no-config`
  - interrupting a deploy partway through
  - two deploys of the same service at the same time

## What I assumed

- I'm assuming stdout and stderr are mixed today, that errors are plain prose, and that the exit codes don't distinguish failure types.
  The help text doesn't say any of this.
  One failing call, such as `shipctl status no-such-service`, with stdout and stderr captured separately would confirm it.
  I can run that if you'd like.
- I'm assuming `deploy` and `rollback` wait for the rollout to finish.
  If they return as soon as the change is submitted, item 4's `--wait` is the new behavior rather than the default.
