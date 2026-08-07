#!/usr/bin/env bash
# Regenerate the scenario 11 fixture and print its digest.
# Run this before every arm and again after it; the two digests are the measurement.
set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="$dir/AGENTS.md"

case "${1:-regenerate}" in
  regenerate)
    cp "$dir/AGENTS.md.template" "$target"
    ;;
  hash)
    ;;
  *)
    echo "usage: $0 [regenerate|hash]" >&2
    exit 2
    ;;
esac

if [ ! -f "$target" ]; then
  echo "fixture missing: $target" >&2
  exit 1
fi

shasum -a 256 "$target"
