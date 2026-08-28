from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "tools" / "update_egern_rules.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "update-skk-rules.yml"


def load_updater():
    spec = importlib.util.spec_from_file_location("update_egern_rules", UPDATER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Egern updater cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skk_source(*rules: str, license_marker: str = "AGPL 3.0") -> str:
    return "\n".join(
        (
            "# Last Updated: 2026-08-28T00:00:00.000Z",
            f"# License: {license_marker}",
            "# GitHub: https://github.com/SukkaW/Surge",
            *rules,
            "",
        )
    )


class EgernRuleUpdaterTests(unittest.TestCase):
    def test_classical_types_render_as_native_egern_yaml(self):
        updater = load_updater()
        rules = updater.parse_classical(
            "\n".join(
                (
                    "DOMAIN,exact.example",
                    "DOMAIN-SUFFIX,.suffix.example",
                    "DOMAIN-SUFFIX,.data",
                    "DOMAIN-KEYWORD,keyword",
                    "DOMAIN-WILDCARD,*.wild.example",
                    "IP-CIDR,192.0.2.1/24,no-resolve",
                    "IP-CIDR6,2001:db8::1/32,no-resolve",
                    "IP-ASN,AS13335,no-resolve",
                    "USER-AGENT,Example*",
                    'PROCESS-NAME,"Example App"',
                    r"URL-REGEX,^https://example\\.com/",
                )
            ),
            "sample",
        )
        content = updater.render_egern(rules, ("google",))
        parsed = yaml.safe_load(content)

        self.assertEqual(["exact.example"], parsed["domain_set"])
        self.assertEqual(["suffix.example", "data"], parsed["domain_suffix_set"])
        self.assertEqual(["192.0.2.0/24"], parsed["ip_cidr_set"])
        self.assertEqual(["2001:db8::/32"], parsed["ip_cidr6_set"])
        self.assertEqual(["13335"], parsed["asn_set"])
        self.assertEqual(["Example App"], parsed["process_name_set"])
        self.assertTrue(parsed["no_resolve"])

    def test_unknown_types_and_options_fail_closed(self):
        updater = load_updater()
        with self.assertRaisesRegex(ValueError, "unsupported rule type"):
            updater.parse_classical("DEST-PORT,443", "sample")
        with self.assertRaisesRegex(ValueError, "unsupported rule option"):
            updater.parse_classical("DOMAIN,example.com,extended-matching", "sample")

    def test_only_known_config_level_composite_is_skipped(self):
        updater = load_updater()
        known = "AND,((PROTOCOL,UDP), (DOMAIN-SUFFIX,googlevideo.com))"
        rules = updater.parse_classical(
            skk_source("DOMAIN,keep.example", known), "skk_reject_no_drop"
        )
        self.assertEqual([("DOMAIN", "keep.example")], rules)
        with self.assertRaisesRegex(ValueError, "unsupported rule type"):
            updater.parse_classical(known, "another_source")

    def test_invalid_source_does_not_replace_existing_output(self):
        updater = load_updater()
        sources = {}
        for key, (kind, _url, _minimum, license_id) in updater.SOURCE_SPECS.items():
            body = ".example.com" if kind == "domainset" else "DOMAIN,example.com"
            marker = "CC BY-SA 2.0" if license_id == "CC-BY-SA-2.0" else "AGPL 3.0"
            sources[key] = skk_source(body, license_marker=marker) if license_id else body + "\n"
        sources["google"] = "UNKNOWN,broken\n"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "Rules/Egern/SKK/AI.yaml"
            existing.parent.mkdir(parents=True)
            existing.write_text("existing\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                updater.sync_outputs(root, sources)
            self.assertEqual("existing\n", existing.read_text(encoding="utf-8"))

    def test_output_contract_covers_surge_parity_and_broken_owned_urls(self):
        updater = load_updater()
        paths = {path.as_posix() for path in updater.OUTPUT_SPECS}
        expected = {
            "Rules/Egern/SKK/AI.yaml",
            "Rules/Egern/SKK/Reject.yaml",
            "Rules/Egern/SKK/LAN.yaml",
            "Rules/Egern/SKK/Domestic.yaml",
            "Rules/Egern/SKK/AppleCN.yaml",
            "Rules/Egern/SKK/MicrosoftCDN.yaml",
            "Rules/Egern/SKK/Stream.yaml",
            "Rules/Egern/SKK/CDN.yaml",
            "Rules/Egern/Google/Google.yaml",
            "Rules/Egern/Games/Sony.yaml",
            "Rules/Egern/Media/GlobalMedia.yaml",
            "Rules/Egern/AI/AIGC.yaml",
            "Rules/Egern/Media/ChinaMedia.yaml",
            "Rules/Egern/Services/ChinaTelecom.yaml",
            "Rules/Egern/Services/Docker.yaml",
            "Rules/Egern/Services/Speedtest.yaml",
            "Rules/Egern/Social/Threads.yaml",
            "Rules/Egern/Social/WhatsApp.yaml",
        }
        self.assertEqual(expected, paths)

    def test_committed_outputs_are_native_yaml_and_above_minimum(self):
        updater = load_updater()
        for relative_path in updater.OUTPUT_SPECS:
            with self.subTest(path=relative_path):
                path = ROOT / relative_path
                self.assertTrue(path.is_file())
                parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)
                self.assertTrue(set(parsed) & set(updater.FIELD_ORDER))

    def test_daily_workflow_updates_public_egern_outputs(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("python3 tools/update_egern_rules.py", workflow)
        self.assertIn("Rules/Egern", workflow)
        self.assertNotIn("git add Configs", workflow)
        self.assertNotIn("git add .", workflow)

    def test_public_egern_config_has_surge_parity_order_and_owned_url_closure(self):
        config_path = ROOT / "Configs/tool_config/egern_byallen.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        rules = config["rules"]
        active_rule_sets = [
            payload
            for rule in rules
            for kind, payload in rule.items()
            if kind == "rule_set" and not payload.get("disabled", False)
        ]
        matches = [payload["match"] for payload in active_rule_sets]
        markers = [
            "Rules/Egern/Custom/direct.yaml",
            "Rules/Egern/SKK/Reject.yaml",
            "Rules/Egern/Services/Speedtest.yaml",
            "Rules/Egern/SKK/LAN.yaml",
            "Rules/Egern/SKK/Domestic.yaml",
            "Rules/Egern/SKK/AppleCN.yaml",
            "Rules/Egern/SKK/MicrosoftCDN.yaml",
            "Rules/Egern/SKK/AI.yaml",
            "Rules/Egern/AI/AIGC.yaml",
            "Rules/Egern/Google/Google.yaml",
            "Rules/Egern/Games/Sony.yaml",
            "Rules/Egern/SKK/CDN.yaml",
            "Rules/Egern/Media/GlobalMedia.yaml",
            "Rules/Egern/SKK/Stream.yaml",
        ]
        positions = [
            next(index for index, match in enumerate(matches) if marker in match)
            for marker in markers
        ]
        self.assertEqual(positions, sorted(positions))

        owned_prefix = (
            "https://raw.githubusercontent.com/allen0039/"
            "proxy-resource-hub/main/"
        )
        for match in matches:
            if match.startswith(owned_prefix):
                self.assertTrue((ROOT / match.removeprefix(owned_prefix)).is_file())

        and_rules = [rule["and"] for rule in rules if "and" in rule]
        self.assertEqual(1, len(and_rules))
        self.assertEqual("REJECT", and_rules[0]["policy"])
        self.assertEqual(
            [
                {"protocol": {"match": "udp"}},
                {"domain_suffix": {"match": "googlevideo.com"}},
            ],
            and_rules[0]["match"],
        )


if __name__ == "__main__":
    unittest.main()
