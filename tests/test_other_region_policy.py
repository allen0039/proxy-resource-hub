from pathlib import Path
import re
import unittest

import yaml


CONFIGS = Path(__file__).resolve().parents[1] / "Configs/tool_config"
SURGE = ("surge_mac_allen.conf", "surge_iphone_allen.conf")
MERGED_NODES = (
    "🇬🇧 London 01", "英国 01", "倫敦 01", "UK_01", "GBR02",
    "United Kingdom 01", "🇰🇷 Seoul 01", "韩国 01", "韓國 01",
    "首爾 01", "KR_01", "KOR02", "Korea 01", "Canada 01",
)
EXCLUDED_NODES = (
    "香港 01", "HK_01", "台湾 01", "日本 01", "SG_01", "US_01",
    "德国 01", "DE_01", "家宽 韩国 01", "英国 回国 01", "韩国 游戏 01",
    "剩余流量 20G", "套餐到期 2026-12-31", "官网客服", "官方交流群",
)


def ini_line(text, prefix):
    return next(line for line in text.splitlines() if line.startswith(prefix))


def egern_groups(text):
    return {
        body["name"]: body
        for entry in yaml.safe_load(text)["policy_groups"]
        for body in entry.values()
    }


class OtherRegionPolicyTest(unittest.TestCase):
    def test_merged_regions_match_and_existing_exclusions_remain(self):
        patterns = {}
        for name in SURGE:
            text = (CONFIGS / name).read_text(encoding="utf-8")
            line = ini_line(text, "其他地区 = select,")
            patterns[name] = (line.split("policy-regex-filter=", 1)[1].split(", no-alert=", 1)[0], False)
        text = (CONFIGS / "quantumultx_allen.conf").read_text(encoding="utf-8")
        line = ini_line(text, "static=其他地区,")
        patterns["quantumultx_allen.conf"] = (line.split("server-tag-regex=", 1)[1].split(", img-url=", 1)[0], False)
        text = (CONFIGS / "loon_allen.lcf").read_text(encoding="utf-8")
        line = ini_line(text, "其他 = NameRegex,")
        patterns["loon_allen.lcf"] = (line.split('FilterKey = "', 1)[1].rsplit('"', 1)[0], False)
        text = (CONFIGS / "mihomo_allen.yaml").read_text(encoding="utf-8")
        groups = {g["name"]: g for g in yaml.safe_load(text)["proxy-groups"]}
        patterns["mihomo_allen.yaml"] = (groups["其他地区"]["exclude-filter"], True)
        text = (CONFIGS / "egern_byallen.yaml").read_text(encoding="utf-8")
        patterns["egern_byallen.yaml"] = (egern_groups(text)["其他"]["filter"], False)

        for name, (expression, exclusion) in patterns.items():
            pattern = re.compile(expression)
            for node in MERGED_NODES + EXCLUDED_NODES:
                with self.subTest(config=name, node=node):
                    accepted = bool(pattern.search(node)) != exclusion
                    self.assertEqual(node in MERGED_NODES, accepted)

    def test_other_region_has_no_helper_group_or_permanent_direct_member(self):
        for name in SURGE:
            text = (CONFIGS / name).read_text(encoding="utf-8")
            other = ini_line(text, "其他地区 = select,")
            with self.subTest(config=name):
                # Surge supplies its native DIRECT substitute when the group is empty.
                self.assertIn('include-other-group="拼好鸡"', other)
                self.assertNotIn("其他地区兜底", text)
                self.assertNotRegex(other, r",\s*DIRECT\s*(?:,|$)")

        text = (CONFIGS / "quantumultx_allen.conf").read_text(encoding="utf-8")
        self.assertTrue(ini_line(text, "static=其他地区,").startswith("static=其他地区, server-tag-regex="))
        text = (CONFIGS / "loon_allen.lcf").read_text(encoding="utf-8")
        self.assertTrue(ini_line(text, "其他地区 = select,").startswith("其他地区 = select,其他,url ="))

        text = (CONFIGS / "egern_byallen.yaml").read_text(encoding="utf-8")
        groups = egern_groups(text)
        self.assertEqual(["其他"], groups["其他地区"]["policies"])
        self.assertTrue(groups["其他地区"]["flatten"])
        self.assertNotIn("DIRECT", groups["其他"]["policies"])
        self.assertTrue(groups["其他"]["flatten"])

    def test_mihomo_uses_native_direct_fallback_without_a_permanent_member(self):
        text = (CONFIGS / "mihomo_allen.yaml").read_text(encoding="utf-8")
        group = next(g for g in yaml.safe_load(text)["proxy-groups"] if g["name"] == "其他地区")
        self.assertEqual("DIRECT", group["empty-fallback"])
        self.assertTrue(group["include-all"])
        self.assertNotIn("DIRECT", group.get("proxies", []))

    def test_removed_groups_and_filters_have_no_remaining_references(self):
        for path in CONFIGS.iterdir():
            if path.suffix not in (".conf", ".lcf", ".yaml"):
                continue
            text = path.read_text(encoding="utf-8")
            with self.subTest(config=path.name):
                self.assertNotIn("韩国节点", text)
                self.assertNotIn("英国节点", text)
                self.assertNotRegex(text, r"(?m)^(?:韩国|英国) = NameRegex,")
                if path.name == "egern_byallen.yaml":
                    groups = egern_groups(text)
                    self.assertNotIn("韩国", groups)
                    self.assertNotIn("英国", groups)
                    for menu in ("Apple", "国内媒体"):
                        self.assertIn("其他地区", groups[menu]["policies"])
                elif path.name == "mihomo_allen.yaml":
                    groups = {g["name"]: g for g in yaml.safe_load(text)["proxy-groups"]}
                    for menu in ("Apple", "国内媒体"):
                        self.assertIn("其他地区", groups[menu]["proxies"])
                else:
                    for menu in ("Apple", "国内媒体"):
                        prefix = f"static={menu}," if path.name == "quantumultx_allen.conf" else f"{menu} = select,"
                        self.assertIn("其他地区", ini_line(text, prefix))


if __name__ == "__main__":
    unittest.main()
