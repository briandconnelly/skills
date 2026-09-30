# B1 with-skill, 2026-09-29

Prompt: "Add a Pi tool that returns the current git branch and whether the working tree is dirty."
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) extension tool | pass | `git-status.ts` registers `git_status` |
| (b) self-test run and shown | pass | command 4: 7 PASS, `RESULT self-test PASS` |
| (c) Tier 1 and Tier 2 run and shown | pass | command 8: 8 PASS incl. three scripted tool results |
| (d) names unchecked items | pass | late registration, detached HEAD, live model |
| (e) real agent directory unchanged | pass | hash diff after batch empty |

Finding against the skill: `toolResults[].contains` is matched against the JSON-encoded result, so an expected string containing a newline never matches (the agent worked around it).

## Transcript (the agent's final report, verbatim)

**Final answer to user**

I added a Pi extension tool, `git_status`, at `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b1-with-skill/git-status.ts`. Its gate file is `git-status.gate.json` in the same directory. The tool takes no arguments and runs `git branch --show-current` and `git status --porcelain` in the session cwd. It returns `branch: <name>` and `dirty: true|false`, with `details {branch, dirty}`. On a detached HEAD it reports `(detached HEAD at <sha>)`. Outside a git repo it throws, so the result is an error. It is annotated `readOnlyHint`.

Installed Pi is 0.99.1, which matches the version the skill was verified against. I chose an extension tool from `docs/quickstart.md#choose-how-to-customize-pi` ("Add executable tools, commands, or event handlers"). The contract is in `docs/extensions.md#tools`. The model is `examples/extensions/hello.ts` and `dirty-repo-guard.ts`, which uses `pi.exec`. Citations are from the installed docs.

Verified by the gate, which passed after a passing self-test in the same session (8 PASS, 0 FAIL, 1 UNCHECKED):
- The extension loads with no `extension_error`.
- `git_status` is registered with exposure `direct`.
- In a scripted faux-model turn the gate's work directory is not a git repo, so the first call returned an error containing "not a git repository".
- The scripted turn then ran `git init` on branch `gate-branch` through the `bash` tool. The next call returned `branch: gate-branch`, `dirty: false`.
- After `touch dirty.txt`, the third call returned `dirty: true`.

UNCHECKED: late registration (resources registered after a run settles) is not observed.

Two limits on what the gate covers:
- The gate isolates what Pi reads and writes, not what the extension's code does. The extension runs with your own filesystem and network permissions and is not sandboxed (`docs/security.md#choose-how-to-run-pi`).
- Only the error and the two `dirty` states have an assertion of their own in the gate file. The gate's `contains` check matches the JSON-escaped text, so a multi-line match like `branch: X\ndirty: false` fails. The gate file therefore asserts the `dirty:` lines. The `branch: gate-branch` output appears in the gate report but has no assertion of its own.
- The detached-HEAD path was not exercised.
- I did not run the tool in a live Pi session with a real model.

**Commands run, with key output**

1. `uv run <skill-dir>/scripts/pi_docs.py where` (with `PI_CODING_AGENT_DIR` exported first)
   - Output: "Pi 0.99.1 at /opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent … Skill verified against 0.99.1 (matches installed)".
2. `pi_docs.py index`
   - Listed all doc pages and sections.
3. Reads of `docs/quickstart.md#choose-how-to-customize-pi`, `references/choosing-a-surface.md`, `references/gate-recipes.md`, `docs/extensions.md` (create/load, lifecycle, tools, exposure), and `examples/extensions/hello.ts`.
   - Also read `pi_docs.py grep exec`, `grep pi.exec` over the bundled examples, and `tests/fixtures/gate/tool/word-count.ts`.
4. `pi_gate.py --self-test`
   - Output: 7 PASS lines, then `RESULT self-test PASS (Pi 0.99.1)`.
   - The trailing `====` in my compound command was a zsh parse error, so the first gate run in that command never executed.
5. `pi_gate.py git-status.ts` (first gate run, gate file with only the single scripted call)
   - RESULT FAIL, 1 failed. `git_status returned isError=True … fatal: not a git repository`, because the gate's work directory is not a git repo. The tool behaved correctly.
6. `pi_gate.py git-status.ts` after rewriting the gate script to run `git init` through `bash` first.
   - RESULT FAIL, 2 failed. The tool output was correct (`branch: gate-branch\ndirty: false`), but my `contains` strings with `\n` did not match the escaped text.
7. `pi_gate.py git-status.ts` after switching to single-line `contains` strings.
   - RESULT FAIL, 2 failed. This was my own bug: I had left an extra expectation entry that no tool call matched.
8. `pi_gate.py git-status.ts` after removing the extra expectation entry.
   - RESULT: `PASS: 0 failed, 8 passed, 1 unchecked`.
   - The 8 PASS lines are: load, tool registered with exposure `direct`, target loaded, physical models, script consumed (all 6 steps), and three tool results (the error, `dirty: false`, `dirty: true`).
   - The UNCHECKED line is late registration.
   - The NOTE line is the sandboxing caveat.

Two of the edits above used `python3` to rewrite the JSON gate file in place. I created no files outside `b1-with-skill`.
