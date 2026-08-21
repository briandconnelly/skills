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
  EVIDENCE: pending

- [ ] G2: <manual outcome no command can decide>
  FOR: C2
  EVIDENCE: pending

ABANDON: G2 <reason — required; only when a gate must be visibly surrendered>
```

Rules the parser enforces:

- A gate line is `- [ ]` or `- [x]` with an `<id>:` prefix on the title. Ids
  must be unique across all frozen files.
- Indented `CHECK:` / `EXPECT:` / `EXIT:` / `FOR:` / `EVIDENCE:` lines up to the
  next gate belong to the gate above. Every gate must have an `EVIDENCE:` line.
- `EXPECT:` is a substring match against combined stdout+stderr, or a JavaScript
  regex when wrapped in slashes (`/8\/8 passed/`).
- A CHECK passes only when the exit status matches (default `0`, override with
  `EXIT: <n>`) **and** EXPECT matches, when present. A matching EXPECT never
  excuses a wrong exit status.
- If a `## Criteria` section exists, every gate needs a `FOR:` line naming real
  criteria, and every criterion must be covered by at least one gate. An
  uncovered criterion is silent scope-narrowing — freeze rejects it.
- `ABANDON: <id> <reason>` marks a visible surrender. It permits stopping as
  INCOMPLETE-HANDOFF; it never contributes to PROVEN.

## The manifest (freeze / amend)

`freeze` records every gate's spec (CHECK, EXPECT, EXIT, FOR) plus the criteria
map into `.completion-gates/manifest.json` and prints the commands it
authorizes — review them; they will be executed as shell. After freezing:

- `run` executes only manifest gates, and refuses entirely on *spec drift*
  (a gate file whose CHECK/EXPECT/EXIT/FOR no longer matches the manifest).
- `amend --reason "<why>"` is the legitimate path for scope change: it appends
  a revision (timestamp, reason, per-gate diff) that reports must surface.

The manifest is auditable and safe to commit. `state.json`, `hook-state.json`,
and `artifacts/` are machine-local (a `.gitignore` covering them is written
into `.completion-gates/` at freeze).

## Evidence and staleness

`run` writes each CHECK's full output to `.completion-gates/artifacts/<id>.log`
and puts only metadata (pass/fail, exit, timestamp, artifact path) on the
markdown `EVIDENCE:` line — check output routinely contains secrets, and
tracked markdown plus pasted ledgers is how they leak. Quote from artifacts
selectively.

A passing run is stamped with a workspace fingerprint (git HEAD + dirty-file
list). When the workspace changes afterward, the gate shows **stale** and must
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
- **Prove sensitivity.** For a new CHECK, `control <id>` on the pre-fix state
  records that it can fail. A trivially-green CHECK (`echo ok`) is the gamed
  ledger this system exists to expose.
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
