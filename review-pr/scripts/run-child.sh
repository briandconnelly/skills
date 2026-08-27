#!/usr/bin/env bash
# run-child.sh [LEVEL]  < checkout JSON
# Launches the locked-down `claude -p` child in the clone, captures its output, cleans up.
# Spec R4, R6.1, R6.3.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

LEVEL="${1:-}"
if [ -n "$LEVEL" ]; then
  case "$LEVEL" in low|medium|high|xhigh|max) ;; *) die 2 "LEVEL must be one of low|medium|high|xhigh|max, got '$LEVEL'";; esac
fi
for c in jq claude; do need_cmd "$c"; done
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set"

IN="$(cat)"
DIR="$(jq -er .dir <<<"$IN")" || die 2 "stdin must be the checkout-pr.sh JSON object"
CLONE="$DIR/repo"
[ -d "$CLONE" ] || die 2 "clone not found at $CLONE"
scratch_guard "$DIR"                                   # R6.3, before anything that might delete

# R6.1/R5: purge any previous run's leftovers now, before this run can fail or
# be interrupted. Once claude has been launched below, finish() copies
# child.json/child.stderr here; if that copy never happens or fails, the
# paths must point at nothing rather than a stale prior review.
rm -f "$REVIEW_PR_SCRATCH/review-pr-last.json" "$REVIEW_PR_SCRATCH/review-pr-last.stderr"

BUDGET="${REVIEW_PR_BUDGET:-5}"
TURNS="${REVIEW_PR_MAX_TURNS:-60}"
TIMEOUT="${REVIEW_PR_TIMEOUT:-900}"
KEEP="${REVIEW_PR_KEEP:-}"
[[ "$BUDGET" =~ ^[0-9]+([.][0-9]+)?$ ]] || die 2 "REVIEW_PR_BUDGET must be a non-negative number, got '$BUDGET'"
[[ "$TURNS" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_TURNS must be a non-negative integer, got '$TURNS'"
[[ "$TIMEOUT" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_TIMEOUT must be a non-negative integer, got '$TIMEOUT'"

CHILD_PID=""
WATCHDOG=""
CHILD_EXIT=1
FINISHED=""
TMP_JSON="$DIR/child.json.tmp"

finish() {
  # R6.1 removes the job dir on every outcome, so the results are copied out first (R5 needs them).
  local kept=false cj="$DIR/child.json" se="$DIR/child.stderr"
  if [ -n "$KEEP" ]; then
    kept=true
  else
    cp -f "$DIR/child.json" "$REVIEW_PR_SCRATCH/review-pr-last.json" 2>/dev/null || true
    cp -f "$DIR/child.stderr" "$REVIEW_PR_SCRATCH/review-pr-last.stderr" 2>/dev/null || true
    cj="$REVIEW_PR_SCRATCH/review-pr-last.json"; se="$REVIEW_PR_SCRATCH/review-pr-last.stderr"
    scratch_guard "$DIR" && rm -rf "$DIR"
  fi
  jq -n --arg cj "$cj" --arg se "$se" --argjson ex "${CHILD_EXIT:-1}" --argjson k "$kept" --arg d "$DIR" \
    '{child_json_path:$cj, stderr_path:$se, exit:$ex, kept:$k, dir:$d}'
}

# R6.1 binding: the job dir must be removed (or the JSON emitted, if kept) on
# EVERY exit path, not just the happy one. An EXIT trap guarantees finish()
# runs even if a `die` fires partway through, or `set -e` aborts the script
# on an unexpected failure after the child has started. FINISHED guards
# against running finish() twice: the explicit call at the bottom of the
# normal path sets it before the EXIT trap gets a chance to fire again.
on_exit() {
  local rc=$?
  [ -n "$FINISHED" ] && return 0
  FINISHED=1
  finish
  exit "$rc"
}
trap on_exit EXIT

on_signal() {
  trap - INT TERM                                     # re-entrancy: a second signal just kills us
  kill "${WATCHDOG:-}" 2>/dev/null || true
  [ -n "${CHILD_PID:-}" ] && kill -TERM "$CHILD_PID" 2>/dev/null
  CHILD_EXIT=130
  # R4.5: salvage whatever the child wrote so far, best-effort, before finish() runs via the EXIT trap.
  mv -f "$TMP_JSON" "$DIR/child.json" 2>/dev/null || true
  printf '%s\n' "$CHILD_EXIT" > "$DIR/child.exit" 2>/dev/null || true
  exit 130
}
trap on_signal INT TERM

N="$(jq -r '.number // empty' "$DIR/pr.json" 2>/dev/null || true)"
if [ -z "$N" ]; then
  N="$(git -C "$CLONE" for-each-ref --format='%(refname:short)' 'refs/heads/pr-*' | grep -E '^pr-[0-9]+$' | head -1 | sed 's/^pr-//')"
fi
[ -n "$N" ] || die 1 "cannot determine PR number from $DIR/pr.json or pr-N branch"

PROMPT="/code-review pr-$N"
[ -n "$LEVEL" ] && PROMPT="$PROMPT $LEVEL"
ARGS=(-p "$PROMPT" --output-format json --no-session-persistence
      --permission-mode dontAsk --strict-mcp-config
      --max-budget-usd "$BUDGET" --max-turns "$TURNS")
[ -n "$LEVEL" ] && ARGS+=(--effort "$LEVEL")
ARGS+=(--disallowedTools Edit Write NotebookEdit WebFetch WebSearch
       --allowedTools 'Bash(git diff:*)' 'Bash(git log:*)' 'Bash(git show:*)' 'Bash(git merge-base:*)' Read Grep Glob Skill Agent)

# R4.5 atomic write of child.json; R4.6 stdin from /dev/null.
( cd "$CLONE" && exec claude "${ARGS[@]}" < /dev/null > "$TMP_JSON" 2> "$DIR/child.stderr" ) &
CHILD_PID=$!

# R4.4 watchdog: TERM at deadline, KILL 30s later.
# Polls in 1s steps (rather than one long `sleep "$TIMEOUT"`) so the watchdog
# subshell exits on its own as soon as the child does: killing a shell that is
# blocked in a long foreground `sleep` reparents that sleep to PID 1 before a
# subsequent `pkill -P "$WATCHDOG"` can catch it, leaving an orphaned sleep
# that lingers for the rest of its duration (reproduced: a 20s sleep survived
# its watchdog's death and kept running as an init child). Short polls bound
# the orphan risk to about a second either way.
# Redirected to /dev/null so this subshell cannot hold open the caller's
# stdout/stderr (relevant when run-child.sh's own output is captured via
# command substitution, e.g. in tests).
(
  elapsed=0
  while kill -0 "$CHILD_PID" 2>/dev/null && [ "$elapsed" -lt "$TIMEOUT" ]; do
    sleep 1; elapsed=$((elapsed + 1))
  done
  if kill -0 "$CHILD_PID" 2>/dev/null; then
    kill -TERM "$CHILD_PID" 2>/dev/null
    grace=0
    while kill -0 "$CHILD_PID" 2>/dev/null && [ "$grace" -lt 30 ]; do
      sleep 1; grace=$((grace + 1))
    done
    kill -KILL "$CHILD_PID" 2>/dev/null
  fi
) >/dev/null 2>&1 &
WATCHDOG=$!

CHILD_EXIT=0
wait "$CHILD_PID" || CHILD_EXIT=$?
# The watchdog may already have exited on its own (it polls and self-terminates
# once the child is gone, including instantly when REVIEW_PR_TIMEOUT=0) --
# `kill` on an already-dead PID fails under `set -e` and must not abort the
# script before the mv/child.exit/finish below run.
kill "$WATCHDOG" 2>/dev/null || true
pkill -P "$WATCHDOG" 2>/dev/null || true
mv -f "$TMP_JSON" "$DIR/child.json"
printf '%s\n' "$CHILD_EXIT" > "$DIR/child.exit"
FINISHED=1
trap - INT TERM
finish
