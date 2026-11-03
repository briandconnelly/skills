#!/usr/bin/env bash
# Skill-only-rule case (#231), 21 skills, a vague description, as a diagnostic of how much on-demand reading depends on description quality. Builder: ../skill-only-rule.lib.sh.
# shellcheck disable=SC1091
. "$(dirname -- "${BASH_SOURCE[0]}")/../skill-only-rule.lib.sh"

# Diagnostic-only: collected with --diagnostic and excluded from the case-by-runner coverage check, because a
# miss here is a finding to document rather than a regression (lens-rubric.md).
# shellcheck disable=SC2034
CASE_DIAGNOSTIC=1

build_case() { build_skill_only_rule "$1" "$2" 21 'Project conventions.'; }
