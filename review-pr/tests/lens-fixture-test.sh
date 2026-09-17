#!/usr/bin/env bash
# Collect and score a case snapshot; see lens-rubric.md.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
RUNNER=""; CASE=""; SNAPSHOT=""; RUNS=3; BUDGET=1; LEVEL=high
usage() {
  echo "usage: $0 --runner NAME --case CASE --snapshot baseline|candidate [--runs N] [--budget USD] [--level LEVEL]" >&2
  exit 2
}
while [ $# -gt 0 ]; do
  [ $# -ge 2 ] || usage
  case "$1" in
    --runner) RUNNER="$2";; --case) CASE="$2";; --snapshot) SNAPSHOT="$2";;
    --runs) RUNS="$2";; --budget) BUDGET="$2";; --level) LEVEL="$2";;
    *) usage;;
  esac
  shift 2
done
[ -n "$RUNNER" ] || usage
[[ "$CASE" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || usage
[[ "$RUNS" =~ ^[1-9][0-9]*$ ]] || usage
[[ "$BUDGET" =~ ^[0-9]+([.][0-9]+)?$ ]] || usage
case "$SNAPSHOT" in baseline|candidate) ;; *) usage;; esac
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SRC="$ROOT/scripts"
SCORER="$ROOT/tests/score-lens.py"
# shellcheck disable=SC1091
. "$SRC/lib.sh"
load_adapter "$RUNNER"
[ -f "$ROOT/tests/lens-cases/$CASE/case.sh" ] || die 2 "unknown lens case: $CASE"
# shellcheck disable=SC1090
. "$ROOT/tests/lens-cases/$CASE/case.sh"
if ! (adapter_check) >/dev/null 2>&1; then echo "lens-fixture-test: SKIP ($RUNNER not runnable)"; exit 0; fi
EVID="$ROOT/tests/evidence/lens/cases/$CASE/$RUNNER/$SNAPSHOT"
[ ! -e "$EVID" ] || die 1 "snapshot already exists: $EVID"
export REVIEW_PR_SCRATCH; REVIEW_PR_SCRATCH="$(mktemp -d)"; trap 'rm -rf "$REVIEW_PR_SCRATCH"' EXIT
COLLECTION_ID="$(printf '%s' "$REVIEW_PR_SCRATCH" | git hash-object --stdin)"
# Build once so every run uses the same calibrated fixture.
build_case "$REVIEW_PR_SCRATCH/fixture" "$REVIEW_PR_SCRATCH/manifest" >/dev/null
python3 "$SCORER" --check-manifest "$REVIEW_PR_SCRATCH/manifest"
mkdir -p "$(dirname "$EVID")"
mkdir "$EVID" || die 1 "snapshot already exists: $EVID"
cp "$REVIEW_PR_SCRATCH/manifest" "$EVID/manifest"
# Hash the lens the runner will use; run-child.sh and validate-result.sh honor the same override.
export REVIEW_PR_LENS="${REVIEW_PR_LENS:-$ROOT/references/review-lens.md}"
LENS_SHA256="$(shasum -a 256 "$REVIEW_PR_LENS" | cut -d' ' -f1)"
jq -n --arg collection "$COLLECTION_ID" --arg runner "$RUNNER" --arg case "$CASE" \
  --arg snapshot "$SNAPSHOT" --arg level "$LEVEL" --argjson runs "$RUNS" --argjson budget "$BUDGET" \
  --arg lens_sha256 "$LENS_SHA256" \
  '{collection_id:$collection, runner:$runner, case:$case, snapshot:$snapshot, level:$level,
    runs:$runs, budget_usd:$budget, lens_sha256:$lens_sha256}' > "$EVID/run-config.json"

mkjob() {
  local job n base head
  job="$(mktemp -d "$REVIEW_PR_SCRATCH/review-pr.XXXXXX")"
  : > "$job/.review-pr"
  cp -R "$REVIEW_PR_SCRATCH/fixture" "$job/repo"
  n="$(git -C "$job/repo" for-each-ref --format='%(refname:short)' 'refs/heads/pr-*-base')"
  n="${n#pr-}"; n="${n%-base}"
  [[ "$n" =~ ^[1-9][0-9]*$ ]] || die 1 "case must define one pr-N / pr-N-base branch pair"
  base="$(git -C "$job/repo" rev-parse "pr-$n-base")"
  head="$(git -C "$job/repo" rev-parse "pr-$n")"
  git -C "$job/repo" checkout -q --detach "$head"
  jq -n --argjson n "$n" --arg title "$CASE_TITLE" --arg body "$CASE_BODY" \
    '{number:$n, title:$title, body:$body}' > "$job/pr.json"
  echo '[]' > "$job/policy-manifest.json"
  git -C "$job/repo" diff --no-ext-diff --no-textconv --binary "pr-$n-base...pr-$n" > "$job/pr.diff"
  jq -n --arg d "$job" --arg b "$base" --arg h "$head" --arg runner "$RUNNER" \
    '{dir:$d, runner:$runner, base_sha:$b, head_sha:$h, head_repo:"fixture/fixture", policy_changes:[], diff_path:($d+"/pr.diff"), meta_path:($d+"/pr.json"), policy_manifest_path:($d+"/policy-manifest.json")}'
}

for k in $(seq 1 "$RUNS"); do
  J="$(mkjob)"; dir="$(jq -r .dir <<<"$J")"
  # Preserve failed runs too; the final gate reports lifecycle and scoring failures.
  printf '%s' "$J" | REVIEW_PR_BUDGET="$BUDGET" REVIEW_PR_KEEP=1 "$SRC/run-child.sh" "$LEVEL" > "$EVID/run-$k.envelope.tmp" || true
  jq --arg collection "$COLLECTION_ID" '. + {collection_id:$collection}' "$EVID/run-$k.envelope.tmp" > "$EVID/run-$k.envelope.json"
  rm -f "$EVID/run-$k.envelope.tmp"
  if [ -f "$dir/runner-output" ]; then cp "$dir/runner-output" "$EVID/run-$k.json"; else echo '{}' > "$EVID/run-$k.json"; fi
  rm -rf "$dir"
done
python3 "$SCORER" "$EVID" --gate --tsv "$EVID/scores.tsv"
