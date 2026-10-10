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

# Resolve base policy symlinks from tree objects before removing or restoring anything (RC11):
# following one through the working tree would read its target from the head checkout.
WORK="$(mktemp -d "${TMPDIR:-/tmp}/review-pr-policy.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
policy_links "$DIR" "$BASE" > "$WORK/links"
LINK_TARGETS=()
while IFS= read -r -d '' _link && IFS= read -r -d '' target; do LINK_TARGETS+=("$target"); done < "$WORK/links"

# Compare from the merge base, like pr.diff: a policy file changed only on the base branch is not a PR change.
# Resolve it first so a missing merge base fails here instead of yielding an empty list.
MERGE_BASE="$(g merge-base "$BASE" "$HEAD")" || die 1 "no merge base for $BASE and $HEAD"
# A path under a base policy symlink's target is policy too: the reviewer reads its base copy at the link.
is_policy_change() {
  local t
  adapter_is_policy_path "$1" && return 0
  if [ "${#LINK_TARGETS[@]}" -gt 0 ]; then
    for t in "${LINK_TARGETS[@]}"; do case "$1" in "$t"|"$t"/*) return 0;; esac; done
  fi
  return 1
}
changes="$(
  while IFS= read -r -d '' p; do if is_policy_change "$p"; then printf '%s\0' "$p"; fi; done < <(g diff -z --name-only "$MERGE_BASE" "$HEAD") \
    | jq -Rs -c 'split("\u0000") | map(select(length > 0))'
)"

while IFS= read -r -d '' p; do rm -f "${DIR:?}/$p"; done < <(policy_paths "$DIR" "$HEAD")
if [ "${#ADAPTER_POLICY_ROOTS[@]}" -gt 0 ]; then
  for p in "${ADAPTER_POLICY_ROOTS[@]}"; do rm -rf "${DIR:?}/$p"; done
fi
# Restore through a private index so a symlinked policy path receives its target's base blobs; the
# repository's own index is left as checked out.
policy_index "$DIR" "$BASE" > "$WORK/records"
if [ -s "$WORK/records" ]; then
  GIT_INDEX_FILE="$WORK/index" git -C "$DIR" update-index -z --index-info < "$WORK/records"
  GIT_INDEX_FILE="$WORK/index" git_wt -C "$DIR" checkout-index -f -a
fi

if [ "${#ADAPTER_ALWAYS_REMOVE[@]}" -gt 0 ]; then
  for p in "${ADAPTER_ALWAYS_REMOVE[@]}"; do rm -rf "${DIR:?}/$p"; done
fi

printf '%s\n' "$changes"
