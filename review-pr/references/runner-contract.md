# Runner adapter contract

A runner adapter connects the agent-neutral review workflow to one agent CLI.

The bundled adapters are executable shell libraries under `scripts/adapters/`.

## Required interface

An adapter must define these functions after it is sourced:

- `adapter_check` verifies the runner executable and every runner-specific prerequisite.
- `adapter_is_policy_path PATH` returns success when `PATH` is reviewer policy that must come from the base commit.
- `adapter_is_context_path PATH` returns success when restored passive policy at `PATH` must be supplied to the reviewer.
- `adapter_build_command PROMPT LEVEL BUDGET TURNS EVIDENCE_DIR` sets the `ADAPTER_COMMAND` array to the complete child command.
- `adapter_normalize RAW_PATH EXIT OUTPUT_PATH` converts native output into the normalized result envelope below.

An adapter must define `ADAPTER_POLICY_ROOTS` as the root paths removed before base policy is restored.

An adapter must define `ADAPTER_ALWAYS_REMOVE` as the paths removed after restoration because they can execute code or attach external tools.

## Execution invariants

- RC1: The child must run with the checked-out repository as its working directory.
- RC2: The child must receive the review lens without runner-specific tool names.
- RC3: The child must be unable to modify files, invoke a shell, access the network, start subagents, or load project-supplied executable configuration.
- RC4: Reviewer instructions and passive review resources must come from the pinned base commit rather than the pull-request head.
- RC5: The adapter must reject an unsupported review level rather than silently changing its meaning.
- RC6: The adapter must normalize native output into the result envelope before the calling session reads it.
- RC7: Each adapter reference must name its offline interface test and runner-backed hostile-fixture test, and both tests must pass before the adapter is advertised as supported.
- RC8: The checkout must list every adapter-selected passive policy file in `policy-manifest.json`, and the child must read every listed file before reviewing the diff.
- RC9: The checkout must fail before review when the policy manifest exceeds `REVIEW_PR_MAX_POLICY_FILES`, which defaults to 40, rather than silently omitting policy or exhausting the child turn budget.

## Normalized result envelope

The adapter writes one JSON object with these fields:

```json
{
  "engine": "runner-name",
  "engine_version": "runner version or null",
  "status": "completed or error",
  "result": "review markdown",
  "duration_ms": 0,
  "cost_usd": null,
  "subtype": null,
  "errors": [],
  "denials": []
}
```

`engine` and `status` are required strings.

`engine_version`, `duration_ms`, `cost_usd`, and `subtype` may be null when the runner does not expose them.

`result` must be a string, while `errors` and `denials` must be arrays.

The normalized envelope intentionally excludes runner-native fields from the calling-session contract.

## Adding a runner

Add `scripts/adapters/NAME.sh` and a runner reference under `references/runners/`.

Keep runner-specific commands, policy paths, permission behavior, and output mapping in that runner reference.

Add the adapter to `scripts/adapters/supported` only after RC7 passes.
