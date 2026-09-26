# phonodist

Language-aware, explainable distance metrics for IPA pronunciations.

`phonodist` compares IPA with IPA. It does not perform grapheme-to-phoneme conversion or synthesize audio.

The package provides two related contracts:

| Contract          | Purpose                              | Stress    |
| ----------------- | ------------------------------------ | --------- |
| `feature-align/1` | Normalized phonetic feature distance | Ignored   |
| `ipa-compare/1`   | Structural difference classification | Preserved |

## Start here

- [Getting started](getting-started.md) — install the package and compare IPA in Python.
- [Command-line interface](cli.md) — use `phonodist compare` and `phonodist diff`.
- [Python API](api.md) — public functions, results, profiles, and errors.
- [Metric v1](METRIC.md) — understand scoring and limitations.
- [Structural IPA comparison](COMPARISON.md) — understand comparison classifications.
- [Language profiles](PROFILES.md) — understand profile-specific rules.

```{toctree}
:maxdepth: 2
:hidden:
:caption: User guide

getting-started
cli
api
COMPARISON
METRIC
PROFILES
```

```{toctree}
:maxdepth: 1
:hidden:
:caption: Project

changelog
RELEASING
```
