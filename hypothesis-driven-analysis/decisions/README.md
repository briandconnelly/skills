# Decision Log

This skill records measured claims in `tests/runs/artifacts/` and open questions as issues.
Neither captures the third kind: calls settled by *argument* — where the evidence was a reasoning failure rather than a run.
Those are the ones that drift, because the next reader inherits the conclusion without the constraint that produced it, and re-litigates it from scratch.

One file per decision, `NNN-slug.md`, with five parts:

- **Question** — the decision point, stated so someone who disagrees would recognize it.
- **Positions** — what was actually argued, including the position that lost.
- **What settled it** — the argument or evidence, not the authority who made the call.
- **Reopening condition** — what would make this worth revisiting. A decision with no reopening condition is a belief.
- **Where the rule lives** — a pointer.

## The pointer rule

**A decision file never states a normative rule.** It points at the file that owns it.

This is not a style preference.
Issue #103 was one rule living in two places until the two disagreed, and a decision log is the most natural third place for that to happen again — it is exactly where someone would write down "what we decided the rule is."
The reasoning belongs here; the rule belongs in SKILL.md.
If you find yourself writing a sentence an agent could follow, you are writing the rule, and it goes in the wrong file.
