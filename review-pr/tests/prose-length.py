#!/usr/bin/env python3
"""Measure report prose length per field; see lens-rubric.md (Prose length)."""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

SEP = " — "
SECTIONS = ("Summary", "Changes", "Critical", "Important", "Suggestions", "Not reviewed")
CONTRACT_LINES = ("Lenses checked:", "Mode:")
# A bullet needs four fields (location, lens, defect, impact); a fifth marks the title grammar.
MIN_FIELDS = 4


def words(text):
    return len(re.findall(r"\S+", text))


def sections(report):
    out = {}
    current = None
    for line in report.splitlines():
        m = re.fullmatch(r"## (.+)", line)
        if m and m[1] in SECTIONS:
            current = m[1]
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def findings(section_text, titled):
    """Finding bullets; `titled` says whether the report's grammar carries a title field."""
    for line in section_text.splitlines():
        if not line.startswith("- ") or line.strip() == "(none)":
            continue
        fields = line[2:].split(SEP)
        if len(fields) < MIN_FIELDS:
            continue
        fix = None
        if fields[-1].startswith("Fix: "):
            fix = fields.pop()[5:]
        impact = fields.pop()
        # v2: location, lens, title, defect...; v1 (no title): location, lens, defect...
        # A defect may contain the separator, so the field count cannot decide the grammar.
        has_title = titled and len(fields) > MIN_FIELDS - 1
        title = fields[2] if has_title else ""
        defect = SEP.join(fields[3:] if has_title else fields[2:])
        yield {"title": title, "defect": defect, "impact": impact, "fix": fix}


def measure(report):
    s = sections(report)
    summary = "\n".join(
        ln for ln in s.get("Summary", "").splitlines() if not ln.startswith(CONTRACT_LINES)
    )
    not_reviewed = s.get("Not reviewed", "")
    if not_reviewed.strip() == "(none)":
        not_reviewed = ""
    changes = s.get("Changes", "")
    # The Changes section arrived with the title grammar, so its presence selects the grammar.
    titled = "Changes" in s
    fs = [
        f
        for sec in ("Critical", "Important", "Suggestions")
        for f in findings(s.get(sec, ""), titled)
    ]
    per = {
        "summary": words(summary),
        "changes": words(changes),
        "not_reviewed": words(not_reviewed),
        "findings": len(fs),
        "title": [words(f["title"]) for f in fs],
        "defect": [words(f["defect"]) for f in fs],
        "impact": [words(f["impact"]) for f in fs],
        "fix": [words(f["fix"]) for f in fs if f["fix"] is not None],
        "fixes": sum(1 for f in fs if f["fix"] is not None),
        "total": words(report),
    }
    per["per_finding"] = (
        sum(per["defect"]) + sum(per["impact"]) + sum(per["fix"]) + sum(per["title"])
    )
    return per


def load_reports(snapshot):
    """Each run's report text, as score-lens.py reads it.

    A run without a report in its envelope falls back to the sibling native output. Codex
    writes that file as JSONL and a timeout can leave it partial, so an unreadable sibling
    means no report for an incomplete run and an error only for a run that claims completion.
    """
    for env in sorted(Path(snapshot).glob("run-*.envelope.json")):
        data = json.loads(env.read_text())
        review = data.get("review") or {}
        completed = data.get("exit") == 0 and review.get("status") == "completed"
        text = review.get("result")
        if text is None:
            sib = env.with_name(env.name.replace(".envelope.json", ".json"))
            if sib.exists():
                try:
                    text = json.loads(sib.read_text()).get("result")
                except ValueError:
                    if completed:
                        raise ValueError(
                            f"{env.name}: completed run has no readable report"
                        ) from None
                    text = None
        if text:
            yield env.name.split(".")[0], text


def summarize(rows):
    """Median per-run totals and mean per-finding field lengths across a snapshot."""

    def med(xs):
        return statistics.median(xs) if xs else 0

    def flat(key):
        return [x for r in rows for x in r[key]]

    return {
        "runs": len(rows),
        "summary": med([r["summary"] for r in rows]),
        "changes": med([r["changes"] for r in rows]),
        "not_reviewed": med([r["not_reviewed"] for r in rows]),
        "findings": med([r["findings"] for r in rows]),
        "title": round(statistics.fmean(flat("title")), 1) if flat("title") else 0,
        "defect": round(statistics.fmean(flat("defect")), 1) if flat("defect") else 0,
        "impact": round(statistics.fmean(flat("impact")), 1) if flat("impact") else 0,
        "fix": round(statistics.fmean(flat("fix")), 1) if flat("fix") else 0,
        "fixes": med([r["fixes"] for r in rows]),
        "total": med([r["total"] for r in rows]),
    }


def cell(value):
    """A whole number prints without a decimal point, whatever type the statistics gave it."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshots", nargs="+", help="snapshot directories")
    ap.add_argument(
        "--runs", action="store_true", help="print one row per run instead of per snapshot"
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cols = [
        "snapshot",
        "runs",
        "summary",
        "changes",
        "not_reviewed",
        "findings",
        "title",
        "defect",
        "impact",
        "fix",
        "fixes",
        "total",
    ]
    out = []
    for snap in args.snapshots:
        rows = [(run, measure(text)) for run, text in load_reports(snap)]
        if not rows:
            print(f"prose-length: no reports in {snap}", file=sys.stderr)
            continue
        if args.runs:
            # One row per run, in the same units as a snapshot row (per-finding means).
            out.extend({"snapshot": f"{snap}/{run}", **summarize([r])} for run, r in rows)
        else:
            out.append({"snapshot": snap, **summarize([r for _, r in rows])})
    if args.json:
        json.dump(out, sys.stdout, indent=1)
        return
    print("\t".join(cols))
    for row in out:
        print("\t".join(cell(row.get(c, "")) for c in cols))


if __name__ == "__main__":
    main()
