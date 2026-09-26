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
    """A primary or secondary stress mark in an IPA comparison.

    Attributes
    ----------
    kind : str
        Stress kind, either ``primary`` or ``secondary``.
    anchor : int
        Number of canonical segments before the stress mark. Zero means before
        the first segment; the segment count means after the final segment.
    """

    kind: StressKind
    anchor: int


@dataclass(frozen=True, slots=True)
class StressOperation:
    """One insertion, deletion, or kind replacement in aligned stress events.

    Attributes
    ----------
    kind : str
        Operation kind: ``insert``, ``delete``, or ``replace``.
    source : StressEvent or None
        Source-side event, or ``None`` when inserted.
    target : StressEvent or None
        Target-side event, or ``None`` when deleted.
    """

    kind: StressOperationKind
    source: StressEvent | None
    target: StressEvent | None


@dataclass(frozen=True, slots=True)
class ComparisonPronunciation:
    """A normalized pronunciation split into canonical segments and stress.

    Attributes
    ----------
    original : str
        Input IPA string before normalization.
    normalized : str
        NFC-normalized IPA after supported format/spacing normalization and
        profile aliases; stress markers are retained.
    segments : tuple of str
        Canonical stress-free segment sequence. Entries are segment strings,
        not codepoint offsets.
    stress : tuple of StressEvent
        Primary and secondary events anchored by the number of preceding
        canonical segments.
    diagnostics : tuple of ParseDiagnostic
        Normalization observations associated with this pronunciation.
    """

    original: str
    normalized: str
    segments: tuple[str, ...]
    stress: tuple[StressEvent, ...]
    diagnostics: tuple[ParseDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class PronunciationComparison:
    """Structural ``ipa-compare/1`` result with an embedded segmental score.

    Attributes
    ----------
    classification : str
        Structural classification; see ``ComparisonKind``.
    source, target : ComparisonPronunciation
        Parsed sides, including canonical segments and anchored stress events.
    raw_equal : bool
        Whether the original input strings are identical.
    canonical_equal : bool
        Whether both canonical segment sequences and stress events are equal.
    segment_equal : bool
        Whether the canonical segment sequences are equal.
    stress_equal : bool
        Whether the anchored stress events are equal.
    segment_relation : str
        ``exact``, ``equivalent``, or ``different`` segment relation.
    segmental : DistanceResult
        Embedded stress-free ``feature-align/1`` result.
    stress_operations : tuple of StressOperation
        Deterministic event insertions, deletions, and replacements.
    metric : str
        Structural metric identifier.
    metric_version : str
        Structural metric version.
    """

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
    """A normalization observation made while preparing IPA input.

    Attributes
    ----------
    offset : int
        Unicode codepoint offset in the normalized working input, after outer
        delimiters and surrounding whitespace have been removed; this is not
        necessarily an offset into ``ParsedPronunciation.original``.
    text : str
        Character or text observed.
    codepoint : str
        Unicode codepoint notation for the observed text.
    category : str
        Unicode general category or categories.
    action : str
        Normalization action, such as ``ignored`` or ``normalized``.
    reason : str
        Machine-readable explanation of the action.
    """

    offset: int
    text: str
    codepoint: str
    category: str
    action: Literal["ignored", "normalized", "unknown"]
    reason: str


@dataclass(frozen=True, slots=True)
class ParsedPronunciation:
    """Normalized IPA input and its segment-level representation.

    Attributes
    ----------
    original : str
        Input value before normalization.
    normalized : str
        NFC-normalized IPA after whitespace/format handling, stress policy,
        and any selected profile aliases.
    segments : tuple of str
        Canonical IPA units produced from the normalized text.
    diagnostics : tuple of ParseDiagnostic
        Normalization observations; offsets refer to the normalized working
        input rather than necessarily to the original string.
    """

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
    """Bundled language-specific defaults and sparse IPA comparison rules.

    ``inventory`` is descriptive metadata, not an exhaustive segment
    rejection list; metric v1 uses PanPhon as the authority for feature
    availability.

    Attributes
    ----------
    id : str
        Canonical profile identifier.
    version : str
        Profile data version, recorded in distance provenance.
    name : str
        Human-readable profile name.
    default_ignore_stress : bool
        Default stress policy used when parsing with this profile.
    inventory : tuple of str
        Descriptive inventory metadata; not an exhaustive accepted-segment set.
    aliases : tuple
        Representation-level notation aliases.
    sequence_equivalences : tuple
        Profile-specific segment-sequence equivalences and their costs.
    sources : tuple of str
        Provenance references for the profile rules.
    """

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
    """One operation in a segment alignment traceback.

    Attributes
    ----------
    source : tuple of str
        Source-side segment sequence; empty for an insertion.
    target : tuple of str
        Target-side segment sequence; empty for a deletion.
    kind : str
        Operation kind: match, substitute, insert, delete, or sequence equivalence.
    cost : float
        Unnormalized operation cost in the metric's alignment units. Costs are
        between zero and one per operation; insertion/deletion cost one.
    reason : str
        Explanation code or profile-rule rationale for the operation.
    """

    source: tuple[str, ...]
    target: tuple[str, ...]
    kind: OperationKind
    cost: float
    reason: str


@dataclass(frozen=True, slots=True)
class DistanceResult:
    """Score, optional traceback, and provenance for ``feature-align/1``.

    ``distance`` is normalized to ``[0, 1]`` as ``raw_cost / denominator``;
    it is zero when both segment sequences are empty. A zero score can result
    from canonicalization or a zero-cost profile equivalence, not only identical
    original strings.

    Attributes
    ----------
    distance : float
        Normalized feature distance in ``[0, 1]``.
    raw_cost : float
        Unnormalized sum of alignment operation costs.
    denominator : float
        Maximum of source and target segment counts, represented as a float.
    source, target : ParsedPronunciation
        Parsed inputs used for scoring.
    operations : tuple of AlignmentOperation
        Deterministic traceback when ``explain=True``; otherwise an empty tuple.
    metric : str
        Metric identifier, currently ``feature-align``.
    metric_version : str
        Metric semantics version.
    language : str or None
        Normalized selected profile tag, or ``None`` in universal mode.
    profile_version : str or None
        Selected profile version, or ``None`` without a profile.
    backend : str
        Feature backend name.
    backend_version : str
        Resolved feature backend version.
    feature_set : str
        Backend feature set used for the calculation.
    """

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
