#!/usr/bin/env bash
# The static adapter env blocks (Claude Variant A JSON, Codex profile TOML)
# are documentation, so nothing else checks them. This extracts both, loads
# them as command-scope config, and asks git — never the text — which
# credential helpers actually run for a mapped github.com URL (also with a
# hostile inherited GIT_CONFIG_PARAMETERS), an unmapped one, and a non-GitHub
# one (the reset is unscoped (all hosts)), what the push URL of an org SSH remote
# becomes, and whether signing is off. Requires python3 >= 3.11 (tomllib).
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_CONFIG_PARAMETERS
python3 -c 'import tomllib' 2>/dev/null || { echo "static-block-test: needs python3 >= 3.11 (tomllib) on PATH"; exit 1; }
FAIL=0
DIR="$(cd -- "$(mktemp -d)" >/dev/null 2>&1 && pwd -P)"
trap 'rm -rf "$DIR"' EXIT
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
export GIT_CONFIG_NOSYSTEM=1
LOG="$DIR/helpers.log"
# Stub helpers: each appends its name to the log and answers, so git never
# prompts and the log says which helpers ran and in what order.
printf '#!/bin/sh\necho personal >>"%s"\necho username=p\necho password=p\n' "$LOG" > "$DIR/personal-helper"
printf '#!/bin/sh\necho bot >>"%s"\necho username=b\necho password=b\n' "$LOG" > "$DIR/git-credential-bot"
chmod +x "$DIR/personal-helper" "$DIR/git-credential-bot"
# The global config holds a personal credential helper and the common force-SSH
# rule in both directions, which the block's push-side entries must defeat.
printf '[credential]\n\thelper = !%s\n[url "ssh://git@github.com/"]\n\tinsteadOf = https://github.com/\n\tpushInsteadOf = https://github.com/\n' "$DIR/personal-helper" > "$DIR/global"
export GIT_CONFIG_GLOBAL="$DIR/global" GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/usr/bin/false
fail() { echo "FAIL: $*"; FAIL=1; }

# claude_block -> KEY=VALUE lines for the "env" object of the first JSON block.
claude_block() {
  awk '/^```json/{f=1;next} /^```/{if(f){exit}} f' "$ROOT/references/adapters/claude-code.md" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(f"{k}={v}") for k,v in d["env"].items()]'
}
# codex_block -> KEY=VALUE lines for the first `set = { ... }` table.
codex_block() {
  awk '/^```toml/{f=1;next} /^```/{if(f){exit}} f' "$ROOT/references/adapters/codex.md" \
    | python3 -c 'import sys,tomllib; d=tomllib.loads(sys.stdin.read()); [print(f"{k}={v}") for k,v in d["shell_environment_policy"]["set"].items()]'
}

helpers_for() {  # helpers_for <url> -> space-joined helper names in run order
  : > "$LOG"
  printf 'url=%s\n\n' "$1" | env "${envs[@]}" git credential fill >/dev/null 2>&1 || true
  tr '\n' ' ' < "$LOG"
}

check_block() {
  local label="$1"
  envs=()
  while IFS= read -r line; do
    case "$line" in PATH=*) continue ;; esac
    # The documented helper path is the user's install dir; point it at the stub.
    case "$line" in GIT_CONFIG_VALUE_*=!*git-credential-bot) line="${line%%=*}=!$DIR/git-credential-bot" ;; esac
    envs+=("$line")
  done
  local n keys
  n="$(printf '%s\n' "${envs[@]}" | sed -n 's/^GIT_CONFIG_COUNT=//p')"
  keys="$(printf '%s\n' "${envs[@]}" | grep -c '^GIT_CONFIG_KEY_' || true)"
  [ "$n" = "$keys" ] || fail "$label: GIT_CONFIG_COUNT=$n but $keys keys"
  printf '%s\n' "${envs[@]}" | grep -q '^GIT_CONFIG_PARAMETERS=$' || fail "$label: GIT_CONFIG_PARAMETERS is not pinned empty"
  [ "$(GIT_CONFIG_PARAMETERS="'credential.helper='" helpers_for https://github.com/acme/x.git)" = "bot " ] || fail "$label: an inherited GIT_CONFIG_PARAMETERS still resets the helper (the pin is not applied)"
  [ "$(helpers_for https://github.com/acme/x.git)" = "bot " ] || fail "$label: mapped URL ran helpers: $(helpers_for https://github.com/acme/x.git)"
  [ "$(helpers_for https://github.com/other/x.git)" = "bot " ] || fail "$label: unmapped github.com URL did not run only the bot helper (decisions/001): $(helpers_for https://github.com/other/x.git)"
  # The reset is unscoped (all hosts), so another host runs the bot helper stub too; the
  # real git-credential-bot stays silent there (selflocate-test.sh case 8).
  [ "$(helpers_for https://gitlab.com/me/x.git)" = "bot " ] || fail "$label: the helper reset is not unscoped (all hosts): $(helpers_for https://gitlab.com/me/x.git)"
  [ "$(env "${envs[@]}" git config commit.gpgsign)" = false ] || fail "$label: commit.gpgsign is not false"
  # One scratch repo per remote shape; the block's env is applied to every git call.
  remote_urls() {  # remote_urls <remote-url> -> "<push url> <fetch url>"
    local r; r="$(mktemp -d "$DIR/repo.XXXXXX")"
    git -C "$r" init -q; git -C "$r" remote add origin "$1"
    (cd "$r" && printf '%s %s' "$(env "${envs[@]}" git remote get-url --push origin)" "$(env "${envs[@]}" git ls-remote --get-url origin)")
    rm -rf "$r"
  }
  local got
  got="$(remote_urls git@github.com:acme/x.git)"
  [ "${got%% *}" = https://github.com/acme/x.git ] || fail "$label: SSH org remote git@github.com:acme/x.git: push URL expected https://github.com/acme/x.git, got ${got%% *}"
  got="$(remote_urls https://github.com/acme/x.git)"
  [ "${got%% *}" = https://github.com/acme/x.git ] || fail "$label: HTTPS org remote https://github.com/acme/x.git: push URL expected https://github.com/acme/x.git, got ${got%% *}"
  [ "${got##* }" = https://github.com/acme/x.git ] || fail "$label: HTTPS org remote https://github.com/acme/x.git: fetch URL expected https://github.com/acme/x.git, got ${got##* }"
  # Documentation anchor, not a protection: the static blocks are org-scoped by
  # construction (claude-code.md: "Variant A's pairs are org-scoped by construction"),
  # so the user's global force-SSH rule still rewrites a non-org github.com remote.
  got="$(remote_urls https://github.com/other/x.git)"
  [ "${got%% *}" = ssh://git@github.com/other/x.git ] || fail "$label: non-org HTTPS remote https://github.com/other/x.git: push URL expected ssh://git@github.com/other/x.git (global rule, org-scoped blocks), got ${got%% *}"
}
# Write each block to a file and redirect it in: a pipeline would run
# check_block in a subshell and FAIL=1 would never reach this shell.
claude_block > "$DIR/claude.env"
check_block "claude variant A" < "$DIR/claude.env"
codex_block > "$DIR/codex.env"
check_block "codex profile" < "$DIR/codex.env"
[ "$FAIL" -eq 0 ] && echo "static-block-test: PASS"
exit "$FAIL"
