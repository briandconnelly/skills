# P5 R2 reference answer (2026-11-19, issue #264)

Written by a fresh subagent (`claude-opus-5-5`) from the R2 prompt and assertions only; no skill, no arm output, no word counts.
Host check: passes R2 A1–A5; no coverage section.
Word count (`wc -w` on the output below): 649. Median limit: 973 (floor 1.5x). Per-arm ceiling: 1,298 (2x).

## Output

# Making `shipctl` agent-drivable: prioritized changes

## 1. Remove every interactive prompt (highest priority)

An agent hangs on a prompt, a menu, or a stream that only Ctrl-C ends.

- `deploy`: add `--dry-run` that prints the diff and exits without changing anything, and `--yes` that deploys without asking.
  Without a TTY and without `--yes`, fail fast with an error (see section 3) instead of waiting for input.
- `rollback`: take the target as an argument, e.g. `shipctl rollback api --to v1.42.0`, plus `--to previous`.
  Add `shipctl versions <service>` (or `rollback --list`) so the agent can pick one, and support `--dry-run` and `--yes` as for `deploy`.
- `logs`: make following opt-in (`--follow`) and give bounded modes: `--since 10m`, `--tail 200`, `--until`, and `--timeout 60s` for `--follow`.
  The default should print and exit.
- Make mutations safe to retry: `deploy` of an already-running build and `rollback` to the already-running version return success with `"changed": false`.
  Accept `--wait/--no-wait` and `--timeout` so the agent knows when a rollout has finished.

## 2. Machine-readable output: `--json` (or `--output json`) on every command

Keep the pretty table for humans; with `--json`, stdout holds exactly one JSON document (JSON Lines for streaming logs), and progress or warnings go to stderr.
Include `"schema_version"` in every document.

- `status`: `{"service", "env", "cluster", "namespace", "version", "image", "replicas": {"desired", "ready", "available"}, "health": "healthy|degraded|down", "last_deploy": {"version", "at", "by"}}`
- `deploy`: `{"service", "env", "from_version", "to_version", "dry_run", "changed", "diff": [{"resource", "kind", "change": "create|update|delete", "fields": [...]}], "rollout": {"status": "succeeded|failed|timed_out|pending", "duration_s"}, "deploy_id"}`
- `rollback`: `{"service", "env", "from_version", "to_version", "dry_run", "changed", "rollout": {"status", "duration_s"}, "deploy_id"}`; `versions` returns `[{"version", "deployed_at", "deployed_by", "current"}]`
- `logs`: one object per line, `{"ts", "pod", "container", "level", "message"}`, and a final `{"event": "end", "reason": "eof|timeout|limit", "lines"}` so the agent knows the stream ended normally.

## 3. Errors an agent can branch on

On failure in `--json` mode, write one object to stderr: `{"error": {"code": "SYMBOLIC_CODE", "message", "retryable": true|false, "details": {...}, "hint"}}`.
Example codes: `SERVICE_NOT_FOUND`, `VERSION_NOT_FOUND`, `ENV_NOT_SET`, `CONFIRMATION_REQUIRED`, `AUTH_FAILED`, `CLUSTER_UNREACHABLE`, `DEPLOY_IN_PROGRESS`, `ROLLOUT_FAILED`, `ROLLOUT_TIMEOUT`.
Document a stable exit-code map, for example:

| Exit | Meaning |
|---|---|
| 0 | Success (including no-op) |
| 1 | Unexpected internal error |
| 2 | Usage error (bad flag or argument, missing `--yes`) |
| 3 | Not found (service or version) |
| 4 | Auth or permission failure |
| 5 | Conflict (another deploy in progress) |
| 6 | Rollout failed or unhealthy |
| 7 | Timed out (retryable) |
| 8 | Cluster or network unreachable (retryable) |

## 4. Make ambient state visible and overridable

The target environment silently comes from `~/.shipctl/config` or `$SHIPCTL_ENV`, so an agent can deploy to production without meaning to.

- Add `shipctl config show --json` that reports the effective values and where each came from: `{"env": {"value": "prod", "source": "SHIPCTL_ENV"}, "config_path": "~/.shipctl/config", "cluster", "context"}`.
- Echo the resolved `env` and its `source` in every `--json` result.
- Document precedence (`--env` > `$SHIPCTL_ENV` > config file) and add `--config PATH` and `--no-config` so an agent can run with no hidden state.
- Recommend that agents always pass `--env` explicitly; consider requiring it (or `--yes`-plus-`--env`) for mutations on production.

## 5. Let agents discover the contract

Add `shipctl schema` (or `shipctl --help --json`) that emits every command, argument, flag, type, default, allowed values, whether it mutates, the output JSON Schema for each command, and the error-code and exit-code tables.
Version it with the CLI version so agents can detect changes rather than learning flags from examples.

## 6. Smaller fixes

- Replace `-q/--quiet` "less output" with defined behavior: `--quiet` prints nothing on success, exit code only.
- Disable color and spinners when stdout is not a TTY or `NO_COLOR` is set.
- Write an `AGENTS.md`-style page with the safe deploy loop: `config show` → `deploy --dry-run --json` → `deploy --yes --json --wait` → `status --json`, and rollback with `versions` → `rollback --to <version> --yes --json`.
