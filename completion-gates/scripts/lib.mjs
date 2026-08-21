// lib.mjs : shared parsing, fingerprinting, and status computation for completion-gates.
// Zero dependencies. Node 18+.

import {
  readFileSync,
  writeFileSync,
  renameSync,
  mkdirSync,
  statSync,
} from "node:fs";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";

export const DIR = ".completion-gates";
export const manifestPath = (cwd) => join(cwd, DIR, "manifest.json");
export const statePath = (cwd) => join(cwd, DIR, "state.json");
export const hookStatePath = (cwd) => join(cwd, DIR, "hook-state.json");
export const artifactsDir = (cwd) => join(cwd, DIR, "artifacts");

export function readJSON(path, fallback = null) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return fallback;
  }
}

export function atomicWriteJSON(path, obj) {
  mkdirSync(dirname(path), { recursive: true });
  const tmp = `${path}.${process.pid}.tmp`;
  writeFileSync(tmp, JSON.stringify(obj, null, 2) + "\n");
  renameSync(tmp, path);
}

const GATE_RE = /^- \[( |x|X)\] (.*)$/;
const ATTR_RE = /^(\s+)(CHECK|EXPECT|EXIT|EVIDENCE|FOR):\s?(.*)$/;
const ABANDON_RE = /^ABANDON:\s*(\S+?):?(?:\s+(.*))?$/;
const CRITERION_RE = /^- (\S+?):\s+(.*)$/;

export function parseGateFile(text, file) {
  const lines = text.split(/\r?\n/);
  const gates = [];
  const criteria = [];
  const abandoned = new Map(); // id -> reason
  const errors = [];
  let cur = null;
  let inCriteria = false;

  lines.forEach((line, i) => {
    if (/^#/.test(line)) {
      inCriteria = /^##\s+criteria\b/i.test(line);
      cur = null;
      return;
    }
    const ab = line.match(ABANDON_RE);
    if (ab) {
      const reason = (ab[2] || "").trim();
      if (!reason) errors.push(`${file}:${i + 1}: ABANDON ${ab[1]} has no reason`);
      abandoned.set(ab[1], reason || "(no reason)");
      cur = null;
      return;
    }
    const g = line.match(GATE_RE);
    if (g) {
      inCriteria = false; // a checkbox gate ends the criteria section
      const m = g[2].match(/^(\S+?):\s*(.*)$/);
      if (!m) {
        errors.push(`${file}:${i + 1}: gate has no "<id>:" prefix`);
        cur = null;
        return;
      }
      cur = {
        file,
        line: i,
        id: m[1],
        title: m[2],
        checked: g[1].toLowerCase() === "x",
        check: null,
        expect: null,
        exit: null,
        evidence: null,
        evidenceLine: -1,
        for: [],
      };
      gates.push(cur);
      return;
    }
    const a = cur && line.match(ATTR_RE);
    if (a) {
      const key = a[2].toLowerCase();
      const val = a[3].trim();
      if (key === "evidence") {
        cur.evidence = val;
        cur.evidenceLine = i;
      } else if (key === "for") {
        cur.for = val.split(/[,\s]+/).filter(Boolean);
      } else {
        cur[key] = val;
      }
      return;
    }
    if (inCriteria) {
      const c = line.match(CRITERION_RE);
      if (c) criteria.push({ id: c[1], text: c[2] });
      return;
    }
    if (/^- /.test(line)) cur = null; // an unrelated list item ends the gate block
  });

  return { file, lines, gates, criteria, abandoned, errors };
}

export function validateForFreeze(parsedFiles) {
  const errors = [];
  const ids = new Set();
  const allCriteria = new Map(); // id -> { covered }
  let gateCount = 0;

  for (const p of parsedFiles) {
    errors.push(...p.errors);
    for (const c of p.criteria) {
      if (allCriteria.has(c.id)) errors.push(`duplicate criterion id ${c.id}`);
      allCriteria.set(c.id, { covered: false });
    }
  }
  for (const p of parsedFiles) {
    for (const gate of p.gates) {
      gateCount++;
      if (ids.has(gate.id)) errors.push(`${p.file}: duplicate gate id ${gate.id}`);
      ids.add(gate.id);
      if (gate.evidenceLine === -1)
        errors.push(`${p.file}: gate ${gate.id} has no EVIDENCE line`);
      if (gate.exit !== null && !/^\d+$/.test(gate.exit))
        errors.push(`${p.file}: gate ${gate.id} EXIT is not a non-negative integer`);
      if (!gate.check && (gate.expect !== null || gate.exit !== null))
        errors.push(`${p.file}: gate ${gate.id} has EXPECT/EXIT but no CHECK`);
      for (const f of gate.for) {
        const c = allCriteria.get(f);
        if (!c) errors.push(`${p.file}: gate ${gate.id} FOR references unknown criterion ${f}`);
        else c.covered = true;
      }
      if (allCriteria.size && !gate.for.length)
        errors.push(
          `${p.file}: gate ${gate.id} has no FOR line (criteria are declared, so traceability is required)`,
        );
    }
  }
  for (const [id, c] of allCriteria)
    if (!c.covered) errors.push(`criterion ${id} is mapped to no gate (unmapped acceptance criterion)`);
  if (!gateCount) errors.push("no gates found");
  return errors;
}

export const specOf = (g) => ({
  id: g.id,
  file: g.file,
  title: g.title,
  check: g.check,
  expect: g.expect,
  exit: g.exit,
  for: [...g.for].sort(),
});

// Compares the enforceable parts of a spec (not the title, which is cosmetic).
export function specDrifted(a, b) {
  return (
    a.check !== b.check ||
    a.expect !== b.expect ||
    a.exit !== b.exit ||
    JSON.stringify([...(a.for || [])].sort()) !== JSON.stringify([...(b.for || [])].sort())
  );
}

export function expectMatches(expect, output) {
  const rx = expect.match(/^\/(.+)\/([a-z]*)$/);
  if (rx) {
    try {
      return new RegExp(rx[1], rx[2]).test(output);
    } catch {
      return false;
    }
  }
  return output.includes(expect);
}

// Tripwire, not a security boundary: hashes HEAD plus the dirty-file list
// (with mtime+size) so evidence recorded before a workspace change reads as
// stale. Gate files and this skill's own state directory are excluded so
// bookkeeping writes don't invalidate evidence. Returns null outside git.
export function workspaceFingerprint(cwd, excludePaths = []) {
  try {
    const git = (args) =>
      execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
    const head = git(["rev-parse", "HEAD"]).trim();
    const entries = [];
    for (const l of git(["status", "--porcelain"]).split("\n")) {
      if (!l) continue;
      let p = l.slice(3);
      const arrow = p.indexOf(" -> ");
      if (arrow !== -1) p = p.slice(arrow + 4);
      p = p.replace(/^"|"$/g, "");
      if (p === DIR || p.startsWith(DIR + "/") || excludePaths.includes(p)) continue;
      let stat = "gone";
      try {
        const s = statSync(join(cwd, p));
        stat = `${s.mtimeMs}:${s.size}`;
      } catch {
        /* deleted file */
      }
      entries.push(`${l.slice(0, 2)} ${p} ${stat}`);
    }
    entries.sort();
    return createHash("sha256").update(`${head}\n${entries.join("\n")}`).digest("hex").slice(0, 16);
  } catch {
    return null;
  }
}

// Resolves every manifest gate to exactly one state:
//   proven     runnable gate with a recorded passing run that is still fresh
//   attested   manual gate, checked with non-pending evidence (trust-based)
//   abandoned  named by an ABANDON line (visible surrender, never success)
//   stale      passing run recorded, but the workspace changed since
//   unmet      everything else, including spec drift vs the manifest
export function computeStatus(cwd) {
  const manifest = readJSON(manifestPath(cwd));
  if (!manifest) return { error: "no manifest — run `gate-check.mjs freeze` first" };
  const state = readJSON(statePath(cwd), { gates: {} });
  const fingerprint = workspaceFingerprint(cwd, manifest.files);

  const abandoned = new Map();
  const currentById = new Map();
  const parseErrors = [];
  for (const f of manifest.files) {
    let text;
    try {
      text = readFileSync(join(cwd, f), "utf8");
    } catch {
      return { error: `gate file missing or unreadable: ${f}` };
    }
    const p = parseGateFile(text, f);
    parseErrors.push(...p.errors);
    for (const [id, r] of p.abandoned) abandoned.set(id, r);
    for (const g of p.gates) currentById.set(g.id, g);
  }
  if (parseErrors.length) return { error: parseErrors.join("; ") };

  const rows = [];
  for (const spec of manifest.gates) {
    const cur = currentById.get(spec.id);
    let resolution;
    let detail = "";
    if (abandoned.has(spec.id)) {
      resolution = "abandoned";
      detail = abandoned.get(spec.id);
    } else if (!cur) {
      resolution = "unmet";
      detail = "gate removed from file (spec drift — amend the manifest)";
    } else if (specDrifted(spec, specOf(cur))) {
      resolution = "unmet";
      detail = "spec drifted from frozen manifest (amend with a reason, then re-run)";
    } else if (spec.check) {
      const st = state.gates?.[spec.id];
      if (!st || st.status !== "pass") {
        resolution = "unmet";
        detail = st?.status ? `last run failed (exit ${st.exit})` : "no recorded run";
      } else if (fingerprint && st.fingerprint && st.fingerprint !== fingerprint) {
        resolution = "stale";
        detail = "workspace changed since the passing run — re-run";
      } else {
        resolution = "proven";
      }
    } else {
      const ev = cur.evidence && !/^pending$/i.test(cur.evidence);
      if (cur.checked && ev) {
        resolution = "attested";
      } else {
        resolution = "unmet";
        detail = !cur.checked ? "unchecked" : "EVIDENCE still pending";
      }
    }
    rows.push({ id: spec.id, title: spec.title, runnable: !!spec.check, resolution, detail });
  }

  const count = (r) => rows.filter((x) => x.resolution === r).length;
  const counts = {
    proven: count("proven"),
    attested: count("attested"),
    abandoned: count("abandoned"),
    stale: count("stale"),
    unmet: count("unmet"),
    total: rows.length,
  };
  const overall =
    counts.unmet || counts.stale
      ? "INCOMPLETE"
      : counts.abandoned
        ? "INCOMPLETE-HANDOFF"
        : "PROVEN";

  return { manifest, state, rows, counts, overall, fingerprint, fingerprintAvailable: fingerprint !== null };
}

export function formatLedger(status) {
  const out = [];
  for (const r of status.rows) {
    const label = r.resolution.toUpperCase().padEnd(9);
    out.push(`  ${label} ${r.id}: ${r.title}${r.detail ? ` — ${r.detail}` : ""}`);
  }
  const c = status.counts;
  const parts = [];
  if (c.proven) parts.push(`${c.proven} proven`);
  if (c.attested) parts.push(`${c.attested} attested`);
  if (c.abandoned) parts.push(`${c.abandoned} abandoned`);
  if (c.stale) parts.push(`${c.stale} stale`);
  if (c.unmet) parts.push(`${c.unmet} unmet`);
  out.push(`OVERALL: ${status.overall} (${parts.join(", ") || "0 gates"} of ${c.total})`);
  if (!status.fingerprintAvailable)
    out.push("note: not a git repository — staleness tripwire unavailable");
  return out.join("\n");
}
