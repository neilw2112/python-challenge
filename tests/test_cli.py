"""Tests for the command-line interface."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import unittest

from python_challenge.cli import build_parser, main


POSITIVE_REPOSITORY = (
    Path(__file__).resolve().parents[1] / "sample-repository/repository-fixtures/positive-repository"
)


class CliTests(unittest.TestCase):
    """Verify the CLI can be constructed and accepts its options."""

    def test_parser_accepts_no_arguments(self) -> None:
        args = build_parser().parse_args([])

        self.assertIsNotNone(args)

    def test_cli_reports_all_explicitly_ignored_findings(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    str(POSITIVE_REPOSITORY),
                    "--ignore-path",
                    "app/settings.py",
                    "--ignore-path",
                    "app/tokens.txt",
                    "--ignore-path",
                    "config/client.ini",
                    "--ignore-path",
                    "docs/config.md",
                ]
            )

        self.assertEqual(status, 0)
        self.assertIn("IGNORED: 4 finding(s)", output.getvalue())
        self.assertIn("CLEAN:", output.getvalue())

    def test_cli_rejects_malformed_finding_ignore(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            status = main([str(POSITIVE_REPOSITORY), "--ignore-finding", "not-a-reference"])

        self.assertEqual(status, 2)
        self.assertIn("Unable to scan", error.getvalue())


if __name__ == "__main__":
    unittest.main()
