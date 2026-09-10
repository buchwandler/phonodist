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

## Inventory semantics

The bundled `inventory` is descriptive profile metadata and an audit aid. It is not an exhaustive rejection list in metric v1. PanPhon remains authoritative for whether an IPA segment has a feature representation, because the profile does not enumerate every length mark, narrow allophone, loanword segment, or external G2P realization.

## Rule types

### Alias

Use when two strings are merely alternate notation for the same intended
segment in the profile.

Example:

```text
de-DE: t͜s -> t͡s
```

Aliases are reserved for representation-level canonicalization. Generic normalization already canonicalizes the supported tie-bar variant; untied affricates are modeled as sequence equivalences so their zero-cost alignment remains visible in explanations.

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
