# Probe P3 (amended fixture) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `2d8c6c1` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 1/1 scored
- **Tokens:** 52,668 (final-turn context plus output, read from the transcript)
- **Output words:** 199
- **Transcript sha256:** `d7d151cc1d2a946dfc2c19a6b4ab3a0bd42f8457c02ee8f2c15fdb78a37a5b26` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/P3r-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | **Passes when** the help text names the schema command and the machine flag. | **PASS** | For the full machine-readable contract, run `widgetctl schema`. / pass --machine on every call Parts: names schema command = pass; names machine flag = pass |

## Verbatim final output

~~~~~~markdown
```text
Usage: widgetctl [--machine] [--isolated] <command> [args]

Agents: pass --machine on every call. It is the canonical machine profile:
non-interactive, structured output only.
`widgetctl widget delete` is the only command that changes state; all others are read-only.
For the full machine-readable contract, run `widgetctl schema`.

Global flags:
  --machine       Non-interactive machine mode: structured output only.
  --isolated      Ignore ambient config, credentials, and caches.

Commands:
  schema [--fingerprint]   Print this CLI's contract as JSON (read-only).
                           --fingerprint prints only its cache key; compare it
                           to a cached copy before re-fetching the full schema.
  widget list              List widgets, paginated (read-only).
  widget get <id>          Show one widget by id (read-only).
  widget delete <id>       Delete one widget by id. MUTATES STATE.

Examples:
  widgetctl --machine schema --fingerprint
  widgetctl --machine widget list
  widgetctl --machine widget get <id>
```

Notes:
- The text lists binding constraints first (always pass `--machine`, which command changes state, where the contract lives) and then gives the details, per the Prose Surfaces rule.
- I used only what the schema states. It does not declare pagination flags, output classes, exit codes, or a dry-run or confirmation flag for `delete`, so the help says nothing about them. Add those to the schema first, then to `--help`.
~~~~~~
