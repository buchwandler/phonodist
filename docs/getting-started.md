# Getting started

## Installation

Install the published package with Python's package installer:

```bash
python -m pip install phonodist
```

For repository development, install the development tools and Sphinx dependencies separately:

```bash
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
```

Normal package users do not need the documentation dependencies.

## First distance

```python
from phonodist import pronunciation_distance

result = pronunciation_distance("p", "b")
print(result.distance)
```

The distance is normalized to `[0, 1]`. A value of `0` means equivalence under the active normalization and profile rules, not necessarily identical input strings. Alignment `operations` are empty unless `explain=True` is requested.

## Inspect the alignment

```python
result = pronunciation_distance("n̩", "ən", language="de-DE", explain=True)
for operation in result.operations:
    print(operation.kind, operation.source, operation.target, operation.cost)
```

A language profile can define sequence equivalences; see [Language profiles](PROFILES.md). Do not treat an exact non-zero feature score as a calibrated measure of human perceptual similarity. See [Metric v1](METRIC.md) for the score contract and its limitations.

## Structural comparison

Use the separate structural API when stress and notation differences should remain visible:

```python
from phonodist import compare_pronunciations

comparison = compare_pronunciations("wɪɹ", "wˈɪɹ")
assert comparison.classification == "stress_only"
```

`ipa-compare/1` preserves stress as structure and includes a segmental `feature-align/1` result. It does not determine which pronunciation is correct. See [Structural IPA comparison](COMPARISON.md).

## Universal mode and language profiles

`pronunciation_distance` uses universal feature mode when `language=None`; this applies general IPA normalization without language-specific profile rules. Pass a language/profile tag such as `"de-DE"` to use a bundled profile. The current bundled profile set and accepted aliases are described in [Language profiles](PROFILES.md).

## Error handling

Catch the package's public exception base class for domain errors:

```python
from phonodist import PhonodistError, pronunciation_distance

try:
    pronunciation_distance("#", "#")
except PhonodistError as exc:
    print(exc)
```

More specific errors, including invalid IPA, unsupported segments, and unknown profiles, are listed in the [Python API reference](api.md).

## Where to go next

- [Python API](api.md) for function signatures, result types, and exceptions.
- [Command-line interface](cli.md) for `compare`, `diff`, and JSON output.
- [Metric v1](METRIC.md) and [Structural IPA comparison](COMPARISON.md) for result interpretation.
