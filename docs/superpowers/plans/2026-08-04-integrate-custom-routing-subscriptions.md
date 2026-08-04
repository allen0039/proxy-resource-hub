# Integrate Custom Routing Subscriptions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `allenrules.list` 生成的九类远程规则订阅接入 Mihomo、Surge Mac、Surge iPhone、Quantumult X 和 Loon 五份配置，同时删除已迁移的本地重复域名规则。

**Architecture:** 五份私有原始配置仍是配置真源，公开仓库模板由 `tools/sanitize_tool_configs.py` 从这些原始文件脱敏重建。每个客户端直接引用仓库 `main` 分支上的九条 raw 规则 URL；客户端配置负责把每条 URL 绑定到 `DIRECT`、地区节点或地区优选策略，规则源仍只维护 `Rules/Source/Custom/allenrules.list`。

**Tech Stack:** Mihomo YAML；Surge/Mac 与 Surge/iPhone `[Rule]`；Quantumult X `[filter_remote]`/`[filter_local]`；Loon `[Remote Rule]`；Python `unittest`、PyYAML、现有 sanitizer 与 GitHub Actions。

## Global Constraints

- 只把 `DIRECT` 与地区分流域名通过远程订阅接入配置；三条 `SRC-IP-CIDR,192.168.50.150/151/152/32,DIRECT` 继续保留在本地并优先匹配。
- 迁移并删除 52 条远程源规则在五份配置中的本地副本，同时删除 `DOMAIN-SUFFIX,hdhive.online,香港节点`；保留 `montbell.com` 和其他未迁移本地规则。
- 五份私有原始配置位于用户自行选择的仓库外目录，不属于仓库，不能加入 Git、提交或推送。执行本计划前，用户须在本地设置 `PRIVATE_CONFIG_DIR`（例如 `export PRIVATE_CONFIG_DIR=/path/to/private/configs`）；计划和提交中只使用 `$PRIVATE_CONFIG_DIR` 占位符，绝不记录其真实值。
- 所有订阅 URL 固定使用 `https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/`，更新周期为 86400 秒。
- 九个订阅 slug 固定为 `direct`、`hk`、`hk-auto`、`us`、`us-auto`、`jp`、`jp-auto`、`sg`、`sg-auto`。
- 远程自定义规则必须位于宽泛第三方远程规则和最终兜底规则之前；客户端规则按从上到下首次匹配。
- 直接在当前 `docker-public` 工作树提交，不创建分支；仅在用户确认后推送到 `origin/main`。

---

### Task 1: Add failing regression coverage for all five clients

**Files:**
- Modify: `tests/test_sanitized_tool_configs.py`

**Interfaces:**
- Consumes: Existing public templates in `Configs/tool_config/`.
- Produces: Regression assertions for the nine URL/policy bindings, priority, and removal of migrated local duplicates.

- [ ] **Step 1: Add shared feed metadata and local-duplicate helpers**

Add these constants near the existing URL constants:

```python
CUSTOM_BASE_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
)
CUSTOM_FEEDS = {
    "direct": ("Custom/direct.list", "DIRECT"),
    "hk": ("Regional/hk.list", "香港节点"),
    "hk-auto": ("Regional/hk-auto.list", "香港优选"),
    "us": ("Regional/us.list", "美国节点"),
    "us-auto": ("Regional/us-auto.list", "美国优选"),
    "jp": ("Regional/jp.list", "日本节点"),
    "jp-auto": ("Regional/jp-auto.list", "日本优选"),
    "sg": ("Regional/sg.list", "新加坡节点"),
    "sg-auto": ("Regional/sg-auto.list", "新加坡优选"),
}
MIGRATED_LOCAL_RULES = (
    "synology.cn", "qbittorrent-nox", "digitalocean.com", "dyndns.com",
    "whatismyip.akamai.com", "volcengine", "xmwsyy.com", "ui.com",
    "imgse.com", "tagweb.vip", "yqc-premium", "ad.12306.cn",
    "gg.caixin.com", "sdkapp.uve.weibo.com", "ucweb.com", "amemv.com",
    "v4.plex.tv", "openwrt.ai", "lsposed.org", "hytron.io", "linux.do",
    "uspatriottactical", "hdhive", "rundongex.com", "servercontrolpanel.de",
    "mgboard.net", "sehuatang", "greasyfork", "qichiyu", "mjji.de",
    "hd-torrents", "embyapp.top", "vps.town", "2fa.fun", "macwk.cn",
    "appstorrent.ru", "kejilion", "nfbyte.com", "onitsukatiger",
    "compliance.chippercash.com", "dmm", "javrate", "jav321", "freejavbt",
    "javbus", "mgstage", "mmtv", "javdb", "javlibrary", "avbase",
    "missav", "ftvgirls",
)

def active_section(text: str, section: str, next_section: str | None = None) -> str:
    start = text.index(section) + len(section)
    end = text.index(next_section, start) if next_section else len(text)
    return text[start:end]

def custom_url(client: str, slug: str) -> str:
    path, _ = CUSTOM_FEEDS[slug]
    return f"{CUSTOM_BASE_URL}Rules/{client}/{path}"
```

- [ ] **Step 2: Add tests for Mihomo providers and rule order**

Add a test that parses `mihomo_allen.yaml` with `yaml.safe_load`, verifies all nine providers have `type=http`, `behavior=classical`, `format=text`, `interval=86400`, and the exact URL from `custom_url("Mihomo", slug)`. Verify `rules` contains, in slug order, `RULE-SET,custom_<slug with '-' replaced by '_'>,<policy>` immediately after the three `SRC-IP-CIDR` entries and before the first existing broad `RULE-SET`.

- [ ] **Step 3: Add tests for Surge Mac/iPhone URL and policy bindings**

For both `surge_mac_allen.conf` and `surge_iphone_allen.conf`, extract `[Rule]` through the next section and assert each URL occurs exactly once in a `RULE-SET,<url>,<policy>` line. Assert the direct policy is `DIRECT`, the eight region policies match `CUSTOM_FEEDS`, and every custom URL occurs before `RULE-SET,https://ruleset.skk.moe/`.

- [ ] **Step 4: Add tests for Quantumult X and Loon bindings**

For Quantumult X, inspect `[filter_remote]` and assert every URL has the expected `tag=自定义-<label>`, `force-policy=direct` for `direct` or the mapped Chinese policy, `update-interval=86400`, `opt-parser=false`, and `enabled=true`; assert all nine occur before the existing `ChinaTelecom` entry. For Loon, inspect `[Remote Rule]` and assert every URL has the mapped `policy=`, `tag=自定义-<label>`, and `enabled=true`, before the existing `ChinaTelecom` entry.

- [ ] **Step 5: Add tests that migrated rules are no longer local**

Use the active local sections (`rules` for Mihomo, `[Rule]` for Surge/Loon, `[filter_local]` for Quantumult X) and assert none of the `MIGRATED_LOCAL_RULES` values appears in an active local rule line. Explicitly assert `montbell.com` remains active locally and `hdhive.online,香港节点` does not remain. Keep the test limited to public templates, so it never reads or publishes the private source configurations.

- [ ] **Step 6: Run the new tests and verify they fail before implementation**

Run:

```bash
python3 -m unittest tests.test_sanitized_tool_configs -v
```

Expected: the new subscription and duplicate-removal assertions fail against the current templates, while the pre-existing sanitizer tests continue to pass.

- [ ] **Step 7: Commit the failing tests**

```bash
git add tests/test_sanitized_tool_configs.py
git commit -m "test: cover custom routing subscriptions in tool configs"
```

### Task 2: Update private source configurations with remote feeds and remove duplicates

**Files:**
- Modify (private, never stage): `$PRIVATE_CONFIG_DIR/mihomo_byallen.yaml`
- Modify (private, never stage): `$PRIVATE_CONFIG_DIR/surge-Mac.conf`
- Modify (private, never stage): `$PRIVATE_CONFIG_DIR/Surge-iPhone.conf`
- Modify (private, never stage): `$PRIVATE_CONFIG_DIR/quantumult_byallen.conf`
- Modify (private, never stage): `$PRIVATE_CONFIG_DIR/allenloon.lcf`

**Interfaces:**
- Consumes: Existing policy group names and the public paths generated under `Rules/Mihomo`, `Rules/Surge`, `Rules/QuantumultX`, and `Rules/Loon`.
- Produces: Five local source configurations with nine remote subscriptions and no migrated active domain duplicates.

- [ ] **Step 1: Record private-file status and confirm no private files are tracked**

Run:

```bash
: "${PRIVATE_CONFIG_DIR:?Set PRIVATE_CONFIG_DIR to the local private configuration directory}"
git status --short
git ls-files --error-unmatch -- "$PRIVATE_CONFIG_DIR/mihomo_byallen.yaml" 2>/dev/null || true
git ls-files --error-unmatch -- "$PRIVATE_CONFIG_DIR/surge-Mac.conf" 2>/dev/null || true
git ls-files --error-unmatch -- "$PRIVATE_CONFIG_DIR/Surge-iPhone.conf" 2>/dev/null || true
git ls-files --error-unmatch -- "$PRIVATE_CONFIG_DIR/quantumult_byallen.conf" 2>/dev/null || true
git ls-files --error-unmatch -- "$PRIVATE_CONFIG_DIR/allenloon.lcf" 2>/dev/null || true
```

Expected: the repository starts clean apart from no tracked private source paths; if any private path is tracked, stop before editing and remove it from the staging scope rather than committing its contents.

- [ ] **Step 2: Insert the Mihomo rule providers and RULE-SET block**

In the private Mihomo YAML, add these nine providers under `rule-providers:` (using the exact corresponding URL path):

```yaml
  custom_direct: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Custom/direct.list" }
  custom_hk: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/hk.list" }
  custom_hk_auto: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/hk-auto.list" }
  custom_us: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/us.list" }
  custom_us_auto: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/us-auto.list" }
  custom_jp: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/jp.list" }
  custom_jp_auto: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/jp-auto.list" }
  custom_sg: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/sg.list" }
  custom_sg_auto: { type: http, interval: 86400, behavior: classical, format: text, url: "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/sg-auto.list" }
```

Immediately after the three source-IP rules in `rules:`, add:

```yaml
  - RULE-SET,custom_direct,DIRECT
  - RULE-SET,custom_hk,香港节点
  - RULE-SET,custom_hk_auto,香港优选
  - RULE-SET,custom_us,美国节点
  - RULE-SET,custom_us_auto,美国优选
  - RULE-SET,custom_jp,日本节点
  - RULE-SET,custom_jp_auto,日本优选
  - RULE-SET,custom_sg,新加坡节点
  - RULE-SET,custom_sg_auto,新加坡优选
```

- [ ] **Step 3: Insert the Surge Mac and iPhone remote blocks**

In each `[Rule]`, insert the following nine lines before existing local domain rules and before any broad third-party `RULE-SET`:

```ini
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Custom/direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/hk.list,香港节点
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/hk-auto.list,香港优选
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/us.list,美国节点
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/us-auto.list,美国优选
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/jp.list,日本节点
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/jp-auto.list,日本优选
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/sg.list,新加坡节点
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Regional/sg-auto.list,新加坡优选
```

Keep the Mac `SRC-IP,192.168.50.150/151/152,DIRECT` entries before this block. The iPhone source has no such source-IP protection, so the custom block follows the `[Rule]` preamble.

- [ ] **Step 4: Insert the Quantumult X filter_remote block**

At the top of `[filter_remote]`, add these exact lines (using `direct` only for the direct feed and the existing Chinese policy names for the other feeds):

```ini
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Custom/direct.list, tag=自定义-直连, force-policy=direct, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/hk.list, tag=自定义-香港节点, force-policy=香港节点, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/hk-auto.list, tag=自定义-香港优选, force-policy=香港优选, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/us.list, tag=自定义-美国节点, force-policy=美国节点, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/us-auto.list, tag=自定义-美国优选, force-policy=美国优选, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/jp.list, tag=自定义-日本节点, force-policy=日本节点, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/jp-auto.list, tag=自定义-日本优选, force-policy=日本优选, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/sg.list, tag=自定义-新加坡节点, force-policy=新加坡节点, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Regional/sg-auto.list, tag=自定义-新加坡优选, force-policy=新加坡优选, update-interval=86400, opt-parser=false, enabled=true
```

Remove the migrated rules from `[filter_local]`, including their previous QX syntax (`host`, `host-suffix`, or `host-keyword`), but retain `montbell.com` and unrelated local rules. The remote block must remain above `ChinaTelecom` and all other broad feeds.

- [ ] **Step 5: Insert the Loon Remote Rule block**

At the top of `[Remote Rule]`, add the following nine lines:

```ini
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Custom/direct.list, policy=DIRECT, tag=自定义-直连, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/hk.list, policy=香港节点, tag=自定义-香港节点, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/hk-auto.list, policy=香港优选, tag=自定义-香港优选, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/us.list, policy=美国节点, tag=自定义-美国节点, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/us-auto.list, policy=美国优选, tag=自定义-美国优选, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/jp.list, policy=日本节点, tag=自定义-日本节点, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/jp-auto.list, policy=日本优选, tag=自定义-日本优选, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/sg.list, policy=新加坡节点, tag=自定义-新加坡节点, enabled=true
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Regional/sg-auto.list, policy=新加坡优选, tag=自定义-新加坡优选, enabled=true
```

Delete the migrated active domain rules from Loon `[Rule]`, including `hdhive.online`, while keeping `montbell.com` and unrelated local rules. Keep the custom Remote Rule block before the existing `ChinaTelecom` remote rule.

- [ ] **Step 6: Verify private source edits without staging them**

Run a read-only check against the five private files:

```bash
rg -n "Rules/(Mihomo|Surge|QuantumultX|Loon)/(Custom|Regional)/(direct|hk|hk-auto|us|us-auto|jp|jp-auto|sg|sg-auto)\.list" \
  "$PRIVATE_CONFIG_DIR/mihomo_byallen.yaml" "$PRIVATE_CONFIG_DIR/surge-Mac.conf" \
  "$PRIVATE_CONFIG_DIR/Surge-iPhone.conf" "$PRIVATE_CONFIG_DIR/quantumult_byallen.conf" \
  "$PRIVATE_CONFIG_DIR/allenloon.lcf"
rg -n "hdhive\.online|DOMAIN-(SUFFIX|KEYWORD),montbell\.com|montbell\.com" \
  "$PRIVATE_CONFIG_DIR/mihomo_byallen.yaml" "$PRIVATE_CONFIG_DIR/surge-Mac.conf" \
  "$PRIVATE_CONFIG_DIR/Surge-iPhone.conf" "$PRIVATE_CONFIG_DIR/quantumult_byallen.conf" \
  "$PRIVATE_CONFIG_DIR/allenloon.lcf"
```

Expected: nine feed references per applicable config, no active `hdhive.online`, and `montbell.com` still present. Confirm three source-IP rules remain in the Mac/Mihomo sources where they originally exist.

### Task 3: Regenerate public templates and update usage documentation

**Files:**
- Modify: `Configs/tool_config/mihomo_allen.yaml`
- Modify: `Configs/tool_config/surge_mac_allen.conf`
- Modify: `Configs/tool_config/surge_iphone_allen.conf`
- Modify: `Configs/tool_config/quantumultx_allen.conf`
- Modify: `Configs/tool_config/loon_allen.lcf`
- Modify: `Configs/tool_config/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: The five private source configurations from Task 2 and the existing sanitizer command.
- Produces: Public, sanitized templates containing the same remote subscriptions without private URLs, secrets, UUIDs, or certificates.

- [ ] **Step 1: Regenerate all five public templates through the sanitizer**

Run from the repository root:

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir "$PRIVATE_CONFIG_DIR" \
  --output-dir Configs/tool_config
```

Do not copy the private files into the repository. The command must write only the five expected files under `Configs/tool_config/`.

- [ ] **Step 2: Update the public configuration README**

Replace the statement that public templates do not include personal remote rules with wording that the templates now include the nine `allenrules.list`-derived subscriptions for each client. Retain the security warning that the templates contain no real proxy subscription, node credential, token, UUID, password, P12, certificate, or private key, and retain instructions to use the raw templates as local configuration files rather than as a private proxy subscription.

Add a short table after the existing “更新订阅和远程资源” guidance:

| 客户端 | 自定义远程规则已接入 |
| --- | --- |
| Mihomo | `Custom/direct` + `Regional/{hk,hk-auto,us,us-auto,jp,jp-auto,sg,sg-auto}` |
| Surge Mac / iPhone | 同上，对应 `Rules/Surge/` |
| Quantumult X | 同上，对应 `Rules/QuantumultX/` |
| Loon | 同上，对应 `Rules/Loon/` |

Explain that future domain changes are made only in `Rules/Source/Custom/allenrules.list`; GitHub Actions regenerates the lists, and clients update them at their configured 86400-second interval.

Update the root `README.md` section `### Custom / Regional 自定义路由订阅`: replace the sentence that says local client configurations remain unchanged with a statement that the five public templates already reference the nine generated subscriptions. Keep the existing subscription address table, and state that changing `Rules/Source/Custom/allenrules.list` updates both the standalone rule URLs and the next generated client-template revision.

- [ ] **Step 3: Run the new regression tests after regeneration**

Run:

```bash
python3 -m unittest tests.test_sanitized_tool_configs -v
```

Expected: all new URL/policy/order and duplicate-removal tests pass, with no sanitizer leakage failures.

- [ ] **Step 4: Commit public templates and documentation**

Before staging, inspect `git status --short` and ensure no path outside `proxy-resource-hub` is listed. Then run:

```bash
git add Configs/tool_config tests/test_sanitized_tool_configs.py
git commit -m "feat: wire custom rule feeds into client configs"
```

### Task 4: Run full validation and publish to main

**Files:**
- Verify only: generated `Rules/`, workflows, templates, tests, docs, and Git history.

**Interfaces:**
- Consumes: Commits from Tasks 1–3 and the existing generator/workflow.
- Produces: A verified `origin/main` containing the integrated configuration templates and tests.

- [ ] **Step 1: Run the complete repository test suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass, including generator, sanitizer, workflow orchestration, SKK update, and the new custom-feed coverage.

- [ ] **Step 2: Verify generated rules are current**

Run:

```bash
python3 tools/generate_rules.py --check
git diff --check
```

Expected: generator check succeeds with no generated-rule diff and no whitespace errors.

- [ ] **Step 3: Inspect public-output safety and configuration bindings**

Run:

```bash
git status --short
git diff --stat origin/main..HEAD
rg -n "private\.invalid|FAKE_|CHANGE_ME|获取到的订阅链接" Configs/tool_config
: "${PRIVATE_CONFIG_DIR:?Set PRIVATE_CONFIG_DIR to the local private configuration directory}"
set -o pipefail
if ! diff_content="$(git diff --no-ext-diff origin/main..HEAD)"; then
  echo "ERROR: unable to inspect committed diff content" >&2
  exit 1
fi
if printf '%s\n' "$diff_content" | rg -n -F -- "$PRIVATE_CONFIG_DIR"; then
  echo "ERROR: private source directory appears in committed diff content" >&2
  exit 1
fi
if printf '%s\n' "$diff_content" | rg -n -i \
  '(private[.]invalid|sk-[a-z0-9]{20,}|gh[pousr]_[a-z0-9]{20,}|xox[baprs]-[a-z0-9-]{10,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|password\s*[:=]\s*[^[:space:]]{8,}|token\s*[:=]\s*[^[:space:]]{8,})'; then
  echo "ERROR: secret or private-endpoint marker appears in committed diff content" >&2
  exit 1
fi
```

Expected: only intended repository files are listed, and both diff-content scans return no matches; no private source directory, private URL, or credential appears in committed content. `获取到的订阅链接` is allowed only as the existing public placeholder, not a real URL. Confirm the nine raw GitHub rule URLs and policy bindings remain visible in the five public templates. A changed-filename list alone is not evidence of content safety.

- [ ] **Step 4: Push the current branch directly to origin/main**

After the local checks pass, publish without creating a branch:

```bash
git push origin HEAD:main
git status --short --branch
```

Expected: `origin/main` points to the new integration commit, the working tree is clean, and the existing GitHub Actions rule-generation workflow is triggered. Report the commit ID and workflow result only after checking the remote state.
