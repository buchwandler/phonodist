from __future__ import annotations

from functools import lru_cache

from .alignment import align_segments
from .features import PanphonFeatureBackend
from .model import DistanceResult, LanguageProfile, ParsedPronunciation
from .normalize import normalize_ipa
from .profiles import get_profile, normalize_language_tag
from .tokenize import apply_aliases, ipa_units

_METRIC = "feature-align"
_METRIC_VERSION = "1"


@lru_cache(maxsize=1)
def _backend() -> PanphonFeatureBackend:
    return PanphonFeatureBackend()


def _resolve_profile(language: str | None) -> LanguageProfile | None:
    if language is None:
        return None
    return get_profile(language)


def parse_ipa(
    value: str,
    *,
    language: str | None = None,
    ignore_stress: bool | None = None,
) -> ParsedPronunciation:
    profile = _resolve_profile(language)

    if ignore_stress is None:
        ignore_stress = profile.default_ignore_stress if profile is not None else True

    normalized, diagnostics = normalize_ipa(value, ignore_stress=ignore_stress)
    normalized = apply_aliases(normalized, profile)
    segments = ipa_units(normalized)

    return ParsedPronunciation(
        original=value,
        normalized=normalized,
        segments=segments,
        diagnostics=diagnostics,
    )


def segment_distance(left: str, right: str) -> float:
    """Return normalized PanPhon feature distance for two IPA segments."""
    return _backend().segment_distance(left, right)


def pronunciation_distance(
    source: str,
    target: str,
    *,
    language: str | None = None,
    ignore_stress: bool | None = None,
) -> DistanceResult:
    profile = _resolve_profile(language)
    normalized_language = normalize_language_tag(language) if language is not None else None

    parsed_source = parse_ipa(
        source,
        language=language,
        ignore_stress=ignore_stress,
    )
    parsed_target = parse_ipa(
        target,
        language=language,
        ignore_stress=ignore_stress,
    )

    raw_cost, operations = align_segments(
        parsed_source.segments,
        parsed_target.segments,
        backend=_backend(),
        equivalences=profile.sequence_equivalences if profile is not None else (),
    )

    denominator = float(max(len(parsed_source.segments), len(parsed_target.segments)))
    distance = raw_cost / denominator if denominator else 0.0
    distance = max(0.0, min(1.0, distance))

    return DistanceResult(
        distance=distance,
        raw_cost=raw_cost,
        denominator=denominator,
        source=parsed_source,
        target=parsed_target,
        operations=operations,
        metric=_METRIC,
        metric_version=_METRIC_VERSION,
        language=normalized_language,
        profile_version=profile.version if profile is not None else None,
    )
