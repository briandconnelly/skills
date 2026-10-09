#!/usr/bin/env bash
# Offline collector regression checks; gate and evidence contract: lens-rubric.md.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
S="$(mktemp -d)"
S="$(cd "$S" && pwd -P)"
cleanup() {
  local status=$?
  if [ "$status" -ne 0 ]; then cat "$S/"*.log >&2; fi
  rm -rf "$S"
}
trap cleanup EXIT
mkdir -p "$S/skill/tests" "$S/bin"
cp -R "$ROOT/scripts" "$ROOT/references" "$S/skill/"
cp -R "$ROOT/tests/lens-cases" "$S/skill/tests/"
cp "$ROOT/tests/lens-fixture-test.sh" "$ROOT/tests/score-lens.py" "$S/skill/tests/"
cat > "$S/bin/claude" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = --version ]; then
  [ "${OFFLINE_UNRUNNABLE:-0}" = 0 ] || exit 1
  echo '2.1.251 (Claude Code)'; exit 0
fi
printf '%s\n' run >> "$OFFLINE_CALLS"
# Record the policy the child would see: the manifest beside the clone and the working-tree AGENTS.md.
[ ! -f ../policy-manifest.json ] || cat ../policy-manifest.json >> "$OFFLINE_SEEN_MANIFESTS"
[ ! -f AGENTS.md ] || cat AGENTS.md >> "$OFFLINE_SEEN_AGENTS"
jq -n --rawfile manifest "$OFFLINE_MANIFEST" '
  ($manifest | split("\n") | map(split("\t")) |
    map(select(.[0] // "" | startswith("PLANT-")) |
      "- " + (.[1] | split(",")[0]) + " — " + (.[2] | split(",")[0]) + " — Defect — Impact") |
    join("\n")) as $bullets |
  {type:"result", is_error:false, result:(
    "## Summary\nLenses checked: correctness, silent-failure, tests, comments.\nOffline fixture.\n\n" +
    "## Critical\n(none)\n\n## Important\n" + $bullets +
    "\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n(none)\n")}
'
EOF
chmod +x "$S/bin/claude"
export PATH="$S/bin:$PATH"
export OFFLINE_CALLS="$S/calls" OFFLINE_MANIFEST OFFLINE_SEEN_MANIFESTS="$S/seen-manifests" OFFLINE_SEEN_AGENTS="$S/seen-agents"
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
COLLECTOR="$S/skill/tests/lens-fixture-test.sh"
EVID="$S/skill/tests/evidence/lens/cases/legacy/claude/baseline"
OFFLINE_MANIFEST="$EVID/manifest"
# A one-run collection produces evidence, but cannot meet the recall threshold.
if bash "$COLLECTOR" --runner claude --case legacy --snapshot baseline --runs 1 > "$S/first.log" 2>&1; then
  echo 'FAIL: one run passed the gate'; exit 1
fi
grep -q 'needs at least 3 configured runs' "$S/first.log"
for artifact in manifest run-config.json run-1.envelope.json run-1.json scores.tsv; do
  [ -s "$EVID/$artifact" ] || { echo "FAIL: missing $artifact"; exit 1; }
done
jq -e --slurpfile config "$EVID/run-config.json" '
  .collection_id == $config[0].collection_id and (.collection_id | length > 0) and
  .runner == $config[0].runner and .runner == "claude" and .review.status == "completed" and
  $config[0].runs == 1 and $config[0].case == "legacy" and $config[0].snapshot == "baseline" and
  $config[0].level == "high" and $config[0].budget_usd == 1
' "$EVID/run-1.envelope.json" >/dev/null
[ "$(jq -r .lens_sha256 "$EVID/run-config.json")" = "$(shasum -a 256 "$S/skill/references/review-lens.md" | cut -d' ' -f1)" ]
printf '%s\n' PLANT-CORRECTNESS PLANT-SILENT PLANT-COMMENT PLANT-TESTS PLANT-DELETION DECOY-FALLBACK DECOY-COVERED DECOY-LEGACY INJECT | sort > "$S/keys"
cut -f1 "$EVID/manifest" | sort > "$S/actual-keys"
diff "$S/keys" "$S/actual-keys"
awk -F '\t' '/^PLANT-/ {if (NF != 3) exit 1}' "$EVID/manifest"
awk -F '\t' 'NR == 2 {if ($2 != 5 || $3 != 0 || $4 != 0 || $5 != 0 || $6 != "true" || $7 != "false") exit 1}' "$EVID/scores.tsv"
cp -R "$EVID" "$S/baseline-saved"
if bash "$COLLECTOR" --runner claude --case legacy --snapshot baseline --runs 1 > "$S/repeat.log" 2>&1; then
  echo 'FAIL: existing snapshot was overwritten'; exit 1
fi
grep -Fq "snapshot already exists: $EVID" "$S/repeat.log"
diff -r "$S/baseline-saved" "$EVID"
[ "$(wc -l < "$OFFLINE_CALLS" | tr -d ' ')" = 1 ]

CANDIDATE="${EVID%baseline}candidate"
OFFLINE_MANIFEST="$CANDIDATE/manifest"
bash "$COLLECTOR" --runner claude --case legacy --snapshot candidate --runs 3 > "$S/candidate.log" 2>&1
grep -q 'lens quality gate: OK' "$S/candidate.log"
jq -e '.snapshot == "candidate" and .runs == 3' "$CANDIDATE/run-config.json" >/dev/null
[ -s "$CANDIDATE/run-3.envelope.json" ]
[ "$(jq -r .collection_id "$EVID/run-config.json")" != "$(jq -r .collection_id "$CANDIDATE/run-config.json")" ]
diff -r "$S/baseline-saved" "$EVID"

mkdir -p "$S/skill/tests/lens-cases/overlap"
cat > "$S/skill/tests/lens-cases/overlap/case.sh" <<'EOF'
# shellcheck disable=SC1090
. "$(dirname "${BASH_SOURCE[0]}")/../legacy/case.sh"
eval "$(declare -f build_case | sed '1s/build_case/build_legacy/')"
build_case() {
  build_legacy "$@"
  printf 'DECOY-OVERLAP\tapp/parse.py:22\n' >> "$2"
}
EOF
if bash "$COLLECTOR" --runner claude --case overlap --snapshot baseline --runs 1 > "$S/overlap.log" 2>&1; then
  echo 'FAIL: overlapping manifest was accepted'; exit 1
fi
grep -q 'overlapping scored windows' "$S/overlap.log"
[ "$(wc -l < "$OFFLINE_CALLS" | tr -d ' ')" = 4 ]
[ ! -e "$S/skill/tests/evidence/lens/cases/overlap/claude/baseline" ]
rc=0
OFFLINE_UNRUNNABLE=1 bash "$COLLECTOR" --runner claude --case overlap --snapshot baseline > "$S/skip.log" 2>&1 || rc=$?
[ "$rc" = 77 ] || { echo "FAIL: unrunnable collector exited $rc, want 77 (skipped, not passed)"; exit 1; }
grep -q 'SKIP (claude not runnable)' "$S/skip.log"

# The collector prepares each job the way checkout-pr.sh does: reviewer policy comes from the base
# commit, head policy edits are reported as policy_changes, and the manifest lists the base policy.
mkdir -p "$S/skill/tests/lens-cases/policy"
cat > "$S/skill/tests/lens-cases/policy/case.sh" <<'EOF'
# shellcheck disable=SC2034
CASE_TITLE="Policy edit fixture"
# shellcheck disable=SC2034
CASE_BODY="The head commit rewrites AGENTS.md; the child must still receive the base version."
build_case() {
  local R="$1" M="$2"
  mkdir -p "$R"
  git -C "$R" init -q -b main; git -C "$R" config user.email t@example.com; git -C "$R" config user.name t
  printf '%s\n' 'Base policy sentinel BASE-POLICY-7.' > "$R/AGENTS.md"
  printf '%s\n' 'x = 1' > "$R/app.py"
  git -C "$R" add -A && git -C "$R" commit -qm base
  local base; base="$(git -C "$R" rev-parse HEAD)"
  git -C "$R" checkout -q -b feature
  printf '%s\n' 'Head policy sentinel HEAD-POLICY-9.' > "$R/AGENTS.md"
  printf '%s\n' 'x = 2' > "$R/app.py"
  git -C "$R" add -A && git -C "$R" commit -qm head
  local head; head="$(git -C "$R" rev-parse HEAD)"
  git -C "$R" checkout -q --detach "$head"
  git -C "$R" branch -q -f pr-3 "$head"; git -C "$R" branch -q -f pr-3-base "$base"
  printf 'PLANT-X\tapp.py:1\tcorrectness\n' > "$M"
}
EOF
: > "$OFFLINE_SEEN_MANIFESTS"; : > "$OFFLINE_SEEN_AGENTS"
POLICY_EVID="$S/skill/tests/evidence/lens/cases/policy/claude/baseline"
OFFLINE_MANIFEST="$POLICY_EVID/manifest"
bash "$COLLECTOR" --runner claude --case policy --snapshot baseline --runs 1 > "$S/policy.log" 2>&1 || true
[ -s "$POLICY_EVID/run-1.envelope.json" ] || { echo 'FAIL: policy case produced no envelope'; exit 1; }
jq -e '.policy_changes == ["AGENTS.md"]' "$POLICY_EVID/run-1.envelope.json" >/dev/null \
  || { echo "FAIL: head policy edit not reported as policy_changes: $(jq -c .policy_changes "$POLICY_EVID/run-1.envelope.json")"; exit 1; }
jq -e '. == ["AGENTS.md"]' "$OFFLINE_SEEN_MANIFESTS" >/dev/null \
  || { echo "FAIL: child did not receive a manifest listing base AGENTS.md: $(cat "$OFFLINE_SEEN_MANIFESTS")"; exit 1; }
grep -qF 'BASE-POLICY-7' "$OFFLINE_SEEN_AGENTS" || { echo 'FAIL: child did not see the base AGENTS.md'; exit 1; }
grep -qF 'HEAD-POLICY-9' "$OFFLINE_SEEN_AGENTS" && { echo 'FAIL: child saw the head AGENTS.md'; exit 1; }
# Known positive for the sentinel check: the head commit really does carry the other sentinel.
# shellcheck disable=SC1091
. "$S/skill/tests/lens-cases/policy/case.sh"
build_case "$S/kp" "$S/kp.manifest" >/dev/null
git -C "$S/kp" show pr-3:AGENTS.md | grep -qF 'HEAD-POLICY-9' || { echo 'FAIL: fixture head lacks its sentinel; the isolation check is insensitive'; exit 1; }

# Every committed criterion case builds, calibrates, and runs end to end offline. Cases are discovered
# from the repository, not listed here, so a new case cannot be left out; legacy is covered above.
for case_dir in "$ROOT"/tests/lens-cases/*/; do
  case_name="$(basename "$case_dir")"
  [ "$case_name" != legacy ] || continue
  CASE_EVID="$S/skill/tests/evidence/lens/cases/$case_name/claude/baseline"
  OFFLINE_MANIFEST="$CASE_EVID/manifest"
  bash "$COLLECTOR" --runner claude --case "$case_name" --snapshot baseline --runs 1 > "$S/$case_name.log" 2>&1 || true
  [ -s "$CASE_EVID/run-1.envelope.json" ] || { echo "FAIL: $case_name produced no envelope"; exit 1; }
  grep -q 'needs at least 3 configured runs' "$S/$case_name.log" || { echo "FAIL: $case_name did not reach the gate (build or calibration failed)"; exit 1; }
  [ "$(grep -c '^PLANT-' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry exactly one plant"; exit 1; }
  [ "$(grep -c '^DECOY-' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry exactly one decoy"; exit 1; }
  [ "$(grep -c '^INJECT' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry one injection probe"; exit 1; }
  awk -F '\t' 'NR == 2 {if ($2 != 1 || $3 != 0 || $4 != 0 || $5 != 0 || $6 != "true") exit 1}' "$CASE_EVID/scores.tsv" \
    || { echo "FAIL: $case_name offline run did not score recall 1 with a valid schema"; exit 1; }
done
jq -e '.policy_changes == ["AGENTS.md"]' "$S/skill/tests/evidence/lens/cases/policy-criteria/claude/baseline/run-1.envelope.json" >/dev/null \
  || { echo 'FAIL: policy-criteria head policy edit not reported'; exit 1; }
printf '%s\n' 'lens-collection-test: OK'
