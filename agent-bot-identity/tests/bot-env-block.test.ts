import { describe, expect, test } from "bun:test"

import { BotEnvError, END_LINE, HOST_WIDE_REWRITE_SOURCES, parseBotEnvBlock } from "../scripts/bot-env-block"
import { BOT_OUTPUT, PERSONAL_OUTPUT } from "./bot-env-fixtures"

const refuse = (out: string): string => {
  try {
    parseBotEnvBlock(out, "/repo")
  } catch (err) {
    expect(err).toBeInstanceOf(BotEnvError)
    return (err as Error).message
  }
  throw new Error("expected a refusal")
}

const withoutPair = (out: string, value: string, kind: "insteadOf" | "pushInsteadOf"): string => {
  // Drop one host-wide entry by renaming its key to an exact-remote key, keeping the count coherent.
  const lines = out.split("\n")
  const i = lines.findIndex((l, n) => l === `export GIT_CONFIG_KEY_${l.match(/KEY_(\d+)/)?.[1]}='url.https://github.com/.${kind}'` && lines[n + 1]?.endsWith(`='${value}'`))
  lines[i] = lines[i].replace("url.https://github.com/.", "url.https://example.invalid/.")
  return lines.join("\n")
}

describe("parseBotEnvBlock", () => {
  test("fixture sanity: 21 counted entries, completeness line last", () => {
    expect(BOT_OUTPUT).toContain("export GIT_CONFIG_COUNT=21\n")
    expect(BOT_OUTPUT.trimEnd().split("\n").at(-1)).toBe(END_LINE)
    expect(HOST_WIDE_REWRITE_SOURCES.length).toBe(7)
  })

  test("bot verdict: exports parsed whole, no unsets", () => {
    const { exports, unsets } = parseBotEnvBlock(BOT_OUTPUT, "/repo")
    expect(exports.GH_TOKEN).toBe("ghs_fixture")
    expect(exports.GIT_CONFIG_VALUE_0).toBe("")
    expect(exports.GIT_CONFIG_COUNT).toBe("21")
    expect(unsets).toEqual([])
  })

  test("personal verdict: unsets only", () => {
    const { exports, unsets } = parseBotEnvBlock(PERSONAL_OUTPUT, "/repo")
    expect(exports).toEqual({})
    expect(unsets).toContain("GH_TOKEN")
    expect(unsets).toContain("GIT_CONFIG_PARAMETERS")
  })

  test("refuses empty output", () => {
    expect(refuse("")).toMatch(/no output/)
  })

  test("refuses a truncated personal block (no completeness line)", () => {
    expect(refuse(PERSONAL_OUTPUT.replace(`${END_LINE}\n`, ""))).toMatch(/does not end with/)
    expect(refuse("unset GIT_AUTHOR_NAME\n")).toMatch(/does not end with/)
  })

  test("refuses a truncated bot block (no completeness line)", () => {
    expect(refuse(BOT_OUTPUT.replace(`${END_LINE}\n`, ""))).toMatch(/does not end with/)
  })

  test("refuses the completeness line anywhere but last", () => {
    expect(refuse(`${END_LINE}\n${PERSONAL_OUTPUT}`)).toMatch(/unrecognized line 1/)
  })

  test("refuses a bot block with GIT_CONFIG_COUNT=3 and no rewrites", () => {
    const lines = BOT_OUTPUT.split("\n").filter((l) => !/GIT_CONFIG_(KEY|VALUE)_([3-9]|[1-9][0-9])=/.test(l))
    const out = lines.join("\n").replace("GIT_CONFIG_COUNT=21", "GIT_CONFIG_COUNT=3")
    const msg = refuse(out)
    expect(msg).toMatch(/partial identity block/)
    expect(msg).toContain("host-wide insteadOf and pushInsteadOf for git@github.com:")
  })

  for (const source of [
    "git@github.com:",
    "github.com:",
    "ssh://git@github.com/",
    "https://github.com/",
    "ssh://git@ssh.github.com:443/",
    "git@ssh.github.com:",
    "ssh.github.com:",
  ]) {
    for (const kind of ["insteadOf", "pushInsteadOf"] as const) {
      test(`refuses a bot block missing the host-wide ${kind} for ${source}`, () => {
        expect(refuse(withoutPair(BOT_OUTPUT, source, kind))).toContain(`host-wide insteadOf and pushInsteadOf for ${source}`)
      })
    }
  }

  test("unrecognized-line refusal never echoes the line's value", () => {
    const out = PERSONAL_OUTPUT.replace("unset GH_TOKEN\n", "export GH_TOKEN=ghs_SECRET value\n")
    const msg = refuse(out)
    expect(msg).toMatch(/unrecognized line 3/)
    expect(msg).toContain("GH_TOKEN")
    expect(msg).not.toContain("ghs_SECRET")
  })

  test("refuses a marker-only block (personal path with no unsets)", () => {
    const msg = refuse(`${END_LINE}\n`)
    expect(msg).toMatch(/personal block missing unsets/)
    for (const name of ["GIT_AUTHOR_NAME", "GH_TOKEN", "GIT_CONFIG_PARAMETERS", "BOT_INSTALL_ID"]) expect(msg).toContain(name)
  })

  test("refuses a personal block with partial unsets, naming each missing unset", () => {
    const msg = refuse(`unset GH_TOKEN\n${END_LINE}\n`)
    expect(msg).toMatch(/personal block missing unsets/)
    expect(msg).toContain("GIT_AUTHOR_NAME")
    expect(msg).toContain("BOT_INSTALL_ID")
    expect(msg).not.toMatch(/missing unsets[^)]*GH_TOKEN/)
  })

  test("personal block with every required unset plus enumerated GIT_CONFIG unsets parses", () => {
    const out = PERSONAL_OUTPUT.replace(`${END_LINE}\n`, `unset GIT_CONFIG_KEY_0\nunset GIT_CONFIG_VALUE_0\n${END_LINE}\n`)
    expect(parseBotEnvBlock(out, "/repo").unsets).toContain("GIT_CONFIG_KEY_0")
  })

  test("unrecognized-line number is the raw 1-based stdout line, blank lines included", () => {
    const out = `\n\nunset GH_TOKEN\n\nbogus\n${END_LINE}\n`
    expect(refuse(out)).toMatch(/unrecognized line 5 /)
  })

  test("a bare export value must be digits only", () => {
    const msg = refuse(PERSONAL_OUTPUT.replace("unset GH_TOKEN\n", "export GH_TOKEN='ghs_x\n"))
    expect(msg).toMatch(/unrecognized line 3/)
    expect(msg).toContain("export GH_TOKEN")
    expect(msg).not.toContain("ghs_x")
    expect(refuse(PERSONAL_OUTPUT.replace("unset GH_TOKEN\n", "export GH_TOKEN=ghs_bare\n"))).toMatch(/unrecognized line 3/)
  })

  test("bot block with unset BOT_INSTALL_ID and no BOT_INSTALL_ID export (default installation) parses", () => {
    const out = BOT_OUTPUT.replace("export BOT_INSTALL_ID='42'\n", "unset BOT_INSTALL_ID\n")
    const { exports, unsets } = parseBotEnvBlock(out, "/repo")
    expect(exports.BOT_INSTALL_ID).toBeUndefined()
    expect(unsets).toEqual(["BOT_INSTALL_ID"])
  })

  test("both-exported-and-unset refusal names the variable, not its value", () => {
    const msg = refuse(BOT_OUTPUT.replace(`${END_LINE}\n`, `unset GH_TOKEN\n${END_LINE}\n`))
    expect(msg).toMatch(/both exported and unset/)
    expect(msg).not.toContain("ghs_")
  })
})
