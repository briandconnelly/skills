#!/usr/bin/env bash
# Offline: native-skill-discovery-probe.sh accepts only complete, tool-free runs whose control surfaces the nonce.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/bin"
# A fake codex whose behaviour FAKE_MODE selects. It reads the probe skill's description from the working tree
# itself, which is how it can answer with the nonce without emitting a tool event.
cat > "$S/bin/codex" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then echo "codex-cli 0.166.0"; exit 0; fi
desc="$(sed -n 's/^description: //p' .agents/skills/release-probe/SKILL.md)"
msg() { jq -nc --arg t "release-probe: $desc" '{type:"item.completed", item:{type:"agent_message", text:$t}}'; }
done_turn() { echo '{"type":"turn.completed","usage":{"input_tokens":1,"cached_input_tokens":0,"output_tokens":1}}'; }
case "$FAKE_MODE" in
  clean) msg; done_turn;;
  exit1) msg; done_turn; exit 1;;
  no-turn) msg;;
  tool) echo '{"type":"item.completed","item":{"type":"command_execution","command":"cat SKILL.md"}}'; msg; done_turn;;
esac
EOF
chmod +x "$S/bin/codex"
FAIL=0
probe() { # probe MODE -> exit status, output in $S/MODE.out
  local rc=0
  PATH="$S/bin:$PATH" FAKE_MODE="$1" bash "$ROOT/tests/native-skill-discovery-probe.sh" codex > "$S/$1.out" 2>&1 || rc=$?
  echo "$rc"
}
[ "$(probe clean)" = 0 ] || { echo "FAIL: a clean run was not accepted: $(cat "$S/clean.out")"; FAIL=1; }
grep -q 'adapter: description=seen' "$S/clean.out" || { echo "FAIL: clean run did not report the nonce: $(cat "$S/clean.out")"; FAIL=1; }
for mode in exit1 no-turn tool; do
  rc="$(probe "$mode")"
  if [ "$rc" != 1 ] || ! grep -q INCONCLUSIVE "$S/$mode.out"; then
    echo "FAIL: $mode run was accepted (exit $rc): $(cat "$S/$mode.out")"; FAIL=1
  fi
done
[ "$FAIL" = 0 ] && echo "native-skill-discovery-probe-test: OK"
exit "$FAIL"
