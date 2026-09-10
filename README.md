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

## CLI

```bash
phonodist compare de-DE \
  'ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt' \
  'lˈʊftvˌafənʃtˌʏt\u200dspʊŋkt' \
  --explain
```

JSON output is available with `--json`, and the package version is available
with `phonodist --version`.

## Strict IPA behavior

PanPhon validates every resulting segment. Unsupported IPA raises
`UnknownSegmentError`, including when an unsupported segment appears on only
one side or is identical on both sides. Unicode format characters such as the
zero-width joiner are ignored during normalization. Stress is intentionally
ignored by `feature-align/1`; retained-stress scoring is not implemented.

## Metric scope and provenance

The MVP score is a phonetic feature distance, not a validated model of human
perceptual similarity. It is intended for deterministic comparison, ranking,
lexicon validation, G2P evaluation, pronunciation regression tests, and
investigation of suspicious pronunciation pairs.

Each result records the metric and metric version, profile and profile version,
and PanPhon backend version and feature set. Consumers such as Lexphon should
define their own thresholds. See [docs/METRIC.md](docs/METRIC.md) and
[docs/PROFILES.md](docs/PROFILES.md).

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

## License

Apache-2.0. PanPhon is an external MIT-licensed dependency and is not vendored
here. PHOIBLE data is not bundled or copied into this package.
