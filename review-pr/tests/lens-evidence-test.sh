#!/usr/bin/env bash
# Offline: replay the recorded quality assessments for each supported adapter.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
while IFS= read -r runner; do
  [ -n "$runner" ] || continue
  python3 "$ROOT/tests/score-lens.py" "$ROOT/tests/evidence/lens/$runner/semantic-v1"
done < "$ROOT/scripts/adapters/supported"
