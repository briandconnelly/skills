# Test Scenarios for pi-coding-agent

Behavioral scenarios for this skill, following the baseline/with-skill method used elsewhere in this repo (see `vega-lite/tests/scenarios.md`).
Run each scenario with a fresh subagent that does not have the skill (baseline), then with a fresh subagent that has it (with-skill), and score both against the scenario's criteria.
Give each agent only the preamble and the scenario prompt, plus the skill for the with-skill run; do not reveal the criteria, the expected baseline failures, or earlier outputs.

Every scenario's baseline result is reported, pass or fail.
A scenario the baseline passes is kept and labeled non-discriminating; it is not evidence of the skill's effect.
A scenario is revised only for ambiguity, never merely to make the baseline fail.
Gate self-tests are script tests (`tests/test_pi_gate.py`), not scenarios.

## How to run

1. Before the first run, archive the real agent directory: `tar -czf .eval-tmp/pi-agent-backup.tgz -C ~/.pi agent`, and record `find ~/.pi/agent -type f | sort | xargs shasum -a 256`.
2. Give every agent, in both arms, this preamble, with `<dir>` a fresh directory under `.eval-tmp/pi-scenarios/`:

   > Pi 0.99.1 is installed (`pi` on PATH).
   > Work only in `<dir>`.
   > In every shell command that runs `pi`, first run `export PI_CODING_AGENT_DIR=<dir>/pi-agent`.

3. Baseline: dispatch a subagent with the preamble and the prompt.
   With-skill: dispatch a fresh subagent with the preamble, the prompt, and the instruction "Read and follow `<repo>/pi-coding-agent/SKILL.md`; `<skill-dir>` is `<repo>/pi-coding-agent`."
4. After each run, recompute the real agent directory's hashes; if any differ, restore it from the archive and record the run as having touched the real directory.
5. Score each criterion pass or fail with a one-line evidence pointer into the output.
6. Save each scored run to `tests/runs/YYYY-MM-DD-<id>-baseline.md` or `tests/runs/YYYY-MM-DD-<id>-with-skill.md`: the transcript, the criteria table, and the evidence pointers.

## A1: Custom system prompt

**Prompt:** "How do I set a custom system prompt in Pi?"

- (a) Covers the CLI flags (`--system-prompt`, `--append-system-prompt`).
- (b) Covers `SYSTEM.md` and `APPEND_SYSTEM.md`, at the agent directory and in `.pi/`, with the trusted-project file taking precedence.
- (c) Covers an extension's `before_agent_start` handler.
- (d) Says when to use each layer.
- (e) Cites installed pages as `docs/<page>.md#<section>` and states the installed version.

## A2: Virtual model

**Prompt:** "What is a virtual model in Pi?"

- (a) Explains selection versus dispatch: a selectable model that routes each request to a physical model.
- (b) Cites `docs/virtual-models.md` with a section anchor.
- (c) States the installed version.

## A3: A feature the installed version lacks

**Prompt:** "How do I set a spending limit in Pi so it stops a session once it has cost $5?"

The feature was chosen as absent from Pi 0.99.1 by reading the candidate pages (see `tests/runs/` for the confirmation record) and confirmed by a second reader.

- (a) Says it could not find the feature in the installed version's docs.
- (b) Names the pages it checked.
- (c) Does not claim that Pi has a built-in spending limit.
- (d) Labels anything taken from outside the installed docs (pi.dev, the changelog, memory) as such.

## B1: A tool with proof

**Prompt:** "Add a Pi tool that returns the current git branch and whether the working tree is dirty."

- (a) The tool is an extension that registers a tool.
- (b) The agent runs `pi_gate.py --self-test` in the session and shows the result (with-skill arm; the baseline passes if it shows any equivalent proof that the tool loads and runs).
- (c) The agent runs a Tier 1 check and a Tier 2 scripted call of the tool and shows the output.
- (d) The agent names what was not checked.
- (e) The real agent directory is unchanged.

## B2: Share with a team

**Prompt:** "Share my skill and extension with my team." (The run directory holds `my-skill/SKILL.md` and `my-extension.ts`, copied from `tests/fixtures/gate/skill/gate-skill/SKILL.md` and `tests/fixtures/gate/tool/word-count.ts`.)

- (a) Chooses a Pi package.
- (b) Builds the package without installing it into the real agent directory.
- (c) Gates the package and shows a passing report.
- (d) Names what was not checked.

## B3: Route by prompt size

**Prompt:** "Send short questions to my local llama.cpp model and everything else to Claude, without me switching models."

- (a) Chooses a virtual model.
- (b) Routes between two physical models by the request.
- (c) Gates it with faux models standing in for both physical models, and the report shows which model answered each turn.
- (d) Does not call a real model.

## B4: Over-correction control

**Prompt:** "Add a line to my system prompt telling Pi to always answer in British English."

- (a) Chooses a file layer (`APPEND_SYSTEM.md` or a context file) and says why.
- (b) Does not write an extension.
- (c) Does not replace the whole system prompt.
