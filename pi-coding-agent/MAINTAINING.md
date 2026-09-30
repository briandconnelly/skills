# Maintaining pi-coding-agent

This file is the only home of the procedure for updating the skill to a new Pi release.
`verified-against` holds the Pi version the skill was last fully checked against; bump it only in step 6.

## Update procedure

1. Install the new Pi release and run `uv run pi-coding-agent/scripts/check_drift.py` from the repository root.
   It checks, in order: every `docs/<page>.md#<section>` citation in `SKILL.md`, this file, and `references/`; every Pi interface listed in `GATE_DEPENDENCIES` in `scripts/pi_gate.py`; `pi_gate.py --self-test` and every fixture under `tests/fixtures/gate/` outside `negative/`.
   It then prints the `CHANGELOG.md` entries between `verified-against` and the installed version.
2. Fix every failure it reports.
   A moved section is fixed by citing its new anchor; a changed gate dependency is fixed in `pi_gate.py` or `faux-harness.ts`, with `GATE_DEPENDENCIES` updated to match; a fixture copied from Pi (the themes under `tests/fixtures/gate/`) is re-copied from the new release.
3. Read the changelog delta for new extension surfaces and for changed contracts the gate or the fixtures rely on; add a fixture and a `references/gate-recipes.md` entry for each new surface.
4. Re-check each entry in `references/choosing-a-surface.md` against the new docs; delete an entry the docs now cover and point to that page instead.
5. Re-run the behavioral scenarios (`tests/scenarios.md`) and trigger cases (`tests/trigger_cases.md`) only if `SKILL.md`'s rules or description changed.
6. Run `check_drift.py` again; when it passes with every stage run, write the installed version to `verified-against`.

## Scheduled drift check

Not set up yet: a CI job that installs the latest Pi and runs `check_drift.py` is deferred until `check_drift.py` has been run against a real Pi release upgrade.
