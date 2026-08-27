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
if [ -n "${FAKE_SLEEP:-}" ]; then exec sleep "$FAKE_SLEEP"; fi
echo "diag line" >&2
printf '{"type":"result","is_error":false,"result":"REVIEW TEXT","total_cost_usd":1.5,"duration_ms":60000}\n'
exit "${FAKE_EXIT:-0}"
EOF
chmod +x "$FAKEBIN/claude"

# 1. Happy path: flags, cwd, capture, cleanup.
J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
expected_cwd="$(cd "$dir/repo" && pwd -P)"  # captured before run-child.sh removes $dir (R6.1)
export FAKE_ARGV="$REVIEW_PR_SCRATCH/argv" FAKE_CWD="$REVIEW_PR_SCRATCH/cwd"
out="$(printf '%s' "$J" | "$SRC/run-child.sh" high)"
argv="$(cat "$FAKE_ARGV")"
grep -qx -- '-p' <<<"$argv" || { echo "FAIL: -p missing"; FAIL=1; }
grep -q '^/code-review pr-12 high' <<<"$argv" || { echo "FAIL: prompt line: $(grep code-review <<<"$argv")"; FAIL=1; }
for f in --output-format json --no-session-persistence --permission-mode dontAsk --strict-mcp-config \
         --max-budget-usd 5 --max-turns 60 --effort high --disallowedTools --allowedTools; do
  grep -qx -- "$f" <<<"$argv" || { echo "FAIL: flag/value $f missing"; FAIL=1; }
done
grep -qxF -- 'Bash(git diff:*)' <<<"$argv" || { echo "FAIL: git diff allow missing"; FAIL=1; }
grep -qw 'gh' <<<"$argv" && { echo "FAIL: gh appears in child argv"; FAIL=1; }
# R4.3: pin every disallow and allow entry, not just a couple of representative ones.
for f in Edit Write NotebookEdit WebFetch WebSearch \
         'Bash(git log:*)' 'Bash(git show:*)' 'Bash(git merge-base:*)' Read Grep Glob Skill Agent; do
  grep -qxF -- "$f" <<<"$argv" || { echo "FAIL: R4.3 argv missing '$f'"; FAIL=1; }
done
[ "$(cat "$FAKE_CWD")" = "$expected_cwd" ] || { echo "FAIL: child cwd not repo"; FAIL=1; }
[ "$(jq -r .exit <<<"$out")" = 0 ] || { echo "FAIL: exit field"; FAIL=1; }
[ "$(jq -r .kept <<<"$out")" = false ] || { echo "FAIL: kept should be false"; FAIL=1; }
[ ! -e "$dir" ] || { echo "FAIL: job dir not removed on success"; FAIL=1; }
[ "$(jq -r .result "$(jq -r .child_json_path <<<"$out")")" = "REVIEW TEXT" ] || { echo "FAIL: child_json_path unreadable after cleanup"; FAIL=1; }
grep -q 'diag line' "$(jq -r .stderr_path <<<"$out")" || { echo "FAIL: stderr_path unreadable after cleanup"; FAIL=1; }

# 2. Level omitted -> no --effort, prompt has no trailing level.
J="$(mkjob)"; out="$(printf '%s' "$J" | "$SRC/run-child.sh")"
grep -qx -- '--effort' "$FAKE_ARGV" && { echo "FAIL: --effort passed without level"; FAIL=1; }
grep -qx -- '/code-review pr-12 — the PR head is local branch pr-12 and its base is pr-12-base; use git diff pr-12-base...pr-12' "$FAKE_ARGV" \
  || { echo "FAIL: prompt without level: $(grep code-review "$FAKE_ARGV")"; FAIL=1; }

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

[ "$FAIL" = 0 ] && echo "run-child-test: OK"
exit "$FAIL"
