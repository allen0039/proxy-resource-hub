#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import ipaddress
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SKK_REPOSITORY = "https://github.com/SukkaW/Surge"
USER_AGENT = "proxy-resource-hub-egern-updater/1.0"
MAX_SOURCE_BYTES = 12 * 1024 * 1024

SOURCE_SPECS = {
    "skk_ai": ("classical", "https://ruleset.skk.moe/List/non_ip/ai.conf", 40, True),
    "skk_reject_domainset": ("domainset", "https://ruleset.skk.moe/List/domainset/reject.conf", 100000, True),
    "skk_reject": ("classical", "https://ruleset.skk.moe/List/non_ip/reject.conf", 300, True),
    "skk_reject_no_drop": ("classical", "https://ruleset.skk.moe/List/non_ip/reject-no-drop.conf", 40, True),
    "skk_reject_drop": ("classical", "https://ruleset.skk.moe/List/non_ip/reject-drop.conf", 20, True),
    "skk_reject_ip": ("classical", "https://ruleset.skk.moe/List/ip/reject.conf", 700, True),
    "skk_lan": ("classical", "https://ruleset.skk.moe/List/non_ip/lan.conf", 40, True),
    "skk_lan_ip": ("classical", "https://ruleset.skk.moe/List/ip/lan.conf", 10, True),
    "skk_domestic": ("classical", "https://ruleset.skk.moe/List/non_ip/domestic.conf", 800, True),
    "skk_domestic_ip": ("classical", "https://ruleset.skk.moe/List/ip/domestic.conf", 2, True),
    "skk_china_ip": ("classical", "https://ruleset.skk.moe/List/ip/china_ip.conf", 3500, "CC-BY-SA-2.0"),
    "skk_apple_cdn": ("domainset", "https://ruleset.skk.moe/List/domainset/apple_cdn.conf", 140, True),
    "skk_apple_cn": ("classical", "https://ruleset.skk.moe/List/non_ip/apple_cn.conf", 8, True),
    "skk_microsoft_cdn": ("classical", "https://ruleset.skk.moe/List/non_ip/microsoft_cdn.conf", 45, True),
    "skk_stream": ("classical", "https://ruleset.skk.moe/List/non_ip/stream.conf", 300, True),
    "skk_cdn_domainset": ("domainset", "https://ruleset.skk.moe/List/domainset/cdn.conf", 4000, True),
    "skk_cdn": ("classical", "https://ruleset.skk.moe/List/non_ip/cdn.conf", 70, True),
    "skk_speedtest": ("domainset", "https://ruleset.skk.moe/List/domainset/speedtest.conf", 3000, True),
    "google": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Google/Google.list", 650, False),
    "sony": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Sony/Sony.list", 100, False),
    "global_media": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/GlobalMedia/GlobalMedia_All_No_Resolve.list", 2200, False),
    "aigc": ("classical", "https://raw.githubusercontent.com/Rabbit-Spec/Surge/Master/Rules/AIGC.list", 100, False),
    "china_telecom": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/ChinaTelecom/ChinaTelecom.list", 70, False),
    "docker": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Docker/Docker.list", 7, False),
    "china_media": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/ChinaMedia/ChinaMedia_Resolve.list", 400, False),
    "threads": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Threads/Threads.list", 1, False),
    "whatsapp": ("classical", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Whatsapp/Whatsapp.list", 15, False),
}

OUTPUT_SPECS = {
    Path("Rules/Egern/SKK/AI.yaml"): ("skk_ai",),
    Path("Rules/Egern/SKK/Reject.yaml"): (
        "skk_reject_domainset", "skk_reject", "skk_reject_no_drop",
        "skk_reject_drop", "skk_reject_ip",
    ),
    Path("Rules/Egern/SKK/LAN.yaml"): ("skk_lan", "skk_lan_ip"),
    Path("Rules/Egern/SKK/Domestic.yaml"): (
        "skk_domestic", "skk_domestic_ip", "skk_china_ip",
    ),
    Path("Rules/Egern/SKK/AppleCN.yaml"): ("skk_apple_cdn", "skk_apple_cn"),
    Path("Rules/Egern/SKK/MicrosoftCDN.yaml"): ("skk_microsoft_cdn",),
    Path("Rules/Egern/SKK/Stream.yaml"): ("skk_stream",),
    Path("Rules/Egern/SKK/CDN.yaml"): ("skk_cdn_domainset", "skk_cdn"),
    Path("Rules/Egern/Google/Google.yaml"): ("google",),
    Path("Rules/Egern/Games/Sony.yaml"): ("sony",),
    Path("Rules/Egern/Media/GlobalMedia.yaml"): ("global_media",),
    Path("Rules/Egern/AI/AIGC.yaml"): ("aigc",),
    Path("Rules/Egern/Media/ChinaMedia.yaml"): ("china_media",),
    Path("Rules/Egern/Services/ChinaTelecom.yaml"): ("china_telecom",),
    Path("Rules/Egern/Services/Docker.yaml"): ("docker",),
    Path("Rules/Egern/Services/Speedtest.yaml"): ("skk_speedtest",),
    Path("Rules/Egern/Social/Threads.yaml"): ("threads",),
    Path("Rules/Egern/Social/WhatsApp.yaml"): ("whatsapp",),
}

TYPE_TO_FIELD = {
    "DOMAIN": "domain_set",
    "DOMAIN-SUFFIX": "domain_suffix_set",
    "DOMAIN-KEYWORD": "domain_keyword_set",
    "DOMAIN-WILDCARD": "domain_wildcard_set",
    "IP-CIDR": "ip_cidr_set",
    "IP-CIDR6": "ip_cidr6_set",
    "IP-ASN": "asn_set",
    "USER-AGENT": "user_agent_set",
    "PROCESS-NAME": "process_name_set",
    "URL-REGEX": "url_regex_set",
}
FIELD_ORDER = tuple(dict.fromkeys(TYPE_TO_FIELD.values()))
DOMAIN_RE = re.compile(
    r"(?=.{1,253}\Z)(?:[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+"
    r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\Z"
)
HOST_LABEL_RE = re.compile(r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\Z")
LAST_UPDATED_RE = re.compile(r"^# Last Updated:\s*(\S+)\s*$", re.MULTILINE)
KNOWN_CONFIG_ONLY_RULES = {
    ("skk_reject_no_drop", "AND,((PROTOCOL,UDP), (DOMAIN-SUFFIX,googlevideo.com))")
}

Rule = tuple[str, str]


def active_lines(text: str) -> list[tuple[int, str]]:
    return [
        (number, line.strip())
        for number, line in enumerate(text.splitlines(), 1)
        if line.strip() and not line.lstrip().startswith(("#", ";", "//"))
    ]


def validate_skk_metadata(text: str, source_name: str, license_id: object) -> str:
    license_marker = (
        "# License: CC BY-SA 2.0"
        if license_id == "CC-BY-SA-2.0"
        else "# License: AGPL 3.0"
    )
    if license_marker not in text:
        raise ValueError(f"{source_name}: expected license marker is missing")
    if f"# GitHub: {SKK_REPOSITORY}" not in text:
        raise ValueError(f"{source_name}: upstream repository marker is missing")
    match = LAST_UPDATED_RE.search(text)
    if match is None:
        raise ValueError(f"{source_name}: Last Updated marker is missing")
    return match.group(1)


def validate_domain(value: str, source_name: str, line_number: int) -> str:
    normalized = value.lstrip(".").casefold()
    if not (DOMAIN_RE.fullmatch(normalized) or HOST_LABEL_RE.fullmatch(normalized)):
        raise ValueError(f"{source_name}:{line_number}: invalid domain: {value}")
    return normalized


def parse_domainset(text: str, source_name: str) -> list[Rule]:
    rules: list[Rule] = []
    for line_number, line in active_lines(text):
        rule_type = "DOMAIN-SUFFIX" if line.startswith(".") else "DOMAIN"
        rules.append((rule_type, validate_domain(line, source_name, line_number)))
    return rules


def normalize_rule_value(
    rule_type: str, value: str, source_name: str, line_number: int
) -> str:
    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
        return validate_domain(value, source_name, line_number)
    if rule_type in {"IP-CIDR", "IP-CIDR6"}:
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError as error:
            raise ValueError(
                f"{source_name}:{line_number}: invalid {rule_type}: {value}"
            ) from error
        expected_version = 4 if rule_type == "IP-CIDR" else 6
        if network.version != expected_version:
            raise ValueError(
                f"{source_name}:{line_number}: address family mismatch: {value}"
            )
        return str(network)
    if rule_type == "IP-ASN":
        normalized = value.upper().removeprefix("AS")
        if not normalized.isdigit() or int(normalized) < 1:
            raise ValueError(f"{source_name}:{line_number}: invalid ASN: {value}")
        return normalized
    if rule_type == "URL-REGEX":
        try:
            re.compile(value)
        except re.error as error:
            raise ValueError(
                f"{source_name}:{line_number}: invalid URL-REGEX: {error}"
            ) from error
    if not value or any(character in "\r\n\0" for character in value):
        raise ValueError(f"{source_name}:{line_number}: invalid rule value")
    return value


def parse_classical(text: str, source_name: str) -> list[Rule]:
    rules: list[Rule] = []
    for line_number, line in active_lines(text):
        if (source_name, line) in KNOWN_CONFIG_ONLY_RULES:
            continue
        try:
            fields = next(csv.reader([line], skipinitialspace=True, strict=True))
        except csv.Error as error:
            raise ValueError(f"{source_name}:{line_number}: malformed CSV") from error
        fields = [field.strip() for field in fields]
        if len(fields) < 2 or not fields[0] or not fields[1]:
            raise ValueError(f"{source_name}:{line_number}: malformed rule: {line}")
        rule_type = fields[0].upper()
        if rule_type not in TYPE_TO_FIELD:
            raise ValueError(
                f"{source_name}:{line_number}: unsupported rule type: {rule_type}"
            )
        options = [option.casefold() for option in fields[2:]]
        if any(option != "no-resolve" for option in options):
            raise ValueError(
                f"{source_name}:{line_number}: unsupported rule option: {fields[2:]}"
            )
        value = normalize_rule_value(rule_type, fields[1], source_name, line_number)
        rules.append((rule_type, value))
    return rules


def deduplicate(rules: list[Rule]) -> list[Rule]:
    seen: set[Rule] = set()
    output: list[Rule] = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            output.append(rule)
    return output


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_egern(rules: list[Rule], source_keys: tuple[str, ...]) -> str:
    source_urls = [SOURCE_SPECS[key][1] for key in source_keys]
    source_licenses = {
        "AGPL-3.0-only" if SOURCE_SPECS[key][3] is True else SOURCE_SPECS[key][3]
        for key in source_keys
        if SOURCE_SPECS[key][3]
    }
    output = ["# Generated by tools/update_egern_rules.py. Do not edit."]
    if source_licenses:
        license_expression = " AND ".join(sorted(source_licenses))
        output.extend(
            (f"# SPDX-License-Identifier: {license_expression}", f"# Derived from {SKK_REPOSITORY}")
        )
    output.extend(f"# Source: {url}" for url in source_urls)
    output.extend((f"# Rule count: {len(rules)}", ""))

    grouped = {field: [] for field in FIELD_ORDER}
    for rule_type, value in rules:
        grouped[TYPE_TO_FIELD[rule_type]].append(value)
    if any(grouped[field] for field in ("ip_cidr_set", "ip_cidr6_set", "asn_set")):
        output.extend(("no_resolve: true", ""))
    for field in FIELD_ORDER:
        values = grouped[field]
        if not values:
            continue
        output.append(f"{field}:")
        output.extend(f"  - {yaml_scalar(value)}" for value in values)
    return "\n".join(output).rstrip() + "\n"


def build_outputs(
    source_texts: dict[str, str], minimum_counts: dict[str, int] | None = None
) -> dict[Path, str]:
    missing = set(SOURCE_SPECS) - set(source_texts)
    if missing:
        raise ValueError(f"missing Egern sources: {', '.join(sorted(missing))}")
    minimums = (
        {key: spec[2] for key, spec in SOURCE_SPECS.items()}
        if minimum_counts is None else minimum_counts
    )
    parsed: dict[str, list[Rule]] = {}
    for key, (kind, _url, _minimum, license_id) in SOURCE_SPECS.items():
        text = source_texts[key]
        if license_id:
            validate_skk_metadata(text, key, license_id)
        rules = parse_domainset(text, key) if kind == "domainset" else parse_classical(text, key)
        minimum = minimums[key]
        if len(active_lines(text)) < minimum:
            raise ValueError(f"{key}: source is below minimum {minimum}")
        if not rules:
            raise ValueError(f"{key}: no convertible rules")
        parsed[key] = rules

    outputs: dict[Path, str] = {}
    for path, source_keys in OUTPUT_SPECS.items():
        merged = deduplicate(
            [rule for source_key in source_keys for rule in parsed[source_key]]
        )
        outputs[path] = render_egern(merged, source_keys)
    return outputs


def fetch_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for key, (_kind, url, _minimum, _license_id) in SOURCE_SPECS.items():
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=45) as response:
            data = response.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError(f"{key}: source exceeds {MAX_SOURCE_BYTES} bytes")
        sources[key] = data.decode("utf-8-sig")
    return sources


def sync_outputs(root: Path, source_texts: dict[str, str], check: bool = False) -> list[Path]:
    outputs = build_outputs(source_texts)
    changed: list[Path] = []
    for relative_path, expected in outputs.items():
        path = root / relative_path
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual == expected:
            continue
        changed.append(path)
        if check:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(expected, encoding="utf-8")
        temporary.replace(path)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert the active Surge sources into native Egern YAML."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        changed = sync_outputs(ROOT, fetch_sources(), check=args.check)
    except (HTTPError, URLError, UnicodeError, OSError, ValueError) as error:
        print(f"Egern update failed: {error}", file=sys.stderr)
        return 1
    for path in changed:
        action = "out of date" if args.check else "updated"
        print(f"{action}: {path.relative_to(ROOT)}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
