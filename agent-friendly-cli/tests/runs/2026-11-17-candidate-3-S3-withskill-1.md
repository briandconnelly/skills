# Scenario 3 (diagnosis) — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 5/6 scored; 0/1 conformance
- **Tokens:** 57,786 (final-turn context plus output, read from the transcript)
- **Output words:** 764
- **Transcript sha256:** `6fe60626185e33b9cd1f09c838080321654cfa20ecd62f2ce9ba005b93d7b94c` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S3-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | Most likely mechanism (evidence: **inferred**, from the `--help` text you quoted, not from a run) Parts: prompt blocking stdin in non-TTY as likely path = pass; distinguishes help text from deduction = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | Pass the confirmation explicitly: `depman sync --yes --quiet`. ... the smallest fix. |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Tool-side fixes to escalate to the depman owners Parts: separates operator vs owner = pass; owner fixes framed as escalation = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **FAIL** | Notes bypass ("`--yes` approves whatever sync was going to do") but never states what the confirmation protects. Parts: notes bypass = pass; states what it protected = fail |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | Probes to confirm (need your OK to run them) |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | Findings table F1-F5 for escalation, not a checklist coverage table: "\| F1 \| P0 \| design-issue \|" |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Mechanism labeled inferred, but the documented prompt is never labeled `observed`. Parts: prompt labeled observed = fail; mechanism labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI: diagnosis

## What's going on

Most likely mechanism (evidence: **inferred**, from the `--help` text you quoted, not from a run): `depman sync` shows a confirmation prompt before it touches the lockfile.
`--quiet` only controls how much it prints. It does not answer the prompt.
In CI, stdin is not a terminal, so nobody can answer.
Either depman blocks reading stdin that never closes, or it waits on a TTY or a timeout that never comes.
The job then sits idle until your 60-minute timeout kills it.
The help text supports this: `sync` is documented as "asks for confirmation first", and `--yes` ("Assume yes") is the documented way to skip the prompt.

## What to do now (pipeline side)

1. **Pass the confirmation explicitly:** `depman sync --yes --quiet`.
   This is the documented non-interactive path and the smallest fix.
   Note that `--yes` approves whatever sync was going to do. Make sure that is acceptable for unattended runs, because it is the same as a human clicking "yes" every time.
2. **Make stdin non-blocking as a backstop:** run it as `depman sync --yes --quiet < /dev/null`.
   If any other prompt exists that `--yes` does not cover, it gets EOF and should fail instead of hanging.
   (Whether depman treats EOF as "no", as an error, or retries is unknown. Check the exit code.)
3. **Put a tight timeout on just this step**, for example `timeout 10m depman sync --yes --quiet < /dev/null`, sized to the normal sync duration.
   A hang then costs minutes instead of an hour, and `timeout` exits `124`, so you can tell a hang apart from a depman error.
4. **Don't use `--quiet` while debugging.**
   It may be hiding the prompt text itself, which is why the log shows nothing.
   Drop it for one run, or capture stderr, to see the prompt.
5. Optionally, pin the depman version in the pipeline, so a future release that adds a new prompt can't silently bring the hang back.

## Probes to confirm (need your OK to run them)

These are cheap and safe, but I haven't run anything:

- `depman sync --quiet < /dev/null; echo "exit=$?"` in a scratch checkout, run under `timeout 60`.
  If it hangs or exits non-zero with a confirmation message, the hypothesis is confirmed.
- `depman sync --help` (not just top-level help), to see whether there's a `--dry-run`, a `--non-interactive`, or an environment variable such as `DEPMAN_YES`/`CI` detection, and whether `--yes` covers every prompt.

## Tool-side fixes to escalate to the depman owners

You can't change depman, but these are worth filing. Ordered by severity:

| # | Sev | Type | Evidence | Issue | Fix direction |
|---|-----|------|----------|-------|---------------|
| F1 | P0 | design-issue | inferred | It prompts with no TTY: a confirmation prompt blocks when stdin is not a terminal, which hangs automation. | When stdin isn't a TTY, never prompt. Fail fast with a distinct exit code (usage/validation, e.g. `2`) and an error that says "confirmation required; pass `--yes`". |
| F2 | P1 | schema-gap | absence-of-evidence | There's no declared non-interactive or machine mode, so callers can't tell which flags guarantee no prompts. | Add a machine profile (e.g. `--machine` / `--non-interactive`) that implies no prompts. Document that `--yes` covers *all* prompts in `sync`. |
| F3 | P2 | design-issue | inferred | `--quiet` can be read as "unattended", but it only reduces output. It may also suppress the prompt text, making the hang invisible. | Never suppress a prompt or a blocking reason. If it would block, write the reason to stderr. |
| F4 | P2 | schema-gap | absence-of-evidence | There's no caller-settable timeout and no declared exit codes for "confirmation required". | Add `--timeout-ms` for networked work, and add a symbolic error code and exit code for confirmation-required. |
| F5 | P3 | design-issue | inferred | The help summary puts the binding constraint in parentheses after the description. | Use rules-first wording, e.g. `sync  Requires --yes when non-interactive. Sync the lockfile.` |

## Assumptions / open questions

- I assumed the CI job runs with no TTY on stdin, which is the default for most CI runners.
  If your runner allocates a pseudo-TTY, the prompt waits forever for a keypress, and the same fix applies.
- I assumed the hang happens at the prompt, not at a network or lock wait.
  If `--yes` doesn't fix it, the next suspects are a lockfile lock held by a concurrent job, or a network call with no timeout. The step-level `timeout` from step 3 contains both.
~~~~~~
