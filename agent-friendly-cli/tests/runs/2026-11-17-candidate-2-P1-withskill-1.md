# Probe P1 — with-skill arm 1 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 57,476 (final-turn context plus output, read from the transcript)
- **Output words:** 605
- **Transcript sha256:** `6599743eca22591a3e61283f13aeba2307ed5555ddba2acedc51723617d94e12` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/P1-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | If the search is empty, that proves nothing. Parts: empty lookup not proof of non-commit = pass; retry-added key not offered as making retry safe = pass; retries justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

Audience is unstated, so this leads with the caller-side recovery and then lists the tool-side fixes.

## Error payload

Exit code `7` (timeout). In machine mode stdout is empty and this object is the only thing on stderr.

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
    "idempotency_key": null,
    "request": {"title": "T"},
    "search_index_lag_ms_max": 30000,
    "retry_safe": false
  },
  "request_id": "req_…",
  "hint": "Do not re-run automatically. The original request may still commit. An empty search does not prove the note is missing. Reconcile first, and pass --idempotency-key on future creates."
}
```

Why these fields:

- `temporary: false`: a timeout can usually be retried, but not here. The create mutates state, the outcome is unknown, and the caller supplied no idempotency key. A blind retry can create a duplicate note.
- `reconcile_first: true`: the caller must reconcile before trying again. The command's error catalog declares `TIMEOUT` with `retryable: false` and `reconcile_first: true` to match.
- `details.outcome: "unknown"` and `details.idempotency_key: null` give the caller the reason as data, so it doesn't have to parse the prose in `hint`.
- `request_id` lets the owner or support trace whether the server committed the write.

## How the caller should recover

1. **Do not re-run the same command.** Adding `--idempotency-key` now won't help: a key that wasn't on the first attempt can't deduplicate it.
2. **A search can confirm the note exists but cannot confirm it doesn't.**
   - If `notectl note search --title T` (or similar) finds a matching note, adopt it and stop. Check that it is really this note, for example by its creation time, because titles may not be unique.
   - If the search is empty, that proves nothing. The index can lag writes by up to 30 s, and the original request can still commit after the search returns.
3. **When the search is empty, the CLI gives no safe automatic path.** It has no idempotency key on the first attempt, no status lookup for that attempt, and no if-not-exists semantics. Pick one of these:
   - Escalate to a human or the note's owner, giving them the `request_id`.
   - Re-create only if a duplicate note is acceptable. Do it with a fresh `--idempotency-key` and a longer `--timeout-ms`, then check again later for duplicates and remove any.
4. **Next time, prevent the problem.** Pass `--idempotency-key <uuid>` on every create, and reuse the same key on any retry. A timed-out create then becomes safe to retry.

## Tool-side fixes, in priority order

1. **Add `--idempotency-key` to `note create`.** Declare in the schema that re-running with the same key is safe after a timeout. With a key, the payload can then say `temporary: true` and `reconcile_first: false`.
2. **Add a status lookup that reads the primary store, not the search index.** For example `notectl note get --idempotency-key K` or `notectl request status <request_id>`. It should return that attempt's final outcome.
3. **Make `--timeout-ms` settable by the caller and declare its default (15000) in the schema.** A fixed network timeout is a contract gap.
4. **Declare the error catalog for `note create`.** It should list `TIMEOUT` (exit 7, `retryable: false`, `reconcile_first: true` when no key was given), a non-timeout transport-failure code such as `TRANSIENT` (exit 9, `reconcile_first: true`), and the rule for unknown codes (non-retryable).
5. **Document in the schema or `reconciliation` text that search is eventually consistent (lag up to 30 s).** Say that search results must not be used to prove a create did not commit.
~~~~~~
