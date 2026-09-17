from __future__ import annotations

import pytest

from phonodist import (
    InvalidIPAError,
    StressEvent,
    StressOperation,
    UnknownSegmentError,
    compare_pronunciations,
)


def test_exact_comparison() -> None:
    result = compare_pronunciations("wˈɪɹ", "wˈɪɹ")

    assert result.classification == "exact"
    assert result.raw_equal
    assert result.canonical_equal
    assert result.segment_equal
    assert result.stress_equal
    assert result.segment_relation == "exact"


def test_espeak_native_cli_contraction_difference_is_stress_only() -> None:
    result = compare_pronunciations("wɪ\u200dɹ", "wˈɪ\u200dɹ")

    assert result.classification == "stress_only"
    assert not result.raw_equal
    assert not result.canonical_equal
    assert result.segment_equal
    assert not result.stress_equal
    assert result.segment_relation == "exact"
    assert result.segmental.distance == 0.0
    assert result.source.stress == ()
    assert result.target.stress == (StressEvent(kind="primary", anchor=1),)
    assert result.metric == "ipa-compare"
    assert result.metric_version == "1"
    assert result.segmental.metric == "feature-align"


def test_zwj_is_not_a_structural_difference() -> None:
    result = compare_pronunciations("wˈɪ\u200dɹ", "wˈɪɹ")

    assert result.classification == "notation_only"
    assert result.canonical_equal
    assert result.source.diagnostics


def test_tie_bar_variant_is_notation_only() -> None:
    result = compare_pronunciations("t͜s", "t͡s")

    assert result.classification == "notation_only"
    assert result.canonical_equal


def test_nfc_and_nfd_are_notation_only() -> None:
    result = compare_pronunciations("a\u0303", "ã")

    assert result.classification == "notation_only"
    assert result.canonical_equal


def test_primary_vs_secondary_stress_is_replacement() -> None:
    result = compare_pronunciations("ˌa", "ˈa")

    assert result.classification == "stress_only"
    assert result.stress_operations == (
        StressOperation(
            kind="replace",
            source=StressEvent(kind="secondary", anchor=0),
            target=StressEvent(kind="primary", anchor=0),
        ),
    )


def test_stress_movement_is_delete_then_insert() -> None:
    result = compare_pronunciations("ˈab", "aˈb")

    assert result.stress_operations == (
        StressOperation(
            kind="delete",
            source=StressEvent(kind="primary", anchor=0),
            target=None,
        ),
        StressOperation(
            kind="insert",
            source=None,
            target=StressEvent(kind="primary", anchor=1),
        ),
    )


def test_segmental_difference() -> None:
    result = compare_pronunciations("p", "b")

    assert result.classification == "segmental"
    assert result.segment_relation == "different"
    assert result.segmental.distance > 0


def test_stress_and_segmental_difference() -> None:
    result = compare_pronunciations("ˈp", "b")

    assert result.classification == "stress_and_segmental"


def test_profile_zero_cost_equivalence() -> None:
    result = compare_pronunciations("t͡s", "ts", language="de-DE")

    assert result.classification == "phonetic_equivalent"
    assert not result.segment_equal
    assert result.stress_equal
    assert result.segment_relation == "equivalent"
    assert result.segmental.distance == 0.0


def test_empty_input_is_exact() -> None:
    result = compare_pronunciations("", "")

    assert result.classification == "exact"
    assert result.segmental.distance == 0.0


def test_invalid_stress_only_input() -> None:
    with pytest.raises(InvalidIPAError):
        compare_pronunciations("ˈ", "")


def test_unknown_segment_is_rejected() -> None:
    with pytest.raises(UnknownSegmentError):
        compare_pronunciations("#", "#")


def test_outer_delimiters_are_notation_only() -> None:
    result = compare_pronunciations("/p/", "p")

    assert result.classification == "notation_only"
    assert result.canonical_equal


def test_stress_and_phonetic_equivalence() -> None:
    result = compare_pronunciations("ˈt͡s", "ts", language="de-DE")

    assert result.classification == "stress_and_phonetic_equivalent"
    assert result.segment_relation == "equivalent"
