# 2026-11-19 candidate 5, scenario S2 control, with-skill arm 2

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o72

## Scorer verdicts

## o72

Scored:
- A1: PASS. "may block forever waiting on terminal input"; "no capture shows non-TTY behavior".
- A2: PASS. "`inferred` from `--help` ("asks for confirmation first"); no capture shows non-TTY behavior".
- A3: PASS. "`depman ls --json | jq` fails"; "`observed` (user capture, stderr discarded)".
- A4: PASS. "Errors have no symbolic code, use a generic exit code"; "The exit code was 1."
- A5: PASS. "Implicit update check on a read command"; "an undeclared network call on a read".
- A6: PASS. "`clean` deletes from a shared global cache, and the help shows no confirmation or `--dry-run` for it."
- A7: PASS. "The aliases `i` and `add` create three spellings"; ""Show stuff" doesn't let an agent pick `ls`".
- A8: PASS. "Shell Safety | `not-checked`: `--` support ... not visible"; "Tests | `not-checked`: no source or tests were supplied."

Conformance:
- C1: PASS. Every finding has severity, type, evidence, location, impact, fix direction.
- C2: PASS. "`inferred`", "`observed`", "`absence-of-evidence`".
- C3: PASS. F1 "severity: `P0`"; F2 "severity: `P1`".
- C4: PASS. Coverage table with "`not-checked`: no source or tests were supplied".

## Output

# DepMan 3.2 agent-friendliness audit

Audience: the tool's author, who can change anything.
Evidence: only the three user-supplied captures, all run with `2>/dev/null`, so every line shown is stdout.
I could not run the tool or probe it.

## Findings (by severity)

### F1 — `sync` confirmation prompt can hang automation
- severity: `P0` (blocking behavior in non-TTY mode is fixed at P0)
- type: `schema-gap`
- evidence: `inferred` from `--help` ("asks for confirmation first"); no capture shows non-TTY behavior
- location: `depman --help`, `sync` entry
- impact: an agent that runs `depman sync` without `--yes` may block forever waiting on terminal input. Nothing declares whether the prompt is skipped, fails, or waits when stdin is not a TTY.
- fix direction: when stdin is not a TTY or machine mode is on, never prompt. Fail fast with a structured error such as `CONFIRMATION_REQUIRED` (exit 2, `hint`: pass `--yes`). Declare `--yes` as the action trigger in the schema for `sync`. Add a test that runs `sync` with stdin closed.

### F2 — `--json` stdout mixes a banner, progress, and a summary with the payload
- severity: `P1` (fixed placement: mixed stdout)
- type: `impl-bug` (`--json` promises JSON)
- evidence: `observed` (user capture, stderr discarded)
- location: `depman ls --json 2>/dev/null`: lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `depman ls --json | jq` fails. Agents have to strip lines by guesswork, and that breaks whenever the banner text changes.
- fix direction: with `--json` (and in machine mode or non-TTY), stdout carries only the JSON array. Send the banner, progress, and timing to stderr, or drop them entirely in machine mode. Add a snapshot test asserting stdout parses as JSON.

### F3 — Implicit update check on a read command
- severity: `P1` (hidden side effect on a read path; there is no evidence it is local-only)
- type: `design-issue`
- evidence: `observed` ("Checking for updates..." on `ls`)
- location: `depman ls --json` output
- impact: an undeclared network call on a read. It adds latency, can hang or fail offline, and leaks usage.
- fix direction: make update checks opt-in, suppress them in machine mode and non-TTY, and never print about them on stdout. If an update check stays, declare it in the schema's side effects.

### F4 — Errors have no symbolic code, use a generic exit code, and go to stdout
- severity: `P1` (fixed placement: no symbolic code)
- type: `impl-bug` (the error is on stdout) plus `schema-gap` (no error contract)
- evidence: `observed`. The error text shows up despite `2>/dev/null`, so it was written to stdout. The exit code was 1.
- location: `depman install nonexistent-pkg`
- impact: an agent cannot tell not-found from network, auth, or bug failures. "something went wrong" carries no information. "see log" points to an undeclared location. The error on stdout pollutes any captured payload.
- fix direction:
  - Write a structured error to stderr: `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg","hint":"..."}`.
  - Use exit 3 for not-found, and give network failures their own code.
  - Declare a fallback `INTERNAL` (exit 1).
  - Publish a per-command error catalog.
  - Return the log path in a `path` field instead of saying "see log".

### F5 — No machine-readable contract
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence` (the help shows no `schema` command, no version command, and no machine profile)
- location: `depman --help`
- impact: agents have to scrape prose to learn the commands, flags, output shapes, and exit codes. `--json` works on `ls` but is not even listed in the help.
- fix direction:
  - Add `depman schema`, `depman schema <command>`, and `depman schema --fingerprint`, with `schema_version` and `fingerprint_scope`.
  - Give each command its output class (`ls`: `list`), stdin contract, read-only vs mutating classification, latency class, and error catalog.
  - Add one machine-profile flag (e.g. `--machine`) that implies JSON output, no prompts, no color, no banners, and no update check.

### F6 — Mutations lack dry-run, idempotency, and interrupt semantics
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `--help` entries for `install`, `clean`, and `sync`
- impact: `clean` deletes from a shared global cache, and the help shows no confirmation or `--dry-run` for it. An agent can't preview the effect, and can't tell whether a retry after a timeout or interrupt is safe.
- fix direction:
  - Add `--dry-run` (output includes `dry_run: true` and the planned removals) to `install`, `clean`, and `sync`.
  - Declare concurrency safety for the cache and lockfile (locking or atomic replace) and what SIGINT leaves behind.
  - Declare which commands are safe to retry.

### F7 — Ambient state is undocumented
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `--help` (a global cache and a log are referenced but neither is described)
- impact: agents can't predict which cache, config, registry, or credentials drive results, and can't isolate runs.
- fix direction:
  - Document the config files, env vars, cache and log paths, registry credentials, and how the working directory selects the project, plus precedence between them.
  - Add `config show --resolved`, with secrets redacted.
  - Add `--isolated` or `--no-config`.

### F8 — Prose surfaces and command naming
- severity: `P3`
- type: `design-issue`
- evidence: `observed` (help text)
- location: `depman --help`
- impact:
  - "Show stuff" doesn't let an agent pick `ls` with confidence.
  - The aliases `i` and `add` create three spellings of one operation.
  - "Less output" doesn't say what `--quiet` suppresses.
  - The "friendly" banner line spends tokens on every help call.
- fix direction:
  - Use task-selective summaries that put constraints first, for example "List installed packages (name, version). Read-only."
  - Use full-word canonical names (`list`), declare aliases in the schema as migration-only, and keep them out of examples.
  - Define `--quiet` precisely, or replace it with the machine profile.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F5 |
| Stdin Contract | F5 (none declared); `not-checked` at runtime |
| Shell Safety | `not-checked`: `--` support and argument handling are not visible in the captures |
| Agent-Safe Invocation | F1, F2, F5 |
| Output | F2 |
| Errors And Exit Codes | F4 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F1, F6 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F8 |
| Tests | `not-checked`: no source or tests were supplied. At minimum, the fixes for F1–F4 need regression tests (JSON-only stdout, non-TTY `sync`, exit-code mapping). |

## Open questions and assumptions

- I assume the error went to stdout because it is visible despite `2>/dev/null`. The same reasoning places the banner and progress lines on stdout.
- Does `sync` without `--yes` wait on stdin when it is not a TTY, or does it fail? This could not be probed, so F1 is inferred.
- Does `clean` prompt? Does `--yes` apply to `install`?
- Does the update check hit the network on every command? Is there an env var that disables it?
- Where does "see log" write, and does the log contain secrets?

## Release gating and suggested order

F1–F4 (P0/P1) block release. Fix them in this order:
1. Make stdout JSON-only and send errors to stderr (F2, F4).
2. Stop the prompt from hanging in non-TTY mode (F1).
3. Remove the implicit update check (F3).
4. Add the schema and the machine profile (F5).
F5–F8 are scheduled work.
