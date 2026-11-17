# Probe P1 — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 57,425 (final-turn context plus output, read from the transcript)
- **Output words:** 589
- **Transcript sha256:** `7e5e7bf57834dfa40e74a2bfd38577794c2d895898ad33f59a46734128b5a035` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **FAIL** | "No match after the wait: the create did not commit; retry." -- empty search presented as proof and used to justify retry. Parts: empty lookup not presented as proof of non-commit = fail; retry-added key not offered as making that retry safe = pass; every recommended retry justified by dedup covering original / authoritative terminal outcome / safe-repeat semantics, else withheld = fail |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## What happened

The create timed out after 15 s with no idempotency key, so the outcome is unknown: the note may or may not have been committed.
A blind retry can create a duplicate note.
The search index lags writes by up to 30 s, so a search that returns nothing right after the timeout does not prove the create failed.

## Error payload

In machine mode, this is the only content on stderr, stdout is empty, and the exit code is `7` (timeout).

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "details": {
    "operation": "note create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key": null,
    "reconcile_first": true,
    "search_index_lag_ms": 30000,
    "title": "T"
  },
  "request_id": "<request id sent to the API>",
  "hint": "Do not retry blindly. Wait at least 30 s for the search index, then run `notectl note list --title T --machine`; if exactly one matching note was created after the original request, use it; if none, retry with --idempotency-key <new key>."
}
```

Why the fields are set this way:

- `temporary: false`: a plain retry is not safe, because the create may have committed and no idempotency key protects it.
  The catalog entry for `note create` should declare `TIMEOUT` with `"retryable": false, "reconcile_first": true`.
- `details.outcome: "unknown"` and `reconcile_first: true` let an agent branch without parsing the message.
- `details.search_index_lag_ms` tells the caller that a lookup through search needs a wait first.
- `request_id` lets the owner check server logs if reconciliation stays ambiguous.

## How the caller recovers

1. Do not rerun the same command right away.
2. Wait at least 30 s after the timed-out request so the search index has caught up.
   A search within that window can miss a note that was created, which would lead to a duplicate.
3. Look up notes titled `T` created at or after the original request time.
   - Exactly one match: the create succeeded; use that note's ID and stop.
   - No match after the wait: the create did not commit; retry.
   - More than one match, or a match that might be an older note with the same title: stop and escalate rather than guess.
4. When you retry, pass an idempotency key (for example `--idempotency-key <uuid>`) and reuse that key on every later retry of the same create, so further timeouts are safe to retry without reconciling.
5. Pass a longer `--timeout-ms` on the retry if the API is slow.

If the API offers a strongly consistent lookup that does not go through search (for example a get by a client-chosen ID or by idempotency key), use it instead of the 30 s wait.

## Tool-side fixes for the `notectl` owner

- Declare the reconciliation path for `note create` in the schema: on `TIMEOUT` the outcome is unknown, reconcile before retrying, and say how.
- Accept `--idempotency-key` on `note create`, and consider generating one automatically and returning it in the error's `details` so the caller can retry safely even when it did not pass one.
- Provide a lookup that does not depend on the lagging search index, such as `notectl note get --idempotency-key K`, so reconciliation does not need a 30 s wait.
- Expose a caller-settable `--timeout-ms` and declare the 15 s default and the retry behaviour in the schema.
- Declare the search index lag in the schema so agents know search results can be up to 30 s stale.
~~~~~~
