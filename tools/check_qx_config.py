#!/usr/bin/env python3
"""Audit QX filters with real downloads and the configuration's actual parser.

Does not request node subscriptions or read certificate values. A conversion
that skips unsupported rules is a failure even if its remaining output is valid.
Requires Node.js to execute the parser in a bounded context without I/O APIs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'host', 'host-suffix', 'host-keyword', 'host-wildcard', 'user-agent',
         'ip-cidr', 'ip6-cidr', 'ip-asn', 'geoip'}
BUILTINS = {'direct', 'proxy', 'reject', 'reject-tinygif', 'reject-drop'}


def active_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()
            and not line.lstrip().startswith(('#', ';', '//'))]


def sections(text):
    result, current = {}, None
    for line in text.splitlines():
        match = re.fullmatch(r'\s*\[([^\]]+)\]\s*', line)
        if match:
            current = match[1]
            if current in result:
                raise ValueError('duplicate section: ' + current)
            result[current] = []
        elif current:
            result[current].append(line)
    return {key: active_lines('\n'.join(lines)) for key, lines in result.items()}


def resource_entry(line):
    parts = [s.strip() for s in line.split(',')]
    options = dict(part.split('=', 1) for part in parts[1:] if '=' in part)
    return {'url': parts[0], 'parser': options.get('opt-parser') == 'true',
            'tag': options.get('tag', ''), 'policy': options.get('force-policy'),
            'enabled': options.get('enabled', 'true') != 'false'}


def validate_filters(text, local=False, policies=None, forced_policy=None):
    lines = active_lines(text)
    if not lines:
        raise ValueError('resource contains no active filters')
    count, finals = 0, []
    for number, line in enumerate(lines, 1):
        fields = [s.strip() for s in line.split(',')]
        kind = fields[0].lower()
        if local and kind == 'final':
            if len(fields) != 2 or not fields[1]:
                raise ValueError(f'line {number}: invalid final filter')
            finals.append(number)
            policy = fields[1]
        else:
            if kind not in TYPES or len(fields) < 3 or not fields[1] or not fields[2]:
                raise ValueError(f'line {number}: unsupported or malformed filter type {fields[0]}')
            for option in fields[3:]:
                if option not in {'force-cellular', 'multi-interface', 'multi-interface-balance'} and not option.startswith('via-interface='):
                    raise ValueError(f'line {number}: unsupported QX filter option {option}')
            policy = forced_policy or fields[2]
        if policies is not None and policy not in policies and policy.lower() not in BUILTINS:
            raise ValueError(f'line {number}: undefined filter policy {policy}')
        count += 1
    if local and finals != [len(lines)]:
        raise ValueError('local filters must end with exactly one final filter')
    return count


def policy_names(config):
    names = set()
    for line in config.get('policy', []):
        head = line.split(',', 1)[0]
        kind, name = head.split('=', 1)
        if kind.strip() not in {'static', 'available', 'round-robin', 'dest-hash', 'url-latency-benchmark'}:
            raise ValueError('unsupported policy type: ' + kind)
        name = name.strip()
        if name in names:
            raise ValueError('duplicate policy: ' + name)
        names.add(name)
    # Only extract local server names; never print or download node material.
    names.update(m[1].strip() for line in config.get('server_local', [])
                 if (m := re.search(r'(?:^|,)\s*tag=([^,]+)', line)))
    for line in config.get('policy', []):
        for member in line.split(',')[1:]:
            member = member.strip()
            if '=' not in member and member not in names and member.lower() not in BUILTINS:
                raise ValueError('undefined policy member: ' + member)
    return names


def download(url, directory):
    request = Request(url, headers={'User-Agent': 'proxy-resource-hub-qx-audit/1.0'})
    with urlopen(request, timeout=30) as response:
        body = response.read(16 * 1024 * 1024 + 1)
        status = response.status
        content_type = response.headers.get('Content-Type', '')
    if not body or len(body) > 16 * 1024 * 1024:
        raise ValueError('empty or oversized resource')
    if 'text/html' in content_type or re.search(br'<!doctype\s+html|<html\b', body[:1024], re.I):
        raise ValueError('HTML returned instead of a resource')
    snapshot = directory / (hashlib.sha256(url.encode()).hexdigest() + '.txt')
    snapshot.write_bytes(body)
    return {'url': url, 'status': status, 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest(), 'snapshot': str(snapshot.resolve())}


def audit(path, cache_dir):
    config = sections(path.read_text())
    names = policy_names(config)
    local_count = validate_filters('\n'.join(config.get('filter_local', [])), local=True, policies=names)
    entries = [resource_entry(line) for line in config.get('filter_remote', [])]
    entries = [entry for entry in entries if entry['enabled']]
    urls = [entry['url'] for entry in entries]
    if len(urls) != len(set(urls)):
        raise ValueError('duplicate active filter resource')
    parser_url = next(line.split('=', 1)[1].strip() for line in config['general']
                      if line.startswith('resource_parser_url='))
    cache_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=12) as pool:
        downloads = dict(zip([parser_url] + urls, pool.map(
            lambda url: download(url, cache_dir), [parser_url] + urls)))
    inputs = []
    for entry in entries:
        inputs.append(dict(entry, content=Path(downloads[entry['url']]['snapshot']).read_text(encoding='utf-8-sig')))
    payload = {'parser': Path(downloads[parser_url]['snapshot']).read_text(), 'resources': inputs}
    completed = subprocess.run(['node', str(ROOT / 'tools/parse_qx_resources.cjs')],
                               input=json.dumps(payload), capture_output=True, text=True,
                               check=True, timeout=max(60, 16 * len(inputs)))
    parsed = json.loads(completed.stdout)
    results = []
    for entry, output in zip(entries, parsed):
        result = dict(downloads[entry['url']], parser=entry['parser'], tag=entry['tag'],
                      notifications=output['notifications'], ok=False)
        try:
            if output['error']:
                raise ValueError(output['error'])
            if output['notifications']:
                raise ValueError('resource parser posted a notification; inspect skipped/changed rules')
            count = validate_filters(output['content'], policies=names, forced_policy=entry['policy'])
            snapshot = cache_dir / ('parsed-' + hashlib.sha256(entry['url'].encode()).hexdigest() + '.txt')
            snapshot.write_text(output['content'])
            result.update(ok=True, count=count, parsed_snapshot=str(snapshot.resolve()))
        except ValueError as error:
            result['error'] = str(error)
        results.append(result)
    return {'config': path.name, 'total': len(results), 'passed': sum(r['ok'] for r in results),
            'local_filters': local_count, 'policies': len(names),
            'parser_download': downloads[parser_url], 'resources': results,
            'limits': 'Checks filter syntax, references, real downloads and parser notifications; does not emulate the QX app or node connectivity.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'Configs/tool_config/quantumultx_allen.conf')
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.config, args.cache_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"QX filter resources without conversion warnings: {report['passed']}/{report['total']}; local filters: {report['local_filters']}")
    for result in report['resources']:
        if not result['ok']:
            print(result['error'] + ': ' + result['url'])
    return int(report['passed'] != report['total'])


if __name__ == '__main__':
    raise SystemExit(main())
