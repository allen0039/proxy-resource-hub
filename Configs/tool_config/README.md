# Allen 的脱敏工具配置

本目录提供五种代理客户端的公开配置模板：

- `mihomo_allen.yaml`：Mihomo
- `surge_mac_allen.conf`：Surge for Mac
- `surge_iphone_allen.conf`：Surge for iPhone
- `quantumultx_allen.conf`：Quantumult X
- `loon_allen.lcf`：Loon

这些文件保留策略组、公开规则订阅、本地域名规则、注释及客户端结构；
`gongyiai`、个人 `Domain` 和 `PT/Domain` 远程规则继续使用直连策略。

## 使用前必须配置

这些文件是脱敏模板。请只在自己的私有副本中替换：

- `https://example.com/...`：节点订阅地址；
- `CHANGE_ME`：控制器口令、UUID、密码或密钥；
- 本地节点占位注释：按客户端语法添加自己的节点；
- MITM 占位注释：在设备本地重新生成或导入证书及口令。

不要把填写完成的私人副本提交回 GitHub。

## 维护方式

公开模板由 `tools/sanitize_tool_configs.py` 从本地私人配置生成。脚本只输出脱敏后的
五个文件，并在写入前检查订阅、节点认证、UUID、控制器密钥、P12、证书和私钥等
敏感类别。公开规则、插件、脚本和 rule-provider 地址不会被替换。

生成时必须显式指定私人配置所在目录：

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir "<PRIVATE_CONFIG_DIR>" \
  --output-dir Configs/tool_config
```

脚本日志只显示公开输出文件名，不显示私人源值。
