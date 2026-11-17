# Scenario 2b (audit, fail-fast control) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,587 (final-turn context plus output, read from the transcript)
- **Output words:** 1,644
- **Transcript sha256:** `96af245373058be8dcdf4cfff1048a11b3e2faabeba10fbc5fbd0c92fee72c66` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o5`; the scorer received the assertions verbatim and no arm labels

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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2b-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 — `sync` uses exit `4` ... severity: P2; No `P0` was found Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — `ls --json` mixes banners, an update-check line, and a summary into stdout with the JSON |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author, who can change anything (Workflow §1: lead with contract gaps, release-blocking findings, and concrete redesign guidance).
Task: review of an existing CLI from captured material only; no probes were run.
All `observed` labels below mean "user-supplied verbatim capture", not runs by me.
Stream attribution is observed: every capture except the last discards stderr, so each line shown in them is stdout.

**Release verdict: blocked.** Four `P1` findings (F1–F4) must be fixed before release.
No `P0` was found: the one prompting command (`sync`) failed fast with a structured error instead of hanging on closed stdin.

## Findings

### F1 — `ls --json` mixes banners, an update-check line, and a summary into stdout with the JSON
- severity: P1 (fixed placement: successful stdout that mixes banners, progress, or summaries with the payload)
- type: impl-bug
- evidence: observed (user capture, `depman ls --json 2>/dev/null`)
- location: lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the JSON array on stdout
- impact: `depman ls --json | jq` fails on line 1; agents must strip lines heuristically, which breaks the moment the banner text, emoji, or timing line changes. Non-ASCII decorations also cost tokens on every call.
- fix direction: In `--json` (and any non-TTY stdout), stdout must be the JSON array alone. Remove the banner and "Done in" summary entirely, or move them to stderr and suppress them when stderr is not a TTY. Add a test asserting `depman ls --json` stdout parses as a single JSON document.

### F2 — A read command (`ls`) performs an update check
- severity: P1 (fixed placement: hidden side effect on a read path; no evidence it stays local, so no downgrade)
- type: design-issue
- evidence: observed (user capture: `Checking for updates...` on stdout of `ls --json`)
- location: `depman ls --json` output, line 2
- impact: An undeclared network call on every read adds latency, fails or hangs offline/in sandboxes, and phones home without consent; it also leaks the update-check text into stdout (F1).
- fix direction: Make update checks opt-in (config or env var), never run them on read verbs or in machine mode, and never print to stdout. Declare any remaining network use in the schema's side-effects field.

### F3 — `install` failure has no symbolic code, goes to stdout, and gives no actionable detail
- severity: P1 (fixed placement: errors that offer no symbolic code to branch on)
- type: impl-bug
- evidence: observed (user capture, `depman install nonexistent-pkg 2>/dev/null` → `Error: something went wrong (see log)`, exit 1)
- location: `install` error path
- impact: Agents cannot tell not-found from network failure from auth failure; they get generic exit `1`, must parse English, and the message points at an unnamed log. Because stderr was discarded, the error text was written to stdout, so a caller capturing stdout as payload receives an error string instead.
- fix direction: Emit the same structured error object `sync` already uses, on stderr, with empty stdout, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg"}`, and exit `3` (not found). Use `temporary: true` with exit `9`/`7` for transient registry failures. If a log is relevant, include its absolute path in a `path` field. Apply this on every command, not only under `--json`, or at least whenever stderr is non-TTY.

### F4 — No machine schema, machine profile, or exit-code map
- severity: P1
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `schema` command, no `--json`/machine flag, no exit codes; no substitute such as `--help --json` shown)
- location: `depman --help`
- impact: Agents cannot discover which commands accept `--json` (it works on `ls` and `sync` but is undocumented), which commands mutate, what each output shape is, or what exit `4` means (see F5). Every integration is reverse-engineered from prose.
- fix direction: Add `depman schema` and `depman schema --fingerprint` (with `schema_version` and `fingerprint_scope`), declaring per command: read-only vs mutating, output class (`ls` → `list`, `install`/`sync` → `record` or `bulk-result`), shape in JSON Schema, stdin contract, side effects, latency class, timeouts, and a per-command error catalog mapping symbolic codes to exit codes with `retryable`/`reconcile_first`. Add a single machine profile flag (e.g. `--machine`) implying JSON output, no prompts, no color/banners/progress, no update check.

### F5 — `sync` uses exit `4` for "confirmation required"
- severity: P2
- type: design-issue
- evidence: observed (user capture: `exit=4` with `CONFIRMATION_REQUIRED`)
- location: `depman sync --json < /dev/null`
- impact: Under the skill's suggested exit-code convention `4` means unauthenticated; an agent branching on the shell exit may try re-authenticating instead of passing `--yes`. With no declared map (F4), the meaning is unknowable from the exit alone.
- fix direction: Map `CONFIRMATION_REQUIRED` to `2` (usage/validation: a required flag was not supplied) or a declared domain code in `10`–`125`, and declare it in the `sync` error catalog with "suppressed by `--yes`".
- note (what is right here): `sync` did not hang on closed stdin, wrote nothing to stdout, and emitted a well-formed structured error on stderr with `code`, `message`, `hint`, and `temporary: false`. Keep this behavior and use it as the template for F3.

### F6 — `sync`, `clean`, and `install` mutate with no dry run, idempotency, or reconciliation contract
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `--dry-run`; no interrupt or retry semantics documented)
- location: `depman --help` Commands/Options
- impact: Agents cannot preview `clean` (deletes from the global cache) or `sync` (rewrites the lockfile) before committing, and after a timeout cannot tell whether `install` or `sync` completed.
- fix direction: Add `--dry-run` to all three, returning `dry_run: true` plus the planned changes. Declare that installs are idempotent (re-running is safe) or provide a status/lookup path, declare SIGINT behavior and whether lockfile writes are atomic, and lock the global cache and lockfile against concurrent invocations. Consider requiring `--yes` (or non-TTY failure as `sync` already does) for `clean`, since it is destructive and currently has no documented confirmation.

### F7 — Ambient state is undocumented and uninspectable
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (a global cache exists per `clean`'s summary; no config, env vars, registry credentials, or inspection commands are documented)
- location: `depman --help`
- impact: Agents cannot know which registry, credentials, or cache state an `install` will use, nor run in a clean environment.
- fix direction: Document credential sources, config files, env vars, and cache location with precedence (flags > env > config > cache); add `depman config show --resolved` (secrets redacted) and an `--isolated`/`--no-config` flag.

### F8 — Command naming and help prose are not task-selective
- severity: P3
- type: design-issue
- evidence: observed (user capture of `--help`)
- location: `ls  Show stuff`; `install (aliases: i, add)`; `--quiet  Less output`; banner `the friendly dependency manager!`
- impact: "Show stuff" does not say what `ls` lists (installed deps? lockfile? cache?); `--quiet` does not say what it suppresses or whether it affects JSON; aliases `i`/`add` invite agents to use non-canonical forms.
- fix direction: Write summaries rules-first and selective, e.g. `list  List installed dependencies of the current project (read-only)`. Prefer full-word canonical names (`list` with `ls` as a declared alias); declare aliases in the schema and keep them out of examples. Describe `--quiet` and `--yes` precisely (what is suppressed; which commands `--yes` applies to). Add `--` end-of-options support and declare it, since package names are operands.

### F9 — No evidence of contract tests
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (no source or tests supplied)
- location: n/a
- impact: F1 and F3 suggest stdout cleanliness and error payloads are not pinned; regressions will recur silently.
- fix direction: Add tests for: `--json` stdout parses as one JSON document; failures leave stdout empty and put one structured object on stderr; declared exit codes match observed exits; non-TTY stdin never prompts; no network call on `ls`; dry-run behavior; concurrent cache/lockfile writes.

## Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F4 |
| Stdin Contract | Partly OK: `sync` with `< /dev/null` failed fast rather than prompting (observed). Undeclared otherwise → F4. |
| Shell Safety | F8 (`--` support); hint `"pass --yes"` embeds no caller input — OK |
| Agent-Safe Invocation | F4 (no machine profile); non-TTY prompt suppression OK for `sync` (observed); banner/update check in non-TTY → F1, F2 |
| Output | F1 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F8 |
| Tests | F9 |

## Open Questions / Assumptions

- Was `install nonexistent-pkg` run without `--json` on purpose? If `--json` produces a structured stderr error like `sync`'s, F3 narrows to the default mode, but the text error still belongs on stderr and still needs a non-generic exit code.
- Does `ls --json` with a TTY stdout behave differently? Only the redirected-stderr case was captured; the banner appeared on stdout even then, which is enough for F1.
- What does the update check contact, and does it write a cache/timestamp file? That decides whether F2 also includes an implicit write.
- Does `clean` prompt or require `--yes`? Not captured; if it prompts in non-TTY mode without failing fast, that would be `P0`.
- What do stdout and stderr contain for `ls --json` on stderr? Not captured; warnings there are fine if non-interleaved and suppressible.

## Suggested Remediation Order

1. F1 + F2: strip banner/summary/update check from stdout; disable update checks on reads and in non-TTY mode.
2. F3: route every failure through the structured error object `sync` already emits, with meaningful exit codes.
3. F4 + F5: publish `depman schema` with a declared exit-code map and a `--machine` profile; remap `CONFIRMATION_REQUIRED`.
4. F6, F7, F9, then F8.
~~~~~~
