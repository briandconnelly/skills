# Scenario 2 (Audit) — With-skill scoring

Date: 2026-07-11
Tree: `a3cd37f`
Run: with-skill (produced WITH the skill)
Artifact scored: `scratchpad/s2-treatment.md` (see conversation scratchpad path)

Scored against `agent-friendly-mcp/tests/scenarios.md` § "Scenario 2: Audit (retrieval test)" — bullets labeled **(Scored — ...)** plus the unlabeled assertions in that section. "(Non-scored conformance.)" bullets and the bullet explicitly marked "(Covered by the priority-band bullet above.)" are excluded from the pass count (the latter folded into the priority-judgment row).

| # | Assertion | Pass/Fail | Evidence pointer |
|---|---|---|---|
| 1 | **(Scored — defect detection.)** Surfaces readOnlyHint lie, send/post_message overlap, unstructured error strings, 61-tool no-reduction gap, AND missing `additionalProperties: false` | PASS | F1 (lines 20-26) readOnlyHint lie; F3 (lines 36-42) overlap; F2 (lines 28-34) unstructured errors; F6 (lines 60-66) 61-tool no-reduction gap; F7 (lines 68-74) explicitly "none of the three `inputSchema` objects declare... `additionalProperties: false`." All five present. |
| 2 | **(Scored — priority judgment, predeclared bands.)** readOnlyHint ranked highest/merge-blocking; overlap and error strings ranked at least major-equivalent, distinguished from minor items | PASS | F1 and F2 both marked `Severity: Critical` (lines 22, 30); Summary (lines 118-122) explicitly names F1, F2, F5 as the three that "should be fixed first" — merge-blocking framing for the readOnlyHint lie. F3 (overlap) marked `Severity: Major` (line 38), F2 (errors) marked Critical — both clearly at/above major-equivalent, and distinguished from the Minor-tier F7/F8 (lines 70, 78). |
| 3 | send vs post_message overlap flagged as wrong-tool-selection finding | PASS | F3 (lines 36-42): "an agent cannot reliably pick the correct one on first call... Tool-selection probe: reading both definitions side by side gives no basis to choose," Section §3. |
| 4 | delete_all_messages flagged needing explicit destructiveHint:true + confirmation boundary, without claiming omission = safe | PASS | F5 (lines 52-58): notes spec defaults would apply implicitly but explicitly states "§3 requires declaring these explicitly rather than relying on inheritance" — flags the gap without treating the default as making it safe; remediation requires `destructiveHint: true` explicitly plus `confirm: true`. |
| 5 | Unstructured error strings flagged Critical or Major against §6 | PASS | F2 (lines 28-34): `Severity: Critical`, `Section: §6`. |
| 6 | 61 tools flagged as Major, no-reduction gap against §2 (not via a bare "search_tools would fix it" claim) | PASS | F6 (lines 60-66): `Severity: Major`, `Section: §1, §2`; remediation offers surface reduction OR "a documented host-managed disclosure mechanism (`search_tools`/`describe_tool`)" as one option among several, not asserted alone as sufficient. |
| 7 | Missing `additionalProperties: false` + ambiguous channel/msg parameter names flagged | PASS | F7 (lines 68-74): "`channel` (not `channel_id`) appears in all three tools; `msg`/`text` differ across near-duplicate tools... none of the three `inputSchema` objects declare a `required` array or `additionalProperties: false`." |
| 8 | **(Scored — coverage completeness.)** Accounts for every checklist section §1–§9, with explicit not-checked/N/A reasons for §4/§5 | PASS | "Checklist Coverage Table" (lines 102-114) rows §1-§9; §4 "not-checked... Notes state 'no resources'; §4 does not apply," §5 "not-checked... Notes state 'no prompts'; §5 does not apply." |
| 9 | Remediations name real callable surfaces (renamed tools, parameter names), not generic advice | PASS | F4 (line 50): "`<svc>_send_message`, `<svc>_delete_channel_messages`"; F5 (line 58): "rename to something unambiguous about scope (e.g. `clear_channel_history`)"; F7 (line 74): "Rename to `channel_id`; add `\"required\": [\"channel_id\", \"text\"]`." |

**Total: 9/9**
