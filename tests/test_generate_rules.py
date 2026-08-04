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
CUSTOM_RULES = (
    ("DOMAIN-SUFFIX", "synology.cn", "DIRECT"),
    ("DOMAIN", "qbittorrent-nox", "DIRECT"),
    ("DOMAIN-SUFFIX", "digitalocean.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "dyndns.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "whatismyip.akamai.com", "DIRECT"),
    ("DOMAIN-KEYWORD", "volcengine", "DIRECT"),
    ("DOMAIN-SUFFIX", "xmwsyy.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "ui.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "imgse.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "tagweb.vip", "DIRECT"),
    ("DOMAIN-KEYWORD", "yqc-premium", "DIRECT"),
    ("DOMAIN-SUFFIX", "ad.12306.cn", "DIRECT"),
    ("DOMAIN-SUFFIX", "gg.caixin.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "sdkapp.uve.weibo.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "ucweb.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "amemv.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "v4.plex.tv", "DIRECT"),
    ("DOMAIN-SUFFIX", "openwrt.ai", "美国节点"),
    ("DOMAIN-SUFFIX", "lsposed.org", "美国节点"),
    ("DOMAIN-SUFFIX", "hytron.io", "香港节点"),
    ("DOMAIN-SUFFIX", "linux.do", "美国节点"),
    ("DOMAIN-KEYWORD", "uspatriottactical", "美国节点"),
    ("DOMAIN-KEYWORD", "hdhive", "美国节点"),
    ("DOMAIN-SUFFIX", "rundongex.com", "美国节点"),
    ("DOMAIN-SUFFIX", "servercontrolpanel.de", "美国节点"),
    ("DOMAIN-SUFFIX", "mgboard.net", "美国节点"),
    ("DOMAIN-KEYWORD", "sehuatang", "美国节点"),
    ("DOMAIN-KEYWORD", "greasyfork", "美国节点"),
    ("DOMAIN-KEYWORD", "qichiyu", "美国节点"),
    ("DOMAIN-SUFFIX", "mjji.de", "美国节点"),
    ("DOMAIN-KEYWORD", "hd-torrents", "美国节点"),
    ("DOMAIN-SUFFIX", "embyapp.top", "美国节点"),
    ("DOMAIN-SUFFIX", "vps.town", "美国节点"),
    ("DOMAIN-SUFFIX", "2fa.fun", "美国节点"),
    ("DOMAIN-SUFFIX", "macwk.cn", "美国节点"),
    ("DOMAIN-SUFFIX", "appstorrent.ru", "美国节点"),
    ("DOMAIN-KEYWORD", "kejilion", "香港节点"),
    ("DOMAIN-SUFFIX", "nfbyte.com", "香港节点"),
    ("DOMAIN-KEYWORD", "onitsukatiger", "日本节点"),
    ("DOMAIN-SUFFIX", "compliance.chippercash.com", "美国节点"),
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
    ("DOMAIN-KEYWORD", "missav", "美国节点"),
    ("DOMAIN-KEYWORD", "ftvgirls", "美国节点"),
)
REGIONAL_POLICY_FILES = {
    "香港节点": "hk",
    "香港优选": "hk-auto",
    "美国节点": "us",
    "美国优选": "us-auto",
    "日本节点": "jp",
    "日本优选": "jp-auto",
    "新加坡节点": "sg",
    "新加坡优选": "sg-auto",
}
CUSTOM_SOURCE_LABEL = "Rules/Source/Custom/allenrules.list"
CUSTOM_HEADER = (
    f"# Generated from {CUSTOM_SOURCE_LABEL} by tools/generate_rules.py. Do not edit."
)
QX_CUSTOM_TYPES = {
    "DOMAIN": "host",
    "DOMAIN-SUFFIX": "host-suffix",
    "DOMAIN-KEYWORD": "host-keyword",
}
REGIONAL_CLIENTS = ("Mihomo", "Surge", "QuantumultX", "Loon")
REGIONAL_SLUGS = tuple(REGIONAL_POLICY_FILES.values())


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

        self.assertIn(CUSTOM_SOURCE_LABEL, readme)
        self.assertNotIn("Rules/Source/Regional/allenrules.list", readme)
        expected_row = (
            f"| 自定义直连 | [订阅]({base_url}/Mihomo/Custom/direct.list) | "
            f"[订阅]({base_url}/Surge/Custom/direct.list) | "
            f"[订阅]({base_url}/QuantumultX/Custom/direct.list) | "
            f"[订阅]({base_url}/Loon/Custom/direct.list) |"
        )
        self.assertIn(expected_row, readme)

    def test_regional_subscription_documentation_is_complete(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        base_url = (
            "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules"
        )

        self.assertIn(CUSTOM_SOURCE_LABEL, readme)
        for client in REGIONAL_CLIENTS:
            for slug in REGIONAL_SLUGS:
                with self.subTest(client=client, slug=slug):
                    self.assertIn(
                        f"{base_url}/{client}/Regional/{slug}.list", readme
                    )

    def test_local_configuration_documentation_publishes_remote_rules_only(self):
        config_readme = (ROOT / "Configs" / "tool_config" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("只发布远程规则订阅", config_readme)

    def test_all_generated_outputs_are_current(self):
        generator = load_generator()
        self.assertEqual([], generator.sync_outputs(ROOT, check=True))

    def test_output_map_contains_all_expected_files(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        self.assertEqual(57, len(outputs))
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

    def test_custom_direct_outputs_are_generated_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)
        direct_rules = tuple(rule for rule in CUSTOM_RULES if rule[2] == "DIRECT")

        for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
            with self.subTest(client=client):
                path = ROOT / "Rules" / client / "Custom" / "direct.list"
                self.assertIn(path, outputs)
                content = outputs[path]
                self.assertEqual(CUSTOM_HEADER, content.splitlines()[0])
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
        source = ROOT / "Rules" / "Source" / "Custom" / "allenrules.list"

        self.assertTrue(source.exists())
        self.assertEqual(CUSTOM_RULES, tuple(generator.parse_custom_source(source)))
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
                    self.assertTrue(content.startswith(CUSTOM_HEADER))
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

    def test_regional_preferred_outputs_are_header_only_for_every_client(self):
        generator = load_generator()
        outputs = generator.build_outputs(ROOT)

        for slug in ("hk-auto", "us-auto", "jp-auto", "sg-auto"):
            for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
                with self.subTest(client=client, slug=slug):
                    self.assertEqual(
                        f"{CUSTOM_HEADER}\n",
                        outputs[
                            ROOT / "Rules" / client / "Regional" / f"{slug}.list"
                        ],
                    )

    def test_custom_source_contains_only_confirmed_rules(self):
        generator = load_generator()
        source = ROOT / "Rules" / "Source" / "Custom" / "allenrules.list"

        self.assertTrue(source.exists())
        self.assertEqual(CUSTOM_RULES, tuple(generator.parse_custom_source(source)))
        content = source.read_text(encoding="utf-8")
        self.assertNotIn("SRC-IP-CIDR", content)
        self.assertNotIn("hdhive.online", content)
        self.assertNotIn("montbell.com", content)

    def test_parse_custom_source_accepts_exact_hosts(self):
        generator = load_generator()
        shortest_label = "a"
        longest_label = "a" * 63
        valid_cases = {
            "DOMAIN,example.com,美国节点\n": [
                ("DOMAIN", "example.com", "美国节点")
            ],
            "DOMAIN,qbittorrent-nox,DIRECT\n": [
                ("DOMAIN", "qbittorrent-nox", "DIRECT")
            ],
            f"DOMAIN,{shortest_label},DIRECT\n": [
                ("DOMAIN", shortest_label, "DIRECT")
            ],
            f"DOMAIN,{longest_label},DIRECT\n": [
                ("DOMAIN", longest_label, "DIRECT")
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            for content, expected in valid_cases.items():
                with self.subTest(content=content.strip()):
                    path.write_text(content, encoding="utf-8")
                    self.assertEqual(expected, generator.parse_custom_source(path))

    def test_parse_custom_source_rejects_invalid_rows(self):
        generator = load_generator()
        overlong_label = "a" * 64
        invalid_cases = {
            "DOMAIN,-invalid,DIRECT\n": "invalid exact host",
            "DOMAIN,invalid-,DIRECT\n": "invalid exact host",
            "DOMAIN,UPPERCASE,DIRECT\n": "invalid exact host",
            f"DOMAIN,{overlong_label},DIRECT\n": "invalid exact host",
            "DOMAIN-SUFFIX,example.com,UNKNOWN\n": "unknown policy",
            "IP-CIDR,192.0.2.0/24,美国节点\n": "unsupported rule type",
            "DOMAIN-SUFFIX,example.com,欧洲节点\n": "unknown policy",
            "DOMAIN-SUFFIX,https://example.com/path,美国节点\n": "invalid domain",
            "DOMAIN-SUFFIX,example.com,美国节点\nDOMAIN-SUFFIX,example.com,日本节点\n": "duplicate rule",
            "DOMAIN-KEYWORD,hdhive,美国节点\nDOMAIN-SUFFIX,hdhive.online,香港节点\n": "overlapping keyword and suffix",
            "DOMAIN-SUFFIX,example.com\n": "expected three non-empty fields",
            "DOMAIN-SUFFIX,,美国节点\n": "expected three non-empty fields",
            "DOMAIN-SUFFIX,example.com,\n": "expected three non-empty fields",
            "DOMAIN-SUFFIX,Example.com,美国节点\n": "invalid domain",
            "DOMAIN-KEYWORD,Example,美国节点\n": "invalid keyword",
            "DOMAIN-KEYWORD,example keyword,美国节点\n": "invalid keyword",
            "DOMAIN-SUFFIX,example.com,美国节点\nDOMAIN-SUFFIX,example.com,美国节点\n": "duplicate rule",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            for content, reason in invalid_cases.items():
                with self.subTest(content=content.strip(), reason=reason):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, reason):
                        generator.parse_custom_source(path)

    def test_parse_custom_source_skips_whitespace_only_lines(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            path.write_text(
                "   \t  \nDOMAIN-SUFFIX,example.com,美国节点\n", encoding="utf-8"
            )

            self.assertEqual(
                [("DOMAIN-SUFFIX", "example.com", "美国节点")],
                generator.parse_custom_source(path),
            )

    def test_parse_custom_source_skips_indented_comments(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.list"
            path.write_text(
                "  # policy note\nDOMAIN-SUFFIX,example.com,美国节点\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [("DOMAIN-SUFFIX", "example.com", "美国节点")],
                generator.parse_custom_source(path),
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
                    CUSTOM_HEADER,
                    "",
                    "DOMAIN,qbittorrent-nox",
                    "DOMAIN-SUFFIX,linux.do",
                    "DOMAIN-KEYWORD,hdhive",
                    "",
                ]
            ),
            generator.render_custom_rules(rules, "classical", CUSTOM_SOURCE_LABEL),
        )
        self.assertEqual(
            "\n".join(
                [
                    CUSTOM_HEADER,
                    "",
                    "host, qbittorrent-nox, proxy",
                    "host-suffix, linux.do, proxy",
                    "host-keyword, hdhive, proxy",
                    "",
                ]
            ),
            generator.render_custom_rules(rules, "quantumultx", CUSTOM_SOURCE_LABEL),
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
            custom_dir = root / "Rules" / "Source" / "Custom"
            custom_dir.mkdir(parents=True)
            (custom_dir / "allenrules.list").write_text(
                "DOMAIN-SUFFIX,example.com,美国节点\n", encoding="utf-8"
            )
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
            custom_dir = root / "Rules" / "Source" / "Custom"
            custom_dir.mkdir(parents=True)
            custom_source = custom_dir / "allenrules.list"
            custom_source.write_text(
                "DOMAIN-SUFFIX,example.com,美国节点\n", encoding="utf-8"
            )

            generator.sync_outputs(root, check=False)
            output_paths = tuple(generator.build_outputs(root))
            before = {
                path: path.read_text(encoding="utf-8") for path in output_paths
            }
            custom_source.write_text(
                "DOMAIN-SUFFIX,example.com,美国节点\n"
                "DOMAIN-SUFFIX,example.com,日本节点\n",
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
