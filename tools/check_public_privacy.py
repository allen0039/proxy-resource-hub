#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import sanitize_tool_configs as sanitizer


ROOT = Path(__file__).resolve().parents[1]
URL_CREDENTIAL_RE = re.compile(
    r"https?://[^\s\"'<>]*[?&](?:token|password|passwd|secret|auth|access_token|api_key)=[^\s\"'<>]+",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,63}\b"
)
USER_PATH_RE = re.compile(r"/(?:Users|home)/(?!runner/|user/|example/)[^/\s]+/")
SOURCE_IP_RE = re.compile(r"SRC-IP(?:-CIDR|6-CIDR)?\s*,\s*([^,\s\"'\\]+)", re.IGNORECASE)
FORBIDDEN_SUFFIXES = {".p12", ".pfx", ".key", ".bundle"}


def findings(path: str, text: str, private_values: list[str]) -> list[tuple[int, str]]:
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        if re.search(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY|CERTIFICATE)-----", line):
            result.append((number, "certificate or private key"))
        for match in sanitizer.TS_AUTH_KEY_RE.finditer(line):
            suffix = match[0].split("-", 2)[-1]
            samples = ("1234567890abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyz1234567890")
            if not (path.startswith("tests/") and any(suffix in sample for sample in samples)):
                result.append((number, "Tailscale credential"))
        for match in URL_CREDENTIAL_RE.finditer(line):
            host = urlsplit(match[0]).hostname or ""
            if not (host.endswith((".invalid", ".example")) or host in {"example.com", "public.example"}):
                result.append((number, "credential in URL"))
        for match in EMAIL_RE.finditer(line):
            host = match[0].rsplit("@", 1)[-1]
            if host not in {"users.noreply.github.com", "github.com", "example.com"} and not host.endswith(".invalid"):
                result.append((number, "personal email"))
        if USER_PATH_RE.search(line):
            result.append((number, "personal local path"))
        for match in SOURCE_IP_RE.finditer(line):
            try:
                address = ipaddress.ip_address(match[1].split("/", 1)[0])
            except ValueError:
                continue
            if not any(address in ipaddress.ip_network(network) for network in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")):
                result.append((number, "device-specific source address"))
        if any(value.casefold() in line.casefold() for value in private_values):
            result.append((number, "private publishing value"))
    return result


def check(root: Path, staged: bool, privacy_file: Path | None, identity: bool) -> list[str]:
    policy = sanitizer.load_privacy_policy(root.parent, privacy_file)
    private_values = [*policy["private_domains"], *policy["private_literals"]]
    paths = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
    errors = []
    for name in filter(None, paths):
        path = Path(name)
        if path.suffix in FORBIDDEN_SUFFIXES or any(part in {".private", ".planning", "backups"} for part in path.parts) or path.name.startswith(".env"):
            errors.append(f"{name}: private file must not be published")
            continue
        if staged:
            content = subprocess.check_output(["git", "-C", str(root), "show", ":" + name])
        else:
            content = (root / name).read_bytes()
        if b"\0" in content:
            continue
        text = content.decode("utf-8", errors="replace")
        errors.extend(f"{name}:{number}: {category}" for number, category in findings(name, text, private_values))
        if name.startswith("Configs/tool_config/") and path.name in sanitizer.CONFIG_NAMES:
            try:
                sanitizer.validate_common_patterns(path.name, text)
                sanitizer.validate_client_structure(path.name, text)
            except sanitizer.SanitizationError:
                errors.append(f"{name}: template privacy or structure validation failed")
        if name == "Rules/Source/Personal/Domain.txt" and any(line.strip() and not line.lstrip().startswith("#") for line in text.splitlines()):
            errors.append(f"{name}: personal compatibility feed must remain empty")
    if identity:
        emails = subprocess.check_output(["git", "-C", str(root), "log", "-1", "--format=%ae%n%ce"], text=True).splitlines()
        if any(not (email.endswith("@users.noreply.github.com") or email == "noreply@github.com") for email in emails):
            errors.append("commit identity must use a public noreply address")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--private-values-file", type=Path)
    parser.add_argument("--check-identity", action="store_true")
    arguments = parser.parse_args()
    try:
        errors = check(ROOT, arguments.staged, arguments.private_values_file, arguments.check_identity)
    except (OSError, ValueError, subprocess.CalledProcessError):
        print("privacy check could not complete", file=sys.stderr)
        return 1
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Public files passed privacy and template checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
