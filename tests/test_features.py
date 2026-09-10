from __future__ import annotations

import pytest

from phonodist import UnknownSegmentError, segment_distance
from phonodist.features import PanphonFeatureBackend


def test_feature_distance_orders_nearby_segments() -> None:
    assert segment_distance("p", "b") < segment_distance("p", "a")
    assert segment_distance("t", "d") < segment_distance("t", "a")
    assert segment_distance("ʊ", "u") < segment_distance("ʊ", "a")


def test_unknown_segment_is_rejected_before_vector_extraction() -> None:
    backend = PanphonFeatureBackend()

    assert backend.has_segment("p")
    assert not backend.has_segment("#")
    with pytest.raises(UnknownSegmentError):
        backend.vector("a\u0301")


def test_backend_provenance_is_explicit() -> None:
    backend = PanphonFeatureBackend()

    assert backend.name == "panphon"
    assert backend.version
    assert backend.feature_set == "spe+"
