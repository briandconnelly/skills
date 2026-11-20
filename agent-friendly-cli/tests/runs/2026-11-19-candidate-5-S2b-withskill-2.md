# 2026-11-19 candidate 5, scenario S2b control, with-skill arm 2

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o90

## Scorer verdicts

## o90

- A1 (scored): PASS.
  - Part 1: PASS — "Positive: the command did not hang on non-TTY stdin". The only "hang" text is in F2, about the update check.
  - Part 2: PASS — the top severity is P1, and the sync finding is "F5 — `P2` — `sync` exit `4` is undeclared".
- A2 (scored): PASS — "F1 — `P1` — `ls --json` stdout mixes banner, progress, and summary with the payload".

## Output

# depman 3.2 — agent-friendliness audit

Audience: the tool author.
Evidence is the user-supplied capture only; nothing was run.
Two `P1` classes (stdout pollution, unbranchable errors) and a likely update check on a read path block a release under the severity rules below.

## Findings (by severity)

### F1 — `P1` — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: `impl-bug` (`--json` promises a JSON payload)
- evidence: `observed` (user capture, stderr discarded via `2>/dev/null`)
- location: `depman ls --json 2>/dev/null` — lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the array
- impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks the moment wording changes.
- fix direction: stdout carries only the JSON array under `--json`; send banner, progress, and timing to stderr (and suppress them entirely in machine mode or when stderr is not a TTY).

### F2 — `P1` — Read path performs an update check
- type: `design-issue`
- evidence: `inferred` (the `Checking for updates...` line on `ls` implies a network call; whether it actually contacts a server is not shown)
- location: `depman ls --json` output
- impact: an undeclared network call on a read adds latency, can hang or fail offline/in sandboxes, and leaks usage.
- fix direction: no update check by default; make it opt-in (e.g. `depman self check-update` or `DEPMAN_UPDATE_CHECK=1`), always suppressed in machine mode, never on stdout.
  Downgrade to `P2` only if source shows the check is local-only.

### F3 — `P1` — `install` failure has no symbolic code, goes to stdout, and points at an unnamed log
- type: `design-issue`
- evidence: `observed` (user capture: `Error: something went wrong (see log)` on stdout, exit `1`)
- location: `depman install nonexistent-pkg`
- impact: agents cannot tell not-found from network, auth, or validation failure; exit `1` is generic; the error is on stdout where a success payload is expected; "see log" gives no path.
- fix direction: emit a structured error on stderr, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"Package not found.","resource_id":"nonexistent-pkg","temporary":false}`, exit `3` (not found), with empty stdout.
  If a log exists, put its location in a `path` field.
  Declare a fallback code (e.g. `INTERNAL`, exit `1`) for anything uncaught.
  Note `sync` already emits the right shape (F5) — reuse that error path everywhere.

### F4 — `P2` — No machine-readable contract; `--json` is undocumented
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` lists no `schema`, `version`, `--json`, exit codes, or output shapes)
- location: `depman --help`
- impact: agents discover `--json` and exit meanings only by trial; no way to cache or detect contract changes.
- fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint` with `fingerprint_scope`) declaring commands, aliases, flags, read-only vs mutating, output class per command (`ls` → `list`), stdin use, ambient state, exit-code map, and per-command error catalog.
  Add a single machine-profile flag (e.g. `--machine` = JSON + no prompts + no banners/progress) and declare it.

### F5 — `P2` — `sync` exit `4` is undeclared and collides with the conventional "unauthenticated" meaning
- type: `schema-gap`
- evidence: `observed` (user capture: exit `4`; stderr is a well-formed `CONFIRMATION_REQUIRED` object with `temporary:false` and a `hint`)
- location: `depman sync --json < /dev/null`
- impact: shell-level callers branching on exit codes will misread this; nothing documents what `4` means.
  Positive: the command did not hang on non-TTY stdin, stdout was empty, and the payload is branchable — this is the model for F3.
- fix direction: declare the exit-code map in the schema; move confirmation-required to `2` (usage) or a declared domain code in `10`–`123`, and list `CONFIRMATION_REQUIRED` in `sync`'s error catalog.
  Express the hint as structured repair data too (e.g. `"details":{"required_flag":"--yes"}`).

### F6 — `P2` — Mutating commands lack dry-run, idempotency, and interrupt semantics
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` shows no `--dry-run`; `clean` and `install` show no confirmation or retry contract)
- location: `install`, `clean`, `sync` in `--help`
- impact: `clean` deletes from a global cache with no preview; agents cannot check what `sync`/`install` would change, or know whether a timed-out/interrupted run is safe to retry; lockfile and cache writes may race under concurrent invocations.
- fix direction: add `--dry-run` (output includes `dry_run: true` and the planned changes) to all three; declare whether `clean` requires `--yes`; declare retry safety, signal behavior, and atomic/locked writes for lockfile and cache.

### F7 — `P2` — Ambient state undocumented
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `--help` (mentions a global cache, a lockfile, and a log, with no paths, env vars, or overrides)
- impact: agents cannot predict which project/cache/registry a command acts on or reproduce runs.
- fix direction: document config files, env vars, registry credentials source and precedence, cache and log locations, and cwd-based project selection (with an override flag); add `config show --resolved` and an `--isolated`/`--no-config` flag.

### F8 — `P3` — Help prose is not task-selective
- type: `design-issue`
- evidence: `observed` (user capture)
- location: `depman --help`
- impact: `ls  Show stuff` and `--quiet  Less output` do not let an agent choose or predict behavior; aliases `i`/`add` invite non-canonical calls; the tagline precedes the rules.
- fix direction: e.g. `ls  List installed packages (name, version) for the current project; read-only`; state what `--quiet` suppresses; mark aliases as aliases in the schema and use `install` in examples; lead with usage and constraints, drop the tagline.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 (vague summaries, aliases); otherwise noun set is small and flat — OK |
| Machine Schema | F4 |
| Stdin Contract | not-checked: only `sync` with `/dev/null` captured (it did not block); no declaration exists — part of F4 |
| Shell Safety | not-checked: no `--` support or quoting evidence in capture |
| Agent-Safe Invocation | F1, F4 (no machine profile); `sync` non-TTY non-blocking is OK (observed) |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F8 |
| Tests | not-checked: no source or test suite supplied |

## Open questions / assumptions
- Does `sync` (or `clean`) prompt when stdin *is* a TTY but stdout is not, or under `--json` without redirected stdin? Only the `/dev/null` case was captured.
- Does the update check hit the network, and does it run on every command?
- Where is "the log", and what did `install` write to stderr (discarded in the capture)?
- Does `install` without `--json` differ from `install --json` on failure?

## Suggested remediation order
1. Route all non-payload text to stderr and remove the default update check (F1, F2).
2. Generalize `sync`'s structured stderr error to every command, with declared codes and exits (F3, F5).
3. Ship `depman schema` + machine profile (F4), then dry-run/ambient-state declarations (F6, F7), then help rewrite (F8).
4. Add tests pinning stdout-only-payload, error payloads + exit codes, and non-TTY no-prompt behavior.
