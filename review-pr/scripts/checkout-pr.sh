#!/usr/bin/env bash
# checkout-pr.sh OWNER/REPO N
# Pins a PR to SHAs, clones it into $REVIEW_PR_SCRATCH, isolates policy files, and prints one JSON object.
# Spec: docs/superpowers/specs/2026-08-27-review-pr-design.md (R1.2, R2, R3, R6.3, R7).
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

[ "$#" -eq 2 ] || die 2 "usage: checkout-pr.sh OWNER/REPO N"
SLUG="$1"; N="$2"
validate_ref "$SLUG" "$N"
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set to a writable directory"

for c in git jq gh claude; do need_cmd "$c"; done   # R7.1
check_claude_version                                 # R7.2

gh auth status >/dev/null 2>&1 || die 3 "gh is not authenticated (run: gh auth login)"

# R2.1 — resolve everything once.
META="$(gh pr view "$N" -R "$SLUG" --json number,baseRefOid,headRefOid,headRepository,headRefName,isCrossRepository,url 2>&1)" \
  || die 1 "gh pr view failed: $META"
BASE_SHA="$(jq -r .baseRefOid <<<"$META")"
HEAD_SHA="$(jq -r .headRefOid <<<"$META")"
HEAD_REPO="$(jq -r '.headRepository.nameWithOwner' <<<"$META")"
[[ "$BASE_SHA" =~ ^[0-9a-f]{40}$ && "$HEAD_SHA" =~ ^[0-9a-f]{40}$ ]] || die 1 "could not resolve base/head SHAs from gh: $META"

# Job directory (R2.2, R6.3).
mkdir -p "$REVIEW_PR_SCRATCH"
JOB="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
chmod 700 "$JOB"
: > "$JOB/.review-pr"
CLONE="$JOB/repo"
cleanup_on_fail() { keep_requested || { scratch_guard "$JOB" && rm -rf "$JOB"; }; }
# shellcheck disable=SC2154 # rc is assigned by this same trap string; shellcheck doesn't track it.
trap 'rc=$?; if [ $rc -ne 0 ]; then cleanup_on_fail; fi; exit $rc' EXIT

# R2.2 — clone the BASE repository (never the fork), fetch the PR ref, detach at the pinned head.
gh repo clone "$SLUG" "$CLONE" -- --depth 50 --quiet >&2 || die 1 "gh repo clone failed for $SLUG"
g() { git -C "$CLONE" "$@"; }
g fetch --quiet --depth 50 origin "refs/pull/$N/head" || die 1 "git fetch refs/pull/$N/head failed"
g cat-file -e "$HEAD_SHA^{commit}" 2>/dev/null || die 1 "pinned head $HEAD_SHA is not the current refs/pull/$N/head (PR moved?)"
# The head commit is untrusted: git_wt keeps its .gitattributes from selecting caller-configured filters.
git_wt -C "$CLONE" checkout -q --detach "$HEAD_SHA" || die 1 "git checkout --detach $HEAD_SHA failed"

# R2.3 — deepen until the merge base is present (lib.sh: every fetch names the pull ref).
ensure_merge_base "$CLONE" "$BASE_SHA" "$HEAD_SHA" "refs/pull/$N/head" \
  || die 1 "merge base of $BASE_SHA and $HEAD_SHA not found after unshallow"

# R2.5 — local branches for the child (no network needed inside).
g branch -q -f "pr-$N" "$HEAD_SHA" || die 1 "git branch pr-$N failed"
g branch -q -f "pr-$N-base" "$BASE_SHA" || die 1 "git branch pr-$N-base failed"

# R2.4 — pre-fetch diff and metadata; re-check the pin.
gh pr diff "$N" -R "$SLUG" > "$JOB/pr.diff" || die 1 "gh pr diff failed"
printf '%s\n' "$META" > "$JOB/pr.json"
NOW_HEAD="$(gh pr view "$N" -R "$SLUG" --json headRefOid -q .headRefOid 2>&1)" \
  || die 1 "gh pr view failed: $NOW_HEAD"
[ "$NOW_HEAD" = "$HEAD_SHA" ] || die 1 "PR head changed during checkout ($HEAD_SHA -> $NOW_HEAD); re-run"

# R3 — policy isolation.
CHANGES="$("$HERE/isolate-policy.sh" "$CLONE" "$BASE_SHA" "$HEAD_SHA")"

jq -n --arg dir "$JOB" --arg base "$BASE_SHA" --arg head "$HEAD_SHA" --arg hr "$HEAD_REPO" \
  --arg diff "$JOB/pr.diff" --arg meta "$JOB/pr.json" --argjson changes "$CHANGES" \
  '{dir:$dir, base_sha:$base, head_sha:$head, head_repo:$hr, policy_changes:$changes, diff_path:$diff, meta_path:$meta}'
