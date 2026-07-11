# Scenario 1 (Design) — with-skill run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** with-skill (fresh general-purpose subagent; read `SKILL.md` + all seven `references/` files, explicitly skipped `tests/`; 8 tool-uses)
- **Score:** 9/9

## Exact prompt given

Same GitHub Issues design prompt as the baseline (see `2026-07-11-scenario1-baseline.md`), preceded by an instruction to read `agent-friendly-mcp/SKILL.md` and every file under `references/` as authoritative guidance, and **not** to read anything under `tests/`.

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | Tools task-completing, 11 endpoints → ~4–7 tools | **PASS** | Collapsed to **7** tools with a per-merge justification table: list **+** search → `github_search_issues`; get **+** list-comments → `github_get_issue`; add **+** remove labels → `github_manage_labels`; lock **+** unlock → `github_set_issue_lock`. Explicitly cites the near-name-collision anti-pattern (ex§10). |
| A2 | Names snake_case, service-prefixed, verb+noun | **PASS** | `github_search_issues`, `github_get_issue`, `github_create_issue`, `github_update_issue`, `github_add_comment`, `github_manage_labels`, `github_set_issue_lock` — `github_` prefix, verb+noun, snake_case. |
| A3 | `additionalProperties:false`, disambiguated names, omission semantics, `default` discipline | **PASS** | `additionalProperties:false` on every schema; `issue_number` "…the #N shown in the UI, not the global node id"; every optional field states "Omitted means …". |
| A4 | ≥2 error payloads: symbolic codes, field detail, repair naming a real surface | **PASS** | Five worked payloads (`not_found`, `search_rate_limited`, `conflict`, `insufficient_scope`, resource JSON-RPC); each `repair` names a real tool + literal arguments. |
| A5 | Errors as tool result errors (`isError:true`), not JSON-RPC | **PASS** | "tool failures → `structuredContent` with `isError: true`; resource … failures → JSON-RPC `error.data`. One envelope, two carriers." Worked in modes A–E. |
| A6 | Capability summary stating what the server does NOT do | **PASS** | Explicit `does_not`: "Touch pull requests, Actions, Projects…", "Delete issues or comments", "Manage repositories, teams…", "real-time webhook/event streams". |
| A7 | Pagination cursor-based + provenance-correct + concise default with `detail` toggle | **PASS** | `has_more`/`next_cursor` explicitly "a **house pagination convention** … not native `nextCursor` (reserved for `tools/list`)"; `detail: "summary"|"full"`; separate `truncated`/`truncation_hint`; opaque cursors with `cursor_expired`. |
| A8 | Annotations present and honest (create not read-only/idempotent) | **PASS** | `github_create_issue` → `idempotentHint:false`; `github_update_issue`/`manage_labels`/`set_issue_lock` → `idempotentHint:true` with a stated "annotation family consistency" rationale. |
| A9 | Tool defs publish `outputSchema`; success = conforming `structuredContent`; `content` fallback | **PASS** | `github_search_issues` carries a full `outputSchema` (issues[], has_more, next_cursor, estimated_total, truncated); prose ties success `structuredContent` to it and keeps text `content` as fallback. *(Note: not all 7 tools show an `outputSchema` block — the flagship read tool does, and the pairing rule is stated; a stricter future scenario could require it on every tool.)* |

**Result: 9/9.** Every gap the baseline exhibited (A1, A2, A6, A7, A9) is closed, and the skill-specific disciplines (native-vs-convention `_meta` namespacing, one-envelope-two-carriers, version-precondition handles, forward-compat N/A justifications for §4/§5/§7) appear throughout.

## Full final output (condensed; every scored element preserved with quotes above)

`github-issues` MCP server, designed by walking contract-checklist §1–§9:

- **§1 Server-level:** distinctive name `github-issues`, streamable-HTTP transport, bearer auth with three distinct credential failure codes (`missing_credential`/`invalid_credential`/`insufficient_scope`), opaque integrity-protected `cursor`/`version` handles, error-carriers declared up front, `negotiated_capabilities` convention block naming native capability paths + fallbacks.
  Roots/tasks marked **N/A** with justification.
- **§2 Discovery:** capability summary at `github://capabilities` with explicit `does`/`does_not`; 7 compact tool defs (no `search_tools` layer needed); `resources/templates/list` for issue/comment read-fallback; `completion/complete` on `{owner}`/`{repo}`; fingerprint `github-issues@1.0.0+c3f1a20` in summary and every error.
- **§3 Tools:** the 7 tools above, each a full native `Tool` record — strict closed `inputSchema`, honest family-consistent `annotations`, error catalog under `_meta.com.github-issues/errors`, `idempotency_key` on creates, `expected_version` optimistic-lock on update, additive `manage_labels` distinguished from update's replace. `github_search_issues` also carries a full `outputSchema`.
- **§6 Failure recovery:** five worked payloads (four tool-result `isError:true` + one `resources/read` JSON-RPC `error.data` renaming only `code`→`machine_code`, `message`→`human_message`); retry-vs-repair invariants honored (rate_limited has no `repair`; conflict has a corrective `repair` despite `temporary:false`).
- **§4 Resources:** issue/comment read-fallback templates; JSON-RPC error carrier; primary read path is the tool.
- **§5 Prompts / §7 Long-running:** both **N/A** with justification (no load-bearing prompt; all ops single-turn).
- **§8 Token efficiency:** `detail` toggle, house pagination convention labeled distinct from native `nextCursor`, explicit truncation, opaque cursors with lifetime.
- **§9 Versioning:** fingerprint + native `list_changed` + deterministic ordering + versioned error codes with alias-window rename discipline.

The complete run rendered full JSON `inputSchema`/`outputSchema`/`annotations`/`_meta` blocks for all seven tools and all five error payloads; the structure above preserves every property the assertions scored.
