# Probe P1 — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 0/1 scored
- **Tokens:** 57,719 (final-turn context plus output, read from the transcript)
- **Output words:** 535
- **Transcript sha256:** `736af65692dee8c2d4b9efbc3d78d05e025c32be1e0178174e6cfc0e010cdbf5` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/P1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **FAIL** | Only if none is found after the lag window, retry — recommended retry rests on a search miss, not a dedup guarantee, authoritative outcome, or safe-repeat semantics Parts: empty lookup not proof = pass; retry-added key not offered as making retry safe = pass; recommended retries justified or automatic retry withheld = fail |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

Audience is unstated, so this leads with the payload and caller-side recovery, then owner-side fixes.

## Error payload

JSON on stderr, empty stdout, exit `7` (timeout).

```json
{
  "code": "TIMEOUT",
  "message": "note create timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "reconcile_first": true,
  "hint": "Do not retry automatically. The outcome is unknown and no idempotency key was sent, so a retry may create a duplicate note. Search cannot prove the note is absent: the index lags writes by up to 30 s.",
  "details": {
    "outcome": "unknown",
    "operation": "note create",
    "timeout_ms": 15000,
    "idempotency_key": null,
    "retry_safe": false,
    "lookup_lag_ms": 30000,
    "inputs": {"title": "T"}
  },
  "request_id": "<request id if the client generated one>"
}
```

Why `temporary: false` even though timeouts are often retryable: per the contract checklist (§ Mutations And Long-Running Work), a mutation that times out has an unknown outcome, and with no caller-supplied idempotency key, no status command for the attempt, and no repeat-safe semantics, it is declared not safe to retry automatically.
`temporary` is the authoritative retry signal, so it must be `false` here; `reconcile_first: true` says what to do instead.

## How the caller should recover

1. Do not blindly re-run `notectl note create --title T`.
2. Do not treat an empty search as proof the note was not created; the index lags up to 30 s, so "not found" is uninformative within that window — and even after it, search is only evidence, not proof, unless the API documents a bound.
3. Reconcile with a read that hits the primary store if one exists (e.g., `note get <id>` or listing by creation time from a non-indexed endpoint); if not, wait at least 30 s past the timeout and search for title `T` with a creation time inside the attempt window.
4. If a matching note exists, adopt it as the result. If several exist, report duplicates rather than deleting automatically.
5. Only if none is found after the lag window, retry — and this time pass an idempotency key, reusing it on any further retries. Note that a key first added on the retry does not deduplicate the original attempt; it only protects the retries after it.
6. If titles are not unique enough to reconcile with confidence, escalate to a human rather than guess.

Going forward: always pass an idempotency key on the first attempt of `note create`, so a timed-out attempt can be retried safely with the same key.

## Tool-side fixes (for the notectl owner)

- Declare `TIMEOUT` in `note create`'s error catalog with `retryable: false, reconcile_first: true` unless a key was supplied; when the caller supplied a key, the payload can say `temporary: true` and the hint can say "retry with the same key".
- Support an idempotency key flag (e.g., `--idempotency-key`) and echo it in `details` on errors.
- Return a request/operation ID and offer a status command that reports that attempt's terminal outcome, so reconciliation does not depend on the lagging search index.
- Expose a caller-settable `--timeout-ms` and declare retry defaults.
- Declare in the schema that search/list are eventually consistent (up to 30 s) and cannot confirm absence.
~~~~~~
