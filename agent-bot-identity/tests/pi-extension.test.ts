import { afterAll, describe, expect, test } from "bun:test"
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from "node:fs"
import { homedir, tmpdir } from "node:os"
import { basename, dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

import { __resolveEnvForTest, createAgentBotIdentity, piShellEnv, wrapOperations } from "../scripts/pi/agent-bot-identity"
import { BOT_OUTPUT, PERSONAL_OUTPUT, script } from "./bot-env-fixtures"

// Run with: bash agent-bot-identity/tests/pi-extension-test.sh (from the repo
// root). bun test ignores NODE_PATH; the runner links the installed pi package
// into agent-bot-identity/node_modules, which is gitignored.
// Fixture bot-env scripts exercise the real spawn + parse path through the
// createAgentBotIdentity({ botEnv, timeoutMs }) test seam.

const root = mkdtempSync(join(tmpdir(), "agent-bot-identity-pi-test-"))
afterAll(() => rmSync(root, { recursive: true, force: true }))

function fixture(name: string, body: string, executable = true): string {
  const path = join(root, name)
  writeFileSync(path, body)
  chmodSync(path, executable ? 0o755 : 0o644)
  return path
}

function dir(name: string): string {
  return mkdtempSync(join(root, `${name}-`))
}

type Handler = (event: unknown, ctx: unknown) => unknown
function load(botEnv: string, settings: Record<string, unknown> = {}, extra: Record<string, unknown> = {}) {
  const tools: Record<string, any> = {}
  const handlers: Record<string, Handler[]> = {}
  const pi = {
    registerTool: (t: any) => (tools[t.name] = t),
    on: (event: string, h: Handler) => (handlers[event] ??= []).push(h),
    getSettings: () => settings,
  }
  createAgentBotIdentity({ botEnv, ...extra })(pi as never)
  return { tools, handlers }
}

const ctxFor = (cwd: string, notes: string[] = []) => ({
  cwd,
  sessionManager: { getSessionId: () => "s", getSessionFile: () => undefined },
  ui: { notify: (m: string) => notes.push(m) },
})

const PRINT = 'printf "%s|%s|%s\\n" "${GH_TOKEN-unset}" "${GIT_AUTHOR_NAME-unset}" "${GIT_CONFIG_KEY_0-unset}"'

async function runBash(botEnv: string, cwd: string, command = PRINT, settings: Record<string, unknown> = {}) {
  const { tools } = load(botEnv, settings)
  const result = await tools.bash.execute("call-1", { command }, undefined, undefined, ctxFor(cwd))
  return result.content.map((c: { text: string }) => c.text).join("").trim()
}

describe("pi adapter: agent bash tool", () => {
  test("registers a replacement named bash", () => {
    const { tools } = load(fixture("reg", script(BOT_OUTPUT)))
    expect(Object.keys(tools)).toContain("bash")
  })

  test("bot verdict: the command sees the bot identity", async () => {
    expect(await runBash(fixture("bot", script(BOT_OUTPUT)), dir("bot"))).toBe("ghs_fixture|acme-agent[bot]|credential.helper")
  })

  test("personal verdict strips identity variables present only in the base env", async () => {
    // Like the real bot-env, this fixture enumerates numbered GIT_CONFIG vars
    // from its own inherited env, which must be the routed base env.
    const personal = fixture(
      "personal-enum",
      `#!/usr/bin/env bash\nprintf '%s\\n' 'unset GH_TOKEN GIT_AUTHOR_NAME'\nfor v in $(compgen -v | grep -E '^GIT_CONFIG_(KEY|VALUE)_[0-9]+$' || true); do echo "unset $v"; done\necho '# bot-env: end'\n`,
    )
    let captured: Record<string, string | undefined> = {}
    const inner = {
      exec: async (_command: string, _cwd: string, opts: { env?: Record<string, string | undefined> }) => {
        captured = opts.env ?? {}
        return { exitCode: 0 }
      },
    }
    const ops = wrapOperations(inner as never, (cwd, base) => __resolveEnvForTest(personal, cwd, base))
    await ops.exec("true", dir("personal"), {
      onData: () => {},
      env: { PATH: process.env.PATH ?? "", GH_TOKEN: "stale", GIT_AUTHOR_NAME: "me", GIT_CONFIG_KEY_0: "x", GIT_CONFIG_VALUE_0: "y" },
    })
    expect(captured.GH_TOKEN).toBeUndefined()
    expect(captured.GIT_AUTHOR_NAME).toBeUndefined()
    expect(captured.GIT_CONFIG_KEY_0).toBeUndefined()
    expect(captured.GIT_CONFIG_VALUE_0).toBeUndefined()
    expect(captured.PATH).toBe(process.env.PATH ?? "")
  })

  for (const [name, body, pattern] of [
    ["crash", `#!/usr/bin/env bash\necho broken >&2\nexit 1\n`, /bot-env exited 1/],
    ["empty", `#!/usr/bin/env bash\nexit 0\n`, /no output/],
    ["truncated", script(PERSONAL_OUTPUT.replace("# bot-env: end\n", "")), /does not end with/],
    ["partial", script("export GIT_AUTHOR_NAME='acme-agent[bot]'\n# bot-env: end\n"), /partial identity block/],
  ] as const) {
    test(`fail closed (${name}): the inner exec never runs`, async () => {
      let ran = false
      const { tools } = load(fixture(`fc-${name}`, body))
      // A marker file proves the shell never started.
      const marker = join(dir(`fc-${name}`), "ran")
      await expect(
        tools.bash.execute("c", { command: `touch ${marker}` }, undefined, undefined, ctxFor(dir(`fc-${name}-cwd`))),
      ).rejects.toThrow(pattern)
      ran = await Bun.file(marker).exists()
      expect(ran).toBe(false)
    })
  }

  test("fail closed: bot-env not executable", async () => {
    const { tools } = load(fixture("noexec", script(BOT_OUTPUT), false))
    await expect(tools.bash.execute("c", { command: "true" }, undefined, undefined, ctxFor(dir("noexec")))).rejects.toThrow(/failed to spawn bot-env|EACCES/)
  })

  test("fail closed: bot-env missing", async () => {
    const { tools } = load(join(root, "does-not-exist"))
    const marker = join(dir("missing"), "ran")
    await expect(tools.bash.execute("c", { command: `touch ${marker}` }, undefined, undefined, ctxFor(dir("missing-cwd")))).rejects.toThrow(/failed to spawn bot-env/)
    expect(await Bun.file(marker).exists()).toBe(false)
  })

  test("fail closed: DEFAULT_BOT_ENV left as REPLACE", async () => {
    const { tools } = load(undefined as unknown as string)
    await expect(tools.bash.execute("c", { command: "true" }, undefined, undefined, ctxFor(dir("replace")))).rejects.toThrow(/DEFAULT_BOT_ENV/)
  })

  test("a wedged bot-env is abandoned at the deadline", async () => {
    const { tools } = load(fixture("wedged", `#!/usr/bin/env bash\n(sleep 5) &\nwait\n`), {}, { timeoutMs: 300 })
    const t0 = Date.now()
    await expect(tools.bash.execute("c", { command: "true" }, undefined, undefined, ctxFor(dir("wedged")))).rejects.toThrow(/did not complete within 300ms/)
    expect(Date.now() - t0).toBeLessThan(2000)
  }, 10_000)

  test("configured shellCommandPrefix applies to agent bash", async () => {
    const out = await runBash(fixture("prefix", script(BOT_OUTPUT)), dir("prefix"), 'echo "$PREFIXED"', { shellCommandPrefix: "PREFIXED=yes" })
    expect(out).toBe("yes")
  })

  test("shellPath with a leading ~/ is expanded like pi's built-in", async () => {
    // A real shell reachable only through ~/: a symlink in a temp dir under the home directory.
    const home = mkdtempSync(join(homedir(), ".agent-bot-identity-pi-test-"))
    try {
      symlinkSync("/bin/bash", join(home, "bash"))
      const out = await runBash(fixture("tilde", script(BOT_OUTPUT)), dir("tilde"), "echo ran-ok", { shellPath: `~/${basename(home)}/bash` })
      expect(out).toContain("ran-ok")
    } finally {
      rmSync(home, { recursive: true, force: true })
    }
  })

  test("bot-env stderr warnings reach the UI", async () => {
    const notes: string[] = []
    const { tools } = load(fixture("warn", `#!/usr/bin/env bash\necho 'bot-env: no remotes' >&2\n${script(PERSONAL_OUTPUT).split("\n").slice(1).join("\n")}`))
    await tools.bash.execute("c", { command: "true" }, undefined, undefined, ctxFor(dir("warn"), notes))
    expect(notes.join("\n")).toContain("no remotes")
  })
})

describe("pi adapter: user bash (! and RPC)", () => {
  test("returns wrapped operations that resolve at exec time, in the exec cwd", async () => {
    // The fixture prints the bot block only in a directory named bot-*.
    const cwdAware = fixture(
      "cwd-aware",
      `#!/usr/bin/env bash\ncase "$(basename "$PWD")" in bot-*) cat <<'OUT'\n${BOT_OUTPUT}OUT\n;; *) cat <<'OUT'\n${PERSONAL_OUTPUT}OUT\n;; esac\n`,
    )
    const { handlers } = load(cwdAware)
    const personalCwd = dir("personal")
    const botCwd = dir("bot")
    const result = (await handlers.user_bash[0]({ type: "user_bash", command: "x", excludeFromContext: false, cwd: personalCwd }, ctxFor(personalCwd))) as {
      operations: { exec: (c: string, cwd: string, o: { onData: (b: Buffer) => void }) => Promise<{ exitCode: number | null }> }
    }
    let out = ""
    await result.operations.exec(PRINT, botCwd, { onData: (b) => (out += b.toString()) })
    expect(out.trim()).toBe("ghs_fixture|acme-agent[bot]|credential.helper")
  })

  test("refusal: exec throws and the command never runs", async () => {
    const { handlers } = load(fixture("ub-crash", `#!/usr/bin/env bash\nexit 1\n`))
    const cwd = dir("ub-crash")
    const marker = join(cwd, "ran")
    const { operations } = (await handlers.user_bash[0]({ type: "user_bash", command: "x", excludeFromContext: false, cwd }, ctxFor(cwd))) as any
    await expect(operations.exec(`touch ${marker}`, cwd, { onData: () => {} })).rejects.toThrow(/bot-env exited 1/)
    expect(await Bun.file(marker).exists()).toBe(false)
  })

  test("the user path does not add shellCommandPrefix (executeBash already does)", async () => {
    const { handlers } = load(fixture("ub-prefix", script(BOT_OUTPUT)), { shellCommandPrefix: "PREFIXED=yes" })
    const cwd = dir("ub-prefix")
    const { operations } = (await handlers.user_bash[0]({ type: "user_bash", command: "x", excludeFromContext: false, cwd }, ctxFor(cwd))) as any
    let out = ""
    await operations.exec('echo "${PREFIXED-none}"', cwd, { onData: (b: Buffer) => (out += b.toString()) })
    expect(out.trim()).toBe("none")
  })

  test("base env for user commands is pi's shell env (managed bin dir on PATH)", () => {
    const env = piShellEnv()
    const pathKey = Object.keys(env).find((k) => k.toLowerCase() === "path") ?? "PATH"
    expect((env[pathKey] ?? "").split(":")).toContain(join(process.env.HOME ?? "", ".pi", "agent", "bin"))
  })
})

describe("pi adapter: powershell", () => {
  test("blocks powershell calls", async () => {
    const { handlers } = load(fixture("ps", script(BOT_OUTPUT)))
    const res = (await handlers.tool_call[0]({ type: "tool_call", toolName: "powershell", input: {} }, {})) as { block?: boolean; reason?: string }
    expect(res?.block).toBe(true)
    expect(res?.reason).toMatch(/agent-bot-identity/)
    expect(await handlers.tool_call[0]({ type: "tool_call", toolName: "read", input: {} }, {})).toBeUndefined()
  })
})

describe("co-installation", () => {
  test("both adapters' masters and the shared module coexist in one flat directory", async () => {
    const bin = dir("bin")
    // bun test does not honor NODE_PATH, and the copies live in a temp dir, so
    // expose the same pi package to them through a node_modules symlink.
    const piPkg = dirname(dirname(fileURLToPath(import.meta.resolve("@earendil-works/pi-coding-agent"))))
    mkdirSync(join(bin, "node_modules", "@earendil-works"), { recursive: true })
    symlinkSync(piPkg, join(bin, "node_modules", "@earendil-works", "pi-coding-agent"))
    copyFileSync(join(import.meta.dir, "../scripts/bot-env-block.ts"), join(bin, "bot-env-block.ts"))
    copyFileSync(join(import.meta.dir, "../scripts/opencode/agent-bot-identity.ts"), join(bin, "agent-bot-identity-opencode.ts"))
    copyFileSync(join(import.meta.dir, "../scripts/pi/agent-bot-identity.ts"), join(bin, "agent-bot-identity-pi.ts"))
    const pi = await import(join(bin, "agent-bot-identity-pi.ts"))
    const oc = await import(join(bin, "agent-bot-identity-opencode.ts"))
    expect(typeof pi.createAgentBotIdentity).toBe("function")
    expect(typeof oc.default).toBe("function")
  })
})
