#!/usr/bin/env bash
# Offline: run-child.sh flags, capture, watchdog, cleanup, using a fake `claude` (R4, R6).
set -euo pipefail
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
export REVIEW_PR_SCRATCH; REVIEW_PR_SCRATCH="$(mktemp -d)"; trap 'rm -rf "$REVIEW_PR_SCRATCH"' EXIT
FAKEBIN="$REVIEW_PR_SCRATCH/bin"; mkdir -p "$FAKEBIN"
for c in jq git bash; do ln -sf "$(command -v $c)" "$FAKEBIN/$c"; done
export PATH="$FAKEBIN:/usr/bin:/bin"

mkjob() { # mkjob -> prints checkout JSON for a fresh job dir
  local job; job="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
  : > "$job/.review-pr"; mkdir -p "$job/repo"; git -C "$job/repo" init -q
  echo '{"number":12}' > "$job/pr.json"
  jq -n --arg d "$job" '{dir:$d, base_sha:"b", head_sha:"h", head_repo:"o/r", policy_changes:[".claude/x"], diff_path:($d+"/pr.diff"), meta_path:($d+"/pr.json")}'
}

# Fake claude: record argv and cwd, emit a result envelope.
cat > "$FAKEBIN/claude" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$FAKE_ARGV"; pwd -P > "$FAKE_CWD"
[ -t 0 ] && echo "stdin is a tty" >&2
if [ -n "${FAKE_SLEEP:-}" ]; then sleep "$FAKE_SLEEP" & echo $! > "$FAKE_GRANDCHILD"; wait; exit 0; fi
echo "diag line" >&2
[ -n "${FAKE_EMPTY:-}" ] && exit 0
if [ -n "${FAKE_RESULT:-}" ]; then
  jq -n --arg r "$(printf "$FAKE_RESULT")" '{type:"result",is_error:false,result:$r,total_cost_usd:1.5,duration_ms:60000}'
else
  printf '{"type":"result","is_error":false,"result":"REVIEW TEXT","total_cost_usd":1.5,"duration_ms":60000}\n'
fi
exit "${FAKE_EXIT:-0}"
EOF
chmod +x "$FAKEBIN/claude"

# 1. Happy path: flags, cwd, capture, cleanup.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
expected_cwd="$(cd "$dir/repo" && pwd -P)"  # captured before run-child.sh removes $dir (R6.1)
export FAKE_ARGV="$REVIEW_PR_SCRATCH/argv" FAKE_CWD="$REVIEW_PR_SCRATCH/cwd" FAKE_GRANDCHILD="$REVIEW_PR_SCRATCH/grandchild"
out="$(printf '%s' "$J" | "$SRC/run-child.sh" high)"
argv="$(cat "$FAKE_ARGV")"
grep -qx -- '-p' <<<"$argv" || { echo "FAIL: -p missing"; FAIL=1; }
# R4.1: the prompt is the lens with branches substituted; it carries the R5.6 headings and no placeholder.
prompt="$(awk '/^-p$/{p=1;next} /^--output-format$/{exit} p' "$FAKE_ARGV")"
for h in '## Summary' '## Critical' '## Important' '## Suggestions' '## Strengths' '## Not reviewed'; do
  grep -qF -- "$h" <<<"$prompt" || { echo "FAIL: prompt lacks heading $h"; FAIL=1; }
done
grep -qF -- 'git diff pr-12-base...pr-12' <<<"$prompt" || { echo "FAIL: prompt lacks substituted diff command"; FAIL=1; }
grep -q '{{' <<<"$prompt" && { echo "FAIL: unsubstituted placeholder in prompt"; FAIL=1; }
grep -q '/code-review' <<<"$prompt" && { echo "FAIL: prompt still invokes /code-review"; FAIL=1; }
# R5.7 fields on a malformed (fake) result
[ "$(jq -r .schema_valid <<<"$out")" = false ] || { echo "FAIL: fake REVIEW TEXT should be schema_valid=false: $out"; FAIL=1; }
[ "$(jq -r '.schema_errors | length' <<<"$out")" -gt 0 ] || { echo "FAIL: schema_errors empty for malformed result"; FAIL=1; }
[ "$(jq -r .diff_unavailable <<<"$out")" = false ] || { echo "FAIL: diff_unavailable should be false"; FAIL=1; }
for f in --output-format json --no-session-persistence --permission-mode dontAsk --strict-mcp-config \
         --max-budget-usd 5 --max-turns 60 --effort high --disallowedTools --allowedTools; do
  grep -qx -- "$f" <<<"$argv" || { echo "FAIL: flag/value $f missing"; FAIL=1; }
done
grep -qxF -- 'Bash(git diff:*)' <<<"$argv" || { echo "FAIL: git diff allow missing"; FAIL=1; }
# gh may appear only as a deny entry, never after --allowedTools.
sed -n '/^--allowedTools$/,$p' <<<"$argv" | grep -qw 'gh' && { echo "FAIL: gh appears in the allow list"; FAIL=1; }
# R4.3: pin every disallow and allow entry, not just a couple of representative ones.
for f in Edit Write NotebookEdit WebFetch WebSearch \
         'Bash(gh:*)' 'Bash(curl:*)' 'Bash(wget:*)' 'Bash(ssh:*)' 'Bash(git push:*)' 'Bash(git fetch:*)' 'Bash(git pull:*)' 'Bash(git remote:*)' \
         'Bash(git log:*)' 'Bash(git show:*)' 'Bash(git merge-base:*)' Read Grep Glob Skill Agent; do
  grep -qxF -- "$f" <<<"$argv" || { echo "FAIL: R4.3 argv missing '$f'"; FAIL=1; }
done
[ "$(cat "$FAKE_CWD")" = "$expected_cwd" ] || { echo "FAIL: child cwd not repo"; FAIL=1; }
[ "$(jq -r .exit <<<"$out")" = 0 ] || { echo "FAIL: exit field"; FAIL=1; }
[ "$(jq -r .kept <<<"$out")" = false ] || { echo "FAIL: kept should be false"; FAIL=1; }
[ "$(jq -c '[.head_sha, .base_sha, .policy_changes]' <<<"$out")" = '["h","b",[".claude/x"]]' ] || { echo "FAIL: checkout facts not passed through: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed on success"; FAIL=1; }
[ "$(jq -r .result "$(jq -r .child_json_path <<<"$out")")" = "REVIEW TEXT" ] || { echo "FAIL: child_json_path unreadable after cleanup"; FAIL=1; }
grep -q 'diag line' "$(jq -r .stderr_path <<<"$out")" || { echo "FAIL: stderr_path unreadable after cleanup"; FAIL=1; }
# Result copies are named per job, not a single fixed slot (two reviews in one scratchpad must not clobber each other).
case "$(jq -r .child_json_path <<<"$out")" in *"$(basename "$dir")"*) ;; *) echo "FAIL: child_json_path is not job-specific: $(jq -r .child_json_path <<<"$out")"; FAIL=1;; esac
first_json="$(jq -r .child_json_path <<<"$out")"

# 2. Level omitted -> no --effort, prompt has no trailing level.
J="$(mkjob)"; out="$(printf '%s' "$J" | "$SRC/run-child.sh")"
grep -qx -- '--effort' "$FAKE_ARGV" && { echo "FAIL: --effort passed without level"; FAIL=1; }
grep -qF -- 'git diff pr-12-base...pr-12' "$FAKE_ARGV" || { echo "FAIL: prompt without level lacks substituted diff command"; FAIL=1; }

[ "$(jq -r .result "$first_json")" = "REVIEW TEXT" ] || { echo "FAIL: first run's result was clobbered by the second run"; FAIL=1; }

# 2b. REVIEW_PR_KEEP=0 is not KEEP (R6.1 says =1): dir removed, kept=false.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_KEEP=0 "$SRC/run-child.sh")"
[ "$(jq -r .kept <<<"$out")" = false ] || { echo "FAIL: REVIEW_PR_KEEP=0 reported kept=true"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir kept with REVIEW_PR_KEEP=0"; FAIL=1; }

# 3. REVIEW_PR_KEEP=1 keeps the dir and reports the path; child.json/stderr/exit captured.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_KEEP=1 "$SRC/run-child.sh")"
[ "$(jq -r .kept <<<"$out")" = true ] || { echo "FAIL: kept should be true"; FAIL=1; }
[ -d "$dir" ] || { echo "FAIL: job dir removed despite KEEP"; FAIL=1; }
[ "$(jq -r .result "$dir/child.json")" = "REVIEW TEXT" ] || { echo "FAIL: child.json"; FAIL=1; }
grep -q 'diag line' "$dir/child.stderr" || { echo "FAIL: child.stderr"; FAIL=1; }
grep -q 'stdin is a tty' "$dir/child.stderr" && { echo "FAIL: stdin was a tty (R4.6)"; FAIL=1; }
[ "$(cat "$dir/child.exit")" = 0 ] || { echo "FAIL: child.exit"; FAIL=1; }

# 4. Non-zero child exit is reported, not masked; dir kept for inspection only with KEEP (R6.1 says removed).
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | FAKE_EXIT=7 "$SRC/run-child.sh")"
[ "$(jq -r .exit <<<"$out")" = 7 ] || { echo "FAIL: exit 7 not reported: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed after child failure"; FAIL=1; }

# 5. Watchdog: child sleeps longer than REVIEW_PR_TIMEOUT -> killed, exit reported non-zero, dir removed.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
start=$(date +%s)
out="$(printf '%s' "$J" | FAKE_SLEEP=20 REVIEW_PR_TIMEOUT=2 "$SRC/run-child.sh")"
elapsed=$(( $(date +%s) - start ))
[ "$elapsed" -lt 15 ] || { echo "FAIL: watchdog did not fire (took ${elapsed}s)"; FAIL=1; }
[ "$(jq -r .exit <<<"$out")" -gt 128 ] || { echo "FAIL: timed-out child exit not > 128: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed after timeout"; FAIL=1; }
# R4.4: the whole process group dies, not just the claude PID — a grandchild must not outlive the timeout.
gc="$(cat "$FAKE_GRANDCHILD")"
if kill -0 "$gc" 2>/dev/null; then echo "FAIL: grandchild $gc survived the watchdog"; FAIL=1; kill "$gc" 2>/dev/null || true; fi

# 6. R6.3 guard: a dir without the marker is never deleted, and the reason is reported.
bad="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"; mkdir -p "$bad/repo"; git -C "$bad/repo" init -q
J="$(jq -n --arg d "$bad" '{dir:$d, base_sha:"b", head_sha:"h", head_repo:"o/r", policy_changes:[], diff_path:"", meta_path:""}')"
rc=0; err="$(printf '%s' "$J" | "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ -d "$bad" ] || { echo "FAIL: unmarked dir was deleted"; FAIL=1; }
[ "$rc" = 1 ] || { echo "FAIL: missing marker should exit 1, got $rc"; FAIL=1; }
grep -qF 'no .review-pr marker' <<<"$err" || { echo "FAIL: stderr missing marker reason: $err"; FAIL=1; }

# 7. REVIEW_PR_TIMEOUT=0: regression for the unguarded `kill "$WATCHDOG"` bug -- the watchdog
#    can already have exited by the time the script tries to kill it, which must not abort the
#    script before cleanup/output.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | REVIEW_PR_TIMEOUT=0 "$SRC/run-child.sh")"
jq -e . >/dev/null 2>&1 <<<"$out" || { echo "FAIL: TIMEOUT=0 produced no/invalid JSON: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed with TIMEOUT=0"; FAIL=1; }

# 8. Bad REVIEW_PR_TIMEOUT (non-numeric) -> exit 2, job dir removed, stderr names REVIEW_PR_TIMEOUT.
#    Regression: this validation used to run before the EXIT trap was installed and leaked the job dir.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
rc=0; err="$(printf '%s' "$J" | REVIEW_PR_TIMEOUT=abc "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 2 ] || { echo "FAIL: REVIEW_PR_TIMEOUT=abc should exit 2, got $rc"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed for bad REVIEW_PR_TIMEOUT"; FAIL=1; }
grep -qF 'REVIEW_PR_TIMEOUT' <<<"$err" || { echo "FAIL: stderr missing REVIEW_PR_TIMEOUT: $err"; FAIL=1; }

# 8b. Bad LEVEL -> exit 2, stderr names the allowed values, stdout is valid JSON with .exit == 2, job
#     dir removed. Regression: LEVEL validation runs after KEEP is read by finish(); if KEEP is assigned
#     after the EXIT trap is installed, a bad LEVEL trips `KEEP: unbound variable` inside the trap instead.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
out="$(printf '%s' "$J" | "$SRC/run-child.sh" bogus 2>"$REVIEW_PR_SCRATCH/badlevel.stderr")" || true
err="$(cat "$REVIEW_PR_SCRATCH/badlevel.stderr")"
grep -qF 'LEVEL must be one of' <<<"$err" || { echo "FAIL: stderr missing LEVEL message: $err"; FAIL=1; }
jq -e . >/dev/null 2>&1 <<<"$out" || { echo "FAIL: bad LEVEL produced no/invalid JSON: $out"; FAIL=1; }
[ "$(jq -r .exit <<<"$out")" = 2 ] || { echo "FAIL: bad LEVEL exit field not 2: $out"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed for bad LEVEL"; FAIL=1; }

# 9. No pr.json and no pr-* branch -> exit 1, stderr names the reason, job dir removed.
#    Regression: the `head -1` pipeline with no grep match aborted under set -e before `die 1` ran.
job="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"; : > "$job/.review-pr"
mkdir -p "$job/repo"; git -C "$job/repo" init -q
J="$(jq -n --arg d "$job" '{dir:$d, base_sha:"b", head_sha:"h", head_repo:"o/r", policy_changes:[], diff_path:($d+"/pr.diff"), meta_path:($d+"/pr.json")}')"
rc=0; err="$(printf '%s' "$J" | "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: undeterminable PR number should exit 1, got $rc"; FAIL=1; }
[ ! -e "$job" ] || { echo "FAIL: job dir not removed when PR number undeterminable"; FAIL=1; }
grep -qF 'cannot determine PR number' <<<"$err" || { echo "FAIL: stderr missing PR number reason: $err"; FAIL=1; }

# 10. R5.7: a contract-valid result reports schema_valid=true; a sentinel reports diff_unavailable=true.
VALID_RESULT='## Summary\nx\n\n## Critical\n(none)\n\n## Important\n(none)\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n(none)\n'
J="$(mkjob)"; out="$(printf '%s' "$J" | FAKE_RESULT="$VALID_RESULT" "$SRC/run-child.sh")"
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: valid result not schema_valid: $out"; FAIL=1; }
SENT_RESULT='## Summary\nx\n\n## Critical\n(none)\n\n## Important\n(none)\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n- DIFF-UNAVAILABLE: denied\n'
J="$(mkjob)"; out="$(printf '%s' "$J" | FAKE_RESULT="$SENT_RESULT" "$SRC/run-child.sh")"
[ "$(jq -r .diff_unavailable <<<"$out")" = true ] || { echo "FAIL: sentinel not detected: $out"; FAIL=1; }
[ "$(jq -r .schema_valid <<<"$out")" = true ] || { echo "FAIL: sentinel result should still be schema_valid: $out"; FAIL=1; }

# 11. R5.7: when the child produces no JSON at all, the fields are false/["no result"]/false and the JSON is still emitted.
J="$(mkjob)"; out="$(printf '%s' "$J" | FAKE_EMPTY=1 "$SRC/run-child.sh")"
jq -e . >/dev/null 2>&1 <<<"$out" || { echo "FAIL: empty child output produced no/invalid JSON: $out"; FAIL=1; }
[ "$(jq -c '[.schema_valid, .schema_errors, .diff_unavailable]' <<<"$out")" = '[false,["no result"],false]' ] || { echo "FAIL: R5.7 fields for missing result: $out"; FAIL=1; }

# 12. The lens file is the single home: run-child.sh must fail loudly if it is missing, not send an empty prompt.
J="$(mkjob)"; rc=0; err="$(printf '%s' "$J" | REVIEW_PR_LENS=/nonexistent "$SRC/run-child.sh" 2>&1 >/dev/null)" || rc=$?
[ "$rc" = 3 ] || { echo "FAIL: missing lens should exit 3, got $rc"; FAIL=1; }
grep -qF 'review-lens.md' <<<"$err" || { echo "FAIL: missing lens stderr: $err"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "run-child-test: OK"
exit "$FAIL"
