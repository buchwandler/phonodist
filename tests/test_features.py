from __future__ import annotations

from phonodist import segment_distance


def test_feature_distance_orders_nearby_segments() -> None:
    assert segment_distance("p", "b") < segment_distance("p", "a")
    assert segment_distance("t", "d") < segment_distance("t", "a")
    assert segment_distance("ʊ", "u") < segment_distance("ʊ", "a")
