# Test Scenarios for agent-friendly-cli

Behavioral test scenarios for this skill, following the baseline/with-skill methodology: run each scenario with a fresh subagent that does NOT have the skill loaded (baseline), then with the skill loaded (treatment), and compare against the assertions.
An assertion the with-skill run misses is a finding against the skill, not against the agent.

## Scenario sets

Every scenario belongs to exactly one set, and the set decides what a baseline pass means.
Never pool the two sets into one score.

- **Representative set** — ordinary in-scope work, whose job is to estimate what the skill does on tasks nobody tuned against it.
  A scenario here is never tightened in response to its own results.
  A baseline that satisfies every assertion is a result to record, not a scenario to fix.
  Editing a representative scenario resets its history; say so in the Results table when you do.
- **Challenge set** — scenarios built to be hard enough to separate the arms and show whether a specific rule lands.
  Here a baseline that passes everything does mean the scenario is too easy; tighten it.
  Because this set selects for baseline failure by construction, its totals measure whether rules land, never the skill's net benefit.

Scenarios 1–3 are **challenge set**.
Scenario R1 is **representative**.

## Scoring dimensions

Each assertion is one of two kinds; scenarios label which.

- **Scored.** Substantive outcomes: a defect detected, a contract element present, a mitigation led with, a severity ranking defensible on the evidence.
  These are what a run passes or fails on.
- **Non-scored conformance.** House vocabulary and layout: the `P0`–`P3` words, the finding template's field names, the coverage-table shape.
  A baseline cannot pass these without the skill, so they are recorded for consistency and never counted in the score.

Every run records its set, any **regression** (an assertion the baseline satisfied and the treatment missed), and the treatment's token cost as a ratio to the baseline's when both are known.

## How to run

1. **Baseline:** dispatch a subagent with only the scenario prompt below, told that the prompt is its only input and that it must not read any repository file.
   Record which assertions its output satisfies.
2. **Treatment:** dispatch a fresh subagent with the skill content available (or triggered via its description) and the same prompt, told not to read `tests/`.
3. **Score:** every scored assertion is pass/fail with a one-line evidence pointer into the transcript; quote the assertion text verbatim when scoring, never a paraphrase.
   Record results in the table at the bottom and archive each run under `tests/runs/<date>-<scenario>-<arm>.md` with the exact prompt, the per-assertion table, and the verbatim final output.
   Assertion lists in the challenge set may be tightened over time; a results row reflects the assertions as of its date.

## Scenario 1: Design (application test, challenge set)

**Prompt:**

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

**Assertions (with-skill run must satisfy; all scored):**

- [ ] A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema).
- [ ] The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes).
- [ ] stdout is success payload only; structured failures go to stderr with declared framing (Output).
- [ ] `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work).
- [ ] List/search output declares pagination with `has_more` and a navigation token (Output).
- [ ] Export is the only `--output <file>` command and returns path, byte size, and content hash (Output).
- [ ] Duration flags declare units in the name or a `unit` field (Machine Schema).
- [ ] Each command declares one output class; any flag that switches the class declares the switch (Output).
- [ ] Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State).
- [ ] Every canonical example that uses `--` places all options before it and only operands after it (Shell Safety). Added 2026-10-11 after a with-skill run shipped `-- "query" --machine`; every scenario 1 row except `runs/2026-10-11-scenario1-with-skill-final.md` (10/10) was scored on the nine assertions above.

**Expected baseline failures:** no machine profile or schema fingerprint, prose-only errors, no exit-code map, no stdin/ambient-state declarations, dry-run absent or unmarked, pagination undeclared.

## Scenario 2: Audit (retrieval test, challenge set)

**Prompt:**

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

**Assertions (with-skill run must satisfy):**

Scored:

- [ ] `sync` prompting for confirmation is flagged as a hang risk in automation and ranked as the most severe finding, above stdout pollution (Invocation Safety, Severity).
- [ ] The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence).
- [ ] Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence).
- [ ] The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes).
- [ ] The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry).
- [ ] `clean` mutating the global cache without `--dry-run` is flagged (Mutations).
- [ ] Alias duplication (`i`, `add`) and the vague `ls  Show stuff` description are flagged against the discovery path (Command Model / Discovery).
- [ ] The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format).

Non-scored conformance:

- [ ] Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction.
- [ ] Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`.
- [ ] The hang finding is `P0` and the stdout pollution finding is `P1` or higher.
- [ ] The coverage statement takes the form of the checklist coverage table with `not-checked` reasons.

**Expected baseline failures:** hang risk ranked below stdout pollution or missed, no observed-vs-inferred split, misses the update-check side effect or the `clean` dry-run gap, no statement of what the material cannot answer.

## Scenario 3: Diagnosis (routing test, challenge set)

**Prompt:**

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

**Assertions (with-skill run must satisfy):**

Scored:

- [ ] Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, and distinguishes what the help text shows from what is deduced about the hang (Review Workflow §0-1).
- [ ] Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator).
- [ ] Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team.
- [ ] Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting.
- [ ] Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1).
- [ ] Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria).

Non-scored conformance:

- [ ] The documented prompt is labeled `observed` and the hang mechanism `inferred`, in those words.

**Expected baseline failures:** jumps to auditing or redesigning depman, no evidence labels, no operator-vs-owner split, recommends `--yes` without noting the bypassed safety check.

## Scenario R1: Hardening an internal CLI (representative set)

Ordinary in-scope work: an owner asks for the changes that would make an existing internal CLI safe for agents to call.
Assertions are skill-neutral outcomes; this scenario is never tightened in response to its own results.

**Prompt:**

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

**Assertions (all scored):**

- [ ] Proposes a non-interactive, machine-readable output mode and says what each command's output looks like in it (Output).
- [ ] Proposes errors an agent can branch on without parsing prose: symbolic codes, an exit-code map, or both (Errors And Exit Codes).
- [ ] Removes every interactive prompt from the agent path: `create` takes values non-interactively, `delete` has an explicit non-prompting trigger plus a preview or dry-run, and `login` has a non-browser bootstrap (Agent-Safe Invocation, Mutations).
- [ ] Names the ambient state (`~/.envctl` cache, login credentials) and proposes how an agent inspects or disables it (Ambient State).
- [ ] Proposes how an agent discovers the contract (a schema command, `--help --json`, or equivalent) rather than learning flags from examples (Machine Schema).

**Expected baseline behavior:** likely passes several of these; record the result either way.

## Results

Rows dated before 2026-10-11 were scored against the earlier scenario 2 fixture (no stream attribution) and the earlier assertion lists; rows from 2026-10-11 on use the sets and scored/conformance split above.

| Date | Scenario | Run | Assertions passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-09 | 2 (audit) | baseline | 4/9 | Caught stdout pollution, opaque error, update-check side effect, `ls`/alias issues — but ad-hoc CRITICAL/HIGH/MEDIUM/LOW scale, no finding types, no evidence labels, no coverage table, missed `clean` dry-run entirely, ranked the `sync` hang below stdout pollution with no P0 concept. |
| 2026-06-09 | 2 (audit) | with-skill | 9/9 | Findings F1-F16 with P0-P3 + impl-bug/schema-gap/design-issue types; `sync` hang and update-check side effect both P0; `clean`/`install` dry-run gaps found; full coverage table with `not-checked` reason for Tests; open questions labeled absence-of-evidence. |
| 2026-06-09 | 1 (design) | baseline | 1/9 | Envelope design put errors on stdout by design; no machine profile, no dry-run (used `--confirm`), no per-command error catalog, no content hash on export, no inspection/isolation affordances; timeout unit only in prose; passed only pagination, scored leniently — `has_next_page` + `page` accepted as semantic equivalents of `has_more` + a navigation token. |
| 2026-06-09 | 1 (design) | with-skill | 9/9 | Declared machine profile with all flags in `global_flags`; `stderr_framing` field; `--dry-run` with `dry_run: true` and a declared dry-run output shape on both mutations; `errors_possible` per command; `--timeout-ms` with `unit` field; export returns path/byte_size/content_hash; `whoami`/`config show --resolved`/`env` plus `--isolated`. |
| 2026-07-05 | 1 (design) | with-skill | 9/9 | Post-#39 skill: single-flag `--machine` profile with `implies` and all implied flags declared; `--timeout` with `unit: ms`; export is the only `--output` command with path/byte_size/content_hash; per-command `errors_possible`; also organically exercised new contract items — `reconciliation` and `signal_semantics` on both mutations, secret intake via env/credential file only (no `--token` flag), `end_of_options_supported`, `shape_dialect`, cursor lifecycle contract, `single-error-object` framing, repair data in `details` with `field: "--title"`. |
| 2026-07-05 | 2 (audit) | with-skill | 9/9 | F1-F13 with P0-P3 + impl-bug/schema-gap/design-issue types; `sync` hang P0 with evidence "inferred (from help text; non-TTY behavior not observed)" — satisfies the split though the literal `observed` tag sits on the finding location rather than the prompt text; update check P1 with an explicit downgrade caveat if it proves local-only; coverage table includes the new Shell Safety and Prose Surfaces sections, with `not-checked` reasons for Stdin, Shell Safety, and Tests. |
| 2026-07-05 | 3 (diagnosis) | baseline | 2/6 | Passed the mitigation lead (`--yes`, `</dev/null`, step timeout) and stayed diagnosis-sized; no evidence labels, declared "no change to depman is needed" instead of an operator/owner split with escalation, no note that `--yes` bypasses the confirmation safety check, no probes offered. |
| 2026-07-05 | 3 (diagnosis) | with-skill | 6/6 | Failure path labeled `inferred` plus an explicit absence-of-evidence finding on missing non-TTY docs; mitigations first (`--yes`, `</dev/null`, short `timeout` with exit-124 note); owner-side fixes framed as P0-P2 escalation items to the owning team; `--yes` bypass caveat with "confirm the team is OK with unattended approval"; probes scoped to a throwaway checkout since `sync` mutates; no audit coverage table. |
| 2026-10-11 | 2 (audit, challenge) | baseline | 6/8 scored; 0/4 conformance | Revised fixture (stderr discarded) and revised assertions. Caught confirmed stdout pollution, opaque error, update-check side effect, `clean` dry-run gap, `ls` summary, and listed what it could not verify; demoted the `sync` hang to an unverified probe below stdout pollution and raised the aliases only as a question. Record: `runs/2026-10-11-scenario2-baseline.md`. |
| 2026-10-11 | 2 (audit, challenge) | with-skill | 8/8 scored; 4/4 conformance | Final wording (post commit 4); an identical 8/8 run against the pre-commit-4 wording is archived too. No regression vs same-day baseline; 1.81x tokens. Hang `P0` ranked above pollution `P1`; `observed`/`inferred` split on every finding; coverage table with `not-checked` reasons; restored timeout rule cited as a finding. Record: `runs/2026-10-11-scenario2-with-skill.md`. |
| 2026-10-11 | 1 (design, challenge) | with-skill | 9/9 | Post commit 4 wording, scored on nine assertions; its examples put options after `--` (found by Copilot, recorded in the run file, led to A10). A 9/9 run against the pre-commit-4 wording is archived too. Baseline not re-run (prompt unchanged since 2026-06-09). Used the new projection rule, `temporary` + catalog `retryable`/`reconcile_first`, `retry_after_ms` on rate limits; chose `ndjson-typed` framing. Most expensive arm of the day (131k tokens). Record: `runs/2026-10-11-scenario1-with-skill.md`. |
| 2026-10-11 | 1 (design, challenge) | with-skill | 10/10 | Third arm, after Copilot round 1 (commit d64e535) and the first scored against A10: all six `--` examples put options first. Side effect noted: the verb-set rule now in the checklist led the run to rename `search` to `find`. Record: `runs/2026-10-11-scenario1-with-skill-final.md`. |
| 2026-10-11 | 3 (diagnosis, challenge) | with-skill | 6/6 scored; 1/1 conformance | Pre-commit-4 wording (review-workflow §0/§1 unchanged by commit 4). Baseline not re-run (prompt unchanged since 2026-07-05). New `observed` definition applied to the user-supplied help text; mitigations first; owner fixes as escalation; probes gated on permission; no coverage table. Record: `runs/2026-10-11-scenario3-with-skill.md`. |
| 2026-10-11 | R1 (hardening, representative) | baseline | 4/5 | First run of the representative scenario. Strong baseline: non-interactive paths for `create`/`delete`/`login`, exit-code map with structured errors, cache and credential inspection, optional `schema`/`--help-json`. Missed only per-command output shapes (A1). Record: `runs/2026-10-11-scenarioR1-baseline.md`. |
| 2026-10-11 | R1 (hardening, representative) | with-skill | 4/5 | No regression and no scored gain: both arms miss A1 at the per-command-fields threshold (treatment names a class per command but fields for only two). Initially recorded 5/5; corrected after a Codex scoring review. Cost: 1.85x tokens and a full audit-shaped report (15 findings, coverage table, three-release plan) for a "propose changes in priority order" prompt. Record: `runs/2026-10-11-scenarioR1-with-skill.md`. |
