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
const ATTR_RE = /^(\s+)(CHECK|EXPECT|EXIT|EVIDENCE|FOR|CONTROL|CONTROL_EXPECT):\s?(.*)$/;
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
      if (abandoned.has(ab[1])) errors.push(`${file}:${i + 1}: ABANDON ${ab[1]} declared more than once`);
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
        control: null,
        control_expect: null,
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
      if (gate.expect !== null) {
        const rx = gate.expect.match(/^\/(.+)\/([a-z]*)$/);
        if (rx) {
          try {
            new RegExp(rx[1], rx[2]);
          } catch (e) {
            errors.push(`${p.file}: gate ${gate.id} EXPECT regex is invalid (${e.message})`);
          }
        }
      }
      if (!gate.check && (gate.expect !== null || gate.exit !== null))
        errors.push(`${p.file}: gate ${gate.id} has EXPECT/EXIT but no CHECK`);
      if (!gate.check && (gate.control !== null || gate.control_expect !== null))
        errors.push(`${p.file}: gate ${gate.id} has CONTROL without a CHECK`);
      if (gate.check) {
        if (gate.control === null)
          errors.push(`${p.file}: gate ${gate.id} has a CHECK but no CONTROL line (declare "required" or "exempt <reason>")`);
        else if (gate.control === "exempt")
          errors.push(`${p.file}: gate ${gate.id} CONTROL: exempt needs a reason`);
        else if (gate.control !== "required" && !/^exempt\s+\S/.test(gate.control))
          errors.push(`${p.file}: gate ${gate.id} CONTROL must be "required" or "exempt <reason>"`);
      }
      if (gate.control_expect !== null) {
        const rx = gate.control_expect.match(/^\/(.+)\/([a-z]*)$/);
        if (rx) {
          try {
            new RegExp(rx[1], rx[2]);
          } catch (e) {
            errors.push(`${p.file}: gate ${gate.id} CONTROL_EXPECT regex is invalid (${e.message})`);
          }
        }
      }
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
  for (const p of parsedFiles)
    for (const id of p.abandoned.keys())
      if (!ids.has(id)) errors.push(`${p.file}: ABANDON ${id} names no gate`);
  if (!gateCount) errors.push("no gates found");
  return errors;
}

// Checks the live gate files as a whole against the frozen manifest. Anything
// the per-gate resolution loop cannot see (a gate that exists only in the live
// file, a duplicated id, an ABANDON for nothing, a reworded criterion) is an
// error here, so status can never report on a ledger that differs from the
// contract in ways the ledger does not show.
export function validateLive(parsedFiles, manifest) {
  const errors = [];
  const manifestIds = new Set(manifest.gates.map((g) => g.id));
  const seen = new Set();
  for (const p of parsedFiles) {
    errors.push(...p.errors);
    for (const g of p.gates) {
      if (seen.has(g.id)) errors.push(`${p.file}: duplicate gate id ${g.id}`);
      seen.add(g.id);
      if (!manifestIds.has(g.id))
        errors.push(`${p.file}: gate ${g.id} is not in the frozen manifest (amend with a reason)`);
    }
    for (const id of p.abandoned.keys())
      if (!manifestIds.has(id)) errors.push(`${p.file}: ABANDON ${id} names no gate`);
  }
  const liveCriteria = new Map(parsedFiles.flatMap((p) => p.criteria).map((c) => [c.id, c.text.trim()]));
  const frozenCriteria = new Map((manifest.criteria || []).map((c) => [c.id, c.text.trim()]));
  for (const [id, text] of liveCriteria) {
    if (!frozenCriteria.has(id)) errors.push(`criterion ${id} added since freeze (amend with a reason)`);
    else if (frozenCriteria.get(id) !== text) errors.push(`criterion ${id} changed since freeze (amend with a reason)`);
  }
  for (const id of frozenCriteria.keys())
    if (!liveCriteria.has(id)) errors.push(`criterion ${id} removed since freeze (amend with a reason)`);
  return errors;
}

export const specOf = (g) => ({
  id: g.id,
  file: g.file,
  title: g.title,
  check: g.check,
  expect: g.expect,
  exit: g.exit,
  control: g.control,
  control_expect: g.control_expect,
  for: [...g.for].sort(),
});

export const controlRequired = (spec) => spec.control === "required";

// Identity of what a CHECK proves: the command, its expectation, and its exit
// code. Run and control records carry this so evidence recorded under an old
// spec cannot satisfy an amended one. FOR is excluded — retargeting a gate at
// a criterion does not change what the command demonstrated.
// CONTROL (required/exempt) is deliberately excluded: waiving a control must
// not invalidate the passing run. CONTROL_EXPECT is included because it
// changes what a control run demonstrates.
export function specFingerprint(spec) {
  return createHash("sha256")
    .update(JSON.stringify([spec.check, spec.expect, spec.exit ?? null, spec.control_expect ?? null]))
    .digest("hex")
    .slice(0, 16);
}

// Compares the enforceable parts of a spec (not the title, which is cosmetic).
export function specDrifted(a, b) {
  return (
    a.check !== b.check ||
    a.expect !== b.expect ||
    a.exit !== b.exit ||
    (a.control ?? null) !== (b.control ?? null) ||
    (a.control_expect ?? null) !== (b.control_expect ?? null) ||
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

// Latest control attempt for a gate, classified against the current spec.
function controlState(st, fp) {
  const attempts = st?.controls?.length ? st.controls : st?.control ? [st.control] : [];
  const latest = attempts[attempts.length - 1] || null;
  if (!latest) return { state: "none", latest: null, attempts: 0 };
  const state = latest.specFp !== fp ? "stale" : latest.outcome || (latest.failedAsExpected ? "ok" : "insensitive");
  return { state, latest, attempts: attempts.length };
}

// Revision number (1-based) in which a gate's CONTROL went from required to
// exempt, or null. A waiver is legal; it must be visible on the gate's row.
function waivedIn(manifest, id) {
  const revs = manifest.revisions || [];
  for (let i = revs.length - 1; i >= 0; i--)
    for (const ch of revs[i].changes)
      if (ch.op === "changed" && ch.id === id && ch.from?.control === "required" && ch.to?.control !== "required")
        return i + 1;
  return null;
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
  const parsedFiles = [];
  for (const f of manifest.files) {
    let text;
    try {
      text = readFileSync(join(cwd, f), "utf8");
    } catch {
      return { error: `gate file missing or unreadable: ${f}` };
    }
    const p = parseGateFile(text, f);
    parsedFiles.push(p);
    for (const [id, r] of p.abandoned) abandoned.set(id, r);
    for (const g of p.gates) currentById.set(g.id, g);
  }
  const liveErrors = validateLive(parsedFiles, manifest);
  if (liveErrors.length) return { error: liveErrors.join("; ") };

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
      const fp = specFingerprint(spec);
      const ctl = controlState(st, fp);
      if (controlRequired(spec) && ctl.state !== "ok") {
        resolution = "unmet";
        detail =
          ctl.state === "none"
            ? "control required, none recorded — run `control <id>` on the pre-fix state"
            : ctl.state === "stale"
              ? "control required but stale — spec amended since the control; re-run it"
              : `control required but ${ctl.state} — the CHECK has not been shown to fail`;
      } else if (!st || !st.status) {
        resolution = "unmet";
        detail = "no recorded run";
      } else if (st.specFp !== fp) {
        resolution = "unmet";
        detail = "spec amended since last run — re-run";
      } else if (st.status !== "pass") {
        resolution = "unmet";
        detail = `last run failed (exit ${st.exit})`;
      } else if (fingerprint && st.fingerprint && st.fingerprint !== fingerprint) {
        resolution = "stale";
        detail = "workspace changed since the passing run — re-run";
      } else if (controlRequired(spec) && ctl.latest.at > st.at) {
        resolution = "unmet";
        detail = "control recorded after the passing run — re-run";
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
    let control = null;
    let waived = null;
    if (spec.check) {
      const st = state.gates?.[spec.id];
      const ctl = controlState(st, specFingerprint(spec));
      const flags = [];
      if (ctl.attempts > 1) flags.push(`${ctl.attempts} attempts`);
      if (ctl.state === "ok" && st?.status === "pass" && st.fingerprint && ctl.latest.fingerprint === st.fingerprint)
        flags.push("same-workspace");
      control = flags.length ? `${ctl.state} (${flags.join(", ")})` : ctl.state;
      if (!controlRequired(spec)) {
        waived = waivedIn(manifest, spec.id);
        if (waived) control = `waived rev ${waived}`;
      }
    }
    rows.push({ id: spec.id, title: spec.title, runnable: !!spec.check, resolution, detail, control, waived: !!waived });
  }

  const count = (r) => rows.filter((x) => x.resolution === r).length;
  const counts = {
    proven: count("proven"),
    attested: count("attested"),
    abandoned: count("abandoned"),
    stale: count("stale"),
    unmet: count("unmet"),
    waived: rows.filter((x) => x.waived).length,
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
    const ctl = r.control ? ` [control: ${r.control}]` : "";
    out.push(`  ${label} ${r.id}: ${r.title}${ctl}${r.detail ? ` — ${r.detail}` : ""}`);
  }
  const c = status.counts;
  const parts = [];
  if (c.proven) parts.push(`${c.proven} proven`);
  if (c.attested) parts.push(`${c.attested} attested`);
  if (c.waived) parts.push(`${c.waived} waived`);
  if (c.abandoned) parts.push(`${c.abandoned} abandoned`);
  if (c.stale) parts.push(`${c.stale} stale`);
  if (c.unmet) parts.push(`${c.unmet} unmet`);
  out.push(`OVERALL: ${status.overall} (${parts.join(", ") || "0 gates"} of ${c.total})`);
  (status.manifest.revisions || []).forEach((rev, i) => {
    const ops = rev.changes.map((ch) => `${ch.op}${ch.id ? " " + ch.id : ""}`).join(", ");
    out.push(`  revision ${i + 1} ${rev.at}: ${rev.reason} (${ops})`);
  });
  if (!status.fingerprintAvailable)
    out.push("note: not a git repository — staleness tripwire unavailable");
  return out.join("\n");
}
