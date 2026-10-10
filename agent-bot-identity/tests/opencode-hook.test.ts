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

const hooksOf = async (botEnv: string, extra: Record<string, unknown> = {}) => {
  const client = { app: { log: async () => ({}) } }
  const plugin = AgentBotIdentity as (input: unknown, options?: unknown) => Promise<Record<string, unknown>>
  const hooks = (await plugin({ client } as never, { botEnv, ...extra })) as {
    "shell.env": (input: { cwd: string; sessionID?: string; callID?: string }, output: { env: Record<string, string> }) => Promise<void>
  }
  return hooks["shell.env"]
}

const call = async (
  botEnv: string,
  cwd: string,
  ids: { sessionID?: string; callID?: string } = { sessionID: "s", callID: "c" },
  extra: Record<string, unknown> = {},
) => {
  const hook = await hooksOf(botEnv, extra)
  const output = { env: {} as Record<string, string> }
  await hook({ cwd, ...ids }, output)
  return output.env
}

// The shape bot-env emits for a bot verdict since the transport-routing fix
// (PR #180): helper reset + bot helper, gpgsign off, the seven host-wide
// insteadOf/pushInsteadOf pairs, the account identity pair, and one exact pair
// per raw remote value seen in the repo.
const BOT_BLOCK = `#!/usr/bin/env bash
cat <<'OUT'
export GIT_AUTHOR_NAME='acme-agent[bot]'
export GIT_AUTHOR_EMAIL='123+acme-agent[bot]@users.noreply.github.com'
export GIT_COMMITTER_NAME='acme-agent[bot]'
export GIT_COMMITTER_EMAIL='123+acme-agent[bot]@users.noreply.github.com'
export GIT_CONFIG_PARAMETERS=''
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
export GIT_CONFIG_KEY_11='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_11='ssh://git@ssh.github.com:443/'
export GIT_CONFIG_KEY_12='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_12='ssh://git@ssh.github.com:443/'
export GIT_CONFIG_KEY_13='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_13='git@ssh.github.com:'
export GIT_CONFIG_KEY_14='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_14='git@ssh.github.com:'
export GIT_CONFIG_KEY_15='url.https://github.com/.insteadOf'
export GIT_CONFIG_VALUE_15='ssh.github.com:'
export GIT_CONFIG_KEY_16='url.https://github.com/.pushInsteadOf'
export GIT_CONFIG_VALUE_16='ssh.github.com:'
export GIT_CONFIG_KEY_17='url.https://github.com/acme/.insteadOf'
export GIT_CONFIG_VALUE_17='https://github.com/acme/'
export GIT_CONFIG_KEY_18='url.https://github.com/acme/.pushInsteadOf'
export GIT_CONFIG_VALUE_18='https://github.com/acme/'
export GIT_CONFIG_KEY_19='url.https://github.com/acme/repo.git.insteadOf'
export GIT_CONFIG_VALUE_19='git@github.com:acme/repo.git'
export GIT_CONFIG_KEY_20='url.https://github.com/acme/repo.git.pushInsteadOf'
export GIT_CONFIG_VALUE_20='git@github.com:acme/repo.git'
export BOT_INSTALL_ID='42'
export GIT_CONFIG_COUNT=21
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
    expect(env.GIT_CONFIG_VALUE_20).toBe("git@github.com:acme/repo.git") // exact per-remote pair survives
    expect(env.GIT_CONFIG_COUNT).toBe("21") // bare scalar survives
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

  test("fail closed: identity block missing committer or GIT_CONFIG entries", async () => {
    const botEnv = fixture(
      "bot-two-fields",
      `#!/usr/bin/env bash\nprintf '%s\\n' "export GIT_AUTHOR_NAME='acme-agent[bot]'" "export GH_TOKEN='ghs_x'"\n`,
    )
    await expect(call(botEnv, gitRepo("two-fields"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: bot helper is not at GIT_CONFIG index 1", async () => {
    const botEnv = fixture("bot-no-helper", BOT_BLOCK.replace("GIT_CONFIG_VALUE_1='!", "GIT_CONFIG_VALUE_1='"))
    await expect(call(botEnv, gitRepo("no-helper"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: a GIT_CONFIG_COUNT entry without its key/value", async () => {
    const botEnv = fixture("bot-short", BOT_BLOCK.replace("GIT_CONFIG_COUNT=21", "GIT_CONFIG_COUNT=22"))
    await expect(call(botEnv, gitRepo("short"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: GIT_CONFIG_PARAMETERS absent", async () => {
    const botEnv = fixture("bot-no-params", BOT_BLOCK.replace("export GIT_CONFIG_PARAMETERS=''\n", ""))
    await expect(call(botEnv, gitRepo("no-params"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: GH_TOKEN without an identity", async () => {
    const botEnv = fixture("bot-token-only", `#!/usr/bin/env bash\necho "export GH_TOKEN='ghs_x'"\n`)
    await expect(call(botEnv, gitRepo("token-only"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: an undercounted GIT_CONFIG_COUNT leaves entries git would ignore", async () => {
    const botEnv = fixture("bot-undercount", BOT_BLOCK.replace("GIT_CONFIG_COUNT=21", "GIT_CONFIG_COUNT=2"))
    await expect(call(botEnv, gitRepo("undercount"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: GIT_CONFIG entries beyond a valid lowered GIT_CONFIG_COUNT", async () => {
    // COUNT=3 is within bounds and indices 0-2 are well formed; git would ignore
    // the insteadOf/pushInsteadOf pairs still exported at 3 and above.
    const botEnv = fixture("bot-lowered", BOT_BLOCK.replace("GIT_CONFIG_COUNT=21", "GIT_CONFIG_COUNT=3"))
    await expect(call(botEnv, gitRepo("lowered"))).rejects.toThrow(/GIT_CONFIG_KEY_3 beyond GIT_CONFIG_COUNT/)
  })

  test("fail closed: a non-numeric or huge GIT_CONFIG_COUNT", async () => {
    for (const [name, count] of [["nan", "abc"], ["huge", "99999999999"]]) {
      const botEnv = fixture(`bot-count-${name}`, BOT_BLOCK.replace("GIT_CONFIG_COUNT=21", `GIT_CONFIG_COUNT=${count}`))
      await expect(call(botEnv, gitRepo(`count-${name}`))).rejects.toThrow(/partial identity block/)
    }
  })

  test("fail closed: a block with only GIT_CONFIG exports", async () => {
    const botEnv = fixture(
      "bot-config-only",
      `#!/usr/bin/env bash\nprintf '%s\\n' "export GIT_CONFIG_COUNT=1" "export GIT_CONFIG_KEY_0='credential.helper'" "export GIT_CONFIG_VALUE_0=''"\n`,
    )
    await expect(call(botEnv, gitRepo("config-only"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: a non-empty GIT_CONFIG_PARAMETERS", async () => {
    const botEnv = fixture("bot-params", BOT_BLOCK.replace("GIT_CONFIG_PARAMETERS=''", "GIT_CONFIG_PARAMETERS='x'"))
    await expect(call(botEnv, gitRepo("params"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: the fixed GIT_CONFIG entries are not the bot-env shape", async () => {
    const noReset = fixture("bot-reset", BOT_BLOCK.replace("GIT_CONFIG_VALUE_0=''", "GIT_CONFIG_VALUE_0='x'"))
    await expect(call(noReset, gitRepo("reset"))).rejects.toThrow(/partial identity block/)
    const gpg = fixture("bot-gpg", BOT_BLOCK.replace("GIT_CONFIG_VALUE_2='false'", "GIT_CONFIG_VALUE_2='true'"))
    await expect(call(gpg, gitRepo("gpg"))).rejects.toThrow(/partial identity block/)
  })

  test("fail closed: bot-env not executable", async () => {
    const botEnv = fixture("bot-noexec", BOT_BLOCK, false)
    await expect(call(botEnv, gitRepo("noexec"))).rejects.toThrow()
  })

  test("fail closed: a wedged bot-env is abandoned at the deadline, not awaited", async () => {
    // bash defers SIGTERM while a foreground child runs and the child keeps
    // the pipes open, so a signal alone never bounded this; the hook must
    // reject at the deadline whatever the child does.
    const botEnv = fixture("bot-wedged", `#!/usr/bin/env bash\nsleep 5\necho "export GH_TOKEN='x'"\n`)
    const t0 = Date.now()
    await expect(call(botEnv, gitRepo("wedged"), undefined, { timeoutMs: 300 })).rejects.toThrow(/did not complete within 300ms/)
    expect(Date.now() - t0).toBeLessThan(2000)
  }, 10_000)

  test("a non-finite timeoutMs falls back to the default instead of an immediate timeout", async () => {
    // Infinity used to be coerced by setTimeout into a ~1 ms timer, which
    // would time out every command; it must behave like the 20 s default.
    const botEnv = fixture("bot-ok-inf", BOT_BLOCK)
    const env = await call(botEnv, gitRepo("inf", "git@github.com:acme/repo.git"), undefined, { timeoutMs: Infinity })
    expect(env.GH_TOKEN).toBe("ghs_fixture")
    // A fractional value below 1 would floor to a 0 ms timer; it falls back too.
    const frac = await call(botEnv, gitRepo("frac", "git@github.com:acme/repo.git"), undefined, { timeoutMs: 0.5 })
    expect(frac.GH_TOKEN).toBe("ghs_fixture")
  })

  test("the deadline releases the pipe readers it was waiting on", async () => {
    // After the deadline wins, the collectors must have been cancelled so a
    // lingering descendant cannot keep this process's pipe ends open: the
    // wedged fixture backgrounds a sleep that holds stdout, and the hook
    // must still reject at the deadline and not hang on that sleep.
    const botEnv = fixture("bot-held-pipe", `#!/usr/bin/env bash\n(sleep 5) &\nwait\n`)
    const t0 = Date.now()
    await expect(call(botEnv, gitRepo("held"), undefined, { timeoutMs: 300 })).rejects.toThrow(/did not complete within 300ms/)
    expect(Date.now() - t0).toBeLessThan(2000)
  }, 10_000)

  test("fail closed: DEFAULT_BOT_ENV placeholder left as REPLACE", async () => {
    const client = { app: { log: async () => ({}) } }
    const hooks = (await (AgentBotIdentity as (i: unknown) => Promise<Record<string, never>>)({ client } as never)) as {
      "shell.env": (i: { cwd: string; sessionID: string; callID: string }, o: { env: Record<string, string> }) => Promise<void>
    }
    await expect(
      hooks["shell.env"]({ cwd: gitRepo("replace"), sessionID: "s", callID: "c" }, { env: {} }),
    ).rejects.toThrow(/DEFAULT_BOT_ENV/)
  })

  test("a hung logger cannot hold the hook open past the deadline", async () => {
    const neverSettles = () => new Promise<never>(() => {})
    const client = { app: { log: neverSettles } }
    const plugin = AgentBotIdentity as (input: unknown, options?: unknown) => Promise<Record<string, unknown>>
    const botEnv = fixture("bot-wedged-log", `#!/usr/bin/env bash\nsleep 5\necho "export GH_TOKEN='x'"\n`)
    const hooks = (await plugin({ client } as never, { botEnv, timeoutMs: 300 })) as {
      "shell.env": (i: { cwd: string; sessionID: string; callID: string }, o: { env: Record<string, string> }) => Promise<void>
    }
    const t0 = Date.now()
    await expect(hooks["shell.env"]({ cwd: gitRepo("wedged-log"), sessionID: "s", callID: "c" }, { env: {} })).rejects.toThrow(/did not complete within 300ms/)
    expect(Date.now() - t0).toBeLessThan(2000)
  }, 10_000)
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
