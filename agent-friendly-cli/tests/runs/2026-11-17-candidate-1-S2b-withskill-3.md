# Scenario 2b (audit, fail-fast control) — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/2 scored
- **Tokens:** 64,791 (final-turn context plus output, read from the transcript)
- **Output words:** 1,460
- **Transcript sha256:** `9c0ca3131784134d684d776e6c37dc0553e76503a3648344a95847cbe4cb037a` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2b-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **FAIL** | No hang claim ("`sync < /dev/null` did not block"), but F4 — P1 (top severity) covers the sync prompt: "Map `CONFIRMATION_REQUIRED` to exit `2` ... or to a declared domain code" Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding carries top severity = fail |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author, who can change anything.
I could not run the tool, so every `observed` label below refers to the verbatim captures you supplied.
Stream attribution comes from your redirects: lines captured with `2>/dev/null` are stdout, and the last capture is stderr only.

## Findings (ordered by severity)

Release gating: F1–F5 are P0/P1 findings, so each blocks a release until fixed.

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: `impl-bug` (`--json` promises JSON, but stdout is not valid JSON)
- evidence: `observed` (supplied capture of `depman ls --json 2>/dev/null`)
- location: stdout lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` around the array
- impact: `json.loads(stdout)` fails, so agents have to strip lines by heuristic. Non-ASCII glyphs and timing text also make the output non-deterministic and add tokens.
- fix direction: In JSON or machine mode, stdout carries only the payload. Send the banner, progress, and timing to stderr, or drop them, and suppress them on non-TTY stdout. Add a test that parses stdout of every `--json` command as a single JSON document.

### F2 — P1 — Hidden update check (likely a network call) on a read path
- type: `design-issue`
- evidence: `observed` that the check runs (`Checking for updates...` on stdout of `ls`). That it makes a network call is `inferred`.
- location: `depman ls --json` stdout
- impact: A read verb makes an undeclared network call. It adds latency and can fail or hang offline or in sandboxes, and agents cannot predict or disable it. The P1 placement is fixed because nothing shows the check stays on the local machine.
- fix direction: Turn update checks off by default, or at least suppress them in machine mode and non-TTY mode. Never print their output to stdout. If you keep the check, declare it in the schema's side effects and provide an opt-out such as `DEPMAN_NO_UPDATE_CHECK=1` or `--isolated`.

### F3 — P1 — `install` failure: no symbolic code, prose on stdout, cause hidden behind a log
- type: `impl-bug` (failure output belongs on stderr) plus `schema-gap` (no error contract)
- evidence: `observed` (`Error: something went wrong (see log)` appears with `2>/dev/null`, so it went to stdout; exit `1`)
- location: `depman install nonexistent-pkg` capture
- impact:
  - Agents cannot branch on the failure. The not-found case uses generic exit `1`, and there is no `code` field.
  - The error goes to stdout, where it pollutes the success stream.
  - "see log" points to an undeclared log file, so the actual cause can't be found without guessing where the log is.
- fix direction:
  - Emit `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg"}` on stderr, leave stdout empty, and exit `3` (not found). `sync` already does this; make every command follow it.
  - Declare an `INTERNAL` fallback code (exit `1`) for anything unanticipated.
  - If a log exists, put its path in the error's `path` field.

### F4 — P1 — No machine-readable contract: no schema, no machine profile, no exit-code map
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` lists no `schema` command, no `--json`/`--machine` global flag, and no exit codes). `--json` works but isn't documented in help.
- location: `depman --help`
- impact:
  - Agents learn flags by trial; `--json` only appears in the captures.
  - Exit `4` from `sync` is undocumented, and under this skill's convention `4` means unauthenticated, so a caller following that convention would misread it.
  - Nothing tells an agent which commands mutate, read stdin, or touch the network.
- fix direction:
  - Add `depman schema` (plus `schema <command>` and `schema --fingerprint`). It should cover:
    - the command tree, with aliases declared
    - flags, with types and defaults
    - read-only vs mutating
    - the output class per command (`ls`: `list`)
    - stdin contract
    - side effects
    - the latency class
    - the exit-code map
    - a per-command error catalog
  - Add a single `--machine` profile that implies JSON, no prompts, no banners or color, and no update check.
  - Map `CONFIRMATION_REQUIRED` to exit `2` (usage/validation) or to a declared domain code ≥10, and record that mapping in the schema.

### F5 — P1 — No tests evident for the contract
- type: `schema-gap`
- evidence: `absence-of-evidence` (no source or test suite was supplied)
- impact: F1 and F3 suggest no test pins payload purity or error shape.
- fix direction: Add tests for:
  - stdout of every `--json` command parsing as a single JSON document
  - failure payloads and exit codes
  - TTY vs non-TTY behavior
  - suppression of the update check in machine mode
  - non-interactive `sync`
  - dry-run behavior for mutations

  This finding is rated P1 because the tests guard the P1 behaviors above.

### F6 — P2 — Mutating commands lack `--dry-run`, and mutation classification is undeclared
- type: `schema-gap`
- evidence: `absence-of-evidence` (help shows no `--dry-run`; `clean` and `sync` mutate)
- location: `depman --help`
- impact:
  - `clean` deletes from a global cache, and help shows no confirmation for it, so agents cannot preview the deletion.
  - `--yes` is a global "assume yes" flag, so one flag silently approves every mutation.
- fix direction:
  - Add `--dry-run` to `install`, `clean`, and `sync`. Its output should include `dry_run: true` and the planned effect.
  - Declare `clean`'s confirmation behavior and its concurrency safety against the shared global cache, and declare interrupt semantics for `sync` and `install`.

### F7 — P2 — Ambient state undeclared
- type: `schema-gap`
- evidence: `absence-of-evidence`. That the CLI uses ambient state at all is `inferred` from the global cache, the lockfile, and the log.
- impact: Agents can't tell which lockfile or cache a run will touch, or whether the current directory selects the project.
- fix direction:
  - Document how the cache location, lockfile discovery (current directory?), config, and env vars are resolved.
  - Add `depman config show --resolved` and an `--isolated` mode.

### F8 — P2 — `install` and `ls` don't follow the checklist's Command Model
- type: `design-issue`
- evidence: `observed` (help)
- impact:
  - Three names for `install` (`i` and `add` are aliases) mean agents' call sites vary.
  - `ls` is an abbreviation.
  - The commands are verbs with no nouns, which matters as the tool grows (e.g., cache vs. lockfile operations).
- fix direction:
  - Pick canonical names and keep aliases only for migration, declared in the schema and kept out of examples.
  - Consider `list`.
  - Add `--limit`, `--filter`, and a declared deterministic sort to `list`.

### F9 — P3 — Prose surfaces are not task-selective
- type: `design-issue`
- evidence: `observed` (help)
- location: `ls  Show stuff`, `--quiet  Less output`, banner line
- impact: Agents can't tell from help what `ls` lists (direct deps? installed? cache?) or what `--quiet` suppresses.
- fix direction:
  - Write the summaries rules-first, e.g. `ls  List installed packages (name, version) for the current project; read-only`.
  - Have `--quiet` state exactly what it suppresses, or replace it with the machine profile.
  - Drop the marketing banner from help.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F4 |
| Stdin Contract | F4 (undeclared). `OK` on behavior: `sync < /dev/null` did not block |
| Shell Safety | `not-checked`: no `--` support visible in help, and no hostile-argument captures |
| Agent-Safe Invocation | F2, F4. `OK` partly: non-interactive `sync` fails fast with exit 4 instead of hanging, but no machine profile exists |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F4. `OK` partly: the `sync` error is well-formed (`code`/`message`/`temporary`/`hint`, stderr only) |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F9 |
| Tests | F5 |

## Open questions / assumptions

- Does `Checking for updates...` make a network request every time? I assumed so. If it only consults a local cache, F2 drops to P2.
- Does `ls` also print the banner in TTY or non-`--json` mode? I assumed it does in every mode.
- Does `install` fail the same way on stdout when `--json` is passed? It was captured without `--json`.
- Is there an exit-code map anywhere (docs or source) that defines `4`?
- `clean`'s confirmation behavior isn't shown. If it deletes without asking, F6 rises.

## Suggested remediation order

1. Clean stdout and gate the update check (F1, F2). These are small changes.
2. Use the structured error shape from `sync` everywhere, with a code catalog and exit-code map (F3, F4).
3. Add a `schema` command and a `--machine` profile, with contract tests (F4, F5).
4. Add dry-run, document ambient state, and settle command names and help text (F6–F9).
~~~~~~
