# allenrules source split

## Goal

Replace the single `Rules/Source/Custom/allenrules.list` source with five
policy-owned source files while preserving every existing generated rule URL.

## Source layout

```text
Rules/Source/allenrules/
  direct.list
  hk.list
  us.list
  jp.list
  sg.list
```

Each non-comment row contains exactly two fields: `RULE-TYPE,VALUE`. The file
name supplies the policy:

| Source file | Policy | Published output |
| --- | --- | --- |
| `direct.list` | `DIRECT` | `Custom/direct.list` |
| `hk.list` | Hong Kong node | `Regional/hk.list` |
| `us.list` | US node | `Regional/us.list` |
| `jp.list` | Japan node | `Regional/jp.list` |
| `sg.list` | Singapore node | `Regional/sg.list` |

The published output applies to Mihomo, Surge, Quantumult X, and Loon. Their
paths and content formats remain unchanged; only generated headers will name
the corresponding new source file.

## Validation

The generator will validate every source row as before and, after combining
the five files, reject duplicate rules or keyword/suffix overlaps across the
whole set. This prevents a rule from being assigned to conflicting policies.

## Migration and acceptance

Move all existing rules to the file that matches their current policy, keeping
their order within that policy. Remove the legacy source file. Update the
documentation and tests, then regenerate outputs. Success requires the full
test suite and `python3 tools/generate_rules.py --check` to pass, with all
published output paths retained.
