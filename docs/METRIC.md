# Metric v1

Metric identifier:

```text
feature-align/1
```

## Pipeline

1. NFC-normalize IPA.
2. Remove Unicode format (`Cf`) characters.
3. Ignore stress by default for broad pronunciation comparison.
4. Normalize tie-bar variants.
5. Apply sparse language-profile notation aliases.
6. Tokenize IPA into segment-like units.
7. Compare single segments using PanPhon articulatory feature vectors.
8. Align sequences with dynamic programming.
9. Permit sparse profile-defined N↔M equivalences.
10. Normalize raw cost by the maximum segment count.

## Costs

Default MVP costs:

```text
exact match             0
feature substitution    PanPhon-derived [0, 1]
insertion               1
deletion                1
profile equivalence     profile-defined [0, 1]
```

The normalized pronunciation score is bounded to `[0, 1]`.

## Interpreting a result

A [`DistanceResult`](api.md) exposes the normalized `distance`, unnormalized `raw_cost`,
and `denominator` used for normalization. `raw_cost` is the alignment cost before
normalization; `denominator` is the larger of the source and target segment counts. The
score is `raw_cost / denominator`, with zero for two empty segment sequences, and is
bounded to `[0, 1]`.

A zero score can result from canonicalization or a zero-cost profile equivalence, not just
identical input strings. Stress removal, notation normalization, and profile sequence
equivalences can make different strings score zero. `phonodist` does not supply universal
decision thresholds; choose thresholds for the application and data being evaluated.

```{testcode}
from phonodist import pronunciation_distance

assert pronunciation_distance("p", "p").distance == 0.0
```

## Explanation mode

Score-only and traceback modes are intended to produce the same score. The default
score-only mode leaves `DistanceResult.operations` empty; pass `explain=True` to add the
deterministic alignment operations without changing the distance.

## Important limitation

This score is not a calibrated human perceptual-distance model. It is a deterministic
phonetic-feature comparison intended for validation and ranking.

## Diagnostic offsets

[`ParseDiagnostic.offset`](api.md) is an index into the normalized working input after
outer delimiters and surrounding whitespace have been removed. It is not necessarily an
index into `ParsedPronunciation.original` when those transformations changed the input.

## Stress scope

`feature-align/1` intentionally ignores primary and secondary stress. Stress-aware or
prosodic comparison is outside the v0.1 metric. The public pronunciation-distance API
rejects retained-stress scoring instead of treating stress markers as ordinary PanPhon
segments. Use [Structural IPA comparison](COMPARISON.md) for separate structural stress
diagnostics.

## Structural comparison

The separate structural contract is identified as `ipa-compare/1`. It preserves primary
and secondary stress as `StressEvent` values anchored in the stress-free canonical segment
sequence. Its result classifies exact, notation-only, stress-only, phonetic-equivalent, and
segmental differences, while embedding the `feature-align/1` segmental result.

`ipa-compare/1` is a structural diagnostic, not a calibrated stress-distance model. It does
not alter pronunciations or determine expected stress. See [Structural IPA comparison](COMPARISON.md).

## Provenance and versioning

Every [`DistanceResult`](api.md) records the metric and metric version, selected profile and
profile version, and the PanPhon backend name, resolved version, and `spe+` feature set.
Bump the metric version when alignment, normalization, costs, or feature formulas change.
Bump a profile version when language-specific rules or costs change. Package-only fixes
that preserve scores do not require a metric version bump.
