from __future__ import annotations

from importlib.resources import files

import phonodist


def test_profile_and_type_marker_are_package_data() -> None:
    package = files("phonodist")
    assert package.joinpath("data", "profiles", "de-DE.toml").is_file()
    assert package.joinpath("py.typed").is_file()
    assert phonodist.__version__
