import importlib.util
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SANITIZER_PATH = ROOT / "tools" / "sanitize_tool_configs.py"
OUTPUT_DIR = ROOT / "Configs" / "tool_config"
CONFIG_NAMES = {
    "mihomo_allen.yaml",
    "surge_mac_allen.conf",
    "surge_iphone_allen.conf",
    "quantumultx_allen.conf",
    "loon_allen.lcf",
}

PUBLIC_RULE_URL = "https://public.example/rules.list"
PRIVATE_URL = "https://private.invalid/sub?token=FAKE_TOKEN"
SURGE_PT_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "Rules/Surge/PT/Domain.list"
)
QX_PT_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "Rules/QuantumultX/PT/Domain.list"
)
LOON_PT_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "Rules/Loon/PT/Domain.list"
)
MIHOMO_PT_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "Rules/Mihomo/PT/Domain.list"
)
DUPLICATE_PT_VALUES = {
    "piggo.me",
    "pt.keepfrds.com",
    "ourbits.club",
    "sunnypt.top",
    "open.cd",
    "ultrahd.net",
    "audiences.me",
    "pterclub.com",
    "springsunday.net",
}


def load_sanitizer():
    if not SANITIZER_PATH.exists():
        raise AssertionError("tool config sanitizer is not implemented")
    spec = importlib.util.spec_from_file_location(
        "sanitize_tool_configs", SANITIZER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("tool config sanitizer cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SanitizedToolConfigTests(unittest.TestCase):
    def test_generator_uses_current_mihomo_source_filename(self):
        sanitizer = load_sanitizer()

        self.assertIn("mihomo_byallen.yaml", sanitizer.OUTPUT_NAMES)
        self.assertNotIn("mihomo_byallen-nokey.yaml", sanitizer.OUTPUT_NAMES)

    def test_normalize_text_removes_trailing_whitespace(self):
        sanitizer = load_sanitizer()

        self.assertEqual("one\n two\n", sanitizer.normalize_text("one  \r\n two\t \n"))

    def test_surge_replaces_policy_paths_and_mitm_material(self):
        sanitizer = load_sanitizer()
        source = f"""[General]
loglevel = notify

[Proxy Group]
Proxy = select, policy-path={PRIVATE_URL}, DIRECT, img-url=https://public.example/icon.png

[Rule]
RULE-SET,{PUBLIC_RULE_URL},Proxy
FINAL,Proxy

[MITM]
hostname = example.org
ca-passphrase = FAKE_PASSWORD
ca-p12 = FAKE_P12_BASE64
"""

        result = sanitizer.sanitize_surge(source, "surge-mac")

        self.assertNotIn("private.invalid", result)
        self.assertNotIn("FAKE_PASSWORD", result)
        self.assertNotIn("FAKE_P12_BASE64", result)
        self.assertIn("https://example.com/surge-mac/subscription-1.conf", result)
        self.assertIn(PUBLIC_RULE_URL, result)
        self.assertIn("https://public.example/icon.png", result)
        self.assertIn("Configure MITM certificate and passphrase locally", result)
        sanitizer.validate_client_structure("surge_mac_allen.conf", result)

    def test_quantumultx_replaces_remote_servers_and_removes_local_nodes(self):
        sanitizer = load_sanitizer()
        source = f"""[policy]
static=Proxy, direct

[server_remote]
{PRIVATE_URL}, tag=One, enabled=true, resource-parser=https://public.example/parser.js
https://private.invalid/two, tag=Two, enabled=false
;https://private.invalid/commented, tag=Backup, enabled=false

[server_local]
shadowsocks=private.invalid:443, password=FAKE_PASSWORD
;vmess=private.invalid:443, password=FAKE-COMMENTED-UUID

[filter_remote]
{PUBLIC_RULE_URL}, tag=Rules, force-policy=Proxy, enabled=true

[filter_local]
final, Proxy

[mitm]
hostname = example.org
passphrase = FAKE_PASSWORD
p12 = FAKE_P12_BASE64
"""

        result = sanitizer.sanitize_quantumultx(source)

        self.assertNotIn("private.invalid", result)
        self.assertNotIn("FAKE_PASSWORD", result)
        self.assertNotIn("FAKE-COMMENTED-UUID", result)
        self.assertNotIn("FAKE_P12_BASE64", result)
        self.assertIn("https://example.com/quantumultx/subscription-1.conf", result)
        self.assertIn("https://example.com/quantumultx/subscription-2.conf", result)
        self.assertIn("Configure local proxy nodes privately", result)
        self.assertIn(PUBLIC_RULE_URL, result)
        self.assertIn("https://public.example/parser.js", result)
        sanitizer.validate_client_structure("quantumultx_allen.conf", result)

    def test_loon_replaces_remote_proxies_and_mitm_material(self):
        sanitizer = load_sanitizer()
        source = f"""[Proxy]
Local = Shadowsocks, private.invalid, 443, encrypt-method=aes-128-gcm, password=FAKE_PASSWORD

[Remote Proxy]
One = {PRIVATE_URL}, enabled=true, img-url=https://public.example/icon.png
Two = https://private.invalid/two, enabled=false
# Backup = https://private.invalid/commented, enabled=false

[Proxy Group]
Proxy = select, One, Two, DIRECT

[Rule]
FINAL,Proxy

[Remote Rule]
{PUBLIC_RULE_URL},policy=Proxy,tag=Rules,enabled=true

[Plugin]

[Mitm]
hostname = example.org
ca-p12 = FAKE_P12_BASE64
ca-passphrase = FAKE_PASSWORD
"""

        result = sanitizer.sanitize_loon(source)

        self.assertNotIn("private.invalid", result)
        self.assertNotIn("FAKE_PASSWORD", result)
        self.assertNotIn("FAKE_P12_BASE64", result)
        self.assertIn("https://example.com/loon/subscription-1.conf", result)
        self.assertIn("https://example.com/loon/subscription-2.conf", result)
        self.assertIn("Configure local proxy nodes privately", result)
        self.assertIn(PUBLIC_RULE_URL, result)
        self.assertIn("https://public.example/icon.png", result)
        sanitizer.validate_client_structure("loon_allen.lcf", result)

    def test_mihomo_renames_providers_and_replaces_secrets(self):
        sanitizer = load_sanitizer()
        source = f"""proxy-providers:
  PersonalName:
    url: \"{PRIVATE_URL}\"
    type: http
    interval: 86400
    health-check:
      enable: true
      url: https://public.example/generate_204
      interval: 300
proxies:
  - name: LocalNode
    type: vless
    server: private.invalid
    port: 443
    uuid: FAKE-UUID
secret: FAKE_SECRET
proxy-groups:
  - name: Proxy
    type: select
    use: [PersonalName]
    proxies: [LocalNode]
rules:
  - RULE-SET,gongyiai,DIRECT
  - MATCH,Proxy
rule-providers:
  gongyiai:
    type: http
    behavior: classical
    format: text
    url: {PUBLIC_RULE_URL}
    interval: 86400
"""

        result = sanitizer.sanitize_mihomo(source)
        parsed = yaml.safe_load(result)

        self.assertNotIn("private.invalid", result)
        self.assertNotIn("FAKE-UUID", result)
        self.assertNotIn("FAKE_SECRET", result)
        self.assertNotIn("PersonalName", result)
        self.assertIn("subscription_1", parsed["proxy-providers"])
        self.assertEqual(["subscription_1"], parsed["proxy-groups"][0]["use"])
        self.assertEqual("CHANGE_ME", parsed["secret"])
        self.assertEqual("example.com", parsed["proxies"][0]["server"])
        self.assertIn(PUBLIC_RULE_URL, result)

    def test_validator_rejects_a_private_endpoint(self):
        sanitizer = load_sanitizer()
        outputs = {
            name: "[General]\n" for name in CONFIG_NAMES if not name.endswith(".yaml")
        }
        outputs["mihomo_allen.yaml"] = "rules:\n  - MATCH,DIRECT\n"
        outputs["surge_mac_allen.conf"] += PRIVATE_URL

        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.validate_sanitized_outputs(outputs)

    def test_committed_outputs_are_safe_and_structurally_complete(self):
        self.assertTrue(OUTPUT_DIR.exists())
        actual = {
            path.name
            for path in OUTPUT_DIR.iterdir()
            if path.is_file() and path.name != "README.md"
        }
        self.assertEqual(CONFIG_NAMES, actual)
        self.assertFalse(
            {"surge-Mac.conf", "Surge-iPhone.conf", "mihomo_byallen-nokey.yaml"}
            & actual
        )

        sanitizer = load_sanitizer()
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        sanitizer.validate_sanitized_outputs(outputs)
        combined = "\n".join(outputs.values())
        self.assertIsNone(re.search(r"(?i)token=[^\s,]+", combined))
        self.assertNotIn("BEGIN PRIVATE KEY", combined)
        self.assertNotIn("BEGIN CERTIFICATE", combined)

        for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
            self.assertRegex(outputs[name], r"gongyiai\.list,DIRECT(?:,|\n)")
            self.assertRegex(
                outputs[name], r"Personal/Domain\.list,DIRECT(?:,|\n)"
            )
            self.assertEqual(1, outputs[name].count(SURGE_PT_URL))
            self.assertIn(f"RULE-SET,{SURGE_PT_URL},DIRECT", outputs[name])
        self.assertRegex(
            outputs["quantumultx_allen.conf"],
            r"gongyiai\.list[^\n]*force-policy=direct",
        )
        self.assertRegex(
            outputs["quantumultx_allen.conf"],
            r"Personal/Domain\.list[^\n]*force-policy=direct",
        )
        self.assertEqual(1, outputs["quantumultx_allen.conf"].count(QX_PT_URL))
        self.assertRegex(
            outputs["quantumultx_allen.conf"],
            r"Rules/QuantumultX/PT/Domain\.list[^\n]*force-policy=direct",
        )
        self.assertRegex(
            outputs["loon_allen.lcf"], r"gongyiai\.list[^\n]*policy=DIRECT"
        )
        self.assertRegex(
            outputs["loon_allen.lcf"], r"Personal/Domain\.list[^\n]*policy=DIRECT"
        )
        self.assertEqual(1, outputs["loon_allen.lcf"].count(LOON_PT_URL))
        self.assertRegex(
            outputs["loon_allen.lcf"],
            r"Rules/Loon/PT/Domain\.list[^\n]*policy=DIRECT",
        )
        mihomo = yaml.safe_load(outputs["mihomo_allen.yaml"])
        self.assertEqual(1, mihomo["rules"].count("RULE-SET,gongyiai,直连策略"))
        self.assertEqual(
            1, mihomo["rules"].count("RULE-SET,personal_domain,直连策略")
        )
        self.assertEqual(1, mihomo["rules"].count("RULE-SET,pt_domain,直连策略"))
        self.assertLess(
            mihomo["rules"].index("RULE-SET,pt_domain,直连策略"),
            mihomo["rules"].index("RULE-SET,pt_cn_domain,直连策略"),
        )
        self.assertEqual(MIHOMO_PT_URL, mihomo["rule-providers"]["pt_domain"]["url"])

        local_rule_pattern = re.compile(
            r"^\s*-?\s*(?:DOMAIN|DOMAIN-SUFFIX|HOST|HOST-SUFFIX)\s*,\s*([^,\s]+)",
            re.IGNORECASE,
        )
        for name, text in outputs.items():
            active_values = {
                match.group(1).casefold()
                for line in text.splitlines()
                if not line.lstrip().startswith(("#", ";", "//"))
                if (match := local_rule_pattern.match(line)) is not None
            }
            with self.subTest(name=name, check="duplicate PT local rules"):
                self.assertEqual(set(), DUPLICATE_PT_VALUES & active_values)

    def test_committed_outputs_exclude_private_custom_rule_keywords(self):
        private_keywords = {"oracle3", "allen0039"}
        rule_pattern = re.compile(
            r"^\s*-?\s*(?:DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|"
            r"HOST|HOST-SUFFIX|HOST-KEYWORD)\s*,\s*([^,\s]+)",
            re.IGNORECASE,
        )

        for name in CONFIG_NAMES:
            text = (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for line in text.splitlines():
                match = rule_pattern.match(line)
                if match is not None:
                    self.assertNotIn(match.group(1).casefold(), private_keywords)

    def test_committed_outputs_preserve_routing_optimizations(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        cloudflare_rules = {
            "surge_mac_allen.conf": "DOMAIN-SUFFIX,cloudflare.com,CDN",
            "surge_iphone_allen.conf": "DOMAIN-SUFFIX,cloudflare.com,CDN",
            "quantumultx_allen.conf": "host-suffix, cloudflare.com, CDN",
            "loon_allen.lcf": "DOMAIN-SUFFIX,cloudflare.com,CDN",
            "mihomo_allen.yaml": "DOMAIN-SUFFIX,cloudflare.com,CDN",
        }
        for name, rule in cloudflare_rules.items():
            with self.subTest(name=name, check="Cloudflare CDN"):
                self.assertEqual(outputs[name].count(rule), 1)

        mihomo = yaml.safe_load(outputs["mihomo_allen.yaml"])
        self.assertNotIn("gfw_domain", mihomo["rule-providers"])
        self.assertFalse(
            any(rule.startswith("RULE-SET,gfw_domain,") for rule in mihomo["rules"])
        )
        self.assertEqual(
            mihomo["rules"].count("RULE-SET,geolocation-!cn,Proxy"), 1
        )
        self.assertEqual(
            mihomo["rules"].count("RULE-SET,Cloudflare_domain,CDN"), 1
        )

        qx = outputs["quantumultx_allen.conf"]
        header = qx.split("[general]", maxsplit=1)[0]
        self.assertNotIn("1234567", header)
        self.assertIn("脱敏工具", header)
        self.assertNotRegex(qx, r"server-tag-regex=[^\n,]*(?:^|\|)(?:新|日|台|United)(?:\||,)")
        self.assertIn("United States", qx)
        self.assertIn("Singapore", qx)


if __name__ == "__main__":
    unittest.main()
