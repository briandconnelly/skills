/**
 * OpenCode adapter for the agent-bot-identity skill.
 *
 * Implements the SKILL Phase 4 routing contract for OpenCode: per-command,
 * cwd-aware identity routing via the "shell.env" plugin hook. OpenCode fires
 * "shell.env" before every shell-tool command with that command's cwd and
 * merges the hook's output env over the server process env for that command
 * only (verified against opencode 1.18.22, packages/opencode/src/tool/shell.ts
 * `shellEnv`), so identity is re-decided per command and a personal-verdict
 * command carries no bot vars.
 *
 * The routing decision itself is delegated to the shared harness-neutral
 * bot-env script (SKILL Phase 4); this file only executes it per command and
 * translates its emitted shell into the env map. The verdict table exists
 * exactly once, in bot-env, across all harnesses.
 *
 * Install (see references/adapters/opencode.md):
 *   Variant A (per-project opt-in):  copy to <repo>/.opencode/plugin/agent-bot-identity.ts
 *   Variant B (user-level automatic): copy to ~/.config/opencode/plugin/agent-bot-identity.ts
 * then set DEFAULT_BOT_ENV to the absolute path of the installed bot-env and
 * restart opencode (plugins load at startup).
 *
 * Never commit the installed copy: it is machine-local routing config. Add
 * `.opencode/plugin/agent-bot-identity.ts` to the repo's .git/info/exclude.
 */

import type { Plugin } from "@opencode-ai/plugin"

// Absolute path to the installed, customized bot-env script.
const DEFAULT_BOT_ENV = "REPLACE" // e.g. "/Users/<you>/.config/acme-agent/bin/bot-env"

// bot-env's hot path is a few local git probes plus a cached-token read (well
// under a second); a cold mint is bounded by bot-token's own 10s request
// timeout. This bound exists so a wedged subprocess fails the command loudly
// instead of hanging the session.
const TIMEOUT_MS = 20_000

type ShellEnvInput = { cwd: string; sessionID?: string; callID?: string }
type ShellEnvOutput = { env: Record<string, string> }

// bot-env emits exactly three line shapes:
//   export KEY='value'   single-quoted; bot-env refuses values containing a quote
//   export KEY=value     unquoted scalars, e.g. GIT_CONFIG_COUNT=6
//   unset KEY [KEY ...]
const EXPORT_QUOTED = /^export ([A-Z_][A-Z0-9_]*)='([^']*)'$/
const EXPORT_BARE = /^export ([A-Z_][A-Z0-9_]*)=(\S+)$/
const UNSET = /^unset ([A-Z_][A-Z0-9_]*(?: [A-Z_][A-Z0-9_]*)*)$/

class BotEnvError extends Error {}

async function runBotEnv(botEnv: string, cwd: string): Promise<{ stdout: string; stderr: string }> {
  if (botEnv === "REPLACE") {
    throw new BotEnvError(
      "agent-bot-identity: DEFAULT_BOT_ENV is not customized; set it to the absolute path of the installed bot-env (see references/adapters/opencode.md)",
    )
  }
  // Spawn the script directly rather than via `bash <script>`: a missing or
  // non-executable bot-env must fail closed (spawn throws), not run degraded.
  let proc: ReturnType<typeof Bun.spawn>
  try {
    proc = Bun.spawn([botEnv], {
      cwd,
      stdin: "ignore",
      stdout: "pipe",
      stderr: "pipe",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
  } catch (err) {
    throw new BotEnvError(`agent-bot-identity: failed to spawn bot-env at ${botEnv}: ${err}`)
  }
  let stdout: string, stderr: string, code: number
  try {
    ;[stdout, stderr, code] = await Promise.all([
      new Response(proc.stdout as ReadableStream<Uint8Array>).text(),
      new Response(proc.stderr as ReadableStream<Uint8Array>).text(),
      proc.exited,
    ])
  } catch (err) {
    throw new BotEnvError(`agent-bot-identity: bot-env did not complete within ${TIMEOUT_MS}ms in ${cwd}: ${err}`)
  }
  if (code !== 0) {
    throw new BotEnvError(`agent-bot-identity: bot-env exited ${code} in ${cwd}: ${stderr.trim() || "(no stderr)"}`)
  }
  return { stdout, stderr }
}

export const AgentBotIdentity: Plugin = async ({ client }, options) => {
  const botEnv = typeof options?.botEnv === "string" ? options.botEnv : DEFAULT_BOT_ENV

  const log = async (level: "warn" | "error", message: string, extra?: Record<string, unknown>) => {
    // Logging is best-effort; a log failure must never affect routing.
    try {
      await client.app.log({ body: { service: "agent-bot-identity", level, message, extra } })
    } catch {}
  }

  const fail = async (err: unknown, cwd: string): Promise<never> => {
    // A throwing hook fails the shell command before it runs: that is this
    // adapter's fail-closed path, so every undetermined-identity outcome raises.
    await log("error", String(err), { cwd })
    throw err
  }

  return {
    "shell.env": async (input: ShellEnvInput, output: ShellEnvOutput) => {
      // PTY spawns (interactive terminal tabs) carry no session/call id; leave
      // those shells personal, matching the personal-terminal invariant the
      // other adapters' verification enforces. They also could not honor the
      // 1h token lifetime: a PTY env is fixed at spawn.
      if (!input.sessionID || !input.callID) return

      const { stdout, stderr } = await runBotEnv(botEnv, input.cwd).catch((err) => fail(err, input.cwd))

      // bot-env's stderr carries the ambiguity warnings (no remotes, probe
      // failures); their repetition is the signal, so forward every one.
      const warning = stderr.trim()
      if (warning) await log("warn", warning, { cwd: input.cwd })

      const lines = stdout.split("\n").filter((line) => line !== "")
      if (lines.length === 0) {
        await fail(
          new BotEnvError(`agent-bot-identity: bot-env emitted no output in ${input.cwd}; refusing to continue with undetermined identity`),
          input.cwd,
        )
      }
      for (const line of lines) {
        let match = EXPORT_QUOTED.exec(line)
        if (match) {
          output.env[match[1]] = match[2]
          continue
        }
        match = EXPORT_BARE.exec(line)
        if (match) {
          output.env[match[1]] = match[2]
          continue
        }
        match = UNSET.exec(line)
        if (match) {
          // Each command's env is built fresh from the server process env, so
          // bot vars from earlier commands cannot linger; unsets only guard
          // against collisions within this block.
          for (const name of match[1].split(" ")) delete output.env[name]
          continue
        }
        await fail(
          new BotEnvError(`agent-bot-identity: bot-env emitted an unrecognized line in ${input.cwd}: ${JSON.stringify(line)}`),
          input.cwd,
        )
      }

      // Contract check: bot-env emits the identity block only together with a
      // non-empty GH_TOKEN (its fail-closed sentinel included). Anything else
      // means the output shape changed; do not route with half an identity.
      const hasIdentity = "GIT_AUTHOR_NAME" in output.env
      const hasToken = "GH_TOKEN" in output.env
      if (hasIdentity !== hasToken || (hasToken && output.env.GH_TOKEN === "")) {
        await fail(
          new BotEnvError(`agent-bot-identity: bot-env emitted a partial identity block in ${input.cwd}; refusing to route`),
          input.cwd,
        )
      }
    },
  }
}

export default AgentBotIdentity
