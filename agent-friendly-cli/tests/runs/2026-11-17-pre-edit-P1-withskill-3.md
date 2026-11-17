# Probe P1 — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 64,434 (final-turn context plus output, read from the transcript)
- **Output words:** 570
- **Transcript sha256:** `86c54e86619327b4a0a6d5e7e136d488007306fb31ec26013c9a9e74e4a30d4c` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note create --title T` timed out after 15 s.
> The caller passed no idempotency key.
> The API's search index lags writes by up to 30 s.
> Write the error payload and tell the caller how to recover.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **FAIL** | "No match after the lag window -> retry the create, this time with --idempotency-key <fresh-uuid>" -- retry rests on an eventually-consistent search, not an authoritative outcome or dedup covering the original. Parts: empty lookup not presented as proof of non-commit = pass; retry-added key not offered as making that retry safe = pass; every recommended retry justified by dedup covering original / authoritative terminal outcome / safe-repeat semantics, else withheld = fail |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload (stderr, machine mode, exit `7`; stdout empty)

```json
{
  "code": "TIMEOUT",
  "message": "Note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "details": {
    "operation": "note.create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key_supplied": false,
    "reconcile_first": true,
    "safe_to_retry_blindly": false,
    "search_index_lag_ms": 30000,
    "earliest_reliable_search_after_ms": 30000,
    "title": "T"
  },
  "hint": "Do not retry yet. Wait at least 30000 ms, then check for a note with --title \"T\" created after the attempt; retry only if none exists, and pass --idempotency-key on the retry.",
  "request_id": "req_…"
}
```

Why these values:

- `temporary: false` — the timeout itself may be transient, but an identical retry is not safe: with no idempotency key, a create that committed server-side would be duplicated. The per-command catalog entry is `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}`.
- `outcome: "unknown"` — a timed-out mutation has an unknown outcome; the payload must say so rather than imply failure.
- Index lag is exposed as structured data (`search_index_lag_ms`), so the caller does not have to parse the hint to learn that an immediate search can falsely report "not found".
- `hint` uses flag values, not a pre-built shell string containing the caller's title.
- If the server returned a note ID or request ID before the timeout, include it (`resource_id` / `request_id`); that enables a direct lookup that bypasses the search index.

## Recovery for the caller

1. **Do not retry immediately.** A blind retry may create a duplicate note.
2. **Reconcile before retrying:**
   - If the error carries a `resource_id` (or there is a by-ID/by-request lookup), use `notectl note get <id>` — it reads the primary store, not the lagging index, so the answer is reliable immediately.
   - Otherwise, wait until at least 30 s have passed since the create started (`earliest_reliable_search_after_ms`), then search, e.g. `notectl note list --filter title="T"` (restrict to notes created at or after the attempt's start time if supported).
     A "not found" earlier than 30 s is not evidence the create failed.
3. **Decide:**
   - Exactly one match created in the window → the create committed; use it, do not retry.
   - No match after the lag window → retry the create, this time with `--idempotency-key <fresh-uuid>`, and reuse that same key on any further retries.
   - Multiple matches (title is not unique, or a prior retry already happened) → do not delete or retry automatically; escalate with the IDs, since `T` alone cannot identify which note is yours.
4. **Going forward:** always pass `--idempotency-key` on `note create`; then a timeout becomes `retryable: true` for the same key and step 2 is unnecessary.

## Owner-side contract fixes (if you own `notectl`)

- Declare in the schema for `note create`: `reconciliation` (as above), the `TIMEOUT` catalog entry with `reconcile_first: true`, and the search consistency lag.
- Support `--idempotency-key` (and document that retry with the same key is safe), or `--if-not-exists` keyed on a unique field.
- Expose a caller-settable `--timeout-ms` instead of a fixed 15 s.
- Provide a read-your-writes lookup (by ID or by idempotency key, e.g. `notectl note get --idempotency-key K`) that does not depend on the search index.
- Return the client-generated request/note ID in the timeout error so reconciliation can skip the lag wait.
- Add tests for the timeout payload, its exit code `7`, and that retry with the same idempotency key does not duplicate.
~~~~~~
