# Scenario 3 (Diagnosis) — with-skill run

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill files as of commit c154b17)
- **Mode:** with-skill (fresh general-purpose subagent, skill files read live from this tree; challenge set)
- **Score:** 6/6 scored; 1/1 non-scored conformance
- **Subagent tokens:** 69,790 (harness-reported total for the run)
- **Transcript sha256:** `f2c6b7692e90826c8d04d23058e0b2a74bed24656e2552e6f0655a6807d1caf4` (session-local copy; not committed)

## Exact prompt given

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

With-skill wrapper: read `SKILL.md` and every file under `references/` in full and follow them; do not read `tests/` or any other repository file; do not modify files, run git, or run the tool.
Tool audit: Read `SKILL.md`; `ls` + `cat` of the four reference files; nothing under `tests/`; no other file.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| S1 | Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1). | **PASS** | "the prompt's read on stdin blocks forever"; `observed` for the help text and the user's report, `inferred` for the mechanism, `absence-of-evidence` for undocumented non-TTY behavior. |
| S2 | Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator). | **PASS** | "What to do now (caller-side ...)" opens with `--yes --quiet`, then `</dev/null`, then `timeout 10m` with the exit-124 note. |
| S3 | Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team. | **PASS** | Separate "What to escalate to the depman owners (tool-side fixes)" section: "They are the owner's to make; your mitigation above does not depend on them." |
| S4 | Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting. | **PASS** | Item 4: "`sync` mutates the lockfile; the prompt existed to guard that", with the `--check`/`--frozen` alternative and a `git diff --exit-code` guard. |
| S5 | Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1). | **PASS** | Two probes in a throwaway checkout, "I have not run them and will not without your go-ahead", stdout and stderr captured separately. |
| S6 | Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria). | **PASS** | "Diagnosis stops here per the skill's workflow; a full checklist audit of `depman` is not needed". |
| C1 | The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words. | met | Literal labels used. |

**Set:** challenge.
**Regression vs 2026-07-05 baseline (2/6):** none.
**Overhead:** 69,790 subagent tokens; no ratio, because no same-day scenario 3 baseline was run (the prompt is unchanged since 2026-07-05, whose baseline row stands, but its token count was not recorded).
**Notes:** the new `observed` definition (user-supplied verbatim capture) was applied exactly as written; the run also cited the Severity fixed placement for blocking behavior.

## Full final output

Verbatim final message returned by the subagent:

## What's going on

`depman sync` asks for confirmation before it mutates the lockfile, and `--quiet` does not turn that off. In your CI job there is no terminal to answer, so the prompt's read on stdin blocks forever (CI runners typically hand the process an open pipe or an empty pseudo-terminal, neither of which delivers EOF), and the job sits there until the 60-minute timeout kills it. `--quiet` almost certainly also hid the prompt text, which is why the log looks like a silent hang rather than a question nobody answered.

Evidence labels (per the skill's review workflow):

- `observed` (your verbatim `--help` capture): `sync` is documented as "asks for confirmation first", and a `--yes  Assume yes` option exists.
- `observed` (your report): the non-interactive job hangs to the timeout.
- `inferred`: the hang is the confirmation prompt waiting on terminal input. This is the textbook case the skill names for the `inferred` label ("a non-TTY hang inferred from documented prompting"). It is the most likely mechanism; it is not yet confirmed by a capture of the prompt itself.
- `absence-of-evidence`: nothing in the help text says `--quiet` implies non-interactive, that `sync` detects a non-TTY stdin, or that a `--non-interactive`/`--machine`/`--dry-run` flag exists.

Severity on the skill's scale: `P0` (fixed placement, "blocking behavior in machine or non-TTY mode", type `design-issue`), because automation cannot recover from a prompt.

## What to do now (caller-side, pipeline you control)

Smallest change first, then two cheap defenses so the next prompt-shaped bug fails fast instead of eating an hour:

1. Pass the documented action trigger:
   `depman sync --yes --quiet`
   This is the mutation trigger the tool wants (`--yes`), which is the correct fix rather than a workaround. Confirm in `depman sync --help` that `--yes` is accepted on `sync` (the top-level help lists it, but not whether it is global or per-subcommand) and place it accordingly.

2. Close stdin so any remaining prompt gets EOF instead of blocking:
   `depman sync --yes --quiet </dev/null`
   With stdin at EOF, a prompt read returns immediately; the tool then either aborts with an error (good, you see it) or treats it as "no" (also visible, exits nonzero). Either beats a hang.

3. Bound the step independently of the job timeout, and keep stderr:
   `timeout 10m depman sync --yes --quiet </dev/null`
   `timeout` exits 124 on expiry, which distinguishes "hung again" from "sync failed" in the log. Do not redirect stderr to `/dev/null`; if the prompt or an error is printed anywhere, it will be there.

4. Do not pass `--yes` blindly without deciding what you are consenting to. `sync` mutates the lockfile; the prompt existed to guard that. If your CI intent is "verify the lockfile is up to date" rather than "rewrite it", check `depman sync --help` for a `--dry-run`, `--check`, `--frozen`, or `--locked` style option and prefer that in CI. If no such mode exists, that is one of the gaps to escalate (below). Also decide whether a changed lockfile should fail the job (e.g. `git diff --exit-code` on the lockfile after sync).

## Optional confirming probes (run only if you want the mechanism confirmed before changing the pipeline)

Both are safe to run in a throwaway checkout; I have not run them and will not without your go-ahead. Capture stdout and stderr separately so stream attribution is observed, not guessed:

- Reproduce the hang with a short bound:
  `timeout 30 depman sync --quiet </dev/null >out.txt 2>err.txt; echo exit=$?`
  Expected if the hypothesis holds: either a prompt string in `err.txt`/`out.txt` and a nonzero exit (EOF treated as no), or exit 124 if it blocks even on EOF. Also run once without `</dev/null` but with `timeout 30` to match CI's open-stdin condition; exit 124 there is the hang.
- Confirm the fix:
  `timeout 30 depman sync --yes --quiet </dev/null >out.txt 2>err.txt; echo exit=$?`
  Expected: exit 0, no prompt text, lockfile synced.

If the first probe shows the hang persists even with `--yes`, the prompt is something else (credentials, first-run setup, update check), and `depman sync --help` plus a run without `--quiet` is the next step to see what it is asking.

## What to escalate to the depman owners (tool-side fixes)

These are from the skill's contract checklist (§ Agent-Safe Invocation, § Prose Surfaces, § Mutations And Long-Running Work, § Tests). They are the owner's to make; your mitigation above does not depend on them.

- Never block on a prompt when stdin is not a TTY. Evaluate TTY status per stream (stdin controls prompts) and, when confirmation is required but stdin is non-interactive and `--yes` is absent, fail fast with a structured error on stderr, a stable symbolic code (e.g. `CONFIRMATION_REQUIRED`), a `hint` naming `--yes`, and a usage exit code (2). A 60-minute hang is the worst possible contract for automation.
- Provide one canonical machine profile (`--machine` or `--non-interactive`) that implies no prompts, no color, no progress, structured output. `--quiet` is an output-volume flag, not a non-interactive flag, and the two should not be conflated; today the only way to discover the distinction is to hang.
- `--quiet` must not hide the fact that the tool is waiting on input. Prompts and failures belong on stderr and must survive `--quiet`.
- Fix the `sync` help summary rules-then-context so the binding constraint is discoverable without a failed run, e.g. "Sync the lockfile. Prompts for confirmation unless `--yes`; with non-TTY stdin and no `--yes`, exits 2 with CONFIRMATION_REQUIRED." The current "asks for confirmation first" reads as background, not as a constraint with a bypass.
- Add `--dry-run` (or a check/frozen mode) for `sync` so CI can verify without mutating, and document what a `sync` interrupted by a job timeout leaves behind (is the lockfile write atomic?). Killing the job at 60 minutes mid-write is a reconciliation question you currently cannot answer from the help text.
- Ship tests for TTY vs non-TTY behaviour and for machine-mode suppression of prompts, so this cannot regress.

Diagnosis stops here per the skill's workflow; a full checklist audit of `depman` is not needed to unblock your pipeline, but I can do one if the owners want a complete report.
