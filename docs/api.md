# Python API

The supported public API is exported from the top-level `phonodist` package. The package version is available as `phonodist.__version__`.

## Core functions

### `pronunciation_distance`

Computes the normalized `feature-align/1` distance.

```{eval-rst}
.. autofunction:: phonodist.pronunciation_distance
```

### `compare_pronunciations`

Returns an `ipa-compare/1` structural comparison with an embedded segmental distance result.

```{eval-rst}
.. autofunction:: phonodist.compare_pronunciations
```

### `parse_ipa`

Normalizes and parses IPA into a public parsed-pronunciation result.

```{eval-rst}
.. autofunction:: phonodist.parse_ipa
```

### `segment_distance`

Returns a feature distance for two IPA segments.

```{eval-rst}
.. autofunction:: phonodist.segment_distance
```

## Profiles

```{eval-rst}
.. autofunction:: phonodist.available_profiles

.. autofunction:: phonodist.get_profile
```

Profile names and aliases are described in [Language profiles](PROFILES.md).

## Distance results

```{eval-rst}
.. autoclass:: phonodist.DistanceResult
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.AlignmentOperation
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.ParsedPronunciation
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.ParseDiagnostic
   :members:
```

## Structural comparison results

```{eval-rst}
.. autoclass:: phonodist.PronunciationComparison
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.ComparisonPronunciation
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.StressEvent
   :members:
```

```{eval-rst}
.. autoclass:: phonodist.StressOperation
   :members:
```

`ComparisonKind` is one of `exact`, `notation_only`, `stress_only`, `phonetic_equivalent`, `stress_and_phonetic_equivalent`, `segmental`, or `stress_and_segmental`. `SegmentRelation` is `exact`, `equivalent`, or `different`. Their structural meanings are explained in [Structural IPA comparison](COMPARISON.md).

## Language profiles

```{eval-rst}
.. autoclass:: phonodist.LanguageProfile
   :members:
```

Profile inventory is descriptive metadata; it is not an exhaustive list of segments accepted by the metric. See [Language profiles](PROFILES.md).

## Exceptions

All package domain exceptions inherit from `PhonodistError`.

```{eval-rst}
.. autoexception:: phonodist.PhonodistError

.. autoexception:: phonodist.InvalidIPAError

.. autoexception:: phonodist.UnknownSegmentError

.. autoexception:: phonodist.UnknownLanguageProfileError

.. autoexception:: phonodist.ProfileValidationError
```

`InvalidIPAError` reports malformed or invalid input. `UnknownSegmentError` reports IPA segments unsupported by the configured feature backend. `UnknownLanguageProfileError` reports a language tag without a bundled profile; `ProfileValidationError` reports invalid profile data.
