"""Command-line entry point for Python Challenge."""

import argparse
import sys

from .scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="python-challenge",
        description="Practice and extend Python problem-solving challenges.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument("path", nargs="?", help="one local repository path to scan")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the scanner and return 0 for clean, 1 when findings are present."""
    args = build_parser().parse_args(argv)
    if args.path is None:
        print("Python Challenge is ready for your next exercise!")
        return 0

    try:
        result = scan_repository(args.path)
    except (OSError, UnicodeError) as error:
        print(f"Unable to scan {args.path}: {error}", file=sys.stderr)
        return 2

    if result.clean:
        print(f"CLEAN: no likely secrets found in {args.path}")
        return 0

    for finding in result.findings:
        print(
            f"FINDING: {finding.relative_path}:line {finding.line_number}, "
            f"rule {finding.rule_id}, "
            f"match {finding.redacted_match}"
        )
    return 1
