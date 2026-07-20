"""Command-line entry point for Python Challenge."""

import argparse
import logging
import sys

from .rules import RULES
from .scanner import IgnoreSpec, parse_finding_reference, scan_repository


LOGGER = logging.getLogger(__name__)


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
    parser.add_argument(
        "--ignore-path",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="explicitly ignore findings in this exact repository-relative path (repeatable)",
    )
    parser.add_argument(
        "--ignore-rule",
        action="append",
        default=[],
        metavar="RULE_ID",
        help="explicitly ignore this exact rule identifier (repeatable)",
    )
    parser.add_argument(
        "--ignore-finding",
        action="append",
        default=[],
        metavar="PATH:LINE:RULE_ID",
        help="explicitly ignore one exact finding (repeatable)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the scanner and return 0 for clean, 1 when findings are present."""
    args = build_parser().parse_args(argv)
    if args.path is None:
        print("Python Challenge is ready for your next exercise!")
        return 0

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        known_rule_ids = {rule.identifier for rule in RULES}
        unknown_rules = set(args.ignore_rule) - known_rule_ids
        if unknown_rules:
            raise ValueError(f"unknown rule identifier(s): {', '.join(sorted(unknown_rules))}")
        ignore = IgnoreSpec(
            paths=frozenset(args.ignore_path),
            rules=frozenset(args.ignore_rule),
            findings=frozenset(parse_finding_reference(value) for value in args.ignore_finding),
        )
        result = scan_repository(args.path, ignore=ignore)
    except (OSError, UnicodeError, ValueError) as error:
        LOGGER.error(
            "scan_failure path=%s error_type=%s",
            args.path,
            type(error).__name__,
        )
        print(f"Unable to scan {args.path}: {error}", file=sys.stderr)
        return 2

    if result.ignored_findings:
        print(
            f"IGNORED: {len(result.ignored_findings)} finding(s) matched explicit ignore criteria."
        )

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
