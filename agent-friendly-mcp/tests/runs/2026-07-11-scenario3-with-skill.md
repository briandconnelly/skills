# Scenario 3 (Long-running) — with-skill run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** with-skill (fresh general-purpose subagent; read `SKILL.md` + all seven `references/` files, explicitly skipped `tests/`; 8 tool-uses)
- **Score:** 7/7

## Exact prompt given

Same `video_render` prompt as the baseline (see `2026-07-11-scenario3-baseline.md`), preceded by an instruction to read `agent-friendly-mcp/SKILL.md` and every file under `references/` as authoritative guidance, and **not** to read anything under `tests/`.

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Task support declared at **both** levels (`tasks.requests.tools.call` + `execution.taskSupport`), not per-tool alone | **PASS** | Server: `"tasks": {"cancel": {}, "requests": {"tools": {"call": {}}}}` — the **nested** spec shape (unlike the baseline's array); tool: `execution.taskSupport: "optional"`. States "Both are declared" and "the per-tool `execution.taskSupport` flag alone is insufficient (§7)." Also correctly **withholds** `tasks/list` citing requestor-isolation. |
| A2 | Native task fields spec casing + statuses exactly `working/input_required/completed/failed/cancelled` | **PASS** | `taskId`, `status`, `statusMessage`, `createdAt`, `lastUpdatedAt`, `ttl`, `pollInterval` throughout; statuses used exactly; explicitly references `native-wire-shapes.md`. |
| A3 | `CreateTaskResult` nests `Task` under `result.task`; `tasks/get` returns it directly | **PASS** | Create response nests under `result.task` with a `model-immediate-response` `_meta`; `tasks/get` "returns … directly in `result` (not nested, and no `related-task` `_meta` — the `taskId` already travels)." |
| A4 | `progressToken` originates in request's `_meta`, not server-minted | **PASS** | Create request carries `_meta: {"progressToken": "pt_render_01"}`; `notifications/progress` echoes that token plus `io.modelcontextprotocol/related-task`. Explicitly "keyed by the requestor's `progressToken`." |
| A5 | Watermark pause via `input_required` with native recovery (preemptively call `tasks/result` and hold it open; input arrives as a separate request while pending) | **PASS** | "On seeing `input_required` the requestor **preemptively calls `tasks/result` and holds it open**. The pending input request is *not* the `tasks/result` response — it arrives as a separate server-to-client `elicitation/create` … while that call is pending"; "the already-held `tasks/result` call completes." |
| A6 | Fallback status/cancel tools labeled as convention, mirror native signals (state, poll, result location, expiry), don't replace `tasks/*` | **PASS** | Section titled "Fallback … (labeled convention)"; "mirrors the native signals (current state, when to poll again, result location, expiry) — it does not replace `tasks/*`"; fallback payloads carry `poll_after_ms`, `preview_resource_uri`, `terminal_states`, `expires_at`. |
| A7 | Native fields and house conventions not mixed; native casing never snake_cased | **PASS** | Native casing preserved everywhere; convention metadata under namespaced `_meta` (`com.video-render/errors`, `com.video-render/duration`) and labeled convention envelopes; domain fields stay `snake_case`; §7 coverage block asserts the discipline explicitly. |

**Result: 7/7.** The three baseline gaps are closed: native progress via a request-originated `progressToken` (A4), the preemptive-hold `input_required` recovery (A5), and a convention-labeled fallback that mirrors expiry/result-location (A6).
The correct nested `tasks.requests.tools.call` shape (vs the baseline's array) also lands.

## Full final output (condensed; every scored element preserved with quotes above)

`video-render-mcp` contract for MCP 2025-11-25, walked against contract-checklist §7 (long-running) with §1–§9 coverage:

- **Design decisions:** execution = task-augmented (not blocking); watermark pause = native `input_required` + elicitation with a labeled domain fallback; granularity = one task-completing `video_render` (human-approval boundary handled as an `input_required` turn inside the task, not a pre-step tool); `execution.taskSupport: "optional"` justified over `required`.
- **§1 Capabilities:** server `tasks: {cancel, requests: {tools: {call}}}` + `resources: {subscribe, listChanged}`; `tasks/list` deliberately withheld (isolation); `negotiated_capabilities` convention block naming native paths + `no_tasks`/`no_elicitation`/`no_resource_subscribe` fallbacks; capability summary with `does`/`does_not`, `error_carriers`, `long_running`, `prerequisites`.
- **§2 Tool:** `video_render` full native record — `inputSchema` with a `watermark.mode` discriminator (not an `anyOf` union), `require_watermark_approval` default, `idempotency_key` (30-min window), a success-scoped `outputSchema`, honest annotations, `execution.taskSupport`, and `_meta.com.video-render/errors` catalog.
- **§3 Create:** task-augmented `tools/call` with `task: {ttl}` and `_meta.progressToken` → `CreateTaskResult` (`result.task` nested + `model-immediate-response`); optional `notifications/progress` keyed by the request token.
- **§4 Poll + pause:** `tasks/get` returns the `Task` directly; on the watermark step status → `input_required`; the preemptive-hold `tasks/result` recovery with a separate `elicitation/create` (form or URL mode) carrying related-task `_meta`.
- **§5 Recover:** `tasks/result` (blocks to terminal, carries related-task `_meta`, delivers video as a `resource_link` not inlined bytes); a rejected-watermark terminal `failed` carrying the §6 error envelope (not the success shape); `tasks/cancel`; a create-time `invalid_field` tool-result error.
- **§6 Fallback (labeled convention):** un-augmented `video_render` returns immediately (dispatched-but-unconfirmed) with a `follow_up`; `video_get_render_status` mirrors `tasks/get` (incl. `awaiting_watermark_approval`, `expires_at`); `video_approve_watermark` / `video_cancel_render` mirror the elicitation response and `tasks/cancel`, same `video_` prefix and error taxonomy.
- **§7 coverage block:** explicit §1–§9 done-criteria, asserting native casing per `native-wire-shapes.md`, `snake_case` domain fields, and namespaced/labeled conventions.
