---
name: pi-coding-agent
description: Use when answering questions about the Pi coding agent (pi.dev, npm @earendil-works/pi-coding-agent) or building for it — extensions and custom tools, commands, event hooks, Pi packages, skills, prompt templates, providers and virtual models, themes, TUI components, and MCP servers. Triggers on Pi feature questions, `.pi/` paths, `pi.registerTool` and other `pi.*` extension APIs, and `@earendil-works/*` imports. Answers are cited from the installed Pi's own docs, and built artifacts are proven by a gate that loads them in an isolated Pi and runs a scripted faux-model turn. Not for Raspberry Pi, π, Claude Code or Codex extensions, or generic MCP server design.
---

# Pi coding agent

Pi ships version-matched docs with every install, and those docs are the only home of every Pi contract.
This skill finds them, covers the two choices they leave unmade, and proves what you build loads and runs.
`<skill-dir>` below is this skill's directory; run its scripts from any working directory with `uv run <skill-dir>/scripts/<name>.py`.

## Rules for every Pi task

1. Run `uv run <skill-dir>/scripts/pi_docs.py where` first and state the installed Pi version in your answer.
2. If `where` reports that the skill was verified against a different version, tell the user "this skill was verified against Pi vA; vB is installed" and continue.
3. If no Pi is installed, answer from https://pi.dev/docs/latest, label every answer as not from an installed version, and report build work as not verified.
4. Never answer from memory or from this skill's text; every Pi fact comes from the installed docs, changelog, or bundled examples.

## Answer mode

1. Navigate from `pi_docs.py index`, which lists every page with its sections, including `index.md` and the quickstart chooser; follow links from each relevant page.
2. Use `pi_docs.py grep <terms>` to find terms, not as the navigation path.
3. Find every home of the feature: when the answer spans layers (CLI flag, config file, extension API), present each layer with its precedence and when to use it.
4. Cite each fact as `docs/<page>.md#<section>` with the installed version.
5. When you cannot find the feature, say "I could not find this in the installed vX.Y.Z docs after checking <the pages you read>"; never say "not supported" without that list.
6. Only after step 5, consult `pi_docs.py changelog <term>` and https://pi.dev/docs/latest, and label anything found there as not the installed version.

## Build mode

1. Choose the surface with Pi's own chooser, docs/quickstart.md#choose-how-to-customize-pi, and, where it is silent, `references/choosing-a-surface.md`.
2. Read the installed contract page for that surface and the nearest bundled example (`pi_docs.py grep <term>` searches `examples/` headers).
3. Write the artifact's `gate.json` next to it before calling the work done; copy the shape for its surface from `references/gate-recipes.md`.
4. Run `uv run <skill-dir>/scripts/pi_gate.py --self-test` once per session; a gate result counts only after a passing self-test in the same session.
5. Run `uv run <skill-dir>/scripts/pi_gate.py <artifact>` and show the user the full report.
6. Report the work as verified only for the checks the report lists as PASS.
7. Name every UNCHECKED item from the report to the user; never call the work done without that list.
8. Tell the user the gate isolates what Pi reads and writes, not what the artifact's code does: the code runs with the user's own filesystem and network permissions and is not sandboxed (docs/security.md#choose-how-to-run-pi).

If `pi_gate.py` reports that Pi is not installed, say the build work is not verified.
If a check fails, fix the artifact or its `gate.json` and rerun the gate; do not edit the report or skip the failing check.

## What the gate does

`pi_gate.py` runs Pi with discovery off, a throwaway agent directory, and no network access for Pi itself.
It loads the artifact, then a harness that registers a scripted faux model, and runs a one-step turn (Tier 1) and the turns scripted in `gate.json` (Tier 2).
It lists every check as PASS, FAIL (with a named reason), or UNCHECKED, and fails if anything under the real `~/.pi/agent` changed during the run.

## Maintenance

`MAINTAINING.md` holds the update procedure for a new Pi release; `verified-against` records the Pi version the skill was last fully checked against.
