#!/usr/bin/env bash
# Live (needs gh auth): checkout-pr.sh pins and clones a real PR (R2, R3, R6.3).
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
if ! gh auth status >/dev/null 2>&1; then echo "checkout-pr-test: SKIP (gh not authenticated)"; exit 0; fi
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
export REVIEW_PR_SCRATCH; REVIEW_PR_SCRATCH="$(mktemp -d)"; trap 'rm -rf "$REVIEW_PR_SCRATCH"' EXIT
SLUG=briandconnelly/cwms-tools; N=112

out="$("$SRC/checkout-pr.sh" "$SLUG" "$N")"
echo "$out" | jq -e . >/dev/null || { echo "FAIL: stdout is not one JSON object: $out"; exit 1; }
dir="$(jq -r .dir <<<"$out")"; head="$(jq -r .head_sha <<<"$out")"; base="$(jq -r .base_sha <<<"$out")"
clone="$dir/repo"

# R2.1/R2.2 pinned detached head
[ "$(git -C "$clone" rev-parse HEAD)" = "$head" ] || { echo "FAIL: HEAD != head_sha"; FAIL=1; }
git -C "$clone" symbolic-ref -q HEAD >/dev/null && { echo "FAIL: HEAD is not detached"; FAIL=1; }
# R2.1 the pinned SHA is what GitHub reports now (tolerates a push between: prints, does not fail)
gh_head="$(gh pr view "$N" -R "$SLUG" --json headRefOid -q .headRefOid)"
[ "$gh_head" = "$head" ] || echo "NOTE: PR head moved during test ($gh_head vs $head)"
# R2.3 merge base present
git -C "$clone" merge-base "$base" "$head" >/dev/null || { echo "FAIL: merge-base missing"; FAIL=1; }
# R2.5 local branches
[ "$(git -C "$clone" rev-parse "pr-$N")" = "$head" ] || { echo "FAIL: pr-$N branch"; FAIL=1; }
[ "$(git -C "$clone" rev-parse "pr-$N-base")" = "$base" ] || { echo "FAIL: pr-$N-base branch"; FAIL=1; }
# R2.4 pre-fetched artifacts
[ -s "$(jq -r .diff_path <<<"$out")" ] || { echo "FAIL: pr.diff empty"; FAIL=1; }
[ "$(jq -r .headRefOid "$(jq -r .meta_path <<<"$out")")" = "$head" ] || { echo "FAIL: pr.json head mismatch"; FAIL=1; }
# R3.2 stripped
[ ! -e "$clone/.claude/settings.json" ] || { echo "FAIL: settings.json present"; FAIL=1; }
[ ! -e "$clone/.mcp.json" ] || { echo "FAIL: .mcp.json present"; FAIL=1; }
# R3 base skills still present (cwms-tools ships tracked skills)
[ -d "$clone/.claude/skills" ] || { echo "FAIL: project skills missing"; FAIL=1; }
# R6.3 marker
[ -f "$dir/.review-pr" ] || { echo "FAIL: .review-pr marker missing"; FAIL=1; }
jq -e '.policy_changes | type == "array"' <<<"$out" >/dev/null || { echo "FAIL: policy_changes not array"; FAIL=1; }

# Non-existent PR -> exit 1 with gh stderr
rc=0; err="$("$SRC/checkout-pr.sh" "$SLUG" 999999 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: missing PR exit $rc, want 1"; FAIL=1; }
grep -qi 'not find\|no pull\|could not resolve' <<<"$err" || { echo "FAIL: missing PR stderr: $err"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "checkout-pr-test: OK"
exit "$FAIL"
