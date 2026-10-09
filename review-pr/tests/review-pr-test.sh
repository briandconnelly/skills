#!/usr/bin/env bash
# Offline: the public wrapper emits one normalized object and owns scratch cleanup.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX REVIEW_PR_SCRATCH REVIEW_PR_KEEP
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
S="$(mktemp -d)"
trap 'rm -rf "$S"' EXIT
WORK="$S/work"
ORIGIN="$S/origin.git"
FAKEBIN="$S/bin"
mkdir -p "$WORK" "$FAKEBIN" "$S/temp"

git -C "$WORK" init -q -b main
git -C "$WORK" config user.email t@example.com
git -C "$WORK" config user.name t
printf '%s\n' base > "$WORK/file.txt"
printf '%s\n' 'Review fixture policy.' > "$WORK/AGENTS.md"
# The default branch selects a filter by name; the clone must not run a caller-configured driver.
printf '%s\n' '* filter=evil' > "$WORK/.gitattributes"
git -C "$WORK" add file.txt AGENTS.md .gitattributes
git -C "$WORK" commit -qm base
MERGE_BASE_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -qb feature
printf '%s\n' head > "$WORK/file.txt"
git -C "$WORK" commit -qam head
HEAD_SHA="$(git -C "$WORK" rev-parse HEAD)"
# The base branch moves on after the PR branched, so base_sha and the merge base differ.
git -C "$WORK" checkout -q main
printf '%s\n' 'Base moved on.' > "$WORK/other.txt"
git -C "$WORK" add other.txt
git -C "$WORK" commit -qm base-advance
BASE_SHA="$(git -C "$WORK" rev-parse HEAD)"
git clone -q --bare "$WORK" "$ORIGIN"
git --git-dir="$ORIGIN" symbolic-ref HEAD refs/heads/main
git --git-dir="$ORIGIN" update-ref refs/pull/12/head "$HEAD_SHA"

cat > "$FAKEBIN/gh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >> "$FAKE_GH_LOG"
if [ "$1 $2" = "auth status" ]; then exit 0; fi
if [ "$1 $2" = "repo clone" ]; then dest="$4"; shift 4; [ "${1:-}" != -- ] || shift; exec git clone "$@" "file://$FAKE_ORIGIN" "$dest"; fi
if [ "$1 $2" = "pr view" ]; then
  for arg in "$@"; do [ "$arg" != -q ] || { printf '%s\n' "$FAKE_HEAD_SHA"; exit 0; }; done
  jq -n --arg base "$FAKE_BASE_SHA" --arg head "$FAKE_HEAD_SHA" \
    '{number:12,title:"Fixture PR",body:(if env.FAKE_PR_BODY_BYTES then ("x" * (env.FAKE_PR_BODY_BYTES | tonumber)) else "Fixture body" end),
      baseRefOid:$base,headRefOid:$head,headRepository:{nameWithOwner:"owner/repo"},headRefName:"feature",isCrossRepository:false,url:(env.FAKE_PR_URL // "https://github.com/owner/repo/pull/12"),
      state:(env.FAKE_PR_STATE // "OPEN"), isDraft:((env.FAKE_PR_DRAFT // "false") == "true"), mergedAt:(env.FAKE_PR_MERGED_AT // null),
      author:{login:(env.FAKE_PR_AUTHOR // "octocat"), is_bot:((env.FAKE_PR_AUTHOR_BOT // "false") == "true")}}'
  exit 0
fi
exit 2
EOF

cat > "$FAKEBIN/claude" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then printf '%s\n' '2.1.251 (Claude Code)'; exit 0; fi
result='## Summary
Lenses checked: correctness, silent-failure, tests, comments.
Fixture review completed.

## Critical
(none)

## Important
(none)

## Suggestions
(none)

## Strengths
(none)

## Not reviewed
(none)'
jq -n --arg result "$result" '{type:"result",is_error:false,result:$result,total_cost_usd:0,duration_ms:1,permission_denials:[]}'
EOF
chmod +x "$FAKEBIN/gh" "$FAKEBIN/claude"
for command in git jq bash sed awk grep tail pkill sleep; do
  path="$(command -v "$command")"
  [ -e "$FAKEBIN/$command" ] || ln -s "$path" "$FAKEBIN/$command"
done
export PATH="$FAKEBIN:/usr/bin:/bin" FAKE_ORIGIN="$ORIGIN" FAKE_BASE_SHA="$BASE_SHA" FAKE_HEAD_SHA="$HEAD_SHA"
export FAKE_GH_LOG="$S/gh.log"
# A caller's GH_HOST must not redirect a github.com review to another host.
export GH_HOST=ghe.example.invalid

rc=0
err="$("$SRC/review-pr.sh" owner/repo 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 2 ] || { echo "FAIL: wrapper usage exit $rc"; FAIL=1; }
grep -qF 'usage: review-pr.sh' <<<"$err" || { echo "FAIL: wrapper usage diagnostic missing"; FAIL=1; }

out="$(TMPDIR="$S/temp/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e 'keys == ["base_sha","diff_unavailable","dir","exit","head_sha","kept","merge_base_sha","policy_changes","pr_author","pr_author_is_bot","pr_is_draft","pr_merged_at","pr_state","review","runner","schema_errors","schema_valid","stderr_tail"]' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper envelope fields changed: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: wrapper result is not schema-valid: $out"; FAIL=1; }
# Pull-request status as observed at checkout rides the envelope for the relay.
jq -e '.pr_state == "OPEN" and .pr_is_draft == false and .pr_merged_at == null and .pr_author == "octocat" and .pr_author_is_bot == false' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper did not relay pull-request status: $out"; FAIL=1; }
# [base] citations resolve at the merge base, which is not the base-branch tip once it moves on.
[ "$(jq -r .merge_base_sha <<<"$out")" = "$MERGE_BASE_SHA" ] || { echo "FAIL: merge_base_sha != merge base: $out"; FAIL=1; }
[ "$(jq -r .base_sha <<<"$out")" = "$BASE_SHA" ] || { echo "FAIL: base_sha != base-branch tip: $out"; FAIL=1; }
[ "$MERGE_BASE_SHA" != "$BASE_SHA" ] || { echo "FAIL: fixture base did not diverge; merge_base_sha check is insensitive"; FAIL=1; }
dir="$(jq -r .dir <<<"$out")"
[ ! -e "$dir" ] || { echo "FAIL: wrapper leaked default scratch directory: $dir"; FAIL=1; }
temp_real="$(cd -- "$S/temp" >/dev/null 2>&1 && pwd -P)"
case "$dir" in "$temp_real"/*) ;; *) echo "FAIL: TMPDIR default was not normalized: $dir"; FAIL=1;; esac

grep -qxF 'auth status --hostname github.com' "$FAKE_GH_LOG" \
  || { echo "FAIL: gh auth status was not pinned to github.com: $(cat "$FAKE_GH_LOG")"; FAIL=1; }
if grep -E '^(pr view|repo clone) ' "$FAKE_GH_LOG" | grep -vqF 'github.com/owner/repo'; then
  echo "FAIL: a gh repository call was not host-qualified: $(cat "$FAKE_GH_LOG")"; FAIL=1
fi
[ "$(grep -cE '^(pr view|repo clone) ' "$FAKE_GH_LOG")" = 3 ] \
  || { echo "FAIL: expected two pr view calls and one clone: $(cat "$FAKE_GH_LOG")"; FAIL=1; }

# Inherited config injection must not run a smudge filter during clone or checkout.
mark="$S/SMUDGE-RAN"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=filter.evil.smudge GIT_CONFIG_VALUE_0="touch $mark; cat" \
  REVIEW_PR_SCRATCH="$S/filter/" "$SRC/review-pr.sh" owner/repo 12 >/dev/null 2>&1 || true
[ ! -e "$mark" ] || { echo "FAIL: an inherited smudge filter ran on untrusted repository content"; FAIL=1; }
# Known positive: the same injection does run the filter on an ordinary checkout.
git -C "$S" clone -q "file://$ORIGIN" filter-probe 2>/dev/null
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=filter.evil.smudge GIT_CONFIG_VALUE_0="touch $mark; cat" \
  git -C "$S/filter-probe" checkout -q -f "$HEAD_SHA" -- file.txt
[ -e "$mark" ] || { echo "FAIL: injected smudge filter never runs; the clone probe is insensitive"; FAIL=1; }
rm -f "$mark"

rc=0
err="$(FAKE_PR_URL=https://ghe.example.invalid/owner/repo/pull/12 REVIEW_PR_SCRATCH="$S/offhost/" "$SRC/review-pr.sh" owner/repo 12 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: off-host pull request exit $rc"; FAIL=1; }
grep -qF 'outside github.com' <<<"$err" || { echo "FAIL: off-host diagnostic missing: $err"; FAIL=1; }
[ -z "$(find "$S/offhost" -name .review-pr -print -quit 2>/dev/null)" ] || { echo "FAIL: off-host rejection leaked a checkout"; FAIL=1; }

rc=0
err="$(REVIEW_PR_MAX_POLICY_FILES=0 REVIEW_PR_SCRATCH="$S/capped/" "$SRC/review-pr.sh" owner/repo 12 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: policy manifest cap exit $rc"; FAIL=1; }
grep -qF 'exceeding REVIEW_PR_MAX_POLICY_FILES=0' <<<"$err" \
  || { echo "FAIL: policy manifest cap diagnostic missing: $err"; FAIL=1; }
[ -z "$(find "$S/capped" -name .review-pr -print -quit)" ] || { echo "FAIL: policy cap leaked a checkout"; FAIL=1; }

out="$(REVIEW_PR_KEEP=1 REVIEW_PR_SCRATCH="$S/kept/" "$SRC/review-pr.sh" owner/repo 12)"
dir="$(jq -r .dir <<<"$out")"
[ "$(jq -r .kept <<<"$out")" = true ] || { echo "FAIL: wrapper did not relay kept=true"; FAIL=1; }
[ -d "$dir" ] || { echo "FAIL: wrapper removed a kept checkout"; FAIL=1; }

# Draft, bot-authored, and merged pull requests are reported, not refused.
out="$(FAKE_PR_DRAFT=true FAKE_PR_AUTHOR='app/dependabot' FAKE_PR_AUTHOR_BOT=true REVIEW_PR_SCRATCH="$S/draft/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e '.exit == 0 and .pr_state == "OPEN" and .pr_is_draft == true and .pr_author == "app/dependabot" and .pr_author_is_bot == true' <<<"$out" >/dev/null \
  || { echo "FAIL: draft bot PR status not relayed: $out"; FAIL=1; }
out="$(FAKE_PR_STATE=MERGED FAKE_PR_MERGED_AT=2026-10-01T12:00:00Z REVIEW_PR_SCRATCH="$S/merged/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e '.exit == 0 and .pr_state == "MERGED" and .pr_merged_at == "2026-10-01T12:00:00Z" and .pr_is_draft == false' <<<"$out" >/dev/null \
  || { echo "FAIL: merged PR status not relayed: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: merged PR was not reviewed: $out"; FAIL=1; }

# PR metadata must never ride a process argument: GitHub allows 65,536 body characters, which can exceed
# Linux's 128 KiB single-argument limit once JSON-escaped. This probe is sized past macOS's 1 MiB ARG_MAX
# as well so it fails under either kernel when the body reaches argv.
out="$(FAKE_PR_BODY_BYTES=1500000 REVIEW_PR_SCRATCH="$S/bigbody/" "$SRC/review-pr.sh" owner/repo 12 2>"$S/bigbody.stderr")" \
  || { echo "FAIL: a large PR body aborted the checkout: $(tail -3 "$S/bigbody.stderr")"; FAIL=1; }
jq -e '.exit == 0 and .pr_state == "OPEN" and .schema_valid == true' <<<"${out:-null}" >/dev/null \
  || { echo "FAIL: large PR body was not reviewed with status relayed: ${out:-<no output>}"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "review-pr-test: OK"
exit "$FAIL"
