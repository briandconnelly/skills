#!/usr/bin/env node
// gate-check.mjs : freeze, run, and audit completion gates.
// Zero dependencies. Node 18+. Part of the completion-gates skill.
//
// Usage:
//   gate-check.mjs freeze [files...]               validate gate files, write the frozen manifest
//   gate-check.mjs reset --reason "<why>" [files]  replace the contract; prior revisions and a
//                                                  snapshot of the old contract stay in the manifest
//   gate-check.mjs run [--gate ID] [--timeout N]   execute unproven/stale CHECK gates from the manifest
//   gate-check.mjs status                          report only, change nothing
//   gate-check.mjs amend --reason "<why>"          record a visible spec revision after gate files change
//   gate-check.mjs control <ID> [--timeout N]      negative control: verify the CHECK can fail (run pre-fix)
//
// Exit codes: 0 = PROVEN, 1 = INCOMPLETE, 2 = usage/parse/drift error, 3 = INCOMPLETE-HANDOFF
// (abandoned gates present, everything else proven). An ABANDON line never produces exit 0.

import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync, rmSync, renameSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, relative, isAbsolute } from "node:path";
import {
  DIR,
  manifestPath,
  statePath,
  hookStatePath,
  artifactsDir,
  readJSON,
  atomicWriteJSON,
  parseGateFile,
  validateForFreeze,
  specOf,
  specDrifted,
  expectMatches,
  workspaceFingerprint,
  specFingerprint,
  computeStatus,
  formatLedger,
} from "./lib.mjs";

const cwd = process.cwd();
const argv = process.argv.slice(2);
const command = argv[0];

function fail(msg) {
  console.error(`gate-check: ${msg}`);
  process.exit(2);
}

// Deliberately positional-safe: consume flags and their values explicitly,
// everything left over is a positional argument, none silently dropped.
function parseArgs(rest, flagsWithValue = [], booleanFlags = []) {
  const flags = {};
  const positional = [];
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (flagsWithValue.includes(a)) {
      if (i + 1 >= rest.length) fail(`${a} requires a value`);
      flags[a.replace(/^--/, "")] = rest[++i];
    } else if (booleanFlags.includes(a)) {
      flags[a.replace(/^--/, "")] = true;
    } else if (a.startsWith("--")) {
      fail(`unknown flag ${a}`);
    } else {
      positional.push(a);
    }
  }
  return { flags, positional };
}

const relPath = (p) => (isAbsolute(p) ? relative(cwd, p) : p).replaceAll("\\", "/");

function discoverDefaultFiles() {
  const found = [];
  if (existsSync(join(cwd, "GATES.md"))) found.push("GATES.md");
  const gdir = join(cwd, "gates");
  if (existsSync(gdir))
    for (const f of readdirSync(gdir).sort()) if (f.endsWith(".md")) found.push(`gates/${f}`);
  return found;
}

function parseFiles(files) {
  return files.map((f) => {
    let text;
    try {
      text = readFileSync(join(cwd, f), "utf8");
    } catch (e) {
      fail(`cannot read ${f}: ${e.message}`);
    }
    return parseGateFile(text, f);
  });
}

function exitForStatus(status) {
  console.log(formatLedger(status));
  process.exit(status.overall === "PROVEN" ? 0 : status.overall === "INCOMPLETE-HANDOFF" ? 3 : 1);
}

function loadManifestOrFail() {
  const manifest = readJSON(manifestPath(cwd));
  if (!manifest) fail("no manifest — run `gate-check.mjs freeze` first");
  return manifest;
}

function runCheck(spec, timeoutSec) {
  const res = spawnSync(spec.check, {
    cwd,
    shell: true,
    encoding: "utf8",
    timeout: timeoutSec * 1000,
    maxBuffer: 8 * 1024 * 1024,
  });
  const output = `${res.stdout || ""}\n${res.stderr || ""}`;
  const timedOut = res.error?.code === "ETIMEDOUT" || (res.status === null && res.signal);
  const expectedExit = spec.exit === null ? 0 : Number(spec.exit);
  // Both must hold — an EXPECT match never excuses a wrong exit status.
  const pass = !timedOut && res.status === expectedExit && (!spec.expect || expectMatches(spec.expect, output));
  return { pass, exit: res.status, timedOut, output };
}

function writeArtifact(id, output) {
  mkdirSync(artifactsDir(cwd), { recursive: true });
  const rel = `${DIR}/artifacts/${id}.log`;
  writeFileSync(join(cwd, rel), output);
  return rel;
}

// Rewrites only the checkbox and EVIDENCE lines of one gate in its file.
// Evidence is metadata only — raw output stays in the untracked artifact file,
// so secrets a CHECK prints never land in a tracked markdown file.
function recordInMarkdown(file, gateId, pass, summary) {
  const path = join(cwd, file);
  const lines = readFileSync(path, "utf8").split(/\r?\n/);
  const parsed = parseGateFile(lines.join("\n"), file);
  const gate = parsed.gates.find((g) => g.id === gateId);
  if (!gate) return;
  lines[gate.line] = lines[gate.line].replace(/^- \[( |x|X)\]/, pass ? "- [x]" : "- [ ]");
  if (gate.evidenceLine !== -1) {
    const indent = lines[gate.evidenceLine].match(/^\s*/)[0];
    lines[gate.evidenceLine] = `${indent}EVIDENCE: ${summary}`;
  }
  writeFileSync(path, lines.join("\n"));
}

// Validates the given (or discovered) gate files and returns the contract
// they define. Shared by freeze and reset; both refuse on any validation error.
function buildContract(positional) {
  const files = positional.length ? positional.map(relPath) : discoverDefaultFiles();
  if (!files.length) fail("no gate files found (GATES.md or gates/*.md) and none given");
  const parsed = parseFiles(files);
  const errors = validateForFreeze(parsed);
  if (errors.length) {
    for (const e of errors) console.error(`  ${e}`);
    fail(`${errors.length} validation error(s) — fix the gate files, then try again`);
  }
  return { files, criteria: parsed.flatMap((p) => p.criteria), gates: parsed.flatMap((p) => p.gates.map(specOf)) };
}

function writeManifest(contract, revisions) {
  atomicWriteJSON(manifestPath(cwd), {
    schema: 1,
    frozen_at: new Date().toISOString(),
    files: contract.files,
    criteria: contract.criteria,
    gates: contract.gates,
    revisions,
  });
  // state, hook state, and artifacts are machine-local; the manifest itself is auditable and committable
  writeFileSync(join(cwd, DIR, ".gitignore"), "state.json\nhook-state.json\nartifacts/\nartifacts-reset-*/\n*.tmp\n");
  console.log(`Frozen ${contract.gates.length} gates (${contract.criteria.length} criteria) from: ${contract.files.join(", ")}`);
  console.log("Review the commands this manifest authorizes for execution:");
  for (const g of contract.gates) if (g.check) console.log(`  ${g.id}: ${g.check}`);
}

// ---------------------------------------------------------------- freeze
if (command === "freeze") {
  const { positional } = parseArgs(argv.slice(1), [], []);
  if (existsSync(manifestPath(cwd)))
    fail("manifest already exists — use `amend --reason` to change the contract, or `reset --reason` to replace it");
  writeManifest(buildContract(positional), []);
  process.exit(0);
}

// ---------------------------------------------------------------- reset
// The only way to replace a contract wholesale. Nothing is erased: the old
// contract is snapshotted into a revision, old artifacts are archived, and
// only machine-local run/hook state (which described the old contract) goes.
if (command === "reset") {
  const { flags, positional } = parseArgs(argv.slice(1), ["--reason"], []);
  if (!flags.reason?.trim()) fail('reset requires --reason "<why the contract is being replaced>"');
  if (!existsSync(manifestPath(cwd))) fail("no manifest to reset — use `freeze`");
  const prev = readJSON(manifestPath(cwd));
  if (!prev) fail("existing manifest is unreadable — inspect or remove .completion-gates/manifest.json by hand; reset will not overwrite it blindly");

  const contract = buildContract(positional);
  const at = new Date().toISOString();
  const revisions = [
    ...(prev.revisions || []),
    {
      at,
      reason: flags.reason.trim(),
      changes: [{ op: "reset", previous: { frozen_at: prev.frozen_at, files: prev.files, criteria: prev.criteria, gates: prev.gates } }],
    },
  ];
  rmSync(statePath(cwd), { force: true });
  rmSync(hookStatePath(cwd), { force: true });
  if (existsSync(artifactsDir(cwd)))
    renameSync(artifactsDir(cwd), join(cwd, DIR, `artifacts-reset-${at.replace(/[:.]/g, "-")}`));
  writeManifest(contract, revisions);
  console.log(`Revision ${revisions.length} recorded (reset): ${flags.reason.trim()} — surface it in your final report.`);
  process.exit(0);
}

// ---------------------------------------------------------------- run
if (command === "run" || command === undefined) {
  const { flags } = parseArgs(argv.slice(1), ["--gate", "--timeout"], []);
  const timeoutSec = flags.timeout ? Number(flags.timeout) : 120;
  if (!Number.isFinite(timeoutSec) || timeoutSec <= 0) fail("--timeout must be a positive number");
  loadManifestOrFail();

  let status = computeStatus(cwd);
  if (status.error) fail(status.error);

  const drifted = status.rows.filter((r) => r.detail.includes("drift"));
  if (drifted.length)
    fail(
      `spec drift on ${drifted.map((r) => r.id).join(", ")} — the gate files no longer match the frozen manifest; run \`amend --reason\` to record the change`,
    );

  const runnable = status.manifest.gates.filter((g) => {
    if (!g.check) return false;
    if (flags.gate && g.id !== flags.gate) return false;
    const row = status.rows.find((r) => r.id === g.id);
    return row.resolution === "unmet" || row.resolution === "stale";
  });
  if (flags.gate && !runnable.length && !status.manifest.gates.some((g) => g.id === flags.gate))
    fail(`no gate named ${flags.gate} in the manifest`);

  const state = readJSON(statePath(cwd), { schema: 1, gates: {} });
  const ranNow = [];
  for (const spec of runnable) {
    const res = runCheck(spec, timeoutSec);
    const artifact = writeArtifact(spec.id, res.output);
    const at = new Date().toISOString();
    state.gates[spec.id] = {
      ...(state.gates[spec.id] || {}), // preserve control records — they are part of the audit trail
      status: res.pass ? "pass" : "fail",
      exit: res.exit,
      at,
      artifact,
      specFp: specFingerprint(spec),
    };
    const why = res.timedOut ? `timeout after ${timeoutSec}s` : `exit=${res.exit}`;
    recordInMarkdown(spec.file, spec.id, res.pass, `${res.pass ? "pass" : "FAIL"} ${why} ${at} artifact=${artifact}`);
    console.log(`  ${res.pass ? "PASS" : "FAIL"} ${spec.id}: ${spec.title} (${why})`);
    if (res.pass) ranNow.push(spec.id);
  }

  // One fingerprint for the whole invocation, taken after every check ran,
  // so a check that writes build output doesn't immediately stale its siblings.
  const fp = workspaceFingerprint(cwd, status.manifest.files);
  for (const id of ranNow) state.gates[id].fingerprint = fp;
  atomicWriteJSON(statePath(cwd), state);

  status = computeStatus(cwd);
  if (status.error) fail(status.error);
  exitForStatus(status);
}

// ---------------------------------------------------------------- status
if (command === "status") {
  const status = computeStatus(cwd);
  if (status.error) fail(status.error);
  exitForStatus(status);
}

// ---------------------------------------------------------------- amend
if (command === "amend") {
  const { flags, positional } = parseArgs(argv.slice(1), ["--reason"], []);
  if (!flags.reason?.trim()) fail("amend requires --reason \"<why the contract changed>\"");
  const manifest = loadManifestOrFail();

  const files = [...new Set([...manifest.files, ...positional.map(relPath)])];
  const parsed = parseFiles(files);
  const errors = validateForFreeze(parsed);
  if (errors.length) {
    for (const e of errors) console.error(`  ${e}`);
    fail(`${errors.length} validation error(s) — fix the gate files, then amend again`);
  }

  const nextGates = parsed.flatMap((p) => p.gates.map(specOf));
  const prevById = new Map(manifest.gates.map((g) => [g.id, g]));
  const nextById = new Map(nextGates.map((g) => [g.id, g]));
  const changes = [];
  for (const [id, g] of nextById)
    if (!prevById.has(id)) changes.push({ op: "added", id, spec: g });
    else if (specDrifted(prevById.get(id), g))
      changes.push({ op: "changed", id, from: prevById.get(id), to: g });
  for (const id of prevById.keys())
    if (!nextById.has(id)) changes.push({ op: "removed", id, spec: prevById.get(id) });
  const nextCriteria = parsed.flatMap((p) => p.criteria);
  const prevCrit = new Map((manifest.criteria || []).map((c) => [c.id, c.text.trim()]));
  const nextCrit = new Map(nextCriteria.map((c) => [c.id, c.text.trim()]));
  for (const [id, text] of nextCrit)
    if (!prevCrit.has(id)) changes.push({ op: "criterion-added", id, to: text });
    else if (prevCrit.get(id) !== text) changes.push({ op: "criterion-changed", id, from: prevCrit.get(id), to: text });
  for (const [id, text] of prevCrit)
    if (!nextCrit.has(id)) changes.push({ op: "criterion-removed", id, from: text });
  if (!changes.length) fail("nothing to amend — gate specs and criteria match the manifest");

  manifest.files = files;
  manifest.criteria = nextCriteria;
  manifest.gates = nextGates;
  manifest.revisions.push({ at: new Date().toISOString(), reason: flags.reason.trim(), changes });
  atomicWriteJSON(manifestPath(cwd), manifest);

  console.log(`Revision ${manifest.revisions.length} recorded: ${flags.reason.trim()}`);
  for (const c of changes) {
    let detail = "";
    if (c.op === "changed")
      detail = `: spec now ${JSON.stringify({ check: c.to.check, expect: c.to.expect, exit: c.to.exit, control: c.to.control, control_expect: c.to.control_expect, for: c.to.for })}`;
    else if (c.op.startsWith("criterion") && c.to) detail = `: ${JSON.stringify(c.to)}`;
    console.log(`  ${c.op} ${c.id}${detail}`);
  }
  console.log("Surface this revision (and its reason) in your final report.");
  process.exit(0);
}

// ---------------------------------------------------------------- control
if (command === "control") {
  const { flags, positional } = parseArgs(argv.slice(1), ["--timeout"], []);
  const id = positional[0];
  if (!id) fail("control requires a gate id");
  const manifest = loadManifestOrFail();
  const spec = manifest.gates.find((g) => g.id === id);
  if (!spec) fail(`no gate named ${id} in the manifest`);
  if (!spec.check) fail(`${id} is a manual gate — negative controls apply to CHECK gates`);

  const timeoutSec = flags.timeout ? Number(flags.timeout) : 120;
  const res = runCheck(spec, timeoutSec);
  const artifact = writeArtifact(`${id}.control`, res.output);
  // Outcomes, never collapsed to one boolean. "ok" means the CHECK did not
  // pass (and, with CONTROL_EXPECT, failed with the expected signature) — it
  // does not prove the failure was caused by the missing fix.
  let outcome;
  let why;
  if (res.timedOut || res.exit === null) {
    outcome = "invalid";
    why = res.timedOut ? `timeout after ${timeoutSec}s` : "could not run";
  } else if (res.exit === 126 || res.exit === 127) {
    outcome = "invalid";
    why = `exit=${res.exit} (command not found or not executable)`;
  } else if (res.pass) {
    outcome = "insensitive";
  } else if (spec.control_expect && !expectMatches(spec.control_expect, res.output)) {
    outcome = "invalid";
    why = `exit=${res.exit} but output did not match CONTROL_EXPECT ${JSON.stringify(spec.control_expect)}`;
  } else {
    outcome = "ok";
  }
  const state = readJSON(statePath(cwd), { schema: 1, gates: {} });
  const prior = state.gates[id] || {};
  const record = {
    at: new Date().toISOString(),
    outcome,
    failedAsExpected: outcome === "ok",
    exit: res.exit,
    timedOut: res.timedOut,
    artifact,
    specFp: specFingerprint(spec),
    fingerprint: workspaceFingerprint(cwd, manifest.files),
  };
  // A control invalidates any earlier run: evidence must be recorded in the
  // order control -> fix -> run, or the control shows nothing about the fix.
  const { status: _s, exit: _e, at: _a, artifact: _ar, fingerprint: _f, specFp: _sf, ...rest } = prior;
  state.gates[id] = { ...rest, controls: [...(prior.controls || (prior.control ? [prior.control] : [])), record], control: record };
  atomicWriteJSON(statePath(cwd), state);

  if (outcome === "invalid") {
    console.log(`CONTROL INVALID for ${id}: ${why} — this shows nothing about sensitivity.`);
    process.exit(1);
  }
  if (outcome === "insensitive") {
    console.log(`CONTROL FAILED for ${id}: the CHECK already passes, so it cannot demonstrate sensitivity.`);
    console.log("Run controls on the pre-fix state, or sharpen the CHECK until it fails without the work.");
    process.exit(1);
  }
  console.log(`CONTROL OK for ${id}: the CHECK fails without the work (exit=${res.exit}). Recorded; any earlier run is invalidated.`);
  process.exit(0);
}

fail(`unknown command "${command}" (expected freeze | run | status | amend | reset | control)`);
