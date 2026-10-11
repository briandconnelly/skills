#!/usr/bin/env bash
# Runs the pi adapter's bun tests. bun test ignores NODE_PATH, so link the
# installed pi package into agent-bot-identity/node_modules (gitignored).
# Run from the repo root: bash agent-bot-identity/tests/pi-extension-test.sh
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
pkg=$(cd "$root" && uv run pi-coding-agent/scripts/pi_docs.py where --json |
  python3 -c 'import json,sys; i=json.load(sys.stdin)["installs"]; print(i[0]["root"] if i else "")')
if [ -z "$pkg" ] || [ ! -d "$pkg" ]; then
  echo "pi-extension-test: no installed pi package found (pi_docs.py where --json returned no installs)" >&2
  exit 2
fi

link="$root/agent-bot-identity/node_modules/@earendil-works/pi-coding-agent"
mkdir -p "$(dirname "$link")"
ln -sfn "$pkg" "$link"

cd "$root/agent-bot-identity"
exec bun test tests/pi-extension.test.ts
