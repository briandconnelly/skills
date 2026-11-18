# Probe P1 — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 65,260 (final-turn context plus output, read from the transcript)
- **Output words:** 563
- **Transcript sha256:** `5b84227f7a4162cbc514c9e95cbc7d523aebcc2313d570b96c8fef2bbd8a90c7` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note create --title T` timed out after 15 s.
> The caller passed no idempotency key.
> The API's search index lags writes by up to 30 s.
> Write the error payload and tell the caller how to recover.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **FAIL** | Found none → reasonably safe to create again, this time with an idempotency key — retry justified only by an empty lagging lookup, not dedup of original, terminal outcome, or safe-repeat semantics Parts: empty lookup not proof = pass; retry-added key not offered as making retry safe = pass; recommended retries justified or automatic retry withheld = fail |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload (machine-mode stderr, exit 7, empty stdout)

```json
{
  "code": "TIMEOUT",
  "message": "Note creation timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "reconcile_first": true,
  "details": {
    "outcome": "unknown",
    "timeout_ms": 15000,
    "idempotency_key_supplied": false,
    "safe_to_retry_automatically": false,
    "search_index_lag_ms_max": 30000,
    "attempted": {"command": "note create", "title": "T"}
  },
  "hint": "Do not retry automatically. Reconcile first: wait at least 30000 ms, then list notes with title T and confirm the count before deciding to create again. On future calls, supply an idempotency key.",
  "request_id": "req_…"
}
```

Why these values:

- `temporary: false` — a blind retry is not safe, so the payload must not signal retryability (the payload's `temporary` is authoritative; exit 7 alone does not mean retry).
- `reconcile_first: true` — the outcome is unknown; the request may have committed server-side after the client gave up.
- `details.outcome: "unknown"` and the structured fields carry the repair data so the agent does not parse `message` or `hint`.
- The `hint` names the repair as flags/values, not a shell string built from the caller's title.
- `request_id` (if the API returned or the client generated one) lets the owner check server logs.

## How the caller should recover

1. **Do not retry now.** With no idempotency key on the original attempt, a retry — even one that adds a key now — cannot deduplicate the first attempt and may create a duplicate note.
2. **Do not treat an immediate search miss as "not created."** The search index lags writes by up to 30 s, so a lookup now proves nothing.
3. **Reconcile:**
   - Preferred: if notectl has a primary-store read or a status command for the request (e.g. by `request_id`), use that — it is authoritative.
   - Otherwise wait ≥ 30 s past the timeout, then search/list notes by title `T` (and creation time near the attempt).
     - Found exactly one → the create committed; use that note's ID. Done.
     - Found none → reasonably safe to create again, this time **with an idempotency key**, and reuse that same key on any further retry.
     - Found more than one, or titles aren't unique → stop and escalate to a human/owner; title alone can't identify which is yours.
   - Note: even after 30 s, a search miss is best-effort evidence, not proof (the 30 s is the stated bound, not a guarantee). If duplicates are costly, prefer a primary-store read.
4. **Going forward:** always pass an idempotency key on `note create` and reuse it on retries; then a `TIMEOUT` becomes safely retryable with the same key.

## Owner-side contract fixes (notectl)

- Catalog entry for `note create`: `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}`; declare that the outcome is unknown after a timeout and that the search lag means a lookup does not establish non-commit.
- Declare what makes a retry safe: the idempotency-key flag (supplied on the original attempt and reused), and ideally a primary-store `note get`/status-by-request-id command that is not subject to index lag.
- Consider making the CLI generate and report an idempotency key on every create (echoed in the error `details`), so even a caller who forgot one can retry safely with it.
- Expose `--timeout-ms` so callers can set a longer deadline, and declare signal/interrupt semantics (remote creation may still commit after the process dies).
~~~~~~
