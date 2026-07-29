# Rename the `OpenAI` Policy Group to `AI` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the active AI policy group and every policy reference from `OpenAI` to `AI` in five private configurations and five sanitized public templates.

**Architecture:** Treat `OpenAI` as a semantic policy name, not a global string. Update private configurations first under a focused cross-client test, regenerate the public templates through the existing sanitizer, then enforce the same contract in repository tests while preserving third-party URLs, icon names, service names, and generated rule comments.

**Tech Stack:** Python 3, PyYAML 6.x, `unittest`, Mihomo YAML, Surge/Quantumult X/Loon configuration formats, GitHub Actions.

## Global Constraints

- Rename only the maintained policy group and policy targets from `OpenAI` to `AI`.
- Change Quantumult X to `tag=AI, force-policy=AI`.
- Preserve `/OpenAI/OpenAI.list`, `OpenAI.png`, OpenAI service/domain names, generated rule comments, historical notes, and `direct-ai`.
- Preserve group candidates, ordering, icons, rule ordering, and routing behavior.
- Keep private configuration values local; publish only sanitizer-produced templates.
- Do not fix unrelated failures in the private workspace's pre-existing full test suite.
- Update GitHub `main` only; do not create or push a feature branch.

---

### Task 1: Rename the policy in all five private configurations

**Files:**
- Create: `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_ai_policy_group.py`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/mihomo_byallen.yaml:161,292-295,377,380`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/surge-Mac.conf:65,209-213,309-310`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/Surge-iPhone.conf:66,205-209,301-302`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/quantumult_byallen.conf:47,151,285-290`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/allenloon.lcf:61,191-195,259`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_config_alignment.py:110-115,1555-1568`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/tests/test_direct_ai_integration.py:76-81`
- Modify: `/Users/allen/Downloads/Agent_Worker/vpn/jiyi.md`

**Interfaces:**
- Consumes: five active private configuration files.
- Produces: five configurations that define exactly one `AI` policy and contain no active `OpenAI` policy target.

- [ ] **Step 1: Add a failing cross-client policy test**

Create `tests/test_ai_policy_group.py` with:

```python
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class AiPolicyGroupTest(unittest.TestCase):
    def test_surge_configs_use_ai_policy(self):
        for name in ("surge-Mac.conf", "Surge-iPhone.conf"):
            text = read(name)
            with self.subTest(name=name):
                self.assertEqual(1, len(re.findall(r"(?m)^AI = select,", text)))
                self.assertNotRegex(text, r"(?m)^OpenAI = ")
                self.assertNotRegex(text, r"(?m)^[^#\n]*,OpenAI(?:,|$)")
                self.assertIn("OpenAI.png", text)

    def test_quantumult_x_uses_ai_policy_and_tag(self):
        text = read("quantumult_byallen.conf")
        self.assertEqual(1, len(re.findall(r"(?m)^static=AI,", text)))
        self.assertNotRegex(text, r"(?m)^static=OpenAI,")
        self.assertNotIn("force-policy=OpenAI", text)
        self.assertNotRegex(text, r"(?m)^[^#\n]*,\s*OpenAI$")
        self.assertIn(
            "/OpenAI/OpenAI.list, tag=AI, force-policy=AI,",
            text,
        )
        self.assertIn("OpenAI.png", text)

    def test_loon_uses_ai_policy(self):
        text = read("allenloon.lcf")
        self.assertEqual(1, len(re.findall(r"(?m)^AI = select,", text)))
        self.assertNotRegex(text, r"(?m)^OpenAI = ")
        self.assertNotIn("policy=OpenAI", text)
        self.assertNotRegex(text, r"(?m)^[^#\n]*,OpenAI(?:,|$)")
        self.assertIn("policy=AI, tag=AI", text)

    def test_mihomo_uses_ai_policy(self):
        parsed = yaml.safe_load(read("mihomo_byallen.yaml"))
        groups = [group["name"] for group in parsed["proxy-groups"]]
        self.assertEqual(1, groups.count("AI"))
        self.assertNotIn("OpenAI", groups)
        rule_targets = {
            parts[2]
            for rule in parsed["rules"]
            if isinstance(rule, str)
            and len(parts := [part.strip() for part in rule.split(",")]) >= 3
        }
        self.assertIn("AI", rule_targets)
        self.assertNotIn("OpenAI", rule_targets)
        self.assertIn(
            "https://raw.githubusercontent.com/erdongchanyo/icon/"
            "main/Policy-Filter/OpenAI.png",
            read("mihomo_byallen.yaml"),
        )


if __name__ == "__main__":
    unittest.main()
```

The break this catches is a client defining `AI` without updating all policy
targets, or an accidental global replacement damaging external OpenAI paths.

- [ ] **Step 2: Run the focused test and verify RED**

Run from `/Users/allen/Downloads/Agent_Worker/vpn`:

```bash
python3 -m unittest tests.test_ai_policy_group -v
```

Expected: FAIL in all four test methods because the active group is still
named `OpenAI`.

- [ ] **Step 3: Update the private policy definitions and references**

Apply these semantic changes:

```text
Mihomo:
  name: OpenAI                         → name: AI
  policy target ,OpenAI                → ,AI

Surge Mac/iPhone:
  OpenAI = select,                     → AI = select,
  local/remote rule target ,OpenAI     → ,AI

Quantumult X:
  static=OpenAI,                       → static=AI,
  tag=OpenAI, force-policy=OpenAI      → tag=AI, force-policy=AI
  local rule target , OpenAI           → , AI
  comment "OpenAI 与 Google 远程规则"  → "AI 与 Google 远程规则"

Loon:
  OpenAI = select,                     → AI = select,
  local rule target ,OpenAI            → ,AI
  remote policy=OpenAI                 → policy=AI
```

Do not alter `/OpenAI/OpenAI.list`, `OpenAI.png`, `openai.com`, or
`direct-ai`.

- [ ] **Step 4: Update existing private tests and current maintenance notes**

Change:

```python
"🤖 AI": "OpenAI"
```

to:

```python
"🤖 AI": "AI"
```

Change both existing Mihomo ordering references:

```python
"RULE-SET,ai,OpenAI"
```

to:

```python
"RULE-SET,ai,AI"
```

Append a dated `AI 策略组统一命名` entry to `jiyi.md` that records the five
clients and the distinction between policy names and external OpenAI resource
names. Do not rewrite historical entries.

- [ ] **Step 5: Run focused private verification and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_ai_policy_group -v
python3 -m unittest tests.test_direct_ai_integration -v
python3 -m unittest \
  tests.test_config_alignment.ConfigAlignmentTest.test_googleapis_uses_service_policy_groups \
  -v
```

Expected: the new 4 tests and direct-AI integration tests pass. The selected
alignment test must pass; unrelated baseline failures are not part of this
command.

### Task 2: Regenerate and enforce the five sanitized public templates

**Files:**
- Modify: `tests/test_sanitized_tool_configs.py`
- Regenerate: `Configs/tool_config/mihomo_allen.yaml`
- Regenerate: `Configs/tool_config/surge_mac_allen.conf`
- Regenerate: `Configs/tool_config/surge_iphone_allen.conf`
- Regenerate: `Configs/tool_config/quantumultx_allen.conf`
- Regenerate: `Configs/tool_config/loon_allen.lcf`

**Interfaces:**
- Consumes: the five private configurations updated in Task 1.
- Produces: five public templates with the same `AI` policy contract and no private values.

- [ ] **Step 1: Add a failing committed-template test**

Add this method to `SanitizedToolConfigTests`:

```python
def test_committed_configs_use_ai_policy_group(self):
    configs = {
        name: (OUTPUT_DIR / name).read_text(encoding="utf-8")
        for name in CONFIG_NAMES
    }

    for name in ("surge_mac_allen.conf", "surge_iphone_allen.conf"):
        with self.subTest(name=name):
            self.assertEqual(1, len(re.findall(r"(?m)^AI = select,", configs[name])))
            self.assertNotRegex(configs[name], r"(?m)^OpenAI = ")
            self.assertNotRegex(configs[name], r"(?m)^[^#\n]*,OpenAI(?:,|$)")

    qx = configs["quantumultx_allen.conf"]
    self.assertEqual(1, len(re.findall(r"(?m)^static=AI,", qx)))
    self.assertNotRegex(qx, r"(?m)^static=OpenAI,")
    self.assertNotIn("force-policy=OpenAI", qx)
    self.assertIn("/OpenAI/OpenAI.list, tag=AI, force-policy=AI,", qx)

    loon = configs["loon_allen.lcf"]
    self.assertEqual(1, len(re.findall(r"(?m)^AI = select,", loon)))
    self.assertNotRegex(loon, r"(?m)^OpenAI = ")
    self.assertNotIn("policy=OpenAI", loon)
    self.assertIn("policy=AI, tag=AI", loon)

    mihomo = yaml.safe_load(configs["mihomo_allen.yaml"])
    groups = [group["name"] for group in mihomo["proxy-groups"]]
    self.assertEqual(1, groups.count("AI"))
    self.assertNotIn("OpenAI", groups)
    targets = {
        parts[2]
        for rule in mihomo["rules"]
        if isinstance(rule, str)
        and len(parts := [part.strip() for part in rule.split(",")]) >= 3
    }
    self.assertIn("AI", targets)
    self.assertNotIn("OpenAI", targets)
```

- [ ] **Step 2: Run the committed-template test and verify RED**

Run:

```bash
/tmp/codex-direct-ai-venv-20260729/bin/python -m unittest \
  tests.test_sanitized_tool_configs.SanitizedToolConfigTests.test_committed_configs_use_ai_policy_group \
  -v
```

Expected: FAIL because the committed templates still define `OpenAI`.

- [ ] **Step 3: Regenerate sanitized templates**

Run:

```bash
/tmp/codex-direct-ai-venv-20260729/bin/python \
  tools/sanitize_tool_configs.py \
  --source-dir /Users/allen/Downloads/Agent_Worker/vpn \
  --output-dir Configs/tool_config
```

Expected: exactly five public templates are regenerated and validated without
printing private values.

- [ ] **Step 4: Run sanitizer and full repository tests and verify GREEN**

Run:

```bash
/tmp/codex-direct-ai-venv-20260729/bin/python -m unittest \
  tests.test_sanitized_tool_configs -v
/tmp/codex-direct-ai-venv-20260729/bin/python -m unittest discover -s tests -v
/tmp/codex-direct-ai-venv-20260729/bin/python tools/generate_rules.py --check
git diff --check
```

Expected: all sanitizer tests and at least 40 repository tests pass; generated
rules remain current and no whitespace error is reported.

### Task 3: Update public policy documentation

**Files:**
- Modify: `README.md:31-41,175-179`
- Modify: `Configs/tool_config/README.md:165-175`

**Interfaces:**
- Consumes: the final `AI` policy-group name.
- Produces: documentation that uses `AI` for the maintained policy while retaining OpenAI as a service name.

- [ ] **Step 1: Update the main README**

Change the AI service row to:

```markdown
| AI 服务 | OpenAI、Claude、Gemini 等 AI 服务 | `AI` 或自定义 AI 策略 |
```

In the business-policy list, change only the policy name from `OpenAI` to
`AI`. Keep `OpenAI` in service descriptions and links.

- [ ] **Step 2: Update the sanitized-config README**

Change the business-routing policy list from:

```text
Google、OpenAI、YouTube
```

to:

```text
Google、AI、YouTube
```

- [ ] **Step 3: Review semantic OpenAI occurrences**

Run:

```bash
rg -n "OpenAI" Configs README.md tests tools Rules .github
```

Classify every remaining match. It is allowed only when it is:

- an external URL or icon path;
- an OpenAI service/domain description or generated rule comment;
- a negative test assertion proving the old policy name is absent;
- a design or plan history reference.

No active policy definition or policy target may remain.

- [ ] **Step 4: Review and commit repository changes**

Run:

```bash
git status --short
git diff --stat
git diff -- Configs README.md tests/test_sanitized_tool_configs.py
```

Confirm no private configuration file appears and public config differences
contain only the semantic policy rename. Commit:

```bash
git add Configs README.md tests/test_sanitized_tool_configs.py
git commit -m "refactor: rename OpenAI policy group to AI"
```

### Task 4: Final verification and main-only publication

**Files:**
- Verify: the complete detached commit chain
- Verify locally: five private configurations and focused tests
- Publish: GitHub `main` only

**Interfaces:**
- Consumes: a clean detached worktree based on the current `origin/main`.
- Produces: synchronized private/public configurations and a successful no-op generation workflow.

- [ ] **Step 1: Re-fetch and confirm fast-forward safety**

Run:

```bash
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

Expected: exit status 0. If not, stop and move the commits onto the new
`origin/main`; never force-push.

- [ ] **Step 2: Run fresh repository and private verification**

In the repository:

```bash
/tmp/codex-direct-ai-venv-20260729/bin/python -m unittest discover -s tests -v
/tmp/codex-direct-ai-venv-20260729/bin/python tools/generate_rules.py --check
git diff --check origin/main..HEAD
git status --short --branch
git log --oneline origin/main..HEAD
```

In `/Users/allen/Downloads/Agent_Worker/vpn`:

```bash
python3 -m unittest tests.test_ai_policy_group -v
python3 -m unittest tests.test_direct_ai_integration -v
```

Expected: repository and focused private tests pass; the repository worktree is
clean and no private file is in the commit list.

- [ ] **Step 3: Push only to `main`**

Run:

```bash
git push origin HEAD:main
```

Expected: a normal fast-forward push with no named branch.

- [ ] **Step 4: Verify GitHub**

Confirm:

- remote `main` equals the published local SHA;
- all five public templates contain an `AI` policy definition;
- none contains an active `OpenAI` policy definition or target;
- the `Sync generated rules` workflow completes successfully;
- its tests and generator check pass;
- it reports `Generated files are already up to date.` and creates no follow-up commit.
