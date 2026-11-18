# Scenario S2b — with-skill arm 1 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1308
- **Scoring:** blinded packet, output id `o26`; the scorer received the assertion block verbatim and no arm labels

## Exact prompt given

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> Each capture discards stderr (`2>/dev/null`), so every line shown is stdout, except the last, which shows stderr only (`2>&1 >/dev/null`).
> The audience is the tool's author, who can change anything.
>
> ```text
> $ depman --help 2>/dev/null
> DepMan 3.2 — the friendly dependency manager!
> Usage: depman [command] [options]
> Commands:
>   install     Install dependencies (aliases: i, add)
>   ls          Show stuff
>   clean       Remove unused packages from the global cache
>   sync        Sync the lockfile (asks for confirmation first)
> Options:
>   --quiet     Less output
>   --yes       Assume yes
>
> $ depman ls --json 2>/dev/null
> ✨ DepMan 3.2
> Checking for updates...
> [{"name":"left-pad","version":"1.3.0"},{"name":"is-odd","version":"3.0.1"}]
> Done in 0.42s ✓
>
> $ depman install nonexistent-pkg 2>/dev/null
> Error: something went wrong (see log)
> $ echo $?
> 1
>
> $ depman sync --json < /dev/null 2>/dev/null; echo "exit=$?"
> exit=4
> $ depman sync --json < /dev/null 2>&1 >/dev/null
> {"code":"CONFIRMATION_REQUIRED","message":"sync needs confirmation","hint":"pass --yes","temporary":false}
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2b-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

## A1: No finding claims `sync` hangs/blocks in automation, and no `sync`-prompt finding carries top severity
- o26: FAIL
  - Part 1 (no hang claim): FAIL — F7: "When stdin is a TTY but the run is still automated (e.g. a pty-based agent harness), `sync` may prompt and hang." (hedged as `inferred`, but still a finding claiming a hang in automation)
  - Part 2 (not top severity): PASS — F7 and F4 are P2; top is P1.
## A2: Stdout pollution on `ls --json` is still flagged
- o26: PASS — F1 "`ls --json` stdout mixes banner, progress, and summary with the payload".

## Verbatim final output

~~~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: the tool's author, who can change anything.
Evidence basis: the four captures you supplied (`observed` below means "observed in your verbatim capture"; I did not run the tool).
Stream attribution: every capture used `2>/dev/null`, so all lines shown are stdout, except the final `sync` capture, which is stderr only.

## Findings (ordered by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Type: `impl-bug` (`--json` promises a JSON payload; stdout is not parseable JSON)
- Evidence: `observed` (user capture, stdout only)
- Location: `depman ls --json` output lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- Impact: `json.loads(stdout)` fails; agents must scrape for the line starting with `[`, which breaks the moment any line changes. The non-ASCII glyphs also cost tokens on every call.
- Fix direction: in `--json` mode (and whenever stdout is not a TTY) write only the JSON array to stdout. Move banner/progress/timing to stderr, and suppress them in machine mode. Add a single machine-profile flag (e.g. `--machine`) that implies `--json`, no color, no banner, no prompts.

### F2 — P1 — Update check on a read path
- Type: `design-issue`
- Evidence: `observed` that the message `Checking for updates...` is printed during `ls`; the network call itself is `inferred` from that message.
- Location: `depman ls --json` stdout line 2
- Impact: a read command makes an undeclared network call: added latency, failure when offline or sandboxed, possible phone-home. Nothing shows the effect stays on the local machine, so it stays at P1.
- Fix direction: make update checks opt-in (`depman self check-update` or a config setting), never on by default, always off in machine mode, and never written to stdout.

### F3 — P1 — `install` failure has no symbolic code, goes to stdout, and points to a hidden log
- Type: `design-issue`
- Evidence: `observed` (stdout `Error: something went wrong (see log)`, exit `1`); whether anything also went to stderr is `not-checked` (stderr was discarded).
- Location: `depman install nonexistent-pkg`
- Impact: agents cannot tell "package not found" from network failure, auth failure, or a bug. Exit `1` is generic, and "see log" names no path. The error text on stdout can also be mistaken for payload.
- Fix direction: emit a structured error on stderr with stdout empty, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","field":"package"}`, exit `3` (not found). Declare a fallback `INTERNAL` code (exit `1`). If a log exists, put its path in a `path` field.

### F4 — P2 — Exit code `4` used for `CONFIRMATION_REQUIRED`, and no exit-code map is declared
- Type: `schema-gap` (no declared map) plus `design-issue` (`4` conventionally means unauthenticated)
- Evidence: `observed` (`exit=4`); missing map is `absence-of-evidence`
- Location: `depman sync --json < /dev/null`
- Impact: agents branching on the shell exit code may treat a missing `--yes` as an auth failure and try to re-authenticate.
- Fix direction: return this as a usage/validation error (exit `2`), or declare `4` explicitly in a published exit-code map. Either way, publish the map in the schema and per-command error catalogs.
- Credit: the payload itself is good. It is structured, on stderr, includes `code`/`message`/`temporary`, and does not block when stdin is not a TTY.

### F5 — P2 — No machine-readable schema or contract
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (`--help` lists no `schema` command, no `--help --json`, no version or fingerprint command)
- Location: `depman --help`
- Impact: agents must parse prose help to learn commands, flags, output shapes, mutation class, and exit codes.
- Fix direction: add `depman schema` (full contract, `schema_version`, fingerprint plus `fingerprint_scope`), `depman schema --fingerprint`, and `depman schema <command>`. Each command declares: read-only vs mutating, output class (`ls` → `list`), stdin contract, side effects, latency class (`install`/`sync` → `network`), and its error catalog with `retryable`/`reconcile_first`.

### F6 — P2 — `--help` prose is not task-selective, and naming is inconsistent
- Type: `design-issue`
- Evidence: `observed` (user capture)
- Location: `depman --help`
- Impact: `ls  Show stuff` gives an agent nothing to pick on: what is listed, installed packages, the lockfile, or the cache? `--quiet  Less output` does not say what is removed. `--json` appears nowhere in help even though `ls` and `sync` accept it. The aliases `i`/`add` are not marked as aliases-for-migration, and `add` suggests different semantics from `install`. The tagline comes before any rules.
- Fix direction: write help rules-first: e.g. `list   List installed packages in the current project (read-only; --json → array of {name,version})`. Rename `ls` to `list`, keeping `ls` as a declared alias. Document `--json` (or the machine profile) as a global flag. Declare the aliases in the schema and keep them out of examples. Drop the tagline, or move it after the rules.

### F7 — P2 — Mutating commands lack `--dry-run`, and the stdin/prompt contract is undeclared
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (help lists no `--dry-run`; prompting is documented only as "asks for confirmation first")
- Location: `depman --help` (`clean`, `sync`, `install`)
- Impact: agents cannot preview `clean` (it deletes from the global cache) or `sync` before mutating, so `--yes` is all-or-nothing. When stdin is a TTY but the run is still automated (e.g. a pty-based agent harness), `sync` may prompt and hang. Only the `/dev/null` case was captured, so this hang is `inferred`, not observed.
- Fix direction: add `--dry-run` to `install`, `sync`, and `clean`, emitting `dry_run: true` plus the planned changes. Guarantee that machine mode never prompts, whatever the TTY state. Declare each command's stdin contract.

### F8 — P2 — Ambient state is undeclared
- Type: `schema-gap`
- Evidence: `absence-of-evidence`
- Location: `depman --help`
- Impact: the global cache, the lockfile located from the cwd, the registry URL and credentials, and config files are all implicit. Agents cannot inspect what they resolve to, or isolate from them.
- Fix direction: document config/env/cache/credential sources and their precedence. Add a resolved-config inspection command (e.g. `depman config show --resolved`, with secrets redacted), a `--project-dir` override for cwd selection, and `--isolated`/`--no-config`.

### F9 — P3 — Missing caller-settable timeout and version command
- Type: `schema-gap`
- Evidence: `absence-of-evidence`
- Location: `depman --help`
- Fix direction: add `--timeout-ms` on networked commands and declare their retry behavior. Add `depman version --json`.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F6 |
| Machine Schema | F5 |
| Stdin Contract | F7 |
| Shell Safety | not-checked (no evidence of `--` support or of argument handling) |
| Agent-Safe Invocation | F1, F7, F9 (no machine profile; with stdin from `/dev/null`, `sync` correctly refused instead of prompting) |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F4 |
| Ambient State | F8 |
| Mutations And Long-Running Work | F7; interrupt and concurrency semantics for the lockfile and cache are not-checked |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F6 |
| Tests | not-checked (no source or tests supplied); add tests that pin F1–F4 (pure-JSON stdout, structured errors and exit codes, non-TTY no-prompt) |

## Open questions / assumptions

- Was `install`'s error duplicated on stderr? Your capture discarded stderr, so this is unknown.
- Does the update check actually hit the network, and does it write any local state?
- Is exit `4` reused for other errors (e.g. auth)? If so, F4 is worse.
- `sync` was captured only with stdin from `/dev/null`. Its behavior under a TTY or a pty is unverified.

## Suggested remediation order

1. Fix F1–F3 first. Each is P1 and blocks a release: clean JSON stdout, no default update check, structured errors.
2. Add a machine profile and `depman schema` with an exit-code map (F4, F5).
3. Add `--dry-run`, ambient-state inspection and isolation, and rewrite the help text (F6–F9). Pin all of it with tests.
~~~~~~~~
