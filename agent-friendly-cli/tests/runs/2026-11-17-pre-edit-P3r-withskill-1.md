# Probe P3 (amended fixture) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `2d8c6c1` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 58,320 (final-turn context plus output, read from the transcript)
- **Output words:** 243
- **Transcript sha256:** `9aca4e8f48c904fda7cc0b875a99049e211f6dd7aa41fe904f9023ee4aec7b59` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P3r-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** the help text names the schema command and the machine flag. | **PASS** | The machine-readable contract is `widgetctl schema` / run every command with --machine Parts: names schema command = pass; names machine flag = pass |

## Verbatim final output

~~~~~~markdown
```text
Usage: widgetctl [GLOBAL FLAGS] <command> [ARGS]

Agents: run every command with --machine (non-interactive, structured output only).
The machine-readable contract is `widgetctl schema`; it is authoritative over this text.
`widget delete` mutates; every other command is read-only.

Commands:
  schema [--fingerprint]   Print this contract as JSON (read-only).
                           --fingerprint prints only its cache key; re-fetch the schema when it changes.
  widget list              List widgets, paginated (read-only).
  widget get <id>          Show one widget by id (read-only).
  widget delete <id>       Delete one widget by id. MUTATES: removes the widget.

Global flags:
  --machine                Non-interactive machine mode: structured output only.
                           Canonical machine profile.
  --isolated               Ignore ambient config, credentials, and caches.
                           Separate from --machine; it does not imply it.

Examples:
  widgetctl --machine schema --fingerprint
  widgetctl --machine widget list
  widgetctl --machine widget get "<id>"
```

Notes on what I left out of the help text, because the schema doesn't say:

- **Shell safety:** I left out `--` end-of-options and a delete example because the schema doesn't declare `--` support.
- **Delete safety:** I left out `--dry-run`, `--yes` and `--if-exists` for `delete`. None are declared, so the help cannot say how to run it safely.
- **Errors, output and paging:** I left out exit codes, error codes, output classes, pagination flags (`--limit`, cursors) and timeouts. None are in the schema.
- **Ambient state:** the schema doesn't say what `--isolated` disables in detail, so the help only restates its description.

Each gap belongs in the schema first, and then in the help text.
~~~~~~
