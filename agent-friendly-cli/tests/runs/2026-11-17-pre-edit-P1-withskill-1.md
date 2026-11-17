# Probe P1 — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 64,517 (final-turn context plus output, read from the transcript)
- **Output words:** 597
- **Transcript sha256:** `4d497751172bdb3302313af513ac520e247990dafa823a7289142d566a5c93f5` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **FAIL** | "No match after the lag window: the create did not commit. Go to step 4." -- empty search treated as proof; retry justified only by a non-authoritative search, not a dedup guarantee covering the original or a terminal outcome. Parts: empty lookup not presented as proof of non-commit = fail; retry-added key not offered as making that retry safe = pass; every recommended retry justified by dedup covering original / authoritative terminal outcome / safe-repeat semantics, else withheld = fail |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

Audience is unclear, so this leads with what the caller can do now and lists the tool-side fixes after.

## Error payload

In machine mode this goes to stderr as the only stderr content (`single-error-object`), with empty stdout and exit `7`.

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "details": {
    "operation": "note create",
    "outcome": "unknown",
    "timeout_ms": 15000,
    "idempotency_key_supplied": false,
    "reconcile_first": true,
    "search_index_lag_ms": 30000,
    "reconcile_not_before": "2026-11-17T18:04:45Z",
    "submitted_at": "2026-11-17T18:04:15Z",
    "request_fields": {"--title": "T"}
  },
  "hint": "Do not retry yet. Wait until details.reconcile_not_before, look for a note with this title created at or after details.submitted_at, and create again only if none exists. Pass --idempotency-key on the retry.",
  "request_id": "req_7f3a9c"
}
```

Why each choice was made:

- `temporary: false`. The same call is not safe to repeat. With no idempotency key, a blind retry can create a second note if the first one was committed. Per the checklist, `temporary` is what decides retries, not exit `7`.
- `details.outcome: "unknown"` and `reconcile_first: true`. A mutation that times out has an unknown outcome, so the caller must reconcile before retrying.
- `details.search_index_lag_ms` and `reconcile_not_before`. A search run right away can miss a note that was committed, because the index lags writes by up to 30 s. An empty search during that window is not evidence that the create failed. `reconcile_not_before` is `submitted_at` plus the lag, in UTC.
- `request_id`. It lets the owner trace the request on the server.
- The `hint` uses flag names, not a shell string built from the caller's title, so it is shell-safe.

## How the caller recovers

1. Do not rerun `note create` right away.
2. Wait until `details.reconcile_not_before` (at least 30 s after submission).
3. Look for the note with something like `notectl note find --title "T" --created-after <submitted_at> --machine`. Titles are not unique, so filtering by creation time is what separates this attempt from older notes titled `T`.
   - One match: the create committed. Use that note's ID and stop.
   - No match after the lag window: the create did not commit. Go to step 4.
   - More than one match created after `submitted_at`: an earlier blind retry, or another caller, already made a duplicate. Escalate or delete the extras on purpose. Do not create another note.
4. Retry with a key you generate: `notectl note create --title "T" --idempotency-key <uuid> --timeout-ms 30000 --machine`. Reuse the same key if this attempt also times out, which makes the next retry safe without searching again.

There is one limit you can't get around. The original call had no key, so no key passed now can deduplicate it. Only the step 3 lookup can tell you whether that attempt committed.

## Fixes for the tool owner

- Generate an idempotency key on the client when the caller doesn't pass one. Return it in `details.idempotency_key` on timeout, and accept it on retry. A timed-out create then becomes safe to retry.
- Add a read-after-write lookup that skips the search index, such as `note get --idempotency-key <key>` or `note get --request-id <id>`. Then reconciling doesn't have to wait out the 30 s index lag.
- Declare this in the schema's per-command error catalog: `{"code": "TIMEOUT", "exit": 7, "retryable": false, "reconcile_first": true}`. Add a `reconciliation` field describing the steps above.
- Expose `--timeout-ms` with a declared default of 15000, and declare `retry_defaults: {"retries": 0}` for `note create`.
- Declare the signal semantics: if the process is interrupted or times out, the server-side create may still complete.
~~~~~~
