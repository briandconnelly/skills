# Test Scenarios for agent-friendly-github

Behavioral test scenarios for this skill, following the baseline/with-skill methodology: run each scenario with a fresh subagent that does NOT have the skill loaded (baseline), then with the skill loaded (treatment), and compare against the assertions.
A baseline run that already satisfies every assertion means the scenario is too easy; tighten it.
An assertion the with-skill run misses is a finding against the skill, not against the agent.

## How to run

1. **Baseline:** dispatch a subagent with only the scenario prompt below.
   Record which assertions its output satisfies.
2. **Treatment:** dispatch a fresh subagent with the skill content available (or triggered via its description) and the same prompt.
3. **Score:** every assertion is pass/fail with a one-line evidence pointer into the transcript.
   Record results in the table at the bottom.

## Scenario 1: Set up (application test)

**Prompt:**

> You are configuring a GitHub repository so an AI coding agent can work in it safely.
> Facts: the repo is `acme/billing-api`, private, on the GitHub Team plan, with one active human maintainer.
> The AI agent currently authenticates with the maintainer's own user-account credentials; no separate agent identity exists yet.
> CI is GitHub Actions; the repo is a traditional (non-monorepo) Python service whose workflow file is named `CI` and contains a single job with id `test`.
> There are production deployments to a `production` environment.
> Deliverables: (1) the branch-protection/ruleset configuration you would apply RIGHT NOW, as JSON for the GitHub rulesets REST API; (2) the identity plan for the agent, and exactly what changes in the ruleset once that plan is carried out; (3) the Actions / supply-chain hardening list; (4) anything you would explicitly defer or mark not-applicable, with reasons.

**Assertions (with-skill run must satisfy):**

- [ ] Picks the solo profile and treats the current state as the pre-identity interim: `required_approving_review_count: 0` now, with the actor-independent gates carrying the load (Repository Profiles, solo interim posture).
- [ ] Keeps `bypass_actors` empty in the interim, with the agent-reachable-bypass rationale (§2).
- [ ] Plans a distinct identity (GitHub App preferred over fine-grained PAT over shared account) and flips reviews to >= 1 with a human `User` bypass actor in `pull_request` mode — never `always`/`exempt`, never the `Write` role — only after the identity exists (§2, §4).
- [ ] Required-check context is the job name (`test`), not the `CI / test` PR-UI string (examples.md, hardened ruleset).
- [ ] Sets `strict_required_status_checks_policy: true` (§2).
- [ ] Requires linear history, and blocks force-push and deletion (§2).
- [ ] Defers `required_signatures` as opt-in, with the App-token-local-commits-not-auto-signed rationale (§2, §4).
- [ ] Notes plan gating accurately: secret scanning/push protection and code scanning on a private Team-plan repo need GitHub Secret Protection / Code Security; environment required reviewers and wait timers on private repos are Enterprise-only → N/A or external alternative (Plan & Visibility Caveats).
- [ ] Lays down the productivity surface: canonical `AGENTS.md` with thin per-tool adapters, issue/PR templates, label taxonomy (§1, setup Step 4).
- [ ] Covers attribution: `Co-authored-by:` trailers when pairing, trailer survival through squash, distinct authorship for audit (§4).

**Expected baseline failures:** no linear-history/force-push/deletion rules, no instruction-file or template surface, no attribution/co-authorship plan, possible `CI / test` check-name mistake, fuzzy plan gating.

## Scenario 2: Audit (retrieval test)

**Prompt:**

> Audit this repository's readiness and security posture for AI-agent collaboration, and report your findings.
> You cannot run commands; you have only this captured material.
> The audience is the repository admin, who can change anything.
>
> Repo: `acme/payments` — private, GitHub Enterprise Cloud, 6 active human maintainers.
> An AI agent works the repo via the GitHub App `acme-agent-bot`.
>
> ```text
> $ gh api repos/acme/payments/rulesets
> [{"id": 42, "name": "main-protection", "target": "branch", "enforcement": "active"}]
>
> $ gh ruleset view 42
> main-protection (id 42), target: branch (~DEFAULT_BRANCH), enforcement: active
> bypass_actors: [{"actor_id": 510023, "actor_type": "Integration", "bypass_mode": "always"}]   <- this is the acme-agent-bot App
> rules:
>   pull_request: {required_approving_review_count: 1, dismiss_stale_reviews_on_push: false, require_code_owner_review: true, require_last_push_approval: false}
>   required_status_checks: {strict_required_status_checks_policy: false, required_status_checks: [{"context": "build"}]}
> (no deletion, non_fast_forward, or required_linear_history rules present)
> ```
>
> `.github/CODEOWNERS`:
> ```text
> *                 @acme/platform
> /payments-core/   @acme-agent-bot
> ```
>
> `.github/workflows/triage.yml`:
> ```yaml
> on: pull_request_target
> permissions: write-all
> jobs:
>   triage:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>         with:
>           ref: ${{ github.event.pull_request.head.sha }}
>       - run: |
>           echo "Triaging: ${{ github.event.pull_request.title }}"
>           ./scripts/triage.sh
>         env:
>           SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
> ```
>
> `.github/workflows/ci.yml` (workflow name: `ci`, single job id `build` — this is the job the required check refers to):
> ```yaml
> on:
>   pull_request:
>     paths:
>       - "src/**"
> jobs:
>   build:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>       - uses: actions/setup-node@main
>       - run: npm ci && npm test
> ```
>
> Notes from the admin: "The agent sometimes pushes straight to main when CI is slow — that's why we gave the App bypass. We set ACTIONS_STEP_DEBUG=true repo-wide to debug flaky tests. Agent commits show up authored as github-actions[bot]."

**Assertions (with-skill run must satisfy):**

- [ ] Findings carry the five labeled lines (Severity, Section, Threat, Evidence, Remediation) with §N and Tn references (Finding Format).
- [ ] Findings ordered Critical → Low (Audit Procedure step 4).
- [ ] Agent App in `bypass_actors` with `always` = Critical (§2, T4); remediation removes the automation identity rather than softening its mode.
- [ ] Agent listed in CODEOWNERS for `/payments-core/` = Critical (§1/§2, T3) — a required review the agent could satisfy itself.
- [ ] `pull_request_target` checkout-and-execute of head code with `write-all` + secrets = Critical (§3, T2), with the `env:`-binding fix for the title interpolation.
- [ ] `paths:`-filtered required check flagged: a skipped required check stays pending and blocks merge; remediation is the always-running gate (§2).
- [ ] `dismiss_stale_reviews_on_push: false`, missing linear-history/force-push/deletion rules, and non-strict checks flagged (§2; T3, T4, T8).
- [ ] Mutable action tags (`@v4`, `@main`) flagged (§3, T6).
- [ ] `ACTIONS_STEP_DEBUG` flagged with accurate framing — registered secrets stay masked; the risk is unregistered or derived values (§3, T5).
- [ ] `github-actions[bot]` authorship flagged as attribution loss → commit as the distinct App identity (§4, T8).
- [ ] Coverage table with one row per §1–§4 and `not-checked` reasons for items the captured material cannot answer (e.g., Dependabot, secret scanning, audit log).

**Expected baseline failures:** ad-hoc severity/format with no §/T references, no coverage table or `not-checked` discipline, debug logging framed as "secrets leak" without the masking nuance.

## Results

| Date | Scenario | Run | Assertions passed | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-09 | 1 (set up) | baseline | 7/10 | Strong on mechanics: reviews 0 in the interim with empty bypass, post-identity flip to 1 with `pull_request`-mode human bypass, job-name check context (`test`) with `integration_id` pin, strict checks, signing deferred with the App-token rationale, plan gating right (Secret Protection paid on Team; env reviewers Enterprise-only). Missed: no `required_linear_history` (and no deletion/non_fast_forward pairing rationale), no `AGENTS.md`/templates/labels surface at all, no attribution/co-authorship plan. |
| 2026-06-09 | 1 (set up) | with-skill | 9/10 | Solo pre-identity interim named and applied (reviews 0, empty bypass with inherited-bypass rationale); ruleset JSON matched the hardened example (context `test` with job-name-not-`CI / test` explanation, linear history, non_fast_forward, deletion, strict checks); identity plan flips reviews to 1 + human `User` bypass in `pull_request` mode, never `always`/`exempt`/`Write`; signing deferred with the App-token rationale; plan gating exact (Secret Protection / Code Security add-ons on Team, env reviewers Enterprise-only N/A); co-authorship trailers + squash survival covered. **Miss:** §1 productivity surface (canonical `AGENTS.md`, issue/PR templates, label taxonomy) never laid down or deferred — the run scoped itself to the four deliverable bullets and skipped setup Step 4; finding against the skill: Done Criteria compliance did not pull the full checklist walk into the output. |
| 2026-06-09 | 2 (audit) | baseline | 8/11 | Caught all three Criticals (bypass `always`, pwn-request with env-binding fix, agent in CODEOWNERS), stale reviews, paths-filter merge-block with always-running remediation, mutable tags, bot attribution. Missed: own ad-hoc format (no five labeled lines, no §N/Tn), no coverage table or `not-checked` discipline, debug logging framed as broad secret leakage with no masking nuance and rated Medium. |
| 2026-06-09 | 2 (audit) | with-skill | 11/11 | Findings F1–F12 each with the five labeled lines and §/T references, ordered Critical→Low; three Criticals match the severity scale's examples, and F1's remediation explicitly refuses softening to `pull_request`/`exempt` mode; F8 cites the pending-check trap with the always-running-gate remediation and ties it to the bypass habit; F7 uses the masked-vs-unregistered debug framing at High with justification; probe record covers all Critical-risk probes with `not-checked` reasons; coverage table rows §1–§4 with `not-checked` reasons for Dependabot, secret scanning, audit log, and PAT inventory. |
