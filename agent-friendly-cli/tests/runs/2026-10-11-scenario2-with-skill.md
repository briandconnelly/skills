# Scenario 2 (Audit) — with-skill run (final wording)

- **Date:** 2026-10-11
- **Tree:** `9fa4763` (branch `fix/agent-friendly-cli-review-2026-10-11`, final skill wording after commit 4)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set). Final-wording validation run; the earlier run against commit 3's wording is in `2026-10-11-scenario2-with-skill-prefix.md`.
- **Score:** 8/8 scored; 4/4 non-scored conformance
- **Subagent tokens:** 74,183 (harness-reported total for the run)
- **Transcript sha256:** `95be3a33e3ad812b4a6aa2efb7204b5c88d758c3d93f370dec3563c54cf77da1` (session-local copy; not committed)

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

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files, run git, or run the tool described.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; nothing under `tests/`; no other file.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| S1 | `sync` prompting for confirmation is flagged as a hang risk in automation and ranked as the most severe finding, above stdout pollution (Invocation Safety, Severity). | **PASS** | F1 `P0` ("fixed placement: blocking behaviour in non-TTY mode") ranked first; F2 stdout pollution `P1` second. |
| S2 | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | F1 evidence "inferred (from documented prompting in `--help` ...)" with the P2 downgrade condition stated. |
| S3 | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | F2 "evidence: observed (user capture, stderr discarded)"; "not parseable with `json.loads`/`jq` without line-scraping". |
| S4 | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | F4 `P1` plus F6 (no exit-code map or catalog). |
| S5 | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | F3 `P1`, with the local-only downgrade explicitly declined for lack of evidence. |
| S6 | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | F8: "`clean` deletes from a global cache ... with no `--dry-run`". |
| S7 | Alias duplication (`i`, `add`) and the vague `ls  Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | F7 (`ls` summary) and F11 (aliases in canonical help; `add` reads as a different operation). |
| S8 | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Coverage table: Tests `not-checked (no source or test suite available)`; Shell Safety and Output rows name their `not-checked` sub-items. |
| C1 | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`. | met | severity / type / evidence / location / impact / fix direction on all 13 findings. |
| C2 | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | met | All three used. |
| C3 | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | met | F1 `P0`, F2 `P1`. |
| C4 | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | met | Twelve-row table. |

**Set:** challenge.
**Regression vs same-day baseline (6/8):** none.
**Overhead:** 74,183 vs 41,044 subagent tokens (1.81x).
**Notes:** the commit-4 wording landed as written: F10 cites the restored networked-command timeout rule, and `not-checked` is used for sub-items the captures cannot settle (hint/subshell handling, default sort) rather than scoring them as findings.
Same 8/8 as the pre-commit-4 run; no regression from the wording change.

## Full final output

Verbatim final message returned by the subagent:

# Agent-friendliness audit: `depman` 3.2

Audience: tool author. Task: audit (not diagnosis). Evidence base: three user-supplied captures with `2>/dev/null`, so stream attribution for every visible line is `observed` as stdout. I could not run the tool; anything not in the captures is labelled `inferred` or `absence-of-evidence` per review-workflow.md §1.

## Findings (ordered by severity)

### F1 — `sync` documents a confirmation prompt with no declared non-TTY behaviour
- severity: P0 (fixed placement: blocking behaviour in non-TTY mode). Downgrades to P2 schema-gap if you confirm the prompt is skipped or fails fast when stdin is not a TTY.
- type: design-issue
- evidence: inferred (from documented prompting in `--help`: `sync  Sync the lockfile (asks for confirmation first)`)
- location: `depman --help`, Commands section
- impact: an agent or CI job that runs `depman sync` without `--yes` may block forever waiting on terminal input. The only escape hatch is a global `--yes` ("Assume yes"), which also waives any confirmation `clean` or `install` might raise, so agents learn to pass blanket consent to get past one prompt.
- fix direction: when stdin is not a TTY (or in machine mode), never prompt: either proceed only if `--yes` is given and otherwise exit `2` with a structured `CONFIRMATION_REQUIRED` error naming `--yes` in `hint`. Declare this in the schema and help. Prefer per-command explicit triggers over one global `--yes`.

### F2 — `ls --json` stdout mixes banner, progress, and summary with the JSON payload
- severity: P1 (fixed placement: successful stdout mixing banners/progress/summaries with payload)
- type: impl-bug
- evidence: observed (user capture, stderr discarded)
- location: `depman ls --json 2>/dev/null` output lines 1, 2, and 4: `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `--json` output is not parseable with `json.loads`/`jq` without line-scraping; the timing line is non-deterministic so output is unstable across runs and cannot be snapshotted; the emoji and decorations cost tokens for nothing.
- fix direction: under `--json` (or a `--machine` profile, see F5), stdout is the JSON payload only. Move the banner and "Done in" to stderr in human mode and drop them entirely in machine mode. Remove the wall-clock duration from any default output, or put it in a structured `meta` field only when requested.

### F3 — Read verb `ls` performs an update check by default, under `--json`
- severity: P1 (fixed placement: hidden side effect on a read path; downgrade to P2 only with evidence the effect is confined to the local machine, which the capture does not provide)
- type: design-issue
- evidence: inferred (the line `Checking for updates...` is observed; that it makes a network call is deduced)
- location: `depman ls --json 2>/dev/null`, line 2
- impact: a listing command makes an undeclared network call, adds latency and a failure mode (offline/proxy) to a local read, and phones home on every invocation even in the closest thing the tool has to machine mode. Agents cannot predict latency class or safety of `ls`.
- fix direction: make update checks opt-in (`depman self-update --check` or a config key), suppress them whenever `--json`/machine mode is active or stdout is not a TTY, and never write them to stdout. Declare `ls` as `read_only: true`, `latency_class: local`, `side_effects: none`.

### F4 — `install` failure offers no symbolic code, a generic exit, and lands on stdout
- severity: P1 (fixed placement: errors with no symbolic code to branch on)
- type: impl-bug
- evidence: observed (user capture; stderr discarded, so the error line is on stdout; `$?` is `1`)
- location: `depman install nonexistent-pkg 2>/dev/null` → `Error: something went wrong (see log)`, exit `1`
- impact: an agent cannot distinguish "package not found" from a network failure, auth failure, or lockfile conflict; exit `1` is the generic bucket; "see log" names no path; and because the error is on stdout an agent reading stdout for payload gets prose instead. Whether `--json` changes the error shape is not-checked (no capture).
- fix direction: write errors to stderr; emit a structured object `{code, message, hint, temporary, ...}` with a stable symbolic `code` (e.g. `PACKAGE_NOT_FOUND`) and map it to a declared exit code (`3` not found per the skill convention). Put the log path in a `details.log_path` field, not prose. Make `--json` govern error rendering as well as success rendering.

### F5 — No machine schema, no declared machine profile; `--json` is undocumented and `--quiet` undefined
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists only `--quiet` and `--yes`; `--json` works for `ls` but is not in Options; no `schema`, `version`, or `--version` surface)
- location: `depman --help`, Options section
- impact: agents cannot discover `--json` from help, cannot tell whether it is global or `ls`-only, cannot tell whether `--quiet` suppresses the banner (F2) or the update check (F3), and have no stable contract to cache. Version is only available by parsing a banner.
- fix direction: add `depman schema` (full contract) and `depman schema --fingerprint` with `schema_version`, `fingerprint`, `fingerprint_scope`; add `depman version`/`--version`; declare one canonical machine profile (e.g. `--machine` implying `--json --no-progress --yes-is-explicit --no-update-check`); document every global flag with type, default, and what it suppresses. examples.md §1 shows the shape.

### F6 — No exit-code map or per-command error catalog
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (nothing in `--help`; only exit observed is `1`)
- location: `depman --help`; `depman install nonexistent-pkg` exit
- impact: agents cannot branch on exit codes or know which failures are retryable (registry timeout vs not-found vs lockfile conflict).
- fix direction: declare numeric exit codes and symbolic codes at tool level, and per command list `errors_possible` with `exit`, `retryable`, `reconcile_first`, and `suppressed_by` (e.g. `install --if-not-installed`). Observed exit `1` should become `3` for not-found.

### F7 — `ls` summary ("Show stuff") is not task-selective
- severity: P2
- type: design-issue
- evidence: observed (`--help`)
- location: `depman --help`, `ls          Show stuff`
- impact: an agent choosing between `ls`, `install`, and `sync` cannot tell what `ls` shows (installed packages? outdated? lockfile contents? cache?). The `--json` capture reveals it lists installed name/version, but help does not say so.
- fix direction: rules-then-context summaries: `ls  List installed packages (name, version); read-only; --json for machine output`. Apply the same pass to `clean` (what counts as "unused"?) and `sync` (what does sync change: lockfile from manifest, or installed tree from lockfile?).

### F8 — Mutations (`install`, `clean`, `sync`) lack dry-run, reconciliation, and local-state safety declarations
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`, Commands section
- impact: `clean` deletes from a global cache and `sync` rewrites a lockfile with no `--dry-run`, no statement of what an interrupted run leaves behind, and no concurrent-invocation guarantee. After F4's failed `install`, an agent cannot tell whether the lockfile or manifest was touched before the error.
- fix direction: add `--dry-run` to all three with `dry_run: true` in output; declare lockfile/cache writes as atomic (write-temp-rename) or locked; declare SIGINT semantics; give `install` an idempotent re-run story (`--if-not-installed` or document that re-running is safe) and a status command (`ls`) agents can use to reconcile.

### F9 — Ambient state undeclared and not disableable
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help` (mentions a "global cache" and "the lockfile" but nothing else)
- impact: agents do not know where the cache lives, which config files or env vars (registry URL, auth token, proxy) are read, their precedence, or how to run in a clean environment for reproducibility.
- fix direction: document credential, config, env, and cache sources with precedence; add `--no-config`/`--isolated`; add `depman config show --resolved` (with secrets redacted); state that secrets are accepted via env/credential file, not flags.

### F10 — No caller-settable timeout on networked commands
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`, Options section
- impact: `install` (and the update check in F3) can hang on a slow registry with no agent-controlled bound.
- fix direction: add `--timeout-ms` with a declared default and declare retry behaviour; declare `latency_class` per command.

### F11 — Aliases advertised in canonical help; abbreviated vs full-word sibling names
- severity: P3
- type: design-issue
- evidence: observed (`install ... (aliases: i, add)`; `ls` beside `install`, `clean`, `sync`)
- location: `depman --help`
- impact: `add` reads as a different operation (add to manifest) from `install`, so an agent may pick it expecting different semantics; one abbreviated sibling among full words invites `list` guesses that fail.
- fix direction: keep aliases only in the schema's `aliases` field for migration; use one canonical name in help and examples; consider `list` for consistency or declare `ls` canonical and `list` an alias.

### F12 — End-of-options and stdin contract undeclared
- severity: P3
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`
- impact: an agent installing a package whose name begins with `-` cannot know whether `--` is honoured; no command declares whether it reads stdin (e.g. a package list), so an agent cannot tell whether a stray pipe will block.
- fix direction: support and declare `--`; declare a stdin contract per command (`reads: false` for all is fine, say so).

### F13 — Help leads with a tagline instead of constraints
- severity: P3
- type: design-issue
- evidence: observed
- location: `depman --help`, line 1 (`DepMan 3.2 — the friendly dependency manager!`)
- impact: minor token cost; the first line an agent reads carries no decision-relevant content.
- fix direction: put usage and the machine-mode flag first; move the tagline to the end or drop it.

## Checklist coverage

| contract-checklist.md section | Status |
|---|---|
| Command Model | covered by F7, F11 |
| Machine Schema | covered by F5, F6 |
| Stdin Contract | covered by F12 |
| Shell Safety | covered by F12 (`--`); hint/subshell handling not-checked (no source) |
| Agent-Safe Invocation | covered by F1, F5, F10 |
| Output | covered by F2, F4; `ls --json` payload itself is OK (compact, shallow array of `{name, version}`); default sort, pagination, truncation not-checked |
| Errors And Exit Codes | covered by F4, F6 |
| Ambient State | covered by F9 |
| Mutations And Long-Running Work | covered by F8 |
| Side Effects And Telemetry | covered by F3 |
| Prose Surfaces | covered by F7, F13 |
| Tests | not-checked (no source or test suite available) |

## Open questions and assumptions

1. Does `sync` skip or fail the prompt when stdin is not a TTY? Determines whether F1 stays P0.
2. Is `Checking for updates...` a network call? Determines whether F3 stays P1 (yes) or drops to P2 (local-only check).
3. Does `--json` change the error rendering of `install`, and does `--quiet` suppress the banner, the update check, or both?
4. Does a failed `install` write to the lockfile or manifest before exiting?
5. Where is "the log" referenced in the error, and is it machine-readable?
6. Is `--json` accepted by `install`, `clean`, and `sync`, or only `ls`?

Cheapest probes to settle these, each captured with stdout and stderr separated (`>out 2>err`): `depman sync </dev/null` (with a timeout wrapper), `depman ls --json --quiet`, `depman install nonexistent-pkg --json`, `depman ls --json` while offline, and `depman install --help`.

## Suggested remediation order

1. F2 + F4 together: one `--json`/machine-mode rendering path for success (stdout, payload only) and failure (stderr, structured object with `code`). This is the smallest change that makes the tool parseable at all.
2. F1 + F3: never prompt or phone home when stdin/stdout is not a TTY or machine mode is set.
3. F5 + F6: publish `depman schema` and `schema --fingerprint` with the exit-code map and per-command error catalog; document `--json`, `--quiet`, and add `--timeout-ms` (F10).
4. F7–F9, F11–F13: prose, mutation safety, ambient state, and polish.
