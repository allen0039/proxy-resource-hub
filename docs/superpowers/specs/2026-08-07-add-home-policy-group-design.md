# 增加家宽节点策略组：设计

## 目标

在五份公开脱敏客户端配置中增加统一的“家宽节点”策略组，并将它加入 AI 策略组；家宽节点只按节点名称筛选，不公开任何真实节点、订阅地址或凭据。

## 范围

- 修改：
  - `Configs/tool_config/mihomo_allen.yaml`
  - `Configs/tool_config/surge_mac_allen.conf`
  - `Configs/tool_config/surge_iphone_allen.conf`
  - `Configs/tool_config/quantumultx_allen.conf`
  - `Configs/tool_config/loon_allen.lcf`
- 更新 `tests/test_sanitized_tool_configs.py`，验证五份公开模板均存在活动的家宽策略组，并且 AI 组可选择它。
- 必要时更新 `Configs/tool_config/README.md`，说明家宽组的匹配方式和使用范围。
- 使用已公开的 `icons/home.png` 作为策略组图标，不添加任何私有节点数据。

## 设计

### 统一筛选规则

所有客户端使用不区分大小写的节点名称匹配：

```regex
(?i)(家用|家庭|家宽|\bISP\b)
```

这会匹配中文家宽标签以及独立的英文 ISP 标签，同时避免把普通单词中的 `isp` 误匹配。

### 客户端映射

- Mihomo：增加 `name: 家宽节点` 的 `select` 组，使用 `include-all: true` 和 `filter`；将 `家宽节点` 加入 `AI` 的 `proxies`。
- Surge：在 Mac 与 iPhone 的 `[Proxy Group]` 增加 `家宽节点 = select`，使用 `include-other-group="拼好鸡,自建"` 和 `policy-regex-filter`；将 `家宽节点` 加入 `AI` 组。
- Quantumult X：增加 `static=家宽节点`，使用 `server-tag-regex`；将 `家宽节点` 加入 `static=AI`。
- Loon：增加 `家宽节点 = select`，使用 `include-other-group="拼好鸡,自建"` 和 `policy-regex-filter`；将 `家宽节点` 加入 `AI`。

家宽组是手动选择入口，不自动接管普通流量，也不加入其他业务策略组。

## 脱敏边界

不在公开仓库中写入任何代理服务器、节点密码、订阅 URL、UUID、证书、私钥或本地源 IP。策略组仅引用公开模板中已有的脱敏订阅组名称和节点名称筛选条件。

## 验证

- 测试五份配置的家宽组定义均为活动配置，且匹配表达式包含 `家用`、`家庭`、`家宽` 和 `ISP`。
- 测试每份配置的 AI 组均包含 `家宽节点`，且没有把它意外加入其他业务组。
- 运行完整测试套件与脱敏配置验证。
- 检查 GitHub 推送前后提交哈希一致。
