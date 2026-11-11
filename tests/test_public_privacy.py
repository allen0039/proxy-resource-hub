from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("public_privacy", ROOT / "tools/check_public_privacy.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class PublicPrivacyTests(unittest.TestCase):
    def test_checks_tests_and_docs_without_logging_sensitive_values(self):
        value = "PRIVATE_AUDIT_VALUE"
        findings = checker.findings("tests/fixture.py", f"value = '{value}'", [value])
        self.assertEqual([(1, "private publishing value")], findings)
        self.assertNotIn(value, str(findings))

    def test_source_addresses_must_use_documentation_ranges(self):
        self.assertFalse(checker.findings("tests/fixture.py", "SRC-IP,192.0.2.10,DIRECT", []))
        address = "10.1." + "2.3"
        self.assertEqual([(1, "device-specific source address")], checker.findings("tests/fixture.py", f"SRC-IP,{address},DIRECT", []))

    def test_private_tokens_and_paths_are_rejected(self):
        key = "tskey-auth-" + "x" * 32
        self.assertTrue(checker.findings("docs/example.md", key, []))
        path = "/Users/" + "private-person" + "/project"
        self.assertTrue(checker.findings("docs/example.md", path, []))

    def test_invalid_sample_urls_are_allowed_but_real_hosts_are_checked(self):
        self.assertFalse(checker.findings("tests/fixture.py", "https://service.invalid/sub?token=FAKE_TOKEN", []))
        url = "https://service.example.org/sub?" + "token=FAKE_TOKEN"
        self.assertEqual([(1, "credential in URL")], checker.findings("docs/example.md", url, []))


if __name__ == "__main__":
    unittest.main()
