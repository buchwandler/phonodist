from __future__ import annotations

from dataclasses import dataclass

from .features import FeatureBackend
from .model import AlignmentOperation, OperationKind, SequenceEquivalence


@dataclass(frozen=True, slots=True)
class _Step:
    previous_i: int
    previous_j: int
    operation: AlignmentOperation
    precedence: int


def _suffix_matches(
    sequence: tuple[str, ...],
    end: int,
    suffix: tuple[str, ...],
) -> bool:
    start = end - len(suffix)
    return start >= 0 and sequence[start:end] == suffix


def _substitution_cost(backend: FeatureBackend, left: str, right: str) -> float:
    return 0.0 if left == right else backend.segment_distance(left, right)


def _align_score_only(
    source: tuple[str, ...],
    target: tuple[str, ...],
    *,
    backend: FeatureBackend,
    equivalences: tuple[SequenceEquivalence, ...],
) -> float:
    rows = len(source) + 1
    cols = len(target) + 1
    costs = [[float("inf")] * cols for _ in range(rows)]
    costs[0][0] = 0.0

    for i in range(rows):
        for j in range(cols):
            if i == 0 and j == 0:
                continue

            candidates: list[tuple[float, int, int, int]] = []
            if i > 0 and j > 0:
                candidates.append(
                    (
                        costs[i - 1][j - 1]
                        + _substitution_cost(backend, source[i - 1], target[j - 1]),
                        0 if source[i - 1] == target[j - 1] else 1,
                        i - 1,
                        j - 1,
                    )
                )

            for rule in equivalences:
                for left_sequence, right_sequence in (
                    (rule.left, rule.right),
                    (rule.right, rule.left),
                ):
                    if _suffix_matches(source, i, left_sequence) and _suffix_matches(
                        target, j, right_sequence
                    ):
                        previous_i = i - len(left_sequence)
                        previous_j = j - len(right_sequence)
                        candidates.append(
                            (costs[previous_i][previous_j] + rule.cost, 2, previous_i, previous_j)
                        )

            if i > 0:
                candidates.append((costs[i - 1][j] + 1.0, 3, i - 1, j))
            if j > 0:
                candidates.append((costs[i][j - 1] + 1.0, 4, i, j - 1))

            costs[i][j] = min(
                candidates,
                key=lambda item: (round(item[0], 12), item[1], item[2], item[3]),
            )[0]

    return costs[-1][-1]


def _align_with_traceback(
    source: tuple[str, ...],
    target: tuple[str, ...],
    *,
    backend: FeatureBackend,
    equivalences: tuple[SequenceEquivalence, ...],
) -> tuple[float, tuple[AlignmentOperation, ...]]:
    rows = len(source) + 1
    cols = len(target) + 1

    costs = [[float("inf")] * cols for _ in range(rows)]
    steps: list[list[_Step | None]] = [[None] * cols for _ in range(rows)]
    costs[0][0] = 0.0

    for i in range(rows):
        for j in range(cols):
            if i == 0 and j == 0:
                continue

            candidates: list[tuple[float, int, _Step]] = []

            kind: OperationKind
            if i > 0 and j > 0:
                left = source[i - 1]
                right = target[j - 1]
                if left == right:
                    kind = "match"
                    reason = "exact_segment"
                    precedence = 0
                    sub_cost = 0.0
                else:
                    kind = "substitute"
                    reason = "panphon_feature_substitution"
                    precedence = 1
                    sub_cost = backend.segment_distance(left, right)

                operation = AlignmentOperation(
                    source=(left,),
                    target=(right,),
                    kind=kind,
                    cost=sub_cost,
                    reason=reason,
                )
                candidates.append(
                    (
                        costs[i - 1][j - 1] + sub_cost,
                        precedence,
                        _Step(i - 1, j - 1, operation, precedence),
                    )
                )

            for rule in equivalences:
                for left_sequence, right_sequence in (
                    (rule.left, rule.right),
                    (rule.right, rule.left),
                ):
                    if _suffix_matches(source, i, left_sequence) and _suffix_matches(
                        target, j, right_sequence
                    ):
                        previous_i = i - len(left_sequence)
                        previous_j = j - len(right_sequence)
                        operation = AlignmentOperation(
                            source=left_sequence,
                            target=right_sequence,
                            kind="sequence_equivalence",
                            cost=rule.cost,
                            reason=rule.reason,
                        )
                        candidates.append(
                            (
                                costs[previous_i][previous_j] + rule.cost,
                                2,
                                _Step(previous_i, previous_j, operation, 2),
                            )
                        )

            if i > 0:
                operation = AlignmentOperation(
                    source=(source[i - 1],),
                    target=(),
                    kind="delete",
                    cost=1.0,
                    reason="segment_deletion",
                )
                candidates.append((costs[i - 1][j] + 1.0, 3, _Step(i - 1, j, operation, 3)))

            if j > 0:
                operation = AlignmentOperation(
                    source=(),
                    target=(target[j - 1],),
                    kind="insert",
                    cost=1.0,
                    reason="segment_insertion",
                )
                candidates.append((costs[i][j - 1] + 1.0, 4, _Step(i, j - 1, operation, 4)))

            best_cost, _, best_step = min(
                candidates,
                key=lambda item: (
                    round(item[0], 12),
                    item[1],
                    item[2].previous_i,
                    item[2].previous_j,
                ),
            )
            costs[i][j] = best_cost
            steps[i][j] = best_step

    operations: list[AlignmentOperation] = []
    i = len(source)
    j = len(target)

    while i or j:
        step = steps[i][j]
        if step is None:
            raise RuntimeError(f"missing traceback step at {(i, j)}")
        operations.append(step.operation)
        i = step.previous_i
        j = step.previous_j

    operations.reverse()
    return costs[-1][-1], tuple(operations)


def align_segments(
    source: tuple[str, ...],
    target: tuple[str, ...],
    *,
    backend: FeatureBackend,
    equivalences: tuple[SequenceEquivalence, ...] = (),
    explain: bool = False,
) -> tuple[float, tuple[AlignmentOperation, ...]]:
    """Align segments, optionally returning the deterministic traceback."""
    if explain:
        return _align_with_traceback(
            source,
            target,
            backend=backend,
            equivalences=equivalences,
        )
    return _align_score_only(
        source,
        target,
        backend=backend,
        equivalences=equivalences,
    ), ()
