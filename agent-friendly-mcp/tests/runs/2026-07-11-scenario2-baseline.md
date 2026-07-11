# Scenario 2 (Audit) — Baseline scoring

Date: 2026-07-11
Tree: `a3cd37f`
Run: baseline (produced WITHOUT the skill)
Artifact scored: `scratchpad/s2-baseline.md` (see conversation scratchpad path)

Scored against `agent-friendly-mcp/tests/scenarios.md` § "Scenario 2: Audit (retrieval test)" — bullets labeled **(Scored — ...)** plus the unlabeled assertions in that section. "(Non-scored conformance.)" bullets and the bullet explicitly marked "(Covered by the priority-band bullet above.)" are excluded from the pass count (the latter folded into the priority-judgment row).

| # | Assertion | Pass/Fail | Evidence pointer |
|---|---|---|---|
| 1 | **(Scored — defect detection.)** Surfaces readOnlyHint lie, send/post_message overlap, unstructured error strings, 61-tool no-reduction gap, AND missing `additionalProperties: false` | FAIL | Covers readOnlyHint (line 7-10), overlap (line 18-22), error string (line 45-49), 61-tool/pagination gap (line 53-55) — but never mentions `additionalProperties` anywhere in the document (grep confirms zero hits). Conjunctive assertion requires all five; missing one fails it. |
| 2 | **(Scored — priority judgment, predeclared bands.)** readOnlyHint ranked highest/merge-blocking; overlap and error strings ranked at least major-equivalent, distinguished from minor items | FAIL | Doc uses only one ad hoc tier, "## Critical Issues" (lines 5-22), which does correctly include readOnlyHint (line 7, called "the most dangerous finding") and the overlap (line 18) — good. But the error-string finding sits in its own untiered "## Error Handling" section (line 43-49), given no Major/Minor label and organizationally indistinguishable in weight from the minor schema nits in "## Schema / Description Quality Issues" (lines 24-41, e.g. "No enums or format constraints", line 40). No predeclared Critical/Major/Minor/Nit bands are used anywhere, so error strings are not demonstrably ranked above minor nits. |
| 3 | send vs post_message overlap flagged as wrong-tool-selection finding | PASS | Lines 18-22: "Duplicate/overlapping tools... An agent has no principled way to choose between them," listed under "## Critical Issues." |
| 4 | delete_all_messages flagged needing explicit destructiveHint:true + confirmation boundary, without claiming omission = safe | PASS | Lines 12-16: "No `destructiveHint` / `idempotentHint` annotations at all... No confirmation parameter... should almost certainly require explicit confirmation semantics and a strong `destructiveHint: true`." Never claims the omission implies safety. |
| 5 | Unstructured error strings flagged Critical or Major against §6 | FAIL | Lines 45-49 call it a "severe... problem" in prose but the finding lives outside the "## Critical Issues" section and receives no Major/Minor tier; no §6 (or any checklist-section) citation anywhere in the document. |
| 6 | 61 tools flagged as Major, no-reduction gap against §2 (not via a bare "search_tools would fix it" claim) | FAIL | Lines 53-55 raise pagination and namespacing concerns ("no visible namespacing... makes tool selection harder") but never as an explicitly Major-ranked finding, and no §2/checklist anchoring; framed mainly as a pagination gap rather than a surface-reduction/progressive-disclosure gap. |
| 7 | Missing `additionalProperties: false` + ambiguous channel/msg parameter names flagged | FAIL | `additionalProperties` never appears (grep confirms). Parameter-name inconsistency is noted only as `msg` vs `text` mismatch across tools (line 21), not as a general ambiguity/`additionalProperties` gap. |
| 8 | **(Scored — coverage completeness.)** Accounts for every checklist section §1–§9, with explicit not-checked/N/A reasons for §4/§5 | FAIL | Document never cites checklist section numbers (§1–§9) anywhere; no coverage table. Resources/prompts are covered as a substantive finding (lines 57-59, "No resources or prompts exposed") rather than an explicit not-checked/N/A entry against §4/§5. |
| 9 | Remediations name real callable surfaces (renamed tools, parameter names), not generic advice | FAIL | "Summary of Recommendations" (lines 63-69) references some real annotation fields (`destructiveHint`, `tools/list`) but proposes no concrete renamed tool or parameter identifiers (no e.g. `channel_id`, no new tool name) — stays at generic "add X" / "consolidate" level. |

**Total: 2/9**
