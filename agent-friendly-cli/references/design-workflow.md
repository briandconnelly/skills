# Design Workflow

Use this workflow when creating a new CLI, redesigning a CLI surface, or writing a contract for a tool that agents will call.
Every rule the design must satisfy lives in [contract-checklist.md](contract-checklist.md).
This file orders the work and adds design-only guidance; where it names a checklist section it points at that section and does not restate its rules.

## 1. Model Tasks First

Define the smallest useful task model before choosing names, framework, or flags.

1. List the agent jobs the CLI must support.
2. Classify each job as `discover`, `inspect`, `query`, `mutate`, or `admin`.
3. Define the minimum input needed for each operation.
4. Define the minimum successful output needed for the next machine step.
5. Remove convenience wrappers around shell pipelines unless they provide a real contract advantage.

Prefer a few high-value verbs over a wide surface area.
If two commands require long prose to explain the difference, the command model is not ready.

## 2. Design A Guessable Command Surface

Apply [contract-checklist.md](contract-checklist.md) § Command Model, § Shell Safety, and § Prose Surfaces.
Draft the command tree and the primary selector for each resource before any flag, and check every sibling pair of commands against the task model from §1: if the two need prose to tell apart, merge or rename them.

## 3. Write The Schema Before Behavior

Write the schema before the implementation.
It declares every item in [contract-checklist.md](contract-checklist.md) § Machine Schema, plus the per-command declarations that § Stdin Contract, § Output, § Errors And Exit Codes, § Ambient State, and § Mutations And Long-Running Work require.

The schema and fingerprint endpoints to expose are defined in § Machine Schema.
Design-only addition: consider `tool schema --summary` or `tool schema <command>` so agents can load one command's contract without the whole document.

## 4. Choose Agent-Safe Defaults

Make the safe path the default path by satisfying [contract-checklist.md](contract-checklist.md) § Agent-Safe Invocation, § Ambient State, § Mutations And Long-Running Work, and § Side Effects And Telemetry at design time rather than retrofitting them.

Design for partial information:

- Provide `find` or `search` when exact identifiers are unrealistic.
- Return enough IDs, names, and disambiguating fields for the next refinement step.

## 5. Design Output And Errors Up Front

Declare each command's output and error contracts per [contract-checklist.md](contract-checklist.md) § Output and § Errors And Exit Codes before writing any renderer.
Write the example success and error payloads into the schema now; [examples.md](examples.md) shows the shapes to mimic.

## 6. Build For Testability

Use a result-then-render architecture:

- typed command inputs
- typed success payloads
- typed error payloads
- separate human renderer
- separate machine renderer

Lay out imports and startup so the metadata-path rule in [contract-checklist.md](contract-checklist.md) § Agent-Safe Invocation holds.

Ship the contract tests listed in [contract-checklist.md](contract-checklist.md) § Tests.
