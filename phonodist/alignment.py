from __future__ import annotations

from dataclasses import dataclass

from .features import FeatureBackend
from .model import AlignmentOperation, SequenceEquivalence


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


def align_segments(
    source: tuple[str, ...],
    target: tuple[str, ...],
    *,
    backend: FeatureBackend,
    equivalences: tuple[SequenceEquivalence, ...] = (),
) -> tuple[float, tuple[AlignmentOperation, ...]]:
    """Weighted dynamic-programming alignment with sparse N<->M rules."""
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

            if i > 0 and j > 0:
                left = source[i - 1]
                right = target[j - 1]
                if left == right:
                    sub_cost = 0.0
                    kind = "match"
                    reason = "exact_segment"
                    precedence = 0
                else:
                    sub_cost = backend.segment_distance(left, right)
                    kind = "substitute"
                    reason = "panphon_feature_substitution"
                    precedence = 1

                operation = AlignmentOperation(
                    source=(left,),
                    target=(right,),
                    kind=kind,  # type: ignore[arg-type]
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
                orientations = (
                    (rule.left, rule.right),
                    (rule.right, rule.left),
                )
                for left_sequence, right_sequence in orientations:
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
                                _Step(
                                    previous_i,
                                    previous_j,
                                    operation,
                                    2,
                                ),
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
                candidates.append(
                    (
                        costs[i - 1][j] + 1.0,
                        3,
                        _Step(i - 1, j, operation, 3),
                    )
                )

            if j > 0:
                operation = AlignmentOperation(
                    source=(),
                    target=(target[j - 1],),
                    kind="insert",
                    cost=1.0,
                    reason="segment_insertion",
                )
                candidates.append(
                    (
                        costs[i][j - 1] + 1.0,
                        4,
                        _Step(i, j - 1, operation, 4),
                    )
                )

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
