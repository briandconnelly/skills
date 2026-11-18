# Scenario 3 (diagnosis) — with-skill arm 1 (candidate-3b wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` skill files (branch at `fca4a7f`); a second batch of three arms on the same wording, run to gauge variance
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 6/6 scored; 0/1 conformance
- **Tokens:** 56,463 (final-turn context plus output, read from the transcript)
- **Output words:** 635
- **Transcript sha256:** `1dec255e508e54479f4c0699e5ca23b9a0639070f7a19321d9ea6ab28342d919` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/prompts/S3.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave5/out/S3-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | **Most likely mechanism (evidence: `inferred`, from the user-supplied `--help` text, not run):** `depman sync` waits for a confirmation prompt Parts: prompt blocking stdin in non-TTY job as likely cause = pass; distinguishes help text shown vs deduced hang = pass |
| A2 | scored | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | 1. **Run `depman sync --yes --quiet`.** |
| A3 | scored | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | ## What to ask the depman owners for (tool side) Parts: separates operator vs owner fixes = pass; owner fixes framed as escalation to owning team = pass |
| A4 | scored | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | `--yes` means you are pre-approving whatever sync would have asked about, in every run. Before relying on it, make sure you're comfortable with sync rewriting the lockfile unattended. Parts: notes --yes bypasses safety check = pass; states what confirmation protected = pass |
| A5 | scored | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | ## Confirming it (optional, needs your OK) ... You can run one safe probe in a scratch checkout Parts: one or two safe probes offered = pass; permission requested first = pass |
| A6 | scored | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | Only a 3-row owner-findings table, not a full audit checklist coverage table. |
| C1 | conformance | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | **FAIL** | Mechanism labeled `inferred`; the word `observed` never appears for the documented prompt. Parts: prompt labeled observed = fail; hang labeled inferred = pass |

## Verbatim final output

~~~~~~markdown
# depman sync hang in CI — diagnosis

## What's going on

**Most likely mechanism (evidence: `inferred`, from the user-supplied `--help` text, not run):** `depman sync` waits for a confirmation prompt, and nothing in a CI job answers it.
The help line says sync "asks for confirmation first", and `--yes` ("Assume yes") is the only documented way to skip it.
`--quiet` almost certainly just reduces output; it does not answer the prompt.
It may even hide the prompt text, which would explain why the log shows nothing before the timeout.
Instead of seeing that stdin is not a terminal and failing fast, depman blocks reading stdin, which CI typically leaves open or attached to nothing, until the 60-minute kill.

I haven't run depman.
If you want confirmation before changing the pipeline, see "Confirming it" below.

## What to do now (pipeline side, you control this)

1. **Run `depman sync --yes --quiet`.**
   This is the documented non-interactive path and should fix the hang.
   Be aware that `--yes` means you are pre-approving whatever sync would have asked about, in every run.
   Before relying on it, make sure you're comfortable with sync rewriting the lockfile unattended.
   If you're not, check whether depman has a `--dry-run`/check mode and gate on that first.
2. **Close stdin:** `depman sync --yes --quiet < /dev/null`.
   If a different prompt shows up later (for example a new version adds one, or `--yes` doesn't cover every prompt), the read hits EOF immediately instead of blocking.
   You still need to check that depman treats EOF as "no" or an error and doesn't spin.
3. **Put a short timeout on the step**, for example `timeout 10m depman sync ...` or a per-step `timeout-minutes`, sized to how long a normal sync takes.
   That way any future hang fails in minutes, not after the 60-minute job limit.
4. **Optional:** pin the depman version in CI so an upgrade can't quietly change what the prompt asks or what `--yes` covers.

## What to ask the depman owners for (tool side)

| Issue | Severity | Type | Fix direction |
|---|---|---|---|
| `sync` blocks on a confirmation prompt when stdin is not a TTY | P0 (a command that hangs in automation) | design-issue | When stdin is not a TTY and `--yes` isn't passed, fail immediately with a non-zero exit, a symbolic error code (e.g. `CONFIRMATION_REQUIRED`), and a message naming `--yes`. Never wait on stdin. |
| `--quiet` doesn't imply non-interactive, and there's no single machine-mode flag | P2 | schema-gap | Document which flags make sync non-interactive. Ideally add a machine profile (e.g. `--machine` / `--non-interactive`) that implies no prompts. |
| Help doesn't say what the confirmation guards or what `--yes` approves | P3 | schema-gap | State what sync mutates, and whether `--yes` covers every prompt. |

Ask them to add a test that runs `sync` with stdin closed or not a TTY and checks that it exits quickly instead of hanging.

## Confirming it (optional, needs your OK)

You can run one safe probe in a scratch checkout or a throwaway CI job, so the real lockfile isn't touched:

- `timeout 30 depman sync --quiet < /dev/null; echo "exit=$?"`. Exit 124 means it hung (prompt confirmed). An immediate EOF error also confirms the prompt.

Also check the old job log for a partial prompt line such as `Proceed? [y/N]`.
Run the probe only in a scratch environment, because if it doesn't hang it may actually sync.

## Assumptions

- The hang is the prompt and not something else, such as a network or lock wait.
  The probe above tells these apart: a network hang will still hang with `--yes`.
- You're OK with sync mutating the lockfile in CI. If not, `--yes` is the wrong fix and you need a check-only mode from the owners.
~~~~~~
