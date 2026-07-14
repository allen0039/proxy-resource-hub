# Publish Sanitized Tool Configs Design

## Goal

Publish five reusable, privacy-safe client configuration templates under
`Configs/tool_config/` without changing or copying the private source files into
Git. Preserve policy groups, public rule resources, local routing rules, comments,
and client-specific structure while removing credentials and personal endpoints.

## Published Files

- `Configs/tool_config/mihomo_allen.yaml`
- `Configs/tool_config/surge_mac_allen.conf`
- `Configs/tool_config/surge_iphone_allen.conf`
- `Configs/tool_config/quantumultx_allen.conf`
- `Configs/tool_config/loon_allen.lcf`
- `Configs/tool_config/README.md`

The README will state that the files are templates and identify the categories of
placeholders users must replace locally. It will not contain real subscription or
credential examples.

## Generation Boundary

`tools/sanitize_tool_configs.py` will read the five private files from an explicit
local source directory and write only sanitized outputs to the repository. The
source directory and source values are never recorded in generated files, tests,
logs, commit messages, or documentation. Diagnostics print filenames, section
names, field categories, and counts only.

The generator will fail closed when a required section cannot be recognized or a
known sensitive construct cannot be sanitized. It will use targeted text patches
for INI-style clients and a controlled YAML transformation for Mihomo, followed by
stable formatting and structural validation.

## Sanitization Rules

### Surge Mac and iPhone

- Replace subscription-bearing `policy-path` values with distinct
  `https://example.com/...` placeholders while retaining group names and options.
- Remove or placeholder any manual proxy server definitions and authentication.
- Remove MITM certificate payloads and passphrases; retain a comment explaining
  that certificates must be configured locally.
- Replace controller/API secrets if present.
- Retain public rule, script, panel, icon, and test URLs.

### Quantumult X

- Replace every `[server_remote]` subscription URL with a distinct example URL;
  retain tags and non-secret options.
- Remove active `[server_local]` node definitions and leave a local placeholder
  comment.
- Remove `[mitm]` passphrase and P12 material while retaining non-secret settings
  and a local-configuration comment.
- Retain public filter, rewrite, task, icon, and parser resources.

### Loon

- Replace every `[Remote Proxy]` subscription URL with a distinct example URL;
  retain entry names and non-secret options.
- Remove active `[Proxy]` node definitions and leave a local placeholder comment.
- Remove `[Mitm]` certificate payloads and passphrases while retaining non-secret
  settings and a local-configuration comment.
- Retain public rules, plugins, filters, icons, and scripts.

### Mihomo

- Rename private proxy-provider identifiers to generic stable names and update all
  corresponding `use` references.
- Replace proxy-provider subscription URLs with distinct example URLs.
- Preserve explicit proxy names needed by strategy groups, but replace server,
  UUID, password, key, and protocol-authentication values with typed placeholders.
- Replace controller/API secrets and remove certificate/private-key material.
- Retain public rule-provider URLs, policy groups, DNS/TUN behavior, and rules.

## Verification

`tests/test_sanitized_tool_configs.py` will verify:

- all five expected filenames exist and no private source filename is published;
- all placeholder-bearing subscription and credential locations are sanitized;
- no UUID, long certificate/base64 payload, controller secret, private-key block,
  or non-example subscription endpoint remains in a sensitive section;
- public rule resources and the `gongyiai`/`Domain` direct-routing contracts remain;
- INI sections, policy definitions, and active policy references remain coherent;
- Mihomo parses as YAML, has unique group/provider names, resolves group and
  `RULE-SET` references, and ends with `MATCH`;
- the existing rule generator and repository tests continue to pass.

The local publication run will additionally compare source-derived secret
fingerprints against all generated files and the staged Git diff without printing
the fingerprint inputs.

## Git and Publication Safety

Work occurs on `agent/sanitized-tool-configs`, based directly on the latest
`origin/main`, so the unrelated local-only commit on the existing `main` branch is
not included. Stage only the design, sanitizer, tests, README, and five sanitized
outputs. After tests and secret scans pass, push the branch commit to `origin/main`
without force and verify the remote commit and raw files. Do not create a pull
request unless requested.
