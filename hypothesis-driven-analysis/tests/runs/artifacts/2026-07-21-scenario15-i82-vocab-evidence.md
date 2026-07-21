# Evidence — issue #82 vocabulary gate (Fifteenth-wave companion), 2026-07-21

Three free with-skill Sonnet arms @ skill `9f48a9f` (S15 prompt) and ten decision-point probes (five @ SKILL.md `31b345e` pre-#84, five @ `9f48a9f`), dispatched 2026-07-21.
Every machine claim below is re-executed scorer output from the scoring session, not run self-report.
Transcripts and outputs snapshotted to scorer scratch (`i82/` under the session scratchpad); digests below.

## Digests (sha256)

```text
78f153ba3a20f2c1608c00544a122ef0795319db189984225a2e8d2d2791bbf1  i82-free-a.jsonl
f1f67f2a1eb0c174dec5a66d70b8311a2c03837d643e1561f61fe3f0a6cc8e80  i82-free-b.jsonl
4556b284500e2b49e92c523601343c4d9679e52ed8d6a0a3aac44f150f3bc3f7  i82-free-c.jsonl
5338bb49baed2d3185b2c2e0a0a2f6e4c0c376908729555bee5e5ec991dd134e  i82-probe-new-1.jsonl
b436fe850155978d9590062bbe65f476e5a9fe620b25329212c5a8474137c338  i82-probe-new-2.jsonl
52fa6bae109ff034a83fbaf061300ef3b5614927bafd001fb99970d2669f3a19  i82-probe-new-3.jsonl
f20947fa4b10438776e1e8d5b9f53341794c50a7b355e0bb9603a19b03cdd82e  i82-probe-new-4.jsonl
5f218e3714fe63597f9899006443d0ed8514fca015e67b7feb3754d92f7706b8  i82-probe-new-5.jsonl
6557f8bb39abead861a5c8a025830c7f165aeac464ea946bb98c7ca7a04d07d6  i82-probe-old-1.jsonl
b5a366d8d3e258554a21f325487b5a698cc5fadb0d69623746f10a69a9aa9ac9  i82-probe-old-2.jsonl
cbf1db8bbe68a6d0e8e700cef1fe2844e93690dd77b3fbcd72280c45b477194b  i82-probe-old-3.jsonl
f8ab3713e0df3f48824151aeccf6a5750f28b96aa9cd20f26eb21768754bd5e0  i82-probe-old-4.jsonl
21d8efe99e618b3c4a8569ba7724faafd6db48436361a7c0d43e3d307a1b8193  i82-probe-old-5.jsonl
24bc3ff066f53429a56ffdf70cde6ccffd020f0636aba793b46c4d99f1d25ceb  free-a/ledger.md
67c5ae613ffbc10f508a026a1ea661fb42258e0234671af6f60784ca1ce1a638  free-b/ledger.md
22395e947d8a70f744d75de07cc4c83e0cd3e55eb7c548bca4447c7811fc87dc  free-c/ledger.md
1f14107bf5a0973e25874ecf0d727b30a2754e6d50cfcd04a48e44a6ffb42224  probe-new-1/tables.md
fda5686ee88efb53de705d9af9fa121f69abdb7fb27d3bd208aff73ee55c51de  probe-new-2/tables.md
94c44a2f8ba7b3402affdfa7c39f2accd95a9141b6d5c475be0011e94fb91867  probe-new-3/tables.md
d31c0052175d1baa78c981a6f90e7d29e891707645a32c189bd90228ef9f98cc  probe-new-4/tables.md
e6b91028ffb6db81816fb5460fc6f831f8ec4677d46a870c289bd88abbe75ee2  probe-new-5/tables.md
f4072eae5cbfc6d48a06319155598c9e5bc67b7c9fced07f167532b5a67a7dd6  probe-old-1/tables.md
44325b4dbf7fddd9fbecfc69cc45502b0f5aeaed28be25726050c96c0bc459c1  probe-old-2/tables.md
e98f7e5b5142878c2940412b6db08e262254a9dd312f727ea2c9965508110cf8  probe-old-3/tables.md
796289bdd3ff4374c308d308f91476cd3ed2325ec5dbb64e6d3c47b8c5883cd1  probe-old-4/tables.md
b207310138128b6ffde7293b0f737fb0a58ec5faa691a9f6189bf6ba56811ef9  probe-old-5/tables.md
```

## score_ledger.py output, free arms (verbatim)

### free-a

```text
OK:
  - C1 checked and passed: 3 summary row(s) read, 0 REFUTED, none of them causal
  - C2 NOT CHECKED: no --plan supplied; status laundering was not verified
  - C3 NOT CHECKED: no --c3-unknown-source supplied; completeness-direction consistency was not verified
  - C4 NOT CHECKED: no --c4-positive-contradiction supplied; positive-contradiction adequacy was not verified
note: --plan omitted; C2 (status laundering) not checked
note: --c3-unknown-source omitted; C3 (completeness-direction) not checked
note: --c4-positive-contradiction omitted; C4 (positive-contradiction adequacy) not checked
exit: 0
```

### free-b

```text
OK:
  - C1 checked and passed: 4 summary row(s) read, 0 REFUTED, none of them causal
  - C2 NOT CHECKED: no --plan supplied; status laundering was not verified
  - C3 NOT CHECKED: no --c3-unknown-source supplied; completeness-direction consistency was not verified
  - C4 NOT CHECKED: no --c4-positive-contradiction supplied; positive-contradiction adequacy was not verified
note: --plan omitted; C2 (status laundering) not checked
note: --c3-unknown-source omitted; C3 (completeness-direction) not checked
note: --c4-positive-contradiction omitted; C4 (positive-contradiction adequacy) not checked
exit: 0
```

### free-c

```text
OK:
  - C1 checked and passed: 5 summary row(s) read, 0 REFUTED, none of them causal
  - C2 NOT CHECKED: no --plan supplied; status laundering was not verified
  - C3 NOT CHECKED: no --c3-unknown-source supplied; completeness-direction consistency was not verified
  - C4 NOT CHECKED: no --c4-positive-contradiction supplied; positive-contradiction adequacy was not verified
note: --plan omitted; C2 (status laundering) not checked
note: --c3-unknown-source omitted; C3 (completeness-direction) not checked
note: --c4-positive-contradiction omitted; C4 (positive-contradiction adequacy) not checked
exit: 0
```

## Known-positive mutation check

Exactly one cell of a copy of free-a's ledger — the Conclusion summary table's H1 claim cell — was set to `associative` (python string replace on that one row, count=1; an earlier address-less `sed` draft of this check changed two lines and was discarded).
Before/after diff, confirming a single changed line, then the same scorer:

```text
65c65
<   | H1 | causal | UNRESOLVED | necessary prediction failed under T1 (every severity stratum worse under Assist), but T1 is an exposure-outcome contrast from an unidentified before/after design and cannot by itself mark a causal hypothesis REFUTED; recorded as strong disconfirming evidence, not refutation |
---
>   | H1 | associative | UNRESOLVED | necessary prediction failed under T1 (every severity stratum worse under Assist), but T1 is an exposure-outcome contrast from an unidentified before/after design and cannot by itself mark a causal hypothesis REFUTED; recorded as strong disconfirming evidence, not refutation |
FAIL:
  - parse: final ledger: H1 has an unrecognized claim cell: 'associative' -- `associative` is conclusion wording (SKILL.md Conclusion), not a claim class; a non-causal explanation is `descriptive` or `data-artifact`
note: --plan omitted; C2 (status laundering) not checked
note: --c3-unknown-source omitted; C3 (completeness-direction) not checked
note: --c4-positive-contradiction omitted; C4 (positive-contradiction adequacy) not checked
exit: 1
```

## Free arms: Hypotheses and per-hypothesis summary tables (verbatim)

### free-a

Hypotheses:

  | id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | H1 | causal | The Assist workflow itself caused lower time-to-close / responder-minutes | improvement persists (or is not reversed) once severity mix is held fixed | improvement disappears or reverses once severity mix is held fixed | a real workflow effect should not require the incident mix to have also changed in Assist's favor at the exact same moment | T1 | incidents.csv, activity.csv, stratified by severity |
  | H2 | descriptive (estimand: share of the aggregate median/responder-minutes change attributable to the severity-mix shift vs. to within-stratum change) | The apparent aggregate improvement is a composition effect: the incident mix shifted toward faster/cheaper sev3 tickets in the Assist week | standardizing each week's stratum times to a common severity mix reverses or materially shrinks the raw aggregate gap | standardized comparison matches the raw comparison | the mix-standardized comparison must not still show net improvement for Assist if the raw gap is a pure composition artifact | T2 | incidents.csv, activity.csv, severity field, daily counts |
  | H3 | data-artifact | The Assist week's reported time-to-close and responder-minutes are optimistically biased by differential right-censoring of still-open incidents | unresolved-incident rate and censor duration differ sharply by workflow, concentrated in the harder severities | unresolved incidents are rare and symmetric across workflows, with durations comparable to the closed-incident range | the still-open incidents' elapsed time must not already exceed the entire closed-incident range if censoring is to plausibly bias the reported medians | T3 | incidents.csv, activity.csv (join for missing rows), extract timestamp |

Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction failed under T1 (every severity stratum worse under Assist), but T1 is an exposure-outcome contrast from an unidentified before/after design and cannot by itself mark a causal hypothesis REFUTED; recorded as strong disconfirming evidence, not refutation |
  | H2 | descriptive (estimand: composition share of the aggregate change) | UNRESOLVED | best supported — T2 CONSISTENT: mix-standardized comparison reproduces the entire raw gap without any Assist-specific improvement |
  | H3 | data-artifact | UNRESOLVED | best supported — T3 CONSISTENT: differential, severity-concentrated right-censoring far outside the closed-incident range, probed via coverage/missingness as the skill requires for a data-artifact claim |

### free-b

Hypotheses:

  | id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | H1 | causal | Assist caused faster recovery (the rollout claim) | within each severity tier, assist incidents close no slower than manual incidents | assist is slower within severity tiers | a majority of severity tiers must not show assist slower than manual | T1 | incidents.csv, activity.csv |
  | H2 | data-artifact | The aggregate median drop is a composition (severity-mix) shift, not a within-incident effect | reweighting assist's severity mix onto manual's per-severity times reproduces most/all of the observed drop | reweighting produces little to no drop | the reweighted counterfactual must sit at or below the observed manual median | T2 | incidents.csv, activity.csv |
  | H3 | data-artifact | Right-censoring (open, unresolved incidents excluded from "closed" stats) is concentrated in the Assist week and biases it to look better | assist week's open-incident share is higher than manual's, concentrated in severe tiers | open-incident share is flat across weeks/severities | assist week's open share must exceed manual's | T3 | incidents.csv, activity.csv |
  | H4 | causal | Concurrent operational changes at the same cutover (staffing increase, interruption spike) confound the before/after contrast | staffing/interruption metrics shift level exactly at the cutover, independent of severity mix | staffing/interruption metrics flat across the cutover | staffing/interruption metrics must show a synchronized step at the cutover | T4 | staffing.csv |

Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction contradicted in all three severity strata (T1), but the before/after contrast is not an identified causal design (no randomization, and H4 confirms concurrent confounds moved at the same boundary) — per the skill's rule, a contrast that doesn't identify the causal effect can worsen-looking-data without licensing REFUTED; reported as unsupported, not proven negative |
  | H2 | data-artifact | UNRESOLVED | best supported — T2 shows composition alone predicts a larger drop (436->196) than was observed (436->326.5), so the mix shift more than accounts for the headline number |
  | H3 | data-artifact | UNRESOLVED | best supported — T3 shows a 0.5%->4.8% jump in open/unresolved incidents at the cutover, concentrated in sev1 (36% still open), which excludes the hardest assist-week cases from the very "closed-incident" statistics being cited |
  | H4 | causal | UNRESOLVED | T4 confirms a real, synchronized confound (staffing +19%, interruption minutes up sharply) — this is a valid alternative explanation for any residual signal in either direction, and blocks a clean causal read of H1 |

### free-c

Hypotheses:

  | id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | H1 | causal | Assist caused faster time-to-close / lower responder-minutes | net of severity composition, assist incidents close faster / use fewer responder-minutes than manual in comparable incidents | assist incidents are flat or slower once severity is held constant | at least the well-powered severity strata must not be uniformly slower under assist — a true speed-up cannot manifest as slower-in-every-stratum | T1 (severity-stratified comparison + bootstrap CI) | incidents.csv, activity.csv |
  | H2 | descriptive (estimand: share of the aggregate median-ttc drop attributable to the severity-mix shift between the two weeks) | The aggregate "median fell" headline is a Simpson's-paradox artifact of a severity-mix shift that happens to land on the same calendar boundary as the workflow switch | standardizing assist week to manual week's severity mix reverses or erases the aggregate drop | standardizing leaves assist still faster | the mix-standardized assist figure must not still show assist faster, if the raw aggregate gap is mix-driven | T2 (direct standardization) | incidents.csv, activity.csv |
  | H3 | causal | A simultaneous staffing increase (headcount and scheduled hours rose ~15–20% at both service groups exactly at the cutover) is a rival driver of any throughput change, independent of Assist | staffing metrics step up at the same boundary as workflow | staffing flat across the boundary | staffing must not be flat across 06-07→06-08 for this rival to be viable | T3 (staffing time series inspection) | staffing.csv |
  | H4 | data-artifact | The activity extract right-censors incidents that have not yet closed, and this censoring falls disproportionately on the hardest (sev1) assist-week incidents, biasing the "closed" comparison in Assist's favor | sev1 closure rate (share with an activity row) is markedly lower in the assist week than the manual week | closure rates are comparable across weeks and severities | sev1 closure rate must not be uniform across weeks for this artifact to be real | T4 (closure-rate cross-tab by severity x workflow) | incidents.csv, activity.csv |
  | H5 | data-artifact (estimand: whether `responder_minutes` on closed incidents fully captures effort for incidents that reopen) | `responder_minutes` undercounts true effort on the hardest incidents because reopened tickets generate further unrecorded work, inflating apparent "hours saved" | 72h-reopen rate is markedly elevated for assist-week sev1 incidents vs manual-week sev1 | reopen rates are comparable | sev1 reopen rate must not spike under assist for this undercount concern to be live | T5 (reopen-rate cross-tab by severity x workflow) | activity.csv |

Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | no design here identifies Assist's causal effect (workflow, severity mix, and staffing all step at the identical boundary), so T1's contrary direction cannot formally REFUTE a causal claim per the skill's rule — but T1 gives zero supporting evidence in every adequately-sampled stratum, so H1 cannot be called "best supported" either |
  | H2 | descriptive | UNRESOLVED | best supported: T2 shows standardizing for severity composition reverses the raw aggregate gap |
  | H3 | causal | UNRESOLVED | best supported as a live confound: T3 confirms staffing stepped up at the same boundary as workflow; nothing in this data isolates its contribution from Assist's, so it remains an open rival, not a settled explanation |
  | H4 | data-artifact | UNRESOLVED | best supported: T4 confirms the closed-incident sample under-represents the hardest assist-week incidents |
  | H5 | data-artifact | UNRESOLVED | best supported: T5 confirms a 100%-vs-0% reopen-rate gap isolated to the one cell (sev1, assist) driving the "fastest" raw numbers |

## Probe arms: claim and status cell tallies

Extraction: rows matching `^\| *H\d` in each `probe-*/tables.md`, split on `|`, column 2 (claim) and column 3 tallied; the claim tally pools the Hypotheses and summary tables (both carry a claim cell).
In the column-3 tally, summary rows contribute their status cell and Hypotheses rows contribute candidate-explanation prose, so the machine-read status cells are exactly the `REFUTED`/`UNRESOLVED` entries.
Generator: `gen_evidence.py`, snapshotted beside the transcripts in scorer scratch.

```text
-- probe-new-1: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: severity-mix-standardized time-to-close)
-- probe-new-1: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery
   5  UNRESOLVED
   1  closed-only medians exclude Assist-week incidents under-represented in the extract (11 incidents opened in the Assist week have no closure record, concentrated in sev1)
   1  the headline decline is an aggregation artifact of the severity-mix shift (sev3 share 46.7%→73.3%)
   1  the same-day +18% staffing increase explains any apparent speedup
-- probe-new-2: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: case-mix-standardized median time-to-close)
-- probe-new-2: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery (a genuine reduction in time-to-close attributable to the workflow)
   1  Records under-represent the Assist week's hardest incidents: 11 incidents opened that week have no closure record in the extract, concentrated in sev1, so closed-only medians exclude them
   1  The +18% staffing increase landing the same day explains any apparent speedup
   1  The headline decline is an aggregation artifact of a severity-mix shift (sev3 share 46.7% to 73.3%)
   5  UNRESOLVED
-- probe-new-3: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: case-mix-standardized median time-to-close)
-- probe-new-3: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster incident recovery
   1  The +18% same-day staffing increase explains the apparent speedup
   1  The extract under-represents the Assist week's hardest incidents because still-open incidents are excluded from closed-only medians
   1  The headline decline is an aggregation artifact of the severity-mix shift toward sev3
   5  UNRESOLVED
-- probe-new-4: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: severity-mix-standardized median time-to-close)
-- probe-new-4: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster time-to-close
   1  Records under-represent the Assist week's hardest incidents: 11 incidents opened that week have no closure record in the extract
   1  The headline decline is a statistical artifact of a severity-mix shift (sev3 share 46.7%→73.3%)
   1  The same-day +18% staffing increase explains the apparent speedup
   5  UNRESOLVED
-- probe-new-5: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: severity-mix-standardized median time-to-close)
-- probe-new-5: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery (the cutover reduced time-to-close)
   5  UNRESOLVED
   1  closed-only medians exclude the Assist week's hardest incidents — 11 opened incidents have no closure record in the extract, concentrated in sev1
   1  the headline decline is an aggregation artifact of a severity-mix shift (sev3 share 46.7% to 73.3%)
   1  the same-day +18% staffing increase explains any apparent speedup
-- probe-old-1: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: case-mix-standardized median time-to-close)
-- probe-old-1: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery (time-to-close) for incidents in the cutover week
   1  Closed-only medians under-represent the Assist week's hardest incidents: 11 incidents opened that week have no closure record in the extract, concentrated in sev1
   1  The +18% same-day staffing increase, not Assist, explains the apparent speedup
   1  The headline decline is a statistical artifact of a severity-mix shift (more sev3, faster-closing incidents) that reverses under standardization
   5  UNRESOLVED
-- probe-old-2: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: severity-mix-standardized median time-to-close)
-- probe-old-2: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery (the 7.27h→5.44h median decline reflects genuine speedup)
   1  Closed-only medians under-represent the Assist week's hardest incidents (11 opened incidents have no closure record, concentrated in sev1)
   1  The headline decline is a case-mix (Simpson's-type) aggregation artifact of the sev3-share shift (46.7%→73.3%)
   1  The same-day +18% staffing increase explains the apparent speedup
   5  UNRESOLVED
-- probe-old-3: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: case-mix-standardized median time-to-close)
-- probe-old-3: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on genuinely difficult (sev1) incidents
   1  Assist caused faster incident recovery (lower time-to-close)
   1  Closed-only medians undercount the Assist week's hardest incidents: 11 incidents opened that week have no closure record in the extract, concentrated in sev1
   1  The +18% staffing increase landing the same day explains the apparent speedup
   1  The headline decline is an aggregation artifact of a severity-mix shift (sev3 share 46.7%→73.3%) toward faster-closing cases
   5  UNRESOLVED
-- probe-old-4: claim cells
   6  causal
   2  data-artifact
   2  descriptive (estimand: case-mix-standardized median time-to-close)
-- probe-old-4: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster recovery (the cutover reduced time-to-close)
   5  UNRESOLVED
   1  closed-only medians undercount the Assist week because incidents still open at extract time (concentrated in sev1) are excluded
   1  the +18% staffing increase (same-day as cutover) explains any apparent speedup
   1  the headline decline is an aggregation artifact of the severity-mix shift (sev3 share 46.7%→73.3%)
-- probe-old-5: claim cells
   6  causal
   2  data-artifact
   1  descriptive (estimand: case-mix-standardized median time-to-close)
   1  descriptive (estimand: case-mix-standardized median)
-- probe-old-5: column 3 (summary status + hypotheses prose)
   1  Assist adds burden on the genuinely difficult (sev1) incidents
   1  Assist caused faster time-to-close in the pilot week
   5  UNRESOLVED
   1  the extract under-represents the Assist week's hardest incidents: 11 incidents opened that week have no closure record, concentrated in sev1, so closed-only medians exclude them
   1  the headline decline is a Simpson's-paradox artifact of the sev3-share shift (46.7%→73.3%), not a genuine change
   1  the same-day +18% staffing increase, not Assist, explains any apparent speedup
```

Probe control (pre-#84): 0/5 drift in claim and status cells, so the probe fails known-positive validation and is non-discriminating; see the run record for the reading.
