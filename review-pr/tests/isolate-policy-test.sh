#!/usr/bin/env bash
# Offline: isolate-policy.sh restores policy from base and strips hooks/MCP (R3.1-R3.3).
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
FAIL=0
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"
R="$(mktemp -d)"; trap 'rm -rf "$R"' EXIT

git -C "$R" init -q -b main
git -C "$R" config user.email t@example.com; git -C "$R" config user.name t
mkdir -p "$R/.claude/skills/zebra-review"
echo '# base sentinel' > "$R/CLAUDE.md"
echo 'base agents' > "$R/AGENTS.md"
printf -- '---\nname: zebra-review\ndescription: base skill\n---\nbody\n' > "$R/.claude/skills/zebra-review/SKILL.md"
echo '{"permissions":{"allow":["Bash(rm:*)"]}}' > "$R/.claude/settings.json"
echo '{"mcpServers":{}}' > "$R/.mcp.json"
echo 'x' > "$R/src.txt"
git -C "$R" add -A && git -C "$R" commit -qm base
BASE="$(git -C "$R" rev-parse HEAD)"

git -C "$R" checkout -q -b head
echo '# HEAD sentinel' > "$R/CLAUDE.md"                                # changed policy file
mkdir -p "$R/.claude/skills/code-review"                              # shadowing skill added at head
printf -- '---\nname: code-review\ndescription: evil\n---\n' > "$R/.claude/skills/code-review/SKILL.md"
echo '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"true"}]}]}}' > "$R/.claude/settings.json"
echo '{"mcpServers":{"evil":{"command":"true"}}}' > "$R/.mcp.json"
git -C "$R" rm -q AGENTS.md                                            # policy file deleted at head
echo 'y' > "$R/src.txt"                                                # non-policy change
git -C "$R" add -A && git -C "$R" commit -qm head
HEAD="$(git -C "$R" rev-parse HEAD)"
git -C "$R" checkout -q --detach "$HEAD"

out="$("$SRC/isolate-policy.sh" "$R" "$BASE" "$HEAD")"

# R3.1 base versions restored, head-only policy removed, head deletions undone
grep -q 'base sentinel' "$R/CLAUDE.md" || { echo "FAIL: CLAUDE.md not restored from base"; FAIL=1; }
[ -f "$R/AGENTS.md" ] || { echo "FAIL: AGENTS.md deleted at head was not restored"; FAIL=1; }
[ ! -e "$R/.claude/skills/code-review" ] || { echo "FAIL: head-only shadow skill survived"; FAIL=1; }
[ -f "$R/.claude/skills/zebra-review/SKILL.md" ] || { echo "FAIL: base skill missing"; FAIL=1; }
# R3.2 unconditional deletions
[ ! -e "$R/.claude/settings.json" ] || { echo "FAIL: settings.json present"; FAIL=1; }
[ ! -e "$R/.mcp.json" ] || { echo "FAIL: .mcp.json present"; FAIL=1; }
# non-policy head content untouched
grep -q '^y$' "$R/src.txt" || { echo "FAIL: src.txt reverted"; FAIL=1; }
# R3.3 changed policy paths reported, exactly
want='[".claude/settings.json",".claude/skills/code-review/SKILL.md",".mcp.json","AGENTS.md","CLAUDE.md"]'
[ "$(jq -c 'sort' <<<"$out")" = "$want" ] || { echo "FAIL: policy_changes=$out"; FAIL=1; }

# Known positive: identical SHAs report no changes
out2="$("$SRC/isolate-policy.sh" "$R" "$BASE" "$BASE")"
[ "$(jq -c . <<<"$out2")" = "[]" ] || { echo "FAIL: expected [] for identical SHAs, got $out2"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "isolate-policy-test: OK"
exit "$FAIL"
