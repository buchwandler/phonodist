from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StressKind = Literal["primary", "secondary"]
StressOperationKind = Literal["insert", "delete", "replace"]
SegmentRelation = Literal["exact", "equivalent", "different"]
ComparisonKind = Literal[
    "exact",
    "notation_only",
    "stress_only",
    "phonetic_equivalent",
    "stress_and_phonetic_equivalent",
    "segmental",
    "stress_and_segmental",
]


@dataclass(frozen=True, slots=True)
class StressEvent:
    kind: StressKind
    anchor: int


@dataclass(frozen=True, slots=True)
class StressOperation:
    kind: StressOperationKind
    source: StressEvent | None
    target: StressEvent | None


@dataclass(frozen=True, slots=True)
class ComparisonPronunciation:
    original: str
    normalized: str
    segments: tuple[str, ...]
    stress: tuple[StressEvent, ...]
    diagnostics: tuple[ParseDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class PronunciationComparison:
    classification: ComparisonKind
    source: ComparisonPronunciation
    target: ComparisonPronunciation
    raw_equal: bool
    canonical_equal: bool
    segment_equal: bool
    stress_equal: bool
    segment_relation: SegmentRelation
    segmental: DistanceResult
    stress_operations: tuple[StressOperation, ...]
    metric: str
    metric_version: str


OperationKind = Literal[
    "match",
    "substitute",
    "insert",
    "delete",
    "sequence_equivalence",
]


@dataclass(frozen=True, slots=True)
class ParseDiagnostic:
    offset: int
    text: str
    codepoint: str
    category: str
    action: Literal["ignored", "normalized", "unknown"]
    reason: str


@dataclass(frozen=True, slots=True)
class ParsedPronunciation:
    original: str
    normalized: str
    segments: tuple[str, ...]
    diagnostics: tuple[ParseDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class AliasRule:
    input: str
    canonical: str
    reason: str


@dataclass(frozen=True, slots=True)
class SequenceEquivalence:
    left: tuple[str, ...]
    right: tuple[str, ...]
    cost: float
    reason: str


@dataclass(frozen=True, slots=True)
class LanguageProfile:
    id: str
    version: str
    name: str
    default_ignore_stress: bool
    inventory: tuple[str, ...]
    aliases: tuple[AliasRule, ...]
    sequence_equivalences: tuple[SequenceEquivalence, ...]
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AlignmentOperation:
    source: tuple[str, ...]
    target: tuple[str, ...]
    kind: OperationKind
    cost: float
    reason: str


@dataclass(frozen=True, slots=True)
class DistanceResult:
    distance: float
    raw_cost: float
    denominator: float
    source: ParsedPronunciation
    target: ParsedPronunciation
    operations: tuple[AlignmentOperation, ...]
    metric: str
    metric_version: str
    language: str | None
    profile_version: str | None
    backend: str
    backend_version: str
    feature_set: str
