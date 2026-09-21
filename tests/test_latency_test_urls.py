from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "Configs" / "tool_config"
TARGET = "http://cp.cloudflare.com/generate_204"
FORBIDDEN = (
    "https://www.gstatic.com/generate_204",
    "http://www.qualcomm.cn/generate_204",
    "http://detectportal.firefox.com/success.txt",
)


def section(text: str, name: str) -> str:
    match = re.search(
        rf"(?ms)^\[{re.escape(name)}\]\s*\n(.*?)(?=^\[|\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"missing section: {name}")
    return match.group(1)


class LatencyTestUrlTests(unittest.TestCase):
    def test_all_tool_configs_use_surge_proxy_test_url(self):
        files = (
            "mihomo_allen.yaml",
            "surge_mac_allen.conf",
            "surge_iphone_allen.conf",
            "quantumultx_allen.conf",
            "egern_byallen.yaml",
            "loon_allen.lcf",
        )
        for filename in files:
            text = (CONFIG_DIR / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn(TARGET, text)
                for old_url in FORBIDDEN:
                    self.assertNotIn(old_url, text)

    def test_yaml_client_latency_urls_are_aligned(self):
        mihomo = yaml.safe_load((CONFIG_DIR / "mihomo_allen.yaml").read_text())
        mihomo_urls = {
            provider["health-check"]["url"]
            for provider in mihomo["proxy-providers"].values()
            if provider.get("health-check", {}).get("enable")
        }
        mihomo_urls.update(
            group["url"] for group in mihomo["proxy-groups"] if "url" in group
        )
        self.assertEqual({TARGET}, mihomo_urls)

        egern = yaml.safe_load((CONFIG_DIR / "egern_byallen.yaml").read_text())
        egern_urls = {egern["proxy_latency_test_url"]}
        egern_urls.update(
            body["latency_test_url"]
            for entry in egern["policy_groups"]
            for body in entry.values()
            if "latency_test_url" in body
        )
        self.assertEqual({TARGET}, egern_urls)

    def test_text_client_latency_urls_are_aligned(self):
        surge_mac = (CONFIG_DIR / "surge_mac_allen.conf").read_text()
        surge_ios = (CONFIG_DIR / "surge_iphone_allen.conf").read_text()
        qx = (CONFIG_DIR / "quantumultx_allen.conf").read_text()
        loon = (CONFIG_DIR / "loon_allen.lcf").read_text()

        self.assertIn(f"proxy-test-url = {TARGET}", surge_mac)
        self.assertIn(f"proxy-test-url = {TARGET}", surge_ios)
        self.assertIn(f"server_check_url={TARGET}", qx)
        self.assertIn(f"proxy-test-url = {TARGET}", loon)

        group_urls = {
            match.group(1).strip()
            for line in section(loon, "Proxy Group").splitlines()
            if not line.lstrip().startswith(("#", ";"))
            for match in [re.search(r"(?:^|,)\s*url\s*=\s*([^,]+)", line)]
            if match is not None
        }
        self.assertEqual({TARGET}, group_urls)


if __name__ == "__main__":
    unittest.main()
