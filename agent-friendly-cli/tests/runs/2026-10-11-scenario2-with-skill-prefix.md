# Scenario 2 (Audit) — with-skill run (wording before commit 4)

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill files as of commit c154b17)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set). Ran against the skill text of commit c154b17, before the Codex implementation-review fixes in commit 4; the final-wording validation run is recorded separately.
- **Score:** 8/8 scored; 4/4 non-scored conformance
- **Subagent tokens:** 74,883 (harness-reported total for the run)
- **Transcript sha256:** `4f0085b4d53e1a9e7a765f451a2329b057d75a12f3588e005cd1d38b2ad8a344` (session-local copy; not committed)

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

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files or run git.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; nothing under `tests/`; no other file. The wrapper also forbade running the tool described.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| S1 | `sync` prompting for confirmation is flagged as a hang risk in automation and ranked as the most severe finding, above stdout pollution (Invocation Safety, Severity). | **PASS** | F1 `P0` ("fixed placement: blocking behavior in machine or non-TTY mode"), ranked above F2 `P1` stdout pollution. |
| S2 | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | F1 evidence: "`inferred` — from the documented prompting in `--help` ... Not observed; `sync` was not captured." |
| S3 | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | F2: "`observed` — user-supplied capture of `depman ls --json 2>/dev/null`; stderr was discarded, so all four lines are stdout"; "`depman ls --json \| jq` fails". |
| S4 | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | F4 `P1`: "an agent has nothing to branch on". |
| S5 | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | F3 `P1` with the local-only downgrade rule cited and declined for lack of evidence. |
| S6 | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | F7: "`clean` deletes from a global, shared cache with no visible preview ... add `--dry-run` to all three mutating commands". |
| S7 | Alias duplication (`i`, `add`) and the vague `ls  Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | F6 covers both: "`ls  Show stuff` gives an agent nothing to choose on" and "`install` advertises aliases `i, add` in the canonical help". |
| S8 | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Coverage table: Tests `not-checked` with reason; Stdin and Shell Safety covered by an `absence-of-evidence` finding (F9). |
| C1 | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`. | met | severity / type / evidence / location / impact / fix direction on every finding. |
| C2 | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | met | All three used. |
| C3 | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | met | F1 `P0`, F2 `P1`. |
| C4 | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | met | Twelve-row table including the new Shell Safety and Prose Surfaces sections. |

**Set:** challenge.
**Regression vs same-day baseline (6/8):** none.
**Overhead:** 74,883 vs 41,044 subagent tokens (1.82x).
**Notes:** the two baseline misses (hang ranking, alias duplication) are exactly the two the treatment closes.
The new Severity fixed placements were cited by name on F1, F2, F3, and F4; the evidence field was present on every finding.

## Full final output

Verbatim final message returned by the subagent:

# Agent-friendliness audit: `depman` 3.2

Audience: tool author (can change anything), so findings lead with contract gaps and concrete redesign guidance.
Task class: audit of an existing CLI from a captured session; nothing was run.
Evidence basis: three user-supplied captures, each with stderr discarded (`2>/dev/null`), so every line shown is known to be stdout.
That makes stream attribution `observed`, not inferred.

## 1. Findings (by severity)

### F1 — `sync` prompts for confirmation; no evidence it detects non-TTY or machine mode
- severity: `P0` (fixed placement: blocking behavior in machine or non-TTY mode)
- type: `design-issue`
- evidence: `inferred` — from the documented prompting in `--help` ("Sync the lockfile (asks for confirmation first)") and the absence of any documented non-interactive behavior other than `--yes`. Not observed; `sync` was not captured.
- location: `depman --help`, `sync` summary and `--yes` option
- impact: an agent that runs `depman sync` in CI or through a tool call without `--yes` waits on terminal input indefinitely. Nothing in the help tells an agent that `--yes` is mandatory in automation, and `--yes` is a global flag whose effect on `install` and `clean` is undeclared, so an agent cannot tell which commands will block.
- fix direction: when stdin is not a TTY, or a machine flag is set, never prompt. Either proceed (if `--yes` is given) or fail fast with a structured error on stderr, e.g. `{"code":"CONFIRMATION_REQUIRED","message":"sync modifies the lockfile; pass --yes to confirm.","hint":"--yes","temporary":false}` with exit `2`. Declare, per command, whether it can prompt and which flag suppresses the prompt. Fold `--yes` into the machine profile (see F5) so one flag makes the whole CLI non-interactive.

### F2 — `ls --json` mixes a banner, a progress line, and a timing summary with the JSON payload on stdout
- severity: `P1` (fixed placement: successful stdout that mixes banners, progress, or summaries with the payload)
- type: `impl-bug`
- evidence: `observed` — user-supplied capture of `depman ls --json 2>/dev/null`; stderr was discarded, so all four lines are stdout.
- location: output of `depman ls --json`: `✨ DepMan 3.2`, `Checking for updates...`, `[{...}]`, `Done in 0.42s ✓`
- impact: `depman ls --json | jq` fails. An agent must heuristically find the JSON line, which breaks the moment the banner wording or line count changes. The `Done in 0.42s` line is also non-deterministic run to run, so output cannot be snapshot-tested or cached, and the emoji/decoration spends tokens on nothing. The payload itself (a bare array of `{name, version}`) is a reasonable `list`-class shape for a small finite collection; the problem is everything around it.
- fix direction: stdout is success payload only. Move the banner, progress, and summary to stderr in human mode and suppress them entirely when `--json` (or the machine profile) is set. Drop the timing line from any non-TTY output, or put it in a structured stderr record (`{"type":"progress",...}`) if you want to keep it, with the framing declared in the schema. Add a test that asserts `depman ls --json` stdout parses as JSON with nothing else.

### F3 — `ls` (a read verb) performs an undeclared update check
- severity: `P1` (fixed placement: hidden side effect on a read path, including update checks; downgrade to `P2` only with evidence the effect is local — none is available)
- type: `design-issue`
- evidence: `observed` that the line `Checking for updates...` appears during `ls --json`; `inferred` that it is a network call (an update check with no network would be meaningless).
- location: output of `depman ls --json`, line 2
- impact: a plain read becomes a network call with unbounded latency, a failure mode unrelated to listing (`ls` can fail or stall offline), and, if it is a self-update check, a phone-home the caller never asked for. The help text declares none of this. It is ambiguous whether this checks for newer *package* versions or a newer *depman*; either way it is outside `ls`'s declared purpose ("Show stuff").
- fix direction: remove the check from `ls`. If an update check exists at all, make it opt-in, never run it in machine or non-TTY mode, never write it to stdout, and declare it in the schema under side effects and ambient state (with the env var or config key that disables it). If the intent is "show outdated packages", make that a separate command or flag (`depman outdated`, `ls --outdated`) with `latency_class: network` declared, and leave the default `ls` at `latency_class: local`.

### F4 — Failure is a prose sentence on stdout with a generic exit code and no symbolic code
- severity: `P1` (fixed placement: errors that offer no symbolic code to branch on)
- type: `impl-bug`
- evidence: `observed` — user-supplied capture of `depman install nonexistent-pkg 2>/dev/null` printed `Error: something went wrong (see log)` with stderr discarded, so the error went to stdout; `echo $?` showed `1`.
- location: output and exit of `depman install nonexistent-pkg`
- impact: an agent has nothing to branch on. Exit `1` does not distinguish "package not found" from "registry unreachable" from "lockfile conflict", so it cannot decide whether to retry, rename, or escalate. The error is on stdout, the success stream, so a caller that routes streams correctly sees the failure text where it expects payload. "See log" points to an undeclared location the agent cannot open. The message names neither the package nor a correction.
- fix direction: emit a structured error object on stderr and leave stdout empty on failure in machine mode. For this case: `{"code":"PACKAGE_NOT_FOUND","message":"Package not found.","resource_id":"nonexistent-pkg","field":"<package>","hint":"Check the spelling or registry.","temporary":false}` with exit `3`. Declare the numeric exit-code map and the per-command error catalog (which codes `install` can return, their exit codes, `retryable`, `reconcile_first`). If a log file exists, put its path in a `path` or `details.log_path` field rather than in prose. Declare the stderr framing as a closed enum (`single-error-object` or `ndjson-typed`).

### F5 — No machine schema, fingerprint, exit-code map, or declared machine profile; `--json` is undocumented
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence` for schema/fingerprint/exit codes/version command; `observed` that `--json` is accepted by `ls` yet absent from the `--help` Options list.
- location: `depman --help` (Options lists only `--quiet` and `--yes`); `depman ls --json` capture
- impact: the only structured output flag that exists cannot be discovered from help. `--quiet` ("Less output") and `--yes` ("Assume yes") have no declared semantics: an agent cannot tell whether `--quiet` suppresses the banner and `Done in` lines (which would make `--json --quiet` the de facto machine profile), or whether `--yes` affects `clean` and `install`. There is no `depman schema`, no fingerprint to cache against, no exit-code map, and the version is only discoverable by parsing the banner (`DepMan 3.2`). Checklist § Machine Schema items (stdin contract, read-only vs mutating, latency class, side effects, timeouts, output class per command) are all undeclared. No stable substitute (`--help --json`, completion metadata, generated schema file) is visible in the captures.
- fix direction: add `depman schema` (full contract) and `depman schema --fingerprint` (`schema_version`, `fingerprint`, `fingerprint_scope`), plus `depman version` or `--version`. Declare one canonical machine profile, ideally a single `--machine` that implies `--json`, no prompts (`--yes` behavior or fail-fast per F1), no color, no progress, no update check. List `--json` in `--help` now, and give `--quiet` and `--yes` precise definitions (what each suppresses or answers, and for which commands).

### F6 — Help prose is not task-selective and leads with branding rather than constraints
- severity: `P2`
- type: `design-issue`
- evidence: `observed` — `depman --help` capture
- location: `depman --help`
- impact: `ls  Show stuff` gives an agent nothing to choose on: installed packages? the manifest? the lockfile? direct vs transitive? outdated? An agent picking between `ls` and `sync` to answer "what is pinned" has to guess. `clean` says it removes from the "global cache" but not what counts as unused, whether it is interactive, or whether it is reversible. The first line is a slogan (`the friendly dependency manager!`), context before any rule. `install` advertises aliases `i, add` in the canonical help; the checklist reserves aliases for migration and keeps them out of canonical surfaces, and `add` in particular usually means "add to manifest", which may not be what `install` does.
- fix direction: rewrite each summary rules-then-context, with enough to pick between siblings: e.g. `ls    List installed packages from the lockfile (read-only, local)`; `clean  Delete cache entries not referenced by any lockfile (mutating; supports --dry-run)`; `sync   Rewrite the lockfile from the manifest (mutating; prompts unless --yes or non-TTY)`. Drop the slogan from `--help`. Move aliases out of the main listing into the schema's `aliases` field with a deprecation note, or remove `add` if its semantics differ from `install`. Note: the checklist says to use a separating-context-from-constraints skill as the lens here if available; it was not available in this session, so this finding rests on the checklist's own Prose Surfaces rules.

### F7 — Mutations (`install`, `sync`, `clean`) declare no dry-run, idempotency, reconciliation, or interrupt semantics
- severity: `P2` as a contract gap; becomes `P1` (fixed placement) if in fact there is no way to reconcile an interrupted or failed `install`/`sync`
- type: `schema-gap`
- evidence: `absence-of-evidence` — nothing in `--help` or the captures declares any of these
- location: `depman --help`, `install`/`sync`/`clean` entries; the failed `install` capture
- impact: after `install` exits `1` (F4), an agent cannot tell whether the lockfile or manifest was touched, whether the operation is safe to re-run, or whether a partially-fetched package is now in the cache. `clean` deletes from a global, shared cache with no visible preview. There is no `--dry-run`, `--frozen-lockfile`, or `--if-not-exists`-style replay control, and nothing says what SIGINT during `install` leaves behind, or whether two concurrent `depman` processes can corrupt the lockfile or cache.
- fix direction: add `--dry-run` to all three mutating commands with `dry_run: true` in the output and the planned effect listed (for `clean`: the entries and bytes that would be removed). Declare `install`/`sync` as idempotent on retry if they are (same inputs, same lockfile), or provide a status/verify command (`depman verify`) that confirms lockfile consistency before a retry. Declare lockfile writes as atomic (write-temp-then-rename) and cache operations as locked, and document what an interrupt leaves behind. Put all of this in the schema's `side_effects`, `reconciliation`, and `errors_possible` fields.

### F8 — Ambient state (global cache, lockfile, registries, config, credentials) is undocumented and cannot be inspected or disabled
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence` — `--help` mentions a "global cache" and "the lockfile" and nothing else; no `config`, `--no-config`, `--isolated`, or inspection commands are visible
- location: `depman --help`
- impact: an agent cannot predict which registry `install` hits, where credentials come from, which config files alter behavior, or where the cache lives; it cannot run `depman` in a clean sandbox to get reproducible results; and if the update check in F3 is configurable, there is no visible way to find or set that configuration.
- fix direction: document credential sources, config files, environment variables, cache location, and precedence (flags > env > config > cache). Add `depman config show --resolved` (with secrets redacted) and an isolation flag (`--isolated` or `--no-config`). Keep the isolation profile distinct from the machine profile.

### F9 — Shell-safety and stdin contracts are undeclared
- severity: `P3`
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help`
- impact: no declared `--` end-of-options support, so an agent cannot safely pass package specs or paths that begin with `-`; no declaration of whether any command reads stdin (e.g. a package list piped to `install`) or how empty stdin is handled. Low risk today because package names rarely start with `-`, but it is a gap the schema should close.
- fix direction: support and declare `--`; declare a stdin contract per command (`reads: false` is fine, but say so).

## 2. Checklist coverage

| Section | Status |
|---|---|
| Command Model | covered by F6 (`ls` summary, aliases in canonical help, `ls` abbreviation vs full-word `install`) |
| Machine Schema | covered by F5 |
| Stdin Contract | covered by F9 |
| Shell Safety | covered by F9 |
| Agent-Safe Invocation | covered by F1, F5 (no machine profile; prompt not suppressed in non-TTY) |
| Output | covered by F2, F4 |
| Errors And Exit Codes | covered by F4 (no symbolic code; exit `1` for a not-found case; no declared map, so the observed exit matches nothing) |
| Ambient State | covered by F8 |
| Mutations And Long-Running Work | covered by F1, F7 |
| Side Effects And Telemetry | covered by F3 |
| Prose Surfaces | covered by F6 |
| Tests | `not-checked`: no source or test tree was available; given F2 and F4, a stdout-is-JSON test and an exit-code mapping test evidently do not exist or do not run |

## 3. Open questions and assumptions

- Does `sync` already detect non-TTY stdin and skip the prompt? If so, F1 drops to a `P2` documentation gap. The help text gives no sign of it.
- Does `clean` prompt? If it does and `--yes` is the only escape, it inherits F1.
- Does `--quiet` suppress the banner, `Checking for updates...`, and `Done in` lines? If `--json --quiet` yields clean stdout, F2's immediate fix is to make `--json` imply that, and to document it.
- Does `--json` apply to `install` and to errors? The failure capture ran without `--json`; the machine-mode failure shape is unknown.
- Is `Checking for updates...` a depman self-update check or a registry refresh for package versions? The fix differs (remove vs separate command) but the severity does not.
- Was the `install` failure actually not-found, or a registry/network error? The message cannot tell us, which is F4's point.
- Did the failed `install` modify the manifest, lockfile, or cache? Unknown; feeds F7.
- What does `ls` list: installed packages, manifest entries, lockfile entries, direct only or transitive? Needed for F6's rewrite.
- Where is "the log" referenced by the error message?
- The checklist asks to use a separating-context-from-constraints skill as the lens for prose surfaces; it was not available in this session, so F6 rests on the checklist's own Prose Surfaces rules.
- Severity labels follow review-workflow.md's fixed placements; F1 is `inferred`, not observed, and should be confirmed with one probe: `echo | depman sync` (stdin non-TTY) with a timeout, which is safe only in a scratch project since `sync` mutates the lockfile.

## 4. Suggested remediation order

1. Stop the bleeding (F1, F2, F4): never prompt when stdin is not a TTY; make `--json` put nothing but JSON on stdout; emit structured errors on stderr with a symbolic `code` and a declared exit code. These three are small code changes and remove every `P0`/`P1` except F3.
2. Remove the update check from `ls`, or move it behind an opt-in flag that is off in machine mode and never writes to stdout (F3).
3. Add `depman schema` and `schema --fingerprint`, declare the machine profile (`--machine` implying `--json`, no prompts, no progress, no update check), and list `--json` in `--help` (F5).
4. Rewrite command summaries rules-first and task-selective; remove aliases from the canonical listing (F6).
5. Add `--dry-run`, declare reconciliation and interrupt behavior, and document ambient state with `config show --resolved` and an isolation flag (F7, F8, F9).
6. Pin each of the above with tests: stdout-parses-as-JSON, declared-exit-codes-match-observed, non-TTY-never-prompts.
