# Probe P1 — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 62,072 (final-turn context plus output, read from the transcript)
- **Output words:** 592
- **Transcript sha256:** `e15041fefed29ba37137e6eb61e5442bd21461fb97163e5ee49d0668ff5b76ce` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P1-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | A key added only on the retry cannot match the original request, which had none. Parts: empty lookup not proof = pass; retry-added key not offered as safe = pass; every retry justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

Audience isn't stated, so this covers what the caller does now first, then what the tool should change.

## Error payload

Exit code `7` (timeout). In machine mode, stdout is empty and stderr holds only this object.

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "reconcile_first": true,
  "details": {
    "operation": "note.create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key_supplied": false,
    "safe_to_retry_automatically": false,
    "search_index_lag_ms": 30000,
    "requested": {"title": "T"}
  },
  "hint": "Do not retry automatically. Reconcile first: check whether a note titled T exists before creating another one. A search that finds nothing does not prove the note was not created.",
  "request_id": "<server request id, if one was assigned>"
}
```

Why the fields are set this way:

- `temporary: false`: timeouts are often retryable, but this create has nothing that makes a retry safe. The caller sent no idempotency key, there is no status command for the attempt, and a create cannot be repeated safely by design. A blind retry can create a second note.
- `reconcile_first: true`: the outcome is unknown, so the caller must find out what happened before acting.
- `hint` only describes the next step. It does not contain a shell command built from the title, because the title is caller input.
- `details.search_index_lag_ms`: this tells the caller that search results cannot be trusted right away.

## How the caller should recover

1. **Do not retry right away.** Adding an idempotency key now will not help. A key added only on the retry cannot match the original request, which had none.
2. **Look for the note.** If `request_id` is present and the API can look up a request's outcome, use that first, because it gives a definite answer. Otherwise wait at least 30 s after the timeout so the search index can catch up, then search for title `T`. If you know a read that goes to the primary store rather than the search index, use that instead.
3. **If the note is there, the create succeeded.** Use the existing note and do not create another.
4. **If nothing is found, you still don't know.** The index might still be behind, or the original request might commit after you checked. Choose one of these:
   - Hand the decision to the user or the owner of the workflow.
   - Retry only if a duplicate note is acceptable. Pass an idempotency key on the retry so any later retries are protected, then check for duplicate notes titled `T` afterward.
5. **To avoid this next time,** pass an idempotency key on every `note create` and reuse the same key on retries. A timeout then becomes safe to retry within the service's deduplication window.

## What the tool should change

- Generate an idempotency key automatically, or accept `--idempotency-key`, and include the key in the error's `details`. A caller can then retry with the same key and be sure the create happens only once.
- Add a status or get command that reads the primary store by request ID or idempotency key, so the caller does not have to rely on search, which lags.
- In the `note create` error catalog, declare `TIMEOUT` with exit `7`, `retryable: false` and `reconcile_first: true` when no key was sent. Also declare the signal behavior: whether the server keeps working on the create after the client gives up.
- Make sure `--timeout-ms` can be set by the caller, so 15 s is not a fixed limit.
~~~~~~
