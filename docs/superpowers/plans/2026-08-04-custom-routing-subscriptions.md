# Custom Routing Subscriptions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Maintain the confirmed 52 custom domain rules in one source file and generate policy-specific remote subscriptions for Mihomo, Surge, Quantumult X, and Loon without modifying any local client configuration.

**Architecture:** Move the single maintenance source to `Rules/Source/Custom/allenrules.list`, extend the custom parser to accept exact `DOMAIN` rules, and map each policy to a stable output directory and slug. `DIRECT` gets a new `Custom/direct.list` for each client while all existing Regional URLs remain unchanged.

**Tech Stack:** Python 3 standard library, `unittest`, text-based client rule formats, GitHub Actions, Git.

---

## File Map

- Rename `Rules/Source/Regional/allenrules.list` to `Rules/Source/Custom/allenrules.list`: the only manually maintained custom-routing source.
- Modify `tools/generate_rules.py`: parse the broader source contract, validate exact hosts, group policies, and render Custom plus Regional outputs.
- Modify `tests/test_generate_rules.py`: define the exact 52-rule contract and test all new paths and formats.
- Create `Rules/{Mihomo,Surge,QuantumultX,Loon}/Custom/direct.list`: generated DIRECT rule resources.
- Regenerate `Rules/{Mihomo,Surge,QuantumultX,Loon}/Regional/*.list`: preserve paths while updating content and source headers.
- Modify `README.md`: document the new maintenance path and four DIRECT subscription URLs.
- Modify `docs/superpowers/specs/2026-08-03-regional-routing-subscriptions-design.md`: replace the obsolete source path with the new single source path so current documentation does not conflict.
- Do not modify files under `Configs/tool_config/` or any private local client configuration.

### Task 1: Specify the custom source and parser contract

**Files:**
- Modify: `tests/test_generate_rules.py`
- Rename later: `Rules/Source/Regional/allenrules.list` to `Rules/Source/Custom/allenrules.list`
- Modify later: `tools/generate_rules.py`

- [ ] **Step 1: Replace the Regional source fixture with the exact Custom contract**

In `tests/test_generate_rules.py`, rename the source constants and define the exact rules approved in the design:

```python
CUSTOM_SOURCE_LABEL = "Rules/Source/Custom/allenrules.list"
CUSTOM_HEADER = (
    f"# Generated from {CUSTOM_SOURCE_LABEL} by tools/generate_rules.py. Do not edit."
)
CUSTOM_RULES = (
    ("DOMAIN-SUFFIX", "synology.cn", "DIRECT"),
    ("DOMAIN", "qbittorrent-nox", "DIRECT"),
    ("DOMAIN-SUFFIX", "digitalocean.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "dyndns.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "whatismyip.akamai.com", "DIRECT"),
    ("DOMAIN-KEYWORD", "volcengine", "DIRECT"),
    ("DOMAIN-SUFFIX", "xmwsyy.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "ui.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "imgse.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "tagweb.vip", "DIRECT"),
    ("DOMAIN-KEYWORD", "yqc-premium", "DIRECT"),
    ("DOMAIN-SUFFIX", "ad.12306.cn", "DIRECT"),
    ("DOMAIN-SUFFIX", "gg.caixin.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "sdkapp.uve.weibo.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "ucweb.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "amemv.com", "DIRECT"),
    ("DOMAIN-SUFFIX", "v4.plex.tv", "DIRECT"),
    ("DOMAIN-SUFFIX", "openwrt.ai", "美国节点"),
    ("DOMAIN-SUFFIX", "lsposed.org", "美国节点"),
    ("DOMAIN-SUFFIX", "hytron.io", "香港节点"),
    ("DOMAIN-SUFFIX", "linux.do", "美国节点"),
    ("DOMAIN-KEYWORD", "uspatriottactical", "美国节点"),
    ("DOMAIN-KEYWORD", "hdhive", "美国节点"),
    ("DOMAIN-SUFFIX", "rundongex.com", "美国节点"),
    ("DOMAIN-SUFFIX", "servercontrolpanel.de", "美国节点"),
    ("DOMAIN-SUFFIX", "mgboard.net", "美国节点"),
    ("DOMAIN-KEYWORD", "sehuatang", "美国节点"),
    ("DOMAIN-KEYWORD", "greasyfork", "美国节点"),
    ("DOMAIN-KEYWORD", "qichiyu", "美国节点"),
    ("DOMAIN-SUFFIX", "mjji.de", "美国节点"),
    ("DOMAIN-KEYWORD", "hd-torrents", "美国节点"),
    ("DOMAIN-SUFFIX", "embyapp.top", "美国节点"),
    ("DOMAIN-SUFFIX", "vps.town", "美国节点"),
    ("DOMAIN-SUFFIX", "2fa.fun", "美国节点"),
    ("DOMAIN-SUFFIX", "macwk.cn", "美国节点"),
    ("DOMAIN-SUFFIX", "appstorrent.ru", "美国节点"),
    ("DOMAIN-KEYWORD", "kejilion", "香港节点"),
    ("DOMAIN-SUFFIX", "nfbyte.com", "香港节点"),
    ("DOMAIN-KEYWORD", "onitsukatiger", "日本节点"),
    ("DOMAIN-SUFFIX", "compliance.chippercash.com", "美国节点"),
    ("DOMAIN-KEYWORD", "dmm", "日本节点"),
    ("DOMAIN-KEYWORD", "javrate", "日本节点"),
    ("DOMAIN-KEYWORD", "jav321", "日本节点"),
    ("DOMAIN-KEYWORD", "freejavbt", "日本节点"),
    ("DOMAIN-KEYWORD", "javbus", "日本节点"),
    ("DOMAIN-KEYWORD", "mgstage", "日本节点"),
    ("DOMAIN-KEYWORD", "mmtv", "日本节点"),
    ("DOMAIN-KEYWORD", "javdb", "新加坡节点"),
    ("DOMAIN-KEYWORD", "javlibrary", "新加坡节点"),
    ("DOMAIN-KEYWORD", "avbase", "新加坡节点"),
    ("DOMAIN-KEYWORD", "missav", "美国节点"),
    ("DOMAIN-KEYWORD", "ftvgirls", "美国节点"),
)
```

- [ ] **Step 2: Add a failing test for exact source content and exclusions**

```python
def test_custom_source_contains_only_confirmed_rules(self):
    generator = load_generator()
    source = ROOT / "Rules" / "Source" / "Custom" / "allenrules.list"

    self.assertTrue(source.exists())
    self.assertEqual(CUSTOM_RULES, tuple(generator.parse_custom_source(source)))
    content = source.read_text(encoding="utf-8")
    self.assertNotIn("SRC-IP-CIDR", content)
    self.assertNotIn("hdhive.online", content)
    self.assertNotIn("montbell.com", content)
```

- [ ] **Step 3: Extend invalid-source cases with exact DOMAIN validation**

Update the parser test so it calls `parse_custom_source` and includes:

```python
invalid_cases = {
    "DOMAIN,example.com,美国节点\n": None,
    "DOMAIN,qbittorrent-nox,DIRECT\n": None,
    "DOMAIN,-invalid,DIRECT\n": "invalid exact host",
    "DOMAIN,invalid-,DIRECT\n": "invalid exact host",
    "DOMAIN,UPPERCASE,DIRECT\n": "invalid exact host",
    "DOMAIN-SUFFIX,example.com,UNKNOWN\n": "unknown policy",
}
```

For the two entries whose expected value is `None`, assert parsing succeeds. For each string expectation, use `assertRaisesRegex(ValueError, expected)`.

- [ ] **Step 4: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_source_contains_only_confirmed_rules \
  tests.test_generate_rules.RuleGeneratorTests.test_parse_custom_source_rejects_invalid_rows -v
```

Expected: FAIL because the Custom source path and `parse_custom_source` do not exist.

- [ ] **Step 5: Commit the failing contract tests**

```bash
git add tests/test_generate_rules.py
git commit -m "test: specify custom routing source"
```

### Task 2: Move the source and support exact DOMAIN rules

**Files:**
- Rename: `Rules/Source/Regional/allenrules.list` to `Rules/Source/Custom/allenrules.list`
- Modify: `tools/generate_rules.py`
- Test: `tests/test_generate_rules.py`

- [ ] **Step 1: Move and replace the source file with the confirmed 52 lines**

Use `apply_patch` to delete the old source and add `Rules/Source/Custom/allenrules.list` with the exact `CUSTOM_RULES` order from Task 1, rendered as `type,value,policy` without leading dashes. This removes `montbell.com`, adds the 17 DIRECT rules plus `openwrt.ai` and `lsposed.org`, and keeps only the US keyword form of `hdhive`.

- [ ] **Step 2: Define policy destinations and exact-host validation**

Replace the Regional-only constants in `tools/generate_rules.py` with:

```python
CUSTOM_POLICY_OUTPUTS = {
    "DIRECT": ("Custom", "direct"),
    "香港节点": ("Regional", "hk"),
    "香港优选": ("Regional", "hk-auto"),
    "美国节点": ("Regional", "us"),
    "美国优选": ("Regional", "us-auto"),
    "日本节点": ("Regional", "jp"),
    "日本优选": ("Regional", "jp-auto"),
    "新加坡节点": ("Regional", "sg"),
    "新加坡优选": ("Regional", "sg-auto"),
}
CUSTOM_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}
HOST_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
```

- [ ] **Step 3: Rename and extend the source parser**

Rename `parse_regional_source` to `parse_custom_source`. Validate `DOMAIN` as either a normal FQDN accepted by `DOMAIN_RE` or a single label accepted by `HOST_LABEL_RE`:

```python
if rule_type == "DOMAIN" and not (
    DOMAIN_RE.fullmatch(value) or HOST_LABEL_RE.fullmatch(value)
):
    raise ValueError(f"{path}:{number}: invalid exact host: {value}")
```

Use `CUSTOM_TYPES` and `CUSTOM_POLICY_OUTPUTS` for the existing type and policy checks. Keep duplicate detection, source ordering, whitespace/comment handling, keyword/suffix overlap detection, and fail-before-write behavior unchanged.

- [ ] **Step 4: Point the generator at the Custom source**

In `build_outputs`, replace the source path and parser call:

```python
source = root / "Rules" / "Source" / "Custom" / "allenrules.list"
source_label = source.relative_to(root).as_posix()
grouped: dict[str, list[tuple[str, str, str]]] = {}
for rule in parse_custom_source(source):
    grouped.setdefault(rule[2], []).append(rule)
```

- [ ] **Step 5: Run focused parser tests and verify GREEN**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_source_contains_only_confirmed_rules \
  tests.test_generate_rules.RuleGeneratorTests.test_parse_custom_source_rejects_invalid_rows -v
```

Expected: both tests pass.

- [ ] **Step 6: Commit source and parser changes**

```bash
git add Rules/Source/Regional/allenrules.list Rules/Source/Custom/allenrules.list tools/generate_rules.py tests/test_generate_rules.py
git diff --cached --check
git commit -m "feat: support custom routing source"
```

### Task 3: Generate DIRECT and preserve Regional subscriptions

**Files:**
- Modify: `tests/test_generate_rules.py`
- Modify: `tools/generate_rules.py`
- Create: `Rules/Mihomo/Custom/direct.list`
- Create: `Rules/Surge/Custom/direct.list`
- Create: `Rules/QuantumultX/Custom/direct.list`
- Create: `Rules/Loon/Custom/direct.list`
- Regenerate: `Rules/{Mihomo,Surge,QuantumultX,Loon}/Regional/*.list`

- [ ] **Step 1: Add a failing output-map test**

Update the expected output count from 53 to 57 and add:

```python
def test_custom_direct_outputs_are_generated_for_every_client(self):
    generator = load_generator()
    outputs = generator.build_outputs(ROOT)
    direct_rules = [rule for rule in CUSTOM_RULES if rule[2] == "DIRECT"]

    for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
        with self.subTest(client=client):
            path = ROOT / "Rules" / client / "Custom" / "direct.list"
            self.assertIn(path, outputs)
            content = outputs[path]
            self.assertTrue(content.startswith(f"{CUSTOM_HEADER}\n"))
            self.assertNotIn("SRC-IP-CIDR", content)
            if client == "QuantumultX":
                self.assertIn("host, qbittorrent-nox, proxy", content)
                self.assertIn("host-suffix, synology.cn, proxy", content)
                self.assertIn("host-keyword, volcengine, proxy", content)
            else:
                self.assertIn("DOMAIN,qbittorrent-nox", content)
                self.assertIn("DOMAIN-SUFFIX,synology.cn", content)
                self.assertIn("DOMAIN-KEYWORD,volcengine", content)
            self.assertEqual(len(direct_rules), len(rule_lines(content)))
```

Define the test helper near the constants:

```python
def rule_lines(content):
    return tuple(
        line for line in content.splitlines() if line and not line.startswith("#")
    )
```

- [ ] **Step 2: Update the existing Regional output contract**

Keep all eight Regional slugs and all four clients. Change expected headers to `CUSTOM_HEADER`, derive Regional rule buckets from `CUSTOM_RULES`, and assert the existing output paths remain:

```python
for policy, slug in REGIONAL_POLICY_FILES.items():
    rules = [rule for rule in CUSTOM_RULES if rule[2] == policy]
    for client in REGIONAL_CLIENTS:
        self.assertIn(ROOT / "Rules" / client / "Regional" / f"{slug}.list", outputs)
```

- [ ] **Step 3: Run output tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_direct_outputs_are_generated_for_every_client \
  tests.test_generate_rules.RuleGeneratorTests.test_regional_outputs_include_all_clients_and_policies \
  tests.test_generate_rules.RuleGeneratorTests.test_output_map_contains_all_expected_files -v
```

Expected: FAIL because DIRECT is not yet mapped to generated output paths and `DOMAIN` is not yet rendered for Quantumult X.

- [ ] **Step 4: Extend client rendering for DOMAIN**

In the custom renderer, add Quantumult X's exact-host mapping while classical clients continue to emit the source rule type unchanged:

```python
qx_type = {
    "DOMAIN": "host",
    "DOMAIN-SUFFIX": "host-suffix",
    "DOMAIN-KEYWORD": "host-keyword",
}[rule_type]
```

Rename `render_regional` to `render_custom_rules` so the function name matches its expanded responsibility.

- [ ] **Step 5: Generate each policy at its declared destination**

Replace the Regional-only output loop with:

```python
for client, style in client_styles.items():
    for policy, (directory, slug) in CUSTOM_POLICY_OUTPUTS.items():
        outputs[root / "Rules" / client / directory / f"{slug}.list"] = (
            render_custom_rules(grouped.get(policy, []), style, source_label)
        )
```

- [ ] **Step 6: Generate files and verify GREEN**

Run:

```bash
python3 tools/generate_rules.py
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_direct_outputs_are_generated_for_every_client \
  tests.test_generate_rules.RuleGeneratorTests.test_regional_outputs_include_all_clients_and_policies \
  tests.test_generate_rules.RuleGeneratorTests.test_output_map_contains_all_expected_files -v
python3 tools/generate_rules.py --check
```

Expected: tests pass, check exits 0, four new DIRECT outputs exist, and existing Regional files are current.

- [ ] **Step 7: Commit generated outputs**

```bash
git add tools/generate_rules.py tests/test_generate_rules.py \
  Rules/Mihomo/Custom Rules/Surge/Custom \
  Rules/QuantumultX/Custom Rules/Loon/Custom \
  Rules/Mihomo/Regional Rules/Surge/Regional \
  Rules/QuantumultX/Regional Rules/Loon/Regional
git diff --cached --check
git commit -m "feat: generate custom direct subscriptions"
```

### Task 4: Document the new maintenance source and DIRECT URLs

**Files:**
- Modify: `tests/test_generate_rules.py`
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-08-03-regional-routing-subscriptions-design.md`

- [ ] **Step 1: Add a failing documentation test**

```python
def test_custom_direct_subscription_documentation_is_complete(self):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    base_url = (
        "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules"
    )

    self.assertIn(CUSTOM_SOURCE_LABEL, readme)
    self.assertNotIn("Rules/Source/Regional/allenrules.list", readme)
    for client in REGIONAL_CLIENTS:
        self.assertIn(f"{base_url}/{client}/Custom/direct.list", readme)
```

- [ ] **Step 2: Run the documentation test and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_direct_subscription_documentation_is_complete -v
```

Expected: FAIL because README still names the old source and has no Custom DIRECT URLs.

- [ ] **Step 3: Update README**

Change the Regional introduction to name `Rules/Source/Custom/allenrules.list`. Add a row to the subscription table:

```markdown
| 自定义直连 | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Custom/direct.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Surge/Custom/direct.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/QuantumultX/Custom/direct.list) | [订阅](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Loon/Custom/direct.list) |
```

State that the single source produces both Custom DIRECT and Regional resources, and that local client configs remain unchanged.

- [ ] **Step 4: Update the earlier Regional design's current source reference**

In `docs/superpowers/specs/2026-08-03-regional-routing-subscriptions-design.md`, replace `Rules/Source/Regional/allenrules.list` with `Rules/Source/Custom/allenrules.list` and add one sentence that the source was broadened by the 2026-08-04 Custom design while Regional output URLs stayed stable.

- [ ] **Step 5: Run documentation and generator tests**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_custom_direct_subscription_documentation_is_complete \
  tests.test_generate_rules.RuleGeneratorTests.test_regional_subscription_documentation_is_complete -v
python3 tools/generate_rules.py --check
```

Expected: all tests pass and generated files are current.

- [ ] **Step 6: Commit documentation**

```bash
git add README.md tests/test_generate_rules.py \
  docs/superpowers/specs/2026-08-03-regional-routing-subscriptions-design.md
git diff --cached --check
git commit -m "docs: publish custom direct subscriptions"
```

### Task 5: Full verification and direct main push

**Files:**
- Verify: all files changed since `origin/main`
- Do not modify: `Configs/tool_config/*`

- [ ] **Step 1: Run the complete test suite**

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass with zero failures and zero errors.

- [ ] **Step 2: Verify generated resources and diff hygiene**

```bash
python3 tools/generate_rules.py --check
git diff --check origin/main...HEAD
git status -sb
```

Expected: generator check exits 0, diff check exits 0, and the worktree is clean.

- [ ] **Step 3: Confirm no local client configuration changed**

```bash
git diff --name-only origin/main...HEAD -- Configs/tool_config
```

Expected: no output.

- [ ] **Step 4: Confirm exact source exclusions and output paths**

```bash
rg -n 'SRC-IP-CIDR|hdhive\.online|montbell\.com' Rules/Source/Custom/allenrules.list Rules/*/Custom Rules/*/Regional
rg -n 'DOMAIN,qbittorrent-nox|DOMAIN-SUFFIX,synology\.cn|DOMAIN-KEYWORD,volcengine' Rules/Mihomo/Custom/direct.list
```

Expected: the first command finds nothing; the second command finds all three rules.

- [ ] **Step 5: Synchronize with remote main without creating a branch**

```bash
git fetch origin --prune
git rev-list --left-right --count origin/main...HEAD
```

Expected before push: `0` behind and one or more commits ahead. If remote main advanced, rebase onto `origin/main`, rerun Steps 1-4, and never force-push.

- [ ] **Step 6: Push the current branch directly to main**

```bash
git push origin HEAD:main
git fetch origin --prune
git rev-list --left-right --count origin/main...HEAD
```

Expected: push succeeds without creating a new remote branch; final count is `0 0`.

- [ ] **Step 7: Verify GitHub's sync workflow**

```bash
gh run list --workflow "Sync generated rules" --branch main --limit 1
```

Expected: the latest main run completes successfully. If it is still running, watch that run with `gh run watch <run-id> --exit-status` and report any failure with its log evidence.
