#!/usr/bin/env bash
# Implements references/runners/codex.md.

# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_POLICY_ROOTS=(.codex .agents)
# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_ALWAYS_REMOVE=(.codex)

adapter_check() {
  need_cmd codex
  local version want=0.151.0
  version="$(codex --version 2>/dev/null | awk '{print $2}')" || die 3 "cannot run 'codex --version'"
  valid_semver "$version" || die 3 "cannot parse Codex CLI version: ${version:-empty}"
  semver_at_least "$version" "$want" || die 3 "Codex CLI $want or newer is required, found $version"
}

adapter_is_policy_path() {
  [[ "$1" =~ (^|/)(AGENTS\.md|AGENTS\.override\.md)$|^\.codex/|^\.agents/ ]]
}

adapter_context_paths() {
  local paths=() p peer q shadowed
  while IFS= read -r -d '' p; do paths+=("$p"); done < <(policy_paths "$1" "$2")
  [ "${#paths[@]}" -gt 0 ] || return 0
  for p in "${paths[@]}"; do
    case "$p" in
      .agents/skills/*/SKILL.md) printf '%s\0' "$p" ;;
      AGENTS.override.md|*/AGENTS.override.md) printf '%s\0' "$p" ;;
      AGENTS.md|*/AGENTS.md)
        peer="${p%AGENTS.md}AGENTS.override.md"
        shadowed=""
        for q in "${paths[@]}"; do
          if [ "$q" = "$peer" ]; then shadowed=1; break; fi
        done
        [ -n "$shadowed" ] || printf '%s\0' "$p"
        ;;
    esac
  done
}

adapter_build_command() {
  local prompt="$1" level="$2"
  case "$level" in ''|low|medium|high|xhigh) ;; *) die 2 "LEVEL must be one of low|medium|high|xhigh, got '$level'";; esac
  ADAPTER_COMMAND=(
    codex exec
    --json --ephemeral --ignore-user-config --ignore-rules
    --sandbox read-only --color never --strict-config
    -c 'approval_policy="never"'
    -c 'project_doc_max_bytes=0'
    --disable multi_agent
    --disable apps
    --disable browser_use
    --disable in_app_browser
    --disable computer_use
    --disable image_generation
    --disable hooks
    --disable plugins
    --disable skill_search
    --disable goals
  )
  [ -n "$level" ] && ADAPTER_COMMAND+=(-c "model_reasoning_effort=\"$level\"")
  ADAPTER_COMMAND+=("$prompt")
  return 0
}

adapter_normalize() {
  local raw="$1" child_exit="$2" output="$3" version
  version="$(codex --version 2>/dev/null | awk '{print $2}')" || version=""
  jq -s --arg version "$version" --argjson child_exit "$child_exit" '
    [ .[] | select(.type == "item.completed" and .item.type == "agent_message") | .item.text ] as $messages
    | ([ .[]
        | if .type == "error" then
            (.message // (if (.error | type) == "object" then .error.message else .error end) // "Codex error")
          elif .type == "turn.failed" then
            ((if (.error | type) == "object" then (.error.message // (.error | tostring)) else .error end) // "Codex turn failed")
          else empty
          end
      ]) as $errors
    | {
        engine: "codex",
        engine_version: (if ($version | length) > 0 then $version else null end),
        status: (if $child_exit != 0 or ($errors | length) > 0 or ($messages | length) == 0 then "error" else "completed" end),
        result: ($messages[-1] // ""),
        duration_ms: null,
        cost_usd: null,
        subtype: null,
        errors: $errors,
        denials: []
      }
  ' "$raw" > "$output"
}
