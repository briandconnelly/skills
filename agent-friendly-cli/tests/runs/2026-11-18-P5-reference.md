# P5 reference answer (issue #264)

- **Date:** 2026-11-18
- **Drafted by:** fresh general-purpose subagent, `claude-opus-5-5`, no skill loaded; it read only the R1 prompt and R1's five scored assertions, and saw no arm output or recorded word count
- **Instruction:** satisfy all five assertions, include no checklist or coverage section, be no longer than a complete, correct answer needs
- **Host check:** A1 pass (fields named for `list`, `show`, `create`, `delete`), A2 pass (symbolic codes and exit map), A3 pass (`create` flags, `delete --yes` plus `--dry-run`, `login --token-stdin`/`ENVCTL_TOKEN`), A4 pass (`~/.envctl` cache and credentials, `status`, `--no-cache`), A5 pass (`envctl schema --json`); no coverage section (its one table is the exit-code map)
- **Output words (`wc -w`):** 746
- **Known gap (Codex review, 2026-11-18):** `--set KEY=VALUE` is not restricted to non-secret values although the answer recognizes profiles hold secrets, against `references/contract-checklist.md` § Ambient State's secret-intake rule; the reference passes A1–A5 but is not a complete safe answer. Kept frozen for this wave.
- **Fit limit:** floor(1.5 × 746) = 1,119 words

## Verbatim output

~~~~~~markdown
# Making `envctl` agent-safe, in priority order

## 1. Remove every interactive prompt from the agent path

An agent with no TTY will hang or fail on any prompt, so fix this first.

- `create <name>` takes values non-interactively: repeatable `--set KEY=VALUE`, `--from-file vars.env` (or `-` for stdin), and `--from-json` for a JSON object. If values are missing and stdin is not a TTY, fail with `MISSING_VALUES` instead of prompting. Add `--if-not-exists` so retries are idempotent.
- `delete <name>` never asks when `--yes` (or `--force`) is passed, and refuses with `CONFIRMATION_REQUIRED` when stdin is not a TTY and `--yes` is absent. Add `--dry-run`, which prints what would be deleted (name, variable count, keys) and exits 0 without deleting.
- `create` also gets `--dry-run` showing the profile it would write.
- Add a global `--no-input` (and honor `ENVCTL_NO_INPUT=1` or a non-TTY stdin) that turns any remaining prompt into an error.
- `login` gets a non-browser bootstrap: read a token from `ENVCTL_TOKEN`, or `envctl login --token-stdin` for a CI service-account token. Add a device-code flow (`login --device`) for humans on headless boxes. Commands that need auth and have none fail with `AUTH_REQUIRED`, never by opening a browser.

## 2. A machine-readable output mode with a stable shape per command

Add `--output json` (alias `--json`); also honor `ENVCTL_OUTPUT=json`. JSON goes to stdout only; logs, progress and `--verbose` text go to stderr. No color or spinners when not a TTY.

Every response uses one envelope: `{"ok": true, "data": ...}` or `{"ok": false, "error": {...}}`.

- `list` → `data.profiles`: array of `{name, var_count, created_at, updated_at, owner}`, plus `next_cursor` (null when done). Add `--limit` and `--cursor` so large lists don't flood the agent's context.
- `show <name>` → `data`: `{name, vars: {KEY: value}, created_at, updated_at, owner}`. Secret values are redacted (`"***"`) unless `--reveal` is passed, so agent transcripts don't capture secrets by default. `--keys-only` returns just the key list.
- `create <name>` → `data`: `{name, created: true|false, var_count, keys}` (`created: false` when `--if-not-exists` found an existing profile). With `--dry-run`, `{dry_run: true, would_create: {name, keys}}`.
- `delete <name>` → `data`: `{name, deleted: true, var_count}`. With `--dry-run`, `{dry_run: true, would_delete: {name, var_count, keys}}`.

Document the shape as versioned (`"schema_version": 1` in the envelope) and treat field removals or renames as breaking.

## 3. Errors an agent can branch on without parsing prose

Errors in JSON mode: `{"ok": false, "error": {"code": "PROFILE_NOT_FOUND", "message": "...", "retryable": false, "hint": "run envctl list"}}`.

Symbolic codes: `PROFILE_NOT_FOUND`, `PROFILE_EXISTS`, `INVALID_ARGUMENT`, `MISSING_VALUES`, `CONFIRMATION_REQUIRED`, `AUTH_REQUIRED`, `AUTH_EXPIRED`, `PERMISSION_DENIED`, `SERVICE_UNAVAILABLE`, `RATE_LIMITED`, `INTERNAL`.

Exit-code map, documented and stable:

| Exit | Meaning |
| --- | --- |
| 0 | Success (including a dry run) |
| 1 | Unexpected internal error |
| 2 | Usage error / invalid argument / missing values / confirmation required |
| 3 | Not found |
| 4 | Conflict (already exists) |
| 5 | Auth required, expired, or permission denied |
| 6 | Service unavailable or rate limited (retryable) |

## 4. Make ambient state visible and controllable

Two pieces of hidden state change behavior today: the profile cache in `~/.envctl` (`--profile-dir`) and stored login credentials.

- Add `envctl status --json` reporting `{auth: {source: "env"|"keychain"|"file"|null, identity, expires_at}, cache: {dir, enabled, entries, oldest_at}, service_url, config_files}`.
- Let agents disable or isolate the cache: `--no-cache` / `ENVCTL_NO_CACHE=1`, `ENVCTL_PROFILE_DIR` as the env form of `--profile-dir`, and `envctl cache clear`. Reads in CI should default to the service, or every JSON result should carry `source: "cache"|"service"` and `fetched_at`, so an agent never acts on stale data unknowingly.
- Credentials: document precedence (`ENVCTL_TOKEN` > config file > keychain), and let `ENVCTL_CONFIG_DIR` point everything at a throwaway directory so CI runs don't read or write a developer's home.
- `envctl logout` removes stored credentials.

## 5. A discoverable machine contract

Add `envctl schema --json` (and make `envctl <cmd> --help --json` equivalent per command) that emits every command, its positional args, flags with types/defaults/env-var equivalents, whether it mutates, whether it supports `--dry-run`, its output JSON Schema, and the error codes and exit codes it can return. Include the CLI version, and generate it from the same Go flag definitions so it cannot drift from the binary. Agents read this instead of inferring flags from examples or prose help.

## Rollout

Ship 1–3 together as the agent contract for next quarter, then 4 and 5. Add a CI test that runs each command with stdin closed and `--json`, asserting it never blocks and that its output validates against the published schema.
~~~~~~
