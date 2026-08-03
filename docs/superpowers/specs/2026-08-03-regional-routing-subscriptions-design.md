# Regional Routing 规则订阅设计

## 目标

将用户指定的地区分流规则从五份本地客户端配置中抽象为一个公开、无敏感信息的唯一维护源，并自动生成 Mihomo、Surge、Quantumult X 和 Loon 可订阅的规则文件。

本功能只发布用户明确提供的地区分流规则。本阶段不修改任何本地客户端配置，不迁移其他本地 `DIRECT`、`AI`、`REJECT` 或业务规则，也不发布节点订阅 URL、Token、证书、密钥或具体机场节点。

规则的第三列引用稳定的逻辑策略组，而不是具体代理节点。策略组包括四个地区的手动节点组和优选节点组。

## 唯一维护源

源文件固定为：

```text
Rules/Source/Regional/routing.list
```

每条有效规则使用三字段、逗号分隔格式：

```text
<TYPE>,<VALUE>,<POLICY>
```

支持空行和以 `#` 开头的整行注释。字段前后空白由解析器去除，但生成结果使用规范化格式。源值统一使用小写。

本阶段只支持以下规则类型：

- `DOMAIN-SUFFIX`
- `DOMAIN-KEYWORD`

只允许以下策略组：

- `香港节点`
- `香港优选`
- `美国节点`
- `美国优选`
- `日本节点`
- `日本优选`
- `新加坡节点`
- `新加坡优选`

## 初始规则

源文件写入以下 34 条规则：

```text
DOMAIN-SUFFIX,hytron.io,香港节点
DOMAIN-SUFFIX,linux.do,美国节点
DOMAIN-KEYWORD,uspatriottactical,美国节点
DOMAIN-KEYWORD,hdhive,美国节点
DOMAIN-SUFFIX,rundongex.com,美国节点
DOMAIN-SUFFIX,servercontrolpanel.de,美国节点
DOMAIN-SUFFIX,mgboard.net,美国节点
DOMAIN-KEYWORD,sehuatang,美国节点
DOMAIN-KEYWORD,greasyfork,美国节点
DOMAIN-KEYWORD,qichiyu,美国节点
DOMAIN-SUFFIX,mjji.de,美国节点
DOMAIN-KEYWORD,hd-torrents,美国节点
DOMAIN-SUFFIX,embyapp.top,美国节点
DOMAIN-SUFFIX,vps.town,美国节点
DOMAIN-SUFFIX,2fa.fun,美国节点
DOMAIN-SUFFIX,macwk.cn,美国节点
DOMAIN-SUFFIX,appstorrent.ru,美国节点
DOMAIN-KEYWORD,kejilion,香港节点
DOMAIN-SUFFIX,nfbyte.com,香港节点
DOMAIN-KEYWORD,onitsukatiger,日本节点
DOMAIN-SUFFIX,montbell.com,香港节点
DOMAIN-SUFFIX,compliance.chippercash.com,美国节点
DOMAIN-KEYWORD,dmm,日本节点
DOMAIN-KEYWORD,javrate,日本节点
DOMAIN-KEYWORD,jav321,日本节点
DOMAIN-KEYWORD,freejavbt,日本节点
DOMAIN-KEYWORD,javbus,日本节点
DOMAIN-KEYWORD,mgstage,日本节点
DOMAIN-KEYWORD,mmtv,日本节点
DOMAIN-KEYWORD,javdb,新加坡节点
DOMAIN-KEYWORD,javlibrary,新加坡节点
DOMAIN-KEYWORD,avbase,新加坡节点
DOMAIN-KEYWORD,missav,美国节点
DOMAIN-KEYWORD,ftvgirls,美国节点
```

用户提供的 `DOMAIN-SUFFIX,hdhive.online,香港节点` 不写入源文件。它与 `DOMAIN-KEYWORD,hdhive,美国节点` 存在覆盖冲突；用户已明确选择保留后者并统一走美国节点。

## 策略文件映射

生成器使用稳定的英文文件名，避免 URL 中出现策略组中文字符：

| 策略组 | 文件名 |
| --- | --- |
| 香港节点 | `hk.list` |
| 香港优选 | `hk-auto.list` |
| 美国节点 | `us.list` |
| 美国优选 | `us-auto.list` |
| 日本节点 | `jp.list` |
| 日本优选 | `jp-auto.list` |
| 新加坡节点 | `sg.list` |
| 新加坡优选 | `sg-auto.list` |

四种客户端各生成八个文件，共 32 个稳定产物：

```text
Rules/Mihomo/Regional/<file>
Rules/Surge/Regional/<file>
Rules/QuantumultX/Regional/<file>
Rules/Loon/Regional/<file>
```

即使某个策略组暂时没有规则，生成器仍创建只包含生成说明注释的文件。这样对应 Raw URL 始终存在，后续添加规则时无需修改订阅地址。

## 客户端格式

Mihomo、Surge 和 Loon 使用不带策略列的经典规则格式：

```text
DOMAIN-SUFFIX,hytron.io
DOMAIN-KEYWORD,kejilion
```

Quantumult X 使用原生格式，并写入可被客户端资源配置覆盖的占位策略 `proxy`：

```text
host-suffix, hytron.io, proxy
host-keyword, kejilion, proxy
```

策略不嵌入前三种客户端的生成文件中。客户端接入时分别通过 Mihomo/Surge 的 `RULE-SET`、Quantumult X 的 `force-policy`、Loon 的 `policy` 将每个远程资源绑定到文件名对应的逻辑策略组。

本阶段只生成并发布规则资源，不向五份本地配置添加这些引用。

## 解析、校验与冲突处理

生成器在写入任何产物前完成全部校验：

1. 每条有效行必须恰好包含三个非空字段。
2. 规则类型必须属于本阶段的类型白名单。
3. 策略组必须属于八个策略组白名单。
4. `DOMAIN-SUFFIX` 的值必须是合法、小写、不含协议、路径和端口的域名。
5. `DOMAIN-KEYWORD` 的值必须为小写、不得包含逗号或空白。
6. 同一个 `TYPE + VALUE` 只能出现一次；无论策略是否相同，重复均报错。
7. 当某个 `DOMAIN-KEYWORD` 的值包含在任一 `DOMAIN-SUFFIX` 值中时，视为覆盖重叠并报错。用户必须明确只保留一条，避免跨策略文件的匹配顺序产生歧义。
8. 只有全部源规则通过校验后才构建输出；失败时不留下部分更新的生成文件。

每个生成文件内部保持对应规则在源文件中的相对顺序。由于生成器禁止跨类型覆盖冲突，不依赖不同策略订阅在客户端配置中的排列顺序来解决冲突。

## 自动生成与发布

现有 `tools/generate_rules.py` 扩展为解析 Regional 三字段源文件，并将规则按策略组分桶、按客户端渲染。

现有 `.github/workflows/sync-generated-rules.yml` 继续作为发布入口：

1. `main` 分支收到源规则提交。
2. GitHub Actions 运行生成器。
3. 运行完整测试和生成漂移检查。
4. 全部通过后，由 `github-actions[bot]` 提交变化的 `Rules/` 产物。

README 增加 Regional 规则说明、八个策略的四端 Raw 订阅地址，以及四种客户端的接入示例。文档必须明确本次只发布资源，用户本地配置尚未自动引用它们。

## 测试与验收

自动化测试覆盖：

- 唯一源文件包含预期的 34 条规则，且不包含已移除的 `hdhive.online` 香港规则。
- 32 个预期产物全部存在于生成映射中，包括四个客户端当前为空的 16 个优选策略产物。
- 各策略文件只包含属于该策略的规则。
- Mihomo、Surge、Loon 的 `DOMAIN-SUFFIX` 和 `DOMAIN-KEYWORD` 输出格式正确。
- Quantumult X 正确转换为 `host-suffix` 和 `host-keyword`。
- 非法类型、非法策略、非法域名、字段缺失、完全重复、跨策略重复和关键词/后缀覆盖冲突均被拒绝。
- 生成失败不会写入部分产物。
- `python3 tools/generate_rules.py --check` 成功。
- `python3 -m unittest discover -s tests -v` 成功。
- Git 差异不包含五份本地客户端配置或任何私人订阅材料。

## 非目标

- 不修改 `Rules/Source/Personal/Domain.txt` 或既有 Personal 订阅。
- 不迁移用户未提供的其他本地规则。
- 不直接修改五份本地客户端配置。
- 不维护或发布具体代理节点。
- 不在本阶段支持 IP、CIDR、进程、URL 正则或更多规则类型。
- 不改变既有 AI、PT、购物、SKK 或 Personal 规则的生成行为。
