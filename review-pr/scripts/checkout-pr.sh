#!/usr/bin/env bash
# checkout-pr.sh OWNER/REPO N
# Implements RC4, RC12 and RC13 in references/runner-contract.md.
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
MAX_SKILL_INDEX="${REVIEW_PR_MAX_SKILL_INDEX:-200}"
[[ "$MAX_SKILL_INDEX" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_SKILL_INDEX must be a non-negative integer, got '$MAX_SKILL_INDEX'"

for c in git jq gh cmp; do need_cmd "$c"; done
# pinned_diff needs --attr-source (RC12), which git 2.41 added.
GIT_VERSION="$(git --version 2>/dev/null | awk '{print $3}')"
semver_at_least "${GIT_VERSION:-0}" 2.41 || die 3 "git 2.41 or newer is required, found ${GIT_VERSION:-unknown}"

# Only github.com is supported: qualify every gh call with the host so GH_HOST cannot redirect it.
REPO="github.com/$SLUG"
gh auth status --hostname github.com >/dev/null 2>&1 || die 3 "gh is not authenticated to github.com (run: gh auth login)"

META="$(gh pr view "$N" -R "$REPO" --json number,title,body,baseRefName,baseRefOid,headRefOid,headRepository,headRefName,isCrossRepository,url,state,isDraft,mergedAt,author 2>&1)" \
  || die 1 "gh pr view failed: $META"
BASE_SHA="$(jq -r .baseRefOid <<<"$META")"
HEAD_SHA="$(jq -r .headRefOid <<<"$META")"
HEAD_REPO="$(jq -r '.headRepository.nameWithOwner' <<<"$META")"
PR_URL="$(jq -r '.url' <<<"$META")"
[[ "$PR_URL" == "https://github.com/"* ]] || die 1 "gh returned a pull request outside github.com: $PR_URL"
[[ "$BASE_SHA" =~ ^[0-9a-f]{40}$ && "$HEAD_SHA" =~ ^[0-9a-f]{40}$ ]] || die 1 "could not resolve base/head SHAs from gh: $META"

mkdir -p "$REVIEW_PR_SCRATCH"
JOB="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
chmod 700 "$JOB"
: > "$JOB/.review-pr"
CLONE="$JOB/repo"
cleanup_on_fail() { keep_requested || { scratch_guard "$JOB" && rm -rf "$JOB"; }; }
# shellcheck disable=SC2154 # rc is assigned by this same trap string; shellcheck doesn't track it.
trap 'rc=$?; if [ $rc -ne 0 ]; then cleanup_on_fail; fi; exit $rc' EXIT

# --no-checkout: the default branch of a third-party repository is untrusted too, so only the
# git_wt checkout below may populate the working tree (and run any .gitattributes filters).
gh repo clone "$REPO" "$CLONE" -- --depth 50 --quiet --no-checkout >&2 || die 1 "gh repo clone failed for $SLUG"
g() { git -C "$CLONE" "$@"; }
# The clone's origin/HEAD names the default branch; empty when the remote does not advertise one, which the
# checkout reports as an unknown (null) pr_base_is_default rather than guessing.
DEFAULT_REF="$(g symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || true)"
DEFAULT_REF="${DEFAULT_REF#origin/}"
g fetch --quiet --depth 50 origin "refs/pull/$N/head" || die 1 "git fetch refs/pull/$N/head failed"
g cat-file -e "$HEAD_SHA^{commit}" 2>/dev/null || die 1 "pinned head $HEAD_SHA is not the current refs/pull/$N/head (PR moved?)"
# The head commit is untrusted: git_wt keeps its .gitattributes from selecting caller-configured filters.
git_wt -C "$CLONE" checkout -q --detach "$HEAD_SHA" || die 1 "git checkout --detach $HEAD_SHA failed"

ensure_merge_base "$CLONE" "$BASE_SHA" "$HEAD_SHA" "refs/pull/$N/head" \
  || die 1 "merge base of $BASE_SHA and $HEAD_SHA not found after unshallow"
# The pinned diff and the lens's [base] citations refer to this commit, not to the base-branch tip.
MERGE_BASE_SHA="$(g merge-base "$BASE_SHA" "$HEAD_SHA")" || die 1 "git merge-base $BASE_SHA $HEAD_SHA failed"

g branch -q -f "pr-$N" "$HEAD_SHA" || die 1 "git branch pr-$N failed"
g branch -q -f "pr-$N-base" "$BASE_SHA" || die 1 "git branch pr-$N-base failed"

# The child reads this pinned diff as data and receives no capability to modify it.
pinned_diff "$CLONE" "$BASE_SHA" "$HEAD_SHA" > "$JOB/pr.diff" \
  || die 1 "git diff failed for pinned base/head"
printf '%s\n' "$META" > "$JOB/pr.json"
NOW_HEAD="$(gh pr view "$N" -R "$REPO" --json headRefOid -q .headRefOid 2>&1)" \
  || die 1 "gh pr view failed: $NOW_HEAD"
[ "$NOW_HEAD" = "$HEAD_SHA" ] || die 1 "PR head changed during checkout ($HEAD_SHA -> $NOW_HEAD); re-run"

# The policy-changes array is PR-sized, so it reaches jq as a file, never as an argument.
"$HERE/isolate-policy.sh" "$RUNNER" "$CLONE" "$BASE_SHA" "$HEAD_SHA" > "$JOB/policy-changes.json" \
  || die 1 "isolate-policy.sh failed (exit $?)"
write_policy_manifest "$CLONE" "$BASE_SHA" "$JOB/policy-manifest.json"

# Status is as observed at checkout. Booleans are copied with has(), since jq's // would turn false into null.
# The metadata comes from pr.json on disk, never from argv: a PR body can exceed a single argument's size limit.
jq -n --arg dir "$JOB" --arg runner "$RUNNER" --arg base "$BASE_SHA" --arg head "$HEAD_SHA" --arg mb "$MERGE_BASE_SHA" --arg hr "$HEAD_REPO" --arg default_ref "$DEFAULT_REF" \
  --arg diff "$JOB/pr.diff" --arg meta "$JOB/pr.json" --arg context "$JOB/policy-manifest.json" \
  --slurpfile changes_doc "$JOB/policy-changes.json" --slurpfile meta_doc "$JOB/pr.json" \
  '$meta_doc[0] as $pr |
   {dir:$dir, runner:$runner, base_sha:$base, head_sha:$head, merge_base_sha:$mb, head_repo:$hr, policy_changes:$changes_doc[0],
    pr_state:($pr.state // null), pr_is_draft:(if ($pr | has("isDraft")) then $pr.isDraft else null end), pr_merged_at:($pr.mergedAt // null),
    pr_author:($pr.author.login // null), pr_author_is_bot:(if (($pr.author | type) == "object" and ($pr.author | has("is_bot"))) then $pr.author.is_bot else null end),
    pr_base_ref:(($pr.baseRefName // "") | if . == "" then null else . end),
    pr_base_is_default:(if (($pr.baseRefName // "") == "" or $default_ref == "") then null else $pr.baseRefName == $default_ref end),
    diff_path:$diff, meta_path:$meta, policy_manifest_path:$context}'
