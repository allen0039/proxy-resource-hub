#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_NAMES = {
    "mihomo_byallen.yaml": "mihomo_allen.yaml",
    "surge-Mac.conf": "surge_mac_allen.conf",
    "Surge-iPhone.conf": "surge_iphone_allen.conf",
    "quantumult_byallen.conf": "quantumultx_allen.conf",
    "allenloon.lcf": "loon_allen.lcf",
}
CONFIG_NAMES = set(OUTPUT_NAMES.values())

URL_RE = re.compile(r"https?://[^,\s\"']+")
POLICY_PATH_RE = re.compile(r"(policy-path\s*=\s*)([^,\s]+)")
UUID_RE = re.compile(
    r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b"
)
LONG_BASE64_RE = re.compile(
    r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{256,}={0,2}(?![A-Za-z0-9+/])"
)
PRIVATE_QUERY_RE = re.compile(
    r"(?i)https?://[^\s,]*(?:token|password|passwd|secret|auth|key)="
)
PEM_MARKERS = ("BEGIN PRIVATE KEY", "BEGIN CERTIFICATE")


class SanitizationError(ValueError):
    pass


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.splitlines()).rstrip() + "\n"


def section_name(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        return stripped[1:-1].strip().casefold()
    return None


def example_url(
    client: str, category: str, index: int, suffix: str = "conf"
) -> str:
    return f"https://example.com/{client}/{category}-{index}.{suffix}"


def _active_content(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(("#", ";", "//")):
        return ""
    return stripped


def _key(line: str) -> str | None:
    content = _active_content(line)
    if "=" not in content:
        return None
    return content.split("=", 1)[0].strip().casefold()


def _replace_first_url(line: str, replacement: str) -> str:
    if not URL_RE.search(line):
        raise SanitizationError("subscription entry has no recognizable URL")
    return URL_RE.sub(replacement, line, count=1)


def _append_placeholder_once(
    output: list[str], marker: str, already_added: bool
) -> bool:
    if not already_added:
        output.append(marker)
    return True


def sanitize_surge(text: str, slug: str) -> str:
    lines = normalize_text(text).splitlines()
    output: list[str] = []
    current = ""
    subscription_index = 0
    mitm_marker = False
    proxy_marker = False
    secret_keys = {
        "ca-passphrase",
        "ca-p12",
        "http-api",
        "http-api-tls",
        "external-controller-access",
        "secret",
    }

    for line in lines:
        if (name := section_name(line)) is not None:
            current = name
            output.append(line)
            continue

        if POLICY_PATH_RE.search(line):
            subscription_index += 1
            replacement = example_url(slug, "subscription", subscription_index)
            line, count = POLICY_PATH_RE.subn(
                lambda match: match.group(1) + replacement,
                line,
                count=1,
            )
            if count != 1:
                raise SanitizationError(f"{slug}: unrecognized policy-path")

        key = _key(line)
        if current == "mitm" and key in {"ca-passphrase", "ca-p12"}:
            mitm_marker = _append_placeholder_once(
                output,
                "# Configure MITM certificate and passphrase locally.",
                mitm_marker,
            )
            continue
        if current == "proxy" and line.strip():
            proxy_marker = _append_placeholder_once(
                output,
                "# Configure local proxy nodes privately.",
                proxy_marker,
            )
            continue
        if key in secret_keys:
            output.append(line.split("=", 1)[0].rstrip() + " = CHANGE_ME")
            continue
        output.append(line)

    if subscription_index == 0:
        raise SanitizationError(f"{slug}: no policy-path subscriptions found")
    return normalize_text("\n".join(output))


def sanitize_quantumultx(text: str) -> str:
    lines = normalize_text(text).splitlines()
    output: list[str] = []
    current = ""
    subscription_index = 0
    node_marker = False
    mitm_marker = False

    for line in lines:
        if (name := section_name(line)) is not None:
            current = name
            output.append(line)
            continue

        content = _active_content(line)
        if current == "server_remote":
            if URL_RE.search(line):
                subscription_index += 1
                output.append(
                    _replace_first_url(
                        line,
                        example_url(
                            "quantumultx", "subscription", subscription_index
                        ),
                    )
                )
                continue
            if content:
                raise SanitizationError(
                    "quantumultx: active remote subscription has no URL"
                )
        if current == "server_local" and line.strip():
            node_marker = _append_placeholder_once(
                output,
                "# Configure local proxy nodes privately.",
                node_marker,
            )
            continue
        if current == "mitm" and _key(line) in {
            "passphrase",
            "p12",
            "certificate",
            "private-key",
        }:
            mitm_marker = _append_placeholder_once(
                output,
                "# Configure MITM certificate and passphrase locally.",
                mitm_marker,
            )
            continue
        output.append(line)

    if subscription_index == 0:
        raise SanitizationError("quantumultx: no remote subscriptions found")
    return normalize_text("\n".join(output))


def sanitize_loon(text: str) -> str:
    lines = normalize_text(text).splitlines()
    output: list[str] = []
    current = ""
    subscription_index = 0
    node_marker = False
    mitm_marker = False

    for line in lines:
        if (name := section_name(line)) is not None:
            current = name
            output.append(line)
            continue

        content = _active_content(line)
        if current == "remote proxy":
            if URL_RE.search(line):
                subscription_index += 1
                output.append(
                    _replace_first_url(
                        line,
                        example_url("loon", "subscription", subscription_index),
                    )
                )
                continue
            if content:
                raise SanitizationError(
                    "loon: active remote subscription has no URL"
                )
        if current == "proxy" and line.strip():
            node_marker = _append_placeholder_once(
                output,
                "# Configure local proxy nodes privately.",
                node_marker,
            )
            continue
        if current == "mitm" and _key(line) in {
            "ca-p12",
            "ca-passphrase",
            "certificate",
            "private-key",
        }:
            mitm_marker = _append_placeholder_once(
                output,
                "# Configure MITM certificate and passphrase locally.",
                mitm_marker,
            )
            continue
        output.append(line)

    if subscription_index == 0:
        raise SanitizationError("loon: no remote subscriptions found")
    return normalize_text("\n".join(output))


def _provider_names(text: str) -> list[str]:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise SanitizationError("mihomo: source YAML cannot be parsed") from error
    if not isinstance(parsed, dict):
        raise SanitizationError("mihomo: source YAML root is not a mapping")
    providers = parsed.get("proxy-providers")
    if not isinstance(providers, dict) or not providers:
        raise SanitizationError("mihomo: proxy-providers mapping is missing")
    return list(providers)


def _rename_provider_tokens(text: str, names: list[str]) -> str:
    for index, old_name in enumerate(names, 1):
        new_name = f"subscription_{index}"
        token = re.compile(
            rf"(?<![\w\u4e00-\u9fff]){re.escape(str(old_name))}"
            rf"(?![\w\u4e00-\u9fff])"
        )
        text = token.sub(new_name, text)
    return text


def _replace_mihomo_provider_urls(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    in_providers = False
    provider_index = 0

    for line in lines:
        if line and not line.startswith((" ", "\t", "#")):
            in_providers = line.strip() == "proxy-providers:"
        if in_providers and re.match(r"^  subscription_\d+:\s*$", line):
            provider_index += 1
        if in_providers and re.match(r"^    url:\s*", line):
            if provider_index == 0:
                raise SanitizationError("mihomo: provider URL precedes provider name")
            line = (
                "    url: \""
                + example_url("mihomo", "subscription", provider_index, "yaml")
                + "\""
            )
        elif in_providers and re.match(r"^#    url:\s*", line):
            line = (
                "#    url: \""
                + example_url("mihomo", "subscription-example", 1, "yaml")
                + "\""
            )
        output.append(line)
    return "\n".join(output)


def _sanitize_mihomo_proxy_scalars(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    current = ""
    replacements = {
        "server": "example.com",
        "uuid": "CHANGE_ME",
        "password": "CHANGE_ME",
        "private-key": "CHANGE_ME",
        "certificate": "CHANGE_ME",
        "token": "CHANGE_ME",
        "key": "CHANGE_ME",
    }

    for line in lines:
        if line and not line.startswith((" ", "\t", "#")) and ":" in line:
            current = line.split(":", 1)[0].strip().casefold()
        if current == "proxies":
            match = re.match(
                r"^(\s+(?:-\s+)?)(server|uuid|password|private-key|certificate|token|key)(:\s*).*$",
                line,
            )
            if match:
                line = (
                    match.group(1)
                    + match.group(2)
                    + match.group(3)
                    + replacements[match.group(2)]
                )
        if re.match(r"^secret:\s*", line):
            line = "secret: CHANGE_ME"
        output.append(line)
    return "\n".join(output)


def sanitize_mihomo(text: str) -> str:
    normalized = normalize_text(text)
    names = _provider_names(normalized)
    sanitized = _rename_provider_tokens(normalized, names)
    sanitized = _replace_mihomo_provider_urls(sanitized)
    sanitized = _sanitize_mihomo_proxy_scalars(sanitized)
    return normalize_text(sanitized)


def _sections(text: str) -> dict[str, list[tuple[int, str]]]:
    result: dict[str, list[tuple[int, str]]] = {}
    current = ""
    for number, line in enumerate(text.splitlines(), 1):
        if (name := section_name(line)) is not None:
            current = name
            result.setdefault(current, [])
            continue
        if current:
            result.setdefault(current, []).append((number, line))
    return result


def _require_sections(filename: str, text: str, expected: set[str]) -> None:
    missing = expected - set(_sections(text))
    if missing:
        raise SanitizationError(
            f"{filename}: missing expected section category ({len(missing)})"
        )


def _sensitive_section_urls(
    filename: str, lines: list[tuple[int, str]]
) -> None:
    for number, line in lines:
        match = URL_RE.search(line)
        if match and urlsplit(match.group(0)).hostname != "example.com":
            raise SanitizationError(
                f"{filename}:{number}: non-placeholder subscription URL remains"
            )


def _surge_policy_path_urls(
    filename: str, lines: list[tuple[int, str]]
) -> None:
    for number, line in lines:
        match = POLICY_PATH_RE.search(line)
        if match is None or urlsplit(match.group(2)).hostname != "example.com":
            raise SanitizationError(
                f"{filename}:{number}: non-placeholder policy-path remains"
            )


def _validate_ini_client(filename: str, text: str) -> None:
    sections = _sections(text)
    if filename.startswith("surge_"):
        _require_sections(filename, text, {"general", "proxy group", "rule", "mitm"})
        policy_paths = [
            (number, line)
            for number, line in sections["proxy group"]
            if POLICY_PATH_RE.search(line)
        ]
        _surge_policy_path_urls(filename, policy_paths)
        forbidden = {"ca-passphrase", "ca-p12"}
    elif filename == "quantumultx_allen.conf":
        _require_sections(
            filename,
            text,
            {"policy", "server_remote", "server_local", "filter_remote", "filter_local", "mitm"},
        )
        _sensitive_section_urls(filename, sections["server_remote"])
        if any(
            line.strip()
            and line.strip() != "# Configure local proxy nodes privately."
            for _, line in sections["server_local"]
        ):
            raise SanitizationError(f"{filename}: active local proxy node remains")
        forbidden = {"passphrase", "p12", "certificate", "private-key"}
    elif filename == "loon_allen.lcf":
        _require_sections(
            filename,
            text,
            {"remote proxy", "proxy group", "rule", "remote rule", "plugin", "mitm"},
        )
        _sensitive_section_urls(filename, sections["remote proxy"])
        if "proxy" in sections and any(
            line.strip()
            and line.strip() != "# Configure local proxy nodes privately."
            for _, line in sections["proxy"]
        ):
            raise SanitizationError(f"{filename}: active local proxy node remains")
        forbidden = {"ca-p12", "ca-passphrase", "certificate", "private-key"}
    else:
        raise SanitizationError(f"{filename}: unknown INI client")

    for number, line in sections["mitm"]:
        if _key(line) in forbidden:
            raise SanitizationError(
                f"{filename}:{number}: MITM credential material remains"
            )


def _validate_mihomo(filename: str, text: str) -> None:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise SanitizationError(f"{filename}: YAML cannot be parsed") from error
    if not isinstance(parsed, dict):
        raise SanitizationError(f"{filename}: YAML root is not a mapping")

    providers = parsed.get("proxy-providers")
    groups = parsed.get("proxy-groups")
    proxies = parsed.get("proxies", [])
    rules = parsed.get("rules")
    rule_providers = parsed.get("rule-providers")
    if not isinstance(providers, dict) or not providers:
        raise SanitizationError(f"{filename}: proxy-providers mapping is missing")
    if not isinstance(groups, list) or not isinstance(rules, list):
        raise SanitizationError(f"{filename}: groups or rules list is missing")
    if not isinstance(rule_providers, dict):
        raise SanitizationError(f"{filename}: rule-providers mapping is missing")

    expected_provider_names = {
        f"subscription_{index}" for index in range(1, len(providers) + 1)
    }
    if set(providers) != expected_provider_names:
        raise SanitizationError(f"{filename}: provider names are not generic")
    for provider in providers.values():
        if not isinstance(provider, dict):
            raise SanitizationError(f"{filename}: provider entry is not a mapping")
        if urlsplit(str(provider.get("url", ""))).hostname != "example.com":
            raise SanitizationError(
                f"{filename}: non-placeholder provider URL remains"
            )
    if parsed.get("secret") != "CHANGE_ME":
        raise SanitizationError(f"{filename}: controller secret is not sanitized")

    group_names = [
        group.get("name") for group in groups if isinstance(group, dict)
    ]
    if len(group_names) != len(groups) or len(set(group_names)) != len(group_names):
        raise SanitizationError(f"{filename}: proxy group names are invalid")
    proxy_names = {
        proxy.get("name") for proxy in proxies if isinstance(proxy, dict)
    }
    allowed_members = set(group_names) | proxy_names | {
        "DIRECT",
        "REJECT",
        "PASS",
        "COMPATIBLE",
    }
    for group in groups:
        uses = group.get("use", []) or []
        if not set(uses) <= set(providers):
            raise SanitizationError(f"{filename}: group provider reference is missing")
        explicit = group.get("proxies", []) or []
        if not set(explicit) <= allowed_members:
            raise SanitizationError(f"{filename}: explicit group member is missing")

    referenced_rule_providers: set[str] = set()
    for rule in rules:
        if not isinstance(rule, str):
            raise SanitizationError(f"{filename}: non-string rule remains")
        parts = [part.strip() for part in rule.split(",")]
        if parts and parts[0].upper() == "RULE-SET" and len(parts) >= 3:
            referenced_rule_providers.add(parts[1])
    if not referenced_rule_providers <= set(rule_providers):
        raise SanitizationError(f"{filename}: RULE-SET provider reference is missing")
    if not rules or str(rules[-1]).split(",", 1)[0].upper() != "MATCH":
        raise SanitizationError(f"{filename}: MATCH is not the final rule")


def validate_common_patterns(filename: str, text: str) -> None:
    if UUID_RE.search(text):
        raise SanitizationError(f"{filename}: UUID remains")
    if any(marker in text for marker in PEM_MARKERS):
        raise SanitizationError(f"{filename}: certificate material remains")
    if LONG_BASE64_RE.search(text):
        raise SanitizationError(f"{filename}: long base64 material remains")
    if PRIVATE_QUERY_RE.search(text):
        raise SanitizationError(f"{filename}: credential query parameter remains")


def validate_client_structure(filename: str, text: str) -> None:
    if filename == "mihomo_allen.yaml":
        _validate_mihomo(filename, text)
    else:
        _validate_ini_client(filename, text)


def validate_sanitized_outputs(outputs: dict[str, str]) -> None:
    if set(outputs) != CONFIG_NAMES:
        raise SanitizationError("generated filename set does not match contract")
    for filename, text in outputs.items():
        validate_common_patterns(filename, text)
        validate_client_structure(filename, text)


def generate(source_dir: Path, output_dir: Path) -> dict[str, str]:
    sanitizers = {
        "surge-Mac.conf": lambda text: sanitize_surge(text, "surge-mac"),
        "Surge-iPhone.conf": lambda text: sanitize_surge(text, "surge-iphone"),
        "quantumult_byallen.conf": sanitize_quantumultx,
        "allenloon.lcf": sanitize_loon,
        "mihomo_byallen.yaml": sanitize_mihomo,
    }
    outputs: dict[str, str] = {}
    for source_name, output_name in OUTPUT_NAMES.items():
        source_path = source_dir / source_name
        if not source_path.is_file():
            raise SanitizationError(f"missing private source category: {source_name}")
        outputs[output_name] = sanitizers[source_name](
            source_path.read_text(encoding="utf-8")
        )
    validate_sanitized_outputs(outputs)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in outputs.items():
        (output_dir / filename).write_text(text, encoding="utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "Configs" / "tool_config"
    )
    args = parser.parse_args()
    try:
        outputs = generate(args.source_dir, args.output_dir)
    except (OSError, UnicodeError, SanitizationError) as error:
        print(error, file=sys.stderr)
        return 1
    for filename in sorted(outputs):
        print(f"updated: {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
