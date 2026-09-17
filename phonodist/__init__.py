from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .api import compare_pronunciations, parse_ipa, pronunciation_distance, segment_distance
from .errors import (
    InvalidIPAError,
    PhonodistError,
    ProfileValidationError,
    UnknownLanguageProfileError,
    UnknownSegmentError,
)
from .model import (
    AlignmentOperation,
    ComparisonKind,
    ComparisonPronunciation,
    DistanceResult,
    LanguageProfile,
    ParseDiagnostic,
    ParsedPronunciation,
    PronunciationComparison,
    SegmentRelation,
    StressEvent,
    StressOperation,
)
from .profiles import available_profiles, get_profile

try:
    __version__ = version("phonodist")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    "ComparisonKind",
    "ComparisonPronunciation",
    "PronunciationComparison",
    "SegmentRelation",
    "StressEvent",
    "StressOperation",
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
    "compare_pronunciations",
    "parse_ipa",
    "pronunciation_distance",
    "segment_distance",
    "available_profiles",
    "get_profile",
]
