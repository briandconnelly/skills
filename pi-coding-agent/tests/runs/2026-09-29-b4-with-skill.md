# B4 with-skill, 2026-09-29

Prompt: "Add a line to my system prompt telling Pi to always answer in British English."
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) chooses a file layer and says why | pass | `APPEND_SYSTEM.md`, cites configuration.md |
| (b) no extension | pass |  |
| (c) does not replace the whole prompt | pass |  |

Finding against the skill: the agent ran `pi_gate.py` on `APPEND_SYSTEM.md` and got `FAIL no-gate`, because the gate has no kind for configuration files; SKILL.md build-mode rule 3 asks for a `gate.json` for every artifact. The agent reported this honestly and did not fake a gate file.

## Transcript (the agent's final report, verbatim)

I added the line, but it is not verified: I never ran Pi with the new file, and the gate has no check for this kind of file.

**What I did.** I created `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b4-with-skill/pi-agent/APPEND_SYSTEM.md` containing `Always answer in British English.` Installed Pi 0.99.1 documents this file as the user-level way to add instructions to Pi's system prompt while keeping Pi's own prompt (docs/configuration.md, "Agent directory" table). The alternative, `SYSTEM.md`, replaces Pi's prompt entirely, so I didn't use it.

**Precedence.** A trusted project `.pi/APPEND_SYSTEM.md` takes precedence over this file. The two are not combined (docs/configuration.md#project-pi-directory). I only created the agent-directory file.

**Verification.** The skill's gate self-test passed, but the gate has no kind for a prompt-instruction file. Its supported kinds are extension, package, skill, prompt, theme and mcp-config. Pointing it at the file returned `FAIL no-gate`, because there is no gate file and no recipe applies. That is not a defect in the file. I did not write a fake `gate.json` to get a pass. Nothing here shows Pi actually loads the file or that the model follows it.

**Commands run** (all `pi_docs.py` and `pi_gate.py` calls went through `uv run`):
1. Read `SKILL.md`.
2. `pi_docs.py where`: Pi 0.99.1 installed at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`, and the skill was verified against 0.99.1, so no version mismatch. The `PI_CODING_AGENT_DIR` export was in this shell command.
3. `pi_docs.py grep system prompt`: about 48KB of output, too broad to use as navigation.
4. `pi_docs.py index | head -80`, then `grep -rli "SYSTEM.md|APPEND_SYSTEM"` over the docs: only `configuration.md` and `security.md` mention them.
5. `grep -n -i -B2 -A6 "SYSTEM.md|APPEND_SYSTEM" configuration.md`: gave the table rows and the precedence sentence above.
6. `grep` in `references/gate-recipes.md` and `references/choosing-a-surface.md`: `choosing-a-surface.md` says to choose `APPEND_SYSTEM.md` to add Pi-specific instructions, and `gate-recipes.md` has no prompt-file recipe.
7. `printf 'Always answer in British English.\n' > pi-agent/APPEND_SYSTEM.md && cat pi-agent/APPEND_SYSTEM.md`: printed the line.
8. `pi_gate.py --self-test`: `RESULT self-test PASS (Pi 0.99.1)`.
9. `pi_gate.py <path to APPEND_SYSTEM.md>`: `FAIL [tier -] no-gate: no gate file at .../APPEND_SYSTEM.gate.json`. It also reported `RESULT FAIL: 1 failed, 0 passed, 0 unchecked`.

**UNCHECKED.**
- That Pi loads `APPEND_SYSTEM.md` from this agent directory.
- That the model then answers in British English.

Checking those would need a real model turn.

**Note.** The gate isolates what Pi reads and writes, not what an artifact's code does. That doesn't matter here, since this file is plain text.
