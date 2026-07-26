# agent-friendly-mcp — critical review (Claude Opus 5 + Codex + fable, 2026-07-26)

Three passes. Claude (network access, verified spec claims live), Codex (repo-only, read all 8 files
plus `tests/runs/` artifacts), then a fable-model pass reviewing **the findings themselves**, which
corrected or demoted seven of the twenty. This document is the post-correction version; retracted
claims are kept visible rather than deleted, since some were confident and wrong.

**Headline:** the skill's MCP facts are accurate. Annotation defaults, native field lists per record
type, the task lifecycle MUST/SHOULD NOT rules, `-32002`, `client.capabilities.elicitation.{form,url}`,
and the RC forecast all verify. No factual protocol error was found by any pass. The defects are
**currency**, **example/rule consistency**, and two narrow gaps in what the tests enforce.

Source key: **[Cl]** Claude · **[Cx]** Codex · **[F]** fable correction

---

## Retracted or materially corrected

These were in the first version. They do not hold as stated.

- **"The test suite has no negative control" — retracted [F].** `test_validate_fixture.py` contains
  14 tests, **13 of which are deliberate mutations that must produce issues**: wrong enum, `isError:
  false`, dropped envelope, malformed degraded carrier, missing content fallback, and both
  `retry_after_ms` cross-field invariants the schema alone would permit. The instrument is
  calibrated. My error: I ran pytest, saw 14 green, and never opened the test file — the exact
  failure of examining an instrument before trusting a result.
- **"The fixture ships a repair object that violates §6" — retracted [F].** The *wire* repair
  (`github_issues.json:71–76`) is fully conformant: `{next_step, tool, arguments, alternative}`.
  `inject_error` is harness metadata, and its `{code, repair:{tool}}` shape follows the skill's own
  worked fixture at `design-workflow.md:169`. Category error on my part.
- **"'Still subject to change' is already false" — retracted [F].** The RC blog frames the ten-week
  window as time for SDK and client implementers "to validate the changes against real workloads,"
  so changes may still land. `SKILL.md:14` is accurate as written.
- **`SKILL.md:32` "drops the condition" — retracted [F].** The same sentence ends "selective
  on-demand loading is a client-dependent optimization layered on top" — the §2 qualification is
  retained.
- **`SKILL.md:78` "claims the map does not restate the rules eight lines below a block that does" —
  retracted [F].** "This index" scopes to the Checklist Map table, which indeed does not restate.
  The single-authority tension with Core Standard is real; the contradiction was manufactured.
- **`SKILL.md:28` Step 8 mis-pointer — retracted [F].** The pointer attaches to "measure both," and
  the measurements *are* defined in Step 8.
- **`SKILL.md:67` skills-over-MCP pointer — mostly retracted [F].** It is named in the draft's
  extension list but links to a working-group charter; SEP-2640 is In Review and the repo is still
  `experimental-ext-skills`. "Experimental — revisit when stable" is substantially correct.
- **`examples.md:165` "asserts the property the JSON breaks" — retracted [F].** Line 165 asserts the
  strict *field*-subset property, which the JSON satisfies. The broken invariant is row count, a
  different rule.

---

## Major

### 1. The 2026-07-28 revision supersedes far more of this skill than its forward-compat notes cover **[Cl, corrected by F]**

Confirmed against the official draft changelog (`/specification/draft/changelog`), not inference.
Item 6 (SEP-2663) verbatim: the tasks extension "replaces the blocking `tasks/result` method with
polling via `tasks/get` and a new `tasks/update` for client-to-server input, removes `tasks/list`,
and allows servers to return task handles unsolicited without per-request opt-in."

`SKILL.md:15` already names server-directed creation, `tasks/update`, and `tasks/list` removal —
credit where due, and it shrinks this finding. What it does not name, and what §7 teaches as settled:

| §7 teaches | 2026-07-28 |
| --- | --- |
| `tasks/result` blocks until terminal, returns the underlying result | **removed**; `tasks/get` carries `result`/`error` |
| `execution.taskSupport` per tool | **removed**; unsolicited server-returned handles |
| `input_required` → hold `tasks/result` open; input arrives as a separate server→client request (`contract-checklist.md:508`, "**The native path is fixed**") | `inputRequests` on `tasks/get`, answered by `tasks/update` |
| `ttl`, `pollInterval`, `notifications/tasks/status` | `ttlMs`, `pollIntervalMs`, `notifications/tasks` via `subscriptions/listen` |

**The blast radius is wider than §7.** The changelog also lands, all touching rules this skill states:

- **`initialize` removed** (item 2); capabilities travel per request in `_meta`. §1's "record
  negotiated capabilities during initialization" and `SKILL.md:27`'s "gate … on the initialized
  capabilities" both lose their mechanism.
- **`server/discover` added as a MUST** (item 3) — a new, mandatory discovery surface §2 doesn't know about.
- **`resources/subscribe`/`unsubscribe` replaced by `subscriptions/listen`** (item 4) — §4's
  subscription rules and `examples.md` §5b are superseded wholesale.
- **`notifications/roots/list_changed` removed** (item 5) — `contract-checklist.md:63` instructs
  authors to handle it.
- **Every result carries a required `resultType`** (item 8).
- **`ttlMs` + `cacheScope` become required** on `tools/list`, `prompts/list`, `resources/list`,
  `resources/read`, `resources/templates/list` (Minor 5) — native caching that overlaps §9's
  fingerprint rationale.
- **Deterministic `tools/list` ordering becomes a spec SHOULD** (Minor 3) — the skill's §9 house rule
  is now protocol, and should be re-cited as such.
- **`outputSchema` loosened to any 2020-12 keyword; `structuredContent` to any JSON value** (Minor 10)
  — bears directly on §3's portable-constructs rule and the outputSchema-scope position.
- **Error-code allocation policy** (Minor 12): `-32000..-32019` implementation-defined, `-32020..-32099`
  reserved for MCP, with renumbering. §6's code advice should reference it.
- **MRTR (SEP-2322, item 7)** replaces server-initiated `elicitation/create` / `roots/list` /
  `sampling/createMessage` entirely with `InputRequiredResult` + retry.

**Fix — and the first version got this wrong [F].** Do **not** gate on `protocolVersion`: extensions
version independently of the spec, so task behavior follows *extension negotiation*
(`io.modelcontextprotocol/tasks` in `capabilities.extensions`), not the revision date. The load-time
rule must branch on what the peer negotiated. Add a Step 0 to `design-workflow.md` asking which
revision **and which extensions** the target client speaks.

**Timing [F].** This is not a Tuesday emergency — it is the opposite. The final text publishes in two
days and the RC may still shift; rewriting §7/§1/§2/§4 against RC text now means doing it twice.
Schedule this deliberately *after* 2026-07-28, against final text. Nothing breaks in the interim: the
current baseline is still the current baseline.

### 2. The flagship example's description contradicts its own schema **[Cx]**

`examples.md:34` — "DMs to users require a `user_id`" — but the schema (38–68) has no `user_id`;
`channel_id` is `^[CDG][A-Z0-9]{8,}$`, so a DM needs a **D-prefixed `channel_id`**.

This is the failure `design-workflow.md:190` tells auditors to hunt, in the example the skill offers
as its model of a coherent contract. *Softened [F]:* line 43 already says `channel_id` accepts
"DM id (D…)", so the charitable reading is compressed prose — "you need a `user_id` *to resolve* the
DM channel." Still worth fixing, because the compression is exactly what an agent would copy.

**Fix.** Say `slack_lookup_user` returns a D-prefixed `channel_id` this schema accepts.

### 3. The detail-toggle example violates the invariant it illustrates **[Cx]**

`examples.md:112–163`: concise returns **two** messages, `detail: "full"` returns **one**.
`contract-checklist.md:533` — "Detail toggles change field density, never row count."
**Fix:** same item set and cursor in both blocks; vary only field density.

### 4. "Adding optional fields is safe" contradicts the closed-schema mandate **[Cx]**

`contract-checklist.md:610` vs `:181`, with no carve-out nearby. A client that cached a closed
`outputSchema` rejects a newly added optional output field — exactly the pinning client §9 protects.
The spec confirms clients SHOULD validate `structuredContent` against `outputSchema`.
**Fix:** qualify by direction — optional *input* additions are additive; *output* additions are safe
only for tolerant clients or after rediscovery. Bump the fingerprint either way.

*(Both later passes rated this the cleanest single catch in the review.)*

### 5. §6's "JSON-RPC errors are reserved for non-tool methods" never names `-32042` **[Cl, remedy corrected by F]**

`contract-checklist.md:430`. Under the current baseline, `-32042 URLElicitationRequiredError` is
MUST-grade for elicitation-gated calls and is reachable from `tools/call` (the spec's own flow
diagram shows it). It greps to **zero hits** in the skill.

*Corrected [F]:* the rule reserves JSON-RPC errors for "transport, **protocol**, and non-tool RPC
methods," and an elicitation gate is arguably protocol-level — so the rule text doesn't strictly
force the wrong behavior. The genuine gap is that `-32042` is never named at all.

**Fix — and the first version got this wrong [F].** Name `-32042`, but do **not** reference
`notifications/elicitation/complete`: the draft removes it *and* `elicitationId` (Minor 11), because
MRTR replaces the whole server-initiated-request model. Name the code; leave the retry mechanism to
the #1 pass.

### 6. §7 never couples tool-result errors to task status **[Cl]**

Spec: "when the tool result has `isError` set to `true`, the task should reach `failed` status";
`tasks/get` SHOULD carry diagnostics in `statusMessage`. `isError` appears only in §3/§6 of the
checklist — never in §7. A conforming-looking server can sit at `completed` with an `isError: true`
result, and clients branching on task status miss the failure. Verified clean by all three passes.

### 7. Normative rules have more than one home **[both, narrowed by F]**

`AGENTS.md`: "A normative rule has exactly one home." `SKILL.md:20–33` (Core Standard) restates
§3:194, §3:209, §3:258, §2:89–99. Codex counted 65 `outputSchema`/`structuredContent` and 22
pagination-field mentions across prose, workflows, examples, and tests.

*Narrowed [F]:* three of the four "drift instances" in the first version were wrong (see Retracted).
The one that survives: `execution.taskSupport`'s value enum appears in `contract-checklist.md:496`,
`design-workflow.md:132`, and `vocabulary.md:19` — and **all three omit the default** (see #10).
That is the drift mechanism working exactly as AGENTS.md predicts.

**Fix.** Give checklist rules stable IDs; make Core Standard non-normative framing or pointers.

---

## Minor

8. **Design-workflow Step 9 has no `not-run` path [Cx, narrowed by F].** `review-workflow.md` has one
   (lines 7, 30); `design-workflow.md` doesn't. *Narrowed:* Step 8's output is *authorable* without a
   host — a suite is fixtures plus assertions. The unsatisfiable demand is Step 9's "eval-measured
   improvement against the prior baseline." And `design-workflow.md:181` was mischaracterized: it's a
   blame-assignment rule (don't dismiss failures as flakiness), not a demand to run without a host.
   *(The evidence gates on the §3 stringified-argument shim and §2 retrieval phrasing are good design
   and should stay — those rules correctly do nothing without captures.)*
9. **Prompt-argument encoding [Cx].** `examples.md:282–283` describes `channels` as an array and `pin`
   as a Boolean, but `prompts/get` carries `arguments` as `{[key: string]: string}`. The skill knows
   this (`examples.md:307`), but gives no encoding — so agents will send a JSON array.
10. **`execution.taskSupport` default is `"forbidden"` [Cl].** Never stated in any of its three homes.
    The skill teaches that "an omitted annotation is not neutral"; the same is owed here — omitting the
    field silently disables the task design.
11. **`Task.ttl` is `number | null` [Cl].** `native-wire-shapes.md:83` says only "milliseconds."
    `null` means unlimited retention — a §1 state-handle question.
12. **DCR deprecation missing [Cl].** §1:67 is good on resource indicators and step-up scopes, but
    Dynamic Client Registration is Deprecated with Client ID Metadata Documents as the migration.
13. **`SKILL.md:15` overstates the extensions framework [Cx].** It says the RC "gives the convention
    metadata below an official home." Extensions need a reverse-DNS id, their own spec, and
    negotiation — a house `_meta` key does not become one. Say *migration path*, not ratification.
14. **Notation collision [Cx, widened by F].** `SKILL.md:51` cites ex§3 for the `_meta` pattern (ex§3
    has none; its own line 208 defers to §4). `examples.md:465`'s bare "(see §1)" collides with
    `SKILL.md:80`'s "bare `§N` **always** means contract-checklist." *Widened:* the collision is
    systematic (`examples.md:208` does it too), so reconcile the notation rule with examples.md's
    internal convention rather than patching one line.
15. **Validator under-enforcement [Cx, demoted from Major by F].** `validate()` reads only
    `fixture["wire"]`; `error_schema` is `additionalProperties: true` with a `repair` subschema
    requiring only `next_step`; the JSON-RPC `error.data` carrier — one of §6's two — is never
    exercised. Real, but narrow: the suite's 13 mutation tests do calibrate what it *does* cover.
16. **`review-workflow.md:24` severity calibration [Cx, reframed by F].** *Not* a self-contradiction:
    a verified absence is evidence, and the rule already escalates upward for broad surfaces. The
    kernel is that it never scales *down* — a one-tool server still starts at Major.
17. **Stability/deprecation `_meta` shape [Cx, demoted from Major by F].** §9:620's "part of its
    discovery record" points at §2, whose discovery records include convention surfaces — where the
    examples *do* carry `stability` (603–631) and `deprecation` (684–733). `SKILL.md:48` already
    dictates `_meta` placement on native records. Residue: native-list-only clients see no tier; an
    explicit `_meta` shape would help.
18. **"Wire-valid" claim scope [Cx, demoted from Major by F].** `SKILL.md:50` defines the term by its
    own colon — "never as a top-level field **on a native record**." Neither flagged block is a native
    record (`249–261` is resource body content; `1074–1091` is a `structuredContent` payload, the same
    convention as ex§2/ex§2a, which the first version did not flag — inconsistent application).
    Residue: add envelope labels, and add `resources/read`/`prompts/get` to `native-wire-shapes.md` —
    the two surfaces where the example defects landed.

## Nit

19. **Unreachable evidence pointer [Cl].** Nine `tests/scenarios.md` rows cite tree `a3cd37f`;
    `git branch -a --contains` matches nothing. Cite the merge commit. *(Substance is fine — `git diff
    a3cd37f..HEAD -- SKILL.md references/` is empty, so the results do reflect the current text.)*
20. **Scenario 1 A9 scoring [Cx, softened by F].** `tests/runs/2026-07-11-scenario1-with-skill.md:24`
    marks A9 PASS while noting "not all 7 tools show an `outputSchema` block." *Softened:* the
    shortfall is disclosed **in the scoring cell**, with a rationale and a proposed stricter future
    scenario — a documented judgment call on one of nine criteria, not concealment. Make A9 per-tool
    next time; the first version's "the headline 9/9 rests on" overstated it.

---

## Contested — resolved

**`readOnlyHint` on a filesystem-writing tool** (`contract-checklist.md:219–230`, `examples.md:1052–1101`).

Codex rated this Major and wanted the observable-scope reading removed. Both later passes disagree,
and fable strengthened the defense: the skill labels it a deliberate reading of an ambiguous hint,
requires the server to document which reading it uses, requires cross-tool consistency, names the
auto-approval concern itself at line 281 — and `contract-checklist.md:226` **already makes
resource/resource-link delivery the default rule**, not the closing aside I cited. Codex's position
is further weakened by the spec's own stance that annotations are untrusted hints (mirrored at
checklist:232) and by `review-workflow.md:12` already rating `readOnlyHint: true` on shared/persistent
mutation as Critical.

**Verdict: keep the reading.** One worthwhile edit — state the auto-approval consequence inside the
rule at 219–222, not only in the anti-pattern below it.

---

## How the three passes diverged

Codex found what the files contradict about themselves (#2, #3, #4, #18) — it had no network and
accepted the skill's RC framing wholesale. I found what the files get wrong about the world (#1, #5,
#6, #12) but misread scope on the repo side and asserted an uncalibrated test suite without opening
the test file. Fable found what the *review* got wrong — seven corrections, including the two
retractions above, and the ordering argument that inverts the whole plan.

No pass alone produces this list, and the second review of the findings was worth more per token than
the first review of the skill.

---

## Recommended order (fable's, adopted)

1. **#2, #3, #14** — cheapest, highest per-line impact. Examples are what agents copy; no reason they
   wait behind a spec migration.
2. **#4** — a real trap, fixable in three lines.
3. **#5, #6, #10, #11, #12** — small, spec-confirmed contract gaps. For #5, name `-32042` and *omit*
   the completion-notification path.
4. **#1, reframed and rescheduled** — do it **after 2026-07-28**, against final text, branching on
   extension negotiation rather than protocol version. It is the one finding that gets cheaper and
   safer by waiting a week.
5. **#20, #15, #8, #7** — the evidence-base and structural passes, done deliberately.

The first version said "fix #1 first, everything else can wait." That was backwards.
