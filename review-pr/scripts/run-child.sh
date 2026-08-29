#!/usr/bin/env bash
# run-child.sh [LEVEL]  < checkout JSON
# Launches the locked-down `claude -p` child in the clone, captures its output, cleans up.
# Spec R4, R5.7, R6.1, R6.3.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"
# shellcheck disable=SC1091
. "$HERE/child-flags.sh"

for c in jq claude; do need_cmd "$c"; done
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set"

IN="$(cat)"
DIR="$(jq -er .dir <<<"$IN")" || die 2 "stdin must be the checkout-pr.sh JSON object"
CLONE="$DIR/repo"
[ -d "$CLONE" ] || die 2 "clone not found at $CLONE"
scratch_guard "$DIR"                                   # R6.3, before anything that might delete

CHILD_PID=""
WATCHDOG=""
CHILD_EXIT=2                                            # honest default: die-before-launch means usage/prereq failure
FINISHED=""
TMP_JSON="$DIR/child.json.tmp"
KEEP=""; keep_requested && KEEP=1                       # finish() reads this; must be set before the EXIT trap below
JOBNAME="$(basename "$DIR")"                            # per-job result names: two reviews in one scratchpad never clobber each other

finish() {
  # R6.1 removes the job dir on every outcome, so the results are copied out first (R5 needs them).
  local kept=false cj="$DIR/child.json" se="$DIR/child.stderr"
  # R5.7: validate the contract before the job dir can be removed; a missing or invalid
  # child.json yields false/["no result"]/false.
  local v='{"schema_valid":false,"schema_errors":["no result"],"diff_unavailable":false}'
  if [ -s "$DIR/child.json" ] && jq -e . "$DIR/child.json" >/dev/null 2>&1; then
    v="$(jq -r '.result // ""' "$DIR/child.json" | "$HERE/validate-result.sh")"
  fi
  if [ -n "$KEEP" ]; then
    kept=true
  else
    cp -f "$DIR/child.json" "$REVIEW_PR_SCRATCH/$JOBNAME.child.json" 2>/dev/null || true
    cp -f "$DIR/child.stderr" "$REVIEW_PR_SCRATCH/$JOBNAME.child.stderr" 2>/dev/null || true
    cj="$REVIEW_PR_SCRATCH/$JOBNAME.child.json"; se="$REVIEW_PR_SCRATCH/$JOBNAME.child.stderr"
    scratch_guard "$DIR" && rm -rf "$DIR"
  fi
  # head_sha, base_sha, and policy_changes are passed through from the checkout JSON so the relay
  # step reads one file.
  jq -n --arg cj "$cj" --arg se "$se" --argjson ex "${CHILD_EXIT:-1}" --argjson k "$kept" --arg d "$DIR" --argjson in "$IN" --argjson v "$v" \
    '{child_json_path:$cj, stderr_path:$se, exit:$ex, kept:$k, dir:$d,
      head_sha:$in.head_sha, base_sha:$in.base_sha, policy_changes:($in.policy_changes // []),
      schema_valid:$v.schema_valid, schema_errors:$v.schema_errors, diff_unavailable:$v.diff_unavailable}'
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
  [ -n "${CHILD_PID:-}" ] && kill -TERM -- "-$CHILD_PID" 2>/dev/null
  CHILD_EXIT=130
  # R4.5: salvage whatever the child wrote so far, best-effort, before finish() runs via the EXIT trap.
  mv -f "$TMP_JSON" "$DIR/child.json" 2>/dev/null || true
  printf '%s\n' "$CHILD_EXIT" > "$DIR/child.exit" 2>/dev/null || true
  exit 130
}
trap on_signal INT TERM

# LEVEL and the numeric env vars are validated only now, with the EXIT trap
# already installed: a `die 2` here still removes the job dir (or emits the
# kept-JSON) via finish(), instead of leaking it as it did when this
# validation ran before the trap was in place.
LEVEL="${1:-}"
if [ -n "$LEVEL" ]; then
  case "$LEVEL" in low|medium|high|xhigh|max) ;; *) die 2 "LEVEL must be one of low|medium|high|xhigh|max, got '$LEVEL'";; esac
fi

# R6.1/R5: the result copies are named after this job's unique mktemp directory, so a
# copy that never happens leaves the reported paths pointing at nothing rather than at a
# stale prior review; no purge of earlier runs is needed or wanted.
rm -f "$REVIEW_PR_SCRATCH/$JOBNAME.child.json" "$REVIEW_PR_SCRATCH/$JOBNAME.child.stderr"

BUDGET="${REVIEW_PR_BUDGET:-5}"
TURNS="${REVIEW_PR_MAX_TURNS:-60}"
TIMEOUT="${REVIEW_PR_TIMEOUT:-900}"
[[ "$BUDGET" =~ ^[0-9]+([.][0-9]+)?$ ]] || die 2 "REVIEW_PR_BUDGET must be a non-negative number, got '$BUDGET'"
[[ "$TURNS" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_TURNS must be a non-negative integer, got '$TURNS'"
[[ "$TIMEOUT" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_TIMEOUT must be a non-negative integer, got '$TIMEOUT'"

N="$(jq -r '.number // empty' "$DIR/pr.json" 2>/dev/null || true)"
if [ -z "$N" ]; then
  # grep exits 1 with no match; under `set -e` that would abort the script
  # before the `die 1` below ever runs, so the failure must be tolerated here.
  N="$(git -C "$CLONE" for-each-ref --format='%(refname:short)' 'refs/heads/pr-*' | grep -E '^pr-[0-9]+$' | head -1 | sed 's/^pr-//')" || true
fi
[ -n "$N" ] || die 1 "cannot determine PR number from $DIR/pr.json or pr-N branch"

# R4.1/R4.7: the prompt is the skill-owned lens with the local branch names substituted.
LENS="${REVIEW_PR_LENS:-$HERE/../references/review-lens.md}"
[ -r "$LENS" ] || die 3 "review lens not found: $LENS (expected review-pr/references/review-lens.md)"
PROMPT="$(sed -e "s/{{PR_BRANCH}}/pr-$N/g" -e "s/{{BASE_BRANCH}}/pr-$N-base/g" "$LENS")"
ARGS=(-p "$PROMPT" "${CHILD_FLAGS[@]}" --max-budget-usd "$BUDGET" --max-turns "$TURNS")
[ -n "$LEVEL" ] && ARGS+=(--effort "$LEVEL")

# R4.5 atomic write of child.json; R4.6 stdin from /dev/null.
# R4.4: job control (set -m) puts the background job in its own process group whose id is
# CHILD_PID, so TERM/KILL below reach every descendant claude spawns, not only the claude PID.
set -m
( cd "$CLONE" && exec claude "${ARGS[@]}" < /dev/null > "$TMP_JSON" 2> "$DIR/child.stderr" ) &
CHILD_PID=$!
set +m

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
    kill -TERM -- "-$CHILD_PID" 2>/dev/null
    grace=0
    while kill -0 "$CHILD_PID" 2>/dev/null && [ "$grace" -lt 30 ]; do
      sleep 1; grace=$((grace + 1))
    done
    kill -KILL -- "-$CHILD_PID" 2>/dev/null
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
