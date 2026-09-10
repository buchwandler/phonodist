# Language profiles

Profiles add sparse language-specific knowledge to the generic IPA feature
distance.

A profile may contain:

- an intended language/variety identifier
- version
- inventory metadata
- notation aliases
- low-cost sequence equivalences
- provenance sources

Profiles should **not** become:

- pronunciation dictionaries
- G2P engines
- TTS-specific rewrite systems
- exhaustive N×N distance matrices

## Rule types

### Alias

Use when two strings are merely alternate notation for the same intended
segment in the profile.

Example:

```text
de-DE: ts -> t͡s
```

Aliases have effectively zero comparison cost because they canonicalize
before alignment.

### Sequence equivalence

Use when common language-specific realization/phonological behavior maps
different segment sequences closely.

Example:

```text
de-DE: ə n ↔ n̩
```

These rules have low non-zero cost so the explanation remains visible.

## Provenance

Profile authors should cite linguistic/research sources, but should not copy
incompatibly licensed linguistic databases into Apache-2.0 profile files.
