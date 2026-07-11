# Scenario 1 (Design) — baseline run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** baseline (fresh general-purpose subagent, prompt only, instructed not to read the repo/skill; 0 tool-uses confirms no skill access)
- **Score:** 4/9

## Exact prompt given

> Design the agent-facing MCP server contract for a service wrapping the GitHub Issues REST API.
> The underlying API has these endpoints: list issues, get issue, create issue, update issue, add comment, list comments, lock issue, unlock issue, add labels, remove labels, search issues.
> Produce: the tool list with input schemas, the error shape for at least two failure modes, and whatever discovery surface you think agents need.

(Wrapped with a guardrail forbidding reading any repo file, especially under `agent-friendly-mcp/`.)

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Tools task-completing, 11 endpoints → ~4–7 tools | **FAIL** | Produced 11 endpoint-mirroring tools (`issues_list`, `issue_get`, `issue_create`, `issue_update`, `comment_add`, `comments_list`, `issue_lock`, `issue_unlock`, `labels_add`, `labels_remove`, `issues_search`) plus 1 more — one-per-endpoint; lock/unlock and labels_add/remove kept separate rather than folded into update. |
| A2 | Names snake_case, service-prefixed, verb+noun | **FAIL** | snake_case yes, but no service prefix (`issue_get`, not `github_get_issue`) and noun_verb ordering, not verb+noun. |
| A3 | `additionalProperties:false`, disambiguated names, omission semantics, `default` discipline | **PASS** | `additionalProperties:false` on every schema; `issue_number` not `issue`; enums with server-applied `default`s; "Omit to leave labels untouched"; nullable cursor semantics. |
| A4 | ≥2 error payloads: symbolic codes, field detail, repair naming a real surface | **PASS** | `ISSUE_NOT_FOUND` (remediation names `issues_list`/`issues_search`), `RATE_LIMITED` (retry_after), `VALIDATION_FAILED` (field-level `invalid_values`), `FORBIDDEN`. |
| A5 | Errors as tool result errors (`isError:true`), not JSON-RPC | **PASS** | "The MCP tool result sets `isError: true`; the structured payload is …". |
| A6 | Capability summary stating what the server does NOT do | **FAIL** | `server_capabilities` tool lists limits/scopes but states no explicit negative scope ("this server does NOT …"). |
| A7 | Pagination cursor-based + provenance-correct + concise default with `detail` toggle | **FAIL** | Cursor-based `page_info` present, but no native (`nextCursor`) vs house (`has_more`) provenance distinction and no concise/detailed response toggle. |
| A8 | Annotations present and honest (create not read-only/idempotent) | **PASS** | `issue_create` → `readOnlyHint:false, destructiveHint:false, idempotentHint:false`; reads marked `readOnlyHint:true, idempotentHint:true`. |
| A9 | Tool defs publish `outputSchema`; success = conforming `structuredContent`; `content` fallback | **FAIL** | Prose claims "Tools declare an `outputSchema` and return `structuredContent`," but no tool definition actually includes an `outputSchema` block. |

**Passed:** A3, A4, A5, A8 (4/9).
Baseline confirms the scenario is not trivially passable and isolates the skill-sensitive gaps: granularity (A1), naming convention (A2), negative scope (A6), pagination provenance/detail toggle (A7), and shown `outputSchema` (A9).

## Full final output

````markdown
# Agent-Facing MCP Server Contract: GitHub Issues

This is a design produced from knowledge of MCP and API design — it wraps the eleven listed REST endpoints but shapes them for an LLM agent consumer, not as a 1:1 REST mirror.

## 1. Design principles applied

- **Task-named tools, not endpoint-named.** Agents match tools by intent. Names use a `noun_verb` grouping (`issue_get`, `comments_list`) so related tools cluster in the tool list.
- **One obvious way to address a repo.** Every tool takes `owner` + `repo` as separate strings. `issue_number` is the human-visible number, never the opaque internal `id`.
- **Annotations tell the agent what's safe.** Each tool carries MCP `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`).
- **Pagination is explicit and bounded.** List/search tools return a `page_info` object with an opaque `next_cursor`; the server caps `per_page`.
- **Structured output.** Tools declare an `outputSchema` and return `structuredContent`, plus a short human-readable `text` summary.
- **Errors are data, not prose.** A single typed error envelope with a machine `code`, a `retryable` flag, and a `remediation` hint.

## 2. Shared conventions

Repo addressing (`owner`, `repo` as separate strings on every tool) and a `page_info` pagination envelope (`returned`, `has_more`, `next_cursor`); cursor-based, `per_page` clamped to [1,100] default 30.

## 3. Tool list (11 tools)

`issues_list`, `issue_get`, `issue_create`, `issue_update`, `comment_add`, `comments_list`, `issue_lock`, `issue_unlock`, `labels_add`, `labels_remove`, `issues_search` — each with a strict JSON `inputSchema` (`additionalProperties:false`, enums, bounds) and honest annotations. `issue_update.labels` documented as full-replace; `labels_add`/`labels_remove` for incremental changes. `issue_create` annotated non-idempotent.

## 4. Result envelope & error shape

Uniform error envelope with `isError:true` and `{code, message, http_status, retryable, retry_after_seconds, remediation, details}`. Worked failure modes: `ISSUE_NOT_FOUND` (404), `RATE_LIMITED` (429, retry_after), `VALIDATION_FAILED` (422, field detail), `FORBIDDEN` (403).

## 5. Discovery surface

`server_capabilities` tool (auth context, rate limits incl. the lower search limit, max_per_page, supported lock reasons); five resources (issue schema, repo labels, assignable users, milestones, search-qualifier help) via `resources/list` + templates; two workflow prompts (`triage_issue`, `find_duplicates`).
````

*(Deliverable condensed to the scored structure above; the full run showed complete JSON `inputSchema` blocks for all 11 tools and all four error payloads.
No `outputSchema` block appeared in any tool definition — the basis for the A9 FAIL.)*
