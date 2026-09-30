# B2 with-skill, 2026-09-29

Prompt: "Share my skill and extension with my team."
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) package | pass | `team-kit/` |
| (b) not installed into real directory | pass | nothing installed |
| (c) gated, passing report shown | pass | `RESULT PASS: 0 failed, 8 passed, 1 unchecked` |
| (d) names unchecked | pass | late registration; sandbox note |

## Transcript (the agent's final report, verbatim)

I packaged your extension and skill as a Pi package at `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b2-with-skill/team-kit`. The gate passes, but I have not published or pushed it, so your team can't install it yet.

**Installed Pi:** 0.99.1. The skill was verified against 0.99.1, so the versions match.

**What is in the package**
- `team-kit/package.json` has the `pi-package` keyword and declares `@earendil-works/pi-ai`, `@earendil-works/pi-coding-agent` and `typebox` as `peerDependencies` with `"*"`, as docs/packages.md#declare-dependencies says.
- `team-kit/extensions/word-count.ts` is a copy of `my-extension.ts`.
- `team-kit/skills/gate-skill/SKILL.md` is a copy of `my-skill/SKILL.md`. The directory is named `gate-skill` to match the skill's `name`.
- `team-kit/gate.json` holds the gate checks. The originals are untouched.

**Gate result:** PASS, with 8 passed, 0 failed and 1 unchecked.
- The extension loaded with no error.
- The `word_count` tool was registered.
- The `gate-skill` skill was found, and `SKILL-MARKER-2C9D` reached the model's transcript.
- A scripted `word_count` call returned "3 words".
- **Unchecked:** late registration, meaning resources registered after a run settles (for example in `agent_settled`), is not observed.
- The gate isolates what Pi reads and writes, not what the extension's code does. That code ran with your filesystem and network permissions and was not sandboxed (docs/security.md#choose-how-to-run-pi).

**Sharing it with your team** (docs/packages.md#install-and-manage-packages)
1. Publish the package, either as a git repo or to npm.
   - **Git:** push `team-kit` to a repo and tag it. Teammates run `pi install git:github.com/<org>/team-kit@v0.1.0`.
   - **npm:** run `npm publish`. Teammates run `pi install npm:<name>@0.1.0`.
2. `pi install` writes a personal install to `~/.pi/agent/settings.json`. Adding `-l` writes it to `.pi/settings.json` instead, so a project can carry it. Pi reads that file only after the project is trusted.
3. A teammate can try it for one run with `pi -e <source>`, without touching their settings.
4. Packages can run code and their skills can instruct the model to run programs, so your team should review the source before installing.

**Commands run** (each `pi_gate.py` command ran after `export PI_CODING_AGENT_DIR=/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b2-with-skill/pi-agent`)
1. `pi_docs.py where` reported Pi 0.99.1 and "Skill verified against 0.99.1 (matches installed)".
2. `pi_docs.py index | head -80` and `pi_docs.py index | grep -i -n "package\|share"` located packages.md and the skills.md#validate-and-share-a-skill section.
3. `pi_docs.py grep "pi package"` confirmed that packages.md is the home for sharing extensions and skills.
4. `cat` on `docs/packages.md` and on the quickstart chooser (which lists "Install or distribute several resources" as Pi package).
5. `mkdir`, `cp`, and heredocs created `team-kit/` with its `package.json` and `gate.json`.
6. `pi_gate.py --self-test` printed 7 PASS lines and `RESULT self-test PASS (Pi 0.99.1)`.
   - My first combined command also contained a stray `echo ====`. zsh raised `(eval):36: === not found`, so the gate did not run in that call.
7. `pi_gate.py team-kit` printed the PASS report above, ending "RESULT PASS: 0 failed, 8 passed, 1 unchecked".
