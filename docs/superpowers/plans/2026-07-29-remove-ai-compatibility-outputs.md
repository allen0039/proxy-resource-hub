# Remove `Rules/AI` Compatibility Outputs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the two obsolete generic AI rule outputs and prevent local and GitHub Actions generation from recreating them.

**Architecture:** Keep `Rules/Source/AI/` as the canonical source and retain all four client-specific output families. Remove only the AI compatibility-directory setting and tracked `Rules/AI` files; keep the independent shopping compatibility output unchanged.

**Tech Stack:** Python 3 standard library, `unittest`, GitHub Actions, Git.

## Global Constraints

- Delete only `Rules/AI/ai.list` and `Rules/AI/direct-ai.list`.
- Keep `Rules/shop/shopping.list`.
- Keep both AI sources and all eight client-specific AI outputs.
- Do not modify private or sanitized client configurations.
- Update GitHub `main` only; do not create or push a feature branch.
- Never force-push.

---

### Task 1: Stop generating the generic AI outputs

**Files:**
- Modify: `tests/test_generate_rules.py:113-130`
- Modify: `tools/generate_rules.py:9-15`
- Delete: `Rules/AI/ai.list`
- Delete: `Rules/AI/direct-ai.list`

**Interfaces:**
- Consumes: `RULESET_SPECS` tuples shaped as `(source_directory: str, ruleset_name: str, compatibility_directory: str | None)`.
- Produces: 21 generated output paths: eight client-specific AI outputs, four Personal outputs, four PT outputs, four client-specific shopping outputs, and one generic shopping output.

- [ ] **Step 1: Change the output-map test to require removal**

Replace the count and AI compatibility assertions in
`test_output_map_contains_all_expected_files` with:

```python
self.assertEqual(21, len(outputs))
for client in ("Mihomo", "Surge", "QuantumultX", "Loon"):
    for ruleset in ("ai", "direct-ai"):
        expected = ROOT / "Rules" / client / "AI" / f"{ruleset}.list"
        self.assertIn(expected, outputs)

for ruleset in ("ai", "direct-ai"):
    retired = ROOT / "Rules" / "AI" / f"{ruleset}.list"
    self.assertNotIn(retired, outputs)
    self.assertFalse(retired.exists())

compatibility = ROOT / "Rules" / "shop" / "shopping.list"
self.assertIn(compatibility, outputs)
self.assertTrue(compatibility.exists())
```

This test catches either AI entry regaining a compatibility directory, either
retired file being committed again, or accidental removal of the shopping
compatibility output.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_output_map_contains_all_expected_files \
  -v
```

Expected: FAIL because the current generator still returns 23 outputs and both
`Rules/AI` files still exist.

- [ ] **Step 3: Remove AI compatibility-directory generation**

Change only the two AI specifications:

```python
RULESET_SPECS = (
    ("AI", "ai", None),
    ("AI", "direct-ai", None),
    ("Personal", "Domain", None),
    ("PT", "Domain", None),
    ("shop", "shopping", "shop"),
)
```

Do not change `build_outputs`, `sync_outputs`, or the shopping specification.

- [ ] **Step 4: Delete the two tracked compatibility files**

Delete exactly:

```text
Rules/AI/ai.list
Rules/AI/direct-ai.list
```

Do not delete `Rules/Source/AI/`, any `Rules/<client>/AI/` file, or
`Rules/shop/shopping.list`.

- [ ] **Step 5: Run the focused and complete generator tests and verify GREEN**

Run:

```bash
python3 -m unittest \
  tests.test_generate_rules.RuleGeneratorTests.test_output_map_contains_all_expected_files \
  -v
python3 -m unittest tests.test_generate_rules -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: 1 focused test and all 11 generator tests pass; the generator check
reports no drift; Git reports no whitespace errors.

### Task 2: Remove public compatibility documentation

**Files:**
- Modify: `README.md:244-252`
- Modify: `README.md:300-317`

**Interfaces:**
- Consumes: the output paths finalized in Task 1.
- Produces: public documentation that lists only existing compatibility paths and directories.

- [ ] **Step 1: Remove the two retired links**

In `README.md` under `### 兼容地址`, delete:

```markdown
- [Rules/AI/ai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/ai.list)
- [Rules/AI/direct-ai.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/AI/direct-ai.list)
```

Keep:

```markdown
- [Rules/shop/shopping.list](https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/Rules/shop/shopping.list)
```

- [ ] **Step 2: Remove the obsolete directory-tree entry**

Delete this line from the README directory tree:

```text
├── AI/                      # 旧订阅地址兼容层
```

Keep the `Source`, `Mihomo`, `Surge`, `QuantumultX`, `Loon`, `shop`, and `SKK`
descriptions as they exist. Adjust tree connectors only if necessary for valid
visual hierarchy.

- [ ] **Step 3: Verify references and exact retained outputs**

Run:

```bash
rg -n "Rules/AI/" README.md Rules Configs tools .github || true
test -f Rules/shop/shopping.list
test -f Rules/Source/AI/ai.txt
test -f Rules/Source/AI/direct-ai.txt
```

Expected: no active `Rules/AI/` reference is found; all three required retained
files exist.

- [ ] **Step 4: Run the complete repository suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: all 39 repository tests pass and no generation or whitespace drift
is reported.

- [ ] **Step 5: Review and commit the implementation**

Run:

```bash
git status --short
git diff --stat
git diff -- Rules README.md tools/generate_rules.py tests/test_generate_rules.py
```

Confirm the diff contains only the two deletions plus generator, test, and
README changes. Then commit:

```bash
git add Rules/AI README.md tools/generate_rules.py tests/test_generate_rules.py
git commit -m "refactor: remove generic AI rule outputs"
```

### Task 3: Verify and publish to `main`

**Files:**
- Verify: the complete detached commit chain since `origin/main`
- Publish: GitHub `main` only

**Interfaces:**
- Consumes: a clean detached worktree whose base is the current `origin/main`.
- Produces: retired generic URLs returning 404, dedicated URLs remaining live, and successful no-op generation automation.

- [ ] **Step 1: Confirm fast-forward safety**

Run:

```bash
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

Expected: exit status 0. If it fails, stop and move the commits onto the new
`origin/main`; never force-push.

- [ ] **Step 2: Run fresh pre-push verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check origin/main..HEAD
git status --short --branch
git log --oneline origin/main..HEAD
```

Expected: all tests pass, no drift or whitespace errors exist, the worktree is
clean, and the commit list contains only the approved design, plan, and
implementation.

- [ ] **Step 3: Push the detached commit chain directly to `main`**

Run:

```bash
git push origin HEAD:main
```

Expected: a normal fast-forward update. Do not push any named branch.

- [ ] **Step 4: Verify raw URL behavior**

Confirm both retired URLs return 404:

```text
Rules/AI/ai.list
Rules/AI/direct-ai.list
```

Confirm these remain available with HTTP 200:

```text
Rules/Mihomo/AI/ai.list
Rules/Mihomo/AI/direct-ai.list
Rules/Surge/AI/ai.list
Rules/Surge/AI/direct-ai.list
Rules/QuantumultX/AI/ai.list
Rules/QuantumultX/AI/direct-ai.list
Rules/Loon/AI/ai.list
Rules/Loon/AI/direct-ai.list
Rules/shop/shopping.list
```

- [ ] **Step 5: Verify automatic generation**

Wait for the `Sync generated rules` workflow for the published SHA. Confirm:

- the workflow completes successfully;
- its 39-test suite passes;
- `python3 tools/generate_rules.py --check` passes;
- the log says `Generated files are already up to date.`;
- remote `main` remains on the published SHA, proving no follow-up generated
  commit was needed.
