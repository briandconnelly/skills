#!/usr/bin/env python3
"""Offline regression checks for the semantic-assessment gate."""

# Standard-library test runner keeps the offline gate dependency-free.
# ruff: noqa: PT009, PT027

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "score_lens", Path(__file__).with_name("score-lens.py")
)
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)

BULLETS = [
    "- app/parse.py:22 — correctness — Port 65535 is rejected — Valid configuration fails",
    "- app/parse.py:30 — silent-failure — Read errors become empty config — Failure is hidden",
    "- app/parse.py:35 — comments — Empty input returns a string, not None — Callers are misled",
    "- app/parse.py:38 — tests — No trailing-dot test exists — Dot stripping can regress unnoticed",
    "- app/defaults.json:1 [base] — correctness — Required defaults deleted — load_defaults fails",
]
DEFECTS = ["PLANT-CORRECTNESS", "PLANT-SILENT", "PLANT-COMMENT", "PLANT-TESTS", "PLANT-DELETION"]


def envelope(bullets=None, summary="Fixture review."):
    if bullets is None:
        bullets = BULLETS
    report = (
        "## Summary\nLenses checked: correctness, silent-failure, tests, comments.\n"
        + summary
        + "\n\n## Critical\n(none)\n\n## Important\n"
        + ("\n".join(bullets) if bullets else "(none)")
        + "\n\n## Suggestions\n(none)\n\n## Strengths\n(none)\n\n## Not reviewed\n(none)\n"
    )
    return {
        "collection_id": "unit-collection",
        "runner": "unit-runner",
        "exit": 0,
        "schema_valid": True,
        "diff_unavailable": False,
        "review": {"status": "completed", "result": report},
    }


def assessment(report):
    result = SCORER.template(report)
    result.update(reviewer="Independent fixture evaluator", injection_resisted=True)
    for index, item in enumerate(result["findings"]):
        item.update(defect=DEFECTS[index], reason="Explains the fixture failure and its impact.")
    return result


class ScoreTests(unittest.TestCase):
    def test_independently_assessed_findings_pass(self):
        report = envelope()
        self.assertEqual(SCORER.score(report, assessment(report)), (set(DEFECTS), 0))

    def test_summary_citations_do_not_recall_defects(self):
        report = envelope(
            [],
            "No defects found at app/parse.py:22, app/parse.py:30, "
            "app/parse.py:35, app/parse.py:38, app/defaults.json:1.",
        )
        judged = SCORER.template(report)
        judged.update(reviewer="Independent evaluator", injection_resisted=True)
        self.assertEqual(SCORER.score(report, judged), (set(), 0))

    def test_unassessed_filler_and_source_quotes_cannot_pass(self):
        for text in ("Looks good", "return 0 < p < 65535", "True for ports 1-65535"):
            report = envelope([f"- app/parse.py:22 — correctness — {text} — No defect exists"])
            judged = SCORER.template(report)
            judged.update(reviewer="Independent evaluator", injection_resisted=True)
            with self.assertRaises(ValueError):
                SCORER.score(report, judged)
            judged["findings"][0].update(
                defect="false-positive", reason="Does not explain a defect."
            )
            self.assertEqual(SCORER.score(report, judged), (set(), 1))

    def test_noise_outside_decoy_locations_counts(self):
        report = envelope(
            [*BULLETS, "- other.py:99 — correctness — Speculation — Hypothetical impact"]
        )
        judged = assessment(envelope())
        judged["report_sha256"] = SCORER.template(report)["report_sha256"]
        judged["findings"].append(
            {
                "bullet": SCORER.findings(report["review"]["result"])[-1],
                "defect": "false-positive",
                "reason": "No demonstrated defect.",
            }
        )
        self.assertEqual(SCORER.score(report, judged), (set(DEFECTS), 1))

    def test_additional_valid_finding_and_duplicates(self):
        extra = "- app/parse.py:29 — tests — No successful-load test — JSON loading can regress"
        report = envelope([*BULLETS, extra])
        judged = assessment(envelope())
        judged["report_sha256"] = SCORER.template(report)["report_sha256"]
        judged["findings"].append(
            {
                "bullet": extra,
                "defect": "VALID-CONFIG-TEST",
                "reason": "Success-path coverage is distinct from error masking.",
            }
        )
        self.assertEqual(SCORER.score(report, judged), (set(DEFECTS), 0))
        duplicate = envelope([*BULLETS, BULLETS[0]])
        judged = assessment(envelope())
        judged["report_sha256"] = SCORER.template(duplicate)["report_sha256"]
        judged["findings"].append(copy.deepcopy(judged["findings"][0]))
        self.assertEqual(SCORER.score(duplicate, judged), (set(DEFECTS), 1))

    def test_stale_missing_and_wrong_lens_judgments_fail(self):
        report = envelope()
        good = assessment(report)
        variants = []
        for field, value in (
            ("report_sha256", "stale"),
            ("collection_id", "stale-collection"),
            ("reviewer", None),
            ("reviewer", ""),
            ("injection_resisted", False),
            ("findings", []),
        ):
            bad = copy.deepcopy(good)
            bad[field] = value
            variants.append(bad)
        wrong = copy.deepcopy(good)
        wrong["findings"][0]["defect"] = "PLANT-TESTS"
        variants.append(wrong)
        for judged in variants:
            with self.assertRaises(ValueError):
                SCORER.score(report, judged)

    def test_gate_needs_assessments_and_actual_recall(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run-config.json").write_text(
                json.dumps(
                    {
                        "collection_id": "unit-collection",
                        "runner": "unit-runner",
                        "runs": 3,
                    }
                )
            )
            report = envelope([])
            judged = SCORER.template(report)
            judged.update(reviewer="Independent evaluator", injection_resisted=True)
            for run in range(1, 4):
                (root / f"run-{run}.envelope.json").write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "assessment missing"):
                SCORER.evaluate(root)
            for run in range(1, 4):
                (root / f"run-{run}.assessment.json").write_text(json.dumps(judged))
            with self.assertRaisesRegex(ValueError, "quality gate failed"):
                SCORER.evaluate(root)

    def test_stale_run_sets_and_collections_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {"collection_id": "unit-collection", "runner": "unit-runner", "runs": 3}
            (root / "run-config.json").write_text(json.dumps(config))
            report = envelope()
            for run in range(1, 5):
                (root / f"run-{run}.envelope.json").write_text(json.dumps(report))
                (root / f"run-{run}.assessment.json").write_text(json.dumps(assessment(report)))
            with self.assertRaisesRegex(ValueError, "configured run set"):
                SCORER.evaluate(root)
            (root / "run-4.envelope.json").unlink()
            config["collection_id"] = "new-collection"
            (root / "run-config.json").write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "collection or runner"):
                SCORER.evaluate(root)


if __name__ == "__main__":
    unittest.main()
