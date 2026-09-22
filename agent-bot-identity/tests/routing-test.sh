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

cp "$SRC/git-credential-bot" "$DIR/"
awk '{ if ($0 == "acme:REPLACE") print "acme:111"; else print }' "$SRC/bot-env" > "$DIR/bot-env"
printf '#!/usr/bin/env bash\necho "ghs_stub-${BOT_INSTALL_ID:-none}"\n' > "$DIR/bot-token"
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

# 15. Every emitted line must still match the three shapes the OpenCode
#     plugin parses (export KEY='...', export KEY=bare, unset KEY ...).
R="$(mkrepo git@github.com:acme/x.git)"
git -C "$R" remote add upstream SSH://git@GITHUB.COM/oss-project/x.git
bad="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | grep -Ev "^export [A-Z_][A-Z0-9_]*='[^']*'$|^export [A-Z_][A-Z0-9_]*=[^ ]+$|^unset [A-Z_][A-Z0-9_]*( [A-Z_][A-Z0-9_]*)*$" || true)"
[ -z "$bad" ] || fail "bot-env emitted a line the adapters cannot parse: $bad"
count="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | sed -n 's/^export GIT_CONFIG_COUNT=//p')"
keys="$(cd "$R" && "$DIR/bot-env" 2>/dev/null | grep -c '^export GIT_CONFIG_KEY_')"
[ "$count" = "$keys" ] || fail "GIT_CONFIG_COUNT=$count but $keys keys were emitted"
rm -rf "$R"

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
printf '[url "ssh://git@github.com/acme/x.git"]\n\tinsteadOf = https://github.com/acme/x.git\n' > "$FULL_URL_RULE"
R="$(mkrepo https://github.com/acme/x.git)"
rc=0
out="$(cd "$R" && GIT_CONFIG_GLOBAL="$FULL_URL_RULE" "$DIR/bot-env" 2>"$DIR/err")" || rc=$?
[ "$rc" -ne 0 ] || fail "remote still resolving to SSH after the rewrites did not abort"
[ -z "$out" ] || fail "SSH-resolving remote abort still emitted env lines"
grep -q 'origin' "$DIR/err" && grep -q 'ssh://git@github.com/acme/x.git' "$DIR/err" || fail "SSH-resolving remote abort did not name the remote and its effective URL: $(cat "$DIR/err")"
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

[ "$FAIL" -eq 0 ] && echo "routing-test: PASS"
exit "$FAIL"
