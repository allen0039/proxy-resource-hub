# Rename `gongyiai` to `direct-ai`

## Goal

Rename the public rule set and every active consumer from `gongyiai` to
`direct-ai`. The rename is intentionally breaking: no compatibility file,
provider name, or old raw URL remains after the migration.

The rule contents and routing behavior do not change. The renamed rule set
continues to use `DIRECT` in the maintained client configurations.

## Repository changes

The canonical source moves from:

`Rules/Source/AI/gongyiai.txt`

to:

`Rules/Source/AI/direct-ai.txt`

`tools/generate_rules.py` will register `direct-ai` as the rule-set name. A
normal generator run will then produce:

- `Rules/AI/direct-ai.list`
- `Rules/Mihomo/AI/direct-ai.list`
- `Rules/Surge/AI/direct-ai.list`
- `Rules/QuantumultX/AI/direct-ai.list`
- `Rules/Loon/AI/direct-ai.list`

The corresponding five `gongyiai.list` outputs will be removed. README links,
generator tests, sanitizer tests, and the committed sanitized client
configurations will use the new filenames and URLs.

## Private client configurations

The active private configurations outside the repository will be updated in the
same operation:

- `mihomo_byallen.yaml`: rename the provider key to `direct-ai`, update its raw
  URL, and change the rule to `RULE-SET,direct-ai,DIRECT`.
- `surge-Mac.conf` and `Surge-iPhone.conf`: update the remote rule-set URL to
  `Rules/Surge/AI/direct-ai.list` while retaining `DIRECT`.
- `quantumult_byallen.conf`: update the remote rule-set URL to
  `Rules/QuantumultX/AI/direct-ai.list`; retain `force-policy=direct`.
- `allenloon.lcf`: update the remote rule-set URL to
  `Rules/Loon/AI/direct-ai.list`; retain the direct policy.

The local integration tests and current operational notes will be updated so
they validate and document `direct-ai`, not the retired name.

## Automatic generation

The existing `Sync generated rules` workflow remains the automation entry
point. It runs `tools/generate_rules.py` on pushes to `main`, executes the test
suite, verifies generated outputs, and commits generated changes only when the
repository differs.

Because the generator specification itself is renamed, future runs will keep
the five `direct-ai.list` files current and will no longer recreate
`gongyiai.list`.

## Validation

Before publishing:

1. Run `python3 tools/generate_rules.py`.
2. Run `python3 -m unittest discover -s tests -v` in the repository.
3. Run `python3 tools/generate_rules.py --check`.
4. Run the private configuration integration tests.
5. Search the active repository, private configurations, tests, and current
   notes for `gongyiai`; no active reference may remain.
6. Confirm every new raw URL maps to a generated `direct-ai.list` file and every
   maintained client still routes the rule set directly.

## Publication

The completed atomic change will update `main` only. No feature branch or
compatibility branch will be pushed. Since the old raw URLs are deliberately
removed, all maintained client configurations must be updated before or
together with publication.
