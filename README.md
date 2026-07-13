# Proxy Resource Hub

面向 Mihomo、Surge、Quantumult X 和 Loon 的分流规则订阅仓库。后续可继续扩展脚本、模块和其他代理资源。

## 维护方式

域名只在 `Rules/Source/` 中维护一次，平台目录中的 `.list` 文件由生成器创建，请勿直接编辑。

```bash
python3 tools/generate_rules.py
python3 tools/generate_rules.py --check
python3 -m unittest discover -s tests -v
```

更新规则时，修改源文件并运行第一条命令，然后将源文件和生成结果放在同一个提交中。GitHub Actions 只验证生成结果是否同步，不会自动修改仓库。

## 订阅地址

### Mihomo

- [AI 服务](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/AI/ai.list)
- [公益 AI](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/AI/gongyiai.list)

```yaml
rule-providers:
  gongyiai:
    type: http
    behavior: classical
    format: text
    url: https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/AI/gongyiai.list
    path: ./ruleset/gongyiai.list
    interval: 86400

rules:
  - RULE-SET,gongyiai,AI
```

### Surge

- [AI 服务](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/AI/ai.list)
- [公益 AI](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/AI/gongyiai.list)

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/AI/gongyiai.list,AI
```

### Quantumult X

- [AI 服务](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/AI/ai.list)
- [公益 AI](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/AI/gongyiai.list)

Quantumult X 输出中的默认策略是 `proxy`。推荐使用 `force-policy` 替换为自己配置中的策略名称：

```ini
[filter_remote]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/AI/gongyiai.list, tag=公益 AI, force-policy=AI, update-interval=86400, enabled=true
```

### Loon

- [AI 服务](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/AI/ai.list)
- [公益 AI](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/AI/gongyiai.list)

```ini
[Remote Rule]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/AI/gongyiai.list, AI
```

## 个人网站（默认直连）

个人网站域名统一在 `Rules/Source/Personal/sites.txt` 中维护，四端订阅默认映射到直连策略。

### Mihomo

- [个人网站](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Personal/sites.list)

```yaml
rule-providers:
  personal_sites:
    type: http
    behavior: classical
    format: text
    url: https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Personal/sites.list
    path: ./ruleset/personal-sites.list
    interval: 86400

rules:
  - RULE-SET,personal_sites,DIRECT
```

### Surge

- [个人网站](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Personal/sites.list)

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Personal/sites.list,DIRECT
```

### Quantumult X

- [个人网站](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Personal/sites.list)

```ini
[filter_remote]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Personal/sites.list, tag=个人网站, force-policy=direct, update-interval=86400, enabled=true
```

### Loon

- [个人网站](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Personal/sites.list)

```ini
[Remote Rule]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Personal/sites.list, policy=DIRECT, tag=个人网站, enabled=true
```

## 兼容地址

原有地址继续保留，并由同一个生成器维护：

- [Rules/AI/ai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/ai.list)
- [Rules/AI/gongyiai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/gongyiai.list)

兼容文件使用 Mihomo classical、Surge RULE-SET 和 Loon 订阅规则均可识别的 `DOMAIN-SUFFIX,<domain>` 格式。Quantumult X 请使用专属目录下的文件。

## 目录

```text
Rules/
├── Source/                  # 唯一手工维护入口
│   ├── AI/
│   └── Personal/
├── Mihomo/
│   ├── AI/
│   └── Personal/
├── Surge/
│   ├── AI/
│   └── Personal/
├── QuantumultX/
│   ├── AI/
│   └── Personal/
├── Loon/
│   ├── AI/
│   └── Personal/
└── AI/                      # 旧订阅地址兼容层
```
