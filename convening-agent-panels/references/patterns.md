# Pattern catalog

Each pattern below lists **when it fits**, the **member layout**, the **aggregation** it pairs with, and a **worked example**. Patterns compose — the closing section shows common stacks. Pick the pattern in step 2 of the selection procedure; pick its aggregation in step 3 (see `aggregation.md`).

A recurring distinction: **symmetric** patterns run every member on the same job and combine; **asymmetric** patterns give members different roles (produce vs check vs refine).

**On member count.** Two entries below — single **Judge** (#2) and **Generator + verifier** (#7) — are one- and two-member *primitives*. They are catalogued because the larger patterns compose from them and because they are the right **trade-down** when the gate clears but a full panel is overkill. If your whole job is exactly one Claude + one Codex, the tuned home is `deliberating-with-codex` (if installed). Reach for this skill's full machinery when you need **three or more members**, intra-family diversity, or a deliberate choice among the aggregation menu.

---

## 1. Independent ensemble (symmetric)

**When it fits.** An open problem with no committed answer, and you want robustness from independent attempts. The cheapest pattern that buys real diversity.

**Member layout.** N members each get the *same neutral task statement* and answer independently — no cross-talk, no shared drafts. Diversity comes from family/model spread (staff per step 4).

**Aggregation.** Majority/plurality vote for discrete answers; median/trimmed mean for scores; synthesis or select-best for free text.

**Worked example.** "Is this migration plan safe to run Friday?" → a heavier-model subagent + a cheaper-model subagent + a `codex_consult` member, each handed only the plan and the question. Two say yes, one flags an unguarded backfill. The split *is* the result: investigate the backfill before deciding. Do not let 2-of-3 "pass" the plan — verify the dissent.

**Failure mode.** Same-family, same-model members with reworded prompts fail together; the vote then manufactures confidence. Spend the diversity budget before adding members.

---

## 2. Judge (asymmetric, one judge)

**When it fits.** You have an artifact — a draft, a diff, a design — and want an independent critique *of it*. This is the single-judge case; scale to a judge panel (pattern 3) when one judge's bias is the risk.

**Member layout.** You produce the artifact; one member judges it. For a diff, `codex_review_changes` (structured `verdict`/`confidence`/`findings`). For a design or prose, `codex_consult` or a Claude subagent with a rubric.

**Aggregation.** None — a single judge. The verdict is signal toward your call, not a passing grade.

**Worked example.** You wrote a retry helper; `codex_review_changes` on the diff returns `concerns` with a "backoff never resets after success" finding. You reproduce it against the code before acting — read-only review is static and did not run the test.

---

## 3. LLM-as-judge panel (asymmetric, multiple judges)

**When it fits.** You have one or several candidate outputs and want a principled score, ranking, or pick — and a single judge's position bias or self-preference is a real risk. The highest-value place to spend on cross-family diversity.

**Member layout.** 3+ judges (cross-family where possible) each score or rank the candidate(s) against a shared rubric. **Cross-judge** when judging members' own work: each family judges the *other's* output, never its own, to cancel self-preference. **Swap positions** across calls (A-then-B and B-then-A) — position bias survives even across families.

**Aggregation.** Median or trimmed mean of scores; per-criterion aggregation when the rubric is multi-dimensional; Borda/Condorcet for rankings. High inter-judge variance is itself a signal the item is genuinely ambiguous.

**Worked example.** Three implementations of the same endpoint; two Claude judges on different models and a `codex_consult` judge each rank all three on correctness, clarity, and risk. Borda over the three rankings picks the winner; you read the one criterion where they disagreed before committing.

---

## 4. Debate / deliberation (symmetric, with cross-talk)

**When it fits.** A decision blocked by disagreement, where seeing the strongest case on each side is what unblocks it. The most expensive pattern — reserve for genuinely contested, high-stakes calls.

**Member layout.** Two members take assigned opposing positions (adversarial) or critique-and-revise toward agreement (collaborative), exchanging across rounds. A separate judge or the chair resolves. Cross-family makes the strongest debate.

**Aggregation.** A resolving judge call, or chair adjudication. **Rounds are explicit and ≤2** — open-ended debate burns spend and tends to converge on confident-but-wrong consensus.

**Worked example.** "Rewrite vs. patch this module?" A Claude subagent argues rewrite, a Codex member argues patch, each rebuts once; the chair adjudicates on the migration-cost evidence each surfaced.

---

## 5. Persona / role panel (symmetric)

**When it fits.** A problem with several legitimate angles (no single "correct" answer) where you want coverage — domain expert, skeptic, red-teamer, end-user — rather than a vote.

**Member layout.** Each member gets a distinct stance or expertise in its prompt; they answer independently. Persona is a *coverage* device, not a diversity substitute — back it with family/model spread or the personas just paraphrase one model.

**Aggregation.** Extract-and-union (collect distinct concerns, dedupe) usually beats voting here — you want the union of angles, not a majority.

**Worked example.** A new auth flow reviewed by a "security" seat, a "developer-experience" seat, and an "ops/on-call" seat across two families; the chair unions their distinct concerns into one issue list.

---

## 6. Mixture-of-Agents / layered (asymmetric, layered)

**When it fits.** A hard problem with budget to spend, where layering proposers and aggregators beats any single strong member.

**Member layout.** Layer 1: several proposers generate candidates independently. Layer 2: one or more aggregators synthesize the candidates into an improved answer; optionally feed forward into another layer.

**Aggregation.** Built into the aggregator layer (synthesis). Cap layers at 2 unless you can measure that a third pays for itself.

**Worked example.** Three proposers (two Claude models plus a Codex member) draft three answers to a thorny schema-design question; a heavyweight aggregator merges them into one design, citing which idea came from where.

---

## 7. Generator + verifier (asymmetric)

**When it fits.** You have one strong producer and want to catch the errors *that producer would not catch in itself*. A cheaper, targeted alternative to a full panel.

**Member layout.** Family A produces; family B verifies (fact-checks, finds bugs, scores against a rubric). The verifier being a **different family** is the whole point — it is less likely to rubber-stamp errors it would have made too.

**Aggregation.** Pass/fail gate from the verifier, or a findings list the producer must resolve.

**Worked example.** A Claude subagent implements a parser; a `codex_review_changes` pass verifies the diff. Distinct from Judge only in framing — here the producer is also a panel member you chose, not just "your own work."

---

## Composing patterns

Real panels stack:

- **Propose → judge → synthesize.** Ensemble generates candidates (1) → judge panel ranks them (3) → chair synthesizes the winner with the dissent noted. The default high-stakes stack.
- **Propose → verify.** Ensemble or single producer → generator+verifier gate (7) before you act.
- **Debate → judge.** Deliberation (4) surfaces the cases → judge panel (3) resolves.

Keep the stack as shallow as the blocker requires. Each added layer is more spend, more latency, and another place for correlated error to creep in. If two members and one aggregation rule resolve the decision, stop there.
