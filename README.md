# Mihomo 配置规则

这是 Allen 自用的 Mihomo / Clash Meta 配置模板，包含代理组、DNS、TUN、规则匹配和远程规则集供应器。

## 文件说明

- `mihomo_byallen注释版.yaml`：主配置文件，可直接作为 Mihomo 配置使用或在此基础上维护。
- `Rules/AI/ai.list`：自维护 AI 服务规则集，主配置通过 `RULE-SET,ai,🤖 ChatGPT` 引用。
- `.gitignore`：避免把本地临时文件、缓存和私密配置误传到仓库。
- `.gitattributes`：固定文本文件换行，减少不同系统编辑时产生的无关变更。

## 使用方式

1. 克隆或下载本仓库。
2. 打开 `mihomo_byallen注释版.yaml`。
3. 将 `proxy-providers` 中的订阅地址替换为你自己的地址。
4. 上传到 GitHub 后，把 `rule-providers.ai.url` 改成你的真实 Raw 地址。
5. 根据实际节点名称调整 `proxy-groups` 和 `rules`。
6. 在 Mihomo 客户端中导入该配置。

## AI 规则维护

国外 AI 服务域名统一放在 `Rules/AI/ai.list`。这个文件使用 Mihomo classical 规则格式，只写 `DOMAIN-SUFFIX`、`DOMAIN-KEYWORD` 等规则本身，不要在行尾追加策略组名。

主配置中的 `rule-providers.ai.url` 需要在上传 GitHub 后改成你的真实 Raw 地址，例如：

```text
https://raw.githubusercontent.com/allen0039/mihomo/main/Rules/AI/ai.list
```

配置文件中只需要保留这一条规则即可：

```yaml
- RULE-SET,ai,🤖 ChatGPT
```

## 维护建议

- 不要把真实订阅链接、Token、账号信息提交到公开仓库。
- 如果需要公开分享，建议把真实订阅地址替换为示例地址。
- 每次修改规则后，先在本地客户端加载确认无误，再提交到 GitHub。
- 规则顺序会影响匹配结果，越具体的规则应放在越靠前的位置。

## Raw 地址

上传到 GitHub 后，可以使用 Raw 地址订阅主配置。格式通常是：

```text
https://raw.githubusercontent.com/allen0039/mihomo/main/mihomo_byallen%E6%B3%A8%E9%87%8A%E7%89%88.yaml
```

如果仓库是私有仓库，Raw 地址不能直接被大多数客户端无登录访问。

## 免责声明

本仓库仅用于个人配置维护和规则学习。请遵守当地法律法规以及相关服务条款。