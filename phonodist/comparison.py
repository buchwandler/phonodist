from __future__ import annotations

from collections import defaultdict
from typing import cast

from ._symbols import STRESS_KIND_BY_MARKER
from .errors import InvalidIPAError
from .model import (
    ComparisonKind,
    ComparisonPronunciation,
    SegmentRelation,
    StressEvent,
    StressKind,
    StressOperation,
)
from .normalize import normalize_ipa
from .profiles import get_profile
from .tokenize import apply_aliases, ipa_units


def _parse_comparison_pronunciation(
    value: str,
    *,
    language: str | None,
) -> ComparisonPronunciation:
    profile = get_profile(language) if language is not None else None
    normalized, diagnostics = normalize_ipa(value, ignore_stress=False)
    normalized = apply_aliases(normalized, profile)

    segments: list[str] = []
    stress: list[StressEvent] = []
    for unit in ipa_units(normalized):
        kind = STRESS_KIND_BY_MARKER.get(unit)
        if kind is not None:
            stress.append(
                StressEvent(
                    kind=cast(StressKind, kind),
                    anchor=len(segments),
                )
            )
            continue
        segments.append(unit)

    if not segments and value.strip():
        raise InvalidIPAError("IPA value contains no parseable IPA characters")

    return ComparisonPronunciation(
        original=value,
        normalized=normalized,
        segments=tuple(segments),
        stress=tuple(stress),
        diagnostics=diagnostics,
    )


def _stress_operations(
    source: tuple[StressEvent, ...],
    target: tuple[StressEvent, ...],
) -> tuple[StressOperation, ...]:
    source_by_anchor: dict[int, list[StressEvent]] = defaultdict(list)
    target_by_anchor: dict[int, list[StressEvent]] = defaultdict(list)
    for event in source:
        source_by_anchor[event.anchor].append(event)
    for event in target:
        target_by_anchor[event.anchor].append(event)

    operations: list[StressOperation] = []
    for anchor in sorted(source_by_anchor.keys() | target_by_anchor.keys()):
        source_events = source_by_anchor[anchor]
        target_events = target_by_anchor[anchor]
        paired = min(len(source_events), len(target_events))
        for index in range(paired):
            source_event = source_events[index]
            target_event = target_events[index]
            if source_event.kind != target_event.kind:
                operations.append(
                    StressOperation(kind="replace", source=source_event, target=target_event)
                )
        for event in source_events[paired:]:
            operations.append(StressOperation(kind="delete", source=event, target=None))
        for event in target_events[paired:]:
            operations.append(StressOperation(kind="insert", source=None, target=event))
    return tuple(operations)


def _segment_relation(
    source: ComparisonPronunciation,
    target: ComparisonPronunciation,
    segmental_distance: float,
) -> SegmentRelation:
    if source.segments == target.segments:
        return "exact"
    if segmental_distance == 0.0:
        return "equivalent"
    return "different"


def _classification(
    *,
    raw_equal: bool,
    segment_equal: bool,
    stress_equal: bool,
    segment_relation: SegmentRelation,
) -> ComparisonKind:
    if raw_equal:
        return "exact"
    if segment_equal and stress_equal:
        return "notation_only"
    if segment_equal:
        return "stress_only"
    if segment_relation == "equivalent":
        if stress_equal:
            return "phonetic_equivalent"
        return "stress_and_phonetic_equivalent"
    if stress_equal:
        return "segmental"
    return "stress_and_segmental"
