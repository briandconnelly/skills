# Gate file format and semantics

The machine-readable contract between "I say it is done" and "it is done".
Both bundled scripts parse exactly this format; deviations are validation
errors at freeze time, not silent weaknesses.

## Format

```markdown
# Gates: <scope name>

## Criteria
- C1: <acceptance criterion, restated faithfully from the request>
- C2: <another criterion>

## Gates
- [ ] G1: <outcome, not activity>
  FOR: C1
  CHECK: <shell command>
  EXPECT: <substring or /regex/>
  CONTROL: required | exempt <reason>
  CONTROL_EXPECT: <optional: substring or /regex/ the pre-fix failure must print>
  EVIDENCE: pending

- [ ] G2: <manual outcome no command can decide>
  FOR: C2
  EVIDENCE: pending

ABANDON: G2 <reason — required; only when a gate must be visibly surrendered>
```

Rules the parser enforces:

- A gate line is `- [ ]` or `- [x]` with an `<id>:` prefix on the title. Ids
  must be unique across all frozen files.
- Indented `CHECK:` / `EXPECT:` / `EXIT:` / `FOR:` / `CONTROL:` /
  `CONTROL_EXPECT:` / `EVIDENCE:` lines up to the next gate belong to the gate
  above. Every gate must have an `EVIDENCE:` line.
- Every CHECK gate must have `CONTROL: required` or `CONTROL: exempt <reason>`;
  a bare `exempt` or any other value is rejected, as is CONTROL on a manual
  gate. `CONTROL_EXPECT` is optional and only meaningful with a CHECK.
- `EXPECT:` is a substring match against combined stdout+stderr, or a JavaScript
  regex when wrapped in slashes (`/8\/8 passed/`).
- A CHECK passes only when the exit status matches (default `0`, override with
  `EXIT: <n>`) **and** EXPECT matches, when present. A matching EXPECT never
  excuses a wrong exit status.
- If a `## Criteria` section exists, every gate needs a `FOR:` line naming real
  criteria, and every criterion must be covered by at least one gate. An
  uncovered criterion is silent scope-narrowing — freeze rejects it.
- `ABANDON: <id> <reason>` marks a visible surrender. It permits stopping as
  INCOMPLETE-HANDOFF; it never contributes to PROVEN. The id must name a
  frozen gate (from any frozen file — a driver may abandon a leaf gate), and a
  gate may be abandoned only once.
- A regex EXPECT must compile; freeze and amend reject one that does not.

## The manifest (freeze / amend)

`freeze` records every gate's spec (CHECK, EXPECT, EXIT, FOR) plus the criteria
map into `.completion-gates/manifest.json` and prints the commands it
authorizes — review them; they will be executed as shell. After freezing:

- `run` and `status` check the live files against the manifest as a whole and
  refuse on any mismatch: a gate whose CHECK/EXPECT/EXIT/FOR/CONTROL/CONTROL_EXPECT changed, a gate
  added or removed, a criterion added/removed/reworded, a duplicate id, or an
  ABANDON that names no gate.
- `amend --reason "<why>"` records a contract change as a revision
  `{at, reason, changes}`; change ops are `added`, `changed`, `removed`,
  `criterion-added`, `criterion-changed`, `criterion-removed`.
- `reset --reason "<why>"` replaces the contract. It appends a revision whose
  single change is `{op: "reset", previous: {frozen_at, files, criteria, gates}}`,
  keeps every prior revision, deletes `state.json` and `hook-state.json`, and
  moves `artifacts/` to `artifacts-reset-<timestamp>/`.
- `status` prints every revision under the ledger.
- Which of these is allowed when is governed by the escape rule in SKILL.md;
  this file describes mechanics only.

The manifest is auditable and safe to commit. `state.json`, `hook-state.json`,
and `artifacts/` are machine-local (a `.gitignore` covering them is written
into `.completion-gates/` at freeze).

## Evidence and staleness

`run` writes each CHECK's full output to `.completion-gates/artifacts/<id>.log`
and puts only metadata (pass/fail, exit, timestamp, artifact path) on the
markdown `EVIDENCE:` line — check output routinely contains secrets, and
tracked markdown plus pasted ledgers is how they leak. Quote from artifacts
selectively.

A passing run is stamped with a spec fingerprint (CHECK, EXPECT, EXIT,
CONTROL_EXPECT — not CONTROL, so waiving a control keeps the run) and a
workspace fingerprint (git HEAD + dirty-file list). If the spec is amended,
the old run resolves **unmet** ("spec amended since last run") — evidence
produced by a different command never satisfies the new one. When the workspace changes afterward, the gate shows **stale** and must
be re-run — evidence describes the workspace it was recorded against, not the
one you are reporting on. Outside git the tripwire is unavailable and status
says so.

Manual gates are **attested**, not proven: box checked by hand plus an
`EVIDENCE:` line holding actual proof (a measurement, quoted output, a
`file:line`). `pending` is unmet regardless of the checkbox — a checkbox is a
claim; evidence is the proof.

## Writing good gates

- **Outcomes, not activities.** "All 8 planets clickable" is checkable; "work
  on planet interaction" is not.
- **Prefer runnable gates.** A CHECK converts tokens of self-assessment into a
  free subprocess. If no CHECK exists, ask whether the outcome is observable at
  all; if not, sharpen the outcome.
- **Make EXPECT decisive.** Match the line that only appears on success
  (`8/8 passed`), never one that appears either way (`done`).
- **Prove sensitivity.** `control <id>` on the pre-fix state records whether
  the CHECK can fail. Outcomes: `ok` (did not pass; with `CONTROL_EXPECT`, also
  printed the expected failure), `insensitive` (already passed — shows
  nothing), `invalid` (timed out, could not run, exit 126/127, or failed
  without the expected signature — shows nothing). Every attempt is kept
  (`controls` in state; the ledger shows `(N attempts)`); the latest one
  counts. A control invalidates any earlier run, so evidence is always ordered
  control → fix → run. Each record carries the spec fingerprint (after an
  amend it shows `stale`) and the workspace fingerprint; `same-workspace`
  flags a control and passing run on identical files, i.e. a nondeterministic
  CHECK. `ok` means "did not pass", not "failed because the fix was missing" —
  use `CONTROL_EXPECT` when that distinction matters. Output goes to
  `artifacts/<id>.control.log`. A trivially-green CHECK (`echo ok`) is the
  gamed ledger this system exists to expose.
- **Waivers are visible.** Amending `CONTROL: required` to `exempt <reason>`
  is legal; the gate's row shows `control: waived rev N` and OVERALL counts
  waived gates. Which gates may be required or exempt is policy, owned by
  SKILL.md.
- **Numbers rule.** Any number destined for the final report gets its own gate
  with a CHECK that measures it. Reports written from memory get numbers wrong;
  measured runs of the ancestor project showed exactly this failure.

## Exit codes (gate-check.mjs)

| Code | Meaning |
|---|---|
| 0 | PROVEN — every gate proven or attested |
| 1 | INCOMPLETE — unmet or stale gates remain |
| 2 | Usage, parse, validation, or spec-drift error |
| 3 | INCOMPLETE-HANDOFF — abandons present, everything else proven |
