# Scenario 6 — necessary-prediction variant scope (issue #72), evidence

Measures the SKILL.md wording change for issue #72: a declared necessary prediction can encode a narrower mechanism (one variant) than the hypothesis it refutes, producing a false `REFUTED` of a general mechanism.
The change adds two clauses — Site 1 (status rule, variant-necessity) and Site 2 (sensitivity, positive-contradiction adequacy) — committed in `d2a2c5c`.

## The failure, and why a decision-point probe

The Eighth-wave close-out (`2026-07-18-scenario6-sensitivity-evidence.md`, §"Adjudication: ws-f's H4 refutation") recorded one run marking a retrospective "warm-up effect that decays across the 6-hour window" hypothesis `REFUTED` because the 6 slow events were not concentrated in the first third — a false refutation of the general mechanism, since a true decay with τ ≥ 2h fails that early-concentration criterion 32–53% of the time at n=6 (τ = 2–3h; see ground truth below).

A free-investigation before/after cannot measure this: the failure rides a **minority route** (the run must spontaneously raise the retrospective decay hypothesis *and* over-refute it). Three fresh free-investigation baseline arms (a/b/c) on the current wording confirmed this — **0 of 3 even raised** a retrospective decay/warm-up hypothesis; all three correctly answered `UNRESOLVED` on the median claim via the interval-first check. A clean post-edit free run would therefore prove nothing (the known positive never appears).

So the measurement is a **focused decision-point probe**: each clean-room arm is handed the retrospective hypothesis already on its ledger, its declared necessary prediction ("a majority of the 6 slow events fall in the first third, near-absent in the last third"), the observed timing (2 first / 3 middle / 1 last, one event near hour 4), and asked to assign the skill-dictated status. This removes the "does the arm spontaneously raise it" filter and tests the exact reasoning step the wording governs. Prompts are identical across the old-wording and new-wording batches; only the committed SKILL.md differs.

A **leading** variant of the probe (which additionally instructed "perform and show any sensitivity or adequacy check the skill requires") was run first and is reported below as a control: it scored 0/5 `REFUTED`, confirming the failure is specifically that arms do not *engage* an adequacy check on a positive contradiction — not that they cannot perform one.

## Ground truth (re-derived at scoring time, `gt.py`)

Computed directly from the shipped `s6-latency/latency_sample.csv` (n=41), not trusting any arm's arithmetic:

- Median 202.0ms; exact-binomial 95% CI **[177.6, 249.6]** (14th/27th order stats, coverage 0.956); the claimed +30ms (230) sits inside → `NON_DISCRIMINATING`. Sign test vs 230: p=0.117. (Matches the fixture's documented [177.6, 252.9] / p=0.117.)
- Variant-necessity instrument: for "≥4 of 6 slow events in the first third" under a truncated-exponential decay of the event rate over the 6h window, P(a true decay **fails** the criterion) = **0.035 at τ=1h, 0.322 at τ=2h, 0.533 at τ=3h**. For any decay slower than τ≈1h — fully compatible with "decays across the window" — the false-failure rate is far above the 5% complement of 95% coverage, so the criterion's failure refutes only fast decay, not the hypothesis. (Same shape as the Eighth-wave evidence's 0.061/0.388/0.582.)

## Results — before/after, identical neutral probe

| Batch | Wording | id/route | Verdict | Reading |
| --- | --- | --- | --- | --- |
| free-investigation a,b,c | old | full S6 investigation | 3× `UNRESOLVED` on median claim | 0/3 raised the retrospective decay hypothesis — minority route confirmed |
| leading probe 1–5 | old | decision point + "run the check" | **5× `UNRESOLVED`** | control: told to check, arms get it right; failure is check-skip, not check-failure |
| neutral probe 1–5 | old | decision point | **5× `REFUTED`** | **known positive** — every arm skipped adequacy on the positive contradiction |
| neutral probe 1–5 | new | decision point (same prompt) | **5× `UNRESOLVED`** | **fix** — every arm ran the Site 2 adequacy bound → `NON_DISCRIMINATING` |
| S1 over-correction 1–3 | new | deploy-timing decision point | **3× `REFUTED`** | legitimate deterministic refutation preserved — no over-correction |

**Headline: the identical neutral probe flips 5/5 `REFUTED` (old) → 5/5 `UNRESOLVED` (new), while a legitimate refutation control holds 3/3 `REFUTED`.**

### Verbatim — the known positive (old wording, neutral probe)

Every REFUTED arm stated the exact #72 defect. Representative:

> "This is a positive measurement (not a null result, so no known-positive sensitivity check applies), and it falsifies a preregistered necessary prediction that follows from H's own causal mechanism without relying on any unidentified exposure–outcome contrast, so REFUTED stands." — arm 1

> "All 6 events were measured directly — a full census, not a sample — so no sensitivity/known-positive check is triggered." — arm 2

Both gaps appear: the positive-contradiction route ("not a null … no check applies") and the variant route ("follows from H's own mechanism", no worst-case check).

### Verbatim — the fix (new wording, neutral probe)

Every arm engaged Site 2 and reached the correct outcome. Representative:

> "on fresh realizations of the whole 6-hour window, a genuinely decaying warm-up effect would still produce a split like 2/3/1 far more than 1 run in 20, because count variance at n=6 is large. That failure-under-truth rate exceeds the 5% complement of the 95% coverage level, so the test is NON_DISCRIMINATING, not a refutation." — arm 4

> "taking the worst case over the variants 'decays across the 6-hour window' permits, on fresh realizations of the whole window … the failure rate exceeds the 5% complement of the (unnamed → 95%) coverage level." — arm 1

The census escape (which two old-wording arms took) is explicitly closed: new-wording arms say "over only 6 draws" and "fresh realizations of the whole window", not "census".

### Verbatim — the over-correction control (new wording, S1 deploy)

The legitimate refutation still lands, justified by the deterministic escape Site 2 carries:

> "The prediction is deterministic, clearing the sensitivity discipline at a zero rate without simulation." — arm 1

> "A cause cannot follow its effect … the prediction is deterministic, so no known-positive/sensitivity simulation is needed." — arm 2

## Honest limits

- **Subtle over-correction is unmeasured.** S1's refutation is *flagrant* (deploy postdates the drop by two days). No fixture in the suite tests a *subtle* legitimate refutation (scenarios.md:641), which is where an over-cautious rule would bite; the S1 control rules out only gross over-correction.
- **The probe is not a free run.** It measures the reasoning step in isolation; it does not establish how often a free investigation reaches this decision point (the free arms show: rarely). The claim is "when at the decision point, the wording flips the verdict", not "the false REFUTED occurs at rate X in the wild".
- **Verdicts are one scorer's reading of the arms' own quoted reasoning**; the status tokens were emitted first-line by each arm. τ error rates assume exponential rate decay; the adjudication needs only that some decay compatible with the wording fails the criterion well above 5%, which τ ≥ 2h supplies.
- **Transcripts** live in scorer scratch and are not committed; the digests below authenticate any retained copy.

## Transcript digests (sha256, generated programmatically)

```
2443390dffecf7e11e9f7c6a3394a0e98396a9e77cfc617b2a1ccee0af42725f  s6-baseline/arm-a.jsonl
a4bf860722a9e2a01a013ac33c2c944cc8b01a0e38f5f23f21e46faaa8ab1227  s6-baseline/arm-b.jsonl
a5d8c57ead4de2c978f9ef49c1998b7cf63bb2560feb32845582028f7a0e4240  s6-baseline/arm-c.jsonl
3b45ea7001e3da4b9ae76fc547b10bb55110da59dd9e7588112032ce17a9f4a2  probe-old/arm-1.jsonl
1cbb14368c8dd3930d2c82ab2df84ccf1433cb6af97efd59d7f9de687691cd6b  probe-old/arm-2.jsonl
fc997d9d7f471929c64fe7dddce2dc01f5605b903035ce771ed15241d9d1722b  probe-old/arm-3.jsonl
c0e5bd266fefce7778f32f23e86cedb7e32bf6cae62d4d2a5d737831912c204e  probe-old/arm-4.jsonl
0ca07243289d539e2d9bf8ad73b9c34dd269587380bb2c2b26e4b994f0a21e54  probe-old/arm-5.jsonl
c1e180b16eca789c7993942339567d39ac2ac56f43a3cd2e47a611652b85edc9  probe-old-neutral/arm-1.jsonl
4992fcaf89ae8e3dc948ab1adebe16fbe34c5390fbadbbf038915f85253204fa  probe-old-neutral/arm-2.jsonl
40dcda7be77dcb1fc7ffec06c14d8eaa6bbb2f215787c714037c9cd13cc9e9f6  probe-old-neutral/arm-3.jsonl
ee197036e456a543e959022d5b96293204612a71453ee7b17fbee6e3b6628c2d  probe-old-neutral/arm-4.jsonl
97b0ed58a6db5f3b5237e4934dd2491889f5d73e676178ab3668281c697a53e0  probe-old-neutral/arm-5.jsonl
7aa3c3d1b44ed503e7cf2a91a6843d97a012ac4bcf58294cb0879ec8e5eacdfb  probe-new/arm-1.jsonl
aa7c125bbe6134289234e274e231e1b979598cc3d4e39bf256197c609f7f8476  probe-new/arm-2.jsonl
71c8d1271b63b10d8189bc9ddd9be70fb211b7d4846cd81c976f387490fe4dd3  probe-new/arm-3.jsonl
0ded97088256033f0b5b1e579cfbd5eec8ebfd97d4ba15b980e658bba8c8ecf4  probe-new/arm-4.jsonl
1b9409ac145ceb0e8086de95a6c20f4e7d4a92893d70e299860c92b09e73fa6d  probe-new/arm-5.jsonl
32759deef5b9ec24501461f494c451cb26512df6827fa8d64bba65173db1fe64  probe-s1/arm-1.jsonl
9d566721ca38e547f78fd951d0081f01a968aa961628348e504fb2958f97b222  probe-s1/arm-2.jsonl
9940c7397bb6dfc2f4b1a835ad6e1b0a2118940d8f57405f09b259a2a0191189  probe-s1/arm-3.jsonl
```
