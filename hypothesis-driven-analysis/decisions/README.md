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

**Name the decision; never state the rule in operable form.** Point at the file that owns it.

A decision file has to say what was chosen, or it records nothing — "we adopted an evidentiary convention over a modal test" is the decision, and writing it down is the point.
What it must not carry is the rule in a form someone could *act on*: the conditions, the thresholds, the vocabulary, the branches.
The test is whether a reader could apply this file without opening the file that owns the rule.
If they could, this file has become a second home, and the next edit to the real one leaves it silently wrong.

This is not a style preference.
Issue #103 was one rule living in two places until the two disagreed, and a decision log is the most natural third place for that to happen again — it is exactly where someone would write down "what we decided the rule is."
The reasoning belongs here; the rule belongs where the pointer says.

The line is genuinely fine, and this repo has already been on the wrong side of it: the first draft of these files stated their rules operationally, which an external review caught in the same pull request that introduced the pointer rule.
