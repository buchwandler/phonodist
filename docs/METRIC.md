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
7. Compare single segments using PanPhon feature vectors.
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

## Important limitation

This score is not a calibrated human perceptual-distance model. It is a
deterministic phonetic-feature comparison intended for validation and
ranking.
