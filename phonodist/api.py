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
    """Normalize IPA text and split it into IPA units.

    Parameters
    ----------
    value : str
        IPA string to normalize. Matching outer ``/.../`` or ``[...]`` delimiters
        and surrounding whitespace are stripped.
    language : str or None
        Bundled language-profile tag used for profile defaults and notation aliases.
        ``None`` selects universal parsing. Aliases include ``de``, ``de-DE``, and
        ``de_de`` for the German profile.
    ignore_stress : bool or None
        Whether to remove primary/secondary stress markers. ``None`` uses the
        selected profile's default; in universal mode it defaults to ``True``.

    Returns
    -------
    ParsedPronunciation
        Original and normalized text, canonical segment units, and diagnostics.

    Raises
    ------
    InvalidIPAError
        If ``value`` is not a string or a non-empty value normalizes to no parseable content.
    UnknownLanguageProfileError
        If ``language`` does not resolve to a bundled profile.

    Notes
    -----
    Normalization applies NFC, ignores internal whitespace and Unicode format
    characters, and canonicalizes supported tie-bar variants. It does not check
    whether every segment is supported by the metric's feature backend.
    """
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
    """Return normalized PanPhon feature distance for two IPA segments.

    Parameters
    ----------
    left, right : str
        IPA segments to compare. Each value must be recognized as exactly one
        segment by the PanPhon backend.

    Returns
    -------
    float
        Unweighted feature difference normalized to ``[0, 1]``.

    Raises
    ------
    UnknownSegmentError
        If either input is not a supported single segment or their feature
        vectors are incompatible.
    """
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
    """Compute normalized ``feature-align/1`` distance between IPA values.

    Parameters
    ----------
    source, target : str
        IPA pronunciations to compare.
    language : str or None
        Language-profile tag; ``None`` selects universal mode without
        language-specific profile rules.
    ignore_stress : bool or None
        Stress policy passed to IPA parsing. ``None`` uses the selected profile's
        default, or ignores stress in universal mode. Explicit ``False`` is
        unsupported by ``feature-align/1`` and raises ``NotImplementedError``.
    explain : bool
        If true, include the deterministic segment-alignment traceback in
        ``DistanceResult.operations``. The default score-only path returns an
        empty operations tuple.

    Returns
    -------
    DistanceResult
        Normalized distance, raw alignment cost, denominator, parsed inputs,
        optional operations, and metric/profile/backend provenance.

    Raises
    ------
    InvalidIPAError
        If an input cannot be normalized into parseable IPA.
    UnknownLanguageProfileError
        If ``language`` does not resolve to a bundled profile.
    UnknownSegmentError
        If the selected feature backend cannot represent an input segment.
    NotImplementedError
        If ``ignore_stress=False`` requests unimplemented stress-sensitive scoring.

    Notes
    -----
    The score is bounded to ``[0, 1]`` and is not a calibrated human perceptual
    distance. Score-only and traceback modes are intended to produce the same
    score; ``explain=True`` adds operation detail. Stress is ignored by this
    metric. Use :func:`compare_pronunciations` for structural stress diagnostics.
    """
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
    """Classify structural differences between two IPA pronunciations.

    Parameters
    ----------
    source, target : str
        IPA pronunciations to compare.
    language : str or None
        Optional language-profile tag for notation aliases and sequence
        equivalences; ``None`` uses universal rules.
    explain : bool
        If true, include segment-alignment and stress-operation details.

    Returns
    -------
    PronunciationComparison
        ``ipa-compare/1`` classification, canonical sides, anchored stress
        events, and an embedded stress-free ``feature-align/1`` result.

    Raises
    ------
    InvalidIPAError
        If an input contains no parseable IPA content.
    UnknownLanguageProfileError
        If ``language`` does not resolve to a bundled profile.
    UnknownSegmentError
        If the feature backend cannot represent an input segment.

    Notes
    -----
    Stress anchors count canonical segments preceding each stress mark. The
    classification is structural, not a calibrated stress-distance model or a
    judgment about which pronunciation is correct. The profile is optional.
    """
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
