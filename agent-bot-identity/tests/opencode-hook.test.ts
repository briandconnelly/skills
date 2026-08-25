import { afterAll, describe, expect, test } from "bun:test"
import { mkdtempSync, rmSync, writeFileSync, chmodSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"

import AgentBotIdentity from "../scripts/opencode/agent-bot-identity"

// Fixture bot-env scripts are written to disk and passed via the `botEnv`
// plugin option, so these tests exercise the real spawn + parse path without
// needing an installed agent-bot-identity setup.

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
export GIT_CONFIG_KEY_2='url.https://github.com/acme/.insteadOf'
export GIT_CONFIG_VALUE_2='git@github.com:acme/'
export GIT_CONFIG_KEY_3='commit.gpgsign'
export GIT_CONFIG_VALUE_3='false'
export BOT_INSTALL_ID='42'
export GIT_CONFIG_COUNT=4
export GH_TOKEN='ghs_fixture'
OUT
`

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
    expect(env.GIT_CONFIG_KEY_2).toBe("url.https://github.com/acme/.insteadOf") // url rewrite pair survives
    expect(env.GIT_CONFIG_VALUE_2).toBe("git@github.com:acme/")
    expect(env.GIT_CONFIG_COUNT).toBe("4") // bare scalar survives
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
    expect(Number(env.GIT_CONFIG_COUNT)).toBeGreaterThan(3)
  })
})
