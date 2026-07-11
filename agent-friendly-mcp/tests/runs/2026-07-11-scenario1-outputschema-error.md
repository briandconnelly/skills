# Scenario 1 — focused probe: error-path / `outputSchema` contract-correctness

Date: 2026-07-11
Tree: `a3cd37f`
Run: with-skill, focused error-path probe (Scenario 1 "Design", scored assertion only)
Artifact: `/private/tmp/claude-501/-Users-bdc-projects-skills/24b2ced2-be35-4d8a-86bb-f5a73a4c40c9/scratchpad/s1err-treatment.md`

## Assertion scored

Scenario 1, **(Scored.)** bullet: "The error path is contract-correct and distinct from the success shape" —
`isError: true` carries the §6 error envelope in `structuredContent` with a `content` fallback;
`outputSchema` scoped to success only, stated as an interpretation;
either a success-only `outputSchema` with the error envelope validated separately OR a success∪error union;
text-only error only as a disclosed degraded mode.

## Verdict: PASS

Evidence, from the artifact's `### ERROR — wire shape` section (all three worked examples: `issue_not_found`, `repo_not_found`, `rate_limited`):

1. **`isError: true` present on every error result**, e.g.:
   ```json
   "result": {
     "isError": true,
     "content": [...],
     "structuredContent": { "code": "issue_not_found", ... }
   }
   ```

2. **Error envelope lives in `structuredContent`, distinct from the success shape**, with a `content` textual fallback kept alongside it in every example (`content[0].text` present in all three). The artifact states this explicitly: "The error envelope travels in `structuredContent`, not `content`. `content[0].text` is a redundant human-readable mirror for weak clients, never the parsed source of truth."

3. **`outputSchema` scoped to success only, and explicitly flagged as an interpretation, not asserted as settled spec**: "`outputSchema` governs success results only (the §3 deliberate reading of the unsettled point)." And again: "None of the three `structuredContent` bodies above would validate against `get_issue`'s success `outputSchema`... that's correct and expected under this skill's scoping position, not a bug; a validating client must branch on `isError` before choosing which schema (success `outputSchema` vs. the documented error envelope) to check against." This matches the accepted "success-only `outputSchema` with the error envelope validated separately" branch (not a union, and the union alternative is not claimed either — no conflict).

4. **Text-only-error framed correctly as a degraded mode, not the default**: "This server never needs the degraded `content[0].text`-only carrier. Its framework places native `structuredContent` on `isError: true` results without limitation, so `error_carriers` in the capability summary names only `structuredContent`/`error.data` — no disclosed degraded mode." The artifact never uses text-only as the primary error carrier in any of the three examples; it correctly treats the text-only path as an optional degraded mode this server doesn't need, and would disclose if it did.

All four sub-requirements of the assertion are satisfied with direct textual and wire-shape evidence.

## Baseline expectation (not a scored run)

Per the Scenario 1 "Expected baseline failures" list (prose-only error descriptions, no output schema), the documented baseline expectation for this specific assertion is that a baseline (no-skill) run's error results either reuse the success `structuredContent` shape (no distinct error envelope) or omit the structured error envelope entirely, falling back to prose-only / `content`-only error reporting with no `outputSchema` scoping discussion at all. No fresh baseline run was executed for this focused probe — this is the expected baseline failure mode, not a scored baseline result.
