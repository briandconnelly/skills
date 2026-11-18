# Scenario R1 (hardening) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 64,563 (final-turn context plus output, read from the transcript)
- **Output words:** 1,827
- **Transcript sha256:** `c4941fa776b854cb0a3f1be6f2e95263cd7daa0f9f5ccd53453e795300cb14ef` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels
- **Checklist coverage table present:** yes

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

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/R1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | show: a `record` -- class only; list/create/delete given partial shape, show has no fields Parts: machine-readable mode = pass; list shape = pass; show shape = fail; create shape = pass; delete shape = pass |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | \| 3 \| `PROFILE_NOT_FOUND` \| |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `delete` takes an explicit `--yes` ... Add `--dry-run` to both Parts: create non-interactive = pass; delete non-prompting trigger = pass; delete preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | Add `envctl config show --resolved` ... Add `--isolated` to bypass the cache and config. Parts: names ambient state = pass; inspect or disable = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | Add `envctl schema`. |

## Verbatim final output

~~~~~~markdown
# Making `envctl` agent-safe: prioritized proposal

Audience: you own the tool, so this leads with tool-side fixes and release-blocking gaps.
Evidence: only the `--help` text you pasted. I did not run `envctl`.
Every finding below is labelled `inferred` (deduced from the help text) or `absence-of-evidence` (a required contract piece the help does not show).
Severity: P0 = hangs or unsafe mutation; P1 = agents can't reliably invoke, parse, or recover; P2 = contract gaps; P3 = polish.
P0 and P1 block letting CI agents call it.

## Findings, in priority order

### F1 (P0, design-issue, inferred): `create` and `delete` block on prompts
- Location: `create <name>` "(prompts for values)", `delete <name>` (asks "are you sure?").
- Impact: under Claude Code or Codex in CI, stdin is not a TTY.
  The command either hangs until the job times out or reads EOF and does something you didn't intend.
- Fix:
  - Add one machine profile flag, `--machine`.
    It turns off prompts, color, progress, pager, and browser launch, and switches to JSON output.
    Also turn all of those off automatically whenever the relevant stream is not a TTY (stdin decides prompts; stdout decides rendering; stderr decides color and progress).
  - `delete` takes an explicit `--yes`.
    In machine or non-TTY mode, if `--yes` is missing, fail right away with `CONFIRMATION_REQUIRED` (exit 2). Never prompt.
  - `create` takes its values without prompting: repeatable `--set KEY=VALUE` for values that aren't secret, and `--from-file <path>` or `--stdin` (a JSON or dotenv object) for bulk values and secrets.
    In machine mode, missing values are a usage error. Never prompt for them.

### F2 (P0, design-issue, inferred): login only works through a browser
- Location: `login` "Log in via browser".
- Impact: a CI agent can't finish a browser flow.
  If any command falls back to `login` when auth fails, it hangs or tries to open a browser on a headless runner.
- Fix: document a non-interactive bootstrap that reads a service token from `ENVCTL_TOKEN` or a credential file (`--credentials-file`).
  Never take the token as a flag value, because command arguments leak into process listings and agent transcripts.
  In machine mode, an auth failure exits 4 with `UNAUTHENTICATED` and must never launch a browser.
  Add `envctl auth status` / `whoami` so an agent can check its identity before it mutates anything.

### F3 (P1, schema-gap, absence-of-evidence): no structured output and no output contract
- Impact: agents end up parsing prose from `list` and `show`.
  `-v` hints at mixed human output, but nothing says what goes to stdout and what goes to stderr.
- Fix:
  - Add `--format json|text` (implied by `--machine`).
  - stdout carries only the success payload: no banners, and no "Fetched 12 profiles" lines.
  - Each command declares an output class:
    - `list`: a `list` with a deterministic sort (by name), plus `--limit` and `has_more`/`next_cursor` pagination once the number of profiles can grow
    - `show`: a `record`
    - `create` and `delete`: a `record` or `scalar` with the profile's name and id
  - Timestamps are in UTC, and all text is UTF-8.

### F4 (P1, schema-gap, absence-of-evidence): no symbolic errors or exit-code map
- Impact: agents can't tell "profile not found" from "not logged in", "permission denied", or "network blip", so they can't decide whether to retry, stop, or ask a human.
- Fix:
  - In machine mode, a failure writes exactly one JSON object to stderr (declare the framing as `single-error-object`) with `code`, `message`, `temporary`, and optional `hint`, `field`, `resource_id`, `retry_after_ms`, and `request_id`.
  - Exit codes:

    | Exit | Meaning |
    |---|---|
    | 0 | ok |
    | 1 | generic |
    | 2 | usage or validation, including `CONFIRMATION_REQUIRED` |
    | 3 | `PROFILE_NOT_FOUND` |
    | 4 | `UNAUTHENTICATED` |
    | 5 | `FORBIDDEN` |
    | 6 | `RATE_LIMITED` (with `retry_after_ms`) |
    | 7 | `TIMEOUT` |
    | 8 | `PROFILE_EXISTS` / conflict |
    | 9 | transient |

  - Each command gets an error catalog listing which codes it can return, and `retryable` / `reconcile_first` for each.

### F5 (P1, design-issue, inferred): `create` and `delete` can't be safely replayed or reconciled
- Impact: if an agent's `create` times out against the shared service, the agent can't tell whether the profile now exists.
  Retrying gives a conflict or a duplicate.
  Retrying `delete` after a lost response gives a confusing not-found.
- Fix:
  - Add `create --if-not-exists` and `delete --if-exists`, which return success with `"changed": false`.
  - Declare the reconciliation path: after a `TIMEOUT` on a mutation, run `show <name>` before retrying.
  - Mark `create` and `delete` as `reconcile_first: true` in the catalog unless the matching `--if-*` flag is present.
  - Add `--dry-run` to both: it validates and resolves the target, exits 0, and outputs `"dry_run": true` along with the planned effect.

### F6 (P1, design-issue, inferred): secrets are likely to leak through output
- Location: `show` prints profile values, and `create` takes values.
- Impact: environment profiles almost certainly contain credentials.
  Printing them into agent transcripts and CI logs is a leak.
- Fix:
  - Redact secret values by default in `show` and `list`.
    Add an explicit `show <name> --reveal` (or `get-value <name> <key>`) when a caller really needs the secret, and mark it in the schema as returning secrets.
  - Accept secret values only through stdin or a file, not `--set` on the command line, and say so in the canonical examples.
  - Redact `--verbose`/debug output too.

### F7 (P1, schema-gap, absence-of-evidence): no machine-readable schema
- Impact: agents work out the contract from prose `--help` and break silently when it changes.
- Fix:
  - Add `envctl schema`. It declares:
    - the command tree, arguments, flags, types, and defaults
    - the machine profile
    - the stdin contract for each command
    - whether each command is read-only or mutating
    - auth requirements
    - output class and shape, as JSON Schema
    - the error catalog
    - side effects
    - latency class (`network` for everything that talks to the service; `local` for `schema` and `--help`)
    - timeout and retry defaults
    - `schema_version` with its compatibility promise
  - Add `envctl schema --fingerprint`, which returns a hash with `fingerprint_scope: schema-contract`.
  - Optionally add `envctl schema <command>` so an agent can load one command's contract without the whole document.
  - Metadata paths (`--help`, `schema`) must not touch the network or check auth, and should answer in under 100ms.

### F8 (P2, schema-gap, absence-of-evidence): ambient state isn't documented or inspectable
- Location: `--profile-dir` (default `~/.envctl`) is a cache. Credential storage after `login` isn't described.
- Impact: two CI jobs on one runner, or a stale cache, can give different answers, and the agent can't see why.
- Fix:
  - Document where credentials come from, which config, environment variables, and caches are read, and the precedence: flags > env > config > cache.
  - Add `envctl config show --resolved`, with secrets redacted.
  - Add `--isolated` to bypass the cache and config.
  - Write the cache atomically so concurrent jobs can't corrupt it.
  - Rename `--profile-dir` to `--cache-dir`, because "profile" already means the resource.
  - Say whether `list` and `show` are served from the cache, which also sets their latency class.

### F9 (P2, design-issue, absence-of-evidence): no timeout or retry control
- Impact: a hung shared service stalls CI with no way to bound it.
- Fix: add a global `--timeout-ms` with a declared default, and declare how many automatic retries happen (none on mutations).

### F10 (P2, design-issue, inferred): no shell-safety guarantees for names
- Impact: profile names come from agents.
  A name that starts with `-` is parsed as a flag.
- Fix: support `--` end-of-options and declare it in the schema.
  Validate names against a declared pattern and return `INVALID_NAME` (exit 2, `field: "name"`).
  Never pass names into a shell.

### F11 (P3, design-issue): command model and prose
- Rename `show` to `get`, and keep `show` as a declared, deprecated alias.
  Optionally move to `envctl profile list|get|create|delete` for room to grow, with the current forms kept as aliases.
- Add `update` (or `set`/`unset` for keys) so agents don't delete and recreate profiles.
  Delete-then-create isn't atomic.
- Write the help text with the rules first, for example: "`delete <name>` — permanently deletes a shared profile. Requires `--yes` in non-interactive use. Exit 3 if absent unless `--if-exists`."
- Replace `-v` with stderr-only diagnostics that are never printed to stdout.
- Make sure there's no update check or telemetry by default.

### F12 (P2, schema-gap, absence-of-evidence): no contract tests
- Fix: add tests that pin:
  - the schema snapshot
  - JSON success and error payloads
  - that each declared exit code is the one actually observed
  - non-TTY behavior: no prompts or browser, and `CONFIRMATION_REQUIRED` without `--yes`
  - stdin handling, including empty stdin
  - dry-run output
  - that secrets are redacted
  - `--isolated`
  - concurrent cache writes
  - what an interrupted `create` leaves behind

## Suggested rollout

1. **Before agents get access (release-blocking, F1–F7):**
   - `--machine` and non-TTY detection
   - `--yes`, plus `create` taking `--set`, `--from-file`, and `--stdin`
   - token bootstrap through the environment or a file, and `whoami`
   - JSON output and structured errors with the exit map
   - `--if-exists` / `--if-not-exists` / `--dry-run`
   - secret redaction
   - `envctl schema` and its fingerprint
2. **Next:** ambient-state docs and inspection, `--isolated`, `--timeout-ms`, `--`, and name validation (F8–F10).
3. **Then:** `get`/`update` verbs, rewritten help text, and contract tests in CI (F11–F12), though start the tests alongside step 1.

Example canonical agent call:

```sh
ENVCTL_TOKEN=... envctl --machine delete --if-exists --yes -- "ci-preview-123"
```

## Checklist coverage

| Section | Covered by |
|---|---|
| Command Model | F11 |
| Machine Schema | F7 |
| Stdin Contract | F1, F7 |
| Shell Safety | F10 |
| Agent-Safe Invocation | F1, F2, F7 |
| Output | F3 |
| Errors And Exit Codes | F4 |
| Ambient State | F2, F8 |
| Mutations And Long-Running Work | F5. Long-running jobs don't apply, because none of the operations look asynchronous. |
| Side Effects And Telemetry | F8 (cache writes on reads), F11 (update checks), but not checked: nothing shows whether reads write to the cache or whether there is telemetry |
| Prose Surfaces | F11 |
| Tests | F12 |

## Open questions

- Do `list` and `show` read from `~/.envctl` or from the service? This decides the latency class and whether reads have a hidden write.
- What happens today when stdin isn't a TTY: hang, EOF abort, or default "yes"? If it defaults to "yes", F1 is a data-loss bug, not only a hang.
- Which profile values are secrets? Is there a per-key secret flag in the service?
- Does the service support idempotency keys or conditional deletes? If not, `--if-*` has to be done by checking first, which can race.
- With your permission I can run these safe probes to turn the inferences into observations:
  - `envctl --help`
  - `envctl list` with stdout and stderr captured separately
  - `envctl show does-not-exist`
  - `envctl delete x < /dev/null` against a throwaway name
~~~~~~
