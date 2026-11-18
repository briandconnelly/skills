# Scenario S2b — with-skill arm 2 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1234
- **Scoring:** blinded packet, output id `o21`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2b-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

## A1: No finding claims `sync` hangs/blocks in automation, and no `sync`-prompt finding carries top severity
- o21: PASS
  - Part 1: PASS — F6: "the non-TTY behavior itself is good (no hang...)".
  - Part 2: PASS — F6 "(P2)"; top is P1.
## A2: Stdout pollution on `ls --json` is still flagged
- o21: PASS — F1 "`ls --json` stdout mixes banner, update-check text, and summary with the payload (P1)".

## Verbatim final output

~~~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author (can change anything).
Evidence source: user-supplied verbatim captures; I did not run the tool.
Release gating: F1–F4 (P1) block a release until fixed.

## 1. Findings (by severity)

### F1 — `ls --json` stdout mixes banner, update-check text, and summary with the payload (P1)

- type: `impl-bug` (`--json` promises a JSON payload)
- evidence: `observed` (user capture, stderr discarded)
- location: `depman ls --json 2>/dev/null` — lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the array
- impact: `json.loads(stdout)` fails; agents must guess which line is the payload, and the guess breaks when wording changes.
- fix direction: in `--json` (and in any non-TTY stdout), stdout is exactly one JSON document. Drop the banner and the timing line entirely in machine mode; if timing is useful, put it in a declared field or a structured stderr diagnostic.

### F2 — Read command performs an update check by default (P1)

- type: `design-issue`
- evidence: `observed` (`Checking for updates...` on `ls`), network call `inferred` from the text
- location: `depman ls --json` output
- impact: an undeclared network call on a read path — adds latency, can fail or hang offline/in sandboxes, and leaks usage. Not downgraded to P2: nothing shows it is local-only.
- fix direction: make update checks opt-in (e.g. `DEPMAN_UPDATE_CHECK=1` or `depman self update-check`), never in machine mode, never on stdout.

### F3 — `install` failure has no symbolic code, goes to stdout, and exits generic `1` (P1)

- type: `impl-bug` (failure on stdout) + `schema-gap` (no error contract)
- evidence: `observed` (`Error: something went wrong (see log)` printed with stderr discarded, so it is stdout; `$?` = 1)
- location: `depman install nonexistent-pkg`
- impact: agents cannot tell "package not found" from network, auth, or bug; "see log" names no log path; stdout is polluted on failure.
- fix direction: emit the same structured object `sync` already uses, on stderr, with empty stdout:
  `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","field":"<package>","hint":"check the package name"}` and exit `3` (not found).
  Add a fallback `INTERNAL` (exit 1) for uncaught failures and a log `path` field when a log exists.

### F4 — No machine profile, no structured error mode on `install`/`ls` by default (P1)

- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` lists only `--quiet`, `--yes`; `--json` exists but is undocumented)
- location: `depman --help`
- impact: agents cannot know which flags yield stable output; `--quiet` ("Less output") does not define what is removed; `--json` support per command is unknown.
- fix direction: add a single `--machine` flag (implies `--json`, no banners, no color/progress, no prompts, no update check, structured stderr errors) and declare it; document `--json` per command.

### F5 — No machine-readable schema or fingerprint (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence` (no `schema` command or `--help --json` in help)
- location: `depman --help`
- impact: agents parse prose help to discover commands, flags, output shapes, and exit codes; every release risks silent breakage.
- fix direction: add `depman schema [command]` and `depman schema --fingerprint` declaring command tree, aliases, flags/types/defaults, read-only vs mutating, output class (`ls`: `list`; `install`/`sync`/`clean`: `record` or `bulk-result`), stdin contract, exit-code map, per-command error catalog, side effects, latency class, `schema_version`, `fingerprint_scope`.

### F6 — `sync` uses exit `4` for "confirmation required" (P2)

- type: `design-issue`
- evidence: `observed` (exit=4 with `CONFIRMATION_REQUIRED` on stderr)
- location: `depman sync --json < /dev/null`
- impact: the non-TTY behavior itself is good (no hang, clean structured stderr, empty stdout, `temporary:false`, actionable `hint`). But `4` conventionally means unauthenticated; shell-level callers branching on exit codes will misclassify it. The mapping is undeclared.
- fix direction: map `CONFIRMATION_REQUIRED` to `2` (usage — a required flag is missing) or a declared domain code (`10`+), and declare it in the error catalog. Consider `"field":"--yes"` and `"details"` in the payload so the repair is machine-usable, not only in `hint`.

### F7 — Mutations lack `--dry-run`, retry/interrupt semantics, and confirmation on `clean` (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence` (help shows no `--dry-run`; `clean` "Remove unused packages from the global cache" shows no confirmation note)
- location: `depman --help`
- impact: agents cannot preview `install`/`sync`/`clean`; unknown whether `clean` deletes without confirmation; unknown whether an interrupted `install`/`sync` leaves a half-written lockfile or whether concurrent runs are safe.
- fix direction: add `--dry-run` (output with `dry_run: true`) to `install`, `sync`, `clean`; declare idempotency (install is likely repeat-safe), atomic lockfile writes and locking, and SIGINT behavior.

### F8 — Ambient state undocumented (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help`
- impact: `clean` touches a global cache; `sync` works on a lockfile probably selected by cwd; registry credentials/config sources unknown. Agents get burned by hidden state.
- fix direction: document config files, env vars, cache location, cwd-selected project and an override flag (e.g. `--project <path>`), precedence; add `config show --resolved` and `--isolated`/`--no-config`.

### F9 — Command model: vague `ls`, alias sprawl, abbreviations (P3)

- type: `design-issue`
- evidence: `observed` (help text)
- location: `depman --help`
- impact: "Show stuff" does not let an agent choose `ls`; aliases `i`/`add` invite inconsistent invocations; `ls` abbreviates.
- fix direction: rename to `list` (keep `ls` as declared alias), summary "List installed dependencies with name and version"; declare aliases in schema and use only canonical names in examples. Rewrite help rules-first: `sync` should say "Requires --yes in non-interactive use; exits N with CONFIRMATION_REQUIRED otherwise".

### F10 — No metadata-path guarantees / timeouts (P3)

- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help`
- impact: networked commands (`install`, `sync`, update check) show no `--timeout-ms` or retry policy; `--help` puts a marketing banner first.
- fix direction: add `--timeout-ms` to networked commands, declare retries; keep `--help` network-free.

## 2. Checklist coverage

| Section | Status |
| --- | --- |
| Command Model | F9 |
| Machine Schema | F5, F4 |
| Stdin Contract | `not-checked` beyond `sync`: `sync` with `/dev/null` stdin did not block (observed); no stdin contract declared for any command (F5) |
| Shell Safety | `not-checked`: no captures of `--` handling or hostile names |
| Agent-Safe Invocation | F4, F10; `sync` non-TTY prompt suppression `OK` (observed) |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F6; `sync` error object `OK` on required fields (`code`, `message`, `temporary`) |
| Ambient State | F8 |
| Mutations And Long-Running Work | F7; `sync` explicit `--yes` trigger `OK` |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F9 |
| Tests | `not-checked`: no source or tests supplied; ship tests pinning F1, F3, F6 fixes and non-TTY behavior |

## 3. Open questions / assumptions

- Is `Checking for updates...` an actual network call, or cosmetic? (Assumed network.)
- Does `sync` prompt when stdin is a TTY? Assumed yes per help; non-TTY behavior was observed safe.
- Does `clean` confirm before deleting? Help says nothing.
- Where is "the log" from the `install` error?
- Is `--json` supported on `install`, `clean`? Only `ls` and `sync` were captured.

## 4. Suggested remediation plan

1. Machine-clean stdout: no banners/summary/update check under `--json`/non-TTY; add `--machine` (F1, F2, F4).
2. Port `sync`'s structured stderr error to all commands, with a code catalog and conventional exit codes (F3, F6).
3. Publish `depman schema` + fingerprint (F5), then ambient state, dry-run and mutation semantics (F7, F8).
4. Help/command naming polish (F9, F10), plus tests for each.
~~~~~~~~
