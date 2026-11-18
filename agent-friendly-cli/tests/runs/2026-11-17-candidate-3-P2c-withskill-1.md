# Probe P2c — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 62,073 (final-turn context plus output, read from the transcript)
- **Output words:** 944
- **Transcript sha256:** `1afb713174efcdd1686be9006521cf23390d439c4395602cf9534c7368d840c2` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> `notectl note delete <id>` has never prompted; the team wants deletes to stay one call.
> Specify the delete contract for agent callers.

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/P2c.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/P2c-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** it does not add a mandatory confirmation step. | **PASS** | **Stays one call, no prompt, no `--yes`.** |

## Verbatim final output

~~~~~~markdown
# `notectl note delete` — agent delete contract

Audience: tool author (your team owns notectl). Task: contract hardening of an existing command.
Assumption: notes live on a remote service reached over the network; if notectl is local-only, drop the network/timeout items marked (net).

## Decisions

1. **Stays one call, no prompt, no `--yes`.** The verb `delete` is itself the explicit action trigger the checklist requires (§ Mutations: "`create`, `apply`, `delete`, or `--yes`"). Adding a confirmation prompt or a required `--yes` would break existing callers and add nothing for agents. Declare in the schema that the command never prompts, in any mode, so callers can rely on it not hanging.
2. **Safety comes from `--dry-run` and `--if-exists`, not confirmation.**
   - `--dry-run`: resolves the id, checks permission, reports what would be deleted, mutates nothing.
   - `--if-exists`: makes delete repeat-safe — a missing note returns success with `deleted: false` instead of `NOTE_NOT_FOUND`. This is what makes automatic retry safe.
3. **Retry rule.** A delete that times out or is interrupted has an unknown outcome.
   - With `--if-exists`: safe to retry automatically.
   - Without it: not safe to retry blindly; a retry after a committed delete returns `NOTE_NOT_FOUND`, which the caller must not treat as failure of its intent. Catalog marks `TIMEOUT`/`NETWORK_ERROR` `reconcile_first: true` when `--if-exists` is absent.
   - An empty `note get`/`note list` right after does not prove the original attempt did not commit (it can lag or commit later); only `--if-exists` repeat-safety establishes safe retry.
4. **Selector:** one positional `<id>` (the only positional). Support `--` so ids starting with `-` are safe: `notectl note delete --machine -- "<id>"`.
5. **Single item only.** No bulk form in this contract; if added later (`--from-file`), it must declare a `bulk-result` alternate class, per-item results, stop-vs-continue, and aggregate exit code.

## Schema entry

```json
{
  "command": "note delete",
  "summary": "Permanently delete one note by id. Never prompts. Use --if-exists for retry-safe deletes; use --dry-run to preview.",
  "classification": "mutating",
  "interactive": false,
  "arguments": [
    {"name": "id", "type": "string", "required": true, "cardinality": 1, "positional": true,
     "description": "Note id as returned by note list/get/find."}
  ],
  "flags": [
    {"name": "--if-exists", "type": "boolean", "default": false,
     "description": "Succeed with deleted=false when the note does not exist. Makes the call repeat-safe."},
    {"name": "--dry-run", "type": "boolean", "default": false,
     "description": "Validate and report the planned delete; no mutation."},
    {"name": "--timeout-ms", "type": "integer", "unit": "ms", "default": 10000, "description": "(net) Request deadline."}
  ],
  "end_of_options": true,
  "stdin": {"read": false},
  "auth": "same credential sources as other note commands; requires write scope on the note",
  "side_effects": ["removes the note permanently (or: moves to trash — declare which)"],
  "latency_class": "network",
  "retry": {"automatic": false, "safe_to_retry": "only with --if-exists"},
  "output": {
    "class": "record",
    "format": "json",
    "streaming": false,
    "shape_dialect": "JSON Schema 2020-12",
    "shape": {
      "type": "object",
      "required": ["id", "deleted", "dry_run"],
      "properties": {
        "id": {"type": "string"},
        "deleted": {"type": "boolean", "description": "false only with --if-exists on a missing note, or with --dry-run"},
        "dry_run": {"type": "boolean"},
        "existed": {"type": "boolean"},
        "title": {"type": "string", "description": "present in dry-run output to confirm the target"}
      }
    },
    "examples": [
      {"id": "n_8f2a", "deleted": true, "dry_run": false, "existed": true},
      {"id": "n_8f2a", "deleted": false, "dry_run": false, "existed": false},
      {"id": "n_8f2a", "deleted": false, "dry_run": true, "existed": true, "title": "Q3 plan"}
    ],
    "flag_combination": "--dry-run with --if-exists: dry run on a missing note exits 0 with existed=false, deleted=false, dry_run=true."
  },
  "errors": [
    {"code": "NOTE_NOT_FOUND", "exit": 3, "suppressed_by": ["--if-exists"]},
    {"code": "INVALID_ARGUMENT", "exit": 2},
    {"code": "UNAUTHENTICATED", "exit": 4},
    {"code": "FORBIDDEN", "exit": 5},
    {"code": "RATE_LIMITED", "exit": 6, "retryable": true},
    {"code": "TIMEOUT", "exit": 7, "retryable": true, "reconcile_first": true,
     "description": "Outcome unknown. reconcile_first is false when --if-exists was passed."},
    {"code": "NETWORK_ERROR", "exit": 9, "retryable": true, "reconcile_first": true},
    {"code": "NOTE_LOCKED", "exit": 8, "description": "note is being edited / has a conflicting lock"},
    {"code": "INTERNAL", "exit": 1, "reconcile_first": true}
  ],
  "unknown_code_policy": "act on payload fields; reconcile before retry",
  "signals": "SIGINT/SIGTERM after the request is sent leaves the outcome unknown; the server may still complete the delete. No local state is written.",
  "closed_stdout": "finishes the delete; exit code still reports the outcome"
}
```

Error payload (stderr, `single-error-object` framing in machine mode, stdout empty):

```json
{"code": "NOTE_NOT_FOUND", "message": "Note n_8f2a not found.", "temporary": false,
 "resource_id": "n_8f2a", "hint": "Pass --if-exists to treat a missing note as success."}
```

`TIMEOUT` payloads carry `"temporary": true, "reconcile_first": true` (or `false` when `--if-exists` was set); `RATE_LIMITED` carries `retry_after_ms`.

## Checklist walk

- **Command Model:** `note delete <id>` is `noun verb`, one canonical op, one positional selector. OK.
- **Machine Schema:** entry above; tool-level schema/fingerprint/version rules apply unchanged — adding `--if-exists`/`--dry-run` is additive and must change the fingerprint.
- **Stdin:** not read. Declared.
- **Shell Safety:** `--` supported; `hint` gives a flag, not a shell string built from the id.
- **Agent-Safe Invocation:** never prompts regardless of TTY; `--timeout-ms` (net) exposed; retry behavior declared.
- **Output:** `record` class; `dry_run` field makes dry-run output distinguishable; stdout empty on failure; closed-stdout behavior declared.
- **Errors:** required fields, per-command catalog with `retryable`/`reconcile_first`/`suppressed_by`, fallback `INTERNAL`, transport code `NETWORK_ERROR`, unknown-code policy.
- **Ambient State:** inherits the tool-level declaration (credentials, profile/workspace selection); delete must honor the same `--isolated`/explicit-profile flags so an agent cannot delete in the wrong workspace via ambient config.
- **Mutations:** explicit verb trigger; `--dry-run`; `--if-exists` repeat-safety; unknown-outcome and retry rules; signal semantics. Open item for the team: declare whether delete is permanent or soft (trash) — this changes `side_effects` and whether a `note restore` exists.
- **Side Effects/Telemetry:** none beyond the delete.
- **Prose Surfaces:** summary leads with the binding facts (permanent, never prompts, retry flag).
- **Tests:** `note delete` never prompts with TTY stdin; exit codes 0/2/3/… observed match the catalog; `--if-exists` on missing id exits 0 with `deleted:false`; `--dry-run` mutates nothing and output differs from real output; `--` with a `-`-leading id; interrupted delete behavior; schema snapshot.
~~~~~~
