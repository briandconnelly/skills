# Scenario 2b (audit, fail-fast control) — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,745 (final-turn context plus output, read from the transcript)
- **Output words:** 1,201
- **Transcript sha256:** `55076458811395ccf295caee67cf18845c483d527224cd3833730be23e421496` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2b-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 (sync, P2): "the command did not hang with stdin from `/dev/null`"; top severity is P1 (F1-F3), not sync Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — `ls --json` stdout mixes banner, progress, and summary with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything), so findings lead with contract gaps and release-blocking issues.
Task: audit of an existing CLI from captured material only; no probes run.
All `observed` findings rest on the user-supplied verbatim captures (stdout-only except the final stderr-only capture).

Release gating: F1–F3 are `P1` and block a release until fixed.

## Findings

### F1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- severity: P1
- type: impl-bug (`--json` promises a JSON payload; stdout is not parseable JSON)
- evidence: observed (user capture, `depman ls --json 2>/dev/null`)
- location: lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the array on stdout
- impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks whenever the banner or summary text changes. Emoji/non-ASCII also burns tokens.
- fix direction: in JSON/machine mode stdout carries only the payload. Move banner, progress, and timing to stderr (and suppress them entirely in machine mode and when stdout is not a TTY). Add a test asserting `depman ls --json | jq .` succeeds.

### F2 — Hidden update check on a read path
- severity: P1 (no evidence the effect is local-only, so no downgrade)
- type: design-issue
- evidence: observed for the announcement (`Checking for updates...` on stdout of `ls`); the network call itself is inferred
- location: `depman ls --json` output
- impact: a read command phones home, adding latency, failure modes in offline/sandboxed agents, and nondeterminism; the notice also pollutes stdout (F1).
- fix direction: no update checks by default; make them opt-in (e.g. `depman self check-update` or a config flag), always suppressed in machine mode, and never written to stdout.

### F3 — `install` failure has no symbolic code, prose-only message, and lands on stdout
- severity: P1
- type: design-issue
- evidence: observed (`depman install nonexistent-pkg 2>/dev/null` printed `Error: something went wrong (see log)` to stdout; exit `1`)
- location: `install` error path
- impact: agents cannot branch on a not-found package vs. network failure vs. permission error; "something went wrong" has no recovery path; error text on stdout can be mistaken for payload. "see log" points at an undeclared location.
- fix direction: emit the same structured error shape `sync` already uses (`code`, `message`, `temporary`, plus `hint`, `resource_id`) on stderr, with stdout empty on failure. Use a specific code such as `PACKAGE_NOT_FOUND` with a distinct exit code (the skill convention is `3` for not-found), and a fallback `INTERNAL` code for uncaught failures. Put the log path in a structured `details.path` field, or omit it.

### F4 — No machine-readable contract (schema, fingerprint, version, machine profile)
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `schema`, `version`, or machine-mode flag; `--json` is used but not listed in help)
- location: `depman --help`
- impact: agents must learn commands, flags, output shapes, exit codes, and which commands mutate from prose and trial runs.
- fix direction: add `depman schema` (full and per-command), `depman schema --fingerprint` with `fingerprint_scope`, `schema_version`, and a single machine-profile flag (e.g. `--machine`) implying JSON output, no prompts, no banners/color/progress. Declare per command: output class, read-only vs mutating, stdin contract, latency class, timeout/retry defaults, exit codes, and error catalog.

### F5 — `sync` exit code `4` is undeclared and collides with a common meaning
- severity: P2
- type: schema-gap
- evidence: observed (`exit=4`); declaration absent
- location: `depman sync --json < /dev/null`
- impact: under the skill's suggested convention `4` means unauthenticated; an agent branching on exit code alone could misclassify. Positive: the stderr payload is well-formed (`code`, `message`, `hint`, `temporary:false`), it was the only stderr content, stdout was empty, and the command did not hang with stdin from `/dev/null`.
- fix direction: declare the exit-code map and `sync`'s error catalog (`CONFIRMATION_REQUIRED` → exit `2` usage, or a declared domain code ≥10, with `retryable: false`); declare the stderr framing as `single-error-object`.

### F6 — Mutating commands lack dry-run, confirmation, and idempotency declarations
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`--help` shows no `--dry-run`; `clean` and `install` show no confirmation gate; only `sync` is documented as confirming)
- location: `install`, `clean`, `sync` in `--help`
- impact: an agent cannot preview `clean` (which deletes from a shared global cache) or `sync`; retry safety after an interrupted `install`/`sync` is unknown; lockfile concurrency is undeclared.
- fix direction: add `--dry-run` (output with `dry_run: true`) to `install`, `clean`, `sync`; require `--yes` uniformly for destructive operations; declare interrupt semantics, retry safety (`reconcile_first`), and lockfile atomicity/locking.

### F7 — Prose help is not task-selective and has ambiguous names
- severity: P2
- type: design-issue
- evidence: observed (user capture of `--help`)
- location: `ls  Show stuff`; `--quiet  Less output`; aliases `i, add`
- impact: "Show stuff" does not say what is listed (installed deps? global cache? lockfile?); `--quiet` effect is undefined; multiple aliases invite non-canonical calls. The marketing tagline costs tokens.
- fix direction: rules-first summaries, e.g. `list  List installed dependencies of the current project (read-only)`; define `--quiet` precisely or replace with the machine profile; declare aliases in the schema as migration-only and use `install` in all examples. Consider the canonical name `list` with `ls` as a declared alias.

### F8 — Ambient state undocumented
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `--help`; references to "the global cache", "the lockfile", and "log"
- impact: agents cannot tell which project directory, config, registry credentials, cache, or log file are in play, or how to isolate a run.
- fix direction: document cwd/project selection and override flag, config files, env vars, registry credentials, cache and log locations, and precedence; add `depman config show --resolved` and an `--isolated`/`--no-config` flag.

## Checklist Coverage

- Command Model: F7 (aliases, abbreviations); otherwise shallow tree is OK.
- Machine Schema: F4, F5.
- Stdin Contract: partially OK — `sync` with `/dev/null` stdin exited promptly (observed); otherwise undeclared (F4).
- Shell Safety: not-checked — no `--` support or hostile-argument evidence in captures.
- Agent-Safe Invocation: F1, F2, F4 (no machine profile); `sync` non-TTY prompt suppression OK (observed); TTY-stdin behavior not-checked.
- Output: F1, F3.
- Errors And Exit Codes: F3, F5.
- Ambient State: F8.
- Mutations And Long-Running Work: F6.
- Side Effects And Telemetry: F2; F3 (undeclared log write, inferred).
- Prose Surfaces: F7.
- Tests: not-checked — no source or tests supplied; at minimum add tests for F1 (stdout is pure JSON), F3/F5 (error payloads and exit codes), and non-TTY prompt suppression.

## Open Questions / Assumptions

- Does `install --json` produce a structured error? Only the non-JSON `install` failure was captured; F3 assumes the prose form is the only one.
- Does `Checking for updates...` actually make a network call, and is it ever on stderr? Assumed networked.
- Does `sync` without `--json` (or with a TTY stdin but no terminal) block? Only the `/dev/null` case was captured.
- Does `ls` without `--json` honor non-TTY suppression?

## Suggested Remediation Order

1. Fix F1/F2 together: clean stdout, remove the default update check.
2. Fix F3: reuse `sync`'s structured error shape across all commands with specific codes.
3. Ship `depman schema` + fingerprint + machine profile (F4/F5), then dry-run and ambient-state work (F6/F8), then help text (F7).
~~~~~~
