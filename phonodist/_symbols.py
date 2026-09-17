from __future__ import annotations

from typing import Final

PRIMARY_STRESS: Final = "ˈ"
SECONDARY_STRESS: Final = "ˌ"

STRESS_MARKERS: Final = frozenset({PRIMARY_STRESS, SECONDARY_STRESS})
STRESS_KIND_BY_MARKER: Final = {
    PRIMARY_STRESS: "primary",
    SECONDARY_STRESS: "secondary",
}
