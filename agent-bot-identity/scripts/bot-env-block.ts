/**
 * The bot-env output contract, shared by the agent-bot-identity adapters
 * that parse bot-env's emitted shell (OpenCode, pi). Runtime-neutral: no
 * Bun or Node process APIs, so each adapter keeps only its own spawning.
 *
 * Installed flat beside the adapters (~/.config/<bot>/bin/bot-env-block.ts);
 * in the repo each adapter directory carries a symlink to this file so the
 * same `./bot-env-block` import resolves in both layouts.
 */

export class BotEnvError extends Error {}

// bot-env ends every successful emission, bot or personal, with this line,
// so a truncated block is refused instead of routed partially.
export const END_LINE = "# bot-env: end"

// The host-wide rewrites bot-env emits as both insteadOf and pushInsteadOf.
// The rule they implement lives in SKILL.md Phase 4 (adapter contract); this
// list only names what bot-env emits for it.
export const HOST_WIDE_REWRITE_SOURCES: readonly string[] = [
  "git@github.com:",
  "github.com:",
  "ssh://git@github.com/",
  "https://github.com/",
  "ssh://git@ssh.github.com:443/",
  "git@ssh.github.com:",
  "ssh.github.com:",
]

export type BotEnvBlock = { exports: Record<string, string>; unsets: string[] }

// bot-env's line shapes besides END_LINE:
//   export KEY='value'   single-quoted; bot-env refuses values containing a quote
//   export KEY=value     unquoted scalars, e.g. GIT_CONFIG_COUNT=6
//   unset KEY [KEY ...]
const EXPORT_QUOTED = /^export ([A-Z_][A-Z0-9_]*)='([^']*)'$/
const EXPORT_BARE = /^export ([A-Z_][A-Z0-9_]*)=(\S+)$/
const UNSET = /^unset ([A-Z_][A-Z0-9_]*(?: [A-Z_][A-Z0-9_]*)*)$/
// Names a line for an error message without its value.
const LINE_HEAD = /^(export|unset) ([A-Z_][A-Z0-9_]*)/

// A bot verdict's identity block must carry all of these, plus the counted
// GIT_CONFIG_KEY_i/VALUE_i pairs. GIT_CONFIG_PARAMETERS is expected to be empty.
const REQUIRED_IDENTITY = [
  "GIT_AUTHOR_NAME",
  "GIT_AUTHOR_EMAIL",
  "GIT_COMMITTER_NAME",
  "GIT_COMMITTER_EMAIL",
  "GIT_CONFIG_COUNT",
  "GH_TOKEN",
  "GIT_CONFIG_PARAMETERS",
]

const identityExport = (name: string): boolean =>
  REQUIRED_IDENTITY.includes(name) || name === "BOT_INSTALL_ID" || /^GIT_CONFIG_(KEY|VALUE)_[0-9]+$/.test(name)

export function parseBotEnvBlock(stdout: string, cwd: string): BotEnvBlock {
  const lines = stdout.split("\n").filter((line) => line !== "")
  if (lines.length === 0) {
    throw new BotEnvError(`agent-bot-identity: bot-env emitted no output in ${cwd}; refusing to continue with undetermined identity`)
  }
  if (lines[lines.length - 1] !== END_LINE) {
    throw new BotEnvError(
      `agent-bot-identity: bot-env output in ${cwd} does not end with "${END_LINE}" (truncated, or a bot-env older than this adapter); refusing to continue with undetermined identity`,
    )
  }

  // Parse into a local map and validate the whole block before returning, so
  // a caller never merges part of a block.
  const exports: Record<string, string> = {}
  const unsets: string[] = []
  lines.slice(0, -1).forEach((line, i) => {
    let match = EXPORT_QUOTED.exec(line) ?? EXPORT_BARE.exec(line)
    if (match) {
      exports[match[1]] = match[2]
      return
    }
    match = UNSET.exec(line)
    if (match) {
      unsets.push(...match[1].split(" "))
      return
    }
    const head = LINE_HEAD.exec(line)
    const what = head ? `${head[1]} ${head[2]}` : "not an export or unset line"
    throw new BotEnvError(`agent-bot-identity: bot-env emitted an unrecognized line ${i + 1} in ${cwd} (${what}); refusing to route`)
  })

  // Exports are applied first and unsets after, so a name in both would be
  // deleted despite being exported. bot-env never emits that; refuse it.
  const conflicts = [...new Set(unsets)].filter((name) => name in exports)
  if (conflicts.length > 0) {
    throw new BotEnvError(
      `agent-bot-identity: bot-env emitted a variable both exported and unset in ${cwd} (${conflicts.join(", ")}); refusing to route`,
    )
  }

  // Contract check: bot-env emits the identity block only whole, in a fixed
  // shape: author and committer identity, a non-empty GH_TOKEN (its
  // fail-closed sentinel included), an empty GIT_CONFIG_PARAMETERS (git
  // applies a non-empty one after the counted entries, so it could override
  // the helper), exactly GIT_CONFIG_COUNT key/value pairs starting with the
  // helper reset (0), the bot credential helper (1) and commit.gpgsign=false
  // (2), and every host-wide rewrite as both insteadOf and pushInsteadOf.
  // Entries at or beyond the count would be ignored by git, so they are
  // refused too. Unset-only (personal) blocks skip this; their completeness
  // is the END_LINE check above.
  if (Object.keys(exports).some(identityExport)) {
    const problems = REQUIRED_IDENTITY.filter((name) => !(name in exports))
    if (exports.GH_TOKEN === "") problems.push("non-empty GH_TOKEN")
    if ("GIT_CONFIG_PARAMETERS" in exports && exports.GIT_CONFIG_PARAMETERS !== "") problems.push("empty GIT_CONFIG_PARAMETERS")
    if ("GIT_CONFIG_COUNT" in exports) {
      const keyCount = Object.keys(exports).filter((name) => /^GIT_CONFIG_KEY_[0-9]+$/.test(name)).length
      const count = /^[0-9]+$/.test(exports.GIT_CONFIG_COUNT) ? Number(exports.GIT_CONFIG_COUNT) : NaN
      if (Number.isNaN(count) || count < 3 || count > keyCount) {
        problems.push("GIT_CONFIG_COUNT between 3 and the number of GIT_CONFIG_KEY_n exports")
      } else {
        for (let i = 0; i < count; i++) {
          for (const name of [`GIT_CONFIG_KEY_${i}`, `GIT_CONFIG_VALUE_${i}`]) if (!(name in exports)) problems.push(name)
        }
        for (const name of Object.keys(exports)) {
          const m = /^GIT_CONFIG_(?:KEY|VALUE)_([0-9]+)$/.exec(name)
          if (m && Number(m[1]) >= count) problems.push(`${name} beyond GIT_CONFIG_COUNT`)
        }
        if (exports.GIT_CONFIG_KEY_0 !== "credential.helper" || exports.GIT_CONFIG_VALUE_0 !== "") {
          problems.push("helper reset at GIT_CONFIG index 0")
        }
        // bot-env emits `!<install dir>/git-credential-bot` and refuses an
        // install path outside this character set; any other `!` helper
        // (`!true`) returns nothing and lets git fall through to a prompt.
        if (
          exports.GIT_CONFIG_KEY_1 !== "credential.helper" ||
          !/^!\/[A-Za-z0-9._\/-]*\/git-credential-bot$/.test(exports.GIT_CONFIG_VALUE_1 ?? "")
        ) {
          problems.push("bot credential helper at GIT_CONFIG index 1")
        }
        if (exports.GIT_CONFIG_KEY_2 !== "commit.gpgsign" || exports.GIT_CONFIG_VALUE_2 !== "false") {
          problems.push("commit.gpgsign=false at GIT_CONFIG index 2")
        }
        const counted = (key: string, value: string): boolean => {
          for (let i = 0; i < count; i++) {
            if (exports[`GIT_CONFIG_KEY_${i}`] === key && exports[`GIT_CONFIG_VALUE_${i}`] === value) return true
          }
          return false
        }
        for (const source of HOST_WIDE_REWRITE_SOURCES) {
          if (!counted("url.https://github.com/.insteadOf", source) || !counted("url.https://github.com/.pushInsteadOf", source)) {
            problems.push(`host-wide insteadOf and pushInsteadOf for ${source}`)
          }
        }
      }
    }
    if (problems.length > 0) {
      throw new BotEnvError(
        `agent-bot-identity: bot-env emitted a partial identity block in ${cwd} (problems: ${problems.join(", ")}); refusing to route`,
      )
    }
  }

  return { exports, unsets }
}
