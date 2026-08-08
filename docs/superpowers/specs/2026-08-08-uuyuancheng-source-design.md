# UU Remote 进程规则单一源维护：设计

## 目标

将 UU Remote 的进程规则纳入统一源文件维护，并由现有规则生成器自动生成 Surge 与 Loon 的客户端规则文件，避免直接编辑生成结果。

## 范围

- 新增唯一维护源：
  - `Rules/Source/allenrules/uuyuancheng.list`
- 生成并维护：
  - `Rules/Surge/Custom/uuyuancheng.list`
  - `Rules/Loon/Custom/uuyuancheng.list`
- 修改 `tools/generate_rules.py`，增加仅面向 Surge/Loon 的进程规则生成规格。
- 更新 `tests/test_generate_rules.py`，验证源文件解析、两份输出和输出格式。
- 更新 `README.md`，说明 UU Remote 的源文件和生成文件关系。
- 保留现有 Surge Mac 与 Loon Mac 配置中的远程规则引用，不新增 Mihomo、Quantumult X 或其他客户端输出。

## 源文件格式

源文件每行使用两个逗号分隔字段：

```text
PROCESS-NAME,uuremote
PROCESS-NAME,uuremoteserver
PROCESS-NAME,uuremoteservice
PROCESS-NAME,uuremotedaemon
```

允许空行和以 `#` 开头的注释。生成器必须拒绝空字段、未知规则类型、额外字段和重复的 `PROCESS-NAME` 值。

## 生成行为

生成器新增独立的进程规则规格，不复用域名源的五客户端循环：

- 读取 `Rules/Source/allenrules/uuyuancheng.list`。
- Surge 与 Loon 输出保持 `PROCESS-NAME,<process>` 格式，并写入标准生成头：
  `# Generated from Rules/Source/allenrules/uuyuancheng.list by tools/generate_rules.py. Do not edit.`
- 不生成 Mihomo、Quantumult X 或根目录兼容文件。
- `python3 tools/generate_rules.py --check` 必须检测两份输出是否过期。
- GitHub Actions 继续通过现有生成器流程自动更新输出。

## 配置与文档

现有配置引用保持不变：

- Surge Mac 使用 `Rules/Surge/Custom/uuyuancheng.list` 并指定 `DIRECT`。
- Loon Mac 保持当前默认关闭的注释示例，并指向 `Rules/Loon/Custom/uuyuancheng.list`。
- 不将规则加入其他客户端配置或业务策略组。

README 应明确说明：只在 `Rules/Source/allenrules/uuyuancheng.list` 维护，Surge/Loon 文件为自动生成结果，生成文件不可直接编辑；该规则只适用于 Mac。

## 验证

- 测试源文件包含四个 UU Remote 进程且无重复。
- 测试两份输出存在、头部正确、规则顺序与源文件一致。
- 测试输出映射不包含 Mihomo/QX 的 UU 文件。
- 运行完整测试、生成器检查和 `git diff --check`。
