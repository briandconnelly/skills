#!/usr/bin/env node
// install-hooks.mjs : register (or remove) the completion-gates Stop hook in Claude Code settings.
//
// Default target: <cwd>/.claude/settings.local.json (personal, per-project,
// conventionally untracked, so a machine-specific absolute path never lands in git).
//
//   node install-hooks.mjs               install into project settings.local.json
//   node install-hooks.mjs --shared      install into project settings.json (tracked)
//   node install-hooks.mjs --global      install into ~/.claude/settings.json
//   node install-hooks.mjs --uninstall   remove from the chosen target (same flags)
//
// Idempotent: running install twice changes nothing. The hook only activates in
// directories containing .completion-gates/manifest.json, so even a --global
// install is inert outside gated projects.

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const args = process.argv.slice(2);
const uninstall = args.includes("--uninstall");
const global_ = args.includes("--global");
const shared = args.includes("--shared");

const hookScript = join(dirname(fileURLToPath(import.meta.url)), "stop-hook.mjs");
const MARKER = "completion-gates";

const target = global_
  ? join(homedir(), ".claude", "settings.json")
  : join(process.cwd(), ".claude", shared ? "settings.json" : "settings.local.json");

let settings = {};
if (existsSync(target)) {
  try {
    settings = JSON.parse(readFileSync(target, "utf8"));
  } catch (e) {
    console.error(`Refusing to touch ${target}: it exists but is not valid JSON (${e.message}).`);
    process.exit(1);
  }
}

settings.hooks = settings.hooks || {};
const stopHooks = Array.isArray(settings.hooks.Stop) ? settings.hooks.Stop : [];

const isOurs = (entry) =>
  Array.isArray(entry?.hooks) &&
  entry.hooks.some(
    (h) =>
      typeof h?.command === "string" &&
      h.command.includes("stop-hook.mjs") &&
      h.command.toLowerCase().includes(MARKER),
  );

const kept = stopHooks.filter((e) => !isOurs(e));

if (uninstall) {
  if (kept.length === stopHooks.length) {
    console.log(`Nothing to remove: no completion-gates Stop hook found in ${target}`);
    process.exit(0);
  }
  settings.hooks.Stop = kept;
  if (!settings.hooks.Stop.length) delete settings.hooks.Stop;
  if (!Object.keys(settings.hooks).length) delete settings.hooks;
  writeFileSync(target, JSON.stringify(settings, null, 2) + "\n");
  console.log(`Removed completion-gates Stop hook from ${target}`);
  process.exit(0);
}

if (stopHooks.some(isOurs)) {
  console.log(`Already installed in ${target} (idempotent, nothing changed).`);
  process.exit(0);
}

settings.hooks.Stop = [
  ...kept,
  { hooks: [{ type: "command", command: `node "${hookScript}"`, timeout: 20 }] },
];
mkdirSync(dirname(target), { recursive: true });
writeFileSync(target, JSON.stringify(settings, null, 2) + "\n");

console.log(`Installed completion-gates Stop hook into ${target}
  command: node "${hookScript}"
  effect:  in directories with a frozen .completion-gates/manifest.json, ending
           the turn is blocked while gates are open (max 6 blocks without
           progress; ABANDON lines allow a labeled INCOMPLETE-HANDOFF stop).
  remove:  node "${fileURLToPath(import.meta.url)}"${global_ ? " --global" : shared ? " --shared" : ""} --uninstall`);
