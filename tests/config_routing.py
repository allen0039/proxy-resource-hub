"""Read routing data without exposing subscription or certificate sections."""
from pathlib import Path
import re
import yaml

HUB = Path(__file__).resolve().parents[1]
ROOT = HUB / 'Configs/tool_config'
CLIENTS = ('surge_mac_allen.conf', 'surge_iphone_allen.conf', 'quantumultx_allen.conf',
           'loon_allen.lcf', 'mihomo_allen.yaml', 'egern_byallen.yaml')
BASE = 'https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/'


def read(name):
    return (ROOT / name).read_text()


def section(name, key):
    match = re.search(r'(?ms)^\[' + re.escape(key) + r'\]\s*\n(.*?)(?=^\[|\Z)', read(name))
    return [line.strip() for line in match[1].splitlines()
            if line.strip() and not line.lstrip().startswith(('#', ';', '//'))]


def groups(name):
    if name.endswith('.yaml'):
        data = yaml.safe_load(read(name))
        if name.startswith('mihomo'):
            return {g['name']: g.get('proxies', []) for g in data['proxy-groups']}
        return {g['name']: g.get('policies', []) for item in data['policy_groups'] for g in item.values()}
    qx = name.startswith('quantumult')
    result = {}
    for line in section(name, 'policy' if qx else 'Proxy Group'):
        head, *tail = line.split(',')
        group = head.split('=', 1)[1 if qx else 0].strip()
        result[group] = [p.strip() for p in tail if '=' not in p]
    return result


def normalized_members(name, members):
    return [p.replace('优选', '故转') if name.endswith('.lcf') else
            {'direct': 'DIRECT', 'proxy': 'Proxy'}.get(p, p) for p in members]


def remote(name):
    if name.startswith('mihomo'):
        data = yaml.safe_load(read(name))
        return [(data['rule-providers'][r.split(',')[1]]['url'], r.split(',')[2])
                for r in data['rules'] if r.startswith('RULE-SET,')]
    if name.startswith('egern'):
        return [(r['rule_set']['match'], r['rule_set']['policy'])
                for r in yaml.safe_load(read(name))['rules'] if 'rule_set' in r]
    if name.startswith('quantumult') or name.endswith('.lcf'):
        qx = name.startswith('quantumult')
        entries = []
        for line in section(name, 'filter_remote' if qx else 'Remote Rule'):
            if 'enabled=false' in line:continue
            policy = re.search(r'(?:force-policy|policy)=([^,]+)', line)
            if policy:entries.append((line.split(',')[0], policy[1]))
        return entries
    return [(parts[1], parts[2]) for line in section(name, 'Rule')
            if (parts := line.split(','))[0] in {'RULE-SET', 'DOMAIN-SET'}]


def local(name):
    if name.startswith('mihomo'):
        lines = yaml.safe_load(read(name))['rules']
    elif name.startswith('egern'):
        return [(kind.upper().replace('_','-'), body.get('match'), body.get('policy'))
                for item in yaml.safe_load(read(name))['rules'] for kind, body in item.items()
                if kind in {'domain','domain_suffix','domain_keyword','ip_cidr','ip_cidr6'}]
    else:
        lines = section(name, 'filter_local' if name.startswith('quantumult') else 'Rule')
    types = {'HOST':'DOMAIN','HOST-SUFFIX':'DOMAIN-SUFFIX','HOST-KEYWORD':'DOMAIN-KEYWORD','IP6-CIDR':'IP-CIDR6'}
    out = []
    for line in lines:
        fields = [p.strip() for p in line.split(',')]
        typ = types.get(fields[0].upper(), fields[0].upper())
        if typ in {'DOMAIN','DOMAIN-SUFFIX','DOMAIN-KEYWORD','IP-CIDR','IP-CIDR6'}:
            out.append((typ, fields[1], {'direct':'DIRECT','reject':'REJECT','proxy':'Proxy'}.get(fields[2],fields[2])))
    return out


def remote_index(name, token):
    return next(i for i,(url,_) in enumerate(remote(name)) if token in url)


def assert_business_alignment(test, name):
    source = groups('surge_iphone_allen.conf')
    actual = groups(name)
    for group, members in source.items():
        if group not in ('Proxy','Final','Google','AI','Telegram','TikTok','国外社交','YouTube',
                         'Netflix','Emby','Spotify','巴哈姆特','哔哩哔哩','国外媒体','特殊媒体',
                         '国内媒体','海淘','PayPal','Apple','Microsoft','OneDrive','GitHub','Docker','游戏平台','CDN','测速'):
            continue
        if name.startswith('quantumult') and group == 'Proxy':continue
        got = normalized_members(name, actual[group])
        if group == 'Telegram':got = [p for p in got if p != 'DIRECT']
        test.assertEqual(got, members, f'{name}: {group} menu differs from Surge')


def assert_stage_order(test, name):
    urls = [u for u,_ in remote(name)]
    def at(*tokens):
        return next(i for i,u in enumerate(urls) if any(t in u for t in tokens))
    positions = [
        at('ChinaTelecom'), at('/anti-ad-', '/Rules/Ads_SukkaW.', '/domainset/reject'),
        at('/BiliBili/', '/Bilibili.yaml'), at('/egern/cn.yaml', '/non_ip/domestic'),
        at('/speedtest.', '/domainset/speedtest'), at('/AI/ai.'),
        at('/Google/Google.', '/Rules/Google.yaml', '/egern/google.yaml'),
        at('/ProxyMedia.', '/non_ip/stream'), at('/shop/shopping.'),
        at('/SKK/CDN.', '/domainset/cdn'), at('/Rules/Proxy.yaml', '/non_ip/global'),
    ]
    test.assertEqual(positions, sorted(positions), f'{name}: routing stage order')
    ip_tokens = ('/Rules/Telegram.yaml', '/ip/telegram.', '/ip/domestic.', '/egern/cncidr.yaml', '/ip/china_ip.')
    for i,url in enumerate(urls):
        if any(t in url for t in ip_tokens):
            threshold = positions[-2] if name.startswith('egern') and '/Rules/Telegram.yaml' in url else positions[-1]
            test.assertGreater(i, threshold, f'{name}: IP fallback precedes business/CDN rules')
            if name.startswith('egern') and '/Rules/Telegram.yaml' in url:
                test.assertLess(i, positions[-1], f'{name}: generic proxy IPs shadow Telegram')


def assert_canonical_local(test, name):
    required = set(local('surge_iphone_allen.conf'))
    actual = local(name)
    missing = required - set(actual)
    test.assertFalse(missing, f'{name}: missing {len(missing)} canonical local overrides')
    for rule in required:
        test.assertEqual(actual.count(rule), 1, f'{name}: duplicate canonical override')


def assert_compatibility(test, name):
    rules = local(name)
    test.assertIn(('IP-CIDR','203.107.1.0/24','DIRECT'), rules)
    for host in ('httpdns.alicdn.com','httpdns.danuoyi.tbcache.com','httpdns.bilivideo.com',
                 'httpdns.meituan.com','httpdns.music.163.com','httpdns.volces.com','dns.weixin.qq.com'):
        test.assertIn(('DOMAIN',host,'DIRECT'), rules, f'{name}: missing HTTPDNS exception')
    test.assertIn(('DOMAIN-SUFFIX','ggpht.com','YouTube'), rules)
    test.assertIn(('DOMAIN-SUFFIX','pool.ntp.org','DIRECT'), rules)
    test.assertIn(('DOMAIN-SUFFIX','media-amazon.com','海淘'), rules)
