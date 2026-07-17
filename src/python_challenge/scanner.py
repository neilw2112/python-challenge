"""Small local scanner for synthetic secret-like patterns."""

from dataclasses import dataclass
import os
from pathlib import Path
import re


_VALUE = r'''(?P<value>"[^"\r\n]*"|'[^'\r\n]*'|[^\s#]+)'''
_RULES = (
    ("password-assignment", re.compile(rf"(?i)\bpassword\s*=\s*{_VALUE}")),
    ("api-key-assignment", re.compile(rf"(?i)\bapi_key\s*=\s*{_VALUE}")),
)

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
class ScanResult:
    """The result of scanning one file or a repository."""

    findings: tuple[Finding, ...]

    @property
    def clean(self) -> bool:
        """Return whether the scan found no likely secrets."""
        return not self.findings


def scan_text(text: str, relative_path: str = "<text>") -> ScanResult:
    """Scan text and return findings without retaining secret-like values."""
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern in _RULES:
            for match in pattern.finditer(line):
                prefix = match.group(0)[: match.start("value") - match.start()]
                findings.append(
                    Finding(
                        relative_path=relative_path,
                        line_number=line_number,
                        rule_id=rule_id,
                        redacted_match=f"{prefix}[REDACTED]",
                    )
                )
    return ScanResult(findings=tuple(findings))


def scan_file(path: str | Path, relative_path: str | None = None) -> ScanResult:
    """Read one UTF-8 text file and scan it for likely secrets."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    return scan_text(text, relative_path or file_path.name)


def scan_repository(path: str | Path, output_dir: str | Path = ".scanner-output") -> ScanResult:
    """Recursively scan supported text files below a local repository path.

    The scan skips Git metadata, virtual environments, cache directories,
    generated files, and the configured scanner output directory.
    """
    repository = Path(path)
    if not repository.exists():
        raise FileNotFoundError(repository)
    if not repository.is_dir():
        raise NotADirectoryError(repository)

    repository = repository.resolve()
    configured_output = Path(output_dir)
    output_path = (repository / configured_output).resolve() if not configured_output.is_absolute() else configured_output.resolve()
    findings: list[Finding] = []

    for current, directories, files in os.walk(repository, topdown=True, followlinks=False):
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
            findings.extend(scan_file(file_path, relative_path).findings)

    return ScanResult(findings=tuple(findings))
