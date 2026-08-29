#!/usr/bin/env bash
# Offline: ensure_merge_base reaches the merge base of a PR with more than --depth commits (R2.3).
# The deepen fetches must name refs/pull/N/head: a plain `git fetch --deepen origin` follows only the
# clone's refs/heads/* refspec and never deepens the PR-only lineage, so only --unshallow would recover.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
U="$S/upstream"; mkdir -p "$U"
git -C "$U" init -q -b main; git -C "$U" config user.email t@example.com; git -C "$U" config user.name t
for i in 1 2 3 4 5; do echo "$i" > "$U/f"; git -C "$U" add f; git -C "$U" commit -qm "base $i"; done
git -C "$U" checkout -qb feat
for i in $(seq 1 80); do echo "p$i" > "$U/p"; git -C "$U" add p; git -C "$U" commit -qm "pr $i"; done   # 80 PR-only commits > depth 50
HEAD="$(git -C "$U" rev-parse HEAD)"
git -C "$U" update-ref refs/pull/7/head "$HEAD"
git -C "$U" checkout -q main
for i in 1 2 3; do echo "m$i" > "$U/m"; git -C "$U" add m; git -C "$U" commit -qm "main $i"; done
BASE="$(git -C "$U" rev-parse HEAD)"
git -C "$U" config uploadpack.allowReachableSHA1InWant true

C="$S/clone"
git clone -q --depth 50 "file://$U" "$C"
git -C "$C" fetch -q --depth 50 origin refs/pull/7/head
git -C "$C" merge-base "$BASE" "$HEAD" >/dev/null 2>&1 && { echo "FAIL: known positive — merge base already reachable at depth 50; the fixture does not exercise deepening"; FAIL=1; }

# Log every git invocation so the test can assert which fetch strategy succeeded.
SHIM="$S/bin"; mkdir -p "$SHIM"; LOG="$S/git.log"
printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$*" >> "%s"\nexec "%s" "$@"\n' "$LOG" "$(command -v git)" > "$SHIM/git"; chmod +x "$SHIM/git"
PATH="$SHIM:$PATH" ensure_merge_base "$C" "$BASE" "$HEAD" "refs/pull/7/head" || { echo "FAIL: ensure_merge_base failed"; FAIL=1; }
git -C "$C" merge-base "$BASE" "$HEAD" >/dev/null 2>&1 || { echo "FAIL: merge base still missing"; FAIL=1; }
grep -q -- '--unshallow' "$LOG" && { echo "FAIL: fell through to --unshallow; deepen did not reach the PR lineage:"; cat "$LOG"; FAIL=1; }
grep -q -- '--deepen=200.*refs/pull/7/head' "$LOG" || { echo "FAIL: deepen fetch did not name refs/pull/7/head:"; cat "$LOG"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "deepen-test: OK"
exit "$FAIL"
