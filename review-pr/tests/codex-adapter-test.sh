#!/usr/bin/env bash
# Offline: Codex adapter flags, policy selection, level mapping, and JSONL normalization.
set -euo pipefail
FAIL=0
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SRC="$ROOT/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"

S="$(mktemp -d)"
trap 'rm -rf "$S"' EXIT
FAKEBIN="$S/bin"
mkdir -p "$FAKEBIN"
cat > "$FAKEBIN/codex" <<'EOF'
#!/usr/bin/env bash
echo 'codex-cli 0.151.0'
EOF
chmod +x "$FAKEBIN/codex"
PATH="$FAKEBIN:$PATH"
export PATH

load_adapter codex
adapter_check

for case_data in '0.150.9|Codex CLI 0.151.0 or newer' '0.151.0-alpha|cannot parse Codex CLI version' 'unexpected|cannot parse Codex CLI version'; do
  fake_version="${case_data%%|*}"
  want_error="${case_data#*|}"
  printf '#!/usr/bin/env bash\necho %q\n' "codex-cli $fake_version" > "$FAKEBIN/codex"
  rc=0
  (adapter_check) >/dev/null 2>"$S/version.err" || rc=$?
  [ "$rc" = 3 ] || { echo "FAIL: Codex version $fake_version was accepted"; FAIL=1; }
  grep -qF "$want_error" "$S/version.err" || { echo "FAIL: Codex version $fake_version has the wrong error"; FAIL=1; }
done
cat > "$FAKEBIN/codex" <<'EOF'
#!/usr/bin/env bash
echo 'codex-cli 0.151.0'
EOF
[ "${ADAPTER_POLICY_ROOTS[*]}" = '.codex .agents' ] || { echo "FAIL: Codex policy roots changed"; FAIL=1; }
[ "${ADAPTER_ALWAYS_REMOVE[*]}" = '.codex' ] || { echo "FAIL: Codex executable configuration is not removed"; FAIL=1; }

adapter_build_command 'PROMPT-SENTINEL' high 9 17 "$S"
args="$(printf '<%s>\n' "${ADAPTER_COMMAND[@]}")"
for arg in \
  '<codex>' '<exec>' '<--json>' '<--ephemeral>' '<--ignore-user-config>' '<--ignore-rules>' \
  '<--sandbox>' '<read-only>' '<--strict-config>' '<approval_policy="never">' \
  '<project_doc_max_bytes=0>' '<model_reasoning_effort="high">' '<PROMPT-SENTINEL>';
do
  grep -qF "$arg" <<<"$args" || { echo "FAIL: Codex command lacks $arg"; FAIL=1; }
done
[ "${ADAPTER_COMMAND[${#ADAPTER_COMMAND[@]}-1]}" = 'PROMPT-SENTINEL' ] \
  || { echo "FAIL: prompt is not the final Codex argument"; FAIL=1; }
[ "$(grep -cF '<--disable>' <<<"$args")" = 10 ] || { echo "FAIL: Codex feature-disable set changed"; FAIL=1; }
grep -qF '<9>' <<<"$args" && { echo "FAIL: unsupported budget leaked into Codex command"; FAIL=1; }
grep -qF '<17>' <<<"$args" && { echo "FAIL: unsupported turn limit leaked into Codex command"; FAIL=1; }

rc=0
(adapter_build_command p max 1 1 "$S") >/dev/null 2>"$S/level.err" || rc=$?
[ "$rc" = 2 ] || { echo "FAIL: Codex accepted unsupported level max"; FAIL=1; }
grep -qF 'low|medium|high|xhigh' "$S/level.err" || { echo "FAIL: invalid-level error is not actionable"; FAIL=1; }

R="$S/repo"
git -C "$S" init -q repo
git -C "$R" config user.email t@example.com
git -C "$R" config user.name t
mkdir -p "$R/pkg" "$R/other" "$R/.agents/skills/reviewer" "$R/.agents/agents" \
  "$R/nested/.agents/skills/ignored" "$R/.codex"
echo root > "$R/AGENTS.md"
echo override > "$R/AGENTS.override.md"
echo pkg > "$R/pkg/AGENTS.md"
echo other > "$R/other/AGENTS.md"
echo other-override > "$R/other/AGENTS.override.md"
echo skill > "$R/.agents/skills/reviewer/SKILL.md"
echo reference > "$R/.agents/skills/reviewer/reference.md"
echo agent > "$R/.agents/agents/reviewer.md"
echo nested-skill > "$R/nested/.agents/skills/ignored/SKILL.md"
echo config > "$R/.codex/config.toml"
git -C "$R" add -A
git -C "$R" commit -qm base
sha="$(git -C "$R" rev-parse HEAD)"
got="$(context_paths_json "$R" "$sha" | jq -c sort)"
want="$(jq -nc '[".agents/skills/reviewer/SKILL.md","AGENTS.override.md","other/AGENTS.override.md","pkg/AGENTS.md"] | sort')"
[ "$got" = "$want" ] || { echo "FAIL: Codex context precedence is wrong: $got"; FAIL=1; }
adapter_is_policy_path nested/.agents/skills/ignored/SKILL.md \
  && { echo "FAIL: nested .agents skill was treated as Codex policy"; FAIL=1; }

EMPTY="$S/empty-repo"
git -C "$S" init -q empty-repo
git -C "$EMPTY" config user.email t@example.com
git -C "$EMPTY" config user.name t
echo content > "$EMPTY/file.txt"
git -C "$EMPTY" add file.txt
git -C "$EMPTY" commit -qm base
empty_sha="$(git -C "$EMPTY" rev-parse HEAD)"
[ "$(context_paths_json "$EMPTY" "$empty_sha")" = '[]' ] \
  || { echo "FAIL: empty Codex policy set does not produce an empty manifest"; FAIL=1; }

cat > "$S/success.jsonl" <<'EOF'
{"type":"thread.started","thread_id":"t"}
{"type":"item.completed","item":{"type":"agent_message","text":"draft"}}
{"type":"item.completed","item":{"type":"agent_message","text":"final review"}}
{"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":2}}
EOF
adapter_normalize "$S/success.jsonl" 0 "$S/success.json"
jq -e '.engine == "codex" and .engine_version == "0.151.0" and .status == "completed" and .result == "final review" and .errors == [] and .denials == []' "$S/success.json" >/dev/null \
  || { echo "FAIL: successful Codex JSONL normalization failed: $(cat "$S/success.json")"; FAIL=1; }

cat > "$S/error.jsonl" <<'EOF'
{"type":"item.completed","item":{"type":"agent_message","text":"partial"}}
{"type":"turn.failed","error":{"message":"model failed"}}
EOF
adapter_normalize "$S/error.jsonl" 0 "$S/error.json"
jq -e '.status == "error" and .result == "partial" and .errors == ["model failed"]' "$S/error.json" >/dev/null \
  || { echo "FAIL: failed-turn normalization failed: $(cat "$S/error.json")"; FAIL=1; }

printf '%s\n' '{"type":"turn.failed","error":"string failure"}' > "$S/string-error.jsonl"
adapter_normalize "$S/string-error.jsonl" 1 "$S/string-error.json"
jq -e '.status == "error" and .errors == ["string failure"]' "$S/string-error.json" >/dev/null \
  || { echo "FAIL: string error normalization failed: $(cat "$S/string-error.json")"; FAIL=1; }

printf '%s\n' '{"type":"error"}' > "$S/message-error.jsonl"
adapter_normalize "$S/message-error.jsonl" 1 "$S/message-error.json"
jq -e '.status == "error" and .errors == ["Codex error"]' "$S/message-error.json" >/dev/null \
  || { echo "FAIL: missing error message normalization failed: $(cat "$S/message-error.json")"; FAIL=1; }

printf '%s\n' '{"type":"turn.completed"}' > "$S/empty.jsonl"
adapter_normalize "$S/empty.jsonl" 0 "$S/empty.json"
jq -e '.status == "error" and .result == ""' "$S/empty.json" >/dev/null \
  || { echo "FAIL: missing final message did not become an error"; FAIL=1; }

cat > "$FAKEBIN/codex" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
skip="$(bash "$ROOT/tests/lens-fixture-test.sh" --runner codex --arm lens --runs 1)" || { echo "FAIL: unavailable Codex lens gate did not skip"; FAIL=1; skip=''; }
grep -qF 'SKIP (codex not runnable)' <<<"$skip" || { echo "FAIL: unavailable Codex lens gate lacks a skip message"; FAIL=1; }
skip="$(bash "$ROOT/tests/codex-hostile-fixture-test.sh")" || { echo "FAIL: unavailable Codex hostile gate did not skip"; FAIL=1; skip=''; }
grep -qF 'SKIP (codex not runnable)' <<<"$skip" || { echo "FAIL: unavailable Codex hostile gate lacks a skip message"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "codex-adapter-test: OK"
exit "$FAIL"
