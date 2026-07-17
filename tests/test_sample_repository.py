"""Contract tests for the synthetic sample repository fixture."""

import json
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "sample-repository"
EXPECTED_FINDINGS = FIXTURE_ROOT / "expected-findings.json"


class SampleRepositoryTests(unittest.TestCase):
    """Keep the sample repository useful as stable test input."""

    @classmethod
    def setUpClass(cls) -> None:
        with EXPECTED_FINDINGS.open(encoding="utf-8") as file:
            cls.expected = json.load(file)

    def test_fixture_contains_expected_top_level_sections(self) -> None:
        self.assertEqual(self.expected["repository"], "synthetic-sample-repository")
        self.assertIsInstance(self.expected["findings"], list)
        self.assertIsInstance(self.expected["excluded_paths"], list)

    def test_expected_findings_point_to_matching_evidence(self) -> None:
        for finding in self.expected["findings"]:
            path = FIXTURE_ROOT / finding["path"]
            self.assertTrue(path.is_file(), finding["path"])

            lines = path.read_text(encoding="utf-8").splitlines()
            evidence = lines[finding["line"] - 1]
            if finding["rule"] == "synthetic-token":
                self.assertIn("DEMO_API_TOKEN", evidence)
                self.assertIn("synthetic-token", evidence)
            elif finding["rule"] == "todo-marker":
                self.assertIn("TODO", evidence)
            else:
                self.fail(f"Unknown fixture rule: {finding['rule']}")

    def test_expected_findings_do_not_include_excluded_paths(self) -> None:
        excluded = {entry["path"] for entry in self.expected["excluded_paths"]}
        finding_paths = {finding["path"] for finding in self.expected["findings"]}

        self.assertTrue(excluded)
        self.assertTrue(excluded.isdisjoint(finding_paths))

    def test_excluded_path_documents_known_false_positive(self) -> None:
        for entry in self.expected["excluded_paths"]:
            path = FIXTURE_ROOT / entry["path"]
            false_positive = entry["known_false_positive"]
            line = path.read_text(encoding="utf-8").splitlines()[false_positive["line"] - 1]

            self.assertTrue(path.is_file(), entry["path"])
            self.assertIn(false_positive["rule"].split("-")[0].upper(), line)
            self.assertTrue(entry["reason"])

    def test_sample_user_data_is_synthetic(self) -> None:
        users_path = FIXTURE_ROOT / "data/users.json"
        users = json.loads(users_path.read_text(encoding="utf-8"))

        self.assertEqual(len(users), 2)
        self.assertEqual([user["id"] for user in users], [1001, 1002])
        self.assertTrue(all(user["email"].endswith(".test") for user in users))
        self.assertTrue(all(user["name"].startswith("Test User") for user in users))

    def test_fixture_has_no_real_secret_format(self) -> None:
        secret_pattern = re.compile(r"(?:AKIA|ghp_|sk_live_|-----BEGIN [A-Z ]+ PRIVATE KEY-----)")
        for path in FIXTURE_ROOT.rglob("*"):
            if path.is_file():
                contents = path.read_text(encoding="utf-8")
                self.assertIsNone(secret_pattern.search(contents), str(path))


if __name__ == "__main__":
    unittest.main()
