#!/usr/bin/env node
// stop-hook.mjs : Claude Code Stop hook for the completion-gates skill.
//
// Activation is the frozen manifest (.completion-gates/manifest.json), never a
// bare GATES.md, so a globally installed hook cannot collide with unrelated
// repos that happen to contain a file by that name.
//
// This hook is an auditable tripwire, not enforcement: the agent it constrains
// can edit every file it reads. Its job is to make an early stop visible and
// awkward, not impossible.
//
// Behavior:
//   no manifest                         -> allow (skill not active here)
//   status computation errors           -> allow with a warning (never trap on broken state)
//   PROVEN                              -> allow
//   INCOMPLETE-HANDOFF (abandons only)  -> allow, labeled as a handoff, not success
//   INCOMPLETE, resolution progressing  -> block with the unmet gate ids
//   INCOMPLETE, no progress in MAX_BLOCKS consecutive stops -> release with a warning
//
// Progress = the count of resolved gates (proven + attested + abandoned)
// increased since the last block. Cosmetic edits to gate files do not count,
// so an agent cannot reset the release counter by rewriting whitespace.
// It never runs CHECK commands itself (a Stop hook must not execute
// manifest-supplied shell); it only reads files and git metadata.
//
// stdin: hook JSON with { cwd, stop_hook_active, ... }. The block/release
// counter bounds re-blocking, so stop_hook_active does not change the logic.

import { readFileSync, existsSync } from "node:fs";
import { manifestPath, hookStatePath, readJSON, atomicWriteJSON, computeStatus } from "./lib.mjs";

const MAX_BLOCKS = 6;

let payload = {};
try {
  payload = JSON.parse(readFileSync(0, "utf8") || "{}");
} catch {
  /* stay permissive */
}
const cwd = payload.cwd || process.cwd();

if (!existsSync(manifestPath(cwd))) process.exit(0);

const status = computeStatus(cwd);

if (status.error) {
  console.log(
    JSON.stringify({
      systemMessage: `completion-gates: cannot evaluate gates (${status.error}); allowing stop rather than trapping. Fix the gate files or manifest.`,
    }),
  );
  process.exit(0);
}

if (status.overall === "PROVEN") process.exit(0);

if (status.overall === "INCOMPLETE-HANDOFF") {
  const ab = status.rows.filter((r) => r.resolution === "abandoned").map((r) => r.id);
  console.log(
    JSON.stringify({
      systemMessage: `completion-gates: stopping as INCOMPLETE-HANDOFF, not success — abandoned: ${ab.join(", ")}. The final report must list each abandoned gate and its reason.`,
    }),
  );
  process.exit(0);
}

// INCOMPLETE: progress-gated block.
const resolved = status.counts.proven + status.counts.attested + status.counts.abandoned;
const key = `resolved:${resolved}/${status.counts.total}`;
let hookState = readJSON(hookStatePath(cwd), { key: "", blocks: 0 });
if (hookState.key !== key) hookState = { key, blocks: 0 };
hookState.blocks += 1;
try {
  atomicWriteJSON(hookStatePath(cwd), hookState);
} catch {
  /* non-fatal */
}

const open = status.rows.filter((r) => r.resolution === "unmet" || r.resolution === "stale");
const list =
  open
    .slice(0, 5)
    .map((r) => `${r.id} (${r.resolution})`)
    .join(", ") + (open.length > 5 ? `, +${open.length - 5} more` : "");

if (hookState.blocks > MAX_BLOCKS) {
  console.log(
    JSON.stringify({
      systemMessage: `completion-gates: releasing after ${MAX_BLOCKS} blocks without gate progress; status is INCOMPLETE with ${open.length} open gate(s): ${list}. Do not report this work as done.`,
    }),
  );
  process.exit(0);
}

console.log(
  JSON.stringify({
    decision: "block",
    reason: `completion-gates: ${open.length} gate(s) open: ${list}. Work the next open gate (run gate-check.mjs run), hand-fill EVIDENCE on manual gates, or add "ABANDON: <id> <reason>" for a visible handoff. Only PROVEN counts as done.`,
  }),
);
process.exit(0);
