#!/usr/bin/env bash
# Offline evidence replay; see lens-rubric.md.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SCORER="$ROOT/tests/score-lens.py"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
while IFS= read -r runner; do
  [ -n "$runner" ] || continue
  found=false
  for snapshot in "$ROOT/tests/evidence/lens/cases/"*/"$runner/"*; do
    [ -d "$snapshot" ] || continue
    found=true
    python3 "$SCORER" "$snapshot" --gate
  done
  if [ "$found" = false ]; then
    echo "lens-evidence-test: NOTICE (no case snapshots yet for $runner)"
  fi
done < "$ROOT/scripts/adapters/supported"
for arm in claude/lens codex/lens baseline; do
  expected=4
  set --
  if [ "$arm" = baseline ]; then expected=3; set -- --whole-text; fi
  python3 "$SCORER" "$ROOT/tests/evidence/lens/$arm" --allow-overlap "$@" > "$S/scores.tsv"
  awk -F '\t' -v expected="$expected" '
    NR == 1 {if ($1 != "run" || $2 != "recall" || $3 != "decoys") exit 1; next}
    {if ($2 != expected || $3 != 0 || $4 != 0 || $5 != 0) exit 1; runs++}
    END {if (runs != 3) exit 1}
  ' "$S/scores.tsv"
  echo "lens-evidence-test: $arm OK (3 runs, recall $expected, decoys 0)"
done
printf '%s\n' 'lens-evidence-test: OK'
