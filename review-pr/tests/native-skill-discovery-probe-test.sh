#!/usr/bin/env bash
# Offline: native-skill-discovery-probe.sh accepts only complete, tool-free runs whose control surfaces the nonce,
# for each runner, and fails closed when either arm alone is broken.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/bin"
# Fake runners. Each tells the adapter arm from the control by a flag only the adapter command passes, and behaves
# as FAKE_ADAPTER or FAKE_CONTROL selects: clean, exit1, broken (Codex: no turn.completed; Claude: is_error),
# tool (a tool event, or a second turn for Claude), or none (a complete, tool-free answer of NONE). It reads the
# probe skill's description from the working tree itself, so it can answer with the nonce without a tool event.
cat > "$S/bin/codex" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then echo "codex-cli 0.166.0"; exit 0; fi
mode="$FAKE_CONTROL"; case " $* " in *" --disable "*) mode="$FAKE_ADAPTER";; esac
desc="$(sed -n 's/^description: //p' .agents/skills/release-probe/SKILL.md)"
msg() { jq -nc --arg t "$1" '{type:"item.completed", item:{type:"agent_message", text:$t}}'; }
done_turn() { echo '{"type":"turn.completed","usage":{"input_tokens":1,"cached_input_tokens":0,"output_tokens":1}}'; }
case "$mode" in
  clean) msg "release-probe: $desc"; done_turn;;
  exit1) msg "release-probe: $desc"; done_turn; exit 1;;
  broken) msg "release-probe: $desc";;
  tool) echo '{"type":"item.completed","item":{"type":"command_execution","command":"cat SKILL.md"}}'; msg "release-probe: $desc"; done_turn;;
  none) msg NONE; done_turn;;
esac
EOF
cat > "$S/bin/claude" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then echo "2.1.317 (Claude Code)"; exit 0; fi
mode="$FAKE_CONTROL"; case " $* " in *" --restricted "*) mode="$FAKE_ADAPTER";; esac
desc="$(sed -n 's/^description: //p' .claude/skills/release-probe/SKILL.md)"
out() { jq -nc --arg r "$1" --argjson turns "$2" --argjson err "$3" '{type:"result", is_error:$err, result:$r, num_turns:$turns}'; }
case "$mode" in
  clean) out "release-probe: $desc" 1 false;;
  exit1) out "release-probe: $desc" 1 false; exit 1;;
  broken) out "release-probe: $desc" 1 true;;
  tool) out "release-probe: $desc" 2 false;;
  none) out NONE 1 false;;
esac
EOF
chmod +x "$S/bin/codex" "$S/bin/claude"
FAIL=0
probe() { # probe RUNNER ADAPTER CONTROL -> exit status; output in $S/RUNNER-ADAPTER-CONTROL.out
  local rc=0
  PATH="$S/bin:$PATH" FAKE_ADAPTER="$2" FAKE_CONTROL="$3" bash "$ROOT/tests/native-skill-discovery-probe.sh" "$1" \
    > "$S/$1-$2-$3.out" 2>&1 || rc=$?
  echo "$rc"
}
accepts() { # accepts RUNNER ADAPTER CONTROL EXPECTED_DESCRIPTION
  local out="$S/$1-$2-$3.out"
  [ "$(probe "$1" "$2" "$3")" = 0 ] || { echo "FAIL: $1 $2/$3 was not accepted: $(cat "$out")"; FAIL=1; return; }
  grep -q "^$1 adapter: description=$4 " "$out" || { echo "FAIL: $1 $2/$3 did not report description=$4: $(cat "$out")"; FAIL=1; }
}
rejects() { # rejects RUNNER ADAPTER CONTROL
  local rc out="$S/$1-$2-$3.out"
  rc="$(probe "$1" "$2" "$3")"
  if [ "$rc" != 1 ] || ! grep -q INCONCLUSIVE "$out"; then
    echo "FAIL: $1 $2/$3 was accepted (exit $rc): $(cat "$out")"; FAIL=1
  fi
}
for runner in codex claude; do
  # Both conclusive outcomes: the adapter arm sees the skill, or answers NONE while the control sees it.
  accepts "$runner" clean clean seen
  accepts "$runner" none clean absent
  # Either arm alone failing, broken or using a tool makes the probe inconclusive.
  for bad in exit1 broken tool; do
    rejects "$runner" "$bad" clean
    rejects "$runner" clean "$bad"
  done
  # A control that never surfaces the skill cannot back a negative adapter result.
  rejects "$runner" none none
done
[ "$FAIL" = 0 ] && echo "native-skill-discovery-probe-test: OK"
exit "$FAIL"
