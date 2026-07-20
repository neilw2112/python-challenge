# Design decisions

This document records the main decisions behind the current small local scanner.

## Package and project layout

- **Decision:** Use a `src/` package with `pyproject.toml` and editable installation.
- **Reason:** This is a conventional Python layout that catches packaging mistakes and keeps setup simple.
- **Alternatives considered:** A flat package at the repository root or a larger framework template.
- **Consequences:** Development requires a virtual environment and editable install; the project remains easy to extend.

## Standard-library tests

- **Decision:** Use `unittest` rather than adding a test framework dependency.
- **Reason:** The application is small and the built-in discovery command is sufficient.
- **Alternatives considered:** `pytest` and a larger testing stack.
- **Consequences:** There is less tooling overhead, but fewer conveniences than third-party frameworks provide.

## Narrow recursive scan scope

- **Decision:** Scan only a small allowlist of text-file extensions and skip Git metadata, environments, caches, generated files, and scanner output.
- **Reason:** This avoids binary decoding, noisy dependencies, and accidental traversal of non-source content.
- **Alternatives considered:** Scanning every file or recursively following all directories.
- **Consequences:** Extensionless files and unsupported formats are not scanned, and symlinked directories are not followed.

## Rule registry

- **Decision:** Keep detection rules in `src/python_challenge/rules.py` with stable identifiers.
- **Reason:** A new rule can be added without changing traversal, reporting, or CLI code.
- **Alternatives considered:** Inline conditionals in the scanner or a configurable rule plug-in system.
- **Consequences:** Rules remain simple and code-defined; dynamic configuration is intentionally deferred.

## Redaction and heuristic findings

- **Decision:** Report likely matches with paths, lines, rule IDs, and redacted values.
- **Reason:** Assignment patterns are useful signals, but they do not prove a value is a real credential.
- **Alternatives considered:** Printing source lines or attempting live credential validation.
- **Consequences:** Users must investigate findings separately, and the scanner cannot confirm validity.

## Explicit ignores

- **Decision:** Support exact path, rule-ID, and `path:line:rule` ignores only when explicitly supplied.
- **Reason:** Suppression can be useful for known synthetic or accepted findings, but must remain visible and narrow.
- **Alternatives considered:** Wildcards, a silent ignore file, or suppressing all findings by default.
- **Consequences:** Ignored counts are logged and reported; malformed or unknown ignore specifications fail with exit code `2`.

## Logging and exit codes

- **Decision:** Log scan metadata to stderr and use exit codes `0` clean, `1` findings, and `2` errors.
- **Reason:** This supports local use and future CI while keeping secrets out of logs.
- **Alternatives considered:** Writing log files or using one non-zero status for every problem.
- **Consequences:** No persistent logs are created, and callers must distinguish findings from execution errors by status code.
