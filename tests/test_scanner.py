"""Tests for the callable scanner and its synthetic fixtures."""

import json
import tempfile
import unittest
from pathlib import Path

from python_challenge.scanner import scan_file, scan_text


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "sample-repository/scanner-fixtures"
EXPECTED_RESULTS = FIXTURE_ROOT / "expected-results.json"


class ScannerTests(unittest.TestCase):
    """Verify clean scans, findings, locations, and redaction."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = json.loads(EXPECTED_RESULTS.read_text(encoding="utf-8"))

    def test_clean_fixture_has_no_findings(self) -> None:
        result = scan_file(FIXTURE_ROOT / "clean.txt")

        expected = self.expected["clean"]
        self.assertEqual(expected["file"], "clean.txt")
        self.assertEqual(len(result.findings), expected["finding_count"])
        self.assertTrue(result.clean)

    def test_positive_fixture_reports_redacted_finding(self) -> None:
        result = scan_file(FIXTURE_ROOT / "positive.txt")

        expected = self.expected["positive"]
        self.assertEqual(expected["file"], "positive.txt")
        self.assertEqual(len(result.findings), expected["finding_count"])
        self.assertFalse(result.clean)
        finding = result.findings[0]
        self.assertEqual(finding.line_number, expected["line"])
        self.assertEqual(finding.rule_id, expected["rule_id"])
        self.assertEqual(finding.redacted_match, expected["redacted_match"])
        self.assertNotIn("synthetic-password-value", finding.redacted_match)

    def test_multiple_assignments_report_each_line(self) -> None:
        result = scan_text("password=first\nmessage=ok\nPASSWORD = second\npassword=third")

        self.assertEqual([finding.line_number for finding in result.findings], [1, 3, 4])
        self.assertTrue(all("[REDACTED]" in finding.redacted_match for finding in result.findings))

    def test_quoted_value_is_detected_and_redacted(self) -> None:
        result = scan_text('password="synthetic quoted value"')

        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].redacted_match, "password=[REDACTED]")
        self.assertNotIn("synthetic quoted value", result.findings[0].redacted_match)

    def test_whitespace_around_assignment_is_preserved_when_redacted(self) -> None:
        result = scan_text("  Password   =   synthetic-value  ")

        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].redacted_match, "Password   =   [REDACTED]")

    def test_missing_file_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            scan_file(FIXTURE_ROOT / "does-not-exist.txt")

    def test_non_utf8_file_raises_decode_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "binary.dat"
            path.write_bytes(b"password=\xff\xfe")

            with self.assertRaises(UnicodeDecodeError):
                scan_file(path)


if __name__ == "__main__":
    unittest.main()
