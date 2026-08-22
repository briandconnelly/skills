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
const stopHook = (dir, extra = {}) =>
  spawnSync("node", [join(SCRIPTS, "stop-hook.mjs")], {
    cwd: dir,
    encoding: "utf8",
    input: JSON.stringify({ cwd: dir, stop_hook_active: false, ...extra }),
  });

const SIMPLE_GATES = `# Gates: test

- [ ] G1: says hello
  CHECK: echo hello
  CONTROL: exempt fixture
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
  writeFileSync(join(dir, "a.md"), "# Gates: a\n\n- [ ] A1: a\n  CHECK: echo aaa\n  CONTROL: exempt fixture\n  EXPECT: aaa\n  EVIDENCE: pending\n");
  writeFileSync(join(dir, "b.md"), "# Gates: b\n\n- [ ] B1: b\n  CHECK: echo bbb\n  CONTROL: exempt fixture\n  EXPECT: bbb\n  EVIDENCE: pending\n");
  assert.equal(gateCheck(dir, "freeze", "a.md", "b.md").status, 0);
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(readFileSync(join(dir, "a.md"), "utf8"), /- \[x\] A1/);
  assert.match(readFileSync(join(dir, "b.md"), "utf8"), /- \[x\] B1/);
});

test("EXPECT match never excuses a nonzero exit", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: lies\n  CHECK: echo hello; exit 1\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  const run = gateCheck(dir, "run");
  assert.equal(run.status, 1, run.stdout);
  assert.match(run.stdout, /FAIL G1/);
  assert.match(readFileSync(join(dir, "GATES.md"), "utf8"), /- \[ \] G1/);
});

test("a declared EXIT makes a nonzero exit passing", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: fails by design\n  CHECK: echo hello; exit 3\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EXIT: 3\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "run").status, 0);
});

test("freeze rejects a gate with no EVIDENCE line (no in-memory-only evidence)", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: no evidence slot\n  CHECK: echo hi\n  CONTROL: exempt fixture\n  EXPECT: hi\n");
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
  const dir = freshGated("# Gates: t\n\n- [ ] G1: real check\n  CHECK: node --version\n  CONTROL: exempt fixture\n  EXPECT: /v\\d+/\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [ ] G1: real check\n  CHECK: echo ok\n  CONTROL: exempt fixture\n  EXPECT: ok\n  EVIDENCE: pending\n");
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
  const unmapped = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n- C2: goodbye works\n\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EVIDENCE: pending\n");
  const r1 = gateCheck(unmapped, "freeze");
  assert.equal(r1.status, 2);
  assert.match(r1.stderr, /criterion C2 is mapped to no gate/);

  const unknown = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n\n- [ ] G1: hello\n  FOR: C9\n  CHECK: echo hello\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EVIDENCE: pending\n");
  const r2 = gateCheck(unknown, "freeze");
  assert.equal(r2.status, 2);
  assert.match(r2.stderr, /unknown criterion C9/);

  const good = freshGated("# Gates: t\n\n## Criteria\n- C1: hello works\n\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EVIDENCE: pending\n");
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
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0); // pre-fix: check fails => control ok
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "control", "G1").status, 1); // post-fix: check passes => no sensitivity shown
});

test("run preserves a prior negative-control record in state", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0);
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "run").status, 0);
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  assert.equal(state.gates.G1.status, "pass");
  assert.equal(state.gates.G1.control.failedAsExpected, true, "run must not erase the control record");
});

// ---------------------------------------------------------------- live-ledger integrity

const CRIT_GATES = "# Gates: t\n\n## Criteria\n- C1: hello works\n\n## Gates\n- [ ] G1: hello\n  FOR: C1\n  CHECK: echo hello\n  CONTROL: exempt fixture\n  EXPECT: hello\n  EVIDENCE: pending\n";

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
  writeFileSync(join(dir, "GATES.md"), "# Gates: driver\n\n- [ ] D1: integrates\n  CHECK: echo ok\n  CONTROL: exempt fixture\n  EXPECT: ok\n  EVIDENCE: pending\n\nABANDON: L1 tool missing\n");
  writeFileSync(join(dir, "gates/leaf.md"), "# Gates: leaf\n\n- [ ] L1: leaf thing\n  CHECK: false\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
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
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0);
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f other.txt\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
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

  writeFileSync(join(dir, "GATES.md"), "# Gates: v2\n\n- [ ] G1: brand new contract\n  CHECK: echo new\n  CONTROL: exempt fixture\n  EXPECT: new\n  EVIDENCE: pending\n");
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

// ---------------------------------------------------------------- control outcomes

test("ledger shows control outcome per runnable gate: none, ok, insensitive", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: file exists\n  CHECK: test -f built.txt\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n\n- [ ] G2: manual\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  let out = gateCheck(dir, "status").stdout;
  assert.match(out, /G1: file exists \[control: none\]/);
  assert.doesNotMatch(out, /G2: manual \[control/);
  gateCheck(dir, "control", "G1");
  assert.match(gateCheck(dir, "status").stdout, /\[control: ok\]/);
  writeFileSync(join(dir, "built.txt"), "x");
  gateCheck(dir, "control", "G1");
  out = gateCheck(dir, "status").stdout;
  assert.match(out, /\[control: insensitive \(2 attempts\)\]/);
});

test("a control that times out is invalid, not ok", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: slow\n  CHECK: sleep 5\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  const r = gateCheck(dir, "control", "G1", "--timeout", "1");
  assert.equal(r.status, 1);
  assert.match(r.stdout, /CONTROL INVALID/);
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  assert.equal(state.gates.G1.control.outcome, "invalid");
  assert.equal(state.gates.G1.control.timedOut, true);
  assert.match(gateCheck(dir, "status").stdout, /\[control: invalid\]/);
});

test("an invalid EXPECT regex is rejected at freeze instead of silently never matching", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: bad\n  CHECK: echo x\n  CONTROL: exempt fixture\n  EXPECT: /(unclosed/\n  EVIDENCE: pending\n");
  const r = gateCheck(dir, "freeze");
  assert.equal(r.status, 2);
  assert.match(r.stderr, /EXPECT regex is invalid/);
});

// ---------------------------------------------------------------- CONTROL: required

const REQ = (check = "test -f built.txt", extra = "") =>
  `# Gates: t\n\n- [ ] G1: file exists\n  CHECK: ${check}\n  CONTROL: required\n${extra}  EVIDENCE: pending\n`;

test("every CHECK gate must declare CONTROL: required or CONTROL: exempt <reason>", () => {
  const absent = freshGated("# Gates: t\n\n- [ ] G1: x\n  CHECK: echo x\n  EVIDENCE: pending\n");
  let r = gateCheck(absent, "freeze");
  assert.equal(r.status, 2);
  assert.match(r.stderr, /G1 has a CHECK but no CONTROL line/);
  const bare = freshGated("# Gates: t\n\n- [ ] G1: x\n  CHECK: echo x\n  CONTROL: exempt\n  EVIDENCE: pending\n");
  r = gateCheck(bare, "freeze");
  assert.equal(r.status, 2);
  assert.match(r.stderr, /CONTROL: exempt needs a reason/);
  const bogus = freshGated("# Gates: t\n\n- [ ] G1: x\n  CHECK: echo x\n  CONTROL: maybe\n  EVIDENCE: pending\n");
  assert.match(gateCheck(bogus, "freeze").stderr, /CONTROL must be "required" or "exempt <reason>"/);
  const manual = freshGated("# Gates: t\n\n- [ ] G1: x\n  CONTROL: required\n  EVIDENCE: pending\n");
  assert.match(gateCheck(manual, "freeze").stderr, /CONTROL without a CHECK/);
});

test("required: unmet without a control, with an insensitive one, and with an invalid one", () => {
  const dir = freshGated(REQ());
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "run").status, 1);
  let out = gateCheck(dir, "status").stdout;
  assert.match(out, /UNMET.*control required, none recorded/);
  gateCheck(dir, "control", "G1"); // already passes -> insensitive
  out = gateCheck(dir, "status").stdout;
  assert.match(out, /control required but insensitive/);
  const slow = freshGated(REQ("sleep 5"));
  gateCheck(slow, "freeze");
  gateCheck(slow, "control", "G1", "--timeout", "1");
  assert.match(gateCheck(slow, "status").stdout, /control required but invalid/);
});

test("required: proven only with ok control recorded before the passing run", () => {
  const dir = freshGated(REQ());
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "control", "G1").status, 0);
  writeFileSync(join(dir, "built.txt"), "x");
  const r = gateCheck(dir, "run");
  assert.equal(r.status, 0, r.stdout);
  assert.match(r.stdout, /PROVEN.*\[control: ok\]/);
});

test("required: a control recorded after the passing run invalidates that run", () => {
  const dir = freshGated(REQ());
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "built.txt"), "x");
  gateCheck(dir, "run"); // passes, but unmet (no control)
  rmSync(join(dir, "built.txt"));
  assert.equal(gateCheck(dir, "control", "G1").status, 0); // ok, but post-hoc
  writeFileSync(join(dir, "built.txt"), "x");
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 1, st.stdout);
  assert.match(st.stdout, /no recorded run/); // control wiped the earlier run
  assert.equal(gateCheck(dir, "run").status, 0); // a fresh run after the control proves it
});

test("missing command (exit 127) is an invalid control, not ok", () => {
  const dir = freshGated(REQ("no-such-tool-xyz --version"));
  gateCheck(dir, "freeze");
  const r = gateCheck(dir, "control", "G1");
  assert.equal(r.status, 1);
  assert.match(r.stdout, /CONTROL INVALID.*exit=127/);
});

test("CONTROL_EXPECT: control is ok only when the failure matches the expected signature", () => {
  const dir = freshGated(REQ("sh -c 'echo wrong reason; exit 1'", "  CONTROL_EXPECT: AssertionError\n"));
  gateCheck(dir, "freeze");
  const r = gateCheck(dir, "control", "G1");
  assert.equal(r.status, 1);
  assert.match(r.stdout, /did not match CONTROL_EXPECT/);
  const good = freshGated(REQ("sh -c 'echo AssertionError: off by one; exit 1'", "  CONTROL_EXPECT: AssertionError\n"));
  gateCheck(good, "freeze");
  assert.equal(gateCheck(good, "control", "G1").status, 0);
});

test("changing CONTROL or CONTROL_EXPECT is spec drift; waiving required does not invalidate the run", () => {
  const dir = freshGated(REQ());
  gateCheck(dir, "freeze");
  gateCheck(dir, "control", "G1");
  writeFileSync(join(dir, "built.txt"), "x");
  assert.equal(gateCheck(dir, "run").status, 0);
  writeFileSync(join(dir, "GATES.md"), REQ().replace("CONTROL: required", "CONTROL: exempt pre-fix state gone"));
  let st = gateCheck(dir, "status");
  assert.equal(st.status, 1, st.stdout);
  assert.match(st.stdout, /spec drifted/);
  assert.equal(gateCheck(dir, "run").status, 2);
  const am = gateCheck(dir, "amend", "--reason", "pre-fix state gone");
  assert.equal(am.status, 0, am.stderr);
  assert.match(am.stdout, /changed G1/);
  st = gateCheck(dir, "status");
  assert.equal(st.status, 0, st.stdout);
  assert.match(st.stdout, /\[control: waived rev 1\]/);
  assert.match(st.stdout, /OVERALL: PROVEN \(1 proven, 1 waived of 1\)/);
});

test("control attempts accumulate; ledger shows the count", () => {
  const dir = freshGated(REQ());
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "built.txt"), "x");
  gateCheck(dir, "control", "G1"); // insensitive
  rmSync(join(dir, "built.txt"));
  gateCheck(dir, "control", "G1"); // ok
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  assert.equal(state.gates.G1.controls.length, 2);
  assert.match(gateCheck(dir, "status").stdout, /control: ok \(2 attempts\)/);
});

test("control records the workspace fingerprint; same-workspace as the passing run is flagged (git)", () => {
  const dir = freshGated(REQ("grep -q v2 src.txt"), { git: true });
  gateCheck(dir, "freeze");
  gateCheck(dir, "control", "G1"); // src.txt is v1 -> fails -> ok
  writeFileSync(join(dir, "src.txt"), "v2\n");
  assert.equal(gateCheck(dir, "run").status, 0);
  assert.doesNotMatch(gateCheck(dir, "status").stdout, /same-workspace/);
  // a flaky check: fails on control, passes on run, workspace untouched
  const flaky = freshGated(REQ("test -f .completion-gates/artifacts/G1.control.1.log"), { git: true });
  gateCheck(flaky, "freeze");
  gateCheck(flaky, "control", "G1"); // log does not exist yet -> fails -> ok; and writes the log
  assert.equal(gateCheck(flaky, "run").status, 0);
  assert.match(gateCheck(flaky, "status").stdout, /same-workspace/);
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
    "# Gates: t\n\n- [ ] G1: a\n  CHECK: echo aaa\n  CONTROL: exempt fixture\n  EXPECT: aaa\n  EVIDENCE: pending\n\n- [ ] G2: manual\n  EVIDENCE: pending\n",
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

// ---------------------------------------------------------------- close (end of life)

test("close on PROVEN archives the epoch, exits 0, and leaves the hook inert", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  const r = gateCheck(dir, "close");
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /closed as PROVEN/);
  assert.ok(!existsSync(join(dir, ".completion-gates/manifest.json")));
  assert.ok(!existsSync(join(dir, ".completion-gates/state.json")));
  const epochs = readdirSync(join(dir, ".completion-gates/history"));
  assert.equal(epochs.length, 1);
  const closure = JSON.parse(readFileSync(join(dir, ".completion-gates/history", epochs[0], "manifest.json"), "utf8"));
  assert.equal(closure.closure.final_status, "PROVEN");
  assert.match(closure.closure.final_ledger, /PROVEN +G1/);
  assert.ok(existsSync(join(dir, ".completion-gates/history", epochs[0], "GATES.md")), "gate files archived");
  assert.ok(existsSync(join(dir, ".completion-gates/history", epochs[0], "artifacts/G1.log")));
  assert.equal(stopHook(dir).stdout.trim(), "", "hook inert after a PROVEN close");
  assert.equal(gateCheck(dir, "freeze").status, 0, "a new contract can start without reset");
});

test("close on INCOMPLETE requires a reason, exits 1, and the hook labels exactly one stop", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "close").status, 2);
  const r = gateCheck(dir, "close", "--reason", "user cancelled");
  assert.equal(r.status, 1, r.stdout);
  assert.match(r.stdout, /closed as INCOMPLETE/);
  const first = JSON.parse(stopHook(dir).stdout);
  assert.equal(first.decision, undefined);
  assert.match(first.systemMessage, /closed as INCOMPLETE.*user cancelled.*do not report/i);
  assert.equal(stopHook(dir).stdout.trim(), "", "second stop is silent");
});

test("close on INCOMPLETE-HANDOFF exits 3 without a reason", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  appendFileSync(join(dir, "GATES.md"), "\nABANDON: G1 tool missing\n");
  assert.equal(gateCheck(dir, "close").status, 3);
});

test("status after close prints the final ledger with its exit code; a new contract inherits nothing", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  gateCheck(dir, "close");
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 0, st.stderr);
  assert.match(st.stdout, /closed .* as PROVEN/);
  assert.match(st.stdout, /PROVEN +G1/);
  // same id, same CHECK, no workspace change: must not start proven
  gateCheck(dir, "freeze");
  const fresh = gateCheck(dir, "status");
  assert.equal(fresh.status, 1, fresh.stdout);
  assert.match(fresh.stdout, /no recorded run/);
});

test("close refuses when the ledger cannot be computed", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  rmSync(join(dir, "GATES.md"));
  const r = gateCheck(dir, "close", "--reason", "x");
  assert.equal(r.status, 2);
  assert.match(r.stderr, /gate file missing/);
});

test("history artifacts and state are gitignored", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  const gi = readFileSync(join(dir, ".completion-gates/.gitignore"), "utf8");
  assert.match(gi, /history\/\*\/artifacts\//);
  assert.match(gi, /history\/\*\/state\.json/);
});

// ---------------------------------------------------------------- pause (ask the user)

test("pause: refused unless INCOMPLETE, and only one pending at a time", () => {
  const dir = freshGated();
  assert.equal(gateCheck(dir, "pause", "--reason", "q").status, 2); // no manifest
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "pause").status, 2); // no reason
  assert.equal(gateCheck(dir, "pause", "--reason", "Which DB should I target?").status, 0);
  const dup = gateCheck(dir, "pause", "--reason", "another");
  assert.equal(dup.status, 2);
  assert.match(dup.stderr, /pause already pending/);
  gateCheck(dir, "run");
  const done = freshGated();
  gateCheck(done, "freeze");
  gateCheck(done, "run");
  assert.equal(gateCheck(done, "pause", "--reason", "q").status, 2); // PROVEN: nothing to pause
});

test("pause: the hook allows one labeled stop, consumes the token, and does not touch the block counter", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  stopHook(dir); // blocks: 1
  gateCheck(dir, "pause", "--reason", "Which DB should I target?");
  const paused = JSON.parse(stopHook(dir).stdout);
  assert.equal(paused.decision, undefined);
  assert.match(paused.systemMessage, /paused, not done.*Which DB should I target\?.*1 gate\(s\) open/);
  const hs = JSON.parse(readFileSync(join(dir, ".completion-gates/hook-state.json"), "utf8"));
  assert.equal(hs.blocks, 1, "a paused stop must not increment the counter");
  assert.equal(hs.pause, undefined, "token consumed");
  assert.equal(hs.pauses.length, 1);
  assert.equal(JSON.parse(stopHook(dir).stdout).decision, "block", "next stop blocks again");
});

test("pause: seven pauses never reach the release; the counter only moves on real blocks", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  for (let i = 0; i < 7; i++) {
    gateCheck(dir, "pause", "--reason", `question ${i}`);
    assert.equal(JSON.parse(stopHook(dir).stdout).decision, undefined);
  }
  assert.equal(JSON.parse(stopHook(dir).stdout).decision, "block");
  assert.match(gateCheck(dir, "status").stdout, /7 pauses/);
});

test("pause: the reason must appear in last_assistant_message when the harness supplies it", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "pause", "--reason", "Which DB should I target?");
  const wrong = JSON.parse(stopHook(dir, { last_assistant_message: "All done, shipping it." }).stdout);
  assert.equal(wrong.decision, "block");
  assert.match(wrong.reason, /present the question/);
  const hs = JSON.parse(readFileSync(join(dir, ".completion-gates/hook-state.json"), "utf8"));
  assert.ok(hs.pause, "token kept for the next stop");
  const right = JSON.parse(stopHook(dir, { last_assistant_message: "Before I continue: which DB should I target?" }).stdout);
  assert.equal(right.decision, undefined);
});

test("pause: a token minted under one gate state is dropped when the state changes", () => {
  const dir = freshGated(
    "# Gates: t\n\n- [ ] G1: a\n  CHECK: echo aaa\n  CONTROL: exempt fixture\n  EXPECT: aaa\n  EVIDENCE: pending\n\n- [ ] G2: manual\n  EVIDENCE: pending\n",
  );
  gateCheck(dir, "freeze");
  gateCheck(dir, "pause", "--reason", "q");
  gateCheck(dir, "run"); // G1 proven: resolved count changed
  assert.equal(JSON.parse(stopHook(dir).stdout).decision, "block");
});

test("pauses survive reset and close in the audit trail", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "pause", "--reason", "q1");
  stopHook(dir);
  gateCheck(dir, "reset", "--reason", "new scope");
  const m = JSON.parse(readFileSync(join(dir, ".completion-gates/manifest.json"), "utf8"));
  assert.equal(m.revisions[0].changes[0].pauses[0].reason, "q1");
  gateCheck(dir, "pause", "--reason", "q2");
  stopHook(dir);
  gateCheck(dir, "close", "--reason", "cancelled");
  const epochs = readdirSync(join(dir, ".completion-gates/history"));
  const closure = JSON.parse(readFileSync(join(dir, ".completion-gates/history", epochs[0], "manifest.json"), "utf8"));
  assert.equal(closure.closure.pauses[0].reason, "q2");
});

// ---------------------------------------------------------------- copilot review (PR #158)

test("a gates/*.md file created after freeze is drift, not invisible", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  mkdirSync(join(dir, "gates"));
  writeFileSync(join(dir, "gates/new.md"), "# Gates: new\n\n- [ ] N1: thing\n  EVIDENCE: pending\n");
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 2, st.stdout);
  assert.match(st.stderr, /gates\/new.md is not in the frozen manifest/);
  assert.equal(gateCheck(dir, "amend", "--reason", "add leaf").status, 0);
  const m = JSON.parse(readFileSync(join(dir, ".completion-gates/manifest.json"), "utf8"));
  assert.deepEqual(m.files, ["GATES.md", "gates/new.md"]);
  assert.equal(gateCheck(dir, "status").status, 1);
});

test("duplicate ABANDON across files is rejected at freeze and live", () => {
  const dir = makeDir();
  mkdirSync(join(dir, "gates"));
  writeFileSync(join(dir, "GATES.md"), "# Gates: d\n\n- [ ] D1: x\n  CHECK: echo ok\n  CONTROL: exempt fixture\n  EVIDENCE: pending\n\nABANDON: L1 from driver\n");
  writeFileSync(join(dir, "gates/leaf.md"), "# Gates: l\n\n- [ ] L1: y\n  EVIDENCE: pending\n\nABANDON: L1 from leaf\n");
  const fr = gateCheck(dir, "freeze");
  assert.equal(fr.status, 2);
  assert.match(fr.stderr, /ABANDON L1 declared more than once/);
  writeFileSync(join(dir, "gates/leaf.md"), "# Gates: l\n\n- [ ] L1: y\n  EVIDENCE: pending\n");
  assert.equal(gateCheck(dir, "freeze").status, 0);
  appendFileSync(join(dir, "gates/leaf.md"), "\nABANDON: L1 again\n");
  assert.match(gateCheck(dir, "status").stderr, /ABANDON L1 declared more than once/);
});

test("close clears live checkboxes and evidence so a new contract cannot inherit attestations", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: manual\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [x] G1: manual\n  EVIDENCE: reviewed by hand\n");
  assert.equal(gateCheck(dir, "close").status, 0);
  const live = readFileSync(join(dir, "GATES.md"), "utf8");
  assert.match(live, /- \[ \] G1/);
  assert.match(live, /EVIDENCE: pending/);
  const epochs = readdirSync(join(dir, ".completion-gates/history"));
  assert.match(readFileSync(join(dir, ".completion-gates/history", epochs[0], "GATES.md"), "utf8"), /reviewed by hand/);
  gateCheck(dir, "freeze");
  assert.equal(gateCheck(dir, "status").status, 1);
});

test("reset clears live checkboxes and evidence too", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: manual\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  writeFileSync(join(dir, "GATES.md"), "# Gates: t\n\n- [x] G1: manual\n  EVIDENCE: reviewed by hand\n");
  gateCheck(dir, "reset", "--reason", "start over");
  assert.match(readFileSync(join(dir, "GATES.md"), "utf8"), /- \[ \] G1[^]*EVIDENCE: pending/);
  assert.equal(gateCheck(dir, "status").status, 1);
});

test("control validates --timeout like run does", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  for (const bad of ["nope", "-1", "0"]) {
    const r = gateCheck(dir, "control", "G1", "--timeout", bad);
    assert.equal(r.status, 2, bad);
    assert.match(r.stderr, /--timeout must be a positive number/);
  }
});

test("each control attempt keeps its own artifact", () => {
  const dir = freshGated("# Gates: t\n\n- [ ] G1: f\n  CHECK: test -f built.txt\n  CONTROL: required\n  EVIDENCE: pending\n");
  gateCheck(dir, "freeze");
  gateCheck(dir, "control", "G1");
  gateCheck(dir, "control", "G1");
  const state = JSON.parse(readFileSync(join(dir, ".completion-gates/state.json"), "utf8"));
  const [a, b] = state.gates.G1.controls.map((c) => c.artifact);
  assert.notEqual(a, b);
  assert.ok(existsSync(join(dir, a)) && existsSync(join(dir, b)));
});

test("removing a gate's EVIDENCE line after freeze is a live validation error", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  writeFileSync(join(dir, "GATES.md"), readFileSync(join(dir, "GATES.md"), "utf8").replace(/\n  EVIDENCE:[^\n]*/, ""));
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 2, st.stdout);
  assert.match(st.stderr, /G1 has no EVIDENCE line/);
});

test("a manifest frozen before CONTROL existed is refused until amended", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  const mp = join(dir, ".completion-gates/manifest.json");
  const m = JSON.parse(readFileSync(mp, "utf8"));
  for (const g of m.gates) delete g.control;
  writeFileSync(mp, JSON.stringify(m));
  const st = gateCheck(dir, "status");
  assert.equal(st.status, 2, st.stdout);
  assert.match(st.stderr, /manifest predates CONTROL/);
  assert.equal(gateCheck(dir, "amend", "--reason", "upgrade").status, 0);
  assert.equal(gateCheck(dir, "status").status, 1);
});

test("close archives artifacts-reset-* too and clears a stale close notice", () => {
  const dir = freshGated();
  gateCheck(dir, "freeze");
  gateCheck(dir, "close", "--reason", "abandoned"); // writes last-close.json, never consumed
  assert.ok(existsSync(join(dir, ".completion-gates/last-close.json")));
  gateCheck(dir, "freeze");
  gateCheck(dir, "run");
  gateCheck(dir, "reset", "--reason", "x"); // creates artifacts-reset-*
  assert.ok(readdirSync(join(dir, ".completion-gates")).some((f) => f.startsWith("artifacts-reset-")));
  gateCheck(dir, "run");
  assert.equal(gateCheck(dir, "close").status, 0);
  const top = readdirSync(join(dir, ".completion-gates"));
  assert.ok(!top.some((f) => f.startsWith("artifacts-reset-")), "reset archives moved into the epoch");
  assert.ok(!top.includes("last-close.json"), "stale notice cleared by a PROVEN close");
  assert.equal(stopHook(dir).stdout.trim(), "");
});

// ----------------------------------------------------------------

console.log(`\n${passed} passed, ${failed} failed`);
for (const d of tempDirs) rmSync(d, { recursive: true, force: true });
process.exit(failed ? 1 : 0);
