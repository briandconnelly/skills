#!/usr/bin/env bash
# Offline: normalized runner lifecycle, Claude adapter flags, watchdog, and cleanup.
set -euo pipefail
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
export REVIEW_PR_SCRATCH
REVIEW_PR_SCRATCH="$(mktemp -d)"
trap 'rm -rf "$REVIEW_PR_SCRATCH"' EXIT
FAKEBIN="$REVIEW_PR_SCRATCH/bin"
mkdir -p "$FAKEBIN"
for c in jq git bash; do ln -sf "$(command -v "$c")" "$FAKEBIN/$c"; done
export PATH="$FAKEBIN:/usr/bin:/bin"

mkjob() {
  local job
  job="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
  : > "$job/.review-pr"
  mkdir -p "$job/repo"
  git -C "$job/repo" init -q
  echo '{"number":12}' > "$job/pr.json"
  echo 'diff data' > "$job/pr.diff"
  echo '[]' > "$job/policy-manifest.json"
  jq -n --arg d "$job" '{dir:$d, runner:"claude", base_sha:"b", head_sha:"h", head_repo:"o/r", policy_changes:[".claude/x"], diff_path:($d+"/pr.diff"), meta_path:($d+"/pr.json"), policy_manifest_path:($d+"/policy-manifest.json")}'
}

cat > "$FAKEBIN/claude" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then echo "2.1.251 (Claude Code)"; exit 0; fi
printf '%s\n' "$@" > "$FAKE_ARGV"
pwd -P > "$FAKE_CWD"
[ -t 0 ] && echo "stdin is a tty" >&2
if [ -n "${FAKE_SLEEP:-}" ]; then sleep "$FAKE_SLEEP" & echo $! > "$FAKE_GRANDCHILD"; wait; exit 0; fi
echo "diag line" >&2
[ -n "${FAKE_EMPTY:-}" ] && exit 0
if [ -n "${FAKE_RESULT:-}" ]; then
  jq -n --arg r "$(printf "$FAKE_RESULT")" '{type:"result",is_error:false,result:$r,total_cost_usd:1.5,duration_ms:60000,permission_denials:[]}'
else
  printf '{"type":"result","is_error":false,"result":"REVIEW TEXT","total_cost_usd":1.5,"duration_ms":60000,"permission_denials":[]}\n'
fi
exit "${FAKE_EXIT:-0}"
EOF
chmod +x "$FAKEBIN/claude"

export FAKE_ARGV="$REVIEW_PR_SCRATCH/argv" FAKE_CWD="$REVIEW_PR_SCRATCH/cwd" FAKE_GRANDCHILD="$REVIEW_PR_SCRATCH/grandchild"

# Happy path validates the adapter command, normalization, and embedded diagnostics.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
expected_cwd="$(cd "$dir/repo" && pwd -P)"
out="$(printf '%s' "$J" | "$SRC/run-child.sh" high)"
argv="$(cat "$FAKE_ARGV")"
prompt="$(awk '/^-p$/{p=1;next} /^--output-format$/{exit} p' "$FAKE_ARGV")"
for h in '## Summary' '## Critical' '## Important' '## Suggestions' '## Strengths' '## Not reviewed'; do
  grep -qF -- "$h" <<<"$prompt" || { echo "FAIL: prompt lacks heading $h"; FAIL=1; }
done
grep -qF -- '../policy-manifest.json' <<<"$prompt" || { echo "FAIL: prompt does not require the policy manifest"; FAIL=1; }
grep -qF -- '../pr.diff' <<<"$prompt" || { echo "FAIL: prompt does not require the pinned diff file"; FAIL=1; }
grep -q 'git diff' <<<"$prompt" && { echo "FAIL: prompt still asks the child to run git diff"; FAIL=1; }
grep -q '{{' <<<"$prompt" && { echo "FAIL: prompt contains an unsubstituted placeholder"; FAIL=1; }
for f in --output-format json --no-session-persistence --permission-mode dontAsk --restricted --strict-mcp-config \
         --max-budget-usd 5 --max-turns 60 --effort high --tools --add-dir \
         Read Grep Glob "$dir"; do
  grep -qxF -- "$f" <<<"$argv" || { echo "FAIL: adapter argv lacks '$f'"; FAIL=1; }
done
for forbidden in Bash Agent Edit Write WebFetch WebSearch 'Bash(git diff:*)' 'Bash(git log:*)' 'Bash(git show:*)'; do
  grep -qxF -- "$forbidden" <<<"$argv" && { echo "FAIL: write-capable shell pattern remains: $forbidden"; FAIL=1; }
done
[ "$(cat "$FAKE_CWD")" = "$expected_cwd" ] || { echo "FAIL: child cwd is not the clone"; FAIL=1; }
[ "$(jq -r .review.engine <<<"$out")" = claude ] || { echo "FAIL: normalized engine missing: $out"; FAIL=1; }
[ "$(jq -r .review.result <<<"$out")" = 'REVIEW TEXT' ] || { echo "FAIL: normalized result missing: $out"; FAIL=1; }
[ "$(jq -r .review.cost_usd <<<"$out")" = 1.5 ] || { echo "FAIL: normalized cost missing: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = false ] || { echo "FAIL: malformed review should fail schema validation"; FAIL=1; }
grep -q 'diag line' <<<"$(jq -r .stderr_tail <<<"$out")" || { echo "FAIL: stderr tail not embedded"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job directory survived normal cleanup"; FAIL=1; }

# Omitted level does not add an effort flag.
J="$(mkjob)"
out="$(printf '%s' "$J" | "$SRC/run-child.sh")"
grep -qx -- '--effort' "$FAKE_ARGV" && { echo "FAIL: --effort passed without a level"; FAIL=1; }

# Only the exact keep value preserves native artifacts.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_KEEP=0 "$SRC/run-child.sh")"
[ "$(jq -r .kept <<<"$out")" = false ] || { echo "FAIL: REVIEW_PR_KEEP=0 reported kept"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: REVIEW_PR_KEEP=0 preserved the job"; FAIL=1; }
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_KEEP=1 "$SRC/run-child.sh")"
[ "$(jq -r .kept <<<"$out")" = true ] || { echo "FAIL: REVIEW_PR_KEEP=1 did not report kept"; FAIL=1; }
[ -s "$dir/result.json" ] || { echo "FAIL: normalized result was not kept"; FAIL=1; }
grep -q 'diag line' "$dir/runner.stderr" || { echo "FAIL: native stderr was not kept"; FAIL=1; }
grep -q 'stdin is a tty' "$dir/runner.stderr" && { echo "FAIL: runner stdin was a tty"; FAIL=1; }

# Nonzero runner exits map to an error result without leaking the job directory.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | FAKE_EXIT=7 "$SRC/run-child.sh")"
[ "$(jq -r .exit <<<"$out")" = 7 ] || { echo "FAIL: runner exit 7 not reported"; FAIL=1; }
[ "$(jq -r .review.status <<<"$out")" = error ] || { echo "FAIL: runner exit 7 not normalized as error"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: failed runner job was not removed"; FAIL=1; }

# The watchdog terminates the runner process group.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
start="$(date +%s)"
out="$(printf '%s' "$J" | FAKE_SLEEP=20 REVIEW_PR_TIMEOUT=2 "$SRC/run-child.sh")"
elapsed=$(( $(date +%s) - start ))
[ "$elapsed" -lt 15 ] || { echo "FAIL: watchdog took ${elapsed}s"; FAIL=1; }
[ "$(jq -r .exit <<<"$out")" -gt 128 ] || { echo "FAIL: watchdog exit is not signal-derived"; FAIL=1; }
gc="$(cat "$FAKE_GRANDCHILD")"
if kill -0 "$gc" 2>/dev/null; then echo "FAIL: grandchild $gc survived"; FAIL=1; kill "$gc" 2>/dev/null || true; fi

# A watchdog that exits before the parent reaches kill must not suppress cleanup or output under set -e.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_TIMEOUT=0 "$SRC/run-child.sh")"
jq -e . >/dev/null 2>&1 <<<"$out" || { echo "FAIL: TIMEOUT=0 produced invalid JSON: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: TIMEOUT=0 leaked the job"; FAIL=1; }

# Cleanup refuses an unmarked directory.
bad="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
mkdir -p "$bad/repo"
git -C "$bad/repo" init -q
J="$(jq -n --arg d "$bad" '{dir:$d,runner:"claude",base_sha:"b",head_sha:"h",policy_changes:[]}')"
rc=0
err="$(printf '%s' "$J" | "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: unmarked directory exit $rc"; FAIL=1; }
[ -d "$bad" ] || { echo "FAIL: unmarked directory was deleted"; FAIL=1; }
grep -qF 'no .review-pr marker' <<<"$err" || { echo "FAIL: guard reason missing"; FAIL=1; }

# Invalid inputs still emit a cleanup envelope after ownership is established.
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_TIMEOUT=abc "$SRC/run-child.sh" 2>"$REVIEW_PR_SCRATCH/bad.stderr")" || true
[ "$(jq -r .exit <<<"$out")" = 2 ] || { echo "FAIL: invalid timeout envelope missing"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: invalid timeout leaked the job"; FAIL=1; }
grep -qF 'REVIEW_PR_TIMEOUT' "$REVIEW_PR_SCRATCH/bad.stderr" \
  || { echo "FAIL: invalid timeout diagnostic missing"; FAIL=1; }
J="$(mkjob)"
dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | "$SRC/run-child.sh" bogus 2>"$REVIEW_PR_SCRATCH/bad-level.stderr")" || true
[ "$(jq -r .exit <<<"$out")" = 2 ] || { echo "FAIL: invalid level envelope missing"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: invalid level leaked the job"; FAIL=1; }
grep -qF 'LEVEL must be one of' "$REVIEW_PR_SCRATCH/bad-level.stderr" \
  || { echo "FAIL: invalid level diagnostic missing"; FAIL=1; }

# An absent pr.json and pr-N branch reaches the explicit error instead of aborting in the grep pipeline.
job="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
: > "$job/.review-pr"
mkdir -p "$job/repo"
git -C "$job/repo" init -q
J="$(jq -n --arg d "$job" '{dir:$d,runner:"claude",base_sha:"b",head_sha:"h",policy_changes:[]}')"
rc=0
err="$(printf '%s' "$J" | "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: missing PR number exit $rc"; FAIL=1; }
[ ! -e "$job" ] || { echo "FAIL: missing PR number leaked the job"; FAIL=1; }
grep -qF 'cannot determine PR number' <<<"$err" \
  || { echo "FAIL: missing PR number diagnostic absent: $err"; FAIL=1; }

# Contract-valid, unavailable-diff, and missing native results are distinguished.
VALID_RESULT='## Summary\nLenses checked: correctness, silent-failure, tests, comments.\nLooks sound.\n\n## Critical\n(none)\n\n## Important\n(none)\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n(none)\n'
J="$(mkjob)"
out="$(printf '%s' "$J" | FAKE_RESULT="$VALID_RESULT" "$SRC/run-child.sh")"
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: valid review failed schema validation: $out"; FAIL=1; }
SENT_RESULT='## Summary\nLenses checked: correctness, silent-failure, tests, comments.\nCould not read the diff.\n\n## Critical\n(none)\n\n## Important\n(none)\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n- DIFF-UNAVAILABLE: denied\n'
J="$(mkjob)"
out="$(printf '%s' "$J" | FAKE_RESULT="$SENT_RESULT" "$SRC/run-child.sh")"
[ "$(jq -r .diff_unavailable <<<"$out")" = true ] || { echo "FAIL: diff sentinel not detected"; FAIL=1; }
J="$(mkjob)"
out="$(printf '%s' "$J" | FAKE_EMPTY=1 "$SRC/run-child.sh")"
[ "$(jq -c '[.review,.schema_valid,.schema_errors]' <<<"$out")" = '[null,false,["no result"]]' ] || { echo "FAIL: missing native result envelope is wrong: $out"; FAIL=1; }

# The lens remains the sole review-behavior source.
J="$(mkjob)"
rc=0
err="$(printf '%s' "$J" | REVIEW_PR_LENS=/nonexistent "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 3 ] || { echo "FAIL: missing lens exit $rc"; FAIL=1; }
grep -qF 'review-lens.md' <<<"$err" || { echo "FAIL: missing lens reason absent"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "run-child-test: OK"
exit "$FAIL"
