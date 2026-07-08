#!/usr/bin/env bash
# Verifies shared scripts resolve siblings from an arbitrary install dir.
set -euo pipefail
FAIL=0
DIR="$(cd -- "$(mktemp -d)" >/dev/null 2>&1 && pwd -P)"
trap 'rm -rf "$DIR"' EXIT
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"

cp "$SRC/git-credential-bot" "$SRC/bot-env" "$DIR/"
# Stub bot-token: prints a fake token so no network or key is needed.
printf '#!/usr/bin/env bash\necho ghs_stubtoken\n' > "$DIR/bot-token"
chmod +x "$DIR"/git-credential-bot "$DIR"/bot-env "$DIR"/bot-token

# 1. git-credential-bot must call the SIBLING bot-token, not ~/.claude/bot-shims.
out="$(printf 'protocol=https\nhost=github.com\n\n' | "$DIR/git-credential-bot" get)"
echo "$out" | grep -q '^password=ghs_stubtoken$' || { echo "FAIL: git-credential-bot did not use sibling bot-token"; FAIL=1; }

# 2. bot-env (bot verdict, org repo) must emit sibling paths and the stub token.
REPO="$(mktemp -d)"
git -C "$REPO" init -q
git -C "$REPO" remote add origin git@github.com:acme/scratch.git
out="$(cd "$REPO" && "$DIR/bot-env")"
echo "$out" | grep -qF "GIT_CONFIG_VALUE_1='!$DIR/git-credential-bot'" || { echo "FAIL: bot-env credential-helper path not self-located"; FAIL=1; }
echo "$out" | grep -qF "GH_TOKEN='ghs_stubtoken'" || { echo "FAIL: bot-env did not mint via sibling bot-token"; FAIL=1; }
rm -rf "$REPO"

# 3. session-env.sh must embed its own dir's bot-token in the env-file line.
cp "$SRC/claude/session-env.sh" "$SRC/claude/bot-env-hook.sh" "$DIR/"
chmod +x "$DIR"/session-env.sh "$DIR"/bot-env-hook.sh
ENVF="$(mktemp)"
CLAUDE_ENV_FILE="$ENVF" "$DIR/session-env.sh"
grep -qF "$DIR/bot-token" "$ENVF" || { echo "FAIL: session-env.sh line not self-located"; FAIL=1; }
# The installed line must actually work: eval it and check the stub token landed.
unset GH_TOKEN || true
eval "$(cat "$ENVF")"
[ "${GH_TOKEN:-}" = "ghs_stubtoken" ] || { echo "FAIL: session-env.sh installed line did not mint"; FAIL=1; }
rm -f "$ENVF"

# 4. bot-env-hook.sh must embed its own dir's bot-env; the guard must fail closed.
ENVF="$(mktemp)"
CLAUDE_ENV_FILE="$ENVF" "$DIR/bot-env-hook.sh"
grep -qF "$DIR/bot-env" "$ENVF" || { echo "FAIL: bot-env-hook.sh guard not self-located"; FAIL=1; }
# Fail-closed: with bot-env made non-executable, running the guard must abort.
chmod -x "$DIR/bot-env"
if bash -c "$(cat "$ENVF"); echo reached"; then
  echo "FAIL: guard did not abort with non-executable bot-env"; FAIL=1
fi
chmod +x "$DIR/bot-env"
rm -f "$ENVF"

# 5. Glue metachar guard: an install path with $ or " must be refused, not installed.
EVIL="$DIR/evil\$dir"
mkdir -p "$EVIL"
cp "$DIR/session-env.sh" "$DIR/bot-env-hook.sh" "$EVIL/"
chmod +x "$EVIL"/session-env.sh "$EVIL"/bot-env-hook.sh
ENVF="$(mktemp)"
if CLAUDE_ENV_FILE="$ENVF" "$EVIL/session-env.sh" 2>/dev/null; then
  echo "FAIL: session-env.sh accepted a \$-bearing install path"; FAIL=1
fi
if CLAUDE_ENV_FILE="$ENVF" "$EVIL/bot-env-hook.sh" 2>/dev/null; then
  echo "FAIL: bot-env-hook.sh accepted a \$-bearing install path"; FAIL=1
fi
[ -s "$ENVF" ] && { echo "FAIL: refused install still wrote to the env file"; FAIL=1; }
rm -f "$ENVF"

[ "$FAIL" -eq 0 ] && echo "selflocate-test: PASS"
exit "$FAIL"
