from __future__ import annotations

from functools import lru_cache

from .alignment import align_segments
from .comparison import (
    _classification,
    _parse_comparison_pronunciation,
    _segment_relation,
    _stress_operations,
)
from .errors import UnknownSegmentError
from .features import FeatureBackend, PanphonFeatureBackend
from .model import (
    ComparisonPronunciation,
    DistanceResult,
    LanguageProfile,
    ParsedPronunciation,
    PronunciationComparison,
)
from .normalize import normalize_ipa
from .profiles import get_profile, normalize_language_tag
from .tokenize import apply_aliases, ipa_units

_METRIC = "feature-align"
_METRIC_VERSION = "1"
_COMPARISON_METRIC = "ipa-compare"
_COMPARISON_METRIC_VERSION = "1"


@lru_cache(maxsize=1)
def _backend() -> PanphonFeatureBackend:
    return PanphonFeatureBackend()


def _resolve_profile(language: str | None) -> LanguageProfile | None:
    if language is None:
        return None
    return get_profile(language)


def _validate_segments(
    parsed: ParsedPronunciation,
    backend: FeatureBackend,
    *,
    pronunciation: str,
    language: str | None,
) -> None:
    for index, segment in enumerate(parsed.segments):
        if not backend.has_segment(segment):
            profile = f" for profile {language}" if language is not None else ""
            raise UnknownSegmentError(
                f"unsupported IPA segment {segment!r} at segment index {index}{profile} "
                f"in {pronunciation!r} using {backend.name} {backend.version}"
            )


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


def _distance_from_parsed(
    parsed_source: ParsedPronunciation,
    parsed_target: ParsedPronunciation,
    *,
    profile: LanguageProfile | None,
    normalized_language: str | None,
    backend: FeatureBackend,
    explain: bool,
) -> DistanceResult:
    _validate_segments(
        parsed_source,
        backend,
        pronunciation=parsed_source.original,
        language=normalized_language,
    )
    _validate_segments(
        parsed_target,
        backend,
        pronunciation=parsed_target.original,
        language=normalized_language,
    )

    raw_cost, operations = align_segments(
        parsed_source.segments,
        parsed_target.segments,
        backend=backend,
        equivalences=profile.sequence_equivalences if profile is not None else (),
        explain=explain,
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
        backend=backend.name,
        backend_version=backend.version,
        feature_set=backend.feature_set,
    )


def pronunciation_distance(
    source: str,
    target: str,
    *,
    language: str | None = None,
    ignore_stress: bool | None = None,
    explain: bool = False,
) -> DistanceResult:
    """Return feature-align/1 distance, optionally with an alignment explanation."""
    if ignore_stress is False:
        raise NotImplementedError(
            "feature-align/1 is stress-insensitive; stress-aware comparison is not implemented"
        )
    profile = _resolve_profile(language)
    normalized_language = normalize_language_tag(language) if language is not None else None
    backend = _backend()
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
    return _distance_from_parsed(
        parsed_source,
        parsed_target,
        profile=profile,
        normalized_language=normalized_language,
        backend=backend,
        explain=explain,
    )


def _stress_free_parsed(parsed: ComparisonPronunciation) -> ParsedPronunciation:
    return ParsedPronunciation(
        original=parsed.original,
        normalized="".join(parsed.segments),
        segments=parsed.segments,
        diagnostics=parsed.diagnostics,
    )


def compare_pronunciations(
    source: str,
    target: str,
    *,
    language: str | None = None,
    explain: bool = False,
) -> PronunciationComparison:
    """Explain structural, stress, and segmental differences between IPA values."""
    profile = _resolve_profile(language)
    normalized_language = normalize_language_tag(language) if language is not None else None
    backend = _backend()
    structural_source = _parse_comparison_pronunciation(source, language=language)
    structural_target = _parse_comparison_pronunciation(target, language=language)
    segmental = _distance_from_parsed(
        _stress_free_parsed(structural_source),
        _stress_free_parsed(structural_target),
        profile=profile,
        normalized_language=normalized_language,
        backend=backend,
        explain=explain,
    )

    raw_equal = source == target
    segment_equal = structural_source.segments == structural_target.segments
    stress_equal = structural_source.stress == structural_target.stress
    segment_relation = _segment_relation(structural_source, structural_target, segmental.distance)
    classification = _classification(
        raw_equal=raw_equal,
        segment_equal=segment_equal,
        stress_equal=stress_equal,
        segment_relation=segment_relation,
    )

    return PronunciationComparison(
        classification=classification,
        source=structural_source,
        target=structural_target,
        raw_equal=raw_equal,
        canonical_equal=segment_equal and stress_equal,
        segment_equal=segment_equal,
        stress_equal=stress_equal,
        segment_relation=segment_relation,
        segmental=segmental,
        stress_operations=_stress_operations(structural_source.stress, structural_target.stress),
        metric=_COMPARISON_METRIC,
        metric_version=_COMPARISON_METRIC_VERSION,
    )
