"""Tests for the scanner rule registry."""

import unittest

from python_challenge.rules import RULES


class RuleRegistryTests(unittest.TestCase):
    """Verify rules have stable, unique identifiers."""

    def test_rule_identifiers_are_unique_and_non_empty(self) -> None:
        identifiers = [rule.identifier for rule in RULES]

        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(identifiers))

    def test_expected_rules_are_registered(self) -> None:
        identifiers = {rule.identifier for rule in RULES}

        self.assertEqual(
            identifiers,
            {
                "password-assignment",
                "api-key-assignment",
                "access-token-assignment",
                "client-secret-assignment",
            },
        )


if __name__ == "__main__":
    unittest.main()
