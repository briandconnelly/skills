#!/usr/bin/env bash
# isolate-policy.sh RUNNER DIR BASE_SHA HEAD_SHA
# Implements RC4 from references/runner-contract.md with runner-owned policy definitions.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"
need_cmd jq

[ "$#" -eq 4 ] || die 2 "usage: isolate-policy.sh RUNNER DIR BASE_SHA HEAD_SHA"
RUNNER="$1"; DIR="$2"; BASE="$3"; HEAD="$4"
load_adapter "$RUNNER"
[ -d "$DIR/.git" ] || die 2 "not a git repository: $DIR"
g() { git -C "$DIR" "$@"; }

changes="$(
  while IFS= read -r -d '' p; do if adapter_is_policy_path "$p"; then printf '%s\0' "$p"; fi; done < <(g diff -z --name-only "$BASE" "$HEAD") \
    | jq -Rs -c 'split("\u0000") | map(select(length > 0))'
)"

while IFS= read -r -d '' p; do rm -f "${DIR:?}/$p"; done < <(policy_paths "$DIR" "$HEAD")
if [ "${#ADAPTER_POLICY_ROOTS[@]}" -gt 0 ]; then
  for p in "${ADAPTER_POLICY_ROOTS[@]}"; do rm -rf "${DIR:?}/$p"; done
fi
BASE_PATHS=()
while IFS= read -r -d '' p; do BASE_PATHS+=("$p"); done < <(policy_paths "$DIR" "$BASE")
if [ "${#BASE_PATHS[@]}" -gt 0 ]; then
  git_wt -C "$DIR" checkout -q "$BASE" -- "${BASE_PATHS[@]}"
fi

if [ "${#ADAPTER_ALWAYS_REMOVE[@]}" -gt 0 ]; then
  for p in "${ADAPTER_ALWAYS_REMOVE[@]}"; do rm -rf "${DIR:?}/$p"; done
fi

printf '%s\n' "$changes"
