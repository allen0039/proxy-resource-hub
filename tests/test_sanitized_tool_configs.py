from __future__ import annotations

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
SUPPORTED_AI_REGION_ORDER = [
    "美国优选",
    "日本优选",
    "新加坡优选",
    "美国节点",
    "日本节点",
    "新加坡节点",
    "台湾节点",
    "韩国节点",
    "英国节点",
    "其他地区",
    "香港优选",
    "香港节点",
]
DOCKER_ICON_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "assets/docker.png?v=b5317ee"
)
LEGACY_DOCKER_ICON_URL = (
    "https://raw.githubusercontent.com/walkxcode/dashboard-icons/"
    "main/png/docker.png"
)
BROKEN_DOCKER_ICON_URL = (
    "https://raw.githubusercontent.com/Koolson/Qure/master/"
    "IconSet/Color/Docker.png"
)
CUSTOM_BASE_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
)
CUSTOM_FEEDS = {
    "direct": ("Custom/direct.list", "DIRECT"),
    "hk": ("Regional/hk.list", "香港节点"),
    "hk-auto": ("Regional/hk-auto.list", "香港优选"),
    "us": ("Regional/us.list", "美国节点"),
    "us-auto": ("Regional/us-auto.list", "美国优选"),
    "jp": ("Regional/jp.list", "日本节点"),
    "jp-auto": ("Regional/jp-auto.list", "日本优选"),
    "sg": ("Regional/sg.list", "新加坡节点"),
    "sg-auto": ("Regional/sg-auto.list", "新加坡优选"),
}
MIGRATED_LOCAL_RULES = (
    "synology.cn", "qbittorrent-nox", "digitalocean.com", "dyndns.com",
    "whatismyip.akamai.com", "volcengine", "xmwsyy.com", "ui.com",
    "imgse.com", "tagweb.vip", "yqc-premium", "ad.12306.cn",
    "gg.caixin.com", "sdkapp.uve.weibo.com", "ucweb.com", "amemv.com",
    "v4.plex.tv", "openwrt.ai", "lsposed.org", "hytron.io", "linux.do",
    "uspatriottactical", "hdhive", "rundongex.com", "servercontrolpanel.de",
    "mgboard.net", "sehuatang", "greasyfork", "qichiyu", "mjji.de",
    "hd-torrents", "embyapp.top", "vps.town", "2fa.fun", "macwk.cn",
    "appstorrent.ru", "kejilion", "nfbyte.com", "onitsukatiger",
    "compliance.chippercash.com", "dmm", "javrate", "jav321", "freejavbt",
    "javbus", "mgstage", "mmtv", "javdb", "javlibrary", "avbase",
    "missav", "ftvgirls",
)


def active_section(text: str, section: str, next_section: str | None = None) -> str:
    start = text.index(section) + len(section)
    end = text.index(next_section, start) if next_section else len(text)
    return text[start:end]


def custom_url(client: str, slug: str) -> str:
    path, _ = CUSTOM_FEEDS[slug]
    return f"{CUSTOM_BASE_URL}Rules/{client}/{path}"


def active_lines(section: str) -> list[str]:
    return [
        line
        for line in section.splitlines()
        if not line.lstrip().startswith(("#", ";", "//"))
    ]


def option_fields(line: str) -> list[tuple[str, str]]:
    return [
        (key.strip(), value.strip())
        for field in line.split(",")[1:]
        if "=" in field
        for key, value in [field.split("=", maxsplit=1)]
    ]


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
        self.assertIn("policy-path=获取到的订阅链接", result)
        self.assertIn("拼好鸡 = select", result)
        self.assertIn(PUBLIC_RULE_URL, result)
        self.assertIn("https://public.example/icon.png", result)
        self.assertIn("请在本机配置并信任 MitM 证书与口令", result)
        sanitizer.validate_client_structure("surge_mac_allen.conf", result)

    def test_surge_distinguishes_policy_path_docs_from_subscriptions(self):
        sanitizer = load_sanitizer()
        source = f"""[General]
loglevel = notify

[Proxy Group]
# 订阅使用说明：policy-path 是订阅地址，只替换等号后的 URL。
Primary = select, policy-path={PRIVATE_URL}, DIRECT
# Backup = select, policy-path=https://private.invalid/backup, DIRECT

[Rule]
FINAL,Primary

[MITM]
hostname = example.org
"""

        result = sanitizer.sanitize_surge(source, "surge-mac")

        self.assertIn("policy-path 是订阅地址", result)
        self.assertEqual(2, result.count("policy-path=获取到的订阅链接"))
        self.assertIn("拼好鸡 = select", result)
        self.assertIn("# 机场 = select", result)
        self.assertNotIn("private.invalid", result)
        sanitizer.validate_client_structure("surge_mac_allen.conf", result)

    def test_quantumultx_replaces_remote_servers_and_removes_local_nodes(self):
        sanitizer = load_sanitizer()
        source = f"""[policy]
static=Main, proxy, direct

[server_remote]
{PRIVATE_URL}, tag=One, enabled=true, resource-parser=https://public.example/parser.js
https://private.invalid/two, tag=Two, enabled=false
;https://private.invalid/commented, tag=Backup, enabled=false

[server_local]
shadowsocks=private.invalid:443, password=FAKE_PASSWORD
;vmess=private.invalid:443, password=FAKE-COMMENTED-UUID

[filter_remote]
{PUBLIC_RULE_URL}, tag=Rules, force-policy=Main, enabled=true

[filter_local]
final, Main

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
        self.assertEqual(3, result.count("获取到的订阅链接"))
        self.assertIn("tag=拼好鸡", result)
        self.assertIn("tag=机场", result)
        self.assertIn("请在本机配置代理节点", result)
        self.assertIn(PUBLIC_RULE_URL, result)
        self.assertIn("https://public.example/parser.js", result)
        sanitizer.validate_client_structure("quantumultx_allen.conf", result)

    def test_quantumultx_replaces_internal_preamble_with_public_title(self):
        sanitizer = load_sanitizer()
        source = f"""# Allen 维护 - Quantumult X 配置
# 维护说明
# - 公开版本请使用脱敏工具生成。
# - enabled=true 为启用，false 为保留但禁用。

[server_remote]
{PRIVATE_URL}, tag=One, enabled=true
"""

        result = sanitizer.sanitize_quantumultx(source)
        header = result.split("[server_remote]", maxsplit=1)[0]

        self.assertEqual("# Allen 维护 - Quantumult X 配置\n\n", header)

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
        self.assertEqual(3, result.count("获取到的订阅链接"))
        self.assertIn("拼好鸡 = 获取到的订阅链接", result)
        self.assertIn("机场 = 获取到的订阅链接", result)
        self.assertIn("请在本机配置代理节点", result)
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
  - RULE-SET,direct-ai,DIRECT
  - MATCH,Proxy
rule-providers:
  direct-ai:
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
        self.assertIn("拼好鸡", parsed["proxy-providers"])
        self.assertEqual(["拼好鸡"], parsed["proxy-groups"][0]["use"])
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
            self.assertRegex(outputs[name], r"direct-ai\.list,DIRECT(?:,|\n)")
            self.assertRegex(
                outputs[name], r"Personal/Domain\.list,DIRECT(?:,|\n)"
            )
            self.assertEqual(1, outputs[name].count(SURGE_PT_URL))
            self.assertIn(f"RULE-SET,{SURGE_PT_URL},DIRECT", outputs[name])
        self.assertRegex(
            outputs["quantumultx_allen.conf"],
            r"direct-ai\.list[^\n]*force-policy=direct",
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
            outputs["loon_allen.lcf"], r"direct-ai\.list[^\n]*policy=DIRECT"
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
        self.assertEqual(1, mihomo["rules"].count("RULE-SET,direct-ai,DIRECT"))
        self.assertIn("direct-ai", mihomo["rule-providers"])
        self.assertNotIn("gongyiai", combined)
        self.assertEqual(
            1, mihomo["rules"].count("RULE-SET,personal_domain,DIRECT")
        )
        self.assertEqual(1, mihomo["rules"].count("RULE-SET,pt_domain,DIRECT"))
        self.assertLess(
            mihomo["rules"].index("RULE-SET,pt_domain,DIRECT"),
            mihomo["rules"].index("RULE-SET,pt_cn_domain,DIRECT"),
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

    def test_committed_configs_use_ai_policy_group(self):
        configs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }

        for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
            with self.subTest(name=name):
                self.assertEqual(
                    1, len(re.findall(r"(?m)^AI = select,", configs[name]))
                )
                self.assertNotRegex(configs[name], r"(?m)^OpenAI = ")
                self.assertNotRegex(
                    configs[name], r"(?m)^[^#\n]*,OpenAI(?:,|$)"
                )

        qx = configs["quantumultx_allen.conf"]
        self.assertEqual(1, len(re.findall(r"(?m)^static=AI,", qx)))
        self.assertNotRegex(qx, r"(?m)^static=OpenAI,")
        self.assertNotIn("force-policy=OpenAI", qx)
        self.assertIn("/OpenAI/OpenAI.list, tag=AI, force-policy=AI,", qx)

        loon = configs["loon_allen.lcf"]
        self.assertEqual(1, len(re.findall(r"(?m)^AI = select,", loon)))
        self.assertNotRegex(loon, r"(?m)^OpenAI = ")
        self.assertNotIn("policy=OpenAI", loon)
        self.assertIn("policy=AI, tag=AI", loon)

        mihomo = yaml.safe_load(configs["mihomo_allen.yaml"])
        groups = [group["name"] for group in mihomo["proxy-groups"]]
        self.assertEqual(1, groups.count("AI"))
        self.assertNotIn("OpenAI", groups)
        targets = {
            parts[2]
            for rule in mihomo["rules"]
            if isinstance(rule, str)
            and len(parts := [part.strip() for part in rule.split(",")]) >= 3
        }
        self.assertIn("AI", targets)
        self.assertNotIn("OpenAI", targets)

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

    def test_committed_outputs_use_public_titles_and_user_facing_notes(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        titles = {
            "surge_iphone_allen.conf": "# Allen 维护 - Surge iPhone 配置",
            "surge_mac_allen.conf": "# Allen 维护 - Surge Mac 配置",
            "loon_allen.lcf": "# Allen 维护 - Loon 配置",
            "quantumultx_allen.conf": "# Allen 维护 - Quantumult X 配置",
            "mihomo_allen.yaml": "# Allen 维护 - Mihomo 配置",
        }

        for name, title in titles.items():
            with self.subTest(name=name, check="title"):
                self.assertEqual(title, outputs[name].splitlines()[0])
            with self.subTest(name=name, check="internal publishing notes"):
                self.assertNotIn("公开前必须脱敏", outputs[name])
                self.assertNotIn("使用脱敏工具生成", outputs[name])
                self.assertNotIn("Configure MITM certificate", outputs[name])
                self.assertNotIn("Configure local proxy nodes", outputs[name])

        self.assertNotIn(
            "将 policy-path 替换为自己的订阅地址",
            outputs["surge_iphone_allen.conf"],
        )
        self.assertNotIn(
            "将 policy-path 替换为自己的订阅地址",
            outputs["surge_mac_allen.conf"],
        )
        for name in CONFIG_NAMES:
            with self.subTest(name=name, check="subscription placeholder"):
                self.assertIn("获取到的订阅链接", outputs[name])

    def test_committed_policy_sections_have_no_explanatory_comments(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        section_specs = {
            "surge_mac_allen.conf": (
                "[Proxy Group]",
                "[Rule]",
                r"^#\s*[^=#][^=]*\s=\s*select\b",
            ),
            "surge_iphone_allen.conf": (
                "[Proxy Group]",
                "[Rule]",
                r"^#\s*[^=#][^=]*\s=\s*select\b",
            ),
            "quantumultx_allen.conf": ("[policy]", "[server_remote]", None),
            "loon_allen.lcf": ("[Proxy Group]", "[Remote Filter]", None),
        }

        for name, (start, end, allowed_pattern) in section_specs.items():
            lines = outputs[name].splitlines()
            body = lines[lines.index(start) + 1 : lines.index(end)]
            comments = [
                line.strip()
                for line in body
                if line.lstrip().startswith(("#", ";"))
            ]
            with self.subTest(name=name):
                if allowed_pattern is None:
                    self.assertEqual([], comments)
                else:
                    self.assertTrue(
                        all(re.match(allowed_pattern, line) for line in comments)
                    )

        mihomo_groups = outputs["mihomo_allen.yaml"].split(
            "proxy-groups:", maxsplit=1
        )[1].split("\nrules:", maxsplit=1)[0]
        mihomo_comments = [
            line.strip()
            for line in mihomo_groups.splitlines()
            if line.lstrip().startswith("#")
        ]
        self.assertTrue(
            all(re.match(r"^#\s*-\s*\{name:", line) for line in mihomo_comments)
        )

    def test_committed_node_subscriptions_refresh_every_six_hours(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }

        for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
            subscriptions = [
                line
                for line in outputs[name].splitlines()
                if "policy-path=" in line
            ]
            with self.subTest(name=name):
                self.assertEqual(5, len(subscriptions))
                self.assertTrue(
                    all("update-interval=21600" in line for line in subscriptions)
                )

        qx_server_remote = outputs["quantumultx_allen.conf"].split(
            "[server_remote]", maxsplit=1
        )[1].split("[server_local]", maxsplit=1)[0]
        qx_subscriptions = [
            line
            for line in qx_server_remote.splitlines()
            if line.startswith("获取到的订阅链接")
        ]
        self.assertEqual(4, len(qx_subscriptions))
        self.assertTrue(
            all("update-interval=21600" in line for line in qx_subscriptions)
        )

        mihomo = yaml.safe_load(outputs["mihomo_allen.yaml"])
        self.assertEqual(
            {21600},
            {
                provider["interval"]
                for provider in mihomo["proxy-providers"].values()
            },
        )
        self.assertEqual(
            3,
            outputs["mihomo_allen.yaml"].count("#    interval: 21600"),
        )

        loon_remote_proxy = outputs["loon_allen.lcf"].split(
            "[Remote Proxy]", maxsplit=1
        )[1].split("[Proxy Group]", maxsplit=1)[0]
        self.assertNotIn("update-interval=", loon_remote_proxy)
        self.assertIn(
            "请在 App 的节点订阅设置中选择每 6 小时更新",
            loon_remote_proxy,
        )

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
        missing_icons = [
            group.get("name")
            for group in mihomo["proxy-groups"]
            if not isinstance(group.get("icon"), str)
            or not group["icon"].startswith("https://")
        ]
        self.assertEqual([], missing_icons)
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
        self.assertNotIn("维护说明", header)
        self.assertNotIn("脱敏工具", header)
        self.assertNotIn("enabled=true 为启用", header)
        self.assertNotRegex(qx, r"server-tag-regex=[^\n,]*(?:^|\|)(?:新|日|台|United)(?:\||,)")
        self.assertIn("United States", qx)
        self.assertIn("Singapore", qx)

    def test_committed_docker_policy_uses_a_valid_icon_source(self):
        icon_path = ROOT / "assets" / "docker.png"
        self.assertTrue(icon_path.is_file())
        self.assertGreater(icon_path.stat().st_size, 0)
        for name in CONFIG_NAMES:
            text = (OUTPUT_DIR / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn(DOCKER_ICON_URL, text)
                self.assertNotIn(LEGACY_DOCKER_ICON_URL, text)
                self.assertNotIn(BROKEN_DOCKER_ICON_URL, text)

    def test_committed_docker_domains_have_no_local_override(self):
        domains = ("docker.com", "docker.io", "dockerhub.com")
        local_rules = {
            "surge_mac_allen.conf": [
                f"DOMAIN-SUFFIX,{domain},{{policy}}" for domain in domains
            ],
            "surge_iphone_allen.conf": [
                f"DOMAIN-SUFFIX,{domain},{{policy}}" for domain in domains
            ],
            "quantumultx_allen.conf": [
                f"host-suffix, {domain}, {{policy}}" for domain in domains
            ],
            "loon_allen.lcf": [
                f"DOMAIN-SUFFIX,{domain},{{policy}}" for domain in domains
            ],
            "mihomo_allen.yaml": [
                f"- DOMAIN-SUFFIX,{domain},{{policy}}" for domain in domains
            ],
        }
        for name, rules in local_rules.items():
            text = (OUTPUT_DIR / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                for rule_template in rules:
                    self.assertNotIn(rule_template.format(policy="Docker"), text)
                    self.assertNotIn(rule_template.format(policy="美国节点"), text)

    def test_committed_quantumultx_uses_builtin_lowercase_proxy(self):
        qx = (OUTPUT_DIR / "quantumultx_allen.conf").read_text(encoding="utf-8")
        policy = qx.split("[policy]", maxsplit=1)[1].split(
            "[server_remote]", maxsplit=1
        )[0]
        self.assertNotRegex(policy, r"(?m)^static=代理,")
        self.assertNotRegex(policy, r"(?m)^static=Proxy,")
        self.assertNotRegex(policy, r"(?m)^static=proxy,")
        self.assertNotRegex(policy, r"(?:^|,\s*)(?:Proxy|代理)(?:,|$)")
        self.assertRegex(policy, r"(?:^|,\s*)proxy(?:,|$)")
        self.assertNotRegex(qx, r"(?:^|,\s*)force-policy=(?:Proxy|代理)(?:,|$)")
        self.assertRegex(qx, r"(?:^|,\s*)force-policy=proxy(?:,|$)")

    def test_committed_configs_share_optimized_apns_routing(self):
        configs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf")
        }
        apple_push_group = (
            "Apple Push = fallback, 日本节点, 香港节点, 美国节点, DIRECT, "
            "url=http://cp.cloudflare.com/generate_204, interval=300, "
            "icon-url=https://fastly.jsdelivr.net/gh/fmz200/wool_scripts@main/"
            "icons/apps/Apple_Messages.png"
        )
        local_rule = "DOMAIN-SUFFIX,push.apple.com,Apple Push"
        remote_rule = (
            "RULE-SET,https://raw.githubusercontent.com/QuixoticHeart/rule-set/"
            "refs/heads/ruleset/loon/apns.list,Apple Push"
        )

        for name, text in configs.items():
            with self.subTest(name=name):
                self.assertEqual(text.count(apple_push_group), 1)
                self.assertEqual(text.count(local_rule), 1)
                self.assertEqual(text.count(remote_rule), 1)
                self.assertLess(text.index(local_rule), text.index(remote_rule))
                self.assertNotIn("DOMAIN-SUFFIX,push.apple.com,香港节点", text)
                self.assertNotIn("IP-CIDR,17.0.0.0/8,Apple Push", text)

        self.assertNotIn("include-all-networks = true", configs["surge_mac_allen.conf"])
        self.assertNotIn("include-apns = true", configs["surge_mac_allen.conf"])
        self.assertEqual(
            configs["surge_iphone_allen.conf"].count("include-all-networks = true"),
            1,
        )
        self.assertEqual(
            configs["surge_iphone_allen.conf"].count("include-apns = true"),
            1,
        )

        loon = (OUTPUT_DIR / "loon_allen.lcf").read_text(encoding="utf-8")
        self.assertEqual(
            loon.count(
                "Apple Push = fallback,日本节点,香港节点,美国节点,DIRECT,"
            ),
            1,
        )

        qx = (OUTPUT_DIR / "quantumultx_allen.conf").read_text(encoding="utf-8")
        self.assertEqual(
            qx.count(
                "static=Apple Push, 日本节点, 香港节点, 美国节点, direct,"
            ),
            1,
        )
        for group_name in (
            "香港节点",
            "台湾节点",
            "日本节点",
            "新加坡节点",
            "美国节点",
            "韩国节点",
            "英国节点",
        ):
            self.assertRegex(qx, rf"(?m)^static={group_name},")
            self.assertNotRegex(
                qx,
                rf"(?m)^(?:available|url-latency-benchmark)={group_name},",
            )
        for group_name in ("香港优选", "日本优选", "新加坡优选", "美国优选"):
            self.assertRegex(
                qx, rf"(?m)^url-latency-benchmark={group_name},"
            )

    def test_committed_quantumultx_excludes_unsupported_source_ip_rules(self):
        qx = (OUTPUT_DIR / "quantumultx_allen.conf").read_text(encoding="utf-8")
        local_rules = qx.split("[filter_local]", maxsplit=1)[1].split(
            "[rewrite_local]", maxsplit=1
        )[0]
        self.assertNotRegex(local_rules, r"(?im)^\s*src-ip-cidr,")

    def test_committed_outputs_preserve_requested_policy_fixes(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        mihomo = yaml.safe_load(outputs["mihomo_allen.yaml"])

        group_lines = {
            "surge_mac_allen.conf": next(
                line
                for line in outputs["surge_mac_allen.conf"].splitlines()
                if line.startswith("AI = select,")
            ),
            "surge_iphone_allen.conf": next(
                line
                for line in outputs["surge_iphone_allen.conf"].splitlines()
                if line.startswith("AI = select,")
            ),
            "quantumultx_allen.conf": next(
                line
                for line in outputs["quantumultx_allen.conf"].splitlines()
                if line.startswith("static=AI,")
            ),
            "loon_allen.lcf": next(
                line
                for line in outputs["loon_allen.lcf"].splitlines()
                if line.startswith("AI = select,")
            ),
        }
        mihomo_ai = next(
            group
            for group in mihomo["proxy-groups"]
            if group.get("name") == "AI"
        )
        for name, line in group_lines.items():
            with self.subTest(name=name, check="AI region order"):
                self.assertEqual(
                    SUPPORTED_AI_REGION_ORDER,
                    [
                        region
                        for region in SUPPORTED_AI_REGION_ORDER
                        if re.search(rf"(?:^|,\s*){re.escape(region)}(?:,|$)", line)
                    ],
                )
                positions = [line.index(region) for region in SUPPORTED_AI_REGION_ORDER]
                self.assertEqual(positions, sorted(positions))
        self.assertEqual(
            SUPPORTED_AI_REGION_ORDER,
            [
                member
                for member in mihomo_ai["proxies"]
                if member in SUPPORTED_AI_REGION_ORDER
            ],
        )

        self.assertRegex(outputs["surge_mac_allen.conf"], r"(?m)^Proxy = select,")
        self.assertRegex(outputs["surge_iphone_allen.conf"], r"(?m)^Proxy = select,")
        self.assertNotRegex(outputs["quantumultx_allen.conf"], r"(?m)^static=Proxy,")
        self.assertNotRegex(outputs["quantumultx_allen.conf"], r"(?m)^static=proxy,")
        self.assertNotRegex(outputs["quantumultx_allen.conf"], r"(?m)^static=代理,")
        self.assertRegex(
            outputs["quantumultx_allen.conf"],
            r"(?:^|,\s*)proxy(?:,|$)",
        )
        self.assertRegex(outputs["loon_allen.lcf"], r"(?m)^Proxy = select,")
        mihomo_groups = [group["name"] for group in mihomo["proxy-groups"]]
        self.assertIn("Proxy", mihomo_groups)
        self.assertNotIn("代理", mihomo_groups)
        self.assertNotIn("proxy", mihomo_groups)
        self.assertNotIn("ai_custom", mihomo["rule-providers"])
        self.assertFalse(
            any(rule.startswith("RULE-SET,ai_custom,") for rule in mihomo["rules"])
        )

        combined = "\n".join(outputs.values())
        self.assertNotRegex(
            combined,
            r"(?im)^\s*-?\s*(?:DOMAIN-SUFFIX|HOST-SUFFIX)\s*,\s*dmm\.co\.jp\s*,",
        )
        self.assertEqual(
            0,
            len(
                re.findall(
                    r"(?im)^\s*-?\s*(?:DOMAIN-KEYWORD|HOST-KEYWORD)\s*,\s*dmm\s*,",
                    combined,
                )
            ),
        )

        loon_remote = outputs["loon_allen.lcf"].split(
            "[Remote Rule]", maxsplit=1
        )[1].split("[Rule]", maxsplit=1)[0]
        first_service = min(
            loon_remote.index("policy=AI, tag=AI"),
            loon_remote.index("policy=YouTube, tag=YouTube"),
            loon_remote.index("policy=Google, tag=谷歌分流"),
        )
        for marker in (
            "Rules/Loon/AI/direct-ai.list",
            "Rules/Loon/Personal/Domain.list",
            "Rules/Loon/PT/Domain.list",
        ):
            self.assertLess(loon_remote.index(marker), first_service)
        self.assertIn("tag=ProxyLite", loon_remote)
        self.assertIn("tag=GFWList", loon_remote)

    def test_committed_outputs_use_renamed_primary_subscription(self):
        named_outputs = (
            "surge_mac_allen.conf",
            "surge_iphone_allen.conf",
            "quantumultx_allen.conf",
            "loon_allen.lcf",
        )
        for filename in named_outputs:
            text = (OUTPUT_DIR / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn("拼好鸡", text)
                self.assertNotIn("Allen合集订阅", text)

        mihomo_text = (OUTPUT_DIR / "mihomo_allen.yaml").read_text(
            encoding="utf-8"
        )
        mihomo = yaml.safe_load(mihomo_text)
        self.assertEqual(["拼好鸡"], list(mihomo["proxy-providers"]))
        self.assertNotIn("Allen合集订阅", mihomo_text)

    def test_committed_outputs_use_owned_ai_priority_layer(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        broad_values = (
            "githubusercontent.com",
            "cloudflare.com",
            "gstatic.com",
            "googleusercontent.com",
            "googleapis",
        )
        for name, text in outputs.items():
            with self.subTest(name=name, check="GitHub API override"):
                self.assertRegex(
                    text,
                    r"(?im)^\s*-?\s*(?:DOMAIN|host)\s*,\s*api\.github\.com\s*,\s*GitHub",
                )
            for value in broad_values:
                with self.subTest(name=name, value=value):
                    self.assertNotRegex(
                        text,
                        rf"(?im)^\s*-?\s*(?:DOMAIN-SUFFIX|DOMAIN-KEYWORD|"
                        rf"host-suffix|host-keyword)\s*,\s*{re.escape(value)}\s*,",
                    )
                    self.assertRegex(
                        text,
                        rf"(?im)^\s*#\s*-?\s*(?:DOMAIN-SUFFIX|DOMAIN-KEYWORD|"
                        rf"host-suffix|host-keyword)\s*,\s*{re.escape(value)}\s*,",
                    )

        surge_markers = (
            "Rules/Surge/AI/direct-ai.list",
            "Rules/Surge/AI/ai.list",
            "ruleset.skk.moe/List/non_ip/ai.conf",
            "Rabbit-Spec/Surge/Master/Rules/AIGC.list",
        )
        for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
            for marker in surge_markers:
                self.assertIn(marker, outputs[name])
            positions = [outputs[name].index(marker) for marker in surge_markers]
            self.assertEqual(positions, sorted(positions))

        qx = outputs["quantumultx_allen.conf"]
        self.assertIn("Rules/QuantumultX/AI/ai.list", qx)
        owned_qx = next(
            line for line in qx.splitlines() if "Rules/QuantumultX/AI/ai.list" in line
        )
        self.assertIn("force-policy=AI", owned_qx)
        self.assertIn("inserted-resource=true", owned_qx)

        loon = outputs["loon_allen.lcf"]
        self.assertIn("Rules/Loon/AI/ai.list", loon)
        openai_index = loon.find("/rule/Loon/OpenAI/OpenAI.list")
        self.assertNotEqual(-1, openai_index)
        self.assertLess(
            loon.index("Rules/Loon/AI/ai.list"),
            openai_index,
        )
        for marker in (
            "/rule/Loon/OpenAI/OpenAI.list",
            "/rule/Loon/Speedtest/Speedtest.list",
            "/rule/Loon/Steam/Steam.list",
            "/rule/Loon/Game/Game.list",
        ):
            self.assertIn(marker, loon)
        self.assertNotRegex(
            loon,
            r"(?im)^(?![#;]).*kelee\.one/.*enabled=true",
        )
        self.assertNotRegex(
            loon,
            r"(?im)^(?![#;]).*FKTG\.sgmodule.*enabled=true",
        )

        mihomo = yaml.safe_load(outputs["mihomo_allen.yaml"])
        self.assertIn("ai_priority", mihomo["rule-providers"])
        mihomo_markers = (
            "RULE-SET,direct-ai,DIRECT",
            "RULE-SET,personal_domain,DIRECT",
            "RULE-SET,ai_priority,AI",
            "RULE-SET,Cloudflare_domain,CDN",
            "RULE-SET,ai,AI",
        )
        self.assertEqual(
            [mihomo["rules"].index(marker) for marker in mihomo_markers],
            sorted(mihomo["rules"].index(marker) for marker in mihomo_markers),
        )

    def test_committed_loon_excludes_fktg_plugin(self):
        loon = (OUTPUT_DIR / "loon_allen.lcf").read_text(encoding="utf-8")
        plugin = loon.split("\n[Plugin]\n", maxsplit=1)[1].split(
            "\n[Mitm]\n", maxsplit=1
        )[0]
        self.assertNotIn("FKTG.sgmodule", plugin)

    def test_committed_mihomo_uses_builtin_direct(self):
        mihomo = yaml.safe_load(
            (OUTPUT_DIR / "mihomo_allen.yaml").read_text(encoding="utf-8")
        )
        local_proxies = mihomo.get("proxies") or []
        providers = (mihomo.get("proxy-providers") or {}).values()
        groups = mihomo.get("proxy-groups") or []

        self.assertNotIn(
            "直连",
            {
                proxy.get("name")
                for proxy in local_proxies
                if isinstance(proxy, dict)
            },
        )
        self.assertTrue(providers)
        self.assertTrue(
            all(provider.get("proxy") == "DIRECT" for provider in providers)
        )
        self.assertFalse(
            any(
                "直连" in group.get("proxies", [])
                for group in groups
                if isinstance(group, dict)
            )
        )
        self.assertTrue(
            any(
                "DIRECT" in group.get("proxies", [])
                for group in groups
                if isinstance(group, dict)
            )
        )

    def test_committed_mihomo_does_not_use_yaml_merge_keys(self):
        text = (OUTPUT_DIR / "mihomo_allen.yaml").read_text(encoding="utf-8")
        unmerged = yaml.load(text, Loader=yaml.BaseLoader)

        self.assertNotIn("<<:", text)
        self.assertNotRegex(
            text,
            r"(?m)^\s+\S+:\s+\{[^\n]*\bformat:\s+\S+,[^\n]*\bformat:",
        )
        self.assertTrue(
            all("type" in group for group in unmerged["proxy-groups"])
        )
        self.assertTrue(
            all(
                provider.get("type") == "http"
                and provider.get("behavior") in {"domain", "ipcidr", "classical"}
                and provider.get("format") in {"mrs", "text", "yaml"}
                for provider in unmerged["rule-providers"].values()
            )
        )

    def test_mihomo_validator_rejects_legacy_custom_direct(self):
        sanitizer = load_sanitizer()
        text = (OUTPUT_DIR / "mihomo_allen.yaml").read_text(encoding="utf-8")
        legacy = text.replace(
            "\n# 全局配置\n",
            "\nproxies:\n  - {name: 直连, type: direct}\n\n# 全局配置\n",
            1,
        )

        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer._validate_mihomo("mihomo_allen.yaml", legacy)

    def test_mihomo_validator_rejects_yaml_merge_keys(self):
        sanitizer = load_sanitizer()
        text = (OUTPUT_DIR / "mihomo_allen.yaml").read_text(encoding="utf-8")
        legacy = (
            "MergeBase: &MergeBase {enabled: true}\n"
            "Merged: {<<: *MergeBase}\n"
            f"{text}"
        )

        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer._validate_mihomo("mihomo_allen.yaml", legacy)

    def test_committed_non_gateway_configs_exclude_active_source_ip_rules(self):
        configs = {
            "surge_iphone_allen.conf": r"(?im)^\s*#?\s*src-ip,",
            "quantumultx_allen.conf": r"(?im)^\s*#?\s*src-ip-cidr,",
            "loon_allen.lcf": r"(?im)^\s*#?\s*src-ip-cidr,",
        }
        for name, pattern in configs.items():
            text = (OUTPUT_DIR / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertNotRegex(text, pattern)
                self.assertNotIn(
                    "# 1. 局域网与管理规则 (最高优先级)", text
                )

    def test_mihomo_custom_routing_providers_precede_broad_rule_sets(self):
        mihomo = yaml.safe_load(
            (OUTPUT_DIR / "mihomo_allen.yaml").read_text(encoding="utf-8")
        )
        slugs = list(CUSTOM_FEEDS)

        for slug in slugs:
            _, policy = CUSTOM_FEEDS[slug]
            provider_key = f"custom_{slug.replace('-', '_')}"
            with self.subTest(slug=slug, check="provider metadata"):
                self.assertIn(provider_key, mihomo["rule-providers"])
                provider = mihomo["rule-providers"][provider_key]
                self.assertEqual("http", provider["type"])
                self.assertEqual("classical", provider["behavior"])
                self.assertEqual("text", provider["format"])
                self.assertEqual(86400, provider["interval"])
                self.assertEqual(custom_url("Mihomo", slug), provider["url"])

        expected_rules = [
            f"RULE-SET,custom_{slug.replace('-', '_')},{policy}"
            for slug, (_, policy) in CUSTOM_FEEDS.items()
        ]
        rules = mihomo["rules"]
        source_ip_rules = [
            "SRC-IP-CIDR,192.168.50.150/32,DIRECT",
            "SRC-IP-CIDR,192.168.50.151/32,DIRECT",
            "SRC-IP-CIDR,192.168.50.152/32,DIRECT",
        ]
        self.assertEqual(source_ip_rules, rules[:3])
        self.assertEqual(expected_rules, rules[3 : 3 + len(expected_rules)])
        self.assertLess(
            rules.index(expected_rules[-1]),
            rules.index("RULE-SET,steam_cn_domain,DIRECT"),
        )

    def test_surge_custom_routing_urls_and_policies_precede_skk_rules(self):
        for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
            rules = active_lines(
                active_section(
                    (OUTPUT_DIR / name).read_text(encoding="utf-8"),
                    "[Rule]",
                    "[Host]",
                )
            )
            skk_index = next(
                index
                for index, line in enumerate(rules)
                if line.startswith("RULE-SET,https://ruleset.skk.moe/")
            )
            for slug, (_, policy) in CUSTOM_FEEDS.items():
                url = custom_url("Surge", slug)
                matches = [line for line in rules if url in line]
                with self.subTest(name=name, slug=slug):
                    self.assertEqual(1, len(matches))
                    rule_parts = [part.strip() for part in matches[0].split(",")]
                    self.assertEqual(["RULE-SET", url, policy], rule_parts[:3])
                    self.assertLess(rules.index(matches[0]), skk_index)

    def test_quantumultx_and_loon_bind_custom_routing_feeds_before_telecom(self):
        qx = active_lines(
            active_section(
                (OUTPUT_DIR / "quantumultx_allen.conf").read_text(encoding="utf-8"),
                "[filter_remote]",
                "[rewrite_remote]",
            )
        )
        loon = active_lines(
            active_section(
                (OUTPUT_DIR / "loon_allen.lcf").read_text(encoding="utf-8"),
                "[Remote Rule]",
                "[Plugin]",
            )
        )
        qx_telecom_index = next(
            index for index, line in enumerate(qx) if "ChinaTelecom" in line
        )
        loon_telecom_index = next(
            index for index, line in enumerate(loon) if "ChinaTelecom" in line
        )

        for slug, (_, policy) in CUSTOM_FEEDS.items():
            qx_url = custom_url("QuantumultX", slug)
            loon_url = custom_url("Loon", slug)
            qx_policy = "direct" if slug == "direct" else policy
            tag = "自定义-直连" if slug == "direct" else f"自定义-{policy}"
            qx_matches = [line for line in qx if qx_url in line]
            loon_matches = [line for line in loon if loon_url in line]
            with self.subTest(client="Quantumult X", slug=slug):
                self.assertEqual(1, len(qx_matches))
                self.assertEqual(
                    [
                        ("tag", tag),
                        ("force-policy", qx_policy),
                        ("update-interval", "86400"),
                        ("opt-parser", "false"),
                        ("enabled", "true"),
                    ],
                    option_fields(qx_matches[0]),
                )
                self.assertLess(qx.index(qx_matches[0]), qx_telecom_index)
            with self.subTest(client="Loon", slug=slug):
                self.assertEqual(1, len(loon_matches))
                self.assertEqual(
                    [("policy", policy), ("tag", tag), ("enabled", "true")],
                    option_fields(loon_matches[0]),
                )
                self.assertLess(loon.index(loon_matches[0]), loon_telecom_index)

    def test_custom_routing_migrated_rules_are_not_active_locally(self):
        outputs = {
            name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
            for name in CONFIG_NAMES
        }
        active_local_sections = {
            "mihomo_allen.yaml": active_section(outputs["mihomo_allen.yaml"], "rules:"),
            "surge_mac_allen.conf": active_section(
                outputs["surge_mac_allen.conf"], "[Rule]", "[Host]"
            ),
            "surge_iphone_allen.conf": active_section(
                outputs["surge_iphone_allen.conf"], "[Rule]", "[Host]"
            ),
            "quantumultx_allen.conf": active_section(
                outputs["quantumultx_allen.conf"], "[filter_local]", "[rewrite_local]"
            ),
            "loon_allen.lcf": active_section(
                outputs["loon_allen.lcf"], "[Rule]", "[Remote Rule]"
            ),
        }
        local_rule_pattern = re.compile(
            r"^\s*-?\s*(?:DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|"
            r"HOST|HOST-SUFFIX|HOST-KEYWORD)\s*,\s*([^,\s]+)",
            re.IGNORECASE,
        )

        for name, section in active_local_sections.items():
            active_values = {
                match.group(1).casefold()
                for line in active_lines(section)
                if (match := local_rule_pattern.match(line)) is not None
            }
            with self.subTest(name=name, check="migrated rules"):
                self.assertFalse(set(MIGRATED_LOCAL_RULES) & active_values)
                self.assertIn("montbell.com", active_values)
                self.assertNotIn("hdhive.online", active_values)


if __name__ == "__main__":
    unittest.main()
