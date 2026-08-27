#!/usr/bin/env bash
# isolate-policy.sh DIR BASE_SHA HEAD_SHA
# Restores reviewer policy paths from BASE_SHA, deletes hook/MCP files, prints changed policy paths as JSON.
# Spec R3.1, R3.2, R3.3. Network-free.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"
need_cmd jq

[ "$#" -eq 3 ] || die 2 "usage: isolate-policy.sh DIR BASE_SHA HEAD_SHA"
DIR="$1"; BASE="$2"; HEAD="$3"
[ -d "$DIR/.git" ] || die 2 "not a git repository: $DIR"
g() { git -C "$DIR" "$@"; }

POLICY=(CLAUDE.md AGENTS.md .claude .mcp.json)

# R3.3 — computed before any change so the report reflects the PR, not our edits.
changes="$(g diff --name-only "$BASE" "$HEAD" -- "${POLICY[@]}" | jq -R . | jq -s -c .)"

# R3.1 — for each policy path: take base's version if it exists there, else remove head's.
for p in "${POLICY[@]}"; do
  if g cat-file -e "$BASE:$p" 2>/dev/null; then
    rm -rf "${DIR:?}/$p"
    g checkout -q "$BASE" -- "$p"
  else
    rm -rf "${DIR:?}/$p"
  fi
done

# R3.2 — unconditional.
rm -f "$DIR/.claude/settings.json" "$DIR/.claude/settings.local.json" "$DIR/.mcp.json"

printf '%s\n' "$changes"
