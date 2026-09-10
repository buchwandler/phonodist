from __future__ import annotations

import pytest

from phonodist import pronunciation_distance


def test_identity_is_zero() -> None:
    result = pronunciation_distance("hallo", "hallo", language="de-DE")
    assert result.distance == 0.0
    assert result.raw_cost == 0.0


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
