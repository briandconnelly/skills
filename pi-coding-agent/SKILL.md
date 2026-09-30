---
name: pi-coding-agent
description: Use when answering questions about the Pi coding agent (pi.dev, npm @earendil-works/pi-coding-agent) or building for it — extensions and custom tools, commands, event hooks, Pi packages, skills, prompt templates, providers and virtual models, themes, TUI components, and MCP servers. Triggers on Pi feature questions, `.pi/` paths, `pi.registerTool` and other `pi.*` extension APIs, and `@earendil-works/*` imports. Answers cite version-matched docs when Pi is installed; build gates distinguish checked behavior from unchecked behavior. Not for Raspberry Pi, π, Claude Code or Codex extensions, or generic MCP server design.
---

# Pi coding agent

Pi ships version-matched docs with every install, and those docs are the only home of every Pi contract.
This skill finds them, covers remaining surface choices, and reports which parts of an artifact were checked.
`<skill-dir>` below is this skill's directory.

## Rules for every Pi task

1. Run `uv run <skill-dir>/scripts/pi_docs.py where` first.
2. Run this skill's other scripts with `uv run <skill-dir>/scripts/<name>.py` from your working directory.
3. If Pi is installed, state its version in your answer.
4. If `where` reports that the skill was verified against a different version, tell the user "this skill was verified against Pi vA; vB is installed" and continue.
5. If no Pi is installed, follow **No installed Pi** instead of **Answer mode** or **Build mode**.
6. Never answer Pi facts from memory or from this skill's text.
7. When Pi is installed, source Pi facts from its docs, changelog, or bundled examples, except for the hosted fallback in **Answer mode**, steps 6–7.
8. When you cannot find a feature in the documentation you read, name the pages checked before saying it was not found or is not supported.
9. Name changed context or configuration files without a gate kind as unchecked by the gate when reporting completion, including when the task also changes a gated artifact.

## No installed Pi

1. Navigate from https://pi.dev/docs/latest and follow links to the relevant pages.
2. Cite every Pi fact with its hosted page URL.
3. Label the answer as not from an installed version.
4. Report build work as not verified.

## Answer mode

1. Navigate from `pi_docs.py index`, which lists every page with its sections, including `index.md` and the quickstart chooser; follow links from each relevant page.
2. Use `pi_docs.py grep <terms>` to find terms, not as the navigation path.
3. Find every home of the feature: when the answer spans layers (CLI flag, config file, extension API), present each layer with its precedence and when to use it.
4. Cite installed facts as `docs/<page>.md#<section>` with the installed version.
5. When you cannot find the feature, report the absence in accordance with **Rules for every Pi task**, step 8, including the installed version.
6. Only after step 5, consult `pi_docs.py changelog <term>` and https://pi.dev/docs/latest.
7. Cite hosted findings with their page URLs and label them as not from the installed version.

## Build mode

1. Choose the surface with Pi's own chooser, docs/quickstart.md#choose-how-to-customize-pi, and, where it is silent, `references/choosing-a-surface.md`.
2. Read the installed contract page for that surface and the nearest bundled example (`pi_docs.py grep <term>` searches `examples/` headers).
3. If the change consists only of context or configuration files without a gate kind, follow **Configuration-only mode** instead of the remaining steps below.
4. Write the artifact's gate file next to it before calling the work done; copy the shape for its surface from `references/gate-recipes.md`.
5. Run `uv run <skill-dir>/scripts/pi_gate.py --self-test` once per session; a gate result counts only after a passing self-test in the same session.
6. Run `uv run <skill-dir>/scripts/pi_gate.py <artifact>` and show the user the full report.
7. Report the work as verified only for the checks the report lists as PASS.
8. Name every UNCHECKED item from the report to the user; never call the work done without that list.
9. Tell the user the gate isolates what Pi reads and writes, not what the artifact's code does: the code runs with the user's own filesystem and network permissions and is not sandboxed (docs/security.md#choose-how-to-run-pi).
10. If `pi_gate.py` reports that Pi is not installed, follow **No installed Pi**.
11. If a check fails with `gate-environment`, `pi-shape`, or `gate-dependency`, follow [Gate failure recovery](MAINTAINING.md#gate-failure-recovery).
12. For other failures, fix the artifact or its gate file and rerun the gate.
13. Never edit the report or skip a failing check.

## Configuration-only mode

Context and configuration files such as `AGENTS.md`, `SYSTEM.md`, `APPEND_SYSTEM.md`, `settings.json`, and `models.json` have no gate kind.
`mcp.json` has the `mcp-config` kind described in `references/gate-recipes.md`.

### Rules

1. Report changed files according to **Rules for every Pi task**, step 9.
2. Do not create a gate file or run the gate self-test or artifact gate for this branch.

## What the gate does

`pi_gate.py` runs Pi with discovery off, a throwaway agent directory, and credentials removed from its environment, and points Pi's HTTP proxy at a dead port, so Pi's own model requests cannot reach a real provider.
The artifact's code is not held to that: it can open its own connections (Build mode, step 9).
For RPC surfaces, it loads the artifact, then a harness that registers a scripted faux model, and runs a one-step turn (Tier 1) and the turns scripted in the gate file (Tier 2).
Theme checks validate the installed schema; MCP configuration checks validate original server entries with Pi's own validator before listing a copy with every server disabled.
Assertion coverage and limits are documented in [gate.json recipes, Fields](references/gate-recipes.md#fields).
It lists every check as PASS, FAIL (with a named reason), or UNCHECKED, and fails if anything under the real `~/.pi/agent` changed during the run.

## Maintenance

`MAINTAINING.md` holds the update procedure for a new Pi release; `verified-against` records the Pi version the skill was last fully checked against.
