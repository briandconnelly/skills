#!/usr/bin/env bash
# Fixed claude flags shared by run-child.sh (the real child) and
# hostile-fixture-test.sh (the locked-down probe), so the test exercises the
# actual flag set rather than a hand-rolled copy of it.
# Sourced, not executed. Spec R4.2, R4.3.
# Excludes: -p PROMPT, --max-budget-usd, --max-turns, --effort (per-invocation).
# shellcheck disable=SC2034  # used by scripts that source this file
CHILD_FLAGS=(
  --output-format json --no-session-persistence
  --permission-mode dontAsk --strict-mcp-config
  --disallowedTools Edit Write NotebookEdit WebFetch WebSearch
  --allowedTools 'Bash(git diff:*)' 'Bash(git log:*)' 'Bash(git show:*)' 'Bash(git merge-base:*)' Read Grep Glob Skill Agent
)
