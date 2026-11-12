#!/usr/bin/env bash
# Implements references/runners/pi.md.

# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_POLICY_ROOTS=(.pi .agents .claude)
# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_ALWAYS_REMOVE=(
  .pi/settings.json .pi/mcp.json .pi/SYSTEM.md .pi/APPEND_SYSTEM.md
  .pi/extensions .pi/prompts .pi/themes .pi/npm .pi/git
)

adapter_check() {
  need_cmd pi
  local version want=1.2.0
  version="$(pi --version 2>/dev/null | awk 'NR == 1 {print $1}')" || die 3 "cannot run 'pi --version'"
  valid_semver "$version" || die 3 "cannot parse pi version: ${version:-empty}"
  semver_at_least "$version" "$want" || die 3 "pi $want or newer is required, found $version"
}

adapter_is_policy_path() {
  [[ "$1" =~ (^|/)(AGENTS\.override\.md|AGENTS\.md|AGENTS\.MD|CLAUDE\.md|CLAUDE\.MD)$|^\.pi/|^\.agents/|^\.claude/ ]]
}

# pi loads the first of these names that exists in a directory.
PI_CONTEXT_NAMES=(AGENTS.override.md AGENTS.md AGENTS.MD CLAUDE.md CLAUDE.MD)

adapter_context_paths() {
  local paths=() p q name dir rank best_rank i shadowed
  while IFS= read -r -d '' p; do paths+=("$p"); done < <(restored_policy_paths "$1" "$2")
  [ "${#paths[@]}" -gt 0 ] || return 0
  for p in "${paths[@]}"; do
    case "$p" in
      .agents/skills/*/SKILL.md|.pi/skills/*/SKILL.md|.claude/skills/*/SKILL.md) printf '%s\0' "$p"; continue ;;
    esac
    name="${p##*/}"
    rank=""
    for i in "${!PI_CONTEXT_NAMES[@]}"; do [ "$name" != "${PI_CONTEXT_NAMES[$i]}" ] || rank="$i"; done
    [ -n "$rank" ] || continue
    case "$p" in */*) dir="${p%/*}/";; *) dir="";; esac
    shadowed=""
    for ((best_rank = 0; best_rank < rank; best_rank++)); do
      for q in "${paths[@]}"; do
        if [ "$q" = "$dir${PI_CONTEXT_NAMES[$best_rank]}" ]; then shadowed=1; break 2; fi
      done
    done
    [ -n "$shadowed" ] || printf '%s\0' "$p"
  done
}

adapter_build_command() {
  local prompt="$1" level="$2" ext
  case "$level" in ''|low|medium|high|xhigh|max) ;; *) die 2 "LEVEL must be one of low|medium|high|xhigh|max, got '$level'";; esac
  ADAPTER_PI_LEVEL="$level"
  ADAPTER_COMMAND=(
    pi -p --mode json --no-session --no-approve --offline
    --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files --no-mcp
    --tools 'read,grep,find,ls'
  )
  if [ -n "${REVIEW_PR_PI_EXTENSIONS:-}" ]; then
    local -a exts=()
    IFS=: read -r -a exts <<<"$REVIEW_PR_PI_EXTENSIONS"
    for ext in "${exts[@]}"; do
      [ -n "$ext" ] || continue
      [ -e "$ext" ] || die 3 "REVIEW_PR_PI_EXTENSIONS entry does not exist: $ext"
      ADAPTER_COMMAND+=(-e "$ext")
    done
  fi
  [ -z "${REVIEW_PR_PI_MODEL:-}" ] || ADAPTER_COMMAND+=(--model "$REVIEW_PR_PI_MODEL")
  [ -z "$level" ] || ADAPTER_COMMAND+=(--thinking "$level")
  ADAPTER_COMMAND+=(-- "$prompt")
  return 0
}

adapter_normalize() {
  local raw="$1" child_exit="$2" output="$3" version
  version="$(pi --version 2>/dev/null | awk 'NR == 1 {print $1}')" || version=""
  # A child killed mid-record leaves a partial last line; skipping unparseable lines keeps the earlier records.
  jq -R 'fromjson? // empty' "$raw" | jq -s --arg version "$version" --arg level "${ADAPTER_PI_LEVEL:-}" --argjson child_exit "$child_exit" '
    [ .[] | select(.type == "message_end" and .message.role == "assistant") | .message ] as $messages
    | ($messages[-1] // null) as $final
    | ($final.stopReason // null) as $stop
    | ([ $final.content[]? | select(.type == "text") | .text ] | join("\n")) as $text
    | ([ $messages[] | .usage.cost.total | numbers ]) as $costs
    | ([ $messages[] | .thinkingLevel | strings | select($level != "" and . != $level) ] | unique) as $levels
    | ([
        (if $final == null then "pi produced no assistant message"
         elif $stop == "error" or $stop == "aborted" then ($final.errorMessage // "pi assistant turn ended with \($stop)")
         elif $stop != "stop" then "pi assistant turn ended with \($stop)"
         else empty end),
        (.[] | select(.type == "auto_retry_end" and .success == false) | (.finalError // "pi retries were exhausted")),
        (.[] | select(.type == "compaction_end" and (.errorMessage | type) == "string") | .errorMessage),
        (.[] | select(.type == "agent_settled" and .aborted == true) | "pi run was aborted"),
        ($levels[] | "pi ran at thinking level \(.), not the requested \($level)")
      ]) as $errors
    | {
        engine: "pi",
        engine_version: (if ($version | length) > 0 then $version else null end),
        status: (if $child_exit != 0 or ($errors | length) > 0 or ($text | length) == 0 then "error" else "completed" end),
        result: $text,
        duration_ms: null,
        cost_usd: (if ($costs | length) > 0 then ($costs | add) else null end),
        subtype: (if $stop == null or $stop == "stop" then null else $stop end),
        errors: $errors,
        denials: []
      }
  ' > "$output"
}
