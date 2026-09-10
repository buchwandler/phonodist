from __future__ import annotations

import phonodist


def test_version_is_available() -> None:
    assert isinstance(phonodist.__version__, str)
    assert phonodist.__version__
