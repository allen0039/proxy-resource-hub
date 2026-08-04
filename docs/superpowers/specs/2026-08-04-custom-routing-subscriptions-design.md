# Custom Routing 规则订阅设计

## 目标

将用户确认的 `DIRECT` 与地区分流域名集中到一个 GitHub 源文件维护，并由现有生成器为 Mihomo、Surge、Quantumult X 和 Loon 自动生成按策略拆分的远程规则订阅。

本次只发布远程规则资源，不修改任何本地客户端配置。三条 `SRC-IP-CIDR` 规则和 Apple、GitHub、AI、YouTube、Google、REJECT 等其他本地规则继续由用户在本地维护。

## 单一维护入口

源文件从原来的地区目录迁移到：

```text
Rules/Source/Custom/allenrules.list
```

源文件每条有效规则使用三字段、逗号分隔格式，不使用 YAML 列表前缀：

```text
<规则类型>,<匹配值>,<策略组>
```

本次支持的规则类型为：

- `DOMAIN`
- `DOMAIN-SUFFIX`
- `DOMAIN-KEYWORD`

本次允许的策略组为：

- `DIRECT`
- `香港节点`
- `香港优选`
- `美国节点`
- `美国优选`
- `日本节点`
- `日本优选`
- `新加坡节点`
- `新加坡优选`

保留现有四个优选策略名和稳定输出，即使本次源文件没有指向优选策略的规则。

## 确认的规则范围

源文件包含以下 52 条有效规则，其中 17 条使用 `DIRECT`，35 条使用地区节点策略：

```text
DOMAIN-SUFFIX,synology.cn,DIRECT
DOMAIN,qbittorrent-nox,DIRECT
DOMAIN-SUFFIX,digitalocean.com,DIRECT
DOMAIN-SUFFIX,dyndns.com,DIRECT
DOMAIN-SUFFIX,whatismyip.akamai.com,DIRECT
DOMAIN-KEYWORD,volcengine,DIRECT
DOMAIN-SUFFIX,xmwsyy.com,DIRECT
DOMAIN-SUFFIX,ui.com,DIRECT
DOMAIN-SUFFIX,imgse.com,DIRECT
DOMAIN-SUFFIX,tagweb.vip,DIRECT
DOMAIN-KEYWORD,yqc-premium,DIRECT
DOMAIN-SUFFIX,ad.12306.cn,DIRECT
DOMAIN-SUFFIX,gg.caixin.com,DIRECT
DOMAIN-SUFFIX,sdkapp.uve.weibo.com,DIRECT
DOMAIN-SUFFIX,ucweb.com,DIRECT
DOMAIN-SUFFIX,amemv.com,DIRECT
DOMAIN-SUFFIX,v4.plex.tv,DIRECT
DOMAIN-SUFFIX,openwrt.ai,美国节点
DOMAIN-SUFFIX,lsposed.org,美国节点
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

以下两项是用户明确确认的排除项：

- 不收录 `DOMAIN-SUFFIX,hdhive.online,香港节点`，因为 `DOMAIN-KEYWORD,hdhive,美国节点` 已覆盖它，且用户选择美国策略。
- 删除原远程源中的 `DOMAIN-SUFFIX,montbell.com,香港节点`。

## 输出结构

`DIRECT` 规则生成到新的 Custom 订阅：

```text
Rules/Mihomo/Custom/direct.list
Rules/Surge/Custom/direct.list
Rules/QuantumultX/Custom/direct.list
Rules/Loon/Custom/direct.list
```

地区规则继续生成到现有稳定路径：

```text
Rules/<Client>/Regional/hk.list
Rules/<Client>/Regional/hk-auto.list
Rules/<Client>/Regional/us.list
Rules/<Client>/Regional/us-auto.list
Rules/<Client>/Regional/jp.list
Rules/<Client>/Regional/jp-auto.list
Rules/<Client>/Regional/sg.list
Rules/<Client>/Regional/sg-auto.list
```

`<Client>` 为 `Mihomo`、`Surge`、`QuantumultX` 或 `Loon`。现有 Regional 订阅 URL 保持不变；生成文件头中的源路径更新为新的 Custom 源文件。

Mihomo、Surge 和 Loon 使用 classical 文本规则：

```text
DOMAIN,qbittorrent-nox
DOMAIN-SUFFIX,synology.cn
DOMAIN-KEYWORD,volcengine
```

Quantumult X 对应转换为：

```text
host, qbittorrent-nox, proxy
host-suffix, synology.cn, proxy
host-keyword, volcengine, proxy
```

远程列表本身不嵌入最终策略选择。客户端后续接入时，由 Mihomo 的 `RULE-SET`、Surge 的 `RULE-SET`、Quantumult X 的 `force-policy` 和 Loon 的 `policy` 将每个订阅绑定到对应策略。本次不执行这一步。

## 生成器与校验

扩展 `tools/generate_rules.py`：

- 从新的 Custom 源路径读取一次规则。
- 支持 `DOMAIN`，包括 `qbittorrent-nox` 这类单标签主机名。
- 按策略组分桶，DIRECT 写入 Custom 输出，地区策略写入现有 Regional 输出。
- 保持源文件顺序。
- 拒绝未知规则类型、未知策略、空字段、非法匹配值和重复规则。
- 继续拒绝会产生冲突的 `DOMAIN-KEYWORD` 与 `DOMAIN-SUFFIX` 覆盖组合。
- 生成失败时不部分写入输出。

测试覆盖以下行为：

- 源文件精确包含确认的 52 条规则。
- 四种客户端均生成 `Custom/direct.list`。
- 四种客户端的现有 Regional 输出路径和策略映射保持不变。
- `DOMAIN` 在各客户端格式中正确转换。
- `hdhive.online` 与 `montbell.com` 不出现在源文件或生成结果中。
- 本地客户端配置文件不在本次改动范围内。
- GitHub Actions 在 `main` 收到源文件修改后继续自动生成、测试并提交 Rules 下的变化。

## 文档与使用说明

README 将维护入口更新为 `Rules/Source/Custom/allenrules.list`，保留现有地区订阅链接，并增加四种客户端的 DIRECT 订阅地址。文档明确说明本次只生成远程规则，不修改本地配置。
