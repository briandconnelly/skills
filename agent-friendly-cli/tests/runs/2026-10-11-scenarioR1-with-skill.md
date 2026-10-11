# Scenario R1 (Hardening an internal CLI) — with-skill run

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill files as of commit c154b17)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; representative set, first run)
- **Score:** 4/5 scored (corrected after a Codex review of the scoring; see A1)
- **Subagent tokens:** 76,531 (harness-reported total for the run)
- **Transcript sha256:** `743aef1657ccbf8f352790d9bd16b792c7c3fe5e51c0ab92f3a69f80b29d082f` (session-local copy; not committed)

## Exact prompt given

> Our team owns `envctl`, an internal Go CLI that lists, shows, creates, and deletes environment-variable profiles stored in a shared service.
> Developers use it interactively today; our CI agents (Claude Code and Codex) will start calling it next quarter.
> Propose the changes that would make it safe and easy for agents to call, in priority order.
> Here is the current help:
>
> ```text
> $ envctl --help
> envctl — manage environment profiles
>
> Usage: envctl <command> [flags]
>
> Commands:
>   list              List profiles
>   show <name>       Show a profile
>   create <name>     Create a profile (prompts for values)
>   delete <name>     Delete a profile (asks "are you sure?")
>   login             Log in via browser
>
> Flags:
>   -v, --verbose     More output
>   --profile-dir     Where profiles are cached (default ~/.envctl)
> ```

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files or run git.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; nothing under `tests/`; no other file.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Proposes a non-interactive, machine-readable output mode and says what each command's output looks like in it (Output). | **FAIL** | F4 declares a `--machine` profile and an output class per command, but states fields for only `list` and `delete`; `show`, `create`, `whoami`, and `login` get the label `record` and nothing else. Scored at the same threshold as the baseline, which was failed for naming a stable JSON object per command without per-command fields. Initially scored PASS; corrected after a Codex review of the scoring. |
| A2 | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | F5: exit-code map 0–9 with symbolic codes per exit, single-error-object stderr framing. |
| A3 | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | F1 (`--from-file`/`--values-stdin`/`--set`, fail-fast `INPUT_REQUIRED`), F2 (`--yes`, `--dry-run`, `--if-exists`, `CONFIRMATION_REQUIRED`), F3 (`ENVCTL_TOKEN`, `--token-stdin`, `--no-browser` device code). |
| A4 | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | F8: cache declared in schema, `--no-cache`/`--isolated`, `config show --resolved` with redaction; F3: `whoami` for token source and expiry. |
| A5 | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | F9: `envctl schema` and `schema --fingerprint` with a compatibility promise. |

**Set:** representative; never tightened in response to its own results.
**Regression vs same-day baseline (4/5):** none; same assertion missed by both arms.
**Overhead:** 76,531 vs 41,318 subagent tokens (1.85x), and a markedly longer answer (15 findings, coverage table, three-release plan) for a prompt that asked for a prioritized list of changes.
**Notes:** no scored difference between the arms on this representative task: both miss A1 at the per-command-fields threshold, the treatment by less.
The treatment also surfaced a secret-exposure concern (`show` printing values into agent transcripts) that the baseline raised too, so that is not a skill effect.
The cost side is worth recording: the skill turned a "propose changes" request into a full audit report, which the audience step (tool author) permits but the prompt did not ask for.

## Full final output

Verbatim final message returned by the subagent:

# envctl: agent-readiness proposal (priority order)

**Framing (per agent-friendly-cli SKILL.md Workflow §1–2).** Audience: tool author (your team owns `envctl`), so this leads with contract gaps, release-blocking findings, and concrete redesign guidance. Task: contract hardening of an existing CLI you own — the skill routes that through review-workflow.md to find gaps, then design-workflow.md for the fixes. Findings come first, ordered by severity; a checklist-coverage table, open questions, and a phased plan follow.

**Evidence basis.** I did not run `envctl` (it is internal and I was told not to). Every finding is labelled per review-workflow §1: `observed` means the supplied `--help` capture states it; `inferred` means deduced from that text; `absence-of-evidence` means a required contract piece is missing from the help. Before implementing, I recommend collecting the §1 probe set (listed under "Open questions") so stream attribution and exit codes are observed rather than inferred.

---

## Findings, ordered by severity

### P0 — commands that hang in automation

**F1. `create <name>` prompts for values** — `impl-bug` · `observed` (help: "prompts for values") · location: `--help`, `create` line.
- Impact: in CI there is no TTY on stdin; the prompt either blocks forever or reads EOF and creates an empty/garbage profile. Agents cannot recover from a hang. (Fixed `P0` placement: blocking behavior in non-TTY mode — review-workflow § Severity.)
- Fix: never prompt when stdin is not a TTY or when `--machine` is set. Take values via declared channels instead: `--from-file <path>` (dotenv or JSON, declared format), `--values-stdin` (explicit flag, not auto-detected, so an accidental pipe can't be mistaken for input), and `--set KEY=VALUE` (repeatable) for non-secret values only. If no values are supplied in machine mode, fail fast with `INPUT_REQUIRED` (exit 2) rather than waiting. Because profile values are frequently secrets, canonical examples should use `--from-file`/`--values-stdin`; document that `--set` leaks into process listings, shell history, and agent transcripts (checklist § Ambient State, Secret intake).

**F2. `delete <name>` asks "are you sure?"** — `impl-bug` · `observed` (help: `asks "are you sure?"`) · location: `--help`, `delete` line.
- Impact: same hang in CI; worse, if the implementation treats EOF as "yes", an unattended delete proceeds silently — the P0 data-loss case.
- Fix: `--yes` as the explicit action trigger (checklist § Mutations). In machine/non-TTY mode without `--yes`, exit 2 with `CONFIRMATION_REQUIRED` and `hint: "add --yes"`; never read the answer from a non-TTY stdin. Add `--dry-run` (output includes `dry_run: true`, `planned_action: "delete"`, `name`) and `--if-exists` so a retried delete is idempotent.

**F3. `login` opens a browser; no non-interactive bootstrap** — `design-issue` · `observed` for the browser launch (help: "Log in via browser"), `absence-of-evidence` for any alternative.
- Impact: CI agents cannot complete the browser flow, so every authenticated command is unusable until a human intervenes. Checklist § Agent-Safe Invocation requires a documented non-interactive bootstrap for every interactive login flow; non-TTY mode must suppress browser launch.
- Fix, in order of preference: (1) accept a token from `ENVCTL_TOKEN` or a credential file path (`ENVCTL_CREDENTIALS_FILE`) with no `login` step at all; (2) `envctl login --token-stdin` for injecting a CI-minted token; (3) if a human-in-the-loop device-code flow is needed, `login --no-browser` prints the verification URL/code as a structured record and polls with a declared `--timeout`. Never accept the token as a flag/argument value by default. Add `envctl whoami` (record: identity, token source, expiry) so agents can verify auth state before mutating.

### P1 — agents cannot reliably invoke, parse, branch, or recover

**F4. No machine profile and no structured output** — `schema-gap` · `absence-of-evidence` (no `--json`, `--machine`, `--format`, `--no-color`, or `--no-input` in help).
- Impact: agents must parse human prose for `list`/`show`, which breaks on any copy change, and any banner or summary on stdout corrupts the payload (fixed P1 placement). Successful `show` output probably mixes labels and values; agents cannot tell a profile with no vars from an error.
- Fix: one canonical machine profile `--machine` that implies `--json --no-color --no-progress --no-input --no-pager --no-browser`, each implied flag still declared individually. Per-command output class (SKILL.md Vocabulary): `list` → `list` (`{items, has_more, next_cursor?, limit}`), `show` → `record`, `create` → `record`, `delete` → `record` (`{name, status: "deleted"}`), `whoami` → `record`, `login` → `record`. stdout is the payload only; everything else to stderr. Deterministic default sort for `list` (by `name`), UTC timestamps, UTF-8.

**F5. No exit-code map and no symbolic error codes** — `schema-gap` · `absence-of-evidence`.
- Impact: agents branching on "not found" vs "unauthenticated" vs "transient" have only English text (fixed P1 placement: errors with no symbolic code).
- Fix: adopt the checklist § Errors map and declare it in schema: `0` success, `1` generic, `2` usage/validation (`VALIDATION_ERROR`, `INPUT_REQUIRED`, `CONFIRMATION_REQUIRED`), `3` `PROFILE_NOT_FOUND`, `4` `UNAUTHENTICATED`, `5` `FORBIDDEN`, `6` `RATE_LIMITED` (retryable), `7` `TIMEOUT`, `8` `PROFILE_EXISTS` (conflict on `create`), `9` `TRANSIENT`. On failure in machine mode, stderr carries exactly one JSON error object (`stderr_framing: "single-error-object"`) with required `code`, `message` and recommended `hint`, `temporary`, `retry_after_ms`, `resource_id`, `field`, `request_id`; stdout is empty. `field` names a published flag (`--set`), never an internal identifier. Hints express repairs as flag values, never as shell strings built from caller input (§ Shell Safety).

**F6. Secret exposure on `show`, `create`, and `--verbose` is undeclared** — `design-issue` · `inferred` (a profile of environment variables is a secret store by nature; help says nothing about redaction).
- Impact: an agent that runs `envctl show prod` to "check what's there" copies every secret into its transcript and possibly into CI logs. `--verbose` may dump requests/responses containing the token. Checklist § Errors: secrets redacted everywhere unless returning a secret is the command's explicit purpose.
- Fix: make `show` redact values by default (`"value": null, "redacted": true`, optionally a stable `value_hash` for drift detection) and require an explicit `--reveal` to include values; declare that `--reveal` returns secrets. Redact tokens from `--verbose` output and from error `details`. Consider `envctl exec <name> -- <cmd>` later: it injects the profile into a child process so the agent never sees values — a real contract advantage over `show --reveal | export`.

**F7. Mutation outcome after timeout/interrupt is not reconcilable as declared** — `schema-gap` · `absence-of-evidence` (no `--timeout`, `--if-exists`, `--if-not-exists`, or retry guidance).
- Impact: `create` that times out mid-flight may or may not have committed; a blind retry hits a conflict or double-creates. Fixed P1 placement. Reconciliation via `show` only works if `show` reads the service rather than the local cache (see F8 — currently unknown).
- Fix: declare per-command `reconciliation` in schema ("on timeout run `envctl show <name> --no-cache`; `PROFILE_NOT_FOUND` means the create did not commit; `--if-not-exists` makes retry safe"). Add `--if-not-exists` to `create`, `--if-exists` to `delete`, a `--timeout-ms` flag with declared default, and declare signal semantics (SIGINT leaves no partial local cache write; remote request may still complete).

### P2 — important contract gaps and costly behavior

**F8. Ambient state via `~/.envctl` cache is hidden and uninspectable** — `schema-gap` · `absence-of-evidence` (help declares the cache dir but not what reads/writes it, precedence, or how to disable it).
- Impact: `list`/`show` may silently serve stale data to an agent that just created or deleted a profile from another job; parallel CI jobs sharing `$HOME` may race on cache writes. Any write on a read path is P1 by fixed placement but downgrades to P2 here because the effect is confined to the local machine — unless the cache also stores credentials, in which case see F3/F6.
- Fix: schema declares `cache: {reads, writes, path, disable_with: "--no-cache"}`, env vars read (`ENVCTL_TOKEN`, `ENVCTL_PROFILE_DIR`, …), config files read, and precedence `flags > env > config > cache`. Add `--isolated` (distinct from `--machine`), `--no-cache`/`--refresh` on reads, `envctl config show --resolved` with secret values redacted, and atomic (write-temp-then-rename) cache writes.

**F9. No `envctl schema` / fingerprint** — `schema-gap` · `absence-of-evidence`.
- Impact: agents discover the contract by scraping help each run; no cache key means re-reading it every session. (Review-workflow §2: I could not check for a substitute such as `--help --json` or generated completion metadata without running the tool — see open questions.)
- Fix: `envctl schema` (full contract per checklist § Machine Schema, JSON Schema as the `shape_dialect`), `envctl schema --fingerprint` returning `{schema_version, fingerprint, fingerprint_scope: "schema-contract"}`, and a declared compatibility promise (additive vs breaking). Metadata paths must be sub-100ms with no network or auth validation.

**F10. `list` has no pagination, filter, or size contract** — `schema-gap` · `absence-of-evidence`.
- Fix: `--limit`, `--filter <glob>`, `--select name,updated_at`, `has_more` + `next_cursor` with declared cursor opacity/lifetime/expiry code (`CURSOR_EXPIRED`, exit 2), deterministic sort, declared projection rule.

**F11. No `--` end-of-options; operands beginning with `-` are unsafe** — `schema-gap` · `absence-of-evidence`.
- Fix: support `--`, declare `end_of_options_supported: true`, quote `<name>` in canonical examples, and never pass names or values to a subshell.

**F12. Help prose does not state prerequisites or constraints** — `design-issue` · `observed` (summaries say what a command does but not that it needs auth, hits the network, or mutates).
- Fix (checklist § Prose Surfaces, rules-then-context): each summary states auth requirement, read-only vs mutating, and the non-interactive input path. E.g. `create <name>   Create a profile from --from-file or --values-stdin (auth required; mutating; no prompt in --machine mode)`. If the `separating-context-from-constraints` skill is available, run it over the final help text.

**F13. No tests pin agent-facing behavior** — `schema-gap` · `absence-of-evidence`.
- Fix: ship the checklist § Tests set, prioritizing: non-TTY/machine suppression of prompts and browser launch (F1–F3), stdout/stderr separation with streams captured separately, observed-vs-declared exit codes, `--dry-run` for `create`/`delete`, `--if-exists`/`--if-not-exists`, concurrent cache writes, and a schema snapshot.

### P3 — polish

**F14. `-v/--verbose` is undefined** — `design-issue` · `observed`. Declare what it adds and that it goes to stderr; ensure it is a no-op on stdout in machine mode; `-v` is conventionally `--version` in many CLIs, so add an explicit `envctl version`.

**F15. Command model** — `design-issue` · `observed`. The flat `envctl <verb>` tree is fine for one noun. If a second noun is coming (e.g. secrets, teams), move to `envctl profile <verb>` now and keep the bare verbs as declared, deprecated aliases. `show` is acceptable; `get` is the conventional verb (design-workflow §2) — pick one and avoid aliases in examples. Add `--timeout-ms` (unit in the name) rather than `--timeout`.

---

## Checklist coverage (contract-checklist.md sections)

| Section | Status |
|---|---|
| Command Model | F15 (minor); otherwise OK — one noun, five guessable verbs |
| Machine Schema | F9, F4, F5 |
| Stdin Contract | F1 (create input), F3 (`--token-stdin`); must be declared per command, `reads: false` for the rest |
| Shell Safety | F11, F5 (hint rule) |
| Agent-Safe Invocation | F1, F2, F3, F4 |
| Output | F4, F6, F10 |
| Errors And Exit Codes | F5, F7 |
| Ambient State | F8, F3, F6 |
| Mutations And Long-Running Work | F2, F7; long-running/job-ID items not-applicable — all operations appear to be single network round trips (assumption; the device-code login in F3 is the one polling path and declares its own `--timeout-ms`) |
| Side Effects And Telemetry | not-checked — the help text cannot show update checks, telemetry, or auto-login on expired tokens; see open questions |
| Prose Surfaces | F12 |
| Tests | F13 |

## Open questions / assumptions (and the probes that resolve them)

1. Does any command auto-launch `login` (browser) when the token is missing or expired? If yes, that is a second P0 hang on every command, not just `login`.
2. Do `list`/`show` read the service or the `~/.envctl` cache, and does `show` write the cache (implicit write on a read path)? Decides whether F7's reconciliation path is trustworthy and whether F8 stays P2.
3. What does `delete` do on EOF at the "are you sure?" prompt — abort or proceed? Determines whether F2 is a hang or a data-loss bug today.
4. Is there telemetry, an update check, or any network call on `--help`?
5. Is this a cobra CLI? If so, `__complete` metadata exists but is not a contract substitute for F9.

Suggested probe set (review-workflow §1; run with your approval, capturing stdout and stderr separately, in a sandbox account): `envctl --help </dev/null`, `envctl version`, `envctl list </dev/null`, `envctl show nonexistent </dev/null; echo $?`, `envctl create probe </dev/null` (observe hang vs exit), `envctl delete probe </dev/null` (observe EOF handling), and the same with `ENVCTL_TOKEN` set to an obviously invalid placeholder for the auth-failure case. Do not run `login` or a real `delete` unattended.

## Remediation plan (three releases)

**Release 1 — unblock CI (F1, F2, F3, F4, F5).** `--machine` profile; no prompts/browser when stdin or stdout is not a TTY; `--yes`, `--from-file`/`--values-stdin`; `ENVCTL_TOKEN` + `whoami`; JSON on stdout, single JSON error object on stderr, exit-code map. Ship the non-TTY and stdout/stderr tests with it. Agents can start calling `envctl` after this release.

**Release 2 — make mutations safe (F6, F7, F8).** `--dry-run`, `--if-exists`, `--if-not-exists`, `--timeout-ms`, declared reconciliation; `show` redacts by default with `--reveal`; `--no-cache`/`--isolated`, `config show --resolved`, atomic cache writes.

**Release 3 — publish the contract (F9–F15).** `envctl schema` + `--fingerprint` with compatibility promise; `list` pagination/filter/select; `--`; rules-then-context help text; schema snapshot tests; `version`.

### Target help after Release 1 (illustrative)

```text
envctl — manage environment profiles stored in the shared profile service

Usage: envctl [global flags] <command> [flags] [--] [args]

Commands (all except version/schema require auth: ENVCTL_TOKEN or `envctl login`):
  list                      List profiles (read-only; network). JSON: {items, has_more, next_cursor}
  show <name>               Show a profile with values redacted (read-only). --reveal includes values.
  create <name>             Create a profile from --from-file <path> or --values-stdin (mutating).
                            Never prompts in --machine or non-TTY mode; fails INPUT_REQUIRED (exit 2).
  delete <name>             Delete a profile (mutating). Requires --yes; supports --dry-run, --if-exists.
  login                     Authenticate. --token-stdin for CI; --no-browser prints a device code.
  whoami                    Show identity, token source, and expiry (read-only).
  schema [--fingerprint]    Machine-readable contract (local; no network).
  version                   Print version (local).

Global flags:
  --machine                 Machine mode: implies --json --no-color --no-progress --no-input --no-browser
  --json                    Structured output on stdout; structured errors on stderr
  --timeout-ms <int>        Network timeout (default 5000)
  --no-cache                Bypass ~/.envctl cache; --isolated also ignores config and env credentials
  --profile-dir <path>      Cache location (default ~/.envctl; env ENVCTL_PROFILE_DIR)
  -v, --verbose             Extra diagnostics on stderr (secrets redacted)

Exit codes: 0 ok · 2 usage/validation · 3 not found · 4 unauthenticated · 5 forbidden
            6 rate limited · 7 timeout · 8 conflict · 9 transient · 1 other
```

### Schema sketch for `envctl delete` (shape to mimic; full schema follows examples.md §1)

```json
{
  "canonical_invocation_path": "envctl delete <name>",
  "classification": "mutate", "read_only": false,
  "arguments": [{"name": "name", "type": "string", "cardinality": "one", "examples": ["ci-prod"]}],
  "flags": [
    {"name": "--yes", "type": "boolean", "default": false, "description": "required to perform the deletion in machine mode"},
    {"name": "--dry-run", "type": "boolean", "default": false},
    {"name": "--if-exists", "type": "boolean", "default": false},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 5000}
  ],
  "stdin_contract": {"reads": false, "auto_detected_when_piped": false, "can_block": false, "empty_stdin": "ignored"},
  "output": {"class": "record", "format": "json", "shape": {"name": "string", "status": "deleted"}},
  "alternate_outputs": {"--dry-run": {"class": "record", "shape": {"dry_run": true, "planned_action": "delete", "name": "string"}}},
  "side_effects": {"external_mutation": true, "writes": ["profile service", "~/.envctl cache entry removed"]},
  "latency_class": "network",
  "reconciliation": "on TIMEOUT or interrupt run `envctl show <name> --no-cache`; PROFILE_NOT_FOUND means the delete committed; --if-exists makes retry safe",
  "errors_possible": [
    {"code": "CONFIRMATION_REQUIRED", "exit": 2},
    {"code": "PROFILE_NOT_FOUND", "exit": 3, "suppressed_by": "--if-exists"},
    {"code": "UNAUTHENTICATED", "exit": 4}, {"code": "FORBIDDEN", "exit": 5},
    {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
    {"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}
  ]
}
```

**Caveat restated:** nothing above was executed; the three P0 findings are read directly from the help text, the P1s are inferred or follow from absent contract pieces, and the open questions (especially auto-login on expired tokens and cache-vs-service reads) could raise or lower individual severities once probed.
