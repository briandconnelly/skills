# 2026-11-19 candidate 5, scenario S2 control, with-skill arm 1

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o20

## Scorer verdicts

## o20

Scored:
- A1: PASS. "can hang waiting on stdin"; "F1 is inferred from help text."
- A2: PASS. "evidence: inferred (from `--help`: "asks for confirmation first")"; "nothing says the prompt is skipped when stdin is not a TTY".
- A3: PASS. "`depman ls --json | jq` fails"; "evidence: observed"; "these lines are proven to be on stdout."
- A4: PASS. "Errors carry no symbolic code"; "Exit `1` (generic) for what is a not-found case."
- A5: PASS. "Read command performs an update check (hidden network side effect)".
- A6: PASS. "`clean` deletes from a global cache with no preview"; fix "`--dry-run` on ... `clean`".
- A7: PASS. "`ls — Show stuff` doesn't say what is listed"; "`install` has two aliases (`i`, `add`)".
- A8: PASS. "Tests | not-checked — no source or test suite supplied"; "Stdin Contract | ... not-checked — no stdin usage shown".

Conformance:
- C1 template: FAIL. F9 has type, evidence, impact, fix direction but no location line.
- C2: PASS. "inferred", "observed", "absence-of-evidence".
- C3: PASS. "F1 — P0"; "F2 — P1".
- C4: PASS. Coverage table with "not-checked — no source or test suite supplied".

## Output

# depman agent-friendliness audit

Audience: tool author (can change anything), so findings lead with contract gaps and redesign guidance.
Evidence basis: the three captures you supplied (stdout only; stderr was discarded), so "observed" below means "observed in your verbatim capture".
I did not run the tool.

## Findings (by severity)

### F1 — P0 — `sync` prompts for confirmation with no declared non-interactive behavior
- type: design-issue · evidence: inferred (from `--help`: "asks for confirmation first")
- location: `depman --help`, `sync` line
- impact: an agent or CI job calling `depman sync` without a TTY can hang waiting on stdin. `--yes` exists globally, but nothing says the prompt is skipped when stdin is not a TTY, or that it fails fast instead of blocking.
- fix direction: when stdin is not a TTY (and always in machine mode), never prompt; without `--yes`, exit `2` with `{"code":"CONFIRMATION_REQUIRED","message":...,"temporary":false,"hint":"pass --yes"}` on stderr. Declare this in the schema and test it.

### F2 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: impl-bug (`--json` promises JSON) · evidence: observed
- location: `depman ls --json` stdout lines 1, 2, 4 (`✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`)
- impact: `depman ls --json | jq` fails; agents must guess which line is JSON. Because stderr was discarded, these lines are proven to be on stdout.
- fix direction: stdout carries only the payload. Move banner/timing to stderr, and suppress them entirely in machine mode and when stdout is not a TTY.

### F3 — P1 — Read command performs an update check (hidden network side effect)
- type: design-issue · evidence: observed (`Checking for updates...` during `ls`)
- location: `depman ls --json` stdout line 2
- impact: an undeclared network call on a read path adds latency, can fail or hang offline/sandboxed, and leaks usage. No evidence it stays local, so no downgrade to P2.
- fix direction: make update checks opt-in (e.g. `depman self check-update`), never on by default, always off in machine mode; declare network side effects per command in the schema.

### F4 — P1 — Errors carry no symbolic code, and the failure goes to stdout
- type: design-issue · evidence: observed
- location: `depman install nonexistent-pkg` → stdout `Error: something went wrong (see log)`, exit `1`
- impact: agents can't distinguish not-found from network, auth, or usage failures; the message is uninformative prose, points at an unnamed log, and pollutes stdout (a caller parsing stdout sees it as output). Exit `1` (generic) for what is a not-found case.
- fix direction: on failure, stdout empty; stderr carries one structured object, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"field":"package","resource_id":"nonexistent-pkg"}`, exit `3`. Declare a tool-level exit-code map, a fallback `INTERNAL` (exit 1), a transport-failure code, and a per-command error catalog with `retryable`. If a log file is relevant, return its `path` in the error.

### F5 — P1 — No machine schema or machine profile
- type: schema-gap · evidence: absence-of-evidence (no `schema` command, no `--help --json`, no `--machine` in `--help`)
- location: `depman --help`
- impact: agents must parse prose help to learn arguments, output shapes, exit codes, and which commands mutate. `--json` appears in the capture but is not even listed in `--help`.
- fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint` with `fingerprint_scope`, `schema_version`), declaring per command: args/flags with types, read-only vs mutating, output class (`ls` → `list`), stdin contract, side effects, latency class, timeouts, error catalog. Add a single `--machine` flag implying JSON, no prompts, no color/progress/banners.

### F6 — P2 — `clean` and `install` mutate without declared dry-run, idempotency, or retry semantics
- type: schema-gap · evidence: absence-of-evidence
- location: `depman --help` (`clean`, `install`, `sync`)
- impact: `clean` deletes from a global cache with no preview; agents can't tell what a retry after timeout/interrupt will do, or whether concurrent runs corrupt the lockfile/cache.
- fix direction: `--dry-run` on `install`, `clean`, `sync` with `dry_run: true` output listing planned changes; declare which are safe to retry, interrupt behavior, and lockfile/cache locking.

### F7 — P2 — Ambient state undocumented
- type: schema-gap · evidence: absence-of-evidence
- location: `depman --help`
- impact: the global cache, registry config, credentials, and cwd-selected project/lockfile are implicit; agents can't inspect or isolate them.
- fix direction: document config files, env vars, cache location, cwd selection (+ a `--project <path>` override), precedence; add `depman config show --resolved` and `--isolated`/`--no-config`.

### F8 — P2 — Ambiguous command model and prose summaries
- type: design-issue · evidence: observed
- location: `depman --help`
- impact: `ls — Show stuff` doesn't say what is listed (installed deps? project vs global?); `--quiet — Less output` is undefined for machine use; `install` has two aliases (`i`, `add`) that multiply call forms; `--yes` and `--json` meanings per command are unstated.
- fix direction: task-selective summaries, rules first (e.g. `list  List installed dependencies of the current project (read-only). Output: list of {name, version}`); rename `ls` → `list` keeping `ls` as a declared deprecated alias; declare aliases as migration-only in the schema and drop them from examples; document `--quiet` precisely or remove it in favor of `--machine`.

### F9 — P3 — No `--` / version / pagination / filtering declarations for `ls`
- type: schema-gap · evidence: absence-of-evidence
- impact: large dependency trees have no declared size cap, sort order, or `--filter`/`--field`; `install` doesn't declare `--` support for operands starting with `-`.
- fix direction: declare deterministic sort (by name), truncation/pagination behavior, `--` support, and a `depman version --json`.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F5 |
| Stdin Contract | F1 (prompt); otherwise not-checked — no stdin usage shown |
| Shell Safety | F9 (`--`); subshell use not-checked — no source |
| Agent-Safe Invocation | F1, F2, F5; metadata-path latency and timeouts not-checked |
| Output | F2, F4, F9 |
| Errors And Exit Codes | F4 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F1, F6 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F8 |
| Tests | not-checked — no source or test suite supplied; add tests for every fix above, especially non-TTY `sync`, clean `--json` stdout, and error codes/exits |

## Open questions / assumptions
- What does `depman` write to stderr? Captures discard it; banner/progress placement there is unknown.
- Does `sync` prompt when stdin is not a TTY, or already fail/proceed? F1 is inferred from help text.
- Is the update check network-bound and cached? Assumed a network call.
- Exit codes beyond `1` are unknown; only one failure case was captured.

## Release summary
F1 (P0) and F2–F5 (P1) block a release under this standard. Suggested order: non-interactive `sync` (F1) → clean stdout + no update check (F2, F3) → structured errors and exit map (F4) → `schema` + `--machine` (F5) → P2/P3 items.
