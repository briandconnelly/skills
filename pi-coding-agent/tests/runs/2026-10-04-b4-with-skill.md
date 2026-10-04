# B4 with-skill, 2026-10-04

Prompt: "Add a line to my system prompt telling Pi to always answer in British English."
Agent: fresh Sonnet 5.5 subagent, Pi 1.0.1, skill at commit 12059d1, with the `tests/scenarios.md` preamble.
Closing line: "When you are done, give your final report."
The closing line used on 2026-09-29 is not recorded in this repository, so this line may differ from it.
Purpose: re-measure B4 after #190 added Configuration-only mode, which the 2026-09-29 run's finding against build-mode rule 3 prompted.
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) chooses a file layer and says why | pass | `APPEND_SYSTEM.md`, because `SYSTEM.md` would replace Pi's prompt; cites `docs/configuration.md`, "Agent directory" |
| (b) no extension | pass | the run directory holds only `pi-agent/APPEND_SYSTEM.md` |
| (c) does not replace the whole prompt | pass | same evidence as (a) |

Compared with 2026-09-29: the agent followed Configuration-only mode.
It did not run the gate against the file, wrote no `gate.json`, and reported the change as unchecked by the gate and unverified at runtime.
The earlier run had run the gate and got `FAIL no-gate`.

Checked by the scorer: the file contains the one line; the precedence claim matches docs/configuration.md line 39; the real `~/.pi/agent` hashes were unchanged after the run.
Not cited by the agent: the claim that a running session needs `/reload`. docs/slash-commands.md says `/reload` reloads "context files", and it does not say whether that includes `APPEND_SYSTEM.md`.

## Transcript (the agent's final report, verbatim)

Done. I added the line `Always answer in British English.` to `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b4-with-skill-2026-10-04/pi-agent/APPEND_SYSTEM.md`. The file didn't exist, so I created it. Pi's docs list this file as the user-level way to add instructions to the system prompt (`docs/configuration.md`, "Agent directory").

- **Version:** `pi_docs.py where` reported Pi 1.0.1, and the skill was verified against 1.0.1, so there is no version mismatch.
- **File choice:** I used `APPEND_SYSTEM.md` because `SYSTEM.md` would replace Pi's default prompt entirely. Pi's agent directory is whatever `PI_CODING_AGENT_DIR` points to, which here is the `pi-agent` directory.
- **Not checked:** `APPEND_SYSTEM.md` has no gate kind, so the skill's Configuration-only mode applies. I did not create a gate file or run the gate self-test or artifact gate. Nothing was run against Pi to confirm the line reaches the prompt, so the change is unchecked by the gate and unverified at runtime.
- **Precedence:** a trusted project `.pi/APPEND_SYSTEM.md` takes precedence over this agent-directory file, and the two files are not combined. Any project that has its own `.pi/APPEND_SYSTEM.md` will ignore this line.
- **Reload:** a running Pi session needs `/reload` to pick up the change.
- **Real install:** this change is in the eval directory's agent dir, not your real `~/.pi/agent`. To apply it for real, put the same line in `~/.pi/agent/APPEND_SYSTEM.md`.
