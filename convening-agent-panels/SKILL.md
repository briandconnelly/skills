---
name: convening-agent-panels
description: Use when the user wants more than one model instance run on the same problem and combined into one result — "get a panel of models", "have several models vote / judge / debate", "ensemble", "best-of-N", "cross-check with multiple models", "a second and third opinion", or asks how to combine, aggregate, or reconcile outputs from more than two model calls. Members may span families (e.g. Claude + Codex) and models within a family. For the specific two-model Claude+Codex case, prefer `deliberating-with-codex` if it is installed.
---

# Convening agent panels

A panel is two or more model instances run on the same problem and combined into one result.
This skill does three things: (1) decides **whether** a panel is worth it, (2) **selects** the pattern and the aggregation rule that fit the situation, and (3) tells you how to **run** the members across families and models and synthesize their outputs.

**The panel logic here is self-contained and model-agnostic.** The gate, pattern selection, aggregation rules, and diversity budget apply to any set of model members regardless of backend. Two backends are spelled out — Claude subagents and Codex tools — but the reasoning does not depend on either, and the minimum safety contract for a Codex member is inlined below (see *Independence and safety*).

Two **optional** sibling skills, available only if the `codex-in-claude` plugin is installed, go deeper on the Codex backend specifically. Neither is required to run a panel:

- `collaborating-with-codex` — the per-tool contract for the Codex tools (envelope shapes, dry-runs, redaction, server-down fallback).
- `deliberating-with-codex` — the tuned **two-model** Claude+Codex patterns (Judge, two-member panel, review–revise). If the job is exactly "one Claude + one Codex," prefer that skill. This skill is the generalization: **three or more members**, **intra-family diversity** (a heavier vs. a cheaper model in one family), or a **deliberate choice among the full aggregation menu**.

## Default: don't convene

**A single member is the default. A panel is opt-in and exceptional.** Every added member multiplies token spend and latency, and most members route context to an external provider on each active call. Convene a panel only when the value/risk gate clears — all three must hold:

- **Stakes are high** — a hard-to-reverse change, a load-bearing design decision, a security- or data-integrity-sensitive artifact.
- **One opinion is genuinely insufficient** — either a live disagreement is what blocks the decision, or you face a load-bearing choice where genuine uncertainty is stopping you from acting. You do **not** need a committed answer already; an open decision you can't confidently make qualifies.
- **You can act on the result** — you have the context to verify and synthesize, not just collect more text.

If those don't all hold, make one call (or none) and move on. Scaling from two members to N raises the bar, it does not lower it: a third member is justified only when a tie, a split decision, or a coverage gap in the two-member case is the actual blocker.

**Check stakes first, and beware the suitability trap.** The gate turns on stakes, reversibility, and actionability — *not* on whether the task is shaped like something a panel handles well. "This is a bounded, verifiable correctness check" describes a great panel mechanic and is still a gate **failure** if the stakes are low: an artifact that is cheap to verify directly (a regex, a small helper, a lookup) is one you *verify directly*. Verifiability **lowers** a panel's value — you can just check it — it does not raise it. If you can't name which of high-stakes / irreversible / blocked-decision is present, the gate has failed regardless of how well the task fits a pattern.

**When the user asks for a panel but the gate fails, lead with the trade-down — don't convene reflexively.** A direct request ("have a few models check this") is not gate clearance, and the wrong response is to skip straight to staffing members. Lead with a one-line reason (a panel multiplies spend and latency on something cheap to verify directly) and the cheaper path: do the actual check yourself, or offer a single second opinion. "This is quick to verify directly, so a panel would mostly burn tokens — I can just check it, or get one outside opinion if you'd like a second pair of eyes. Want either?" beats both reflexive compliance and a flat no.

**If the user reaffirms with that information, comply — the discipline is that they're *informed*, not that you refuse.** It's their decision and their tokens. Two things are non-negotiable before and after you run a below-gate panel:

1. **Inform first, every time.** Never convene silently. State in one line that this is below the bar and why, and name the false-confidence trap: members reasoning from one framing share blind spots, so agreement is *the absence of a caught error, not proof*.
2. **Label the result low-signal; never sell it as rigor.** Report convergence as "nobody caught a problem," not "verified" or "high confidence." Surface any genuine dissent, and do **not** merge the outputs into a confident averaged consensus. A below-gate panel that gets dressed up as verification is the real failure.

**New facts can also legitimately reopen the gate.** If the user supplies information that actually raises the stakes, makes the change harder to reverse, or shows your "quick to verify directly" read was wrong, re-run the gate — it may now genuinely clear, which is different from informed-comply on something still low-stakes.

| Rationalization | Reality |
|---|---|
| "They asked, so just dispatch the members" | A request still gets the advisory first. Inform + offer the trade-down, *then* comply if they reaffirm — never skip to silent dispatch. |
| "They'll pay, so it must be worth running" | Cost consent doesn't make a panel *informative*. Run it if they insist, but say plainly it's low-signal. |
| "More models = more confidence" | Members reasoning from one framing share blind spots; agreement is the absence of a caught error, not proof. |
| "Five agreed, so it's solid — report it as verified" | Convergence below the gate means "nobody caught a problem," not "verified." Report it that way; surface any dissent; no averaged mush. |
| "It's a bounded, verifiable task — a great fit for a panel" | Panel-*suitability* is not gate clearance. "Easy to verify directly" lowers a panel's value, not raises it. Lead with the direct check. |
| "I'll quietly merge the outputs into one clean verdict" | Manufacturing consensus from a below-gate panel is selling theater as rigor. Keep it honest: convergence-or-dissent, plainly stated. |

**Red flags — stop and correct course:**

- You're staffing members without first telling the user this is below the bar and why.
- You convened because the task "fits a pattern," not because stakes / irreversibility / a blocked decision is present — and you skipped the trade-down offer.
- You're about to report a below-gate panel's agreement as "verified" or "high confidence" rather than "nobody caught a problem."
- You're averaging or merging below-gate outputs into a confident consensus instead of surfacing convergence-or-dissent plainly.

**Worked example (gate fails — lead with the trade-down).** *"I wrote a quick regex to parse log lines. Can you have a few models double-check it for me?"* This is the trap: a regex is a bounded, verifiable artifact, which *feels* like a great panel task — but low stakes + cheap-to-verify-directly means the gate fails. The right opener is not "sure, here's the panel I'd run," it's: *"A regex is something I can verify directly in seconds — run it against sample lines, check the edge cases and capture groups. Several models voting on it would mostly burn tokens, and their agreement wouldn't prove it's right. Paste it with a few sample lines and I'll check it, or I can grab one outside opinion if you'd like fresh eyes."* If they then say "no, run the panel anyway," comply — informed — and report it as low-signal.

All of these mean: **stop, state the one-line reason, and offer the trade-down (direct check or one second opinion) — then run only a labeled low-signal panel if the user reaffirms.**

## The selection procedure

Work these five steps in order. Steps 1–2 pick the **pattern**; step 3 picks the **aggregation rule**; step 4 staffs the **members**; step 5 **bounds** the run. Read `references/patterns.md` for the full catalog and `references/aggregation.md` for the rule menu.

### 1. Gate

Apply the value/risk gate above. If it fails, stop here with a single call (or, if the user reaffirms after the below-gate warning, a labeled low-signal panel — see *Default: don't convene*). If it passes, continue.

### 2. Shape — what you have and what you want

Match your situation to a pattern. Full descriptions and worked layouts are in `references/patterns.md`.

| You have… | and you want… | Pattern |
|-----------|---------------|---------|
| An artifact (draft, diff, design) | independent critique *of it* | **Judge** (one or a panel of judges) |
| An open problem, no committed answer | independent attempts, then merge | **Independent ensemble** |
| Several candidate outputs | a principled pick or ranking | **LLM-as-judge panel** |
| A decision blocked by disagreement | the strongest case on each side surfaced | **Debate / deliberation** |
| A problem needing multiple angles | coverage by distinct expertises or stances | **Persona / role panel** |
| A hard problem and budget to spend | proposers' candidates synthesized in layers | **Mixture-of-Agents (MoA)** |
| One strong member and a checker | catch errors the producer would miss | **Generator + verifier** (asymmetric) |

These compose. A common stack is *ensemble (propose) → judge panel (rank) → orchestrator (synthesize)*.

### 3. Aggregation — how outputs become one result

The output type dictates the rule. Pick deliberately; the wrong rule silently discards signal. Details and caveats in `references/aggregation.md`.

- **Discrete answer/label** → majority or plurality vote; weighted vote when members differ in reliability.
- **Numeric scores (judge panels)** → median or trimmed mean (robust to one miscalibrated judge), not bare mean. Aggregate **per criterion** when judges score multiple dimensions.
- **Structured findings (review/judge panels)** → **findings merge**: union the findings across judges, dedupe, keep the highest severity assigned to each, and treat a finding only one judge raised as a lead to verify, not as outvoted. The common shape for two- or three-judge code review.
- **Rankings** → Borda count, or Condorcet/pairwise when you need a robust winner.
- **Free text** → orchestrator **synthesis** (merge), **select-best** (pick one verbatim, avoids averaged mush), or **extract-and-union** (when completeness beats a single voice).

Always decide three cross-cutting things: how **abstention** is handled (let unsure members opt out rather than add noise), whether **disagreement itself is the output** (high variance often means "genuinely ambiguous — route to a human"), and the **even-count tiebreak** (a designated tiebreaker member, or fall to the chair).

### 4. Staff — assign families and models to members

Diversity is the only reason a panel beats one member. Spend a fixed **diversity budget** in this priority order (strongest decorrelation first):

1. **Cross-family** (Claude ↔ Codex) — different pretraining and tooling, the least-correlated errors. Spend here first.
2. **Cross-model within a family** (a heavier vs. a cheaper model in the same family) — real capability spread, but shared lineage means **correlated blind spots remain**. Worth less than it looks on niche topics.
3. **Cross-prompt / persona / seed on one model** — cheapest, weakest. Use to round out coverage, not as your primary diversity.

A panel of three same-family-same-model members with reworded prompts is mostly theater: they fail together, and a vote over correlated members manufactures false confidence. If you can afford only two members, make them cross-family before you make them cross-model.

### 5. Bound

Before dispatching, fix and state: **member count** (smallest N that resolves the blocker — usually 3, rarely >5), **per-member call cap** (members answer once; debate rounds are explicit and ≤2), **cost ceiling** (preview Codex spend with the free dry-runs), and the **stop condition** (you stop when you can act, not when you feel certain).

## Running the panel

The orchestrator is the **chair**: it selects (steps 1–5), dispatches members, gathers outputs, applies the aggregation rule, and writes the synthesis. Members do not talk to each other unless the pattern is Debate.

**Invocation by family** (full recipes, parameters, and parallel fan-out in `references/invocation.md`):

- **Claude members** → one subagent per member, each with its **model set to that member's slug** (a heavyweight model for a hard seat, a cheaper one for a throwaway seat). Hand each a **neutral task prompt** — never another member's output (except in Judge/Debate, where reacting is the point) — plus the return contract for its output type (see `references/invocation.md`).
- **Codex members** → the `codex-in-claude` tools, choosing by artifact: `codex_consult` for a design/question (read-only), `codex_review_changes` for judging a diff, `codex_delegate` for producing an implementation diff. Set `model` to the chosen slug (discover valid slugs via `codex_models`). For an N-member fan-out, use the **`*_async` variants** so members run concurrently — each returns a `job_id`; poll `codex_job_status` / `codex_job_result` and honor `poll_after_ms`.
- **The chair as a member** → the orchestrator may also contribute one attempt, but only if it **commits that attempt before reading any other member's output**. Otherwise it is a judge, not a peer, and the panel silently collapses to Judge.

**Dispatch in parallel.** Spawn all Claude subagents and kick off all Codex async jobs in the same turn, then gather. Serial dispatch wastes the main latency advantage of a panel.

### Independence and safety

These hold for every panel; the skill states them so it stands alone:

- **Preserve independence.** Ensemble/panel members get the same neutral task statement you started from — not your draft, reasoning, or workspace files containing it. Members reacting to your work are judges, not peers (that's the Judge pattern — call it that).
- **False agreement is weak evidence.** Members reasoning from your framing can share your blind spot; agreement is the *absence of a caught error*, not confirmation. Disagreement is the useful signal — it localizes where to check.
- **Verify, don't tally.** A confident-but-wrong claim survives a vote count; it does not survive running the test. Check each load-bearing finding against the actual code or design before you commit.

**Codex member safety (inlined — applies whenever a member is a Codex tool):**

- **Clean baseline for independence.** `codex_consult` reads the resolved workspace *in place* and `codex_delegate` seeds its worktree from your tracked state, so an independent Codex member must run from a **clean baseline** — stash your draft, or commit it on a branch and switch back — or your attempt leaks and the member silently degrades to a judge. (If `deliberating-with-codex` is installed, it documents the exact leak paths.)
- **Read-only calls are static.** `codex_consult` / `codex_review_changes` run sandboxed read-only: a "this breaks X" finding was *not* validated by running X. Reproduce it yourself.
- **Egress and redaction.** Your inputs are sent to OpenAI raw; redaction is defense-in-depth, not a guarantee. Scope `paths`/`question`/`extra_context` to what the decision needs.
- **`delegate` is contained.** It only ever writes inside a throwaway worktree and never applies to your tree.

### Synthesis

The chair holds the synthesis; members carry no verdict (a `codex_review_changes` Judge returns a `verdict`/`confidence`, but that is signal toward your decision, not the decision). Name the consensus, name the disagreements and why you resolved each as you did, and record what you verified. Then **decide and stop** — do not convene another pattern to feel more certain.

## Hard bounds (at a glance)

- Single member is the default; a panel is gated; a third+ member needs a tie/split/coverage gap to justify it. A below-gate panel runs only on the user's informed reaffirmation and is reported as low-signal, never as rigor.
- Members answer **once**; debate rounds are explicit and **≤2 total**; no member is called in a loop.
- Diversity budget spends **cross-family first**, then cross-model, then cross-prompt.
- Independence is mandatory for ensembles/panels: neutral prompts, clean Codex baseline.
- Findings and verdicts are claims to verify, not tallies to count. Agreement is weak; disagreement is the signal.
- Aggregate by the rule that matches the output type; handle abstention and even-count ties explicitly.

## References

- `references/patterns.md` — the pattern catalog: when each fits, member layout, and a worked example each.
- `references/aggregation.md` — the aggregation menu in detail, with calibration, abstention, and tiebreak handling.
- `references/invocation.md` — concrete member-invocation recipes (Claude subagents, Codex tools), the member return contract, parallel fan-out, and per-family model selection.
