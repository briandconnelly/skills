#!/usr/bin/env bash
# run-child.sh [LEVEL] < checkout JSON
# Implements the runner lifecycle and normalized envelope in references/runner-contract.md.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

need_cmd jq
[ -n "${REVIEW_PR_SCRATCH:-}" ] || die 2 "REVIEW_PR_SCRATCH must be set"

IN="$(cat)"
DIR="$(jq -er .dir <<<"$IN")" || die 2 "stdin must be the checkout-pr.sh JSON object"
RUNNER="$(jq -er .runner <<<"$IN")" || die 2 "checkout JSON does not name a runner"
CLONE="$DIR/repo"
[ -d "$CLONE" ] || die 2 "clone not found at $CLONE"
scratch_guard "$DIR"
load_adapter "$RUNNER"

CHILD_PID=""
WATCHDOG=""
CHILD_EXIT=2
FINISHED=""
NATIVE_TMP="$DIR/runner-output.tmp"
NATIVE="$DIR/runner-output"
NORMALIZED="$DIR/result.json"
STDERR="$DIR/runner.stderr"
KEEP=""
keep_requested && KEEP=1

normalize_native() {
  [ -s "$NATIVE" ] || return 1
  adapter_normalize "$NATIVE" "${CHILD_EXIT:-1}" "$NORMALIZED" || return 1
  validate_normalized_result "$NORMALIZED"
}

finish() {
  local kept=false review_json=null stderr_tail="" validation
  validation='{"schema_valid":false,"schema_errors":["no result"],"diff_unavailable":false}'
  if validate_normalized_result "$NORMALIZED"; then
    review_json="$(jq -c . "$NORMALIZED")"
    validation="$(jq -r .result "$NORMALIZED" | "$HERE/validate-result.sh")"
  fi
  [ ! -f "$STDERR" ] || stderr_tail="$(tail -n 30 "$STDERR")"
  [ -z "$KEEP" ] || kept=true

  local output
  output="$(jq -n \
    --arg runner "$RUNNER" \
    --arg stderr_tail "$stderr_tail" \
    --argjson review "$review_json" \
    --argjson ex "${CHILD_EXIT:-1}" \
    --argjson kept "$kept" \
    --arg dir "$DIR" \
    --argjson input "$IN" \
    --argjson validation "$validation" \
    '{runner:$runner, review:$review, stderr_tail:$stderr_tail, exit:$ex, kept:$kept, dir:$dir,
      head_sha:$input.head_sha, base_sha:$input.base_sha, policy_changes:($input.policy_changes // []),
      schema_valid:$validation.schema_valid, schema_errors:$validation.schema_errors,
      diff_unavailable:$validation.diff_unavailable}')"

  if [ -z "$KEEP" ]; then
    scratch_guard "$DIR" && rm -rf "$DIR"
  fi
  printf '%s\n' "$output"
}

on_exit() {
  local rc=$?
  [ -n "$FINISHED" ] && return 0
  FINISHED=1
  finish
  exit "$rc"
}
trap on_exit EXIT

on_signal() {
  trap - INT TERM
  kill "${WATCHDOG:-}" 2>/dev/null || true
  [ -n "${CHILD_PID:-}" ] && kill -TERM -- "-$CHILD_PID" 2>/dev/null || true
  CHILD_EXIT=130
  mv -f "$NATIVE_TMP" "$NATIVE" 2>/dev/null || true
  normalize_native || true
  printf '%s\n' "$CHILD_EXIT" > "$DIR/runner.exit" 2>/dev/null || true
  exit 130
}
trap on_signal INT TERM

adapter_check

LEVEL="${1:-}"
BUDGET="${REVIEW_PR_BUDGET:-5}"
TURNS="${REVIEW_PR_MAX_TURNS:-60}"
TIMEOUT="${REVIEW_PR_TIMEOUT:-900}"
[[ "$BUDGET" =~ ^[0-9]+([.][0-9]+)?$ ]] || die 2 "REVIEW_PR_BUDGET must be a non-negative number, got '$BUDGET'"
[[ "$TURNS" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_MAX_TURNS must be a non-negative integer, got '$TURNS'"
[[ "$TIMEOUT" =~ ^[0-9]+$ ]] || die 2 "REVIEW_PR_TIMEOUT must be a non-negative integer, got '$TIMEOUT'"

N="$(jq -r '.number // empty' "$DIR/pr.json" 2>/dev/null || true)"
if [ -z "$N" ]; then
  # No matching branch makes grep return 1; keep that expected miss from bypassing the explicit error below under set -e.
  N="$(git -C "$CLONE" for-each-ref --format='%(refname:short)' 'refs/heads/pr-*' | grep -E '^pr-[0-9]+$' | head -1 | sed 's/^pr-//')" || true
fi
[ -n "$N" ] || die 1 "cannot determine PR number from $DIR/pr.json or pr-N branch"

LENS="${REVIEW_PR_LENS:-$HERE/../references/review-lens.md}"
[ -r "$LENS" ] || die 3 "review lens not found: $LENS (expected review-pr/references/review-lens.md)"
PROMPT="$(sed -e "s/{{PR_BRANCH}}/pr-$N/g" "$LENS")"
adapter_build_command "$PROMPT" "$LEVEL" "$BUDGET" "$TURNS" "$DIR"

set -m
(cd "$CLONE" && exec "${ADAPTER_COMMAND[@]}" < /dev/null > "$NATIVE_TMP" 2> "$STDERR") &
CHILD_PID=$!
set +m

(
  elapsed=0
  while kill -0 "$CHILD_PID" 2>/dev/null && [ "$elapsed" -lt "$TIMEOUT" ]; do
    sleep 1
    elapsed=$((elapsed + 1))
  done
  if kill -0 "$CHILD_PID" 2>/dev/null; then
    kill -TERM -- "-$CHILD_PID" 2>/dev/null
    grace=0
    while kill -0 "$CHILD_PID" 2>/dev/null && [ "$grace" -lt 30 ]; do
      sleep 1
      grace=$((grace + 1))
    done
    kill -KILL -- "-$CHILD_PID" 2>/dev/null
  fi
) >/dev/null 2>&1 &
WATCHDOG=$!

CHILD_EXIT=0
wait "$CHILD_PID" || CHILD_EXIT=$?
# A zero-second timeout can let the watchdog exit before this cleanup signal.
kill "$WATCHDOG" 2>/dev/null || true
pkill -P "$WATCHDOG" 2>/dev/null || true
mv -f "$NATIVE_TMP" "$NATIVE"
normalize_native || printf 'review-pr: runner output did not match the normalized adapter contract\n' >&2
printf '%s\n' "$CHILD_EXIT" > "$DIR/runner.exit"
FINISHED=1
trap - INT TERM
finish
