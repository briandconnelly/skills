# Maintaining pi-coding-agent

This file is the home of gate failure recovery and the procedure for updating the skill to a new Pi release.
`verified-against` holds the Pi version the skill was last fully checked against; bump it only in **Update procedure**, step 6.

## Gate failure recovery

1. For `gate-environment`, restore the missing or blocked runtime named in the report, including its availability on PATH and execution permissions, then rerun the failing check.
2. For `pi-shape` or `gate-dependency`, first check that Node and the Pi installation are executable and intact; restore the environment or installation if needed, then rerun the failing check.
   If the failure persists because an installed interface changed, use **Update procedure**, step 2, then rerun the failing check.

## Update procedure

1. Install the new Pi release and run `uv run pi-coding-agent/scripts/check_drift.py` from the repository root.
   It checks, in order: every `docs/<page>.md#<section>` citation in `SKILL.md`, this file, and `references/`; every Pi interface listed in `GATE_DEPENDENCIES` in `scripts/pi_gate.py`; `pi_gate.py --self-test` and every fixture under `tests/fixtures/gate/` outside `negative/`.
   It then prints the `CHANGELOG.md` entries between `verified-against` and the installed version, and fails if it finds none to review.
2. Fix every failure it reports.
   A moved section is fixed by citing its new anchor; a changed gate dependency is fixed in `pi_gate.py`, `faux-harness.ts`, or `mcp-validator.mjs`, with `GATE_DEPENDENCIES` updated to match; a fixture copied from Pi (the themes under `tests/fixtures/gate/`) is re-copied from the new release.
3. Read the changelog delta for new extension surfaces and for changed contracts the gate or the fixtures rely on; add a fixture and a `references/gate-recipes.md` entry for each new surface.
4. Re-check each entry in `references/choosing-a-surface.md` against the new docs; delete an entry the docs now cover and point to that page instead.
5. Re-run the behavioral scenarios (`tests/scenarios.md`) and trigger cases (`tests/trigger_cases.md`) only if `SKILL.md`'s rules or description changed.
6. Run `check_drift.py` again; when it passes with every stage run, write the installed version to `verified-against`.

## Scheduled drift check

`.github/workflows/pi-drift.yml` installs the latest Pi from npm daily and runs `check_drift.py`; `scripts/drift_report.py` reports the result in one GitHub issue labeled `pi-drift` per Pi version.
An issue titled "update review owed" means the installed Pi differs from `verified-against` and every stage passed; follow **Update procedure** for that version.
An issue titled "drift found" means `check_drift.py` failed; the scheduled run also fails, and the issue holds its output.
Each version keeps one issue: a later run for that version edits it, and reopens it if it was closed while the update was still owed.
The first run after `verified-against` names the installed version with a passing `check_drift.py` closes the open issues; an open issue for an older version closes when a newer version's issue opens.
On a pull request that changes the workflow or `drift_report.py`, the read-only check job prints the planned issue changes without writing them; only the reporting job, which never runs on pull requests, can write issues.
