# Probe P1 — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 58,788 (final-turn context plus output, read from the transcript)
- **Output words:** 605
- **Transcript sha256:** `6bf09c84fdca3018153b713ecdceb32c98d9dbb45d77e7f935a06466d7c670bc` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P1.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P1-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** all three hold: - It does not present an empty lookup as proof the create did not commit. - It does not offer a key first added on the retry as making that retry safe. - Every retry it recommends is justified by a deduplication guarantee covering the original attempt, an authoritative terminal outcome, or declared safe-repeat semantics; otherwise it withholds automatic retry. | **PASS** | Treat this as a deliberate choice to accept duplicate risk, not as a safe retry. Parts: empty lookup not proof = pass; retry-added key not offered as safe = pass; every retry justified or automatic retry withheld = pass |

## Verbatim final output

~~~~~~markdown
# `notectl note create` timeout: error payload and recovery

## Error payload

Exit code `7` (timeout). In machine mode this JSON object is the only content on stderr, and stdout is empty.

```json
{
  "code": "TIMEOUT",
  "message": "Note creation timed out after 15000 ms; the note may or may not have been created.",
  "temporary": false,
  "reconcile_first": true,
  "request_id": "req_8f2c1a",
  "details": {
    "command": "note create",
    "timeout_ms": 15000,
    "outcome": "unknown",
    "idempotency_key": null,
    "search_index_lag_ms": 30000
  },
  "hint": "Do not retry automatically. The original request carried no idempotency key, so a retry can create a duplicate note. Reconcile first; pass --idempotency-key on future create calls."
}
```

Why these values:

- `temporary: false`: the payload's `temporary` field is what decides retries, not exit `7`. A blind retry is not safe here, because the mutation's outcome is unknown and nothing makes a retry repeat-safe.
- `reconcile_first: true`: the caller has to work out what happened before doing anything else. The command's error catalog should declare `TIMEOUT` with `retryable: false, reconcile_first: true`.
- `details.outcome: "unknown"`: a timeout means the CLI stopped waiting. It does not mean the server rejected the write. The request may still commit after this error is returned.
- `request_id`: gives the caller and the owner a handle for checking server-side logs.
- `hint` describes the repair in words and flag names. It contains no shell string built from caller input such as the title.

## How the caller should recover

1. **Do not retry automatically.** None of the three things that make a retry safe is present:
   - The original attempt carried no idempotency key. Adding a key on the retry does not deduplicate the original attempt.
   - There is no status command that can report a terminal outcome for this specific attempt.
   - `note create` is not repeat-safe. Two creates with title `T` produce two notes.
2. **Do not treat an empty search as proof of absence.** Search can lag writes by up to 30 s, and the original request may still commit after the search returns. So `notectl note search --title T` returning nothing does **not** show the create failed.
   A *positive* result settles it: if a search finds a note titled `T` created at the time of the attempt, the create committed. Use that note and do not retry.
3. **If the result is still unresolved**, choose by how much a duplicate costs:
   - If a duplicate is harmful, stop and escalate to a human or the owner. Include the `request_id` so the server side can confirm whether the write landed.
   - If a duplicate is acceptable, retry once with a fresh `--idempotency-key`, then check later (after more than 30 s) for duplicates titled `T` and delete the extra one. Treat this as a deliberate choice to accept duplicate risk, not as a safe retry.
4. **Next time**, always pass `--idempotency-key <uuid>` on `note create`, and reuse the same key on any retry within the service's deduplication window. With a key, a retry after a timeout is safe.

## Tool-side fixes for the `notectl` owner

- Add `--idempotency-key` to `note create`, or document it in the schema if it already exists, and use it in the canonical examples.
- Add a way to look up an attempt's status by `request_id` or idempotency key, reading the primary store and not the lagging index, so callers can reconcile without guessing.
- Declare `note create` as not safe to retry automatically when no key was supplied, and declare `TIMEOUT` with `reconcile_first: true` in its error catalog.
- Make sure `--timeout-ms` is settable by the caller and declared, so the fixed 15 s is not the only option.
~~~~~~
