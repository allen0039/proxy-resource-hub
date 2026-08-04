# 将自定义规则订阅接入客户端配置：设计

## 目标

把已发布的个人规则订阅直接接入五份客户端配置，使 Mihomo、Surge Mac、Surge iPhone、Quantumult X 与 Loon 下载或更新配置后都会拉取同一份 GitHub 规则。后续只维护 `Rules/Source/Custom/allenrules.list`，生成器和 GitHub Actions 负责更新各客户端的订阅文件。

## 范围与边界

- 修改五份私有原始配置，并用 `tools/sanitize_tool_configs.py` 重建仓库中的五份公开脱敏模板。
- 私有原始配置只在父工作目录保存，绝不纳入 Git、提交或推送。
- 从五份本地配置中删除已迁移到远程源的 52 条域名规则；三条 `SRC-IP-CIDR` 下载器直连规则保持本地且处于最高优先级。
- 删除本地 `DOMAIN-SUFFIX,hdhive.online,香港节点`：它不在远程源中，且会覆盖远程的 `DOMAIN-KEYWORD,hdhive,美国节点`。
- `DOMAIN-SUFFIX,montbell.com,香港节点` 不在远程源中，继续作为本地自定义规则保留。其他未迁移的 Apple、GitHub、AI、YouTube、Google、REJECT 等规则也保持本地。

## 订阅矩阵

每个客户端接入九条订阅，全部使用 `https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/` 作为固定基址：

| 订阅 | 路径模式 | 最终策略 |
| --- | --- | --- |
| 自定义直连 | `Rules/<Client>/Custom/direct.list` | 内置 `DIRECT` / `direct` |
| 香港节点 | `Rules/<Client>/Regional/hk.list` | `香港节点` |
| 香港优选 | `Rules/<Client>/Regional/hk-auto.list` | `香港优选` |
| 美国节点 | `Rules/<Client>/Regional/us.list` | `美国节点` |
| 美国优选 | `Rules/<Client>/Regional/us-auto.list` | `美国优选` |
| 日本节点 | `Rules/<Client>/Regional/jp.list` | `日本节点` |
| 日本优选 | `Rules/<Client>/Regional/jp-auto.list` | `日本优选` |
| 新加坡节点 | `Rules/<Client>/Regional/sg.list` | `新加坡节点` |
| 新加坡优选 | `Rules/<Client>/Regional/sg-auto.list` | `新加坡优选` |

当前优选列表可以为空；预先接入可使未来把源规则改为“优选”策略时无需再改五份客户端配置。

## 各客户端实现

### Mihomo

在 `rule-providers` 添加九个 `type: http`、`behavior: classical`、`format: text`、`interval: 86400` 的 provider。`rules` 在现有 `SRC-IP-CIDR` 规则之后，通过九个 `RULE-SET` 将 provider 分别绑定到策略表中的最终策略。

### Surge（Mac 与 iPhone）

在 `[Rule]` 中将九条 `RULE-SET` 放在现有本地例外和宽泛第三方订阅之前；直连项使用 `DIRECT`，地区项使用对应的中文策略组。Mac 的三条来源 IP 直连规则仍位于该区块之前。

### Quantumult X

在 `[filter_remote]` 顶部添加九条订阅，均设为 `update-interval=86400, opt-parser=false, enabled=true`。直连订阅使用 `force-policy=direct`，地区订阅使用对应的中文策略组。同步删除已迁移规则的 `[filter_local]` 条目，避免本地规则先匹配而掩盖远程订阅。

### Loon

在 `[Remote Rule]` 顶部添加九条订阅，均启用且每条指定 `policy=`。直连项使用 `DIRECT`，地区项使用对应策略组。同步删除已迁移规则的本地 `[Rule]` 条目。

## 优先级

规则从上到下首次匹配。每个客户端都遵循：

1. Mac/Mihomo 中已有的来源 IP 下载器直连规则；
2. 九条自定义远程订阅；
3. 仍需本地维护的精确例外规则；
4. 既有宽泛第三方远程规则与兜底规则。

因此迁移的规则在外部大规则之前生效，且不会和本地副本重复。

## 文档与验证

更新 `Configs/tool_config/README.md`，说明公开模板已内置九条个人规则订阅，并仍提醒用户不要把私人订阅或密钥提交到仓库。

新增或扩展回归测试，验证：

- 五份脱敏模板各自接入九条正确的 raw GitHub URL 与策略；
- 自定义订阅处于广泛第三方规则之前；
- 迁移的 52 条规则与 `hdhive.online` 不再以本地规则形式存在；
- `montbell.com` 及其余未迁移本地规则仍保留；
- 脱敏脚本可从私有原始配置重建模板，现有结构校验继续通过。

实施完成后运行规则生成器检查、配置脱敏、全部测试和 YAML/配置结构检查；确认只提交 `proxy-resource-hub` 内的公开模板、测试与文档，不包含任何私有原始配置。
