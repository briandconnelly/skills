# Probe P1 — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 57,228 (final-turn context plus output, read from the transcript)
- **Output words:** 523
- **Transcript sha256:** `f4de810279a8abb57b31d59bee94d4d550adaee6d3d9300b57360d729929c8be` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | Found none: the create most likely did not commit, but this is inferred from a lagging index, not established. Retry only if a duplicate is acceptable or a human confirms Parts: empty lookup not proof = pass; retry-added key not offered as making retry safe = pass; recommended retries justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload (stdout in machine mode, exit 7)

```json
{
  "error": {
    "code": "TIMEOUT",
    "message": "note create did not complete within 15000 ms; the note may or may not have been created.",
    "temporary": false,
    "reconcile_first": true,
    "hint": "Do not re-run note create automatically. The original attempt had no idempotency key, and search lags writes by up to 30 s, so neither a retry nor an immediate search is safe.",
    "details": {
      "outcome": "unknown",
      "operation": "note create",
      "timeout_ms": 15000,
      "idempotency_key_supplied": false,
      "search_index_lag_ms_max": 30000,
      "title": "T"
    },
    "request_id": "<server request id, if one was assigned before the timeout>"
  }
}
```

Why these values:

- `temporary: false` — the payload's `temporary` field is authoritative for retry decisions, and a blind retry here can create a duplicate note.
- `reconcile_first: true` — the outcome is unknown; the caller must reconcile before any retry.
- Exit `7` (timeout) is the shell fallback; agents branch on `code`.
- `details` carries the machine-usable facts (no key, lag bound) rather than leaving them only in `hint` prose.
- `request_id` is included only if the server assigned one; it is the one handle that could identify this attempt.

## Telling the caller how to recover

The outcome is unknown, and none of the three things that make a retry safe exist for this attempt:

1. **No idempotency key on the original attempt.** Adding `--idempotency-key` on the retry does not deduplicate the first attempt — it only protects attempts from now on.
2. **No status command for this attempt** (unless `notectl` can look up by `request_id`; if it can, that is the recovery: query it and act on its terminal outcome).
3. **`note create` is not repeat-safe** (no `--if-not-exists`).

A search by title does not prove the note was not created, because the index lags writes by up to 30 s.

Recommended caller procedure:

1. Do not retry automatically.
2. If a `request_id` is present and a status/get-by-request command exists, use it; it is authoritative.
3. Otherwise, wait more than 30 s (the declared lag bound, plus margin), then search for title `T`.
   - Found exactly one matching note created around the attempt time: treat the create as committed; do not retry.
   - Found none: the create most likely did not commit, but this is inferred from a lagging index, not established. Retry only if a duplicate is acceptable or a human confirms; when retrying, pass a new idempotency key so *that* attempt is reconcilable.
   - Found several / ambiguous: stop and escalate to a human.

## Owner-side fixes (so the next timeout is recoverable)

- Accept `--idempotency-key` on `note create` and show it in canonical examples, so a caller can reuse the key on retry.
- Return a `request_id` or note id early and provide a status command that reports that attempt's terminal outcome from the primary store (not search).
- Optionally add `--if-not-exists` keyed on a caller-chosen external id.
- Declare in the schema: `note create` is not safe to retry automatically; catalog entry `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}`; expose `--timeout-ms` so callers can set the deadline.
~~~~~~
