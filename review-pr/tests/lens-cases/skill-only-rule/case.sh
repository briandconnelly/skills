#!/usr/bin/env bash
# Skill-only-rule case (#231), 21 skills, the description names the topic. Builder: ../skill-only-rule.lib.sh.
# shellcheck disable=SC1091
. "$(dirname -- "${BASH_SOURCE[0]}")/../skill-only-rule.lib.sh"

build_case() { build_skill_only_rule "$1" "$2" 21 'Use when adding, renaming, or removing a command-line flag in cli/.'; }
