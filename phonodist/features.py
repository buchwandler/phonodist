from __future__ import annotations

from functools import lru_cache
from typing import Protocol

import panphon

from .errors import UnknownSegmentError


class FeatureBackend(Protocol):
    def segment_distance(self, left: str, right: str) -> float: ...


class PanphonFeatureBackend:
    """PanPhon-backed segment feature distance.

    The MVP uses PanPhon's numeric articulatory feature vectors and computes
    a normalized unweighted feature difference in [0, 1].
    """

    def __init__(self) -> None:
        self._table = panphon.FeatureTable()

    @lru_cache(maxsize=4096)
    def vector(self, segment: str) -> tuple[int, ...]:
        vectors = self._table.word_to_vector_list(segment, numeric=True)
        if len(vectors) != 1:
            raise UnknownSegmentError(
                f"PanPhon does not recognize {segment!r} as exactly one IPA segment"
            )
        return tuple(int(value) for value in vectors[0])

    @lru_cache(maxsize=16384)
    def segment_distance(self, left: str, right: str) -> float:
        if left == right:
            return 0.0

        left_vector = self.vector(left)
        right_vector = self.vector(right)

        if len(left_vector) != len(right_vector) or not left_vector:
            raise UnknownSegmentError(f"incompatible feature vectors for {left!r} and {right!r}")

        # PanPhon uses -1, 0, +1 feature values. Opposite specified values have
        # difference 2; specified vs unspecified has difference 1.
        cost = sum(
            abs(left_value - right_value) / 2.0
            for left_value, right_value in zip(left_vector, right_vector)
        ) / len(left_vector)

        return max(0.0, min(1.0, float(cost)))
