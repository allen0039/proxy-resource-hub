# 新手配置使用指南

这里提供 Mihomo、Surge、Quantumult X 和 Loon 的五份完整配置模板。

> [!IMPORTANT]
> 这些是公开脱敏模板，里面没有真实节点。必须先下载到本地，把 `https://example.com/...` 替换成自己的机场订阅，才能正常使用。

## 只看这四步

1. 在下面表格中找到自己的客户端。
2. 点击 `Raw 下载`，把配置保存到本地。
3. 搜索 `https://example.com/`，替换第一条已启用订阅的 URL。
4. 导入客户端，更新订阅和远程资源。

不要直接把本页或 Raw 地址当成远程配置订阅。公开模板需要填写私人信息，应该作为本地配置使用。

## 我该下载哪个文件

| 你使用的客户端 | 下载文件 | 格式 |
| --- | --- | --- |
| Mihomo、Clash Meta、OpenClash | [mihomo_allen.yaml](mihomo_allen.yaml) · [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/mihomo_allen.yaml) | YAML |
| Surge for Mac | [surge_mac_allen.conf](surge_mac_allen.conf) · [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/surge_mac_allen.conf) | Surge 配置 |
| Surge for iPhone | [surge_iphone_allen.conf](surge_iphone_allen.conf) · [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/surge_iphone_allen.conf) | Surge 配置 |
| Quantumult X | [quantumultx_allen.conf](quantumultx_allen.conf) · [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/quantumultx_allen.conf) | Quantumult X 配置 |
| Loon | [loon_allen.lcf](loon_allen.lcf) · [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/loon_allen.lcf) | Loon 配置 |

## 三分钟完成配置

### 第一步：下载并创建私人副本

打开对应的 `Raw 下载`，将文件保存到本地。建议保留一份未修改的原文件，再复制一份作为自己的私人配置。

私人配置中会包含机场订阅、节点密码和证书，不要上传到 GitHub、网盘公开链接或聊天群。

### 第二步：填写机场订阅

每份模板默认只启用 `Allen合集订阅`，其他订阅只是禁用备用项。先替换第一条即可。

| 客户端 | 搜索位置 | 需要修改的内容 |
| --- | --- | --- |
| Mihomo | `proxy-providers` | 替换 `Allen合集订阅` 下的 `url` |
| Surge | `[Proxy Group]` | 替换 `Allen合集订阅` 行中的 `policy-path` |
| Quantumult X | `[server_remote]` | 替换第一条 `enabled=true` 的 URL |
| Loon | `[Remote Proxy]` | 替换 `Allen合集订阅 =` 后面的 URL |

只替换 URL，不要随意修改 `Allen合集订阅` 这个名称。地区策略组依赖该名称读取节点。

### 第三步：处理密码和证书

- Mihomo：将 `secret: CHANGE_ME` 改成自己的强口令。
- 看到 `Configure local proxy nodes privately.`：这是单节点预留位置，不使用单节点可以不处理。
- 看到 `Configure MITM certificate and passphrase locally.`：证书已经被脱敏删除，需要在设备本地重新生成或导入。

如果只需要基础分流，可以先不启用 MITM。依赖 HTTPS 解密的重写、脚本或插件会暂时不可用，但普通规则分流不受影响。

### 第四步：导入并更新

1. 把修改后的私人配置导入客户端。
2. 更新节点订阅、远程规则和插件资源。
3. 打开 `香港优选`、`日本优选`、`新加坡优选`、`美国优选`，确认能够看到节点。
4. 在 `Proxy` 和 `Final` 中选择默认出口。
5. 先测试网页、DNS 和直连站点，再按需开启 MITM、重写、脚本或插件。

## 各客户端具体改法

### Mihomo

需要修改：

```yaml
proxy-providers:
  Allen合集订阅:
    url: "https://example.com/your-private-subscription.yaml"

secret: CHANGE_ME
```

操作要点：

1. 把 `url` 改成自己的订阅地址。
2. 把 `CHANGE_ME` 改成强口令。
3. 保持 YAML 缩进，不要使用 Tab。
4. 加载配置后，在面板中更新 Proxy Provider。

单节点写在 `proxies`，订阅节点由 `proxy-providers` 提供。模板中的 `proxy: 直连` 只表示使用直连下载订阅，不代表节点流量全部直连。

### Surge for Mac / iPhone

需要修改：

```ini
Allen合集订阅 = select, policy-path=https://example.com/your-private-subscription.conf, update-interval=86400
```

操作要点：

1. 只替换 `policy-path=` 后面的 URL。
2. 保留 `Allen合集订阅` 名称和后续参数。
3. 备用订阅行以 `#` 开头；替换 URL 并删除 `#` 后才会启用。
4. MITM 证书需要在 Surge 和系统中本地配置并信任。

Mac 和 iPhone 必须选择对应文件。Surge Mac 模板包含 qB 下载器来源 IP 直连保护；iPhone 版不包含这类规则。

### Quantumult X

需要修改：

```ini
[server_remote]
https://example.com/your-private-subscription.conf, tag=Allen合集订阅, update-interval=172800, opt-parser=false, enabled=true

[server_local]
# 需要单节点时写在这里
```

操作要点：

1. 替换 `[server_remote]` 第一条 URL。
2. 原生 Quantumult X 订阅使用 `opt-parser=false`。
3. 需要转换的非原生订阅才使用 `opt-parser=true`。
4. 单节点添加到保留的 `[server_local]`。
5. 导入后更新节点资源和分流资源。

### Loon

需要修改：

```ini
[Remote Proxy]
Allen合集订阅 = https://example.com/your-private-subscription.conf,udp=true,skip-cert-verify=false,enabled=true
```

操作要点：

1. 只替换等号后的订阅 URL，保留其他参数。
2. `enabled=true` 表示启用，`enabled=false` 表示保留但停用。
3. 保持 `skip-cert-verify=false`，不要为了省事关闭证书校验。
4. 如果地区组没有节点，检查订阅节点名称能否匹配 `[Remote Filter]`。
5. MITM 类插件需要先安装并信任本地证书。

## 这套配置包含什么

- 通用入口：`Proxy`、`Final`、直连策略。
- 地区优选：香港、日本、新加坡、美国自动测速。
- 地区节点：香港、台湾、日本、新加坡、美国、韩国、英国。
- 业务分流：Google、OpenAI、YouTube、Telegram、Netflix、Emby、GitHub、Microsoft、Apple、TikTok、测速、CDN 等。
- 默认直连：PT 站点、个人域名、公益 AI 和部分国内服务。
- 远程资源：AI、PT、个人域名、CDN、媒体、游戏平台和常用服务规则。

`Download` 规则仍在仓库中自动维护，但这五份模板没有启用 Download 策略组，避免国外下载域名被过度分流。

## 新手不要随便改这些内容

- 不要重命名 `Allen合集订阅`、`Proxy`、`Final` 和地区策略组。
- 不要打乱规则顺序，规则从上到下首次匹配生效。
- 不要随意修改地区筛选正则，否则可能出现节点串组或节点为空。
- 不要全局关闭证书校验。
- 不要在公开仓库提交真实订阅、Token、UUID、密码、P12、证书或私钥。

## 常见问题

| 问题 | 优先检查 |
| --- | --- |
| 导入后没有节点 | 订阅 URL 是否有效、订阅是否启用、是否更新了节点资源 |
| 地区策略组为空 | 节点名称是否包含香港、HK、日本、JP 等地区关键词 |
| 提示策略不存在 | 是否修改了策略组名称，规则中的策略名是否与配置一致 |
| Mihomo 提示 YAML 错误 | 缩进是否正确，是否误用 Tab，冒号后是否保留空格 |
| Quantumult X 订阅解析失败 | `opt-parser` 是否与订阅格式匹配 |
| MITM、重写或插件无效 | 是否生成、安装并信任证书，客户端开关是否开启 |
| 更新后配置被覆盖 | 不要直接远程订阅公开模板；下载新版后手工合并私人信息 |

## 配置更新方法

仓库有新版本时：

1. 下载新的脱敏模板。
2. 备份旧私人配置中的订阅 URL、密码、证书和单节点。
3. 将私人信息手工合并到新模板。
4. 重新导入并更新资源。

不要直接用新模板覆盖私人配置，否则自己的订阅和证书会丢失。

## 安全提醒

公开模板只保留策略组、规则、插件和配置结构。真实订阅、节点认证、UUID、控制器密钥、P12、证书和私钥都已删除或替换成占位符。

填写完成后的文件属于私人配置。不要截图公开订阅 URL，也不要把文件上传到公开 Issue、聊天记录或 GitHub 提交中。

需要了解规则订阅、自动更新和仓库维护方式，请返回[项目主 README](../../README.md)。
