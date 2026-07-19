# Proxy Resource Hub

[![Validate rules](https://github.com/allen0039/proxy-resource-hub/actions/workflows/validate-rules.yml/badge.svg)](https://github.com/allen0039/proxy-resource-hub/actions/workflows/validate-rules.yml)

面向 Mihomo、Surge、Quantumult X 和 Loon 的代理配置与分流规则仓库。仓库提供五份脱敏配置模板，以及 AI、个人域名、PT 站点和 SKK CDN/Download 规则订阅。

> [!IMPORTANT]
> `Configs/tool_config/` 中的文件是公开脱敏模板，不是开箱即用的节点订阅。使用前必须在自己的私人副本中替换 `https://example.com/...`、`CHANGE_ME`、本地节点和 MITM 证书。不要把填写后的私人配置提交到公开仓库。

## 内容导航

- [快速开始](#快速开始)
- [客户端配置教程](#客户端配置教程)
- [配置与策略说明](#配置与策略说明)
- [规则订阅](#规则订阅)
- [维护与自动更新](#维护与自动更新)
- [安全与脱敏](#安全与脱敏)

## 可用资源

### 脱敏配置模板

| 客户端 | 配置文件 | 订阅配置位置 | 单节点配置位置 |
| --- | --- | --- | --- |
| Mihomo | [mihomo_allen.yaml](Configs/tool_config/mihomo_allen.yaml) · [Raw](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/mihomo_allen.yaml) | `proxy-providers` | `proxies` |
| Surge for Mac | [surge_mac_allen.conf](Configs/tool_config/surge_mac_allen.conf) · [Raw](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/surge_mac_allen.conf) | `[Proxy Group]` 中的 `policy-path` | 按需添加 `[Proxy]` |
| Surge for iPhone | [surge_iphone_allen.conf](Configs/tool_config/surge_iphone_allen.conf) · [Raw](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/surge_iphone_allen.conf) | `[Proxy Group]` 中的 `policy-path` | 按需添加 `[Proxy]` |
| Quantumult X | [quantumultx_allen.conf](Configs/tool_config/quantumultx_allen.conf) · [Raw](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/quantumultx_allen.conf) | `[server_remote]` | `[server_local]` |
| Loon | [loon_allen.lcf](Configs/tool_config/loon_allen.lcf) · [Raw](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/loon_allen.lcf) | `[Remote Proxy]` | 按需添加 `[Proxy]` |

### 规则类型

| 规则 | 用途 | 模板默认策略 |
| --- | --- | --- |
| AI 服务 | OpenAI、Claude、Gemini 等 AI 服务 | `OpenAI` 或自定义 AI 策略 |
| 公益 AI | 指定公益 AI 站点 | 直连 |
| 个人域名 | 个人维护的域名 | 直连 |
| PT 站点 | 经确认的 PT 站点域名 | 直连 |
| SKK CDN | CDN 与静态资源域名 | `CDN` |
| SKK Download | 下载域名规则 | 仅自动维护，五份模板当前未启用 |

## 快速开始

### 1. 选择并下载配置

从上方表格选择对应客户端，打开 `Raw` 链接后下载为本地文件。建议保留一份未修改的公开模板，并单独创建私人配置副本。

不要直接把公开 Raw 地址长期作为远程配置订阅，因为模板中的节点地址、密码和证书都是占位内容。

### 2. 替换私人信息

在私人副本中处理以下占位内容：

| 占位内容 | 处理方式 |
| --- | --- |
| `https://example.com/...` | 替换为自己的节点订阅 URL |
| `CHANGE_ME` | 设置控制器口令、UUID、密码或其他密钥 |
| `Configure local proxy nodes privately.` | 按客户端语法添加单节点；不需要时保留注释即可 |
| `Configure MITM certificate and passphrase locally.` | 在设备本地生成或导入 MITM 证书和口令 |

默认只启用第一份订阅 `Allen合集订阅`，其他订阅保留为禁用状态。替换订阅 URL 时不要随意修改订阅名称，否则地区策略组可能无法读取节点。

### 3. 导入客户端

1. 将修改后的私人配置导入对应客户端。
2. 更新节点订阅、远程规则和插件资源。
3. 检查 `香港优选`、`日本优选`、`新加坡优选`、`美国优选` 是否能读取节点。
4. 在 `Proxy` 和 `Final` 中选择需要的默认出口。
5. 确认网页访问、DNS、流媒体和直连站点工作正常后，再启用 MITM、脚本或插件。

不同客户端版本的导入按钮名称可能略有差异，但配置区段和占位字段保持一致。

### 4. 首次使用检查

- 节点列表为空：检查订阅是否启用、URL 是否有效，以及节点名称能否匹配地区筛选正则。
- 规则提示策略不存在：确认规则引用的策略名在策略组中已经定义，名称和大小写必须一致。
- MITM 或重写失败：确认系统已经安装并信任本地证书，且客户端相关开关已启用。
- YAML 无法加载：检查 Mihomo 缩进，不要使用 Tab，也不要破坏锚点和列表层级。
- 订阅更新失败：先确认网络出口和订阅有效性，不要通过全局关闭证书校验规避证书问题。

## 客户端配置教程

### Mihomo

1. 打开 `Configs/tool_config/mihomo_allen.yaml`。
2. 在 `proxy-providers` 中替换启用订阅的 `url`。
3. 将 `secret: CHANGE_ME` 改为强口令；如不需要远程控制，也应限制控制接口的访问范围。
4. 单节点写入 `proxies`，订阅节点由 `proxy-providers` 提供。
5. 加载配置后更新 Provider，并检查地区组是否获得节点。

```yaml
proxy-providers:
  Allen合集订阅:
    url: "https://example.com/your-private-subscription.yaml"
    type: http
    interval: 46400
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
    proxy: 直连

secret: CHANGE_ME
```

`proxy` 只表示下载订阅时使用的出口，不代表订阅内节点流量全部直连。模板默认校验节点 TLS 证书。

### Surge for Mac / iPhone

1. 在 `[Proxy Group]` 找到 `Allen合集订阅`。
2. 只替换 `policy-path=` 后面的 URL，保留策略组名称和其他参数。
3. 需要启用备用订阅时，替换对应 URL 后删除该行开头的 `#`。
4. 如需手写节点，添加 `[Proxy]` 区段并使用 Surge 节点语法。
5. MITM 证书必须在设备本地配置，不要使用公开模板中的占位注释代替证书。

```ini
[Proxy Group]
Allen合集订阅 = select, policy-path=https://example.com/your-private-subscription.conf, update-interval=86400, include-all-proxies=0
```

地区组通过 `include-other-group=Allen合集订阅` 读取节点。若重命名订阅组，需要同步修改所有 `include-other-group` 引用。

Surge Mac 模板保留 qB 下载器来源 IP 直连规则；Surge iPhone 不包含该类规则，避免客户端兼容问题。

### Quantumult X

1. 在 `[server_remote]` 中替换订阅 URL，并通过 `enabled=true/false` 控制启停。
2. 原生 Quantumult X 订阅使用 `opt-parser=false`；只有需要转换的非原生订阅才设置 `opt-parser=true`。
3. 单节点直接添加到保留的 `[server_local]`。
4. `[filter_remote]` 中的 `force-policy` 必须对应 `[policy]` 中存在的策略名。
5. 在 `[mitm]` 中配置本地生成的证书和口令。

```ini
[server_remote]
https://example.com/your-private-subscription.conf, tag=Allen合集订阅, update-interval=172800, opt-parser=false, enabled=true

[server_local]
# 在这里按 Quantumult X 节点语法逐行添加单节点
```

### Loon

1. 在 `[Remote Proxy]` 中替换等号后的订阅 URL。
2. `enabled=true` 表示启用，`enabled=false` 表示仅保留配置。
3. 保持 `skip-cert-verify=false`，除非已经明确确认特定订阅的证书兼容问题。
4. 如需手写单节点，可在 `[Remote Proxy]` 前添加 `[Proxy]` 区段。
5. 地区节点为空时，检查 `[Remote Filter]` 的正则和订阅节点名称。

```ini
[Remote Proxy]
Allen合集订阅 = https://example.com/your-private-subscription.conf,udp=true,skip-cert-verify=false,enabled=true
```

Loon 的远程规则位于 `[Remote Rule]`，插件位于 `[Plugin]`。启用需要 HTTPS 解密的插件前，必须先正确配置 `[Mitm]`。

## 配置与策略说明

### 策略组顺序

地区相关策略在五份模板中统一按以下顺序排列：

```text
香港优选 → 日本优选 → 新加坡优选 → 美国优选
香港节点 → 台湾节点 → 日本节点 → 新加坡节点 → 美国节点
韩国节点 → 英国节点 → 其他节点组
```

- `优选`：自动测速并选择地区内延迟较低的节点。
- `节点`：手动选择指定地区节点；个别客户端中的台湾、韩国组可能使用自动测速。
- `Proxy`：通用代理入口。
- `Final`：未匹配流量的最终出口。
- `直连策略`、`DIRECT` 或 `direct`：不同客户端中的直连策略名称。

### 业务策略

模板包含 Google、OpenAI、YouTube、Telegram、Netflix、Emby、Disney+、GitHub、PayPal、Spotify、Microsoft、游戏平台、Apple、TikTok、测速、CDN、OneDrive 等独立策略组。修改某类业务的出口时，优先调整对应策略组，不要直接修改远程规则内容。

`CDN` 作为独立策略组保留，便于处理 Cloudflare 和 SKK CDN 规则。`Download` 规则仍由 GitHub Actions 自动生成，但当前模板不启用 Download 策略组，以避免国外下载域名被过度分流。

### 本地规则优先级

所有客户端都按从上到下首次匹配生效。本地精确规则位于远程大类规则之前，最终规则必须位于末尾。

Surge Mac 和 Mihomo 支持 qB 下载器来源 IP 直连保护。使用时应把模板中的私有网段地址改成自己的下载器地址，并保持这些规则位于规则列表最前。Quantumult X、Loon 和 Surge iPhone 不包含这类来源 IP 规则。

## 规则订阅

### 订阅地址表

| 规则 | Mihomo | Surge | Quantumult X | Loon |
| --- | --- | --- | --- | --- |
| AI 服务 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/AI/ai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/AI/ai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/AI/ai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/AI/ai.list) |
| 公益 AI | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/AI/gongyiai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/AI/gongyiai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/AI/gongyiai.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/AI/gongyiai.list) |
| 个人域名 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Personal/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Personal/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Personal/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Personal/Domain.list) |
| PT 站点 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/PT/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/PT/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/PT/Domain.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/PT/Domain.list) |
| SKK CDN | 使用 SKK 原生格式 | 使用 SKK 原生格式 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/SKK/CDN.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/SKK/CDN.list) |
| SKK Download | 使用 SKK 原生格式 | 使用 SKK 原生格式 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/SKK/Download.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/SKK/Download.list) |

PT 规则当前包含 36 个经确认的站点域名。书签中明确排除的站点和 PT 工具链接不在该规则集中。

### 单独添加规则订阅

以下示例使用 PT 规则并默认直连。策略名称可以替换，但必须确保对应策略已经存在。

#### Mihomo

```yaml
rule-providers:
  pt_domain:
    type: http
    behavior: classical
    format: text
    url: https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/PT/Domain.list
    path: ./ruleset/PT-Domain.list
    interval: 86400

rules:
  - RULE-SET,pt_domain,DIRECT
```

#### Surge

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/PT/Domain.list,DIRECT
```

#### Quantumult X

```ini
[filter_remote]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/PT/Domain.list, tag=PT站点, force-policy=direct, update-interval=86400, opt-parser=false, enabled=true
```

#### Loon

```ini
[Remote Rule]
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/PT/Domain.list, policy=DIRECT, tag=PT站点, enabled=true
```

### 兼容地址

以下旧地址继续由同一个生成器维护：

- [Rules/AI/ai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/ai.list)
- [Rules/AI/gongyiai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/gongyiai.list)

兼容文件使用 `DOMAIN-SUFFIX,<domain>` 格式，可用于 Mihomo classical、Surge RULE-SET 和 Loon。Quantumult X 应使用专属目录中的规则。

## 维护与自动更新

### 手工规则维护

域名只在 `Rules/Source/` 中维护一次。各客户端目录中的生成文件不要直接编辑。

```bash
python3 tools/generate_rules.py
python3 tools/generate_rules.py --check
python3 -m unittest discover -s tests -v
```

更新规则时：

1. 修改 `Rules/Source/` 中对应的源文件。
2. 运行 `python3 tools/generate_rules.py` 生成各客户端规则。
3. 运行检查和测试。
4. 将源文件与全部生成结果放在同一个提交中。

`.github/workflows/validate-rules.yml` 会在 Push 和 Pull Request 时运行测试，并检查生成文件是否最新。

### SKK 自动更新

`.github/workflows/update-skk-rules.yml` 每天北京时间 04:17 自动获取 SKK 的 `domainset` 与 `non_ip` 规则，校验来源和最低条目数后转换。也可以从 GitHub Actions 手动运行 `workflow_dispatch`。

自动化只会提交以下四个公开文件，不会修改 `Configs/`：

- `Rules/QuantumultX/SKK/CDN.list`
- `Rules/QuantumultX/SKK/Download.list`
- `Rules/Loon/SKK/CDN.list`
- `Rules/Loon/SKK/Download.list`

SKK 转换产物继承 `AGPL-3.0-only` 许可证，来源和许可证范围见 [Rules/SKK/README.md](Rules/SKK/README.md)。

### 生成脱敏配置

公开模板由 `tools/sanitize_tool_configs.py` 从本地私人配置生成。必须显式指定私人配置目录：

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir "<PRIVATE_CONFIG_DIR>" \
  --output-dir Configs/tool_config
```

生成器会替换节点订阅、控制器密钥、UUID、节点认证、P12、证书和私钥，并在写入前验证公开输出。脚本日志只显示公开文件名，不输出私人源值。

## 目录结构

```text
Configs/
└── tool_config/             # 五份公开脱敏配置模板
Rules/
├── Source/                  # AI、个人域名和 PT 的唯一手工维护入口
├── Mihomo/                  # Mihomo 规则
├── Surge/                   # Surge 规则
├── QuantumultX/             # Quantumult X 规则及 SKK 转换结果
├── Loon/                    # Loon 规则及 SKK 转换结果
├── AI/                      # 旧订阅地址兼容层
└── SKK/                     # SKK 来源与许可证说明
tools/
├── generate_rules.py        # 生成跨客户端规则
├── sanitize_tool_configs.py # 生成脱敏配置
└── update_skk_rules.py      # 转换 SKK 规则
tests/                        # 生成、脱敏和自动更新测试
```

## 安全与脱敏

- 只在私人副本中保存真实订阅 URL、节点密码、UUID、控制器口令和证书。
- 不要把机场订阅、MITM 证书、私钥或带 Token 的 URL 提交到 GitHub。
- `skip-cert-verify=false` 和 `skip-server-cert-verify=false` 表示保持证书校验，建议维持默认值。
- 配置引用多个第三方规则、图标和插件；启用前应自行确认来源、更新状态和适用范围。
- 修改规则后先进行小范围验证。过宽的 `DOMAIN-KEYWORD` 规则可能误匹配无关域名。

## 免责声明

本仓库用于个人配置维护与技术研究。不同客户端版本、网络环境和订阅格式可能存在差异，使用者应在导入前检查配置，并自行承担第三方规则、插件和脚本带来的兼容性及安全风险。
