/**
 * pi adapter for the agent-bot-identity skill.
 *
 * Implements the SKILL Phase 4 routing contract for pi (verified against
 * pi 1.1.0): the extension re-registers the `bash` tool and handles
 * `user_bash` (TUI `!`/`!!` and RPC `bash`), both with a BashOperations
 * wrapper that runs the shared bot-env in the command's actual cwd and hands
 * pi's local shell a complete env. Identity is decided per command at
 * execution time; any undetermined-identity outcome throws, and a throw from
 * operations.exec fails the command with no local fallback.
 *
 * The routing decision lives in bot-env; the output contract lives in
 * ./bot-env-block (installed beside this file). This file owns neither.
 *
 * Install (see references/adapters/pi.md): copy to
 * ~/.config/<bot>/bin/agent-bot-identity-pi.ts beside bot-env-block.ts, set
 * DEFAULT_BOT_ENV, and forward to it from <repo>/.pi/extensions/ (Variant A)
 * or ~/.pi/agent/extensions/ (Variant B).
 */

import { spawn } from "node:child_process"
import { delimiter, join } from "node:path"

import type { BashOperations, ExtensionAPI } from "@earendil-works/pi-coding-agent"
import { createBashToolDefinition, createLocalBashOperations, getAgentDir } from "@earendil-works/pi-coding-agent"

import { BotEnvError, parseBotEnvBlock } from "./bot-env-block"

// Absolute path to the installed, customized bot-env script.
const DEFAULT_BOT_ENV = "REPLACE" // e.g. "/Users/<you>/.config/acme-agent/bin/bot-env"

// Same deadline and rationale as the OpenCode adapter: bot-env's hot path is
// well under a second and a cold mint is bounded by bot-token's own 10 s
// timeout; the deadline makes a wedged subprocess fail the command loudly.
const TIMEOUT_MS = 20_000

const POWERSHELL_REASON =
  "agent-bot-identity: the powershell tool is not routed through the bot identity; disable it (see references/adapters/pi.md)"

export type AgentBotIdentityOptions = { botEnv?: string; timeoutMs?: number }

type Env = Record<string, string | undefined>
type Warn = (message: string) => void

// pi's local shell uses its internal getShellEnv() when given no env:
// process.env with pi's managed bin directory (getAgentDir()/bin) prepended
// to PATH (pi/dist/utils/shell.js). getShellEnv is not exported, so this
// mirrors it from the public getAgentDir(); re-check it after a pi upgrade.
export function piShellEnv(): Env {
  const binDir = join(getAgentDir(), "bin")
  const pathKey = Object.keys(process.env).find((key) => key.toLowerCase() === "path") ?? "PATH"
  const current = process.env[pathKey] ?? ""
  const updated = current.split(delimiter).filter(Boolean).includes(binDir) ? current : [binDir, current].filter(Boolean).join(delimiter)
  return { ...process.env, [pathKey]: updated }
}

function runBotEnv(botEnv: string, cwd: string, base: Env, timeoutMs: number): Promise<{ stdout: string; stderr: string }> {
  if (botEnv === "REPLACE") {
    return Promise.reject(
      new BotEnvError(
        "agent-bot-identity: DEFAULT_BOT_ENV is not customized; set it to the absolute path of the installed bot-env (see references/adapters/pi.md)",
      ),
    )
  }
  return new Promise((resolve, reject) => {
    let settled = false
    let timer: ReturnType<typeof setTimeout> | undefined
    const finish = (settle: () => void): void => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      settle()
    }
    // Spawn the script directly, not via a shell: a missing or non-executable
    // bot-env must fail closed, not run degraded. bot-env inherits exactly the
    // env being routed, so its unset lines cover the variables actually present.
    let child: ReturnType<typeof spawn>
    try {
      child = spawn(botEnv, [], { cwd, env: base as NodeJS.ProcessEnv, stdio: ["ignore", "pipe", "pipe"] })
    } catch (err) {
      reject(new BotEnvError(`agent-bot-identity: failed to spawn bot-env at ${botEnv}: ${err}`))
      return
    }
    const out: Buffer[] = []
    const errOut: Buffer[] = []
    child.stdout?.on("data", (chunk: Buffer) => out.push(chunk))
    child.stderr?.on("data", (chunk: Buffer) => errOut.push(chunk))
    child.on("error", (err) => finish(() => reject(new BotEnvError(`agent-bot-identity: failed to spawn bot-env at ${botEnv}: ${err.message}`))))
    child.on("close", (code, signal) =>
      finish(() => {
        const stderr = Buffer.concat(errOut).toString("utf8")
        if (code !== 0) {
          reject(new BotEnvError(`agent-bot-identity: bot-env exited ${code ?? signal} in ${cwd}: ${stderr.trim() || "(no stderr)"}`))
          return
        }
        resolve({ stdout: Buffer.concat(out).toString("utf8"), stderr })
      }),
    )
    // At the deadline stop waiting: kill the script and release this
    // process's pipe ends, since a descendant may still hold them open.
    timer = setTimeout(
      () =>
        finish(() => {
          child.kill("SIGKILL")
          child.stdout?.destroy()
          child.stderr?.destroy()
          reject(new BotEnvError(`agent-bot-identity: bot-env did not complete within ${timeoutMs}ms in ${cwd}; refusing to continue with undetermined identity`))
        }),
      timeoutMs,
    )
  })
}

async function resolveEnv(botEnv: string, cwd: string, base: Env, timeoutMs: number, warn: Warn): Promise<Env> {
  const { stdout, stderr } = await runBotEnv(botEnv, cwd, base, timeoutMs)
  // bot-env's stderr carries the ambiguity warnings; their repetition is the signal.
  if (stderr.trim()) warn(stderr.trim())
  const { exports, unsets } = parseBotEnvBlock(stdout, cwd)
  const env: Env = { ...base }
  for (const name of unsets) delete env[name]
  return Object.assign(env, exports)
}

// Test seam for the base-env test; not part of the adapter's interface.
export const __resolveEnvForTest = (botEnv: string, cwd: string, base: Env): Promise<Env> =>
  resolveEnv(botEnv, cwd, base, TIMEOUT_MS, () => {})

export function wrapOperations(inner: BashOperations, resolve: (cwd: string, base: Env) => Promise<Env>): BashOperations {
  return {
    exec: async (command, cwd, options) => {
      // Agent bash passes pi's shell env plus PI_* session variables;
      // executeBash (user commands) passes none, so use pi's shell env.
      const env = await resolve(cwd, options.env ?? piShellEnv())
      return inner.exec(command, cwd, { ...options, env: env as NodeJS.ProcessEnv })
    },
  }
}

function usableTimeout(requested: unknown): number {
  return typeof requested === "number" && Number.isFinite(requested) && requested >= 1 && requested <= 2_147_483_647
    ? Math.floor(requested)
    : TIMEOUT_MS
}

export function createAgentBotIdentity(options: AgentBotIdentityOptions = {}): (pi: ExtensionAPI) => void {
  const botEnv = typeof options.botEnv === "string" ? options.botEnv : DEFAULT_BOT_ENV
  const timeoutMs = usableTimeout(options.timeoutMs)

  return function agentBotIdentity(pi: ExtensionAPI): void {
    // Warnings are best-effort and never delay routing or a refusal.
    const warnVia =
      (ctx: unknown): Warn =>
      (message) => {
        try {
          ;(ctx as { ui?: { notify?: (m: string, t?: string) => void } })?.ui?.notify?.(`agent-bot-identity: ${message}`, "warning")
        } catch {}
      }
    const resolver = (warn: Warn) => (cwd: string, base: Env) => resolveEnv(botEnv, cwd, base, timeoutMs, warn)

    // Registered at load for its name, schema, prompt text and renderers. The
    // built-in bash receives shellCommandPrefix and shellPath from settings
    // (agent-session.js _buildRuntime), a replacement does not inherit them,
    // and settings are unavailable during load, so each call builds the
    // definition from the effective settings (which also follows /reload).
    const template = createBashToolDefinition(process.cwd(), {
      operations: wrapOperations(createLocalBashOperations(), resolver(() => {})),
    })
    pi.registerTool({
      ...template,
      async execute(toolCallId, params, signal, onUpdate, ctx) {
        const settings = pi.getSettings() as { shellPath?: string; shellCommandPrefix?: string }
        const definition = createBashToolDefinition((ctx as { cwd?: string })?.cwd || process.cwd(), {
          operations: wrapOperations(createLocalBashOperations({ shellPath: settings.shellPath }), resolver(warnVia(ctx))),
          commandPrefix: settings.shellCommandPrefix,
          shellPath: settings.shellPath,
        })
        return definition.execute(toolCallId, params, signal, onUpdate, ctx)
      },
    })

    // TUI `!`/`!!` and RPC `bash`. Identity resolves inside exec, in the cwd
    // executeBash actually uses, never from event.cwd: RPC requests run
    // concurrently and a switch_session can change the cwd in between. No
    // prefix here: executeBash already applies it to user commands.
    pi.on("user_bash", (_event, ctx) => ({
      operations: wrapOperations(
        createLocalBashOperations({ shellPath: (pi.getSettings() as { shellPath?: string }).shellPath }),
        resolver(warnVia(ctx)),
      ),
    }))

    pi.on("tool_call", (event) => (event.toolName === "powershell" ? { block: true, reason: POWERSHELL_REASON } : undefined))
  }
}

export default createAgentBotIdentity()
