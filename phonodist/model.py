from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

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
