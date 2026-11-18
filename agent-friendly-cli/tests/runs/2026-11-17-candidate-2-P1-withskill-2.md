# Probe P1 — with-skill arm 2 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 67,631 (final-turn context plus output, read from the transcript)
- **Output words:** 534
- **Transcript sha256:** `bc00e5b054911f207290e980635488ad311a8061cefea637d4ffe5d44b3bacef` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/P1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | Retry only if it reports a terminal "not created". Parts: empty lookup not proof of non-commit = pass; retry-added key not offered as making retry safe = pass; retries justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload

Exit code `7`.
In machine mode this is the only content on stderr, and stdout is empty.

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "reconcile_first": true,
  "request_id": "req_7f3a91c2",
  "details": {
    "operation": "note.create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key_supplied": false,
    "submitted": {"title": "T"},
    "search_index_lag_ms": 30000
  },
  "hint": "Do not retry automatically. The request may still commit. An empty search for this title does not show that the note was not created. Future create calls should pass --idempotency-key."
}
```

Why these values:

- `temporary: false`: a plain retry is not safe here.
  The create mutates state and has no idempotency key.
  The timeout leaves the outcome unknown, so a retry could create a duplicate note.
- `reconcile_first: true`: the caller has to resolve the unknown outcome before doing anything else.
- `request_id`: this is the only handle on the original attempt.
  Any status lookup or support request needs it.
- `hint` describes the fix in words and flags.
  It contains no shell string built from the caller's title.

## Recovering

1. **Do not retry automatically.**
   Adding an idempotency key now does not help.
   A key first added on the retry cannot deduplicate the original attempt.
2. **Do not use `note search` / `list` to decide the note is missing.**
   The search index can lag writes by up to 30 s.
   The original request can also commit after your lookup returns.
   An empty result therefore proves nothing.
   A hit does confirm the note exists, though another note may share the title `T`.
3. **Reconcile against the original attempt.**
   - If notectl has a status command that reads the primary store by `request_id`, such as `notectl request get <request_id>`, use it.
     Retry only if it reports a terminal "not created".
   - If no such command exists, notectl cannot reconcile this attempt for you.
     Escalate to a human or the note's owner, giving them the `request_id`.
     As a best-effort check, search by title after the 30 s lag has passed.
     Treat a hit as "created".
     Treat a miss as "still unknown", not as "safe to create".
     If you then create the note anyway, accept that you may end up with a duplicate and clean it up afterward.
4. **From now on**, pass `--idempotency-key <stable-key>` on every `note create`.
   Reuse that same key if you retry after a timeout.
   With a key, a retry after a timeout is safe.

## Changes the tool owner should make (contract gaps)

- Add an `--idempotency-key` flag to `note create`.
  Declare it in the schema as the mechanism that makes retries safe.
- In `note create`'s error catalog, declare `TIMEOUT` (exit 7) as `retryable: false, reconcile_first: true` when no key is supplied.
  Declare it retryable when a key is supplied.
- Add a status lookup by `request_id` (or by idempotency key) that reads the primary store, not the lagging index.
- Expose `--timeout-ms` so callers can set the timeout instead of being stuck with a fixed 15 s.
- Declare the search index's eventual consistency (up to 30 s lag) in the schema for `note search`/`list`.
~~~~~~
