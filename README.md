# phonodist

Language-aware, explainable distance metrics for IPA pronunciations.

`phonodist` compares IPA with IPA. It does not perform grapheme-to-phoneme
conversion or synthesize audio. The initial metric combines Unicode-safe IPA
normalization, segment tokenization, PanPhon articulatory features, weighted
alignment, and sparse language-specific equivalence rules.

## Installation

```bash
pip install phonodist
```

Development dependencies are installed with:

```bash
python -m pip install -e ".[dev]"
```

## Supported profiles

The bundled profile is:

```text
de-DE
```

`de`, `de-DE`, and `de_de` resolve to `de-DE`. Use `language=None` for
universal feature mode without language-specific profile rules.

## Quick start

```python
from phonodist import pronunciation_distance

result = pronunciation_distance(
    "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt",
    "lˈʊftvˌafənʃtˌʏt\u200dspʊŋkt",
    language="de-DE",
)

print(result.distance)
```

`pronunciation_distance` uses score-only mode by default. Request alignment
operations explicitly with `explain=True`.

`compare_pronunciations` provides the separate `ipa-compare/1` structural diagnostic. It
preserves primary and secondary stress as anchored events while embedding the existing
segmental result. For example, `wɪ\u200dɹ` versus `wˈɪ\u200dɹ` has zero `feature-align/1` distance
but classifies as `stress_only`. See [docs/COMPARISON.md](docs/COMPARISON.md).

## CLI

```bash
phonodist compare de-DE \
  'ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt' \
  'lˈʊftvˌafənʃtˌʏtspʊŋkt' \
  --explain
```

Structural diagnostics use the separate `diff` command and do not require a profile:

```bash
phonodist diff 'wɪ\u200dɹ' 'wˈɪ\u200dɹ' --explain
```

JSON output is available with `--json`, and the package version is available
with `phonodist --version`.

## Strict IPA behavior

PanPhon validates every resulting segment. Unsupported IPA raises
`UnknownSegmentError`, including when an unsupported segment appears on only
one side or is identical on both sides. Unicode format characters such as the
zero-width joiner are ignored during normalization. Stress is intentionally
ignored by `feature-align/1`; retained-stress scoring is not implemented. The separate
`ipa-compare/1` structural API preserves stress for diagnostics.

## Metric scope and provenance

The MVP score is a phonetic feature distance, not a validated model of human
perceptual similarity. It is intended for deterministic comparison, ranking,
lexicon validation, G2P evaluation, pronunciation regression tests, and
investigation of suspicious pronunciation pairs.

Each result records the metric and metric version, profile and profile version,
and PanPhon backend version and feature set. Consumers such as Lexphon
should define their own thresholds. See [docs/METRIC.md](https://github.com/buchwandler/phonodist/blob/main/docs/METRIC.md) and
[docs/PROFILES.md](https://github.com/buchwandler/phonodist/blob/main/docs/PROFILES.md).

Metric and profile details may evolve during the 0.x series. Changes to metric
semantics require a metric version bump. Language-specific rule or cost changes
require a profile version bump. Documentation and performance fixes that
preserve scores only require a package version change.

## Development

```bash
pytest
ruff check .
mypy phonodist
pre-commit run --all-files
python -m build
```

## Benchmarking

Run the representative throughput benchmark with a small count during development:

```bash
python benchmarks/benchmark_distance.py --count 1000
```

The benchmark compares score-only and explained calls and reports profile load time. Its values are engineering baselines, not calibrated human-perceptual examples. Profile costs remain explicitly tunable parameters until a later calibration study.

## Release publishing

Before pushing a `v0.1.0` tag, configure and verify the PyPI Trusted Publisher for the `pypi` GitHub environment. The publisher must use GitHub Actions OIDC and does not require an API token. See [docs/RELEASING.md](https://github.com/buchwandler/phonodist/blob/main/docs/RELEASING.md).

## License

Apache-2.0. PanPhon is an external MIT-licensed dependency and is not vendored
here. PHOIBLE data is not bundled or copied into this package.
