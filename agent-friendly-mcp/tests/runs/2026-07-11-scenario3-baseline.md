# Scenario 3 (Long-running) — baseline run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** baseline (fresh general-purpose subagent, prompt only, forbidden from reading the repo/skill; 0 tool-uses confirms no skill access)
- **Score:** 4/7

## Exact prompt given

> Design the agent-facing MCP contract for a `video_render` tool whose renders take 1–10 minutes and can pause waiting for the user to approve a watermark.
> Target MCP 2025-11-25.
> Produce: the capability declarations, the tool definition, the wire shapes an agent sees when creating, polling, and recovering the render, and whatever fallback you think clients without task support need.

(Wrapped with a guardrail forbidding reading any repo file, especially under `agent-friendly-mcp/`.)

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Task support declared at **both** levels (`tasks.requests.tools.call` + `execution.taskSupport`), not per-tool alone | **PASS** (with caveat) | Server declares `"tasks": {"requests": ["tools/call"], "list": true, "cancel": true}` and the tool declares `execution.taskSupport: "optional"` — both levels present. **Caveat:** `requests` uses an array `["tools/call"]`, not the spec's nested `requests.tools.call` object — a shape deviation the with-skill run gets right. |
| A2 | Native task fields spec casing + statuses exactly `working/input_required/completed/failed/cancelled` | **PASS** | `taskId`, `status`, `statusMessage`, `createdAt`, `lastUpdatedAt`, `ttl`, `pollInterval` all correct casing; statuses `working`, `input_required`, `completed`, `cancelled`, `failed` used correctly. |
| A3 | `CreateTaskResult` nests `Task` under `result.task`; `tasks/get` returns it directly | **PASS** | Create response nests under `result.task`; `tasks/get` returns task fields directly in `result`. |
| A4 | `progressToken` originates in request's `_meta`, not server-minted | **FAIL** | No `progressToken` used. Invented a non-native `notifications/tasks/status` notification instead of `notifications/progress` keyed by a request-supplied `progressToken`. |
| A5 | Watermark pause via `input_required` with native recovery (preemptively call `tasks/result` and hold it open; input arrives as a separate request while pending) | **FAIL** | Uses `input_required` + `elicitation/create`, but drives it by **polling** `tasks/get` then receiving a separate elicitation — never describes the "call `tasks/result` preemptively and hold it open" recovery pattern the spec/skill require. |
| A6 | Fallback status/cancel tools labeled as convention, mirror native signals (state, poll, result location, expiry), don't replace `tasks/*` | **FAIL** | Provides `video_render_status`/`video_render_approve` fallback that mirrors state + `pollAfterMs`, but does not label them as a non-native convention and omits expiry; "result location" only implied. |
| A7 | Native fields and house conventions not mixed; native casing never snake_cased | **PASS** | Consistent camelCase for native fields; house fields (`pollAfterMs`, `renderId`) kept in fallback payloads; native `_meta` key `io.modelcontextprotocol/related-task` used correctly; no native field snake_cased. |

**Passed:** A1, A2, A3, A7 (4/7).
This is a strong baseline — a current model knows the MCP task lifecycle well — but it misses the two subtlest, most error-prone points the skill teaches: native progress via a request-originated `progressToken` (A4) and the preemptive-hold `input_required` recovery (A5), plus the convention-labeling discipline on the fallback (A6).

## Full final output (condensed; scored elements preserved with quotes above)

Baseline design of `video_render` for MCP 2025-11-25:

- **Capabilities:** client sends `capabilities: {tasks: {}, elicitation: {}}`; server returns `tasks: {requests: ["tools/call"], list: true, cancel: true}` (**array** form), `elicitation: {}`, `tools.listChanged`.
- **Tool:** `video_render` with `inputSchema` (sourceUri, format, resolution, watermark{text,position,onNoElicitation}), an `outputSchema` (renderId, url, durationSeconds, watermarkApplied), honest `annotations`, and `execution.taskSupport: "optional"` (justified over `required`/`forbidden`).
- **Create:** task-augmented `tools/call` with `task: {ttl}` → immediate `result.task` (nested, correct casing, `pollInterval`).
- **Poll / pause:** `tasks/get`; on the watermark step, status → `input_required` and the server sends `elicitation/create` correlated via `_meta.io.modelcontextprotocol/related-task`; also emits a **(non-native) `notifications/tasks/status`** on each transition.
  Basis for the A4 FAIL.
- **Complete:** terminal status via poll, then `tasks/result` → `CallToolResult` with `structuredContent` + a `resource_link`; premature `tasks/result` returns a JSON-RPC error.
- **Recover:** persisted `taskId` re-`tasks/get`; `tasks/list` to re-find; notes that a lost `input_required` elicitation must be re-issued by the server; `ttl` retention; `taskId` as idempotency anchor.
- **Fallback:** `video_render_status` + `video_render_approve` (+`video_render_cancel`) mirroring create/poll/pause-resolve/complete via plain tool calls; `onNoElicitation` (skip/apply/fail) for the non-interactive case.
  Not labeled as a non-native convention and no expiry mirroring — basis for the A6 FAIL.
