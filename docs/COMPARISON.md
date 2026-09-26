# Structural IPA comparison

`phonodist` exposes two deliberately separate comparison contracts:

| Contract          | Purpose                              | Stress    | Result                              |
| ----------------- | ------------------------------------ | --------- | ----------------------------------- |
| `feature-align/1` | Phonetic feature distance            | Ignored   | [`DistanceResult`](api.md)          |
| `ipa-compare/1`   | Structural difference classification | Preserved | [`PronunciationComparison`](api.md) |

`ipa-compare/1` is a diagnostic classifier, not a calibrated stress-distance model. It
explains supplied IPA output. It does not decide which pronunciation is correct, rewrite
pronunciations, perform grapheme-to-phoneme conversion, or apply word-specific rules.

## Python API

```python
from phonodist import compare_pronunciations, pronunciation_distance

distance = pronunciation_distance("wɪɹ", "wˈɪɹ")
assert distance.distance == 0.0

comparison = compare_pronunciations("wɪɹ", "wˈɪɹ")
assert comparison.classification == "stress_only"
assert comparison.segment_equal
assert not comparison.stress_equal
assert comparison.target.stress[0].kind == "primary"
assert comparison.target.stress[0].anchor == 1
```

The distance API answers whether the normalized segment sequences have feature distance.
The structural API additionally reports raw equality, canonical segment equality, stress
equality, segment relation, stress operations, and the embedded segmental distance result.
See the [`PronunciationComparison`](api.md), [`ComparisonPronunciation`](api.md),
[`StressEvent`](api.md), and [`StressOperation`](api.md) API entries for field details.

## Structural fields

`ComparisonPronunciation.segments` is a stress-free canonical segment tuple.
`ComparisonPronunciation.stress` contains `StressEvent` values. Each event has kind
`primary` or `secondary` and an anchor equal to the number of canonical segments before it.
Anchors count segments, not Unicode codepoints.

`segment_relation` is one of:

- `exact`: canonical segment tuples are identical.
- `equivalent`: tuples differ, but `feature-align/1` has zero cost under the selected profile.
- `different`: the segmental distance is greater than zero.

Classifications are deterministic:

| Classification                   | Meaning                                                           |
| -------------------------------- | ----------------------------------------------------------------- |
| `exact`                          | Raw input strings are equal.                                      |
| `notation_only`                  | Raw strings differ, but canonical segments and stress are equal.  |
| `stress_only`                    | Canonical segments are equal and stress differs.                  |
| `phonetic_equivalent`            | Stress is equal, segments differ, and segmental distance is zero. |
| `stress_and_phonetic_equivalent` | Stress and segments differ, but segmental distance is zero.       |
| `segmental`                      | Stress is equal and segmental distance is greater than zero.      |
| `stress_and_segmental`           | Both stress and segmental structure differ.                       |

Stress operations are deterministic. Same-anchor kind changes are `replace` operations.
Source-only events are `delete` operations, and target-only events are `insert`
operations. Stress movement is represented by a delete followed by an insert. No
syllabification or fuzzy movement algorithm is involved.

## CLI

Use `diff` for structural diagnostics. A language profile is optional.

```bash
phonodist diff 'wɪɹ' 'wˈɪɹ'
phonodist diff --language de-DE 't͡s' 'ts'
phonodist diff --explain 'ˌa' 'ˈa'
phonodist diff --json 'wɪɹ' 'wˈɪɹ'
```

The existing `phonodist compare de-DE SOURCE TARGET` command remains the
`feature-align/1` distance command. Ordinary structural differences do not cause `diff`
to return a non-zero status. See the [CLI reference](cli.md) for JSON and error behavior.

## Profile boundary

Profiles can define notation aliases, segment equivalences, and segment distance behavior.
Stress extraction is universal IPA structure. Profiles do not define expected stress,
contraction rules, or pronunciation rewrites.

## See also

- [Python API](api.md)
- [Metric v1](METRIC.md)
- [Language profiles](PROFILES.md)
