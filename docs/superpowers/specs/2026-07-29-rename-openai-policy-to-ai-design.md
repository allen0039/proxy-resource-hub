# Rename the `OpenAI` Policy Group to `AI`

## Goal

Rename the maintained AI routing policy group from `OpenAI` to `AI` across all
five private client configurations and their five public sanitized templates.
Every active rule that currently selects the `OpenAI` policy must select `AI`
after the migration.

## Scope

Update the policy definition and policy references in:

- `mihomo_byallen.yaml`
- `surge-Mac.conf`
- `Surge-iPhone.conf`
- `quantumult_byallen.conf`
- `allenloon.lcf`
- the five corresponding files under `Configs/tool_config/`

For Quantumult X, change both the visible remote-rule label and its policy:

```text
tag=OpenAI, force-policy=OpenAI
```

becomes:

```text
tag=AI, force-policy=AI
```

Update current tests and public documentation where `OpenAI` specifically
means the maintained policy-group name.

## Values that must remain unchanged

This is not a global text replacement. Keep `OpenAI` when it identifies the
service or an external resource, including:

- `openai.com` and related domains;
- third-party paths such as `/OpenAI/OpenAI.list`;
- icon paths such as `OpenAI.png`;
- generated rule comments such as `# OpenAI / ChatGPT`;
- historical entries in `jiyi.md`.

The existing `direct-ai` rule-set identifier also remains unchanged.

## Client behavior

- Mihomo: rename the proxy-group `name` to `AI` and change every local and
  `RULE-SET` policy target from `OpenAI` to `AI`.
- Surge Mac and iPhone: rename the `[Proxy Group]` entry to `AI` and update
  every local and remote rule policy target.
- Quantumult X: rename the `static` policy to `AI`, update local rule targets,
  and change the OpenAI remote resource to `tag=AI, force-policy=AI` while
  retaining its third-party URL.
- Loon: rename the proxy group to `AI` and update local and remote rule policy
  targets while retaining `tag=AI`.

Group candidates, ordering, icons, rule ordering, and routing behavior remain
unchanged.

## Sanitized templates

Update the five private configurations first, then run
`tools/sanitize_tool_configs.py` to regenerate the public templates. The
sanitizer continues replacing subscriptions, credentials, certificates,
tokens, UUIDs, and private nodes; it must not copy private values into the
repository.

## Documentation and tests

Update the main README and `Configs/tool_config/README.md` where the maintained
business policy is named `OpenAI`. Descriptions of OpenAI as a service remain
unchanged.

Add or update focused private tests to verify:

- each client defines the `AI` policy exactly once;
- active local and remote rules target `AI`;
- no active policy definition or policy target still uses `OpenAI`;
- Quantumult X uses `tag=AI, force-policy=AI`;
- Mihomo rule references resolve to an existing `AI` proxy group.

Update repository sanitizer tests to enforce the same contract in all five
public templates.

Run the focused private tests and the complete repository test suite. The
private workspace has unrelated pre-existing full-suite failures; they remain
out of scope and must not cause unrelated policy changes.

## Publication

Publish the repository changes directly to `main` with a normal fast-forward
push. Do not create or push a feature branch. Keep the private configurations
local and publish only their sanitized derivatives.
