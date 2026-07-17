"""Tests for the command-line interface."""

import unittest

from python_challenge.cli import build_parser


class CliTests(unittest.TestCase):
    """Verify the CLI can be constructed and accepts its options."""

    def test_parser_accepts_no_arguments(self) -> None:
        args = build_parser().parse_args([])

        self.assertIsNotNone(args)


if __name__ == "__main__":
    unittest.main()
