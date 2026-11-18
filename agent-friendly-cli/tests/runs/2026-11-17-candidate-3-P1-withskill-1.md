# Probe P1 — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 61,039 (final-turn context plus output, read from the transcript)
- **Output words:** 567
- **Transcript sha256:** `d67d8b62c099302116c9eaf7775a64cc6fadd107edaa46c129bddd03d3e9f205` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | An empty search is not evidence of absence. Parts: empty lookup not proof = pass; retry-added key not offered as safe = pass; every retry justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

Audience is unclear, so this leads with what the caller does now, then what the tool should change.

## Error payload

Machine mode, `single-error-object` stderr framing, empty stdout, exit `7`:

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": true,
  "reconcile_first": true,
  "details": {
    "operation": "note.create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key_supplied": false,
    "safe_to_retry_automatically": false,
    "search_index_lag_ms_max": 30000
  },
  "hint": "Do not re-run note create automatically. Reconcile against the primary store before deciding to retry.",
  "request_id": "<request id from the API, if one was assigned>"
}
```

Notes on the fields:

- `temporary: true` says the timeout condition itself may clear; `reconcile_first: true` says the caller must not retry before reconciling. Both are needed — `temporary` alone would invite a blind retry.
- `outcome: "unknown"`: a timed-out mutation may have committed, and it can still commit after the CLI gives up.
- `request_id` is the best reconciliation handle when the API returned one before the timeout; omit the field otherwise rather than emitting null.
- The per-command catalog entry should read `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}` — the create has no idempotency key and no repeat-safe semantics, so it is not safe to retry automatically.

## How the caller recovers (now)

None of the three things that make a retry safe are available for this attempt:

1. No idempotency key was passed on the original call. Adding one on the retry does **not** deduplicate the original attempt.
2. A search/list for title `T` does **not** prove the note wasn't created: the index lags writes by up to 30 s, and the original request may still commit after your lookup returns. An empty search is not evidence of absence.
3. `note create` has no declared repeat-safe mode (e.g. `--if-not-exists`).

So:

- If a `request_id` was returned, check the attempt's status against the primary store (a status/get command that reads the primary, not the search index). A terminal "no effect" result there makes a retry safe.
- Otherwise, a positive search hit for `T` (after waiting past the 30 s lag) confirms creation — use that note, don't create another. A miss is inconclusive.
- If you still can't establish the outcome, choose explicitly: accept a possible duplicate (retry, then dedupe by title/content later), or escalate to a human. Don't retry silently in a loop.
- Next time, pass an idempotency key on the **first** attempt and reuse it on retries within the service's deduplication window; then a timeout becomes safely retryable.

## Tool-side fixes (owner)

- Accept an idempotency key on `note create` (e.g. `--idempotency-key`), and declare the service's dedup window in the schema.
- Or support `--if-not-exists` keyed on a declared unique selector, so the create is repeat-safe.
- Return/emit a `request_id` early and provide a status command that reads the primary store, so a timed-out attempt can be reconciled without the lagging index.
- Expose `--timeout-ms` (caller-settable; the fixed 15 s is a contract gap if it isn't) and declare the schema's `reconciliation` text for `note create`: outcome unknown on timeout; search is eventually consistent and cannot prove absence; retry is safe only with a reused key, a primary-store "no effect" status, or `--if-not-exists`.
- Include a separate catalog code for non-timeout transport failures (e.g. `TRANSIENT`, exit `9`) with the same `reconcile_first: true`.
~~~~~~
