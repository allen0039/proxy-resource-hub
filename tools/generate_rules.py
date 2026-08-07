#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULESET_SPECS = (
    ("AI", "ai", None),
    ("AI", "direct-ai", None),
    ("Personal", "Domain", None),
    ("PT", "Domain", None),
    ("shop", "shopping", None),
)
CLASSICAL_TARGETS = ("Mihomo", "Surge", "Loon")
DOMAIN_RE = re.compile(
    r"(?=.{1,253}\Z)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z"
)
CUSTOM_SOURCE_SPECS = (
    ("direct", "DIRECT", "Custom", "direct"),
    ("hk", "香港节点", "Regional", "hk"),
    ("us", "美国节点", "Regional", "us"),
    ("jp", "日本节点", "Regional", "jp"),
    ("sg", "新加坡节点", "Regional", "sg"),
)
CUSTOM_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}
HOST_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
KEYWORD_RE = re.compile(r"[a-z0-9][a-z0-9.-]*\Z")


def parse_source(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    for number, line in enumerate(lines, 1):
        if not line or line.startswith("#"):
            continue
        if not DOMAIN_RE.fullmatch(line):
            raise ValueError(f"{path}:{number}: invalid domain: {line}")
        if line in seen:
            raise ValueError(f"{path}:{number}: duplicate domain: {line}")
        seen.add(line)
    return lines


def validate_custom_rule_conflicts(
    rules: list[tuple[str, str, str]], location: Path
) -> None:
    seen: set[tuple[str, str]] = set()
    for rule_type, value, _ in rules:
        key = (rule_type, value)
        if key in seen:
            raise ValueError(f"{location}: duplicate rule: {rule_type},{value}")
        seen.add(key)

    keywords = [value for rule_type, value, _ in rules if rule_type == "DOMAIN-KEYWORD"]
    suffixes = [value for rule_type, value, _ in rules if rule_type == "DOMAIN-SUFFIX"]
    for keyword in keywords:
        for suffix in suffixes:
            if keyword in suffix:
                raise ValueError(
                    f"{location}: overlapping keyword and suffix: {keyword}, {suffix}"
                )


def parse_custom_source(path: Path, policy: str) -> list[tuple[str, str, str]]:
    rules: list[tuple[str, str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 2 or not all(fields):
            raise ValueError(f"{path}:{number}: expected two non-empty fields")
        rule_type, value = fields
        if rule_type not in CUSTOM_TYPES:
            raise ValueError(f"{path}:{number}: unsupported rule type: {rule_type}")
        if rule_type == "DOMAIN" and not (
            DOMAIN_RE.fullmatch(value) or HOST_LABEL_RE.fullmatch(value)
        ):
            raise ValueError(f"{path}:{number}: invalid exact host: {value}")
        if rule_type == "DOMAIN-SUFFIX" and not DOMAIN_RE.fullmatch(value):
            raise ValueError(f"{path}:{number}: invalid domain: {value}")
        if rule_type == "DOMAIN-KEYWORD" and not KEYWORD_RE.fullmatch(value):
            raise ValueError(f"{path}:{number}: invalid keyword: {value}")
        rules.append((rule_type, value, policy))

    validate_custom_rule_conflicts(rules, path)
    return rules


def parse_custom_sources(
    source_root: Path,
) -> dict[str, tuple[Path, list[tuple[str, str, str]]]]:
    parsed: dict[str, tuple[Path, list[tuple[str, str, str]]]] = {}
    all_rules: list[tuple[str, str, str]] = []
    for slug, policy, _, _ in CUSTOM_SOURCE_SPECS:
        source = source_root / f"{slug}.list"
        rules = parse_custom_source(source, policy)
        parsed[policy] = (source, rules)
        all_rules.extend(rules)
    validate_custom_rule_conflicts(all_rules, source_root)
    return parsed


def render(lines: list[str], style: str, source_label: str) -> str:
    output = [
        f"# Generated from {source_label} by tools/generate_rules.py. Do not edit.",
        "",
    ]
    for line in lines:
        if not line or line.startswith("#"):
            output.append(line)
        elif style == "classical":
            output.append(f"DOMAIN-SUFFIX,{line}")
        elif style == "quantumultx":
            output.append(f"host-suffix, {line}, proxy")
        else:
            raise ValueError(f"unknown output style: {style}")
    return "\n".join(output).rstrip() + "\n"


def render_custom_rules(
    rules: list[tuple[str, str, str]], style: str, source_label: str
) -> str:
    output = [
        f"# Generated from {source_label} by tools/generate_rules.py. Do not edit.",
        "",
    ]
    for rule_type, value, _ in rules:
        if style == "classical":
            output.append(f"{rule_type},{value}")
        elif style == "quantumultx":
            qx_type = {
                "DOMAIN": "host",
                "DOMAIN-SUFFIX": "host-suffix",
                "DOMAIN-KEYWORD": "host-keyword",
            }[rule_type]
            output.append(f"{qx_type}, {value}, proxy")
        else:
            raise ValueError(f"unknown output style: {style}")
    return "\n".join(output).rstrip() + "\n"


def build_outputs(root: Path) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for directory, name, compatibility_directory in RULESET_SPECS:
        source = root / "Rules" / "Source" / directory / f"{name}.txt"
        source_label = source.relative_to(root).as_posix()
        lines = parse_source(source)
        classical = render(lines, "classical", source_label)
        for client in CLASSICAL_TARGETS:
            outputs[root / "Rules" / client / directory / f"{name}.list"] = classical
        outputs[
            root / "Rules" / "QuantumultX" / directory / f"{name}.list"
        ] = render(lines, "quantumultx", source_label)
        if compatibility_directory:
            outputs[
                root / "Rules" / compatibility_directory / f"{name}.list"
            ] = classical

    source_root = root / "Rules" / "Source" / "allenrules"
    custom_sources = parse_custom_sources(source_root)
    client_styles = {
        "Mihomo": "classical",
        "Surge": "classical",
        "QuantumultX": "quantumultx",
        "Loon": "classical",
    }
    for client, style in client_styles.items():
        for _, policy, directory, slug in CUSTOM_SOURCE_SPECS:
            source, rules = custom_sources[policy]
            outputs[root / "Rules" / client / directory / f"{slug}.list"] = (
                render_custom_rules(rules, style, source.relative_to(root).as_posix())
            )
    return outputs


def sync_outputs(root: Path, check: bool) -> list[Path]:
    stale: list[Path] = []
    for path, expected in build_outputs(root).items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual == expected:
            continue
        stale.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    return stale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        stale = sync_outputs(ROOT, args.check)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if args.check and stale:
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if not args.check:
        for path in stale:
            print(f"updated: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
