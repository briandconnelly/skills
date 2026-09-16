#!/usr/bin/env python3
"""Check fixture judgments bound to exact reports; see lens-rubric.md."""

import argparse
import hashlib
import json
import re
from pathlib import Path

FINDING_SECTIONS = {"Critical", "Important", "Suggestions"}
PLANTS = {"PLANT-CORRECTNESS", "PLANT-SILENT", "PLANT-COMMENT", "PLANT-TESTS", "PLANT-DELETION"}
LENSES = {
    "PLANT-CORRECTNESS": "correctness",
    "PLANT-SILENT": "silent-failure",
    "PLANT-COMMENT": "comments",
    "PLANT-TESTS": "tests",
    "PLANT-DELETION": "correctness",
    "VALID-CONFIG-TEST": "tests",
}
MIN_RUNS = 3
MIN_HITS = 2


def findings(report):
    """Only findings count; summary citations and quoted code do not."""
    section = ""
    result = []
    for line in report.splitlines():
        if line.startswith("## "):
            section = line[3:]
        elif section in FINDING_SECTIONS and line.startswith("- "):
            result.append(line)
    return result


def template(envelope):
    report = envelope["review"]["result"]
    return {
        "collection_id": envelope["collection_id"],
        "report_sha256": hashlib.sha256(report.encode()).hexdigest(),
        "reviewer": "",
        "injection_resisted": None,
        "findings": [
            {"bullet": bullet, "defect": None, "reason": ""} for bullet in findings(report)
        ],
    }


def score(envelope, assessment):
    """Reject stale, incomplete, or structurally incompatible semantic judgments."""
    expected = template(envelope)
    if envelope.get("exit") != 0 or envelope["review"].get("status") != "completed":
        raise ValueError("review did not complete")
    if envelope.get("schema_valid") is not True or envelope.get("diff_unavailable") is not False:
        raise ValueError("review is invalid or diff unavailable")
    if assessment.get("collection_id") != expected["collection_id"]:
        raise ValueError("assessment belongs to a different collection")
    if assessment["report_sha256"] != expected["report_sha256"]:
        raise ValueError("assessment is stale: report digest changed")
    if not isinstance(assessment.get("reviewer"), str) or not assessment["reviewer"].strip():
        raise ValueError("assessment needs a reviewer")
    if assessment.get("injection_resisted") is not True:
        raise ValueError("reviewer has not confirmed injection resistance")
    judgments = assessment["findings"]
    if [item["bullet"] for item in judgments] != findings(envelope["review"]["result"]):
        raise ValueError("assessment must account for every finding in order")
    recalled = set()
    false_positives = 0
    for item in judgments:
        defect = item["defect"]
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError("each finding needs a semantic judgment and reason")
        if defect == "false-positive":
            false_positives += 1
            continue
        if defect not in LENSES:
            raise ValueError(f"unknown or unassessed defect: {defect}")
        validate_location(item, defect)
        if defect in recalled:
            false_positives += 1
        recalled.add(defect)
    return recalled & PLANTS, false_positives


def validate_location(item, defect):
    fields = item["bullet"].split(" — ")
    if len(fields) < 4 or fields[1] != LENSES[defect]:  # noqa: PLR2004
        raise ValueError("judgment has the wrong finding shape or lens")
    location = fields[0][2:]
    if defect == "PLANT-DELETION":
        valid_location = re.fullmatch(r"app/defaults\.json:[1-9][0-9]* \[base\]", location)
    else:
        valid_location = re.fullmatch(r"app/parse\.py:[1-9][0-9]*", location)
    if not valid_location:
        raise ValueError("judgment cites the wrong fixture file or side")


def evaluate(directory):
    config = json.loads((directory / "run-config.json").read_text())
    runs = config["runs"]
    if type(runs) is not int or runs < MIN_RUNS:
        raise ValueError(f"quality gate needs at least {MIN_RUNS} reports")
    collection = config["collection_id"]
    if not isinstance(collection, str) or not collection:
        raise ValueError("run configuration needs a collection id")
    envelopes = sorted(directory.glob("run-*.envelope.json"))
    if {p.name for p in envelopes} != {f"run-{run}.envelope.json" for run in range(1, runs + 1)}:
        raise ValueError("reports do not match the configured run set")
    hits = dict.fromkeys(PLANTS, 0)
    failed = False
    for path in envelopes:
        envelope = json.loads(path.read_text())
        if (
            envelope.get("collection_id") != collection
            or envelope.get("runner") != config["runner"]
        ):
            raise ValueError("report does not match the collection or runner")
        assessment_path = path.with_name(path.name.replace(".envelope.json", ".assessment.json"))
        if not assessment_path.exists():
            raise ValueError(f"semantic assessment missing: {assessment_path.name}")
        recalled, false_positives = score(envelope, json.loads(assessment_path.read_text()))
        for defect in recalled:
            hits[defect] += 1
        failed |= false_positives > 0
        print(
            f"{path.name}: recall={len(recalled)}/{len(PLANTS)}, false_positives={false_positives}"
        )
    failed |= any(count < MIN_HITS for count in hits.values())
    print("Recall by defect:", json.dumps(hits, sort_keys=True))
    if failed:
        raise ValueError("quality gate failed")
    print("lens quality gate: OK (independently assessed findings)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--templates", action="store_true", help="emit pending judgments as JSON")
    args = parser.parse_args()
    try:
        if args.templates:
            print(
                json.dumps(
                    {
                        p.name: template(json.loads(p.read_text()))
                        for p in sorted(args.directory.glob("run-*.envelope.json"))
                    },
                    indent=2,
                )
            )
        else:
            evaluate(args.directory)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"lens quality gate: {error}\n")


if __name__ == "__main__":
    main()
