# Probe P1 — with-skill arm 3 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 61,203 (final-turn context plus output, read from the transcript)
- **Output words:** 580
- **Transcript sha256:** `b87d3c90dfe5373f0da951f33cb1dd3a487cd1f884580829c65b9df1e40b442d` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/P1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | No match does not prove it failed. Parts: empty lookup not proof of non-commit = pass; retry-added key not offered as making retry safe = pass; retries justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload

Exit code `7` (timeout).
In machine mode this object is the only stderr content, and stdout is empty.

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
    "safe_to_retry": false,
    "search_index_lag_ms": 30000,
    "reconcile_with": {"command": "note search", "match_field": "title", "match_value": "T"}
  },
  "hint": "Do not re-run note create automatically. Look for a note titled T with note search, waiting at least 30000 ms after the timeout. A match means the create committed. No match does not prove it failed.",
  "request_id": "req_…"
}
```

Why these fields have these values:

- `temporary: false`. A create with no idempotency key is not safe to retry automatically. A blind retry can make a duplicate note. `temporary` decides retries, not the exit code, so it is `false` even though timeouts are often retryable.
- `reconcile_first: true`. The outcome is unknown. The request may have committed, or may still commit after the CLI gave up.
- `outcome: "unknown"` and `idempotency_key_supplied: false` give the caller the exact reason in fields it can branch on, so it does not have to parse the prose.
- `hint` expresses the repair as a command name plus field values. It does not build a shell string from the caller's title.
- `request_id` lets the owner or support look up the original attempt on the server side, if the API offers that.

## How the caller should recover

1. **Do not retry `note create` automatically.** Adding an idempotency key now does not help: a key used for the first time on the retry cannot deduplicate the original attempt.
2. **Reconcile.** Wait at least 30 s after the timeout because of the index lag, then search for a note titled `T`.
   - **Match found** (and it fits the expected creation time and content): the create committed. Use that note's ID and stop.
   - **More than one match**: titles are not unique, so pick by creation time or content. If it is still ambiguous, escalate.
   - **No match**: the outcome is **still unknown**, not "failed". The search can lag beyond its usual bound, and the original request can commit after the search returns. Re-run the search once or twice over a longer window. If there is still no match, choose explicitly:
     - if a duplicate note is acceptable, or easy to detect and delete later, create it again **with an idempotency key** and record that you knowingly accepted the duplicate risk; or
     - if duplicates are not acceptable, stop and escalate to a human or the tool owner, with the `request_id`.
3. **Next time, pass an idempotency key on the first attempt** and reuse that same key on any retry. Then retrying after a timeout is safe and needs no search.

## Owner-side fixes (so this error stops needing a judgment call)

- Generate an idempotency key client-side when the caller does not supply one, and print it in the error (`details.idempotency_key`), so the caller can retry with the same key.
- Or return a server-assigned operation or request ID before the deadline and add a status command (for example `notectl op get <id>`) that reports that attempt's final outcome from the primary store, not from the lagging index.
- Declare both in the per-command error catalog, plus `--timeout-ms`: `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}`.
~~~~~~
