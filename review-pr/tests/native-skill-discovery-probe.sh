#!/usr/bin/env bash
# native-skill-discovery-probe.sh RUNNER
# Runner-backed probe for #231: does the runner's CLI, under the adapter's exact command, give the child the
# repository's skill names and descriptions on its own? A skill description and a skill body each carry a nonce
# that appears in no prompt; the child is told not to read files or call tools and to repeat any skill it was
# told about. The same prompt without the adapter's restrictions is the known positive, so a NONE answer under
# the adapter is evidence only when that control surfaces the description nonce.
# Prints one line per arm. Exits 0 only when both arms completed and the control surfaced the description nonce;
# exits 1 as inconclusive otherwise, since a failed run would read as "not given"; skips (77) when not runnable.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
RUNNER="${1:-}"
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"
[ -n "$RUNNER" ] || die 2 "usage: native-skill-discovery-probe.sh RUNNER"
load_adapter "$RUNNER"
if ! (adapter_check) >/dev/null 2>&1; then echo "native-skill-discovery-probe: SKIP ($RUNNER not runnable)"; exit 77; fi
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
nonce() { printf '%s-%s' "$1" "$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"; }
DESC="$(nonce DESC)"; BODY="$(nonce BODY)"
R="$S/repo"; mkdir -p "$R"
git -C "$R" init -q -b main
printf '%s\n' '# Probe repository' > "$R/AGENTS.md"
# Claude Code discovers .claude/skills and Codex discovers .agents/skills, so the probe skill is in both.
for root in .claude/skills .agents/skills; do
  mkdir -p "$R/$root/release-probe"
  printf -- '---\nname: release-probe\ndescription: Use when drafting release notes. Marker %s.\n---\n# Release probe\n\nBody marker %s.\n' \
    "$DESC" "$BODY" > "$R/$root/release-probe/SKILL.md"
done
git -C "$R" add -A && git -C "$R" -c user.email=t@example.com -c user.name=t -c commit.gpgsign=false commit -qm probe
Q="Do not call any tools and do not read any files. List the name and full description of every skill you were told about in your instructions or context, verbatim, one per line. If you were told about no skills, answer exactly NONE."

completed() { # completed RAW -> success when the process exited 0 and produced a final answer without an error
  [ "$(cat "$1.status")" = 0 ] || return 1
  case "$RUNNER" in
    claude) jq -e '.type == "result" and (.is_error // false) == false and (.result | type) == "string"' "$1" > /dev/null 2>&1;;
    codex) jq -se '([.[] | select(.type == "error" or .type == "turn.failed")] | length) == 0 and
                   ([.[] | select(.type == "turn.completed")] | length) > 0 and
                   ([.[] | select(.type == "item.completed" and .item.type == "agent_message")] | length) > 0' "$1" > /dev/null 2>&1;;
  esac
}
# untouched RAW -> success when the run used no tool, so a nonce in its answer came from its context, not a file read.
# Claude's JSON output has no tool transcript, but any tool call costs a second turn.
untouched() {
  case "$RUNNER" in
    claude) jq -e '.num_turns == 1' "$1" > /dev/null 2>&1;;
    codex) jq -se '([.[] | select(.type == "item.started" or .type == "item.completed") | select(.item.type != "agent_message" and .item.type != "reasoning")] | length) == 0' "$1" > /dev/null 2>&1;;
  esac
}
answer() { # answer RAW -> the child's final text
  case "$RUNNER" in
    claude) jq -r '.result' "$1";;
    codex) jq -rs '[.[] | select(.type == "item.completed" and .item.type == "agent_message") | .item.text] | last' "$1";;
  esac
}
# shellcheck disable=SC2016 # Backticks in the sed pattern are literal Markdown.
report() { # report ARM RAW
  local text
  if ! completed "$2"; then
    printf '%s %s: INCONCLUSIVE, the run did not complete: %s\n' "$RUNNER" "$1" "$(tail -c 300 "$2.err" 2>/dev/null | tr '\n' ' ')"
    return 1
  fi
  if ! untouched "$2"; then
    printf '%s %s: INCONCLUSIVE, the run used a tool, so a nonce in its answer may come from reading the file\n' "$RUNNER" "$1"
    return 1
  fi
  text="$(answer "$2")"
  printf '%s %s: description=%s body=%s skills=%s\n' "$RUNNER" "$1" \
    "$(grep -qF "$DESC" <<<"$text" && echo seen || echo absent)" \
    "$(grep -qF "$BODY" <<<"$text" && echo seen || echo absent)" \
    "$(sed -nE 's/^[-*[:space:]`]*([A-Za-z0-9:_.-]+)`?[[:space:]]*[:—-].*/\1/p' <<<"$text" | sort -u | paste -sd, - | cut -c1-400)"
}

adapter_build_command "$Q" low 1 3 "$S"
rc=0; (cd "$R" && "${ADAPTER_COMMAND[@]}" < /dev/null > "$S/adapter.raw" 2> "$S/adapter.raw.err") || rc=$?
echo "$rc" > "$S/adapter.raw.status"
FAIL=0
report adapter "$S/adapter.raw" || FAIL=1

# Known positive: the same CLI and prompt without the adapter's skill and context restrictions, still read-only.
rc=0
case "$RUNNER" in
  claude) (cd "$R" && claude -p "$Q" --output-format json --no-session-persistence --max-turns 2 --max-budget-usd 1 \
            < /dev/null > "$S/control.raw" 2> "$S/control.raw.err") || rc=$?;;
  codex) (cd "$R" && codex exec --json --ephemeral --sandbox read-only --color never -c 'approval_policy="never"' "$Q" \
            < /dev/null > "$S/control.raw" 2> "$S/control.raw.err") || rc=$?;;
esac
echo "$rc" > "$S/control.raw.status"
report control "$S/control.raw" || FAIL=1
if [ "$FAIL" = 0 ] && ! answer "$S/control.raw" | grep -qF "$DESC"; then
  echo "$RUNNER: INCONCLUSIVE, the control did not surface the probe skill, so a negative adapter result is no evidence"
  FAIL=1
fi
exit "$FAIL"
