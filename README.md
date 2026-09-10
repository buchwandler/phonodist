# phonodist

Language-aware, explainable distance metrics for IPA pronunciations.

`phonodist` compares **IPA with IPA**. It does not perform grapheme-to-phoneme
conversion and does not synthesize audio.

The initial MVP combines:

- Unicode-safe IPA normalization
- IPA segment tokenization
- PanPhon-backed articulatory feature distance
- weighted sequence alignment
- sparse language-specific equivalence rules
- an initial `de-DE` profile

## Layout

This project intentionally does **not** use a `src/` directory:

```text
phonodist/
├── phonodist/
│   ├── __init__.py
│   ├── api.py
│   ├── ...
│   └── data/profiles/de-DE.toml
├── tests/
├── pyproject.toml
└── README.md
```

## Dynamic versioning

Versions come from Git tags through `setuptools-scm`.

After unpacking:

```bash
git init
git add .
git commit -m "Initial phonodist scaffold"
git tag v0.1.0

python -m pip install -e ".[dev]"
python -c "import phonodist; print(phonodist.__version__)"
```

Without Git metadata, builds fall back to:

```text
0+unknown
```

Do not manually maintain a version constant.

## Quick start

```python
from phonodist import pronunciation_distance

result = pronunciation_distance(
    "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt",
    "lˈʊftvˌafənʃtˌʏt‍spʊŋkt",
    language="de-DE",
)

print(result.distance)

for operation in result.operations:
    print(operation)
```

The German profile removes representation noise such as stress differences
in broad mode, recognizes German affricate notation aliases, and provides a
low-cost equivalence for common reductions such as:

```text
ən ↔ n̩
əm ↔ m̩
əl ↔ l̩
```

## CLI

```bash
phonodist compare de-DE \
  'ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt' \
  'lˈʊftvˌafənʃtˌʏt‍spʊŋkt' \
  --explain
```

JSON output:

```bash
phonodist compare de-DE 'p' 'b' --json
```

## Metric scope

The MVP score is a **phonetic feature distance**, not a validated model of
human perceptual similarity.

It is intended as a deterministic comparison primitive for:

- lexicon validation
- G2P evaluation
- pronunciation regression tests
- investigation of suspicious pronunciation pairs

Consumers such as Lexphon should define their own acceptance/reporting
thresholds.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy phonodist
python -m build
```

## License

Apache-2.0.

PanPhon is an external MIT-licensed dependency and is not vendored here.
PHOIBLE data is not bundled or copied into this package.
