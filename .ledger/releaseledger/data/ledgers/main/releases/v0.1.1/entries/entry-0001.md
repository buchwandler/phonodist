---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0001
release_version: v0.1.1
kind: added
summary:
  Added structural IPA comparison diagnostics with stress-aware classifications
  and a profile-aware diff CLI
status: accepted
audience: null
scopes: []
source_refs:
  - git:637ecd22cfda8eaf8b2908f7cbe07d7a97bd9999
paths:
  - README.md
  - benchmarks/benchmark_comparison.py
  - docs/COMPARISON.md
  - docs/METRIC.md
  - phonodist/__init__.py
  - phonodist/_symbols.py
  - phonodist/api.py
  - phonodist/cli.py
  - phonodist/comparison.py
  - phonodist/model.py
  - phonodist/normalize.py
  - phonodist/profiles.py
  - phonodist/tokenize.py
  - tests/test_cli.py
  - tests/test_comparison.py
  - tests/test_distance.py
  - tests/test_profiles.py
issues: []
prs: []
sources:
  - git:637ecd22cfda8eaf8b2908f7cbe07d7a97bd9999
contributors:
  - "@holgern"
breaking: false
internal: false
order: 1
---
