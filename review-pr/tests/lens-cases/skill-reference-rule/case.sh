#!/usr/bin/env bash
# Skill-reference-rule case (#231, level 3), 21 skills: the cli-flags body points at reference.md beside it, which
# alone states the rule; the manifest lists SKILL.md but not reference.md, so recall needs a read of an unlisted file.
# Builder: ../skill-only-rule.lib.sh.
# shellcheck disable=SC1091
. "$(dirname -- "${BASH_SOURCE[0]}")/../skill-only-rule.lib.sh"

build_case() { build_skill_only_rule "$1" "$2" 21 'Use when adding, renaming, or removing a command-line flag in cli/.' reference; }
