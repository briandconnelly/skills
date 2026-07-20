# c3-completeness fixtures

`entry-a.md` through `entry-f.md` are the six measured s15 arms' `Source
completeness semantics` Data Validity entries, copied verbatim (no
paraphrase) from the archived evidence artifact
`tests/runs/artifacts/2026-07-18-scenario15-completeness-evidence.md`:

- `entry-a.md`, `entry-b.md`, `entry-c.md` — arms a, b, c, quoted at
  `2026-07-18-scenario15-completeness-evidence.md:253`, `:257`, `:261`
  ("Verbatim `Source completeness semantics` entries" section).
- `entry-d.md`, `entry-e.md`, `entry-f.md` — arms d, e, f, quoted at
  `2026-07-18-scenario15-completeness-evidence.md:590`, `:594`, `:598`
  (the second "Verbatim `Source completeness semantics` entries" section,
  further down the same artifact).

Each file is a minimal `## Data Validity` section wrapping that arm's
original bullet, with only the artifact's `>` blockquote marker stripped so
it reads as a normal bullet — the bullet's own wording (including arm d's
`(S2 activity.csv)` parenthetical, which the other five arms did not write)
is untouched.

These are C3b **known positives**: every one of the six arms inferred an
event-status/direction reading for S2 from evidence the artifact's own
adjudication section rejects as insufficient (closure-status-invariant
evidence, a random-drop-only discriminator, a content statement misread as
a completeness guarantee, and so on) — none wrote the canonical
`S2: UNKNOWN — <why>` atom `check_c3b` requires. `test_c3_reconstructed_entries_fail_c3b`
in `test_score_ledger.py` asserts all six fail `check_c3b(md, "S2")`, i.e.
6/6, calibrating C3b's fail-closed behavior against the exact prose it was
built to catch.
