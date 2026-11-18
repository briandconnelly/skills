# Scenario 3 (diagnosis) — baseline arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/6 scored; 0/1 conformance
- **Tokens:** 48,828 (final-turn context plus output, read from the transcript)
- **Output words:** 349
- **Transcript sha256:** `a01aeffae1954e14a74ee7bbd626726b6b795fb719f81b513fce19a36da3c2c1` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | This is very likely the cause, but it is still an inference. Parts: prompt blocking stdin in non-TTY most likely = pass; distinguishes shown vs deduced = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | **Pass `--yes`** in the pipeline: `depman sync --quiet --yes`. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## Worth raising with the depman owners Parts: separates operator vs owner = pass; owner fixes as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | Only warns about `yes \|`; never says --yes bypasses the safety check or what the confirmation protected. Parts: --yes bypasses safety check = fail; states what confirmation protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **FAIL** | Offers probes ('You can confirm it in a minute or two') without asking permission first. |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | No coverage table; short diagnosis. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Says 'inference' but no `observed`/`inferred` labels. Parts: prompt labeled observed = fail; hang labeled inferred = fail |

## Verbatim final output

~~~~~~markdown
# depman sync hanging in CI

## What's going on

`depman sync` asks for confirmation before it does anything.
`--quiet` most likely only turns down output, so it does not answer the prompt.
In CI there is no TTY and no one to type "y".
depman is waiting on stdin, and it either never sees EOF or ignores EOF.
`--quiet` probably makes this worse because it may hide the prompt text, so the log shows nothing.

This is very likely the cause, but it is still an inference.
You can confirm it in a minute or two:

- Run it locally with stdin closed and a short timeout: `timeout 30 depman sync --quiet < /dev/null; echo "exit=$?"`.
  If it exits with 124 (killed by timeout), it is blocking on input.
- Run it without `--quiet` in a terminal and look for the confirmation prompt.

## What to do

1. **Pass `--yes`** in the pipeline: `depman sync --quiet --yes`.
   This is the option depman provides for exactly this case.
   Check that `--yes` really skips the `sync` confirmation (e.g. `timeout 30 depman sync --yes < /dev/null` finishes without waiting).
2. **Close stdin** so any prompt you didn't expect fails fast instead of hanging: `depman sync --quiet --yes < /dev/null`.
3. **Add a step timeout** well under 60 minutes, sized to a normal sync time plus some headroom (e.g. `timeout 10m ...` or the CI system's per-step timeout).
   Then a future hang costs minutes, not an hour of runner time.

Avoid `yes | depman sync`.
It may work, but it also answers "yes" to any other prompt depman adds later, which might be a destructive one you'd want to see.
`--yes` is the supported, explicit way.

## Worth raising with the depman owners

You can't change depman, but a short issue would help other teams:

- In a non-interactive run (no TTY, or stdin at EOF), `sync` should fail with a clear error and a non-zero exit, not wait forever.
- The `--help` text, or the error, should mention `--yes` for automation.
- `--quiet` should not hide a prompt that is blocking.
~~~~~~
