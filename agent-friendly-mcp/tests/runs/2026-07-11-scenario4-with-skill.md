# Scenario 4 (Instructions and description prose) — with-skill run

- **Date:** 2026-07-11
- **Tree:** `a3cd37f`
- **Run:** with-skill (produced with the skill)
- **Artifact scored:** `/private/tmp/claude-501/-Users-bdc-projects-skills/24b2ced2-be35-4d8a-86bb-f5a73a4c40c9/scratchpad/s4-treatment.md`

## Per-assertion scoring

| # | Result | Evidence |
| --- | --- | --- |
| A1 | **PASS** | Every prose surface uses an explicit "Rules:" bulleted list distinguished from a separate "Background:" sentence or a "When to use:" line — e.g. instructions lines 5–12 (`Rules:` bullets then `Background:` paragraph); `deployctl_deploy_service` lines 18–29 (`When to use:` / `Rules:` / `Usage note:` / `Example:` as separate labeled blocks); `deployctl_rollback_service` lines 33–42 (same pattern). No rule is buried mid-narrative. |
| A2 | **PASS** | Every rule states its strength explicitly: change-ticket is flatly mandatory ("calls without one are rejected," lines 7, 23); dry-run is default-with-override ("Default to `dry_run: true`; only call with `dry_run: false` once a prior dry run ... reports no config drift," lines 8, 24); `force` is default-off-with-condition ("only when the target service's health has already been verified some other way," lines 9, 25); the 30-day rollback window is a checkable precondition ("confirm the previous release is less than 30 days old," lines 10, 40). No source hedge ("generally," "try to," "probably," "honestly") survives verbatim anywhere in the file. |
| A3 | **PASS** | `force`: sourced fact ("skips the pre-deploy health checks") plus an explicit permitted-use condition, not a bare "be careful" (lines 9, 25). Rollback: "pretty safe" is scoped directly to the observable condition rather than left as a free-floating vibe — "fast and low-risk **when the target release still exists**" (line 35) — paired with the checkable 30-day/GC rule (line 40), so the safety claim and the observable condition are integrated rather than parallel. |
| A4 | **PASS** | The rollback sentence is split cleanly: symlink mechanics/context lives in "Background" (instructions line 12) and in the rollback description's opening context sentence (line 35), while the 30-day limit is its own atomic Rule bullet (lines 10, 40) — mechanics and the binding constraint are never fused into one compound clause. |
| A5 | **PASS** | Spinnaker/Jenkins/2021 trivia is explicitly labeled "Background:" and kept structurally apart from the "Rules:" list, never interleaved (lines 5–12). The Friday soft norm is dropped entirely — "Friday" does not appear anywhere in the file — a valid resolution per the assertion (state as default-with-override, or drop), and no vibe-echo remains. |

**Total: with-skill 5/5**
