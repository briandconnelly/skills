# Scenario 5 (Resources) — baseline run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** baseline (fresh general-purpose subagent, prompt only, forbidden from reading the repo/skill; 0 tool-uses confirms no skill access)
- **Score:** 5/8

## Exact prompt given

> Design the agent-facing MCP resource surface for a server that exposes a large internal documentation wiki to an agent.
> The wiki has thousands of pages organized in spaces (e.g. `eng`, `hr`); pages can be large (some over 100 KB); page content changes during the day; and agents need to look up a specific page by space + slug as well as browse.
> Produce: the resource URI scheme, what a resource index/list entry looks like versus a full body, how large pages are delivered, how an agent discovers parameterized lookups, how an agent is notified when a page it cares about changes, and any fallback for clients that do not handle resources well.

(Wrapped with a guardrail forbidding reading any repo file, especially under `agent-friendly-mcp/`.)

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Stable, hierarchical, domain-noun URIs (not numeric ids) | **PASS** | `wiki://{space}/{slug}`, `wiki://{space}/{slug}?chunk={n}`, `wiki://{space}/{slug}@{version}` — hierarchical, stable slugs, no numeric ids. |
| A2 | Index entries carry **native** triage metadata (`title`, `description`, `mimeType`, `size`, `annotations.lastModified`), no inlined body, summary ≤3 sentences | **FAIL** | Page index entries are a custom JSON list using **non-native** field names — `summary` (not `description`), `sizeBytes` (not `size`), `updatedAt` (not `annotations.lastModified`). Bodies correctly not inlined and summaries short, but the native triage field set is not used. |
| A3 | Large bodies chunkable; every chunk has its own callable URI as a resource template (or labeled tool fallback by chunk id) | **PASS** | `wiki://{space}/{slug}?chunk={n}` chunks, template `wiki://{space}/{slug}{?chunk}` published via `resources/templates/list`; heading-boundary splitting + `outline` TOC. |
| A4 | Chunk ids stable across reads of a page version; version change observable via modification metadata | **PASS** | "Chunks are pinned to the version" (`@v210?chunk=1`); `version`/`updatedAt`/`etag` expose changes. |
| A5 | Custom metadata under a **namespaced** `_meta` key, never a new top-level field on the `Resource` record | **FAIL** | Read envelope uses `_meta`, but keys are **not namespaced** (`_meta: {space, slug, version, chunk, …}`, and notification `_meta: {previousVersion, version}`) rather than `com.wiki/…`. Index-entry JSON also carries custom fields at top level. |
| A6 | Subscriptions (`resources.subscribe` + `notifications/resources/updated`) distinguished from `list_changed` | **PASS** | Declares `resources: {subscribe:true, listChanged:true}`; per-page `notifications/resources/updated` for body edits vs `notifications/resources/list_changed` for structural changes — explicitly distinguished, incl. a `moved` edge case. |
| A7 | Parameterized lookups via resource templates **with completion** for `{space}`/`{slug}` where negotiated | **FAIL** | Resource templates present, but no `completion/complete` for template variables is mentioned. |
| A8 | Tool fallback reaches the same indexed content, self-sufficient from `tools/list` alone | **PASS** | `search_pages`, `get_page`, `list_space`, `check_updates` mirror the surface with the identical chunk envelope; explicitly the lowest-common-denominator path. |

**Passed:** A1, A3, A4, A6, A8 (5/8).
A strong baseline — the architecture (bounded enumeration, templates for lookup, chunking with an outline, version pinning, subscriptions, tool mirror) is sound.
The skill-sensitive gaps are the native-vs-convention disciplines: native triage field **names** on index entries (A2), **namespaced** `_meta` keys (A5), and completion on template variables (A7).

## Full final output (condensed; scored elements preserved with quotes above)

Wiki resource surface design:

- **URI scheme:** `wiki://` root, `wiki://{space}/` space index, `wiki://{space}/{slug}` page, `?chunk={n}` for chunks, `@{version}` immutable pin.
- **Templates:** `resources/templates/list` publishes `wiki://{space}/{slug}`, `wiki://{space}/`, `wiki://{space}/{slug}{?chunk}` with rich `description`s; the primary docs surface an agent reads.
- **Enumeration:** root `resources/list` returns **spaces only** (bounded, native `title`/`description`/`mimeType`); reading a space returns a custom JSON index of lightweight page entries (`title`, `summary`, `updatedAt`, `version`, `sizeBytes`, `chunked`, `uri`) — no bodies. *(Non-native field names → A2 FAIL.)*
- **Body / chunking:** `resources/read` returns body + `_meta` envelope; pages >~50 KB return chunk 0 with `nextChunk`/`nextChunkUri`, `totalChunks`, an `outline` TOC, heading-boundary splitting, version-pinned chunk URIs. *(Non-namespaced `_meta` keys → A5 FAIL.)*
- **Change notifications:** `resources/subscribe` on the bare URI → `notifications/resources/updated` (with additive `_meta` incl. `previousVersion`/`version`/`changeType`); `notifications/resources/list_changed` for structural changes; both capabilities declared. *(No `completion/complete` for `{space}`/`{slug}` → A7 FAIL.)*
- **Fallback:** `search_pages` / `get_page` / `list_space` / `check_updates` tools returning the same envelope shapes, with polling as the subscription substitute.
