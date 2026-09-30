# B3 with-skill, 2026-09-29

Prompt: "Send short questions to my local llama.cpp model and everything else to Claude, without me switching models."
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) virtual model | pass | `router/router.ts` |
| (b) routes by request | pass | "How it decides" |
| (c) gated with faux stand-ins, answering model per turn shown | pass | "short turn was answered by `llama.cpp/qwen` and the long turn by `anthropic/claude-sonnet-4-5`" |
| (d) no real model call | pass | gate only |

Finding against the skill: the virtual-model recipe and fixture use the provider id `llama-cpp`; the agent found Pi's built-in llama.cpp provider id is `llama.cpp` and corrected it in its own gate file.

## Transcript (the agent's final report, verbatim)

## Answer

I built a Pi extension that registers a virtual model, `router/auto`. It sends short prompts to your local llama.cpp model and everything else to Claude, so you pick one model and never switch. The gate passed 4 checks with 3 UNCHECKED. It does not show that the router works against your real llama.cpp server or a real Claude login.

Files (in `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b3-with-skill/`):
- `router/router.ts` is the extension.
- `router/router.gate.json` is the gate config.

Installed Pi is 0.99.1, and the skill was verified against 0.99.1.

How it decides:
- **Where the docs point:** the surface is a virtual model registered from an extension, per `docs/virtual-models.md#register-a-virtual-model` (v0.99.1). `docs/models.md#use-classifier-models` covers a classifier-based alternative, which I did not use.
- **Short vs long:** a prompt is "short" if the last message is under 200 characters. That threshold is my own choice, because the docs leave "short" undefined. Change `SHORT` in `router.ts` if you want a different cutoff.
- **Local model:** short prompts go to the first available model on the `llama.cpp` provider. `docs/llama-cpp.md#manage-models` says only models the router has loaded appear, so load one with `/llama` first. If none is loaded, short prompts fall through to Claude.
- **Claude model:** everything else goes to `anthropic/claude-sonnet-4-5`. That ID comes from the docs example, and I could not check it against a real Anthropic login because the isolated agent directory has no credentials. If that model is unavailable, the router throws an error.
- **Tool follow-ups and retries:** these stay on the model that handled the turn, which keeps prompt caches valid (`docs/virtual-models.md#route-requests`).

To use it: run `pi -e /Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b3-with-skill/router/router.ts --model router/auto`. To make it permanent, install it as an extension with `docs/extensions.md`. I did not do that.

## Gate report

Passing:
- Pi loaded the extension with no error.
- `router/auto` shows up as an available model.
- With faux models standing in for the two providers, the short turn was answered by `llama.cpp/qwen` and the long turn by `anthropic/claude-sonnet-4-5`.
- Both scripted steps ran.

UNCHECKED (the gate could not test these):
- The target-loaded check: the artifact declares nothing Pi reports.
- Late registration: resources registered after a run settles are not observed.
- Model provenance: models carry no `sourceInfo`.

The gate isolates what Pi reads and writes, not what the extension's code does. The code ran with your own filesystem and network permissions and is not sandboxed (`docs/security.md#choose-how-to-run-pi`).

Pi's `--list-models anthropic` printed "No models available" here because the isolated agent directory has no credentials.

## Commands run (in `/Users/bdc/projects/skills/.eval-tmp/pi-scenarios/b3-with-skill` unless noted)

Every `pi` and `pi_gate.py` shell command first ran `export PI_CODING_AGENT_DIR=.../b3-with-skill/pi-agent`.

1. `ls`/`find` of the work directory: it held only an empty `pi-agent/`.
2. `uv run <skill-dir>/scripts/pi_docs.py where` printed "Pi 0.99.1 at /opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent" and "Skill verified against 0.99.1 (matches installed)".
3. `pi_docs.py index | head -150` listed the docs pages.
4. `cat` of `docs/llama-cpp.md`, the classifier section of `docs/models.md`, `references/choosing-a-surface.md`, and the quickstart chooser. The chooser sends "Connect an unsupported model service" to a custom provider and "Add executable tools, commands, or event handlers" to an extension.
5. `cat docs/virtual-models.md` and `references/gate-recipes.md`. The recipes include a "Provider or virtual model" fixture matching this task.
6. Read `tests/fixtures/gate/virtual-model/router.ts` and grepped the docs. This showed the fixture uses a placeholder provider `llama-cpp`.
7. A grep of the Pi install and `dist/extensions/llama/provider.js` found the real provider ID is `llama.cpp` (`LLAMA_PROVIDER_ID = "llama.cpp"`). It also showed `modelRegistry.getAvailable()` exists.
8. `pi --list-models anthropic` printed "No models available".
9. `curl -s -m 3 http://127.0.0.1:8080/models` returned nothing, so there is no llama.cpp router on port 8080 and I could not check the real local model name.
10. I wrote `router/router.ts` and `router/router.gate.json`. The gate file is the fixture with `llama-cpp` changed to `llama.cpp`.
11. `pi_gate.py --self-test` printed "RESULT self-test PASS (Pi 0.99.1)", with all 7 cases passing.
12. `pi_gate.py router/router.ts` printed "RESULT PASS: 0 failed, 4 passed, 3 unchecked. A pass covers only the checks listed as PASS."
