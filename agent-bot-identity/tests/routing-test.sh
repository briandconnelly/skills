#!/usr/bin/env bash
# Verifies bot-env's routing verdict and the *effective* git transport under
# the emitted env: which git exit statuses may resolve personal, and that a
# bot verdict routes every github.com remote through HTTPS (and therefore the
# bot credential helper) even when the user's own git config carries the
# common force-SSH rewrites. Every URL assertion goes through git itself
# (`ls-remote --get-url`, `remote get-url --push`), never through the emitted
# text, because insteadOf resolution is longest-match across all config
# scopes and only git knows the answer. No network anywhere.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
unset BOT_INSTALL_ID || true
FAIL=0
DIR="$(cd -- "$(mktemp -d)" >/dev/null 2>&1 && pwd -P)"
trap 'rm -rf "$DIR"' EXIT
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd -P)/scripts"

# The developer's real global config may carry its own rewrites; every case
# below runs against an explicit global file so the assertions are hermetic.
export GIT_CONFIG_NOSYSTEM=1
EMPTY_GLOBAL="$DIR/global-empty"
: > "$EMPTY_GLOBAL"
export GIT_CONFIG_GLOBAL="$EMPTY_GLOBAL"

# Later cases write ~/.netrc and ~/.ssh/config, so the whole suite runs under
# a scratch HOME; the guard below is what protects the developer's real
# files if this block is ever moved or removed.
# UV is not used by the stub bot-token, but keep uv's cache where it was in
# case a later case runs the real one.
export UV_CACHE_DIR="${UV_CACHE_DIR:-$(uv cache dir 2>/dev/null || echo "$DIR/uv-cache")}"
export HOME="$DIR/home"
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
[ "$HOME" = "$DIR/home" ] || { echo "refusing: HOME is not the scratch dir"; exit 2; }
# bot-env resolves ssh hosts through GIT_SSH_COMMAND or GIT_SSH when they are
# set, which would bypass the shim below; the precedence cases set them per
# command themselves.
unset GIT_SSH_COMMAND GIT_SSH
# OpenSSH reads its default user config from the passwd home directory, not
# $HOME, so a scratch HOME alone would let the developer's real ~/.ssh/config
# decide alias cases. This shim points ssh at the scratch config unless the
# caller passes its own -F.
REAL_SSH="$(command -v ssh)"
mkdir -p "$DIR/ssh-shim"
cat > "$DIR/ssh-shim/ssh" <<EOF
#!/bin/sh
for a in "\$@"; do [ "\$a" = -F ] && exec "$REAL_SSH" "\$@"; done
exec "$REAL_SSH" -F "$HOME/.ssh/config" "\$@"
EOF
: > "$HOME/.ssh/config"
chmod +x "$DIR/ssh-shim/ssh"
export PATH="$DIR/ssh-shim:$PATH"

cp "$SRC/git-credential-bot" "$DIR/"
awk '{ if ($0 == "acme:REPLACE") print "acme:111"; else print }' "$SRC/bot-env" > "$DIR/bot-env"
printf '#!/usr/bin/env bash\n[ -n "${BOT_TOKEN_CALLS:-}" ] && : >> "$BOT_TOKEN_CALLS"\necho "ghs_stub-${BOT_INSTALL_ID:-none}"\n' > "$DIR/bot-token"
chmod +x "$DIR"/git-credential-bot "$DIR"/bot-env "$DIR"/bot-token

fail() { echo "FAIL: $*"; FAIL=1; }

# mkrepo <remote-url|""> -> prints repo path
mkrepo() {
  local r; r="$(mktemp -d)"
  git -C "$r" init -q
  [ -n "${1:-}" ] && git -C "$r" remote add origin "$1"
  echo "$r"
}

# verdict <repo> -> BOT | PERSONAL | ABORT; stderr of bot-env lands in $DIR/err
verdict() {
  local out rc=0
  out="$(cd "$1" && "$DIR/bot-env" 2>"$DIR/err")" || rc=$?
  if [ "$rc" -ne 0 ]; then echo ABORT; return; fi
  if echo "$out" | grep -q '^export GH_TOKEN='; then echo BOT; else echo PERSONAL; fi
}

# effective <repo> <remote> [global-config-file] -> "fetch=<url> push=<url>"
# as git resolves them after eval'ing the emitted env in that repo.
effective() {
  local repo="$1" remote="$2" global="${3:-$EMPTY_GLOBAL}"
  (
    cd "$repo"
    eval "$("$DIR/bot-env" 2>/dev/null)"
    printf 'fetch=%s push=%s\n' \
      "$(GIT_CONFIG_GLOBAL="$global" git ls-remote --get-url "$remote")" \
      "$(GIT_CONFIG_GLOBAL="$global" git remote get-url --push "$remote")"
  )
}

# --- Exit-status handling ---------------------------------------------------
# git exits 128 on every fatal error, not only on "not a git repository".
# Only the latter is a definitive personal answer; every other 128 is
# ambiguous and must resolve toward the bot with a warning.

# 1. Corrupt .git/config in an org repo.
R="$(mkrepo git@github.com:acme/x.git)"
printf '[broken\n' >> "$R/.git/config"
[ "$(verdict "$R")" = BOT ] || fail "corrupt .git/config (exit 128) resolved personal in an org repo"
grep -q 'ambiguous' "$DIR/err" || fail "corrupt .git/config gave no ambiguity warning"
rm -rf "$R"

# 2. Unsupported repository format version in an org repo.
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" config core.repositoryformatversion 99
[ "$(verdict "$R")" = BOT ] || fail "unsupported repositoryformatversion (exit 128) resolved personal in an org repo"
rm -rf "$R"

# 3. Malformed inherited GIT_CONFIG_* env (git dies before reading the repo).
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_COUNT=abc "$DIR/bot-env" 2>/dev/null)" || fail "malformed inherited GIT_CONFIG_* aborted instead of resolving bot"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "malformed inherited GIT_CONFIG_* (exit 128) resolved personal in an org repo"
rm -rf "$R"

# 4. A directory that is not a repository is still definitively personal.
R="$(mktemp -d)"
[ "$(verdict "$R")" = PERSONAL ] || fail "a non-repository directory no longer resolves personal"
[ -s "$DIR/err" ] && fail "a non-repository directory produced a warning: $(cat "$DIR/err")"
rm -rf "$R"

# --- Effective transport under a bot verdict --------------------------------

# 5. Canonical org SSH remote, no user rewrites: both directions HTTPS.
R="$(mkrepo git@github.com:acme/x.git)"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "canonical org remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 6. Org HTTPS remote plus the common global force-SSH insteadOf: the user's
#    host-wide rule must not pull the remote back onto the personal SSH key.
FORCE_SSH="$DIR/global-force-ssh"
printf '[url "ssh://git@github.com/"]\n\tinsteadOf = https://github.com/\n' > "$FORCE_SSH"
R="$(mkrepo https://github.com/acme/x.git)"
[ "$(effective "$R" origin "$FORCE_SSH")" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "global force-SSH insteadOf defeated the bot verdict: $(effective "$R" origin "$FORCE_SSH")"
rm -rf "$R"

# 7. Org HTTPS remote plus a global pushInsteadOf force-SSH rule.
FORCE_PUSH="$DIR/global-force-push"
printf '[url "git@github.com:"]\n\tpushInsteadOf = https://github.com/\n' > "$FORCE_PUSH"
R="$(mkrepo https://github.com/acme/x.git)"
[ "$(effective "$R" origin "$FORCE_PUSH")" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "global pushInsteadOf defeated the bot verdict: $(effective "$R" origin "$FORCE_PUSH")"
rm -rf "$R"

# 8. Org SSH remote plus a global pushInsteadOf that matches the SSH form
#    (pushInsteadOf is consulted before insteadOf for pushes).
FORCE_PUSH_SSH="$DIR/global-force-push-ssh"
printf '[url "ssh://git@github.com/"]\n\tpushInsteadOf = git@github.com:\n' > "$FORCE_PUSH_SSH"
R="$(mkrepo git@github.com:acme/x.git)"
[ "$(effective "$R" origin "$FORCE_PUSH_SSH")" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "global SSH pushInsteadOf defeated the bot verdict: $(effective "$R" origin "$FORCE_PUSH_SSH")"
rm -rf "$R"

# 9. Mixed-case SSH remote: git's insteadOf match is literal, GitHub's
#    namespace is not.
R="$(mkrepo SSH://git@GITHUB.COM/ACME/x.git)"
mixed="$(effective "$R" origin | tr '[:upper:]' '[:lower:]')"
[ "$mixed" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "mixed-case org remote not rewritten: $mixed"
rm -rf "$R"

# 10. An unmapped github.com remote in an org repo (fork/upstream shape) is
#     routed through the token too, so the installation boundary is what
#     fails loudly there rather than the personal SSH key succeeding.
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add upstream git@github.com:oss-project/x.git
[ "$(effective "$R" upstream)" = 'fetch=https://github.com/oss-project/x.git push=https://github.com/oss-project/x.git' ] || fail "unmapped github.com remote left on SSH under a bot verdict: $(effective "$R" upstream)"
rm -rf "$R"

# 11. An explicit SSH pushurl is rewritten as well.
R="$(mkrepo https://github.com/acme/x.git)"
git -C "$R" remote set-url --push origin git@github.com:acme/x.git
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "explicit SSH pushurl left on SSH: $(effective "$R" origin)"
rm -rf "$R"

# 12. A non-GitHub remote in an org repo is left alone: the credential helper
#     is host-gated, so rewriting it would only break it.
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add mirror git@gitlab.com:acme/x.git
[ "$(effective "$R" mirror)" = 'fetch=git@gitlab.com:acme/x.git push=git@gitlab.com:acme/x.git' ] || fail "non-GitHub remote was rewritten: $(effective "$R" mirror)"
rm -rf "$R"

# 13. A github.com URL typed on the command line (no remote) is rewritten by
#     the host-wide pairs.
R="$(mkrepo git@github.com:acme/x.git)"
adhoc="$(cd "$R" && eval "$("$DIR/bot-env" 2>/dev/null)" && git ls-remote --get-url git@github.com:acme/other.git)"
[ "$adhoc" = 'https://github.com/acme/other.git' ] || fail "ad-hoc github.com URL not rewritten: $adhoc"
rm -rf "$R"

# 14. scp-style remote with a leading slash in the path (GitHub tolerates it):
#     org verdict and a clean HTTPS target, not a double slash.
R="$(mkrepo git@github.com:/acme/x.git)"
[ "$(verdict "$R")" = BOT ] || fail "leading-slash scp org remote resolved personal"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "leading-slash scp remote rewritten badly: $(effective "$R" origin)"
rm -rf "$R"

# 15. Every emitted line must still match the three shapes the shared parser
#     (scripts/bot-env-block.ts) accepts (export KEY='...', export KEY=digits,
#     unset KEY ...).
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add upstream SSH://git@GITHUB.COM/oss-project/x.git
bad="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | grep -Ev "^export [A-Z_][A-Z0-9_]*='[^']*'$|^export [A-Z_][A-Z0-9_]*=[0-9]+$|^unset [A-Z_][A-Z0-9_]*( [A-Z_][A-Z0-9_]*)*$|^# bot-env: end$" || true)"
[ -z "$bad" ] || fail "bot-env emitted a line the adapters cannot parse: $bad"
count="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | sed -n 's/^export GIT_CONFIG_COUNT=//p')"
keys="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | grep -c '^export GIT_CONFIG_KEY_')"
[ "$count" = "$keys" ] || fail "GIT_CONFIG_COUNT=$count but $keys keys were emitted"
[ "$(cd "$R" && "$DIR/bot-env" 2>/dev/null | tail -n 1)" = '# bot-env: end' ] || fail "bot verdict does not end with the completeness line"
P="$(mkrepo git@gitlab.com:someone/x.git)"
[ "$(cd "$P" && "$DIR/bot-env" 2>/dev/null | tail -n 1)" = '# bot-env: end' ] || fail "personal verdict does not end with the completeness line"
[ "$(cd "$P" && "$DIR/bot-env" 2>/dev/null | grep -c '^# bot-env: end$')" = 1 ] || fail "personal verdict emits the completeness line more than once"
rm -rf "$P"
rm -rf "$R"

# 15b. Real bot-env output satisfies the shared parser's contract check, not
#      only its line shapes: an org bot verdict, an ambiguous (no-remote) bot
#      verdict that unsets BOT_INSTALL_ID, and a personal verdict that also
#      enumerates inherited GIT_CONFIG_* vars. Needs bun; without it the case
#      reports SKIP rather than passing silently.
if command -v bun >/dev/null 2>&1; then
  cat > "$DIR/parse.ts" <<EOF
import { parseBotEnvBlock } from "$SRC/bot-env-block.ts"
const stdout = await new Response(Bun.stdin.stream()).text()
try { parseBotEnvBlock(stdout, process.cwd()) } catch (err) { console.log((err as Error).message); process.exit(1) }
EOF
  R="$(mkrepo git@github.com:acme/x.git)"
  N="$(mkrepo "")"
  P="$(mkrepo git@gitlab.com:someone/x.git)"
  for case in "org-bot:$R:" "ambiguous-bot:$N:" "personal:$P:GIT_CONFIG_KEY_0=x GIT_CONFIG_VALUE_0=y"; do
    name="${case%%:*}"; rest="${case#*:}"; repo="${rest%%:*}"; extra="${rest#*:}"
    # shellcheck disable=SC2086 # $extra is a deliberate word-split list of NAME=value pairs
    out="$(cd "$repo" && env $extra "$DIR/bot-env" 2>/dev/null)" || { fail "$name: bot-env aborted"; continue; }
    msg="$(printf '%s\n' "$out" | bun "$DIR/parse.ts" 2>&1)" || fail "$name: real bot-env output refused by the shared parser: $msg"
  done
  out="$(cd "$N" && "$DIR/bot-env" 2>/dev/null)"
  echo "$out" | grep -q '^unset BOT_INSTALL_ID$' || fail "ambiguous bot verdict no longer unsets BOT_INSTALL_ID (case 15b lost its default-installation shape)"
  out="$(cd "$P" && GIT_CONFIG_KEY_0=x "$DIR/bot-env" 2>/dev/null)"
  echo "$out" | grep -q '^unset GIT_CONFIG_KEY_0$' || fail "personal verdict did not enumerate an inherited GIT_CONFIG_KEY_0 (case 15b lost its enumerated shape)"
  rm -rf "$R" "$N" "$P"
else
  echo "SKIP: case 15b (bun not on PATH)"
fi

# 16. A raw remote value that cannot be emitted safely still aborts rather
#     than routing with a partial identity.
R="$(mkrepo "git@github.com:acme/it's.git")"
[ "$(verdict "$R")" = ABORT ] || fail "unquotable raw remote did not abort"
rm -rf "$R"

# --- Cases from the 2026-09-22 Codex review of the first fix -----------------

# 17. A path character that is legal in a URL must not corrupt the emitted
#     pair (the first fix used it as a record separator).
R="$(mkrepo 'git@github.com:acme/x|y.git')"
out="$(cd "$R" && "$DIR/bot-env" 2>/dev/null)"
echo "$out" | grep -qF "export GIT_CONFIG_KEY_" || fail "pipe-in-path remote produced no env"
echo "$out" | grep -q "^export GIT_CONFIG_VALUE_[0-9]*='git@github.com:acme/x|y.git'$" || fail "pipe-in-path raw value not emitted verbatim"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x|y.git push=https://github.com/acme/x|y.git' ] || fail "pipe-in-path remote rewritten badly: $(effective "$R" origin)"
rm -rf "$R"

# 18. Two scp spellings of one repo, where the second is a suffix of the
#     first: both must get exact pairs, and the username-less form must be
#     rewritten (SSH config can supply the user, so it is a real SSH path).
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote set-url --push origin github.com:acme/x.git
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "suffix-shaped second scp remote left on SSH: $(effective "$R" origin)"
rm -rf "$R"

# 19. The username-less scp form alone is covered host-wide too.
R="$(mkrepo github.com:acme/x.git)"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "username-less scp remote left on SSH: $(effective "$R" origin)"
rm -rf "$R"

# 20. A rule in the user's own config that matches the complete remote URL
#     ties with the exact pair on length, and git keeps the first-read rule —
#     the user's. Rewrites cannot win that, so bot-env must notice that the
#     remote still resolves to SSH and abort rather than route with the
#     personal key.
FULL_URL_RULE="$DIR/global-full-url"
printf '[url "ssh://REDACTED@github.com/acme/x.git"]\n\tinsteadOf = https://github.com/acme/x.git\n' > "$FULL_URL_RULE"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$FULL_URL_RULE" "$DIR/bot-env" 2>"$DIR/err")" || rc=$?
[ "$rc" -ne 0 ] || fail "remote still resolving to SSH after the rewrites did not abort"
[ -z "$out" ] || fail "SSH-resolving remote abort still emitted env lines"
grep -q 'origin' "$DIR/err" && grep -q 'ssh://\*\*\*@github.com/acme/x.git' "$DIR/err" || fail "SSH-resolving remote abort did not name the remote and its masked effective URL: $(cat "$DIR/err")"
! grep -q REDACTED "$DIR/err" || fail "SSH-resolving remote abort echoed the URL's userinfo: $(cat "$DIR/err")"
rm -rf "$R"

# 20b. Same shape on the push side only (pushInsteadOf ties the same way).
FULL_URL_PUSH="$DIR/global-full-url-push"
printf '[url "ssh://git@github.com/acme/x.git"]\n\tpushInsteadOf = https://github.com/acme/x.git\n' > "$FULL_URL_PUSH"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$FULL_URL_PUSH" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "remote whose push URL still resolves to SSH did not abort"
rm -rf "$R"

# 21. An ad-hoc org URL typed on the command line, under the host-wide
#     force-SSH rule: the org-scoped identity pair is longer than the user's
#     host-wide rule, so it wins.
R="$(mkrepo git@github.com:acme/x.git)"
adhoc="$(cd "$R" && eval "$("$DIR/bot-env" 2>/dev/null)" && GIT_CONFIG_GLOBAL="$FORCE_SSH" git ls-remote --get-url https://github.com/acme/other.git)"
[ "$adhoc" = 'https://github.com/acme/other.git' ] || fail "ad-hoc org https URL lost to the global force-SSH rule: $adhoc"
rm -rf "$R"

# 22. Diagnostic text that merely contains the not-a-repository phrase is not
#     the not-a-repository answer: a malformed inherited key whose *value*
#     carries the phrase still exits 128 for a different reason.
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0='not a git repository' GIT_CONFIG_VALUE_0=x "$DIR/bot-env" 2>/dev/null)" || fail "malformed key carrying the phrase aborted instead of resolving bot"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "malformed key carrying the not-a-repository phrase resolved personal"
rm -rf "$R"

# --- Cases from the second Codex review (effective-URL check edge cases) -----

# 23. A remote whose name ends in `.url` must be checked under its real name:
#     naive suffix stripping turns `remote.review.url.pushurl` into `review`.
R="$(mkrepo)"
git -C "$R" remote add review.url git@gitlab.com:acme/x.git
git -C "$R" remote set-url --push review.url git@github.com:acme/review.git
git -C "$R" remote add origin git@github.com:acme/x.git
[ "$(verdict "$R")" = BOT ] || fail "dotted remote name aborted or resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" review.url)" = 'fetch=git@gitlab.com:acme/x.git push=https://github.com/acme/review.git' ] || fail "dotted remote name's GitHub pushurl not rewritten: $(effective "$R" review.url)"
# A tie rule that matches only the dotted remote's push URL, so the abort
# must be attributed to `review.url`, not to `origin`. It is an insteadOf
# rule because git ignores pushInsteadOf for a remote with an explicit
# pushurl, which is what review.url has.
DOTTED_TIE="$DIR/global-dotted-tie"
printf '[url "ssh://git@github.com/acme/review.git"]\n\tinsteadOf = git@github.com:acme/review.git\n' > "$DOTTED_TIE"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$DOTTED_TIE" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "tie on a dotted remote name's pushurl did not abort"
grep -q "'review.url'" "$DIR/err" || fail "tie abort did not name the dotted remote: $(cat "$DIR/err")"
rm -rf "$R"

# 24. A remote with a GitHub fetch URL and a non-GitHub push URL is legitimate:
#     only GitHub destinations are held to HTTPS, other hosts are left alone.
R="$(mkrepo https://github.com/acme/x.git)"
git -C "$R" remote set-url --push origin git@gitlab.com:acme/x.git
[ "$(verdict "$R")" = BOT ] || fail "mixed-host remote aborted or resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=git@gitlab.com:acme/x.git' ] || fail "mixed-host remote rewritten wrongly: $(effective "$R" origin)"
rm -rf "$R"

# 25. A push-only remote (pushurl, no url): git reports the remote name as its
#     fetch URL, which must not be mistaken for an SSH transport.
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" config remote.deploy.pushurl git@github.com:acme/deploy.git
[ "$(verdict "$R")" = BOT ] || fail "push-only remote aborted or resolved personal: $(cat "$DIR/err")"
pushonly="$(cd "$R" && eval "$("$DIR/bot-env" 2>/dev/null)" && git remote get-url --push deploy)"
[ "$pushonly" = 'https://github.com/acme/deploy.git' ] || fail "push-only remote's pushurl not rewritten: $pushonly"
rm -rf "$R"

# --- Cases from Copilot's review of PR #180 ---------------------------------

# 26. A colonless remote value is a local path to git, even when it is named
#     `github.com`; it must not be classified as a GitHub host or rewritten.
R="$(mkrepo git@github.com:acme/x.git)"
mkdir -p "$R/github.com"
git -C "$R" remote add local github.com
[ "$(verdict "$R")" = BOT ] || fail "org repo with a local remote named github.com aborted or resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" local)" = 'fetch=github.com push=github.com' ] || fail "local remote named github.com was rewritten: $(effective "$R" local)"
out="$(cd "$R" && "$DIR/bot-env" 2>/dev/null)"
echo "$out" | grep -q "^export GIT_CONFIG_VALUE_[0-9]*='github.com'$" && fail "an exact pair was emitted for a local path named github.com"
rm -rf "$R"

# 27. A slash before the first colon makes the value a local path, not scp
#     syntax (git's own rule), so `./github.com:x` is left alone as well.
R="$(mkrepo git@github.com:acme/x.git)"
mkdir -p "$R/github.com:x"
git -C "$R" remote add odd './github.com:x'
[ "$(verdict "$R")" = BOT ] || fail "org repo with a slash-before-colon local remote aborted or resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" odd)" = 'fetch=./github.com:x push=./github.com:x' ] || fail "slash-before-colon local remote was rewritten: $(effective "$R" odd)"
rm -rf "$R"

# 28. A repo whose only remote is a local path named github.com is personal.
R="$(mkrepo github.com)"
[ "$(verdict "$R")" = PERSONAL ] || fail "sole local remote named github.com did not resolve personal"
rm -rf "$R"

# --- Cases from the 2026-10-09 dual review --------------------------------

# 29. Inherited GIT_CONFIG_PARAMETERS is applied by git after the
#     GIT_CONFIG_COUNT entries, so a personal helper there would be the last
#     helper and win. A bot verdict must neutralise it; a personal verdict
#     must unset it.
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_PARAMETERS="'credential.helper=human'" "$DIR/bot-env" 2>/dev/null)" || fail "inherited GIT_CONFIG_PARAMETERS aborted bot-env"
echo "$out" | grep -q "^export GIT_CONFIG_PARAMETERS=''$" || fail "bot verdict did not neutralise GIT_CONFIG_PARAMETERS"
last="$(cd "$R" && export GIT_CONFIG_PARAMETERS="'credential.helper=human'" && eval "$out" && git config --get-all credential.helper | tail -1)"
[ "$last" = "!$DIR/git-credential-bot" ] || fail "inherited GIT_CONFIG_PARAMETERS still supplies the last helper: $last"
rm -rf "$R"

# 30. Personal verdict unsets it like the other identity variables.
R="$(mkrepo git@gitlab.com:me/x.git)"
out="$(cd "$R" && GIT_CONFIG_PARAMETERS="'credential.helper=human'" "$DIR/bot-env" 2>/dev/null)"
echo "$out" | grep -q '^unset GIT_CONFIG_PARAMETERS$' || fail "personal verdict left GIT_CONFIG_PARAMETERS exported"
rm -rf "$R"

# 31. A remote defined in a file pulled in by include.path is a raw remote
#     git uses; `git config --local` hides it without --includes, so the
#     verdict was "no remotes, ambiguous" (bot by luck) instead of a
#     recognised org remote with its exact rewrite pair.
R="$(mkrepo)"
printf '[remote "origin"]\n\turl = git@github.com:acme/inc.git\n' > "$R/.git/remotes.inc"
git -C "$R" config include.path remotes.inc
[ "$(verdict "$R")" = BOT ] || fail "included org remote did not resolve bot"
grep -q 'no raw remote URLs' "$DIR/err" && fail "included org remote was reported as no remotes"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/inc.git push=https://github.com/acme/inc.git' ] || fail "included org remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 32. A visible personal remote plus an includeIf-gated org remote must
#     still be the org's repo. git realpaths the git dir before matching the
#     gitdir pattern, so the pattern is built from `pwd -P`.
R="$(mkrepo git@gitlab.com:me/x.git)"
RP="$(cd "$R" && pwd -P)"
printf '[remote "work"]\n\turl = git@github.com:acme/inc.git\n' > "$R/.git/remotes.inc"
git -C "$R" config "includeIf.gitdir:$RP/.elsewhere/.path" remotes.inc
[ "$(verdict "$R")" = PERSONAL ] || fail "a non-matching includeIf changed the verdict"
git -C "$R" config "includeIf.gitdir:$RP/.path" remotes.inc
[ "$(verdict "$R")" = BOT ] || fail "included org remote behind a visible personal remote resolved personal"
rm -rf "$R"

printf 'Host gh\n  HostName github.com\n  User git\nHost gh443\n  HostName ssh.github.com\n  Port 443\n  User git\nHost github.com-work\n  HostName github.com\nHost gl\n  HostName gitlab.com\n' > "$HOME/.ssh/config"

# 33. GitHub's documented SSH-over-443 endpoint is GitHub: bot verdict and an
#     HTTPS target on github.com.
R="$(mkrepo ssh://git@ssh.github.com:443/acme/x.git)"
[ "$(verdict "$R")" = BOT ] || fail "ssh.github.com:443 sole remote resolved personal"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "ssh.github.com remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 34. The scp spelling of the same endpoint.
R="$(mkrepo git@ssh.github.com:acme/x.git)"
[ "$(verdict "$R")" = BOT ] || fail "git@ssh.github.com scp remote resolved personal"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "git@ssh.github.com scp remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 35. An ~/.ssh/config alias that resolves to github.com is GitHub.
R="$(mkrepo gh:acme/x.git)"
[ "$(verdict "$R")" = BOT ] || fail "ssh alias to github.com resolved personal"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "ssh alias remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 36. An alias whose name contains a dot is still resolved, not trusted literally.
R="$(mkrepo github.com-work:acme/x.git)"
[ "$(verdict "$R")" = BOT ] || fail "dotted ssh alias to github.com resolved personal"
rm -rf "$R"

# 37. An alias that resolves elsewhere is another host: personal, untouched.
R="$(mkrepo gl:me/x.git)"
[ "$(verdict "$R")" = PERSONAL ] || fail "ssh alias to gitlab.com did not resolve personal"
rm -rf "$R"

# 38. Org origin plus an aliased ssh.github.com upstream: the upstream must
#     reach HTTPS too, or a push there rides the personal key.
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add upstream gh443:acme/y.git
[ "$(verdict "$R")" = BOT ] || fail "org repo with aliased upstream aborted or resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" upstream)" = 'fetch=https://github.com/acme/y.git push=https://github.com/acme/y.git' ] || fail "aliased ssh.github.com upstream left on SSH: $(effective "$R" upstream)"
rm -rf "$R"

# 39. ssh cannot answer: an alias-shaped host is undeterminable (abort), a
#     dotted literal host is taken literally (personal).
mkdir -p "$DIR/no-ssh"
printf '#!/usr/bin/env bash\nexit 255\n' > "$DIR/no-ssh/ssh"
chmod +x "$DIR/no-ssh/ssh"
R="$(mkrepo gh:acme/x.git)"
rc=0
(cd "$R" && PATH="$DIR/no-ssh:$PATH" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "unresolvable ssh alias did not abort"
grep -q "'gh'" "$DIR/err" || fail "unresolvable-alias abort did not name the host: $(cat "$DIR/err")"
rm -rf "$R"
R="$(mkrepo git@gitlab.com:me/x.git)"
out="$(cd "$R" && PATH="$DIR/no-ssh:$PATH" "$DIR/bot-env" 2>/dev/null)" || fail "dotted non-GitHub host aborted when ssh was unavailable"
echo "$out" | grep -q '^unset GH_TOKEN$' || fail "dotted non-GitHub host did not resolve personal when ssh was unavailable"
rm -rf "$R"

# 40. git's ssh is not the default ssh: the alias lives only in the config
#     core.sshCommand points at, and must be resolved through that command.
printf 'Host work\n  HostName github.com\n  User git\n' > "$HOME/.ssh/work_config"
R="$(mkrepo work:acme/x.git)"
[ "$(verdict "$R")" = PERSONAL ] || fail "alias known only to a non-default ssh config did not resolve personal without the override: $(verdict "$R")"
git -C "$R" config core.sshCommand "ssh -F $HOME/.ssh/work_config"
[ "$(verdict "$R")" = BOT ] || fail "alias resolved through core.sshCommand did not give the bot verdict: $(cat "$DIR/err")"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "core.sshCommand alias not rewritten: $(effective "$R" origin)"
git -C "$R" config --unset core.sshCommand
# 40b. GIT_SSH_COMMAND in the environment outranks core.sshCommand, and a
#      GIT_SSH program wrapper works the same way.
out="$(cd "$R" && GIT_SSH_COMMAND="ssh -F $HOME/.ssh/work_config" "$DIR/bot-env" 2>/dev/null)" || fail "GIT_SSH_COMMAND alias aborted"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "GIT_SSH_COMMAND alias did not give the bot verdict"
printf '#!/bin/sh\nexec ssh -F "%s" "$@"\n' "$HOME/.ssh/work_config" > "$DIR/myssh"
chmod +x "$DIR/myssh"
out="$(cd "$R" && GIT_SSH="$DIR/myssh" "$DIR/bot-env" 2>/dev/null)" || fail "GIT_SSH wrapper alias aborted"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "GIT_SSH wrapper alias did not give the bot verdict"
# 40c. core.sshCommand outranks GIT_SSH (git's connect.c order); only when it is unset does GIT_SSH decide.
printf 'Host work\n  HostName gitlab.com\n  User git\n' > "$HOME/.ssh/other_config"
printf '#!/bin/sh\nexec ssh -F "%s" "$@"\n' "$HOME/.ssh/other_config" > "$DIR/myssh-other"
chmod +x "$DIR/myssh-other"
git -C "$R" config core.sshCommand "ssh -F $HOME/.ssh/work_config"
out="$(cd "$R" && GIT_SSH="$DIR/myssh-other" "$DIR/bot-env" 2>/dev/null)" || fail "core.sshCommand with a disagreeing GIT_SSH aborted"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "GIT_SSH outranked core.sshCommand"
git -C "$R" config --unset core.sshCommand
out="$(cd "$R" && GIT_SSH="$DIR/myssh-other" "$DIR/bot-env" 2>/dev/null)" || fail "GIT_SSH alone aborted"
echo "$out" | grep -q '^unset GH_TOKEN$' || fail "GIT_SSH alone did not decide the destination"
rm -rf "$R"

# 41. An IPv6 literal is another host, never an alias-shaped abort.
R="$(mkrepo 'ssh://git@[::1]:2222/me/x.git')"
[ "$(verdict "$R")" = PERSONAL ] || fail "IPv6 literal remote did not resolve personal: $(cat "$DIR/err")"
rm -rf "$R"

# 42. A user http.extraHeader carrying Authorization for github.com
#     authenticates before the helper is consulted; refuse to route, name
#     the key, never the value, and do not mint.
HDR="$DIR/global-authz"
printf '[http "https://github.com/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$HDR" BOT_TOKEN_CALLS="$DIR/calls" "$DIR/bot-env" 2>"$DIR/err")" || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization extraHeader for github.com did not abort"
[ -z "$out" ] || fail "extraHeader abort still emitted env lines"
grep -q 'http.https://github.com/.extraheader' "$DIR/err" || fail "extraHeader abort did not name the key: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail "extraHeader abort printed the header value"
[ ! -e "$DIR/calls" ] || fail "a refused command still minted a token"
rm -rf "$R"

# 42b. A key that carries userinfo must not be echoed in the refusal.
HDRU="$DIR/global-authz-secret-key"
printf '[http "https://me:REDACTED@github.com/"]\n\textraHeader = Authorization: basic X\n' > "$HDRU"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDRU" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
# (the key's userinfo is part of the scope git matches against an
# https://me:...@github.com/ destination, so a bot verdict refuses it; the
# userinfo must never be printed)
[ "$rc" -ne 0 ] || fail "userinfo-scoped Authorization extraHeader did not abort"
grep -q 'http.https://\*\*\*@github.com/.extraheader' "$DIR/err" || fail "userinfo-scoped refusal did not name the masked key: $(cat "$DIR/err")"
! grep -q REDACTED "$DIR/err" || fail "extraHeader abort echoed userinfo from the key: $(cat "$DIR/err")"
rm -rf "$R"

# 43. A plain (host-less) http.extraHeader with Authorization also aborts.
HDR2="$DIR/global-authz-plain"
printf '[http]\n\textraHeader = Authorization: bearer REDACTED\n' > "$HDR2"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR2" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "plain Authorization extraHeader did not abort"
rm -rf "$R"

# 44. A rule more specific than the host (the shape a command-scope clear
#     cannot beat) aborts too.
HDR3="$DIR/global-authz-specific"
printf '[http "https://github.com/acme/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR3"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR3" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "account-specific Authorization extraHeader did not abort"
rm -rf "$R"

# 45. git keeps the URL subsection's case and matches hosts
#     case-insensitively, so a rule written for `GitHub.com` or with an
#     explicit :443 must abort too.
HDR4="$DIR/global-authz-mixedcase"
printf '[http "https://GitHub.com:443/"]\n\tExtraHeader = authorization: basic REDACTED\n' > "$HDR4"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR4" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "mixed-case GitHub.com:443 Authorization extraHeader did not abort"
rm -rf "$R"

# 45b. The bare host (no trailing slash) and a user@ form apply to every
#      github.com request, so they abort too.
HDR6="$DIR/global-authz-bare"
printf '[http "https://github.com"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR6"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR6" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "bare https://github.com Authorization extraHeader did not abort"
HDR7="$DIR/global-authz-userinfo"
printf '[http "https://me@github.com"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR7"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR7" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
# (a username-scoped key applies to an https://me@github.com/ destination, which any command may name)
[ "$rc" -ne 0 ] || fail "user@github.com-scoped Authorization extraHeader did not abort"
rm -rf "$R"

# 45c. A header written without a space after the colon is still Authorization.
HDR8="$DIR/global-authz-nospace"
printf '[http "https://github.com/"]\n\textraHeader = Authorization:basic REDACTED\n' > "$HDR8"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR8" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization:basic (no space) extraHeader did not abort"
rm -rf "$R"

# 46. A non-Authorization header, or an Authorization header for another
#     host, is not a competing credential.
HDR5="$DIR/global-benign"
printf '[http "https://github.com/"]\n\textraHeader = X-Trace: 1\n[http "https://gitlab.com/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR5"
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$HDR5" "$DIR/bot-env" 2>/dev/null)" || fail "benign extraHeaders aborted"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "benign extraHeaders did not resolve bot"
rm -rf "$R"

# 47. A ~/.netrc github.com entry: git's HTTP transport lets curl use it
#     before any helper runs. Refuse to route.
[ "$HOME" = "$DIR/home" ] || { echo "refusing: HOME is not the scratch dir"; exit 2; }
printf 'machine github.com login me password REDACTED\n' > "$HOME/.netrc"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail ".netrc github.com entry did not abort"
grep -q '\.netrc' "$DIR/err" || fail ".netrc abort did not name the file: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail ".netrc abort printed the entry"

# 48. Multi-line and `default` forms are entries too; another machine is not.
printf 'machine\n  github.com\n  login me\n  password REDACTED\n' > "$HOME/.netrc"
rc=0
(cd "$R" && "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "multi-line .netrc github.com entry did not abort"
printf 'default login me password REDACTED\n' > "$HOME/.netrc"
rc=0
(cd "$R" && "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail ".netrc default entry did not abort"
printf 'machine gitlab.com login me password REDACTED\n' > "$HOME/.netrc"
out="$(cd "$R" && "$DIR/bot-env" 2>/dev/null)" || fail ".netrc gitlab.com entry aborted"
echo "$out" | grep -q '^export GH_TOKEN=' || fail ".netrc gitlab.com entry did not resolve bot"
rm -f "$HOME/.netrc"
rm -rf "$R"

# 49. Personal verdicts never look at either: a competing credential is the
#     human's business in the human's repos.
printf 'machine github.com login me password REDACTED\n' > "$HOME/.netrc"
R="$(mkrepo git@gitlab.com:me/x.git)"
[ "$(verdict "$R")" = PERSONAL ] || fail "personal verdict was affected by .netrc"
rm -f "$HOME/.netrc"
rm -rf "$R"

# 50. A remote whose RAW value is not GitHub but which the user's own git
#     config rewrites onto GitHub SSH (`ghx:` -> `git@github.com:`) must be
#     caught by the effective-URL check too; before this fix only remotes
#     with a GitHub raw value were checked, and the push rode the personal key.
GIT_ALIAS="$DIR/global-git-alias"
printf '[url "git@github.com:"]\n\tinsteadOf = ghx:\n' > "$GIT_ALIAS"
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add upstream ghx:acme/y.git
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$GIT_ALIAS" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "git-insteadOf alias onto GitHub SSH on a second remote did not abort"
grep -q "'upstream'" "$DIR/err" || fail "git-alias abort did not name the remote: $(cat "$DIR/err")"
rm -rf "$R"

# 51. A malformed inherited GIT_CONFIG_COUNT gives the ambiguous bot verdict
#     (case 3) but must not blind the competing-credential check.
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR" GIT_CONFIG_COUNT=abc "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "malformed inherited GIT_CONFIG_COUNT blinded the extraHeader refusal"
rm -rf "$R"

# 52. ssh's `Match user` can make `git@work` resolve to github.com while a
#     bare `work` does not; the lookup must carry the URL's user as git does.
printf 'Match user git\n  HostName github.com\n' > "$HOME/.ssh/user_config"
R="$(mkrepo git@work:acme/x.git)"
git -C "$R" config core.sshCommand "ssh -F $HOME/.ssh/user_config"
[ "$(verdict "$R")" = BOT ] || fail "Match-user alias to github.com resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "Match-user alias remote not rewritten: $(effective "$R" origin)"
rm -rf "$R"

# 53. A wildcard-host scope git applies (`https://*.com/`) must be refused;
#     the handwritten host list could not see it.
HDR6="$DIR/global-authz-wildcard"
printf '[http "https://*.com/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HDR6"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HDR6" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "wildcard-host Authorization extraHeader did not abort"
grep -q 'REDACTED' "$DIR/err" && fail "wildcard abort printed the header value"
rm -rf "$R"

# 54. curl's netrc grammar: a quoted machine name is an entry; a login whose
#     value happens to be `default` is not; a `#` comment and a macdef body
#     are ignored.
[ "$HOME" = "$DIR/home" ] || { echo "refusing: HOME is not the scratch dir"; exit 2; }
R="$(mkrepo git@github.com:acme/x.git)"
printf 'machine "github.com" login me password REDACTED\n' > "$HOME/.netrc"
rc=0
(cd "$R" && "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "quoted .netrc github.com entry did not abort"
printf 'machine gitlab.com login default password REDACTED\n' > "$HOME/.netrc"
out="$(cd "$R" && "$DIR/bot-env" 2>/dev/null)" || fail "a login named default was treated as a default entry"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "login-named-default entry did not resolve bot"
printf '# machine github.com\nmacdef init\nmachine github.com\n\nmachine gitlab.com login me password REDACTED\n' > "$HOME/.netrc"
out="$(cd "$R" && "$DIR/bot-env" 2>/dev/null)" || fail "comment or macdef body was read as an entry"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "comment/macdef .netrc did not resolve bot"
rm -f "$HOME/.netrc"
rm -rf "$R"

# 55. An effective URL in scp form carries its userinfo before the host;
#     the abort message must mask it like the scheme form.
SCP_TIE="$DIR/global-scp-tie"
printf '[url "private-REDACTED@github.com:acme/x.git"]\n\tinsteadOf = https://github.com/acme/x.git\n' > "$SCP_TIE"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$SCP_TIE" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "scp-form tie did not abort"
grep -q '\*\*\*@github.com:acme/x.git' "$DIR/err" || fail "scp-form abort did not mask the userinfo: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail "scp-form abort printed the userinfo"
rm -rf "$R"

# 56. A user rule that rewrites a non-GitHub raw remote onto a credentialed
#     https github.com URL must be refused: git would use the URL's userinfo,
#     never the bot helper. The raw-remote exact pair cannot help here because
#     the raw value is not GitHub.
CRED_RULE="$DIR/global-cred-rule"
printf '[url "https://human:REDACTED@github.com/acme/x.git"]\n\tinsteadOf = mirror:acme/x.git\n' > "$CRED_RULE"
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add mirror mirror:acme/x.git
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$CRED_RULE" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "credentialed https rewrite of a non-GitHub remote did not abort"
grep -q "'mirror'" "$DIR/err" || fail "credentialed-https abort did not name the remote: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail "credentialed-https abort printed the credential"
# A raw credentialed remote is still routed through its exact pair, not refused.
R2="$(mkrepo 'https://REDACTED@github.com/acme/x.git')"
[ "$(verdict "$R2")" = BOT ] || fail "raw credentialed https remote no longer routes: $(cat "$DIR/err")"
[ "$(effective "$R2" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "raw credentialed https remote not rewritten to the clean target: $(effective "$R2" origin)"
rm -rf "$R" "$R2"

# 57. git passes an ssh:// URL's port to ssh as -p, and ssh config can turn
#     on it; the lookup must carry the port so the verdict matches git's ssh.
printf 'Match host work exec "test %%p = 443"\n  HostName github.com\n' > "$HOME/.ssh/port_config"
R="$(mkrepo ssh://git@work:443/acme/x.git)"
git -C "$R" config core.sshCommand "ssh -F $HOME/.ssh/port_config"
[ "$(verdict "$R")" = BOT ] || fail "port-conditional alias to github.com resolved personal: $(cat "$DIR/err")"
[ "$(effective "$R" origin)" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "port-conditional alias remote not rewritten: $(effective "$R" origin)"
git -C "$R" remote set-url origin ssh://git@work:22/acme/x.git
[ "$(verdict "$R")" = PERSONAL ] || fail "port-conditional alias matched on the wrong port"
rm -rf "$R"

# 58. An Authorization header scoped to a path that is reached only through
#     a user rewrite of a non-GitHub raw remote must still be refused.
REWRITE_HDR="$DIR/global-rewrite-hdr"
printf '[url "https://github.com/private/x.git"]\n\tinsteadOf = mirror:x.git\n[http "https://github.com/private/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$REWRITE_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add mirror mirror:x.git
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$REWRITE_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization header on a rewritten GitHub target was not refused"
grep -q 'REDACTED' "$DIR/err" && fail "rewritten-target refusal printed the header value"
rm -rf "$R"

# 59. A remote defined only in the global config is pushable by git but was
#     never in the effective-URL check; a complete-URL insteadOf tie on it
#     kept the personal SSH key under the bot's authorship. Affiliation stays
#     local-only (no local remotes here → ambiguous bot verdict).
GLOBAL_REMOTE="$DIR/global-remote-tie"
printf '[remote "corp"]\n\turl = https://github.com/acme/corp.git\n[url "ssh://git@github.com/acme/corp.git"]\n\tinsteadOf = https://github.com/acme/corp.git\n' > "$GLOBAL_REMOTE"
R="$(mkrepo)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$GLOBAL_REMOTE" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "global remote left on SSH by a tie did not abort"
grep -q "remote 'corp' still resolves to" "$DIR/err" || fail "global-remote abort was not the still-resolves refusal naming the remote: $(cat "$DIR/err")"
# Without the tie the same global remote routes to HTTPS and the command runs.
printf '[remote "corp"]\n\turl = https://github.com/acme/corp.git\n' > "$GLOBAL_REMOTE"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$GLOBAL_REMOTE" "$DIR/bot-env" 2>"$DIR/err")" || fail "global remote without a tie aborted: $(cat "$DIR/err")"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "global remote without a tie did not keep the bot verdict"
rm -rf "$R"

# 60. A global remote section with no url or pushurl (prune = true) has no
#     destination; it must neither abort bot-env nor disturb a local origin.
URLLESS="$DIR/global-urlless"
printf '[remote "origin"]\n\tprune = true\n' > "$URLLESS"
R="$(mkrepo)"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$URLLESS" "$DIR/bot-env" 2>"$DIR/err")" || fail "URL-less global remote section aborted: $(cat "$DIR/err")"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "URL-less global remote section lost the bot verdict"
rm -rf "$R"
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$URLLESS" "$DIR/bot-env" 2>"$DIR/err")" || fail "URL-less global section beside a local origin aborted: $(cat "$DIR/err")"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "URL-less global section beside a local origin lost the bot verdict"
[ "$(effective "$R" origin "$URLLESS")" = 'fetch=https://github.com/acme/x.git push=https://github.com/acme/x.git' ] || fail "local origin not rewritten beside a URL-less global section: $(effective "$R" origin "$URLLESS")"
rm -rf "$R"

# 61. An Authorization header scoped to another account's path applies to
#     an ad-hoc `git push https://github.com/other/x.git`, so it is refused
#     although no remote of this repository targets that path.
OTHER_HDR="$DIR/global-authz-other-org"
printf '[http "https://github.com/other/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$OTHER_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$OTHER_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization header scoped to another github.com path did not abort"
grep -q 'http.https://github.com/other/.extraheader' "$DIR/err" || fail "other-path refusal did not name the key: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail "other-path refusal printed the header value"
rm -rf "$R"

# 61b. A scope path containing `=` is still tested (git -c would split it).
EQ_HDR="$DIR/global-authz-equals"
printf '[http "https://github.com/acme/x=y/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$EQ_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$EQ_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization header scoped to a path containing '=' did not abort"
grep -q 'REDACTED' "$DIR/err" && fail "equals-path refusal printed the header value"
rm -rf "$R"

# 61c. Negative control: an Authorization header for a non-GitHub host never
#      applies to github.com, whatever its path.
EX_HDR="$DIR/global-authz-example"
printf '[http "https://example.com/"]\n\textraHeader = Authorization: basic REDACTED\n[http "https://example.com/acme/x=y/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$EX_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$EX_HDR" "$DIR/bot-env" 2>"$DIR/err")" || fail "non-GitHub Authorization header aborted: $(cat "$DIR/err")"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "non-GitHub Authorization header lost the bot verdict"
rm -rf "$R"

# 61d. An inherited GIT_CONFIG_COUNT/KEY/VALUE must not change the probe:
#      it neither hides a refused scope nor invents one.
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_COUNT=3 GIT_CONFIG_KEY_0=http.https://github.com/other/.botenvprobe GIT_CONFIG_VALUE_0=no GIT_CONFIG_GLOBAL="$OTHER_HDR" "$DIR/bot-env" >/dev/null 2>&1) || rc=$?
[ "$rc" -ne 0 ] || fail "an inherited GIT_CONFIG_COUNT hid a refused Authorization scope"
out="$(cd "$R" && GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.https://github.com/.botenvprobe GIT_CONFIG_VALUE_0=yes GIT_CONFIG_GLOBAL="$EX_HDR" "$DIR/bot-env" 2>"$DIR/err")" || fail "an inherited probe-named GIT_CONFIG entry invented a refusal: $(cat "$DIR/err")"
rm -rf "$R"

# 61e. An inherited GIT_CONFIG_PARAMETERS (what `git -c` leaves behind) must
#      not stop the refusal either.
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_PARAMETERS="'http.https://github.com/other/.botenvprobe'='no'" GIT_CONFIG_GLOBAL="$OTHER_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "an inherited GIT_CONFIG_PARAMETERS hid a refused Authorization scope"
rm -rf "$R"

# 61f. A password containing '@' in a scope's userinfo is masked whole.
AT_HDR="$DIR/global-authz-at-password"
printf '[http "https://me:p@ss@github.com/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$AT_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$AT_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "userinfo-with-@ Authorization scope did not abort"
grep -q 'http.https://\*\*\*@github.com/.extraheader' "$DIR/err" || fail "userinfo-with-@ refusal did not mask the whole userinfo: $(cat "$DIR/err")"
grep -q 'p@ss\|ss@\|me:\|REDACTED' "$DIR/err" && fail "userinfo-with-@ refusal leaked a userinfo fragment or the value: $(cat "$DIR/err")"
rm -rf "$R"

# 61g. A scope git cannot evaluate (--get-urlmatch exits 128 on %zz) is
#      refused, not passed, and the message says how to fix it.
BAD_HDR="$DIR/global-authz-badscope"
printf '[http "https://github.com/%%zz/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$BAD_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$BAD_HDR" "$DIR/bot-env" 2>"$DIR/err")" || rc=$?
[ "$rc" -ne 0 ] || fail "a scope git cannot evaluate did not abort"
[ -z "$out" ] || fail "probe-error abort still emitted env lines"
grep -q 'could not test' "$DIR/err" || fail "probe-error abort was not the could-not-test refusal: $(cat "$DIR/err")"
grep -q 'remove or correct' "$DIR/err" || fail "probe-error refusal did not say how to fix it: $(cat "$DIR/err")"
grep -q 'REDACTED' "$DIR/err" && fail "probe-error refusal printed the header value"
rm -rf "$R"

# 61h. An http:// scope applies to an ad-hoc `git push http://github.com/...`
#      (no rewrite moves it to https), so the probe keeps the scheme.
HTTP_HDR="$DIR/global-authz-http"
printf '[http "http://github.com/other/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$HTTP_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$HTTP_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization header on an http:// github.com scope did not abort"
grep -q 'http.http://github.com/other/.extraheader' "$DIR/err" || fail "http-scope refusal did not name the key: $(cat "$DIR/err")"
rm -rf "$R"

# 61i. A scope with an explicit non-default port applies to a URL naming that
#      port, so the probe keeps the port.
PORT_HDR="$DIR/global-authz-port"
printf '[http "https://github.com:8443/other/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$PORT_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
rc=0
(cd "$R" && GIT_CONFIG_GLOBAL="$PORT_HDR" "$DIR/bot-env" >/dev/null 2>"$DIR/err") || rc=$?
[ "$rc" -ne 0 ] || fail "Authorization header on an explicit-port github.com scope did not abort"
rm -rf "$R"

# 61j. Negative control: keeping the scheme and port does not turn a
#      non-GitHub host into a refusal.
EXP_HDR="$DIR/global-authz-example-port"
printf '[http "http://example.com:8443/other/"]\n\textraHeader = Authorization: basic REDACTED\n' > "$EXP_HDR"
R="$(mkrepo git@github.com:acme/x.git)"
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$EXP_HDR" "$DIR/bot-env" 2>"$DIR/err")" || fail "non-GitHub http/port Authorization header aborted: $(cat "$DIR/err")"
echo "$out" | grep -q '^export GH_TOKEN=' || fail "non-GitHub http/port Authorization header lost the bot verdict"
rm -rf "$R"

[ "$FAIL" -eq 0 ] && echo "routing-test: PASS"
exit "$FAIL"
