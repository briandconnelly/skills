#!/usr/bin/env bash
# Live: checkout-pr.sh pins and clones a real PR for the selected adapter.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
if ! gh auth status >/dev/null 2>&1; then echo "checkout-pr-test: SKIP (gh not authenticated)"; exit 0; fi
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"
export REVIEW_PR_SCRATCH; REVIEW_PR_SCRATCH="$(mktemp -d)"; trap 'rm -rf "$REVIEW_PR_SCRATCH"' EXIT
SLUG=briandconnelly/cwms-tools; N=112

out="$("$SRC/checkout-pr.sh" "$SLUG" "$N")"
echo "$out" | jq -e . >/dev/null || { echo "FAIL: stdout is not one JSON object: $out"; exit 1; }
dir="$(jq -r .dir <<<"$out")"; head="$(jq -r .head_sha <<<"$out")"; base="$(jq -r .base_sha <<<"$out")"
clone="$dir/repo"
[ "$(jq -r .runner <<<"$out")" = claude ] || { echo "FAIL: default runner is not claude"; FAIL=1; }

# The clone is detached at the pinned head.
[ "$(git -C "$clone" rev-parse HEAD)" = "$head" ] || { echo "FAIL: HEAD != head_sha"; FAIL=1; }
git -C "$clone" symbolic-ref -q HEAD >/dev/null && { echo "FAIL: HEAD is not detached"; FAIL=1; }
# A later push is reported without making this live probe flaky.
gh_head="$(gh pr view "$N" -R "$SLUG" --json headRefOid -q .headRefOid)"
[ "$gh_head" = "$head" ] || echo "NOTE: PR head moved during test ($gh_head vs $head)"
# The merge base is available locally.
git -C "$clone" merge-base "$base" "$head" >/dev/null || { echo "FAIL: merge-base missing"; FAIL=1; }
# Stable local branch names point at the pinned commits.
[ "$(git -C "$clone" rev-parse "pr-$N")" = "$head" ] || { echo "FAIL: pr-$N branch"; FAIL=1; }
[ "$(git -C "$clone" rev-parse "pr-$N-base")" = "$base" ] || { echo "FAIL: pr-$N-base branch"; FAIL=1; }
# The child diff is pinned, local, and generated without external diff helpers.
[ -s "$(jq -r .diff_path <<<"$out")" ] || { echo "FAIL: pr.diff empty"; FAIL=1; }
expected_diff="$REVIEW_PR_SCRATCH/expected.diff"
git_wt -C "$clone" diff --no-ext-diff --no-textconv --binary "$base...$head" > "$expected_diff"
cmp -s "$expected_diff" "$(jq -r .diff_path <<<"$out")" \
  || { echo "FAIL: pr.diff does not match pinned base/head byte-for-byte"; FAIL=1; }
[ "$(jq -r .headRefOid "$(jq -r .meta_path <<<"$out")")" = "$head" ] || { echo "FAIL: pr.json head mismatch"; FAIL=1; }
jq -e 'has("title") and (.title | type == "string") and has("body") and (.body | type == "string")' "$(jq -r .meta_path <<<"$out")" >/dev/null \
  || { echo "FAIL: pr.json lacks string title/body evidence"; FAIL=1; }
jq -e 'type == "array" and all(.[]; type == "string")' "$(jq -r .policy_manifest_path <<<"$out")" >/dev/null \
  || { echo "FAIL: policy manifest is not a string array"; FAIL=1; }
# Executable Claude configuration is stripped.
[ ! -e "$clone/.claude/settings.json" ] || { echo "FAIL: settings.json present"; FAIL=1; }
[ ! -e "$clone/.mcp.json" ] || { echo "FAIL: .mcp.json present"; FAIL=1; }
# Passive base skills remain available.
[ -d "$clone/.claude/skills" ] || { echo "FAIL: project skills missing"; FAIL=1; }
# The cleanup ownership marker exists.
[ -f "$dir/.review-pr" ] || { echo "FAIL: .review-pr marker missing"; FAIL=1; }
jq -e '.policy_changes | type == "array"' <<<"$out" >/dev/null || { echo "FAIL: policy_changes not array"; FAIL=1; }
# The head repository is a complete owner/name slug.
[ "$(jq -r .head_repo <<<"$out")" = "$SLUG" ] || { echo "FAIL: head_repo != $SLUG: $(jq -r .head_repo <<<"$out")"; FAIL=1; }

# Non-existent PR -> exit 1 with gh stderr
rc=0; err="$("$SRC/checkout-pr.sh" "$SLUG" 999999 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: missing PR exit $rc, want 1"; FAIL=1; }
grep -qi 'not find\|no pull\|could not resolve' <<<"$err" || { echo "FAIL: missing PR stderr: $err"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "checkout-pr-test: OK"
exit "$FAIL"
