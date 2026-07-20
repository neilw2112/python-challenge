"""Tests for recursive scanning of the synthetic repository fixtures."""

import unittest
from pathlib import Path

from python_challenge.scanner import (
    FindingReference,
    IgnoreSpec,
    parse_finding_reference,
    scan_repository,
)


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "sample-repository/repository-fixtures"


class RepositoryScannerTests(unittest.TestCase):
    """Verify repository traversal, findings, exclusions, and redaction."""

    def test_clean_repository_has_no_findings(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "clean-repository")

        self.assertTrue(result.clean)
        self.assertEqual(result.findings, ())

    def test_positive_repository_has_four_findings(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        self.assertEqual(
            [(finding.relative_path, finding.line_number, finding.rule_id) for finding in result.findings],
            [
                ("app/settings.py", 3, "password-assignment"),
                ("app/tokens.txt", 2, "access-token-assignment"),
                ("config/client.ini", 2, "client-secret-assignment"),
                ("docs/config.md", 3, "api-key-assignment"),
            ],
        )

    def test_unsupported_file_extension_is_skipped(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        finding_paths = {finding.relative_path for finding in result.findings}
        self.assertNotIn("assets/ignored.bin", finding_paths)

    def test_excluded_virtual_environment_path_is_not_scanned(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        finding_paths = {finding.relative_path for finding in result.findings}
        self.assertNotIn(".venv/ignored.py", finding_paths)
        self.assertNotIn(".scanner-output/report.txt", finding_paths)

    def test_repository_findings_are_redacted(self) -> None:
        result = scan_repository(FIXTURE_ROOT / "positive-repository")

        redacted_matches = {finding.redacted_match for finding in result.findings}
        self.assertEqual(
            redacted_matches,
            {
                "password = [REDACTED]",
                "api_key=[REDACTED]",
                "access_token=[REDACTED]",
                "client_secret = [REDACTED]",
            },
        )
        self.assertNotIn("synthetic-repository-password", str(result))
        self.assertNotIn("synthetic-repository-api-key", str(result))
        self.assertNotIn("synthetic-access-token", str(result))
        self.assertNotIn("synthetic-client-secret", str(result))

    def test_exact_path_ignore_is_explicit_and_does_not_hide_other_findings(self) -> None:
        result = scan_repository(
            FIXTURE_ROOT / "positive-repository",
            ignore=IgnoreSpec(paths=frozenset({"app/settings.py"})),
        )

        self.assertEqual(len(result.findings), 3)
        self.assertEqual([finding.relative_path for finding in result.ignored_findings], ["app/settings.py"])

    def test_exact_rule_ignore_is_explicit(self) -> None:
        result = scan_repository(
            FIXTURE_ROOT / "positive-repository",
            ignore=IgnoreSpec(rules=frozenset({"api-key-assignment"})),
        )

        self.assertEqual(len(result.findings), 3)
        self.assertEqual([finding.rule_id for finding in result.ignored_findings], ["api-key-assignment"])

    def test_exact_finding_ignore_is_explicit(self) -> None:
        reference = FindingReference("config/client.ini", 2, "client-secret-assignment")
        result = scan_repository(
            FIXTURE_ROOT / "positive-repository",
            ignore=IgnoreSpec(findings=frozenset({reference})),
        )

        self.assertEqual(len(result.findings), 3)
        self.assertEqual(len(result.ignored_findings), 1)
        self.assertEqual(result.ignored_findings[0].relative_path, "config/client.ini")

    def test_finding_reference_parser_requires_exact_shape(self) -> None:
        self.assertEqual(
            parse_finding_reference("config/client.ini:2:client-secret-assignment"),
            FindingReference("config/client.ini", 2, "client-secret-assignment"),
        )
        with self.assertRaises(ValueError):
            parse_finding_reference("client.ini:bad")

    def test_scan_logs_metadata_without_secret_values(self) -> None:
        with self.assertLogs("python_challenge.scanner", level="INFO") as captured:
            scan_repository(FIXTURE_ROOT / "positive-repository")

        logs = "\n".join(captured.output)
        self.assertIn("scan_start", logs)
        self.assertIn("scan_complete", logs)
        self.assertIn("files=4", logs)
        self.assertIn("findings=4", logs)
        self.assertIn("password-assignment", logs)
        self.assertIn("api-key-assignment", logs)
        self.assertIn("ignored_paths=none", logs)
        self.assertNotIn("synthetic-repository-password", logs)
        self.assertNotIn("synthetic-repository-api-key", logs)
        self.assertNotIn("synthetic-access-token", logs)
        self.assertNotIn("synthetic-client-secret", logs)

    def test_scan_failure_logs_error_type_without_file_contents(self) -> None:
        missing = FIXTURE_ROOT / "missing-repository"

        with self.assertLogs("python_challenge.scanner", level="ERROR") as captured:
            with self.assertRaises(FileNotFoundError):
                scan_repository(missing)

        logs = "\n".join(captured.output)
        self.assertIn("scan_failure", logs)
        self.assertIn("error_type=FileNotFoundError", logs)
        self.assertNotIn("password=", logs)


if __name__ == "__main__":
    unittest.main()
