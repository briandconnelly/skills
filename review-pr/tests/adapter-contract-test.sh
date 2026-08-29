#!/usr/bin/env bash
# Offline: adapter inventory, interface, rule references, and generic-core boundaries.
set -euo pipefail
FAIL=0
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SRC="$ROOT/scripts"
# shellcheck disable=SC1091
. "$SRC/lib.sh"

runners=()
while IFS= read -r runner; do [ -z "$runner" ] || runners+=("$runner"); done < "$SRC/adapters/supported"
[ "${#runners[@]}" -gt 0 ] || { echo "FAIL: no supported adapters"; FAIL=1; }
[ "$(printf '%s\n' "${runners[@]}" | sort | uniq -d | wc -l | tr -d ' ')" = 0 ] || { echo "FAIL: duplicate supported adapter"; FAIL=1; }

for runner in "${runners[@]}"; do
  [ -x "$SRC/adapters/$runner.sh" ] || { echo "FAIL: adapter is missing or not executable: $runner"; FAIL=1; continue; }
  [ -r "$ROOT/references/runners/$runner.md" ] || { echo "FAIL: adapter reference missing: $runner"; FAIL=1; }
  load_adapter "$runner"
done

load_adapter claude
accepted=(CLAUDE.md nested/CLAUDE.local.md docs/AGENTS.md .claude/skills/a/SKILL.md .claude/agents/reviewer.md $'odd\nname/CLAUDE.md')
rejected=(README.md .claude/settings.json .claude/skills/a/reference.md .mcp.json nested/.claude/agents/reviewer.md)
for path in "${accepted[@]}"; do
  adapter_is_context_path "$path" || { echo "FAIL: Claude context selector rejected: $path"; FAIL=1; }
done
for path in "${rejected[@]}"; do
  adapter_is_context_path "$path" && { echo "FAIL: Claude context selector accepted: $path"; FAIL=1; }
done

# Loading an incomplete adapter cannot inherit functions from the previous adapter.
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT
cp -R "$SRC" "$fixture/scripts"
fake_runner=contract-incomplete
fake_adapter="$fixture/scripts/adapters/$fake_runner.sh"
printf '%s\n' "$fake_runner" >> "$fixture/scripts/adapters/supported"
printf '%s\n' 'ADAPTER_POLICY_ROOTS=()' 'ADAPTER_ALWAYS_REMOVE=()' 'adapter_check() { :; }' > "$fake_adapter"
# shellcheck disable=SC1091
. "$fixture/scripts/lib.sh"
rc=0
err="$(load_adapter "$fake_runner" 2>&1)" || rc=$?
[ "$rc" = 3 ] || { echo "FAIL: incomplete adapter inherited a stale interface"; FAIL=1; }
grep -qF 'does not implement the required interface' <<<"$err" \
  || { echo "FAIL: incomplete adapter error is not actionable: $err"; FAIL=1; }

# Empty policy arrays are valid on the macOS system Bash used by the skill.
printf '%s\n' \
  'ADAPTER_POLICY_ROOTS=()' \
  'ADAPTER_ALWAYS_REMOVE=()' \
  'adapter_check() { :; }' \
  'adapter_is_policy_path() { return 1; }' \
  'adapter_is_context_path() { return 1; }' \
  'adapter_build_command() { ADAPTER_COMMAND=(true); }' \
  'adapter_normalize() { :; }' > "$fake_adapter"
repo="$fixture/repo"
git -C "$fixture" init -q repo
git -C "$repo" config user.email t@example.com
git -C "$repo" config user.name t
printf '%s\n' content > "$repo/file.txt"
git -C "$repo" add file.txt
git -C "$repo" commit -qm base
sha="$(git -C "$repo" rev-parse HEAD)"
"$fixture/scripts/isolate-policy.sh" "$fake_runner" "$repo" "$sha" "$sha" >/dev/null \
  || { echo "FAIL: empty adapter arrays fail policy isolation"; FAIL=1; }
# Restore the production helper definitions for the remaining assertions.
# shellcheck disable=SC1091
. "$SRC/lib.sh"

generic_files=(
  "$ROOT/SKILL.md"
  "$ROOT/references/review-lens.md"
  "$ROOT/references/runner-contract.md"
  "$SRC/checkout-pr.sh"
  "$SRC/isolate-policy.sh"
  "$SRC/lib.sh"
  "$SRC/run-child.sh"
  "$SRC/review-pr.sh"
)
if grep -nE 'Claude Code|CLAUDE\.md|CLAUDE\.local\.md|--allowedTools|--disallowedTools|permission_denials|total_cost_usd' "${generic_files[@]}"; then
  echo "FAIL: runner-specific behavior leaked into the generic core"
  FAIL=1
fi

if grep -nE 'low.*,.*medium.*,.*high.*,.*xhigh.*,.*max' "$ROOT/SKILL.md"; then
  echo "FAIL: runner-specific level vocabulary leaked into SKILL.md"
  FAIL=1
fi

[ "$(grep -Fh 'Lenses checked: correctness, silent-failure, tests, comments.' "$ROOT/references/review-lens.md" "$ROOT/scripts/validate-result.sh" | awk 'END {print NR}')" = 1 ] \
  || { echo "FAIL: lenses-checked line must have exactly one home"; FAIL=1; }

definitions="$(grep -RhoE '^- (RC|CA)[0-9]+:' "$ROOT/references" | sed -E 's/^- ([A-Z]+[0-9]+):$/\1/' | sort)"
duplicates="$(uniq -d <<<"$definitions")"
[ -z "$duplicates" ] || { echo "FAIL: rule ids have multiple homes: $duplicates"; FAIL=1; }

citations="$(grep -RhoE '(RC|CA)[0-9]+' "$ROOT" | sort -u)"
while IFS= read -r id; do
  [ -z "$id" ] || grep -qx "$id" <<<"$definitions" || { echo "FAIL: unresolved rule id: $id"; FAIL=1; }
done <<<"$citations"

[ ! -e "$SRC/child-flags.sh" ] || { echo "FAIL: legacy Claude flag file remains outside the adapter"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "adapter-contract-test: OK"
exit "$FAIL"
