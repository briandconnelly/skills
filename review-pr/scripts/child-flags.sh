#!/usr/bin/env bash
# Fixed claude flags shared by run-child.sh (the real child) and
# hostile-fixture-test.sh (the locked-down probe), so the test exercises the
# actual flag set rather than a hand-rolled copy of it.
# Sourced, not executed. Spec R4.2, R4.3.
# The Bash(...) deny entries are defense in depth: --allowedTools adds to the user's own
# permissions.allow rules rather than replacing them, and deny rules win over allow at every
# level (tests/hostile-fixture-test.sh, precedence probe). They are not a complete boundary.
# Excludes: -p PROMPT, --max-budget-usd, --max-turns, --effort (per-invocation).
# shellcheck disable=SC2034  # used by scripts that source this file
CHILD_FLAGS=(
  --output-format json --no-session-persistence
  --permission-mode dontAsk --strict-mcp-config
  --disallowedTools Edit Write NotebookEdit WebFetch WebSearch
    'Bash(gh:*)' 'Bash(curl:*)' 'Bash(wget:*)' 'Bash(ssh:*)'
    'Bash(git push:*)' 'Bash(git fetch:*)' 'Bash(git pull:*)' 'Bash(git remote:*)'
  --allowedTools 'Bash(git diff:*)' 'Bash(git log:*)' 'Bash(git show:*)' 'Bash(git merge-base:*)' Read Grep Glob Skill Agent
)
