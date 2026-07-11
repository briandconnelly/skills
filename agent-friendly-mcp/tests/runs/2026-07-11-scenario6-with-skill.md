# Scenario 6 (Prompts) — with-skill run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** with-skill (fresh general-purpose subagent; read `SKILL.md` + all seven `references/` files, explicitly skipped `tests/`; 8 tool-uses)
- **Score:** 7/7

## Exact prompt given

Same `open_incident` prompt-design prompt as the baseline (see `2026-07-11-scenario6-baseline.md`), preceded by an instruction to read `agent-friendly-mcp/SKILL.md` and every file under `references/` as authoritative guidance, and **not** to read anything under `tests/`.

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | References follow-on tools/resource by canonical name, does not redefine their contracts | **PASS** | Names all three tools + `incidents://active`; "defines **no** argument shapes, side effects, error codes, or idempotency semantics of its own … references them by name and must not redefine them." |
| A2 | Prerequisites declared (tools, resources, permission/context assumptions) | **PASS** | `_meta.com.incident-mcp/prerequisites` lists `tools`, `resources`, `permissions` (`incident:write`, `responder:page`), a `capabilities` note (completions + fallback), and `context_assumptions` (duplicate-check). |
| A3 | No load-bearing behavior in prompt text (audit; shapes/side-effects/errors in schemas) | **PASS** | Explicitly runs the §5 audit: "Removing the prompt entirely must leave [the tools + resource] fully correct and callable"; "delete `open_incident` and nothing breaks." Side effects/idempotency/errors assigned to the tool schemas. |
| A4 | Only native `PromptArgument` fields (`name`, `title`, `description`, `required`); value-shape guidance in `description` | **PASS** | Arguments use only native fields; "value-shape guidance goes in each `description`, never as `type`/`items`/`default`." Severity value-set explicitly deferred to `incident_create`'s schema. |
| A5 | Convention metadata under a **namespaced** `_meta` key, never top-level `Prompt` fields | **PASS** | "all convention metadata rides under a namespaced `_meta` key so the block is wire-valid" — `com.incident-mcp/when-to-use`, `/prerequisites`, `/expected-followups`, `/notes`; top level is native-only. |
| A6 | Completion for arguments with dynamic value sets where negotiated | **PASS** | "request completion for this argument" (severity) and "Request completion for these values rather than guessing handles" (responders/commander); prerequisites note `completion/complete` gated on `server.capabilities.completions` with a schema-read fallback. |
| A7 | States explicitly the prompt is optional scaffolding; schema-only clients still call every tool correctly | **PASS** | "a prompt is **advisory orchestration scaffolding, not contract**"; "any client that bypasses the prompt still calls the tool"; the delete-and-nothing-breaks test. |

**Result: 7/7.** The two baseline gaps close — a declared prerequisites block (A2) and completion on dynamic arguments (A6) — and the run actively demonstrates the disciplines the baseline only skirted: namespaced `_meta` for all convention metadata (A5), the explicit "remove every prompt" audit (A3), and the optional-scaffolding framing (A7).
It also correctly pushes `idempotency_key`, the structured error envelope, dispatched-vs-applied paging, and the `incidents://active` index shape into the tool/resource schemas rather than the prompt.

## Full final output (condensed; every scored element preserved with quotes above)

`open_incident` prompt design, walked against SKILL §5 + native-vs-convention:

- **Boundary first:** prompt = advisory scaffolding; the §5 audit ("delete the prompt — does anything break?") is applied up front, so no shapes/side-effects/errors live in prompt text.
- **Prompt definition:** native top level only (`name`, `title`, `description`, `arguments`, `_meta`); `description` carries when-to-use **and** when-NOT-to-use; arguments `title`/`severity`/`summary` (required) + `responders`/`commander` (optional), each with value-shape guidance in `description` and the severity value-set deferred to `incident_create`'s schema.
- **`_meta` (namespaced `com.incident-mcp/*`):** `when-to-use`; `prerequisites` (tools, resource, permissions, completions capability + fallback, duplicate-check assumption); `expected-followups` (6 ordered steps naming each tool, incl. "branch on the structured error code and follow its `repair` hint — do not re-run `incident_create` blind"); `notes` restating advisory-only.
- **What belongs where:** prompt = when-to-use, ordering, prerequisites, follow-on tools by name, confirm-before-paging judgment; tool schemas = argument shapes, severity enum, `additionalProperties:false`, honest mutating annotations, `idempotency_key` + dedup window, structured error envelope with `repair`, dispatched-vs-applied paging result; resource = `incidents://active` stable-URI index (id/title/severity/status/lastModified) with optional subscribe.
- **Test held to:** "delete `open_incident` and nothing breaks — the three tools and the resource remain independently correct, discoverable, and safe to call."
