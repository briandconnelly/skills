# Test Scenarios for agent-friendly-cli

Behavioral test scenarios for this skill, following the baseline/with-skill methodology: run each scenario with a fresh subagent that does NOT have the skill loaded (baseline), then with the skill loaded (treatment), and compare against the assertions.
A baseline run that already satisfies every assertion means the scenario is too easy; tighten it.
An assertion the with-skill run misses is a finding against the skill, not against the agent.

## How to run

1. **Baseline:** dispatch a subagent with only the scenario prompt below.
   Record which assertions its output satisfies.
2. **Treatment:** dispatch a fresh subagent with the skill content available (or triggered via its description) and the same prompt.
3. **Score:** every assertion is pass/fail with a one-line evidence pointer into the transcript.
   Record results in the table at the bottom.
   Assertion lists may be tightened over time; a results row reflects the assertions as of its date.

## Scenario 1: Design (application test)

**Prompt:**

> Design the agent-facing CLI contract for a tool named `notectl` that manages notes (`id`, `title`, `body`, `tags`) backed by a remote API.
> It must support: list notes, get a note, search notes, create a note, delete a note, and export all notes to a file.
> Produce: the command surface, the machine-readable schema, example success payloads, and example error payloads for at least two failure modes.

**Assertions (with-skill run must satisfy):**

- [ ] A canonical machine profile is declared in the schema, and every flag it names is declared as a flag (Machine Schema).
- [ ] The schema declares numeric exit codes plus symbolic error codes, with a per-command error catalog for at least the mutating command (Errors And Exit Codes).
- [ ] stdout is success payload only; structured failures go to stderr with declared framing (Output).
- [ ] `delete` requires an explicit trigger and supports `--dry-run` whose output includes `dry_run: true` (Mutations And Long-Running Work).
- [ ] List/search output declares pagination with `has_more` and a navigation token (Output).
- [ ] Export is the only `--output <file>` command and returns path, byte size, and content hash (Output).
- [ ] Duration flags declare units in the name or a `unit` field (Machine Schema).
- [ ] Each command declares one output class; any flag that switches the class declares the switch (Output).
- [ ] Ambient state (config, credentials, cache) is declared with inspection and isolation affordances (Ambient State).

**Expected baseline failures:** no machine profile or schema fingerprint, prose-only errors, no exit-code map, no stdin/ambient-state declarations, dry-run absent or unmarked, pagination undeclared.

## Scenario 2: Audit (retrieval test)

**Prompt:**

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> The audience is the tool's author, who can change anything.
>
> ```text
> $ depman --help
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
> $ depman ls --json
> ✨ DepMan 3.2
> Checking for updates...
> [{"name":"left-pad","version":"1.3.0"},{"name":"is-odd","version":"3.0.1"}]
> Done in 0.42s ✓
>
> $ depman install nonexistent-pkg
> Error: something went wrong (see log)
> $ echo $?
> 1
> ```

**Assertions (with-skill run must satisfy):**

- [ ] Findings use the `P0`-`P3` severity scale and the finding format from `review-workflow.md`: severity, type (`impl-bug`/`schema-gap`/`design-issue`), location, impact, fix direction.
- [ ] Evidence labels are applied: `observed` for session behavior, `inferred` for deduced behavior such as the non-TTY hang mechanism, `absence-of-evidence` for the missing schema/machine profile.
- [ ] `sync` prompting for confirmation is flagged as a hang risk in automation, severity `P0`, with the documented prompt labeled `observed` and the actual non-TTY hang behavior labeled `inferred` (Invocation Safety, Evidence).
- [ ] Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged at `P1` or higher (Output).
- [ ] The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes).
- [ ] The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry).
- [ ] `clean` mutating the global cache without `--dry-run` is flagged (Mutations).
- [ ] Alias duplication (`i`, `add`) and the vague `ls  Show stuff` description are flagged against the discovery path (Command Model / Discovery).
- [ ] A checklist coverage table is produced with `not-checked` reasons for sections the captured material cannot answer (e.g., stdin contract, tests).

**Expected baseline failures:** ad-hoc severity labels or none, no finding format, no evidence labels, no coverage table, misses the update-check side effect or the prompt hang risk.

## Scenario 3: Diagnosis (routing test)

**Prompt:**

> Our CI pipeline calls `depman sync --quiet` in a non-interactive job, and the job hangs until the 60-minute timeout kills it.
> I'm an SRE on the platform team; another team owns depman, so we can't change it, but we control the pipeline.
> The `--help` output says: `sync    Sync the lockfile (asks for confirmation first)` and lists a `--yes  Assume yes` option.
> What's going on and what should we do?

**Assertions (with-skill run must satisfy):**

- [ ] Names the confirmation prompt blocking on stdin in a non-TTY job as the most likely failure path, with evidence labels: the documented prompt `observed`, the hang mechanism `inferred` (Review Workflow §0-1).
- [ ] Leads with the smallest caller-side mitigation available today (e.g., `--yes`, stdin closed via `</dev/null` to fail fast, a short job-level timeout) rather than tool redesign (SKILL.md Workflow §1, internal operator).
- [ ] Separates operator-side workarounds from owner-side fixes, and frames owner-side fixes as escalation items to the owning team.
- [ ] Notes that `--yes` bypasses the confirmation safety check and states what that confirmation was protecting.
- [ ] Offers one or two safe confirmation probes with permission requested first, or states why probing isn't useful (Review Workflow §1).
- [ ] Stays diagnosis-sized: no full audit checklist coverage table (SKILL.md Done Criteria).

**Expected baseline failures:** jumps to auditing or redesigning depman, no evidence labels, no operator-vs-owner split, recommends `--yes` without noting the bypassed safety check.

## Results

| Date | Scenario | Run | Assertions passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-09 | 2 (audit) | baseline | 4/9 | Caught stdout pollution, opaque error, update-check side effect, `ls`/alias issues — but ad-hoc CRITICAL/HIGH/MEDIUM/LOW scale, no finding types, no evidence labels, no coverage table, missed `clean` dry-run entirely, ranked the `sync` hang below stdout pollution with no P0 concept. |
| 2026-06-09 | 2 (audit) | with-skill | 9/9 | Findings F1-F16 with P0-P3 + impl-bug/schema-gap/design-issue types; `sync` hang and update-check side effect both P0; `clean`/`install` dry-run gaps found; full coverage table with `not-checked` reason for Tests; open questions labeled absence-of-evidence. |
| 2026-06-09 | 1 (design) | baseline | 1/9 | Envelope design put errors on stdout by design; no machine profile, no dry-run (used `--confirm`), no per-command error catalog, no content hash on export, no inspection/isolation affordances; timeout unit only in prose; passed only pagination, scored leniently — `has_next_page` + `page` accepted as semantic equivalents of `has_more` + a navigation token. |
| 2026-06-09 | 1 (design) | with-skill | 9/9 | Declared machine profile with all flags in `global_flags`; `stderr_framing` field; `--dry-run` with `dry_run: true` and a declared dry-run output shape on both mutations; `errors_possible` per command; `--timeout-ms` with `unit` field; export returns path/byte_size/content_hash; `whoami`/`config show --resolved`/`env` plus `--isolated`. |
