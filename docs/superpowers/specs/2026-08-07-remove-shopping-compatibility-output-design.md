# 移除海淘购物兼容订阅：设计

## 目标

停止发布根目录 `Rules/shop/shopping.list` 兼容订阅，只保留 Mihomo、Surge、Quantumult X 与 Loon 的客户端专属海淘购物规则。

## 范围

- 唯一维护入口保持为 `Rules/Source/shop/shopping.txt`。
- `tools/generate_rules.py` 不再把 shopping 规则生成到 `Rules/shop/shopping.list`。
- 删除已生成的根目录兼容文件。
- 删除 README 中该兼容 URL 的单独链接。
- 更新测试：验证四个客户端输出仍被生成，且生成映射中不再存在根目录兼容输出。

## 兼容性

旧 URL `Rules/shop/shopping.list` 将失效并返回 404。这是用户明确确认的破坏性变更；当前五份公开客户端模板都使用 `Rules/<Client>/shop/shopping.list`，因此不受影响。

## 验证

运行规则生成器、生成器测试和全量测试。确认 `Rules/shop/shopping.list` 不存在，四份客户端输出仍与 `shopping.txt` 一致，且 README 不再发布旧兼容 URL。
