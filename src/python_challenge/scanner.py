"""Small local scanner for synthetic secret-like patterns."""

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path

from .rules import RULES


LOGGER = logging.getLogger(__name__)

# This intentionally small allowlist keeps repository scans focused on common
# text files and avoids treating arbitrary binary files as source text.
TEXT_EXTENSIONS = frozenset(
    {".cfg", ".conf", ".ini", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
)

# These directories are not application source and should not produce findings.
EXCLUDED_DIR_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".scanner-output",
        ".venv",
        "ENV",
        "env",
        "generated",
        "venv",
    }
)


@dataclass(frozen=True)
class Finding:
    """A redacted scanner finding."""

    relative_path: str
    line_number: int
    rule_id: str
    redacted_match: str


@dataclass(frozen=True)
class FindingReference:
    """An exact finding location and rule used by an ignore specification."""

    relative_path: str
    line_number: int
    rule_id: str


@dataclass(frozen=True)
class IgnoreSpec:
    """Explicit exact-match ignore criteria for repository findings."""

    paths: frozenset[str] = field(default_factory=frozenset)
    rules: frozenset[str] = field(default_factory=frozenset)
    findings: frozenset[FindingReference] = field(default_factory=frozenset)

    def matches(self, finding: Finding) -> bool:
        """Return whether a finding matches one explicit ignore criterion."""
        reference = FindingReference(
            relative_path=finding.relative_path,
            line_number=finding.line_number,
            rule_id=finding.rule_id,
        )
        return (
            finding.relative_path in self.paths
            or finding.rule_id in self.rules
            or reference in self.findings
        )


@dataclass(frozen=True)
class ScanResult:
    """The result of scanning one file or a repository."""

    findings: tuple[Finding, ...]
    ignored_findings: tuple[Finding, ...] = ()

    @property
    def clean(self) -> bool:
        """Return whether the scan found no likely secrets."""
        return not self.findings


def parse_finding_reference(value: str) -> FindingReference:
    """Parse an exact ``relative/path:line:rule-id`` ignore reference."""
    try:
        relative_path, line_number, rule_id = value.rsplit(":", 2)
        line_number = int(line_number)
    except (ValueError, TypeError):
        raise ValueError("expected relative/path:line:rule-id") from None
    if not relative_path or line_number < 1 or not rule_id:
        raise ValueError("expected relative/path:line:rule-id")
    return FindingReference(relative_path, line_number, rule_id)


def scan_text(text: str, relative_path: str = "<text>") -> ScanResult:
    """Scan text and return findings without retaining secret-like values."""
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                prefix = match.group(0)[: match.start("value") - match.start()]
                findings.append(
                    Finding(
                        relative_path=relative_path,
                        line_number=line_number,
                        rule_id=rule.identifier,
                        redacted_match=f"{prefix}[REDACTED]",
                    )
                )
    return ScanResult(findings=tuple(findings))


def scan_file(path: str | Path, relative_path: str | None = None) -> ScanResult:
    """Read one UTF-8 text file and scan it for likely secrets."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    return scan_text(text, relative_path or file_path.name)


def scan_repository(
    path: str | Path,
    output_dir: str | Path = ".scanner-output",
    ignore: IgnoreSpec | None = None,
) -> ScanResult:
    """Recursively scan supported text files below a local repository path.

    The scan skips Git metadata, virtual environments, cache directories,
    generated files, and the configured scanner output directory.
    """
    repository = Path(path)
    LOGGER.info("scan_start repository=%s", repository)
    if not repository.exists():
        LOGGER.error(
            "scan_failure repository=%s error_type=FileNotFoundError",
            repository,
        )
        raise FileNotFoundError(repository)
    if not repository.is_dir():
        LOGGER.error(
            "scan_failure repository=%s error_type=NotADirectoryError",
            repository,
        )
        raise NotADirectoryError(repository)

    repository = repository.resolve()
    configured_output = Path(output_dir)
    output_path = (repository / configured_output).resolve() if not configured_output.is_absolute() else configured_output.resolve()
    findings: list[Finding] = []
    ignored_findings: list[Finding] = []
    file_count = 0
    ignore = ignore or IgnoreSpec()

    def handle_walk_error(error: OSError) -> None:
        LOGGER.error(
            "scan_failure repository=%s error_type=%s",
            repository,
            type(error).__name__,
        )
        raise error

    for current, directories, files in os.walk(
        repository,
        topdown=True,
        followlinks=False,
        onerror=handle_walk_error,
    ):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in EXCLUDED_DIR_NAMES
            and (current_path / directory).resolve() != output_path
        )
        for filename in sorted(files):
            file_path = current_path / filename
            if file_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            relative_path = file_path.relative_to(repository).as_posix()
            file_count += 1
            try:
                file_findings = scan_file(file_path, relative_path).findings
            except (OSError, UnicodeError) as error:
                LOGGER.error(
                    "scan_failure repository=%s file=%s error_type=%s",
                    repository,
                    relative_path,
                    type(error).__name__,
                )
                raise
            for finding in file_findings:
                if ignore.matches(finding):
                    ignored_findings.append(finding)
                else:
                    findings.append(finding)

    finding_rules = sorted({finding.rule_id for finding in findings})
    ignored_paths = sorted({finding.relative_path for finding in ignored_findings})
    ignored_rules = sorted({finding.rule_id for finding in ignored_findings})
    LOGGER.info(
        "scan_complete repository=%s files=%d findings=%d finding_rules=%s "
        "ignored_paths=%s ignored_rules=%s",
        repository,
        file_count,
        len(findings),
        ",".join(finding_rules) or "none",
        ",".join(ignored_paths) or "none",
        ",".join(ignored_rules) or "none",
    )
    return ScanResult(
        findings=tuple(findings),
        ignored_findings=tuple(ignored_findings),
    )
