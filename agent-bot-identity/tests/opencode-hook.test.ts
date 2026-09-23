import { afterAll, describe, expect, test } from "bun:test"
import { mkdtempSync, rmSync, writeFileSync, chmodSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"

import AgentBotIdentity from "../scripts/opencode/agent-bot-identity"

// Fixture bot-env scripts are written to disk and passed via the `botEnv`
// plugin option, so these tests exercise the real spawn + parse path without
// needing an installed agent-bot-identity setup.
//
// Run with `bun test tests/opencode-hook.test.ts`. Without a bun install, the
// bun embedded in the opencode binary runs it:
//   BUN_BE_BUN=1 opencode test tests/opencode-hook.test.ts

const root = mkdtempSync(join(tmpdir(), "agent-bot-identity-test-"))
afterAll(() => rmSync(root, { recursive: true, force: true }))

function fixture(name: string, body: string, executable = true): string {
  const path = join(root, name)
  writeFileSync(path, body)
  chmodSync(path, executable ? 0o755 : 0o644)
  return path
}

function gitRepo(name: string, remote?: string): string {
  const dir = mkdtempSync(join(root, `${name}-`))
  Bun.spawnSync(["git", "init", "-q", "."], { cwd: dir })
  if (remote) Bun.spawnSync(["git", "remote", "add", "origin", remote], { cwd: dir })
  return dir
}

const hooksOf = async (botEnv: string) => {
  const client = { app: { log: async () => ({}) } }
  const plugin = AgentBotIdentity as (input: unknown, options?: unknown) => Promise<Record<string, unknown>>
  const hooks = (await plugin({ client } as never, { botEnv })) as {
    "shell.env": (input: { cwd: string; sessionID?: string; callID?: string }, output: { env: Record<string, string> }) => Promise<void>
  }
  return hooks["shell.env"]
}

const call = async (botEnv: string, cwd: string, ids: { sessionID?: string; callID?: string } = { sessionID: "s", callID: "c" }) => {
  const hook = await hooksOf(botEnv)
  const output = { env: {} as Record<string, string> }
  await hook({ cwd, ...ids }, output)
  return output.env
}

// The shape bot-env emits for a bot verdict since the transport-routing fix
// (PR #180): helper reset + bot helper, gpgsign off, the four host-wide
// insteadOf/pushInsteadOf pairs, the account identity pair, and one exact pair
// per raw remote value seen in the repo.
const BOT_BLOCK = `#!/usr/bin/env bash
cat <<'OUT'
export GIT_AUTHOR_NAME='acme-agent[bot]'
export GIT_AUTHOR_EMAIL='123+acme-agent[bot]@users.noreply.github.com'
export GIT_COMMITTER_NAME='acme-agent[bot]'
export GIT_COMMITTER_EMAIL='123+acme-agent[bot]@users.noreply.github.com'
export GIT_CONFIG_KEY_0='credential.helper'
export GIT_CONFIG_VALUE_0=''
export GIT_CONFIG_KEY_1='credential.helper'
export GIT_CONFIG_VALUE_1='!/home/u/bin/git-credential-bot'
export GIT_CONFIG_KEY_2='commit.gpgsign'
export GIT_CONFIG_VALUE_2='false'
export GIT_CONFIG_KEY_3='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_3='git@github.com:'
export GIT_CONFIG_KEY_4='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_4='git@github.com:'
export GIT_CONFIG_KEY_5='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_5='github.com:'
export GIT_CONFIG_KEY_6='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_6='github.com:'
export GIT_CONFIG_KEY_7='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_7='ssh://git@github.com/'
export GIT_CONFIG_KEY_8='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_8='ssh://git@github.com/'
export GIT_CONFIG_KEY_9='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_9='https://github.com/'
export GIT_CONFIG_KEY_10='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_10='https://github.com/'
export GIT_CONFIG_KEY_11='url.https://github.com/acme/.insteadOf'
export GIT_CONFIG_VALUE_11='https://github.com/acme/'
export GIT_CONFIG_KEY_12='url.https://github.com/acme/.pushInsteadOf'
export GIT_CONFIG_VALUE_12='https://github.com/acme/'
export GIT_CONFIG_KEY_13='url.https://github.com/acme/repo.git.insteadOf'
export GIT_CONFIG_VALUE_13='git@github.com:acme/repo.git'
export GIT_CONFIG_KEY_14='url.https://github.com/acme/repo.git.pushInsteadOf'
export GIT_CONFIG_VALUE_14='git@github.com:acme/repo.git'
export BOT_INSTALL_ID='42'
export GIT_CONFIG_COUNT=15
export GH_TOKEN='ghs_fixture'
OUT
`

// The env a fixture's `export` lines describe, read independently of the
// plugin's parser so a full-equality assertion can catch what spot checks miss.
function expectedEnv(fixture: string): Record<string, string> {
  const env: Record<string, string> = {}
  for (const line of fixture.split("\n")) {
    const m = /^export ([A-Z_][A-Z0-9_]*)=(?:'([^']*)'|(\S+))$/.exec(line)
    if (m) env[m[1]] = m[2] ?? m[3]
  }
  return env
}

const PERSONAL_BLOCK = `#!/usr/bin/env bash
cat <<'OUT'
unset GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL
unset GIT_CONFIG_COUNT
unset GH_TOKEN
unset BOT_INSTALL_ID
OUT
`

describe("shell.env hook", () => {
  test("bot verdict: maps the full identity block into the env", async () => {
    const botEnv = fixture("bot-ok", BOT_BLOCK)
    const env = await call(botEnv, gitRepo("org", "git@github.com:acme/repo.git"))
    expect(env.GIT_AUTHOR_NAME).toBe("acme-agent[bot]")
    expect(env.GIT_AUTHOR_EMAIL).toBe("123+acme-agent[bot]@users.noreply.github.com")
    expect(env.GH_TOKEN).toBe("ghs_fixture")
    expect(env.BOT_INSTALL_ID).toBe("42")
    expect(env.GIT_CONFIG_VALUE_0).toBe("") // quoted empty survives
    expect(env.GIT_CONFIG_KEY_4).toBe("url.https://github.com/.pushInsteadOf") // push twin of a host-wide pair survives
    expect(env.GIT_CONFIG_VALUE_14).toBe("git@github.com:acme/repo.git") // exact per-remote pair survives
    expect(env.GIT_CONFIG_COUNT).toBe("15") // bare scalar survives
    // The whole block round-trips: nothing dropped, added, renamed or shifted.
    expect(env).toEqual(expectedEnv(BOT_BLOCK))
    // And the fixture itself is coherent the way real bot-env output is: one
    // key/value pair per index below GIT_CONFIG_COUNT, no gaps.
    const count = Number(env.GIT_CONFIG_COUNT)
    for (let i = 0; i < count; i++) {
      expect(env[`GIT_CONFIG_KEY_${i}`]).toBeDefined()
      expect(env[`GIT_CONFIG_VALUE_${i}`]).toBeDefined()
    }
    expect(Object.keys(env).filter((k) => k.startsWith("GIT_CONFIG_KEY_")).length).toBe(count)
  })

  test("personal verdict: no bot vars in the env", async () => {
    const botEnv = fixture("bot-personal", PERSONAL_BLOCK)
    const env = await call(botEnv, gitRepo("personal", "git@gitlab.com:someone/repo.git"))
    expect(env).toEqual({})
  })

  test("PTY spawn (no session/call id): stays personal even on a bot verdict", async () => {
    const botEnv = fixture("bot-pty", BOT_BLOCK)
    expect(await call(botEnv, gitRepo("pty", "git@github.com:acme/repo.git"), {})).toEqual({})
    expect(await call(botEnv, gitRepo("pty2", "git@github.com:acme/repo.git"), { sessionID: "s" })).toEqual({})
    expect(await call(botEnv, gitRepo("pty3", "git@github.com:acme/repo.git"), { callID: "c" })).toEqual({})
  })

  test("fail closed: bot-env exits non-zero", async () => {
    const botEnv = fixture("bot-crash", `#!/usr/bin/env bash\necho "broken" >&2\nexit 1\n`)
    await expect(call(botEnv, gitRepo("crash"))).rejects.toThrow(/bot-env exited 1/)
  })

  test("fail closed: bot-env spawns no output", async () => {
    const botEnv = fixture("bot-empty", `#!/usr/bin/env bash\nexit 0\n`)
    await expect(call(botEnv, gitRepo("empty"))).rejects.toThrow(/no output/)
  })

  test("fail closed: unrecognized output line", async () => {
    const botEnv = fixture("bot-garbage", `#!/usr/bin/env bash\necho 'GIT_AUTHOR_NAME=evil'\n`)
    await expect(call(botEnv, gitRepo("garbage"))).rejects.toThrow(/unrecognized line/)
  })

  test("fail closed: identity block without GH_TOKEN", async () => {
    const botEnv = fixture(
      "bot-partial",
      `#!/usr/bin/env bash\nprintf '%s\\n' "export GIT_AUTHOR_NAME='acme-agent[bot]'"\n`,
    )
    await expect(call(botEnv, gitRepo("partial"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: bot-env not executable", async () => {
    const botEnv = fixture("bot-noexec", BOT_BLOCK, false)
    await expect(call(botEnv, gitRepo("noexec"))).rejects.toThrow()
  })

  test("fail closed: DEFAULT_BOT_ENV placeholder left as REPLACE", async () => {
    const client = { app: { log: async () => ({}) } }
    const hooks = (await (AgentBotIdentity as (i: unknown) => Promise<Record<string, never>>)({ client } as never)) as {
      "shell.env": (i: { cwd: string; sessionID: string; callID: string }, o: { env: Record<string, string> }) => Promise<void>
    }
    await expect(
      hooks["shell.env"]({ cwd: gitRepo("replace"), sessionID: "s", callID: "c" }, { env: {} }),
    ).rejects.toThrow(/DEFAULT_BOT_ENV/)
  })
})

// Optional integration case against a real install: run with
//   BOT_ENV=<installed bot-env> BOT_ENV_CWD=<org repo> bun test
const realBotEnv = process.env.BOT_ENV
const realCwd = process.env.BOT_ENV_CWD
const integration = realBotEnv && realCwd ? describe : describe.skip
integration("integration: installed bot-env", () => {
  test("org repo verdict carries a live token", async () => {
    const env = await call(realBotEnv as string, realCwd as string)
    expect(env.GIT_AUTHOR_NAME).toEndWith("[bot]")
    expect(env.GH_TOKEN).toStartWith("ghs_")
    expect(Number(env.GIT_CONFIG_COUNT)).toBeGreaterThanOrEqual(15)
  })
})
