from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "config_sync_sanitizer", ROOT / "tools" / "sanitize_tool_configs.py"
)
sanitizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sanitizer)


class ConfigSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "private"
        self.output = Path(self.temp.name) / "public"
        self.source.mkdir()
        for source, target in sanitizer.OUTPUT_NAMES.items():
            self.source.joinpath(source).write_text(
                (ROOT / "Configs" / "tool_config" / target).read_text().replace(
                    "获取到的订阅链接", "https://example.com/subscription"
                )
            )

    def test_check_detects_drift_without_writing_or_disclosing_content(self):
        sanitizer.generate(self.source, self.output)
        self.assertEqual(6, len(sanitizer.generate(self.source, self.output, check=True)))
        target = self.output / "surge_mac_allen.conf"
        target.write_text(target.read_text() + "# drift sentinel\n")
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/sanitize_tool_configs.py"),
             "--source-dir", str(self.source), "--output-dir", str(self.output), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("surge_mac_allen.conf", result.stderr)
        self.assertNotIn("drift sentinel", result.stderr)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_check_missing_output_does_not_create_directory(self):
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.generate(self.source, self.output, check=True)
        self.assertFalse(self.output.exists())

    def test_only_accepts_single_source_and_preserves_other_outputs(self):
        for path in self.source.iterdir():
            if path.name != "Surge-iPhone.conf":
                path.unlink()
        self.output.mkdir()
        untouched = self.output / "egern_byallen.yaml"
        untouched.write_text("unrelated template")
        result = sanitizer.generate(
            self.source, self.output, only={"Surge-iPhone.conf"}
        )
        self.assertEqual({"surge_iphone_allen.conf"}, set(result))
        self.assertEqual("unrelated template", untouched.read_text())

    def test_validation_failure_does_not_partially_update_templates(self):
        sanitizer.generate(self.source, self.output)
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        (self.source / "egern_byallen.yaml").write_text("invalid: [")
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.generate(self.source, self.output)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_rejects_output_directory_that_would_overwrite_private_sources(self):
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.generate(self.source, self.source)


if __name__ == "__main__":
    unittest.main()
