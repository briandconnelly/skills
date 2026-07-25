# H3 status determination

## Status: `UNRESOLVED`

(Worker recorded `CONTRADICTED`, but that outcome does not survive reconciliation — see below. The status column itself only ever holds `REFUTED` or `UNRESOLVED`, per SKILL.md Conclusion: "The status set is closed: `REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise.")

## Reasoning

**1. The method never touched the preregistered prediction.**

H3's necessary prediction is: "The export's row count for automated closures matches the ticketing system's own independent counter for the same window."

T3's Method, as reported: "ran a field-validity sweep over the export: every timestamp parses, every `status` value is in the documented enum, no negative durations, no nulls in required columns — 41,882 rows, zero anomalies."

That is a schema/field-validity audit, not a row-count reconciliation against an independent counter. No comparison to the ticketing system's own counter appears anywhere in the method. The skill draws this exact line at Plan time:

> "A schema audit is not this check — nulls, duplicates, and type drift cannot detect a row that is simply absent." (SKILL.md, Plan)

A validity sweep confirming well-formed rows says nothing about whether rows are missing; it cannot speak to the prediction at all.

**2. This is an established deviation, and it makes the outcome NON_DISCRIMINATING, not CONTRADICTED.**

The Method column is itself the execution record here, and it plainly shows a procedure the brief did not authorize (a field-validity sweep in place of a row-count-vs-independent-counter reconciliation) — a "coherent execution record" showing the deviation, per:

> "A deviation is established when the worker reports it and the execution record does not contradict the report, or when a coherent execution record shows it — that is, when the command and the tool's own output agree on a procedure the brief did not authorize." (SKILL.md, Analysis)

> "An established deviation makes the reconciled outcome `NON_DISCRIMINATING` when the procedure that record evidences did not adequately test the preregistered prediction, unless evidence from outside the return verifies the deviation harmless." (SKILL.md, Analysis)

Nothing outside the return verifies the substituted procedure as harmless (no cross-check against the ticketing system's counter is mentioned anywhere), so the reconciled outcome for T3 is `NON_DISCRIMINATING`, not the worker's self-reported `CONTRADICTED`.

**3. Even taken at face value, this test class is barred from refuting a data-artifact hypothesis.**

Independent of the reconciliation argument above, the skill states a categorical rule for exactly this hypothesis class and exactly this test shape:

> "A data-artifact hypothesis is never `REFUTED` on a validity check that did not probe coverage and missingness." (SKILL.md, Conclusion)

T3 probed field validity (nulls, enum membership, negative durations) — not coverage or missingness against an independent denominator. This rule forecloses `REFUTED` for H3 on this evidence regardless of how the worker labeled the outcome.

**4. Applying the closed status vocabulary.**

Since the necessary prediction was never adequately tested (no adequate test failed it), H3 does not meet the bar for `REFUTED`:

> "`REFUTED` when the hypothesis's declared necessary prediction failed under an adequate test, `UNRESOLVED` otherwise." (SKILL.md, Conclusion)

H3 therefore is `UNRESOLVED`. The per-hypothesis summary row (per the ledger template's Conclusion form, `references/ledger-template.md`) would read:

| id | claim | status | basis |
| --- | --- | --- | --- |
| H3 | data-artifact | UNRESOLVED | T3's method (field-validity sweep) never tested the preregistered prediction (export row count vs. the ticketing system's independent counter); reconciled outcome is NON_DISCRIMINATING, and a data-artifact hypothesis is never REFUTED on a validity check that did not probe coverage and missingness. Coverage/missingness for automated closures remains untested. |

## Sources

- `/Users/bdc/projects/skills/hypothesis-driven-analysis/SKILL.md` — Plan section ("A schema audit is not this check..."), Analysis section (established-deviation rules), Conclusion section (closed status vocabulary; data-artifact/validity-check rule).
- `/Users/bdc/projects/skills/hypothesis-driven-analysis/references/ledger-template.md` — Conclusion per-hypothesis summary table format ("status is REFUTED or UNRESOLVED and nothing else"); worked example's H5 (data-artifact) row shows the correct comparator test (T6: independent LB counter vs. log volume) that T3 should have but did not run.
