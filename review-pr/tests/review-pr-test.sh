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
# RC9 counts base sources, not names: three distinct policy files reached by six names.
mkdir -p "$WORK/sub" "$WORK/skills/a" "$WORK/.claude"
printf '%s\n' 'Nested fixture policy.' > "$WORK/sub/AGENTS.md"
printf -- '---\nname: a\ndescription: fixture skill\n---\nbody\n' > "$WORK/skills/a/SKILL.md"
ln -s AGENTS.md "$WORK/CLAUDE.md"
ln -s AGENTS.md "$WORK/sub/CLAUDE.md"
ln -s ../skills "$WORK/.claude/skills"
ln -s ../skills "$WORK/.claude/agents"
git -C "$WORK" add file.txt AGENTS.md .gitattributes sub skills CLAUDE.md .claude
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
# PR 13: the head's .gitattributes marks its own new file -diff, which must not hide that file's hunk (RC12),
# while the base's -diff line for a generated file is still honoured.
printf '%s\n' '* filter=evil' 'generated.txt -diff' > "$WORK/.gitattributes"
printf '%s\n' 'generated v1' > "$WORK/generated.txt"
git -C "$WORK" add .gitattributes generated.txt
git -C "$WORK" commit -qm base-attributes
BASE13_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -qb feature13
printf '%s\n' 'secret.py -diff' >> "$WORK/.gitattributes"
printf '%s\n' 'PAYLOAD = "HIDDEN-PAYLOAD-7731"' > "$WORK/secret.py"
printf '%s\n' 'generated v2' > "$WORK/generated.txt"
git -C "$WORK" add .gitattributes secret.py generated.txt
git -C "$WORK" commit -qm head13
HEAD13_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -q main
# PR 14: 12,000 policy files with 100-character names, a policy_changes array past one argument's limit.
# Built through a private index so the files never need to exist in the work tree.
NOTE_BLOB="$(printf '%s\n' note | git -C "$WORK" hash-object -w --stdin)"
GIT_INDEX_FILE="$S/index14" git -C "$WORK" read-tree "$BASE13_SHA"
awk -v blob="$NOTE_BLOB" 'BEGIN {
  pad = sprintf("%92s", ""); gsub(/ /, "n", pad)
  for (i = 1; i <= 12000; i++) printf "100644 %s\t.claude/notes/%s%05d.md\n", blob, pad, i
}' | GIT_INDEX_FILE="$S/index14" git -C "$WORK" update-index --add --index-info
HEAD14_SHA="$(git -C "$WORK" commit-tree "$(GIT_INDEX_FILE="$S/index14" git -C "$WORK" write-tree)" -p "$BASE13_SHA" -m head14)"
git -C "$WORK" update-ref refs/heads/feature14 "$HEAD14_SHA"
# PR 15: a stacked pull request, whose base is another pull request's branch rather than the default branch.
# The parent branch changes policy; the child changes one file and no policy.
git -C "$WORK" checkout -qb parent
printf '%s\n' 'Parent-only fixture policy.' >> "$WORK/AGENTS.md"
git -C "$WORK" commit -qam parent
PARENT_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -qb child
printf '%s\n' child > "$WORK/child.txt"
git -C "$WORK" add child.txt
git -C "$WORK" commit -qm child
CHILD_SHA="$(git -C "$WORK" rev-parse HEAD)"
git -C "$WORK" checkout -q main
git clone -q --bare "$WORK" "$ORIGIN"
git --git-dir="$ORIGIN" symbolic-ref HEAD refs/heads/main
git --git-dir="$ORIGIN" update-ref refs/pull/12/head "$HEAD_SHA"
git --git-dir="$ORIGIN" update-ref refs/pull/13/head "$HEAD13_SHA"
git --git-dir="$ORIGIN" update-ref refs/pull/14/head "$HEAD14_SHA"
git --git-dir="$ORIGIN" update-ref refs/pull/15/head "$CHILD_SHA"
# The fake gh serves each pull request from $FAKE_PRS/N, which holds "BASE_SHA HEAD_SHA [BASE_REF]"; BASE_REF defaults to main.
FAKE_PRS="$S/prs"
mkdir -p "$FAKE_PRS"
printf '%s %s\n' "$BASE_SHA" "$HEAD_SHA" > "$FAKE_PRS/12"
printf '%s %s\n' "$BASE13_SHA" "$HEAD13_SHA" > "$FAKE_PRS/13"
printf '%s %s\n' "$BASE13_SHA" "$HEAD14_SHA" > "$FAKE_PRS/14"
printf '%s %s %s\n' "$PARENT_SHA" "$CHILD_SHA" parent > "$FAKE_PRS/15"

cat > "$FAKEBIN/gh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >> "$FAKE_GH_LOG"
if [ "$1 $2" = "auth status" ]; then exit 0; fi
if [ "$1 $2" = "repo clone" ]; then dest="$4"; shift 4; [ "${1:-}" != -- ] || shift; exec git clone "$@" "file://$FAKE_ORIGIN" "$dest"; fi
if [ "$1 $2" = "pr view" ]; then
  n="$3"
  [ -f "$FAKE_PRS/$n" ] || exit 1
  read -r base head ref < "$FAKE_PRS/$n"
  [ -z "${FAKE_PR_NO_BASE_REF:-}" ] || ref=""
  [ -n "${FAKE_PR_NO_BASE_REF:-}" ] || ref="${ref:-main}"
  for arg in "$@"; do [ "$arg" != -q ] || { printf '%s\n' "$head"; exit 0; }; done
  jq -n --argjson n "$n" --arg base "$base" --arg head "$head" --arg ref "$ref" \
    '{number:$n,title:"Fixture PR",body:(if env.FAKE_PR_BODY_BYTES then ("x" * (env.FAKE_PR_BODY_BYTES | tonumber)) else "Fixture body" end),
      baseRefName:(if $ref == "" then null else $ref end),baseRefOid:$base,headRefOid:$head,headRepository:{nameWithOwner:"owner/repo"},headRefName:"feature",isCrossRepository:false,url:(env.FAKE_PR_URL // "https://github.com/owner/repo/pull/\($n)"),
      state:(env.FAKE_PR_STATE // "OPEN"), isDraft:((env.FAKE_PR_DRAFT // "false") == "true"), mergedAt:(env.FAKE_PR_MERGED_AT // null),
      author:{login:(env.FAKE_PR_AUTHOR // "octocat"), is_bot:((env.FAKE_PR_AUTHOR_BOT // "false") == "true")}}'
  exit 0
fi
exit 2
EOF

cat > "$FAKEBIN/claude" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then printf '%s\n' '2.1.251 (Claude Code)'; exit 0; fi
[ -z "${FAKE_CLAUDE_LOG:-}" ] || printf '%s\n' review >> "$FAKE_CLAUDE_LOG"
result='## Summary
Lenses checked: correctness, silent-failure, tests, comments.
Fixture review completed.

## Changes
Fixture change summary.

## Critical
(none)

## Important
(none)

## Suggestions
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
export PATH="$FAKEBIN:/usr/bin:/bin" FAKE_ORIGIN="$ORIGIN" FAKE_PRS
export FAKE_GH_LOG="$S/gh.log"
# A caller's GH_HOST must not redirect a github.com review to another host.
export GH_HOST=ghe.example.invalid

rc=0
err="$("$SRC/review-pr.sh" owner/repo 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 2 ] || { echo "FAIL: wrapper usage exit $rc"; FAIL=1; }
grep -qF 'usage: review-pr.sh' <<<"$err" || { echo "FAIL: wrapper usage diagnostic missing"; FAIL=1; }

out="$(TMPDIR="$S/temp/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e 'keys == ["base_sha","diff_unavailable","dir","exit","head_sha","kept","merge_base_sha","policy_changes","pr_author","pr_author_is_bot","pr_base_is_default","pr_base_ref","pr_is_draft","pr_merged_at","pr_state","review","runner","schema_errors","schema_valid","stderr_tail"]' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper envelope fields changed: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: wrapper result is not schema-valid: $out"; FAIL=1; }
# Pull-request status as observed at checkout rides the envelope for the relay.
jq -e '.pr_state == "OPEN" and .pr_is_draft == false and .pr_merged_at == null and .pr_author == "octocat" and .pr_author_is_bot == false' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper did not relay pull-request status: $out"; FAIL=1; }
# The base branch's name, and whether it is the default branch, ride the envelope for the relay.
jq -e '.pr_base_ref == "main" and .pr_base_is_default == true' <<<"$out" >/dev/null \
  || { echo "FAIL: wrapper did not relay the default base branch: $out"; FAIL=1; }
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

# The bound applies to distinct base sources: six names for three files pass at 3 and fail at 2, before any review.
out="$(FAKE_CLAUDE_LOG="$S/claude-calls-at-bound" REVIEW_PR_MAX_POLICY_FILES=3 REVIEW_PR_KEEP=1 REVIEW_PR_SCRATCH="$S/at-bound/" "$SRC/review-pr.sh" owner/repo 12)" \
  || { echo "FAIL: three distinct policy files exceeded REVIEW_PR_MAX_POLICY_FILES=3"; FAIL=1; }
# Known positive for the no-child check below: a review that runs is logged.
[ -s "$S/claude-calls-at-bound" ] || { echo "FAIL: known positive — the fake child did not log its run"; FAIL=1; }
manifest="$(cat "$(jq -r .dir <<<"${out:-null}")/policy-manifest.json" 2>/dev/null || true)"
# skills/a/SKILL.md is reached as an agent definition and as a skill, so it stays a mandatory policy file (RC8).
[ "$manifest" = '{"version":2,"policy_files":[".claude/agents/a/SKILL.md","AGENTS.md","sub/AGENTS.md"],"skills":[]}' ] \
  || { echo "FAIL: deduplicated checkout manifest=$manifest"; FAIL=1; }
rc=0
err="$(FAKE_CLAUDE_LOG="$S/claude-calls" REVIEW_PR_MAX_POLICY_FILES=2 REVIEW_PR_SCRATCH="$S/below-bound/" "$SRC/review-pr.sh" owner/repo 12 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: three distinct policy files under REVIEW_PR_MAX_POLICY_FILES=2 exit $rc"; FAIL=1; }
grep -qF 'base policy manifest has 3 files, exceeding REVIEW_PR_MAX_POLICY_FILES=2' <<<"$err" \
  || { echo "FAIL: deduplicated bound diagnostic missing: $err"; FAIL=1; }
[ ! -s "$S/claude-calls" ] || { echo "FAIL: the child ran although the manifest exceeded the bound"; FAIL=1; }
[ -z "$(find "$S/below-bound" -name .review-pr -print -quit)" ] || { echo "FAIL: deduplicated bound leaked a checkout"; FAIL=1; }

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

# A stacked pull request is reported as targeting a branch that is not the default one. Its policy comes from that
# branch (RC4), so the parent's policy edit governs the review without appearing in policy_changes or pr.diff.
out="$(REVIEW_PR_KEEP=1 REVIEW_PR_SCRATCH="$S/stacked/" "$SRC/review-pr.sh" owner/repo 15)" \
  || { echo "FAIL: stacked PR review failed: ${out:-<no output>}"; FAIL=1; }
jq -e --arg base "$PARENT_SHA" '.exit == 0 and .pr_base_ref == "parent" and .pr_base_is_default == false
  and .base_sha == $base and .merge_base_sha == $base and .policy_changes == []' <<<"${out:-null}" >/dev/null \
  || { echo "FAIL: stacked PR base was not relayed: ${out:-<no output>}"; FAIL=1; }
dir15="$(jq -r .dir <<<"${out:-null}")"
grep -qxF 'Parent-only fixture policy.' "$dir15/repo/AGENTS.md" 2>/dev/null \
  || { echo "FAIL: stacked PR fixture no longer restores the parent branch's policy; the disclosure check is insensitive"; FAIL=1; }
if [ "$(grep -c '^diff --git' "$dir15/pr.diff" 2>/dev/null)" != 1 ] || ! grep -qF 'b/child.txt' "$dir15/pr.diff"; then
  echo "FAIL: stacked PR diff is not the child's change alone"; FAIL=1
fi
jq -e '.baseRefName == "parent"' "$dir15/pr.json" >/dev/null 2>&1 || { echo "FAIL: pr.json lacks the base branch name"; FAIL=1; }
# An absent base branch name is reported as unknown, never as the default branch.
out="$(FAKE_PR_NO_BASE_REF=1 REVIEW_PR_SCRATCH="$S/noref/" "$SRC/review-pr.sh" owner/repo 12)"
jq -e '.exit == 0 and .pr_base_ref == null and .pr_base_is_default == null' <<<"$out" >/dev/null \
  || { echo "FAIL: missing base branch name was not relayed as unknown: $out"; FAIL=1; }

# PR metadata must never ride a process argument: GitHub allows 65,536 body characters, which can exceed
# Linux's 128 KiB single-argument limit once JSON-escaped. This probe is sized past macOS's 1 MiB ARG_MAX
# as well so it fails under either kernel when the body reaches argv.
out="$(FAKE_PR_BODY_BYTES=1500000 REVIEW_PR_SCRATCH="$S/bigbody/" "$SRC/review-pr.sh" owner/repo 12 2>"$S/bigbody.stderr")" \
  || { echo "FAIL: a large PR body aborted the checkout: $(tail -3 "$S/bigbody.stderr")"; FAIL=1; }
jq -e '.exit == 0 and .pr_state == "OPEN" and .schema_valid == true' <<<"${out:-null}" >/dev/null \
  || { echo "FAIL: large PR body was not reviewed with status relayed: ${out:-<no output>}"; FAIL=1; }

# RC12: the pinned diff takes attributes from the base commit, never the head, and carries no binary patch bodies.
out="$(REVIEW_PR_KEEP=1 REVIEW_PR_SCRATCH="$S/attrs/" "$SRC/review-pr.sh" owner/repo 13)" \
  || { echo "FAIL: PR 13 review failed: ${out:-<no output>}"; FAIL=1; }
diff13="$(jq -r .dir <<<"${out:-null}")/pr.diff"
[ -s "$diff13" ] || { echo "FAIL: PR 13 kept no pr.diff"; FAIL=1; }
grep -qF 'HIDDEN-PAYLOAD-7731' "$diff13" 2>/dev/null \
  || { echo "FAIL: a head .gitattributes -diff line hid an added file's hunk from pr.diff"; FAIL=1; }
grep -qxF 'Binary files a/generated.txt and b/generated.txt differ' "$diff13" 2>/dev/null \
  || { echo "FAIL: the base .gitattributes -diff line for generated.txt was not honoured"; FAIL=1; }
if grep -qxF 'GIT binary patch' "$diff13" 2>/dev/null; then echo "FAIL: pr.diff carries a binary patch body"; FAIL=1; fi

# many policy changes: the policy_changes array reaches the envelope through files, never argv.
out="$(REVIEW_PR_KEEP=1 REVIEW_PR_SCRATCH="$S/many/" "$SRC/review-pr.sh" owner/repo 14 2>"$S/many.stderr")" \
  || { echo "FAIL: many policy changes aborted the review: $(tail -c 300 "$S/many.stderr")"; FAIL=1; }
jq -e '.policy_changes | length == 12000' <<<"${out:-null}" >/dev/null 2>&1 \
  || { echo "FAIL: many policy changes: policy_changes does not list 12000 paths: $(tail -c 300 "$S/many.stderr")"; FAIL=1; }
# RC13: the job holds policy-changes.json beside pr.diff, equal to the envelope's policy_changes.
printf '%s' "${out:-null}" > "$S/many.envelope.json"
jq -e --slurpfile env "$S/many.envelope.json" '. == $env[0].policy_changes and length == 12000' \
  "$(jq -r .dir "$S/many.envelope.json")/policy-changes.json" >/dev/null 2>&1 \
  || { echo "FAIL: the kept job's policy-changes.json does not equal the envelope's policy_changes"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "review-pr-test: OK"
exit "$FAIL"
