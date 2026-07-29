# Rename `gongyiai` to `direct-ai` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Atomically rename the maintained public rule set and all active private and sanitized client references from `gongyiai` to `direct-ai`.

**Architecture:** Keep the existing single-source rule generation architecture, but rename the source identifier in `RULESET_SPECS`; regenerate all five public outputs and explicitly remove the five retired outputs. Update the five private configurations first, then regenerate their five sanitized public counterparts so routing behavior stays aligned without exposing private values.

**Tech Stack:** Python 3 standard library, PyYAML 6.x, `unittest`, GitHub Actions, Mihomo YAML, Surge/Quantumult X/Loon configuration formats.

## Global Constraints

- Do not retain a `gongyiai` compatibility source, generated file, provider name, or raw subscription URL.
- Keep the rule contents unchanged.
- Keep the rule set routed through each client's direct policy.
- Keep the existing `Sync generated rules` workflow; make it generate `direct-ai` through `tools/generate_rules.py`.
- Update GitHub `main` only; do not create or push a feature branch.
- Do not commit any private client configuration or secret from `/Users/allen/Downloads/Agent_Worker/vpn`.
- Treat the 26 unrelated failures in the private configuration's pre-existing full test suite as baseline drift; do not change unrelated routing or policy ordering.

---

### Task 1: Rename the canonical rule set and generated outputs

**Files:**
- Rename: `Rules/Source/AI/gongyiai.txt` → `Rules/Source/AI/direct-ai.txt`
- Modify: `tools/generate_rules.py:9-15`
- Modify: `tests/test_generate_rules.py:113-125,232-261`
- Create through generator: `Rules/AI/direct-ai.list`
- Create through generator: `Rules/Mihomo/AI/direct-ai.list`
- Create through generator: `Rules/Surge/AI/direct-ai.list`
- Create through generator: `Rules/QuantumultX/AI/direct-ai.list`
- Create through generator: `Rules/Loon/AI/direct-ai.list`
- Delete: the corresponding five `gongyiai.list` files

**Interfaces:**
- Consumes: `RULESET_SPECS` tuples in the form `(source_directory: str, ruleset_name: str, compatibility_directory: str | None)`.
- Produces: five `direct-ai.list` paths whose contents are rendered from `Rules/Source/AI/direct-ai.txt`.

- [ ] **Step 1: Change generator tests to require the new name and reject the retired name**

Update the AI expectations to:

```python
for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
    for ruleset in ("ai", "direct-ai"):
        expected = ROOT / "Rules" / client / "AI" / f"{ruleset}.list"
        self.assertIn(expected, outputs)
    self.assertNotIn(
        ROOT / "Rules" / client / "AI" / "gongyiai.list",
        outputs,
    )

for ruleset in ("ai", "direct-ai"):
    legacy = ROOT / "Rules" / "AI" / f"{ruleset}.list"
    self.assertIn(legacy, outputs)
self.assertNotIn(ROOT / "Rules" / "AI" / "gongyiai.list", outputs)
```

Change the temporary source fixture from `("ai", "gongyiai")` to
`("ai", "direct-ai")`.

- [ ] **Step 2: Run the focused generator test and verify it fails**

Run:

```bash
python3 -m unittest tests.test_generate_rules.RuleGeneratorTests.test_output_map_contains_all_expected_files -v
```

Expected: FAIL because the generator still produces `gongyiai` paths.

- [ ] **Step 3: Rename the source identifier**

Move the source file without changing its contents and change the generator
specification to:

```python
RULESET_SPECS = (
    ("AI", "ai", "AI"),
    ("AI", "direct-ai", "AI"),
    ("Personal", "Domain", None),
    ("PT", "Domain", None),
    ("shop", "shopping", "shop"),
)
```

- [ ] **Step 4: Generate the five new files and remove the five retired files**

Run:

```bash
python3 tools/generate_rules.py
```

Then delete only:

```text
Rules/AI/gongyiai.list
Rules/Mihomo/AI/gongyiai.list
Rules/Surge/AI/gongyiai.list
Rules/QuantumultX/AI/gongyiai.list
Rules/Loon/AI/gongyiai.list
```

- [ ] **Step 5: Verify generation and source-content preservation**

Run:

```bash
python3 -m unittest tests.test_generate_rules -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: all generator tests pass, check mode reports no drift, and the only
rule-content differences are generated source-header/path changes.

- [ ] **Step 6: Commit the canonical rename**

```bash
git add Rules tools/generate_rules.py tests/test_generate_rules.py
git commit -m "refactor: rename gongyiai ruleset to direct-ai"
```

### Task 2: Update the five private client configurations

**Files:**
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/mihomo_byallen.yaml:378,444`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/surge-Mac.conf:306`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/Surge-iPhone.conf:298`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/quantumult_byallen.conf:148`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/allenloon.lcf:264`
- Rename: `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_gongyiai_integration.py` → `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_direct_ai_integration.py`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_config_alignment.py:413-416,2200-2203`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/jiyi.md`

**Interfaces:**
- Consumes: the five public `direct-ai.list` URLs created by Task 1.
- Produces: five active private clients that reference only the new URLs and retain direct routing.

- [ ] **Step 1: Rename and update the focused integration test**

Rename the test module and class to `DirectAiIntegrationTest`. Define the new
URLs with `DIRECT_AI` names, for example:

```python
SURGE_DIRECT_AI_URL = (
    "https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/"
    "Rules/Surge/AI/direct-ai.list"
)
```

For Mihomo, require:

```python
(
    MIHOMO_DIRECT_AI_URL,
    f'direct-ai: {{ <<: *class, url: "{MIHOMO_DIRECT_AI_URL}" }}',
    "- RULE-SET,direct-ai,DIRECT",
)
```

Update `test_config_alignment.py` to use `PUBLIC_DIRECT_AI_URL` and:

```python
expected_direct = {
    "direct-ai": PUBLIC_DIRECT_AI_URL,
    "personal_domain": PUBLIC_DOMAIN_URL,
}
```

Append a dated `direct-ai` rename record to `jiyi.md`; preserve historical
entries as history rather than rewriting them.

- [ ] **Step 2: Run the renamed focused test and verify it fails**

Run:

```bash
python3 -m unittest tests.test_direct_ai_integration -v
```

Expected: FAIL because the five private configurations still use the retired
URL/provider name.

- [ ] **Step 3: Update all five private configurations**

Apply these exact active-reference changes:

```text
Rules/Surge/AI/gongyiai.list
→ Rules/Surge/AI/direct-ai.list

Rules/QuantumultX/AI/gongyiai.list
→ Rules/QuantumultX/AI/direct-ai.list

Rules/Loon/AI/gongyiai.list
→ Rules/Loon/AI/direct-ai.list

RULE-SET,gongyiai,DIRECT
→ RULE-SET,direct-ai,DIRECT

gongyiai: { <<: *class, url: ".../Rules/Mihomo/AI/gongyiai.list" }
→ direct-ai: { <<: *class, url: ".../Rules/Mihomo/AI/direct-ai.list" }
```

Do not change the display tags `公益AI`, `force-policy=direct`, `policy=DIRECT`,
or any unrelated policy/group ordering.

- [ ] **Step 4: Verify the private direct-AI integration**

Run:

```bash
python3 -m unittest tests.test_direct_ai_integration -v
python3 -m unittest \
  tests.test_config_alignment.ConfigAlignmentTest.test_mihomo_yaml_and_provider_references \
  -v
```

Expected: the renamed integration test passes. In the broader alignment test,
the `direct-ai` provider assertion passes; any remaining failure must match the
documented pre-existing `personal_domain` policy-name drift.

- [ ] **Step 5: Confirm private values were not otherwise changed**

Run a diff limited to these files and confirm only the rule-set identifier,
URLs, renamed test symbols, and the new maintenance note changed:

```bash
git diff --no-index /dev/null /Users/allen/Downloads/Agent_Worker/vpn/tests/test_direct_ai_integration.py
```

Review the five private configuration diffs without printing or copying secret
values into the public repository.

### Task 3: Regenerate sanitized configurations and update public documentation

**Files:**
- Modify through sanitizer: `Configs/tool_config/mihomo_allen.yaml`
- Modify through sanitizer: `Configs/tool_config/surge_mac_allen.conf`
- Modify through sanitizer: `Configs/tool_config/surge_iphone_allen.conf`
- Modify through sanitizer: `Configs/tool_config/quantumultx_allen.conf`
- Modify through sanitizer: `Configs/tool_config/loon_allen.lcf`
- Modify: `tests/test_sanitized_tool_configs.py:248-255,307-340`
- Modify: `README.md:187-199,244-252`

**Interfaces:**
- Consumes: the five private configurations updated by Task 2 through
  `tools/sanitize_tool_configs.py --source-dir`.
- Produces: five privacy-safe public templates with the same `direct-ai`
  routing references.

- [ ] **Step 1: Update sanitized-output tests to require `direct-ai`**

Change the Mihomo sanitizer fixture and all committed-output assertions from
`gongyiai` to `direct-ai`. The direct assertions must include:

```python
self.assertRegex(outputs[name], r"direct-ai\.list,DIRECT(?:,|\n)")
self.assertRegex(
    outputs["quantumultx_allen.conf"],
    r"direct-ai\.list[^\n]*force-policy=direct",
)
self.assertRegex(
    outputs["loon_allen.lcf"],
    r"direct-ai\.list[^\n]*policy=DIRECT",
)
self.assertEqual(1, mihomo["rules"].count("RULE-SET,direct-ai,DIRECT"))
self.assertIn("direct-ai", mihomo["rule-providers"])
self.assertNotIn("gongyiai", "\n".join(outputs.values()))
```

- [ ] **Step 2: Run the committed-output test and verify it fails**

Run:

```bash
python3 -m unittest \
  tests.test_sanitized_tool_configs.SanitizedToolConfigTests.test_committed_outputs_are_safe_and_structurally_complete \
  -v
```

Expected: FAIL because committed sanitized configurations still use
`gongyiai`.

- [ ] **Step 3: Regenerate sanitized configurations from the private source**

Install `requirements-test.txt` in an isolated environment if PyYAML is not
available, then run:

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir /Users/allen/Downloads/Agent_Worker/vpn \
  --output-dir Configs/tool_config
```

Expected: exactly five public configuration files are regenerated; private
subscription endpoints, credentials, certificates, UUIDs, and tokens are
replaced by public placeholders.

- [ ] **Step 4: Update README subscription links**

Change all public rule links from `gongyiai.list` to `direct-ai.list`, including
the four-client subscription table and `Rules/AI/direct-ai.list` compatibility
path. Keep the human-facing description `公益 AI` and direct-policy guidance.

- [ ] **Step 5: Run sanitizer and repository tests**

Run:

```bash
python3 -m unittest tests.test_sanitized_tool_configs -v
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: all 39 or more repository tests pass, generated rules have no drift,
and no whitespace errors are reported.

- [ ] **Step 6: Scan the public diff for secrets and retired active references**

Run:

```bash
git diff -- Configs Rules README.md tools tests
git grep -n "gongyiai" -- \
  Rules Configs README.md tools tests .github ':!docs/superpowers/**'
```

Expected: the public diff contains only intended rule/config/documentation
changes, and `git grep` reports no active `gongyiai` reference.

- [ ] **Step 7: Commit public consumers and documentation**

```bash
git add Configs README.md tests/test_sanitized_tool_configs.py
git commit -m "docs: switch clients to direct-ai rules"
```

### Task 4: Final verification and main-only publication

**Files:**
- Verify: every file changed by Tasks 1-3
- Verify locally only: the five private configurations and their tests/notes

**Interfaces:**
- Consumes: the detached commit chain based on the latest `origin/main`.
- Produces: a fast-forward-only update of GitHub `main`; no remote feature branch.

- [ ] **Step 1: Re-fetch and confirm fast-forward safety**

Run:

```bash
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

Expected: exit status 0. If it fails, stop and rebase/cherry-pick onto the new
`origin/main` before publishing; never force-push.

- [ ] **Step 2: Run final repository verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check origin/main..HEAD
```

Expected: full pass with no generation or whitespace drift.

- [ ] **Step 3: Run final private scoped verification**

From `/Users/allen/Downloads/Agent_Worker/vpn`, run:

```bash
python3 -m unittest tests.test_direct_ai_integration -v
```

Then verify that active configuration/test references use `direct-ai`:

```bash
rg -n "gongyiai" \
  mihomo_byallen.yaml surge-Mac.conf Surge-iPhone.conf \
  quantumult_byallen.conf allenloon.lcf tests/test_direct_ai_integration.py
```

Expected: focused tests pass and the search returns no result. Historical
mentions in `jiyi.md` and the design/plan documents are allowed.

- [ ] **Step 4: Review the exact publication scope**

Run:

```bash
git status --short
git diff --stat origin/main..HEAD
git log --oneline origin/main..HEAD
```

Expected: no private files appear; the detached commit chain contains only the
design, plan, rule rename, generated files, sanitized templates, tests, and
README updates.

- [ ] **Step 5: Push only the detached commit chain to `main`**

Run only after verification:

```bash
git push origin HEAD:main
```

Expected: a normal fast-forward push. Do not push any named feature branch.

- [ ] **Step 6: Verify GitHub**

Confirm:

- remote `main` equals local `HEAD`;
- all five `direct-ai.list` raw URLs return the generated content;
- all five retired `gongyiai.list` raw URLs return 404;
- the `Sync generated rules` workflow completes successfully and does not
  recreate retired outputs.
