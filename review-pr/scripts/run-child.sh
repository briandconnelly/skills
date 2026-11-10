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

# From here on the result envelope is emitted on exit, so failures before the child starts must
# land in the runner stderr file that becomes stderr_tail, not only on this script's stderr.
die() { # die CODE MESSAGE...
  local code="$1"; shift
  printf 'review-pr: %s\n' "$*" | tee -a "$STDERR" >&2
  exit "$code"
}

normalize_native() {
  [ -s "$NATIVE" ] || return 1
  adapter_normalize "$NATIVE" "${CHILD_EXIT:-1}" "$NORMALIZED" || return 1
  validate_normalized_result "$NORMALIZED"
}

# The envelope is assembled from files, never argv: the review, the stderr tail and the checkout's
# policy_changes can each exceed a single argument's size limit.
finish() {
  local kept=false validation review_file="$DIR/envelope-review.json"
  validation='{"schema_valid":false,"schema_errors":["no result"],"diff_unavailable":false}'
  printf 'null\n' > "$review_file"
  if validate_normalized_result "$NORMALIZED"; then
    review_file="$NORMALIZED"
    if ! validation="$(jq -r .result "$NORMALIZED" | "$HERE/validate-result.sh")" \
      || ! validation="$(jq -ces 'select(length == 1 and (.[0] | type == "object" and (.schema_valid | type == "boolean") and (.schema_errors | type == "array") and (.diff_unavailable | type == "boolean"))) | .[0]' <<<"$validation" 2>/dev/null)"; then
      validation='{"schema_valid":false,"schema_errors":["result validator failed"],"diff_unavailable":false}'
    fi
  fi
  printf '%s\n' "$validation" > "$DIR/envelope-validation.json"
  printf '%s\n' "$IN" > "$DIR/envelope-checkout.json"
  : > "$DIR/envelope-stderr-tail"
  # tail -c can split a multibyte character, and jq --rawfile reads each invalid byte as a three-byte U+FFFD,
  # so the jq program below drops a leading U+FFFD run and trims again until the tail fits in 16384 bytes.
  [ ! -f "$STDERR" ] || tail -n 30 "$STDERR" | tail -c 16384 > "$DIR/envelope-stderr-tail"
  [ -z "$KEEP" ] || kept=true

  local output
  output="$(jq -n \
    --arg runner "$RUNNER" \
    --rawfile stderr_raw "$DIR/envelope-stderr-tail" \
    --slurpfile review_doc "$review_file" \
    --argjson ex "${CHILD_EXIT:-1}" \
    --argjson kept "$kept" \
    --arg dir "$DIR" \
    --slurpfile input_doc "$DIR/envelope-checkout.json" \
    --slurpfile validation_doc "$DIR/envelope-validation.json" \
    '($stderr_raw | sub("^�+"; "") | sub("\n+$"; "")
       | until(utf8bytelength <= 16384; .[((length / 8) | floor | if . < 1 then 1 else . end):])) as $stderr_tail |
     $review_doc[0] as $review |
     $input_doc[0] as $input | $validation_doc[0] as $validation |
     {runner:$runner, review:$review, stderr_tail:$stderr_tail, exit:$ex, kept:$kept, dir:$dir,
      head_sha:$input.head_sha, base_sha:$input.base_sha, merge_base_sha:($input.merge_base_sha // null),
      policy_changes:($input.policy_changes // []),
      pr_state:($input.pr_state // null), pr_is_draft:(if ($input | has("pr_is_draft")) then $input.pr_is_draft else null end),
      pr_merged_at:($input.pr_merged_at // null), pr_author:($input.pr_author // null),
      pr_author_is_bot:(if ($input | has("pr_author_is_bot")) then $input.pr_author_is_bot else null end),
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

# reap_group PGID: end every process left in the runner's group, including descendants that outlive the
# leader or ignore TERM. Returns at once when the group is already empty, so a clean run is not delayed.
reap_group() {
  local pgid="$1" waited=0
  kill -0 -- "-$pgid" 2>/dev/null || return 0
  kill -TERM -- "-$pgid" 2>/dev/null || true
  while [ "$waited" -lt 5 ] && kill -0 -- "-$pgid" 2>/dev/null; do
    sleep 1
    waited=$((waited + 1))
  done
  kill -KILL -- "-$pgid" 2>/dev/null || true
  # A killed orphan stays signalable until init reaps it; wait briefly so the group is gone on return.
  waited=0
  while [ "$waited" -lt 20 ] && kill -0 -- "-$pgid" 2>/dev/null; do
    sleep 0.1
    waited=$((waited + 1))
  done
}

stop_watchdog() {
  [ -n "${WATCHDOG:-}" ] || return 0
  kill "$WATCHDOG" 2>/dev/null || true
  pkill -P "$WATCHDOG" 2>/dev/null || true
}

on_signal() {
  # Ignored, not reset: a second signal during the reap below must not end this script before it has
  # killed the group and emitted the envelope.
  trap '' INT TERM
  if [ -n "${CHILD_PID:-}" ]; then
    reap_group "$CHILD_PID"
  fi
  stop_watchdog
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
    # Marked before the signal, so the parent can tell a timeout from a runner that failed on its own.
    : > "$DIR/runner.timeout"
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
# The leader's exit does not end its group: reap what it left behind before the watchdog, which would
# otherwise have sent the final KILL, is stopped.
reap_group "$CHILD_PID"
# A zero-second timeout can let the watchdog exit before this cleanup signal.
stop_watchdog
# The watchdog can kill the child's process group before its redirection creates the output file (a zero-second
# timeout races the fork), so a missing file is an empty result for normalize_native to report, not a fatal error.
if [ -e "$NATIVE_TMP" ]; then mv -f "$NATIVE_TMP" "$NATIVE"; fi
if [ -e "$DIR/runner.timeout" ]; then
  normalize_native || true
  printf 'review-pr: runner timed out after %ss (REVIEW_PR_TIMEOUT)\n' "$TIMEOUT" | tee -a "$STDERR" >&2
else
  normalize_native || printf 'review-pr: runner output did not match the normalized adapter contract\n' | tee -a "$STDERR" >&2
fi
printf '%s\n' "$CHILD_EXIT" > "$DIR/runner.exit"
FINISHED=1
trap - INT TERM
finish
