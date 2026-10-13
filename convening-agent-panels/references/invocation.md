# Member invocation

How to actually spin up each member, set its model, run the panel in parallel, and gather results. The chair (the orchestrating session) owns all of this. The **panel design is backend-neutral** — the seat definition, the return contract, and the gather/aggregate loop below hold for any runtime. Two concrete backends follow (in-runtime subagents and the Codex tools); adapt the mechanics to whatever your host actually provides. If the `codex-in-claude` plugin is installed, `collaborating-with-codex` carries the full Codex tool contract.

## A member is (family, model, role, prompt)

Define each seat before dispatch:

- **family** — the backend/architecture providing the member. In this setup the two available are `claude` (in-runtime subagents) and `codex`; the design does not assume only these.
- **model** — the slug for that seat (e.g. a heavyweight model for a hard seat, a cheaper one for a throwaway seat). Drives both cost and diversity.
- **role** — proposer / judge / verifier / refiner / debater (from the pattern).
- **prompt** — neutral task statement for ensemble/panel members; the artifact-plus-rubric for judges; the assigned position for debaters.

## The member return contract (set this before dispatch)

Aggregation is applied *mechanically*, so members must return *comparable* output — a free-form paragraph can't be voted or scored. Tell each member exactly what to return, keyed to the aggregation rule (step 3):

| Output type | Each member returns |
|---|---|
| Label / choice | the chosen label, verbatim from a fixed set, + one-line rationale |
| Score(s) | a number per rubric criterion on a stated scale, + evidence per score |
| Ranking | a full ordering of the candidates (ties allowed only if you said so) |
| Findings | a list, each with severity + location + evidence + recommendation |
| Free text | the answer itself, plus a one-line self-summary for the synthesizer |

Every member may also return **`abstain`** (with a reason) instead of guessing, and a **confidence** if (and only if) you'll actually use it. A member that errors or times out is a *missing seat*, not a vote — record it, because it changes the tiebreak math. **Codex's envelope maps in:** `codex_review_changes` returns `verdict`/`confidence`/`findings` (→ findings/label rows). `codex_consult` has a closed `summary` + `findings` schema with no score/ranking field, so for a label/score/ranking seat either require a **parseable convention on the first line of `summary`** (e.g. `LABEL: B`, `SCORES: {correctness: 4, clarity: 3}`, `RANKING: A > C > B`) and parse that, or don't staff `codex_consult` as a mechanical score/ranking seat — use `codex_review_changes` or a Claude subagent instead. Free prose in `summary` is not mechanically aggregatable.

## Claude members — in-runtime subagents with per-member model

Spawn one subagent per Claude member and **set that subagent's model to the seat's slug** (e.g. via the Agent/Task tool's model override). This is what makes intra-family panels real — a heavyweight seat and a cheaper seat are genuinely different members, not the same model twice. **Runtime assumption:** this requires a host that honors a per-subagent model override; if yours doesn't, intra-family diversity isn't available and you should lean cross-family.

- Give each subagent only its neutral prompt and the inputs the task needs — **not** another member's output, not the chair's draft, not a workspace path containing the chair's attempt. That is what keeps ensemble/panel members independent.
- Hand each the **return contract** for its output type (above) so its result is mechanically aggregatable.
- The **chair itself is a free Claude member** at the session's own model. It may take a seat, but only if it records its attempt *before* reading any other member — otherwise it is the judge, not a peer.

## Codex members — the codex-in-claude tools

Pick the tool by artifact, set `model` to the seat's slug, and prefer async for fan-out.

- `codex_consult(question, …)` — read-only second opinion / design or prose member.
- `codex_review_changes(scope, base, commit, paths, …)` — judge a diff; returns `verdict`/`confidence`/`findings`.
- `codex_delegate(task, …)` — produce an implementation member; lands a reviewable `diff` in a throwaway worktree, never applied.
- **Model selection.** Set `model` to a valid slug; discover slugs via `codex_models` (advisory catalog; the slug is pass-through, so an unlisted-but-valid slug still works). This is how you staff an intra-Codex panel (e.g. two Codex seats on different model versions).
- **Clean baseline.** `codex_consult` reads the resolved workspace in place; `codex_delegate` seeds its worktree from your tracked state. For an independent ensemble/panel member, run from a clean baseline (stash, or branch-and-switch back to the clean tree) so your own draft does not leak in. (If installed, `deliberating-with-codex` documents the exact leak paths.)

## Parallel fan-out

A panel's latency advantage comes from running members concurrently. Dispatch everything in one turn, then gather:

- **Claude seats** — spawn all subagents in the same turn.
- **Codex seats** — use the **`*_async` variants** (`codex_consult_async`, `codex_review_changes_async`, `codex_delegate_async`). Each returns a `job_id` immediately and commits to spend. Poll `codex_job_status` / `codex_job_result`, and **honor `poll_after_ms`** (it backs off as a job runs) rather than polling in a tight loop. Results are retained for `ttl_seconds` after completion.
- **Preview spend first.** The free `codex_dry_run` / `codex_delegate_dry_run` preview scope and size before any paid call; there is no consult dry-run, so scope `question`/`extra_context` manually.

## Gather → aggregate → synthesize

1. **Gather** every member's output (subagent returns + resolved Codex jobs). Note any member that failed or abstained — a missing seat changes the tiebreak math.
2. **Aggregate** by the rule chosen in step 3 (`aggregation.md`). Apply it mechanically; do not let a confident member override the rule informally.
3. **Verify the load-bearing findings** against the actual code or design before acting — a vote does not validate a claim.
4. **Synthesize**: name the consensus, name each disagreement and how you resolved it, record what you verified, then stop.

## Worked dispatch (propose → judge → synthesize)

1. Chair scopes the question and confirms the gate clears; sets diversity budget cross-family-first.
2. **Propose (parallel):** spawn two Claude subagents on different models on the neutral prompt; kick off `codex_consult_async` on the same neutral prompt. Three independent candidates.
3. **Judge (parallel):** spawn one cross-family judge per candidate (or one judge panel ranking all three), each with the shared rubric; cross-judge so no member grades its own output.
4. **Aggregate:** Borda over the judges' rankings; flag the criterion with highest inter-judge variance.
5. **Synthesize:** chair writes the winning answer, verifies the one contested point, records the split, and stops.

## Server-down fallback

If the `codex-in-claude` server is unreachable, Codex seats are unavailable. Either run a **Claude-only panel** (still real if it spans models) and note the lost cross-family diversity, or reconnect the server (`/mcp`, then `codex_status`). The raw `codex exec --sandbox read-only` fallback bypasses the plugin's redaction and bounding — see `collaborating-with-codex` before using it.
