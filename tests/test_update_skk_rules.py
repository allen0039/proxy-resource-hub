import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "tools" / "update_skk_rules.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "update-skk-rules.yml"
AGPL_LICENSE_PATH = ROOT / "LICENSES" / "AGPL-3.0-only.txt"
SKK_NOTICE_PATH = ROOT / "Rules" / "SKK" / "README.md"


def load_updater():
    if not UPDATER_PATH.exists():
        raise AssertionError("SKK updater is not implemented")
    spec = importlib.util.spec_from_file_location("update_skk_rules", UPDATER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("SKK updater cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skk_source(*rules: str, updated: str = "2026-07-18T00:00:00.000Z") -> str:
    return "\n".join(
        (
            "#########################################",
            "# Test ruleset",
            f"# Last Updated: {updated}",
            f"# Size: {len(rules)}",
            "# License: AGPL 3.0",
            "# GitHub: https://github.com/SukkaW/Surge",
            "#########################################",
            *rules,
            "################## EOF ##################",
            "",
        )
    )


def sample_sources() -> dict[str, str]:
    return {
        "cdn_domainset": skk_source("assets.example", ".static.example"),
        "cdn_non_ip": skk_source(
            "DOMAIN,assets.example",
            "DOMAIN-KEYWORD,asset-cdn",
            "DOMAIN-WILDCARD,cdn*.example",
        ),
        "download_domainset": skk_source("files.example", ".packages.example"),
        "download_non_ip": skk_source(
            "DOMAIN,files.example",
            "DOMAIN-WILDCARD,download*.example",
            r"URL-REGEX,^http://(.+)\.example/files",
        ),
    }


MINIMUMS = {key: 1 for key in sample_sources()}


class SkkRuleUpdaterTests(unittest.TestCase):
    def test_domainset_and_non_ip_rules_are_converted_for_qx_and_loon(self):
        updater = load_updater()

        outputs = updater.build_outputs(sample_sources(), minimum_counts=MINIMUMS)

        qx_cdn = outputs[Path("Rules/QuantumultX/SKK/CDN.list")]
        self.assertIn("host, assets.example, proxy", qx_cdn)
        self.assertIn("host-suffix, static.example, proxy", qx_cdn)
        self.assertIn("host-keyword, asset-cdn, proxy", qx_cdn)
        self.assertIn("host-wildcard, cdn*.example, proxy", qx_cdn)
        self.assertEqual(qx_cdn.count("host, assets.example, proxy"), 1)

        qx_download = outputs[Path("Rules/QuantumultX/SKK/Download.list")]
        self.assertIn("host-wildcard, download*.example, proxy", qx_download)
        self.assertIn(r"url-regex, ^http://(.+)\.example/files, proxy", qx_download)

        loon_cdn = outputs[Path("Rules/Loon/SKK/CDN.list")]
        self.assertIn("DOMAIN,assets.example", loon_cdn)
        self.assertIn("DOMAIN-SUFFIX,static.example", loon_cdn)
        self.assertIn("DOMAIN-KEYWORD,asset-cdn", loon_cdn)
        self.assertIn("DOMAIN-WILDCARD,cdn*.example", loon_cdn)
        self.assertEqual(loon_cdn.count("DOMAIN,assets.example"), 1)

        loon_download = outputs[Path("Rules/Loon/SKK/Download.list")]
        self.assertIn(r"URL-REGEX,^http://(.+)\.example/files", loon_download)

    def test_outputs_record_upstream_sources_and_agpl_license(self):
        updater = load_updater()

        outputs = updater.build_outputs(sample_sources(), minimum_counts=MINIMUMS)

        for content in outputs.values():
            self.assertIn("SPDX-License-Identifier: AGPL-3.0-only", content)
            self.assertIn("https://github.com/SukkaW/Surge", content)
            self.assertIn("https://ruleset.skk.moe/", content)
            self.assertIn("Upstream Last Updated: 2026-07-18T00:00:00.000Z", content)

    def test_upstream_rule_count_shrinkage_is_rejected(self):
        updater = load_updater()
        minimums = dict(MINIMUMS)
        minimums["cdn_domainset"] = 3

        with self.assertRaisesRegex(ValueError, "cdn_domainset.*minimum"):
            updater.build_outputs(sample_sources(), minimum_counts=minimums)

    def test_unknown_non_ip_rule_type_is_rejected(self):
        updater = load_updater()
        sources = sample_sources()
        sources["cdn_non_ip"] = skk_source("PROCESS-NAME,unexpected")

        with self.assertRaisesRegex(ValueError, "unsupported rule type"):
            updater.build_outputs(sources, minimum_counts=MINIMUMS)

    def test_invalid_source_does_not_overwrite_existing_outputs(self):
        updater = load_updater()
        sources = sample_sources()
        sources["download_domainset"] = skk_source("not a domain")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "Rules" / "QuantumultX" / "SKK" / "CDN.list"
            existing.parent.mkdir(parents=True)
            existing.write_text("existing\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.sync_outputs(
                    root, sources, minimum_counts=MINIMUMS
                )

            self.assertEqual("existing\n", existing.read_text(encoding="utf-8"))

    def test_committed_outputs_are_complete(self):
        updater = load_updater()
        expected = {
            ROOT / "Rules" / "QuantumultX" / "SKK" / "CDN.list": 4000,
            ROOT / "Rules" / "QuantumultX" / "SKK" / "Download.list": 1500,
            ROOT / "Rules" / "Loon" / "SKK" / "CDN.list": 4000,
            ROOT / "Rules" / "Loon" / "SKK" / "Download.list": 1500,
        }

        for path, minimum in expected.items():
            with self.subTest(path=path):
                self.assertTrue(path.exists())
                rules = [
                    line
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#")
                ]
                self.assertGreaterEqual(len(rules), minimum)
                self.assertEqual(len(rules), len(set(rules)))

    def test_daily_workflow_updates_only_public_skk_outputs(self):
        self.assertTrue(WORKFLOW_PATH.exists())
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

        self.assertRegex(workflow, r"cron:\s*[\"']?17 20 \* \* \*")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("python3 tools/update_skk_rules.py", workflow)
        self.assertIn("Rules/QuantumultX/SKK/CDN.list", workflow)
        self.assertIn("Rules/QuantumultX/SKK/Download.list", workflow)
        self.assertIn("Rules/Loon/SKK/CDN.list", workflow)
        self.assertIn("Rules/Loon/SKK/Download.list", workflow)
        self.assertNotIn("git add Configs", workflow)
        self.assertNotIn("git add .", workflow)

    def test_skk_derivatives_include_license_and_notice(self):
        self.assertTrue(AGPL_LICENSE_PATH.exists())
        license_text = AGPL_LICENSE_PATH.read_text(encoding="utf-8")
        self.assertIn("GNU AFFERO GENERAL PUBLIC LICENSE", license_text)
        self.assertIn("Version 3, 19 November 2007", license_text)

        self.assertTrue(SKK_NOTICE_PATH.exists())
        notice = SKK_NOTICE_PATH.read_text(encoding="utf-8")
        self.assertIn("SukkaW/Surge", notice)
        self.assertIn("AGPL-3.0-only", notice)
        self.assertIn("tools/update_skk_rules.py", notice)


if __name__ == "__main__":
    unittest.main()
