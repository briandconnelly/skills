#!/usr/bin/env bash
# Implements references/runners/claude.md.

# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_POLICY_ROOTS=(.claude .mcp.json)
# shellcheck disable=SC2034 # Consumed by isolate-policy.sh after this adapter is sourced.
ADAPTER_ALWAYS_REMOVE=(.claude/settings.json .claude/settings.local.json .mcp.json)

claude_version_at_least() {
  awk -v have="$1" -v want="$2" 'BEGIN {
    nh=split(have, h, "."); nw=split(want, w, "."); n=(nh>nw?nh:nw)
    for (i=1; i<=n; i++) {
      hv=h[i]+0; wv=w[i]+0
      if (hv>wv) exit 0
      if (hv<wv) exit 1
    }
    exit 0
  }'
}

adapter_check() {
  need_cmd claude
  local version want=2.1.251
  version="$(claude --version 2>/dev/null | awk '{print $1}')" || die 3 "cannot run 'claude --version'"
  claude_version_at_least "$version" "$want" || die 3 "Claude Code $want or newer is required, found $version"
}

adapter_is_policy_path() {
  [[ "$1" =~ (^|/)(CLAUDE\.md|CLAUDE\.local\.md|AGENTS\.md)$|^\.claude/|^\.mcp\.json$ ]]
}

adapter_is_context_path() {
  [[ "$1" =~ (^|/)(CLAUDE\.md|CLAUDE\.local\.md|AGENTS\.md)$|^\.claude/(skills/.*/SKILL\.md|agents/.*\.md)$ ]]
}

adapter_build_command() {
  local prompt="$1" level="$2" budget="$3" turns="$4" evidence_dir="$5"
  case "$level" in ''|low|medium|high|xhigh|max) ;; *) die 2 "LEVEL must be one of low|medium|high|xhigh|max, got '$level'";; esac
  ADAPTER_COMMAND=(
    claude -p "$prompt"
    --output-format json --no-session-persistence
    --permission-mode dontAsk --restricted --strict-mcp-config
    --tools Read Grep Glob
    --add-dir "$evidence_dir"
    --max-budget-usd "$budget" --max-turns "$turns"
  )
  [ -n "$level" ] && ADAPTER_COMMAND+=(--effort "$level")
  return 0
}

adapter_normalize() {
  local raw="$1" child_exit="$2" output="$3" version
  version="$(claude --version 2>/dev/null | awk '{print $1}')" || version=""
  jq --arg version "$version" --argjson child_exit "$child_exit" '
    {
      engine: "claude",
      engine_version: (if ($version | length) > 0 then $version else null end),
      status: (if $child_exit != 0 or (.is_error // false) then "error" else "completed" end),
      result: (.result // ""),
      duration_ms: (.duration_ms // null),
      cost_usd: (.total_cost_usd // null),
      subtype: (.subtype // null),
      errors: (.errors // []),
      denials: (.permission_denials // [])
    }
  ' "$raw" > "$output"
}
