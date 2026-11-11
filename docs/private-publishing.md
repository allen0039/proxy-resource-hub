# Publish private configurations safely

Keep daily configurations outside this repository. Never place subscriptions,
certificates, private nodes, device addresses, or personal service domains in
tests or documentation.

The generator covers all eight templates, including the two variants without
Tailscale. It reads its publishing policy from
`SOURCE_DIR/.private/publish-privacy.json`, or from an explicit `--privacy-file`.
Keep that policy private and set its permissions to `0600`.

```json
{
  "private_domains": ["private-service.invalid"],
  "private_literals": ["PRIVATE_VALUE"]
}
```

Private domain rules are omitted from public templates. Other listed literals
cause generation to fail without printing their values. Put rules that must
remain local between `# LOCAL_ONLY_BEGIN` and `# LOCAL_ONLY_END` comments.
The generator never writes to the private source directory.

```sh
python3 tools/sanitize_tool_configs.py --source-dir /path/to/private-configs
python3 tools/sanitize_tool_configs.py --source-dir /path/to/private-configs --check
python3 tools/check_public_privacy.py
python3 -m unittest discover -s tests -v
```

Before committing, check the exact index with:

```sh
python3 tools/check_public_privacy.py --staged
```

The public Personal feed contains only `placeholder.invalid` so clients can
load a valid compatibility endpoint. Keep personal service routing in private
client configurations before removing it from a shared feed. Use the GitHub
noreply identity for public commits.

The privacy checker reports file names, line numbers and issue categories.
Do not add assertions that print an entire private configuration on failure.
Repository checks and GitHub secret scanning are complementary; neither can
identify every arbitrary password or infer every personal domain.
