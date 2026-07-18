#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REPOSITORY = "https://github.com/SukkaW/Surge"
USER_AGENT = "proxy-resource-hub-skk-updater/1.0"
MAX_SOURCE_BYTES = 8 * 1024 * 1024

SOURCE_SPECS = {
    "cdn_domainset": {
        "ruleset": "CDN",
        "kind": "domainset",
        "url": "https://ruleset.skk.moe/List/domainset/cdn.conf",
        "minimum": 4000,
    },
    "cdn_non_ip": {
        "ruleset": "CDN",
        "kind": "non_ip",
        "url": "https://ruleset.skk.moe/List/non_ip/cdn.conf",
        "minimum": 50,
    },
    "download_domainset": {
        "ruleset": "Download",
        "kind": "domainset",
        "url": "https://ruleset.skk.moe/List/domainset/download.conf",
        "minimum": 1500,
    },
    "download_non_ip": {
        "ruleset": "Download",
        "kind": "non_ip",
        "url": "https://ruleset.skk.moe/List/non_ip/download.conf",
        "minimum": 5,
    },
}

MINIMUM_COUNTS = {
    key: int(spec["minimum"]) for key, spec in SOURCE_SPECS.items()
}
OUTPUT_SPECS = {
    Path("Rules/QuantumultX/SKK/CDN.list"): ("quantumultx", "CDN"),
    Path("Rules/QuantumultX/SKK/Download.list"): (
        "quantumultx",
        "Download",
    ),
    Path("Rules/Loon/SKK/CDN.list"): ("loon", "CDN"),
    Path("Rules/Loon/SKK/Download.list"): ("loon", "Download"),
}

DOMAIN_RE = re.compile(
    r"(?=.{1,253}\Z)(?:[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+"
    r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\Z"
)
LAST_UPDATED_RE = re.compile(r"^# Last Updated:\s*(\S+)\s*$", re.MULTILINE)
SUPPORTED_NON_IP_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "DOMAIN-WILDCARD",
    "URL-REGEX",
}
QX_TYPE_MAP = {
    "DOMAIN": "host",
    "DOMAIN-SUFFIX": "host-suffix",
    "DOMAIN-KEYWORD": "host-keyword",
    "DOMAIN-WILDCARD": "host-wildcard",
    "URL-REGEX": "url-regex",
}

Rule = tuple[str, str]


def _active_source_lines(text: str) -> list[tuple[int, str]]:
    return [
        (number, line.strip())
        for number, line in enumerate(text.splitlines(), 1)
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _validate_source_metadata(text: str, source_name: str) -> str:
    if "# License: AGPL 3.0" not in text:
        raise ValueError(f"{source_name}: AGPL license marker is missing")
    if f"# GitHub: {UPSTREAM_REPOSITORY}" not in text:
        raise ValueError(f"{source_name}: upstream repository marker is missing")
    updated = LAST_UPDATED_RE.search(text)
    if updated is None:
        raise ValueError(f"{source_name}: Last Updated marker is missing")
    return updated.group(1)


def _validate_domain(value: str, source_name: str, line_number: int) -> None:
    if not DOMAIN_RE.fullmatch(value):
        raise ValueError(
            f"{source_name}:{line_number}: invalid domain value: {value}"
        )


def parse_domainset(text: str, source_name: str) -> list[Rule]:
    rules: list[Rule] = []
    for line_number, line in _active_source_lines(text):
        if line.startswith("."):
            rule_type = "DOMAIN-SUFFIX"
            value = line[1:]
        else:
            rule_type = "DOMAIN"
            value = line
        _validate_domain(value, source_name, line_number)
        rules.append((rule_type, value))
    return rules


def parse_non_ip(text: str, source_name: str) -> list[Rule]:
    rules: list[Rule] = []
    for line_number, line in _active_source_lines(text):
        if "," not in line:
            raise ValueError(f"{source_name}:{line_number}: malformed rule: {line}")
        rule_type, value = (part.strip() for part in line.split(",", 1))
        rule_type = rule_type.upper()
        if rule_type not in SUPPORTED_NON_IP_TYPES:
            raise ValueError(
                f"{source_name}:{line_number}: unsupported rule type: {rule_type}"
            )
        if not value:
            raise ValueError(f"{source_name}:{line_number}: empty rule value")
        if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
            _validate_domain(value.lstrip("."), source_name, line_number)
            value = value.lstrip(".")
        elif rule_type in {"DOMAIN-KEYWORD", "DOMAIN-WILDCARD"}:
            if any(character.isspace() for character in value):
                raise ValueError(
                    f"{source_name}:{line_number}: whitespace in {rule_type}"
                )
        elif rule_type == "URL-REGEX":
            try:
                re.compile(value)
            except re.error as error:
                raise ValueError(
                    f"{source_name}:{line_number}: invalid URL-REGEX: {error}"
                ) from error
        rules.append((rule_type, value))
    return rules


def _deduplicate(rules: list[Rule]) -> list[Rule]:
    seen: set[Rule] = set()
    output: list[Rule] = []
    for rule in rules:
        if rule in seen:
            continue
        seen.add(rule)
        output.append(rule)
    return output


def _render(
    rules: list[Rule],
    client: str,
    ruleset: str,
    source_keys: tuple[str, str],
    last_updated: dict[str, str],
) -> str:
    source_urls = [str(SOURCE_SPECS[key]["url"]) for key in source_keys]
    output = [
        "# Generated by tools/update_skk_rules.py. Do not edit.",
        "# SPDX-License-Identifier: AGPL-3.0-only",
        f"# Derived from {UPSTREAM_REPOSITORY}",
        f"# Source: {source_urls[0]}",
        f"# Source: {source_urls[1]}",
        f"# Upstream Last Updated: {last_updated[source_keys[0]]} (domainset)",
        f"# Upstream Last Updated: {last_updated[source_keys[1]]} (non_ip)",
        f"# Rule count: {len(rules)}",
        "",
    ]
    for rule_type, value in rules:
        if client == "quantumultx":
            output.append(f"{QX_TYPE_MAP[rule_type]}, {value}, proxy")
        elif client == "loon":
            output.append(f"{rule_type},{value}")
        else:
            raise ValueError(f"unsupported output client: {client}")
    return "\n".join(output).rstrip() + "\n"


def build_outputs(
    source_texts: dict[str, str],
    minimum_counts: dict[str, int] | None = None,
) -> dict[Path, str]:
    minimums = MINIMUM_COUNTS if minimum_counts is None else minimum_counts
    missing = set(SOURCE_SPECS) - set(source_texts)
    if missing:
        raise ValueError(f"missing SKK sources: {', '.join(sorted(missing))}")

    parsed: dict[str, list[Rule]] = {}
    last_updated: dict[str, str] = {}
    for key, spec in SOURCE_SPECS.items():
        text = source_texts[key]
        last_updated[key] = _validate_source_metadata(text, key)
        if spec["kind"] == "domainset":
            rules = parse_domainset(text, key)
        else:
            rules = parse_non_ip(text, key)
        minimum = minimums[key]
        if len(rules) < minimum:
            raise ValueError(
                f"{key}: {len(rules)} rules is below minimum {minimum}"
            )
        parsed[key] = rules

    merged: dict[str, tuple[list[Rule], tuple[str, str]]] = {}
    for ruleset in ("CDN", "Download"):
        prefix = ruleset.casefold()
        source_keys = (f"{prefix}_domainset", f"{prefix}_non_ip")
        rules = _deduplicate(parsed[source_keys[0]] + parsed[source_keys[1]])
        merged[ruleset] = (rules, source_keys)

    outputs: dict[Path, str] = {}
    for path, (client, ruleset) in OUTPUT_SPECS.items():
        rules, source_keys = merged[ruleset]
        outputs[path] = _render(
            rules, client, ruleset, source_keys, last_updated
        )
    return outputs


def fetch_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for key, spec in SOURCE_SPECS.items():
        request = Request(str(spec["url"]), headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=45) as response:
            data = response.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError(f"{key}: source exceeds {MAX_SOURCE_BYTES} bytes")
        sources[key] = data.decode("utf-8")
    return sources


def sync_outputs(
    root: Path,
    source_texts: dict[str, str],
    minimum_counts: dict[str, int] | None = None,
    check: bool = False,
) -> list[Path]:
    outputs = build_outputs(source_texts, minimum_counts=minimum_counts)
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
        description="Convert SKK CDN and Download rules for Quantumult X and Loon."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        sources = fetch_sources()
        changed = sync_outputs(ROOT, sources, check=args.check)
    except (HTTPError, URLError, UnicodeError, OSError, ValueError) as error:
        print(f"SKK update failed: {error}", file=sys.stderr)
        return 1

    for path in changed:
        action = "out of date" if args.check else "updated"
        print(f"{action}: {path.relative_to(ROOT)}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
