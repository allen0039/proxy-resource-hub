# Publish Sanitized Tool Configs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate, validate, commit, and publish five privacy-safe proxy client templates under `Configs/tool_config/`.

**Architecture:** A deterministic Python sanitizer reads private configs only from an explicit local directory, applies client-specific text transformations, and writes new public templates. Repository tests validate placeholders, structural references, public direct-rule integrations, YAML parsing, and leak-resistant output without requiring access to private sources in CI.

**Tech Stack:** Python 3 standard library, PyYAML 6.x for YAML validation, `unittest`, Git, GitHub Actions.

## Global Constraints

- Publish exactly `mihomo_allen.yaml`, `surge_mac_allen.conf`, `surge_iphone_allen.conf`, `quantumultx_allen.conf`, and `loon_allen.lcf` under `Configs/tool_config/`.
- Never modify, move, stage, or copy the five private source files into Git.
- Never print subscription URLs, proxy endpoints, UUIDs, passwords, controller secrets, P12 data, certificates, or private keys.
- Preserve public rule/script/plugin/provider URLs, strategy groups, local rules, comments, and client-specific ordering.
- Replace private subscription URLs with distinct `https://example.com/...` placeholders.
- Remove or placeholder local node authentication and MITM certificate material.
- Work only on `agent/sanitized-tool-configs`, based on `origin/main`; do not include the unrelated local-only `main` commit.
- Push to `origin/main` without force and do not create a pull request.

---

## File Responsibilities

- `tools/sanitize_tool_configs.py`: client-specific sanitization, fail-closed validation, CLI generation.
- `tests/test_sanitized_tool_configs.py`: synthetic unit tests and committed-output privacy/structure contract.
- `requirements-test.txt`: PyYAML test dependency.
- `.github/workflows/validate-rules.yml`: install test dependency before repository tests.
- `Configs/tool_config/*.conf|*.lcf|*.yaml`: generated public templates only.
- `Configs/tool_config/README.md`: placeholder and local setup guidance.

### Task 1: Define the Sanitizer Contract and Verify RED

**Files:**
- Create: `tests/test_sanitized_tool_configs.py`
- Create: `requirements-test.txt`
- Modify: `.github/workflows/validate-rules.yml`
- Test: `tests/test_sanitized_tool_configs.py`

**Interfaces:**
- Consumes: no private files; all unit fixtures use fake values.
- Produces: required functions `sanitize_surge(text, slug)`, `sanitize_quantumultx(text)`, `sanitize_loon(text)`, `sanitize_mihomo(text)`, `validate_sanitized_outputs(outputs)`, and `generate(source_dir, output_dir)`.

- [ ] **Step 1: Add a loader and synthetic secret fixtures**

Create a test loader matching the existing repository pattern:

```python
ROOT = Path(__file__).resolve().parents[1]
SANITIZER_PATH = ROOT / "tools" / "sanitize_tool_configs.py"

def load_sanitizer():
    if not SANITIZER_PATH.exists():
        raise AssertionError("tool config sanitizer is not implemented")
    spec = importlib.util.spec_from_file_location("sanitize_tool_configs", SANITIZER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module
```

Synthetic fixtures must use only obvious fake values such as
`https://private.invalid/sub?token=FAKE_TOKEN`, `FAKE-UUID`,
`FAKE-P12-BASE64`, and `FAKE-PASSWORD`.

- [ ] **Step 2: Add client-specific failing tests**

Add these exact test methods:

```python
test_surge_replaces_policy_paths_and_mitm_material()
test_quantumultx_replaces_remote_servers_and_removes_local_nodes()
test_loon_replaces_remote_proxies_and_mitm_material()
test_mihomo_renames_providers_and_replaces_secrets()
test_validator_rejects_a_private_endpoint()
test_committed_outputs_are_safe_and_structurally_complete()
```

Each synthetic test must assert that fake secret literals disappear, distinct
example placeholders exist, public rule URLs remain byte-identical, and policy
or provider references still resolve.

- [ ] **Step 3: Add the YAML test dependency**

Create `requirements-test.txt`:

```text
PyYAML>=6.0,<7
```

In `.github/workflows/validate-rules.yml`, add before the unittest step:

```yaml
      - name: Install test dependencies
        run: python3 -m pip install -r requirements-test.txt
```

- [ ] **Step 4: Run the new tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_sanitized_tool_configs -v
```

Expected: failure stating `tool config sanitizer is not implemented`; no private
source file is opened.

- [ ] **Step 5: Commit the test contract**

```bash
git add tests/test_sanitized_tool_configs.py requirements-test.txt .github/workflows/validate-rules.yml
git commit -m "Test sanitized tool config publishing"
```

### Task 2: Implement Client-Specific Sanitization

**Files:**
- Create: `tools/sanitize_tool_configs.py`
- Test: `tests/test_sanitized_tool_configs.py`

**Interfaces:**
- Consumes: `str` config text and an explicit `Path` source directory.
- Produces: sanitized UTF-8 text ending in one newline and an output map `dict[str, str]`.

- [ ] **Step 1: Add shared INI helpers**

Implement:

```python
OUTPUT_NAMES = {
    "mihomo_byallen-nokey.yaml": "mihomo_allen.yaml",
    "surge-Mac.conf": "surge_mac_allen.conf",
    "Surge-iPhone.conf": "surge_iphone_allen.conf",
    "quantumult_byallen.conf": "quantumultx_allen.conf",
    "allenloon.lcf": "loon_allen.lcf",
}

def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"

def section_name(line: str) -> str | None:
    stripped = line.strip()
    return stripped[1:-1].strip().casefold() if stripped.startswith("[") and stripped.endswith("]") else None

def example_url(client: str, category: str, index: int, suffix: str = "txt") -> str:
    return f"https://example.com/{client}/{category}-{index}.{suffix}"
```

All replacements must preserve comments, unrelated lines, and section ordering.

- [ ] **Step 2: Implement Surge sanitization**

`sanitize_surge(text, slug)` must:

- replace each `policy-path=...` value with a distinct example URL;
- remove active `ca-passphrase` and `ca-p12` lines from `[MITM]`;
- insert `# Configure MITM certificate and passphrase locally.` once;
- replace values for `http-api`, `http-api-tls`, `external-controller-access`,
  and `secret` keys if present;
- leave public `[Rule]`, `[Script]`, `[Panel]`, and icon URLs unchanged.

- [ ] **Step 3: Implement Quantumult X and Loon sanitization**

`sanitize_quantumultx(text)` must replace the leading URL of every active
`[server_remote]` entry, comment out active `[server_local]` entries with a single
local-node placeholder comment, and remove `passphrase`/`p12` values from
`[mitm]`.

`sanitize_loon(text)` must replace the URL following each entry name in
`[Remote Proxy]`, remove active `[Proxy]` entries with a single placeholder
comment, and remove `ca-p12`/`ca-passphrase` from `[Mitm]`.

Both functions retain tags, options, public filter/rule/plugin URLs, policy names,
and local rules unchanged.

- [ ] **Step 4: Implement Mihomo text sanitization**

`sanitize_mihomo(text)` must:

- discover active top-level `proxy-providers` in order and map them to
  `subscription_1`, `subscription_2`, ...;
- update provider keys, anchors, and exact `use` list items;
- replace only provider subscription URLs, including commented provider examples,
  while preserving nested health-check URLs;
- replace top-level `secret:` with `secret: CHANGE_ME`;
- replace sensitive scalar keys under explicit proxy entries (`server`, `uuid`,
  `password`, `private-key`, `certificate`, `token`, `key`) with type-compatible
  placeholders while keeping proxy names and types;
- preserve rule-provider URLs and all rules exactly.

- [ ] **Step 5: Implement fail-closed validation and CLI**

Implement:

```python
class SanitizationError(ValueError):
    pass

def validate_sanitized_outputs(outputs: dict[str, str]) -> None:
    expected = set(OUTPUT_NAMES.values())
    if set(outputs) != expected:
        raise SanitizationError("generated filename set does not match contract")
    for filename, text in outputs.items():
        validate_common_patterns(filename, text)
        validate_client_structure(filename, text)

def generate(source_dir: Path, output_dir: Path) -> dict[str, str]:
    sanitizers = {
        "surge-Mac.conf": lambda text: sanitize_surge(text, "surge-mac"),
        "Surge-iPhone.conf": lambda text: sanitize_surge(text, "surge-iphone"),
        "quantumult_byallen.conf": sanitize_quantumultx,
        "allenloon.lcf": sanitize_loon,
        "mihomo_byallen-nokey.yaml": sanitize_mihomo,
    }
    outputs = {
        OUTPUT_NAMES[source_name]: sanitizers[source_name](
            (source_dir / source_name).read_text(encoding="utf-8")
        )
        for source_name in OUTPUT_NAMES
    }
    validate_sanitized_outputs(outputs)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in outputs.items():
        (output_dir / filename).write_text(text, encoding="utf-8")
    return outputs
```

Implement the common validator with explicit patterns:

```python
UUID_RE = re.compile(
    r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b"
)
PEM_MARKERS = ("BEGIN PRIVATE KEY", "BEGIN CERTIFICATE")
LONG_BASE64_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{256,}={0,2}")

def validate_common_patterns(filename: str, text: str) -> None:
    if UUID_RE.search(text):
        raise SanitizationError(f"{filename}: UUID remains")
    if any(marker in text for marker in PEM_MARKERS):
        raise SanitizationError(f"{filename}: certificate material remains")
    if LONG_BASE64_RE.search(text):
        raise SanitizationError(f"{filename}: long base64 material remains")
```

`validate_client_structure(filename, text)` selects the client by filename,
requires its expected section headings, verifies that sensitive sections contain
only `example.com` subscription URLs and approved placeholder fields, and checks
that every active rule policy resolves to a defined policy or client builtin. For
Mihomo it additionally uses `yaml.safe_load`, requires mapping/list types, unique
proxy group and provider names, complete explicit group references, complete
`RULE-SET` provider references, and a final `MATCH` rule. Both validators raise
only `SanitizationError` with filename, category, and line number.

Validation rejects UUIDs, PEM/private-key markers, certificate-sized base64 runs,
non-placeholder URLs in sensitive subscription sections, non-placeholder secret
values, and missing expected sections. Error messages contain only output filename,
section, field category, and line number.

The CLI accepts required `--source-dir` and optional
`--output-dir` (default `Configs/tool_config`), writes with UTF-8 and one final
newline, and prints only `updated: <relative output filename>`.

- [ ] **Step 6: Run synthetic tests and verify GREEN**

```bash
python3 -m unittest tests.test_sanitized_tool_configs -v
```

Expected: the five synthetic tests pass; the committed-output test may skip only
until all five generated files exist.

- [ ] **Step 7: Commit the sanitizer**

```bash
git add tools/sanitize_tool_configs.py
git commit -m "Add tool config sanitizer"
```

### Task 3: Generate and Validate the Public Templates

**Files:**
- Create: `Configs/tool_config/mihomo_allen.yaml`
- Create: `Configs/tool_config/surge_mac_allen.conf`
- Create: `Configs/tool_config/surge_iphone_allen.conf`
- Create: `Configs/tool_config/quantumultx_allen.conf`
- Create: `Configs/tool_config/loon_allen.lcf`
- Create: `Configs/tool_config/README.md`
- Modify: `tests/test_sanitized_tool_configs.py`

**Interfaces:**
- Consumes: `generate(source_dir, output_dir)` from Task 2.
- Produces: committed public templates that pass CI without private sources.

- [ ] **Step 1: Generate the five outputs locally**

Set `PRIVATE_CONFIG_DIR` only in the shell environment and run:

```bash
python3 tools/sanitize_tool_configs.py \
  --source-dir "$PRIVATE_CONFIG_DIR" \
  --output-dir Configs/tool_config
```

Expected: exactly five `updated:` lines containing public output filenames only.

- [ ] **Step 2: Add the README**

Document the five client mappings, placeholder categories, and this warning:

```text
These files are sanitized templates. Replace example subscription URLs,
CHANGE_ME values, local nodes, and MITM certificates only in your private copy.
Never commit the completed private copy.
```

Document that `gongyiai` and `Domain` remain direct and that public rule resources
are intentionally retained.

- [ ] **Step 3: Make the committed-output test mandatory**

Remove any temporary skip and assert:

- exact output filename set;
- no source filenames such as `surge-Mac.conf` or `mihomo_byallen-nokey.yaml`;
- each subscription placeholder uses `example.com`;
- no active P12/passphrase/local-node secret remains;
- the five configs retain `gongyiai` and `Domain` direct routing;
- Mihomo parses through `yaml.safe_load`, provider/group names are unique, all
  explicit group and `RULE-SET` references resolve, and the final rule is `MATCH`.

- [ ] **Step 4: Compare source secret fingerprints without disclosure**

Run a local diagnostic that extracts known sensitive source values, hashes them in
memory, and reports only:

```text
source_secret_categories=<count>
generated_secret_matches=0
staged_secret_matches=0
```

Any non-zero match blocks staging and publication.

- [ ] **Step 5: Run all repository verification**

```bash
python3 -m unittest discover -s tests -v
python3 tools/generate_rules.py --check
git diff --check
```

Expected: every test passes, generated rules have no drift, and Git whitespace
validation is clean.

- [ ] **Step 6: Commit generated templates and documentation**

```bash
git add Configs/tool_config tests/test_sanitized_tool_configs.py
git diff --cached --check
git commit -m "Publish sanitized tool configs"
```

### Task 4: Final Scope Review and GitHub Publication

**Files:**
- Verify only: design, plan, sanitizer, tests, dependency/workflow, README, and five outputs.

**Interfaces:**
- Consumes: green Task 3 branch state.
- Produces: a non-force fast-forward update of `origin/main` and verified raw files.

- [ ] **Step 1: Confirm staged and committed scope**

```bash
git status -sb
git diff --stat origin/main...HEAD
git log --oneline origin/main..HEAD
```

Reject publication if any private source filename, unrelated local-main commit, or
file outside the approved scope appears.

- [ ] **Step 2: Run a final secret scan over every commit diff**

Scan `git diff --binary origin/main...HEAD` for subscription-token parameters,
UUIDs, passwords, P12/certificate material, private keys, non-placeholder sensitive
URLs, and source-secret fingerprints. Print only category counts; all must be zero.

- [ ] **Step 3: Fetch and confirm fast-forward safety**

```bash
git fetch origin
git merge-base --is-ancestor origin/main HEAD
```

If the second command fails, rebase the publication branch onto the new
`origin/main`, rerun the complete verification, and repeat the scope/secret scans.

- [ ] **Step 4: Push without force**

```bash
git push origin HEAD:main
```

Expected: a normal fast-forward push; never add `--force` or `--force-with-lease`.

- [ ] **Step 5: Verify GitHub publication**

Verify `origin/main` equals local `HEAD`, the GitHub Contents API exposes all six
`Configs/tool_config/` files, each raw file hash equals its local file, old private
source filenames are absent, and the `Validate rules` workflow succeeds.

- [ ] **Step 6: Preserve the private workspace**

Confirm the five original files remain outside Git and byte-for-byte unchanged
from their pre-generation hashes. Do not delete the isolated worktree until the
user has inspected the published files.
