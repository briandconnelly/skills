# Codex runner adapter

The Codex adapter runs the shared review workflow through the Codex CLI.

The generic security and result requirements have their only normative definitions in [the runner adapter contract](../runner-contract.md).

## Prerequisites

- CO1: The adapter requires Codex CLI 0.151.0 or newer.
- CO2: The supported review levels are `low`, `medium`, `high`, and `xhigh`.

## Policy isolation

- CO3: `AGENTS.md`, `AGENTS.override.md`, `.agents/`, and `.codex/` are reviewer-policy paths restored from the base commit.
- CO4: `.codex/` is removed after restoration because it can contain executable runner configuration and rules.
- CO5: For each directory, `AGENTS.override.md` takes precedence over `AGENTS.md`, and the selected instruction file plus Codex skill instructions are passive context listed in the policy manifest.

## Child controls

- CO6: The child runs through `codex exec` with JSONL output, ephemeral sessions, ignored user configuration, ignored execution rules, strict configuration parsing, and the read-only sandbox.
- CO7: Approval is disabled, project instruction auto-discovery is disabled, and the adapter disables multi-agent, app, browser, computer-use, image-generation, hook, plugin, skill-search, and goal features.
- CO8: The Codex shell remains available for read-only evidence inspection, and its filesystem reads are not technically confined to the checkout and private evidence directory.
- CO9: An optional review level maps to `model_reasoning_effort`.
- CO10: Codex CLI does not expose stable budget or turn-limit flags, so `REVIEW_PR_BUDGET` and `REVIEW_PR_MAX_TURNS` are accepted by the shared interface but are not enforced by this adapter.

## Output mapping

- CO11: The final completed `agent_message` maps to the result text, while `error` and `turn.failed` events map to normalized errors.
- CO12: Codex CLI does not expose a stable permission-denial event, so the normalized `denials` field is always empty for this adapter.

## Verification

Run `bash review-pr/tests/codex-adapter-test.sh` for the offline adapter interface and output-mapping gate.

Run `bash review-pr/tests/codex-hostile-fixture-test.sh` for the runner-backed tool and policy-isolation gate.

Run `bash review-pr/tests/lens-fixture-test.sh --runner codex --arm lens --runs 3` for the runner-backed review-quality gate.

Run `REVIEW_PR_RUNNER=codex bash review-pr/tests/checkout-pr-test.sh` for the authenticated GitHub checkout gate.

The command-line controls are based on OpenAI's [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [sandboxing](https://learn.chatgpt.com/docs/sandboxing), and [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) documentation.
