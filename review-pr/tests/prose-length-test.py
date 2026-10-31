#!/usr/bin/env python3
"""Offline checks for the prose-length measure described in lens-rubric.md."""

# Standard-library test runner keeps the offline gate dependency-free.
# ruff: noqa: PT009, PT027

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("prose_length", HERE / "prose-length.py")
PROSE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROSE)

REPORT = (
    "## Summary\n"
    "Lenses checked: correctness, silent-failure, tests, comments.\n"
    "Mode: full review.\n"
    "One defect decides the verdict: the port check rejects 65535.\n\n"
    "## Changes\n"
    "Adds three helpers to the parser.\n\n"
    "## Critical\n(none)\n\n"
    "## Important\n"
    "- app/parse.py:22 — correctness — Accept port 65535 — `is_valid_port(65535)` returns"
    " False because the bound is exclusive. — Valid configurations fail validation."
    " — Fix: Use `<=` and assert both bounds.\n"
    "- app/parse.py:30 — silent-failure — Surface config errors — Every read error"
    " becomes an empty dict. — Operators get nothing to act on.\n\n"
    "## Suggestions\n"
    "- app/parse.py:35 — comments — The docstring says None but line 37 returns an"
    " empty string. — A caller checking None treats it as a host.\n\n"
    "## Not reviewed\n(none)\n"
)


class MeasureTests(unittest.TestCase):
    def test_fields_are_counted_per_section_and_finding(self):
        m = PROSE.measure(REPORT)
        # Summary prose excludes the Lenses checked and Mode lines.
        self.assertEqual(m["summary"], 10)
        self.assertEqual(m["changes"], 6)
        self.assertEqual(m["not_reviewed"], 0)
        self.assertEqual(m["findings"], 3)
        self.assertEqual(m["title"], [3, 3, 0])
        self.assertEqual(m["defect"], [8, 7, 11])
        self.assertEqual(m["impact"], [4, 6, 9])
        self.assertEqual(m["fix"], [6])
        self.assertEqual(m["fixes"], 1)
        self.assertEqual(m["total"], len(REPORT.split()))

    def test_legacy_bullet_without_title_is_measured_as_defect(self):
        m = PROSE.measure(REPORT)
        # The third bullet has four fields, the pre-title grammar: no title, defect, impact.
        self.assertEqual(m["title"][2], 0)
        self.assertEqual(m["defect"][2], 11)

    def test_not_reviewed_text_is_counted_when_present(self):
        report = REPORT.replace(
            "## Not reviewed\n(none)\n", "## Not reviewed\n- The vendored tree.\n"
        )
        self.assertEqual(PROSE.measure(report)["not_reviewed"], 4)

    def test_none_sections_yield_no_findings(self):
        bare = (
            REPORT.split("## Important\n", maxsplit=1)[0]
            + "## Important\n(none)\n\n## Suggestions\n(none)\n\n## Not reviewed\n(none)\n"
        )
        m = PROSE.measure(bare)
        self.assertEqual(m["findings"], 0)
        self.assertEqual(m["defect"], [])


LEGACY_REPORT = (
    "## Summary\n"
    "Lenses checked: correctness, silent-failure, tests, comments.\n"
    "Two defects.\n\n"
    "## Critical\n(none)\n\n"
    "## Important\n"
    "- app/parse.py:22 — correctness — The bound is exclusive — `65535` is a legal port — but it"
    " is rejected. — Valid configurations fail.\n\n"
    "## Suggestions\n(none)\n\n"
    "## Strengths\n(none)\n\n"
    "## Not reviewed\n(none)\n"
)


class LegacyGrammarTests(unittest.TestCase):
    def test_report_without_changes_has_no_title_even_with_interior_separator(self):
        m = PROSE.measure(LEGACY_REPORT)
        self.assertEqual(m["findings"], 1)
        self.assertEqual(m["title"], [0])
        # The separators inside the defect stay inside the defect.
        self.assertEqual(m["defect"], [15])
        self.assertEqual(m["impact"], [3])
        self.assertEqual(m["fix"], [])

    def test_report_with_changes_reads_the_third_field_as_title(self):
        self.assertEqual(PROSE.measure(REPORT)["title"][0], 3)


class SnapshotTests(unittest.TestCase):
    def test_reports_load_from_envelope_or_sibling_and_summarize(self):
        with tempfile.TemporaryDirectory() as tmp:
            snap = Path(tmp)
            (snap / "run-1.envelope.json").write_text(json.dumps({"review": {"result": REPORT}}))
            (snap / "run-2.envelope.json").write_text(json.dumps({"review": {"result": None}}))
            (snap / "run-2.json").write_text(json.dumps({"result": REPORT}))
            (snap / "run-3.envelope.json").write_text(json.dumps({"review": {}}))
            loaded = list(PROSE.load_reports(snap))
            self.assertEqual([run for run, _ in loaded], ["run-1", "run-2"])
            out = subprocess.run(
                [sys.executable, "-I", str(HERE / "prose-length.py"), str(snap)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            header, row = out[0].split("\t"), out[1].split("\t")
            got = dict(zip(header, row, strict=True))
            self.assertEqual(got["runs"], "2")
            self.assertEqual(got["summary"], "10")
            self.assertEqual(got["findings"], "3")
            self.assertEqual(got["defect"], "8.7")
            self.assertEqual(got["fix"], "6")

    def test_unreadable_native_sibling_is_skipped_for_an_incomplete_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            snap = Path(tmp)
            (snap / "run-1.envelope.json").write_text(
                json.dumps({"exit": 0, "review": {"status": "completed", "result": REPORT}})
            )
            # A timed-out Codex run: no report in the envelope and a partial JSONL sibling.
            (snap / "run-2.envelope.json").write_text(json.dumps({"exit": 1, "review": None}))
            (snap / "run-2.json").write_text('{"type":"thread.started"}\n{"type":"turn.started"}\n')
            self.assertEqual([run for run, _ in PROSE.load_reports(snap)], ["run-1"])
            # The same sibling under a run that claims completion is an error, as in score-lens.py.
            (snap / "run-2.envelope.json").write_text(
                json.dumps({"exit": 0, "review": {"status": "completed"}})
            )
            with self.assertRaisesRegex(ValueError, "no readable report"):
                list(PROSE.load_reports(snap))

    def test_runs_rows_keep_per_finding_means(self):
        with tempfile.TemporaryDirectory() as tmp:
            snap = Path(tmp)
            (snap / "run-1.envelope.json").write_text(json.dumps({"review": {"result": REPORT}}))
            out = subprocess.run(
                [sys.executable, "-I", str(HERE / "prose-length.py"), "--runs", str(snap)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            got = dict(zip(out[0].split("\t"), out[1].split("\t"), strict=True))
            self.assertTrue(got["snapshot"].endswith("/run-1"))
            self.assertEqual(got["runs"], "1")
            self.assertEqual(got["findings"], "3")
            # A mean per finding, as in a snapshot row, not a sum over the run's findings.
            self.assertEqual(got["defect"], "8.7")
            self.assertEqual(got["impact"], "6.3")

    def test_empty_snapshot_is_reported_on_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-I", str(HERE / "prose-length.py"), tmp],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn("no reports", proc.stderr)


if __name__ == "__main__":
    unittest.main()
