#!/usr/bin/env node
// test.mjs : regression tests for the completion-gates enforcement scripts.
// Zero dependencies. Run: node test.mjs
//
// Every false-success path found in the ancestor project (unlazy v2) has a
// test here: silently dropped file args, EXPECT match excusing a nonzero
// exit, evidence that only existed in memory, empty ledgers reporting
// success, abandoned gates counted as met, and hook release counters reset
// by cosmetic edits.

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, appendFileSync, rmSync, mkdirSync, existsSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import assert from "node:assert/strict";

const SCRIPTS = dirname(fileURLToPath(import.meta.url));
const tempDirs = [];

function makeDir() {
  const d = mkdtempSync(join(tmpdir(), "completion-gates-test-"));
  tempDirs.push(d);
  return d;
}

function gitInit(dir) {
  const git = (...a) =>
    spawnSync("git", a, { cwd: dir, encoding: "utf8", env: { ...process.env, GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_SYSTEM: "/dev/null" } });
  git("init", "-q");
  git("config", "user.email", "t@t");
  git("config", "user.name", "t");
  writeFileSync(join(dir, "src.txt"), "v1\n");
  git("add", "-A");
  git("commit", "-qm", "init");
  return git;
}

const gateCheck = (dir, ...args) =>
  spawnSync("node", [join(SCRIPTS, "gate-check.mjs"), ...args], { cwd: dir, encoding: "utf8" });
const stopHook = (dir) =>
  spawnSync("node", [join(SCRIPTS, "stop-hook.mjs")], {
    cwd: dir,
    encoding: "utf8",
    input: JSON.stringify({ cwd: dir, stop_hook_active: false }),
  });

const SIMPLE_GATES = `# Gates: test

- [ ] G1: says hello
  CHECK: echo hello
  EXPECT: hello
  EVIDENCE: pending
`;

function freshGated(content = SIMPLE_GATES, { git = false } = {}) {
  const dir = makeDir();
  if (git) gitInit(dir);
  writeFileSync(join(dir, "GATES.md"), content);
  return dir;
}

let passed = 0;
let failed = 0;
function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ok    ${name}`);
  } catch (e) {
    failed++;
    console.log(`  FAIL  ${name}\n        ${e.message.split("\n")[0]}`);
  }
}

// ---------------------------------------------------------------- runner soundness

test("happy path: freeze + run proves the gate, flips the box, writes an artifact", () => {
  const dir = freshGated();
  assert.equal(gateCheck(dir, "freeze").status, 0);
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /OVERALL: PROVEN/);
  assert.match(readFileSync(join(dir, "GATES.md"), "utf8"), /- \[x\] G1/);
  assert.match(readFileSync(join(dir, ".completion-gates/artifacts/G1.log"), "utf8"), /hello/);
});

test("all positional file args are processed — none silently dropped", () => {
  const dir = makeDir();
  writeFileSync(join(dir, "a.md"), "# Gates: a\n\n- [ ] A1: a\n  CHECK: echo aaa\n  EXPECT: aaa\n  EVIDENCE: pending\n");
  writeFileSync(join(dir, "b.md"), "# Gates: b\n\n- [ ] B1: b\n  CHECK: echo bbb\n  EXPECT: bbb\n  EVIDENCE: pending\n");
  assert.equal(gateCheck(dir, "freeze", "a.md", "b.md").status, 0);
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(readFileSync(join(dir, "a.md"), "utf8"), /- \[x\] A1/);
  assert.match(readFileSync(join(dir, "b.md"), "utf8"), /- \[x\] B1/);
});

test("EXPECT match never excuses a nonzero exit", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: lies\n  CHECK: echo hello; exit 1\n  EXPECT: hello\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 1, run.stdout);
  assert.match(run.stdout, /FAIL G1/);
  assert.match(readFileSync(join(dir, "GATES.md"), "utf8"), /- \[ \] G1/);
});

test("a declared EXIT makes a nonzero exit passing", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: fails by design\n  CHECK: echo hello; exit 3\n  EXPECT: hello\n  EXIT: 3\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run").status, 0);
});

test("freeze rejects a gate with no EVIDENCE line (no in-memory-only evidence)", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: no evidence slot\n  CHECK: echo hi\n  EXPECT: hi\n");
  const res = gateCheck(dir, "freeze");
  assert.equal(res.status, 2);
  assert.match(res.stderr, /no EVIDENCE line/);
});

test("zero gates is an error, never an empty success", () => {
  const dir = freshGated("# Gates: empty\n\nnothing here\n");
  const res = gateCheck(dir, "freeze");
  assert.equal(res.status, 2);
  assert.match(res.stderr, /no gates found/);
  assert.equal(gateCheck(dir, "run").status, 2); // and run without a manifest is an error too
});

test("duplicate gate ids are rejected at freeze", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: a\n  EVIDENCE: pending\n\n- [ ] G1: b\n  EVIDENCE: pending\n");
  const res = gateCheck(dir, "freeze");
  assert.equal(res.status, 2);
  assert.match(res.stderr, /duplicate gate id G1/);
});

test("unknown flags and missing flag values are errors, not ignored", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run", "--bogus").status, 2);
  assert.equal(gateCheck(dir, "run", "--timeout").status, 2);
});

// ---------------------------------------------------------------- contract integrity

test("weakening a CHECK after freeze is spec drift: run refuses until amended", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: real check\n  CHECK: node --version\n  EXPECT: /v\\d+/\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [ ] G1: real check\n  CHECK: echo ok\n  EXPECT: ok\n  EVIDENCE: pending\n");
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 2);
  assert.match(run.stderr, /drift/);
  const amend = gateCheck(dir, "amend", "--reason", "check was wrong for this platform");
  assert.equal(amend.status, 0, amend.stderr);
  assert.equal(gateCheck(dir, "run").status, 0);
  const manifest = JSON.parse(readFileSync(join(dir, ".completion-gates/manifest.json"), "utf8"));
  assert.equal(manifest.revisions.length, 1);
  assert.equal(manifest.revisions[0].changes[0].id, "G1");
});

test("amend requires a reason and a real change", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "amend").status, 2);
  const noop = gateCheck(dir, "amend", "--reason", "nothing changed");
  assert.equal(noop.status, 2);
  assert.match(noop.stderr, /nothing to amend/);
});

test("abandoned gates yield INCOMPLETE-HANDOFF (exit 3), never PROVEN", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  appendFileSync(join(dir, "GATES.md"), "\nABANDON: G1 environment lacks the tool\n");
  const res = gateCheck(dir, "status");
  assert.equal(res.status, 3, res.stdout);
  assert.match(res.stdout, /INCOMPLETE-HANDOFF/);
  assert.doesNotMatch(res.stdout, /OVERALL: PROVEN/);
});

test("criteria traceability: unmapped criterion or unknown FOR fails freeze", () => {
  const unmapped = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n- C2: goodbye works\n\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  EXPECT: hello\n  EVIDENCE: pending\n");
  const r1 = gateCheck(unmapped, "freeze");
  assert.equal(r1.status, 2);
  assert.match(r1.stderr, /criterion C2 is mapped to no gate/);

  const unknown = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n\n- [ ] G1: hello\n  FOR: C9\n  CHECK: echo hello\n  EXPECT: hello\n  EVIDENCE: pending\n");
  const r2 = gateCheck(unknown, "freeze");
  assert.equal(r2.status, 2);
  assert.match(r2.stderr, /unknown criterion C9/);

  const good = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  EXPECT: hello\n  EVIDENCE: pending\n");
  assert.equal(gateCheck(good, "freeze").status, 0);
});

test("manual gates: unmet until checked with real evidence, then attested", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: design reviewed by hand\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "status").status, 1);
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [x] G1: design reviewed by hand\n  EVIDENCE: reviewed layout.tsx:120-180, all three tiers present\n");
  const res = gateCheck(dir, "status");
  assert.equal(res.status, 0, res.stdout);
  assert.match(res.stdout, /ATTESTED/);
});

test("checked box with pending evidence is still unmet", () => {
  const dir = freshGated("# Gates: t\n\n- [x] G1: claimed done\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  const res = gateCheck(dir, "status");
  assert.equal(res.status, 1);
  assert.match(res.stdout, /EVIDENCE still pending/);
});

test("staleness: workspace change after a passing run demotes PROVEN (git)", () => {
  const dir = freshGated(SIMPLE_GATES, { git: true });
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run").status, 0);
  assert.equal(gateCheck(dir, "status").status, 0);
  writeFileSync(join(dir, "src.txt"), "v2 changed after the passing run\n");
  const res = gateCheck(dir, "status");
  assert.equal(res.status, 1, res.stdout);
  assert.match(res.stdout, /STALE/);
  assert.equal(gateCheck(dir, "run").status, 0); // re-running re-proves
});

test("negative control: passes when the CHECK fails pre-fix, refuses when it already passes", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0); // pre-fix: check fails => control ok
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "control", "G1").status, 1); // post-fix: check passes => no sensitivity shown
});

test("run preserves a prior negative-control record in state", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0);
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "run").status, 0);
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  assert.equal(state.gates.G1.status, "pass");
  assert.equal(state.gates.G1.control.failedAsExpected, true, "run must not erase the control record");
});

// ---------------------------------------------------------------- live-ledger integrity

const CRIT_GATES = "# Gates: t\n\n## Criteria\n- C1: hello works\n\n## Gates\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  EXPECT: hello\n  EVIDENCE: pending\n";

test("ABANDON of an unknown gate id is rejected at freeze, amend, status, run, and hook", () => {
  const dir = freshGated(SIMPLE_GATES + "\nABANDON: G99 typo\n");
  const fr = gateCheck(dir, "freeze");
  assert.equal(fr.status, 2);
  assert.match(fr.stderr, /ABANDON G99 names no gate/);

  const ok = freshGated();
  gateCheck(ok, "freeze");
  appendFileSync(join(ok, "GATES.md"), "\nABANDON: G99 typo\n");
  for (const cmd of ["status", "run"]) {
    const r = gateCheck(ok, cmd);
    assert.equal(r.status, 2, `${cmd}: ${r.stdout}`);
    assert.match(r.stderr, /ABANDON G99 names no gate/);
  }
  const am = gateCheck(ok, "amend", "--reason", "x");
  assert.equal(am.status, 2);
  assert.match(am.stderr, /ABANDON G99 names no gate/);
  const hook = JSON.parse(stopHook(ok).stdout);
  assert.equal(hook.decision, undefined);
  assert.match(hook.systemMessage, /ABANDON G99 names no gate/);
});

test("duplicate ABANDON lines for one gate are rejected", () => {
  const dir = freshGated(SIMPLE_GATES + "\nABANDON: G1 one\nABANDON: G1 two\n");
  const r = gateCheck(dir, "freeze");
  assert.equal(r.status, 2);
  assert.match(r.stderr, /ABANDON G1 declared more than once/);
});

test("a gate added to the live file after freeze is spec drift, not invisible", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  appendFileSync(join(dir, "GATES.md"), "\n- [ ] G2: unfrozen\n  EVIDENCE: pending\n");
  const r = gateCheck(dir, "status");
  assert.equal(r.status, 2, r.stdout);
  assert.match(r.stderr, /gate G2 is not in the frozen manifest/);
  assert.equal(gateCheck(dir, "amend", "--reason", "add G2").status, 0);
  assert.equal(gateCheck(dir, "status").status, 1); // G2 is now a real unmet gate
});

test("duplicate live gate ids after freeze are rejected, not silently merged", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  appendFileSync(join(dir, "GATES.md"), "\n- [x] G1: impostor\n  EVIDENCE: looks done\n");
  const r = gateCheck(dir, "status");
  assert.equal(r.status, 2, r.stdout);
  assert.match(r.stderr, /duplicate gate id G1/);
});

test("criteria-only edits are drift and are amendable", () => {
  const dir = freshGated(CRIT_GATES);
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run").status, 0);
  writeFileSync(join(dir, "GATES.md"), CRIT_GATES.replace("hello works", "hello works in French too"));
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 2, st.stdout);
  assert.match(st.stderr, /criterion C1 changed since freeze/);
  const am = gateCheck(dir, "amend", "--reason", "scope grew");
  assert.equal(am.status, 0, am.stderr);
  assert.match(am.stdout, /criterion-changed C1/);
  const manifest = JSON.parse(readFileSync(join(dir, ".completion-gates/manifest.json"), "utf8"));
  assert.equal(manifest.revisions[0].changes[0].op, "criterion-changed");
  assert.equal(manifest.criteria[0].text, "hello works in French too");
  assert.equal(gateCheck(dir, "status").status, 0);
});

test("ABANDON for a leaf gate may live in the driver's file", () => {
  const dir = makeDir();
  mkdirSync(join(dir, "gates"));
  writeFileSync(join(dir, "GATES.md"), "# Gates: driver\n\n- [ ] D1: integrates\n  CHECK: echo ok\n  EXPECT: ok\n  EVIDENCE: pending\n\nABANDON: L1 tool missing\n");
  writeFileSync(join(dir, "gates/leaf.md"), "# Gates: leaf\n\n- [ ] L1: leaf thing\n  CHECK: false\n  EVIDENCE: pending\n");
  assert.equal(gateCheck(dir, "freeze").status, 0);
  const r = gateCheck(dir, "run");
  assert.equal(r.status, 3, r.stdout);
  assert.match(r.stdout, /ABANDONED L1/);
});

// ---------------------------------------------------------------- evidence bound to spec

test("amending a CHECK invalidates the old passing run — the new command must execute", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run").status, 0);
  writeFileSync(join(dir, "GATES.md"), SIMPLE_GATES.replace("CHECK: echo hello", "CHECK: false"));
  assert.equal(gateCheck(dir, "amend", "--reason", "tighten").status, 0);
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 1, st.stdout);
  assert.match(st.stdout, /spec amended since last run/);
  assert.equal(gateCheck(dir, "run").status, 1); // the new CHECK really runs and fails
});

test("amending a CHECK invalidates its control record", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0);
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f other.txt\n  EVIDENCE: pending\n");
  gateCheck(dir, "amend", "--reason", "rename");
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  assert.ok(state.gates.G1.control.specFp, "control stores the spec fingerprint");
  assert.match(gateCheck(dir, "status").stdout, /control: stale/);
});

// ---------------------------------------------------------------- reset

test("freeze refuses to overwrite a manifest; --force no longer exists", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  const again = gateCheck(dir, "freeze");
  assert.equal(again.status, 2);
  assert.match(again.stderr, /amend --reason.*reset --reason/);
  const forced = gateCheck(dir, "freeze", "--force");
  assert.equal(forced.status, 2);
  assert.match(forced.stderr, /unknown flag --force/);
});

test("reset requires a reason and an existing manifest, and keeps the revision trail", () => {
  const dir = freshGated();
  assert.equal(gateCheck(dir, "reset", "--reason", "x").status, 2); // nothing to reset yet
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  writeFileSync(join(dir, "GATES.md"), SIMPLE_GATES.replace("echo hello", "echo hi").replace("EXPECT: hello", "EXPECT: hi"));
  gateCheck(dir, "amend", "--reason", "first amend");
  stopHook(dir);
  assert.equal(gateCheck(dir, "reset").status, 2);

  writeFileSync(join(dir, "GATES.md"), "# Gates: v2\n\n- [ ] G1: brand new contract\n  CHECK: echo new\n  EXPECT: new\n  EVIDENCE: pending\n");
  const r = gateCheck(dir, "reset", "--reason", "start over after scope change");
  assert.equal(r.status, 0, r.stderr);
  const m = JSON.parse(readFileSync(join(dir, ".completion-gates/manifest.json"), "utf8"));
  assert.equal(m.revisions.length, 2, "prior amend survives the reset");
  assert.equal(m.revisions[0].reason, "first amend");
  assert.equal(m.revisions[1].reason, "start over after scope change");
  assert.equal(m.revisions[1].changes[0].op, "reset");
  assert.equal(m.revisions[1].changes[0].previous.gates[0].check, "echo hi");
  assert.ok(!existsSync(join(dir, ".completion-gates/state.json")), "old evidence cleared");
  assert.ok(!existsSync(join(dir, ".completion-gates/hook-state.json")), "hook counter cleared");
  assert.ok(!existsSync(join(dir, ".completion-gates/artifacts/G1.log")), "old artifacts archived");
  assert.ok(readdirSync(join(dir, ".completion-gates")).some((f) => f.startsWith("artifacts-reset-")));
  assert.equal(gateCheck(dir, "status").status, 1); // fresh contract, nothing proven
  assert.match(gateCheck(dir, "status").stdout, /revision 2 .*start over/);
});

// ---------------------------------------------------------------- stop hook

test("hook: no manifest means allow, even with a bare GATES.md present", () => {
  const dir = makeDir();
  writeFileSync(join(dir, "GATES.md"), SIMPLE_GATES);
  const res = stopHook(dir);
  assert.equal(res.status, 0);
  assert.equal(res.stdout.trim(), "");
});

test("hook: blocks on open gates, allows on PROVEN", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  const blocked = JSON.parse(stopHook(dir).stdout);
  assert.equal(blocked.decision, "block");
  assert.match(blocked.reason, /G1/);
  gateCheck(dir, "run");
  assert.equal(stopHook(dir).stdout.trim(), "");
});

test("hook: abandoning everything allows stop but labels it a handoff, not success", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  appendFileSync(join(dir, "GATES.md"), "\nABANDON: G1 cannot run in this environment\n");
  const res = JSON.parse(stopHook(dir).stdout);
  assert.equal(res.decision, undefined);
  assert.match(res.systemMessage, /INCOMPLETE-HANDOFF/);
});

test("hook: cosmetic edits do not reset the release counter; resolution progress does", () => {
  const dir = freshGated(
    "# Gates: t\n\n- [ ] G1: a\n  CHECK: echo aaa\n  EXPECT: aaa\n  EVIDENCE: pending\n\n- [ ] G2: manual\n  EVIDENCE: pending\n",
  );
  gateCheck(dir, "freeze");
  stopHook(dir);
  appendFileSync(join(dir, "GATES.md"), "\n\n"); // cosmetic edit
  stopHook(dir);
  let hs = JSON.parse(readFileSync(join(dir, ".completion-gates/hook-state.json"), "utf8"));
  assert.equal(hs.blocks, 2, "cosmetic edit must not reset the counter");
  gateCheck(dir, "run"); // proves G1: real progress
  stopHook(dir);
  hs = JSON.parse(readFileSync(join(dir, ".completion-gates/hook-state.json"), "utf8"));
  assert.equal(hs.blocks, 1, "resolving a gate must reset the counter");
});

test("hook: releases with a warning after MAX_BLOCKS stops without progress", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  let last;
  for (let i = 0; i < 7; i++) last = stopHook(dir);
  const res = JSON.parse(last.stdout);
  assert.equal(res.decision, undefined);
  assert.match(res.systemMessage, /releasing after 6 blocks/);
  assert.match(res.systemMessage, /Do not report this work as done/);
});

test("hook: broken gate state allows stop with a warning instead of trapping", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  rmSync(join(dir, "GATES.md"));
  const res = JSON.parse(stopHook(dir).stdout);
  assert.equal(res.decision, undefined);
  assert.match(res.systemMessage, /allowing stop rather than trapping/);
});

// ----------------------------------------------------------------

console.log(`\n${passed} passed, ${failed} failed`);
for (const d of tempDirs) rmSync(d, { recursive: true, force: true });
process.exit(failed ? 1 : 0);
