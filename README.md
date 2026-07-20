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
FINDING: app/tokens.txt:line 2, rule access-token-assignment, match access_token=[REDACTED]
FINDING: config/client.ini:line 2, rule client-secret-assignment, match client_secret = [REDACTED]
FINDING: docs/config.md:line 3, rule api-key-assignment, match api_key=[REDACTED]
```

The scanner checks `.py`, `.txt`, `.md`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, and `.conf` files. It currently detects `password=`, `api_key=`, `access_token=`, and `client_secret=` assignments. Rule definitions live in `src/python_challenge/rules.py`, so a new rule can be registered without changing traversal or reporting code. It skips `.git`, virtual-environment directories, cache directories, `generated/`, and `.scanner-output/`.

The CLI logs scan start and completion metadata, including the repository path, supported-file count, finding count, ignored paths, and rule identifiers. Failures log only their error type. Logs never include source lines, matched values, or complete secret-like values.

### Explicit ignores

Ignores are opt-in, exact-match command-line options. They never use wildcards and the CLI reports how many findings were ignored:

```bash
python -m python_challenge . \
  --ignore-path docs/example.md \
  --ignore-rule api-key-assignment \
  --ignore-finding config/client.ini:2:client-secret-assignment
```

Use `--ignore-path` for one repository-relative path, `--ignore-rule` for one registered rule identifier, or `--ignore-finding` for one exact `path:line:rule-id` finding. Ignored findings are removed from the finding exit status, but are always reported with an `IGNORED` summary. Unknown rule IDs and malformed finding references return exit code `2`.

Exit codes are:

- `0` — scan completed and found no likely secrets
- `1` — scan completed and found one or more likely secrets
- `2` — invalid input or scan error, such as a missing repository or unreadable text file

## Test

Run the test suite with:

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions runs the same test command on pull requests and pushes to `main`.

## Project layout

```text
src/python_challenge/  Application package
tests/                  Automated tests
sample-repository/      Synthetic analysis fixture and expected findings
docs/                   Design decisions and project notes
pyproject.toml          Packaging and tool configuration
```

## Sample repository

`sample-repository/` contains only synthetic test data. It includes clean and positive scanner fixtures, expected findings, and documents `generated/example.py` as an excluded path with a known false positive. See its [README](sample-repository/README.md) for details.

See [docs/decisions.md](docs/decisions.md) for the main design decisions and their tradeoffs.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for releases and meaningful behavior changes.
