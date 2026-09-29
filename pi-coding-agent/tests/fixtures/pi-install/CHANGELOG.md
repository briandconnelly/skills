# Changelog

## [0.99.1] - 2026-09-29

### New Features

- **GPT-6.1 Sol** — Available on OpenAI, Azure OpenAI, and OpenAI Codex, and now the default OpenAI Codex model. See [Select a model](docs/models.md#select-a-model).

### Added

- Added GPT-6.1 Sol (`gpt-6.1-sol`) to the OpenAI, Azure OpenAI Responses, and OpenAI Codex providers.

### Changed

- Changed the default OpenAI Codex model to GPT-6.1 Sol (`gpt-6.1-sol`).

### Fixed

- Fixed `/login` with OpenAI failing in the bundled release with a missing `openai-chatgpt.js` module error.

## [0.99.0] - 2026-09-29

### New Features

- **Codemode and MCP** — Connect MCP servers and let models run JavaScript that calls tools in parallel. See [MCP Servers](docs/mcp.md) and [Enable codemode](docs/cli.md#enable-codemode).
- **System theme** — Pi's colors now come from your terminal's own palette by default. See [Use your terminal's colors](docs/themes.md#use-your-terminals-colors).
- **Sign in with ChatGPT** — Use a ChatGPT subscription with the OpenAI provider through `/login openai`. See [Authenticate interactively](docs/providers.md#authenticate-interactively).
- **Virtual models** — Extensions can route each request to a different physical model. See [Virtual Models](docs/virtual-models.md).
- **Classifier models** — Run Jev classifiers from codemode scripts, or use any llama.cpp model as a classifier. See [How codemode works](docs/cli.md#how-codemode-works) and [Classification](docs/llama-cpp.md#classification).

### Added

- Added codemode, tool search, and MCP support as built-in extensions. The `codemode` tool runs model-written JavaScript in a QuickJS sandbox that calls pi's tools; enable it with `defaultTools` or `--tools` and configure it with `codemode.mode` and `codemode.inlineBudget`. `tool_search` finds tools that are not declared to the model and declares them. MCP servers over stdio or streamable HTTP, with OAuth, come from `mcp.json` (global, or per project once trusted) or `pi.registerMcpServer()` and are managed with `/mcp` and `pi mcp add|remove|list|login|logout`. See [MCP Servers](docs/mcp.md) and [Enable codemode](docs/cli.md#enable-codemode) ([#10040](https://github.com/earendil-works/pi/issues/10040)).
- Added extension tool APIs for orchestrating tools: `exposure` (`direct`, `model-only`, `codemode`, `deferred`, or `hidden`), `namespace`, `annotations`, `outputSchema` with `structuredContent`, `isError` results, `prepareLoadout()`, and `ctx.executeTool()` for nested tool calls, which emit events with `parentToolCallId` and are recorded as bounded `nestedCalls` on the calling tool's result. See [Tool exposure](docs/extensions.md#tool-exposure).
- Added a warning when an extension that registers the same tool, command, or flag replaces a built-in extension ([#10174](https://github.com/earendil-works/pi/pull/10174) by [@cristinaponcela](https://github.com/cristinaponcela)).
- Added experimental virtual models: extensions register them with `pi.registerVirtualModel()` and pick a physical model and thinking level for each request. The footer shows the routed model, `/session` lists cost per physical model, and `examples/extensions/jev-router.ts` routes with the Jev classifier. See [Virtual Models](docs/virtual-models.md).
- Added Sign in with ChatGPT to the OpenAI provider in `/login`, which uses a ChatGPT subscription with the OpenAI API. Pi stores a stable `deviceId` in the global settings for this login and omits it from bug reports.
- Added the `system` theme, now the default, which derives pi's colors from the terminal's reported foreground, background, and ANSI palette and rebuilds them when the terminal switches between light and dark. See [Use your terminal's colors](docs/themes.md#use-your-terminals-colors).
- Added `#rgb`, `oklch()`, and `okhsl()` colors and an optional `appearance` field to theme files, and `theme.style()`, `theme.colors`, and `theme.appearance` for extensions. See [Themes](docs/themes.md) and [TUI](docs/tui.md).
- Added a classifier model for every llama.cpp chat model, answered from next-token label probabilities. See [Classification](docs/llama-cpp.md#classification).
- Added inherited Jev classifier models on OpenRouter, Cloudflare Workers AI, Vercel AI Gateway, and OpenCode Zen.
- Added the `fullscreenWheelScrollLines` setting and `/settings` entry for fullscreen mouse-wheel scrolling. The default `"auto"` accelerates fast wheel spins outside local macOS terminals ([#9758](https://github.com/earendil-works/pi/issues/9758)).
- Added per-input disposition to successful RPC `prompt`, `steer`, and `follow_up` responses, `AgentSession.steer()`/`followUp()`, and `RpcClient.prompt()`/`steer()`/`followUp()`; `RpcClient.prompt()` also accepts `streamingBehavior` ([#9098](https://github.com/earendil-works/pi/issues/9098), [#9803](https://github.com/earendil-works/pi/issues/9803)).
- Added image generation to `ModelRuntime`: `generateImages()` with runtime-resolved auth (stored credentials, OAuth, runtime API keys, `models.json` headers), plus `getModelsOfType()`, `getModelOfType()`, `getAvailableOfType()`, `getAllModels()`, and `getAllAvailable()`. OpenRouter image models are listed under the `openrouter` provider and share its credential; an upstream ID can have separate chat and image entries. `models.json` providers and extension registrations without a model list keep built-in image generation. Extension model lists can include discriminated chat, image, and classifier entries with operation implementations; when supplied, they replace the provider catalog across every operation. Chat-facing reads (`getModels()`, `getAvailableSnapshot()`, the model picker) are unchanged.
- Added classifier support to `ModelRuntime`, including `classify()`, classifier model accessors, runtime-resolved authentication, and the built-in TypeSafe `jev-latest` model.
- Added `types=chat,image,classifier` to pi.dev model catalog requests so remote refreshes overlay every supported model type; entries of unknown model types are ignored.
- Added the `provider_stream_event` extension event for observing parsed provider events before normalization, with an opt-in `/debug-provider` example viewer ([#9784](https://github.com/earendil-works/pi/issues/9784), [#9901](https://github.com/earendil-works/pi/pull/9901) by [@davidbrai](https://github.com/davidbrai)).
- Added a show/hide toggle (`H`) in HTML exports for custom messages marked `display: false`. Messages remain hidden by default and can also be revealed from the sidebar ([#8896](https://github.com/earendil-works/pi/issues/8896), [#10020](https://github.com/earendil-works/pi/pull/10020) by [@rwachtler](https://github.com/rwachtler)).
- Added inherited Claude Sonnet 5.5 support for Anthropic with adaptive thinking and a 1M context window.
- Added a Built-in section in `pi config` to disable the built-in `mcp`, `llama.cpp`, `codemode`, and `tool-search` extensions globally or per project, stored as `-builtin:<name>` in the `extensions` setting. SDK inline extensions opt in with `builtin: true`.
- Added `+name` and `-name` entries to the `defaultTools` setting to add or remove tools without repeating the defaults, for example `"defaultTools": ["+codemode"]`. Project entries of this form apply on top of the user setting. Documented how to enable `codemode` without MCP and how to use classifier models such as Jev from codemode scripts.
- Added the token usage and cost of codemode `models.classify()` calls to the codemode tool result, so they count toward the session cost; the codemode result shows each call's cost.

### Changed

- Switched the build from the TypeScript native preview to TypeScript 7.0 with an ES2024 target, and replaced `tsx` with Node's built-in type stripping for running from source ([#9965](https://github.com/earendil-works/pi/issues/9965)).
- Removed the `[Themes]` section from the startup banner. Custom themes remain available in `/settings`, and theme conflicts are still reported.
- Changed the startup header to show the pi logo with the version instead of the app name.
- Changed the built-in `dark` and `light` themes to the revised pi colors, written in OKHSL.
- Changed light/dark terminal detection to use the reported background color first, then the terminal's light/dark report, then `COLORFGBG`. The first-time setup no longer shows the detected appearance.
- Renamed the inherited OpenAI Codex provider to "OpenAI Codex (legacy)"; Sign in with ChatGPT on the OpenAI provider supersedes it.
- Changed inherited terminal detection to treat `TERM=*-direct` as truecolor.
- Built-in extensions and tools are named `builtin:<name>` (for example `builtin:mcp` and `builtin:read`) in errors, diagnostics, RPC source info, and bug reports, instead of `<inline:name>` and `<builtin:name>`. Their slash commands no longer carry a `[t]` autocomplete tag.
- `--no-extensions` also disables the built-in extensions, including the llama.cpp provider. Load one explicitly with `-e builtin:<name>`, for example `pi -ne -e builtin:mcp`.
- Tool calls without a custom call renderer, including direct MCP tool calls, now show their arguments: as `key=value` pairs on the title line when collapsed and one `key: value` line per argument when expanded. MCP calls are titled `server/tool` and their results collapse to 5 lines.
- `bash` and `powershell` structured results, which codemode scripts receive, now hold up to 1 MiB of output instead of the model-facing 2000 lines or 50KB, and add `truncated` and `full_output_path`. Longer output keeps its first and last 512 KiB. Empty output is `""` instead of `(no output)`.

### Fixed

- Fixed X11 clipboard text being misidentified as an image when the clipboard owner accepts unadvertised image targets ([#9786](https://github.com/earendil-works/pi/issues/9786)).
- Prevented managed git packages from automatically installing Pi peer dependencies and added warnings for extension packages that list host-provided modules in `dependencies` ([#9863](https://github.com/earendil-works/pi/issues/9863)).
- Fixed pinned git extensions loaded with `-e` continuing to use the first downloaded commit after the ref changes ([#9982](https://github.com/earendil-works/pi/issues/9982)).
- Fixed `RpcClient` skipping the next event listener when a listener unsubscribes while handling an event, which could make `waitForIdle()` time out after `collectEvents()` ([#9990](https://github.com/earendil-works/pi/issues/9990)).
- Fixed full-file `read` calls rendering as `:1` when models send `null` for omitted `offset` and `limit` ([#9996](https://github.com/earendil-works/pi/issues/9996)).
- Fixed new sessions being lost when pi exits before the first assistant response. The session file is now created when the first user message is sent ([#10000](https://github.com/earendil-works/pi/issues/10000)).
- Fixed unloaded llama.cpp autoload presets overwriting a cached runtime context window with the GGUF training context ([#10077](https://github.com/earendil-works/pi/issues/10077), [#10158](https://github.com/earendil-works/pi/pull/10158) by [@cristinaponcela](https://github.com/cristinaponcela)).
- Fixed custom themes ignoring `terminal.trueColor` and other terminal capability overrides and rendering with 256 colors ([#9973](https://github.com/earendil-works/pi/issues/9973), [#10039](https://github.com/earendil-works/pi/pull/10039) by [@christianklotz](https://github.com/christianklotz)).
- Fixed pasting files copied in Finder inserting the file icon image instead of the file paths; paths are quoted in bash mode ([#9999](https://github.com/earendil-works/pi/issues/9999), [#10136](https://github.com/earendil-works/pi/pull/10136) by [@christianklotz](https://github.com/christianklotz)).
- Fixed the startup header, loaded resources, and chat notices keeping their old colors after a theme change.
- Fixed the Fireworks default model pointing at the removed Kimi K2.6 model; it now defaults to Kimi K3.
- Fixed the OpenCode Go default model pointing at the removed Kimi K2.6 model; it now defaults to Kimi K3.
- Fixed the Together default model pointing at the removed Kimi K2.6 model; it now defaults to Kimi K3.
- Reduced CPU use while streaming in long sessions and when previewing themes: the footer caches session usage totals, collapsed bash results cache their preview, and `sanitizeBinaryOutput()` no longer splits output into per-character arrays.
- Fixed the usage of tools called through `ctx.executeTool()`, for example from codemode scripts, being dropped from the session cost; it is now added to the calling tool's result usage.
- Fixed inherited `/skill` autocomplete appearing empty when loaded skill names did not contain the letters in `skill` ([#9944](https://github.com/earendil-works/pi/issues/9944)).
- Fixed inherited path and `@` autocomplete not working after opening wrappers such as `(`, `[`, `{`, `<`, or a backtick.
- Fixed inherited image stretching in terminals that use the Kitty graphics protocol ([#8938](https://github.com/earendil-works/pi/issues/8938), [#9957](https://github.com/earendil-works/pi/pull/9957) by [@rwachtler](https://github.com/rwachtler)).
- Fixed inherited shell cursor staying hidden after exit when an extension closed an overlay during shutdown ([#10026](https://github.com/earendil-works/pi/issues/10026)).
- Fixed inherited keyboard input being lost after a mouse click in a `/settings` submenu closed it.
- Fixed inherited 1-hour Anthropic cache writes through Vercel AI Gateway being priced at the 5-minute rate ([#9210](https://github.com/earendil-works/pi/issues/9210)).
- Fixed inherited model-level `samplingParams` being dropped by direct `stream()`/`complete()` calls on OpenAI-compatible APIs ([#9506](https://github.com/earendil-works/pi/issues/9506)).
- Fixed inherited Mistral GLM requests failing with "Expected at most one leading ThinkChunk" after empty content deltas ([#9674](https://github.com/earendil-works/pi/issues/9674)).
- Fixed inherited OpenAI Fast mode requests being priced at the standard rate ([#10034](https://github.com/earendil-works/pi/issues/10034)).
- Fixed inherited Mistral reasoning models ignoring the requested thinking level ([#9678](https://github.com/earendil-works/pi/issues/9678)).
- Fixed inherited OpenCode Zen and OpenCode Go `qwen3.8-flash` thinking being replayed as plain text on later turns ([#10047](https://github.com/earendil-works/pi/issues/10047)).
- Fixed inherited OpenAI Responses streams from servers that omit `output_index`, such as llama.cpp, running mixed-up tool calls; such streams now end with an error ([#9974](https://github.com/earendil-works/pi/issues/9974)).
- Fixed inherited Anthropic and OpenAI Codex browser sign-in waiting indefinitely after the provider redirected with an authorization error, and Anthropic sign-in failing when its callback port is in use.
- Fixed inherited GitHub Copilot Claude Opus 5.5 offering unsupported thinking levels when upstream model metadata is incomplete.
