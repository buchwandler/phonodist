from __future__ import annotations

from functools import lru_cache
from importlib.metadata import version
from typing import Protocol

import panphon

from .errors import UnknownSegmentError


class FeatureBackend(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def feature_set(self) -> str: ...

    def has_segment(self, segment: str) -> bool: ...

    def segment_distance(self, left: str, right: str) -> float: ...


@lru_cache(maxsize=4096)
def _vector(table: panphon.FeatureTable, segment: str) -> tuple[int, ...]:
    if not table.seg_known(segment):
        raise UnknownSegmentError(f"PanPhon does not recognize {segment!r} as one IPA segment")

    vectors = table.word_to_vector_list(segment, numeric=True)
    if len(vectors) != 1:
        raise UnknownSegmentError(
            f"PanPhon does not recognize {segment!r} as exactly one IPA segment"
        )
    return tuple(int(value) for value in vectors[0])


@lru_cache(maxsize=16384)
def _segment_distance(
    table: panphon.FeatureTable,
    left: str,
    right: str,
) -> float:
    left_vector = _vector(table, left)
    right_vector = _vector(table, right)

    if left == right:
        return 0.0
    if len(left_vector) != len(right_vector) or not left_vector:
        raise UnknownSegmentError(f"incompatible feature vectors for {left!r} and {right!r}")

    # PanPhon uses -1, 0, +1 feature values. Opposite specified values have
    # difference 2; specified versus unspecified has difference 1.
    cost = sum(
        abs(left_value - right_value) / 2.0
        for left_value, right_value in zip(left_vector, right_vector, strict=True)
    ) / len(left_vector)

    return max(0.0, min(1.0, float(cost)))


class PanphonFeatureBackend:
    """PanPhon-backed segment feature distance.

    The MVP uses PanPhon's numeric articulatory feature vectors and computes
    a normalized unweighted feature difference in [0, 1].
    """

    name = "panphon"
    feature_set = "spe+"

    def __init__(self) -> None:
        self.version = version("panphon")
        self._table = panphon.FeatureTable(feature_set=self.feature_set)

    def has_segment(self, segment: str) -> bool:
        return bool(self._table.seg_known(segment))

    def vector(self, segment: str) -> tuple[int, ...]:
        return _vector(self._table, segment)

    def segment_distance(self, left: str, right: str) -> float:
        return _segment_distance(self._table, left, right)
