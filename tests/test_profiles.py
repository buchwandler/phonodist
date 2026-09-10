from __future__ import annotations

import pytest

from phonodist import (
    ProfileValidationError,
    UnknownLanguageProfileError,
    available_profiles,
    get_profile,
)
from phonodist.profiles import _load_profile, _profile_from_raw


def test_profile_aliases_are_normalized_and_cached() -> None:
    assert available_profiles() == ("de-DE",)
    profile = get_profile("de-DE")

    assert profile is get_profile("de")
    assert profile is get_profile("de_de")


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(UnknownLanguageProfileError):
        get_profile("en-US")


def test_profile_validation_rejects_empty_sequence_transition() -> None:
    raw = {"schema_version": 1, "id": "de-DE", "version": "1", "name": "German"}

    with pytest.raises(ProfileValidationError, match="two empty sides"):
        _profile_from_raw(
            {**raw, "sequence_equivalences": [{"left": [], "right": [], "cost": 0}]},
            "de-DE",
        )


def test_profile_validation_rejects_duplicate_aliases() -> None:
    raw = {
        "schema_version": 1,
        "id": "de-DE",
        "version": "1",
        "name": "German",
        "aliases": [
            {"input": "x", "canonical": "y", "reason": "one"},
            {"input": "x", "canonical": "z", "reason": "two"},
        ],
    }

    with pytest.raises(ProfileValidationError, match="duplicate alias"):
        _profile_from_raw(raw, "de-DE")


def test_profile_validation_rejects_alias_whitespace() -> None:
    raw = {
        "schema_version": 1,
        "id": "de-DE",
        "version": "1",
        "name": "German",
        "aliases": [{"input": "x y", "canonical": "z", "reason": "spacing"}],
    }

    with pytest.raises(ProfileValidationError, match="whitespace"):
        _profile_from_raw(raw, "de-DE")


def test_profile_validation_rejects_alias_cascades() -> None:
    raw = {
        "schema_version": 1,
        "id": "de-DE",
        "version": "1",
        "name": "German",
        "aliases": [
            {"input": "x", "canonical": "y", "reason": "first"},
            {"input": "y", "canonical": "z", "reason": "second"},
        ],
    }

    with pytest.raises(ProfileValidationError, match="cascade"):
        _profile_from_raw(raw, "de-DE")


def test_profile_validation_allows_one_sided_sequence_equivalence() -> None:
    raw = {
        "schema_version": 1,
        "id": "de-DE",
        "version": "1",
        "name": "German",
        "sequence_equivalences": [{"left": ["x"], "right": [], "cost": 0.5, "reason": "optional"}],
    }

    profile = _profile_from_raw(raw, "de-DE")
    assert profile.sequence_equivalences[0].right == ()


def test_profile_cache_can_be_cleared() -> None:
    get_profile("de-DE")
    assert _load_profile.cache_info().currsize >= 1
    _load_profile.cache_clear()
    assert _load_profile.cache_info().currsize == 0
