// Raw bot-env stdout shapes shared by the OpenCode, pi, and parser suites.
// BOT_OUTPUT is the shape bot-env emits for a bot verdict since the
// transport-routing fix (PR #180): helper reset + bot helper, gpgsign off,
// the seven host-wide insteadOf/pushInsteadOf pairs, the account pair, one
// exact pair per raw remote value, and the completeness line.

const hostWide = [
  "git@github.com:",
  "github.com:",
  "ssh://git@github.com/",
  "https://github.com/",
  "ssh://git@ssh.github.com:443/",
  "git@ssh.github.com:",
  "ssh.github.com:",
]

const pairs: [string, string][] = [
  ...hostWide.map((v): [string, string] => ["https://github.com/", v]),
  ["https://github.com/acme/", "https://github.com/acme/"],
  ["https://github.com/acme/repo.git", "git@github.com:acme/repo.git"],
]

const configLines: string[] = []
pairs.forEach(([base, value], i) => {
  const idx = 3 + 2 * i
  configLines.push(
    `export GIT_CONFIG_KEY_${idx}='url.${base}.insteadOf'`,
    `export GIT_CONFIG_VALUE_${idx}='${value}'`,
    `export GIT_CONFIG_KEY_${idx + 1}='url.${base}.pushInsteadOf'`,
    `export GIT_CONFIG_VALUE_${idx + 1}='${value}'`,
  )
})

export const BOT_OUTPUT = [
  "export GIT_AUTHOR_NAME='acme-agent[bot]'",
  "export GIT_AUTHOR_EMAIL='123+acme-agent[bot]@users.noreply.github.com'",
  "export GIT_COMMITTER_NAME='acme-agent[bot]'",
  "export GIT_COMMITTER_EMAIL='123+acme-agent[bot]@users.noreply.github.com'",
  "export GIT_CONFIG_PARAMETERS=''",
  "export GIT_CONFIG_KEY_0='credential.helper'",
  "export GIT_CONFIG_VALUE_0=''",
  "export GIT_CONFIG_KEY_1='credential.helper'",
  "export GIT_CONFIG_VALUE_1='!/home/u/bin/git-credential-bot'",
  "export GIT_CONFIG_KEY_2='commit.gpgsign'",
  "export GIT_CONFIG_VALUE_2='false'",
  ...configLines,
  "export BOT_INSTALL_ID='42'",
  `export GIT_CONFIG_COUNT=${3 + 2 * pairs.length}`,
  "export GH_TOKEN='ghs_fixture'",
  "# bot-env: end",
  "",
].join("\n")

export const PERSONAL_OUTPUT = [
  "unset GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL",
  "unset GIT_CONFIG_COUNT",
  "unset GH_TOKEN",
  "unset BOT_INSTALL_ID",
  "unset GIT_CONFIG_PARAMETERS",
  "# bot-env: end",
  "",
].join("\n")

// A bash script that prints `output` verbatim (quoted heredoc: no expansion).
export const script = (output: string): string => `#!/usr/bin/env bash\ncat <<'OUT'\n${output}OUT\n`
