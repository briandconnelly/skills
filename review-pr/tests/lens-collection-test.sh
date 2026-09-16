#!/usr/bin/env bash
# Offline: collecting a new run set removes stale reports and labels each result.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/skill/tests" "$S/bin"
cp -R "$ROOT/scripts" "$ROOT/references" "$S/skill/"
cp "$ROOT/tests/lens-fixture-test.sh" "$S/skill/tests/"
cat > "$S/bin/claude" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = --version ]; then echo '2.1.251 (Claude Code)'; exit 0; fi
printf '%s\n' '{"type":"result","is_error":false,"result":"offline collection fixture"}'
EOF
chmod +x "$S/bin/claude"
EVID="$S/skill/tests/evidence/lens/claude/semantic-v1"
mkdir -p "$EVID"
for artifact in run-4.json run-4.envelope.json run-4.assessment.json run-1.assessment.json; do
  printf '%s\n' stale > "$EVID/$artifact"
done
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
PATH="$S/bin:$PATH" bash "$S/skill/tests/lens-fixture-test.sh" --runner claude --arm lens --runs 1
for artifact in run-4.json run-4.envelope.json run-4.assessment.json run-1.assessment.json; do
  [ ! -e "$EVID/$artifact" ] || { echo "FAIL: stale collection artifact survived: $artifact"; exit 1; }
done
jq -e --slurpfile config "$EVID/run-config.json" '
  .collection_id == $config[0].collection_id and (.collection_id | length > 0) and
  .runner == $config[0].runner and $config[0].runs == 1 and .review.status == "completed"
' "$EVID/run-1.envelope.json" >/dev/null
printf '%s\n' 'lens-collection-test: OK'
