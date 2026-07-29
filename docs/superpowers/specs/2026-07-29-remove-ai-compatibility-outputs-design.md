# Remove `Rules/AI` Compatibility Outputs

## Goal

Remove the two generic AI compatibility outputs because all maintained client
configurations now use client-specific rule paths.

Only these files are retired:

- `Rules/AI/ai.list`
- `Rules/AI/direct-ai.list`

The `Rules/shop/shopping.list` generic output is outside this change and must
remain available.

## Generation behavior

`Rules/Source/AI/ai.txt` and `Rules/Source/AI/direct-ai.txt` remain the
canonical sources. `tools/generate_rules.py` will continue producing both rule
sets for:

- Mihomo
- Surge
- Quantumult X
- Loon

The AI entries in `RULESET_SPECS` will no longer specify `Rules/AI` as a
compatibility directory. Future local runs and the `Sync generated rules`
GitHub Actions workflow therefore cannot recreate either retired file.

The shopping rule keeps its existing `shop` compatibility directory.

## Repository cleanup

Delete both tracked files under `Rules/AI/`. Git does not track empty
directories, so the directory will disappear from GitHub after the deletion.

Remove the two `Rules/AI` compatibility links from `README.md` and remove the
directory's compatibility-layer entry from the documented repository tree.
Keep the compatibility-address section because it still documents
`Rules/shop/shopping.list`.

No private or sanitized client configuration needs modification: all five
maintained client types already reference `Rules/<client>/AI/*.list`.

## Tests

Update `tests/test_generate_rules.py` so it:

- expects 21 generated outputs instead of 23;
- still requires `ai.list` and `direct-ai.list` for all four client-specific
  directories;
- asserts that neither generic `Rules/AI` output appears in the generator
  output map;
- asserts that both retired files are absent from the repository;
- continues requiring `Rules/shop/shopping.list`.

Run the complete repository suite and generator check. The GitHub workflow must
complete successfully and report that generated files are already current.

## Publication

Publish the atomic change directly to `main` with a normal fast-forward push.
Do not create or push a feature branch. After publication:

- both retired raw URLs must return 404;
- all eight client-specific AI raw URLs must continue returning 200;
- `Rules/shop/shopping.list` must continue returning 200;
- the automatic generator must not create a follow-up commit.
