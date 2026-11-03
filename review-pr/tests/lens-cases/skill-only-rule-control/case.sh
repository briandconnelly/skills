#!/usr/bin/env bash
# Skill-only-rule control (#231), 21 skills: the cli-flags body states an unrelated rule the diff meets, so the plant
# has no basis anywhere in the evidence. Recall here would mean the case can be passed without reading the skill
# body. Builder: ../skill-only-rule.lib.sh.
# shellcheck disable=SC1091
. "$(dirname -- "${BASH_SOURCE[0]}")/../skill-only-rule.lib.sh"

# Diagnostic-only: its expected result is a recall miss (lens-rubric.md).
# shellcheck disable=SC2034
CASE_DIAGNOSTIC=1

build_case() { build_skill_only_rule "$1" "$2" 21 'Use when adding, renaming, or removing a command-line flag in cli/.' control; }
