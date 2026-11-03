#!/usr/bin/env bash
# Offline: skill_frontmatter_json reads the narrow frontmatter grammar in scripts/lib.sh and fails closed on the rest,
# so a skill it cannot read becomes a mandatory read rather than an index entry with a wrong description.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
# shellcheck disable=SC1091
. "$ROOT/scripts/lib.sh"
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
git -C "$S" init -q
FAIL=0
blob() { git -C "$S" hash-object -w --stdin; }
reads() { # reads LABEL EXPECTED_JSON < SKILL.md
  local oid got
  oid="$(blob)"
  got="$(skill_frontmatter_json "$S" "$oid")" || { echo "FAIL: $1 was rejected"; FAIL=1; return; }
  [ "$got" = "$2" ] || { echo "FAIL: $1 read as $got, want $2"; FAIL=1; }
}
rejects() { # rejects LABEL < SKILL.md
  local oid got
  oid="$(blob)"
  if got="$(skill_frontmatter_json "$S" "$oid")"; then echo "FAIL: $1 was accepted as $got"; FAIL=1; fi
}

reads plain '{"name":"a","description":"Use when x."}' <<'EOF'
---
name: a
description: Use when x.
---
body
EOF
reads 'quoted scalars' '{"name":"a","description":"Use when x: y, it'\''s fine"}' <<'EOF'
---
name: "a"
description: 'Use when x: y, it''s fine'
---
EOF
reads 'plain continuation and trailing comment' '{"name":"a","description":"Use when x and also y."}' <<'EOF'
---
name: a # the name
description: Use when x
  and also y.
---
EOF
reads 'folded block' '{"name":"a","description":"First line second line.\nNew paragraph."}' <<'EOF'
---
name: a
description: >-
  First line
  second line.

  New paragraph.
---
EOF
reads 'literal block' '{"name":"a","description":"Line one\nLine two"}' <<'EOF'
---
name: a
description: |
  Line one
  Line two
---
EOF
reads 'other keys, nested children and comments skipped' '{"name":"a","description":"Use when x."}' <<'EOF'
---
# leading comment
metadata:
    github-path: skills/a
    nested: value
name: a
license: MIT
description: Use when x.
allowed-tools: Read
---
EOF
rejects 'no opening fence' <<'EOF'
name: a
description: Use when x.
EOF
rejects 'unclosed fence' <<'EOF'
---
name: a
description: Use when x.
EOF
rejects 'missing name' <<'EOF'
---
description: Use when x.
---
EOF
rejects 'missing description' <<'EOF'
---
name: a
---
EOF
rejects 'empty description' <<'EOF'
---
name: a
description:
---
EOF
rejects 'duplicate description' <<'EOF'
---
name: a
description: one
description: two
---
EOF
rejects 'double-quoted escape' <<'EOF'
---
name: a
description: "Use when \"x\"."
---
EOF
rejects 'quoted scalar spanning lines' <<'EOF'
---
name: a
description: 'Use when x
  and y'
---
EOF
rejects 'top-level line that is not a key' <<'EOF'
---
name: a
- item
description: Use when x.
---
EOF
rejects 'name continued on a second line' <<'EOF'
---
name: a
  b
description: Use when x.
---
EOF
rejects 'two double-quoted scalars on one line' <<'EOF'
---
name: a
description: "one" "two"
---
EOF
rejects 'stray quote inside a single-quoted scalar' <<'EOF'
---
name: a
description: 'it's'
---
EOF
rejects 'flow sequence' <<'EOF'
---
name: a
description: [Use when testing]
---
EOF
rejects 'alias' <<'EOF'
---
name: a
description: *shared
---
EOF
rejects 'sequence marker' <<'EOF'
---
name: a
description: - Use when testing
---
EOF
rejects 'block line left of the first' <<'EOF'
---
name: a
description: >-
    Use when testing
  SECURITY
---
EOF
printf -- '---\nname: a\ndescription: |\n\tUse when testing\n---\n' | rejects 'tab-indented block'
long="$(printf 'x%.0s' $(seq 1 1025))"
rejects 'description over 1024 characters' <<EOF
---
name: a
description: $long
---
EOF
printf -- '---\nname: a\ndescription: bad \377 byte\n---\n' | rejects 'description that is not valid UTF-8'

# Known positive: every SKILL.md committed in this repository, which a frontmatter hook validates, is readable.
read_any=0
while IFS= read -r skill; do
  oid="$(git -C "$ROOT/.." rev-parse "HEAD:$skill" 2>/dev/null)" || continue
  read_any=$((read_any + 1))
  skill_frontmatter_json "$ROOT/.." "$oid" > /dev/null || { echo "FAIL: committed $skill was rejected"; FAIL=1; }
done < <(git -C "$ROOT/.." ls-files '*/SKILL.md')
[ "$read_any" -gt 0 ] || { echo "FAIL: known positive found no committed SKILL.md"; FAIL=1; }

[ "$FAIL" = 0 ] && echo "skill-frontmatter-test: OK ($read_any committed skills read)"
exit "$FAIL"
