# Python Challenge

Python Challenge is a small local command-line scanner for detecting likely secrets in a supplied repository. It recursively scans a documented set of text files, reports relative paths, line numbers, and rule identifiers, and redacts matched values. The project also provides synthetic fixtures for clean scans, findings, and excluded paths.

## Requirements

- Python 3.14 or newer

## Setup

Create and activate a virtual environment, then install the project in editable mode:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

## Run

Run the application with a local repository path:

```bash
python3 -m python_challenge sample-repository/repository-fixtures/clean-repository
```

After installation, the console script can also be used:

```bash
python-challenge sample-repository/repository-fixtures/positive-repository
```

## How it works

The scanner can be called directly from Python:

```python
from python_challenge.scanner import scan_repository

result = scan_repository("sample-repository/repository-fixtures/positive-repository")
for finding in result.findings:
    print(finding.relative_path, finding.line_number, finding.rule_id, finding.redacted_match)
```

The CLI reports a clean scan like this:

```text
CLEAN: no likely secrets found in sample-repository/repository-fixtures/clean-repository
```

For a finding, the matched value is redacted:

```text
FINDING: app/settings.py:line 3, rule password-assignment, match password = [REDACTED]
FINDING: docs/config.md:line 3, rule api-key-assignment, match api_key=[REDACTED]
```

The scanner checks `.py`, `.txt`, `.md`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, and `.conf` files. It skips `.git`, virtual-environment directories, cache directories, `generated/`, and `.scanner-output/`.

Exit codes are:

- `0` — scan completed and found no likely secrets
- `1` — scan completed and found one or more likely secrets
- `2` — invalid input or scan error, such as a missing repository or unreadable text file

## Test

Run the test suite with:

```bash
python3 -m unittest discover -s tests -v
```

## Project layout

```text
src/python_challenge/  Application package
tests/                  Automated tests
sample-repository/      Synthetic analysis fixture and expected findings
pyproject.toml          Packaging and tool configuration
```

## Sample repository

`sample-repository/` contains only synthetic test data. It includes clean and positive scanner fixtures, expected findings, and documents `generated/example.py` as an excluded path with a known false positive. See its [README](sample-repository/README.md) for details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for releases and meaningful behavior changes.
