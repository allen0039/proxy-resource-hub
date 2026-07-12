#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULESETS = ("ai", "gongyiai")
CLASSICAL_TARGETS = ("Mihomo", "Surge", "Loon")
DOMAIN_RE = re.compile(
    r"(?=.{1,253}\Z)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z"
)


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


def build_outputs(root: Path) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for name in RULESETS:
        source = root / "Rules" / "Source" / "AI" / f"{name}.txt"
        source_label = source.relative_to(root).as_posix()
        lines = parse_source(source)
        classical = render(lines, "classical", source_label)
        for client in CLASSICAL_TARGETS:
            outputs[root / "Rules" / client / "AI" / f"{name}.list"] = classical
        outputs[root / "Rules" / "QuantumultX" / "AI" / f"{name}.list"] = render(
            lines, "quantumultx", source_label
        )
        outputs[root / "Rules" / "AI" / f"{name}.list"] = classical
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
