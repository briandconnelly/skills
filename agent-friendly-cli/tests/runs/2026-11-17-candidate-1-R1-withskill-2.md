# Scenario R1 (hardening) — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/5 scored
- **Tokens:** 63,120 (final-turn context plus output, read from the transcript)
- **Output words:** 803
- **Transcript sha256:** `ba7bd730d076be55dc9ac6c95d004906e7b5ee5dc6c963edf91cf4e33386291f` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels
- **Checklist coverage table present:** no

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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/R1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/R1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Proposes a non-interactive, machine-readable output mode and, for each of `list`, `show`, `create`, and `delete`, names the fields or shape of its output, not only an output class (Output). Reworded 2026-11-17 to state the threshold the 2026-10-11 scoring correction applied; this resets R1's history, so rows dated before 2026-11-17 are not comparable on this assertion. | **FAIL** | Proposes `--machine` JSON mode but `show` -> `record` and `create`/`delete` -> `record describing the result` name only an output class, no fields or shape (only `list` gets 'JSON array'). Parts: non-interactive machine-readable mode = pass; fields/shape for each of list, show, create, delete = fail |
| A2 | scored | Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes). | **PASS** | Map: 0 ok, 2 usage/validation, 3 `PROFILE_NOT_FOUND`, 4 `UNAUTHENTICATED` |
| A3 | scored | Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations). | **PASS** | `envctl create <name> --from-file <path>`; delete `Add --yes` and `Add --dry-run`; login `token via ENVCTL_TOKEN env var or a credential file path` Parts: create non-interactive = pass; delete non-prompting trigger plus preview/dry-run = pass; login non-browser bootstrap = pass |
| A4 | scored | Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State). | **PASS** | `--profile-dir` (default `~/.envctl`) is a cache plus presumably credentials... add `envctl whoami` and `envctl config show --resolved`... add `--isolated` to ignore the cache Parts: names ambient state (cache, credentials) = pass; how agent inspects or disables it = pass |
| A5 | scored | Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema). | **PASS** | Add `envctl schema` (whole tree), `envctl schema <command>`, and `envctl schema --fingerprint` |

## Verbatim final output

~~~~~~markdown
# envctl: prioritized changes for agent callers

Audience: tool owner. Task: contract hardening.
Evidence: only the `--help` text you pasted (a verbatim capture), so most findings are `inferred` or `absence-of-evidence`; I did not run envctl.
Severity follows P0 (blocks release, hangs/unsafe) → P3 (polish); P0/P1 should land before agents start calling it next quarter.

## P0 — must fix before agents call it

1. **`create` prompts for values → hangs in CI.** (inferred from "prompts for values")
   Add non-interactive input: `envctl create <name> --from-file <path>` and `--from-file -` for JSON/dotenv on stdin, declared explicitly (not auto-detected from a TTY guess).
   Never prompt when stdin is not a TTY or in machine mode; fail fast with a structured `MISSING_INPUT` error (exit 2) instead.
   Accept secret values via stdin/file only, never as `--set KEY=secret` argv (leaks into process lists and agent transcripts).
2. **`delete` asks "are you sure?" → hangs in CI.** (inferred)
   Add `--yes`; without it in non-TTY/machine mode, exit 2 with `CONFIRMATION_REQUIRED` rather than waiting.
   Add `--dry-run` that returns `{"dry_run": true, "would_delete": ...}`, exiting 0 when the delete would succeed.
3. **`login` is browser-only → no CI bootstrap.** (inferred)
   Document a non-interactive bootstrap: token via `ENVCTL_TOKEN` env var or a credential file path (e.g. a service-account/OIDC token from CI), never a `--token` flag value.
   Never launch a browser when stdout/stdin isn't a TTY or in machine mode; return `UNAUTHENTICATED` (exit 4) with a hint naming the env var.
4. **`show` likely prints secret values.** (inferred; profiles are env vars)
   Redact secret values by default in `show`/`list` and in all error/debug output; reveal only with an explicit `--reveal` (or a separate `envctl profile get-value`) so agents don't paste secrets into transcripts and logs.

## P1 — agents can't reliably parse or branch without these

5. **No machine output.** (absence-of-evidence)
   Add one machine profile flag, e.g. `--machine`, implying `--format json`, no color, no progress, no prompts, no browser.
   stdout = payload only; diagnostics to stderr.
   Declare output classes: `list` → `list` (JSON array, or `has_more`/`next_cursor` if it can grow), `show` → `record`, `create`/`delete` → `record` describing the result.
   Deterministic sort (by name) and UTC timestamps.
6. **No structured errors or exit-code map.** (absence-of-evidence)
   On failure in machine mode, stderr is one JSON object `{"code", "message", "temporary", "hint", ...}` and stdout is empty.
   Map: 0 ok, 2 usage/validation, 3 `PROFILE_NOT_FOUND`, 4 `UNAUTHENTICATED`, 5 `FORBIDDEN`, 7 `TIMEOUT`, 8 `PROFILE_EXISTS`, 9 transient/transport, 1 `INTERNAL` fallback.
   Agents branch on `code`, never on `message`.
7. **Mutations aren't replay-safe.** (absence-of-evidence)
   It's a shared network service, so a timed-out `create`/`delete` has an unknown outcome.
   Add `create --if-not-exists` and `delete --if-exists` (exit 0 when already in the target state, reported in the payload), and declare which retries are safe; otherwise mark mutations `reconcile_first` and tell callers to `show` before retrying.
8. **`--verbose` must never pollute stdout.** (inferred)
   Send verbose output to stderr only, so `envctl --machine -v list` still yields clean JSON.

## P2 — contract gaps

9. **No machine-readable schema.** Add `envctl schema` (whole tree), `envctl schema <command>`, and `envctl schema --fingerprint`, declaring commands, flags/types, read-only vs mutating, output shapes, per-command error codes, auth needs, and latency class (`network` for all but `schema`). Keep `--help`/`schema` offline and fast — no auth check or network call.
10. **Ambient state is undeclared.** `--profile-dir` (default `~/.envctl`) is a cache plus presumably credentials. Document every env var/config/credential source and precedence (flags > env > config > cache); add `envctl whoami` and `envctl config show --resolved` (secrets redacted); add `--isolated` to ignore the cache. Declare whether reads warm the cache (an implicit write on a read path) and make cache writes atomic for parallel CI jobs.
11. **No caller-settable timeout.** Add `--timeout-ms` on networked commands and declare retry behavior.
12. **Shell safety.** Support `--` so a profile name starting with `-` isn't parsed as a flag, and treat names as data (never interpolated into shell).

## P3 — polish

13. **Command naming.** Fine as is for a single-resource tool; if you expect more nouns, consider `envctl profile list|show|create|delete` now, keeping current verbs as declared aliases.
14. **Help text.** Make summaries rules-first and selective: e.g. `delete <name>  Delete a profile; requires --yes in non-interactive use`, `--profile-dir  Local cache directory (default ~/.envctl; env ENVCTL_PROFILE_DIR)`.
15. **Tests.** Pin: schema snapshot, JSON payloads, error payloads + exit codes, non-TTY never prompts/opens a browser, `--dry-run`, `--if-exists`/`--if-not-exists`, secret redaction.

## Suggested order
P0 items 1–4 and P1 items 5–6 as one release (`--machine`, `--yes`, `--from-file`, token bootstrap, JSON errors) — that's the minimum for CI agents. Then 7–12, then polish.

## Assumptions / open questions
- Do profile values include secrets? (Drives item 4's urgency.)
- Is `list` bounded, or does it need pagination?
- What does `--profile-dir` hold — only cached profiles, or credentials too?
- Is there a CI-friendly auth path on the service side (service tokens/OIDC) to back item 3?
~~~~~~
