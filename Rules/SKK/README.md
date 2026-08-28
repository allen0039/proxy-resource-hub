# SKK Derived Rules

The generated CDN and Download rules in these directories are derived from
[SukkaW/Surge](https://github.com/SukkaW/Surge):

- `Rules/QuantumultX/SKK/`
- `Rules/Loon/SKK/`
- `Rules/Egern/SKK/`

The upstream source and these derived rule files are licensed under
`AGPL-3.0-only`. A copy of the license is available at
`LICENSES/AGPL-3.0-only.txt`.

The Mainland China IPv4 data in Egern `Domestic.yaml` is sourced from SKK's
`china_ip.conf` under
[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/). The generated
file records both applicable SPDX licenses and the exact source URLs.

`tools/update_skk_rules.py` downloads the official SKK domain-set and non-IP
files, validates their provenance and minimum sizes, converts them into native
Quantumult X and Loon syntax, and removes exact duplicates. The daily workflow
is defined in `.github/workflows/update-skk-rules.yml`.

`tools/update_egern_rules.py` converts the SKK sources used by the maintained
Surge configuration into native Egern YAML. It also converts the selected
non-SKK Surge lists needed to close Egern coverage gaps; every generated file
records its exact upstream URL.

Generated `.list` files must not be edited manually.
