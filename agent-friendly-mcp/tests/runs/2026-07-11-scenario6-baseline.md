# Scenario 6 (Prompts) — baseline run

- **Date:** 2026-07-11
- **Tree:** `d586ce3` (main, post review-batch #53)
- **Mode:** baseline (fresh general-purpose subagent, prompt only, forbidden from reading the repo/skill; 0 tool-uses confirms no skill access)
- **Score:** 5/7

## Exact prompt given

> Design a reusable MCP prompt named `open_incident` for a server that wraps an incident-management service.
> Its tools already exist: `incident_create`, `incident_add_responder`, `incident_post_update`, plus a resource `incidents://active`.
> The prompt should help an agent run the "declare a new incident" workflow.
> Produce: the prompt definition (name, arguments, and any orchestration text), and a short note on what belongs in the prompt versus what belongs in the tool and resource schemas.

(Wrapped with a guardrail forbidding reading any repo file, especially under `agent-friendly-mcp/`.)

## Per-assertion scoring

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| A1 | References follow-on tools/resource by canonical name, does not redefine their contracts | **PASS** | Workflow names `incident_create`, `incident_add_responder`, `incident_post_update`, `incidents://active`; "What belongs where" keeps field structure/enums in the tool schemas, not the prompt. |
| A2 | Prerequisites declared (which tools, resources, permission/context assumptions) | **FAIL** | No prerequisites declaration — tools are named inside the workflow prose, but there is no explicit list of required tools/resources or permission/context assumptions the prompt relies on. |
| A3 | No load-bearing behavior in prompt text (audit; shapes/side-effects/errors in schemas) | **PASS** | "prompts encode the workflow …; schemas encode the contract"; return shape "must actually be in the tool's output schema"; per-tool hints "let the agent reason about a tool even outside this workflow." |
| A4 | Only native `PromptArgument` fields (`name`, `title`, `description`, `required`); value-shape guidance in `description` | **PASS** | Arguments use only `name`/`description`/`required`; the severity enum and value shapes are described in prose, no `type`/`items`/`default` keys. |
| A5 | Convention metadata under a **namespaced** `_meta` key, never top-level `Prompt` fields | **PASS** (by omission) | Uses only native `title`/`description`/`arguments`; folds when-to-use into `description`; adds no top-level convention fields. It does not add prerequisites/expected-followups at all (hence A2), so it never demonstrates the `_meta` pattern — but it also never violates it. |
| A6 | Completion for arguments with dynamic value sets where negotiated | **FAIL** | No `completion/complete` offered for `affected_service`/`reporter` (values the agent should not guess). |
| A7 | States explicitly the prompt is optional scaffolding; schema-only clients still call every tool correctly | **PASS** | "field structure … so it holds for every caller, including ones not using this prompt"; the whole "What belongs where" test — data-constraints in schemas so they hold "for every caller." |

**Passed:** A1, A3, A4, A5, A7 (5/7).
A strong baseline — the workflow-vs-contract split is articulated well, and it correctly avoids non-native argument keys and load-bearing prompt behavior.
The skill-sensitive gaps are the two §5 discovery/declaration disciplines: a declared prerequisites block (A2) and completion on dynamic arguments (A6).

## Full final output (condensed; scored elements preserved with quotes above)

`open_incident` prompt design:

- **`prompts/list` entry:** native `name`/`title`/`description` + `arguments` (`summary` required; `severity`/`affected_service`/`reporter` optional), each argument carrying value-shape guidance in `description` (e.g. the SEV1/2/3 meanings).
  No non-native keys.
- **`prompts/get` result:** a single `user` message with `{{summary}}`/`{{severity}}`/… substitution and a 6-step workflow — dedupe-check `incidents://active` first, settle severity with the user, `incident_create`, `incident_add_responder`, `incident_post_update`, then report back; "operate one step at a time … surface any error rather than continuing."
- **"What belongs where":** prompt = sequencing/judgment/choreography/tone/defaults-as-questions; tool schemas = field structure, required/optional, severity enum, hints, return shape; resource = the live open-incident data for the dedupe heuristic.
  Test: constrains *data* → schema (holds for every caller); constrains *process/judgment* → prompt.
- **Not present:** a prerequisites declaration (A2 FAIL) and any completion mechanism for dynamic arguments (A6 FAIL); no namespaced `_meta` block (avoided by folding when-to-use into `description`).
