from __future__ import annotations

import pytest

from phonodist import UnknownSegmentError, pronunciation_distance


def test_identity_is_zero() -> None:
    result = pronunciation_distance("hallo", "hallo", language="de-DE")
    assert result.distance == 0.0
    assert result.raw_cost == 0.0
    assert result.operations == ()


def test_result_contains_backend_provenance() -> None:
    result = pronunciation_distance("p", "b", language="de-DE")

    assert result.metric == "feature-align"
    assert result.metric_version == "1"
    assert result.language == "de-DE"
    assert result.profile_version == "1"
    assert result.backend == "panphon"
    assert result.backend_version
    assert result.feature_set == "spe+"


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("p", "b"),
        ("ʊ", "u"),
        ("ən", "n̩"),
    ],
)
def test_default_metric_is_symmetric(left: str, right: str) -> None:
    forward = pronunciation_distance(left, right, language="de-DE")
    reverse = pronunciation_distance(right, left, language="de-DE")
    assert forward.distance == pytest.approx(reverse.distance)


@pytest.mark.parametrize(("left", "right"), [("#", "#"), ("#", ""), ("a\u0301", "a")])
def test_unknown_segments_are_rejected_before_alignment(left: str, right: str) -> None:
    with pytest.raises(UnknownSegmentError):
        pronunciation_distance(left, right, language="de-DE")


def test_empty_inputs_are_defined() -> None:
    assert pronunciation_distance("", "").distance == 0.0
    assert pronunciation_distance("a", "").distance == 1.0
    assert pronunciation_distance("", "a").distance == 1.0


def test_contrastive_variants_are_ordered() -> None:
    reference = "bat"
    close = pronunciation_distance(reference, "pat", language="de-DE").distance
    far = pronunciation_distance(reference, "kit", language="de-DE").distance
    assert close < far


def test_retained_stress_is_not_supported() -> None:
    with pytest.raises(NotImplementedError, match="stress-insensitive"):
        pronunciation_distance("ˈa", "a", ignore_stress=False)


def test_comparison_does_not_change_feature_align_stress_policy() -> None:
    assert pronunciation_distance("ˈa", "a").distance == 0.0
    with pytest.raises(NotImplementedError):
        pronunciation_distance("ˈa", "a", ignore_stress=False)


@pytest.mark.parametrize(
    ("left", "right", "language"),
    [
        ("p", "b", "de-DE"),
        ("ən", "n̩", "de-DE"),
        ("t͡s", "ts", "de-DE"),
        ("a", "e", None),
        ("a", "", None),
    ],
)
def test_score_only_matches_traceback(
    left: str,
    right: str,
    language: str | None,
) -> None:
    score_only = pronunciation_distance(left, right, language=language)
    explained = pronunciation_distance(left, right, language=language, explain=True)

    assert explained.raw_cost == pytest.approx(score_only.raw_cost)
    assert explained.distance == pytest.approx(score_only.distance)
    assert sum(operation.cost for operation in explained.operations) == pytest.approx(
        explained.raw_cost
    )


def test_traceback_tie_breaking_is_deterministic() -> None:
    first = pronunciation_distance("ab", "ba", explain=True)
    second = pronunciation_distance("ab", "ba", explain=True)
    assert first.operations == second.operations


def test_universal_mode_provenance_is_explicit() -> None:
    result = pronunciation_distance("p", "b")
    assert result.language is None
    assert result.profile_version is None
