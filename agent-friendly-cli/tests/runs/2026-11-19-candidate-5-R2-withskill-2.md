# 2026-11-19 candidate 5, scenario R2, with-skill arm 2

- Issue: #264 (round 3, P5 revision 2)
- Tree: `1a30fc1` (candidate 5 wording from `845ca99`), read from a detached worktree
- Model: `claude-opus-5-5`
- Words (`wc -w`): 982; median limit 973, per-arm ceiling 1,298 (reference 649 words)
- Blind label: o51

## Scorer verdicts

## Output o51

- Output: PASS. Machine mode: "Add one `--machine` flag (alias for `--format json ...`)". Fields per command: status "`{service, env, cluster, version, image, replicas...}`"; deploy "`{service, env, deployment_id, from_version, to_version, ...}`"; rollback "same as `deploy`, plus `rolled_back_from`"; logs "NDJSON stream, one `{ts, pod, container, line}`".
- Errors And Exit Codes: PASS. "`USAGE`/`CONFIRMATION_REQUIRED`/... 2, `SERVICE_NOT_FOUND`/`VERSION_NOT_FOUND` 3, ..."; "Agents branch on `code`, never on `message`."
- Agent-Safe Invocation, Mutations: PASS.
  - deploy trigger: pass. "add `--yes` to skip the confirm prompt".
  - deploy preview: pass. "`--dry-run` on `deploy` and `rollback` returns `{dry_run: true, ...}`".
  - rollback target arg: pass. "add `--to-version VERSION` (or `--to-previous`) in place of the menu".
  - logs ends without Ctrl-C: pass. "Without `--follow` it prints what exists and exits."
- Ambient State: PASS. "Don't fall back to `~/.shipctl/config` or `$SHIPCTL_ENV`"; "Add `shipctl config show --resolved`"; "Add `--isolated` (or `--no-config`)".
- Machine Schema: PASS. "Add `shipctl schema` (full JSON contract), `shipctl schema <command>`".
- Coverage section: no. Sections are numbered priorities, "Suggested order"; no mapping to a standard's sections.

## Output

# Making `shipctl` agent-drivable: prioritized changes

Based only on the `--help` you pasted; I haven't run `shipctl` or read its source.
Where this says the tool does or doesn't do something, I'm inferring it from the help text, so check each point against the code.

The core problem: every command an agent needs is built for a human at a terminal.
`deploy` waits for a confirmation, `rollback` shows a menu, `status` prints a table, `logs` runs until you press Ctrl-C, and the target environment is picked silently from ambient config.
An agent will hang, guess, or deploy to the wrong cluster.

## 1. Remove every prompt and menu from the agent path (do first; agents hang today)

- `deploy <service>`: add `--yes` to skip the confirm prompt.
  Without `--yes` and with stdin not a TTY, fail at once with error `CONFIRMATION_REQUIRED` (exit 2). Never block waiting for input.
- `rollback <service>`: add `--to-version VERSION` (or `--to-previous`) in place of the menu.
  If no TTY and no target is given, fail with `TARGET_REQUIRED` (exit 2), with `details.available_versions` listing the choices.
- Decide prompts by the terminal status of stdin, colour and progress by stderr, and table rendering by stdout, each checked separately.
- `logs`: add `--since`, `--limit N`, and an explicit `--follow`.
  Without `--follow` it prints what exists and exits.
  With `--follow`, add `--timeout-ms` so the agent never needs Ctrl-C.

## 2. Make the target environment explicit and inspectable (wrong-cluster risk)

- In machine mode, require `--env` on `deploy` and `rollback`. Don't fall back to `~/.shipctl/config` or `$SHIPCTL_ENV` for mutations; fail with `ENV_REQUIRED` (exit 2).
- Document precedence (flag > `$SHIPCTL_ENV` > config file) and where kube credentials and context come from: kubeconfig, current context, and any cache.
- Add `shipctl config show --resolved`, which returns `{env, env_source: "flag"|"env"|"config", cluster, kube_context, namespace, config_path}` with secrets redacted.
  Add `shipctl whoami` if deploy permissions depend on identity.
- Add `--isolated` (or `--no-config`) to ignore `~/.shipctl/config` and `SHIPCTL_*`.
- Echo the resolved `env` and `cluster` in every deploy and rollback payload.

## 3. Add a machine mode with structured output on stdout

- Add one `--machine` flag (alias for `--format json --no-input --no-color`). It turns off prompts, tables, colour, and spinners on every stream.
  `-q` doesn't do this: "less output" isn't a contract.
- stdout carries only the result payload. Banners and progress go to stderr.
- Payloads, by command:
  - `status <service>` (record): `{service, env, cluster, version, image, replicas: {desired, ready}, health: "healthy"|"degraded"|"failed"|"progressing", deployed_at (UTC RFC 3339)}`.
  - `deploy <service>` (record): `{service, env, deployment_id, from_version, to_version, status, started_at, finished_at}`.
  - `rollback <service>` (record): same as `deploy`, plus `rolled_back_from`.
  - `logs <service>`: NDJSON stream, one `{ts, pod, container, line}` per record, with a final `{type: "end"}` record so a finished stream can be told apart from a dead process.
- Make the field order and sort deterministic. No `message` field that repeats data already in the payload.

## 4. Structured errors and an exit-code map

- In machine mode, failures write one JSON object to stderr and nothing to stdout: `{code, message, temporary, hint?, details?, retry_after_ms?, reconcile_first?, request_id?}`.
  `temporary` is always present, `false` included.
- Suggested codes and exits: `USAGE`/`CONFIRMATION_REQUIRED`/`TARGET_REQUIRED`/`ENV_REQUIRED` 2, `SERVICE_NOT_FOUND`/`VERSION_NOT_FOUND` 3, `UNAUTHENTICATED` 4, `FORBIDDEN` 5, `TIMEOUT` 7, `DEPLOY_IN_PROGRESS` (conflict) 8, `CLUSTER_UNREACHABLE` 9 (temporary), `ROLLOUT_FAILED` 10, `HEALTHCHECK_FAILED` 11, and `INTERNAL` 1 as the catch-all for anything unexpected.
- For each command, document which codes it can return, whether each is retryable, and whether the caller must reconcile before retrying.
- Agents branch on `code`, never on `message`.

## 5. Make deploy and rollback safe to retry and observe

- `--dry-run` on `deploy` and `rollback` returns `{dry_run: true, service, env, from_version, to_version, diff: [...]}` as structured data, replacing today's on-screen diff. It mutates nothing and exits 0 if the change is valid.
- `--timeout-ms` on all commands that touch the cluster. Document the default and whether it retries on its own.
- Idempotency:
  - Accept `--idempotency-key KEY`, recorded with the deployment.
  - Make "already at this version" a no-op with `changed: false` and exit 0.
- A timed-out or interrupted deploy has an unknown outcome.
  Return `TIMEOUT` with `reconcile_first: true` and the `deployment_id`.
  Document that the rollout keeps going in the cluster after the CLI exits, and what SIGINT/SIGTERM leaves behind.
- Rollouts take minutes, so add `--wait/--no-wait`.
  With `--no-wait`, return `deployment_id` right away and add `shipctl deployment get <id>` (status: `pending|progressing|succeeded|failed|cancelled`), `shipctl deployment wait <id> --timeout-ms`, and a cancel command if a rollout can be aborted.
- Add `shipctl rollback <service> --list-versions` (or `shipctl versions <service>`) returning `[{version, image, deployed_at, current}]` so agents can choose a rollback target.

## 6. Make the contract discoverable

- Add `shipctl schema` (full JSON contract), `shipctl schema <command>`, and `shipctl schema --fingerprint`.
  The contract covers commands, flags with types, defaults and enums, read-only vs mutating, output shapes, error catalogs, exit codes, env/config sources, and latency class.
- Rewrite help summaries to put rules first, e.g. `deploy <service>  Mutating. Requires --env and --yes (or --dry-run). Deploys the current build.`
  Say what "the current build" is and how to override it (`--build`/`--image`); that's hidden state today.
- Support `--` before operands, and never pass service names to a shell.
- Keep `--help` and `schema` fast and offline. No cluster or auth calls.

## 7. Lock it in with tests

Cover these behaviours with automated tests:

- No hang when stdin isn't a TTY.
- `--machine` output for each command.
- Error payloads and their exit codes.
- Env precedence and `--isolated`.
- Dry run doesn't mutate.
- Interrupt behaviour during a deploy.
- A snapshot of `schema`.

## Suggested order

Ship items 1 and 2 before letting agents deploy unattended.
Items 3–5 are the minimum for agents to make decisions reliably.
Items 6–7 keep it from regressing.
Until then, a caller-side stopgap is to have agents run only `status` and always pass `--env` explicitly, and to keep `deploy` and `rollback` human-gated.
