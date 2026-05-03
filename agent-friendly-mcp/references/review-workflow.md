# MCP Server Review Workflow

Use this workflow when auditing an existing MCP server or advising how to make it more agent-friendly. Inputs are the server's tool, resource, and prompt schemas, its capability summary, and — ideally — at least one real agent transcript exercising the high-value tasks. Outputs are severity-tagged findings against [contract-checklist.md](contract-checklist.md), each anchored to a specific `§N`, plus a coverage table that accounts for every section in the checklist.

A review is grounded when its findings cite evidence from the schema, the response payloads, or a transcript — not from how the server "feels." Where evidence is unavailable, mark the relevant section `not-checked` with a reason rather than guessing.

## Severity Scale

- **Critical** — agent will reliably fail to use the server correctly, or there is a security or data-integrity risk. Examples: a mutating tool advertised `readOnlyHint: true`, `idempotentHint: true` on a tool that creates duplicates on retry, undocumented destructive side effects, secrets leaked in error payloads, a `stdio` server logging to stdout, an auth model collapsed to "credential failure" with no distinction between missing / wrong / insufficient scope. Blocks merge.
- **Major** — agent will frequently choose the wrong primitive, waste tokens, or hit avoidable errors. Examples: overlapping tool descriptions, no progressive-disclosure mechanism on a 50-tool server, unstructured error strings with no symbolic codes, no capability fingerprint, resource lists that inline bodies.
- **Minor** — degrades agent experience but recoverable. Examples: verbose default responses with no detail toggle, missing `request_id` correlation, ambiguous parameter names whose schema types still constrain shape, summaries longer than three sentences.
- **Nit** — style, naming, or doc improvement. Examples: inconsistent verb usage across tools, capitalization drift, a prompt that could be one sentence shorter.

## Audit Procedure

1. **Read or generate the server capability summary.** If the server publishes one, start there. If it does not, that absence is itself a Critical finding against §2 (and §1, since §1 treats server metadata as contract) — record it and continue by reading the discovery surface (tool list, resource catalog, prompts) to reconstruct what the summary should have said. Note auth model, ambient state, transport choice, and stated negative scope.
2. **Walk [contract-checklist.md](contract-checklist.md) section by section, top to bottom.** For each section (§1 through §8), record exactly one of:
   - a **finding** with severity and evidence,
   - **`OK`** with a one-line evidence pointer (file/line, schema field, or transcript excerpt),
   - **`not-checked`** with a reason (e.g., "no transcript available," "auth model out of scope for this audit," "no resources defined — §4 N/A").
   A section may have multiple findings; a section with both findings and `OK` evidence on adjacent items is fine — note both.
3. **Run the transcript-style probes below.** Use a real agent transcript when available; otherwise simulate one from the schema by tracing what an agent would see at each step. At least one probe must be answered with concrete evidence before the audit is done.
4. **Synthesize findings into the report format below.** Order findings by severity (Critical → Nit), then by checklist section. Then assemble the coverage table.

**Safety:** Do not invoke tools that mutate live state, rotate credentials, or trigger paid operations unless the user explicitly approves. When simulating credential failures, prefer obviously invalid placeholder values over real-looking incorrect ones.

## Transcript Probes

Five questions to ask while reading code and transcripts. Each should be answerable from concrete evidence — schema text, response payloads, or transcript excerpts — not intuition.

- **Cold start.** What does an agent see when it first connects? Can it learn what the server does, what it does NOT do, and what it needs (auth, ambient state, transport) in one read? Trace the first few definition loads from a transcript or simulate them from the schema. *(maps to §1, §2)*
- **Tool selection.** Given two adjacent tools (same verb, overlapping nouns, or similar surface), can an agent pick the right one without invoking both? Are descriptions narrow enough that the schema alone disambiguates? Look for tools whose descriptions you cannot tell apart at a glance. *(maps to §3; see `examples.md` §10 for the failure-mode shape)*
- **First repair.** When the agent makes an invalid call, does the error response tell it specifically how to retry — which field, which allowed values, which tool to call instead? Force one invalid call per error code documented for the tool and read the payload, not just the message. *(maps to §6; see `examples.md` §6 for the target payload shape)*
- **Discovery cost.** How many tokens does the agent spend learning the server's surface before its first useful call? Does discovery paginate, filter, and offer summaries before full definitions? Count, do not estimate — a 50-tool server with no progressive disclosure typically costs an order of magnitude more than one with `search_tools` / `describe_tool`. *(maps to §2, §7; see `examples.md` §8 for one valid progressive-disclosure shape)*
- **Cross-version.** What changes when this server upgrades? Does the capability fingerprint move, and can a cached client detect the change without re-walking the full surface? Diff two versions of the discovery surface if available; otherwise inspect what the fingerprint covers. *(maps to §8; see `examples.md` §9 for a deprecation lifecycle)*

## Report Format

Each finding has five labeled lines:

- **Severity:** Critical | Major | Minor | Nit
- **Section:** `§N` reference into `contract-checklist.md` (e.g., `§3`, `§6`); use multiple when a finding spans sections.
- **Summary:** one-line statement of the gap.
- **Evidence:** file/line, schema excerpt, or transcript snippet — never "it feels wrong."
- **Remediation:** concrete fix referencing real callable surfaces (tool names, parameter names, valid enum values), not generic advice.

Concrete example:

> - **Severity:** Major
> - **Section:** §3
> - **Summary:** `slack_post` and `slack_send_message` have overlapping descriptions; agents pick incorrectly on first call.
> - **Evidence:** `tools/slack.py:42` and `tools/slack.py:118` — both descriptions begin "Send a message to a Slack channel." Eval transcript `runs/2026-04-29.jsonl` shows 7/12 first-call selections went to the wrong tool.
> - **Remediation:** Collapse the two into a single `slack_send_message` (§3 granularity rule); if the second variant is truly distinct, rename to reflect the distinguishing axis (e.g., `slack_send_threaded_reply`) and rewrite both descriptions to lead with the disambiguating clause.

After the findings list, include a **checklist coverage table**. One row per section §1–§8; each row records `finding(s)` (with refs into the findings list), `OK` (with evidence), or `not-checked` (with reason). Section names mirror `contract-checklist.md`; if that file changes section count or names, update this template alongside it. Example shape:

| Section | Status | Notes |
| --- | --- | --- |
| §1 Server-Level | finding F1 | name collides with `data` server in multiplexed client |
| §2 Discovery | OK | `search_tools` paginates; capability summary at `server/summary.md` |
| §3 Tools | findings F2, F3 | overlapping descriptions; one mutating tool with `readOnlyHint: true` |
| §4 Resources | not-checked | server defines no resources |
| §5 Prompts | OK | three prompts, all advisory; tool schemas remain authoritative |
| §6 Failure Recovery | finding F4 | error responses are unstructured strings |
| §7 Token Efficiency | OK | cursor pagination present; `detail` toggle on every tool |
| §8 Versioning | finding F5 | no capability fingerprint published |

End the report with open questions or assumptions, and an optional remediation summary if the findings cluster around a theme (e.g., "most Critical findings concentrate in §6 — invest there first").

## Done Criteria

- Every section §1 through §8 in [contract-checklist.md](contract-checklist.md) is accounted for in the coverage table — covered by at least one finding, marked `OK` with brief evidence, or marked `not-checked` with an explicit reason.
- At least one of the five transcript probes was run with concrete evidence (real or simulated transcript), and its answer is recorded in the report.
- Each finding carries all five labeled lines (severity, section, summary, evidence, remediation), and remediation references real callable surfaces.
- When no Critical or Major findings are found, the report says so explicitly and names residual risks (e.g., "no live auth-failure transcript was available" or "fingerprint behavior on upgrade was not exercised").
