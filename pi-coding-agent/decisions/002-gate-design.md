# 002 — Gate design choices beyond the spike

Date: 2026-09-29
Pi: 0.99.1, macOS
Spec: `docs/superpowers/specs/2026-09-29-pi-coding-agent-design.md`, requirement R3 (local planning file, not tracked).

Plan 2 traced the gate against Pi 0.99.1 before it was written.
Each entry states what was observed, what the gate does as a result, and where the spec said otherwise.
The test named in each entry pins the behavior, so a Pi release that changes it fails `check_drift.py`'s gate stage or the test suite rather than drifting silently.

## Inventory after the run settles, not at `agent_end`

Observed: a harness command sent after `agent_settled` sees every tool other extensions registered during the run, including one registered in an `agent_end` handler.
An extension command sent through RPC `prompt` returns `disposition: "handled"` and starts no run, so an `agent_end`-only inventory never fires for a command-only Tier 2.
The gate therefore registers `/pi-gate-inventory` in `faux-harness.ts` and sends it after each run settles (R3.4 said `agent_end`).
Resources registered after the run settles, such as in an `agent_settled` handler, are reported UNCHECKED.
Pinned by: the `command/note.ts` case of `test_rpc_surface_fixture_passes` and the `late registration` UNCHECKED line in `test_report_names_what_rpc_runs_could_not_check`.

## One RPC process for both tiers

Observed: RPC mode streams the same events as JSON mode (`tool_execution_end`, `message_end`, `agent_settled`), answers `get_commands` and `get_available_models` in the same session, and selects a virtual model with `set_model`.
The gate runs Tier 1 and Tier 2 in one `pi --mode rpc` process and splits the record stream at the first Tier 2 command (R3.9 said `--mode json`, with RPC for commands only).
Models come from RPC `get_available_models` only; the harness does not list them (R3.4 listed models in the harness inventory).
Pinned by: every test in `test_rpc_surface_fixture_passes`.

## Retries off

Observed: a provider that fails with a connection error is retried with growing delays (`auto_retry_start`, 2 s then 4 s).
The gate sends `set_auto_retry` with `enabled: false` first, so a wrong provider fails at once, and it still fails a run on any `auto_retry_start` (R3.9).
Pinned by: the `faux provider not answering` self-test control.

## Faux models stand in for physical ones by name

Observed: `fauxProvider({provider: "anthropic", models: [{id: "claude-sonnet-4-5"}]})` registered through `pi.registerProvider` replaces that provider for the run, and a virtual model's `ctx.modelRegistry.find("anthropic", "claude-sonnet-4-5")` returns the faux model.
`gate.json` `tier2.providers` therefore lists the physical models a router targets, and `tier2.assistantModels` lists which must answer each turn.
Pinned by: the `virtual-model/router.ts` case of `test_rpc_surface_fixture_passes`.

## `mcp.json` is checked with `pi mcp list`, every server disabled

Observed: servers from `mcp.json` do not appear in `pi.getMcpServers()`, which lists extension-registered servers only.
`pi mcp list --json` validates the file (exit 1 and an `errors` entry for an invalid server) and lists servers without connecting to disabled ones.
The gate copies the file into the throwaway agent directory with `enabled: false` on every server and runs `pi mcp list --json` (the R3 surface table said "registered, with `builtin:mcp` loaded").
A project `.pi/mcp.json` is checked the same way, as a global file; project trust for it is not exercised.
Pinned by: the `mcp-config/mcp.json` case of `test_static_surface_fixture_passes` and the `negative/sse-mcp.json` case of `test_static_negative_fixture_fails_with_its_reason`.

## Extension dialogs are answered "cancelled"

Observed: `ctx.ui.confirm` in RPC mode emits `extension_ui_request` and blocks until an `extension_ui_response` arrives.
The gate answers every dialog request with `cancelled: true` and lists each as UNCHECKED (other answers are not exercised).
Pinned by: `test_dialog_is_answered_and_reported_unchecked`.

## Environment

The first version removed only `PI_*` and `*_API_KEY` variables.
The final review (fresh reviewer, 2026-09-29) showed that was not enough: with `ANTHROPIC_OAUTH_TOKEN` exported and `tier2.model` set to `anthropic/claude-sonnet-4-5`, the request reached Anthropic (a fake token earned a 401), because `PI_OFFLINE` stops only automatic network activity, not model requests.
The gate now removes every `PI_*`, `AWS_*`, `CLOUDSDK_*`, and `GOOGLE_APPLICATION_*` variable, every variable ending in `_API_KEY` or `_TOKEN`, and every proxy variable; points the AWS and gcloud credential files into the throwaway workspace; and sets `HTTP_PROXY`/`HTTPS_PROXY` to a dead local port, which Pi honours for model requests (the same run then fails with "Connection error").
It also refuses a `tier2.model` that is neither a faux model nor declared in `expect.models` (`unscripted-model`).
The artifact's own code still runs with the user's other environment variables and file permissions (R3.14), and its own HTTP requests also meet the dead proxy.
Pinned by: `test_gate_env_blocks_every_route_to_a_paid_provider` and `test_a_real_provider_is_never_reached`.

## "Target not loaded" control

R3.12 lists "a harness-only run (target not loaded)".
The control is an extension that registers nothing (`scripts/self-test/inert.ts`), so only harness and built-in resources are observed; the gate reports `target-not-loaded`.
Pinned by: the `target not loaded` self-test control.

## A Tier 2 must assert something

Found by the first cross-model review (Codex via amicus, job 216e3992, 2026-09-29): a Tier 2 with no model turn and no declared expectation passed on nothing, a rejected prompt was ignored, and a tool error passed silently when `gate.json` declared no tool result.
The gate now fails a Tier 2 that runs no model turn and declares no `toolResults` or `events` (`tier2-empty`), fails a prompt Pi rejects (`prompt-rejected`), matches each `toolResults` entry to a distinct result in order, and fails any tool error no entry expects.
Pinned by: `test_checkpoint_1_negative_fails_with_its_reason`, `test_rejected_prompt_fails`, and `test_no_model_turn_is_not_reported_as_a_pass`.

## Pi is launched from the install it reports

`pi_docs.find_installs` accepts a project-local install, but the first version ran whatever `pi` was on `PATH`, which crashed when there was none (final review).
The gate now launches the `bin` entry of the install it reports, so the version in the report is the version that ran.
Pinned by: `test_a_project_local_install_without_pi_on_path_is_gated`.
