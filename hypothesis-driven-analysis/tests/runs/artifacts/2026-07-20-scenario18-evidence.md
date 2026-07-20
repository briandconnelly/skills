# Scenario 18 — transcript evidence (both arms), 2026-07-20

Archived at scoring time because the subagent transcripts are harness scratch under
`/private/tmp/.../tasks/<agentId>.output` and expire. This file is the auditable record; the
inline run narrative lives in `tests/scenarios.md` (S18 run A / run B).

## Method

Six fresh general-purpose subagents were dispatched with the S18 prompt and a neutral two-skill
catalog (the "analysis" data skill listed first, hypothesis-driven-analysis second), each free to
read whichever `SKILL.md` it chose. Activation was scored from each transcript by counting
`Read` tool_use records with the strict pattern `"file_path":"…/<skill>/SKILL.md"`.

**Instrument validation (known-positive):** the same grep returns non-zero for both skill files in
every rep (so a zero is a real zero, not a broken matcher). The contamination grep
(`"file_path":"…tests/(scenarios\.md|runs/)…"`) is the same instrument pointed at the forbidden
paths and returns 0 for all six — i.e. no subagent read the assertions or prior runs.

Note: a looser grep without the `"file_path":` key prefix over-counts (it also matches the path
echoed in tool results and in the dispatch prompt); the strict-key counts below supersede any
looser figure. Each rep read each skill exactly once.

## Per-rep scores

| Agent id | Arm | Model | A1 activate | A2 compose | HDA reads | analysis reads | contam | tools | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a28af567c2e54d832 | A (weak) | Sonnet | PASS | PASS | 1 | 1 | 0 | 13 | 73.7k |
| adf2984cf9b5608a9 | A (weak) | Sonnet | PASS | PASS | 1 | 1 | 0 | 14 | 70.8k |
| a92ed7c963ac7d6ed | A (weak) | Sonnet | PASS | PASS | 1 | 1 | 0 | 13 | 66.1k |
| a022ee5ce1d5716de | B (strong) | Opus 4.8 | PASS | PASS | 1 | 1 | 0 | 10 | 71.9k |
| a5c28546586f61856 | B (strong) | Opus 4.8 | PASS | PASS | 1 | 1 | 0 | 8 | 63.1k |
| a8cf1251cca87dd40 | B (strong) | Opus 4.8 | PASS | PASS | 1 | 1 | 0 | 7 | 59.6k |

Arm A used a passive analysis fixture and the non-trigger prompt "Figure out why" (weak displacement
pressure). Arm B used the committed assertive "analysis" fixture (self-declared default skill +
trigger verbs) and the committed prompt "Break it down and tell me what's driving it", on Opus 4.8
— the model of the observed failure. Reasoning effort ran at the subagent default, not the observed
High (the dispatch harness sets model but not effort); recorded as unreproduced, no directional
claim attached.

## Conclusion content (all six composed; representative points)

Every rep read the hypothesis skill, routed **full** PPDAC, and used the analysis skill only as the
data interface. Shared findings, all correct against the `s1-conversion` ground truth:

- The drop is a **composition/mix effect**: a new `/lp/summer-sale` landing page (~21% of week-2
  sessions, ~0.57% conversion) diluted the blended rate; existing pages held flat
  (`/home` 2.71%→2.68%, `/product` 3.93%→3.76%).
- **Counterfactual reweighting** recovers ~3.04% for week 2 vs week 1's 3.12% — ~86–109% of the
  0.60pp drop accounted for, no unexamined residual.
- The **06-10 deploy is refuted on timing** (the drop begins 06-08, before the deploy).
- **Device mix refuted** as a driver — one Opus rep named it a Simpson's-paradox artifact of the
  campaign mix.
- Most reps additionally caught the **`checkout_reached` weekend under-logging** validity trap
  unprompted; one tied it to the 06-12 logging deploy.

## Verdict

6/6 GREEN, **no RED observed**. The observed real-session failure (both skills loaded, model uses
only the data skill, answers as a lookup) did not reproduce out-of-harness. Six greens only loosely
bound a stochastic deferral rate. Consequences and the "unvalidated, plausible-locus" status of the
Routing note and the 2026-07-20 description edit are recorded in `tests/scenarios.md` (S18). S18
still scores a free read-choice, not the both-bodies-loaded condition of the corrected diagnosis; a
redesign that injects both bodies upfront is owed.
