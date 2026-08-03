# Regional Routing 规则订阅 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one three-field regional routing source file that generates 32 stable Mihomo, Surge, Quantumult X, and Loon rule subscriptions for eight logical node/policy groups, without changing the five local client configurations.

**Architecture:** Keep the existing naked-domain generator unchanged for AI, Personal, PT, and shopping rules. Add a separate Regional parser for `DOMAIN-SUFFIX` and `DOMAIN-KEYWORD` rows, validate them against the eight approved policies, bucket them by policy slug, and render one remote file per client/policy pair. Generate empty preferred-policy files so all 32 Raw URLs remain stable.

**Tech Stack:** Python 3 standard library (`argparse`, `re`, `pathlib`, `collections`), unittest, GitHub Actions, Markdown documentation.

## Global Constraints

- Source file is `Rules/Source/Regional/routing.list`; no other file is a Regional maintenance entry point.
- Supported rule types are exactly `DOMAIN-SUFFIX` and `DOMAIN-KEYWORD`.
- Allowed policies are exactly `香港节点`, `香港优选`, `美国节点`, `美国优选`, `日本节点`, `日本优选`, `新加坡节点`, and `新加坡优选`.
- The source contains the 34 approved rules from the design spec; `DOMAIN-SUFFIX,hdhive.online,香港节点` is excluded and `DOMAIN-KEYWORD,hdhive,美国节点` is retained.
- Outputs are `Rules/{Mihomo,Surge,QuantumultX,Loon}/Regional/{hk,hk-auto,us,us-auto,jp,jp-auto,sg,sg-auto}.list`.
- Mihomo, Surge, and Loon output two-field classical rules; Quantumult X outputs `host-suffix`/`host-keyword` with the placeholder policy `proxy`.
- Duplicate `TYPE + VALUE`, duplicate values across policies, invalid types/policies, malformed values, and keyword/suffix overlaps fail before any output is written.
- The five local configurations in the workspace are not modified.
- Existing AI, Personal, PT, shopping, and SKK generation behavior remains unchanged.

---

### Task 1: Add failing Regional parser and output-contract tests

**Files:**
- Modify: `tests/test_generate_rules.py`
- Create: `Rules/Source/Regional/routing.list`

**Interfaces:**
- Consumes: the current `tools/generate_rules.py` module loaded by `load_generator()`.
- Produces: failing tests that define `parse_regional_source(path)`, `render_regional(rules, style, source_label)`, and the 32-path Regional portion of `build_outputs(root)`.

- [ ] **Step 1: Add source constants and a Regional output test**

Add `REGIONAL_RULES` as the 34 exact `(type, value, policy)` tuples from the design spec, plus `REGIONAL_POLICY_FILES` mapping the eight Chinese policies to `hk`, `hk-auto`, `us`, `us-auto`, `jp`, `jp-auto`, `sg`, and `sg-auto`. Add a test with this shape:

```python
def test_regional_outputs_include_all_clients_and_policies(self):
    generator = load_generator()
    outputs = generator.build_outputs(ROOT)
    source = ROOT / "Rules" / "Source" / "Regional" / "routing.list"
    self.assertTrue(source.exists())
    self.assertEqual(REGIONAL_RULES, tuple(generator.parse_regional_source(source)))
    for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
        for slug in ("hk", "hk-auto", "us", "us-auto", "jp", "jp-auto", "sg", "sg-auto"):
            self.assertIn(ROOT / "Rules" / client / "Regional" / f"{slug}.list", outputs)
```

- [ ] **Step 2: Add output-format assertions**

Assert that `us.list` contains the US suffix and keyword rules in source order, `hk-auto.list` is header-only, and the rendered examples are exact:

```python
us = outputs[ROOT / "Rules" / "Surge" / "Regional" / "us.list"]
self.assertIn("DOMAIN-SUFFIX,linux.do", us)
self.assertIn("DOMAIN-KEYWORD,hdhive", us)
self.assertNotIn("hdhive.online", us)
qx = outputs[ROOT / "Rules" / "QuantumultX" / "Regional" / "jp.list"]
self.assertIn("host-keyword, dmm, proxy", qx)
self.assertIn("host-keyword, javbus, proxy", qx)
preferred = outputs[ROOT / "Rules" / "Mihomo" / "Regional" / "us-auto.list"]
self.assertEqual(0, len([line for line in preferred.splitlines() if line and not line.startswith("#")]))
```

The header is the only content in an empty preferred file.

- [ ] **Step 3: Add validation tests before implementation**

Add temporary-directory tests that write these exact invalid contents and assert `ValueError` messages include the relevant reason:

```python
invalid_cases = {
    "DOMAIN,example.com,美国节点\n": "unsupported rule type",
    "DOMAIN-SUFFIX,example.com,欧洲节点\n": "unknown policy",
    "DOMAIN-SUFFIX,https://example.com/path,美国节点\n": "invalid domain",
    "DOMAIN-SUFFIX,example.com,美国节点\nDOMAIN-SUFFIX,example.com,日本节点\n": "duplicate rule",
    "DOMAIN-KEYWORD,hdhive,美国节点\nDOMAIN-SUFFIX,hdhive.online,香港节点\n": "overlapping keyword and suffix",
}
```

Also test missing fields, uppercase values, whitespace in keywords, and duplicate rows with the same policy.

- [ ] **Step 4: Run the focused tests and confirm they fail for the missing API**

Run:

```bash
python3 -m unittest tests.test_generate_rules -v
```

Expected: FAIL because `parse_regional_source` and `render_regional` do not yet exist and `build_outputs` has no Regional paths.

- [ ] **Step 5: Commit the test contract and source fixture**

```bash
git add tests/test_generate_rules.py Rules/Source/Regional/routing.list
git commit -m "test: specify regional routing outputs"
```

### Task 2: Implement Regional parsing, validation, grouping, and rendering

**Files:**
- Modify: `tools/generate_rules.py`
- Test: `tests/test_generate_rules.py`

**Interfaces:**
- Consumes: `Rules/Source/Regional/routing.list` and the constants/tests from Task 1.
- Produces: `parse_regional_source(path) -> list[tuple[str, str, str]]`, `render_regional(rules, style, source_label) -> str`, and 32 Regional entries from `build_outputs(root)`.

- [ ] **Step 1: Add policy and validation constants**

Add these module-level constants without changing `RULESET_SPECS` or the existing `parse_source` behavior:

```python
REGIONAL_POLICY_FILES = {
    "香港节点": "hk",
    "香港优选": "hk-auto",
    "美国节点": "us",
    "美国优选": "us-auto",
    "日本节点": "jp",
    "日本优选": "jp-auto",
    "新加坡节点": "sg",
    "新加坡优选": "sg-auto",
}
REGIONAL_TYPES = {"DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}
KEYWORD_RE = re.compile(r"[a-z0-9][a-z0-9.-]*\Z")
```

Reuse `DOMAIN_RE` for suffix values and keep policy names in the source-facing Chinese form.

- [ ] **Step 2: Implement `parse_regional_source` atomically**

Read the file as UTF-8, skip blank/comment lines, split each line with `line.split(",")`, require exactly three fields, strip each field, and reject empty fields. Validate type, policy, suffix domain, or keyword with the constants above. Track `(rule_type, value)` in a set and reject any repeat, including repeats assigned to different policies.

After parsing all rows, compare every keyword value with every suffix value; if `keyword in suffix`, raise `ValueError` containing `overlapping keyword and suffix`. Return the original parsed list so source order is preserved.

- [ ] **Step 3: Implement `render_regional`**

Render the standard generated header and map each tuple as follows:

```python
if style == "classical":
    output.append(f"{rule_type},{value}")
elif style == "quantumultx":
    qx_type = {"DOMAIN-SUFFIX": "host-suffix", "DOMAIN-KEYWORD": "host-keyword"}[rule_type]
    output.append(f"{qx_type}, {value}, proxy")
```

The renderer receives only one policy bucket, so it must not emit the source policy field. For an empty bucket, return the generated header followed by one trailing newline.

- [ ] **Step 4: Extend `build_outputs` with stable 32-path Regional outputs**

Read the Regional source once, group tuples by `policy`, and for each client/style and each policy in `REGIONAL_POLICY_FILES` add the expected path even when the bucket is empty:

```python
regional_styles = {
    "Mihomo": "classical",
    "Surge": "classical",
    "QuantumultX": "quantumultx",
    "Loon": "classical",
}
for client, style in regional_styles.items():
    for policy, slug in REGIONAL_POLICY_FILES.items():
        outputs[root / "Rules" / client / "Regional" / f"{slug}.list"] = render_regional(
            grouped.get(policy, []), style, source_label
        )
```

Keep all existing `RULESET_SPECS` output construction unchanged and ensure the complete output map is constructed before `sync_outputs` writes anything.

- [ ] **Step 5: Run focused tests and generator check**

Run:

```bash
python3 -m unittest tests.test_generate_rules -v
python3 tools/generate_rules.py
python3 tools/generate_rules.py --check
```

Expected: all generator tests pass, 32 Regional files are created, and the second generator invocation reports no stale outputs.

- [ ] **Step 6: Commit the generator implementation and generated files**

```bash
git add tools/generate_rules.py tests/test_generate_rules.py Rules/Mihomo/Regional Rules/Surge/Regional Rules/QuantumultX/Regional Rules/Loon/Regional
git commit -m "feat: generate regional routing subscriptions"
```

### Task 3: Document the 32 Raw subscriptions and safe client integration

**Files:**
- Modify: `README.md`
- Modify: `Configs/tool_config/README.md`
- Test: `tests/test_generate_rules.py`

**Interfaces:**
- Consumes: the stable Regional output paths and policy mapping from Task 2.
- Produces: user-facing subscription tables and examples; no local configuration edits.

- [ ] **Step 1: Add a Regional section to the root README**

Add a table with one row per policy and four exact Raw URLs using this repository’s real base URL:

```text
https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/<Client>/Regional/<slug>.list
```

Use the exact client directory names `Mihomo`, `Surge`, `QuantumultX`, and `Loon`, and list all eight slugs: `hk`, `hk-auto`, `us`, `us-auto`, `jp`, `jp-auto`, `sg`, `sg-auto`. State that the source to edit is `Rules/Source/Regional/routing.list`, that `节点` and `优选` are logical strategy groups, and that this release does not modify local configs.

- [ ] **Step 2: Add client examples without embedding private information**

Document one example per client showing the resource binding:

```yaml
RULE-SET,https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/Mihomo/Regional/us.list,美国节点
```

Use the actual syntax already established in each existing configuration: Mihomo `rule-providers` plus `RULE-SET`, Surge `[Rule]`, Quantumult X `[filter_remote]` with `force-policy`, and Loon `[Remote Rule]` with `policy`. Do not add any node URL, password, UUID, token, or certificate content.

- [ ] **Step 3: Add documentation assertions**

Extend tests to assert the README contains the Regional source path, all eight slugs, and all four client directory names, and that the local configuration README warns that only remote rules are published.

- [ ] **Step 4: Run documentation and full regression checks**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: all tests pass, generated files are current, and no whitespace errors are reported.

- [ ] **Step 5: Commit documentation**

```bash
git add README.md Configs/tool_config/README.md tests/test_generate_rules.py
git commit -m "docs: publish regional rule subscriptions"
```

### Task 4: Verify workflow scope and sensitive-file safety

**Files:**
- Inspect: `.github/workflows/sync-generated-rules.yml`
- Inspect: `git diff` and generated Regional files
- Test: all repository tests

**Interfaces:**
- Consumes: the complete implementation and documentation from Tasks 1–3.
- Produces: verified local state ready for GitHub Actions; no workflow change is expected because the existing workflow already generates and commits `Rules/`.

- [ ] **Step 1: Confirm the existing workflow covers Regional outputs**

Verify `.github/workflows/sync-generated-rules.yml` still checks out `main`, runs `python3 tools/generate_rules.py`, runs the complete unittest suite, runs `--check`, and commits `Rules`. Do not broaden permissions or add secrets.

- [ ] **Step 2: Run the full verification suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check
```

- [ ] **Step 3: Scan the implementation diff for private data**

Run:

```bash
git diff HEAD~3 -- README.md Configs/tool_config/README.md Rules tools tests .github 2>/dev/null
rg -n -i "token=|password|secret:|uuid|BEGIN .*PRIVATE KEY|BEGIN .*CERTIFICATE|p12|CHANGE_ME|goodcloud|sanfennetwork|guiyun" -- README.md Configs/tool_config/README.md Rules tools tests .github
```

The scan may find existing documented placeholders such as `CHANGE_ME`; it must not find a newly added real subscription URL, credential, certificate, or private key. Do not include the workspace root configuration files in the staged paths.

- [ ] **Step 4: Review final status and commit history**

Run:

```bash
git status --short
git log --oneline -5
```

Confirm the only changed files are the Regional source/outputs, generator, tests, README documentation, and the existing design/plan commits; specifically confirm `mihomo_byallen.yaml`, `surge-Mac.conf`, `Surge-iPhone.conf`, `quantumult_byallen.conf`, and `allenloon.lcf` are absent from the diff.
