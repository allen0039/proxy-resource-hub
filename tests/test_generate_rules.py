import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_rules.py"
PT_DOMAINS = (
    "agsvpt.com",
    "audiences.me",
    "btschool.club",
    "crabpt.vip",
    "cyanbug.net",
    "discfan.net",
    "hdarea.club",
    "hddolby.com",
    "hdfans.org",
    "hdhome.org",
    "hdkyl.in",
    "hdsky.me",
    "hhanclub.net",
    "keepfrds.com",
    "lemonhd.club",
    "m-team.cc",
    "momentpt.top",
    "nicept.net",
    "open.cd",
    "ourbits.club",
    "piggo.me",
    "ptchdbits.co",
    "pterclub.com",
    "ptlgs.org",
    "ptsbao.club",
    "ptskit.com",
    "pttime.org",
    "qingwapt.com",
    "soulvoice.club",
    "springsunday.net",
    "sunnypt.top",
    "totheglory.im",
    "ubits.club",
    "ultrahd.net",
    "zhuque.in",
    "zmpt.cc",
)
PT_EXCLUSIONS = {
    "pting.club",
    "invites.fun",
    "dian115.com",
    "hdhive.com",
    "milkie.cc",
    "hd-torrents.org",
    "cdn.jsdelivr.net",
    "mediaarea.net",
    "github.com",
    "pixhost.to",
    "ptyqm.com",
    "rutracker.org",
}
SHOP_REQUIRED_DOMAINS = {
    "amazon.com",
    "amazon.co.jp",
    "amazon.co.uk",
    "amazonpay.com",
    "amazonimages.com",
    "images-amazon.com",
    "ssl-images-amazon.com",
    "ebay.com",
    "ebaycdn.net",
    "ebayimg.com",
    "ebaystatic.com",
    "rei.com",
    "backcountry.com",
    "steepandcheap.com",
    "competitivecyclist.com",
    "arcteryx.com",
    "patagonia.com",
    "thenorthface.com",
    "campsaver.com",
    "gearx.com",
    "evo.com",
    "sierra.com",
}
SHOP_EXCLUSIONS = {
    "amazonaws.com",
    "cloudfront.net",
    "primevideo.com",
    "amazonvideo.com",
    "media-amazon.com",
    "audible.com",
    "kindle.com",
    "imdb.com",
}
AI_PRIORITY_DOMAINS = (
    "gateway.ai.cloudflare.com",
    "gemini.gstatic.com",
    "default.exp-tas.com",
    "copilot-proxy.githubusercontent.com",
    "origin-tracker.githubusercontent.com",
    "copilot-telemetry.githubusercontent.com",
    "githubcopilot.com",
)


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

    def test_output_map_contains_all_expected_files(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        self.assertEqual(21, len(outputs))
        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            for ruleset in ("ai", "direct-ai"):
                expected = ROOT / "Rules" / client / "AI" / f"{ruleset}.list"
                self.assertIn(expected, outputs)
        for ruleset in ("ai", "direct-ai"):
            retired = ROOT / "Rules" / "AI" / f"{ruleset}.list"
            self.assertNotIn(retired, outputs)
            self.assertFalse(retired.exists())
        compatibility = ROOT / "Rules" / "shop" / "shopping.list"
        self.assertIn(compatibility, outputs)
        self.assertTrue(compatibility.exists())

    def test_personal_sites_outputs_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        source = ROOT / "Rules" / "Source" / "Personal" / "Domain.txt"
        old_source = ROOT / "Rules" / "Source" / "Personal" / "sites.txt"
        expected_domains = (
            "ikirito.de",
            "allennas.de",
            "052909.xyz",
            "mfallen.de",
        )

        self.assertTrue(source.exists())
        self.assertFalse(old_source.exists())
        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            path = ROOT / "Rules" / client / "Personal" / "Domain.list"
            old_path = ROOT / "Rules" / client / "Personal" / "sites.list"
            self.assertIn(path, outputs)
            self.assertNotIn(old_path, outputs)
            self.assertFalse(old_path.exists())
            content = outputs[path]
            rule_lines = tuple(
                line
                for line in content.splitlines()
                if line and not line.startswith("#")
            )
            if client == "QuantumultX":
                expected_lines = tuple(
                    f"host-suffix, {domain}, proxy" for domain in expected_domains
                )
            else:
                expected_lines = tuple(
                    f"DOMAIN-SUFFIX,{domain}" for domain in expected_domains
                )
            self.assertEqual(expected_lines, rule_lines)

    def test_ai_priority_domains_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        source = ROOT / "Rules" / "Source" / "AI" / "ai.txt"
        source_domains = {
            line
            for line in source.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        }
        self.assertTrue(set(AI_PRIORITY_DOMAINS).issubset(source_domains))

        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            path = ROOT / "Rules" / client / "AI" / "ai.list"
            content = outputs[path]
            for domain in AI_PRIORITY_DOMAINS:
                with self.subTest(client=client, domain=domain):
                    if client == "QuantumultX":
                        self.assertIn(f"host-suffix, {domain}, proxy", content)
                    else:
                        self.assertIn(f"DOMAIN-SUFFIX,{domain}", content)

    def test_pt_outputs_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        source = ROOT / "Rules" / "Source" / "PT" / "Domain.txt"
        self.assertTrue(source.exists(), "PT source file is missing")
        source_domains = tuple(
            line
            for line in source.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        )

        self.assertEqual(36, len(PT_DOMAINS))
        self.assertEqual(tuple(sorted(PT_DOMAINS)), PT_DOMAINS)
        self.assertEqual(PT_DOMAINS, source_domains)
        self.assertTrue(PT_EXCLUSIONS.isdisjoint(source_domains))

        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            path = ROOT / "Rules" / client / "PT" / "Domain.list"
            self.assertIn(path, outputs)
            rule_lines = tuple(
                line
                for line in outputs[path].splitlines()
                if line and not line.startswith("#")
            )
            if client == "QuantumultX":
                expected_lines = tuple(
                    f"host-suffix, {domain}, proxy" for domain in PT_DOMAINS
                )
            else:
                expected_lines = tuple(
                    f"DOMAIN-SUFFIX,{domain}" for domain in PT_DOMAINS
                )
            self.assertEqual(expected_lines, rule_lines)
            self.assertFalse(
                any(excluded in outputs[path] for excluded in PT_EXCLUSIONS)
            )

    def test_shop_outputs_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        source = ROOT / "Rules" / "Source" / "shop" / "shopping.txt"
        self.assertTrue(source.exists(), "shop source file is missing")
        source_domains = {
            line
            for line in source.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        }

        self.assertTrue(SHOP_REQUIRED_DOMAINS.issubset(source_domains))
        self.assertTrue(SHOP_EXCLUSIONS.isdisjoint(source_domains))

        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            path = ROOT / "Rules" / client / "shop" / "shopping.list"
            self.assertIn(path, outputs)
            content = outputs[path]
            self.assertTrue(all(domain in content for domain in SHOP_REQUIRED_DOMAINS))
            self.assertFalse(any(domain in content for domain in SHOP_EXCLUSIONS))

        compatibility = ROOT / "Rules" / "shop" / "shopping.list"
        self.assertIn(compatibility, outputs)
        self.assertTrue(
            all(
                line.startswith("DOMAIN-SUFFIX,")
                for line in outputs[compatibility].splitlines()
                if line and not line.startswith("#")
            )
        )

    def test_check_mode_detects_a_stale_output(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "Rules" / "Source" / "AI"
            source_dir.mkdir(parents=True)
            for name in ("ai", "direct-ai"):
                (source_dir / f"{name}.txt").write_text(
                    "example.com\n", encoding="utf-8"
                )
            personal_dir = root / "Rules" / "Source" / "Personal"
            personal_dir.mkdir(parents=True)
            (personal_dir / "Domain.txt").write_text(
                "example.com\n", encoding="utf-8"
            )
            pt_dir = root / "Rules" / "Source" / "PT"
            pt_dir.mkdir(parents=True)
            (pt_dir / "Domain.txt").write_text(
                "example.com\n", encoding="utf-8"
            )
            shop_dir = root / "Rules" / "Source" / "shop"
            shop_dir.mkdir(parents=True)
            (shop_dir / "shopping.txt").write_text(
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
