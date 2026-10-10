#!/usr/bin/env bash
# Exercises the real bot-token mint path against a local stand-in for the
# GitHub API: JWT construction (verified by the fake against the public key),
# the request, expires_at parsing, atomic 0600 cache publication, a cache hit on
# the second call, and the two failure shapes (empty token, 401).
# Network only for uv's one-time dependency warm-up; every mint runs offline
# (UV_OFFLINE=1) and talks to 127.0.0.1 only.
set -euo pipefail
FAIL=0
DIR="$(cd -- "$(mktemp -d)" >/dev/null 2>&1 && pwd -P)"
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SERVER_PID=""
PORT=""  # set by start_server; empty if the fake never started
trap '[ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$DIR"' EXIT
fail() { echo "FAIL: $*"; FAIL=1; }

export UV_CACHE_DIR="${UV_CACHE_DIR:-$(uv cache dir)}"
# An ambient BOT_INSTALL_ID would override the INSTALL_ID substituted below.
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$(uv python dir)}"
unset BOT_INSTALL_ID
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
# A non-empty NO_PROXY also stops httpx consulting macOS system proxies.
export NO_PROXY=127.0.0.1 no_proxy=127.0.0.1
FAKE_HOME="$DIR/home"
mkdir -p "$FAKE_HOME/.config/acme-agent"
openssl genrsa -out "$FAKE_HOME/.config/acme-agent/key.pem" 2048 2>/dev/null
openssl rsa -in "$FAKE_HOME/.config/acme-agent/key.pem" -pubout -out "$DIR/pub.pem" 2>/dev/null
sed -e 's/^APP_ID = "REPLACE"$/APP_ID = "7"/' -e 's/^INSTALL_ID = "REPLACE"$/INSTALL_ID = "123"/' "$SRC/scripts/bot-token" > "$DIR/bot-token"
chmod +x "$DIR/bot-token"

# Warm-up: the only step allowed to touch the network (uv resolves both scripts'
# dependencies into UV_CACHE_DIR). bot-token exits at its first check on the
# non-numeric installation id, so nothing is minted; the fake's --check only
# imports jwt.
HOME="$FAKE_HOME" BOT_INSTALL_ID=warmup "$DIR/bot-token" >/dev/null 2>&1 || true
uv run --quiet --script "$SRC/tests/fake_github_api.py" --check >/dev/null 2>&1 || true

start_server() {  # start_server <mode>; sets PORT
  : > "$DIR/log"; : > "$DIR/port"  # a stale port file would be read as the new port
  UV_OFFLINE=1 UV_NO_CONFIG=1 uv run --quiet --script "$SRC/tests/fake_github_api.py" "$1" "$DIR/log" "$DIR/pub.pem" > "$DIR/port" &
  SERVER_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -s "$DIR/port" ] && { PORT="$(cat "$DIR/port")"; return; }
    sleep 0.1
  done
  fail "fake API did not start"
}
stop_server() { kill "$SERVER_PID" 2>/dev/null || true; wait "$SERVER_PID" 2>/dev/null || true; SERVER_PID=""; }
# TZ is far from UTC (+12:45/+13:45) so a zone-less parse of expires_at is hours off.
mint() { HOME="$FAKE_HOME" BOT_TOKEN_API_BASE="http://127.0.0.1:$PORT" UV_OFFLINE=1 UV_NO_CONFIG=1 TZ=Pacific/Chatham "$DIR/bot-token" "$@"; }

# 1. Cold mint: a JWT the fake verifies, the Accept header, token printed, cache written 0600 atomically.
start_server ok
out="$(mint 2>"$DIR/err")" || {
  if grep -qE 'offline|No solution found' "$DIR/err"; then
    echo "bot-token-test: dependencies not cached after warm-up"
    exit 1
  fi
  fail "cold mint failed: $(cat "$DIR/err")"
}
# Checked first, right after the mint: the fake's lifetime is 2833 s from the
# request (an odd number, so a hard-coded hour cannot pass), and the 60 s floor
# leaves room for the mint's own runtime on a slow runner while still rejecting a hard-coded hour or a zone-shifted parse.
CACHE="$FAKE_HOME/.cache/acme-agent/token-123.json"
exp="$(sed -n 's/.*"exp": *\([0-9.]*\).*/\1/p' "$CACHE" 2>/dev/null || true)"  # a missing cache must not abort under set -e
awk -v e="$exp" -v n="$(date +%s)" 'BEGIN { d = e - n; exit !(e != "" && d >= 2773 && d <= 2833) }' || fail "cached exp does not match the fake's distinctive expires_at (exp='$exp')"
[ "$out" = ghs_fakemint ] || fail "cold mint printed '$out'"
grep -q '^POST /app/installations/123/access_tokens Bearer OK accept-ok$' "$DIR/log" || fail "request shape wrong: $(cat "$DIR/log")"
[ -f "$CACHE" ] || fail "cache not written"
# GNU first: BSD stat rejects -c with no stdout, so the BSD form runs on macOS;
# the other order breaks on GNU, where -f means --file-system and does not print the mode.
[ "$(stat -c '%a' "$CACHE" 2>/dev/null || stat -f '%Lp' "$CACHE")" = 600 ] || fail "cache mode is not 0600"
ls "$FAKE_HOME/.cache/acme-agent/" | grep -q '\.tmp$' && fail "temp file left behind"

# 2. Warm: second call is a cache hit, no request.
out="$(mint)" || fail "warm call failed"
[ "$out" = ghs_fakemint ] || fail "warm call printed '$out'"
[ "$(wc -l < "$DIR/log")" -eq 1 ] || fail "warm call hit the API"
stop_server

# 3. Empty token from the API: refuse, print nothing, leave no cache for that id.
rm -f "$CACHE"
start_server empty-token
rc=0
out="$(mint 2>"$DIR/err")" || rc=$?
[ "$rc" -ne 0 ] || fail "empty token did not fail"
[ -z "$out" ] || fail "empty token printed '$out'"
grep -q 'empty token' "$DIR/err" || fail "empty-token message missing: $(cat "$DIR/err")"
[ ! -f "$CACHE" ] || fail "empty token was cached"
stop_server

# 4. 401: non-zero exit, nothing printed, nothing cached.
start_server unauthorized
rc=0
out="$(mint 2>/dev/null)" || rc=$?
[ "$rc" -ne 0 ] || fail "401 did not fail"
[ -z "$out" ] || fail "401 printed '$out'"
[ "$(wc -l < "$DIR/log")" -eq 1 ] || fail "401 case never reached the fake"
[ ! -f "$CACHE" ] || fail "401 left a cache file"
stop_server

[ "$FAIL" -eq 0 ] && echo "bot-token-test: PASS"
exit "$FAIL"
