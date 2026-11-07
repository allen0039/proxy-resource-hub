# Proxy Resource Hub

[![Sync generated rules](https://github.com/allen0039/proxy-resource-hub/actions/workflows/sync-generated-rules.yml/badge.svg)](https://github.com/allen0039/proxy-resource-hub/actions/workflows/sync-generated-rules.yml)

面向 Mihomo、Surge、Quantumult X、Loon 和 Egern 的公开脱敏配置与分流规则仓库。配置模板包含地区节点策略、AI、媒体、Apple、PT、个人域名、海淘和 CDN 等规则，并由 GitHub Actions 自动校验和生成。

> [!IMPORTANT]
> `Configs/tool_config/` 中的文件是公开模板，不包含真实订阅、节点密码或个人密钥。导入前请复制到本地私人文件，替换占位符；不要把填写后的私人配置提交到 GitHub。

## 配置文件

| 客户端 | 启用 Tailscale | 不启用 Tailscale | 说明 |
| --- | --- | --- | --- |
| Mihomo / Clash Meta / OpenClash | [mihomo_allen.yaml](Configs/tool_config/mihomo_allen.yaml) | [mihomo_allen_no-tailscale.yaml](Configs/tool_config/mihomo_allen_no-tailscale.yaml) | YAML；Android 可使用 FlClash、Clash Verge Rev 等客户端 |
| Surge for iPhone / iPad | [surge_iphone_allen.conf](Configs/tool_config/surge_iphone_allen.conf) | [surge_iphone_allen_no-tailscale.conf](Configs/tool_config/surge_iphone_allen_no-tailscale.conf) | 启用版在策略页提供 `Tailscale策略` |
| Surge for Mac | [surge_mac_allen.conf](Configs/tool_config/surge_mac_allen.conf) | — | 使用 Surge 原生 `Tailnet` |
| Quantumult X | [quantumultx_allen.conf](Configs/tool_config/quantumultx_allen.conf) | — | 不写入伪造 Tailscale 字段 |
| Loon | [loon_allen.lcf](Configs/tool_config/loon_allen.lcf) | — | 使用系统 Tailscale 或其他兼容方案 |
| Egern | [egern_byallen.yaml](Configs/tool_config/egern_byallen.yaml) | — | 使用系统 Tailscale 或其他兼容方案 |

每个文件均提供 [Raw 下载](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Configs/tool_config/)。Raw 地址用于下载模板，不建议直接作为远程配置长期使用。

## 快速开始

1. 下载对应客户端的模板，复制为私人副本。
2. 将第一个启用订阅中的 `获取到的订阅链接` 替换为自己的订阅 URL。保留订阅名称（默认是 `拼好鸡`），否则地区策略组可能无法读取节点。
3. Mihomo 将 `secret: CHANGE_ME` 改为强随机口令；Surge 的订阅地址位于 `[Proxy Group]` 的 `policy-path=`。
4. 导入客户端并更新节点、规则和远程资源。
5. 确认地区组和 `Final` 有可用节点后，再按需启用 MITM、脚本或插件。

### Mihomo Tailscale

启用版包含 `type: tailscale` 出口和独立的 `Tailscale策略` 组。首次使用前：

- 将 `auth-key: CHANGE_ME` 换成自己的短期或受限密钥；
- 按需修改 `hostname` 和 `state-dir`；
- 在客户端策略页选择 `Tailscale策略` 中的 Tailscale；
- `ts.net`、`100.64.0.0/10` 和家庭局域网规则会指向该策略组。

无 Tailscale 需求请直接使用 `mihomo_allen_no-tailscale.yaml`。Mihomo 安卓端对内置 Tailscale 出口的延迟测速支持取决于内核版本，测速失败不等于连接不可用，应通过实际访问 Tailscale 设备验证。

### Surge iPhone Tailscale

启用版包含 Surge 原生 `[Tailscale home-tailnet]` 段和 `Tailscale策略` 组。首次使用需在 Surge 的 Tailscale 策略编辑器完成交互登录，并在策略页选择 `Tailnet`。不需要 Tailscale 时使用 `surge_iphone_allen_no-tailscale.conf`。

Surge Mac 使用原生 `Tailnet` 配置；Quantumult X、Loon 和 Egern 模板不添加非原生 Tailscale 字段，避免导入后出现兼容性问题。

## 规则资源

规则按客户端格式生成，主要包括：

- AI 与 Google/Gemini；
- Apple、iCloud、Private Relay；
- YouTube、Telegram、Netflix、Spotify、TikTok、游戏和媒体；
- PT 站点、个人域名、海淘购物；
- CDN、下载、直连和地区规则；
- Egern 原生 YAML 规则及 Quantumult X/Loon 的 SKK 转换规则。

规则源位于 `Rules/Source/`，生成产物位于 `Rules/Mihomo/`、`Rules/Surge/`、`Rules/QuantumultX/`、`Rules/Loon/` 和 `Rules/Egern/`。普通规则使用公开远程 URL，配置模板会按客户端语法引用它们。

## 安全与脱敏

公开模板会将订阅 URL、控制器口令、UUID、节点认证、Tailscale `auth-key`、证书和私钥替换为占位内容。生成工具为 [`tools/sanitize_tool_configs.py`](tools/sanitize_tool_configs.py)，本地生成方式：

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir "<PRIVATE_CONFIG_DIR>" \
  --output-dir Configs/tool_config
```

提交前请检查：

- 没有真实订阅 URL、token、密码或证书；
- 没有设备私有 IP、主机名或 Tailscale 密钥；
- `CHANGE_ME` 和 `获取到的订阅链接` 仍为占位符；
- 配置语法和规则引用均通过测试。

## 自动化维护

GitHub Actions 会在推送和定时任务中生成规则、检查远程资源、验证配置结构，并在生成内容变化时提交公开规则。完整测试位于 `tests/`；本地运行：

```bash
python3 -m unittest discover -s tests -v
```

仓库只接受公开脱敏内容。私人订阅、真实节点、证书、密钥和本地设备规则应保留在仓库外。
