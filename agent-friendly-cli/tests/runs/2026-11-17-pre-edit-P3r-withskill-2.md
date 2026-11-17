# Probe P3 (amended fixture) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `2d8c6c1` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 58,311 (final-turn context plus output, read from the transcript)
- **Output words:** 248
- **Transcript sha256:** `824fd9e31e769ff43bb4f988eaaf22fd50ec2299ea03646d6f3e247c8a888088` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Here is the schema for `widgetctl`.
> Write the output of `widgetctl --help`.
>
> ```json
> {
>   "schema_version": "1.0",
>   "canonical_machine_profile": ["--machine"],
>   "global_flags": [
>     {"name": "--machine", "type": "boolean", "description": "non-interactive machine mode: structured output only"},
>     {"name": "--isolated", "type": "boolean", "description": "ignore ambient config, credentials, and caches"}
>   ],
>   "command_tree": {
>     "schema": "widgetctl schema [--fingerprint]",
>     "widget": {
>       "list": "widgetctl widget list",
>       "get": "widgetctl widget get <id>",
>       "delete": "widgetctl widget delete <id>"
>     }
>   },
>   "commands": [
>     {"canonical_invocation_path": "widgetctl schema", "summary": "print this contract as JSON; --fingerprint prints only its cache key", "read_only": true},
>     {"canonical_invocation_path": "widgetctl widget list", "summary": "list widgets, paginated", "read_only": true},
>     {"canonical_invocation_path": "widgetctl widget get <id>", "summary": "show one widget by id", "read_only": true},
>     {"canonical_invocation_path": "widgetctl widget delete <id>", "summary": "delete one widget by id", "read_only": false}
>   ]
> }
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/P3r.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P3r-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** the help text names the schema command and the machine flag. | **PASS** | Run `widgetctl schema` for the full / pass --machine on every call Parts: names schema command = pass; names machine flag = pass |

## Verbatim final output

~~~~~~markdown
# `widgetctl --help`

```text
Usage: widgetctl [--machine] [--isolated] <command> [args]

Agents: pass --machine on every call. Run `widgetctl schema` for the full
machine-readable contract; it governs where this text and it disagree.

Global flags:
  --machine     Non-interactive machine mode: structured output only.
                The canonical machine profile.
  --isolated    Ignore ambient config, credentials, and caches.
                Separate from --machine; not implied by it.

Commands:
  schema [--fingerprint]   Print this contract as JSON. Read-only.
                           --fingerprint prints only its cache key; re-fetch
                           the schema when the key changes.
  widget list              List widgets, paginated. Read-only.
  widget get <id>          Show one widget by id. Read-only.
  widget delete <id>       Delete one widget by id. MUTATING.

Run `widgetctl <command> --help` for command details.
```

## Notes

The help text states only what the schema declares, ordered rules first (machine profile, schema authority, read-only vs mutating) and context after.
I did not invent flags, defaults, exit codes, or pagination parameters the schema does not contain.

Gaps in the schema that the help cannot honestly fill (per the contract checklist):

- `widget delete` has no `--dry-run`, confirmation trigger, `--if-exists`, or reconciliation path declared.
- No output classes, output shapes, error catalog, or exit codes are declared.
- `widget list` pagination has no declared flags (`--limit`, cursor) or `has_more`/`next_cursor` contract.
- No stdin contract, `--` end-of-options support, timeouts, latency class, or ambient-state sources (which config/env/credentials `--isolated` disables).
- No `fingerprint` / `fingerprint_scope` or compatibility promise for `schema_version`.
- The per-command `--help` line assumes subcommand help exists; drop it if it does not.
~~~~~~
