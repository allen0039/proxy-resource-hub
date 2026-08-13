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
    "montbell.com",
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
    "deepseek.com",
    "default.exp-tas.com",
    "copilot-proxy.githubusercontent.com",
    "origin-tracker.githubusercontent.com",
    "copilot-telemetry.githubusercontent.com",
    "githubcopilot.com",
    "clawhub.ai",
    "open-meteo.com",
)
CUSTOM_RULES = (
    ("DOMAIN-SUFFIX", "synology.cn", "DIRECT"),
    ("DOMAIN", "qbittorrent-nox", "DIRECT"),
    ("DOMAIN-SUFFIX", "ui.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "digitalocean.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "dyndns.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "whatismyip.akamai.com", "DIRECT"),
    ("DOMAIN-KEYWORD", "volcengine", "DIRECT"),
    ("DOMAIN-SUFFIX", "qq.com", "DIRECT"),
    ("DOMAIN-KEYWORD", "boke", "DIRECT"),
    ("DOMAIN-SUFFIX", "kuwo.cn", "DIRECT"),
    ("DOMAIN-SUFFIX", "xmwsyy.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "imgse.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "tagweb.vip", "DIRECT"),
    ("DOMAIN-KEYWORD", "yqc-premium", "DIRECT"),
    ("DOMAIN-SUFFIX", "ad.12306.cn", "DIRECT"),
    ("DOMAIN-SUFFIX", "gg.caixin.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "sdkapp.uve.weibo.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "ucweb.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "amemv.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "v4.plex.tv", "DIRECT"),
    ("DOMAIN-SUFFIX", "hytron.io", "香港节点"),
    ("DOMAIN-KEYWORD", "kejilion", "香港节点"),
    ("DOMAIN-SUFFIX", "nfbyte.com", "香港节点"),
    ("DOMAIN-SUFFIX", "openwrt.ai", "美国节点"),
    ("DOMAIN-SUFFIX", "lsposed.org", "美国节点"),
    ("DOMAIN-SUFFIX", "linux.do", "美国节点"),
    ("DOMAIN-SUFFIX", "rundongex.com", "美国节点"),
    ("DOMAIN-SUFFIX", "servercontrolpanel.de", "美国节点"),
    ("DOMAIN-SUFFIX", "mgboard.net", "美国节点"),
    ("DOMAIN-KEYWORD", "greasyfork", "美国节点"),
    ("DOMAIN-KEYWORD", "qichiyu", "美国节点"),
    ("DOMAIN-SUFFIX", "mjji.de", "美国节点"),
    ("DOMAIN-SUFFIX", "vps.town", "美国节点"),
    ("DOMAIN-SUFFIX", "2fa.fun", "美国节点"),
    ("DOMAIN-KEYWORD", "themoviedb", "美国节点"),
    ("DOMAIN-KEYWORD", "tmdb", "美国节点"),
    ("DOMAIN-KEYWORD", "dashboardicons", "美国节点"),
    ("DOMAIN-SUFFIX", "ggpht.com", "美国节点"),
    ("DOMAIN-KEYWORD", "uspatriottactical", "美国节点"),
    ("DOMAIN-SUFFIX", "compliance.chippercash.com", "美国节点"),
    ("DOMAIN-KEYWORD", "hdhive", "美国节点"),
    ("DOMAIN-KEYWORD", "sehuatang", "美国节点"),
    ("DOMAIN-KEYWORD", "hd-torrents", "美国节点"),
    ("DOMAIN-SUFFIX", "embyapp.top", "美国节点"),
    ("DOMAIN-SUFFIX", "macwk.cn", "美国节点"),
    ("DOMAIN-SUFFIX", "appstorrent.ru", "美国节点"),
    ("DOMAIN-KEYWORD", "missav", "美国节点"),
    ("DOMAIN-KEYWORD", "ftvgirls", "美国节点"),
    ("DOMAIN-KEYWORD", "onitsukatiger", "日本节点"),
    ("DOMAIN-KEYWORD", "dmm", "日本节点"),
    ("DOMAIN-KEYWORD", "javrate", "日本节点"),
    ("DOMAIN-KEYWORD", "jav321", "日本节点"),
    ("DOMAIN-KEYWORD", "freejavbt", "日本节点"),
    ("DOMAIN-KEYWORD", "javbus", "日本节点"),
    ("DOMAIN-KEYWORD", "mgstage", "日本节点"),
    ("DOMAIN-KEYWORD", "mmtv", "日本节点"),
    ("DOMAIN-KEYWORD", "javdb", "新加坡节点"),
    ("DOMAIN-KEYWORD", "javlibrary", "新加坡节点"),
    ("DOMAIN-KEYWORD", "avbase", "新加坡节点"),
    ("DOMAIN-SUFFIX", "nodeseek.com", "德国节点"),
)
REGIONAL_POLICY_FILES = {
    "香港节点": "hk",
    "美国节点": "us",
    "日本节点": "jp",
    "新加坡节点": "sg",
    "德国节点": "de",
}
ALLENRULE_SOURCE_FILES = {
    "DIRECT": "direct",
    "香港节点": "hk",
    "美国节点": "us",
    "日本节点": "jp",
    "新加坡节点": "sg",
    "德国节点": "de",
}
RETIRED_REGIONAL_SLUGS = ("hk-auto", "us-auto", "jp-auto", "sg-auto")
QX_CUSTOM_TYPES = {
    "DOMAIN": "host",
    "DOMAIN-SUFFIX": "host-suffix",
    "DOMAIN-KEYWORD": "host-keyword",
}
REGIONAL_CLIENTS = ("Mihomo", "Surge", "QuantumultX", "Loon")
REGIONAL_SLUGS = tuple(REGIONAL_POLICY_FILES.values())
UU_REMOTE_SOURCE = "Rules/Source/allenrules/uuyuancheng.list"
UU_REMOTE_RULES = (
    ("PROCESS-NAME", "uuremote"),
    ("PROCESS-NAME", "uuremoteserver"),
    ("PROCESS-NAME", "uuremoteservice"),
    ("PROCESS-NAME", "uuremotedaemon"),
)


def custom_source_label(policy: str) -> str:
    return f"Rules/Source/allenrules/{ALLENRULE_SOURCE_FILES[policy]}.list"


def custom_header(policy: str) -> str:
    return (
        f"# Generated from {custom_source_label(policy)} "
        "by tools/generate_rules.py. Do not edit."
    )


def write_allenrule_sources(
    source_root: Path, rules: tuple[tuple[str, str, str], ...]
) -> None:
    source_root.mkdir(parents=True, exist_ok=True)
    for policy, filename in ALLENRULE_SOURCE_FILES.items():
        content = "".join(
            f"{rule_type},{value}\n"
            for rule_type, value, rule_policy in rules
            if rule_policy == policy
        )
        (source_root / f"{filename}.list").write_text(content, encoding="utf-8")


def write_uuyuancheng_source(source_root: Path) -> None:
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "uuyuancheng.list").write_text(
        "".join(f"{rule_type},{value}\n" for rule_type, value in UU_REMOTE_RULES),
        encoding="utf-8",
    )


def rule_lines(content: str) -> tuple[str, ...]:
    return tuple(
        line
        for line in content.splitlines()
        if line and not line.startswith("#")
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
    def test_custom_direct_subscription_documentation_is_complete(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        base_url = (
            "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules"
        )

        self.assertIn(custom_source_label("DIRECT"), readme)
        self.assertNotIn("Rules/Source/Regional/allenrules.list", readme)
        expected_row = (
            f"| 自定义直连 | [订阅]({base_url}/Mihomo/Custom/direct.list) | "
            f"[订阅]({base_url}/Surge/Custom/direct.list) | "
            f"[订阅]({base_url}/QuantumultX/Custom/direct.list) | "
            f"[订阅]({base_url}/Loon/Custom/direct.list) |"
        )
        self.assertIn(expected_row, readme)

    def test_uu_remote_subscription_documentation_identifies_generated_source(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        base_url = (
            "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules"
        )

        self.assertIn(UU_REMOTE_SOURCE, readme)
        self.assertIn("生成结果，禁止手动编辑", readme)
        self.assertIn(f"{base_url}/Surge/Custom/uuyuancheng.list", readme)
        self.assertIn(f"{base_url}/Loon/Custom/uuyuancheng.list", readme)

    def test_regional_subscription_documentation_is_complete(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        base_url = (
            "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules"
        )

        for policy in REGIONAL_POLICY_FILES:
            self.assertIn(custom_source_label(policy), readme)
        for client in REGIONAL_CLIENTS:
            for slug in REGIONAL_SLUGS:
                with self.subTest(client=client, slug=slug):
                    self.assertIn(
                        f"{base_url}/{client}/Regional/{slug}.list", readme
                    )
            for slug in RETIRED_REGIONAL_SLUGS:
                with self.subTest(client=client, retired_slug=slug):
                    self.assertNotIn(
                        f"{base_url}/{client}/Regional/{slug}.list", readme
                    )

    def test_local_configuration_documentation_describes_embedded_custom_rules(self):
        config_readme = (ROOT / "Configs" / "tool_config" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("五份公开模板默认启用", config_readme)
        self.assertIn("Rules/Source/allenrules/", config_readme)
        self.assertIn("六个源文件", config_readme)
        self.assertNotIn("Rules/Source/Custom/allenrules.list", config_readme)
        self.assertIn("一条 Custom DIRECT 与五条 Regional 规则", config_readme)
        self.assertNotIn("地区优选订阅", config_readme)
        self.assertNotIn("*-auto", config_readme)
        self.assertNotIn(
            "地区路由规则的发布不会修改这五份本地客户端配置", config_readme
        )

    def test_all_generated_outputs_are_current(self):
        generator = load_generator()
        self.assertEqual([], generator.sync_outputs(ROOT, check=True))

    def test_output_map_contains_all_expected_files(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        self.assertEqual(46, len(outputs))
        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            for ruleset in ("ai", "direct-ai"):
                expected = ROOT / "Rules" / client / "AI" / f"{ruleset}.list"
                self.assertIn(expected, outputs)
        for ruleset in ("ai", "direct-ai"):
            retired = ROOT / "Rules" / "AI" / f"{ruleset}.list"
            self.assertNotIn(retired, outputs)
            self.assertFalse(retired.exists())
        compatibility = ROOT / "Rules" / "shop" / "shopping.list"
        self.assertNotIn(compatibility, outputs)
        self.assertFalse(compatibility.exists())

    def test_uu_remote_outputs_are_generated_only_for_surge_and_loon(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        expected_header = (
            f"# Generated from {UU_REMOTE_SOURCE} "
            "by tools/generate_rules.py. Do not edit."
        )

        for client in ("Surge", "Loon"):
            with self.subTest(client=client):
                path = ROOT / "Rules" / client / "Custom" / "uuyuancheng.list"
                self.assertIn(path, outputs)
                self.assertEqual(expected_header, outputs[path].splitlines()[0])
                self.assertEqual(
                    tuple(f"{rule_type},{value}" for rule_type, value in UU_REMOTE_RULES),
                    rule_lines(outputs[path]),
                )
        for client in ("Mihomo", "QuantumultX"):
            with self.subTest(client=client):
                path = ROOT / "Rules" / client / "Custom" / "uuyuancheng.list"
                self.assertNotIn(path, outputs)
                self.assertFalse(path.exists())

    def test_custom_direct_outputs_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        direct_rules = tuple(rule for rule in CUSTOM_RULES if rule[2] == "DIRECT")

        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            with self.subTest(client=client):
                path = ROOT / "Rules" / client / "Custom" / "direct.list"
                self.assertIn(path, outputs)
                content = outputs[path]
                self.assertEqual(custom_header("DIRECT"), content.splitlines()[0])
                self.assertNotIn("SRC-IP-CIDR", content)
                if client == "QuantumultX":
                    expected_lines = tuple(
                        f"{QX_CUSTOM_TYPES[rule_type]}, "
                        f"{value}, proxy"
                        for rule_type, value, _ in direct_rules
                    )
                    self.assertIn("host, qbittorrent-nox, proxy", content)
                    self.assertIn("host-suffix, synology.cn, proxy", content)
                    self.assertIn("host-keyword, volcengine, proxy", content)
                else:
                    expected_lines = tuple(
                        f"{rule_type},{value}"
                        for rule_type, value, _ in direct_rules
                    )
                    self.assertIn("DOMAIN,qbittorrent-nox", content)
                    self.assertIn("DOMAIN-SUFFIX,synology.cn", content)
                    self.assertIn("DOMAIN-KEYWORD,volcengine", content)
                self.assertEqual(expected_lines, rule_lines(content))

    def test_regional_outputs_include_all_clients_and_policies(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            for slug in REGIONAL_POLICY_FILES.values():
                with self.subTest(client=client, slug=slug):
                    self.assertIn(
                        ROOT / "Rules" / client / "Regional" / f"{slug}.list",
                        outputs,
                    )

    def test_regional_outputs_keep_each_policy_bucket_in_source_order(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        for policy, slug in REGIONAL_POLICY_FILES.items():
            rules = [rule for rule in CUSTOM_RULES if rule[2] == policy]
            for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
                with self.subTest(policy=policy, client=client):
                    content = outputs[
                        ROOT / "Rules" / client / "Regional" / f"{slug}.list"
                    ]
                    self.assertTrue(content.startswith(custom_header(policy)))
                    if client == "QuantumultX":
                        expected_lines = tuple(
                            f"{QX_CUSTOM_TYPES[rule_type]}, "
                            f"{value}, proxy"
                            for rule_type, value, _ in rules
                        )
                    else:
                        expected_lines = tuple(
                            f"{rule_type},{value}"
                            for rule_type, value, _ in rules
                        )
                    self.assertEqual(expected_lines, rule_lines(content))

    def test_retired_regional_preferred_outputs_are_not_published(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        for slug in RETIRED_REGIONAL_SLUGS:
            for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
                with self.subTest(client=client, slug=slug):
                    path = ROOT / "Rules" / client / "Regional" / f"{slug}.list"
                    self.assertNotIn(path, outputs)
                    self.assertFalse(path.exists())

    def test_split_sources_use_filename_owned_policies(self):
        generator = load_generator()
        source_root = ROOT / "Rules" / "Source" / "allenrules"
        old_source = ROOT / "Rules" / "Source" / "Custom" / "allenrules.list"

        self.assertFalse(old_source.exists())
        for policy, filename in ALLENRULE_SOURCE_FILES.items():
            with self.subTest(policy=policy):
                source = source_root / f"{filename}.list"
                self.assertTrue(source.exists())
                expected = tuple(
                    rule for rule in CUSTOM_RULES if rule[2] == policy
                )
                self.assertEqual(
                    expected, tuple(generator.parse_custom_source(source, policy))
                )
                content = source.read_text(encoding="utf-8")
                self.assertNotIn("SRC-IP-CIDR", content)
                self.assertNotIn("hdhive.online", content)
                self.assertNotIn("montbell.com", content)

    def test_parse_custom_source_accepts_exact_hosts(self):
        generator = load_generator()
        shortest_label = "a"
        longest_label = "a" * 63
        valid_cases = {
            "DOMAIN,example.com\n": [
                ("DOMAIN", "example.com", "美国节点")
            ],
            "DOMAIN,qbittorrent-nox\n": [
                ("DOMAIN", "qbittorrent-nox", "美国节点")
            ],
            f"DOMAIN,{shortest_label}\n": [
                ("DOMAIN", shortest_label, "美国节点")
            ],
            f"DOMAIN,{longest_label}\n": [
                ("DOMAIN", longest_label, "美国节点")
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            for content, expected in valid_cases.items():
                with self.subTest(content=content.strip()):
                    path.write_text(content, encoding="utf-8")
                    self.assertEqual(
                        expected, generator.parse_custom_source(path, "美国节点")
                    )

    def test_parse_process_source_accepts_comments_and_process_names(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "uuyuancheng.list"
            path.write_text(
                "  # Mac background processes\n\nPROCESS-NAME,uuremote\n"
                "PROCESS-NAME,uuremotedaemon\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [
                    ("PROCESS-NAME", "uuremote"),
                    ("PROCESS-NAME", "uuremotedaemon"),
                ],
                generator.parse_process_source(path),
            )

    def test_parse_process_source_rejects_invalid_rows(self):
        generator = load_generator()
        invalid_cases = {
            "PROCESS-NAME,uu remote\n": "invalid process name",
            "DOMAIN,uuremote\n": "unsupported rule type",
            "PROCESS-NAME,uuremote,extra\n": "expected two non-empty fields",
            "PROCESS-NAME,\n": "expected two non-empty fields",
            "PROCESS-NAME,uuremote\nPROCESS-NAME,uuremote\n": "duplicate process name",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "uuyuancheng.list"
            for content, reason in invalid_cases.items():
                with self.subTest(content=content.strip(), reason=reason):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, reason):
                        generator.parse_process_source(path)

    def test_parse_custom_source_rejects_invalid_rows(self):
        generator = load_generator()
        overlong_label = "a" * 64
        invalid_cases = {
            "DOMAIN,-invalid\n": "invalid exact host",
            "DOMAIN,invalid-\n": "invalid exact host",
            "DOMAIN,UPPERCASE\n": "invalid exact host",
            f"DOMAIN,{overlong_label}\n": "invalid exact host",
            "IP-CIDR,192.0.2.0/24\n": "unsupported rule type",
            "DOMAIN-SUFFIX,https://example.com/path\n": "invalid domain",
            "DOMAIN-KEYWORD,hdhive\nDOMAIN-SUFFIX,hdhive.online\n": "overlapping keyword and suffix",
            "DOMAIN-SUFFIX,example.com,美国节点\n": "expected two non-empty fields",
            "DOMAIN-SUFFIX,\n": "expected two non-empty fields",
            "DOMAIN-SUFFIX,,美国节点\n": "expected two non-empty fields",
            "DOMAIN-SUFFIX,Example.com\n": "invalid domain",
            "DOMAIN-KEYWORD,Example\n": "invalid keyword",
            "DOMAIN-KEYWORD,example keyword\n": "invalid keyword",
            "DOMAIN-SUFFIX,example.com\nDOMAIN-SUFFIX,example.com\n": "duplicate rule",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            for content, reason in invalid_cases.items():
                with self.subTest(content=content.strip(), reason=reason):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, reason):
                        generator.parse_custom_source(path, "美国节点")

    def test_parse_custom_sources_rejects_cross_policy_duplicates(self):
        generator = load_generator()
        cases = (
            (
                "duplicate rule",
                (
                    ("DOMAIN-SUFFIX", "example.com", "DIRECT"),
                    ("DOMAIN-SUFFIX", "example.com", "香港节点"),
                ),
            ),
            (
                "overlapping keyword and suffix",
                (
                    ("DOMAIN-KEYWORD", "hdhive", "DIRECT"),
                    ("DOMAIN-SUFFIX", "hdhive.online", "香港节点"),
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp) / "Rules" / "Source" / "allenrules"
            for reason, rules in cases:
                with self.subTest(reason=reason):
                    write_allenrule_sources(source_root, rules)
                    with self.assertRaisesRegex(ValueError, reason):
                        generator.parse_custom_sources(source_root)

    def test_parse_custom_source_skips_whitespace_only_lines(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            path.write_text(
                "   \t  \nDOMAIN-SUFFIX,example.com\n", encoding="utf-8"
            )

            self.assertEqual(
                [("DOMAIN-SUFFIX", "example.com", "美国节点")],
                generator.parse_custom_source(path, "美国节点"),
            )

    def test_parse_custom_source_skips_indented_comments(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            path.write_text(
                "  # policy note\nDOMAIN-SUFFIX,example.com\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [("DOMAIN-SUFFIX", "example.com", "美国节点")],
                generator.parse_custom_source(path, "美国节点"),
            )

    def test_render_custom_rules_uses_platform_specific_rule_types(self):
        generator = load_generator()
        rules = [
            ("DOMAIN", "qbittorrent-nox", "DIRECT"),
            ("DOMAIN-SUFFIX", "linux.do", "美国节点"),
            ("DOMAIN-KEYWORD", "hdhive", "美国节点"),
        ]

        self.assertEqual(
            "\n".join(
                [
                    custom_header("DIRECT"),
                    "",
                    "DOMAIN,qbittorrent-nox",
                    "DOMAIN-SUFFIX,linux.do",
                    "DOMAIN-KEYWORD,hdhive",
                    "",
                ]
            ),
            generator.render_custom_rules(
                rules, "classical", custom_source_label("DIRECT")
            ),
        )
        self.assertEqual(
            "\n".join(
                [
                    custom_header("DIRECT"),
                    "",
                    "host, qbittorrent-nox, proxy",
                    "host-suffix, linux.do, proxy",
                    "host-keyword, hdhive, proxy",
                    "",
                ]
            ),
            generator.render_custom_rules(
                rules, "quantumultx", custom_source_label("DIRECT")
            ),
        )

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
            custom_source_root = root / "Rules" / "Source" / "allenrules"
            write_allenrule_sources(
                custom_source_root,
                (("DOMAIN-SUFFIX", "example.com", "美国节点"),),
            )
            write_uuyuancheng_source(custom_source_root)
            generator.sync_outputs(root, check=False)
            stale_path = root / "Rules" / "Mihomo" / "AI" / "ai.list"
            stale_path.write_text("stale\n", encoding="utf-8")

            self.assertIn(stale_path, generator.sync_outputs(root, check=True))

    def test_invalid_custom_source_does_not_partially_write_outputs(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_specs = (
                ("AI", ("ai", "direct-ai")),
                ("Personal", ("Domain",)),
                ("PT", ("Domain",)),
                ("shop", ("shopping",)),
            )
            for directory, names in source_specs:
                source_dir = root / "Rules" / "Source" / directory
                source_dir.mkdir(parents=True)
                for name in names:
                    (source_dir / f"{name}.txt").write_text(
                        "example.com\n", encoding="utf-8"
                    )
            custom_source_root = root / "Rules" / "Source" / "allenrules"
            write_allenrule_sources(
                custom_source_root,
                (("DOMAIN-SUFFIX", "example.com", "美国节点"),),
            )
            write_uuyuancheng_source(custom_source_root)

            generator.sync_outputs(root, check=False)
            output_paths = tuple(generator.build_outputs(root))
            before = {
                path: path.read_text(encoding="utf-8") for path in output_paths
            }
            (custom_source_root / "us.list").write_text(
                "DOMAIN-SUFFIX,example.com\n"
                "DOMAIN-SUFFIX,example.com\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate rule"):
                generator.sync_outputs(root, check=False)

            after = {
                path: path.read_text(encoding="utf-8") for path in output_paths
            }
            self.assertEqual(before, after)

    def test_generated_rule_lines_have_platform_specific_fields(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        for path, content in outputs.items():
            rule_lines = [line for line in content.splitlines() if line and not line.startswith("#")]
            if "Regional" in path.parts or "Custom" in path.parts:
                continue
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
