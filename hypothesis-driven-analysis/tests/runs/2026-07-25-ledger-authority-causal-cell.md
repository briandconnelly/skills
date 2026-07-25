# H1 status determination

**Status: `UNRESOLVED`**

(claim class stays `causal`, unchanged from Plan time — the per-hypothesis
summary table "repeats each row's Plan-time claim class in its `claim`
column unchanged" — SKILL.md, Conclusion.)

## Reasoning

T1's outcome is recorded as `CONTRADICTED`: the necessary prediction
("conversion lower among redesign sessions than non-redesign sessions,
same window") failed — conversion came out slightly *higher* among
redesign sessions. Read naively, the Conclusion section's precedence rule
would seem to apply: "an adequate test failing the necessary prediction
makes the hypothesis `REFUTED`" (SKILL.md, Conclusion). But that rule is
conditioned on the test being *adequate*, and a more specific rule governs
exactly this situation: a causal hypothesis tested by a bare
exposure–outcome contrast from a design that doesn't identify the causal
effect.

T1's method assigned exposure by "whether the account had opted into the
beta program, which accounts chose for themselves" — i.e., self-selection,
not randomization and not "something plausibly independent of the
outcome." That fails the design test the skill sets for causal language:

> "Use causal wording only when the design supports a counterfactual:
> exposure was randomized, or assigned by something plausibly independent
> of the outcome, and there is a comparison group or period that would
> have moved the same way had the cause been absent."
> — SKILL.md, Conclusion

And from the routing section, self-selected assignment is explicitly the
non-identifying case:

> "Assigned by anything else — someone launched it, it shipped to whoever
> got it, it happened in a week when other things also happened: nothing
> identifies the effect, every co-occurring change is a live rival, and
> that is full."
> — SKILL.md, "A causal question routes on its design, not its wording"

Accounts that opt into a beta are plausibly different from accounts that
don't (more engaged, higher-intent, etc.) independent of the redesign
itself — a live confound the design does nothing to rule out.

Because the design doesn't identify the causal contrast, the skill's
Conclusion section has a rule that overrides the general
CONTRADICTED-means-REFUTED precedence for exactly this case:

> "An exposure–outcome contrast from a design that does not identify the
> causal contrast cannot by itself mark that causal hypothesis `REFUTED`:
> that test leaves it `UNRESOLVED`, because a co-exposure pushing the
> other way could mask a real effect."
> — SKILL.md, Conclusion

T1 is precisely that: an exposure–outcome contrast (redesign vs.
non-redesign sessions) from a self-selected, non-identifying design. Its
`CONTRADICTED` result on H1's necessary prediction therefore cannot by
itself refute H1 — it leaves H1 `UNRESOLVED`.

The skill does allow one escape hatch — "Independent evidence can still
refute it when that evidence falsifies a preregistered necessary
prediction without relying on the unidentified contrast" (SKILL.md,
Conclusion) — but no such independent evidence exists here; T1 is the only
test on record for H1, and it relies entirely on the unidentified
opt-in contrast. So the escape hatch doesn't apply, and `UNRESOLVED`
stands as the status to record in the per-hypothesis summary table.
