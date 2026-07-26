#!/usr/bin/env python3
"""Emit the Scenario 21 transcript-evidence artifact.

Every digest, count and manifest in the output is produced here at write time,
per the repo rule against hand-transcribed hashes. Nothing in the artifact is
typed by hand except its prose.

Run it against the run directory the arms wrote to:

    python3 hypothesis-driven-analysis/tests/runs/artifacts/build-scenario21-evidence.py \\
        --run-dir /path/to/s21run

The run directory holds `preedit-skill/SKILL.md`, one `transcripts/*.jsonl` per
arm, and `<batch>/<arm>/answer.md`. It is deliberately outside the repository —
arms run on private copies — so this script reproduces the artifact only while
that directory survives. Once it is gone the script still documents exactly how
the artifact was built, and the digests it emitted remain checkable against the
fixtures and `git show HEAD:...SKILL.md`.

The repository root is derived from this file's own location, so the script runs
wherever the repo is checked out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# .../hypothesis-driven-analysis/tests/runs/artifacts/<this file>
REPO = Path(__file__).resolve().parents[4]
HDA = REPO / "hypothesis-driven-analysis"
FIXTURES = HDA / "tests/fixtures/s21-status-disposition"
OUT = HDA / "tests/runs/artifacts/2026-07-25-scenario21-status-disposition-evidence.md"
EXTRACT = HDA / "tests/extract_evidence.py"

# Set by main() from --run-dir or $S21_RUN_DIR; module-level so the section
# helpers can normalize scratch paths out of the emitted text.
S = Path()

# ordinal, timestamp, tool, result status, target
MANIFEST_FIELDS = 5

# The prompt templates are reproduced byte-exactly, because their SHA-256 is what
# makes the archived per-arm prompts auditable. Reflowing them to satisfy the line
# length rule would change the hash and silently invalidate the artifact, so the
# rule is suppressed here rather than the text being edited.
# ruff: noqa: E501
PROMPT_REFUTE = """You are the main agent of an empirical investigation, resuming at a single decision point.

The skill governing your work is at {SKILL_MD} — read it and follow it.

Your status packet is {ARM_DIR}/packet.md

INPUT SCOPE (binding): the packet file and that SKILL.md are your ONLY inputs. Do not read any other file, do not read anything under /Users/bdc/projects/skills, and do not read anything under any tests/ directory. Do not run any git command whatsoever. Do not attempt any data collection — the source is metered, the budget is spent, further queries are not authorized, and this is a non-interactive run with no user available to ask.

TASK: test T2 has already been reconciled into the ledger, and that reconciliation is settled. Derive H2's status from the ledger as the skill dictates.

Write your answer to {ARM_DIR}/answer.md in exactly this form:

H2 STATUS: <the status you derive for H2 — name it exactly>
GOVERNING SKILL TEXT: <quote the sentence(s) from SKILL.md your derivation follows, verbatim>
REASONING: <a short paragraph>

Report the same content as your final message.
"""

PROMPT_SUPPORT = PROMPT_REFUTE.replace(
    "H2 STATUS: <the status you derive for H2 — name it exactly>\n",
    "H2 STATUS: <the status you derive for H2 — name it exactly>\n"
    "BEST SUPPORTED: <whether H2 may be reported as best supported, and on what basis>\n",
)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract(sub: str, path: Path, *extra: str) -> str:
    cmd = ["python3", str(EXTRACT), sub, str(path), *extra]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def arm_of(transcript: Path) -> tuple[str, str] | None:
    """Which batch and cell an arm belongs to, read from the packet it opened.

    Derived from the transcript rather than from dispatch order, so a mislabelled
    dispatch cannot silently attribute an answer to the wrong cell.
    """
    m = re.search(
        r"s21run/(pre|scored-pre)/([a-z0-9-]+)/packet\.md", extract("manifest", transcript)
    )
    return (m.group(1), m.group(2)) if m else None


def norm(text: str) -> str:
    return text.replace(str(S), "<SCRATCH>").replace(str(REPO), "<REPO_ROOT>")


def collect() -> dict[tuple[str, str], Path]:
    found = {}
    for f in sorted((S / "transcripts").glob("*.jsonl")):
        a = arm_of(f)
        if a:
            found[a] = f
    return dict(sorted(found.items()))


def read_answer(batch: str, arm: str) -> tuple[str, str, str]:
    ans = S / batch / arm / "answer.md"
    text = ans.read_text() if ans.exists() else ""
    st = re.search(r"^H2 STATUS:\s*(.+)$", text, re.M)
    bs = re.search(r"^BEST SUPPORTED:\s*(.+)$", text, re.M)
    return (
        st.group(1).strip().split()[0].rstrip(".,") if st else "MISSING",
        bs.group(1).strip().split()[0].rstrip(".,") if bs else "—",
        text,
    )


def scope_audit(transcript: Path) -> tuple[int, str, int, int]:
    """tool_use count, tool tally, reads outside scope, Bash calls."""
    man = extract("manifest", transcript).strip().splitlines()
    tools, outside, bash = [], 0, 0
    for line in man:
        parts = line.split("\t")
        if len(parts) < MANIFEST_FIELDS:
            continue
        tool, target = parts[2], parts[4]
        tools.append(tool)
        if tool == "Bash":
            bash += 1
        if tool == "Read" and "s21run" not in target:
            outside += 1
    tally = ", ".join(f"{t} x{tools.count(t)}" for t in sorted(set(tools)))
    return len(man), tally, outside, bash


def section_header(arms: dict) -> list[str]:
    return [
        "# Scenario 21 — transcript evidence (issue #113, Sixteenth wave, 2026-07-25)",
        "",
        "Generated programmatically by `build-scenario21-evidence.py`, archived beside this file;",
        "every digest is emitted by `hashlib` at write time and every manifest by",
        "`tests/extract_evidence.py`, per the repo rule against hand-transcribed hashes.",
        "",
        f"{len(arms)} Sonnet arms, **all against the pre-edit wording** — six canary (one per",
        "cell, fixture validation, excluded from the scored result per `PROTOCOL.md` step 4) and",
        "twelve scored (n=3 on the four decisive cells). No post-edit batch exists because no edit",
        "was made: the pre-edit arms answered correctly on every cell, so the wording change was",
        "declined. See `decisions/005-status-under-an-unverified-return.md`.",
        "",
    ]


def section_prompts() -> list[str]:
    return [
        "## Prompt templates",
        "",
        "Each arm's prompt is the template below with `{SKILL_MD}` and `{ARM_DIR}` substituted;",
        "only those paths differ between arms, which is what makes the cells comparable.",
        "",
        "```",
        f"{sha(PROMPT_REFUTE.encode())}  PROMPT-refute.txt",
        f"{sha(PROMPT_SUPPORT.encode())}  PROMPT-support.txt",
        "```",
        "",
        "### PROMPT-refute.txt (cells d1, d3, d4, d5)",
        "",
        "```",
        PROMPT_REFUTE.rstrip(),
        "```",
        "",
        "### PROMPT-support.txt (cells d6, d7)",
        "",
        "The same, with one added output field:",
        "",
        "```",
        "BEST SUPPORTED: <whether H2 may be reported as best supported, and on what basis>",
        "```",
        "",
    ]


def section_digests(skill_bytes: bytes, head_skill: bytes) -> list[str]:
    out = ["## Fixture digests", "", "```"]
    for p in sorted(FIXTURES.glob("*.md")):
        out.append(f"{sha(p.read_bytes())}  tests/fixtures/s21-status-disposition/{p.name}")
    out += [
        "```",
        "",
        "## Skill-file digest",
        "",
        "Every arm read this file. It is the unedited skill: the digest of the materialized copy",
        "and of `HEAD` were re-derived rather than trusted, and they match.",
        "",
        "```",
        f"{sha(skill_bytes)}  <SCRATCH>/preedit-skill/SKILL.md",
        f"{sha(head_skill)}  git show HEAD:hypothesis-driven-analysis/SKILL.md",
        "```",
        "",
        f"Match: {'yes' if sha(skill_bytes) == sha(head_skill) else 'NO — INVALID RUN'}",
        "",
    ]
    return out


def section_outcomes(arms: dict, rows: list) -> list[str]:
    out = [
        "## Outcomes",
        "",
        "| Batch | Cell | Arm | H2 status | Best supported |",
        "| --- | --- | --- | --- | --- |",
    ]
    for batch, arm in arms:
        st_v, bs_v, _ = read_answer(batch, arm)
        label = "canary" if batch == "pre" else "scored"
        rows.append((label, arm, st_v, bs_v))
        out.append(f"| {label} | {arm.rsplit('-', 1)[0]} | {arm} | `{st_v}` | {bs_v} |")
    out.append("")
    return out


def section_absence(arms: dict) -> tuple[list[str], int]:
    out = [
        f"## Machine-checked absence claims (all {len(arms)} arms)",
        "",
        "Each arm's binding input scope forbade any collection, any git command, and any read",
        "outside its packet and the named skill file. Verified from the transcripts, not from the",
        "arms' own reports.",
        "",
        "| Arm | tool_use | tools used | reads outside scope | Bash calls |",
        "| --- | --- | --- | --- | --- |",
    ]
    violations = 0
    for (batch, arm), f in arms.items():
        n, tally, outside, bash = scope_audit(f)
        if outside or bash:
            violations += 1
        out.append(f"| {arm} ({batch}) | {n} | {tally} | {outside} | {bash} |")
    out += ["", f"Arms violating input scope: **{violations}**", ""]
    return out, violations


def section_manifests(arms: dict) -> list[str]:
    out = [
        "## Tool-call manifests",
        "",
        "One line per `tool_use`, in JSONL serialization order: ordinal, timestamp, tool, result",
        "status, target. Paths normalized to `<REPO_ROOT>` and `<SCRATCH>`.",
        "",
    ]
    for (batch, arm), f in arms.items():
        out += [f"### {arm} ({batch})", "", "```", norm(extract("manifest", f).rstrip()), "```", ""]
    return out


def section_answers(arms: dict) -> list[str]:
    out = ["## Archived answers", ""]
    for batch, arm in arms:
        _, _, text = read_answer(batch, arm)
        body = norm(text.rstrip()) if text else "(no answer file written)"
        out += [f"### {arm} ({batch})", "", "```markdown", body, "```", ""]
    return out


def resolve_run_dir() -> Path:
    """The run directory, from --run-dir or $S21_RUN_DIR. Fails fast and says
    what it expected, rather than emitting a half-built artifact."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=os.environ.get("S21_RUN_DIR"),
        help="directory holding preedit-skill/, transcripts/ and <batch>/<arm>/answer.md",
    )
    args = ap.parse_args()
    if args.run_dir is None:
        ap.error("pass --run-dir or set S21_RUN_DIR (the arms' run directory)")
    run_dir = Path(args.run_dir).expanduser().resolve()
    for required in ("preedit-skill/SKILL.md", "transcripts"):
        if not (run_dir / required).exists():
            sys.exit(f"run directory {run_dir} has no {required}; is this the right --run-dir?")
    return run_dir


def main() -> None:
    global S  # noqa: PLW0603 — set once from the CLI before anything reads it
    S = resolve_run_dir()
    arms = collect()
    if not arms:
        sys.exit(f"no arm transcripts found under {S / 'transcripts'}")
    skill_bytes = (S / "preedit-skill/SKILL.md").read_bytes()
    head_skill = subprocess.run(
        ["git", "-C", str(REPO), "show", "HEAD:hypothesis-driven-analysis/SKILL.md"],
        capture_output=True,
        check=True,
    ).stdout

    rows: list[tuple] = []
    absence, violations = section_absence(arms)
    lines = (
        section_header(arms)
        + section_prompts()
        + section_digests(skill_bytes, head_skill)
        + section_outcomes(arms, rows)
        + absence
        + section_manifests(arms)
        + section_answers(arms)
    )
    # Sections end with a blank separator line; drop the trailing ones so a
    # regeneration matches the committed file byte for byte. Without this the
    # end-of-file-fixer hook strips them at commit time and every later run
    # shows a one-line diff that means nothing.
    while lines and not lines[-1].strip():
        lines.pop()
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}  ({len(lines)} lines, {len(arms)} arms)")
    print(f"input-scope violations: {violations}")
    print(json.dumps({f"{r[0]}:{r[1]}": f"{r[2]}/{r[3]}" for r in rows}, indent=0))


if __name__ == "__main__":
    main()
