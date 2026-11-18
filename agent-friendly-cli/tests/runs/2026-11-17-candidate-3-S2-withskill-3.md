# Scenario 2 (audit) — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 4/4 conformance
- **Tokens:** 65,305 (final-turn context plus output, read from the transcript)
- **Output words:** 1,631
- **Transcript sha256:** `0c89b9a19dce4a2217af02f2246497b902bdcae23b053b632894219282b1fe37` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> Each capture discards stderr (`2>/dev/null`), so every line shown is stdout.
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
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: inferred (help says "asks for confirmation first"; no machine mode or non-TTY behavior is declared) Parts: blocking risk = pass; established vs not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | help says "asks for confirmation first"; ... F1 is inferred. One safe probe would confirm or clear it |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: observed (capture, stdout only) ... `json.loads(stdout)` fails Parts: flagged breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors have no symbolic code, are written to stdout, and use a generic exit code |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Read path performs an update check (a hidden network side effect) |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` removes packages from a shared global cache, and help shows no `--dry-run` |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | F6 `ls Show stuff` not task-selective; F7 Aliases are ambiguous and undeclared Parts: aliases = pass; Show stuff = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Tests \| not-checked: no source or tests supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | - type: ... - evidence: ... - location: ... - impact: ... - fix direction: (every finding, severity P0-P3 in heading) |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | evidence: observed / inferred / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 — P0 — `sync` prompts; F2 — P1 — `ls --json` stdout mixes banners Parts: hang P0 = pass; pollution >=P1 = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Shell Safety \| not-checked: no capture of `--` handling ... \| |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Audience: the tool's author, who can change anything, so this report leads with contract gaps and the findings that block a release, followed by redesign guidance.
Evidence basis: three captures you supplied, with stderr discarded, so every line shown is stdout.
I ran nothing.
`observed` below means "observed in your verbatim capture".

## Findings (ordered by severity)

### F1 — P0 — `sync` prompts for confirmation, and nothing guarantees it won't block in automation
- type: design-issue
- evidence: inferred (help says "asks for confirmation first"; no machine mode or non-TTY behavior is declared)
- location: `depman --help`, `sync` line
- impact: an agent running `depman sync` in CI or without a TTY can hang forever waiting on stdin.
  Help does not say whether `--yes` applies to `sync`, or whether a prompt is suppressed when stdin is not a TTY.
- fix direction: when stdin is not a TTY, or in machine mode, never prompt.
  Without `--yes`, fail fast with a structured error, for example `code: "CONFIRMATION_REQUIRED"`, exit `2`, `temporary: false`, `hint: "pass --yes"`.
  Declare in the schema that `--yes` is the explicit action trigger for `sync`.
  Add `sync --dry-run`, whose output includes `dry_run: true` and lists the lockfile changes it would make.

### F2 — P1 — `ls --json` stdout mixes banners, progress, and a summary with the JSON payload
- type: impl-bug (`--json` promises JSON; stdout is not parseable as JSON)
- evidence: observed (capture, stdout only)
- location: `depman ls --json` output, lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `json.loads(stdout)` fails.
  Agents end up writing fragile line-scraping, which breaks when the banner text, emoji, or timing line changes.
- fix direction: make stdout carry only the payload.
  Send the banner, progress, and timing to stderr, and suppress them in machine mode and when stderr is not a TTY.
  Add a machine profile, such as a single `--machine` flag that implies `--format json`, no color, no prompts, and no human rendering, and declare it in the schema.

### F3 — P1 — Read path performs an update check (a hidden network side effect)
- type: design-issue
- evidence: observed (`Checking for updates...` on `ls` stdout)
- location: `depman ls --json` output
- impact: a read command makes an undeclared network call.
  That adds latency, can fail or hang offline or in sandboxes, leaks usage, and makes `ls` nondeterministic.
  Nothing shows the effect stays on the local machine, so it does not drop to P2.
- fix direction: make update checks opt-in, never run them on read commands, and suppress them in machine mode.
  Never print them on stdout.
  If you keep them, declare them in the schema's side effects and give the check its own command, such as `depman self check-update`.

### F4 — P1 — Errors have no symbolic code, are written to stdout, and use a generic exit code
- type: design-issue
- evidence: observed (capture, with stderr discarded, shows `Error: something went wrong (see log)` on stdout, and `$?` = `1`)
- location: `depman install nonexistent-pkg`
- impact: the agent cannot tell "package not found" from a network failure, auth failure, or bug.
  It cannot decide whether to retry, and it has to parse English, which here says nothing anyway.
  The error landing on stdout also breaks the rule that stdout carries only a success payload.
  "see log" points at an undeclared log location.
- fix direction: on failure, leave stdout empty and write a structured error to stderr using a declared framing (`single-error-object` or `ndjson-typed`).
  Example:
  `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","hint":"check the package name"}`
  Map it to exit `3` (not found).
  Declare a fallback `INTERNAL` code with exit `1`, and a transport-failure code for registry calls.
  If you keep a log, declare its path and include it in a `path` field rather than in prose.

### F5 — P1 — No machine-readable contract: no schema, fingerprint, version command, exit-code map, or error catalog
- type: schema-gap
- evidence: absence-of-evidence (help lists no `schema`, `version`, or `--format`; no machine-readable substitute appears)
- location: `depman --help`
- impact: agents have to guess flags, output shapes, exit codes, and which commands mutate state.
  `--json` is used, but help does not document it.
- fix direction: add `depman schema` (full contract), `depman schema <command>`, and `depman schema --fingerprint` with a `fingerprint_scope`.
  The schema should declare the command tree, aliases, flags and their types, the stdin contract, read-only vs mutating per command, output class and shape (for example, `ls` is `list` and `install` is `bulk-result`), the exit-code map, a per-command error catalog, side effects, latency class, timeouts, and `schema_version` compatibility rules.
  Replace the bare `--json` with `--format json`.

### F6 — P2 — Command summaries are not task-selective
- type: design-issue
- evidence: observed (help text)
- location: `ls  Show stuff`; `--quiet  Less output`
- impact: from "Show stuff", an agent cannot tell whether `ls` lists installed packages, lockfile entries, or the global cache.
  "Less output" does not say what is suppressed, or whether it makes output machine-safe.
- fix direction: write summaries rules-first.
  For example: `list   List packages installed in the current project (read-only; JSON with --format json)`.
  Spell out what `--quiet` suppresses, and don't let it stand in for a machine profile.

### F7 — P2 — Aliases are ambiguous and undeclared
- type: design-issue
- evidence: observed (`install` aliases: `i`, `add`)
- location: `depman --help`
- impact: in many package managers, `add` means "add to the manifest", which is different from "install from the lockfile".
  Agents may pick `add` expecting that meaning.
  Multiple aliases also make the canonical path unclear.
- fix direction: keep aliases only for migration, declare them in the schema as aliases of `install`, and never use them in examples.
  Prefer full canonical names, such as `list` over `ls`.

### F8 — P2 — Mutating commands lack dry-run, idempotency, and retry and interrupt semantics
- type: schema-gap
- evidence: absence-of-evidence
- location: `install`, `clean`, `sync`
- impact: `clean` removes packages from a shared global cache, and help shows no `--dry-run` or confirmation for it.
  Nothing declares whether concurrent runs (for example, parallel agent jobs) are safe on the global cache or lockfile.
  Nothing says what an interrupted `install` or `sync` leaves behind.
- fix direction: add `--dry-run` to every mutating command, with `dry_run: true` in the output.
  Declare locking or atomic replacement for writes to the lockfile and cache.
  Declare SIGINT/SIGTERM behavior.
  Declare which mutations are safe to retry automatically (for example, `install` of pinned versions) and which need reconciliation first.

### F9 — P2 — Ambient state is undeclared
- type: schema-gap
- evidence: absence-of-evidence
- location: help text; implied by the "global cache", the lockfile, the log, and the registry
- impact: agents cannot tell which config, registry credentials, environment variables, or working-directory project a command uses, or how to get a reproducible run.
- fix direction: document the config files, environment variables, credential sources, cache path, and how the working directory selects the project (plus a `--project <path>` override), along with precedence.
  Provide `depman config show --resolved` and an `--isolated` or `--no-config` flag.
  Accept registry tokens through the environment or a credential file, not through flags.

### F10 — P2 — No caller-settable timeout on networked commands
- type: schema-gap
- evidence: absence-of-evidence
- location: `install`, `sync`, and the update check
- impact: agents cannot bound how long a command waits on a slow registry.
- fix direction: add `--timeout-ms`, and declare retry behavior and the latency class `network`.

### F11 — P3 — Help banner and emoji in human output
- type: design-issue
- evidence: observed
- location: `DepMan 3.2 — the friendly dependency manager!`
- impact: minor token cost, and the version is not exposed in a machine-readable form.
- fix direction: keep the banner out of machine output, and add `depman version --format json`.

**Release gating:** F1 (P0) and F2–F5 (P1) block a release until they are fixed.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F6, F7 (the `ls` abbreviation, ambiguous aliases) |
| Machine Schema | F5 |
| Stdin Contract | F1 (prompt-reading is undeclared); otherwise not-checked: no stdin behavior was captured |
| Shell Safety | not-checked: no capture of `--` handling or operands that start with `-` |
| Agent-Safe Invocation | F1, F2 (no machine profile, prompts), F10 |
| Output | F2, F4 |
| Errors And Exit Codes | F4, F5 |
| Ambient State | F9 |
| Mutations And Long-Running Work | F1, F8 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F6 |
| Tests | not-checked: no source or tests supplied; at minimum, add tests that pin JSON-only stdout, non-TTY prompt suppression, and exit-code mapping |

## Open questions and assumptions
- Does `--yes` apply to `sync`, and does `sync` already skip the prompt when stdin is not a TTY? F1 is inferred. One safe probe would confirm or clear it: `depman sync < /dev/null` with a timeout, in a disposable project.
- Does anything also go to stderr? Stderr was discarded, so I can't tell whether a structured error already exists there.
- Does the update check use the network, or only a local cache? I assumed network (P1).
- Are there undocumented flags such as `--format` or `--no-update-check`? `--json` works but help doesn't list it.

## Suggested remediation order
1. Fix stdout hygiene and add the machine profile (F2), then remove the update check from reads (F3).
2. Add structured errors on stderr, with symbolic codes and the exit map (F4).
3. Make `sync` non-blocking in machine and non-TTY mode, and add `--dry-run` (F1, F8).
4. Publish `schema` and a fingerprint (F5), then clean up prose, aliases, and ambient-state docs (F6, F7, F9).
~~~~~~
