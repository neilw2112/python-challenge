"""Tests for recursive scanning of the synthetic repository fixtures."""

import unittest
from pathlib import Path

from python_challenge.scanner import scan_repository


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "sample-repository/repository-fixtures"


class RepositoryScannerTests(unittest.TestCase):
    """Verify repository traversal, findings, exclusions, and redaction."""

    def test_clean_repository_has_no_findings(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "clean-repository")

        self.assertTrue(result.clean)
        self.assertEqual(result.findings, ())

    def test_positive_repository_has_two_findings(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        self.assertEqual(
            [(finding.relative_path, finding.line_number, finding.rule_id) for finding in result.findings],
            [
                ("app/settings.py", 3, "password-assignment"),
                ("docs/config.md", 3, "api-key-assignment"),
            ],
        )

    def test_excluded_virtual_environment_path_is_not_scanned(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        finding_paths = {finding.relative_path for finding in result.findings}
        self.assertNotIn(".venv/ignored.py", finding_paths)
        self.assertNotIn(".scanner-output/report.txt", finding_paths)

    def test_repository_findings_are_redacted(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        redacted_matches = {finding.redacted_match for finding in result.findings}
        self.assertEqual(redacted_matches, {"password = [REDACTED]", "api_key=[REDACTED]"})
        self.assertNotIn("synthetic-repository-password", str(result))
        self.assertNotIn("synthetic-repository-api-key", str(result))


if __name__ == "__main__":
    unittest.main()
