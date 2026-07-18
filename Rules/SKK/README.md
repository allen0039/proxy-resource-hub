# SKK Derived Rules

The generated CDN and Download rules in these directories are derived from
[SukkaW/Surge](https://github.com/SukkaW/Surge):

- `Rules/QuantumultX/SKK/`
- `Rules/Loon/SKK/`

The upstream source and these derived rule files are licensed under
`AGPL-3.0-only`. A copy of the license is available at
`LICENSES/AGPL-3.0-only.txt`.

`tools/update_skk_rules.py` downloads the official SKK domain-set and non-IP
files, validates their provenance and minimum sizes, converts them into native
Quantumult X and Loon syntax, and removes exact duplicates. The daily workflow
is defined in `.github/workflows/update-skk-rules.yml`.

Generated `.list` files must not be edited manually.
