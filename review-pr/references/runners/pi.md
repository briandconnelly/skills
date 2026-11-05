# Pi runner adapter

The pi adapter runs the shared review workflow through the [pi](https://pi.dev) coding agent.

The generic security and result requirements have their only normative definitions in [the runner adapter contract](../runner-contract.md).

## Prerequisites

- PI1: The adapter requires pi 1.2.0 or newer.
- PI2: The supported review levels are `low`, `medium`, `high`, `xhigh`, and `max`, mapped to pi's `--thinking` levels.
- PI3: The child loads no pi extension discovered from settings or packages, so a model provider that comes from an extension is loaded only from a path listed in `REVIEW_PR_PI_EXTENSIONS`, which is colon-separated and trusted as the caller's own code.
  `REVIEW_PR_PI_MODEL`, when set, is passed to `--model`; otherwise pi selects its default model.
  The child inherits the caller's environment, including `PI_CODING_AGENT_DIR`, so user-level settings, models, and credentials come from the caller's agent directory.

## Policy isolation

- PI4: `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, and `CLAUDE.MD` at any depth, and `.pi/`, `.agents/`, and `.claude/`, are reviewer-policy paths restored from the base commit.
- PI5: `.pi/settings.json`, `.pi/mcp.json`, `.pi/SYSTEM.md`, `.pi/APPEND_SYSTEM.md`, `.pi/extensions`, `.pi/prompts`, `.pi/themes`, `.pi/npm`, and `.pi/git` are removed after restoration because they can load code, servers, packages, or system prompts.
- PI6: In each directory, the first present of `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, and `CLAUDE.MD` is passive context, which is the file pi itself would load there.
  `SKILL.md` files under `.agents/skills/`, `.pi/skills/`, and `.claude/skills/` are passive context too, and both kinds are listed in the policy manifest.

## Child controls

- PI7: The child runs through `pi -p --mode json` with no session file, project trust declined (`--no-approve`), and no startup network operations (`--offline`).
- PI8: Extension, skill, prompt-template, theme, context-file, and MCP discovery are disabled, so pi itself loads no project or user resource of those kinds.
  User-level `SYSTEM.md` and `APPEND_SYSTEM.md` in the caller's agent directory still apply.
- PI9: The exact child tool set is `read`, `grep`, `find`, and `ls`, so the child has no shell, write, or network tool, and the capability prohibition is otherwise defined only by RC3 of [the runner adapter contract](../runner-contract.md).
  Those tools accept absolute paths, so filesystem reads are not technically confined to the checkout and private evidence directory.
- PI10: pi silently lowers a thinking level the selected model does not support, so a run whose assistant turns record a different level than the one requested is normalized as an error.
  A model that ignores reasoning effort, such as Kimi-K3 behind LiteLLM, runs every level at `off` and can review only with no level.
- PI11: pi does not expose budget or turn-limit flags, so `REVIEW_PR_BUDGET` and `REVIEW_PR_MAX_TURNS` are accepted by the shared interface but are not enforced by this adapter.

## Output mapping

- PI12: The text blocks of the final assistant `message_end` map to the result text, and the sum of assistant turns' `usage.cost.total` maps to `cost_usd`.
- PI13: A missing final assistant message, a final stop reason other than `stop`, exhausted retries, a failed compaction, an aborted run, and a lowered thinking level map to normalized errors, and a final stop reason other than `stop` maps to `subtype`.
- PI14: pi has no permission prompts, so the normalized `denials` field is always empty for this adapter.

## Status

The pi adapter is not listed in `scripts/adapters/supported`, because its review-quality gate has not passed as RC7 requires.
The committed snapshots were collected on `litellm/moonshotai/Kimi-K3` with no review level: `adjacent-comment` passes, `legacy` fails on one run's text before `## Summary`, and `policy-criteria` fails on recall and one wrong lens.
The pi tests run against a temporary copy of the skill that lists the adapter, and collecting a snapshot requires adding `pi` to `supported` locally.

## Verification

Run `bash review-pr/tests/pi-adapter-test.sh` for the offline adapter interface and output-mapping gate.

Run `bash review-pr/tests/pi-hostile-fixture-test.sh` for the runner-backed tool and policy-isolation gate.

Replay the committed [review-quality gate](../../tests/lens-rubric.md) evidence with `python3 review-pr/tests/score-lens.py review-pr/tests/evidence/lens/cases/legacy/pi/baseline --gate`; the rubric describes collecting a new snapshot.
The committed pi `run-N.json` files omit `message_update` records, which are delta-only and superseded by each `message_end`, to keep them small.

Run `REVIEW_PR_RUNNER=pi bash review-pr/tests/checkout-pr-test.sh` for the authenticated GitHub checkout gate.

The command-line controls are based on pi's `docs/cli.md`, `docs/json.md`, `docs/security.md#project-trust`, and `docs/configuration.md#context-files`, as shipped with pi 1.2.0.
