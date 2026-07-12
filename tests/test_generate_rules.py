import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_rules.py"


def load_generator():
    if not GENERATOR_PATH.exists():
        raise AssertionError("rule generator is not implemented")
    spec = importlib.util.spec_from_file_location("generate_rules", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("rule generator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuleGeneratorTests(unittest.TestCase):
    def test_parse_source_rejects_duplicates(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.txt"
            path.write_text("example.com\nexample.com\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate domain"):
                generator.parse_source(path)

    def test_parse_source_rejects_urls(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.txt"
            path.write_text("https://example.com/path\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid domain"):
                generator.parse_source(path)

    def test_parse_source_rejects_uppercase_domains(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.txt"
            path.write_text("Example.com\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid domain"):
                generator.parse_source(path)

    def test_render_platform_formats(self):
        generator = load_generator()
        lines = ["# Group", "example.com", ""]

        classical = generator.render(
            lines, "classical", "Rules/Source/AI/test.txt"
        )
        quantumultx = generator.render(
            lines, "quantumultx", "Rules/Source/AI/test.txt"
        )

        self.assertIn("# Group", classical)
        self.assertIn("DOMAIN-SUFFIX,example.com", classical)
        self.assertIn("host-suffix, example.com, proxy", quantumultx)
        self.assertTrue(classical.endswith("\n"))
        self.assertTrue(quantumultx.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
