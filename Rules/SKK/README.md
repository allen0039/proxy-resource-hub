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

Current templates use published upstream classical lists with Loon, and the configured
KOP-XIAO parser with Quantumult X. Egern uses published native YAML sources
and small inline compatibility supplements. The unpublished `SurgeAligned`
experiment has been retired; templates do not depend on those paths.

Quantumult X cannot match URL paths or protocol/domain AND conditions in filter
resources. Its parser skips those unsupported entries without broadening them
to whole domains. Loon process rules are ignored on iOS, as documented upstream.

When introducing new output paths, publish the generated resources before
distributing configurations that reference them. Validate actual HTTP responses
with `python3 tools/check_remote_rules.py`; a local file does not prove its raw
GitHub URL is available. The command checks active rule URLs in the public
templates, excludes node subscriptions and disabled resources, and fails on
404s, HTML error pages, empty resources or invalid rule YAML.
