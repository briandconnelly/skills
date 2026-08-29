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
mkdir -p "$R/sub" "$R/docs"
echo '# base nested' > "$R/sub/CLAUDE.md"                              # nested policy file at base
echo 'base docs agents' > "$R/docs/AGENTS.md"                          # nested, deleted at head
echo 'plain' > "$R/sub/file.txt"
printf -- '---\nname: zebra-review\ndescription: base skill\n---\nbody\n' > "$R/.claude/skills/zebra-review/SKILL.md"
echo '{"permissions":{"allow":["Bash(rm:*)"]}}' > "$R/.claude/settings.json"
echo '{"mcpServers":{}}' > "$R/.mcp.json"
echo 'x' > "$R/src.txt"
git -C "$R" add -A && git -C "$R" commit -qm base
BASE="$(git -C "$R" rev-parse HEAD)"

git -C "$R" checkout -q -b pr-head
echo '# HEAD sentinel' > "$R/CLAUDE.md"                                # changed policy file
mkdir -p "$R/.claude/skills/code-review"                              # shadowing skill added at head
printf -- '---\nname: code-review\ndescription: evil\n---\n' > "$R/.claude/skills/code-review/SKILL.md"
echo '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"true"}]}]}}' > "$R/.claude/settings.json"
echo '{"mcpServers":{"evil":{"command":"true"}}}' > "$R/.mcp.json"
git -C "$R" rm -q AGENTS.md                                            # policy file deleted at head
echo '# HEAD nested' > "$R/sub/CLAUDE.md"                              # nested policy file changed at head
mkdir -p "$R/pkg" "$R/deep/x"
echo '# HEAD-only nested' > "$R/pkg/CLAUDE.md"                         # nested policy file added at head
echo '# HEAD local' > "$R/CLAUDE.local.md"                             # root CLAUDE.local.md added at head
echo '# HEAD deep local' > "$R/deep/x/CLAUDE.local.md"                 # nested CLAUDE.local.md added at head
git -C "$R" rm -q docs/AGENTS.md                                       # nested policy file deleted at head
echo '* filter=evil' > "$R/.gitattributes"                             # head selects a filter driver by name
NL_DIR="$R/"$'evil\nx'; TAB_DIR="$R/"$'tab\ty'; mkdir -p "$NL_DIR" "$TAB_DIR"  # path separators that break line-based tools
echo '# HEAD newline-dir' > "$NL_DIR/CLAUDE.md"
echo '# HEAD tab-dir' > "$TAB_DIR/AGENTS.md"
echo 'y' > "$R/src.txt"                                                # non-policy change
git -C "$R" add -A && git -C "$R" commit -qm head
HEAD="$(git -C "$R" rev-parse HEAD)"
git -C "$R" checkout -q --detach "$HEAD"

# A committed .gitattributes at head names a filter driver; if the caller's git config defines it,
# every working-tree checkout runs it. Known positive first: a plain checkout under that config fires.
CFG="$R/../gitconfig"; MARK="$R/../FILTER-FIRED"
printf '[filter "evil"]\n\tsmudge = touch %s\n' "$MARK" > "$CFG"
GIT_CONFIG_GLOBAL="$CFG" git -C "$R" checkout -q "$BASE" -- src.txt   # content differs, so the smudge filter runs
[ -e "$MARK" ] || { echo "FAIL: known positive — filter did not fire under a plain checkout; the instrument cannot detect the failure"; FAIL=1; }
rm -f "$MARK"; git -C "$R" checkout -q "$HEAD" -- src.txt; rm -f "$MARK"

out="$(GIT_CONFIG_GLOBAL="$CFG" "$SRC/isolate-policy.sh" "$R" "$BASE" "$HEAD")"
[ ! -e "$MARK" ] || { echo "FAIL: head .gitattributes filter ran during policy restore"; FAIL=1; }

# R3.1 base versions restored, head-only policy removed, head deletions undone
grep -q 'base sentinel' "$R/CLAUDE.md" || { echo "FAIL: CLAUDE.md not restored from base"; FAIL=1; }
[ -f "$R/AGENTS.md" ] || { echo "FAIL: AGENTS.md deleted at head was not restored"; FAIL=1; }
[ ! -e "$R/.claude/skills/code-review" ] || { echo "FAIL: head-only shadow skill survived"; FAIL=1; }
[ -f "$R/.claude/skills/zebra-review/SKILL.md" ] || { echo "FAIL: base skill missing"; FAIL=1; }
# nested policy files: restored, removed, or re-created exactly as at base
grep -q 'base nested' "$R/sub/CLAUDE.md" || { echo "FAIL: sub/CLAUDE.md not restored from base"; FAIL=1; }
[ ! -e "$R/pkg/CLAUDE.md" ] || { echo "FAIL: head-only pkg/CLAUDE.md survived"; FAIL=1; }
[ ! -e "$R/CLAUDE.local.md" ] || { echo "FAIL: head-only CLAUDE.local.md survived"; FAIL=1; }
[ ! -e "$R/deep/x/CLAUDE.local.md" ] || { echo "FAIL: head-only deep/x/CLAUDE.local.md survived"; FAIL=1; }
[ -f "$R/docs/AGENTS.md" ] || { echo "FAIL: docs/AGENTS.md deleted at head was not restored"; FAIL=1; }
[ ! -e "$NL_DIR/CLAUDE.md" ] || { echo "FAIL: head-only CLAUDE.md under a newline-named directory survived"; FAIL=1; }
[ ! -e "$TAB_DIR/AGENTS.md" ] || { echo "FAIL: head-only AGENTS.md under a tab-named directory survived"; FAIL=1; }
grep -q '^plain$' "$R/sub/file.txt" || { echo "FAIL: non-policy sub/file.txt touched"; FAIL=1; }
# R3.2 unconditional deletions
[ ! -e "$R/.claude/settings.json" ] || { echo "FAIL: settings.json present"; FAIL=1; }
[ ! -e "$R/.mcp.json" ] || { echo "FAIL: .mcp.json present"; FAIL=1; }
# non-policy head content untouched
grep -q '^y$' "$R/src.txt" || { echo "FAIL: src.txt reverted"; FAIL=1; }
# R3.3 changed policy paths reported, exactly
want="$(jq -nc '[".claude/settings.json",".claude/skills/code-review/SKILL.md",".mcp.json","AGENTS.md","CLAUDE.local.md","CLAUDE.md","deep/x/CLAUDE.local.md","docs/AGENTS.md","evil\nx/CLAUDE.md","pkg/CLAUDE.md","sub/CLAUDE.md","tab\ty/AGENTS.md"] | sort')"
[ "$(jq -c 'sort' <<<"$out")" = "$want" ] || { echo "FAIL: policy_changes=$out"; FAIL=1; }

# Config injected through the environment (GIT_CONFIG_COUNT / GIT_CONFIG_PARAMETERS) must not reach the
# restore checkout either. Known positive: a plain checkout under each channel fires the filter.
git -C "$R" checkout -q -f --detach "$HEAD"; rm -f "$MARK"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=filter.evil.smudge GIT_CONFIG_VALUE_0="touch $MARK" git -C "$R" checkout -q "$BASE" -- src.txt
[ -e "$MARK" ] || { echo "FAIL: known positive — GIT_CONFIG_COUNT filter did not fire under a plain checkout"; FAIL=1; }
git -C "$R" checkout -q -f --detach "$HEAD"; rm -f "$MARK"
GIT_CONFIG_PARAMETERS="'filter.evil.smudge=touch $MARK'" git -C "$R" checkout -q "$BASE" -- src.txt
[ -e "$MARK" ] || { echo "FAIL: known positive — GIT_CONFIG_PARAMETERS filter did not fire under a plain checkout"; FAIL=1; }
git -C "$R" checkout -q -f --detach "$HEAD"; rm -f "$MARK"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=filter.evil.smudge GIT_CONFIG_VALUE_0="touch $MARK" "$SRC/isolate-policy.sh" "$R" "$BASE" "$HEAD" >/dev/null
[ ! -e "$MARK" ] || { echo "FAIL: GIT_CONFIG_COUNT filter ran during policy restore"; FAIL=1; }
git -C "$R" checkout -q -f --detach "$HEAD"; rm -f "$MARK"
GIT_CONFIG_PARAMETERS="'filter.evil.smudge=touch $MARK'" "$SRC/isolate-policy.sh" "$R" "$BASE" "$HEAD" >/dev/null
[ ! -e "$MARK" ] || { echo "FAIL: GIT_CONFIG_PARAMETERS filter ran during policy restore"; FAIL=1; }

# Known positive: identical SHAs report no changes
out2="$("$SRC/isolate-policy.sh" "$R" "$BASE" "$BASE")"
[ "$(jq -c . <<<"$out2")" = "[]" ] || { echo "FAIL: expected [] for identical SHAs, got $out2"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "isolate-policy-test: OK"
exit "$FAIL"
