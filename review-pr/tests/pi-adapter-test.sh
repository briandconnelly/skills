#!/usr/bin/env bash
# Offline: pi adapter flags, policy selection, level mapping, and JSONL normalization.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
unset REVIEW_PR_PI_MODEL REVIEW_PR_PI_EXTENSIONS
FAIL=0
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
# pi is listed in scripts/adapters/supported only after its RC7 gates pass, so until then test a copy that lists it.
if ! grep -Fxq pi "$ROOT/scripts/adapters/supported"; then
  CANDIDATE="$(mktemp -d)"
  trap 'rm -rf "$CANDIDATE"' EXIT
  rsync -a --exclude tests/evidence "$ROOT/" "$CANDIDATE/"
  echo pi >> "$CANDIDATE/scripts/adapters/supported"
  ROOT="$CANDIDATE"
fi
SRC="$ROOT/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"

S="$(mktemp -d)"
trap 'rm -rf "$S" "${CANDIDATE:-}"' EXIT
FAKEBIN="$S/bin"
mkdir -p "$FAKEBIN"
fake_pi() { printf '#!/usr/bin/env bash\necho %q\n' "$1" > "$FAKEBIN/pi"; chmod +x "$FAKEBIN/pi"; }
fake_pi 1.2.0
PATH="$FAKEBIN:$PATH"
export PATH

load_adapter pi
adapter_check

for case_data in '1.1.9|pi 1.2.0 or newer' '1.2.0-beta.1|cannot parse pi version' 'unexpected|cannot parse pi version'; do
  fake_version="${case_data%%|*}"
  want_error="${case_data#*|}"
  fake_pi "$fake_version"
  rc=0
  (adapter_check) >/dev/null 2>"$S/version.err" || rc=$?
  [ "$rc" = 3 ] || { echo "FAIL: pi version $fake_version was accepted"; FAIL=1; }
  grep -qF "$want_error" "$S/version.err" || { echo "FAIL: pi version $fake_version has the wrong error"; FAIL=1; }
done
fake_pi 1.2.0
[ "${ADAPTER_POLICY_ROOTS[*]}" = '.pi .agents .claude' ] || { echo "FAIL: pi policy roots changed"; FAIL=1; }
for p in .pi/settings.json .pi/mcp.json .pi/SYSTEM.md .pi/APPEND_SYSTEM.md .pi/extensions .pi/prompts .pi/themes .pi/npm .pi/git; do
  [[ " ${ADAPTER_ALWAYS_REMOVE[*]} " == *" $p "* ]] || { echo "FAIL: pi executable configuration $p is not removed"; FAIL=1; }
done
[[ " ${ADAPTER_ALWAYS_REMOVE[*]} " == *" .pi/skills "* ]] && { echo "FAIL: pi passive skills are removed"; FAIL=1; }

adapter_build_command 'PROMPT-SENTINEL' high 9 17 "$S"
args="$(printf '<%s>\n' "${ADAPTER_COMMAND[@]}")"
for arg in \
  '<pi>' '<-p>' '<--mode>' '<json>' '<--no-session>' '<--no-approve>' '<--offline>' \
  '<--no-extensions>' '<--no-skills>' '<--no-prompt-templates>' '<--no-themes>' '<--no-context-files>' '<--no-mcp>' \
  '<--tools>' '<read,grep,find,ls>' '<--thinking>' '<high>';
do
  grep -qxF "$arg" <<<"$args" || { echo "FAIL: pi command lacks $arg"; FAIL=1; }
done
n="${#ADAPTER_COMMAND[@]}"
[ "${ADAPTER_COMMAND[n-2]}" = '--' ] && [ "${ADAPTER_COMMAND[n-1]}" = 'PROMPT-SENTINEL' ] \
  || { echo "FAIL: prompt is not the final pi argument after --"; FAIL=1; }
for arg in '<-e>' '<--model>' '<--approve>' '<9>' '<17>'; do
  grep -qxF "$arg" <<<"$args" && { echo "FAIL: pi command unexpectedly has $arg"; FAIL=1; }
done

adapter_build_command p '' 1 1 "$S"
printf '<%s>\n' "${ADAPTER_COMMAND[@]}" | grep -qxF '<--thinking>' && { echo "FAIL: empty level passed --thinking"; FAIL=1; }

mkdir -p "$S/ext-a" "$S/ext b"
REVIEW_PR_PI_MODEL='litellm/some-model' REVIEW_PR_PI_EXTENSIONS="$S/ext-a:$S/ext b" adapter_build_command p low 1 1 "$S"
args="$(printf '<%s>\n' "${ADAPTER_COMMAND[@]}")"
if ! grep -qxF "<$S/ext-a>" <<<"$args" || ! grep -qxF "<$S/ext b>" <<<"$args"; then
  echo "FAIL: REVIEW_PR_PI_EXTENSIONS entries are not passed: $args"; FAIL=1
fi
[ "$(grep -cxF '<-e>' <<<"$args")" = 2 ] || { echo "FAIL: each extension needs its own -e"; FAIL=1; }
grep -qxF '<litellm/some-model>' <<<"$args" || { echo "FAIL: REVIEW_PR_PI_MODEL is not passed"; FAIL=1; }
rc=0
(REVIEW_PR_PI_EXTENSIONS="$S/missing" adapter_build_command p low 1 1 "$S") >/dev/null 2>"$S/ext.err" || rc=$?
if [ "$rc" != 3 ] || ! grep -qF "$S/missing" "$S/ext.err"; then echo "FAIL: a missing extension path was accepted"; FAIL=1; fi

for level in low medium high xhigh max; do
  (adapter_build_command p "$level" 1 1 "$S") || { echo "FAIL: pi rejected level $level"; FAIL=1; }
done
for level in off minimal ultra; do
  rc=0
  (adapter_build_command p "$level" 1 1 "$S") >/dev/null 2>"$S/level.err" || rc=$?
  [ "$rc" = 2 ] || { echo "FAIL: pi accepted unsupported level $level"; FAIL=1; }
done
grep -qF 'low|medium|high|xhigh|max' "$S/level.err" || { echo "FAIL: invalid-level error is not actionable"; FAIL=1; }

for p in AGENTS.md pkg/CLAUDE.md pkg/AGENTS.override.md x/AGENTS.MD x/CLAUDE.MD .pi/settings.json .agents/skills/a/SKILL.md .claude/skills/a/SKILL.md; do
  adapter_is_policy_path "$p" || { echo "FAIL: $p is not pi policy"; FAIL=1; }
done
for p in README.md nested/.pi/settings.json nested/.agents/skills/a/SKILL.md docs/AGENTS.md.bak; do
  adapter_is_policy_path "$p" && { echo "FAIL: $p was treated as pi policy"; FAIL=1; }
done

R="$S/repo"
git -C "$S" init -q repo
git -C "$R" config user.email t@example.com
git -C "$R" config user.name t
mkdir -p "$R/a" "$R/b" "$R/c" "$R/d" "$R/.agents/skills/one" "$R/.pi/skills/two" "$R/.pi/skills/nested/three" \
  "$R/.claude/skills/four" "$R/.claude/agents" "$R/.pi/extensions" "$R/.pi/prompts" "$R/nested/.agents/skills/ignored"
echo root > "$R/AGENTS.md"
echo root-claude > "$R/CLAUDE.md"
echo a-claude > "$R/a/CLAUDE.md"
echo b-agents > "$R/b/AGENTS.md"
echo b-override > "$R/b/AGENTS.override.md"
echo c-upper > "$R/c/AGENTS.MD"
echo c-claude > "$R/c/CLAUDE.md"
echo d-upper-claude > "$R/d/CLAUDE.MD"
for p in .agents/skills/one .pi/skills/two .pi/skills/nested/three .claude/skills/four nested/.agents/skills/ignored; do
  echo skill > "$R/$p/SKILL.md"
done
echo reference > "$R/.pi/skills/two/reference.md"
echo agent > "$R/.claude/agents/reviewer.md"
echo ext > "$R/.pi/extensions/evil.ts"
echo prompt > "$R/.pi/prompts/review.md"
echo '{}' > "$R/.pi/settings.json"
echo system > "$R/.pi/SYSTEM.md"
git -C "$R" add -A
git -C "$R" commit -qm base
sha="$(git -C "$R" rev-parse HEAD)"
got="$(context_paths_json "$R" "$sha" | jq -c sort)"
want="$(jq -nc '[
  "AGENTS.md", "a/CLAUDE.md", "b/AGENTS.override.md", "c/AGENTS.MD", "d/CLAUDE.MD",
  ".agents/skills/one/SKILL.md", ".pi/skills/two/SKILL.md", ".pi/skills/nested/three/SKILL.md", ".claude/skills/four/SKILL.md"
] | sort')"
[ "$got" = "$want" ] || { echo "FAIL: pi context precedence is wrong: $got"; FAIL=1; }
while IFS= read -r -d '' context_path; do
  adapter_is_policy_path "$context_path" || { echo "FAIL: pi context is not restored policy: $context_path"; FAIL=1; }
done < <(context_paths_json "$R" "$sha" | jq -j '.[] + "\u0000"')

EMPTY="$S/empty-repo"
git -C "$S" init -q empty-repo
git -C "$EMPTY" config user.email t@example.com
git -C "$EMPTY" config user.name t
echo content > "$EMPTY/file.txt"
git -C "$EMPTY" add file.txt
git -C "$EMPTY" commit -qm base
empty_sha="$(git -C "$EMPTY" rev-parse HEAD)"
[ "$(context_paths_json "$EMPTY" "$empty_sha")" = '[]' ] \
  || { echo "FAIL: empty pi policy set does not produce an empty manifest"; FAIL=1; }

# Normalization. Each fixture is pi JSON-mode output reduced to the fields the adapter reads.
assistant() { # assistant STOP TEXT COST [THINKING] [ERROR]
  jq -nc --arg stop "$1" --arg text "$2" --argjson cost "$3" --arg thinking "${4:-high}" --arg error "${5:-}" '
    {type:"message_end", message:({role:"assistant", stopReason:$stop, thinkingLevel:$thinking,
      content:([{type:"thinking", thinking:"private"}] + (if $text == "" then [] else [{type:"text", text:$text}] end)),
      usage:{cost:{total:$cost}}} + (if $error == "" then {} else {errorMessage:$error} end))}'
}
normalize() { # normalize NAME EXIT LEVEL -> normalized file path
  ADAPTER_PI_LEVEL="$3" adapter_normalize "$S/$1.jsonl" "$2" "$S/$1.json"
  validate_normalized_result "$S/$1.json" || { echo "FAIL: $1 normalization is not a valid envelope: $(cat "$S/$1.json")"; FAIL=1; }
}

{
  echo '{"type":"session","version":3,"id":"s","cwd":"/x"}'
  echo '{"type":"message_end","message":{"role":"user","content":"prompt"}}'
  assistant toolUse '' 0.25
  echo '{"type":"message_end","message":{"role":"toolResult","content":[{"type":"text","text":"tool output"}]}}'
  assistant stop 'final review' 0.5
  echo '{"type":"agent_settled","aborted":false}'
} > "$S/success.jsonl"
normalize success 0 high
jq -e '.engine == "pi" and .engine_version == "1.2.0" and .status == "completed" and .result == "final review"
  and .cost_usd == 0.75 and .subtype == null and .errors == [] and .denials == []' "$S/success.json" >/dev/null \
  || { echo "FAIL: successful pi normalization failed: $(cat "$S/success.json")"; FAIL=1; }

{ assistant stop 'final review' 0 off; } > "$S/clamped.jsonl"
normalize clamped 0 high
jq -e '.status == "error" and (.errors | any(test("thinking level off, not the requested high")))' "$S/clamped.json" >/dev/null \
  || { echo "FAIL: a silently clamped thinking level was not an error: $(cat "$S/clamped.json")"; FAIL=1; }
normalize clamped 0 ''
jq -e '.status == "completed"' "$S/clamped.json" >/dev/null \
  || { echo "FAIL: no requested level must accept pi's default thinking level"; FAIL=1; }

{ assistant error 'partial' 0.1 high 'provider exploded'; } > "$S/error.jsonl"
normalize error 0 high
jq -e '.status == "error" and .result == "partial" and .subtype == "error" and .errors == ["provider exploded"]' "$S/error.json" >/dev/null \
  || { echo "FAIL: errored turn normalization failed: $(cat "$S/error.json")"; FAIL=1; }

{ assistant length 'truncated' 0.1; } > "$S/length.jsonl"
normalize length 0 high
jq -e '.status == "error" and .subtype == "length" and .errors == ["pi assistant turn ended with length"]' "$S/length.json" >/dev/null \
  || { echo "FAIL: truncated turn was not an error: $(cat "$S/length.json")"; FAIL=1; }

{
  assistant stop 'review' 0.1
  echo '{"type":"auto_retry_end","success":false,"attempt":3,"finalError":"529 overloaded"}'
  echo '{"type":"compaction_end","reason":"overflow","aborted":false,"willRetry":false,"errorMessage":"compaction failed"}'
  echo '{"type":"agent_settled","aborted":true}'
} > "$S/lifecycle.jsonl"
normalize lifecycle 0 high
jq -e '.status == "error" and .errors == ["529 overloaded","compaction failed","pi run was aborted"]' "$S/lifecycle.json" >/dev/null \
  || { echo "FAIL: lifecycle errors were not normalized: $(cat "$S/lifecycle.json")"; FAIL=1; }

{ assistant stop 'review' 0.1; printf '%s' '{"type":"message_upd'; } > "$S/truncated.jsonl"
normalize truncated 0 high
jq -e '.status == "completed" and .result == "review"' "$S/truncated.json" >/dev/null \
  || { echo "FAIL: a partial last record discarded the earlier stream: $(cat "$S/truncated.json")"; FAIL=1; }

{ assistant stop 'review' 0.1; } > "$S/killed.jsonl"
normalize killed 143 high
jq -e '.status == "error"' "$S/killed.json" >/dev/null || { echo "FAIL: nonzero child exit was not an error"; FAIL=1; }

{ echo '{"type":"session","version":3}'; echo '{"type":"agent_settled","aborted":false}'; } > "$S/empty.jsonl"
normalize empty 0 high
jq -e '.status == "error" and .result == "" and .cost_usd == null and .errors == ["pi produced no assistant message"]' "$S/empty.json" >/dev/null \
  || { echo "FAIL: missing assistant message did not become an error: $(cat "$S/empty.json")"; FAIL=1; }

{ assistant stop '' 0.1; } > "$S/no-text.jsonl"
normalize no-text 0 high
jq -e '.status == "error"' "$S/no-text.json" >/dev/null || { echo "FAIL: a final turn without text was not an error"; FAIL=1; }

printf '#!/usr/bin/env bash\nexit 1\n' > "$FAKEBIN/pi"
rc=0
skip="$(bash "$ROOT/tests/lens-fixture-test.sh" --runner pi --case legacy --snapshot baseline --runs 1)" || rc=$?
[ "$rc" = 77 ] || { echo "FAIL: unavailable pi lens gate exited $rc, want 77 (skipped, not passed)"; FAIL=1; }
grep -qF 'SKIP (pi not runnable)' <<<"$skip" || { echo "FAIL: unavailable pi lens gate lacks a skip message"; FAIL=1; }
rc=0
skip="$(bash "$ROOT/tests/pi-hostile-fixture-test.sh")" || rc=$?
[ "$rc" = 77 ] || { echo "FAIL: unavailable pi hostile gate exited $rc, want 77 (skipped, not passed)"; FAIL=1; }
grep -qF 'SKIP (pi not runnable)' <<<"$skip" || { echo "FAIL: unavailable pi hostile gate lacks a skip message"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "pi-adapter-test: OK"
exit "$FAIL"
