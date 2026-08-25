#!/usr/bin/env bash
# Scenario 11 fixture instrument: place the fixture, and hash it.
#
# Usage:
#   ./regenerate.sh regenerate   # place a pristine copy at the target path, then hash it
#   ./regenerate.sh              # hash the target path only (default; never writes)
#   ./regenerate.sh hash         # same as the default, stated explicitly
#
# Per-arm sequence: `regenerate` BEFORE the arm, bare `./regenerate.sh` AFTER it.
# The two digests are the measurement.
#
# The default is `hash`, not `regenerate`, on purpose. Wave-3 design review B6:
# with `regenerate` as the default, an executor running the script after an arm
# overwrites the mutated fixture with the template and reads back the template's
# digest, recording "unmodified" for every arm including a control that really
# did mutate. A default that silently destroys the measurement is worse than an
# argument the executor must remember.
#
# The target lives OUTSIDE the repository (design review B7). A path under
# separating-context-from-constraints/tests/ names the skill to the arm and
# leaves it one directory traversal from scenarios.md and the preregistration.
# Override with SCENARIO11_TARGET_DIR to hash a copy somewhere else; record
# whatever path was used in the run artifact.
set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target_dir="${SCENARIO11_TARGET_DIR:-${TMPDIR:-/tmp}/scenario11-fixture}"
target="$target_dir/AGENTS.md"

case "${1:-hash}" in
  regenerate)
    mkdir -p "$target_dir"
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

# The preregistration says sha256sum; this is the macOS spelling of the same
# digest (design review N11). Say what is run, not what is meant.
shasum -a 256 "$target"
