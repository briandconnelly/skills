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

Design-only guidance the checklist does not state:

- Reuse the conventional verb set where semantics match: `list`, `get`, `find`, `create`, `update`, `delete`, `validate`.
- Pick one primary selector pattern per resource type: name, ID, path, query, or stdin.
- Use the conventional flag names where they fit: `--format`, `--limit`, `--filter`, `--timeout`, `--output`.
- Prefer named flags; reserve positional arguments for one obvious primary selector.

## 3. Write The Schema Before Behavior

Treat the schema as the authoritative design artifact and write it before the implementation.
It declares every item in [contract-checklist.md](contract-checklist.md) § Machine Schema, plus the per-command declarations that § Stdin Contract, § Output, § Errors And Exit Codes, § Ambient State, and § Mutations And Long-Running Work require.

Expose:

- `tool schema`: the authoritative full contract
- `tool schema --fingerprint`: the cache key whose contract is defined in § Machine Schema
- optionally `tool schema --summary` or `tool schema <command>` for compact partial loading

## 4. Choose Agent-Safe Defaults

Make the safe path the default path by satisfying [contract-checklist.md](contract-checklist.md) § Agent-Safe Invocation, § Ambient State, § Mutations And Long-Running Work, and § Side Effects And Telemetry at design time rather than retrofitting them.

Design for partial information:

- Provide `find` or `search` when exact identifiers are unrealistic.
- Return enough IDs, names, and disambiguating fields for the next refinement step.

## 5. Design Output And Errors Up Front

Choose each command's output class from the set defined in [SKILL.md](../SKILL.md) Vocabulary, then declare the output and error contracts per [contract-checklist.md](contract-checklist.md) § Output and § Errors And Exit Codes.
Write the example success and error payloads into the schema now; [examples.md](examples.md) shows the shapes to mimic.

## 6. Build For Testability

Use a result-then-render architecture:

- typed command inputs
- typed success payloads
- typed error payloads
- separate human renderer
- separate machine renderer

Keep metadata paths fast per [contract-checklist.md](contract-checklist.md) § Agent-Safe Invocation.

Ship the contract tests listed in [contract-checklist.md](contract-checklist.md) § Tests.
