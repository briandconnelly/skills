#!/usr/bin/env bash
# Skill-only-rule case (#231), 60 skills, the #81 scale (60 skills). Builder: ../skill-only-rule.lib.sh.
# shellcheck disable=SC1091
. "$(dirname -- "${BASH_SOURCE[0]}")/../skill-only-rule.lib.sh"

build_case() { build_skill_only_rule "$1" "$2" 60 'Use when adding, renaming, or removing a command-line flag in cli/.'; }
