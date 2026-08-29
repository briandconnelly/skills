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
git -C "$WORK" add file.txt AGENTS.md
git -C "$WORK" commit -qm base
BASE_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -qb feature
printf '%s\n' head > "$WORK/file.txt"
git -C "$WORK" commit -qam head
HEAD_SHA="$(git -C "$WORK" rev-parse HEAD)"
git clone -q --bare "$WORK" "$ORIGIN"
git --git-dir="$ORIGIN" symbolic-ref HEAD refs/heads/main
git --git-dir="$ORIGIN" update-ref refs/pull/12/head "$HEAD_SHA"

cat > "$FAKEBIN/gh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [ "$1 $2" = "auth status" ]; then exit 0; fi
if [ "$1 $2" = "repo clone" ]; then exec git clone -q "file://$FAKE_ORIGIN" "$4"; fi
if [ "$1 $2" = "pr view" ]; then
  for arg in "$@"; do [ "$arg" != -q ] || { printf '%s\n' "$FAKE_HEAD_SHA"; exit 0; }; done
  jq -n --arg base "$FAKE_BASE_SHA" --arg head "$FAKE_HEAD_SHA" \
    '{number:12,title:"Fixture PR",body:"Fixture body",baseRefOid:$base,headRefOid:$head,headRepository:{nameWithOwner:"owner/repo"},headRefName:"feature",isCrossRepository:false,url:"https://github.com/owner/repo/pull/12"}'
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

rc=0
err="$("$SRC/review-pr.sh" owner/repo 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 2 ] || { echo "FAIL: wrapper usage exit $rc"; FAIL=1; }
grep -qF 'usage: review-pr.sh' <<<"$err" || { echo "FAIL: wrapper usage diagnostic missing"; FAIL=1; }

out="$(TMPDIR="$S/temp/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e 'keys == ["base_sha","diff_unavailable","dir","exit","head_sha","kept","policy_changes","review","runner","schema_errors","schema_valid","stderr_tail"]' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper envelope fields changed: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: wrapper result is not schema-valid: $out"; FAIL=1; }
dir="$(jq -r .dir <<<"$out")"
[ ! -e "$dir" ] || { echo "FAIL: wrapper leaked default scratch directory: $dir"; FAIL=1; }
temp_real="$(cd -- "$S/temp" >/dev/null 2>&1 && pwd -P)"
case "$dir" in "$temp_real"/*) ;; *) echo "FAIL: TMPDIR default was not normalized: $dir"; FAIL=1;; esac

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

[ "$FAIL" = 0 ] && echo "review-pr-test: OK"
exit "$FAIL"
