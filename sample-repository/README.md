# Synthetic Sample Repository

This directory is a small, self-contained fixture for testing repository-analysis workflows. Every value is synthetic and safe to use in tests; it is not production code and contains no real credentials or personal data.

## Contents

- `app/config.py` contains one intentionally detectable synthetic finding.
- `data/users.json` contains synthetic test records only.
- `docs/example.md` contains a second intentionally detectable finding.
- `generated/example.py` is an excluded path. Its matching text is a documented false positive for tests that verify exclusions.
- `expected-findings.json` records the findings expected from the included paths.
- `scanner-fixtures/` contains clean and positive scanner inputs plus `expected-results.json`.
- `repository-fixtures/` contains clean and positive repository trees for recursive-scan tests.

The `generated/` path should be excluded from analysis because generated artifacts are outside the scope of this fixture. The matching text there is therefore a known false positive, not an expected finding.
