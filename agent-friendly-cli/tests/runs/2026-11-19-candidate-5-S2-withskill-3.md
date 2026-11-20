# 2026-11-19 candidate 5, scenario S2 control, with-skill arm 3

- Issue: #264 (round 3 controls, scored after the owner accepted the R2 length)
- Tree: `1a30fc1` (candidate 5 wording), read from a detached worktree
- Model: `claude-opus-5-5`
- Blind label: o15

## Scorer verdicts

## o15

Scored:
- A1 sync risk + established/not: PASS. Risk: "waits on terminal input forever"; established/not: "inferred from `--help`" and "This decides whether F1 is a live hang or only a contract gap."
- A2 shown vs deduced: PASS. "inferred from `--help` ("asks for confirmation first")"; "Nothing documents whether the prompt is skipped ... when stdin is not a TTY."
- A3 stdout pollution + established: PASS. Flagged: "`depman ls --json | jq` fails"; established: "observed ... all reach stdout even with `2>/dev/null`."
- A4 unstructured error + exit 1: PASS. "Errors have no symbolic code ... and use a generic exit code"; "the exit code was `1`."
- A5 update check side effect: PASS. "A read command makes a network call it does not declare."
- A6 clean without dry-run: PASS. "`clean` deletes from a global cache with no dry run".
- A7 aliases + Show stuff: PASS. "`install` has aliases `i` and `add`"; "`ls` is described as "Show stuff"".
- A8 unanswerable areas: PASS. "Stdin Contract | not-checked. No capture uses stdin"; "Shell Safety | not-checked."

Conformance:
- C1 template: PASS. Every finding has Severity, Type, Evidence, Location, Impact, Fix direction (F11 "Location: not available").
- C2 literal labels: PASS. "inferred", "observed", "absence-of-evidence".
- C3 severities: PASS. F1 "P0"; F2 "P1".
- C4 coverage table with not-checked reasons: PASS. "## Checklist coverage" table with "not-checked. No evidence about `--` support".

## Output

# Agent-friendliness audit: `depman` 3.2

Evidence basis: three user-supplied captures, stdout only (stderr discarded).
I did not run the tool.
"observed" below means the line appears verbatim in your captures.
Release gating: every P0 and P1 finding blocks a release until it is fixed.

## Findings (most severe first)

### F1 — `sync` confirmation prompt can hang automation
- **Severity:** P0
- **Type:** design-issue
- **Evidence:** inferred from `--help` ("asks for confirmation first").
- **Location:** `depman --help`, `sync` line.
- **Impact:** An agent or CI job that runs `depman sync` without `--yes` waits on terminal input forever.
  Nothing documents whether the prompt is skipped, or the command fails, when stdin is not a TTY.
- **Fix direction:**
  - Never prompt when stdin is not a TTY or machine mode is on.
  - Without `--yes`, fail at once with a structured error such as `{"code":"CONFIRMATION_REQUIRED","message":...,"temporary":false,"hint":"pass --yes"}` and exit 2.
  - Add `sync --dry-run`, whose output includes `dry_run: true` and the planned lockfile changes.

### F2 — `ls --json` puts a banner, an update notice and a summary on stdout with the JSON
- **Severity:** P1
- **Type:** impl-bug, because `--json` promises JSON.
- **Evidence:** observed. `✨ DepMan 3.2`, `Checking for updates...` and `Done in 0.42s ✓` all reach stdout even with `2>/dev/null`.
- **Location:** `depman ls --json` output.
- **Impact:** `depman ls --json | jq` fails.
  Agents have to guess which line is the payload.
  The emoji and timing line also cost tokens and change on every run.
- **Fix direction:**
  - With `--json`, or in machine mode, stdout carries the payload and nothing else.
  - Move any diagnostics to stderr, and drop them in machine or non-TTY mode.
  - Add a regression test that runs `ls --json` with stdout not a TTY and parses all of stdout as one JSON document.

### F3 — `ls` checks for updates on a read path
- **Severity:** P1
- **Type:** design-issue
- **Evidence:** observed. `Checking for updates...` appears during `ls`.
- **Location:** `depman ls --json` output.
- **Impact:** A read command makes a network call it does not declare.
  This adds latency, can fail or stall offline or in a sandbox, and the result can change between runs.
  The update notice is also the source of the stdout pollution in F2.
- **Fix direction:**
  - Turn update checks off by default, or make them opt-in through a config key or env var.
  - Always suppress them in machine and non-TTY mode, and never write them to stdout.
  - Declare any network access in each command's side effects.

### F4 — Errors have no symbolic code, go to stdout, and use a generic exit code
- **Severity:** P1
- **Type:** design-issue
- **Evidence:** observed. `Error: something went wrong (see log)` reached stdout with stderr discarded, and the exit code was `1`.
- **Location:** `depman install nonexistent-pkg`.
- **Impact:**
  - An agent cannot tell "package not found" from a network, auth or internal failure.
  - It cannot decide whether to retry, or whether to fix the package name.
  - "see log" does not say which log, or where it is.
  - Because the error is on stdout, a caller that reads stdout as the result receives the error text as if it were the result.
- **Fix direction:**
  - On failure, write one structured error object to stderr and leave stdout empty: `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"field":"package","resource_id":"nonexistent-pkg","path":"<log path>"}`.
  - Map the error to a declared exit code, for example 3 for not found, and keep 1 for the fallback `INTERNAL`.
  - Return the log's location in the `path` field, never in prose.

### F5 — No machine-readable contract, and `--json` is undocumented
- **Severity:** P1
- **Type:** schema-gap
- **Evidence:** absence-of-evidence.
  `--help` lists only `--quiet` and `--yes`.
  `--json` works on `ls`, but no capture documents it.
- **Location:** `depman --help`.
- **Impact:** An agent cannot discover which commands accept `--json`, what shape they return (`ls` returns `[{name, version}]`, which is not declared), which exit codes exist, or which commands mutate.
- **Fix direction:** Add `depman schema`, `depman schema --fingerprint` and `depman schema <command>`.
  The schema should declare:
  - the command tree and its aliases
  - flags with their types and defaults
  - each command's output class and shape (for example `ls` as class `list` with shape `{name: string, version: string}[]`)
  - a read-only or mutating flag per command
  - the exit-code map and a per-command error catalog
  - side effects and latency class
  - a single machine-profile flag such as `--machine`, which implies `--json`, no progress, no prompts and no update check

### F6 — `clean` deletes from a global cache with no dry run or confirmation contract
- **Severity:** P2
- **Type:** schema-gap
- **Evidence:** absence-of-evidence from `--help`.
- **Location:** `clean` line in `depman --help`.
- **Impact:** An agent cannot preview what will be removed.
  It also cannot tell whether `clean` affects other projects or runs safely alongside another depman process.
  I rated this P2 rather than P0 on the assumption that the cache can be rebuilt.
- **Fix direction:**
  - Add `clean --dry-run`, with output `{dry_run: true, would_remove: [...], bytes: N}`.
  - Declare which project scope "unused" is judged against.
  - Declare how cache writes stay safe under concurrent invocations, for example with locking.
  - Declare whether `clean` needs `--yes`.

### F7 — Command and flag help text is vague, and aliases are not distinguished
- **Severity:** P2
- **Type:** design-issue
- **Evidence:** observed in `--help`.
- **Location:** `depman --help`.
- **Impact:**
  - `ls` is described as "Show stuff", which does not say what it lists (direct or transitive dependencies, project or global) or how that differs from the other commands.
  - `--quiet` is described as "Less output", which does not say what it suppresses or whether it makes stdout clean.
  - `install` has aliases `i` and `add`, which spreads agent usage across three spellings.
  - The tagline comes first in the help, ahead of the information an agent needs.
  - `sync` says "Sync the lockfile" without saying in which direction.
- **Fix direction:**
  - Rewrite each summary with its constraints and defaults first, for example "ls: list the project's resolved dependencies (name, version), read-only".
  - Define precisely what `--quiet` does.
  - Name `install` as the canonical command, mark the aliases as aliases in the schema, and keep them out of examples.
  - Say whether `sync` writes the lockfile from the manifest, or installs packages from the lockfile.

### F8 — No exit-code map
- **Severity:** P2
- **Type:** schema-gap
- **Evidence:** absence-of-evidence. The only exit observed is 1, for not found.
- **Location:** `--help`, and the capture of `install nonexistent-pkg`.
- **Impact:** Shell callers cannot branch on not-found, auth, network, timeout or conflict.
- **Fix direction:**
  - Declare a map such as 0 success, 1 internal, 2 usage, 3 not found, 4 unauthenticated, 6 rate limited, 7 timeout, 8 conflict and 9 transient.
  - Add `temporary` to every error, so retry decisions do not depend on the exit code.

### F9 — Ambient state is undocumented
- **Severity:** P2
- **Type:** schema-gap
- **Evidence:** absence-of-evidence.
- **Location:** `--help`.
- **Impact:** A package manager depends on a lot of hidden state:
  - the registry URL
  - credentials
  - the global cache location
  - config files
  - the lockfile found from the current directory
  - the log location that "see log" refers to

  None of this is declared or inspectable, so an agent cannot explain why two runs behaved differently.
- **Fix direction:**
  - Document the sources and their precedence: flags, then env, then config, then cache.
  - Add `depman config show --resolved` with secrets redacted.
  - Add `--isolated` or `--no-config`.
  - Add `--cwd` or `--project` to override discovery from the current directory.
  - Accept registry tokens only through env vars or files, never as flags.

### F10 — Network commands have no timeout control, and mutations have no reconciliation contract
- **Severity:** P2
- **Type:** schema-gap
- **Evidence:** absence-of-evidence.
- **Location:** `--help`.
- **Impact:** `install` and `sync` (and `ls`, through its update check) may block on the network with no caller-settable deadline.
  After an interrupt, an agent does not know whether `node_modules`, or the equivalent install directory, and the lockfile are left half-written.
- **Fix direction:**
  - Add `--timeout-ms`.
  - Declare the default retry behavior.
  - Declare atomic writes for the lockfile and install directory, and what an interrupt leaves behind.
  - State that `install` is repeat-safe, if it is.

### F11 — No evidence of contract tests
- **Severity:** P3
- **Type:** schema-gap
- **Evidence:** absence-of-evidence. I had no source or tests.
- **Location:** not available.
- **Impact:** F2 and F4 suggest that nothing pins clean stdout or the shape of error payloads.
- **Fix direction:** Add tests for:
  - schema snapshots
  - `--json` stdout parsing as one JSON document under non-TTY
  - the error payload and exit code for not-found
  - no prompt when stdin is not a TTY
  - update checks suppressed in machine mode

## Checklist coverage

| Checklist section | Status |
|---|---|
| Command Model | F7 |
| Machine Schema | F5, F8 |
| Stdin Contract | not-checked. No capture uses stdin, and none is declared (also part of F5). |
| Shell Safety | not-checked. No evidence about `--` support or how package names are handled. |
| Agent-Safe Invocation | F1, F5 (no machine profile), F10 (timeouts) |
| Output | F2 |
| Errors And Exit Codes | F4, F8 |
| Ambient State | F9 |
| Mutations And Long-Running Work | F1, F6, F10 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F7 |
| Tests | F11 |

## Open questions and assumptions

- **Stderr content.** Captures discarded stderr, so I cannot tell what depman writes there.
  The diagnostics in F2 and the error in F4 are confirmed on stdout, but stderr may also hold the structured detail that "see log" hints at.
- **Non-TTY behavior.** The captures may have run in a terminal.
  If depman already removes the banner and update check when stdout is not a TTY, F2 and F3 still stand for TTY runs with `--json`, but the fix is smaller.
- **`sync` without a TTY.** Does `sync` without `--yes` currently prompt, auto-accept or fail when stdin is not a TTY?
  This decides whether F1 is a live hang or only a contract gap.
- **The "global" cache.** Is it shared across users or projects, and can it be rebuilt? The answer could raise F6's severity.

## Suggested remediation order

1. F1: never prompt without a TTY, and add `sync --dry-run`.
2. F2 and F3: clean stdout for `--json`, and turn update checks off by default.
3. F4: structured stderr errors with symbolic codes.
4. F5: the `schema` command and a `--machine` profile.
5. F6 through F10.
6. F11: tests that pin each of the above.
