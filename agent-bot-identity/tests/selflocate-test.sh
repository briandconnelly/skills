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

[ "$FAIL" -eq 0 ] && echo "selflocate-test: PASS"
exit "$FAIL"
