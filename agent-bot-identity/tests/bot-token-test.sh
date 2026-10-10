#!/usr/bin/env bash
# Exercises the real bot-token mint path against a local stand-in for the
# GitHub API: JWT construction, the request, expires_at parsing, atomic 0600
# cache publication, a cache hit on the second call, and the two failure
# shapes (empty token, 401). No network beyond 127.0.0.1; uv's cache stays
# where it is so the script's dependencies resolve offline.
set -euo pipefail
FAIL=0
DIR="$(cd -- "$(mktemp -d)" >/dev/null 2>&1 && pwd -P)"
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)"
SERVER_PID=""
trap '[ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$DIR"' EXIT
fail() { echo "FAIL: $*"; FAIL=1; }

export UV_CACHE_DIR="${UV_CACHE_DIR:-$(uv cache dir)}"
# An ambient BOT_INSTALL_ID would override the INSTALL_ID substituted below.
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$(uv python dir)}"
unset BOT_INSTALL_ID
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
python3 -c 'import datetime; datetime.UTC' 2>/dev/null || { echo "bot-token-test: needs python3 >= 3.11 for the fake API"; exit 1; }
FAKE_HOME="$DIR/home"
mkdir -p "$FAKE_HOME/.config/acme-agent"
openssl genrsa -out "$FAKE_HOME/.config/acme-agent/key.pem" 2048 2>/dev/null
sed -e 's/^APP_ID = "REPLACE"$/APP_ID = "7"/' -e 's/^INSTALL_ID = "REPLACE"$/INSTALL_ID = "123"/' "$SRC/scripts/bot-token" > "$DIR/bot-token"
chmod +x "$DIR/bot-token"

start_server() {  # start_server <mode>; sets PORT
  : > "$DIR/log"; : > "$DIR/port"  # a stale port file would be read as the new port
  python3 -I "$SRC/tests/fake_github_api.py" "$1" "$DIR/log" > "$DIR/port" &
  SERVER_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -s "$DIR/port" ] && { PORT="$(cat "$DIR/port")"; return; }
    sleep 0.1
  done
  fail "fake API did not start"
}
stop_server() { kill "$SERVER_PID" 2>/dev/null || true; wait "$SERVER_PID" 2>/dev/null || true; SERVER_PID=""; }
mint() { HOME="$FAKE_HOME" BOT_TOKEN_API_BASE="http://127.0.0.1:$PORT" "$DIR/bot-token" "$@"; }

# 1. Cold mint: JWT bearer with three segments, token printed, cache written 0600 atomically.
start_server ok
out="$(mint)" || fail "cold mint failed"
[ "$out" = ghs_fakemint ] || fail "cold mint printed '$out'"
grep -q '^POST /app/installations/123/access_tokens Bearer 3$' "$DIR/log" || fail "request shape wrong: $(cat "$DIR/log")"
CACHE="$FAKE_HOME/.cache/acme-agent/token-123.json"
[ -f "$CACHE" ] || fail "cache not written"
[ "$(stat -f '%Lp' "$CACHE" 2>/dev/null || stat -c '%a' "$CACHE")" = 600 ] || fail "cache mode is not 0600"
ls "$FAKE_HOME/.cache/acme-agent/" | grep -q '\.tmp$' && fail "temp file left behind"
python3 -c "import json,sys,time; c=json.load(open('$CACHE')); sys.exit(0 if 3500 < c['exp']-time.time() <= 3600 else 1)" || fail "cached exp does not match expires_at"

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

# 4. 401: non-zero exit, nothing printed.
start_server unauthorized
rc=0
out="$(mint 2>/dev/null)" || rc=$?
[ "$rc" -ne 0 ] || fail "401 did not fail"
[ -z "$out" ] || fail "401 printed '$out'"
[ "$(wc -l < "$DIR/log")" -eq 1 ] || fail "401 case never reached the fake"
stop_server

[ "$FAIL" -eq 0 ] && echo "bot-token-test: PASS"
exit "$FAIL"
