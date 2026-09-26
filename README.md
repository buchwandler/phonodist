# phonodist

Language-aware, explainable distance metrics for IPA pronunciations.

`phonodist` compares IPA with IPA. It does not perform grapheme-to-phoneme conversion or
synthesize audio. Its feature metric combines Unicode-safe normalization, segment
tokenization, PanPhon articulatory features, weighted alignment, and sparse
language-specific equivalence rules.

## Installation

```bash
python -m pip install phonodist
```

## Quick start

```python
from phonodist import pronunciation_distance

result = pronunciation_distance("p", "b")
print(result.distance)
```

The score is normalized to `[0, 1]`; alignment operations are available with
`explain=True`. The bundled profile is `de-DE`; `de` and `de_de` are aliases. Use
`language=None` for universal feature mode without language-specific profile rules.

### Profile-aware example

```python
from phonodist import pronunciation_distance

result = pronunciation_distance("n̩", "ən", language="de-DE", explain=True)
```

## Structural comparison

`compare_pronunciations` provides the separate `ipa-compare/1` structural diagnostic. It
preserves primary and secondary stress as anchored events while embedding the segmental
feature result.

```python
from phonodist import compare_pronunciations

comparison = compare_pronunciations("wɪɹ", "wˈɪɹ")
assert comparison.classification == "stress_only"
```

This classifies supplied IPA; it does not determine which pronunciation is correct. See
[Structural IPA comparison](docs/COMPARISON.md).

## CLI

```bash
phonodist compare de-DE 'n̩' 'ən' --explain
phonodist diff 'wɪɹ' 'wˈɪɹ' --explain
```

Use `--json` for structured output and `phonodist --version` to print the installed
version. See the [CLI reference](docs/cli.md) for all options and error behavior.

## Documentation

- [Getting started](docs/getting-started.md)
- [Python API](docs/api.md)
- [CLI](docs/cli.md)
- [Metric v1](docs/METRIC.md)
- [Structural IPA comparison](docs/COMPARISON.md)
- [Language profiles](docs/PROFILES.md)
- [Changelog](docs/changelog.md)
- [Releasing phonodist](docs/RELEASING.md)

## Scope and limitations

`feature-align/1` ignores stress and reports a deterministic feature distance, not a
calibrated model of human perceptual similarity. A zero score means equivalence under
normalization and profile rules, not necessarily raw-string identity. PanPhon validates
resulting segments; unsupported segments raise `UnknownSegmentError`. The separate
`ipa-compare/1` API preserves stress for structural diagnostics. Consumers should define
their own thresholds.

Every result records metric/profile and PanPhon backend provenance. Metric-semantic changes
require a metric version bump; language-specific rule or cost changes require a profile
version bump.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
pytest --cov=phonodist --cov-report=term-missing
ruff check .
mypy phonodist
python docs/make.py html
python docs/make.py doctest
python -m build
```

## Release publishing

Releases are built and published by the tag-triggered GitHub Actions workflow. The current
PyPI publish job uses the `PYPI_API_TOKEN` Actions secret as API-token credentials; it is
not configured for tokenless Trusted Publishing. See [Releasing phonodist](docs/RELEASING.md)
for release guidance.

## License

Apache-2.0. PanPhon is an external MIT-licensed dependency and is not vendored here.
PHOIBLE data is not bundled or copied into this package.
