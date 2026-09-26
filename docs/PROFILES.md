# Language profiles

Profiles add sparse language-specific knowledge to the generic IPA feature
distance. A profile may specify an intended language/variety, a version, descriptive
inventory metadata, notation aliases, low-cost sequence equivalences, and provenance
sources.

Profiles should **not** become:

- pronunciation dictionaries
- G2P engines
- TTS-specific rewrite systems
- exhaustive N×N distance matrices

## Bundled profiles

The currently bundled profile set is:

```text
de-DE
```

The aliases `de`, `de-DE`, and `de_de` resolve to canonical profile ID `de-DE`.
Profile IDs and aliases are normalized case-insensitively.

```{testcode}
from phonodist import available_profiles, get_profile

assert available_profiles() == ("de-DE",)
assert get_profile("de").id == "de-DE"
assert get_profile("de-DE").id == "de-DE"
assert get_profile("de_de").id == "de-DE"
```

## Using a profile

```python
from phonodist import available_profiles, get_profile, pronunciation_distance

print(available_profiles())
profile = get_profile("de_de")
result = pronunciation_distance("n̩", "ən", language=profile.id, explain=True)
```

`LanguageProfile.inventory` is descriptive metadata and an audit aid, not an exhaustive
rejection list. PanPhon remains authoritative for whether a segment has a feature
representation in metric v1. The inventory does not enumerate every length mark, narrow
allophone, loanword segment, or external G2P realization. See the [`LanguageProfile`](api.md)
API entry for profile fields.

## Rule types

### Alias

Use an alias when two strings are alternate notation for the same intended segment in the
profile.

```text
de-DE: t͜s -> t͡s
```

Aliases are reserved for representation-level canonicalization. Generic normalization
already canonicalizes the supported tie-bar variant; untied affricates are modeled as
sequence equivalences so their zero-cost alignment remains visible in explanations.

### Sequence equivalence

Use a sequence equivalence when common language-specific realization or phonological
behavior maps different segment sequences closely.

```text
de-DE: ə n ↔ n̩
```

These rules have low non-zero cost so the explanation remains visible.

## Inventory semantics

The bundled `inventory` is descriptive profile metadata and an audit aid. It is not an
exhaustive rejection list in metric v1. PanPhon remains authoritative for whether an IPA
segment has a feature representation, because the profile does not enumerate every length
mark, narrow allophone, loanword segment, or external G2P realization.

## Provenance

Profile authors should cite linguistic/research sources, but should not copy
incompatibly licensed linguistic databases into Apache-2.0 profile files.
