# Runner adapter contract

A runner adapter connects the agent-neutral review workflow to one agent CLI.

The bundled adapters are executable shell libraries under `scripts/adapters/`.

## Required interface

An adapter must define these functions after it is sourced:

- `adapter_check` verifies the runner executable and every runner-specific prerequisite.
- `adapter_is_policy_path PATH` returns success when `PATH` is reviewer policy that must come from the base commit.
- `adapter_context_paths DIR TREEISH` emits the NUL-separated restored passive policy paths the adapter selects for the reviewer, chosen from `restored_policy_paths DIR TREEISH` so a symlinked policy path contributes its target's files (RC11); RC8 decides which selected paths the manifest lists.
- `adapter_build_command PROMPT LEVEL BUDGET TURNS EVIDENCE_DIR` sets the `ADAPTER_COMMAND` array to the complete child command.
- `adapter_normalize RAW_PATH EXIT OUTPUT_PATH` converts native output into the normalized result envelope below.

An adapter must define `ADAPTER_POLICY_ROOTS` as the root paths removed before base policy is restored.

An adapter must define `ADAPTER_ALWAYS_REMOVE` as the paths removed after restoration because they can execute code or attach external tools.

## Execution invariants

- RC1: The child must run with the checked-out repository as its working directory.
- RC2: The child must receive the review lens without runner-specific tool names.
- RC3: The child must be unable to modify files, access the network, start subagents, request approval, or load project-supplied executable configuration.
- RC4: Reviewer instructions and passive review resources must come from the pinned base commit rather than the pull-request head.
- RC5: The adapter must reject an unsupported review level rather than silently changing its meaning.
- RC6: The adapter must normalize native output into the result envelope before the calling session reads it.
- RC7: Each adapter reference must name its offline interface test, runner-backed hostile-fixture test, and multi-run review-quality gate, and every named gate must pass before the adapter is advertised as supported.
  A runner-backed gate that cannot run its runner exits 77 and prints `SKIP`; a skipped gate has not passed.
- RC8: The checkout must list every adapter-selected passive policy file in `policy-manifest.json` once per distinct base source, and the child must read every listed file before reviewing the diff.
  The base source of a restored path is the base-tree path its bytes come from: the path itself for an ordinary policy file, and the path under the target for a file restored under a link (a directory link `L -> T` restores `L/x` from `T/x`; a file link `L -> T` restores `L` from `T`).
  Among the selected destinations that share a source and survive `ADAPTER_ALWAYS_REMOVE`, the manifest lists the destination equal to the source when there is one, and otherwise the first in byte order (`LC_ALL=C`); it never lists the source as such, since a link target outside the adapter's policy keeps head content.
  Identity is the source path, not the blob: two base files with equal bytes at different paths are two entries.
  The manifest is sorted by byte order of the listed path, and sources are computed from base-tree link text alone, so nothing in the pull request influences which entry is listed.
  `context_paths_json` applies this rule to one adapter; a runner that unions several adapters' selections applies it across the union.
  The review lens instructs these reads, and each runner-backed hostile fixture checks that base-policy sentinels reach the child; individual review runs do not verify that every listed file was read.
- RC9: The checkout must fail before review when the policy manifest, counted after RC8's deduplication, exceeds `REVIEW_PR_MAX_POLICY_FILES`, which defaults to 40, rather than silently omitting policy or exhausting the child turn budget.
- RC10: A runner reference must document its command capability and whether filesystem reads are technically confined, while the review lens must limit commands to read-only inspection and forbid builds, tests, and other execution of repository code.
- RC11: A base policy file, passive resource, or adapter policy root that is a symlink qualifies only when its exact link text, resolved against the base tree alone, names a regular file or a directory inside that tree.
  The target must be reached only through directories, and a directory target must contain no symlink or submodule.
  The checkout must fail before policy restoration when any base policy symlink does not qualify.
  It restores a qualifying link as its target's base content at the link path and reports PR changes under the target as policy changes.
  Policy paths are classified byte-wise (`LC_ALL=C`), so a name that is not valid UTF-8 is still matched as policy.
  The checkout must fail when a policy path it reports, in `policy-manifest.json` or `policy_changes`, is not valid UTF-8, because JSON cannot name that file faithfully.

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
