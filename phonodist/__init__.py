from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .api import parse_ipa, pronunciation_distance, segment_distance
from .errors import (
    InvalidIPAError,
    PhonodistError,
    ProfileValidationError,
    UnknownLanguageProfileError,
    UnknownSegmentError,
)
from .model import (
    AlignmentOperation,
    DistanceResult,
    LanguageProfile,
    ParseDiagnostic,
    ParsedPronunciation,
)
from .profiles import available_profiles, get_profile

try:
    __version__ = version("phonodist")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    "AlignmentOperation",
    "DistanceResult",
    "InvalidIPAError",
    "LanguageProfile",
    "ParseDiagnostic",
    "ParsedPronunciation",
    "PhonodistError",
    "ProfileValidationError",
    "UnknownLanguageProfileError",
    "UnknownSegmentError",
    "parse_ipa",
    "pronunciation_distance",
    "segment_distance",
    "available_profiles",
    "get_profile",
]
