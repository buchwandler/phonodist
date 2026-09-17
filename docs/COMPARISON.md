# Structural IPA comparison

`phonodist` exposes two deliberately separate comparison contracts:

| Contract          | Purpose                              | Stress    | Result                    |
| ----------------- | ------------------------------------ | --------- | ------------------------- |
| `feature-align/1` | Phonetic feature distance            | Ignored   | `DistanceResult`          |
| `ipa-compare/1`   | Structural difference classification | Preserved | `PronunciationComparison` |

`ipa-compare/1` is a diagnostic classifier, not a calibrated stress-distance model. It
explains supplied IPA output. It does not decide which pronunciation is correct, rewrite
pronunciations, perform grapheme-to-phoneme conversion, or apply word-specific rules.

## Python API

```python
from phonodist import compare_pronunciations, pronunciation_distance

distance = pronunciation_distance("wɪ\u200dɹ", "wˈɪ\u200dɹ")
assert distance.distance == 0.0

comparison = compare_pronunciations("wɪ\u200dɹ", "wˈɪ\u200dɹ")
assert comparison.classification == "stress_only"
assert comparison.segment_equal
assert not comparison.stress_equal
assert comparison.target.stress[0].kind == "primary"
assert comparison.target.stress[0].anchor == 1
```

The distance API answers whether the normalized segment sequences have feature distance.
The structural API additionally reports raw equality, canonical segment equality, stress
equality, segment relation, stress operations, and the embedded segmental distance result.

## Structural fields

`ComparisonPronunciation.segments` is a stress-free canonical segment tuple.
`ComparisonPronunciation.stress` contains `StressEvent` values. Each event has kind
`primary` or `secondary` and an anchor immediately after the corresponding number of
canonical segments.

`segment_relation` is one of:

- `exact`: canonical segment tuples are identical.
- `equivalent`: tuples differ, but `feature-align/1` has zero cost under the selected profile.
- `different`: the segmental distance is greater than zero.

Classifications are deterministic:

- `exact`: raw strings are equal.
- `notation_only`: canonical segments and stress are equal, but raw strings differ.
- `stress_only`: canonical segments are equal and stress differs.
- `phonetic_equivalent`: stress is equal, segment tuples differ, and segmental distance is zero.
- `stress_and_phonetic_equivalent`: stress differs, segment tuples differ, and distance is zero.
- `segmental`: stress is equal and segmental distance is greater than zero.
- `stress_and_segmental`: both stress and segmental structure differ.

Stress operations are deterministic. Same-anchor kind changes are `replace` operations.
Source-only events are `delete` operations, and target-only events are `insert`
operations. Stress movement is represented by a delete followed by an insert. No
syllabification or fuzzy movement algorithm is involved.

## CLI

Use `diff` for structural diagnostics. A language profile is optional.

```bash
phonodist diff 'wɪ\u200dɹ' 'wˈɪ\u200dɹ'
phonodist diff --language de-DE 't͡s' 'ts'
phonodist diff --explain 'wɪ\u200dɹ' 'wˈɪ\u200dɹ'
phonodist diff --json 'wɪ\u200dɹ' 'wˈɪ\u200dɹ'
```

The existing `phonodist compare de-DE SOURCE TARGET` command remains the
`feature-align/1` distance command. Ordinary structural differences do not cause `diff`
to return a non-zero status.

## Profile boundary

Profiles can define notation aliases, segment equivalences, and segment distance behavior.
Stress extraction is universal IPA structure. Profiles do not define expected stress,
contraction rules, or pronunciation rewrites.
