#!/usr/bin/env bash
# Offline evidence replay; see lens-rubric.md.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SCORER="$ROOT/tests/score-lens.py"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
LENS_SHA256="$(shasum -a 256 "$ROOT/references/review-lens.md" | cut -d' ' -f1)"
FAIL=0
while IFS= read -r runner; do
  [ -n "$runner" ] || continue
  current=0
  for snapshot in "$ROOT/tests/evidence/lens/cases/"*/"$runner/"*; do
    [ -d "$snapshot" ] || continue
    python3 "$SCORER" "$snapshot" --gate
    [ "$(jq -r .lens_sha256 "$snapshot/run-config.json")" != "$LENS_SHA256" ] || current=$((current+1))
  done
  # A lens edit must arrive with evidence collected under it, for every supported runner.
  if [ "$current" = 0 ]; then
    echo "FAIL: no snapshot for $runner was collected with the current references/review-lens.md; collect a candidate snapshot (see lens-rubric.md)"
    FAIL=1
  else
    echo "lens-evidence-test: $runner has $current snapshot(s) under the current lens"
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
[ "$FAIL" = 0 ] && printf '%s\n' 'lens-evidence-test: OK'
exit "$FAIL"
