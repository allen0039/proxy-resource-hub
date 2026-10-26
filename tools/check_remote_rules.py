#!/usr/bin/env python3
"""Check real HTTP availability of active public-template rule subscriptions.

Never substitute local repository files for an HTTP request. Run this against
the published main branch before distributing configurations that use new URLs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 16 * 1024 * 1024
EGERN_FIELDS = {
    'domain_set', 'domain_suffix_set', 'domain_keyword_set', 'domain_regex_set',
    'domain_wildcard_set', 'url_regex_set', 'user_agent_set', 'geoip_set',
    'ip_cidr_set', 'ip_cidr6_set', 'asn_set', 'ssid_set', 'bssid_set',
    'cellular_set', 'protocol_set', 'dest_port_set', 'and_set', 'or_set', 'not_set',
}


def validate_yaml_rules(parsed):
    if not isinstance(parsed, dict) or not parsed:
        raise ValueError('rule YAML must be a nonempty mapping')
    if set(parsed) == {'payload'}:
        if not isinstance(parsed['payload'], list) or not parsed['payload']:
            raise ValueError('Clash payload must be a nonempty list')
        return
    unknown = set(parsed) - EGERN_FIELDS - {'no_resolve'}
    if unknown:
        raise ValueError('undocumented Egern rule fields: ' + ', '.join(sorted(unknown)))
    if 'no_resolve' in parsed and not isinstance(parsed['no_resolve'], bool):
        raise ValueError('Egern no_resolve must be boolean')
    if any(not isinstance(v, list) for k, v in parsed.items() if k != 'no_resolve'):
        raise ValueError('Egern rule fields must contain lists')
    if not any(v for k, v in parsed.items() if k != 'no_resolve'):
        raise ValueError('Egern resource contains no rules')


def collect_urls(directory):
    urls = {}
    for path in sorted(Path(directory).iterdir()):
        if path.suffix not in {'.conf', '.lcf', '.yaml'}:
            continue
        candidates = []
        if path.suffix == '.yaml':
            data = yaml.safe_load(path.read_text())
            if 'rule-providers' in data:
                for rule in data.get('rules', []):
                    if isinstance(rule, str) and rule.startswith('RULE-SET,'):
                        provider = data['rule-providers'][rule.split(',')[1]]
                        if 'url' in provider:
                            candidates.append(provider['url'])
            else:
                candidates.extend(r['rule_set']['match'] for r in data.get('rules', [])
                                  if 'rule_set' in r)
        else:
            section = ''
            for raw in path.read_text().splitlines():
                line = raw.strip()
                if not line or line.startswith(('#', ';', '//')):
                    continue
                if line.startswith('['):
                    section = line.strip('[]')
                    continue
                if re.search(r'\benabled\s*=\s*false\b', line, re.I):
                    continue
                if section == 'Rule':
                    fields = line.split(',')
                    if fields[0] in {'RULE-SET', 'DOMAIN-SET'}:
                        candidates.append(fields[1].strip())
                elif section in {'Remote Rule', 'filter_remote'}:
                    candidates.append(line.split(',')[0].strip())
        for url in candidates:
            if urlsplit(url).scheme in {'https', 'http'}:
                urls.setdefault(url, []).append(path.name)
    return urls


def check_url(url, timeout=25, cache_dir=None):
    result = {'url': url, 'ok': False}
    try:
        with urlopen(Request(url, headers={'User-Agent': 'proxy-resource-hub-link-check/1.0'}),
                     timeout=timeout) as response:
            result['status'] = response.status
            body = response.read(MAX_BYTES + 1)
            content_type = response.headers.get('Content-Type', '')
        result['bytes'] = len(body)
        result['sha256'] = hashlib.sha256(body).hexdigest()
        if not body or len(body) > MAX_BYTES:
            raise ValueError('empty or oversized resource')
        if 'text/html' in content_type or re.search(br'<!doctype\s+html|<html\b', body[:1024], re.I):
            raise ValueError('HTML returned instead of a rule resource')
        if urlsplit(url).path.endswith(('.yaml', '.yml')):
            parsed = yaml.safe_load(body)
            validate_yaml_rules(parsed)
        elif not urlsplit(url).path.endswith('.mrs'):
            text = body.decode('utf-8-sig')
            if not any(line.strip() and not line.lstrip().startswith(('#', ';', '//'))
                       for line in text.splitlines()):
                raise ValueError('resource contains no active rules')
        result['ok'] = True
        if cache_dir:
            path = Path(cache_dir) / (hashlib.sha256(url.encode()).hexdigest() + '.txt')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            result['snapshot'] = str(path.resolve())
    except HTTPError as error:
        result.update(status=error.code, error=f'HTTP {error.code}')
    except Exception as error:
        result['error'] = str(error)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, default=ROOT / 'Configs/tool_config')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--workers', type=int, default=12)
    parser.add_argument('--cache-dir', type=Path, help='save the actual downloaded bodies for format/routing validation')
    args = parser.parse_args()
    urls = collect_urls(args.config_dir)
    if not urls:
        parser.error('no active remote rules found')
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 24))) as pool:
        results = list(pool.map(lambda url: check_url(url, cache_dir=args.cache_dir), sorted(urls)))
    for result in results:
        result['configs'] = urls[result['url']]
    report = {'total': len(results), 'passed': sum(r['ok'] for r in results),
              'results': results}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"Remote rules available: {report['passed']}/{report['total']}")
    for result in results:
        if not result['ok']:
            print(f"{result['error']}: {result['url']}")
    return int(report['passed'] != report['total'])


if __name__ == '__main__':
    raise SystemExit(main())
