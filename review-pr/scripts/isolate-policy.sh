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

# R3.3 — computed before any change so the report reflects the PR, not our edits.
changes="$(
  while IFS= read -r -d '' p; do if is_policy_path "$p"; then printf '%s\0' "$p"; fi; done < <(g diff -z --name-only "$BASE" "$HEAD") \
    | jq -Rs -c 'split("\u0000") | map(select(length > 0))'
)"

# R3.1 — remove every policy path the head commit carries (any depth), plus the root policy
# directories, then check out every policy path that exists at base. The working tree is the
# head commit, so ls-tree of HEAD_SHA enumerates exactly what is on disk.
while IFS= read -r -d '' p; do rm -f "${DIR:?}/$p"; done < <(policy_paths "$DIR" "$HEAD")
for p in "${POLICY_ROOT[@]}"; do rm -rf "${DIR:?}/$p"; done
BASE_PATHS=()
while IFS= read -r -d '' p; do BASE_PATHS+=("$p"); done < <(policy_paths "$DIR" "$BASE")
if [ "${#BASE_PATHS[@]}" -gt 0 ]; then
  # git_wt: the checkout runs with the head's .gitattributes in place; no caller-configured filter may run.
  git_wt -C "$DIR" checkout -q "$BASE" -- "${BASE_PATHS[@]}"
fi

# R3.2 — unconditional.
rm -f "$DIR/.claude/settings.json" "$DIR/.claude/settings.local.json" "$DIR/.mcp.json"

printf '%s\n' "$changes"
