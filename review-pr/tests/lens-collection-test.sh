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
cp "$ROOT/tests/lens-fixture-test.sh" "$ROOT/tests/score-lens.py" "$ROOT/tests/lens-cost.py" "$S/skill/tests/"
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
if [ -f ../policy-changes.json ]; then cat ../policy-changes.json >> "$OFFLINE_SEEN_CHANGES"; else echo MISSING >> "$OFFLINE_SEEN_CHANGES"; fi
jq -n --rawfile manifest "$OFFLINE_MANIFEST" '
  ($manifest | split("\n") | map(split("\t")) |
    map(select(.[0] // "" | startswith("PLANT-")) |
      "- " + (.[1] | split(",")[0]) + " — " + (.[2] | split(",")[0]) + " — Title — Defect — Impact") |
    join("\n")) as $bullets |
  {type:"result", is_error:false, result:(
    "## Summary\nLenses checked: correctness, silent-failure, tests, comments.\nOffline fixture.\n\n" +
    "## Changes\nFixture change summary.\n\n## Critical\n(none)\n\n## Important\n" + $bullets +
    "\n\n## Suggestions\n(none)\n\n## Not reviewed\n(none)\n")}
'
EOF
chmod +x "$S/bin/claude"
export PATH="$S/bin:$PATH"
export OFFLINE_CALLS="$S/calls" OFFLINE_MANIFEST OFFLINE_SEEN_MANIFESTS="$S/seen-manifests" OFFLINE_SEEN_AGENTS="$S/seen-agents" OFFLINE_SEEN_CHANGES="$S/seen-changes"
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
: > "$OFFLINE_SEEN_MANIFESTS"; : > "$OFFLINE_SEEN_AGENTS"; : > "$OFFLINE_SEEN_CHANGES"
POLICY_EVID="$S/skill/tests/evidence/lens/cases/policy/claude/baseline"
OFFLINE_MANIFEST="$POLICY_EVID/manifest"
bash "$COLLECTOR" --runner claude --case policy --snapshot baseline --runs 1 > "$S/policy.log" 2>&1 || true
[ -s "$POLICY_EVID/run-1.envelope.json" ] || { echo 'FAIL: policy case produced no envelope'; exit 1; }
jq -e '.policy_changes == ["AGENTS.md"]' "$POLICY_EVID/run-1.envelope.json" >/dev/null \
  || { echo "FAIL: head policy edit not reported as policy_changes: $(jq -c .policy_changes "$POLICY_EVID/run-1.envelope.json")"; exit 1; }
jq -e '. == {version: 2, policy_files: ["AGENTS.md"], skills: []}' "$OFFLINE_SEEN_MANIFESTS" >/dev/null \
  || { echo "FAIL: child did not receive a manifest listing base AGENTS.md: $(cat "$OFFLINE_SEEN_MANIFESTS")"; exit 1; }
# The job beside the clone holds policy-changes.json, equal to the envelope's policy_changes (RC13).
jq -e --slurpfile env "$POLICY_EVID/run-1.envelope.json" '. == $env[0].policy_changes' "$OFFLINE_SEEN_CHANGES" >/dev/null \
  || { echo "FAIL: job policy-changes.json differs from the envelope's policy_changes: $(cat "$OFFLINE_SEEN_CHANGES")"; exit 1; }
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
  set --; tree=cases
  if grep -qx 'CASE_DIAGNOSTIC=1' "$case_dir/case.sh"; then set -- --diagnostic; tree=diagnostics; fi
  CASE_EVID="$S/skill/tests/evidence/lens/$tree/$case_name/claude/baseline"
  OFFLINE_MANIFEST="$CASE_EVID/manifest"
  bash "$COLLECTOR" --runner claude --case "$case_name" --snapshot baseline --runs 1 "$@" > "$S/$case_name.log" 2>&1 || true
  [ -s "$CASE_EVID/run-1.envelope.json" ] || { echo "FAIL: $case_name produced no envelope"; exit 1; }
  if [ "$tree" = cases ]; then
    grep -q 'needs at least 3 configured runs' "$S/$case_name.log" || { echo "FAIL: $case_name did not reach the gate (build or calibration failed)"; exit 1; }
  fi
  [ "$(grep -c '^PLANT-' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry exactly one plant"; exit 1; }
  [ "$(grep -c '^DECOY-' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry exactly one decoy"; exit 1; }
  [ "$(grep -c '^INJECT' "$CASE_EVID/manifest")" = 1 ] || { echo "FAIL: $case_name must carry one injection probe"; exit 1; }
  awk -F '\t' 'NR == 2 {if ($2 != 1 || $3 != 0 || $4 != 0 || $5 != 0 || $6 != "true") exit 1}' "$CASE_EVID/scores.tsv" \
    || { echo "FAIL: $case_name offline run did not score recall 1 with a valid schema"; exit 1; }
done
# Every snapshot records cost beside its scores.
[ -s "$S/skill/tests/evidence/lens/cases/policy-criteria/claude/baseline/cost.tsv" ] || { echo 'FAIL: collector wrote no cost.tsv'; exit 1; }
# A diagnostic snapshot lands outside the acceptance tree and is scored without the gate, so a one-run
# collection that would fail the gate still succeeds; the same collection without --diagnostic fails (above).
DIAG_EVID="$S/skill/tests/evidence/lens/diagnostics/skill-only-rule-vague/claude/baseline"
OFFLINE_MANIFEST="$DIAG_EVID/manifest"
# The case loop above collected it with --diagnostic; a one-run gated collection would have failed.
grep -q 'needs at least 3 configured runs' "$S/skill-only-rule-vague.log" && { echo 'FAIL: diagnostic collection was gated'; exit 1; }
# A diagnostic-only case is refused without --diagnostic, so it cannot land in the acceptance tree.
if bash "$COLLECTOR" --runner claude --case skill-only-rule-vague --snapshot candidate --runs 1 > "$S/diag-refused.log" 2>&1; then
  echo 'FAIL: diagnostic-only case collected into the acceptance tree'; exit 1
fi
grep -qF 'diagnostic-only' "$S/diag-refused.log" || { echo 'FAIL: diagnostic-only refusal diagnostic missing'; exit 1; }
for artifact in manifest run-config.json run-1.envelope.json run-1.json scores.tsv cost.tsv; do
  [ -s "$DIAG_EVID/$artifact" ] || { echo "FAIL: diagnostic snapshot missing $artifact"; exit 1; }
done
jq -e '.diagnostic == true' "$DIAG_EVID/run-config.json" >/dev/null || { echo 'FAIL: diagnostic snapshot not marked'; exit 1; }
[ ! -e "$S/skill/tests/evidence/lens/cases/skill-only-rule-vague" ] || { echo 'FAIL: diagnostic snapshot written into the acceptance tree'; exit 1; }
jq -e '.policy_changes == ["AGENTS.md"]' "$S/skill/tests/evidence/lens/cases/policy-criteria/claude/baseline/run-1.envelope.json" >/dev/null \
  || { echo 'FAIL: policy-criteria head policy edit not reported'; exit 1; }

# The evidence replay reports current-lens coverage on every run, and fails on it only when asked.
# Two cases on every supported runner, with one cell left without a snapshot.
REPLAY="$S/replay"
mkdir -p "$REPLAY/tests/lens-cases/alpha" "$REPLAY/tests/lens-cases/beta" "$REPLAY/tests/evidence/lens"
cp -R "$ROOT/scripts" "$ROOT/references" "$REPLAY/"
cp "$ROOT/tests/lens-evidence-test.sh" "$ROOT/tests/score-lens.py" "$REPLAY/tests/"
for arm in claude codex baseline; do cp -R "$ROOT/tests/evidence/lens/$arm" "$REPLAY/tests/evidence/lens/"; done
: > "$REPLAY/tests/lens-cases/alpha/case.sh"; : > "$REPLAY/tests/lens-cases/beta/case.sh"
cells=0; last_runner=""
while IFS= read -r runner; do
  [ -n "$runner" ] || continue
  for case_name in alpha beta; do
    cells=$((cells+1))
    mkdir -p "$REPLAY/tests/evidence/lens/cases/$case_name/$runner"
    cp -R "$CANDIDATE" "$REPLAY/tests/evidence/lens/cases/$case_name/$runner/candidate"
  done
  last_runner="$runner"
done < "$ROOT/scripts/adapters/supported"
rm -rf "$REPLAY/tests/evidence/lens/cases/beta/$last_runner"
rc=0; bash "$REPLAY/tests/lens-evidence-test.sh" > "$S/replay.log" 2>&1 || rc=$?
[ "$rc" = 0 ] || { echo "FAIL: evidence replay with a missing cell exited $rc without REVIEW_PR_LENS_MATRIX"; exit 1; }
grep -Fxq "lens-evidence-test: WARNING: 1 of $cells case-by-runner cells lack current-lens evidence" "$S/replay.log" \
  || { echo 'FAIL: evidence replay did not report the missing cell'; exit 1; }
rc=0; REVIEW_PR_LENS_MATRIX=1 bash "$REPLAY/tests/lens-evidence-test.sh" > "$S/replay-matrix.log" 2>&1 || rc=$?
[ "$rc" = 1 ] || { echo "FAIL: REVIEW_PR_LENS_MATRIX=1 replay with a missing cell exited $rc, want 1"; exit 1; }
grep -Fq "MISSING: beta/$last_runner" "$S/replay-matrix.log" || { echo 'FAIL: matrix replay did not name the missing cell'; exit 1; }
mkdir -p "$REPLAY/tests/evidence/lens/cases/beta/$last_runner"
cp -R "$CANDIDATE" "$REPLAY/tests/evidence/lens/cases/beta/$last_runner/candidate"
bash "$REPLAY/tests/lens-evidence-test.sh" > "$S/replay-full.log" 2>&1
grep -q 'WARNING: .* cells lack' "$S/replay-full.log" && { echo 'FAIL: full coverage still warned'; exit 1; }
printf '%s\n' 'lens-collection-test: OK'
