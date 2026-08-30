#!/usr/bin/env bash
# checkout-pr.sh OWNER/REPO N
# Implements the checkout phase documented in SKILL.md and the policy boundary in references/runner-contract.md.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

[ "$#" -eq 2 ] || die 2 "usage: checkout-pr.sh OWNER/REPO N"
SLUG="$1"; N="$2"
validate_ref "$SLUG" "$N"
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set to a writable directory"
RUNNER="${REVIEW_PR_RUNNER:-claude}"
load_adapter "$RUNNER"
MAX_POLICY_FILES="${REVIEW_PR_MAX_POLICY_FILES:-40}"
[[ "$MAX_POLICY_FILES" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_POLICY_FILES must be a non-negative integer, got '$MAX_POLICY_FILES'"

for c in git jq gh; do need_cmd "$c"; done

gh auth status >/dev/null 2>&1 || die 3 "gh is not authenticated (run: gh auth login)"

META="$(gh pr view "$N" -R "$SLUG" --json number,title,body,baseRefOid,headRefOid,headRepository,headRefName,isCrossRepository,url 2>&1)" \
  || die 1 "gh pr view failed: $META"
BASE_SHA="$(jq -r .baseRefOid <<<"$META")"
HEAD_SHA="$(jq -r .headRefOid <<<"$META")"
HEAD_REPO="$(jq -r '.headRepository.nameWithOwner' <<<"$META")"
[[ "$BASE_SHA" =~ ^[0-9a-f]{40}$ && "$HEAD_SHA" =~ ^[0-9a-f]{40}$ ]] || die 1 "could not resolve base/head SHAs from gh: $META"

mkdir -p "$REVIEW_PR_SCRATCH"
JOB="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
chmod 700 "$JOB"
: > "$JOB/.review-pr"
CLONE="$JOB/repo"
cleanup_on_fail() { keep_requested || { scratch_guard "$JOB" && rm -rf "$JOB"; }; }
# shellcheck disable=SC2154 # rc is assigned by this same trap string; shellcheck doesn't track it.
trap 'rc=$?; if [ $rc -ne 0 ]; then cleanup_on_fail; fi; exit $rc' EXIT

gh repo clone "$SLUG" "$CLONE" -- --depth 50 --quiet >&2 || die 1 "gh repo clone failed for $SLUG"
g() { git -C "$CLONE" "$@"; }
g fetch --quiet --depth 50 origin "refs/pull/$N/head" || die 1 "git fetch refs/pull/$N/head failed"
g cat-file -e "$HEAD_SHA^{commit}" 2>/dev/null || die 1 "pinned head $HEAD_SHA is not the current refs/pull/$N/head (PR moved?)"
# The head commit is untrusted: git_wt keeps its .gitattributes from selecting caller-configured filters.
git_wt -C "$CLONE" checkout -q --detach "$HEAD_SHA" || die 1 "git checkout --detach $HEAD_SHA failed"

ensure_merge_base "$CLONE" "$BASE_SHA" "$HEAD_SHA" "refs/pull/$N/head" \
  || die 1 "merge base of $BASE_SHA and $HEAD_SHA not found after unshallow"

g branch -q -f "pr-$N" "$HEAD_SHA" || die 1 "git branch pr-$N failed"
g branch -q -f "pr-$N-base" "$BASE_SHA" || die 1 "git branch pr-$N-base failed"

# The child reads this pinned diff as data and receives no capability to modify it.
git_wt -C "$CLONE" diff --no-ext-diff --no-textconv --binary "$BASE_SHA...$HEAD_SHA" > "$JOB/pr.diff" \
  || die 1 "git diff failed for pinned base/head"
printf '%s\n' "$META" > "$JOB/pr.json"
NOW_HEAD="$(gh pr view "$N" -R "$SLUG" --json headRefOid -q .headRefOid 2>&1)" \
  || die 1 "gh pr view failed: $NOW_HEAD"
[ "$NOW_HEAD" = "$HEAD_SHA" ] || die 1 "PR head changed during checkout ($HEAD_SHA -> $NOW_HEAD); re-run"

CHANGES="$("$HERE/isolate-policy.sh" "$RUNNER" "$CLONE" "$BASE_SHA" "$HEAD_SHA")" \
  || die 1 "isolate-policy.sh failed (exit $?)"
CONTEXT_PATHS="$(context_paths_json "$CLONE" "$BASE_SHA")"
CONTEXT_COUNT="$(jq -r length <<<"$CONTEXT_PATHS")"
[ "$CONTEXT_COUNT" -le "$MAX_POLICY_FILES" ] \
  || die 1 "base policy manifest has $CONTEXT_COUNT files, exceeding REVIEW_PR_MAX_POLICY_FILES=$MAX_POLICY_FILES"
printf '%s\n' "$CONTEXT_PATHS" > "$JOB/policy-manifest.json"

jq -n --arg dir "$JOB" --arg runner "$RUNNER" --arg base "$BASE_SHA" --arg head "$HEAD_SHA" --arg hr "$HEAD_REPO" \
  --arg diff "$JOB/pr.diff" --arg meta "$JOB/pr.json" --arg context "$JOB/policy-manifest.json" --argjson changes "$CHANGES" \
  '{dir:$dir, runner:$runner, base_sha:$base, head_sha:$head, head_repo:$hr, policy_changes:$changes, diff_path:$diff, meta_path:$meta, policy_manifest_path:$context}'
