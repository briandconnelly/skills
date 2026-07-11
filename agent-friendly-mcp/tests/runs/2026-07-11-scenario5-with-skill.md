# Scenario 5 (Resources) — with-skill run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** with-skill (fresh general-purpose subagent; read `SKILL.md` + all seven `references/` files, explicitly skipped `tests/`; 8 tool-uses)
- **Score:** 8/8

## Exact prompt given

Same wiki resource-surface prompt as the baseline (see `2026-07-11-scenario5-baseline.md`), preceded by an instruction to read `agent-friendly-mcp/SKILL.md` and every file under `references/` as authoritative guidance, and **not** to read anything under `tests/`.

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Stable, hierarchical, domain-noun URIs (not numeric ids) | **PASS** | `wiki://spaces/{space}/pages/{slug}` — "stable domain nouns (space key and slug), never internal page IDs, which are unstable across deployments." |
| A2 | Index entries carry **native** triage metadata (`title`, `description`, `mimeType`, `size`, `annotations.lastModified`), no inlined body, summary ≤3 sentences | **PASS** | Index entry uses native `uri`/`name`/`title`/`description`/`mimeType`/`size`/`annotations.lastModified`; custom triage under `_meta.com.acme-wiki/page`; no body; summary ≤3 sentences. |
| A3 | Large bodies chunkable; every chunk has its own callable URI as a resource template | **PASS** | `wiki://spaces/{space}/pages/{slug}/chunks/{chunk_id}` published as template `wiki_page_chunk`; `_meta.com.acme-wiki/chunks` catalog + in-band `next_chunk_uri`. |
| A4 | Chunk ids stable across reads of a page version; version change observable | **PASS** | "Stable chunk ids per version … If the page is edited, `version` changes and chunk ids may change — but that is observable via `version` / `annotations.lastModified`, never silent." |
| A5 | Custom metadata under a **namespaced** `_meta` key, never a new top-level field | **PASS** | "Every convention field rides under a namespaced `_meta` key (`com.acme-wiki/*`); native `Resource` fields are used verbatim." (`com.acme-wiki/page`, `com.acme-wiki/chunks`.) |
| A6 | Subscriptions (`resources.subscribe` + `notifications/resources/updated`) distinguished from `list_changed` | **PASS** | `notifications/resources/updated` for **body** edits vs `notifications/resources/list_changed` for **catalog** membership — "Different fact, different notification"; both capabilities declared; passive `version`/`lastModified` fallback. |
| A7 | Parameterized lookups via resource templates **with completion** for `{space}`/`{slug}` where negotiated | **PASS** | `resources/templates/list` + a full worked `completion/complete` request/response for `{slug}` (context `{space:eng}`), gated on `server.capabilities.completions`. |
| A8 | Tool fallback reaches the same indexed content, self-sufficient from `tools/list` alone | **PASS** | `wiki_get_page`/`wiki_list_pages`/`wiki_list_spaces`; "`wiki_list_pages()` with no `space` returns the spaces index … No resource read ever required." |

**Result: 8/8.** The three baseline gaps close cleanly: native triage field **names** (A2), **namespaced** `_meta` keys (A5), and completion on template variables (A7).
The run also volunteers the skill's cross-cutting disciplines — bounded `resources/list` (spaces only, not thousands of pages), one-envelope-two-carriers resource failures (§6), house `has_more`/`next_cursor` in the index body kept distinct from native `nextCursor` (§8), and a §4 checklist-coverage table.

## Full final output (condensed; every scored element preserved with quotes above)

`acme-wiki` resource surface, walked against contract-checklist §4 + cross-cuts:

- **URI scheme:** `wiki://spaces`, `wiki://spaces/{space}/pages{?query,updated_after,cursor}`, `wiki://spaces/{space}/pages/{slug}`, `wiki://spaces/{space}/pages/{slug}/chunks/{chunk_id}` — stable domain nouns, not numeric ids.
- **Bounded `resources/list`:** summary + `wiki://spaces` + one page-index resource per space; thousands of pages reached via templates + per-space index, never enumerated (deterministic ordering for cache-diffing).
- **Index vs body:** index entry = native `title`/`description`/`mimeType`/`size`/`annotations.lastModified` + `_meta.com.acme-wiki/page` (version, chunk_count, labels); body opt-in.
- **Chunking:** body read returns first chunk + `_meta.com.acme-wiki/chunks` catalog + in-band `next_chunk_uri`; section-stable chunk ids per version; each chunk its own URI + template; `version` on every chunk to detect mid-read staleness.
- **Discovery:** `resources/templates/list` (`wiki_page`, `wiki_page_chunk`, `wiki_page_index`) + `completion/complete` for `{space}`/`{slug}` with native `completion` envelope; negotiated-capabilities block with `no_resource_subscribe`/`no_list_changed`/`no_completions` fallbacks.
- **Change notifications:** `resources/subscribe` → `notifications/resources/updated` (body) vs `notifications/resources/list_changed` (membership); passive `version`/`lastModified` polling for non-subscribers; `updated_after=` index filter.
- **Fallback:** `wiki_get_page` (with `outputSchema`, `detail` toggle, chunk_id), `wiki_list_pages` (omit `space` → spaces index), `wiki_list_spaces` — self-sufficient from `tools/list`.
- **§6 failures:** resource reads → JSON-RPC `error.data` (`machine_code`/`human_message`); tool fallback → `structuredContent` + `isError:true`; codes `space_not_found`/`page_not_found`/`page_gone`/`chunk_not_found`/`cursor_expired`/`rate_limited` with `repair` routing to real tools.
