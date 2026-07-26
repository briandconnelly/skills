# Comprehensive Review and Recommended Improvements: `hypothesis-driven-analysis` Skill

## 1. Executive Summary

The **Hypothesis-Driven Analysis** skill ([SKILL.md](file://.agents/skills/hypothesis-driven-analysis/SKILL.md)) is an exceptionally well-engineered, methodologically rigorous framework designed to guide AI agents through empirical investigations using the **PPDAC** (Problem, Plan, Data, Analysis, Conclusion) cycle and the scientific method.

The core value proposition of this skill is **eliminating cognitive biases common to LLM-driven investigations**, specifically:
1. **Confirmation bias & post-hoc rationalization**: Writing predictions down in an immutable ledger *before* observing cause-outcome relationships.
2. **Status laundering**: Preventing post-hoc promotion of exploratory guesses into "proven" causes without fresh data.
3. **Causal overclaiming**: Forcing strict adherence to causal identification requirements (counterfactual design vs. associative language).
4. **Unbounded fishing expeditions**: Enforcing explicit effort budgets, cost-aware collection plans, and non-transferable authorization gates.

---

## 2. Comprehensive Review of Current Skill Architecture

### Key Components
The skill consists of a core instruction file, specialized reference templates, subagent execution briefs, and an automated verification test suite:

```
hypothesis-driven-analysis/
├── SKILL.md                          # Primary skill definition and rules engine
├── references/
│   ├── ledger-template.md            # Immutable ledger templates & worked example
│   └── subagent-briefs.md            # Subagent isolation, schemas, & reconciliation rules
└── tests/
    ├── check_prereg.py               # Pre-registration transcript ordering auditor
    ├── score_ledger.py               # Automated ledger syntax & semantics evaluator
    ├── extract_evidence.py           # Transcript parser & evidence extractor
    └── scenarios.md                  # Test scenarios & empirical benchmark metered runs
```

### Key Strengths

1. **Inferential Routing Engine**
   - Routes by inferential shape (`direct`, `estimation`, `mini`, `full`) rather than arbitrary effort or data cost.
   - Treats unstated exposure assignment (e.g. *"we ran variants A and B"*) as unidentified causal by default, preventing unjustified assumptions of randomized designs.

2. **Pre-registration & Falsifiability Engine**
   - Mandates declaring a pre-registered *necessary prediction* (`failure refutes`) for every hypothesis before observing cause-outcome data.
   - Restricts hypothesis `status` to `REFUTED` or `UNRESOLVED`. The concept of "best supported" is basis text residing in the `basis` column, not a status value.
   - Retrospective hypotheses (formulated post-data touch) are explicitly tagged `retrospective` and can only be supported by previously unseen data slices.

3. **Data Validity & Coverage Rules**
   - Requires a crossed-grain coverage matrix (e.g. `hour × segment`) to prevent hidden dropouts sitting between aggregate healthy figures.
   - Explicitly handles absent records. Unless evidence proves whether an absence represents "event absent", "event unrecorded", or "export incomplete", source completeness is marked `UNKNOWN`, blocking directional missingness assumptions.

4. **Authorization & Subagent Guardrails**
   - Non-transferable authorization gate binding even headless execution.
   - Subagents are strictly read-only, barred from git mutations/worktrees, given exact data slices, and required to report per-test outcomes in a strict schema rather than making hypothesis-level conclusions.

5. **Automated Verification Infrastructure**
   - Includes Python scripts ([check_prereg.py](file://.agents/skills/hypothesis-driven-analysis/tests/check_prereg.py), [score_ledger.py](file://.agents/skills/hypothesis-driven-analysis/tests/score_ledger.py), [compare_prereg.py](file://.agents/skills/hypothesis-driven-analysis/tests/compare_prereg.py)) that programmatically verify transcript ordering and ledger semantic integrity.

---

## 3. Recommended Improvements

### 1. Integrate Runtime Self-Validation via Test Scripts
* **Observation**: The repository contains robust python verification scripts ([score_ledger.py](file://.agents/skills/hypothesis-driven-analysis/tests/score_ledger.py), [check_prereg.py](file://.agents/skills/hypothesis-driven-analysis/tests/check_prereg.py)). Currently, these are primarily used for offline benchmark scoring ([scenarios.md](file://.agents/skills/hypothesis-driven-analysis/tests/scenarios.md)).
* **Improvement**: Add an explicit self-validation directive in [SKILL.md](file://.agents/skills/hypothesis-driven-analysis/SKILL.md) instructing live execution agents to run `python tests/score_ledger.py scratch/ledger.md` (when scripts are present) to verify schema compliance before delivering final answers.

### 2. Emergency Operational Triage Fast-Path ("Mitigate First, Investigate Second")
* **Observation**: During active production outages (e.g., P0 incident), filling out a 20-line ledger before taking action can delay critical mitigations (e.g., rollback, failover).
* **Improvement**: Add an explicit operational fast-path exception: when responding to an active, ongoing incident, perform emergency mitigation first, and run the PPDAC root-cause analysis second once stability is restored.

### 3. Disambiguate Borderline Routing Edge Cases (`mini` vs. `full`)
* **Observation**: Agents struggle to distinguish single-claim check (`mini`) from multi-hypothesis diagnostics (`full`) when a user's prompt seeds a candidate cause (e.g. *"Did the 09:10 deploy cause the p95 spike?"* vs. *"Why did p95 spike? Was it the deploy?"*).
* **Improvement**: Clarify in [SKILL.md](file://.agents/skills/hypothesis-driven-analysis/SKILL.md) that an open question (*"Why did Y happen?"*) expands the candidate space to rivals and routes `full`, even if a candidate seed is named.

### 4. Subagent Resilience & Partial Failure Handling
* **Observation**: [subagent-briefs.md](file://.agents/skills/hypothesis-driven-analysis/references/subagent-briefs.md) specifies reconciliation for `NON_DISCRIMINATING` test results, but lacks explicit protocols for worker execution failures (timeouts, crashes, malformed outputs).
* **Improvement**: Define a **Worker Failure Protocol** in [subagent-briefs.md](file://.agents/skills/hypothesis-driven-analysis/references/subagent-briefs.md) instructing the main agent to mark affected test entries as `NON_DISCRIMINATING (worker execution failure)` and proceed with remaining workers.

### 5. Token Premium & Compact Ledger Optimization
* **Observation**: Benchmark runs in [scenarios.md](file://.agents/skills/hypothesis-driven-analysis/tests/scenarios.md) document token premiums of 11% to 138.4%+, largely caused by re-printing verbose markdown tables across intermediate steps.
* **Improvement**: Add compact formatting guidelines to [ledger-template.md](file://.agents/skills/hypothesis-driven-analysis/references/ledger-template.md) encouraging telegraphic cell descriptions and file-based updates to `scratch/ledger.md` rather than re-outputting full tables in conversation turns.

### 6. Guidance on Interactive Clarification vs. Autonomous Assumptions
* **Observation**: The instruction to *"Resolve ambiguity with the user here, where it is cheap"* can stall headless/autonomous pipelines if minor ambiguities trigger user prompts.
* **Improvement**: Establish a clear decision matrix differentiating non-blocking assumptions (e.g., assuming unidentified causal when assignment is unstated) from blocking pauses (e.g., missing authorization or completely unspecified targets).

---

## 4. Concrete Proposed Modifications

### Proposed Addition to `SKILL.md` (Self-Validation & Emergency Triage)

```markdown
### Self-Validation (when scripts are available)
Before finalizing the report, if `tests/score_ledger.py` exists in the workspace, execute:
`python tests/score_ledger.py scratch/ledger.md`
Resolve any reported structural or semantic errors before delivering the final response.

### Emergency Incident Mitigation (Fast-Path)
If responding to an active, ongoing operational outage where immediate action (e.g., rollback, failover) is required:
1. Execute the emergency mitigation first.
2. Once the system is stabilized, run the PPDAC investigation on historical data to determine root cause.
```

### Proposed Addition to `references/subagent-briefs.md` (Partial Worker Failures)

```markdown
## Partial Worker Failure Handling

If a dispatched worker times out, encounters an unrecoverable tool error, or returns an invalid schema:
1. Do not abort the investigation or stall the main loop.
2. Mark the corresponding test entry in the ledger as `NON_DISCRIMINATING (Worker Error: <reason>)`.
3. Proceed with reconciling remaining test results and include the worker failure in the final `Limitations` section.
```
