# 2026-11-19 candidate 5, scenario S2b control, with-skill arm 1

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o34

## Scorer verdicts

## o34

- A1 (scored): PASS.
  - Part 1: PASS — "`sync` in non-TTY with no `--yes` did not hang".
  - Part 2: PASS — the top severity is P1, and the sync material sits in "F5 — P2" and "F6 — P2".
- A2 (scored): PASS — "F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload".

## Output

# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything).
Evidence basis: the user-supplied captures only; I did not run the tool.
Every `observed` label below means "observed in the user's verbatim capture".
Stream attribution is observed because each capture isolates one stream.

## 1. Findings (by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Type: `impl-bug` (`--json` promises a JSON payload)
- Evidence: `observed` — `depman ls --json 2>/dev/null` prints `✨ DepMan 3.2`, `Checking for updates...`, the JSON array, then `Done in 0.42s ✓`, all on stdout.
- Impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks the moment wording changes.
- Fix direction: in `--json` (and any non-TTY stdout) emit only the array on stdout. Move banner/timing to stderr in human mode only, and drop them entirely in machine mode. Add a single machine-profile flag (e.g. `--machine`) that implies `--json`, no color, no prompts, no banners.

### F2 — P1 — Update check on a read path, enabled by default
- Type: `design-issue`
- Evidence: `observed` that `ls` announces `Checking for updates...`; that it makes a network call is `inferred` from the message.
- Impact: a read verb gains an undeclared network side effect (latency, failure in sandboxes/offline CI, phone-home). No evidence it is confined to the local machine, so no downgrade.
- Fix direction: make update checks opt-in, never run them in machine mode or non-TTY, and never print to stdout. Declare any remaining network use per command in the schema.

### F3 — P1 — `install` failure has no symbolic code, goes to stdout, and is uninformative
- Type: `impl-bug` (error on stdout) + `design-issue` (no structured error)
- Evidence: `observed` — `depman install nonexistent-pkg 2>/dev/null` prints `Error: something went wrong (see log)` on stdout and exits `1`.
- Impact: agents cannot branch (no `code`), cannot tell not-found from network failure or auth, cannot decide retry (no `temporary`), and "see log" points at an undeclared location. The error also pollutes stdout.
- Fix direction: on failure, stdout empty; stderr carries one structured object, e.g.
  `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found","temporary":false,"field":"package","resource_id":"nonexistent-pkg"}`, exit `3` (not found). Map network/timeouts to their own codes with `temporary: true`. Declare one fallback code (`INTERNAL`, exit 1). If a log file exists, return its path in a `path`/`details` field.
  Notably, `sync` already does this well (see F6) — reuse that error path everywhere.

### F4 — P2 — No machine-readable schema or discovery surface
- Type: `schema-gap`
- Evidence: `absence-of-evidence` — `--help` lists no `schema`, `--help --json`, or fingerprint command; `--json` itself is not documented in help.
- Impact: agents must parse prose help and guess flags, output classes, exit codes, and which commands mutate.
- Fix direction: add `depman schema [command]` and `depman schema --fingerprint` (with `schema_version`, `fingerprint_scope`), declaring per command: args/flags with types, output class (`ls` = `list`), read-only vs mutating, stdin contract, error catalog with exit codes and `retryable`, latency class (`ls` local/network?), and machine-mode stderr framing (`single-error-object`).

### F5 — P2 — Undeclared exit codes; `4` conflicts with common convention
- Type: `schema-gap`
- Evidence: `observed` — `sync` exits `4` for `CONFIRMATION_REQUIRED`; `install` not-found exits `1`.
- Impact: shell-level callers branching on exit codes have no map; `4` conventionally means unauthenticated.
- Fix direction: publish an exit-code map. Treat a missing confirmation as usage/validation (`2`) or a declared domain code in `10`–`123`; use `3` for not-found.

### F6 — P2 — Mutating commands lack dry-run and are not classified
- Type: `schema-gap` / `design-issue`
- Evidence: `absence-of-evidence` — help shows no `--dry-run`; `clean` (removes packages from the global cache) shows no confirmation or dry-run; `sync` requires `--yes`; `install` mutates without a trigger beyond its verb.
- Impact: agents cannot preview `clean` or `sync`; `clean` deletes shared global state and its safety is unknown. Retry safety after interrupt/timeout is undeclared for all three.
- Fix direction: add `--dry-run` (output includes `dry_run: true` and the planned changes) to `install`, `clean`, `sync`. Mark each command read-only/mutating in the schema. Declare idempotency (is re-running `install X` safe?), interrupt behavior, and lockfile write atomicity / concurrent-invocation safety.
- What already works: `sync` in non-TTY with no `--yes` did not hang; it refused with a structured stderr error (`code`, `message`, `hint`, `temporary:false`) and empty stdout (`observed`). Keep this; just put the `--yes` repair in a structured field (e.g. `details.required_flag: "--yes"`) in addition to `hint`.

### F7 — P2 — Ambient state undocumented
- Type: `schema-gap`
- Evidence: `absence-of-evidence` — a global cache is mentioned (`clean`), a lockfile is implied (`sync`), a log exists ("see log"); no config, env vars, registry credentials, cwd-project selection, or precedence are documented.
- Impact: agents cannot predict which project/lockfile is acted on or reproduce runs.
- Fix direction: document config files, env vars, credential sources, cache/log paths, cwd selection plus a `--project <path>` override; add `config show --resolved` (secrets redacted) and an `--isolated`/`--no-config` flag.

### F8 — P2 — Vague and non-selective command and flag descriptions
- Type: `design-issue`
- Evidence: `observed` — `ls  Show stuff`; `--quiet  Less output`; `--yes  Assume yes` (scope unspecified); help leads with a tagline.
- Impact: agents cannot choose `ls` vs others or know what `--quiet` suppresses or which commands honor `--yes`.
- Fix direction: rules-first summaries, e.g. `list   List installed packages (read-only). Output: JSON array of {name, version} with --json.`; state which commands accept `--yes`. Prefer full words (`list` over `ls`, keep `ls` as declared alias).

### F9 — P3 — Aliases on `install` (`i`, `add`)
- Type: `design-issue`
- Evidence: `observed` in help.
- Impact: multiple spellings for one operation; `add` may be read as a distinct operation (add to manifest vs install).
- Fix direction: keep one canonical name in examples; declare aliases (and any deprecations) in the schema.

## 2. Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8, F9 |
| Machine Schema | F4, F5 |
| Stdin Contract | `not-checked` beyond `sync < /dev/null` (empty stdin did not block — OK for that case); no stdin contract declared (F4) |
| Shell Safety | `not-checked` — no evidence of `--` support or argument handling |
| Agent-Safe Invocation | F1 (no machine profile); `sync` non-TTY no-hang `OK` (observed); TTY-with-`--json` prompt behavior `not-checked`; timeouts for networked install `not-checked` |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F8 |
| Tests | `not-checked` — no source or tests supplied |

## 3. Open questions / assumptions
- Does `Checking for updates...` actually hit the network, and is it suppressed by `--quiet` or non-TTY? (Assumed network, not suppressed.)
- Where is "the log" and does it contain secrets (registry tokens)?
- Does `sync --json` prompt when stdin *is* a TTY? In machine mode it must not.
- Is `install` idempotent, and does `clean` prompt?
- Does `ls` list project or global packages?

## 4. Suggested remediation order
1. Release-blocking (P1): F1 clean stdout under `--json`; F2 remove default update check; F3 structured errors via the existing `sync` error path.
2. Then: schema + exit-code map (F4, F5), dry-run and mutation declarations (F6), ambient-state docs and inspection (F7), help rewrite (F8, F9).
3. Add tests pinning: `--json` stdout parses as JSON, error payloads/exit codes, no prompt in non-TTY, no network on `ls` in machine mode.
