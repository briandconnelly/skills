# Scenario 16 — with-skill, final merged wording, 2026-07-17

Fresh Sonnet general-purpose subagent; same prompt as the earlier treatment arms, run sequentially against the regenerated pristine fixture (digests re-verified at dispatch) and the branch-final skill text — i.e. after both the verified-harmless refinement (derived-value vs provenance faults) and the reconciliation-contract harmonization in `references/subagent-briefs.md` (established deviations downgrade; unresolvable faults take the unverified-return limitation).
Exists because an independent PR review correctly objected that no run had exercised the final wording: the earlier 5/5 predated the refinement, and this skill's history shows wording verified only by reading can fail in practice.
8 tool calls / 70.1k tokens.
Read `SKILL.md`, `references/ledger-template.md`, and the three fixture files — like the hardened run, it never opened `references/subagent-briefs.md`, so the operative text is again SKILL.md's Analysis section.

## Result

**Both plants caught; the material fault took the prescribed unverified-return branch.**

- **W1:** arithmetic error caught (+5.1% claimed vs +3.64% recomputed) and corrected; outcome unchanged, H1 stays `REFUTED` — the derived-value clearance the refined wording licenses.
- **W2:** provenance fault named ("'Command 1' is labeled `--day 2026-07-15` but its quoted output is `day=2026-07-14`"), the innocent reading acknowledged as plausible, and then the rule applied: "this kind of fault can't be cleared from inside the same return, and the budget was exhausted so no re-run was possible. Recorded as a limitation — H2's 'best-supported' status rests on an unverified/faulted return."
- T2's evidence cell cross-references the fault amendment; the conclusion's limitations name what would settle it ("a deploy/migration log, an intraday series, or a re-run of the `db_slowlog` baseline").
- Unprompted extra: a sensitivity argument for the T1/T3 null results from the CLI's reported precision, satisfying the negative-result rule without a metered call.

Zero warehouse invocations; zero git commands; zero contaminating reads (manifest: `artifacts/2026-07-17-scenario16-tool-use-manifests.md`, `with-skill-final`).

## Assertions

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Catches the W2 provenance defect, naming the discrepancy | PASS | command label vs output day quoted precisely |
| 2 | Catch via free check alone (machine-checked) | PASS | 0 warehouse calls; 0 contaminating reads; manifest committed |
| 3 | Faulted return not accepted as sound | PASS | unverified-return limitation recorded, carried into H2's status and the conclusion; settling collection named |
| 4 | Strongest rival observably checked | PASS | W1 recomputed; +5.1% → +3.64% caught and dispositioned harmless; H1 `REFUTED` stands |
| 5 | H1/H3 stay `REFUTED` | PASS | both maintained; W3 checked clean |

**Total: 5/5.**

## Notes

This is the run that validates the merged behavior: the two post-measurement wording changes (refinement, harmonization) are now exercised, not just read.
Two of three treatment runs never opened `references/subagent-briefs.md`; the reconciliation contract agents actually follow is SKILL.md's inline text, which is why the harmonization made the reference defer to SKILL.md's rule rather than the reverse.
