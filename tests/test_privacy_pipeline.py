from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("privacy_sanitizer", ROOT / "tools/sanitize_tool_configs.py")
sanitizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sanitizer)


class PrivacyPipelineTests(unittest.TestCase):
    def source(self, proxies: str) -> str:
        return f"""proxy-providers:
  Original: {{url: 'https://subscription.invalid/private', type: http}}
proxies: {proxies}
secret: FAKE_PASSWORD
proxy-groups:
  - name: Proxy
    type: select
    use: [Original]
rules: ['MATCH,Proxy']
rule-providers: {{}}
"""

    def test_inline_and_nested_proxy_credentials_are_sanitized(self):
        text = self.source(
            "[{name: Node, type: trojan, server: node.invalid, password: FAKE_PASSWORD, "
            "reality-opts: {private-key: FAKE_PRIVATE_KEY, public-key: FAKE_PUBLIC_KEY}, "
            "ws-opts: {headers: {Authorization: FAKE_AUTHORIZATION}}}]"
        )
        output = sanitizer.sanitize_mihomo(text)
        sanitizer.validate_client_structure("mihomo_allen.yaml", output)
        parsed = yaml.safe_load(output)
        self.assertEqual("CHANGE_ME", parsed["proxies"][0]["password"])
        self.assertEqual("example.com", parsed["proxies"][0]["server"])
        self.assertEqual({}, parsed["proxies"][0]["ws-opts"]["headers"])
        self.assertEqual("CHANGE_ME", parsed["proxies"][0]["reality-opts"]["private-key"])
        self.assertEqual("获取到的订阅链接", parsed["proxy-providers"]["拼好鸡"]["url"])
        self.assertNotIn("FAKE_PASSWORD", output)

    def test_validator_independently_rejects_inline_credentials(self):
        text = (ROOT / "Configs/tool_config/mihomo_allen.yaml").read_text()
        parsed = yaml.safe_load(text)
        parsed["proxies"] = [{"name": "Node", "type": "trojan", "server": "example.com", "password": "FAKE_PASSWORD"}]
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.validate_client_structure("mihomo_allen.yaml", yaml.safe_dump(parsed))

    def test_aliases_are_sanitized_without_disclosing_source_exceptions(self):
        text = self.source("[{name: Node, type: trojan, server: node.invalid, password: *password}]")
        text = "shared-password: &password FAKE_PASSWORD\n" + text
        output = sanitizer.sanitize_mihomo(text)
        self.assertNotIn("FAKE_PASSWORD", output)
        parsed = yaml.safe_load(output)
        self.assertEqual("CHANGE_ME", parsed["proxies"][0]["password"])
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.sanitize_mihomo("proxy-providers: [\nprivate-secret")

    def test_all_eight_outputs_are_validated(self):
        outputs = {
            name: (ROOT / "Configs/tool_config" / name).read_text()
            for name in sanitizer.CONFIG_NAMES
        }
        self.assertEqual(8, len(outputs))
        sanitizer.validate_sanitized_outputs(outputs)

    def test_private_policy_drops_rules_without_touching_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "private"
            source.mkdir()
            template = (ROOT / "Configs/tool_config/surge_iphone_allen.conf").read_text()
            template = template.replace("[Rule]", "[Rule]\nDOMAIN-SUFFIX,private-service.invalid,DIRECT")
            path = source / "Surge-iPhone.conf"
            path.write_text(template)
            policy = source / ".private/publish-privacy.json"
            policy.parent.mkdir()
            policy.write_text(json.dumps({"private_domains": ["private-service.invalid"]}))
            outputs = sanitizer.generate(source, Path(temporary) / "public", only={"Surge-iPhone.conf"})
            self.assertNotIn("private-service.invalid", next(iter(outputs.values())))
            self.assertEqual(template, path.read_text())

    def test_recursive_aliases_fail_closed(self):
        text = self.source("[]")
        text += "cycle: &cycle {nested: *cycle}\n"
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.sanitize_mihomo(text)

    def test_commented_credentials_are_redacted_and_independently_checked(self):
        text = self.source("[]") + "# password: FAKE_PASSWORD\n"
        output = sanitizer.sanitize_mihomo(text)
        self.assertNotIn("FAKE_PASSWORD", output)
        self.assertIn("# password: CHANGE_ME", output)
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.validate_common_patterns("mihomo_allen.yaml", text)


if __name__ == "__main__":
    unittest.main()
