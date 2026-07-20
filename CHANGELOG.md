# Changelog

All notable changes to this project are documented here.

## [0.1.0] - 2026-07-17

### Added

- Initial Python package and command-line entry point.
- Local scanner for synthetic `password=...` secret-like patterns.
- Detection of quoted values and assignments with flexible whitespace.
- Redacted findings with line numbers and rule identifiers.
- Synthetic clean and positive scanner fixtures.
- Automated tests covering the scanner and sample repository data.
- Tests for multiple findings, missing files, and non-UTF-8 input handling.
- Recursive scanning of local repositories for supported text-file extensions.
- Synthetic `password=` and `api_key=` repository findings with relative paths.
- Exclusion of Git metadata, virtual environments, cache directories, generated files, and scanner output.
- Distinct CLI exit codes for clean scans, findings, and scan errors.
- Stable `access-token-assignment` and `client-secret-assignment` detection rules with synthetic fixtures.
- Centralized rule registry so new detection rules do not require traversal, reporting, or CLI changes.
- Explicit exact-match ignores for paths, rule identifiers, and individual findings, with visible ignored-finding summaries.
- Expanded test coverage for every rule, CLI ignore handling, malformed text, redaction, and unsupported file types.
- Added metadata and failure logging with source values excluded from log messages.
- Added a concise design-decision record covering architecture, scanning scope, safety, ignores, and exit codes.
- Added a basic GitHub Actions test workflow for pull requests and pushes to `main`.
