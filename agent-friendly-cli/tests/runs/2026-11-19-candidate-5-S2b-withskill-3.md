# 2026-11-19 candidate 5, scenario S2b control, with-skill arm 3

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o91

## Scorer verdicts

## o91

- A1 (scored): PASS.
  - Part 1 (no hang claim): PASS — the Stdin row says "`sync` with `</dev/null` exits rather than hangs (observed, good)". The only "hang" text is about the update check in F3, not `sync`.
  - Part 2 (sync prompt not top severity): PASS — the top severity is P1, and the sync finding is "F5 — P2 — `CONFIRMATION_REQUIRED` exits `4`".
- A2 (scored): PASS — "F2 — P1 — `ls --json` stdout mixes banner, progress and summary with the payload".

## Output

# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything).
Evidence basis: user-supplied verbatim captures only (no live runs); `observed` below means "observed in the supplied capture".
Stdout lines come from `2>/dev/null` captures; the final `sync` line is stderr only.

## 1. Findings (by severity)

### F1 — P1 — `install` failure writes a prose error to stdout with no symbolic code
- Type: design-issue
- Evidence: observed (capture: `depman install nonexistent-pkg 2>/dev/null` printed `Error: something went wrong (see log)` on stdout; exit `1`)
- Location: `install` error path
- Impact: agents cannot branch on the failure (no `code`, no `temporary`), cannot tell not-found from network or auth failure (generic exit `1`), and the error lands on stdout where a payload is expected. "see log" points at an undeclared log location.
- Fix direction: on failure, write a structured error to stderr with `code` (e.g. `PACKAGE_NOT_FOUND`), `message`, `temporary`, plus `resource_id: "nonexistent-pkg"` and `hint`; keep stdout empty; exit `3` (not found) and declare the mapping. Emit the same JSON error shape `sync` already uses. If a log is written, declare its path in the schema and include it as `path` in `details`.

### F2 — P1 — `ls --json` stdout mixes banner, progress and summary with the payload
- Type: impl-bug (`--json` promises JSON stdout)
- Evidence: observed (`✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the JSON array on stdout with stderr discarded)
- Location: `ls` renderer
- Impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks whenever the decoration changes. Wastes tokens on every call.
- Fix direction: with `--json` (and in non-TTY stdout), stdout is the array only. Move any diagnostics to stderr, and suppress banners and timing summaries in machine mode entirely.

### F3 — P1 — Read path performs an update check
- Type: design-issue
- Evidence: observed (`Checking for updates...` during `depman ls --json`); network call itself inferred from the message
- Location: `ls` (likely global startup)
- Impact: an undeclared network call on a read verb adds latency, can fail or hang offline/in sandboxes, and leaks usage. No evidence it is confined to the local machine, so no downgrade.
- Fix direction: make update checks opt-in, off by default and always off in machine mode; never print to stdout. If kept, declare it as a side effect in the schema with an env var/flag to disable.

### F4 — P2 — No machine schema or machine profile
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` lists no `schema` command, no `--json` global flag, no exit-code map; `--json` works on `ls` and `sync` but is undocumented)
- Location: `depman --help`
- Impact: agents must guess which commands accept `--json`, what shapes and exit codes to expect, and which commands mutate.
- Fix direction: add `depman schema` (and `schema <command>`, `schema --fingerprint` with `fingerprint_scope`), declaring per command: arguments/flags, read-only vs mutating, output class (`ls` → `list`), shape dialect, per-command error catalog with exit codes and `retryable`, side effects, latency class, and a single machine-profile flag (e.g. `--machine` implying `--json`, no color/banners/prompts/update checks).

### F5 — P2 — `CONFIRMATION_REQUIRED` exits `4`, an undeclared and convention-conflicting code
- Type: schema-gap
- Evidence: observed (`sync --json < /dev/null` → `exit=4`, stderr `{"code":"CONFIRMATION_REQUIRED",...,"temporary":false}`)
- Location: `sync` error path
- Impact: the stderr object is good (empty stdout, symbolic code, `temporary`, actionable `hint`), but exit `4` conventionally means unauthenticated; shell-level callers branching on exit codes will misclassify. The code is not declared anywhere.
- Fix direction: map confirmation-required to `2` (usage) or a declared domain code in `10`–`123`, and declare it in the exit-code map and `sync`'s error catalog. Put the repair in structured form too, e.g. `details: {"required_flag": "--yes"}`.

### F6 — P2 — Mutating commands lack dry-run and declared confirmation/idempotency semantics
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` shows no `--dry-run`; `clean` deletes from the global cache with no stated confirmation; `install` mutates with no declared idempotency); `clean` behavior without a TTY is not-checked
- Location: `clean`, `install`, `sync`
- Impact: agents cannot preview `clean` (destructive, shared global cache) or `sync`, and cannot know whether re-running `install` after a timeout is safe. If `clean` runs without confirmation it is destructive with no guard; if it prompts, it needs the same non-TTY behavior `sync` shows.
- Fix direction: add `--dry-run` to `install`, `sync`, `clean` returning `dry_run: true` and the planned changes; declare `clean`'s confirmation behavior; declare retry safety for `install`/`sync` (repeat-safe or reconcile-first) and interrupt semantics for lockfile writes (atomic replace, locking).

### F7 — P2 — Command model: aliases, vague summaries, generic options
- Type: design-issue
- Evidence: observed (`--help`)
- Location: `depman --help`
- Impact: `ls — Show stuff` doesn't tell an agent what is listed (installed deps? project or global?). `install` aliases `i`, `add` invite non-canonical invocations. `--quiet — Less output` has undefined effect; `--yes` scope (which commands) is undeclared.
- Fix direction: rewrite summaries task-selective and rules-first (e.g. `ls  List installed packages in the current project as name+version; read-only`). Prefer full verbs (`list`); keep `ls`, `i`, `add` only as declared migration aliases. Define `--quiet` precisely or replace it with the machine profile; state which commands honor `--yes`.

### F8 — P2 — Ambient state undocumented
- Type: schema-gap
- Evidence: absence-of-evidence
- Location: `--help`
- Impact: global cache location, project/lockfile discovery from cwd, registry config and credentials are all implicit; agents cannot inspect or isolate them.
- Fix direction: document config files, env vars, cache path, cwd selection (and a `--project <path>` override), precedence; add `config show --resolved` and an `--isolated`/`--no-config` flag.

### F9 — P3 — No version/fingerprint surface or prose polish
- Type: schema-gap
- Evidence: absence-of-evidence (version appears only in banners)
- Fix direction: `depman version --json`; drop the marketing tagline from `--help` or move it after the usage rules.

## 2. Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F7 |
| Machine Schema | F4, F5 |
| Stdin Contract | not-checked: no stdin contract shown; `sync` with `</dev/null` exits rather than hangs (observed, good), but undeclared — fold into F4 |
| Shell Safety | not-checked: no `--` support shown or tested |
| Agent-Safe Invocation | F2, F4 (no machine profile); `sync` non-TTY prompt correctly fails fast (observed OK) |
| Output | F1, F2 |
| Errors And Exit Codes | F1, F5; `sync` error object shape OK |
| Ambient State | F8 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F7, F9 |
| Tests | not-checked: no source or tests supplied; add tests pinning F1–F6 behavior (stdout purity under `--json`, exit-code map, non-TTY `sync`/`clean`, no update check in machine mode) |

## 3. Open Questions / Assumptions

- Does `ls --json` write anything to stderr? Not captured.
- Does `install` support `--json`, and does its error change shape under it?
- Does `clean` prompt, and how does it behave with stdin not a TTY?
- Is the update check a real network call, and is it run by every command?
- What is "the log" in F1 and where is it written?

## 4. Remediation Plan

Release-blocking (P1): F1, F2, F3 — fix stdout purity, structured errors on stderr, and remove the default update check.
Then: add the schema and machine profile (F4), fix the exit-code map (F5), add dry-run and mutation semantics (F6), then F7–F9.
