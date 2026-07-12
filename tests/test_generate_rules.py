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
    def test_all_generated_outputs_are_current(self):
        generator = load_generator()
        self.assertEqual([], generator.sync_outputs(ROOT, check=True))

    def test_output_map_contains_all_ten_files(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        self.assertEqual(10, len(outputs))
        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            for ruleset in ("ai", "gongyiai"):
                expected = ROOT / "Rules" / client / "AI" / f"{ruleset}.list"
                self.assertIn(expected, outputs)
        for ruleset in ("ai", "gongyiai"):
            legacy = ROOT / "Rules" / "AI" / f"{ruleset}.list"
            self.assertIn(legacy, outputs)

    def test_check_mode_detects_a_stale_output(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "Rules" / "Source" / "AI"
            source_dir.mkdir(parents=True)
            for name in ("ai", "gongyiai"):
                (source_dir / f"{name}.txt").write_text(
                    "example.com\n", encoding="utf-8"
                )
            generator.sync_outputs(root, check=False)
            stale_path = root / "Rules" / "Mihomo" / "AI" / "ai.list"
            stale_path.write_text("stale\n", encoding="utf-8")

            self.assertIn(stale_path, generator.sync_outputs(root, check=True))

    def test_generated_rule_lines_have_platform_specific_fields(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        for path, content in outputs.items():
            rule_lines = [line for line in content.splitlines() if line and not line.startswith("#")]
            if "QuantumultX" in path.parts:
                self.assertTrue(all(line.startswith("host-suffix, ") for line in rule_lines))
                self.assertTrue(all(line.endswith(", proxy") for line in rule_lines))
                self.assertTrue(all(len(line.split(", ")) == 3 for line in rule_lines))
            else:
                self.assertTrue(all(line.startswith("DOMAIN-SUFFIX,") for line in rule_lines))
                self.assertTrue(all(len(line.split(",")) == 2 for line in rule_lines))

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
