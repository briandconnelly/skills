# Trigger Set for agent-friendly-cli

## What this measures

A frontmatter-only selection proxy.
An arm sees skill names and descriptions and says which it would load; no skill is actually loaded.
Results support claims about the description text and none about runtime triggering in any harness.

## How to run

1. Generate the catalog at run time: the `name` and `description` frontmatter of every `*/SKILL.md` in this repository, extracted by a script, never hand-copied.
2. Give a fresh arm the catalog and one prompt below, and ask: "Which of these skills, if any, would you load before responding? Answer with the skill names, or `none`."
   The arm is told the catalog and the prompt are its only input and it must not read any file.
3. Three arms per prompt.
   A prompt **fires** in an arm when the answer includes `agent-friendly-cli`.
4. Record the fired count per prompt in the Results table, and the catalog's sha256.

## Should fire

1. "Design a CLI for our deploy service that Claude Code will call from CI."
2. "Our agent parses the English error text from `acmectl` to decide whether to retry. How should the tool report errors instead?"
3. "Here is `foo --help`. Can an agent use this tool reliably?"
4. "Write a schema command for my CLI so agents can discover its flags."
5. "The pipeline hangs when the bot runs `dbtool migrate`; it seems to wait for input."
6. "Our internal CLI prints a banner before its JSON. Fix the output for automation."

## Should not fire

1. "Should this capability be an MCP server or a CLI?"
2. "Refactor the argument parsing in `cli.py` to use dataclasses; no behavior change."
3. "Design the Python SDK for our deploy service."
4. "Write a bash script that backs up my photos."
5. "Add a `--verbose` flag to `widgetctl list`, following its existing schema."
6. "Make the colors in our TUI dashboard easier to read."

Prompts 1 and 5 are **body-only exclusions**: the reason not to load is in `SKILL.md` § When Not To Use, not in the description.
A fire on either is recorded as a gap between the description and the body, separately from prompts 2, 3, 4, and 6.

## Preregistered reading

Recorded on 2026-11-17, before any arm ran.
Results are recorded only; a description edit is a separate change with its own measurement.
Open an issue if any of these holds:

- fewer than 5 of the 6 should-fire prompts fire in at least 2/3 arms
- 2 or more of should-not-fire prompts 2, 3, 4, and 6 fire in at least 2/3 arms
- either body-only exclusion fires in 3/3 arms

## Results

| Date | Tree | Catalog sha256 | Prompt | Fired | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 1 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 2 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 3 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 4 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 5 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should fire 6 | 3/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 1 | 3/3 | Body-only exclusion; every arm chose `agent-friendly-mcp` and `agent-friendly-cli` together. Meets the preregistered issue condition (a body-only exclusion firing in 3/3). |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 2 | 0/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 3 | 0/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 4 | 0/3 |  |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 5 | 0/3 | Body-only exclusion; did not fire. |
| 2026-11-17 | `b6958e0` | `78424ced0e80…` | should not fire 6 | 0/3 |  |

Full answers and the complete catalog hash: `runs/2026-11-17-pre-edit-triggers.md`.
