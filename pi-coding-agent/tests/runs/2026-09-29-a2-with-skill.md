# A2 with-skill, 2026-09-29

Prompt: "What is a virtual model in Pi?"
Agent: fresh Sonnet 5.5 subagent, preamble and closing line per `tests/scenarios.md` (see the ledger rulings in the PR).
Result: PASS

| Criterion | Result | Evidence |
| --- | --- | --- |
| (a) selection vs dispatch explained | pass | "Selection and dispatch" bullet |
| (b) anchored citation | pass | `docs/virtual-models.md#selection-and-dispatch`, `#register-a-virtual-model`, `#route-requests` |
| (c) states installed version | pass | header |

## Transcript (the agent's final report, verbatim)

**Answer (Pi 0.99.1 installed; skill verified against 0.99.1, matches)**

A virtual model in Pi is a selectable model that picks a physical model for each request. You use it to route by task, cost, or conversation state. For example, a router can send quick questions to a small model and hard problems to a large one, while the user selects just one model. (docs/virtual-models.md, intro)

- **Registration:** You register virtual models from an extension. They appear in `/model`, `--model`, scoped models, and settings like any other model. They can be listed under any provider, including one that has physical models, such as `openai-codex/auto`. (docs/virtual-models.md, intro; docs/virtual-models.md#register-a-virtual-model). Registration uses `registerVirtualModel`. `pi.unregisterVirtualModel(provider, id)` removes one, and `pi.unregisterProvider()` does not. SDK code can call `modelRuntime.registerVirtualModel(definition)`.
- **Selection and dispatch:** A virtual model selects a model plus a thinking level. A router maps that pair to a physical (model, level) pair for each request. The example in the docs is `jev/auto:low -> anthropic/claude-sonnet-4-5:high`. The virtual thinking level is only an input to the router, and its meaning is up to the router. (docs/virtual-models.md#selection-and-dispatch)
- **What gets recorded:** The selection goes in `model_change` and `thinking_level_change` entries. The dispatch goes on each assistant message (`provider`, `api`, `model`, `thinkingLevel`). Providers only receive physical models. (docs/virtual-models.md#selection-and-dispatch; docs/session-format.md)
- **Session resume:** A resumed session restores the virtual selection from the latest `model_change` entry. If the virtual model is no longer registered, Pi falls back to the physical model that answered last. Router state is stored as custom entries with `customType` `pi.virtual-model-state`. (docs/session-format.md)
- **Routing:** `route(request, ctx)` runs before every request and returns `{ model, thinkingLevel }`. The returned model can be any physical model in the catalog whose provider has credentials. A virtual model cannot route to another virtual model. If `route()` throws or returns a virtual model or a model without credentials, the request ends with an error response. (docs/virtual-models.md#route-requests)
- **Classifiers:** Routers can use classifier models via `ctx.modelRegistry.classify()` (docs/models.md#use-classifier-models).
- **Context and compaction:** Context usage and compaction use the limits of the physical model that produced the latest response. (docs/virtual-models.md#selection-and-dispatch)
- **Example:** The bundled `examples/extensions/jev-router.ts` is a virtual model that plans on a strong model and implements on a cheap one.

This was answer mode only, so I built nothing and ran no gate.

**Commands run**
1. `export PI_CODING_AGENT_DIR=.../a2-with-skill/pi-agent && uv run <skill-dir>/scripts/pi_docs.py where`
   - Pi 0.99.1 at /opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent, and "Skill verified against 0.99.1 (matches installed)".
2. `pi_docs.py index | head -150`
   - Listed the doc pages, but the output was cut off before the relevant section.
3. `pi_docs.py index | sed -n 150,400p | grep -i virtual|provider` and `pi_docs.py grep "virtual model"`
   - The index showed the page "Route with Virtual Models — virtual-models.md", with sections Selection and dispatch, Register a virtual model, Route requests, and Keep routing state.
   - The grep hit docs/virtual-models.md, docs/models.md:136, docs/session-format.md:99 and :174, and examples/extensions/jev-router.ts.
4. `sed -n 1,30p .../docs/virtual-models.md`
   - Confirmed the definition and the selection and dispatch text quoted above.

I also read `/Users/bdc/projects/skills/pi-coding-agent/SKILL.md` with the Read tool. The `pi` binary was never invoked, so the `PI_CODING_AGENT_DIR` export had no effect.
